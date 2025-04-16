from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/estruturas")
def obter_estrutura_copy():
    tipo = request.args.get("tipo")
    
    estruturas = {
        "post": {
            "estrutura": "BAB (Before – After – Bridge)",
            "justificativa": "Ideal para engajamento e identificação do público com a mensagem."
        },
        "anuncio": {
            "estrutura": "AIDA (Atenção, Interesse, Desejo, Ação)",
            "justificativa": "Perfeita para capturar atenção rapidamente e gerar ação."
        },
        "email": {
            "estrutura": "PAS (Problema, Agitação, Solução)",
            "justificativa": "Funciona bem para nutrir leads e manter atenção."
        }
    }

    resultado = estruturas.get(tipo.lower(), {
        "estrutura": "AIDA",
        "justificativa": "Estrutura padrão para diversos tipos de conteúdo."
    })

    return jsonify(resultado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/estruturas", methods=["GET"])
def obter_estrutura_copy():
    return jsonify({
        "estrutura": "BAB",
        "justificativa": "Ideal para engajar com transformação: mostra o antes, o depois e como chegar lá."
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/estruturas/cards", methods=["GET"])
def obter_estrutura_copy_card():
    tipo = request.args.get("tipo")
    objetivo = request.args.get("objetivo")
    emocao = request.args.get("emocao", "")

    # Exemplo fixo (substitua pela sua lógica real)
    estrutura = "AIDA"
    justificativa = "Ideal para capturar atenção e guiar o leitor até a ação."

    return jsonify({
        "type": "cards",
        "title": "Framework sugerido",
        "items": [
            {
                "title": estrutura,
                "description": justificativa,
                "button": {
                    "text": "Usar esta estrutura",
                    "action": "usarFramework"
                }
            }
        ]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

