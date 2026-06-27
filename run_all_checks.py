import sys
import os
import importlib

def run_environment_checks():
  print("=" * 60)
  print("SPS ENTERPRISE AI PROPOSAL CAPTURE MANAGER - STARTUP CHECKS")
  print("=" * 60)

  # 1. Check Python dependencies
  packages = ["fastapi", "sqlalchemy", "jwt", "passlib", "celery", "redis", "slowapi", "docx"]
  print("1. Verifying Python dependencies...")
  all_ok = True
  for pkg in packages:
    try:
      importlib.import_module(pkg)
      print(f"  [OK] {pkg} is installed")
    except ImportError:
      print(f"  [FAIL] {pkg} is missing!")
      all_ok = False

  # 2. Check Folder Structures
  print("\n2. Verifying folder scopes...")
  folders = ["storage", "backend/app/db", "frontend/src/components"]
  for folder in folders:
    if os.path.exists(folder):
      print(f"  [OK] {folder}/ exists")
    else:
      print(f"  [FAIL] {folder}/ is missing!")
      all_ok = False

  # 3. Database connection check
  print("\n3. Verifying Database availability...")
  try:
    from backend.app.db.session import SessionLocal
    db = SessionLocal()
    # Simple query test
    from sqlalchemy import text
    db.execute(text("SELECT 1"))
    print("  [OK] Database connection verified successfully.")
    db.close()
  except Exception as err:
    print(f"  [FAIL] Database check failed: {err}")
    print("  [Note] Make sure DATABASE_URL is configured or local SQLite file is accessible.")
    all_ok = False

  print("\n" + "=" * 60)
  if all_ok:
    print("SYSTEM HEALTH STATUS: [READY]")
    sys.exit(0)
  else:
    print("SYSTEM HEALTH STATUS: [WARNING - Missing components]")
    sys.exit(1)

if __name__ == "__main__":
  run_environment_checks()
