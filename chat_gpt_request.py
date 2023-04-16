import openai

import settings

openai.api_key = settings.CHAT_GPT_API_KEY


class ChatGPTRequest:
    """
    Wrapper for sending completion requests to Chat GPT.
    """

    class RequestFailed(Exception):
        """
        Something went wrong during the request to Chat GPT.
        """
        pass

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
            raise self.RequestFailed from e
