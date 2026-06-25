from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.core.logger import logger
from sqlalchemy import text

router = APIRouter()

@router.get("/health", status_code=200)
def health_check():
    """
    Standard health check endpoint.
    """
    logger.debug("Health check invoked")
    return {"status": "healthy", "service": "SPS Enterprise AI Proposal Capture Manager"}

@router.get("/readiness", status_code=200)
def readiness_check(db: Session = Depends(get_db)):
    """
    Verifies connection to database and downstream services.
    """
    try:
        # Perform simple query to verify DB connection
        db.execute(text("SELECT 1"))
        logger.debug("Readiness check DB connection ok")
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {"status": "unready", "database": "disconnected", "detail": str(e)}

@router.get("/version", status_code=200)
def version_info():
    """
    Returns API version info.
    """
    return {
        "version": "1.0.0",
        "api_v1_path": "/api/v1"
    }
