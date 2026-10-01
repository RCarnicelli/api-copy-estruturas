from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup
from swipes_db import SWIPES_DB

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "API de swipes está no ar!"

@app.route('/swipes', methods=['GET'])
def swipes():
    categoria = request.args.get("categoria", "copywriting").lower()
    print(f"[DEBUG] /swipes requisitado com categoria: {categoria}")
    itens = SWIPES_DB.get(categoria, [])
    return jsonify({
        "type": "cards",
        "title": f"Swipes da categoria: {categoria}",
        "items": itens
    })

@app.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = list(SWIPES_DB.keys())
    categorias_ordenadas = sorted(categorias)
    lista_texto = "\n".join([f"{i+1}. {categoria.capitalize()}" for i, categoria in enumerate(categorias_ordenadas)])
    print("[DEBUG] /categorias requisitado")
    return jsonify({
        "type": "text",
        "content": f"Escolha uma categoria digitando o número correspondente:\n\n{lista_texto}"
    })

@app.route('/estruturas/cards', methods=['GET'])
def obter_estrutura_copy_card():
    categoria = request.args.get("categoria", "").lower()
    print(f"[DEBUG] /estruturas/cards requisitado com categoria: {categoria}")

    if not categoria:
        return jsonify({"erro": "Categoria não informada"}), 400

    if categoria == "advice":
        try:
            url = f"https://swipefile.com/category/{categoria}"
            print(f"[DEBUG] Acessando URL externa: {url}")
            response = requests.get(url, timeout=10)
            print(f"[DEBUG] Status da resposta: {response.status_code}")

            if response.status_code != 200:
                return jsonify({"erro": "Não foi possível acessar a categoria externa"}), 500

            soup = BeautifulSoup(response.text, 'html.parser')
            cards = soup.find_all("h2")
            descricoes = soup.find_all("p")

            if not cards:
                print("[DEBUG] Nenhum título encontrado na estrutura da página.")
                return jsonify({"erro": "Estrutura da página não reconhecida ou vazia"}), 500

            swipes = []
            for i in range(min(3, len(cards))):
                titulo = cards[i].get_text(strip=True) if cards[i] else "Sem título"
                descricao = descricoes[i].get_text(strip=True) if i < len(descricoes) else "Swipe sem descrição."
                swipes.append({
                    "title": titulo,
                    "description": descricao,
                    "button": {
                        "text": "Usar esta estrutura",
                        "action": "usarSwipe"
                    }
                })

            return jsonify({
                "type": "cards",
                "title": f"Melhores Estruturas para {categoria.capitalize()}",
                "items": swipes
            })
        except Exception as e:
            print(f"[ERROR] Erro ao acessar Swipefile: {e}")
            return jsonify({"erro": f"Erro ao buscar estruturas: {str(e)}"}), 500

    # fallback para base local
    itens = SWIPES_DB.get(categoria, [])
    return jsonify({
        "type": "cards",
        "title": f"Estrutura sugerida para {categoria}",
        "items": itens
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
