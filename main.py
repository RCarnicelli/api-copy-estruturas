from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup
from swipes_db import SWIPES_DB
from search_engine import buscar_swipes
import psycopg
from seed_db import seed_database
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
@app.route('/buscar-swipes', methods=['GET'])
def buscar_swipes_endpoint():
    categoria = request.args.get("categoria")
    objetivo = request.args.get("objetivo")
    emocao = request.args.get("emocao")
    tom = request.args.get("tom")
    limite = request.args.get("limite", 5)

    resultados = buscar_swipes(
        categoria=categoria,
        objetivo=objetivo,
        emocao=emocao,
        tom=tom,
        limite=limite
    )

    return jsonify({
        "type": "cards",
        "title": "Swipes recomendados para o briefing",
        "filters": {
            "categoria": categoria,
            "objetivo": objetivo,
            "emocao": emocao,
            "tom": tom
        },
        "total": len(resultados),
        "items": resultados
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
@app.route('/db-status', methods=['GET'])
def db_status():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        return jsonify({
            "status": "erro",
            "database": "nao_configurado"
        }), 500

    try:
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM swipes;")
                total = cursor.fetchone()[0]

        return jsonify({
            "status": "ok",
            "database": "postgresql",
            "tabela": "swipes",
            "total_swipes": total
        })

    except Exception as e:
        return jsonify({
            "status": "erro",
            "database": "postgresql",
            "detalhe": str(e)
        }), 500
@app.route('/seed-db', methods=['GET'])
def seed_db():
    try:
        seed_database()
        return jsonify({
            "status": "ok",
            "message": "Seed do PostgreSQL concluído"
        })
    except Exception as e:
        return jsonify({
            "status": "erro",
            "detalhe": str(e)
        }), 500
      if __name__ == '__main__':
          port = int(os.environ.get("PORT", 10000))
          app.run(host='0.0.0.0', port=port)
