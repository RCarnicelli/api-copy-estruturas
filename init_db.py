import os
import psycopg


def init_database():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL não configurada.")

    with psycopg.connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        conn.commit()

    print("Banco inicializado com sucesso.")
    print("Extensão pgvector habilitada.")


if __name__ == "__main__":
    init_database()
