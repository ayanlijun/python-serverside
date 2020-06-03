import typing as ty

import inflection
import ariadne
from django.db import models
from django.contrib.postgres.fields import JSONField as PostgresJSONField
from django.conf import settings
from .django_models import (
    django_get_one, django_get_many,
    django_create, django_update, django_delete
)
from ...django.fields import S3Field


class BaseResolver:

    @classmethod
    def export_resolvers(cls):
        return[getattr(cls, var) for var in vars(cls) if isinstance(getattr(cls, var), ariadne.objects.ObjectType)]

    @classmethod
    def assign_m2m(cls, camel_field_name: str, field_name: str) -> None:
        @cls.OBJECT.field(camel_field_name)
        def resolve(obj, *args, **kwargs):
            return getattr(obj, f"m2m_{field_name}", None)
        setattr(cls, f"resolve_{cls._objectname}_{field_name}", staticmethod(resolve))

    @classmethod
    def assign_camel_to_snake_resolver(cls, camel_field_name: str, snake_field_name: str) -> None:
        @cls.OBJECT.field(camel_field_name)
        def resolve(obj, *args, **kwargs):
            return getattr(obj, snake_field_name, None)
        setattr(cls, f"resolve_{cls._objectname}_{snake_field_name}", staticmethod(resolve))

    @classmethod
    def auto_cruderize(cls):
        """ This function will detect which crud operations the resolver
            wants to be automatically handled, and then set them.
        """

        # The following will automatically add resolvers for fields that were
        # calculated using Prefetch, for optimal db performance, assuming the decorate @objecttype was used (./decorators.py)
        if getattr(cls, "OBJECT", None) is not None:
            ignore_fields = [f.field_name for f in getattr(cls.Meta, "ignore_fields", [])]
            for field in cls.Meta.model._meta.get_fields():
                camel_field_name = inflection.camelize(field.name, False)
                if isinstance(field, models.fields.related.ManyToManyField):
                    cls.assign_m2m(camel_field_name, field.name)
                    continue
                elif isinstance(field, (
                    models.CharField, models.TextField, models.IntegerField, models.FloatField, models.BooleanField,
                    models.FloatField, PostgresJSONField
                )):
                    if field.name in ignore_fields:
                        continue
                    elif isinstance(field, S3Field):
                        continue
                    if camel_field_name != field.name:
                        cls.assign_camel_to_snake_resolver(camel_field_name, field.name)

        ac = cls.Meta.auto_crud

        if ac.count:
            @settings.QUERY.field(ac.count)
            async def func(*args, **kwargs):
                print("queza")
                return cls.Meta.model.objects.all().count()
            setattr(cls, "resolve_count", staticmethod(func))

        if ac.get_one:
            @settings.QUERY.field(ac.get_one)
            async def func(_, info, id: str):
                return await django_get_one(info, cls.Meta.model, id)
            setattr(cls, "resolve_get", staticmethod(func))

        if ac.get_many:
            @settings.QUERY.field(ac.get_many)
            async def func(_, info, *args, **kwargs):
                return await django_get_many(info, cls.Meta.model, ac.get_many, kwargs)
            setattr(cls, "resolve_list", staticmethod(func))

        if ac.create:
            @settings.MUTATION.field(ac.create)
            async def func(_, info, input: ty.Dict):
                return await django_create(info, input, cls.Meta.model, cls.Meta.uid_gen)
            setattr(cls, "resolve_create", staticmethod(func))

        if ac.update:
            @settings.MUTATION.field(ac.update)
            async def func(_, info, id: str, prevUpdated: float, input: ty.Dict):
                return await django_update(info, cls.Meta.model, id, prevUpdated, input)
            setattr(cls, "resolve_update", staticmethod(func))

        if ac.delete:
            @settings.MUTATION.field(ac.delete)
            async def func(_, info, id):
                return await django_delete(info, cls.Meta.model, id)
            setattr(cls, "resolve_delete", staticmethod(func))
