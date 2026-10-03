import copy
import json
import os
import unittest
from contextlib import contextmanager
from unittest.mock import MagicMock, Mock, patch

import classifier
import classification_budget as budget
import ingestion
from classification_contract import validate_classification
from classification_fixture import classification_fixture
from swipe_repository import salvar_swipe


class IngestionV2Tests(unittest.TestCase):
    def test_complete_fixture_and_unknowns_valid(self):
        data = classification_fixture()
        self.assertIs(validate_classification(data), data)

    def test_missing_attribute_or_legacy_field_rejected(self):
        for change in ('taxonomy_field', 'legacy_field'):
            data = classification_fixture()
            if change == 'taxonomy_field': del data['taxonomy']['attributes']['channel']
            else: del data['tone']
            with self.assertRaises(ValueError): validate_classification(data)

    def test_unsupported_vocabulary_rejected(self):
        data = classification_fixture()
        data['category'] = 'invented'
        with self.assertRaises(ValueError): validate_classification(data)

    def test_cannot_claim_asset_inspection_or_verified_proof(self):
        for field, value in [('proof_status', 'observed_in_asset'), ('proof_verification', 'verified')]:
            data = classification_fixture()
            data['taxonomy']['attributes'][field] = dict(value=value, certainty='observed',
                application='present', evidence_origin='source_description', evidence='Source')
            with self.assertRaises(ValueError): validate_classification(data)

    def test_retention_or_reactivation_require_customer_context(self):
        for lifecycle in ('retention', 'reactivation'):
            data = classification_fixture()
            data['taxonomy']['attributes']['lifecycle_function'] = dict(value=[lifecycle],
                certainty='inferred', application='present', evidence_origin='analyst_interpretation', evidence='Email')
            with self.assertRaises(ValueError): validate_classification(data)

    def test_template_testimonial_must_be_recommended(self):
        data = classification_fixture()
        data['taxonomy']['attributes']['record_type']['value'] = 'template'
        data['taxonomy']['attributes']['strategic_summary']['application'] = 'recommended'
        data['taxonomy']['attributes']['proof_types'] = dict(value=['testimonial'],certainty='observed',
            application='present',evidence_origin='stored_template',evidence='Use testimonial')
        with self.assertRaises(ValueError): validate_classification(data)

    def test_invalid_taxonomy_never_saves_or_embeds(self):
        @contextmanager
        def lock(): yield True
        with patch('ingestion.bloquear_ingestao',lock), patch('ingestion.buscar_swipe_por_url',return_value=None), \
             patch('ingestion.capturar_pagina',return_value={'markdown':'source '*100}), \
             patch('ingestion.classificar_swipe',return_value={'title':'partial'}), \
             patch('ingestion.salvar_swipe') as save, patch('ingestion.backfill_embeddings') as embed:
            result=ingestion.processar_lote(['https://swipefile.com/test'],dry_run=False)
            self.assertEqual(result['erros'][0]['etapa'],'validacao_taxonomia')
            save.assert_not_called(); embed.assert_not_called()

    def test_validated_persistence_precedes_embedding(self):
        @contextmanager
        def lock(): yield True
        events=[]
        def classify(page): events.append('classify'); return classification_fixture()
        def save(data): events.append('save'); self.assertIn('taxonomy',data); return 'new'
        def embed(**args): events.append('embed'); return {'erros':[],'chamadas_openai':1}
        with patch('ingestion.bloquear_ingestao',lock), patch('ingestion.buscar_swipe_por_url',return_value=None), \
             patch('ingestion.capturar_pagina',return_value={'markdown':'source '*100}), \
             patch('ingestion.classificar_swipe',side_effect=classify), \
             patch('ingestion.salvar_swipe',side_effect=save), patch('ingestion.backfill_embeddings',side_effect=embed):
            result=ingestion.processar_lote(['https://swipefile.com/test'],dry_run=False)
            self.assertEqual(events,['classify','save','embed'])
            self.assertEqual(result['resultados'][0]['taxonomy_status'],'completa')

    def test_repository_saves_legacy_and_taxonomy_in_one_insert(self):
        conn=MagicMock();conn.__enter__.return_value=conn; cursor=conn.cursor.return_value.__enter__.return_value
        cursor.fetchall.return_value=[];cursor.fetchone.return_value=('new',)
        with patch.dict(os.environ,{'DATABASE_URL':'fake-test-only'}), \
             patch('swipe_repository.psycopg.connect',return_value=conn):
            salvar_swipe(classification_fixture())
        insert=next(call for call in cursor.execute.call_args_list if 'INSERT INTO' in call.args[0])
        self.assertIn('taxonomy',insert.args[0])
        self.assertEqual(insert.args[0].count('%s'),len(insert.args[1]))
        self.assertEqual(insert.args[1][-1].obj['version'],'swipe-taxonomy-v1')
        conn.commit.assert_called_once()

    def test_daily_budget_rejected_before_provider(self):
        conn=MagicMock();conn.execute.return_value.fetchone.return_value={'total':20}
        @contextmanager
        def connection(): yield conn
        with patch('classification_budget.connection',connection), \
             patch('classifier.OPENAI_API_KEY','fake-test-only'),patch('classifier.requests.post') as provider:
            with self.assertRaises(RuntimeError): classifier.classificar_swipe({'content':'source'})
            provider.assert_not_called()

    def test_classifier_one_call_with_full_taxonomy_and_reasoning_first(self):
        data=classification_fixture(); response=Mock(ok=True)
        response.json.return_value={'usage':{'input_tokens':1200,'output_tokens':2500},'output':[
            {'type':'reasoning'},{'type':'message','content':[{'type':'output_text','text':json.dumps(data)}]}]}
        with patch('classifier.OPENAI_API_KEY','fake-test-only'),patch('classifier.reserve',return_value=12), \
             patch('classifier.record_usage') as audit,patch('classifier.mark_valid'), \
             patch('classifier.requests.post',return_value=response) as provider:
            result=classifier.classificar_swipe({'content':'NAVIGATION\n# Specific Ad\noriginal source\n## Creative Variations\nNOT_THE_PIECE',
                                                'source_url':'https://swipefile.com/test'})
        provider.assert_called_once();audit.assert_called_once_with(12,{'input_tokens':1200,'output_tokens':2500})
        self.assertEqual(result['taxonomy']['classifier_version'],'swipe-classifier-v2')
        prompt=provider.call_args.kwargs['json']['input']
        self.assertNotIn('NAVIGATION',prompt);self.assertNotIn('NOT_THE_PIECE',prompt)
        self.assertIn('retention',prompt)

    def test_token_budget_refusal_has_no_provider_call(self):
        with patch('classifier.OPENAI_API_KEY','fake-test-only'),patch('classifier.MAX_INPUT_TOKENS',1), \
             patch('classifier.reserve') as reserve,patch('classifier.requests.post') as provider:
            with self.assertRaises(ValueError): classifier.classificar_swipe({'content':'source'})
            reserve.assert_not_called();provider.assert_not_called()


if __name__=='__main__': unittest.main()
