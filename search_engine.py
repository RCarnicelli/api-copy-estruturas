from swipe_queries import carregar_swipes_postgres
from search_policy import normalize, category, validate_policy, eligible, annotate

def _carregar_swipes_postgres():
    """Carrega os swipes diretamente do PostgreSQL."""
    return carregar_swipes_postgres()


def _normalizar(valor):
    """Normaliza valores recebidos para comparação."""
    return normalize(valor)


def _contem(lista, valor):
    """Verifica se um valor aparece em uma lista de atributos."""
    valor = _normalizar(valor)

    if not valor:
        return False

    return any(_normalizar(item) == valor for item in (lista or []))


def buscar_swipes(
    categoria=None,
    objetivo=None,
    emocao=None,
    tom=None,
    limite=5,
    record_type="all",
    match_mode="all",
):
    """
    Busca e ranqueia swipes de acordo com o briefing.

    Pontuação:
    categoria = 4 pontos
    objetivo  = 3 pontos
    emoção    = 2 pontos
    tom       = 2 pontos
    """

    if isinstance(limite, (bool, float)):
        raise ValueError("O limite deve ser de 1 a 20")
    try:
        limite = int(limite)
    except (TypeError, ValueError):
        raise ValueError("O limite deve ser de 1 a 20") from None
    if not 1 <= limite <= 20:
        raise ValueError("O limite deve ser de 1 a 20")

    validate_policy(record_type, match_mode)
    categoria = category(categoria)
    objetivo = _normalizar(objetivo)
    emocao = _normalizar(emocao)
    tom = _normalizar(tom)

    resultados = []

    swipes_postgres = _carregar_swipes_postgres()

    for swipe in swipes_postgres:
        if not eligible(swipe, record_type):
            continue
        score = 0
        motivos = []

        if categoria and category(swipe.get("category")) == categoria:
            score += 4
            motivos.append("categoria")

        if objetivo and _contem(swipe.get("objective", []), objetivo):
            score += 3
            motivos.append("objetivo")

        if emocao and _contem(swipe.get("emotion", []), emocao):
            score += 2
            motivos.append("emocao")

        if tom and _contem(swipe.get("tone", []), tom):
            score += 2
            motivos.append("tom")

        # Sem filtros, todos podem aparecer.
        # Todos os critérios são exigidos; correspondência parcial requer match_mode=any.
        filtros_usados = any([categoria, objetivo, emocao, tom])

        required = sum(bool(v) for v in (categoria, objetivo, emocao, tom))
        accepted = len(motivos) == required if match_mode == "all" else score > 0
        if not filtros_usados or accepted:
            resultado = annotate(swipe)
            resultado["category"] = swipe.get("category")
            resultado["score"] = score
            resultado["matched_by"] = motivos
            resultado["unmatched_filters"] = [k for k, v in (("categoria", categoria), ("objetivo", objetivo), ("emocao", emocao), ("tom", tom)) if v and k not in motivos]
            resultados.append(resultado)

    resultados.sort(
        key=lambda item: (
            item["score"],
            len(item.get("matched_by", []))
        ),
        reverse=True
    )

    return resultados[:limite]
