
from flask import Flask, request, jsonify

app = Flask(__name__)

estruturas = {
    "posts": {
        "estrutura": "AIDA",
        "justificativa": "Ideal para prender a atenção no feed e conduzir o leitor até uma ação."
    },
    "anúncios": {
        "estrutura": "PAS",
        "justificativa": "Ótimo para anúncios que precisam despertar dor e apresentar solução de forma rápida."
    },
    "roteiros": {
        "estrutura": "4Ps",
        "justificativa": "Ajuda a construir uma linha narrativa envolvente com começo, meio e fim claros."
    },
    "e-mails": {
        "estrutura": "BAB",
        "justificativa": "Mostra o antes, depois e ponte de transformação, excelente para sequências de e-mail marketing."
    },
    "landing pages": {
        "estrutura": "FAB",
        "justificativa": "Perfeito para mostrar funcionalidades, vantagens e benefícios de forma lógica."
    }
}

@app.route("/estruturas", methods=["GET"])
def get_estrutura():
    tipo = request.args.get("tipo", "").lower()
    estrutura = estruturas.get(tipo)
    if estrutura:
        return jsonify(estrutura)
    else:
        return jsonify({"erro": "Tipo de conteúdo não encontrado"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
