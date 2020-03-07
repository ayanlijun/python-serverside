from aiohttp import web
from .router import handle_graphql, handle_hello
from serverside.server_side_events import ServerSideEvents

server_side_events = ServerSideEvents(
    cors_headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Max-Age": "3600",
        "Access-Control-Allow-Headers": "Content-Type, Accept, X-Requested-With, Authorization, device"
    }
)

routes = [
    web.get("/sse", server_side_events.get_system_info),
    web.get("/hello", handle_hello),
    web.options("/graphql", handle_graphql),
    web.post("/graphql", handle_graphql)
]
