import os

from mcp.server.mcpserver import MCPServer

from swipes_db import SWIPES_DB
from search_engine import buscar_swipes as buscar_swipes_engine


mcp = MCPServer(
    "Swipe Brain",
    instructions=(
        "Servidor MCP especializado em swipe files e estruturas de copywriting. "
        "Use as ferramentas para descobrir categorias e encontrar swipes "
        "adequados ao objetivo, emoção e tom do briefing."
    ),
)


@mcp.tool()
def listar_categorias() -> dict:
    """Lista todas as categorias de swipe files disponíveis."""
    categorias = sorted(SWIPES_DB.keys())

    return {
        "total": len(categorias),
        "categorias": categorias,
    }


@mcp.tool()
def obter_swipes_categoria(categoria: str) -> dict:
    """Retorna os swipes disponíveis em uma categoria específica."""
    categoria_normalizada = categoria.strip().lower()
    swipes = SWIPES_DB.get(categoria_normalizada, [])

    return {
        "categoria": categoria_normalizada,
        "total": len(swipes),
        "items": swipes,
    }


@mcp.tool()
def buscar_swipes(
    categoria: str | None = None,
    objetivo: str | None = None,
    emocao: str | None = None,
    tom: str | None = None,
    limite: int = 5,
) -> dict:
    """
    Busca e ranqueia swipes de acordo com o briefing.

    Pode filtrar por categoria, objetivo, emoção e tom.
    """
    resultados = buscar_swipes_engine(
        categoria=categoria,
        objetivo=objetivo,
        emocao=emocao,
        tom=tom,
        limite=limite,
    )

    return {
        "filters": {
            "categoria": categoria,
            "objetivo": objetivo,
            "emocao": emocao,
            "tom": tom,
        },
        "total": len(resultados),
        "items": resultados,
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
    )
