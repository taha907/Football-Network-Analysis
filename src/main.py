import sys
import os
import tkinter as tk

# Proje ana dizinini yola ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.visualizer import SocialNetworkVisualizer
except ImportError:
    from src.ui.visualizer import SocialNetworkVisualizer


def main():
    root = tk.Tk()

    app = SocialNetworkVisualizer(master=root)


    if not app.dm.get_all_nodes():
        print("Veritabanı boş. Otomatik örnek veriler yükleniyor...")
        from core.node import Node

        # 1. Örnek Oyuncular Oluştur
        p1 = Node(1, "Muslera", mevki="Kaleci", hiz=45, pas=85, defans=90)
        p2 = Node(2, "Boey", mevki="Defans", hiz=95, pas=75, defans=85)
        p3 = Node(3, "Torreira", mevki="Orta Saha", hiz=85, pas=88, fizik=90)
        p4 = Node(4, "Kerem", mevki="Orta Saha", hiz=92, pas=78, sut=80)
        p5 = Node(5, "Icardi", mevki="Forvet", hiz=75, pas=90, sut=95)

        # Oyuncuları Kaydet
        app.dm.add_node(p1)
        app.dm.add_node(p2)
        app.dm.add_node(p3)
        app.dm.add_node(p4)
        app.dm.add_node(p5)

        # Örnek Bağlantılar (Pas Trafiği) Kur
        app.dm.add_edge(1, 2, weight=1.5)  # Muslera -> Boey
        app.dm.add_edge(2, 3, weight=1.2)  # Boey -> Torreira
        app.dm.add_edge(3, 4, weight=1.0)  # Torreira -> Kerem
        app.dm.add_edge(3, 5, weight=0.8)  # Torreira -> Icardi (Çok iyi uyum)
        app.dm.add_edge(4, 5, weight=1.1)  # Kerem -> Icardi

        # Ekranı Yenile
        app.refresh_ui()
        print("Örnek veriler yüklendi!")

    # --------------------------------------------------

    def on_closing():
        try:
            if hasattr(app, 'dm') and app.dm:
                app.dm.close()
        except:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()