# 22. Deployment Architecture

## Production Infrastructure
- Containers: Docker
- Deployment: Kubernetes or Cloud Container Run (AWS/GCP)
- Database: Managed PostgreSQL (Relational) & Qdrant/Chroma (Vector)

## CI/CD Pipeline
- Automated unit tests and lint checks.
- Build Docker images and push to secure container registries.

## Phase 1 Deployment Setup
- Defined root-level multi-container orchestration in `docker-compose.yml` linking FastAPI and PostgreSQL.
- Formulated containerization template `backend/Dockerfile` using modular slim-python layers.
- Established active GitHub Actions workflow at `.github/workflows/ci.yml` verifying linting, dependency compilation, and testing suites.
