"""Explicit, bounded ingestion of reviewed Swipefile candidate URLs."""
import time

from crawler import capturar_pagina, normalizar_pagina, canonicalizar_swipe_url
from classifier import classificar_swipe
from swipe_repository import buscar_swipe_por_url, salvar_swipe, bloquear_ingestao

MAX_BATCH_SIZE = 3
MAX_SUBMITTED_URLS = 100
MAX_BATCH_SECONDS = 150


class IngestionBusy(RuntimeError):
    pass


def validar_lote(urls, limite=1, dry_run=True):
    if not isinstance(urls, list) or not 1 <= len(urls) <= MAX_SUBMITTED_URLS:
        raise ValueError("Informe de 1 a 100 URLs selecionadas")
    if isinstance(limite, bool) or not isinstance(limite, int) or not 1 <= limite <= MAX_BATCH_SIZE:
        raise ValueError("O limite deve ser um inteiro de 1 a 3")
    if not isinstance(dry_run, bool):
        raise ValueError("dry_run deve ser booleano")
    canonical = []
    for url in urls:
        if not isinstance(url, str) or len(url) > 2048:
            raise ValueError("URL inválida")
        # Batch accepts absolute detail URLs only; never crawl arbitrary hosts.
        if not url.startswith("https://") or not (normalized := canonicalizar_swipe_url(url)):
            raise ValueError("O lote aceita somente URLs individuais HTTPS do Swipefile")
        canonical.append(normalized)
    return list(dict.fromkeys(canonical))


def processar_lote(urls, limite=1, dry_run=True):
    unique = validar_lote(urls, limite, dry_run)
    response = {
        "status": "ok", "modo": "simulacao" if dry_run else "processamento",
        "descobertos": len(unique), "processados": 0, "ignorados": len(urls) - len(unique),
        "duplicados_entrada": len(urls) - len(unique), "chamadas_openai": 0,
        "limite": limite, "planejados": [], "resultados": [], "erros": [],
    }

    def run():
        attempted = 0
        start = time.monotonic()
        for url in unique:
            stage = "consulta_existente"
            try:
                existing = buscar_swipe_por_url(url)
                if existing:
                    response["ignorados"] += 1
                    response["resultados"].append({"url": url, "status": "existente", "id": existing})
                    continue
                if attempted >= limite or time.monotonic() - start >= MAX_BATCH_SECONDS:
                    response["ignorados"] += 1
                    response["resultados"].append({"url": url, "status": "adiado_por_limite"})
                    continue
                attempted += 1  # Failures consume the limit too; never retry automatically.
                if dry_run:
                    response["planejados"].append(url)
                    continue
                stage = "captura"
                raw = capturar_pagina(url)
                page = normalizar_pagina(raw, url)
                if len(page["content"].strip()) < 100:
                    raise ValueError("Conteúdo insuficiente")
                if time.monotonic() - start >= MAX_BATCH_SECONDS:
                    response["ignorados"] += 1
                    response["resultados"].append({"url": url, "status": "adiado_por_tempo"})
                    continue
                stage = "classificacao"
                response["chamadas_openai"] += 1  # Count attempted calls, including failures.
                classified = classificar_swipe(page)
                stage = "persistencia"
                swipe_id = salvar_swipe(classified)
                response["processados"] += 1
                response["resultados"].append({"url": url, "status": "processado", "id": swipe_id})
            except Exception:
                # Never return provider error bodies, credentials or connection strings.
                response["erros"].append({"url": url, "etapa": stage, "erro": "Falha individual"})
        response["total_erros"] = len(response["erros"])
        if response["erros"]:
            response["status"] = "parcial" if response["processados"] or response["planejados"] else "erro"
        return response

    if dry_run:
        return run()
    with bloquear_ingestao() as acquired:
        if not acquired:
            raise IngestionBusy("Já existe uma ingestão em andamento")
        return run()
