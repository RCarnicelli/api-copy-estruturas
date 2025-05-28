from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

SWIPES_DB = {
    "ads": [
        ("Pare de rolar. Comece a saborear.", "Swipe clássico para anúncios visuais."),
        ("Seu próximo clique pode ser o mais gostoso do dia.", "Call to action direto para conversão.")
    ],
    "emails": [
        ("Já pensou em algo diferente para o jantar?", "Linha de assunto que instiga curiosidade."),
        ("3 motivos para você amar nossa nova pizza.", "Estrutura em lista que aumenta abertura.")
    ],
    "quotes": [
        ("A pizza é a simplicidade feita arte.", "Frase de impacto para posts ou reels."),
        ("Menos ingredientes, mais verdade.", "Quote para reforço de autenticidade.")
    ],
    # ...adicione as demais categorias seguindo o mesmo padrão
}

@app.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = list(SWIPES_DB.keys())
    categorias_formatadas = [f"{i+1}. {categoria.capitalize()}" for i, categoria in enumerate(categorias)]
    return jsonify({
        "type": "lista",
        "title": "Categorias disponíveis",
        "itens": categorias_formatadas
    })

@app.route('/swipes', methods=['GET'])
def obter_swipes():
    categoria = request.args.get("categoria")
    swipes = SWIPES_DB.get(categoria, [])
    swipes_formatados = [f"{i+1}. \"{s[0]}\" — {s[1]}" for i, s in enumerate(swipes)]
    return jsonify({
        "type": "lista",
        "title": f"Swipes da categoria '{categoria}'",
        "itens": swipes_formatados
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
