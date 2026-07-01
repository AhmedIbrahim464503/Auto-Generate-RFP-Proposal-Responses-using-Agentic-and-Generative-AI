# Changelog

All notable changes to the SPS Enterprise AI Proposal Capture Manager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-06-28
### Added
- **Phase 17 (Quality Assurance)**: Created permanent project engineering standards, AI Operating Manual (`AI_RULES.md`), and workspace context maintenance guides under `/docs`.
- **Phase 16 (Workspace Optimization)**: Relocated Python virtual environment outside the workspace directory to eliminate file watching/indexing overhead; configured VS Code exclusions, `.cursorignore`, and optimized `.gitignore`.

## [1.0.0] - 2026-06-27
### Added
- **Phase 15 (Operations)**: Standardized JWT OAuth2 security middleware with Least-Privilege RBAC controls, SlowAPI IP-based rate limiters, background tasks queues via Celery+Redis, and Word DOCX/Markdown proposal compilers.
- **Phase 14 (Command Center)**: Responsive multi-workspace sidebar console with React Flow workflow maps, 3D Neural Particle Visualizer, and Zustand global stores.
- **Phase 13 (Workflow Platform)**: LangGraph state-machines with automatic resume checkpoints, rollback recovery, and branch routing engines.
- **Phase 12 (Evaluations)**: Advanced compliance validator grids and multi-agent QA scoring criteria pipelines.
- **Phases 0-11**: Core bid qualification logic, pgvector/FAISS RAG retrievers, and planning work breakdown structures.
