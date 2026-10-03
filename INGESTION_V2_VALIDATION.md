# Development ingestion v2 validation — 2026-10-03

Implementation: f6d741d6de88b5acff33be86b8273e64862f3ec6 on mcp-upgrade, deployed only to api-copy-estruturas-mcp.

66 unit/regression tests passed. New pieces receive one classification containing both legacy fields and all 21 approved taxonomy attributes. Conservative validation must pass before atomic persistence; only the enriched saved ID is embedded. Unknown evidence remains unknown. No reranking/search-algorithm changes.

One authorized new piece: https://swipefile.com/apple-daily-cost-comparison-ad
Saved ID: swipe_b1fcdbd8f736. Result: 1 processed, 0 errors; 1 classification call, 1 embedding call. Canonical duplicate with trailing slash and tracking parameter returned the same ID with zero paid calls. Dry-run issued zero paid calls. Total library is now 26, with the previous 25 taxonomy objects and embedding hashes/versions/timestamps unchanged.

Classification: gpt-6-luna, 2256 input and 3259 output tokens. Embedding: text-embedding-3-small, 1536 dimensions, 639 tokens, semantic v2. Estimated OpenAI cost at standard unit rates: USD 0.00186788; crawl charge is separate. Daily classification cap: 20 reserved attempts, including failed attempts. Existing batch cap of 3 and embedding budgets/authentication/hash reuse preserved.

Strategic interpretation: cost-per-day comparison to justify price and reframe perceived expense. Product shown does not establish Apple as campaign author. Brand, paid distribution, incentive and conversion action remain unknown. Numerical illustration is reported data evidence, unverified; it is not demonstrated performance or savings. Audience prospect, decision stage, conversion function and static format are explicitly inferred. Source evidence is textual curation, not automated inspection of original creative.

Complete structured result, legacy fields and per-attribute provenance: INGESTION_V2_SINGLE_PIECE.json. Raw third-party page and 1536 vector components are omitted from this report; the actual vector is persisted in PostgreSQL.

Original production remains branch main and unchanged (updatedAt 2025-12-12T22:30:04.353811Z). No collection of the planned 47 pieces took place.

Live REST/MCP validation passed: all 22 categories and 26 swipes consistent; all five tool input/output schemas unchanged; structured search scores and card/category responses compatible with REST. Validation performed zero OpenAI calls and no database mutations.
