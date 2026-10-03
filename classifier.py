import os
import json
import requests

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/responses"
MAX_CONTENT_CHARS = 12000
MAX_OUTPUT_TOKENS = 2000


def classificar_swipe(pagina):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY não configurada")

    original = pagina.get("content", "")
    if not isinstance(original, str) or not original.strip():
        raise ValueError("Conteúdo vazio para classificação")
    conteudo = original[:MAX_CONTENT_CHARS]

    prompt = f"""
Você é um especialista em copywriting, publicidade e análise de swipe files.

Analise o swipe fornecido e retorne SOMENTE um objeto JSON válido.
Não use markdown, não use ```json e não escreva explicações fora do JSON.

Use exatamente esta estrutura:
{{
    "category": "categoria principal do swipe",
    "title": "título curto que identifica o swipe",
    "description": "resumo objetivo da peça",
    "framework": "framework ou estrutura de copy identificada",
    "hook": "principal gancho utilizado",
    "objective": ["objetivo principal", "objetivo secundário"],
    "emotion": ["emoção principal", "emoção secundária"],
    "tone": ["tom principal", "tom secundário"],
    "mechanism": "mecanismo persuasivo central",
    "cta": "call to action identificado, ou vazio se não existir",
    "why_it_works": "explicação objetiva de por que a peça funciona",
    "adaptation": "como essa estrutura pode ser adaptada para outras marcas e ofertas",
    "tags": ["tag1", "tag2", "tag3"]
}}

Para "category", escolha somente UMA destas categorias:
ads, advice, before-and-after, business-ideas, copywriting, data,
direct-mail, emails, images, money, motivation, pricing, print-ads,
quotes, sales-pages, social, swipes-email, testimonials, videos, wisdom.

Escolha a categoria com base no conteúdo e no formato principal da peça.
Não invente uma categoria fora dessa lista.

Baseie a análise somente no conteúdo fornecido.
Não invente informações ausentes.

SWIPE:
{conteudo}
"""

    payload = {
        "model": "gpt-6-luna",
        "input": prompt,
        "max_output_tokens": MAX_OUTPUT_TOKENS,
    }

    response = requests.post(
        OPENAI_API_URL,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )

    if not response.ok:
        raise RuntimeError(
            f"OpenAI retornou HTTP {response.status_code}"
        )

    response.raise_for_status()

    resultado = response.json()
    if resultado.get("status") == "incomplete":
        raise ValueError("Classificação incompleta; nenhuma gravação realizada")
    texto = "".join(
        part.get("text", "")
        for item in resultado.get("output", []) if item.get("type") == "message"
        for part in item.get("content", []) if part.get("type") == "output_text"
    )
    classificacao = json.loads(texto)
    if not isinstance(classificacao, dict):
        raise ValueError("Classificação inválida")

    classificacao["source_url"] = pagina.get("source_url")
    classificacao["original_content"] = original

    return classificacao
