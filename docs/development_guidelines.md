# Developer Implementation Guidelines

This guide establishes the rules and steps for implementing new features, modifying existing logic, and resolving bugs.

---

## 1. Implementing New Features

1. **Schema Definition**: Define input/output payloads under `backend/app/schemas/` using Pydantic. Ensure there are no numeric constraints (`maximum`/`minimum`) or default parameters without cleaning handlers if they will be passed to Gemini API.
2. **Database Models**: Add any new tables under `backend/app/models/` using SQLAlchemy. Generate migrations using Alembic:
   ```bash
   d:\projects\RFP-venv\Scripts\python.exe -m alembic revision --autogenerate -m "description"
   ```
3. **Core Services**: Write the business logic inside a new service under `backend/app/services/`.
4. **API Router**: Expose REST endpoints in `/api/v1/endpoints/` and register them in `/api/v1/router.py`.

---

## 2. Bug Resolution Protocol

1. **Replicate**: Write a failing unit test under `/tests/` to reproduce the bug.
2. **Trace**: Check the logs at `logs/app.log` or console outputs to pinpoint the failure.
3. **Fix**: Apply target edits without modifying unrelated business logic.
4. **Verify**: Run the test suite:
   ```bash
   cmd /c "set PYTHONPATH=. && d:\projects\RFP-venv\Scripts\python.exe -m pytest"
   ```
5. **Human Gate**: Document the root cause and the fix, then request review.

---

## 3. Refactoring Code

* Refactoring must only improve maintainability, speed, or type safety without changing API endpoints, database schemas, or business outcomes.
* Keep edits focused; do not combine refactoring with new feature additions.
* Re-verify all existing tests to guarantee zero regressions.
