# 20. Prompt Engineering Guide

## System Prompt Templates

### Writer Agent
```text
You are a senior proposal response writer. Draft a comprehensive response to the following RFP question based on the retrieved context guidelines...
```

### Reviewer Agent
```text
You are a compliance officer. Check the draft response against the constraints...
```

## Phase 4 AI Document Intelligence Prompts
Prompts are registered inside `backend/app/services/ai_engine.py` under the version key `v1.0`:
- **System Instruction**: Sets context for the Gemini 2.5 Flash agent as an intelligence extraction engine.
- **segmentation_prompt**: Instructs model to segment text into nested hierarchical tree structures.
- **metadata_prompt**: Extracts client name, document title, normalized deadlines, primary contacts, and checks extraction quality.
