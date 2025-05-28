from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SWIPES_DB = {
    "ads": ["Swipe 1", "Swipe 2"],
    "emails": ["Exemplo A", "Exemplo B"],
    "quotes": ["Frase impactante", "Outra frase"],
    "videos": ["Roteiro 1", "Roteiro 2"],
    # Adicione as demais categorias aqui
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
