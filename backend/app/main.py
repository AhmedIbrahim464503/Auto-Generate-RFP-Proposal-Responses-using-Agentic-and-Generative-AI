from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.errors import setup_exception_handlers
from backend.app.api.v1.router import api_router
from backend.app.core.logger import logger

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust for production requirements
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Exception Handlers
    setup_exception_handlers(app)

    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting service: {settings.PROJECT_NAME} in environment: {settings.ENV}")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("Service shutting down")

    return app

app = create_app()
