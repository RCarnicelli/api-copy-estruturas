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

@mcp.tool()
def obter_estrutura_copy_card(categoria: str) -> dict:
    """
    Retorna estruturas de copy em formato de cards para uma categoria.
    Para 'advice', consulta o Swipefile.
    Para as demais categorias, usa a base local do Swipe Brain.
    """
    categoria_normalizada = categoria.strip().lower()

    if not categoria_normalizada:
        return {
            "erro": "Categoria não informada"
        }

    if categoria_normalizada == "advice":
        try:
            import requests
            from bs4 import BeautifulSoup

            url = f"https://swipefile.com/category/{categoria_normalizada}"
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                return {
                    "erro": "Não foi possível acessar a categoria externa"
                }

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.find_all("h2")
            descricoes = soup.find_all("p")

            if not cards:
                return {
                    "erro": "Estrutura da página não reconhecida ou vazia"
                }

            swipes = []

            for i in range(min(3, len(cards))):
                titulo = (
                    cards[i].get_text(strip=True)
                    if cards[i]
                    else "Sem título"
                )

                descricao = (
                    descricoes[i].get_text(strip=True)
                    if i < len(descricoes)
                    else "Swipe sem descrição."
                )

                swipes.append({
                    "title": titulo,
                    "description": descricao,
                    "button": {
                        "text": "Usar esta estrutura",
                        "action": "usarSwipe"
                    }
                })

            return {
                "type": "cards",
                "title": (
                    f"Melhores Estruturas para "
                    f"{categoria_normalizada.capitalize()}"
                ),
                "items": swipes
            }

        except Exception as e:
            return {
                "erro": f"Erro ao buscar estruturas: {str(e)}"
            }

    itens = SWIPES_DB.get(categoria_normalizada, [])

    return {
        "type": "cards",
        "title": f"Estrutura sugerida para {categoria_normalizada}",
        "items": itens
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
