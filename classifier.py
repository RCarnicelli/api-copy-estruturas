import os
import json
def classificar_swipe(pagina):
    """
    Estrutura inicial de classificação de um swipe.
    A classificação por IA será conectada na próxima etapa.
    """

    conteudo = pagina.get("content", "")

    return {
        "source_url": pagina.get("source_url"),
        "title": "",
        "description": "",
        "framework": "",
        "hook": "",
        "objective": [],
        "emotion": [],
        "tone": [],
        "mechanism": "",
        "cta": "",
        "why_it_works": "",
        "adaptation": "",
        "tags": [],
        "original_content": conteudo,
    }
