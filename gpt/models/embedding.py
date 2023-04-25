from hashlib import sha256
from typing import List

from sklearn.neighbors import KDTree


class EmbeddingNode:
    """
    A single text embedding.
    """
    def __init__(self, text: str, vector: List[float], hash: str):
        self._text = text
        self._vector = vector
        self._hash = hash
    
    def dimensionality(self) -> int:
        return len(self._vector)
    
    def text(self) -> str:
        return self._text
    
    def vector(self) -> List[float]:
        return self._vector
    
    def hash(self) -> str:
        return self._hash
    

class EmbeddingNodeFactory:
    """
    Factory for creating `EmbeddingNode` objects.
    """
    @classmethod
    def create_from_request_data(self, text: str, vector: List[float]) -> EmbeddingNode:
        hash = sha256(text.encode('UTF-8')).hexdigest()
        return EmbeddingNode(text, vector, hash)

    @classmethod
    def create_from_file_data(self, text: str, vector: List[float], hash: str) -> EmbeddingNode:
        return EmbeddingNode(text, vector, hash)


class Embedding:
    """
    Embedding object.
    """
    def __init__(self, nodes: List[EmbeddingNode]):
        self.nodes = nodes
        self.vectors = list(map(lambda node: node.vector(), nodes))
        
