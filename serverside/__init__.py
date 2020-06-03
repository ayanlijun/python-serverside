import typing as ty
from .graphql.ariadne import BaseResolver
name = "serverside"


class State:

    def __init__(self):
        self.resolver_dependencies = {}

    def assign(self, key: ty.Any, value: ty.Any) -> None:
        setattr(self, key, value)

    def assign_resolver_field_dependencies(self, resolvers: ty.List[BaseResolver]) -> None:
        for Resolver in resolvers:
            try:
                resolver_model = Resolver.Model
                field_dependencies = Resolver.Meta.field_dependencies
                if resolver_model.__name__ not in self.resolver_dependencies:
                    self.resolver_dependencies[resolver_model.__name__] = {}
                for fdk, fdv in field_dependencies.items():
                    self.resolver_dependencies[resolver_model.__name__][fdk] = fdv
            except KeyError:
                continue
