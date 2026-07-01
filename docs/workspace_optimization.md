# Workspace Optimization & Index Exclusions

This document contains guidelines and configurations for maintaining a fast, lightweight workspace footprint.

---

## 1. Directory Telemetry

A full analysis of the RFP workspace filesystem reveals that dependencies and build cache folders comprise over **99% of total files** and **98% of total storage size**:

* **Total Workspace Files**: ~51,790 files
* **Relocated `.venv` (Python)**: ~11,758 files (326 MB) — **Relocated Outside Workspace**
* **`node_modules` (Frontend)**: ~34,851 files (594 MB) — **Excluded**
* **`.next` (Next.js Cache)**: ~48 files (61 MB) — **Excluded**
* **Codebase Source Files**: ~450 files — **Active Indexing Scope**

By moving the Python virtual environment and excluding dependency folders, the files watched by the IDE and AI tools drop from **51,790 to under 500 files**.

---

## 2. Environment Relocation (Option B)

The Python virtual environment (`.venv`) has been moved to:
`d:\projects\RFP-venv`

### Interpreter Configurations
VS Code is configured to map to this environment via the workspace-level `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "d:\\projects\\RFP-venv\\Scripts\\python.exe",
  "python.analysis.extraPaths": [
    "d:\\projects\\RFP-venv\\Lib\\site-packages"
  ]
}
```

### Script Executions
Any terminal command invoking virtual environment packages (such as `pytest` or `uvicorn`) must run via the python executable directly to avoid absolute shebang errors:
* **Run Tests**: `d:\projects\RFP-venv\Scripts\python.exe -m pytest`
* **Run Server**: `d:\projects\RFP-venv\Scripts\python.exe -m uvicorn backend.app.main:app`

---

## 3. Directory Ignore Filters

The following profiles must be configured in all local editors and indexing tools:

* **`.gitignore`**: Excludes `.venv/`, `node_modules/`, `.next/`, `*.db`, `storage/`, and `memory/`.
* **`.cursorignore`**: Excludes dependencies, database files, compiled assets, caches, and logs.
* **VS Code Exclusions (`settings.json`)**:
  ```json
  "files.exclude": {
    "**/node_modules": true,
    "**/.next": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/.next": true
  }
  ```
This ensures zero file-watching lag, rapid searches, and lightweight AI index updates.
