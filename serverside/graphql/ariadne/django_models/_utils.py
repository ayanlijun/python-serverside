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


def input2snake_input(Model: models.Model, input: ty.Dict) -> ty.Dict:
    snake_input = recursive_camel2snake(input)
    for field in Model._meta.get_fields():
        if isinstance(field, models.fields.related.ForeignKey):
            try:
                fk_id = snake_input.pop(field.name)
                if field.name not in snake_input:
                    snake_input[field.name] = None
                snake_input[field.name] = fk_id
            except KeyError:
                continue  # Foreign key wasn't supplied to be updated
        elif isinstance(field, models.ManyToManyField):
            try:
                m2m_ids = snake_input.pop(field.name)
                if field.name not in snake_input:
                    snake_input[field.name] = []
                snake_input[field.name].extend(m2m_ids)
            except KeyError:
                continue  # Many2Many id's were not supplied to be updated
    return snake_input
