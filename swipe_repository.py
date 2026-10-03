import os
import uuid
import psycopg
from contextlib import contextmanager
from psycopg.types.json import Jsonb
from classification_contract import validate_classification
from crawler import canonicalizar_swipe_url


def _url_canonica(url):
    return canonicalizar_swipe_url(url) or url


def _buscar_existente(cursor, source_url):
    cursor.execute("SELECT id, source_url FROM swipes WHERE source_url IS NOT NULL;")
    canonical = _url_canonica(source_url)
    for swipe_id, saved_url in cursor.fetchall():
        if _url_canonica(saved_url) == canonical:
            return swipe_id
    return None


def buscar_swipe_por_url(source_url):
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada")
    with psycopg.connect(database_url, connect_timeout=10) as conn:
        with conn.cursor() as cursor:
            return _buscar_existente(cursor, source_url)


@contextmanager
def bloquear_ingestao():
    """One paid ingestion at a time across processes, released even on failure."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada")
    with psycopg.connect(database_url, autocommit=True, connect_timeout=10) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT pg_try_advisory_lock(741281003);")
            acquired = cursor.fetchone()[0]
            try:
                yield acquired
            finally:
                if acquired:
                    cursor.execute("SELECT pg_advisory_unlock(741281003);")


def salvar_swipe(classificacao):
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada.")

    swipe_id = f"swipe_{uuid.uuid4().hex[:12]}"
    source_url = _url_canonica(classificacao.get("source_url"))
    if not source_url:
        raise ValueError("source_url obrigatória para salvar um swipe")

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:

            # Serialize writers for this canonical URL without changing existing data.
            cursor.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0));", (source_url,))
            existente = _buscar_existente(cursor, source_url)

            if existente:
                return existente

            validate_classification(classificacao)
            cursor.execute(
                """
                INSERT INTO swipes (
                    id,
                    category,
                    title,
                    description,
                    framework,
                    objective,
                    emotion,
                    tone,
                    hook,
                    mechanism,
                    cta,
                    why_it_works,
                    adaptation,
                    tags,
                    source_url,
                    raw_content,
                    taxonomy
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id;
                """,
                (
                    swipe_id,
                    classificacao.get("category") or "uncategorized",
                    classificacao.get("title") or "Swipe sem título",
                    classificacao.get("description"),
                    classificacao.get("framework"),
                    classificacao.get("objective", []),
                    classificacao.get("emotion", []),
                    classificacao.get("tone", []),
                    classificacao.get("hook"),
                    classificacao.get("mechanism"),
                    classificacao.get("cta"),
                    classificacao.get("why_it_works"),
                    classificacao.get("adaptation"),
                    classificacao.get("tags", []),
                    source_url,
                    classificacao.get("original_content"),
                    Jsonb(classificacao["taxonomy"]),
                ),
            )

            id_salvo = cursor.fetchone()[0]

        conn.commit()

    return id_salvo
