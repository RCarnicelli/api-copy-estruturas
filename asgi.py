from contextlib import asynccontextmanager

from asgiref.wsgi import WsgiToAsgi
from starlette.applications import Starlette
from starlette.routing import Mount

from main import app as flask_app
from mcp_server import mcp
from init_db import init_database

# Converte a aplicação Flask existente de WSGI para ASGI.
flask_asgi = WsgiToAsgi(flask_app)

# Aplicação MCP em Streamable HTTP.
mcp_app = mcp.streamable_http_app(
    streamable_http_path="/",
    json_response=True,
    stateless_http=True,
    host="0.0.0.0",
)

@asynccontextmanager
async def lifespan(app):
    init_database()
    async with mcp.session_manager.run():
        yield


# Uma única aplicação pública:
# /mcp  -> MCP
# /*    -> API REST Flask existente
app = Starlette(
    routes=[
        Mount("/mcp", app=mcp_app),
        Mount("/", app=flask_asgi),
    ],
    lifespan=lifespan,
)
