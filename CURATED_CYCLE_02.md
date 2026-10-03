# Ciclo 02 — especialização em pizza, 3 de outubro de 2026

**Resultado parcial: 6 aceitas de uma meta de 10.** 42 registros, 20 real_piece. Cinco novas referências relacionadas a pizza e uma de gastronomia próxima. O alvo de 9 peças de pizzarias + 1 adjacente não foi alcançado. Não são seis campanhas de pizzarias: há duas de pizzarias (Domino’s e Vinnie’s), duas de pizza congelada, uma de plataforma e uma de varejo para Pizza Night. Mantivemos vagas abertas por evidência e utilidade; nenhuma classificação foi forçada para preencher cotas.

Somente desenvolvimento api-copy-estruturas-mcp, branch mcp-upgrade. Código, prompts, schema, ferramentas, filtros e algoritmo permanecem iguais. Nenhum reranking. Credencial de ingestão renovada apenas no dev, sem ler chaves de provedores. Produção main com updatedAt 2025-12-12T22:30:04.353811Z, sem alteração.

## Aceitas

| Peça | Motivo e limite | Lifecycle | Relacionamento |
|---|---|---|---|
| [Ofertas de pizza da Domino’s](https://reallygoodemails.com/emails/what-would-you-do-for-the-last-slice) | Ofertas legíveis e saldo de pontos. Útil para clareza do pedido e fidelidade; classificação automática mantém subscriber/conversion, sem forçar retenção. | ["conversion"] | subscriber |
| [Peça pelo Slice e apoie pizzarias locais](https://reallygoodemails.com/emails/order-on-the-app-s-pizzerias-trust) | Razão para escolher o canal de pedido, apoio à operação local e CTA direto. Plataforma de pedidos; não campanha criada por uma pizzaria. | ["conversion"] | subscriber |
| [Placa de especiais da Vinnie’s](https://swipefile.com/vinnies-pizzeria-specials-sign) | Quadro local de especiais com nomes criativos e ingredientes. Humor e memorização do produto, distinto do outdoor Donatos. | "unknown" | unknown |
| [Pizza Night em casa](https://reallygoodemails.com/emails/weve-got-your-pizza-night-essentials) | Ocasião de consumo compartilhada, harmonização e retirada/entrega. Varejo de ingredientes para preparar em casa, não delivery de pizza pronta. | ["conversion"] | subscriber |
| [Pizza congelada com massa sourdough](https://reallygoodemails.com/emails/you-sourdough-crust-on-a-frozen-pizza-no-way-us-yes-way) | Diferenciação por fermentação de 48–72 horas e quebra de expectativa sobre pizza congelada. Útil para explicar processo; não é objeção explícita de preço. | ["conversion"] | unknown |
| [Pizza napolitana congelada](https://reallygoodemails.com/emails/-the-best-frozen-pizza-we-swear) | Ingredientes, origem, descrições sensoriais e depoimento. Presença de testimonial relatada; resultado e alegações não verificados. | ["conversion"] | unknown |

## Consumo e segurança

8 tentativas de classificação, 6 válidas e 2 inválidas. Tokens: entrada 19493, saída 25456; inclui falhas pagas. 6 embeddings documentais/4053 tokens, modelo text-embedding-3-small, 1536 dimensões, semantic v2. 5 novos vetores de consulta/226 tokens; os mesmos cinco briefings antigos usaram cache e zero chamadas pagas. Zero retries pagos, zero regeneração de embeddings existentes. Todos os 36 registros anteriores preservaram taxonomy, embedding_hash e embedded_at.

OpenAI estimado sem desconto de cache: USD 0.01476288. Uma captura Crawl4AI: estimativa USD 0.0001–0.004; referência standard USD 0.0002. Total estimado USD 0.01486288–0.01876288 (standard USD 0.01496288). Não é uma fatura: nível faturado da captura não foi registrado. Pesquisa pública sem chamadas Firecrawl pagas. Fontes de preços: https://developers.openai.com/api/docs/models/gpt-6-luna e https://developers.openai.com/api/docs/models/text-embedding-3-small ; referência Crawl4AI da auditoria do ciclo 01 no mesmo dia.

72 testes unittest passaram. REST/MCP live: 6 registros nas duas categorias atuais, quatro ferramentas legadas e schemas das cinco ferramentas preservados. Reenvio das seis URLs com trailing slash/tracking retornou os mesmos IDs, zero novas classificações, zero embeddings e zero duplicatas. Os seis vetores têm dimensão 1536 e embedding_dirty=false.

## Falhas individuais

Ambas tiveram provider_received=true e validated=false. Endpoint sanitizado informa etapa classificacao. Não foi preservado o motivo específico nem a resposta inválida; não é possível determinar qual atributo falhou a partir desta auditoria. Não houve inserção, embedding ou retry.

- https://reallygoodemails.com/emails/discover-the-new-italiano-range
- https://reallygoodemails.com/emails/order-confirmation-for-smiles-davis-from-ozzys-apizza

## Candidatas rejeitadas e reservas

- https://reallygoodemails.com/emails/a-pasta-a-pizza-a-martini: Extração quase só caracteres invisíveis, sem corpo semântico suficiente.
- https://reallygoodemails.com/emails/controversy-at-its-most-delicious: Oferta principal é forno/acessórios; não execução comercial de pizzaria.
- https://reallygoodemails.com/emails/the-hut-originals-collection-available-now: Oferta principal é roupa/merchandising.
- https://reallygoodemails.com/emails/good-job-being-born-time-to-celebrate: Aniversário e bônus não comprovam compra anterior ou inatividade; não preenche reativação sem desconto.
- https://reallygoodemails.com/emails/wish-you-were-here-signed-the-drive-thru: Cadastro em app não comprova compra anterior nem afastamento; setor fora da prioridade.
- https://swipefile.com/personalized-pizza-slice-mailers-boost-foot-traffic: Asset tem nome e endereço exemplificativos. Circulação como campanha real não ficou comprovada; apenas Pinterest como origem.
- https://swipefile.com/pizza-crusts-baby-friendly-distraction-that-sells: Dica/adaptação não demonstra peça publicada por pizzaria.
- https://reallygoodemails.com/emails/nyc-pizza-natural-wine: Editorial de harmonização; não preencher a vaga de peça comercial de pizzaria.

Reservas:

- https://swipefile.com/call-to-action-based-pizza-ad: Anúncio real de pizza rolls industrializados; menor proximidade com a prioridade de operações de pizzaria.
- https://reallygoodemails.com/emails/the-most-important-vote-of-the-year: Sazonal com desconto; deixado em reserva para evitar concentração em ofertas promocionais.

## Os mesmos cinco briefings — antes e depois

1. Preciso de um post para vender uma pizza artesanal. Quero abrir com uma provocação, despertar curiosidade e dar vontade de pedir hoje, sem desconto e sem parecer propaganda genérica.

| Posição | Antes | Score | Depois | Score |
|---|---|---|---|---|
| 1 | Essa pizza não é pra todo mundo | 0.644314 | Essa pizza não é pra todo mundo | 0.644314 |
| 2 | Todo mundo pede pizza. Poucos sabem o que estão pedindo. | 0.632414 | Todo mundo pede pizza. Poucos sabem o que estão pedindo. | 0.632414 |
| 3 | Outdoor da pizza que devora outro anúncio | 0.594888 | Pizza congelada com massa sourdough | 0.602320 |

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
| 2 | Atoms: preço como valor | 0.549611 | Atoms: preço como valor | 0.549611 |
| 3 | Anúncio que converte | 0.537122 | Anúncio que converte | 0.537122 |

4. Quero recuperar clientes que já compraram, mas sumiram. Preciso de um e-mail que retome a conversa de um jeito humano, lembre o valor da marca e convide a voltar sem dar desconto logo de cara.

| Posição | Antes | Score | Depois | Score |
|---|---|---|---|---|
| 1 | Email de reativação da Netflix | 0.568934 | Email de reativação da Netflix | 0.568934 |
| 2 | Email de reativação do Zoom Pro | 0.552827 | Email de reativação do Zoom Pro | 0.552827 |
| 3 | Winback personalizado para Pippin e Patch | 0.551283 | Winback personalizado para Pippin e Patch | 0.551283 |

5. Uma empresa quer mostrar a transformação que seu serviço provoca. Preciso de uma campanha de antes e depois que torne o resultado visível e convincente, com evidências e sem promessas exageradas.

| Posição | Antes | Score | Depois | Score |
|---|---|---|---|---|
| 1 | Antes: problema. Depois: solução | 0.692191 | Antes: problema. Depois: solução | 0.692191 |
| 2 | Hungryroot: geladeira antes e depois | 0.633006 | Hungryroot: geladeira antes e depois | 0.633006 |
| 3 | Anúncio que converte | 0.598790 | Anúncio que converte | 0.598790 |

Só pizza mudou no top 3: General Assembly entrou em terceiro (0.602320), no lugar de Donatos (0.594888). Os dois templates continuam liderando. Os outros quatro briefings mantiveram exatamente IDs, ordem e scores. Isso é melhora incremental de repertório, sem comprovação de ranking resolvido.

## Cinco briefings específicos de pizza — resultados atuais

1. Preciso de um Reel para uma pizzaria artesanal que faça a pessoa imaginar a primeira mordida: crocância da borda, massa leve e sabor, com vontade de pedir hoje e sem desconto.

| Posição | Resultado | Score |
|---|---|---|
| 1 | Outdoor da pizza que devora outro anúncio | 0.555404 |
| 2 | Pizza Night em casa | 0.552582 |
| 3 | Essa pizza não é pra todo mundo | 0.542266 |

Reel sensorial: outdoor e email lideram; ainda falta aderência de canal/formato. Pizza Night contribui com experiência, mas não é pizza pronta.

2. A pizza da minha marca custa mais que a média. Quero explicar o valor da longa fermentação e dos ingredientes sem parecer arrogante nem falar apenas que é premium.

| Posição | Resultado | Score |
|---|---|---|
| 1 | Pizza congelada com massa sourdough | 0.518523 |
| 2 | Pizza Night em casa | 0.491384 |
| 3 | Outdoor da pizza que devora outro anúncio | 0.480020 |

Preço/processo: General Assembly é útil para diferenciação por fermentação; não responde integralmente à objeção explícita de preço.

3. Quero vender pizza para uma noite em família em casa. Procuro uma referência que transforme o jantar em uma experiência compartilhada e facilite o pedido ou a retirada.

| Posição | Resultado | Score |
|---|---|---|
| 1 | Pizza Night em casa | 0.646969 |
| 2 | Todo mundo pede pizza. Poucos sabem o que estão pedindo. | 0.536286 |
| 3 | Pizza napolitana congelada | 0.521256 |

Ocasião família: Pizza Night é a correspondência mais forte; preparo compartilhado e retirada claros. Transferência para pizzaria exige adaptação.

4. Preciso estimular a recompra de quem já pediu pizza. Quero lembrar o valor da marca e facilitar um próximo pedido, aproveitando a relação existente com o cliente.

| Posição | Resultado | Score |
|---|---|---|
| 1 | Peça pelo Slice e apoie pizzarias locais | 0.605767 |
| 2 | Ofertas de pizza da Domino’s | 0.605605 |
| 3 | Pizza Night em casa | 0.603095 |

Recompra: Slice e Domino’s trazem pedido/pontos, mas taxonomy não comprova segmentação pós-compra. Similaridade não equivale a evidência de cliente ativo.

5. Quero trazer de volta clientes da pizzaria que já compraram e estão há dois meses sem pedir. Preciso de uma mensagem humana, com motivo concreto para voltar e sem cupom de desconto.

| Posição | Resultado | Score |
|---|---|---|
| 1 | Winback personalizado para Pippin e Patch | 0.573066 |
| 2 | Pizza Night em casa | 0.538927 |
| 3 | Email de reativação da Netflix | 0.537170 |

Reativação: Lyka continua liderando e pertence a alimentação de cães. Pizza Night em segundo não é reativação. Lacuna de pizzaria permanece.

## Distribuição e lacunas

20 peças reais: 9 de gastronomia humana (45%), 6 relacionadas a pizza no recorte ampliado, 3 de pizzarias propriamente ditas (Donatos, Domino’s, Vinnie’s). Não contar frozen/marketplace/kit como operação de pizzaria. Retenção 3 e reativação 3 na biblioteca geral permanecem inalteradas; zero novas classificações nesses lifecycle. Email passa de 4 para 9; print de 2 para 3. Conversão passa de 4 para 9; unknown de 2 para 3. Contagens multilabel não somam peças distintas.

Lacunas para completar a prioridade: Reels sensoriais publicados por pizzarias; objeção de preço premium explícita; pós-compra/recompra com evidência e classificação válida; reativação sem desconto de ex-compradores; storytelling local. A meta mínima de cinco operações locais/regionais também não foi alcançada. Não completar com cupons genéricos, tutoriais ou novos anúncios de produto industrializado.

## Limites da classificação

Vinnie’s é um quadro físico manuscrito fotografado. O vocabulário atual não possui chalkboard/menu_board; classifier atribuiu print (inferred), static_image (inferred), categoria images, lifecycle unknown. Isso é uma aproximação de formato/canal, não evidência de campanha impressa ou Instagram. Não foi alterada para manipular recuperação. Na Talia di Napoli, geography=Nápoles reflete a origem descrita do produto e não prova a sede do anunciante Bubble Goods. Fidelidade/pontos em emails não foram forçados para active_customer/retention. Nenhum testimonial ou número promocional foi convertido em prova verificada.

Dados completos, evidência por atributo, auditoria e buscas estão em CURATED_CYCLE_02.json.
