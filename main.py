from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Banco de dados simulado
SWIPES_DB = {
    "emails": [
        {
            "title": "📬 Chegou a hora de abrir!",
            "description": "Exemplo de título usado para aumentar taxa de abertura de email.",
            "button": {
                "text": "Usar esta frase",
                "action": "usarSwipe"
            }
        },
        {
            "title": "📢 Última chance para garantir sua vaga",
            "description": "Swipe com senso de urgência para email de fechamento de campanha.",
            "button": {
                "text": "Usar esta frase",
                "action": "usarSwipe"
            }
        }
    ],
    "ads": [
        {
            "title": "🧲 Pare de rolar. Comece a saborear.",
            "description": "Swipe clássico para interromper padrão em anúncios visuais.",
            "button": {
                "text": "Usar no meu anúncio",
                "action": "usarSwipe"
            }
        }
    ],
    "quotes": [
        {
            "title": "“A pizza é a simplicidade feita arte”",
            "description": "Frase de impacto para abertura ou CTA.",
            "button": {
                "text": "Usar esta frase",
                "action": "usarSwipe"
            }
        }
    ],
    "copywriting": [],
    "socialmedia": []
}

# Rota /categorias
@app.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = []
    for categoria in SWIPES_DB:
        categorias.append({
            "title": categoria.replace("swipes", "").replace("email", "Emails").capitalize(),
            "description": f"Exemplos para campanhas, posts ou anúncios em {categoria}",
            "button": {
                "text": "Ver exemplos",
                "action": {
                    "type": "invoke",
                    "name": "obterSwipesPorCategoria",
                    "parameters": {
                        "categoria": categoria
                    }
                }
            }
        })
    return jsonify({
        "type": "cards",
        "title": "Categorias disponíveis",
        "items": categorias
    })

# Rota /swipes
@app.route('/swipes', methods=['GET'])
def obter_swipes_por_categoria():
    categoria = request.args.get('categoria', '')
    swipes = SWIPES_DB.get(categoria.lower(), [])
    return jsonify({
        "type": "cards",
        "title": f"Swipes da categoria {categoria.capitalize()}",
        "items": swipes
    })

# Rota /estruturas/cards
@app.route('/estruturas/cards', methods=['GET'])
def obter_estrutura_cards():
    tipo = request.args.get('tipo', '')
    objetivo = request.args.get('objetivo', '')
    emocao = request.args.get('emocao', '')

    estruturas = [
        {
            "title": "AIDA",
            "description": "Ideal para atrair atenção e guiar até a ação — ótimo para anúncios e reels.",
            "button": {
                "text": "Usar esta estrutura",
                "action": "usarFramework"
            }
        },
        {
            "title": "PAS",
            "description": "Foca na dor e na solução. Funciona muito bem para criar urgência.",
            "button": {
                "text": "Usar esta estrutura",
                "action": "usarFramework"
            }
        }
    ]

    return jsonify({
        "type": "cards",
        "title": "Framework sugerido",
        "items": estruturas
    })

# Roda localmente (apenas para testes locais)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
