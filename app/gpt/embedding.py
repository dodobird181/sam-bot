from typing import List

import openai


class EmbeddingFailed(Exception):
    """
    Embedding request failed.
    """


class EmbeddingRequest:
    """
    Wrapper for sending embedding requests to GPT.
    """
    
    DEFAULT_KWARGS = {
        'model': 'text-embedding-ada-002',
        'temperature': 0.6,
        'max_tokens': 150,
        'frequency_penalty': 0,
        'presence_penalty': 0.6,
        }
    
    def __init__(self, sentences: List[str], **kwargs):
        self._request_kwargs = self.DEFAULT_KWARGS.copy() | kwargs | {'input': sentences}
        self._original_sentences = sentences

    def send(self) -> dict:
        """
        Send a request to Chat GPT and return the response, otherwise throw an error.
        """
        try:
            response = openai.Embedding.create(**self._request_kwargs)
            return response
        except Exception as e:
            raise EmbeddingFailed from e
