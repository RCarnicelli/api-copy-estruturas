import copy
import json
import os
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import taxonomy as tax
import semantic as sem
from main import app


class TaxonomyTests(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads(Path(__file__).with_name('taxonomy_snapshot.json').read_text())
        self.by_id = {x['id']: x['taxonomy'] for x in self.bundle}

    def test_snapshot_all_25_unique_complete(self):
        self.assertEqual(len(self.bundle), 25)
        self.assertEqual(len(self.by_id), 25)
        for item in self.bundle:
            tax.validate_taxonomy(item['taxonomy'])
            self.assertEqual(len(item['source_fingerprint']), 64)

    def test_templates_do_not_contain_real_proof(self):
        attrs = self.by_id['testimonials_001']['attributes']
        self.assertEqual(attrs['proof_types']['value'], ['testimonial'])
        self.assertEqual(attrs['proof_types']['application'], 'recommended')
        self.assertEqual(attrs['proof_status']['value'], 'recommended_only')
        self.assertEqual(attrs['proof_verification']['value'], 'not_applicable')

    def test_no_retention_or_reactivation_or_asset_observation_in_snapshot(self):
        for data in self.by_id.values():
            for attr in data['attributes'].values():
                self.assertNotEqual(attr['evidence_origin'], 'original_asset')
            self.assertNotIn('retention', data['attributes']['lifecycle_function']['value'])
            self.assertNotIn('reactivation', data['attributes']['lifecycle_function']['value'])

    def test_email_sequence_is_format_not_framework(self):
        attrs = self.by_id['swipesemail_001']['attributes']
        self.assertEqual(attrs['format']['value'], 'email_sequence')
        self.assertEqual(attrs['framework_codes']['value'], 'unknown')
        self.assertEqual(attrs['audience_relationship']['value'], 'unknown')

    def test_offer_and_next_step_separate(self):
        attrs = self.by_id['swipe_82b97c105b80']['attributes']
        self.assertEqual(attrs['offer_type']['value'], 'service')
        self.assertEqual(attrs['next_step_offer']['value'], 'free_quote')
        self.assertEqual(attrs['proof_verification']['value'], 'unverified')

    def test_no_unsupported_distribution_or_cta(self):
        for data in self.by_id.values():
            self.assertEqual(data['attributes']['distribution']['value'], 'unknown')
        self.assertEqual(self.by_id['swipe_3847f7d00635']['attributes']['conversion_action']['value'], 'unknown')
        self.assertEqual(self.by_id['directmail_001']['attributes']['channel']['value'], 'unknown')

    def test_semantic_changes_but_evidence_admin_edits_do_not(self):
        row = {'title': 'Test', 'taxonomy': copy.deepcopy(self.by_id['socialmedia_001'])}
        text = sem.semantic_text(row)
        hashed = sem.content_hash(text, sem.row_text_version(row))
        row['taxonomy']['attributes']['channel']['evidence'] = 'Revisão administrativa'
        self.assertEqual(text, sem.semantic_text(row))
        row['taxonomy']['attributes']['channel']['value'] = 'email'
        self.assertNotEqual(hashed, sem.content_hash(sem.semantic_text(row), sem.row_text_version(row)))
        self.assertEqual(sem.row_text_version(row), 'swipe-semantic-v2')
        self.assertEqual(sem.row_text_version({'title': 'Test'}), 'swipe-semantic-v1')

    def test_query_cache_keeps_v1_hash(self):
        import hashlib
        expected = hashlib.sha256(f'{sem.MODEL}|1536|swipe-semantic-v1|query:same'.encode()).hexdigest()
        self.assertEqual(sem.content_hash('query:same'), expected)

    def test_v2_skips_adaptation_and_legacy_mixed_categories(self):
        row = {'taxonomy': self.by_id['swipesemail_001'], 'adaptation': 'NOT_OBSERVED',
               'category': 'swipesemail', 'framework': 'Email Sequence', 'raw_content': 'NOISE'}
        text = sem.semantic_text(row)
        self.assertIn('recommended', text)
        self.assertNotIn('NOT_OBSERVED', text)
        self.assertNotIn('category:', text)
        self.assertNotIn('NOISE', text)

    def test_unknown_is_valid_but_contradictory_certainty_rejected(self):
        data = tax.unknown_taxonomy()
        tax.validate_taxonomy(data)
        data['attributes']['channel']['value'] = 'social'
        with self.assertRaises(ValueError): tax.validate_taxonomy(data)

    def test_stale_snapshot_fails_before_write(self):
        conn = MagicMock()
        conn.execute.return_value.fetchall.return_value = [{'id': item['id']} for item in self.bundle]
        @contextmanager
        def connection(): yield conn
        with patch('semantic.connection', connection):
            with self.assertRaises(ValueError): tax.apply_curated_taxonomy(False)
        self.assertFalse(any(call.args[0].startswith('UPDATE') for call in conn.execute.call_args_list))

    def test_endpoint_dev_opt_in_and_auth_before_migration(self):
        with patch.dict(os.environ, {}, clear=True), patch('main.init_database') as migrate:
            self.assertEqual(app.test_client().post('/taxonomy/apply', json={'dry_run': False}).status_code, 503)
            migrate.assert_not_called()
        with patch.dict(os.environ, {'SWIPE_TAXONOMY_ENABLED': '1'}, clear=True), patch('main.init_database') as migrate:
            self.assertEqual(app.test_client().post('/taxonomy/apply', json={'dry_run': False}).status_code, 401)
            migrate.assert_not_called()


if __name__ == '__main__': unittest.main()
