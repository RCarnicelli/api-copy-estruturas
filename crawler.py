import os
import re
from html import unescape
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests

CRAWL4AI_API_URL = "https://api.crawl4ai.com/scrape"
SWIPEFILE_BASE = "https://swipefile.com"
EXCLUDED_ROOTS = {
    "category", "categories", "database", "tools", "popular", "random",
    "contact", "what-is-a-swipe-file", "business-idea-generator",
    "product-pricing-calculator", "gross-profit-calculator", "secret",
    "signup", "login", "logout", "about", "privacy", "privacy-policy",
    "terms", "terms-of-service", "search", "tag", "tags", "author",
    "api", "_next", "feed", "sitemap.xml", "robots.txt",
}


def validar_pagina_swipefile(url):
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname not in {"swipefile.com", "www.swipefile.com"}
            or parsed.username or parsed.password or parsed.port not in {None, 443}):
        raise ValueError("A descoberta aceita somente páginas HTTPS do Swipefile")
    return urlunsplit(("https", "swipefile.com", parsed.path or "/", parsed.query, ""))


def canonicalizar_swipe_url(link, base_url=SWIPEFILE_BASE + "/database"):
    """Return a candidate detail URL, excluding navigation and external links.

    Candidates still require content review before classification/curation.
    """
    if not isinstance(link, str):
        return None
    link = unescape(link).strip()
    if not link or link.startswith(("#", "?")):
        return None
    try:
        url = validar_pagina_swipefile(urljoin(base_url, link))
    except (ValueError, TypeError):
        return None
    parsed = urlsplit(url)
    path = parsed.path.rstrip("/")
    parts = path.lstrip("/").split("/")
    if not path or parts[0].lower() in EXCLUDED_ROOTS:
        return None
    # Actual Swipefile detail routes: /slug and /case/slug.
    if not (len(parts) == 1 or (len(parts) == 2 and parts[0] == "case")):
        return None
    if any(not re.fullmatch(r"[a-zA-Z0-9_-]+", part) for part in parts):
        return None
    return urlunsplit(("https", "swipefile.com", path, "", ""))


def capturar_pagina(url):
    api_key = os.environ.get("CRAWL4AI_API_KEY")
    if not api_key:
        raise RuntimeError("CRAWL4AI_API_KEY não configurada")
    response = requests.post(
        CRAWL4AI_API_URL, json={"url": url},
        headers={"Authorization": f"Bearer {api_key}"}, timeout=60,
    )
    response.raise_for_status()
    return response.json()


def _conteudos(resultado):
    """Support direct results and Crawl4AI result wrappers."""
    if not isinstance(resultado, dict):
        raise ValueError("Resposta inválida do crawler")
    if resultado.get("success") is False:
        raise ValueError("Crawler não conseguiu capturar a página")
    wrapped = resultado.get("results") or resultado.get("result") or resultado.get("data")
    if isinstance(wrapped, list):
        if not wrapped:
            raise ValueError("Crawler retornou resultado vazio")
        resultado = wrapped[0]
    elif isinstance(wrapped, dict):
        resultado = wrapped
    if not isinstance(resultado, dict) or resultado.get("success") is False:
        raise ValueError("Crawler não conseguiu capturar a página")
    markdown = resultado.get("markdown") or ""
    if isinstance(markdown, dict):
        markdown = markdown.get("raw_markdown") or markdown.get("fit_markdown") or ""
    html = resultado.get("html") or resultado.get("cleaned_html") or ""
    return str(markdown), str(html)


def normalizar_pagina(resultado, url):
    markdown, html = _conteudos(resultado)
    conteudo = markdown or html
    return {"source_url": url, "content": conteudo,
            "content_type": "markdown" if markdown else "html",
            "content_length": len(conteudo)}


def preparar_para_classificacao(pagina):
    return {"source_url": pagina.get("source_url"), "content": pagina.get("content", ""),
            "metadata": {"content_type": pagina.get("content_type"),
                         "content_length": pagina.get("content_length", 0)}}


class _LinksHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


def descobrir_links_swipefile(resultado, base_url=SWIPEFILE_BASE + "/database"):
    """Discover unique candidates only: no OpenAI calls or database writes."""
    base_url = validar_pagina_swipefile(base_url)
    markdown, html = _conteudos(resultado)
    # Ignore markdown images; include inline and reference-style links.
    links = re.findall(r'(?<!!)\[[^\]]*\]\(\s*<?([^\s)>]+)>?(?:\s+[^)]*)?\)', markdown)
    links += re.findall(r'^\s*\[[^\]]+\]:\s*<?([^\s>]+)>?', markdown, re.MULTILINE)
    parser = _LinksHTML()
    parser.feed(html)
    links.extend(parser.links)
    return list(dict.fromkeys(
        url for link in links
        if (url := canonicalizar_swipe_url(link, base_url))
    ))
