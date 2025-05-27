from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

estruturas = [
    {
        "estrutura": "AIDA",
        "justificativa": "Ideal para atrair atenção e guiar até a ação — funciona bem para posts diretos e anúncios.",
    },
    {
        "estrutura": "PAS",
        "justificativa": "Foca na dor, amplifica o problema e oferece solução — ótima para despertar urgência.",
    },
    {
        "estrutura": "BAB",
        "justificativa": "Mostra o antes, depois e a ponte — excelente para gerar empatia e apresentar transformações.",
    },
    {
        "estrutura": "4Ps",
        "justificativa": "Promessa, Prova, Proposta e Pedido — bom para landing pages ou textos comerciais.",
    }
]

@app.route('/estruturas/cards', methods=['GET'])
def obter_estrutura_cards():
    tipo = request.args.get('tipo')
    objetivo = request.args.get('objetivo')
    emocao = request.args.get('emocao', '')

    cards = []

    for estrutura in estruturas:
        card = {
            "title": estrutura["estrutura"],
            "description": estrutura["justificativa"],
            "button": {
                "text": "Usar esta estrutura",
                "action": "usarFramework"
            }
        }
        cards.append(card)

    if not cards:
        return jsonify({"type": "text", "text": "Não encontrei estrutura ideal, mas posso sugerir uma se quiser."})

    return jsonify({
        "type": "cards",
        "title": "Framework sugerido",
        "items": cards
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

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
