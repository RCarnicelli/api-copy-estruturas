from flask import request, jsonify

# Simulação de base de dados de swipes por categoria
SWIPES_DB = {
    "copywriting": [
        {
            "title": "Você achava que X era bom...",
            "description": "Crie desejo mostrando um contraste direto com algo melhor.",
            "button": {
                "text": "Gerar variação com esse swipe",
                "action": "usarSwipe"
            }
        }
    ],
    "quotes": [
        {
            "title": "“A pizza é a simplicidade feita arte”",
            "description": "Frases de impacto para usar em posts e reels",
            "button": {
                "text": "Usar esta frase",
                "action": "usarSwipe"
            }
        }
    ],
    "advice": [
        {
            "title": "Mostre, não diga",
            "description": "Use storytelling sensorial ao invés de adjetivos clichês.",
            "button": {
                "text": "Gerar exemplo disso",
                "action": "usarSwipe"
            }
        }
    ],
    "socialmedia": [
        {
            "title": "Essa pizza não é pra todo mundo",
            "description": "Swipe de provocação para campanhas no Instagram",
            "button": {
                "text": "Usar esse tom",
                "action": "usarSwipe"
            }
        }
    ]
}

@app.route('/swipes', methods=['GET'])
def swipes():
    categoria = request.args.get("categoria", "copywriting")
    itens = SWIPES_DB.get(categoria, [])
    return jsonify({
        "type": "cards",
        "title": f"Swipes da categoria: {categoria}",
        "items": itens
    })
feat: adiciona endpoint /swipes com múltiplas categorias
# -------------------------------
# Novo endpoint de swipes por categoria
# -------------------------------

SWIPES_DB = {
    "copywriting": [
        {
            "title": "Você achava que X era bom...",
            "description": "Crie desejo mostrando um contraste direto com algo melhor.",
            "button": {
                "text": "Gerar variação com esse swipe",
                "action": "usarSwipe"
            }
        }
    ],
    "quotes": [
        {
            "title": "“A pizza é a simplicidade feita arte”",
            "description": "Frases de impacto para usar em posts e reels",
            "button": {
                "text": "Usar esta frase",
                "action": "usarSwipe"
            }
        }
    ],
    "advice": [
        {
            "title": "Mostre, não diga",
            "description": "Use storytelling sensorial ao invés de adjetivos clichês.",
            "button": {
                "text": "Gerar exemplo disso",
                "action": "usarSwipe"
            }
        }
    ],
    "socialmedia": [
        {
            "title": "Essa pizza não é pra todo mundo",
            "description": "Swipe de provocação para campanhas no Instagram",
            "button": {
                "text": "Usar esse tom",
                "action": "usarSwipe"
            }
        }
    ]
}

@app.route('/swipes', methods=['GET'])
def swipes():
    categoria = request.args.get("categoria", "copywriting")
    itens = SWIPES_DB.get(categoria, [])
    return jsonify({
        "type": "cards",
        "title": f"Swipes da categoria: {categoria}",
        "items": itens
    })
