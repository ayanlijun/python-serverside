import typing as ty
import inflection
from collections import OrderedDict

from django.db import models


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


def mutation_input2snake_input(Model: models.Model, input: ty.Dict) -> ty.Tuple[ty.Dict, ty.Dict]:
    snake_input = recursive_camel2snake(input)
    m2m_context = {}
    for field in Model._meta.get_fields():
        if isinstance(field, models.fields.related.ForeignKey):
            pass
        elif isinstance(field, models.ManyToManyField):
            try:
                m2m_context[field.name] = snake_input.pop(field.name)
            except KeyError:
                continue
    return snake_input, m2m_context
