# Correção da pesquisa do Swipe Brain

Base: RCarnicelli/api-copy-estruturas, branch mcp-upgrade, commit e29555e4ca510f1c7d75d1a4e79c52661177dbff.

## Comportamento

- MCP buscar_swipes e buscar_swipes_semanticos: record_type=real_piece por padrão. Exigem classificação real_piece na taxonomia e URL HTTP(S). Isso não comprova a autenticidade da peça nem a validade atual da URL.
- record_type=template permite buscar estruturas. record_type=all inclui os dois tipos e registros sem classificação.
- buscar_swipes exige todos os critérios por padrão (match_mode=all). Para preferências, use match_mode=any; cada resultado informa unmatched_filters. Não há relaxamento automático.
- A busca semântica mantém os filtros obrigatórios; min_similarity é opcional, entre -1 e 1. Nenhum valor arbitrário foi ativado como garantia de relevância. Não há reranker novo.
- Candidatos recebem relevance_status=requires_review. A resposta distingue candidates_require_review de no_candidates. Vazio não significa que a base inteira não contenha uma referência.
- Navegação por categoria continua abrangente por padrão (record_type=all no MCP); cada registro é identificado. Cards também recebem record_type e has_source.
- Categorias equivalentes são consultadas juntas, sem migrar o banco: social/socialmedia, print-ads/printads, before-and-after/beforeandafter, direct-mail/directmail e swipes-email/swipesemail.
- Acentos e maiúsculas são normalizados nos critérios de busca. Não há expansão automática de sinônimos.
- REST /buscar-swipes e /buscar-swipes-semanticos expõem as novas opções e priorizam referências reais. Parâmetros inválidos retornam HTTP 400.
- Werkzeug limitado à série 2.x para compatibilidade com Flask 2.3.2 fixado no projeto.

## Exemplo Zacca no MCP

buscar_swipes(emocao="vaidade", tom="provocativo", record_type="real_piece", match_mode="all", limite=5)

Se não houver candidatos, buscar_swipes_semanticos(consulta="cera para cabelo e barba; homens adultos até 35 anos; vaidade; tom provocativo", record_type="real_piece", limite=5).

Os candidatos ainda precisam ser avaliados. Se for necessário ampliar para perfume ou moda, explicar a ampliação e apresentar título e source_url antes da adaptação.

## Verificação realizada

83 testes unitários/de integração com dependências externas simuladas passaram em Python 3.12.14. Incluem regressões da Zacca, critérios parciais explícitos, templates, fontes ausentes, categorias equivalentes, validação e filtros SQL parametrizados. Nenhuma chamada paga, escrita no banco ou publicação foi realizada.

## Publicação pendente

Aplicar o patch sobre o commit base indicado ou copiar os arquivos do pacote em uma branch de revisão. Conferir diferenças caso o remoto tenha avançado. Depois de revisão e publicação autorizada, verificar a nova lista de parâmetros no MCP e executar o briefing Zacca no banco real. Confirmar a cobertura de taxonomia e embeddings: registros unknown ou sem vetor atualizado podem ficar fora das buscas de referências. Não reclassificar nem gerar embeddings automaticamente.

O pacote não contém credenciais, ambiente virtual ou banco de dados.
