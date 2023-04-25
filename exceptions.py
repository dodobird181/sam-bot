"""
App-level exceptions.
"""


class AbstractException(Exception):
    """
    Any direct child of this class will raise a `NotImplementedError` if 
    someone tries to initialize it directly.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._raise_if_abstract()

    def _raise_if_abstract(self) -> None:
        msg = None
        if type(self) == AbstractException:
            msg = 'Cannot directly initialize an `AbstractException`!'
        if AbstractException in self.__class__.__bases__:
            msg = f'Cannot initialize {type(self)}, because it is a direct child of `AbstractException`!'
        if msg:
            raise NotImplementedError(msg)


class RequestFailed(AbstractException):
    """
    Abstract exception for failing requests.
    """


class SerializationFailed(AbstractException):
    """
    Abstract exception for when serialization fails.
    """


class DeserializationFailed(AbstractException):
    """
    Abstract exception for when deserialization fails.
    """
