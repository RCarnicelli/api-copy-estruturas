import os
import requests


CRAWL4AI_API_URL = "https://api.crawl4ai.com/scrape"


def capturar_pagina(url):
    api_key = os.environ.get("CRAWL4AI_API_KEY")

    if not api_key:
        raise RuntimeError("CRAWL4AI_API_KEY não configurada")

    response = requests.post(
        CRAWL4AI_API_URL,
        data=('{"url": "' + url + '"}').encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8",
        },
        timeout=60,
    )

    response.raise_for_status()
    return response.json()


def normalizar_pagina(resultado, url):
    """Transforma a resposta bruta do Crawl4AI em conteúdo útil."""
    markdown = resultado.get("markdown") or ""
    html = resultado.get("html") or ""

    conteudo = markdown if markdown else html

    return {
        "source_url": url,
        "content": conteudo,
        "content_type": "markdown" if markdown else "html",
        "content_length": len(conteudo),
    }
