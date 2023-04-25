from __future__ import annotations

import abc
import json
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.neighbors import KDTree


class ContextNode(abc.ABC):
    """
    Bit of context that can be mapped to a dictionary for saving locally.
    """
    @abc.abstractmethod
    def get_vector(self) -> str:
        """
        Get the vector representation of this node.
        """
        ...

    @abc.abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary.
        """
        ...
    
    @abc.abstractclassmethod
    def from_dict(cls, dict) -> ContextNode:
        ...


class ContextGenerator():
    """
    Class for extracting strings from a `ContextStore` that are similar 
    to the given input string.
    """

    def __init__(self, store: ContextStore):
        self.store = store
        self.vectors = [node.get_vector() for node in store.nodes]
        self.kdtree = KDTree(self.vectors)

    def generate(self, vector: List[float], k=1, max_dist=1.0) -> List[Tuple(ContextNode, float)]:
        """
        Pull the k-nearest `ContextNode`s from the `ContextStore` that are most 
        similar to the given vector and return a tuple of those nodes along with their
        distances from the vector.
        """
        valid_nodes = []
        valid_distances = []
        distances, indices = self.kdtree.query(np.array([vector]), k=k)
        for index, distance in zip(indices, distances):
            if distance <= max_dist:
                valid_nodes.append(self.store.nodes[index])
                valid_distances.append(distance)
        return list(zip(valid_nodes, valid_distances))
    

class ContextStore:
    """
    Wrapper for a list of `ContextNode` objects.
    """
    def __init__(self, nodes: List[ContextNode]):
        self.nodes = nodes
    
    @staticmethod
    def load_from_file(path, node_cls: ContextNode) -> ContextStore:
        with open(path, "r") as file:
            json_nodes = json.load(file)['nodes']
            nodes = list(map(lambda node: node_cls.from_dict(node), json_nodes))
            return ContextStore(nodes)

    def save_to_file(self, path) -> None:
        nodes = [node.to_dict() for node in self.nodes]
        json_nodes = json.dumps({'nodes': nodes}, indent=4)
        with open(path, "w") as file:
            file.write(json_nodes)

