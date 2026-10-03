"""Reserve paid classification attempts before requests; never record source text or keys."""
from semantic import connection

MAX_DAILY_CALLS = 20


def reserve(model):
    with connection() as conn:
        with conn.transaction():
            conn.execute('SELECT pg_advisory_xact_lock(741281008)')
            row = conn.execute("SELECT count(*) AS total FROM classification_usage "
                               "WHERE created_at >= date_trunc('day',now())").fetchone()
            if row['total'] >= MAX_DAILY_CALLS:
                raise RuntimeError('Limite diário de classificação atingido')
            return conn.execute('INSERT INTO classification_usage(model) VALUES (%s) RETURNING id',
                                (model,)).fetchone()['id']


def record_usage(job, usage):
    values = [usage.get(key, 0) for key in ('input_tokens', 'output_tokens')]
    if any(isinstance(x, bool) or not isinstance(x, int) or x < 0 for x in values):
        raise ValueError('Uso de tokens inválido')
    with connection() as conn:
        conn.execute('UPDATE classification_usage SET input_tokens=%s, output_tokens=%s, '
                     'provider_received=true WHERE id=%s', (*values, job))


def mark_valid(job):
    with connection() as conn:
        conn.execute('UPDATE classification_usage SET validated=true WHERE id=%s', (job,))
