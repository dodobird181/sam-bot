from __future__ import annotations

import json
import sys
import uuid
from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any, Dict, List

import settings
from applogging import logger


class DatabaseNotInitializedError(Exception):
    """
    The database wansn't initialized before being used. Please
    initialize it by calling `init_db_at` before calling `load` and `save` methods.
    """


class ObjectBase(ABC):

    _IS_DB_INITIALIZED = False

    def __init__(self):
        self.id = str(uuid.uuid4())

    def __str__(self):
        id_dict = {'id': self.id[:4] + '..'}
        classname = self.__class__.__name__
        return f'[{classname} - {str(id_dict|self.to_dict())}]'

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Implementations of this method should return a dictionary representation
        of all the object data that needs to be saved locally.
        """
        ...

    def _to_dict_with_id(self) -> Dict[str, Any]:
        """
        Returns the internal dictionary representation of this object to save.
        """
        return {'id': self.id} | self.to_dict()

    @abstractclassmethod
    def from_dict(cls, dict: Dict[str, Any]) -> ObjectBase:
        """
        Implementations of this method should return an instance of `ObjectBase`
        by using the data in the given dictionary.
        """
        ...

    @classmethod
    def _from_dict_with_id(cls, dict) -> Dict[str, Any]:
        """
        Returns an instance of `ObjectBase` from a dictionary, and injects
        the id in the dictionary into the object's id field.
        """
        obj = cls.from_dict(dict)
        obj.id = dict['id']
        return obj

    def save(self, path: str) -> None:
        """
        Saves the object data in JSON format to the given filepath.
        """
        logger().debug(f'Saving file: {path}..')
        if self._IS_DB_INITIALIZED:
            write_dict_to_json_file(path, self._to_dict_with_id())
            return None
        raise DatabaseNotInitializedError
    
    @classmethod
    def load(cls, path: str) -> ObjectBase:
        """
        Load an instance of the object from the given filepath.
        """
        logger().debug(f'Loading file: {path}..')
        if cls._IS_DB_INITIALIZED:
            dict = read_dict_from_json_file(path)
            obj = cls._from_dict_with_id(dict)
            return obj
        raise DatabaseNotInitializedError
    

class ObjectCollection(ObjectBase):
    """
    A collection of database objects.
    """
    def __init__(self, object_class, *objects: ObjectBase):
        super().__init__()
        self.object_class = object_class.__name__
        self.objects = {str(obj.id): obj for obj in objects}
        self.size = len(self.objects)

    def __str__(self):
        desc = self._to_dict_with_id()
        desc.pop('objects')
        s = f'[{self.__class__.__name__} - {str(desc)}\n'
        for obj in self.objects.values():
            s += f'    {str(obj)}\n'
        s += ']'
        return s
    
    def __iter__(self):
        return self.objects.values().__iter__()
    
    def __next__(self):
        return self.objects.values().__next__()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'size': self.size,
            'object_class': str(self.object_class),
            'objects': [obj._to_dict_with_id() for obj in self.objects.values()]}
    
    @classmethod
    def from_dict(self, dict) -> ObjectCollection:
        object_class = eval(dict['object_class'])
        objects = [object_class._from_dict_with_id(obj) for obj in dict['objects']]
        return ObjectCollection(object_class, *objects)
    
    @classmethod
    def load(cls, path) -> ObjectCollection:
        return super().load(path)
    
    def add(self, obj: ObjectBase) -> ObjectCollection:
        """
        Add an element to the collection.
        """
        self.objects[obj.id] = obj
        self.size += 1
        return self
    
    def add_all(self, *objects: ObjectBase) -> ObjectCollection:
        """
        Add multiple elements to the collection.
        """
        for obj in objects:
            self.add(obj)
        return self
    
    def remove(self, id: str) -> ObjectCollection:
        """
        Remove an element by id from the collection.
        """
        self.objects.pop(id)
        return self
    
    def get(self, id: str) -> ObjectBase:
        """
        Get an element by id from the collection.
        """
        return self.objects.get(id)
    
    def get_first(self) -> ObjectBase:
        """
        Get the first element in the collection.
        """
        for key in self.objects.keys():
            return self.objects[key]
        
    def as_list(self) -> List[ObjectBase]:
        """
        Get all elements in the collection as a list.
        """
        return list(self.objects.values())


def get_json_path(path: str) -> str:
    if path[-5:] != '.json':
        return path + '.json'
    return path


def write_dict_to_json_file(path: str, dict: Dict[str, Any]) -> None:
    with open(get_json_path(settings.ROOT_DB_PATH + path), 'w') as file:
        file.write(json.dumps(dict, indent=4))


def read_dict_from_json_file(path: str) -> Dict[str, Any]:
    with open(get_json_path(settings.ROOT_DB_PATH + path), 'r') as file:
        return dict(json.load(file))


def import_class(cls):
    __import__(cls.__module__, globals(), locals(), [cls.__name__,])
    globals().update({cls.__name__: getattr(sys.modules[cls.__module__], cls.__name__)})


def init_db() -> None:
    """
    Initialize the database at the given root directory. All database paths
    are interpreted as relative to the root directory passed in here.
    """
    logger().debug(f'Initializing database at: "{settings.ROOT_DB_PATH}"..')
    ObjectBase._IS_DB_INITIALIZED = True
    for cls in ObjectBase.__subclasses__():
        logger().debug(f'Importing class: {cls.__name__}')
        import_class(cls)
    logger().debug('Finished initializing the database!')
