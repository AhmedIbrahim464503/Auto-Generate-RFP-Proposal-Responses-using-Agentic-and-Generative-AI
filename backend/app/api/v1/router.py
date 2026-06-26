from fastapi import APIRouter
from backend.app.api.v1.endpoints import health, documents, analysis, requirements, reviews, qualification, proposals, knowledge, proposal_generation, ai_platform, ai_platform_v2, proposal_review_v1

api_router = APIRouter()
api_router.include_router(health.router, tags=["system"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(analysis.router, prefix="/documents", tags=["analysis"])
api_router.include_router(requirements.router, prefix="/rfp", tags=["requirements"])
api_router.include_router(reviews.router, prefix="/rfp", tags=["reviews"])
api_router.include_router(qualification.router, prefix="/rfp", tags=["qualification"])
api_router.include_router(proposals.router, prefix="/proposals", tags=["proposals"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(proposal_generation.router, prefix="/proposals", tags=["proposal_generation"])
api_router.include_router(ai_platform.router, prefix="/ai-platform", tags=["ai_platform"])
api_router.include_router(ai_platform_v2.router, prefix="/ai", tags=["ai_platform_v2"])
api_router.include_router(proposal_review_v1.router, prefix="/review", tags=["proposal_review"])







