# 23. Advanced Testing Strategy

## Integration Testing
- End-to-end integration workflows validating agent coordination.
- Mocking external LLM API calls for predictable CI/CD testing.

## Performance & Stress Testing
- Mocking concurrency constraints for 100+ simultaneous proposal processes.

## Phase 1 Testing Status
- Configured backend test environment under `tests/backend/` using `pytest`.
- Provided standard conftest file (`tests/backend/conftest.py`) exposing the FastAPI test client.
- Provided frontend unit testing scaffold under `tests/frontend/` using `vitest`.
- Mapped client tests to verify system route responses (/health and /version endpoints).
