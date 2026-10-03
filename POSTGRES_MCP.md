# PostgreSQL + MCP read layer

All MCP tools use PostgreSQL, through the shared `swipe_queries.py` read model:

| Tool | Read behavior |
| --- | --- |
| `listar_categorias` | Distinct, normalized, populated categories in the database |
| `obter_swipes_categoria` | Exact category match; stable ID ordering |
| `buscar_swipes` | Existing weighted ranking over PostgreSQL records |
| `obter_estrutura_copy_card` | Category records formatted as cards; advice retains three-card maximum |

The equivalent REST reads `/categorias`, `/swipes`, `/buscar-swipes`, and
`/estruturas/cards` use the same queries and card formatting. Advice cards no
longer scrape Swipefile during retrieval. No API key, crawler or OpenAI request
is needed for reading. PostgreSQL is authoritative: an empty database returns
empty results, and unavailable PostgreSQL produces a sanitized error rather
than substituting stale local content. REST returns HTTP 503; MCP reports a tool
error. Connection and statement timeouts bound database reads.

Compatibility: tool names, signatures, result envelopes, search scores,
`matched_by`, default/max search limits, advice card title, and `usarSwipe`
actions are retained. Cards expose persisted IDs and enrichment fields.
Button labels are consistently `Usar esta estrutura`; dates are ISO 8601,
nullable array fields become empty lists. Existing search fields including
`raw_content` and the stored `embedding` field remain available. The subsequent semantic layer adds a separate tool without changing the four
original tools; see SEMANTIC.md.

Search still uses weighted soft matching: category 4, objective 3, emotion 2,
tone 2. Matching any supplied attribute is sufficient, preserving previous
behavior. Category listing/cards instead use exact normalized category filters.

`swipes_db.py` remains only as the input to explicitly requested bootstrap
seeding in `seed_db.py`. The seed module is imported lazily by `/seed-db`;
ordinary REST/MCP startup and reads do not import either module. No seed or
database migration is run as part of this change. Existing startup database
initialization is unchanged. The original production service and branch `main`
are not modified.

Validation: `python -m unittest -v test_discovery test_ingestion test_postgres_mcp`.
The 28 tests include dynamic categories, exact filtering, null attributes,
card envelopes/actions, advice limits, preserved ranking, SQL parameterization,
read-only transactions, database failures, empty results, REST/MCP consistency,
and startup with local seed modules deliberately unavailable. Discovery and
ingestion regression tests remain included. After deployment, verify the
registered tool schemas are unchanged, enumerate database categories through
MCP, compare category/card IDs with REST, retrieve a real ingested swipe, and
confirm the database count is unchanged.
