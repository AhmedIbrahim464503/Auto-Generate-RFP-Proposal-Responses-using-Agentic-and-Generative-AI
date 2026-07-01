# AI Context Management Strategy

This document outlines standard guidelines for managing context size and token efficiency during AI-assisted development sessions.

---

## 1. Simulated Agent Stress Test Matrix

To optimize interaction sizes, we analyzed the context footprint of various typical tasks. The following matrix estimates workload profiles:

| Scenario | Task Description | Estimated Context Size | Estimated Files Loaded | Risk Level | Expected Stability | Key Optimization |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | Review backend architecture | ~25,000 tokens | 6 - 8 files | Low | High | Only load abstract classes/endpoints. |
| **2** | Review frontend only | ~18,000 tokens | 5 - 6 files | Low | High | Limit search to active components and stores. |
| **3** | Review documentation only | ~8,000 tokens | 3 - 5 files | Very Low | High | Read markdown headings instead of full logs. |
| **4** | Review tests only | ~12,000 tokens | 4 - 5 files | Low | High | Target specific test files under `/tests/`. |
| **5** | Generate API documentation | ~15,000 tokens | 4 - 5 files | Low | High | Inspect routing tables and Pydantic schemas only. |
| **6** | Modify one backend file | ~20,000 tokens | 2 - 3 files | Medium | Medium | Perform contiguous replacements on target lines. |
| **7** | Modify one frontend file | ~15,000 tokens | 2 - 3 files | Medium | Medium | Edit targeted React components or Zustand store keys. |
| **8** | Update documentation | ~5,000 tokens | 1 - 2 files | Very Low | High | Append sections using localized edits. |
| **9** | Run testing workflow | ~6,000 tokens | 2 - 3 files | Low | High | Execute tests targeting single files. |
| **10**| Generate implementation report | ~8,000 tokens | 2 - 3 files | Low | High | Output summaries as clean artifacts. |

---

## 2. Hard Constraints & Best Practices

1. **Max File Access Limit**: Never load more than **5 files** into context simultaneously.
2. **Targeted Reading**: Use specific line ranges when calling file viewer tools rather than reading the entire file.
3. **No Wildcard Scans**: Avoid running search commands on the whole repository; restrict searches to subdirectories like `/backend/app/services` or `/frontend/src/components`.
4. **Phase-based Splits**: If a task requires changes across both backend and frontend, implement and verify the backend changes first, then proceed to the frontend in a separate phase.
