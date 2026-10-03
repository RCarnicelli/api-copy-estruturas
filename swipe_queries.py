"""Shared PostgreSQL read model for REST, MCP and briefing search."""
import os
from datetime import date, datetime

import psycopg
from psycopg.rows import dict_row


class SwipeReadError(RuntimeError):
    pass


# Explicit existing read fields preserve the former search result contract.
# Embeddings are only returned as stored; generation/search is outside this stage.
PUBLIC_COLUMNS = """id, category, title, description, framework, objective,
emotion, tone, hook, mechanism, cta, why_it_works, adaptation, when_to_use,
tags, source_url, source_name, raw_content, embedding, created_at, updated_at"""


def _query(sql, parameters=()):
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SwipeReadError("PostgreSQL indisponível para consulta")
    try:
        with psycopg.connect(database_url, row_factory=dict_row, connect_timeout=10,
                             options="-c statement_timeout=15000 -c default_transaction_read_only=on") as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, parameters)
                return cursor.fetchall()
    except Exception:
        raise SwipeReadError("PostgreSQL indisponível para consulta") from None


def normalizar_categoria(categoria):
    return str(categoria or "").strip().lower()


def _public_swipe(row):
    item = dict(row)
    # Preserve the legacy key, but vectors belong in PostgreSQL, not tool context.
    if "embedding" in item:
        item["embedding"] = None
    item["category"] = normalizar_categoria(item.get("category"))
    for field in ("objective", "emotion", "tone", "tags"):
        item[field] = item.get(field) or []
    for field in ("created_at", "updated_at"):
        value = item.get(field)
        if isinstance(value, (date, datetime)):
            item[field] = value.isoformat()
    item["button"] = {"text": "Usar esta estrutura", "action": "usarSwipe"}
    return item


def listar_categorias_postgres():
    rows = _query("""SELECT DISTINCT lower(btrim(category)) AS category
                     FROM swipes WHERE category IS NOT NULL AND btrim(category) <> ''
                     ORDER BY category;""")
    return [row["category"] for row in rows]


def carregar_swipes_postgres(categoria=None):
    sql = f"SELECT {PUBLIC_COLUMNS} FROM swipes"
    parameters = ()
    if categoria is not None:
        categoria = normalizar_categoria(categoria)
        if not categoria:
            return []
        sql += " WHERE lower(btrim(category)) = %s"
        parameters = (categoria,)
    sql += " ORDER BY id;"
    return [_public_swipe(row) for row in _query(sql, parameters)]


def cards_para_categoria(categoria):
    categoria = normalizar_categoria(categoria)
    if not categoria:
        return {"erro": "Categoria não informada"}
    items = carregar_swipes_postgres(categoria)
    if categoria == "advice":
        return {"type": "cards", "title": f"Melhores Estruturas para {categoria.capitalize()}",
                "items": items[:3]}
    return {"type": "cards", "title": f"Estrutura sugerida para {categoria}", "items": items}
