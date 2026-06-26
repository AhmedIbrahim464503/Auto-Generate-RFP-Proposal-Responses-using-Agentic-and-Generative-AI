# 11. Security and Governance

## Data Privacy
- Keep all corporate knowledge base files encrypted at rest and in transit.
- Implement strict RBAC (Role-Based Access Control) to limit visibility to sensitive pricing or tech details.

## Model Governance
- Avoid training public models on uploaded proprietary RFPs.
- Log all API prompts and completions for auditing purposes.

## Plan Locking and Approval Gates (Phase 8)
- Enforce immutable plan locking states: when `ProposalPlan` is marked as `LOCKED`, all updates to metadata, outlines, compliance metrics, and tasks must be blocked at the API layer.
- Require authenticated/authorized signatures for Gate approvals. All planning updates, locks, unlocks, and approvals must be logged relationally with actor context.

## Proposal Generation Security and Governance (Phase 10)
- **Zero-Hallucination Policy**: Strictly prohibit AI agents from fabricating facts or claims. If the retrieval engine cannot find evidence, a `[CONTENT_GAP: ...]` placeholder must be generated.
- **Traceability/Citation Enforcement**: Every AI-generated claim must be traceably linked to a source document reference (e.g., knowledge asset) or marked explicitly as an assumption.
- **Audit Trails**: Capture details of who generated/regenerated which section, what prompt parameters (actor, tone) were used, and version histories in the relational database.

