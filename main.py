from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simulação do banco de dados com 20 categorias
SWIPES_DB = {
    "ads": ["Swipe A1", "Swipe A2"],
    "advice": ["Conselho 1", "Conselho 2"],
    "beforeandafter": ["Antes e Depois 1", "Antes e Depois 2"],
    "copywriting": ["Texto matador 1", "Texto matador 2"],
    "data": ["Dado 1", "Dado 2"],
    "directmail": ["Carta 1", "DM 2"],
    "emails": ["Email 1", "Email 2"],
    "images": ["Imagem 1", "Imagem 2"],
    "money": ["Gatilho financeiro 1", "Gatilho 2"],
    "motivation": ["Motivacional 1", "Frase forte"],
    "pricing": ["Âncora 1", "Justificativa 2"],
    "printads": ["Impresso 1", "Impresso 2"],
    "quotes": ["Frase 1", "Frase 2"],
    "salespages": ["Landing top", "Copy final"],
    "socialmedia": ["Post viral", "Story call"],
    "swipesemail": ["Nutrição 1", "Nutrição 2"],
    "testimonials": ["Depoimento real", "Review top"],
    "videos": ["Script 1", "Script 2"],
    "wisdom": ["Sabedoria 1", "Frase sábia 2"]
}

@app.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = []
    for categoria in SWIPES_DB:
        categorias.append({
            "title": categoria.capitalize(),
            "description": f"Exemplos disponíveis para a categoria '{categoria}'",
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

@app.route('/swipes', methods=['GET'])
def obter_swipes():
    categoria = request.args.get("categoria")
    swipes = SWIPES_DB.get(categoria, [])
    cards = []
    for swipe in swipes:
        cards.append({
            "title": swipe,
            "description": f"Swipe da categoria {categoria}",
            "button": {
                "text": "Usar esta frase",
                "action": "usarSwipe"
            }
        })
    return jsonify({
        "type": "cards",
        "title": f"Swipes da categoria '{categoria}'",
        "items": cards
    })

@app.route('/')
def home():
    return "API de swipes está online."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
