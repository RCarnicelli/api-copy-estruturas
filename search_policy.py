"""Shared retrieval policy; similarity alone is never evidence of relevance."""
import unicodedata
from urllib.parse import urlsplit

ALIASES = {'socialmedia': 'social', 'printads': 'print-ads',
           'beforeandafter': 'before-and-after', 'directmail': 'direct-mail',
           'swipesemail': 'swipes-email'}

def normalize(value):
    text = str(value or '').strip().casefold()
    return ''.join(c for c in unicodedata.normalize('NFKD', text)
                   if not unicodedata.combining(c))

def category(value):
    text = normalize(value)
    return ALIASES.get(text, text)

def category_variants(value):
    canonical = category(value)
    return [canonical] + [alias for alias, target in ALIASES.items() if target == canonical]

def validate_policy(record_type, match_mode='all'):
    if record_type not in ('all', 'real_piece', 'template'):
        raise ValueError('record_type deve ser all, real_piece ou template')
    if match_mode not in ('all', 'any'):
        raise ValueError('match_mode deve ser all ou any')

def has_source(url):
    try:
        parsed = urlsplit(url or '')
        return parsed.scheme in ('http', 'https') and bool(parsed.hostname)
    except (ValueError, TypeError):
        return False

def record_kind(item):
    return ((item.get('taxonomy') or {}).get('attributes') or {}).get('record_type', {}).get('value', 'unknown')

def eligible(item, record_type):
    return record_type == 'all' or (record_kind(item) == record_type and
                                  (record_type != 'real_piece' or has_source(item.get('source_url'))))

def annotate(item):
    item = dict(item)
    item['record_type'] = record_kind(item)
    item['has_source'] = has_source(item.get('source_url'))
    item['relevance_status'] = 'requires_review'
    return item

def envelope(items, **metadata):
    return {**metadata, 'total': len(items), 'items': items,
            'status': 'candidates_require_review' if items else 'no_candidates',
            'limitations': ['Similaridade e correspondência de atributos não comprovam adequação nem desempenho.',
                            'Resultados vazios não comprovam ausência de referências em toda a base.']}
