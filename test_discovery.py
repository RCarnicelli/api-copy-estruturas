import unittest
from unittest.mock import patch

from crawler import descobrir_links_swipefile, normalizar_pagina
from main import app


class DiscoveryTests(unittest.TestCase):
    def test_relative_absolute_canonical_dedup(self):
        result = {"markdown": '[A](/great-ad) [B](https://swipefile.com/great-ad/?utm=a#x) '
                  '[C](//www.swipefile.com/case/good-ad) [D](another-ad "title")'}
        self.assertEqual(descobrir_links_swipefile(result), [
            'https://swipefile.com/great-ad', 'https://swipefile.com/case/good-ad',
            'https://swipefile.com/another-ad'])

    def test_excludes_navigation_assets_external(self):
        paths = ['/', '/category/ads', '/categories', '/database?page=2', '/tools',
                 '/random', '/secret', '/signup', '/login', '/popular',
                 '/contact', '/business-idea-generator', '/photo.png',
                 'https://evil.example/ad', 'https://swipefile.com.evil.example/ad',
                 'https://user@swipefile.com/ad', '/api/data', '#anchor', '?page=2']
        self.assertEqual(descobrir_links_swipefile(
            {'markdown': ' '.join('[link](%s)' % p for p in paths)}), [])

    def test_html_and_wrapped_markdown(self):
        result = {'results': [{'markdown': {'raw_markdown': '[A](/great-ad)'},
                              'html': '<a href="/great-ad#x">A</a><a href="/case/good-ad">B</a>'}]}
        self.assertEqual(len(descobrir_links_swipefile(result)), 2)
        self.assertEqual(normalizar_pagina(result, 'url')['content'], '[A](/great-ad)')

    def test_no_images_and_reference_links(self):
        result = {'markdown': '![photo](/image-slug)\n[x]: /good-ad\n'}
        self.assertEqual(descobrir_links_swipefile(result), ['https://swipefile.com/good-ad'])

    def test_route_never_classifies_or_saves(self):
        with patch('main.capturar_pagina', return_value={'markdown': '[A](/great-ad)'}) as crawl, \
             patch('main.classificar_swipe') as classify, patch('main.salvar_swipe') as save:
            response = app.test_client().get('/coletar-swipes')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json['total_links'], 1)
            self.assertEqual(response.json['chamadas_openai'], 0)
            crawl.assert_called_once()
            classify.assert_not_called()
            save.assert_not_called()

    def test_rejects_foreign_host_before_crawling(self):
        with patch('main.capturar_pagina') as crawl:
            response = app.test_client().get('/coletar-swipes?url=http://localhost/')
            self.assertEqual(response.status_code, 400)
            crawl.assert_not_called()

    def test_errors_are_sanitized(self):
        with patch('main.capturar_pagina', side_effect=RuntimeError('secret-test')):
            response = app.test_client().get('/coletar-swipes')
            self.assertEqual(response.status_code, 500)
            self.assertNotIn('secret-test', response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
