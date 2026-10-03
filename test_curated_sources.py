import json
import unittest
from unittest.mock import patch
from curated_sources import canonicalizar_ingestao, extrair_email_publico, capturar_pagina


class CuratedSourcesTests(unittest.TestCase):
    def test_email_canonical_dedup(self):
        self.assertEqual(canonicalizar_ingestao('https://reallygoodemails.com/emails/a-real-email/?utm=x'),
                         'https://reallygoodemails.com/emails/a-real-email')

    def test_reject_arbitrary_hosts_routes_credentials_and_ports(self):
        for url in ['http://reallygoodemails.com/emails/a', 'https://evil.com/emails/a',
                    'https://reallygoodemails.com/categories/winback',
                    'https://reallygoodemails.com/emails/a/info',
                    'https://user:pass@reallygoodemails.com/emails/a',
                    'https://reallygoodemails.com:444/emails/a']:
            self.assertIsNone(canonicalizar_ingestao(url))

    def test_swipefile_discovery_still_own_domain(self):
        from crawler import canonicalizar_swipe_url
        self.assertIsNone(canonicalizar_swipe_url('https://reallygoodemails.com/emails/a'))
        self.assertEqual(canonicalizar_ingestao('https://swipefile.com/real-ad?utm=x'),
                         'https://swipefile.com/real-ad')

    def test_reads_only_published_body_without_execution_or_tracking_links(self):
        body='<html><head><style>bad</style></head><body>' + '<p>Actual original email body.</p>'*8 + '<a href="https://tracking.example">Restart</a></body></html>'
        stream='17:T'+format(len(body.encode()),'x')+','+body+'7:'+json.dumps({'email':{'slug':'sample','title':'Sample','html':'$17','description':'Cancelled customers','company':{'name':'Brand'}}})
        html='<script>self.__next_f.push('+json.dumps([1,stream])+')</script>'
        result=extrair_email_publico(html,'https://reallygoodemails.com/emails/sample')['markdown']
        self.assertIn('Actual original email',result)
        self.assertNotIn('tracking.example',result)
        self.assertNotIn('bad',result)

    def test_missing_original_body_fails_closed(self):
        with self.assertRaises(ValueError):
            extrair_email_publico('<h1>Subject only</h1>', 'https://reallygoodemails.com/emails/sample')

    def test_invalid_source_never_fetches(self):
        with patch('curated_sources.requests.get') as request:
            with self.assertRaises(ValueError):
                capturar_pagina('https://evil.com/private')
            request.assert_not_called()
