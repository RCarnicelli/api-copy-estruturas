# Development taxonomy validation — 2026-10-03

25 records enriched; legacy classification fields unchanged. Model text-embedding-3-small, dimension 1536. All 25 meaning-bearing texts changed to swipe-semantic-v2; 4 successful document calls, 8273 tokens, estimated USD 0.00016546 using the configured estimate. Repeat taxonomy apply: 0 updates. Repeat embedding backfill: 0 calls. Same five query embeddings reused from cache; 0 new query calls. No ingestion, classifier calls, production changes or reranking.

54 local tests passed (42 existing + 12 taxonomy). Existing five MCP input/output schemas unchanged. Live validation passed across all 22 categories and 25 swipes, including legacy REST/MCP equality and structured scores. Live database count 25, enriched 25, current v2 vectors 25, pending 0.

## Exact before/after (top 3, unfiltered cosine)

### Preciso de um post para vender uma pizza artesanal. Quero abrir com uma provocação, despertar curiosidade e dar vontade de pedir hoje, sem desconto e sem parecer propaganda genérica.

| Rank | Before | After |
|---|---|---|
| 1 | Essa pizza não é pra todo mundo (`socialmedia_001`), 0.628212 | Essa pizza não é pra todo mundo (`socialmedia_001`), 0.644314 |
| 2 | Todo mundo pede pizza. Poucos sabem o que estão pedindo. (`socialmedia_003`), 0.580261 | Todo mundo pede pizza. Poucos sabem o que estão pedindo. (`socialmedia_003`), 0.632414 |
| 3 | Você não precisa estar com fome para querer isso (`socialmedia_002`), 0.543834 | Você não precisa estar com fome para querer isso (`socialmedia_002`), 0.519818 |

### Uma empresa de serviços para casa quer conquistar moradores do bairro com mala direta. Como chamar atenção no cartão postal, transmitir confiança e levar a pessoa a pedir um orçamento?

| Rank | Before | After |
|---|---|---|
| 1 | Cartão-postal que fechou um serviço de US$ 390 mil (`swipe_82b97c105b80`), 0.649728 | Cartão-postal que fechou um serviço de US$ 390 mil (`swipe_82b97c105b80`), 0.625195 |
| 2 | Mensagem direta (`directmail_001`), 0.529088 | Mensagem direta (`directmail_001`), 0.543472 |
| 3 | Placa inflável desmaiada (`swipe_f0c0e15acd43`), 0.519901 | Placa inflável desmaiada (`swipe_f0c0e15acd43`), 0.537989 |

### Vou lançar um produto premium que as pessoas ainda não conhecem. Preciso explicar o diferencial e justificar o preço usando benefícios concretos e provas, sem ficar só em adjetivos.

| Rank | Before | After |
|---|---|---|
| 1 | Anúncio de lançamento do Eight Sleep Pod 6 (`swipe_3847f7d00635`), 0.562038 | Anúncio de lançamento do Eight Sleep Pod 6 (`swipe_3847f7d00635`), 0.570649 |
| 2 | Preço em perspectiva (`pricing_001`), 0.511749 | Anúncio que converte (`ads_001`), 0.537122 |
| 3 | Você achava que X era bom... (`copywriting_001`), 0.507218 | Preço em perspectiva (`pricing_001`), 0.534946 |

### Quero recuperar clientes que já compraram, mas sumiram. Preciso de um e-mail que retome a conversa de um jeito humano, lembre o valor da marca e convide a voltar sem dar desconto logo de cara.

| Rank | Before | After |
|---|---|---|
| 1 | Assunto irresistível (`emails_001`), 0.522779 | Sequência de e-mails (`swipesemail_001`), 0.532098 |
| 2 | Sequência de e-mails (`swipesemail_001`), 0.514833 | Assunto irresistível (`emails_001`), 0.525254 |
| 3 | Cartão-postal que fechou um serviço de US$ 390 mil (`swipe_82b97c105b80`), 0.503055 | Anúncio que converte (`ads_001`), 0.499988 |

### Uma empresa quer mostrar a transformação que seu serviço provoca. Preciso de uma campanha de antes e depois que torne o resultado visível e convincente, com evidências e sem promessas exageradas.

| Rank | Before | After |
|---|---|---|
| 1 | Antes: problema. Depois: solução (`beforeandafter_001`), 0.674678 | Antes: problema. Depois: solução (`beforeandafter_001`), 0.692191 |
| 2 | Cartão-postal que fechou um serviço de US$ 390 mil (`swipe_82b97c105b80`), 0.617822 | Anúncio que converte (`ads_001`), 0.598790 |
| 3 | Deixe o cliente fazer o argumento (`testimonials_001`), 0.598316 | Deixe o cliente fazer o argumento (`testimonials_001`), 0.575397 |

## Interpretation

Mixed retrieval outcome, not a universal improvement. Pizza keeps the same ordering. Direct mail keeps the same ordering including an off-channel reel. Launch keeps Eight Sleep first but a generic AIDA ad enters second. Reactivation puts sequence ahead of subject-line template and removes the postcard from top three, but still lacks any true reactivation piece. Before/after worsens in strategic usefulness: generic AIDA ad displaces the real postcard in second position. Higher scores do not prove better fit. Taxonomy improves transparency and enables future explicit filters; cosine alone does not enforce evidence or strategic suitability. No ranking changes or additional paid tuning were performed. Collection remains queryable to preserve existing behavior.
