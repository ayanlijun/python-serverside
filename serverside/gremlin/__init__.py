import typing as ty
from datetime import datetime


class Property:

    def __init__(self, name: str, default: ty.Any, type: type, description: str = None):
        self.__type_check_name(name)
        self.name = name
        self.default = default
        self.type = type
        self.description = description

    def __str__(self):
        return self.name

    def __type_check_name(self, name: str):
        assert isinstance(name, str)

    def __type_check_description(self, description: str):
        assert isinstance(description, str)


class StringProperty(Property):

    def __init__(self, name: str, default: str = None, description: str = None):
        super(StringProperty, self).__init__(name=name, default=default, type=str, description=description)


class IntegerProperty(Property):

    def __init__(self, name: str, default: int = None, description: str = None):
        super(IntegerProperty, self).__init__(name=name, default=default, type=int, description=description)


class FloatProperty(Property):

    def __init__(self, name: str, default: float = None, description: str = None):
        super(FloatProperty, self).__init__(name=name, default=default, type=float, description=description)


class UIDProperty(Property):

    def __init__(self, name: str, default: str = None, description: str = None):
        super(UIDProperty, self).__init__(name=name, default=default, type=str, description=description)


class DatetimeProperty(Property):

    def __init__(self, name: str, default: datetime = None, description: str = None):
        super(DatetimeProperty, self).__init__(name=name, default=default, type=datetime, description=description)


class ArrayProperty(Property):

    def __init__(self, name: str, value_type: type, default: ty.List[str] = [], description: str = None):
        super(ArrayProperty, self).__init__(name=name, default=default, type=list, description=description)


class ArrayOfDictProperty(Property):

    def __init__(self, name: str, default: ty.List[ty.Dict] = None, description: str = None):
        super(ArrayOfDictProperty, self).__init__(name=name, default=default, type=datetime, description=description)


def label(label: str):
    def wrapper(wrapped):
        setattr(wrapped, "label", label)
        return wrapped
    return wrapper


class Vertex:

    def __init__(self, *args, **kwargs):
        raise NotImplementedError


class Edge:

    def __init__(self, *args, **kwargs):
        raise NotImplementedError
