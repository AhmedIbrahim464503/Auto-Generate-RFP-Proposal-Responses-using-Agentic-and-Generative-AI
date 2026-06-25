# 05. Database Design

## Schema Design

### Users
- `id` (UUID, Primary Key)
- `email` (String, Unique)
- `name` (String)
- `role` (Enum: Admin, Writer, Reviewer)

### Projects (RFPs)
- `id` (UUID, Primary Key)
- `title` (String)
- `description` (Text)
- `status` (Enum: In_Progress, Under_Review, Completed)
- `created_at` (Timestamp)

### Questions
- `id` (UUID, Primary Key)
- `project_id` (UUID, Foreign Key)
- `question_text` (Text)
- `suggested_answer` (Text)
- `status` (Enum: Draft, Reviewed, Approved)

## Database Implementation Status (Phase 1 & 2)
- Configured connection string parsing via pydantic settings.
- Initialized SQL Alchemy base model registry `Base` in `backend/app/db/base_class.py`.
- Formulated local session dependency `get_db` in `backend/app/db/session.py`.
- Configured Alembic configuration file `alembic.ini` and environment `env.py` mapping model metadata for auto-migrations.
- Created all 22 domain database models under `backend/app/models/` and compiled import mapping registry in `backend/app/db/base.py`.
- Wrote full migration runner sequence at `backend/alembic/versions/1a2b3c4d5e6f_create_domain_tables.py`.

## Phase 2 Schema Entities & Relationships
1. **opportunity**: Hub for proposal capture transactions. 1-to-many relationship with `rfp_document`, `financial_review`, `legal_review`, `operations_review`, `technical_review`, and `approval_gate`. 1-to-1 relationship with `qualification_decision` and `proposal_plan`.
2. **rfp_document**: Child of `opportunity`. Parent of `requirement` (1-to-many).
3. **requirement**: Core requirements extracted. Parent of `deliverable`, `evaluation_criteria`, and `submission_instruction` (1-to-many).
4. **reviews**: Individual department assessment tables (`financial_review`, `legal_review`, `operations_review`, `technical_review`). Bind back to `opportunity`.
5. **qualification_decision**: Go/No-Go final choice. Binds to `opportunity`.
6. **proposal_plan**: Proposal outline. Parent of `proposal_section`.
7. **compliance_matrix**: Auto-assessment matrix. Parent of `compliance_item`.
8. **audit_event**: Trace logger tracking actor, action, timestamp, correlation_id, old/new value deltas.
9. **approval_gate & approval_decision**: Tracks the human sign-offs for Gates 1-4.
10. **agent_execution**: Tracks confidence scores, processing times, LLM tokens, and decisions for all agents.
11. **knowledge_asset & search_result**: Relational mapping for Vector retrieval citations.
12. **system_configuration**: Global key-value configs.

