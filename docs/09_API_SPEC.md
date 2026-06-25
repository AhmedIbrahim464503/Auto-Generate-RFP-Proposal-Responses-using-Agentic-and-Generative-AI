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

## Schema Contracts (Phase 2)
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
