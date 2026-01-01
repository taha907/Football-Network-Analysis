from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import yollarını proje yapına göre ayarladım
try:
    from src.core.node import Base, Node
    from src.core.edge import Edge
except ImportError:
    # Eğer IDE kök dizini farklı algılarsa diye alternatif
    from core.node import Base, Node
    from core.edge import Edge
import json
import os


class DataManager:
    # Veritabanı bağlantısını kurar ve dosya yollarını dinamik olarak ayarlar.
    def __init__(self, db_filename="social_network.db"):
        current_file_path = os.path.abspath(__file__)
        core_dir = os.path.dirname(current_file_path)
        src_dir = os.path.dirname(core_dir)

        self.project_root = os.path.dirname(src_dir)

        self.data_dir = os.path.join(self.project_root, 'data')

        os.makedirs(self.data_dir, exist_ok=True)

        # Veritabanı bağlantısı
        db_path = os.path.join(self.data_dir, db_filename)
        connection_string = f'sqlite:///{db_path}'
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    # Verilen dosya adı için data klasörünü baz alarak tam dosya yolunu oluşturur.
    def _get_full_path(self, filename):

        if os.path.isabs(filename):
            return filename
        # Sadece isimse (ornek.json), data klasörüne ekle
        return os.path.join(self.data_dir, filename)

    # veritabanı işlemleri

    # Yeni düğüm ekler veya ID mevcutsa özelliklerini günceller.
    def add_node(self, node):
        try:
            existing = self.session.query(Node).filter_by(node_id=node.node_id).first()
            if not existing:
                self.session.add(node)
            else:
                existing.name = node.name
                existing.mevki = node.mevki
                for attr in ['hiz', 'pas', 'sut', 'defans', 'fizik', 'tecrube']:
                    if hasattr(node, attr):
                        setattr(existing, attr, getattr(node, attr))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"Hata add_node: {e}")

    # Belirtilen ID'li düğümü ve ona bağlı olan tüm kenarları siler.
    def delete_node(self, node_id):
        try:
            node = self.session.query(Node).filter_by(node_id=node_id).first()
            if node:
                self.session.query(Edge).filter((Edge.source_id == node_id) | (Edge.target_id == node_id)).delete()
                self.session.delete(node)
                self.session.commit()
        except Exception as e:
            self.session.rollback()

    # İki düğüm arasına bağlantı ekler veya varsa ağırlığını günceller.
    def add_edge(self, u, v, weight=1.0):
        if u == v: return
        try:
            n1 = self.session.query(Node).filter_by(node_id=u).first()
            n2 = self.session.query(Node).filter_by(node_id=v).first()
            if n1 and n2:
                existing = self.session.query(Edge).filter_by(source_id=u, target_id=v).first()
                if existing:
                    existing.weight = weight
                else:
                    edge = Edge(source_id=u, target_id=v, weight=weight)
                    self.session.add(edge)
                self.session.commit()
        except Exception as e:
            self.session.rollback()

    # veritabanından tüm düğümleri alır ve döndürür
    def get_all_nodes(self):
        self.session.expire_all()
        return self.session.query(Node).all()

    # veritabanındaki tüm kenarları alır ve döndürür
    def get_all_edges(self):
        self.session.expire_all()
        return self.session.query(Edge).all()

    # evritabanı oturumu kapatır
    def close(self):
        self.session.close()

    # JSON İŞLEMLERİ

    # Mevcut düğüm ve kenar verilerini JSON formatında dosyaya kaydeder.
    def export_to_json(self, filename="footballNetwork.json"):
        # UI'dan gelen dosya adını alıp Data klasörüne zorluyoruz
        full_path = self._get_full_path(filename)

        nodes = [n.to_dict() for n in self.get_all_nodes()]
        edges = [{"source": e.source_id, "target": e.target_id, "weight": e.weight} for e in self.get_all_edges()]
        data = {"nodes": nodes, "edges": edges}

        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"✅ Başarılı: Dosya şuraya kaydedildi -> {full_path}")
        except Exception as e:
            print(f"❌ Kaydetme Hatası: {e}")

    # Veritabanını temizler ve JSON verisinden düğüm/kenarları yeniden oluşturur.
    def import_from_extended_json(self, data):
        print("Veritabanı temizleniyor ve yeni veri yükleniyor...")
        try:
            self.session.query(Edge).delete()
            self.session.query(Node).delete()
            self.session.commit()
        except Exception:
            self.session.rollback()

        # Nodes
        nodes_list = data.get("nodes", data.get("futbolcular", []))
        count = 0
        for n_data in nodes_list:
            try:
                n_id = n_data.get('id')
                n_name = n_data.get('name', n_data.get('isim'))
                n_mevki = n_data.get('mevki', 'Bilinmiyor')
                if n_id is not None and n_name is not None:
                    attr = n_data.copy()
                    if 'ozellikler' in attr: attr.update(attr.pop('ozellikler'))
                    attr['mevki'] = n_mevki
                    for k in ['id', 'name', 'isim']:
                        if k in attr: del attr[k]
                    self.add_node(Node(n_id, n_name, **attr))
                    count += 1
            except:
                pass

        # Edges
        edges_list = data.get("edges", data.get("baglantilar", []))
        e_count = 0
        for e_data in edges_list:
            try:
                u = e_data.get('source', e_data.get('kaynak'))
                v = e_data.get('target', e_data.get('hedef'))
                w = e_data.get('weight', 1.0)
                if u is not None and v is not None:
                    self.add_edge(u, v, weight=w)
                    e_count += 1
            except:
                pass
        print(f"İçe aktarma tamamlandı: {count} Oyuncu, {e_count} Bağlantı.")

    # Belirtilen JSON dosyasını okur ve içe aktarma işlemini tetikler.
    def load_from_json(self, filename="footballNetwork.json"):
        full_path = self._get_full_path(filename)
        if not os.path.exists(full_path):
            print(f"❌ Hata: Dosya bulunamadı -> {full_path}")
            return

        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.import_from_extended_json(data)
        except Exception as e:
            print(f"Okuma hatası: {e}")