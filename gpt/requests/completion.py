from dataclasses import dataclass

import openai

from app.exceptions import RequestFailed


class CompletionFailed(RequestFailed):
    """
    Completion request failed.
    """


class CompletionRequest:
    """
    Wrapper for sending completion requests to GPT.
    """

    DEFAULT_KWARGS = {
        'model': 'text-davinci-003',
        'temperature': 0.6,
        'max_tokens': 150,
        'frequency_penalty': 0,
        'presence_penalty': 0.6,
        }
    
    def __init__(self, prompt: str, **kwargs):
        self._request_kwargs = self.DEFAULT_KWARGS.copy() | kwargs | {'prompt': prompt}

    def send(self) -> str:
        """
        Send a request to Chat GPT and return the string response, otherwise throw an error.
        """
        try:
            response = openai.Completion.create(**self._request_kwargs)
            return str(response.choices[0]['text'])
        except Exception as e:
            raise CompletionFailed from e
