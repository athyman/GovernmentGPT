"""
Logging middleware for GovernmentGPT API.
Provides structured logging for requests and responses.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
import logging
from typing import Callable

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Log request and response details"""
        start_time = time.time()
        
        # Log request
        request_log = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client": request.client.host if request.client else None,
            "timestamp": start_time
        }
        
        # Don't log sensitive headers
        sensitive_headers = {"authorization", "cookie", "x-api-key"}
        request_log["headers"] = {
            k: v if k.lower() not in sensitive_headers else "[REDACTED]"
            for k, v in request_log["headers"].items()
        }
        
        logger.info(f"Request: {json.dumps(request_log, default=str)}")
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            response_log = {
                "status_code": response.status_code,
                "process_time": process_time,
                "timestamp": time.time()
            }
            
            logger.info(f"Response: {json.dumps(response_log, default=str)}")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            error_log = {
                "error": str(e),
                "process_time": process_time,
                "timestamp": time.time()
            }
            
            logger.error(f"Error: {json.dumps(error_log, default=str)}")
            raise