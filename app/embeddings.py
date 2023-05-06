from __future__ import annotations

from typing import List

import numpy as np
from applogging import logger
from db import ObjectBase, ObjectCollection, init_db
from gpt.embedding import EmbeddingRequest
from sklearn.neighbors import KDTree


class QAPair(ObjectBase):
    """
    A question-answer pair.
    """

    def __init__(self, question: str, answer: str):
        super().__init__()
        self.question = question
        self.answer = answer
    
    def to_dict(self):
        return {
            'question': self.question,
            'answer': self.answer}
    
    @classmethod
    def from_dict(cls, dict):
        return QAPair(
            dict['question'],
            dict['answer'])


class QAPairEmbedding(ObjectBase):
    """
    TODO
    """

    def __init__(self, pair: QAPair, vector: List[float]):
        super().__init__()
        self.pair = pair
        self.vector = vector

    def to_dict(self):
        return {
            'pair': self.pair._to_dict_with_id(),
            'vector': self.vector}
    
    @classmethod
    def from_dict(cls, dict) -> QAPairEmbedding:
        return QAPairEmbedding(
            QAPair._from_dict_with_id(dict['pair']), 
            dict['vector'])
    
    @classmethod
    def from_qa_pair(cls, pair: QAPair) -> QAPairEmbedding:
        """
        Generate an embedding from a `QAPair` object by sending a request to
        openai's embeddings endpoint.
        """
        response = EmbeddingRequest([pair.question]).send()
        vector = response['data'][0]['embedding']
        return QAPairEmbedding(pair, vector)
    

class KNearestEmbeddings:
    """
    Wrapper for a list of embeddings with k-nearest functionality. Initializes a KDTree
    using the given embeddings and then compares the input vector to these embeddings.
    """

    def __init__(self, embeddings: List[QAPairEmbedding]):
        self.embeddings = embeddings
        self.vectors = [emb.vector for emb in embeddings]
        self.kdtree = KDTree(self.vectors)

    def get(self, vector: List[float], k=1) -> List[QAPairEmbedding]:
        """
        Get the nearest QAPairEmbedding to the given vector.
        """
        distances, indices = self.kdtree.query(np.array([vector]), k=k)
        indices = indices[0] # Indices are wrapped in another list for some reason..
        results = [self.embeddings[i] for i in indices]
        print(f'Distance: {distances}, indices: {indices}')
        return results


logger().warning('Test execution of KNearestEmbeddings!')
init_db()
embeddings = ObjectCollection.load('embeddings')
import time

while True:
    start_time = time.time()
    vector = QAPairEmbedding.from_qa_pair(QAPair(input('User: '), '')).vector
    k_nearest = KNearestEmbeddings(embeddings.as_list())
    nearest_embeddings = k_nearest.get(vector, k=4)
    end_time = time.time()
    for e in nearest_embeddings:
        print(e.pair)
    logger().debug(f'Embeddings result took {end_time - start_time}ms')

exit(0)

while True:
    user_sentence = input()
    user_request = EmbeddingRequest([user_sentence])
    user_embedding = EmbeddingDeserializer.from_request(user_request)
    user_arr = np.array(user_embedding.vectors[0])
    q_input = np.array([user_arr])
    print(f'User shape: {user_arr.shape}')

    arr = np.array(embedding.vectors)
    print(arr.shape)
    tree = KDTree(arr)

    dist, ind = tree.query(q_input)
    print(f'Distance: {dist}, indices: {ind}')
    print(f'Result: {embedding.nodes[ind[0][0]].text()}')


init_db()
pairs = ObjectCollection.load('qa_pairs')
embeddings = ObjectCollection(QAPairEmbedding, *[QAPairEmbedding.from_qa_pair(pair) for pair in pairs])
embeddings.save('embeddings')
