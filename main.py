from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

SWIPES_DB = {
    "ads": [],
    "advice": [],
    "beforeandafter": [],
    "copywriting": [],
    "data": [],
    "directmail": [],
    "emails": [],
    "images": [],
    "money": [],
    "motivation": [],
    "pricing": [],
    "printads": [],
    "quotes": [],
    "salespages": [],
    "socialmedia": [],
    "swipesemail": [],
    "testimonials": [],
    "videos": [],
    "wisdom": []
}

@app.route('/')
def home():
    return "API de swipes está no ar!"

@app.route('/swipes', methods=['GET'])
def swipes():
    categoria = request.args.get("categoria", "").lower()
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
    return jsonify({
        "type": "text",
        "content": f"Escolha uma categoria digitando o número correspondente:\n\n{lista_texto}"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
