from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SWIPES_DB = {
    "ads": ["Swipe de Ads 1", "Swipe de Ads 2"],
    "advice": ["Swipe de Advice 1", "Swipe de Advice 2"],
    "beforeandafter": ["Swipe de Before and After 1", "Swipe de Before and After 2"],
    "copywriting": ["Swipe de Copywriting 1", "Swipe de Copywriting 2"],
    "data": ["Swipe de Data 1", "Swipe de Data 2"],
    "directmail": ["Swipe de Direct Mail 1", "Swipe de Direct Mail 2"],
    "emails": ["Swipe de Emails 1", "Swipe de Emails 2"],
    "images": ["Swipe de Images 1", "Swipe de Images 2"],
    "money": ["Swipe de Money 1", "Swipe de Money 2"],
    "motivation": ["Swipe de Motivation 1", "Swipe de Motivation 2"],
    "pricing": ["Swipe de Pricing 1", "Swipe de Pricing 2"],
    "printads": ["Swipe de Print Ads 1", "Swipe de Print Ads 2"],
    "quotes": ["Swipe de Quotes 1", "Swipe de Quotes 2"],
    "salespages": ["Swipe de Sales Pages 1", "Swipe de Sales Pages 2"],
    "socialmedia": ["Swipe de Social Media 1", "Swipe de Social Media 2"],
    "swipesemail": ["Swipe de Swipes Email 1", "Swipe de Swipes Email 2"],
    "testimonials": ["Swipe de Testimonials 1", "Swipe de Testimonials 2"],
    "videos": ["Swipe de Videos 1", "Swipe de Videos 2"],
    "wisdom": ["Swipe de Wisdom 1", "Swipe de Wisdom 2"]
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
                    "name": "verSwipesCategoria",
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
    return jsonify({
        "type": "cards",
        "title": f"Swipes da categoria '{categoria}'",
        "items": [
            {
                "title": swipe,
                "description": f"Swipe da categoria {categoria}",
                "button": {
                    "text": "Usar esta frase",
                    "action": "usarSwipe"
                }
            } for swipe in swipes
        ]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
