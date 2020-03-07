import typing as ty
import ariadne
from django.conf import settings
from .django_models import (
    django_get_one, django_get_many,
    django_create, django_update, django_delete
)


class BaseResolver:

    @classmethod
    def export_resolvers(cls):
        return[getattr(cls, var) for var in vars(cls) if isinstance(getattr(cls, var), ariadne.objects.ObjectType)]

    @classmethod
    def auto_cruderize(cls):
        """ This function will detect which crud operations the resolver
            wants to be automatically handled, and then set them.
        """
        ac = cls.Meta.auto_crud

        if ac.count:
            @settings.QUERY.field(ac.count)
            async def func(*args, **kwargs):
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
