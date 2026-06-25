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
