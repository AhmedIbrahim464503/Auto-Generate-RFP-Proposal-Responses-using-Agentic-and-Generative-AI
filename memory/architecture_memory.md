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
