"""
Global Error Handler and Logging Utilities
Provides structured error handling, logging, and monitoring
"""
import logging
import traceback
from typing import Any, Dict
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global error handler middleware
    Catches all unhandled exceptions and returns structured JSON responses
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log request details
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
            
        except HTTPException as exc:
            # FastAPI HTTPException - pass through
            logger.warning(
                f"{request.method} {request.url.path} - "
                f"HTTPException: {exc.status_code} - {exc.detail}"
            )
            raise
            
        except Exception as exc:
            # Unhandled exception - log and return 500
            error_id = f"ERR-{int(time.time())}"
            logger.error(
                f"[{error_id}] Unhandled exception in {request.method} {request.url.path}:\n"
                f"{traceback.format_exc()}"
            )
            
            # Return structured error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": str(exc),
                    "error_id": error_id,
                    "path": str(request.url.path),
                }
            )


def log_error(context: str, error: Exception, extra: Dict[str, Any] = None):
    """
    Log an error with context and extra information
    
    Args:
        context: Description of where/when the error occurred
        error: The exception that was raised
        extra: Additional context (user_id, request_id, etc.)
    """
    extra_info = f" | Extra: {extra}" if extra else ""
    logger.error(
        f"{context} - {type(error).__name__}: {str(error)}{extra_info}\n"
        f"{traceback.format_exc()}"
    )


def log_warning(message: str, extra: Dict[str, Any] = None):
    """Log a warning with optional extra context"""
    extra_info = f" | Extra: {extra}" if extra else ""
    logger.warning(f"{message}{extra_info}")


def log_info(message: str, extra: Dict[str, Any] = None):
    """Log an info message with optional extra context"""
    extra_info = f" | Extra: {extra}" if extra else ""
    logger.info(f"{message}{extra_info}")

