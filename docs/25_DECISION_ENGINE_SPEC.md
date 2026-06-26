# 25. Decision Engine Specifications

## Intent Classification
- Route user inputs (e.g., "Draft this", "Summarize this", "Apply pricing context") using structured LLM calls or classifier models.

## Agent Decision Trees
- LangGraph conditional edges determining:
  - If retrieved context is sufficient.
  - If a draft requires review or correction.

## Relational Decision Schemas (Phase 2)
The decision parameters are represented by database schemas:
- `qualification_decision`: Stores final GO/NO_GO, confidence, reasoning, evidence, and recommendations.
- `financial_review`, `legal_review`, `operations_review`, `technical_review`: Individual department assessment nodes feeding the final qualification gate.
- `approval_gate` & `approval_decision`: Track the 4 human approval gate results.

## Section Classification Models (Phase 4)
- **Classifier Labels**: Introduction, Background, Scope, Requirements, Evaluation, Deliverables, Commercial, Legal, Technical, Submission Instructions, Appendix, Other.
- **Confidence Metrics**: Persisted for every section classification. Flat segments list can be queried via `GET /api/v1/documents/{id}/sections`.
