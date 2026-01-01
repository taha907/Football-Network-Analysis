from sqlalchemy import Column, Integer, Float, ForeignKey
from core.node import Base

class Edge(Base):
    __tablename__ = 'edges'

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('nodes.node_id'))
    target_id = Column(Integer, ForeignKey('nodes.node_id'))
    weight = Column(Float)

    def __init__(self, source_id, target_id, weight=1.0):
        self.source_id = source_id
        self.target_id = target_id
        self.weight = weight

    # Visualizer uyumluluğu için property'ler
    @property
    def node1_id(self): return self.source_id

    @property
    def node2_id(self): return self.target_id