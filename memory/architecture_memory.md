# Architecture Memory

## System Layers
1. **Presentation Layer**: Next.js 15, Zustand, Tailwind CSS, ShadCN UI, Framer Motion, Three.js, React Three Fiber.
2. **Application Layer**: FastAPI routes, schemas, and service controllers.
3. **Agent Orchestration Layer**: LangGraph workflows, state management.
4. **Domain Layer**: Clean domain models, validation, business rules.
5. **Persistence Layer**: PostgreSQL + SQLAlchemy (relational), FAISS (vector index).
6. **Infrastructure Layer**: Docker, Docker Compose, external APIs (Gemini 2.5 Flash).

## Architecture Decisions
- Schema-first inputs/outputs using Pydantic between all agents.
- Four mandatory Human-in-the-Loop (HITL) approval gates.
- Observability via trace logs and OpenTelemetry/LangSmith.
- **Relational Domain Layout (Phase 2)**: Standardized mapping database files (`backend/app/db/base.py`) compiling 22 entities.
- **Structured Contracts**: Created Pydantic agent models (`AgentOutput`), state schemas (`GraphState`), and request/response API contracts.
- **Proposal Planning Framework (Phase 8)**: Decoupled planning package representing adaptive outlines, compliance matrices, WBS tasks, timeline milestones, document checklists, and clarifications. Enforces lock states at the API layer to guarantee data immutability.
- **Enterprise Knowledge Platform (Phase 9)**: Pluggable model embeddings and rerankers, abstract vector search interface supporting production pgvector and in-memory list fallbacks, semantic chunking pipelines, and citation metadata tracking.
- **Enterprise Proposal Content Generation Platform (Phase 10)**: Multi-agent coordination engine (Proposal Generator Service) containing a prompt registry, style engine, citation engine, quality validator, and 15 specialized writers. Includes side-by-side diff workspace UI with evidence and quality scoring metrics dashboards.
- **Enterprise AI Platform Foundation (Phase 10.5)**: Reusable BaseAgent framework, database registries (Models, Agents, Prompts, Tools, Workflows, Capabilities), dynamic model routing and resolution, central Governance safety validation layer, pub/sub event bus signaling, stateful cache KV memories, and explainability/metrics persistences.


