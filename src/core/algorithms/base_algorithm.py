from abc import ABC, abstractmethod
import time

class BaseAlgorithm(ABC):
    """Tüm algoritmalar için soyut temel sınıf """
    def __init__(self, graph_data):
        self.graph_data = graph_data
        self.execution_time = 0

    @abstractmethod
    def execute(self, **kwargs):
        """Her algoritma bu metodu override etmelidir """
        pass