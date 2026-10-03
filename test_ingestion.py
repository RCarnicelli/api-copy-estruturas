import os
import json
from classification_fixture import classification_fixture
import unittest
from contextlib import contextmanager
from unittest.mock import patch, Mock

import ingestion
from classifier import classificar_swipe, MAX_CONTENT_CHARS, MAX_OUTPUT_TOKENS
from main import app
from swipe_repository import salvar_swipe


@contextmanager
def acquired_lock():
    yield True


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.urls = ['https://swipefile.com/ad-one', 'https://swipefile.com/ad-two',
                     'https://swipefile.com/ad-three', 'https://swipefile.com/ad-four']

    def test_dry_run_dedup_existing_and_limit_no_paid_calls(self):
        with patch('ingestion.buscar_swipe_por_url', side_effect=lambda url: 'existing' if url == self.urls[0] else None), \
             patch('ingestion.capturar_pagina') as crawl, patch('ingestion.classificar_swipe') as classify, \
             patch('ingestion.salvar_swipe') as save:
            result = ingestion.processar_lote(self.urls + [self.urls[1] + '/?utm=a'], limite=2)
            self.assertEqual(result['descobertos'], 4)
            self.assertEqual(result['planejados'], self.urls[1:3])
            self.assertEqual(result['ignorados'], 3)
            self.assertEqual(result['chamadas_openai'], 0)
            crawl.assert_not_called(); classify.assert_not_called(); save.assert_not_called()

    def test_individual_failure_consumes_limit_and_continues(self):
        with patch('ingestion.bloquear_ingestao', acquired_lock), \
             patch('ingestion.buscar_swipe_por_url', return_value=None), \
             patch('ingestion.capturar_pagina', side_effect=[RuntimeError('secret'), {'markdown': 'good ' * 30}]) as crawl, \
             patch('ingestion.classificar_swipe', return_value=classification_fixture(self.urls[1])) as classify, \
             patch('ingestion.salvar_swipe', return_value='new'):
            result = ingestion.processar_lote(self.urls, limite=2, dry_run=False)
            self.assertEqual(result['processados'], 1)
            self.assertEqual(result['total_erros'], 1)
            self.assertEqual(result['chamadas_openai'], 1)
            self.assertEqual(result['ignorados'], 2)
            self.assertEqual(crawl.call_count, 2)
            classify.assert_called_once()
            self.assertNotIn('secret', str(result))

    def test_classification_failure_counts_call_without_retry(self):
        with patch('ingestion.bloquear_ingestao', acquired_lock), \
             patch('ingestion.buscar_swipe_por_url', return_value=None), \
             patch('ingestion.capturar_pagina', return_value={'markdown': 'good ' * 30}), \
             patch('ingestion.classificar_swipe', side_effect=ValueError()) as classify, \
             patch('ingestion.salvar_swipe') as save:
            result = ingestion.processar_lote(self.urls, limite=1, dry_run=False)
            self.assertEqual(result['chamadas_openai'], 1)
            self.assertEqual(result['total_erros'], 1)
            classify.assert_called_once(); save.assert_not_called()

    def test_existing_skipped_before_crawler(self):
        with patch('ingestion.bloquear_ingestao', acquired_lock), \
             patch('ingestion.buscar_swipe_por_url', return_value='old'), \
             patch('ingestion.capturar_pagina') as crawl:
            result = ingestion.processar_lote(self.urls[:1], dry_run=False)
            self.assertEqual(result['resultados'][0]['id'], 'old')
            self.assertEqual(result['chamadas_openai'], 0)
            crawl.assert_not_called()

    def test_busy_lock_does_not_crawl(self):
        @contextmanager
        def busy():
            yield False
        with patch('ingestion.bloquear_ingestao', busy), patch('ingestion.capturar_pagina') as crawl:
            with self.assertRaises(ingestion.IngestionBusy):
                ingestion.processar_lote(self.urls[:1], dry_run=False)
            crawl.assert_not_called()

    def test_invalid_payloads(self):
        for kwargs in [{'limite': 4}, {'limite': True}, {'dry_run': 'false'}]:
            with self.assertRaises(ValueError):
                ingestion.processar_lote(self.urls, **kwargs)
        for urls in [[], ['http://localhost'], ['https://swipefile.com/database'], ['https://swipefile.com.evil/ad']]:
            with self.assertRaises(ValueError):
                ingestion.processar_lote(urls)

    def test_paid_routes_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True), patch('main.processar_lote') as run:
            response = app.test_client().post('/processar-swipes', json={'urls': self.urls, 'dry_run': False})
            self.assertEqual(response.status_code, 503)
            self.assertEqual(app.test_client().get('/test-crawler?url=' + self.urls[0]).status_code, 503)
            run.assert_not_called()

    def test_auth_and_default_simulation(self):
        with patch.dict(os.environ, {'SWIPE_INGESTION_ENABLED': '1', 'SWIPE_INGESTION_TOKEN': 'x' * 32}), \
             patch('main.processar_lote', return_value={'status': 'ok'}) as run:
            client = app.test_client()
            self.assertEqual(client.post('/processar-swipes', json={'urls': self.urls, 'dry_run': False}).status_code, 401)
            run.assert_not_called()
            self.assertEqual(client.post('/processar-swipes', json={'urls': self.urls}).status_code, 200)
            self.assertEqual(run.call_args.args, (self.urls, 1, True))
            self.assertEqual(client.post('/processar-swipes', json={'urls': self.urls, 'dry_run': False},
                                        headers={'Authorization': 'Bearer ' + 'x' * 32}).status_code, 200)


class ClassifierTests(unittest.TestCase):
    def test_reasoning_before_message_and_cost_limits(self):
        response = Mock(ok=True)
        response.json.return_value = {'output': [
            {'type': 'reasoning'}, {'type': 'message', 'content': [
                {'type': 'output_text', 'text': json.dumps(classification_fixture())}]}]}
        content = 'a' * (MAX_CONTENT_CHARS + 1000)
        with patch('classifier.OPENAI_API_KEY', 'fake-test-only'), patch('classifier.reserve', return_value=1), patch('classifier.record_usage'), patch('classifier.mark_valid'), patch('classifier.requests.post', return_value=response) as post:
            result = classificar_swipe({'content': content, 'source_url': 'https://swipefile.com/ad'})
            payload = post.call_args.kwargs['json']
            self.assertEqual(payload['model'], 'gpt-6-luna')
            self.assertEqual(payload['max_output_tokens'], MAX_OUTPUT_TOKENS)
            self.assertNotIn('a' * (MAX_CONTENT_CHARS + 1), payload['input'])
            self.assertEqual(result['original_content'], content)
            self.assertEqual(result['title'], 'Example')

    def test_incomplete_output_not_saved(self):
        response = Mock(ok=True)
        response.json.return_value = {'status': 'incomplete', 'output': []}
        with patch('classifier.OPENAI_API_KEY', 'fake-test-only'), patch('classifier.reserve', return_value=1), patch('classifier.record_usage'), patch('classifier.mark_valid'), patch('classifier.requests.post', return_value=response):
            with self.assertRaises(ValueError):
                classificar_swipe({'content': 'some content'})


class RepositoryTests(unittest.TestCase):
    def test_canonical_existing_returned_under_transaction_lock(self):
        cursor = Mock()
        cursor.fetchall.return_value = [('old', 'https://www.swipefile.com/ad/?utm=old')]
        connection = Mock()
        connection.cursor.return_value.__enter__ = Mock(return_value=cursor)
        connection.cursor.return_value.__exit__ = Mock(return_value=False)
        context = Mock()
        context.__enter__ = Mock(return_value=connection)
        context.__exit__ = Mock(return_value=False)
        with patch.dict(os.environ, {'DATABASE_URL': 'fake-test-only'}), patch('swipe_repository.psycopg.connect', return_value=context):
            self.assertEqual(salvar_swipe({'source_url': 'https://swipefile.com/ad'}), 'old')
            statements = [call.args[0] for call in cursor.execute.call_args_list]
            self.assertIn('pg_advisory_xact_lock', statements[0])
            self.assertFalse(any('INSERT' in query for query in statements))


if __name__ == '__main__':
    unittest.main()
