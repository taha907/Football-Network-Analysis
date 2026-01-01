import networkx as nx
import time
from .base_algorithm import BaseAlgorithm


class WelshPowellAlgorithm(BaseAlgorithm):
    """Geliştirilmiş Welsh-Powell graf renklendirme algoritması [cite: 38, 45]"""

    def execute(self):
        start_time = time.time()


        # genellikle daha fazla renk grubu oluşmasını sağlar.
        coloring_dict = nx.coloring.greedy_color(
            self.graph_data,
            strategy="random_sequential"
        )

        self.execution_time = time.time() - start_time
        return coloring_dict
class CentralityAlgorithm(BaseAlgorithm):
    """Derece merkeziliği ile en etkili 5 düğümü belirleme [cite: 37]"""
    def execute(self):
        # Düğüm derecelerini hesapla [cite: 37]
        degrees = dict(self.graph_data.degree())
        sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:5]
        return sorted_degrees