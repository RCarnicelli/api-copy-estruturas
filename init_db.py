import os
import psycopg


def init_database():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada.")

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS swipes (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    framework TEXT,
                    objective TEXT[],
                    emotion TEXT[],
                    tone TEXT[],
                    hook TEXT,
                    mechanism TEXT,
                    cta TEXT,
                    when_to_use TEXT,
                    tags TEXT[],
                    source_url TEXT,
                    source_name TEXT,
                    raw_content TEXT,
                    embedding vector(1536),
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
            """)
        conn.commit()

    print("Banco inicializado com sucesso.")
    print("Extensão pgvector habilitada.")


if __name__ == "__main__":
    init_database()
