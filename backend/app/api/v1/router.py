from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, documents, analysis, requirements, reviews

api_router = APIRouter()
api_router.include_router(health.router, tags=["system"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(analysis.router, prefix="/documents", tags=["analysis"])
api_router.include_router(requirements.router, prefix="/rfp", tags=["requirements"])
api_router.include_router(reviews.router, prefix="/rfp", tags=["reviews"])

