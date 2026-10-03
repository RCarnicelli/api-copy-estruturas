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
                    why_it_works TEXT,
                    adaptation TEXT,
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
            cursor.execute("ALTER TABLE swipes ADD COLUMN IF NOT EXISTS why_it_works TEXT;")
            cursor.execute("ALTER TABLE swipes ADD COLUMN IF NOT EXISTS adaptation TEXT;")
            cursor.execute("ALTER TABLE swipes ADD COLUMN IF NOT EXISTS embedding vector(1536);")
            cursor.execute("""SELECT format_type(atttypid, atttypmod) FROM pg_attribute
                              WHERE attrelid='swipes'::regclass AND attname='embedding' AND NOT attisdropped""")
            if cursor.fetchone()[0] != 'vector(1536)':
                raise RuntimeError("A coluna embedding deve ser vector(1536); migração destrutiva não realizada")
            cursor.execute("""ALTER TABLE swipes
                ADD COLUMN IF NOT EXISTS embedding_model TEXT,
                ADD COLUMN IF NOT EXISTS embedding_hash TEXT,
                ADD COLUMN IF NOT EXISTS embedding_text_version TEXT,
                ADD COLUMN IF NOT EXISTS embedding_tokens INTEGER,
                ADD COLUMN IF NOT EXISTS embedded_at TIMESTAMPTZ,
                ADD COLUMN IF NOT EXISTS embedding_dirty BOOLEAN NOT NULL DEFAULT true;""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS semantic_query_cache (
                hash TEXT PRIMARY KEY, model TEXT NOT NULL, embedding vector(1536) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now());""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS embedding_usage (
                id BIGSERIAL PRIMARY KEY, kind TEXT NOT NULL, model TEXT NOT NULL,
                tokens INTEGER NOT NULL DEFAULT 0, succeeded BOOLEAN NOT NULL DEFAULT false,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now());""")
            cursor.execute("CREATE INDEX IF NOT EXISTS embedding_usage_created_idx ON embedding_usage(kind, created_at);")
            cursor.execute("""CREATE OR REPLACE FUNCTION mark_swipe_embedding_dirty() RETURNS trigger
                LANGUAGE plpgsql AS $$ BEGIN
                  IF ROW(OLD.title, OLD.description, OLD.category, OLD.framework, OLD.objective,
                         OLD.emotion, OLD.tone, OLD.hook, OLD.mechanism, OLD.cta, OLD.why_it_works,
                         OLD.adaptation, OLD.when_to_use, OLD.tags) IS DISTINCT FROM
                     ROW(NEW.title, NEW.description, NEW.category, NEW.framework, NEW.objective,
                         NEW.emotion, NEW.tone, NEW.hook, NEW.mechanism, NEW.cta, NEW.why_it_works,
                         NEW.adaptation, NEW.when_to_use, NEW.tags)
                  THEN NEW.embedding_dirty = true; END IF;
                  RETURN NEW;
                END $$;""")
            cursor.execute("DROP TRIGGER IF EXISTS swipes_embedding_dirty ON swipes;")
            cursor.execute("""CREATE TRIGGER swipes_embedding_dirty BEFORE UPDATE ON swipes
                              FOR EACH ROW EXECUTE FUNCTION mark_swipe_embedding_dirty();""")
            conn.commit()

    print("Banco inicializado com sucesso.")
    print("Extensão pgvector habilitada.")


if __name__ == "__main__":
    init_database()
