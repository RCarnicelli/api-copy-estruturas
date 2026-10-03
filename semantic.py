"""Versioned embeddings and exact cosine retrieval; no reranker yet."""
import hashlib
import json
import math
import os
import re
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row
import requests
import tiktoken

from swipe_queries import PUBLIC_COLUMNS, _public_swipe, _query

MODEL = "text-embedding-3-small"
DIMENSIONS = 1536
TEXT_VERSION = "swipe-semantic-v1"  # Stable query-cache and unenriched record version.
TAXONOMY_TEXT_VERSION = "swipe-semantic-v2"
MAX_TOKENS = 2048
CHUNK_SIZE = 8
MAX_BACKFILL = 25
SEMANTIC_FIELDS = ("title", "description", "category", "framework", "objective",
                   "emotion", "tone", "hook", "mechanism", "cta", "why_it_works",
                   "adaptation", "when_to_use", "tags")


class SemanticError(RuntimeError):
    pass


def _encoding():
    return tiktoken.get_encoding("cl100k_base")


def semantic_text(swipe):
    lines = []
    from taxonomy import semantic_projection
    projection = semantic_projection(swipe.get('taxonomy'))
    fields = SEMANTIC_FIELDS if not projection else (
        'title', 'description', 'emotion', 'tone', 'hook', 'mechanism', 'cta')
    if projection:
        lines.append('taxonomy: ' + json.dumps(projection, ensure_ascii=False, sort_keys=True))
    for field in fields:
        value = swipe.get(field)
        if isinstance(value, (list, tuple)):
            value = ", ".join(sorted({re.sub(r"\s+", " ", str(v)).strip() for v in value if v}))
        else:
            value = re.sub(r"\s+", " ", str(value or "")).strip()
        if value:
            lines.append(f"{field}: {value[:1000]}")
    text = "\n".join(lines)
    tokens = _encoding().encode(text, disallowed_special=())
    return _encoding().decode(tokens[:MAX_TOKENS])


def row_text_version(row):
    from taxonomy import semantic_projection
    return TAXONOMY_TEXT_VERSION if semantic_projection(row.get('taxonomy')) else TEXT_VERSION


def content_hash(text, version=None):
    return hashlib.sha256(f"{MODEL}|{DIMENSIONS}|{version or TEXT_VERSION}|{text}".encode()).hexdigest()


def validate_vector(vector):
    if not isinstance(vector, list) or len(vector) != DIMENSIONS:
        raise SemanticError("Dimensão vetorial inválida")
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in vector):
        raise SemanticError("Vetor inválido")
    if not any(vector):
        raise SemanticError("Vetor nulo inválido")
    return vector


def vector_literal(vector):
    return json.dumps(validate_vector(vector), separators=(",", ":"))


@contextmanager
def connection():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SemanticError("PostgreSQL indisponível")
    try:
        conn = psycopg.connect(url, row_factory=dict_row, autocommit=True, connect_timeout=10,
                               options="-c statement_timeout=15000")
    except Exception:
        raise SemanticError("PostgreSQL indisponível") from None
    with conn:
        yield conn


def embed(texts, kind):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SemanticError("Serviço de embeddings indisponível")
    if not 1 <= len(texts) <= CHUNK_SIZE:
        raise ValueError("Lote de embeddings inválido")
    if any(not t.strip() or len(_encoding().encode(t, disallowed_special=())) > MAX_TOKENS for t in texts):
        raise ValueError("Texto de embedding inválido")
    # Reserve budget BEFORE the provider call. Failed calls consume an attempt.
    with connection() as conn:
        with conn.transaction():
            conn.execute("SELECT pg_advisory_xact_lock(741281006)")
            count = conn.execute("""SELECT count(*) AS total FROM embedding_usage
                                    WHERE kind=%s AND created_at >= date_trunc('day', now())""", (kind,)).fetchone()['total']
            if count >= (100 if kind == "query" else 50):
                raise SemanticError("Limite diário de embeddings atingido")
            job = conn.execute("INSERT INTO embedding_usage(kind, model) VALUES (%s,%s) RETURNING id", (kind, MODEL)).fetchone()['id']
    try:
        response = requests.post("https://api.openai.com/v1/embeddings",
                                 headers={"Authorization": "Bearer " + key},
                                 json={"model": MODEL, "dimensions": DIMENSIONS, "input": texts,
                                       "encoding_format": "float"}, timeout=60)
        if not response.ok:
            raise SemanticError(f"Embeddings retornou HTTP {response.status_code}")
        data = response.json()
        records = sorted(data.get('data', []), key=lambda r: r['index'])
        if [r['index'] for r in records] != list(range(len(texts))):
            raise SemanticError("Resposta de embeddings incompleta")
        vectors = [validate_vector(r['embedding']) for r in records]
        tokens = int(data.get('usage', {}).get('total_tokens', 0))
        with connection() as conn:
            conn.execute("UPDATE embedding_usage SET tokens=%s, succeeded=true WHERE id=%s", (tokens, job))
        return vectors, tokens
    except SemanticError:
        raise
    except Exception:
        raise SemanticError("Falha no serviço de embeddings") from None


def embedding_plan(limit=MAX_BACKFILL, swipe_id=None):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_BACKFILL:
        raise ValueError("O limite de vetorização deve ser de 1 a 25")
    rows = _query("SELECT * FROM swipes" + (" WHERE id=%s" if swipe_id else "") + " ORDER BY id", (swipe_id,) if swipe_id else ())
    pending, current = [], 0
    for row in rows:
        text = semantic_text(row)
        version = row_text_version(row)
        hashed = content_hash(text, version)
        valid = (row.get('embedding') is not None and row.get('embedding_hash') == hashed
                 and row.get('embedding_model') == MODEL and row.get('embedding_text_version') == version)
        if valid and not row.get('embedding_dirty'):
            current += 1
        elif text:
            pending.append({'row': row, 'text': text, 'hash': hashed, 'reuse': valid, 'version': version})
    selected = pending[:limit]
    tokens = sum(len(_encoding().encode(p['text'], disallowed_special=())) for p in selected if not p['reuse'])
    dimensions = _query("SELECT DISTINCT vector_dims(embedding) AS dimensao FROM swipes WHERE embedding IS NOT NULL")
    return {'total': len(rows), 'atuais': current, 'pendentes': len(pending), 'selecionados': len(selected),
            'versoes_texto': sorted({p['version'] for p in selected}),
            'dimensoes_no_banco': sorted({r['dimensao'] for r in dimensions}),
            'tokens_estimados': tokens, 'custo_estimado_usd': tokens * 0.02 / 1000000,
            'chamadas_estimadas': math.ceil(sum(not p['reuse'] for p in selected) / CHUNK_SIZE),
            '_items': selected}


def backfill_embeddings(limit=MAX_BACKFILL, dry_run=True, swipe_id=None):
    if not isinstance(dry_run, bool):
        raise ValueError("dry_run deve ser booleano")
    plan = embedding_plan(limit, swipe_id)
    result = {k: v for k, v in plan.items() if k != '_items'}
    result.update(modelo=MODEL, dimensao=DIMENSIONS, versao=TAXONOMY_TEXT_VERSION, vetorizados=0,
                  reutilizados=0, chamadas_openai=0, tokens_reais=0, erros=[])
    if dry_run:
        return result
    with connection() as conn:
        acquired = conn.execute("SELECT pg_try_advisory_lock(741281005) AS acquired").fetchone()['acquired']
        if not acquired:
            raise SemanticError("Vetorização já está em andamento")
        try:
            # Recheck after taking the lock: concurrent retries cannot pay twice.
            selected = embedding_plan(limit, swipe_id)['_items']
            fresh = [item for item in selected if not item['reuse']]
            for item in selected:
                if item['reuse']:
                    with conn.transaction():
                        latest = conn.execute("SELECT * FROM swipes WHERE id=%s FOR UPDATE", (item['row']['id'],)).fetchone()
                        if latest and content_hash(semantic_text(latest), row_text_version(latest)) == item['hash']:
                            conn.execute("UPDATE swipes SET embedding_dirty=false WHERE id=%s AND embedding_hash=%s",
                                         (item['row']['id'], item['hash']))
                            result['reutilizados'] += 1
            for offset in range(0, len(fresh), CHUNK_SIZE):
                chunk = fresh[offset:offset + CHUNK_SIZE]
                try:
                    result['chamadas_openai'] += 1
                    vectors, tokens = embed([p['text'] for p in chunk], 'document')
                    result['tokens_reais'] += tokens
                    for item, vector in zip(chunk, vectors):
                        with conn.transaction():
                            latest = conn.execute("SELECT * FROM swipes WHERE id=%s FOR UPDATE", (item['row']['id'],)).fetchone()
                            if not latest or content_hash(semantic_text(latest), row_text_version(latest)) != item['hash']:
                                result['erros'].append({'id': item['row']['id'], 'erro': 'Conteúdo alterado; vetor não aplicado'})
                                continue
                            conn.execute("""UPDATE swipes SET embedding=%s::vector, embedding_model=%s,
                                          embedding_hash=%s, embedding_text_version=%s, embedding_tokens=%s,
                                          embedded_at=now(), embedding_dirty=false WHERE id=%s""",
                                         (vector_literal(vector), MODEL, item['hash'], item['version'],
                                          len(_encoding().encode(item['text'], disallowed_special=())), item['row']['id']))
                            result['vetorizados'] += 1
                except Exception:
                    result['erros'].extend({'id': p['row']['id'], 'erro': 'Falha no lote de embeddings'} for p in chunk)
            result['pendentes_apos'] = embedding_plan(limit, swipe_id)['pendentes']
            return result
        finally:
            conn.execute("SELECT pg_advisory_unlock(741281005)")


def query_embedding(query):
    query = re.sub(r"\s+", " ", query).strip()
    hashed = content_hash('query:' + query)
    with connection() as conn:
        conn.execute("SELECT pg_advisory_lock(hashtextextended(%s,0))", ('query:' + hashed,))
        try:
            saved = conn.execute("SELECT embedding::text AS embedding FROM semantic_query_cache WHERE hash=%s", (hashed,)).fetchone()
            if saved:
                return json.loads(saved['embedding']), True
            vectors, _ = embed([query], 'query')
            conn.execute("INSERT INTO semantic_query_cache(hash, model, embedding) VALUES (%s,%s,%s::vector)",
                         (hashed, MODEL, vector_literal(vectors[0])))
            return vectors[0], False
        finally:
            conn.execute("SELECT pg_advisory_unlock(hashtextextended(%s,0))", ('query:' + hashed,))


def buscar_swipes_semanticos(consulta, categoria=None, objetivo=None, emocao=None, tom=None, limite=5):
    if not isinstance(consulta, str) or not 1 <= len(consulta.strip()) <= 2000:
        raise ValueError("A consulta deve conter de 1 a 2000 caracteres")
    if isinstance(limite, bool) or not isinstance(limite, int) or not 1 <= limite <= 20:
        raise ValueError("O limite deve ser de 1 a 20")
    filters = {"categoria": categoria, "objetivo": objetivo, "emocao": emocao, "tom": tom}
    clauses = ['embedding IS NOT NULL', 'embedding_dirty=false', 'embedding_model=%s', 'embedding_text_version IN (%s,%s)']
    parameters = [MODEL, TEXT_VERSION, TAXONOMY_TEXT_VERSION]
    for field, value in [('category', categoria), ('objective', objetivo), ('emotion', emocao), ('tone', tom)]:
        if value is not None and not isinstance(value, str):
            raise ValueError("Os filtros devem ser textos")
        if value and value.strip():
            normalized = value.strip().lower()
            if field == 'category':
                clauses.append('lower(btrim(category))=%s')
            else:
                clauses.append(f'EXISTS (SELECT 1 FROM unnest({field}) AS attr WHERE lower(btrim(attr))=%s)')
            parameters.append(normalized)
    where = ' AND '.join(clauses)
    # No eligible candidates means no provider call.
    if not _query('SELECT id FROM swipes WHERE ' + where + ' LIMIT 1', tuple(parameters)):
        return {'consulta': consulta, 'filters': filters, 'total': 0, 'items': [], 'query_cache_hit': False,
                'chamadas_openai': 0, 'ranking': 'cosine', 'modelo': MODEL}
    vector, cached = query_embedding(consulta)
    rows = _query(f'SELECT {PUBLIC_COLUMNS}, 1 - (embedding <=> %s::vector) AS semantic_score '
                  'FROM swipes WHERE ' + where + ' ORDER BY embedding <=> %s::vector, id LIMIT %s',
                  (vector_literal(vector), *parameters, vector_literal(vector), limite))
    items = []
    for row in rows:
        item = _public_swipe(row)
        item['embedding'] = None  # Keep the old field without sending 1536 floats to client context.
        item['semantic_score'] = float(row['semantic_score'])
        item['matched_by'] = ['semantica'] + [key for key, value in filters.items() if value and value.strip()]
        items.append(item)
    return {'consulta': consulta, 'filters': filters, 'total': len(items), 'items': items,
            'query_cache_hit': cached, 'chamadas_openai': 0 if cached else 1,
            'ranking': 'cosine', 'modelo': MODEL}
