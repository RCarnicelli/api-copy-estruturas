"""Narrow public email source adapter; no arbitrary URLs or script execution."""
import json
import re
import unicodedata
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup
from crawler import canonicalizar_swipe_url, capturar_pagina as capturar_swipefile

MAX_PAGE_BYTES = 2 * 1024 * 1024


def canonicalizar_ingestao(url):
    swipe = canonicalizar_swipe_url(url)
    if swipe:
        return swipe
    try:
        p = urlsplit(url)
        if (p.scheme != 'https' or p.hostname != 'reallygoodemails.com' or p.username
                or p.password or p.port not in (None, 443)):
            return None
        if not re.fullmatch(r'/emails/[a-z0-9-]+/?', p.path):
            return None
        return 'https://reallygoodemails.com' + p.path.rstrip('/')
    except (ValueError, TypeError):
        return None


def extrair_email_publico(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    frames = []
    for script in soup.find_all('script'):
        match = re.fullmatch(r'self\.__next_f\.push\((.*)\)', script.get_text(), re.S)
        if match:
            try:
                frame = json.loads(match[1])
                if len(frame) == 2 and frame[0] == 1 and isinstance(frame[1], str):
                    frames.append(frame[1])
            except (ValueError, TypeError):
                pass
    stream = ''.join(frames)
    email = None
    for match in re.finditer(r'"email":\s*(\{)', stream):
        try:
            candidate, _ = json.JSONDecoder().raw_decode(stream[match.start(1):])
            if candidate.get('slug') == urlsplit(url).path.split('/')[-1]:
                email = candidate
                break
        except ValueError:
            pass
    if not email or not isinstance(email.get('html'), str):
        raise ValueError('Email original público indisponível')
    reference = email['html']
    match = re.search(re.escape(reference.lstrip('$')) + r':T([0-9a-f]+),', stream)
    if not reference.startswith('$') or not match:
        raise ValueError('Corpo público do email indisponível')
    length = int(match[1], 16)
    body = stream[match.end():].encode('utf-8')[:length].decode('utf-8')
    content = BeautifulSoup(body, 'html.parser')
    for item in content(['script', 'style', 'head']):
        item.decompose()
    text = content.get_text(' ', strip=True)
    text = ' '.join(''.join(c for c in text if unicodedata.category(c) != 'Cf').split())
    if len(text) < 100:
        raise ValueError('Email sem texto suficiente; não usar apenas assunto')
    description = BeautifulSoup(email.get('description') or '', 'html.parser').get_text(' ', strip=True)
    brand = (email.get('company') or {}).get('name', 'unknown')
    # No tracking links, third-party fetches or subscriber identifiers are retained.
    markdown = '# ' + email['title'] + '\nMarca informada pela curadoria: ' + brand
    markdown += '\nDescrição da fonte: ' + description + '\n## Texto do email publicado\n' + text
    return {'markdown': markdown}


def capturar_pagina(url):
    canonical = canonicalizar_ingestao(url)
    if not canonical:
        raise ValueError('Fonte não permitida')
    if canonical.startswith('https://swipefile.com/'):
        return capturar_swipefile(canonical)
    with requests.get(canonical, timeout=30, allow_redirects=False, stream=True) as response:
        response.raise_for_status()
        if response.status_code != 200:
            raise ValueError('Redirecionamento não permitido')
        chunks, total = [], 0
        for chunk in response.iter_content(65536):
            total += len(chunk)
            if total > MAX_PAGE_BYTES:
                raise ValueError('Página excede limite')
            chunks.append(chunk)
        return extrair_email_publico(b''.join(chunks).decode('utf-8'), canonical)
