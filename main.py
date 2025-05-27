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
  "ads": [
    {
      "title": "Pare de rolar. Comece a saborear.",
      "description": "Swipe clássico para interromper padrão em anúncios visuais.",
      "button": {
        "text": "Usar no meu anúncio",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Quem ama pizza vai entender.",
      "description": "Swipe de identificação usado para engajamento instantâneo.",
      "button": {
        "text": "Adaptar esse",
        "action": "usarSwipe"
      }
    }
  ],
  "advice": [
    {
      "title": "Fale como um humano, não como um anúncio.",
      "description": "Swipe orientativo para tom de voz mais autêntico.",
      "button": {
        "text": "Quero essa dica",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Mostre o benefício, não o processo.",
      "description": "Foco no resultado final desejado.",
      "button": {
        "text": "Aplicar esse foco",
        "action": "usarSwipe"
      }
    }
  ],
  "beforeandafter": [
    {
      "title": "Antes: Estresse. Depois: Massa leve e crocante.",
      "description": "Swipe clássico para mostrar transformação com contraste.",
      "button": {
        "text": "Quero usar esse contraste",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Era uma pizza qualquer. Agora é sua favorita.",
      "description": "Transformação emocional + prova social.",
      "button": {
        "text": "Criar variação",
        "action": "usarSwipe"
      }
    }
  ],
  "copywriting": [
    {
      "title": "Você achava que X era bom...",
      "description": "Crie contraste com promessa mais poderosa.",
      "button": {
        "text": "Gerar variação",
        "action": "usarSwipe"
      }
    },
    {
      "title": "O que ninguém te contou sobre pizza artesanal",
      "description": "Swipe de curiosidade reveladora.",
      "button": {
        "text": "Adaptar esse",
        "action": "usarSwipe"
      }
    }
  ],
  "data": [
    {
      "title": "72% dos nossos clientes voltam em menos de 30 dias.",
      "description": "Swipe com dado de lealdade para criar prova social.",
      "button": {
        "text": "Usar dado de impacto",
        "action": "usarSwipe"
      }
    },
    {
      "title": "10 mil pizzas vendidas. 0 reclamações sobre a borda.",
      "description": "Use números para reforçar diferenciais.",
      "button": {
        "text": "Adaptar com meu número",
        "action": "usarSwipe"
      }
    }
  ],
  "directmail": [
    {
      "title": "Convite exclusivo para a noite mais saborosa do mês.",
      "description": "Swipe com senso de exclusividade para mala direta.",
      "button": {
        "text": "Usar como base",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Você foi selecionado para receber nossa pizza mais premiada.",
      "description": "Swipe de personalização para impressão ou entrega.",
      "button": {
        "text": "Gerar convite",
        "action": "usarSwipe"
      }
    }
  ],
  "emails": [
    {
      "title": "Não abra se estiver com fome!",
      "description": "Assunto provocativo para alta taxa de abertura.",
      "button": {
        "text": "Usar esse tom",
        "action": "usarSwipe"
      }
    },
    {
      "title": "A pizza que conquistou seu bairro (e seu inbox).",
      "description": "Assunto com prova social para campanhas locais.",
      "button": {
        "text": "Testar headline",
        "action": "usarSwipe"
      }
    }
  ],
  "images": [
    {
      "title": "Close no queijo derretendo. Nada mais.",
      "description": "Swipe visual minimalista. Deixe a imagem falar.",
      "button": {
        "text": "Usar esse conceito",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Olhar desejando + fatia no ar = post perfeito.",
      "description": "Swipe com storytelling visual.",
      "button": {
        "text": "Ver variações",
        "action": "usarSwipe"
      }
    }
  ],
  "money": [
    {
      "title": "De R$ 79 por apenas R$ 39",
      "description": "Swipe clássico de ancoragem de preço.",
      "button": {
        "text": "Adaptar ao meu produto",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Menos que um café por dia",
      "description": "Comparativo de valor baixo para percepção acessível.",
      "button": {
        "text": "Gerar esse tipo",
        "action": "usarSwipe"
      }
    }
  ],
  "motivation": [
    {
      "title": "Você merece esse momento.",
      "description": "Swipe motivacional com tom acolhedor.",
      "button": {
        "text": "Transformar em post",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Faça por você. Coma bem hoje.",
      "description": "Swipe com apelo de autocuidado.",
      "button": {
        "text": "Quero uma versão disso",
        "action": "usarSwipe"
      }
    }
  ],
  "pricing": [
    {
      "title": "Última unidade com esse valor",
      "description": "Swipe de escassez + ancoragem.",
      "button": {
        "text": "Usar esse gatilho",
        "action": "usarSwipe"
      }
    },
    {
      "title": "R$29 com ingredientes que custam 3x mais",
      "description": "Swipe de justificativa de valor.",
      "button": {
        "text": "Recriar com meu produto",
        "action": "usarSwipe"
      }
    }
  ],
  "printads": [
    {
      "title": "A pizza que você sente o cheiro só de olhar.",
      "description": "Swipe para ativar os sentidos em mídia impressa.",
      "button": {
        "text": "Transformar em flyer",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Mais crocante que seu domingo.",
      "description": "Swipe com humor e metáfora visual.",
      "button": {
        "text": "Ver versão alternativa",
        "action": "usarSwipe"
      }
    }
  ],
  "quotes": [
    {
      "title": "“A pizza é a simplicidade feita arte”",
      "description": "Frases poéticas para branding.",
      "button": {
        "text": "Usar como frase do dia",
        "action": "usarSwipe"
      }
    },
    {
      "title": "“A felicidade cabe em oito fatias”",
      "description": "Swipe emocional para campanhas leves.",
      "button": {
        "text": "Criar imagem com isso",
        "action": "usarSwipe"
      }
    }
  ],
  "salespages": [
    {
      "title": "A pizza que 9 em cada 10 clientes recomendam (e o 10º voltou no dia seguinte)",
      "description": "Swipe de prova social divertido.",
      "button": {
        "text": "Usar no meu site",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Não é só pizza. É o que você sente ao comer.",
      "description": "Swipe para vendas com apelo emocional.",
      "button": {
        "text": "Usar como headline",
        "action": "usarSwipe"
      }
    }
  ],
  "socialmedia": [
    {
      "title": "Essa pizza não é pra todo mundo",
      "description": "Swipe provocativo para engajamento.",
      "button": {
        "text": "Usar no Instagram",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Prove antes que acabe",
      "description": "Swipe de escassez para postagens com tempo limitado.",
      "button": {
        "text": "Gerar post agora",
        "action": "usarSwipe"
      }
    }
  ],
  "swipesemail": [
    {
      "title": "Seu lugar favorito em Osasco te mandou uma mensagem",
      "description": "Swipe de email com tom pessoal e local.",
      "button": {
        "text": "Gerar variação",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Abrimos ontem. Fechamos amanhã.",
      "description": "Swipe urgente para vendas por email.",
      "button": {
        "text": "Aplicar esse tom",
        "action": "usarSwipe"
      }
    }
  ],
  "testimonials": [
    {
      "title": "“Não como pizza em outro lugar desde que conheci vocês.”",
      "description": "Depoimento real convertido em swipe.",
      "button": {
        "text": "Usar no site",
        "action": "usarSwipe"
      }
    },
    {
      "title": "“Eu chorei com a borda.”",
      "description": "Swipe de prova emocional inesperada.",
      "button": {
        "text": "Quero esse efeito",
        "action": "usarSwipe"
      }
    }
  ],
  "videos": [
    {
      "title": "O queijo estica… a vontade também.",
      "description": "Swipe narrativo para reels curtos.",
      "button": {
        "text": "Criar roteiro",
        "action": "usarSwipe"
      }
    },
    {
      "title": "1 fatia. 2 segundos. 1000 likes.",
      "description": "Swipe para abertura de vídeos virais.",
      "button": {
        "text": "Testar no reels",
        "action": "usarSwipe"
      }
    }
  ],
  "wisdom": [
    {
      "title": "O segredo da pizza está no tempo, não na pressa.",
      "description": "Swipe reflexivo para post de marca.",
      "button": {
        "text": "Postar na terça",
        "action": "usarSwipe"
      }
    },
    {
      "title": "Quem respeita a massa, respeita quem come.",
      "description": "Swipe que conecta valores e processo artesanal.",
      "button": {
        "text": "Usar como manifesto",
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
                    "parameters": {
                        "categoria": categoria
                    },
                    "name": "obterSwipesPorCategoria"
                }
            }
        })
    return jsonify({
        "type": "cards",
        "title": "Categorias disponíveis",
        "items": categorias
    })
    return jsonify({
        "type": "cards",
        "title": "Categorias disponíveis",
        "items": categorias
    })
