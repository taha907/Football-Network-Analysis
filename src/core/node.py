from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

# Base nesnesi burada tanımlanır, diğerleri buradan miras alır
Base = declarative_base()

class Node(Base):
    __tablename__ = 'nodes'

    node_id = Column(Integer, primary_key=True)
    name = Column(String)

    # Görselleştirme ve Analiz için Gerekli Özellikler
    mevki = Column(String, default="Orta Saha")
    hiz = Column(Float, default=50.0)
    pas = Column(Float, default=50.0)
    sut = Column(Float, default=50.0)
    defans = Column(Float, default=50.0)
    fizik = Column(Float, default=50.0)
    tecrube = Column(Float, default=50.0)

    def __init__(self, node_id, name, **kwargs):
        self.node_id = node_id
        self.name = name
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def to_dict(self):
        #json kaydetme için özellik tanımları
        return {
            "id": self.node_id,
            "name": self.name,
            "mevki": self.mevki,
            "hiz": self.hiz,
            "pas": self.pas,
            "sut": self.sut,
            "defans": self.defans,
            "fizik": self.fizik,
            "tecrube": self.tecrube
        }