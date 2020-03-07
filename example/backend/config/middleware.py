from serverside.middleware import middlewareize
from serverside.graphql.ariadne.extractors import extract_actions_from_query
from apps.users.models import User


async def actions(request, context):
    data = await request.json()
    query = data.get("query").strip()
    actions = extract_actions_from_query(query)
    return actions


async def authorize(request, context):
    needs_authentication = False
    for action in context.actions:
        if action == "IntrospectionQuery":
            break
        if action not in []:
            needs_authentication = True

    user = None
    if needs_authentication is True:
        authentication_token = request.headers.get("Authorization")
        if not authentication_token:
            raise Exception("No token in request!")
        user = User.authenticate(token=authentication_token)
    return user


actions_middleware = middlewareize("actions", actions)
authorize_middleware = middlewareize("user", authorize)
