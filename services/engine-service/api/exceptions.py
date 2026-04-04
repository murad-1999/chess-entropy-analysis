from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from core.exceptions import EngineTimeoutError

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Safely returns Pydantic validator errors as HTTP 422."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Validation Error"}
    )

async def engine_timeout_handler(request: Request, exc: EngineTimeoutError):
    """Maps custom EngineTimeoutError to HTTP 504 Gateway Timeout."""
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={"detail": str(exc), "message": "Engine Gateway Timeout"}
    )
