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


def preparar_para_classificacao(pagina):
    """Prepara o conteúdo normalizado para a etapa de classificação por IA."""
    return {
        "source_url": pagina.get("source_url"),
        "content": pagina.get("content", ""),
        "metadata": {
            "content_type": pagina.get("content_type"),
            "content_length": pagina.get("content_length", 0),
        },
    }
def descobrir_links_swipefile(resultado):
    """Extrai links de swipes individuais encontrados em uma página do Swipefile."""
    markdown = resultado.get("markdown") or ""

    import re

    links = re.findall(
    r'\]\((https://swipefile\.com/[^)\s]+|/[^)\s]+)\)',
    markdown
)

links = [
    "https://swipefile.com" + link if link.startswith("/") else link
    for link in links
]

    ignorar = (
        "/category/",
        "/categories",
        "/database",
        "/tools",
        "/popular/",
        "/random",
        "/contact",
        "/what-is-a-swipe-file",
        "/business-idea-generator",
        "/product-pricing-calculator",
        "/gross-profit-calculator",
    )

    links_validos = []

    for link in links:
        link = link.split("?")[0]

        if any(item in link for item in ignorar):
            continue

        if link not in links_validos:
            links_validos.append(link)

    return links_validos
