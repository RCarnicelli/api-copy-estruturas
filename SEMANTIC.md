# Semantic layer v1

Development: `mcp-upgrade` / `api-copy-estruturas-mcp` only.

Model `text-embedding-3-small`, dimensions 1536, text version
`swipe-semantic-v1`. The existing vector(1536) column is reused; incompatible
dimensions cause a safe startup failure instead of destructive conversion.

## Semantic document

Fields, in deterministic order: title, description, category, framework,
objective, emotion, tone, hook, mechanism, cta, why_it_works, adaptation,
when_to_use, tags. Field labels remain present. Whitespace is normalized, lists
are sorted/deduplicated, each field is capped at 1000 characters, and the final
document is capped at 2048 cl100k_base tokens. Raw HTML/Markdown, source URLs,
IDs, dates and brand-specific client knowledge are excluded. This indexes the
classified persuasive structure, without navigation noise or mixing clients'
knowledge into the shared library. Sparse legacy templates remain sparse;
vectors do not turn these examples into evidence-backed real advertisements.

SHA-256 includes normalized text, model, dimension and text version. Unchanged
documents are skipped. The database tracks embedding_model, embedding_hash,
embedding_text_version, embedding_tokens, embedded_at and embedding_dirty.
A trigger marks semantic-field edits dirty. Dirty rows are excluded from
semantic search; whitespace-only/list-order changes can reuse the same hash
without a paid call. A version change requires deliberate reindexing.

## Execution and cost

`POST /embeddings` defaults to a free plan (`dry_run: true`). Paid execution
requires `dry_run: false` and the dedicated SWIPE_EMBEDDING_TOKEN Bearer header.
Maximum 25 selected swipes per execution, API chunks of 8, no automatic retries.
Provider outputs are dimension/finiteness checked and indexed by response
index. Successfully saved chunks survive other chunk failures. A database lock
serializes reindexing; rows are rechecked after acquiring the lock and again
before committing each vector, preventing stale writes and normal duplicate
charges. Failed persistence after a successful provider call can require a
future paid retry; external provider calls cannot be made atomic with PostgreSQL.

At the documented standard rate of USD 0.02 per million input tokens, the
maximum 25*2048 token document job is about USD 0.001024. Plans return actual
token counts and estimates; completed jobs return reported provider usage.
`embedding_usage` reserves and audits all provider attempts, including failures.
Limits are 50 document API calls and 100 uncached query API calls per UTC
database day, shared across processes. These limits are deliberately small and
can be revisited before higher-volume use. Paid backfill is never automatic on
startup. A single newly ingested swipe is embedded after saving; failure leaves
the swipe pending, without recrawling/reclassification on embedding recovery.

## Retrieval

New MCP `buscar_swipes_semanticos(consulta, categoria, objetivo, emocao, tom,
limite)` and REST `POST /buscar-swipes-semanticos` share the same implementation.
The four existing tools and their schemas/ranking remain unchanged. Category,
objective, emotion and tone are optional exact, case/space-normalized filters,
combined with AND. The old structured search retains its soft weighted matching.

The new tool uses pgvector exact cosine distance (`<=>`) over current compatible
vectors, returning `semantic_score`, `matched_by`, `ranking: cosine` and cache
metadata. Similarity is not a probability or proof of business performance.
No eligible filtered rows means no query embedding cost. Normalized query
vectors are cached persistently in `semantic_query_cache`, keyed by model,
dimension, version and text hash. Database locks prevent concurrent cache misses
from charging twice. Query length is capped at 2000 characters and limit at 20.

Exact search is appropriate for the current 25-row library and keeps recall
predictable with filters. An approximate HNSW index is intentionally deferred
until scale justifies it. Semantic scores and persisted structured fields are
returned separately, ready for a future fusion stage and reranker. No fusion
weights or reranker are introduced here. Actual embedding floats stay in the
database; legacy response key `embedding` remains null to avoid 1536-value
payloads in every tool response. No existing swipe is deleted or reclassified.

## Validation

Run `python -m unittest -v test_discovery test_ingestion test_postgres_mcp test_semantic`.
Validate live: free plan -> authenticated backfill -> repeat job with zero new
provider calls -> semantic MCP query -> repeat query with cache hit -> filtered
query reusing its vector -> impossible filter with zero paid calls. Confirm
25 current vectors of dimension 1536, original tool schemas, unchanged swipe
IDs/count and unchanged production service.
