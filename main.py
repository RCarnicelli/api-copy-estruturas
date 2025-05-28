from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # Libera o CORS para consumo externo

# Base de dados de swipes por categoria
SWIPES_DB = {
    "ads": [{"title": "Anúncio que converte", "description": "Modelo direto ao ponto para vendas rápidas", "button": {"text": "Usar este anúncio", "action": "usarSwipe"}}],
    "advice": [{"title": "Dica de ouro", "description": "Use provas sociais para fortalecer sua copy", "button": {"text": "Aplicar dica", "action": "usarSwipe"}}],
    "beforeandafter": [{"title": "Antes: problema. Depois: solução", "description": "Mostre a transformação", "button": {"text": "Usar estrutura", "action": "usarSwipe"}}],
    "copywriting": [{"title": "Você achava que X era bom...", "description": "Crie contraste e desejo", "button": {"text": "Gerar variação", "action": "usarSwipe"}}],
    "data": [{"title": "Dados não mentem", "description": "Comece sua copy com um dado chocante", "button": {"text": "Usar dado", "action": "usarSwipe"}}],
    "directmail": [{"title": "Mensagem direta", "description": "Modelo para conversão via e-mail físico", "button": {"text": "Usar este modelo", "action": "usarSwipe"}}],
    "emails": [{"title": "Assunto irresistível", "description": "Modelo de email com alta taxa de abertura", "button": {"text": "Enviar e-mail", "action": "usarSwipe"}}],
    "images": [{"title": "Imagem que vende", "description": "Sugestão de visual para campanha", "button": {"text": "Gerar imagem", "action": "usarSwipe"}}],
    "money": [{"title": "Fale de dinheiro", "description": "Swipe que ativa o gatilho financeiro", "button": {"text": "Usar esse apelo", "action": "usarSwipe"}}],
    "motivation": [{"title": "Inspire para vender", "description": "Modelo com apelo emocional", "button": {"text": "Usar inspiração", "action": "usarSwipe"}}],
    "pricing": [{"title": "Preço irresistível", "description": "Swipe com ancoragem de valor", "button": {"text": "Aplicar oferta", "action": "usarSwipe"}}],
    "printads": [{"title": "Anúncio impresso eficaz", "description": "Modelo clássico de jornal ou revista", "button": {"text": "Usar esse anúncio", "action": "usarSwipe"}}],
    "quotes": [{"title": "“A pizza é a simplicidade feita arte”", "description": "Frases de impacto", "button": {"text": "Usar citação", "action": "usarSwipe"}}],
    "salespages": [{"title": "Landing page vendedora", "description": "Estrutura de página de vendas", "button": {"text": "Usar estrutura", "action": "usarSwipe"}}],
    "socialmedia": [{"title": "Essa pizza não é pra todo mundo", "description": "Swipe provocador para Instagram", "button": {"text": "Usar esse tom", "action": "usarSwipe"}}],
    "swipesemail": [{"title": "Sequência de e-mails", "description": "Modelo completo de funil", "button": {"text": "Usar sequência", "action": "usarSwipe"}}],
    "testimonials": [{"title": "Depoimento de impacto", "description": "Modelo de prova social", "button": {"text": "Usar depoimento", "action": "usarSwipe"}}],
    "videos": [{"title": "Vídeo que prende atenção", "description": "Estrutura para reels e TikToks", "button": {"text": "Criar vídeo", "action": "usarSwipe"}}],
    "wisdom": [{"title": "Sabedoria aplicada ao marketing", "description": "Swipe reflexivo com gancho comercial", "button": {"text": "Usar insight", "action": "usarSwipe"}}]
}

@app.route('/')
def home():
    return "API de swipes está no ar!"

@app.route('/swipes', methods=['GET'])
def swipes():
    categoria = request.args.get("categoria", "copywriting")
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

@app.route('/estruturas/cards', methods=['GET'])
def obter_estrutura_copy_card():
    categoria = request.args.get("categoria", "").lower()
    if not categoria:
        return jsonify({"erro": "Categoria não informada"}), 400

    # Caso especial: buscar no Swipefile.com se for advice (ou qualquer outra que queira adicionar depois)
    if categoria == "advice":
        try:
            url = f"https://swipefile.com/category/{categoria}"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                return jsonify({"erro": "Não foi possível acessar a categoria externa"}), 500

            soup = BeautifulSoup(response.content, 'html.parser')
            swipes = []
            cards = soup.select("article h2 a")
            descricoes = soup.select("article p")

            for i in range(min(3, len(cards))):
                titulo = cards[i].get_text(strip=True)
                descricao = descricoes[i].get_text(strip=True) if i < len(descricoes) else "Swipe sem descrição detalhada."
                swipes.append({
                    "title": titulo,
                    "description": descricao,
                    "button": {
                        "text": "Usar esta estrutura",
                        "action": "usarSwipe"
                    }
                })

            return jsonify({
                "type": "cards",
                "title": f"Melhores Estruturas para {categoria.capitalize()}",
                "items": swipes
            })
        except Exception as e:
            return jsonify({"erro": f"Erro ao buscar estruturas: {str(e)}"}), 500

    # Fallback: retorna do SWIPES_DB se não for externa
    return jsonify({
        "type": "cards",
        "title": f"Estrutura sugerida para {categoria}",
        "items": SWIPES_DB.get(categoria, [])
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
