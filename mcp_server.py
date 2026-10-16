import os
from search_policy import validate_policy, eligible, annotate, envelope

from mcp.server.mcpserver import MCPServer

from swipe_queries import listar_categorias_postgres, carregar_swipes_postgres, cards_para_categoria
from search_engine import buscar_swipes as buscar_swipes_engine
from semantic import buscar_swipes_semanticos as semantic_search


mcp = MCPServer(
    "Swipe Brain",
    instructions=(
        "Servidor MCP especializado em swipe files e estruturas de copywriting. "
        "Use as ferramentas para descobrir categorias e encontrar swipes "
        "adequados ao objetivo, emoção e tom do briefing. "
        "Para referências, use record_type=real_piece e apresente título e source_url. "
        "Templates não são anúncios originais. Revise os candidatos antes de adaptar. "
        "Se não houver referência adequada, informe a lacuna. Nunca flexibilize filtros "
        "sem explicar. Similaridade não é prova de relevância ou desempenho. "
        "Use limite entre 1 e 20. Não invente fontes, benefícios ou resultados."
    ),
)


@mcp.tool()
def listar_categorias() -> dict:
    """Lista todas as categorias de swipe files disponíveis."""
    categorias = listar_categorias_postgres()

    return {
        "total": len(categorias),
        "categorias": categorias,
    }


@mcp.tool()
def obter_swipes_categoria(categoria: str, record_type: str = "all") -> dict:
    """Retorna os swipes disponíveis em uma categoria específica."""
    validate_policy(record_type)
    categoria_normalizada = categoria.strip().lower()
    swipes = carregar_swipes_postgres(categoria_normalizada)

    return envelope([annotate(item) for item in swipes if eligible(item, record_type)],
                    categoria=categoria_normalizada, record_type=record_type)



@mcp.tool()
def buscar_swipes(
    categoria: str | None = None,
    objetivo: str | None = None,
    emocao: str | None = None,
    tom: str | None = None,
    limite: int = 5,
    record_type: str = "real_piece",
    match_mode: str = "all",
) -> dict:
    """
    Busca e ranqueia swipes de acordo com o briefing.

    Exige todos os critérios por padrão. match_mode=any permite correspondência parcial explícita.
    record_type=real_piece exige classificação de peça real e fonte; template busca estruturas.
    """
    resultados = buscar_swipes_engine(
        categoria=categoria,
        objetivo=objetivo,
        emocao=emocao,
        tom=tom,
        limite=limite,
        record_type=record_type,
        match_mode=match_mode,
    )

    return envelope(resultados, filters={"categoria": categoria, "objetivo": objetivo,
                    "emocao": emocao, "tom": tom}, record_type=record_type,
                    match_mode=match_mode)


@mcp.tool()
def obter_estrutura_copy_card(categoria: str) -> dict:
    """Retorna cards da categoria usando exclusivamente o PostgreSQL."""
    return cards_para_categoria(categoria)


@mcp.tool()
def buscar_swipes_semanticos(
    consulta: str,
    categoria: str | None = None,
    objetivo: str | None = None,
    emocao: str | None = None,
    tom: str | None = None,
    limite: int = 5,
    record_type: str = "real_piece",
    min_similarity: float | None = None,
) -> dict:
    """Busca por significado com filtros opcionais obrigatórios (AND) e similaridade cosseno.

    Retorna candidatos a revisar, não referências validadas. Limite: 1 a 20.
    min_similarity é opcional e deve ser calibrado; não garante adequação.
    Não usa reranking nesta versão.
    """
    return semantic_search(consulta, categoria, objetivo, emocao, tom, limite,
                           record_type=record_type, min_similarity=min_similarity)


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

