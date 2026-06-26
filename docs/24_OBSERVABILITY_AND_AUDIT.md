# 24. Observability and Audit

## Trace Logging
- OpenTelemetry integrations for request/response traces.
- LangSmith / Phoenix tracing for detailed agent and LLM call histories.

## Audit Logs
- Tracking user modifications to generated responses.
- Access history logs for all ingested proprietary files.
- **Ingestion Audit Events (Phase 3)**: Logs `DOCUMENT_UPLOADED` audit events including actor name, action timestamp, entity name, and unique document key reference in the database.
- **Proposal Planning History Trails (Phase 8)**: Tracks `GENERATE`, `EDIT`, `LOCK`, `UNLOCK`, `APPROVE`, and `REJECT` actions with actor, comments, payload snapshot details, and timestamps persisted in `planning_history` table.
- **Proposal Generation Audit & Tracing (Phase 10)**: Logs all generation actions including parameters like writer role, style instructions, prompt configurations, response timestamps, latency, quality validation scores, and citations mapping to `generation_history` and `proposal_citation` tables.

