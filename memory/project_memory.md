# Project Memory

## Project Identity
- **Name**: Auto-Generate RFP Proposal Responses using Agentic and Generative AI
- **Owner**: AhmedIbrahim464503

## Context
This project aims to automate the generation of RFP responses via Generative AI and multi-agent systems.

## Key Design Principles
- Modern, fast, and responsive user interface.
- High retrieval relevance using hybrid search.
- Clean separation of parser, retriever, writer, and compliance/reviewer agents.
- **Contract-First & Strictly Typed**: Fully defined relational SQLAlchemy tables, structured Pydantic input/output schemas (`AgentOutput`), and GraphState.
- **Specialized Writer Orchestration**: Specialized multi-agent writing workflows using a 15-writer persona registry, dynamic tone styling, quality validations, and zero-hallucination gap protections.
- **De-coupled Registries & Safe Governance**: Strict separation of concern by routing all LLM/Agent calls through Model/Agent/Prompt Registries. Real-time safety validation (redactions, injections defense, safety block words) on all agent input/outputs.
