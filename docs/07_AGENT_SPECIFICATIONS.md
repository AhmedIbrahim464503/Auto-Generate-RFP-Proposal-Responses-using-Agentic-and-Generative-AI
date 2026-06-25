# 07. Agent Specifications

## Agent System Overview
The system uses a collaborative multi-agent architecture:

### 1. The Parser Agent
- **Responsibility**: Ingests unstructured files and extracts table headers, questions, metadata, and constraints.

### 2. The Retrieval Agent
- **Responsibility**: Queries the Vector DB and knowledge base, ranking references for relevancy.

### 3. The Writer Agent
- **Responsibility**: Integrates questions and context to write draft responses matching tone and requirements.

### 4. The Compliance & Review Agent
- **Responsibility**: Reviews drafts against original RFP constraints (word counts, formatting, mandatory clauses) and corrects inconsistencies.

## Shared Agent Interface (Phase 2)
All agents output a structured Pydantic model (`AgentOutput`) containing:
- **Decision**: Final outcome
- **Confidence**: Score from 0.0 to 1.0
- **Reasoning**: Plain text reasoning
- **Evidence**: List of source citations
- **Risks**: Potential issues
- **Recommendations**: Proposed steps
- **Processing Time**: Duration in ms
- **Metadata**: Dictionary of model execution details
