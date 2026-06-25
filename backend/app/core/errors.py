from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from backend.app.schemas.error import APIErrorResponse, ErrorDetail
from backend.app.core.logger import logger

class BaseAppException(Exception):
    def __init__(self, message: str, error_code: str, status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(message)

class DomainException(BaseAppException):
    def __init__(self, message: str, error_code: str = "DOMAIN_ERROR", status_code: int = 400):
        super().__init__(message, error_code, status_code)

class InfrastructureException(BaseAppException):
    def __init__(self, message: str, error_code: str = "INFRASTRUCTURE_ERROR", status_code: int = 500):
        super().__init__(message, error_code, status_code)

def setup_exception_handlers(app):
    @app.exception_handler(BaseAppException)
    async def base_app_exception_handler(request: Request, exc: BaseAppException):
        logger.error(f"Application error occurred: {exc.error_code} - {exc.message}")
        response_body = APIErrorResponse(
            success=False,
            error_code=exc.error_code,
            message=exc.message
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=response_body.model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error occurred: {exc.errors()}")
        details = [
            ErrorDetail(
                loc=[str(l) for l in err["loc"]],
                msg=err["msg"],
                type=err["type"]
            )
            for err in exc.errors()
        ]
        response_body = APIErrorResponse(
            success=False,
            error_code="VALIDATION_ERROR",
            message="Input validation failed",
            details=details
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=response_body.model_dump()
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled system error: {str(exc)}", exc_info=True)
        response_body = APIErrorResponse(
            success=False,
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected system error occurred"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=response_body.model_dump()
        )
