# Swipe Brain: controlled ingestion

Development only: branch `mcp-upgrade`, service `api-copy-estruturas-mcp`.
Do not deploy this branch to the original production service.

## Discovery

`GET /coletar-swipes` captures one Swipefile listing through Crawl4AI and
returns canonical, unique candidate URLs. It makes no OpenAI calls and no
database writes. Navigation and assets are excluded. A candidate is not a
guarantee of editorial quality: review candidates before paid ingestion.
There is no recursive crawling or automatic pagination.

## Batch

`POST /processar-swipes` accepts JSON:

```json
{
  "urls": ["https://swipefile.com/postcard-formula-that-closed-a-390k-job"],
  "limite": 1,
  "dry_run": true
}
```

Simulation is the default. It checks existing records without crawling,
classifying or writing. The caller submits selected URLs, not an unrestricted
crawl target. Up to 100 URLs may be submitted; at most 3 new candidates are
attempted per execution. The default limit is 1. Failed candidates consume the
limit and are not retried. Deferred URLs are returned as `adiado_por_limite`.

Paid execution requires `dry_run: false`, the environment setting
`SWIPE_INGESTION_ENABLED=1`, a dedicated `SWIPE_INGESTION_TOKEN` of at least
32 characters, and a matching `Authorization: Bearer` header. Never reuse
OpenAI or Crawl4AI credentials as the ingestion credential, commit tokens, or
place them in URLs. Without these settings paid ingestion returns HTTP 503.
The legacy `/test-crawler` is subject to the same protection and batch limits.

Response counters: `descobertos` (unique canonical submitted candidates),
`processados`, `ignorados` (input duplicates, existing and deferred),
`duplicados_entrada`, `chamadas_openai` (attempts including failures),
`total_erros`, `planejados`, `resultados`, and per-URL `erros`.
In simulation, selected URLs appear in `planejados` rather than `processados`.

## Limits and deduplication

Classification uses `gpt-6-luna`, at most 12,000 content characters and 2,000
output tokens per attempt. There are no automatic retries. These limits bound
calls and payload size, not an exact monetary budget. A 150-second scheduling
budget prevents starting further paid stages after expiry; an in-flight HTTP
call may still take up to its 60-second timeout.

A PostgreSQL advisory lock allows only one paid ingestion at a time across
API workers. Existing source URLs are compared canonically before any capture.
A transaction-level URL lock protects saving against concurrent cooperative
writers. No existing rows are deleted or rewritten and no schema migration is
required. External writers bypassing these locks must be addressed before
opening ingestion to additional systems. URL lookups currently scan source
URLs; add a canonical URL index when the curated library grows.

Failures in one candidate do not discard successfully committed candidates.
Provider exception bodies and credentials are omitted from public errors.
Discovery/simulation are read-only public endpoints; paid ingestion is not
exposed through MCP. Client plugins remain consumers of the shared MCP.

## Validation

Run `python -m unittest -v test_discovery test_ingestion`.
Tests cover filtering and canonicalization, no paid calls during discovery or
simulation, per-item failures, authentication, call limits, existing records,
locking, and reasoning items preceding Responses API messages.

Before enabling paid execution, verify the discovery and simulation endpoints
on the development service. Then validate a single selected candidate and
repeat its URL to verify reuse of its ID without another classification.

## Follow-up

All four MCP tools and equivalent REST reads use the shared PostgreSQL read
model in `swipe_queries.py`. `SWIPES_DB` is retained only for explicit seeding,
with no import or fallback during ordinary startup or reads. Embeddings,
hybrid retrieval, editorial quality validation and new sources are subsequent
stages. Semantic embeddings and a separate semantic tool are now available; see
SEMANTIC.md. Newly saved swipes receive an embedding attempt automatically. See `POSTGRES_MCP.md` for this read-layer contract.
