# Future Maintenance & Upgrades Guide

This guide establishes the maintenance routines and upgrade schedules for the SPS Proposal Capture platform.

---

## 1. Package Upgrades & Security Patches

### 1.1 Python Virtual Environment
- Periodically check for package updates and security advisories.
- Run checks inside the relocated virtual environment:
  ```bash
  d:\projects\RFP-venv\Scripts\python.exe -m pip list --outdated
  ```
- Before upgrading dependencies (such as FastAPI, SQLAlchemy, or Pydantic), verify compatibilities on a separate staging branch and run the pytest suite.

### 1.2 Frontend npm Packages
- Run auditing tools in `/frontend`:
  ```bash
  npm audit
  ```
- Address security vulnerabilities using `npm audit fix` while avoiding updates to locked peer dependencies.

---

## 2. Database Migrations (Alembic)

Whenever models are extended, a new migration version file must be created:
1. Ensure the backend database configuration matches the target environment.
2. Run migration generator:
   ```bash
   d:\projects\RFP-venv\Scripts\python.exe -m alembic revision --autogenerate -m "create_new_tables"
   ```
3. Apply migration changes to local SQLite/PostgreSQL:
   ```bash
   d:\projects\RFP-venv\Scripts\python.exe -m alembic upgrade head
   ```

---

## 3. Quota Management & Backups

### 3.1 Gemini API Quota Control
- Keep usage below the free tier limits (20 requests per day) during development.
- Monitor API consumption via the Google Cloud Platform console.

### 3.2 Database Backups
- For SQLite local development: Create daily snapshots of `sps_proposal_capture.db` and keep them stored securely.
- For production: Configure automated hourly snapshots of PostgreSQL instances.
