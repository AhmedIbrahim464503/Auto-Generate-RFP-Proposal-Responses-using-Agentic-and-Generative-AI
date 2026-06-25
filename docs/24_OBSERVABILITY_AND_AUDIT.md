# 24. Observability and Audit

## Trace Logging
- OpenTelemetry integrations for request/response traces.
- LangSmith / Phoenix tracing for detailed agent and LLM call histories.

## Audit Logs
- Tracking user modifications to generated responses.
- Access history logs for all ingested proprietary files.
- **Ingestion Audit Events (Phase 3)**: Logs `DOCUMENT_UPLOADED` audit events including actor name, action timestamp, entity name, and unique document key reference in the database.
