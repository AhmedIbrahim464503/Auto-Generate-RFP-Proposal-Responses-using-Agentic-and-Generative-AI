# 09. API Specifications

## REST API Endpoints

### Project Management
- `POST /api/projects`: Create project.
- `GET /api/projects/{id}`: Fetch project details.

### Document Management
- `POST /api/projects/{id}/upload`: Upload RFP/Knowledge base file.

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
