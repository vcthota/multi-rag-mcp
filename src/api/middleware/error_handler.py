"""
Global error handler middleware
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback
from typing import Union
import time

from src.core.exceptions import MultiRAGException

logger = logging.getLogger(__name__)


async def error_handler_middleware(request: Request, call_next):
    """
    Global error handling middleware
    Catches all exceptions and returns properly formatted error responses
    """
    request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")
    request.state.request_id = request_id
    
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    
    except MultiRAGException as e:
        logger.error(
            f"MultiRAG Exception: {e.message}",
            extra={
                "request_id": request_id,
                "error_code": e.error_code,
                "details": e.details,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": {
                    "code": e.error_code,
                    "message": e.message,
                    "details": e.details,
                    "request_id": request_id
                }
            }
        )
    
    except StarletteHTTPException as e:
        logger.warning(
            f"HTTP Exception: {e.detail}",
            extra={
                "request_id": request_id,
                "status_code": e.status_code,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=e.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": e.detail,
                    "request_id": request_id
                }
            }
        )
    
    except RequestValidationError as e:
        logger.warning(
            f"Validation Error: {str(e)}",
            extra={
                "request_id": request_id,
                "errors": e.errors(),
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "details": e.errors(),
                    "request_id": request_id
                }
            }
        )
    
    except Exception as e:
        logger.error(
            f"Unhandled Exception: {str(e)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc()
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "request_id": request_id
                }
            }
        )


def custom_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Custom exception handler for FastAPI
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    if isinstance(exc, MultiRAGException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": request_id
                }
            }
        )
    
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "request_id": request_id,
            "traceback": traceback.format_exc()
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request_id
            }
        }
    )
