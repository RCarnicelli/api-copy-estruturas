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
