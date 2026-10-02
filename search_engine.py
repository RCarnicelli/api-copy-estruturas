import os
import psycopg
from psycopg.rows import dict_row

def _carregar_swipes_postgres():
    """Carrega os swipes diretamente do PostgreSQL."""
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada")

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM swipes ORDER BY id;")
            return cursor.fetchall()


def _normalizar(valor):
    """Normaliza valores recebidos para comparação."""
    if not valor:
        return ""
    return str(valor).strip().lower()


def _contem(lista, valor):
    """Verifica se um valor aparece em uma lista de atributos."""
    valor = _normalizar(valor)

    if not valor:
        return False

    return any(_normalizar(item) == valor for item in lista)


def buscar_swipes(
    categoria=None,
    objetivo=None,
    emocao=None,
    tom=None,
    limite=5
):
    """
    Busca e ranqueia swipes de acordo com o briefing.

    Pontuação:
    categoria = 4 pontos
    objetivo  = 3 pontos
    emoção    = 2 pontos
    tom       = 2 pontos
    """

    categoria = _normalizar(categoria)
    objetivo = _normalizar(objetivo)
    emocao = _normalizar(emocao)
    tom = _normalizar(tom)

    resultados = []

    swipes_postgres = _carregar_swipes_postgres()

  for swipe in swipes_postgres:
            score = 0
            motivos = []

            if categoria and _normalizar(swipe.get("category")) == categoria:
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
            # Com filtros, só entram resultados com alguma compatibilidade.
            filtros_usados = any([categoria, objetivo, emocao, tom])

            if not filtros_usados or score > 0:
                resultado = dict(swipe)
                resultado["category"] = nome_categoria
                resultado["score"] = score
                resultado["matched_by"] = motivos
                resultados.append(resultado)

    resultados.sort(
        key=lambda item: (
            item["score"],
            len(item.get("matched_by", []))
        ),
        reverse=True
    )

    try:
        limite = int(limite)
    except (TypeError, ValueError):
        limite = 5

    limite = max(1, min(limite, 20))

    return resultados[:limite]
