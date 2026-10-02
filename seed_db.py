import os
import psycopg
from swipes_db import SWIPES_DB


def seed_database():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada.")

    total_processados = 0

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:

            for categoria, swipes in SWIPES_DB.items():
                for swipe in swipes:

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
                            when_to_use,
                            tags
                        )
                        VALUES (
                            %s, %s, %s, %s, %s,
                            %s, %s, %s, %s, %s,
                            %s, %s, %s
                        )
                        ON CONFLICT (id) DO UPDATE SET
                            category = EXCLUDED.category,
                            title = EXCLUDED.title,
                            description = EXCLUDED.description,
                            framework = EXCLUDED.framework,
                            objective = EXCLUDED.objective,
                            emotion = EXCLUDED.emotion,
                            tone = EXCLUDED.tone,
                            hook = EXCLUDED.hook,
                            mechanism = EXCLUDED.mechanism,
                            cta = EXCLUDED.cta,
                            when_to_use = EXCLUDED.when_to_use,
                            tags = EXCLUDED.tags,
                            updated_at = NOW()
                        """,
                        (
                            swipe["id"],
                            categoria,
                            swipe["title"],
                            swipe["description"],
                            swipe.get("framework"),
                            swipe.get("objective", []),
                            swipe.get("emotion", []),
                            swipe.get("tone", []),
                            swipe.get("hook"),
                            swipe.get("mechanism"),
                            swipe.get("cta"),
                            swipe.get("when_to_use"),
                            swipe.get("tags", []),
                        ),
                    )

                    total_processados += 1

        conn.commit()

    print(f"Seed concluído. {total_processados} swipes processados.")


if __name__ == "__main__":
    seed_database()
