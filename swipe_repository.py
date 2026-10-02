import os
import uuid
import psycopg


def salvar_swipe(classificacao):
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada.")

    swipe_id = f"swipe_{uuid.uuid4().hex[:12]}"
    source_url = classificacao.get("source_url")

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                "SELECT id FROM swipes WHERE source_url = %s LIMIT 1;",
                (source_url,)
            )
            existente = cursor.fetchone()

            if existente:
                return existente[0]

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
                    raw_content
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s
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
                ),
            )

            id_salvo = cursor.fetchone()[0]

        conn.commit()

    return id_salvo
