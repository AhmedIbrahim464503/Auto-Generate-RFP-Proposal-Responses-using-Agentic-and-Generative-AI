# 26. Project Rulebook

## Rules of Development

### Rule 1: Schema-First Agent Interfaces
Never use raw dictionaries between agents.

### Rule 2: Pydantic Enforcement
All agent outputs must be Pydantic models.

### Rule 3: Structured Agent Output Standard
Every agent must provide:
- **Decision**: Clear outcomes or paths chosen.
- **Confidence**: Numerical or semantic confidence scoring.
- **Reasoning**: Plain-text logical flow.
- **Evidence**: Extracted context/source citation references.
- **Risks**: Enumeration of potential bottlenecks or concerns.
- **Recommendations**: Actionable next steps.

### Rule 4: Decoupled UI
No business logic inside the UI.

### Rule 5: UI Access Isolation
No direct database access from the UI.

### Rule 6: Test Requirements
Every feature requires tests.

### Rule 7: Documentation Integrity
Every feature updates documentation.

### Rule 8: No Placeholder Code
No placeholder implementations.

### Rule 9: Fail Loudly
No silent failures.

### Rule 11: Content Gap Isolation
If retrieved knowledge sources are insufficient, do not make up claims. You must output a `[CONTENT_GAP: <details>]` tag rather than hallucinating details.

### Rule 12: Tone Compliance
Ensure style/tone guidelines are translated into explicit system parameters for LLM calls to prevent tone drift in generated output.
