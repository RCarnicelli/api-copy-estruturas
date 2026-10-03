"""Conservative, evidence-bearing taxonomy; no automatic or paid classification."""
import hashlib
import json
from pathlib import Path

from psycopg.types.json import Jsonb

VERSION = 'swipe-taxonomy-v1'
FIELDS = ('record_type', 'channel', 'platform', 'format', 'distribution',
          'lifecycle_function', 'decision_stage', 'strategic_jobs', 'strategic_summary',
          'proof_types', 'proof_status', 'proof_verification', 'audience_relationship',
          'conversion_action', 'offer_type', 'next_step_offer', 'incentive_type',
          'market_context', 'framework_codes', 'technique_codes', 'pattern_codes')
LEGACY_FIELDS = ('id', 'title', 'category', 'description', 'framework', 'emotion', 'tone',
                 'hook', 'mechanism', 'cta', 'objective', 'when_to_use', 'why_it_works',
                 'adaptation', 'tags', 'source_url')
SEMANTIC_FIELDS = ('record_type', 'channel', 'format', 'lifecycle_function', 'decision_stage',
                   'strategic_jobs', 'strategic_summary', 'proof_types', 'proof_status',
                   'audience_relationship', 'conversion_action', 'offer_type',
                   'next_step_offer', 'incentive_type', 'market_context',
                   'framework_codes', 'technique_codes', 'pattern_codes')


def fingerprint(row):
    data = {key: row.get(key) for key in LEGACY_FIELDS}
    return hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def unknown_taxonomy():
    return {'version': VERSION, 'attributes': {field: {
        'value': 'unknown', 'certainty': 'unknown', 'application': 'unknown',
        'evidence_origin': 'none', 'evidence': 'Evidência insuficiente; não classificado.'
    } for field in FIELDS}}


def validate_taxonomy(data):
    if not isinstance(data, dict) or data.get('version') != VERSION:
        raise ValueError('Versão de taxonomia inválida')
    attrs = data.get('attributes')
    if not isinstance(attrs, dict) or set(attrs) != set(FIELDS):
        raise ValueError('Atributos de taxonomia inválidos')
    for attr in attrs.values():
        if not isinstance(attr, dict) or set(attr) != {
                'value', 'certainty', 'application', 'evidence_origin', 'evidence'}:
            raise ValueError('Evidência de atributo inválida')
        if attr['certainty'] not in ('observed', 'inferred', 'unknown', 'not_applicable'):
            raise ValueError('Certeza inválida')
        if attr['application'] not in ('recommended', 'present', 'unknown', 'not_applicable'):
            raise ValueError('Aplicação inválida')
        if attr['evidence_origin'] not in ('stored_template', 'source_description',
                                         'original_asset', 'analyst_interpretation', 'none'):
            raise ValueError('Origem inválida')
        if not isinstance(attr['value'], (str, list, dict)) or not isinstance(attr['evidence'], str):
            raise ValueError('Valor inválido')
        if attr['certainty'] == 'unknown' and attr['value'] != 'unknown':
            raise ValueError('Desconhecido deve ser explícito')
        if attr['certainty'] == 'not_applicable' and attr['value'] != 'not_applicable':
            raise ValueError('Não aplicável deve ser explícito')
        if attr['certainty'] in ('observed', 'inferred') and not attr['evidence'].strip():
            raise ValueError('Classificação deve ter evidência')
    return data


def semantic_projection(data):
    """Only meaning-bearing values/statuses; administrative evidence changes cost nothing."""
    if not data:
        return {}
    validate_taxonomy(data)
    projection = {}
    for field in SEMANTIC_FIELDS:
        attr = data['attributes'][field]
        if attr['value'] not in ('unknown', 'not_applicable'):
            projection[field] = {key: attr[key] for key in ('value', 'application', 'certainty')}
    return projection


def apply_curated_taxonomy(dry_run=True):
    """Apply approved snapshot only. Atomic, locked, idempotent, rejects stale source fields."""
    from semantic import connection
    if not isinstance(dry_run, bool):
        raise ValueError('dry_run deve ser booleano')
    bundle = json.loads(Path(__file__).with_name('taxonomy_snapshot.json').read_text())
    with connection() as conn:
        with conn.transaction():
            conn.execute('SELECT pg_advisory_xact_lock(741281007)')
            rows = conn.execute('SELECT *, to_jsonb(swipes)->\'taxonomy\' AS taxonomy FROM swipes ORDER BY id'
                                + ('' if dry_run else ' FOR UPDATE')).fetchall()
            by_id = {row['id']: row for row in rows}
            pending = []
            for item in bundle:
                row = by_id.get(item['id'])
                if not row or fingerprint(row) != item['source_fingerprint']:
                    raise ValueError('Registro alterado ou ausente; revisar prévia antes de aplicar')
                validate_taxonomy(item['taxonomy'])
                if row.get('taxonomy') != item['taxonomy']:
                    pending.append(item)
            if not dry_run:
                for item in pending:
                    conn.execute('UPDATE swipes SET taxonomy=%s, updated_at=now() WHERE id=%s',
                                 (Jsonb(item['taxonomy']), item['id']))
            return {'version': VERSION, 'dry_run': dry_run, 'reviewed': len(bundle),
                    'pending': len(pending) if dry_run else 0,
                    'updated': 0 if dry_run else len(pending),
                    'unchanged': len(bundle) - len(pending), 'paid_calls': 0}
