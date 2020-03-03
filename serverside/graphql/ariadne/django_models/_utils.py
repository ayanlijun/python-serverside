import typing as ty
import inflection
from collections import OrderedDict


def recursive_snake2camel(d: ty.Dict):
    new = {}
    for k, v in d.items():
        if isinstance(v, OrderedDict):
            v = recursive_snake2camel(v)
        if isinstance(v, list):
            v = [recursive_snake2camel(i) if isinstance(i, OrderedDict) else i for i in v]
        new[inflection.camelize(k, False)] = v
    return new


def recursive_camel2snake(d: ty.Dict):
    new = {}
    for k, v in d.items():
        if isinstance(v, OrderedDict):
            v = recursive_camel2snake(v)
        if isinstance(v, list):
            v = [recursive_camel2snake(i) if isinstance(i, OrderedDict) else i for i in v]
        new[inflection.underscore(k)] = v
    return new
