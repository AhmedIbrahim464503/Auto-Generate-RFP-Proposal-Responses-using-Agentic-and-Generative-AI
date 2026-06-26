# 09. API Specifications

## REST API Endpoints

### Project Management
- `POST /api/projects`: Create project.
- `GET /api/projects/{id}`: Fetch project details.

### Document Ingestion (Phase 3 Active Endpoints)
- `POST /api/v1/documents/upload`: Multi-part form upload for PDF & DOCX files (resolves/auto-creates Opportunity).
- `GET /api/v1/documents`: Lists all active rfp_document entries.
- `GET /api/v1/documents/{id}`: Fetches details of a specific document.
- `GET /api/v1/documents/{id}/status`: Fetches document processing status sequence.
- `GET /api/v1/documents/{id}/metadata`: Extracts structural metadata (page count, format, word counts) from fitz/docx.

### Proposal Processing
- `POST /api/projects/{id}/process`: Start parsing.
- `POST /api/questions/{id}/draft`: Trigger AI response generation.
- `PUT /api/questions/{id}/approve`: Approve response.

### Proposal Planning & WBS (Phase 8 Endpoints)
- `POST /api/v1/proposals/{id}/planning`: Triggers the LLM generation of the planning package.
- `GET /api/v1/proposals/{id}/planning`: Retrieves the full plan summary metadata.
- `GET /api/v1/proposals/{id}/outline`: Fetches proposal outline sections.
- `GET /api/v1/proposals/{id}/compliance-matrix`: Retrieves the mapped compliance matrix rows.
- `GET /api/v1/proposals/{id}/timeline`: Fetches chronological milestones.
- `GET /api/v1/proposals/{id}/tasks`: Retrieves WBS tasks.
- `POST /api/v1/proposals/{id}/approve-plan`: Approves or rejects the planning package.
- `POST /api/v1/proposals/{id}/update-plan`: Supports human editing of outline nodes, compliance rows, timeline dates, and tasks.
- POST /api/v1/proposals/{id}/lock-plan: Locks the plan against modifications.
- POST /api/v1/proposals/{id}/unlock-plan: Unlocks the plan.

### Enterprise Knowledge Platform (Phase 9 Endpoints)
- `POST /api/v1/knowledge/upload`: Uploads a knowledge asset file (PDF, DOCX, TXT, MD) with tags, owner, and BU metadata.
- `POST /api/v1/knowledge/index`: Triggers chunking and embedding index jobs.
- `GET /api/v1/knowledge`: Lists assets with pagination and filters.
- `GET /api/v1/knowledge/{id}`: Fetches asset details.
- `GET /api/v1/knowledge/chunks`: Fetches chunks for specific assets.
- `GET /api/v1/knowledge/search`: Performs hybrid retrieval search querying the pipeline.
- `GET /api/v1/knowledge/categories`: Fetches list of active document types.
- `GET /api/v1/knowledge/history`: Fetches search latency stats and logs.
- `POST /api/v1/knowledge/{id}/update`: Updates asset metadata and governance approval states.

### Enterprise Proposal Content Generation (Phase 10 Endpoints)
- `POST /api/v1/proposals/{id}/generate`: Generates full proposal drafts across all outline sections, running coordinator orchestration.
- `GET /api/v1/proposals/{id}/generated`: Lists generated proposal sections containing content, metadata, and status.
- `POST /api/v1/proposals/{id}/generate/section/{section_id}`: Regenerates a single outline section draft with optional override prompts, style/tone settings, and writer roles.
- `GET /api/v1/proposals/{id}/generation-history`: Retrieves full historical versions and edit history logs of generated contents.
- `GET /api/v1/proposals/{id}/citations`: Retrieves citation records mapping generated paragraphs to verified knowledge chunks.

### Enterprise AI Platform Foundation (Phase 10.5 Endpoints)
- `GET /api/v1/ai-platform/models`: Retrieves list of registered models (e.g. Gemini, OpenAI, Claude).
- `POST /api/v1/ai-platform/models`: Submits/registers a new model configuration.
- `GET /api/v1/ai-platform/agents`: Lists all registered agents and their capabilities.
- `GET /api/v1/ai-platform/prompts`: Lists versioned prompts and user templates.
- `POST /api/v1/ai-platform/prompts`: Creates a new approved prompt template revision.
- `GET /api/v1/ai-platform/metrics`: Fetches detailed agent performance execution logs (latencies, token counts, costs).
- `GET /api/v1/ai-platform/explainability`: Retrieves explainability inputs, reasoning flows, evidence, and rule states logs.


## Schema Contracts (Phase 2 & Phase 8)
All payload requests and response contracts are defined in `backend/app/schemas/api_contracts.py`:
- **Upload**: `UploadResponse`
- **Department Reviews**: `DepartmentReviewRequest`, `DepartmentReviewResponse`
- **Qualification**: `QualificationRequest`, `QualificationResponse`
- **Planning**: `CreatePlanRequest`, `PlanResponse`
- **Proposal Generation**: `GenerateProposalRequest`, `ProposalGenerationResponse`
- **Compliance Matrix**: `ComplianceMatrixResponse`
- **Gate Approvals**: `GateApprovalRequest`, `GateApprovalResponse`
- **Audit logs**: `AuditLogResponse`
- **Dashboard**: `DashboardSummaryResponse`
