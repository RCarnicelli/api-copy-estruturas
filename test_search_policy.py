import unittest
from unittest.mock import patch
import search_engine
import semantic
from search_policy import eligible, category_variants, normalize, envelope


def row(id, kind='real_piece', source='https://example.com/ad', **extra):
    return dict(id=id, category='socialmedia', emotion=['Vaidade'], tone=['provocativo'],
                source_url=source, taxonomy={'attributes': {'record_type': {'value': kind}}}, **extra)


class SearchPolicyTests(unittest.TestCase):
    def test_zacca_rejects_tone_only_and_templates(self):
        rows = [row('pizza', kind='template', source=None),
                {**row('unrelated'), 'emotion': ['desejo']}, row('grooming')]
        with patch('search_engine._carregar_swipes_postgres', return_value=rows):
            found = search_engine.buscar_swipes(emocao='vaidade', tom='provocativo', record_type='real_piece')
        self.assertEqual([x['id'] for x in found], ['grooming'])
        self.assertEqual(found[0]['unmatched_filters'], [])

    def test_partial_match_is_explicit(self):
        with patch('search_engine._carregar_swipes_postgres', return_value=[{**row('ad'), 'emotion': ['desejo']}]):
            found = search_engine.buscar_swipes(emocao='vaidade', tom='provocativo', match_mode='any')
        self.assertEqual(found[0]['unmatched_filters'], ['emocao'])

    def test_unknown_and_invalid_source_are_not_references(self):
        for item in [row('a', kind='unknown'), row('b', source=None), row('c', source='file:///ad')]:
            self.assertFalse(eligible(item, 'real_piece'))

    def test_alias_and_accent_matching(self):
        item = {**row('ad'), 'emotion': ['confiança']}
        with patch('search_engine._carregar_swipes_postgres', return_value=[item]):
            found = search_engine.buscar_swipes(categoria='social', emocao='confianca')
        self.assertEqual(len(found), 1)
        self.assertEqual(set(category_variants('socialmedia')), {'social', 'socialmedia'})
        self.assertEqual(normalize(' URGÊNCIA '), 'urgencia')

    def test_empty_is_explicit(self):
        self.assertEqual(envelope([])['status'], 'no_candidates')

    def test_semantic_policy_applies_before_embedding(self):
        with patch('semantic._query', return_value=[]) as db, patch('semantic.query_embedding') as provider:
            result = semantic.buscar_swipes_semanticos('Zacca', categoria='social', record_type='real_piece')
        sql, args = db.call_args.args
        self.assertIn("taxonomy->'attributes'->'record_type'->>'value'=%s", sql)
        self.assertIn('source_url', sql)
        self.assertIn(['social', 'socialmedia'], args)
        provider.assert_not_called()
        self.assertEqual(result['status'], 'no_candidates')

    def test_mcp_defaults_exclude_template_and_require_all_criteria(self):
        import mcp_server
        rows = [row('template', kind='template'), row('real'),
                {**row('tone_only'), 'emotion': ['desejo']}]
        with patch('search_engine._carregar_swipes_postgres', return_value=rows):
            result = mcp_server.buscar_swipes(emocao='vaidade', tom='provocativo')
        self.assertEqual([i['id'] for i in result['items']], ['real'])
        self.assertEqual(result['record_type'], 'real_piece')
        self.assertEqual(result['match_mode'], 'all')

    def test_template_mode_is_explicit(self):
        with patch('search_engine._carregar_swipes_postgres', return_value=[row('template', kind='template'), row('real')]):
            found = search_engine.buscar_swipes(record_type='template')
        self.assertEqual([i['id'] for i in found], ['template'])

    def test_rest_rejects_bad_policy_and_limit(self):
        from main import app
        with patch('search_engine._carregar_swipes_postgres') as db:
            client = app.test_client()
            for suffix in ('record_type=wrong', 'match_mode=wrong', 'limite=25'):
                response = client.get('/buscar-swipes?' + suffix)
                self.assertEqual(response.status_code, 400)
                self.assertIn('erro', response.json)
            db.assert_not_called()

    def test_optional_similarity_threshold_returns_empty(self):
        with patch('semantic._query', side_effect=[[{'id':'a'}], [row('a', semantic_score=.2)]]), \
             patch('semantic.query_embedding', return_value=([1.] * semantic.DIMENSIONS, True)):
            result = semantic.buscar_swipes_semanticos('Zacca', min_similarity=.6)
        self.assertEqual(result['items'], [])

    def test_validation_rejects_invalid_options_before_db(self):
        with patch('semantic._query') as db:
            for kwargs in ({'limite':25}, {'record_type':'invented'}, {'min_similarity':float('nan')}):
                with self.assertRaises(ValueError):
                    semantic.buscar_swipes_semanticos('Zacca', **kwargs)
            db.assert_not_called()

if __name__ == '__main__':
    unittest.main()
