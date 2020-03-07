import ariadne
from django.conf import settings
from serverside.graphql.ariadne.scalars import datetime_scalar
from serverside.graphql.ariadne.relay import relay_node
from serverside.graphql.ariadne.helpers import combine_resolvers
from apps.users.resolvers import export_resolvers as er1


resolvers = combine_resolvers([er1])

schema = open("/srv/config/schema.graphql", "r").read()
schema = ariadne.make_executable_schema(
    schema,
    [
        settings.QUERY,
        settings.MUTATION,
        relay_node,
        datetime_scalar,
        *resolvers
    ]
)
