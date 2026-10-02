import os
import requests


CRAWL4AI_API_URL = "https://api.crawl4ai.com/scrape"


def capturar_pagina(url):
    api_key = os.environ.get("CRAWL4AI_API_KEY")

    if not api_key:
        raise RuntimeError("CRAWL4AI_API_KEY não configurada")

    response = requests.post(
        CRAWL4AI_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data='{"url": ' + '"' + url + '"' + '}',
        timeout=60,
    )

    response.raise_for_status()
    return response.json()
