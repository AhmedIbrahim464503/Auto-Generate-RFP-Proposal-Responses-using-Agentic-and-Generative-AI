# 03. Software Requirements Specification (SRS)

## Functional Requirements
1. **RFP Parser**: System must parse tabular and structured questions from PDF/DOCX.
2. **Context Retrieval**: System must run hybrid search (BM25 + Vector Search) on uploaded knowledge sources.
3. **Agentic Generation**: Mult-agent workflow to draft, review, and refine answers.
4. **Export**: Export final proposal in standard DOCX or PDF format.

## Non-Functional Requirements
- **Security**: Data isolation for proprietary corporate data.
- **Latency**: Generation of a standard draft response in < 30 seconds.
- **Scalability**: Handle documents up to 500 pages.
