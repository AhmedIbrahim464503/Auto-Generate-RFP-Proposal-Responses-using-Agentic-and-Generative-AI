# 04. System Architecture

## Architecture Overview
The system utilizes a modular, microservice-based architecture composed of:
- **Frontend**: Responsive UI (Next.js/React) for bid managers.
- **Backend API**: FastAPI service managing document upload, processing, and agent invocation.
- **Agent Orchestrator**: LangGraph or Autogen framework managing multi-agent workflows.
- **Retrieval Engine (RAG)**: Vector Database (Chroma/Qdrant/pgvector) + Hybrid Search.

## Phase 1 Foundations
- Established Next.js 15 app bootstrap with Tailwind config, themes, and navigation placeholders.
- Configured FastAPI connection and session management pools for PostgreSQL.
- Implemented structured rotating logging, exception handling pipelines, and dependency injection schemas.

## Component Diagram
```mermaid
graph TD
    UI[Web UI] --> API[FastAPI Backend]
    API --> DB[(Relational DB / PostgreSQL)]
    API --> VectorDB[(Vector DB / Chroma)]
    API --> Orchestrator[Agent Orchestrator]
    Orchestrator --> LLM[LLM / Gemini API]
```
