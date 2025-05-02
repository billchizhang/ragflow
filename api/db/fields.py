"""Custom field types for SQLAlchemy models.

This module provides custom field types for SQLAlchemy models,
including JSON and List types with mutation tracking.
"""

import json
import pickle
from enum import Enum

from sqlalchemy import TypeDecorator, Text
from sqlalchemy.ext.mutable import Mutable


class SerializedFieldType(Enum):
    """Enum for serialization types."""
    JSON = 'json'
    PICKLE = 'pickle'


class MutableDict(Mutable, dict):
    """Mutable dictionary type for SQLAlchemy.
    
    This class enables tracking dictionary changes for SQLAlchemy.
    When a dictionary is modified, SQLAlchemy will know to update the database.
    """
    @classmethod
    def coerce(cls, key, value):
        """Convert plain dictionaries to MutableDict."""
        if value is None:
            return None
        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)
            return Mutable.coerce(key, value)
        return value

    def __setitem__(self, key, value):
        """Track when a key is set."""
        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        """Track when a key is deleted."""
        dict.__delitem__(self, key)
        self.changed()
    
    def update(self, *args, **kwargs):
        """Track when the dictionary is updated."""
        dict.update(self, *args, **kwargs)
        self.changed()
    
    def clear(self):
        """Track when the dictionary is cleared."""
        dict.clear(self)
        self.changed()
    
    def pop(self, *args, **kwargs):
        """Track when an item is popped."""
        result = dict.pop(self, *args, **kwargs)
        self.changed()
        return result


class MutableList(Mutable, list):
    """Mutable list type for SQLAlchemy.
    
    This class enables tracking list changes for SQLAlchemy.
    When a list is modified, SQLAlchemy will know to update the database.
    """
    @classmethod
    def coerce(cls, key, value):
        """Convert plain lists to MutableList."""
        if value is None:
            return None
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        return value

    def __setitem__(self, key, value):
        """Track when an item is set."""
        list.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        """Track when an item is deleted."""
        list.__delitem__(self, key)
        self.changed()
    
    def append(self, item):
        """Track when an item is appended."""
        list.append(self, item)
        self.changed()
    
    def extend(self, other):
        """Track when the list is extended."""
        list.extend(self, other)
        self.changed()
    
    def insert(self, index, item):
        """Track when an item is inserted."""
        list.insert(self, index, item)
        self.changed()
    
    def pop(self, *args, **kwargs):
        """Track when an item is popped."""
        result = list.pop(self, *args, **kwargs)
        self.changed()
        return result
    
    def remove(self, item):
        """Track when an item is removed."""
        list.remove(self, item)
        self.changed()
    
    def clear(self):
        """Track when the list is cleared."""
        list.clear(self)
        self.changed()


class JSONType(TypeDecorator):
    """JSON field type for SQLAlchemy.
    
    This type stores data as JSON in the database.
    """
    impl = Text
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def process_bind_param(self, value, dialect):
        """Convert Python object to JSON string for storage."""
        if value is None:
            return None
        return json.dumps(value)
    
    def process_result_value(self, value, dialect):
        """Convert JSON string to Python object when loaded."""
        if value is None:
            return {}
        return json.loads(value)


class ListType(JSONType):
    """List field type for SQLAlchemy.
    
    This type stores lists as JSON in the database.
    """
    def process_result_value(self, value, dialect):
        """Convert JSON string to Python list when loaded."""
        if value is None:
            return []
        return json.loads(value)


# Register types with SQLAlchemy mutable extension
MutableJSON = MutableDict.as_mutable(JSONType)
MutableList = MutableList.as_mutable(ListType) 