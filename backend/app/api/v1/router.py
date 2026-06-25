from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, documents

api_router = APIRouter()
api_router.include_router(health.router, tags=["system"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
