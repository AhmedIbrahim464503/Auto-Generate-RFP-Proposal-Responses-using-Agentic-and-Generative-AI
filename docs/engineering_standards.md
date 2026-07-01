# Project Engineering Standards

This document establishes the official engineering standards, design patterns, and programming rules for the SPS Proposal Capture platform.

---

## 1. Backend Standards (FastAPI / Python)

### 1.1 Type Annotations
All Python code must include explicit, strict type hints. Do not use `Any` unless absolutely necessary, and prefer `Union` or `Optional` to clarify optional outputs.
```python
async def get_document_meta(db: Session, doc_id: str) -> Optional[dict]:
    ...
```

### 1.2 Async Declarations
Use `async def` for all API endpoint controllers and route handlers. For IO-bound operations running inside background worker cycles, utilize FastAPI's `run_in_threadpool` or Celery tasks to prevent event-loop blocking.

### 1.3 Schema Validation
All request payloads and response contracts must use Pydantic v2 BaseModels. 
* **Warning**: When interacting with the Gemini API via the `google.generativeai` SDK, ensure Pydantic validation constraints (e.g. `Field(..., ge=0, le=1)`) are cleaned dynamically before schema creation using `clean_schema_dict` to avoid serialization exceptions.

---

## 2. Frontend Standards (Next.js / React)

### 2.1 Component Structure
* Design components to be functional, reusable, and single-purpose.
* Store global states inside Zustands stores (`/frontend/src/store/`) rather than prop-drilling or React Context.
* Use Tailwind CSS variables defined in `tailwind.config.ts` for coloring, text styles, and layouts.

### 2.2 Semantic Elements & IDs
Every interactive element (buttons, input fields, select dropdowns) must use valid semantic HTML (e.g., `<button>`, `<input>`) and must have a unique `id` attribute to support automated E2E browser tests.

---

## 3. Error Handling & Exception Logging

* **Backend**: Catch runtime failures in routes and raise a structured `HTTPException` with a diagnostic message and error details.
* **Logging**: Inject clear log markers using the `logger` module:
  * `logger.info()`: Successful service runs, completed processes, latency metrics.
  * `logger.warning()`: Recoverable errors, retried connection attempts, fallbacks.
  * `logger.error()`: Pydantic validation errors, API quota limitations, service failures (always include trackback exceptions).

---

## 4. Testing Requirements

* **Code Coverage**: All backend endpoints and core service engines must have corresponding unit tests under `/tests/backend/`.
* **Mocking**: Mock external network dependencies (such as Gemini API endpoints, pgvector storage, and Redis queues) in tests to guarantee offline test stability.
