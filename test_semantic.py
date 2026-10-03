import math
from classification_fixture import classification_fixture
import os
import unittest
from contextlib import contextmanager
from unittest.mock import patch, Mock

import semantic as sem
from main import app
from test_postgres_mcp import ROWS


class SemanticTests(unittest.TestCase):
    def test_text_excludes_raw_url_and_ids_and_is_deterministic(self):
        a = {'title': 'Pizza hero', 'hook': ' Quebra  de\n expectativa ', 'tags': ['pizza', 'venda'],
             'raw_content': 'NAVIGATION NOISE', 'source_url': 'https://secret.example', 'id': 'id_1'}
        b = {**a, 'tags': ['venda', 'pizza', 'pizza'], 'raw_content': 'changed', 'id': 'id_2'}
        self.assertEqual(sem.semantic_text(a), sem.semantic_text(b))
        text = sem.semantic_text(a)
        self.assertIn('hook: Quebra de expectativa', text)
        self.assertNotIn('NAVIGATION', text); self.assertNotIn('https://', text)
        self.assertEqual(sem.content_hash(text), sem.content_hash(sem.semantic_text(b)))
        self.assertNotEqual(sem.content_hash(text), sem.content_hash(text + ' new meaning'))

    def test_token_limit_and_version_hash(self):
        swipe = {field: 'palavra ' * 1000 for field in sem.SEMANTIC_FIELDS}
        text = sem.semantic_text(swipe)
        self.assertLessEqual(len(sem._encoding().encode(text, disallowed_special=())), sem.MAX_TOKENS)
        old = sem.content_hash(text)
        with patch('semantic.TEXT_VERSION', 'v2'):
            self.assertNotEqual(old, sem.content_hash(text))

    def test_vector_rejects_wrong_dimensions_nonfinite_and_zero(self):
        for vector in [[1.0], [0.0] * sem.DIMENSIONS, [math.nan] * sem.DIMENSIONS, [True] * sem.DIMENSIONS]:
            with self.assertRaises(sem.SemanticError):
                sem.validate_vector(vector)
        self.assertEqual(len(sem.validate_vector([1.0] * sem.DIMENSIONS)), 1536)

    def test_plan_skips_existing_hash_and_handles_dirty_reusable(self):
        row = dict(ROWS[0])
        row.update(embedding='stored-vector', embedding_hash=sem.content_hash(sem.semantic_text(row)),
                   embedding_model=sem.MODEL, embedding_text_version=sem.TEXT_VERSION, embedding_dirty=False)
        with patch('semantic._query', side_effect=lambda sql,*args: [{'dimensao':1536}] if 'vector_dims' in sql else [row]), patch('semantic.embed') as provider:
            plan = sem.backfill_embeddings(dry_run=True)
            self.assertEqual(plan['atuais'], 1)
            self.assertEqual(plan['chamadas_estimadas'], 0)
            self.assertEqual(plan['tokens_estimados'], 0)
            provider.assert_not_called()
        row['embedding_dirty'] = True
        with patch('semantic._query', side_effect=lambda sql,*args: [{'dimensao':1536}] if 'vector_dims' in sql else [row]):
            plan = sem.embedding_plan()
            self.assertEqual(plan['pendentes'], 1)
            self.assertTrue(plan['_items'][0]['reuse'])
            self.assertEqual(plan['chamadas_estimadas'], 0)

    def test_dry_run_safe_max25_and_no_paid_calls(self):
        with patch('semantic._query', side_effect=lambda sql,*args: [] if 'vector_dims' in sql else [dict(ROWS[0]) for _ in range(25)]), patch('semantic.embed') as provider:
            plan = sem.backfill_embeddings()
            self.assertEqual(plan['selecionados'], 25)
            self.assertEqual(plan['versao'], sem.TAXONOMY_TEXT_VERSION)
            self.assertEqual(plan['chamadas_estimadas'], 4)
            self.assertLess(plan['custo_estimado_usd'], .002)
            provider.assert_not_called()
            with self.assertRaises(ValueError): sem.embedding_plan(26)

    def test_search_empty_eligible_set_no_provider(self):
        with patch('semantic._query', return_value=[]), patch('semantic.query_embedding') as embed:
            result = sem.buscar_swipes_semanticos('pizza com desejo', categoria='missing')
            self.assertEqual(result['total'], 0)
            self.assertEqual(result['chamadas_openai'], 0)
            embed.assert_not_called()

    def test_search_parameterized_hard_filters_score_and_cache(self):
        row = {**ROWS[0], 'semantic_score': .78}
        with patch('semantic._query', side_effect=[[{'id':'real_1'}],[row]]) as db, \
             patch('semantic.query_embedding', return_value=([1.0] * sem.DIMENSIONS, True)):
            result = sem.buscar_swipes_semanticos('gerar desejo', ' ADS ', 'vender', 'desejo', 'direto', 3)
            self.assertEqual(result['items'][0]['semantic_score'], .78)
            self.assertEqual(result['items'][0]['embedding'], None)
            self.assertEqual(result['chamadas_openai'], 0)
            sql, params = db.call_args.args
            self.assertIn('<=>', sql)
            self.assertIn('EXISTS', sql)
            self.assertIn('embedding_dirty=false', sql)
            self.assertIn('ads', params)
            self.assertEqual(params[-1], 3)

    def test_invalid_search_never_calls_provider(self):
        with patch('semantic.query_embedding') as provider:
            for query, limit in [('',5), ('a'*2001,5), ('valid',0), ('valid',21)]:
                with self.assertRaises(ValueError): sem.buscar_swipes_semanticos(query, limite=limit)
            provider.assert_not_called()

    def test_query_cache_avoids_provider(self):
        conn = Mock()
        conn.execute.return_value.fetchone.return_value = {'embedding': sem.vector_literal([1.0] * sem.DIMENSIONS)}
        @contextmanager
        def connection(): yield conn
        with patch('semantic.connection', connection), patch('semantic.embed') as provider:
            vector, cache = sem.query_embedding('same query')
            self.assertTrue(cache)
            self.assertEqual(len(vector), 1536)
            provider.assert_not_called()

    def test_provider_reorders_outputs_and_tracks_usage(self):
        conn = Mock()
        conn.execute.return_value.fetchone.side_effect = [{'total':0}, {'id':10}]
        @contextmanager
        def connection(): yield conn
        @contextmanager
        def transaction(): yield
        conn.transaction = transaction
        response = Mock(ok=True)
        response.json.return_value = {'data':[{'index':1,'embedding':[2.0]*1536},
                                              {'index':0,'embedding':[1.0]*1536}], 'usage':{'total_tokens':6}}
        with patch.dict(os.environ, {'OPENAI_API_KEY':'fake-test-only'}), \
             patch('semantic.connection', connection), patch('semantic.requests.post', return_value=response) as provider:
            vectors, tokens = sem.embed(['first', 'second'], 'document')
            self.assertEqual(tokens, 6)
            self.assertEqual(vectors[0][0], 1.0)
            self.assertEqual(provider.call_args.kwargs['json']['dimensions'], 1536)
            self.assertEqual(provider.call_count, 1)

    def test_budget_stops_before_provider(self):
        conn = Mock()
        conn.execute.return_value.fetchone.return_value = {'total':100}
        @contextmanager
        def connection(): yield conn
        @contextmanager
        def transaction(): yield
        conn.transaction = transaction
        with patch.dict(os.environ, {'OPENAI_API_KEY':'fake-test-only'}), \
             patch('semantic.connection', connection), patch('semantic.requests.post') as provider:
            with self.assertRaises(sem.SemanticError): sem.embed(['query'], 'query')
            provider.assert_not_called()

    def test_paid_backfill_requires_separate_auth(self):
        with patch.dict(os.environ, {}, clear=True), patch('main.backfill_embeddings') as run:
            result = app.test_client().post('/embeddings', json={'dry_run':False})
            self.assertEqual(result.status_code, 401)
            run.assert_not_called()

    def test_ingestion_keeps_saved_swipe_when_embedding_fails(self):
        from ingestion import processar_lote
        @contextmanager
        def lock(): yield True
        with patch('ingestion.bloquear_ingestao', lock), patch('ingestion.buscar_swipe_por_url', return_value=None), \
             patch('ingestion.capturar_pagina', return_value={'markdown':'content ' * 100}), \
             patch('ingestion.classificar_swipe', return_value=classification_fixture()), patch('ingestion.salvar_swipe', return_value='saved'), \
             patch('ingestion.backfill_embeddings', side_effect=sem.SemanticError('provider failure')):
            result = processar_lote(['https://swipefile.com/ad'], dry_run=False)
            self.assertEqual(result['processados'], 1)
            self.assertEqual(result['resultados'][0]['embedding_status'], 'pendente')
            self.assertEqual(result['resultados'][0]['id'], 'saved')
            self.assertEqual(result['total_erros'], 0)

    def test_ingestion_auto_embedding_counts_separate_costs(self):
        from ingestion import processar_lote
        @contextmanager
        def lock(): yield True
        with patch('ingestion.bloquear_ingestao', lock), patch('ingestion.buscar_swipe_por_url', return_value=None), \
             patch('ingestion.capturar_pagina', return_value={'markdown':'content ' * 100}), \
             patch('ingestion.classificar_swipe', return_value=classification_fixture()), patch('ingestion.salvar_swipe', return_value='saved'), \
             patch('ingestion.backfill_embeddings', return_value={'erros':[], 'chamadas_openai':1}) as embedding:
            result = processar_lote(['https://swipefile.com/ad'], dry_run=False)
            self.assertEqual(result['chamadas_openai'], 1)
            self.assertEqual(result['chamadas_embeddings'], 1)
            self.assertEqual(result['resultados'][0]['embedding_status'], 'pronto')
            embedding.assert_called_once_with(limit=1, dry_run=False, swipe_id='saved')


if __name__ == '__main__': unittest.main()
