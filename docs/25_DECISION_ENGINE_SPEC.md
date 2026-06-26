# 25. Decision Engine Specifications

## Intent Classification
- Route user inputs (e.g., "Draft this", "Summarize this", "Apply pricing context") using structured LLM calls or classifier models.

## Agent Decision Trees
- LangGraph conditional edges determining:
  - If retrieved context is sufficient.
  - If a draft requires review or correction.

## Relational Decision Schemas (Phase 2 & Phase 7)
The decision parameters are represented by database schemas:
- `qualification_decision`: Stores recommendation, final GO/NO_GO/ESCALATE/GO_WITH_CONDITIONS, confidence, reasoning, evidence, Opportunity Score, and Estimated Win Probability.
- `qualification_scoring_breakdown`: Stores weighted scoring per dimension.
- `qualification_decision_history`: Audit trail for executive overrides/approvals.
- `qualification_executive_comment`: Collaboration logs.
- `qualification_rule`: Versioned ruleset configurations.
- `financial_review`, `legal_review`, `operations_review`, `technical_review`: Individual department assessment nodes feeding the final qualification gate.
- `approval_gate` & `approval_decision`: Track the 4 human approval gate results.

## Section Classification Models (Phase 4)
- **Classifier Labels**: Introduction, Background, Scope, Requirements, Evaluation, Deliverables, Commercial, Legal, Technical, Submission Instructions, Appendix, Other.
- **Confidence Metrics**: Persisted for every section classification. Flat segments list can be queried via `GET /api/v1/documents/{id}/sections`.

## Enterprise Qualification & Decision Engine (Phase 7)
- **Scoring Engine**: Configurable weights loaded dynamically from active ruleset: Strategic Fit, Capability Alignment, Financial Viability, Technical Readiness, Compliance Readiness, Risk, Relationship, Complexity. Calculates an Opportunity Score (0–100).
- **Veto Rules**: Triggers vetoes or strict block overrides based on department review NO_GO (Legal/Financial Veto).
- **Estimated Win Probability**: Separately calculated using Gemini 2.5 Flash based on Opportunity Score, department outcomes, risks, and evidence.

