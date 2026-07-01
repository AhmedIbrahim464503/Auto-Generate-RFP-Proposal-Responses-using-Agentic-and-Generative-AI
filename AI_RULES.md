# AI Operating Manual (`AI_RULES.md`)

This document defines the permanent rules, coding standards, architecture models, and context constraints for any future AI agent or developer tool interacting with this repository.

---

## 1. Project Overview & Architecture Map

### Technology Stack
* **Backend**: FastAPI (Python 3.12+), SQLAlchemy (SQLite), Alembic, Pydantic v2, PyMuPDF, python-docx, Celery (Redis)
* **Frontend**: Next.js 15 (React 19), Zustand (State), Tailwind CSS, Lucide Icons, React Flow (Workflow maps)
* **Orchestration**: LangGraph (workflow lifecycles, states, and nodes)
* **AI Platform**: Google Gemini API via `google.generativeai` SDK with strict JSON output schemas

### Core Directories & Responsibilities
* `/backend/app/api`: FastAPI route handlers (e.g. `/v1/endpoints/`)
* `/backend/app/core`: Configuration (`config.py`), logger, JWT auth, rate limits, and LangGraph workflow nodes
* `/backend/app/db`: Database connection sessions and seed configurations
* `/backend/app/models`: SQLAlchemy data tables and relations
* `/backend/app/schemas`: Pydantic validation schemas
* `/backend/app/services`: Main business engines (RAG retravel, analysis, planning, review coordinator)
* `/frontend/src/components`: Workspace components (NeuralNetwork3D, ExecutiveDecisionDashboard, ProposalWorkspace)
* `/frontend/src/store`: Zustand unified stores
* `/docs`: Project documentation and architecture details
* `/tests`: Pytest backend test suites and Vitest frontend tests
* `/storage`: Temp location for uploaded files (excluded from indexing)
* `/memory`: Temp location for agent runtime states (excluded from indexing)

---

## 2. Forbidden Operations & Safety Constraints

### Protected Files (DO NOT MODIFY UNLESS EXPLICITLY INSTRUCTED)
* `backend/app/core/config.py` (Central config - high risk)
* `backend/app/db/session.py` (Database engine connections)
* `backend/app/core/workflow/workflow_nodes.py` (Orchestration nodes)
* `frontend/package.json` & `package-lock.json` (Dependency locks)
* `backend/pyproject.toml` (Python environment configuration)

### Safe Modification Zones
* `backend/app/services/` (Business logics, RAG search filters, exporters)
* `backend/app/schemas/` (Pydantic schemas and serialization rules)
* `frontend/src/components/` (Frontend React views, widgets, and charts)
* `frontend/src/store/` (Zustand state bindings)
* `tests/` (Test suites)

### Core Restrictions
1. **No Automatic Code Removal**: Do not remove, replace, or prune unused logic/comments unless explicitly requested.
2. **Strict Schema Constraints**: The `google.generativeai` SDK throws `ValueError` for JSON schemas containing `"default"`, `"maximum"`, `"minimum"`, `"exclusiveMaximum"`, or `"exclusiveMinimum"`.
   * **Rule**: When passing Pydantic classes to `response_schema`, they *must* be pre-processed using the `clean_schema_dict` helper in each service's `run_inference_with_retry`.
3. **No Database schema changes without Migrations**: Run Alembic migrations to apply structural changes.

---

## 3. Context & Resource Limits

* **Maximum Files Loaded per Action**: 5 files.
* **Maximum Context Size**: Avoid loading files recursively unless they contain active imports.
* **Files to Never Scan (Exclude from Indexing)**:
  * `frontend/node_modules/`
  * `.venv/` (and the external relocated `d:\projects\RFP-venv/`)
  * `frontend/.next/`
  * `storage/`
  * `memory/`
  * `.pytest_cache/`
  * `__pycache__/`
  * `*.db` (local SQLite files)

---

## 4. Development Workflow Guidelines

### Phase-based Execution
Always split complex requests into logical execution phases:
1. **Research & Plan**: Analyze targets, inspect schemas, map imports.
2. **Implementation**: Modify components, add validation rules, write helper modules.
3. **Verification**: Run `pytest` or `vitest` to verify behavior.
4. **Documentation**: Update code comments, walkthroughs, and logs.

### Coding Standards
* **Python**: Enforce absolute type-hinting, async endpoint declarations, and Pydantic validation schemas.
* **TypeScript/React**: Keep components decoupled, utilize Zustand for unified state management, and write semantic HTML elements with unique IDs.
* **Error Handling**: Log failures recursively via the system logger, and return structured, informative HTTP exceptions.
* **Logging**: Inject logger records into service gateways indicating call latency, success metrics, and RAG retrieval token volumes.
