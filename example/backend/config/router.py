from __future__ import annotations
from dataclasses import dataclass
from ariadne import graphql
import ujson
from aiohttp import web
from .schema import schema
from serverside.middleware import run_middleware
from .middleware import actions_middleware, authorize_middleware


cors_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Max-Age": "3600",
    "Access-Control-Allow-Headers": "Content-Type, Accept, X-Requested-With, Authorization, device"
}


@dataclass
class Context:
    name = "context"


async def handle_graphql(request):
    if request.method == "OPTIONS":
        return web.Response(
            content_type="application/json",
            charset="utf-8",
            headers=cors_headers,
            text=ujson.dumps({}),
        )

    try:
        context = await run_middleware(
            request,
            [
                actions_middleware,
                authorize_middleware
            ],
            Context
        )
    except Exception as err:
        return web.Response(
            content_type="application/json",
            charset="utf-8",
            headers=cors_headers,
            text=ujson.dumps({"error": err}),
        )
    json_data = await request.json()
    success, result = await graphql(schema, json_data, context_value=context)
    return web.Response(
        content_type="application/json",
        charset="utf-8",
        headers=cors_headers,
        text=ujson.dumps(result),
    )


async def handle_hello(request):
    return web.Response(
        content_type="application/json",
        charset="utf-8",
        headers=cors_headers,
        text=ujson.dumps({"Hello": "World!"})
    )
