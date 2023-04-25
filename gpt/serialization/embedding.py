import json

from exceptions import DeserializationFailed, SerializationFailed
from gpt.models.embedding import Embedding, EmbeddingNode, EmbeddingNodeFactory
from gpt.requests.embedding import EmbeddingRequest


class EmbeddingSerializationFailed(SerializationFailed):
    """
    Failed to serialize embedding.
    """


class EmbeddingDeserializationFailed(DeserializationFailed):
    """
    Failed to deserialize embedding.
    """


class EmbeddingSerializer:
    """
    Methods for serializing and seserializing `Embedding` objects.
    """
    @classmethod
    def save_to_file(cls, path: str, embedding: Embedding) -> None:
        """
        Save the embedding object to a file.
        """
        try:
            nodes = []
            for node in embedding.nodes:
                nodes.append({
                    'hash': node.hash(),
                    'text': node.text(),
                    'vector': node.vector(),
                    })
            with open(path, "w") as outfile:
                outfile.write(json.dumps({'nodes': nodes}, indent=4))
        except Exception as e:
            raise EmbeddingSerializationFailed from e


class EmbeddingDeserializer:
    """
    Methods for deserializing `Embedding` objects.
    """
    @classmethod
    def from_request(cls, request: EmbeddingRequest) -> Embedding:
        """
        Generate an `Embedding` object from a request.
        """
        try:
            response = request.send()
            vector_data = response['data']
            text_data = request._original_sentences
            assert len(vector_data) == len(text_data)
            nodes = []
            for i in range(len(vector_data)):
                vector = vector_data[i]['embedding']
                text = text_data[i]
                node = EmbeddingNodeFactory.create_from_request_data(text, vector)
                nodes.append(node)
            return Embedding(nodes)
        except Exception as e:
            raise EmbeddingDeserializationFailed from e

    @classmethod
    def from_file(cls, path: str) -> Embedding:
        """
        Load an embedding object from a JSON file.
        """
        try:
            with open(path, "r") as infile:
                file_data = json.load(infile)
                nodes = []
                for node in file_data['nodes']:
                    nodes.append(
                        EmbeddingNodeFactory.create_from_file_data(
                            text=node['text'],
                            vector=node['vector'],
                            hash=node['hash'],
                            )
                        )
                return Embedding(nodes)
        except Exception as e:
            raise EmbeddingDeserializationFailed from e
