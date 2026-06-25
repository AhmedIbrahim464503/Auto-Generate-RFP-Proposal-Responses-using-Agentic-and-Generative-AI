# 22. Deployment Architecture

## Production Infrastructure
- Containers: Docker
- Deployment: Kubernetes or Cloud Container Run (AWS/GCP)
- Database: Managed PostgreSQL (Relational) & Qdrant/Chroma (Vector)

## CI/CD Pipeline
- Automated unit tests and lint checks.
- Build Docker images and push to secure container registries.
