import os
import json
import requests
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/responses"
def classificar_swipe(pagina):
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY não configurada")
    conteudo = pagina.get("content", "")

    prompt = f"""
Você é um especialista em copywriting, publicidade e análise de swipe files.

Analise o swipe fornecido e retorne SOMENTE um objeto JSON válido.
Não use markdown, não use ```json e não escreva explicações fora do JSON.

Use exatamente esta estrutura:
{{
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

Baseie a análise somente no conteúdo fornecido. Não invente informações ausentes.

SWIPE:
{conteudo}
"""
    payload = {
"model": "gpt-6-luna",
        "input": prompt,
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
    raise RuntimeError(f"OpenAI erro {response.status_code}: {response.text}")
    response.raise_for_status()
    resultado = response.json()
    texto = resultado["output"][0]["content"][0]["text"]
    classificacao = json.loads(texto)
    classificacao["source_url"] = pagina.get("source_url")
    classificacao["original_content"] = conteudo

    return classificacao
