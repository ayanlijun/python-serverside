import typing as ty


def middlewareize(name: str, f: ty.Callable) -> ty.Callable:
    async def middleware_function(request, context):
        new_context = await f(request, context)
        setattr(context, name, new_context)
        return context
    return middleware_function


async def run_middleware(request, middleware_list: ty.List, context):
    assert isinstance(middleware_list, list)
    for middleware in middleware_list:
        context = await middleware(request, context)
    return context
