# Primeiro ciclo de curadoria — 3 de outubro de 2026

Concluído apenas no desenvolvimento `api-copy-estruturas-mcp`, branch `mcp-upgrade`. 10 novas real_piece aceitas; 36 registros totais, 14 peças reais. Os 26 registros anteriores mantiveram taxonomias, hashes, versões e datas de embeddings. Produção main permanece inalterada. Busca cosseno e filtros não foram alterados; nenhum reranking.

| Peça | Cota primária | Motivo |
|---|---|---|
| [Hungryroot: geladeira antes e depois](https://swipefile.com/hungryroot-before-after-ad) | transformação | Transformação visível em duas imagens, acompanhada de depoimento; economia relatada permanece não verificada. |
| [Preço especial para clientes existentes](https://swipefile.com/existing-customer-special-pricing-by-sketch) | retenção | Retenção por renovação e tratamento específico a clientes existentes; distinta do suporte pós-compra. |
| [Outdoor da pizza que devora outro anúncio](https://swipefile.com/new-hand-tossed-pizza-billboard) | gastronomia | Gastronomia com ruptura visual e humor no outdoor; pizza integrada à situação, não foto isolada. |
| [Cartão de garantia GearLight](https://swipefile.com/gearlight-amazon-return-warranty-card) | retenção | Retenção por recuperação de serviço: reconhecer frustração e facilitar substituição após compra. |
| [Email de reativação da Netflix](https://reallygoodemails.com/emails/happy-friday-smiles-davis-time-to-come-back-to-netflix) | reativação | Retorno de ex-membro apoiado no valor do catálogo e em um CTA único; sem desconto explícito. |
| [Winback personalizado para Pippin e Patch](https://reallygoodemails.com/emails/are-pippin-and-patch-running-low-on-food) | reativação | Reativação ligada à necessidade de reposição e aos nomes dos cães; conta explicitamente cancelada; sem desconto. |
| [Anúncio do Whopper em tamanho real](https://swipefile.com/tasty-looking-whopper-ad) | gastronomia | Gastronomia com produto em destaque, escala e saciedade; peça impressa histórica diferente do outdoor. |
| [Email de reativação do Zoom Pro](https://reallygoodemails.com/emails/are-you-ghosting-us-reactivate-today) | reativação | Retorno ao Pro por novas funcionalidades; mostra o que mudou desde a saída, sem reduzir preço. |
| [Atoms: preço como valor](https://swipefile.com/theyre-not-cheap-social-media-ad) | preço/premium | Preço/premium: admite a objeção e explica o valor; abordagem distinta de custo por dia. |
| [Pedido para manter as mensalidades ativas](https://swipefile.com/small-business-email-asking-members-to-stay-active) | retenção | Retenção por transparência e vínculo comunitário diante de fechamento temporário; contexto histórico de crise. |

## Rejeições para este ciclo

- https://swipefile.com/hubspot-re-engagement-email: Reengajamento de newsletter; não comprova compra anterior. Rejeitado para a cota de reativação de clientes.
- https://reallygoodemails.com/emails/howdy-we-saved-your-spot: Cadastro incompleto; recuperação de aquisição, não cliente que já comprou.
- https://reallygoodemails.com/emails/restart-your-avocode-trial: Retorno de trial não comprova cliente pagante anterior.
- https://swipefile.com/gollum-dental-ad: Transformação fictícia/manipulada de personagem; não constitui evidência de resultado em cliente.
- https://swipefile.com/chiropractor-ad-before-and-after-brand-marketing-vs-benefit-marketing: Antes/depois do anúncio, não da transformação do serviço no cliente; inadequado para a lacuna.
- https://swipefile.com/pizza-crusts-baby-friendly-distraction-that-sells: Conteúdo educativo e adaptação recomendada; não comprova execução da campanha por restaurante.
- https://swipefile.com/cost-analysis-calculator: Ferramenta/exercício, não peça publicitária real; também redundante com custo por uso existente.

## Reservas válidas, não ingeridas

- https://reallygoodemails.com/emails/minor-hotels-winback-discount: Candidata real válida; deixada em reserva porque as três selecionadas ampliam reativação sem desconto.
- https://swipefile.com/the-ad-that-made-rolls-royce-legendary-1763576351199: Candidata premium válida; Atoms escolhida pela objeção de preço explícita e aplicabilidade a marcas menores.

## Consumo e validação

72 testes passaram. Compatibilidade live REST/MCP validada nas seis categorias das novas peças, cobrindo todos os dez registros e as quatro ferramentas legadas; schemas das cinco ferramentas preservados. Exatamente 10 tentativas de classificação, todas válidas, e 10 embeddings de documentos (6294 tokens). Classificação: 22146 tokens de entrada e 32051 de saída. Estimativa conservadora OpenAI USD 0.01836598, sem desconto de cache. Sete capturas Crawl4AI e três capturas públicas diretas RGE. Preço publicado do scrape: 0.2 crédito, multiplicador de 0.5 a 20, USD0.001/crédito. Assim, captura estimada USD0.0007–0.028; total estimado USD0.01906598–0.04636598 (referência standard USD0.01976598). Isso não é uma fatura: o pipeline antigo não preserva o nível faturado da captura. Nenhuma chamada paga de pesquisa; os cinco vetores de briefing vieram do cache. Dez URLs repetidas com tracking/trailing slash retornaram os mesmos IDs, sem paid calls. Não houve falhas nem regeneração de embeddings antigos.

## Distribuição

```json
{
  "record_type": {
    "template": 16,
    "guidance": 3,
    "framework": 2,
    "real_piece": 14,
    "collection": 1
  },
  "lifecycle": {
    "unknown": 2,
    "retention": 3,
    "acquisition": 4,
    "reactivation": 3,
    "conversion": 4
  },
  "channel": {
    "social": 3,
    "web": 1,
    "outdoor": 1,
    "unknown": 1,
    "direct_mail": 2,
    "email": 4,
    "print": 2
  },
  "format": {
    "static_ad": 4,
    "pricing_page": 1,
    "unknown": 1,
    "email": 4,
    "print_ad": 2,
    "postcard": 1,
    "reel": 1
  },
  "audience": {
    "unknown": 4,
    "active_customer": 3,
    "lapsed_customer": 3,
    "prospect": 4
  },
  "proof": {
    "before_after": 2,
    "testimonial": 1,
    "social_proof": 1,
    "unknown": 4,
    "none": 5,
    "quantified_benefit": 1,
    "demonstration": 1,
    "data_evidence": 1
  },
  "strategic_jobs": {
    "show_transformation": 2,
    "build_trust": 3,
    "explain_economic_value": 3,
    "communicate_visually": 3,
    "justify_price": 3,
    "encourage_repeat_purchase": 2,
    "clarify_offer": 2,
    "interrupt_attention": 3,
    "make_message_memorable": 1,
    "humanize_brand": 4,
    "introduce_product": 2,
    "explain_value": 5,
    "make_benefits_scannable": 2,
    "restore_relationship": 3,
    "reduce_action_friction": 3,
    "reduce_risk": 1,
    "advance_decision": 2,
    "build_desire": 2,
    "personalize_message": 1,
    "clarify_promise": 2,
    "surface_cost_of_inaction": 1,
    "overcome_objection": 2,
    "reframe_problem": 1,
    "challenge_belief": 1,
    "anchor_value": 1,
    "drive_event_attendance": 1
  }
}
```

Contagens de lifecycle, trabalhos e tipos de prova são multilabel; não somar como peças distintas. 3 reativações e 3 retenções possuem evidência de relação anterior. Hungryroot mantém lifecycle unknown, embora sirva à cota de transformação; não forçamos um funil. A biblioteca continua sem advocacy identificado e sem support_product_usage; apenas cinco das 14 peças reais têm tipo de prova identificado, nove são unknown ou none. Gastronomia humana tem três peças (Donatos, Whopper e Hungryroot); alimentação de cães não entra nessa contagem.

## Os mesmos cinco briefings: top 3 antes/depois


1. Preciso de um post para vender uma pizza artesanal. Quero abrir com uma provocação, despertar curiosidade e dar vontade de pedir hoje, sem desconto e sem parecer propaganda genérica.

| Posição | Antes | Score | Depois | Score |
|---|---|---|---|---|
| 1 | Essa pizza não é pra todo mundo | 0.644314 | Essa pizza não é pra todo mundo | 0.644314 |
| 2 | Todo mundo pede pizza. Poucos sabem o que estão pedindo. | 0.632414 | Todo mundo pede pizza. Poucos sabem o que estão pedindo. | 0.632414 |
| 3 | Você não precisa estar com fome para querer isso | 0.519818 | Outdoor da pizza que devora outro anúncio | 0.594888 |

2. Uma empresa de serviços para casa quer conquistar moradores do bairro com mala direta. Como chamar atenção no cartão postal, transmitir confiança e levar a pessoa a pedir um orçamento?

| Posição | Antes | Score | Depois | Score |
|---|---|---|---|---|
| 1 | Cartão-postal que fechou um serviço de US$ 390 mil | 0.625195 | Cartão-postal que fechou um serviço de US$ 390 mil | 0.625195 |
| 2 | Mensagem direta | 0.543472 | Mensagem direta | 0.543472 |
| 3 | Placa inflável desmaiada | 0.537989 | Placa inflável desmaiada | 0.537989 |

3. Vou lançar um produto premium que as pessoas ainda não conhecem. Preciso explicar o diferencial e justificar o preço usando benefícios concretos e provas, sem ficar só em adjetivos.

| Posição | Antes | Score | Depois | Score |
|---|---|---|---|---|
| 1 | Anúncio de lançamento do Eight Sleep Pod 6 | 0.570649 | Anúncio de lançamento do Eight Sleep Pod 6 | 0.570649 |
| 2 | Anúncio que converte | 0.537122 | Atoms: preço como valor | 0.549611 |
| 3 | Preço em perspectiva | 0.534946 | Anúncio que converte | 0.537122 |

4. Quero recuperar clientes que já compraram, mas sumiram. Preciso de um e-mail que retome a conversa de um jeito humano, lembre o valor da marca e convide a voltar sem dar desconto logo de cara.

| Posição | Antes | Score | Depois | Score |
|---|---|---|---|---|
| 1 | Sequência de e-mails | 0.532098 | Email de reativação da Netflix | 0.568934 |
| 2 | Assunto irresistível | 0.525254 | Email de reativação do Zoom Pro | 0.552827 |
| 3 | Anúncio que converte | 0.499988 | Winback personalizado para Pippin e Patch | 0.551283 |

5. Uma empresa quer mostrar a transformação que seu serviço provoca. Preciso de uma campanha de antes e depois que torne o resultado visível e convincente, com evidências e sem promessas exageradas.

| Posição | Antes | Score | Depois | Score |
|---|---|---|---|---|
| 1 | Antes: problema. Depois: solução | 0.692191 | Antes: problema. Depois: solução | 0.692191 |
| 2 | Anúncio que converte | 0.598790 | Hungryroot: geladeira antes e depois | 0.633006 |
| 3 | Deixe o cliente fazer o argumento | 0.575397 | Anúncio que converte | 0.598790 |

Reativação: top3 de templates para 3 emails reais adequados. Pizza: Donatos entra em terceiro; bom repertório visual, mas o canal e o CTA não coincidem integralmente com um post de pedido imediato. Premium: Atoms entra em segundo; aborda preço, mas não traz prova independente nem necessariamente lançamento. Transformação: Hungryroot entra em segundo; o framework genérico BAB continua em primeiro. Mala direta local: permanece igual, pois não coletamos novas aquisições de serviços locais. Portanto houve ganho de referências estrategicamente úteis em quatro testes, não demonstração de ranking resolvido.

## Limites da classificação e do adaptador

RGE foi necessário para achar ex-clientes reais: adapter estritamente HTTPS no host reallygoodemails.com e rota /emails/slug. Sem redirects, JS execution, tracking-link follow ou hosts arbitrários, com corpo máximo2MiB, timeout30s e falha quando o email original público não está disponível. Site/source changes fail closed. Swipefile continua usando Crawl4AI; descoberta continua restrita ao Swipefile. Os mesmos locks, autenticação, limites de lote3, orçamento diário20 e validação taxonômica antes do embedding continuam ativos.

Inspeção humana das capturas confirmou a existência das peças. O classificador permanece textual; proof_status é reported_in_source e proof_verification nunca é verificada. Para GearLight, o formato ficou unknown porque a taxonomia não possui packaging_insert. Generator ficou com marca unknown na leitura textual e categoria legada swipes-email, embora channel=email, format=email e lifecycle=retention estejam corretos. Isso é uma limitação transparente da classificação legada; não mudamos prompt, vocabulário ou vetor para ajustar ranking. Canais/plataformas sem evidência suficiente permanecem unknown. Valores monetários nas peças são históricos.

Resultados completos e evidências por atributo: CURATED_CYCLE_01.json. Comparação dos cinco testes: CURATED_CYCLE_01_SEARCHES.json.
