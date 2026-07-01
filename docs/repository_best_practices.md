# Repository Best Practices

This document outlines the standard guidelines for version control, commit conventions, and file management.

---

## 1. Git Commit Standards

We adhere to the **Conventional Commits** specification:

* `feat`: A new feature (e.g. `feat(api): add export endpoint`)
* `fix`: A bug fix (e.g. `fix(schema): strip forbidden default keys`)
* `docs`: Documentation changes (`docs(readme): update deployment steps`)
* `style`: Code formatting changes (spaces, semicolons)
* `refactor`: Code changes that neither fix a bug nor add a feature
* `test`: Adding or correcting tests
* `chore`: Maintenance tasks, dependencies updates

---

## 2. Pull Request Guidelines

1. **Clear Descriptions**: Summarize the changes made, the files affected, and the ticket/issue reference.
2. **Review Checklist**:
   * All backend tests pass successfully.
   * Type annotations are present.
   * Unique IDs are added to any new UI elements.
   * `CHANGELOG.md` has been updated.
3. **No Dynamic Logs**: Remove temporary diagnostic print statements (`print()`) and utilize the centralized logger instead.

---

## 3. Directory Cleanliness

* Do not check in temporary run outputs, compiled bytecodes (`.pyc`), or SQLite database journals.
* Strictly maintain `/storage` and `/memory` directories as untracked temporary folders.
* Always verify that `.cursorignore` and `.gitignore` are kept updated with local runtime caches.
