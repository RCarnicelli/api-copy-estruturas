import os
import sys
import subprocess
import unittest
from contextlib import contextmanager
from datetime import datetime, timezone
from unittest.mock import patch, Mock

import mcp_server
import main
import search_engine
import swipe_queries as queries


ROWS = [
    {"id": "real_1", "category": "ads", "title": "Real DB swipe", "description": "Persisted",
     "objective": ["vender"], "emotion": ["desejo"], "tone": ["direto"], "tags": None,
     "source_url": "https://swipefile.com/real-ad", "why_it_works": "Evidence",
     "adaptation": "Apply mechanism", "raw_content": "Original source", "embedding": None,
     "created_at": datetime(2026, 10, 3, tzinfo=timezone.utc)},
    {"id": "real_2", "category": "advice", "title": "DB advice", "objective": None,
     "emotion": None, "tone": None, "tags": []},
    {"id": "real_3", "category": "new-category", "title": "New DB category", "objective": [],
     "emotion": [], "tone": [], "tags": []},
]


def fake_query(sql, parameters=()):
    if "DISTINCT" in sql:
        return [{"category": category} for category in sorted({r['category'] for r in ROWS})]
    return [dict(row) for row in ROWS if not parameters or row['category'] == parameters[0]]


class PostgreSQLMCPTests(unittest.TestCase):
    def test_categories_come_from_database_including_new_category(self):
        with patch('swipe_queries._query', side_effect=fake_query):
            self.assertEqual(mcp_server.listar_categorias(), {
                'total': 3, 'categorias': ['ads', 'advice', 'new-category']})

    def test_category_exact_filter_normalization_and_unknown_empty(self):
        with patch('swipe_queries._query', side_effect=fake_query):
            result = mcp_server.obter_swipes_categoria(' ADS ')
            self.assertEqual(result['categoria'], 'ads')
            self.assertEqual([s['id'] for s in result['items']], ['real_1'])
            self.assertEqual(mcp_server.obter_swipes_categoria('missing')['items'], [])
            self.assertEqual(mcp_server.obter_swipes_categoria(' ')['total'], 0)

    def test_card_and_category_match_database_ids(self):
        with patch('swipe_queries._query', side_effect=fake_query):
            for category in ['ads', 'advice', 'new-category', 'missing']:
                cards = mcp_server.obter_estrutura_copy_card(category)
                self.assertEqual(cards['type'], 'cards')
                self.assertEqual(cards['items'], mcp_server.obter_swipes_categoria(category)['items'])
            self.assertEqual(mcp_server.obter_estrutura_copy_card(' '), {'erro': 'Categoria não informada'})

    def test_advice_preserves_title_and_three_card_limit(self):
        with patch('swipe_queries.carregar_swipes_postgres', return_value=[{'id': str(i)} for i in range(5)]):
            cards = mcp_server.obter_estrutura_copy_card('advice')
            self.assertEqual(cards['title'], 'Melhores Estruturas para Advice')
            self.assertEqual(len(cards['items']), 3)

    def test_search_preserves_scoring_soft_matching_and_limits(self):
        with patch('swipe_queries._query', side_effect=fake_query):
            result = mcp_server.buscar_swipes(categoria=' ADS ', objetivo='vender', emocao='desejo', tom='direto')
            self.assertEqual(result['total'], 1)
            item = result['items'][0]
            self.assertEqual(item['score'], 11)
            self.assertEqual(item['matched_by'], ['categoria', 'objetivo', 'emocao', 'tom'])
            self.assertEqual(item['raw_content'], 'Original source')
            self.assertEqual(item['why_it_works'], 'Evidence')
            self.assertEqual(item['button']['action'], 'usarSwipe')
            self.assertEqual(item['created_at'], '2026-10-03T00:00:00+00:00')
            self.assertEqual(item['tags'], [])
            # Existing search combines score matches with OR, not new hard filters.
            self.assertEqual(len(search_engine.buscar_swipes(categoria='missing', objetivo='vender')), 1)
            self.assertEqual(len(search_engine.buscar_swipes(limite=1)), 1)

    def test_empty_database_no_local_fallback(self):
        with patch('swipe_queries._query', return_value=[]):
            self.assertEqual(mcp_server.listar_categorias()['total'], 0)
            self.assertEqual(mcp_server.obter_swipes_categoria('ads')['total'], 0)
            self.assertEqual(mcp_server.buscar_swipes()['total'], 0)
            self.assertEqual(mcp_server.obter_estrutura_copy_card('advice')['items'], [])

    def test_database_failure_never_falls_back_or_leaks_secrets(self):
        with patch.dict(os.environ, {'DATABASE_URL': 'fake-secret'}), \
             patch('swipe_queries.psycopg.connect', side_effect=RuntimeError('fake-secret')):
            for function, args in [(mcp_server.listar_categorias, ()),
                                   (mcp_server.obter_swipes_categoria, ('ads',)),
                                   (mcp_server.buscar_swipes, ()),
                                   (mcp_server.obter_estrutura_copy_card, ('advice',))]:
                with self.assertRaises(queries.SwipeReadError) as error:
                    function(*args)
                self.assertNotIn('fake-secret', str(error.exception))
            response = main.app.test_client().get('/swipes?categoria=ads')
            self.assertEqual(response.status_code, 503)
            self.assertNotIn('fake-secret', response.get_data(as_text=True))

    def test_parameterized_category_query_and_readonly_connection(self):
        cursor = Mock()
        cursor.fetchall.return_value = []
        @contextmanager
        def fake_cursor():
            yield cursor
        conn = Mock()
        conn.cursor = fake_cursor
        @contextmanager
        def fake_connection(*args, **kwargs):
            self.assertIn('default_transaction_read_only=on', kwargs['options'])
            yield conn
        with patch.dict(os.environ, {'DATABASE_URL': 'fake-test'}), \
             patch('swipe_queries.psycopg.connect', side_effect=fake_connection):
            malicious = "ads'; DROP TABLE swipes; --"
            self.assertEqual(queries.carregar_swipes_postgres(malicious), [])
            sql, parameters = cursor.execute.call_args.args
            self.assertNotIn(malicious, sql)
            self.assertEqual(parameters, (malicious.lower(),))

    def test_rest_and_mcp_consistency(self):
        with patch('swipe_queries._query', side_effect=fake_query):
            client = main.app.test_client()
            for category in ['ads', 'advice', 'new-category', 'missing']:
                self.assertEqual(client.get('/swipes?categoria='+category).json['items'],
                                 mcp_server.obter_swipes_categoria(category)['items'])
                self.assertEqual(client.get('/estruturas/cards?categoria='+category).json,
                                 mcp_server.obter_estrutura_copy_card(category))
            self.assertEqual(client.get('/buscar-swipes?categoria=ads').json['items'],
                             mcp_server.buscar_swipes(categoria='ads')['items'])
            self.assertIn('New-category', client.get('/categorias').json['content'])

    def test_startup_without_local_database_module(self):
        script = '''import builtins
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name in {"swipes_db", "seed_db"}:
        raise AssertionError("Operational local dependency: " + name)
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
import main, mcp_server, search_engine
'''
        result = subprocess.run([sys.executable, '-c', script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
