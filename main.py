from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Lista de estruturas de copy (exemplo simplificado)
estruturas = {
    "post": {
        "venda": {
            "estrutura": "AIDA",
            "justificativa": "Ideal para guiar a atenção do público até a ação de compra."
        },
        "engajamento": {
            "estrutura": "BAB",
            "justificativa": "Cria conexão emocional ao mostrar uma transformação desejada."
        }
    },
    "anúncio": {
        "venda": {
            "estrutura": "PAS",
            "justificativa": "Chama atenção pelo problema e termina com a solução."
        }
    },
    "landing page": {
        "geração de leads": {
            "estrutura": "4Ps",
            "justificativa": "Clareza sobre produto, promessa, prova e proposta."
        }
    }
}

# 🎯 ROTA SIMPLES: /estruturas
@app.route("/estruturas", methods=["GET"])
def obter_estrutura_copy():
    tipo = request.args.get("tipo", "").lower()
    objetivo = request.args.get("objetivo", "").lower()

    estrutura = estruturas.get(tipo, {}).get(objetivo)

    if estrutura:
        return jsonify(estrutura)
    else:
        return jsonify({"erro": "Estrutura não encontrada"}), 404

# 💳 ROTA EM FORMATO DE CARD: /estruturas/cards
@app.route("/estruturas/cards", methods=["GET"])
def obter_estrutura_copy_card():
    tipo = request.args.get("tipo", "").lower()
    objetivo = request.args.get("objetivo", "").lower()

    estrutura = estruturas.get(tipo, {}).get(objetivo)

    if estrutura:
        card = {
            "type": "cards",
            "title": "Framework sugerido",
            "items": [
                {
                    "title": estrutura["estrutura"],
                    "description": estrutura["justificativa"],
                    "button": {
                        "text": "Usar esta estrutura",
                        "action": "usarFramework"
                    }
                }
            ]
        }
        return jsonify(card)
    else:
        return jsonify({"erro": "Estrutura não encontrada"}), 404

# 🟢 Executar app na porta exigida pelo Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

