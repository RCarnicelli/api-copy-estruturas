# Base estruturada de swipes
# Versão inicial preparada para REST, MCP e futura evolução para Swipe Brain.

SWIPES_DB = {
    "ads": [
        {
            "id": "ads_001",
            "title": "Anúncio que converte",
            "description": "Modelo direto ao ponto para vendas rápidas",
            "framework": "AIDA",
            "objective": ["vender", "converter"],
            "emotion": ["desejo", "urgencia"],
            "tone": ["direto", "comercial"],
            "hook": "Apresente rapidamente uma promessa ou benefício relevante.",
            "mechanism": "beneficio + desejo + chamada para acao",
            "cta": "Levar o público para a próxima ação.",
            "when_to_use": "Campanhas de venda e conversão.",
            "tags": ["anuncio", "venda", "conversao"],
            "button": {
                "text": "Usar este anúncio",
                "action": "usarSwipe"
            }
        }
    ],

    "advice": [
        {
            "id": "advice_001",
            "title": "Dica de ouro",
            "description": "Use provas sociais para fortalecer sua copy",
            "framework": "Proof",
            "objective": ["educar", "convencer"],
            "emotion": ["confianca"],
            "tone": ["consultivo"],
            "hook": "Transforme uma recomendação em argumento persuasivo.",
            "mechanism": "autoridade + prova",
            "cta": "Aplicar a recomendação.",
            "when_to_use": "Conteúdos educativos e argumentos de autoridade.",
            "tags": ["conselho", "prova", "autoridade"],
            "button": {
                "text": "Aplicar dica",
                "action": "usarSwipe"
            }
        }
    ],

    "beforeandafter": [
        {
            "id": "beforeandafter_001",
            "title": "Antes: problema. Depois: solução",
            "description": "Mostre a transformação",
            "framework": "BAB",
            "objective": ["vender", "demonstrar"],
            "emotion": ["desejo", "esperanca"],
            "tone": ["visual", "emocional"],
            "hook": "Mostre o contraste entre a situação atual e a desejada.",
            "mechanism": "contraste + transformacao",
            "cta": "Convidar o público para a transformação.",
            "when_to_use": "Produtos ou serviços com transformação perceptível.",
            "tags": ["antes", "depois", "transformacao"],
            "button": {
                "text": "Usar estrutura",
                "action": "usarSwipe"
            }
        }
    ],

    "copywriting": [
        {
            "id": "copywriting_001",
            "title": "Você achava que X era bom...",
            "description": "Crie contraste e desejo",
            "framework": "Contraste",
            "objective": ["vender", "engajar"],
            "emotion": ["curiosidade", "desejo"],
            "tone": ["provocativo"],
            "hook": "Questione uma crença conhecida pelo público.",
            "mechanism": "quebra de expectativa + contraste",
            "cta": "Apresentar uma alternativa superior.",
            "when_to_use": "Posicionamento, diferenciação e lançamento.",
            "tags": ["contraste", "curiosidade", "provocacao"],
            "button": {
                "text": "Gerar variação",
                "action": "usarSwipe"
            }
        }
    ],

    "data": [
        {
            "id": "data_001",
            "title": "Dados não mentem",
            "description": "Comece sua copy com um dado relevante",
            "framework": "Data Hook",
            "objective": ["educar", "convencer"],
            "emotion": ["surpresa", "curiosidade"],
            "tone": ["informativo", "assertivo"],
            "hook": "Abra com um dado capaz de mudar a percepção do público.",
            "mechanism": "dado + interpretacao + consequencia",
            "cta": "Transformar informação em ação.",
            "when_to_use": "Conteúdo educativo e campanhas baseadas em evidências.",
            "tags": ["dados", "estatistica", "curiosidade"],
            "button": {
                "text": "Usar dado",
                "action": "usarSwipe"
            }
        }
    ],

    "directmail": [
        {
            "id": "directmail_001",
            "title": "Mensagem direta",
            "description": "Modelo para comunicação direta",
            "framework": "Direct Response",
            "objective": ["vender", "converter"],
            "emotion": ["interesse"],
            "tone": ["pessoal", "direto"],
            "hook": "Fale com uma pessoa, não com uma audiência.",
            "mechanism": "personalizacao + oferta",
            "cta": "Solicitar uma ação específica.",
            "when_to_use": "Comunicações diretas e ofertas.",
            "tags": ["direto", "oferta", "resposta"],
            "button": {
                "text": "Usar este modelo",
                "action": "usarSwipe"
            }
        }
    ],

    "emails": [
        {
            "id": "emails_001",
            "title": "Assunto irresistível",
            "description": "Estrutura de email orientada à abertura e leitura",
            "framework": "Curiosity Gap",
            "objective": ["engajar", "vender"],
            "emotion": ["curiosidade"],
            "tone": ["pessoal", "envolvente"],
            "hook": "Crie uma lacuna de informação que mereça ser aberta.",
            "mechanism": "curiosidade + recompensa",
            "cta": "Conduzir para uma única próxima ação.",
            "when_to_use": "Email marketing e relacionamento.",
            "tags": ["email", "assunto", "curiosidade"],
            "button": {
                "text": "Usar e-mail",
                "action": "usarSwipe"
            }
        }
    ],

    "images": [
        {
            "id": "images_001",
            "title": "Imagem que vende",
            "description": "Conceito visual orientado à campanha",
            "framework": "Visual Hook",
            "objective": ["engajar", "vender"],
            "emotion": ["desejo"],
            "tone": ["sensorial"],
            "hook": "Faça a imagem comunicar antes do texto.",
            "mechanism": "impacto visual + desejo",
            "cta": "Conectar o visual à ação desejada.",
            "when_to_use": "Social media e campanhas visuais.",
            "tags": ["imagem", "visual", "desejo"],
            "button": {
                "text": "Gerar imagem",
                "action": "usarSwipe"
            }
        }
    ],

    "money": [
        {
            "id": "money_001",
            "title": "Fale de dinheiro",
            "description": "Estrutura baseada em valor econômico",
            "framework": "Value",
            "objective": ["vender", "convencer"],
            "emotion": ["desejo", "seguranca"],
            "tone": ["direto"],
            "hook": "Mostre o valor antes de discutir o preço.",
            "mechanism": "valor + comparacao",
            "cta": "Converter percepção de valor em decisão.",
            "when_to_use": "Ofertas com argumento financeiro.",
            "tags": ["dinheiro", "valor", "economia"],
            "button": {
                "text": "Usar esse apelo",
                "action": "usarSwipe"
            }
        }
    ],

    "motivation": [
        {
            "id": "motivation_001",
            "title": "Inspire para mover",
            "description": "Estrutura com apelo emocional",
            "framework": "Emotional Story",
            "objective": ["engajar", "inspirar"],
            "emotion": ["inspiracao"],
            "tone": ["emocional"],
            "hook": "Comece pela aspiração do público.",
            "mechanism": "identificacao + aspiracao",
            "cta": "Transformar inspiração em movimento.",
            "when_to_use": "Branding e conteúdo emocional.",
            "tags": ["motivacao", "emocao", "aspiracao"],
            "button": {
                "text": "Usar inspiração",
                "action": "usarSwipe"
            }
        }
    ],

    "pricing": [
        {
            "id": "pricing_001",
            "title": "Preço em perspectiva",
            "description": "Estrutura de ancoragem de valor",
            "framework": "Price Anchoring",
            "objective": ["vender", "converter"],
            "emotion": ["desejo", "seguranca"],
            "tone": ["comercial"],
            "hook": "Construa valor antes de revelar ou comparar preço.",
            "mechanism": "ancoragem + valor percebido",
            "cta": "Facilitar a decisão de compra.",
            "when_to_use": "Ofertas, combos e apresentações de preço.",
            "tags": ["preco", "ancoragem", "valor"],
            "button": {
                "text": "Aplicar oferta",
                "action": "usarSwipe"
            }
        }
    ],

    "printads": [
        {
            "id": "printads_001",
            "title": "Anúncio impresso eficaz",
            "description": "Estrutura clássica para mídia impressa",
            "framework": "Headline + Body + CTA",
            "objective": ["vender", "informar"],
            "emotion": ["interesse"],
            "tone": ["claro"],
            "hook": "Use uma manchete que carregue a ideia principal.",
            "mechanism": "headline + argumento + resposta",
            "cta": "Dar uma próxima ação inequívoca.",
            "when_to_use": "Materiais impressos e peças estáticas.",
            "tags": ["impresso", "headline", "anuncio"],
            "button": {
                "text": "Usar esse anúncio",
                "action": "usarSwipe"
            }
        }
    ],

    "quotes": [
        {
            "id": "quotes_001",
            "title": "Uma frase pode carregar uma ideia inteira",
            "description": "Estrutura para frases de impacto",
            "framework": "Quote Hook",
            "objective": ["engajar", "posicionar"],
            "emotion": ["reflexao"],
            "tone": ["elegante"],
            "hook": "Condense uma verdade reconhecível em poucas palavras.",
            "mechanism": "simplicidade + identificacao",
            "cta": "Estimular lembrança ou compartilhamento.",
            "when_to_use": "Branding e social media.",
            "tags": ["frase", "citacao", "branding"],
            "button": {
                "text": "Usar citação",
                "action": "usarSwipe"
            }
        }
    ],

    "salespages": [
        {
            "id": "salespages_001",
            "title": "Página que conduz à decisão",
            "description": "Estrutura para página de vendas",
            "framework": "AIDA",
            "objective": ["vender", "converter"],
            "emotion": ["desejo", "confianca"],
            "tone": ["persuasivo"],
            "hook": "Abra com a promessa central da oferta.",
            "mechanism": "atencao + interesse + desejo + acao",
            "cta": "Converter o interesse em compra.",
            "when_to_use": "Landing pages e páginas de venda.",
            "tags": ["landingpage", "venda", "conversao"],
            "button": {
                "text": "Usar estrutura",
                "action": "usarSwipe"
            }
        }
    ],

    "socialmedia": [
        {
            "id": "socialmedia_001",
            "title": "Essa pizza não é pra todo mundo",
            "description": "Estrutura provocativa para interromper o scroll",
            "framework": "Contrarian Hook",
            "objective": ["vender", "engajar", "posicionar"],
            "emotion": ["curiosidade", "desejo"],
            "tone": ["provocativo"],
            "hook": "Exclua simbolicamente para despertar identificação e curiosidade.",
            "mechanism": "polarizacao leve + identidade + desejo",
            "cta": "Transformar identificação em experimentação.",
            "when_to_use": "Social media, especialmente produtos com personalidade forte.",
            "tags": ["socialmedia", "provocacao", "identidade", "pizza"],
            "button": {
                "text": "Usar esse tom",
                "action": "usarSwipe"
            }
        },
        {
            "id": "socialmedia_002",
            "title": "Você não precisa estar com fome para querer isso",
            "description": "Estrutura sensorial baseada em desejo antecipado",
            "framework": "Sensory Desire",
            "objective": ["vender", "engajar"],
            "emotion": ["desejo", "curiosidade"],
            "tone": ["sensorial", "provocativo"],
            "hook": "Antecipe a experiência antes da necessidade racional.",
            "mechanism": "sensorialidade + antecipacao",
            "cta": "Convidar o público a experimentar.",
            "when_to_use": "Gastronomia e produtos de forte apelo visual.",
            "tags": ["socialmedia", "sensorial", "food", "desejo"],
            "button": {
                "text": "Usar estrutura",
                "action": "usarSwipe"
            }
        },
        {
            "id": "socialmedia_003",
            "title": "Todo mundo pede pizza. Poucos sabem o que estão pedindo.",
            "description": "Estrutura baseada em conhecimento, identidade e diferenciação",
            "framework": "Knowledge Gap",
            "objective": ["engajar", "posicionar", "educar"],
            "emotion": ["curiosidade", "pertencimento"],
            "tone": ["provocativo", "cultural"],
            "hook": "Crie uma diferença entre consumir e compreender.",
            "mechanism": "curiosidade + identidade + conhecimento",
            "cta": "Convidar o público a descobrir algo.",
            "when_to_use": "Conteúdo cultural, educativo e de posicionamento.",
            "tags": ["socialmedia", "cultura", "pizza", "curiosidade"],
            "button": {
                "text": "Explorar estrutura",
                "action": "usarSwipe"
            }
        }
    ],

    "swipesemail": [
        {
            "id": "swipesemail_001",
            "title": "Sequência de e-mails",
            "description": "Estrutura para uma sequência de relacionamento e conversão",
            "framework": "Email Sequence",
            "objective": ["nutrir", "vender"],
            "emotion": ["curiosidade", "confianca"],
            "tone": ["progressivo"],
            "hook": "Cada mensagem abre uma razão para ler a próxima.",
            "mechanism": "sequencia + progressao + oferta",
            "cta": "Mover o leitor progressivamente para a decisão.",
            "when_to_use": "Funis e relacionamento.",
            "tags": ["email", "sequencia", "funil"],
            "button": {
                "text": "Usar sequência",
                "action": "usarSwipe"
            }
        }
    ],

    "testimonials": [
        {
            "id": "testimonials_001",
            "title": "Deixe o cliente fazer o argumento",
            "description": "Estrutura de prova social",
            "framework": "Social Proof",
            "objective": ["convencer", "vender"],
            "emotion": ["confianca"],
            "tone": ["autentico"],
            "hook": "Comece pela experiência concreta de outra pessoa.",
            "mechanism": "prova social + identificacao",
            "cta": "Reduzir a insegurança antes da decisão.",
            "when_to_use": "Campanhas de conversão e reputação.",
            "tags": ["depoimento", "prova", "cliente"],
            "button": {
                "text": "Usar depoimento",
                "action": "usarSwipe"
            }
        }
    ],

    "videos": [
        {
            "id": "videos_001",
            "title": "Vídeo que prende atenção",
            "description": "Estrutura para vídeos curtos",
            "framework": "Hook + Retention + Payoff",
            "objective": ["engajar", "vender"],
            "emotion": ["curiosidade"],
            "tone": ["dinamico"],
            "hook": "Dê uma razão para não passar para o próximo vídeo.",
            "mechanism": "gancho + tensao + recompensa",
            "cta": "Converter atenção em ação.",
            "when_to_use": "Reels, Shorts e TikTok.",
            "tags": ["video", "reels", "retencao"],
            "button": {
                "text": "Criar vídeo",
                "action": "usarSwipe"
            }
        }
    ],

    "wisdom": [
        {
            "id": "wisdom_001",
            "title": "Sabedoria aplicada ao marketing",
            "description": "Estrutura reflexiva com conexão comercial",
            "framework": "Insight",
            "objective": ["engajar", "posicionar"],
            "emotion": ["reflexao", "curiosidade"],
            "tone": ["reflexivo", "elegante"],
            "hook": "Comece com uma observação humana reconhecível.",
            "mechanism": "verdade humana + interpretacao + marca",
            "cta": "Conectar a reflexão à proposta da marca.",
            "when_to_use": "Branding e posicionamento.",
            "tags": ["insight", "sabedoria", "branding"],
            "button": {
                "text": "Usar insight",
                "action": "usarSwipe"
            }
        }
    ]
}
