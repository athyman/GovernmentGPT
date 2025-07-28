"""
Security middleware for GovernmentGPT API.
Implements rate limiting, request validation, and security headers.
"""

from fastapi import Request, HTTPException
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from typing import Dict, List
import hashlib
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for API protection"""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limits: Dict[str, List[float]] = defaultdict(list)
        self.blocked_ips: set = set()
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security checks"""
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            raise HTTPException(status_code=429, detail="IP temporarily blocked")
        
        # Rate limiting
        if not await self._check_rate_limit(client_ip, request.url.path):
            self.blocked_ips.add(client_ip)
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Validate request
        await self._validate_request(request)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers"""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def _check_rate_limit(self, client_ip: str, path: str) -> bool:
        """Check rate limits for client IP"""
        current_time = time.time()
        
        # Clean old requests (older than 1 hour)
        self.rate_limits[client_ip] = [
            req_time for req_time in self.rate_limits[client_ip]
            if current_time - req_time < 3600
        ]
        
        # Check rate limits
        recent_requests = len([
            req_time for req_time in self.rate_limits[client_ip]
            if current_time - req_time < 60  # 1 minute
        ])
        
        if recent_requests >= settings.RATE_LIMIT_PER_MINUTE:
            return False
        
        # Check hourly limit
        hourly_requests = len(self.rate_limits[client_ip])
        if hourly_requests >= settings.RATE_LIMIT_PER_HOUR:
            return False
        
        # Add current request
        self.rate_limits[client_ip].append(current_time)
        return True
    
    async def _validate_request(self, request: Request):
        """Validate incoming request"""
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.MAX_DOCUMENT_SIZE:
            raise HTTPException(status_code=413, detail="Request too large")
        
        # Check for suspicious patterns in query parameters
        for key, value in request.query_params.items():
            if self._contains_suspicious_patterns(str(value)):
                logger.warning(f"Suspicious query parameter detected: {key}={value}")
                raise HTTPException(status_code=400, detail="Invalid request parameters")
    
    def _contains_suspicious_patterns(self, text: str) -> bool:
        """Check for suspicious patterns in input"""
        suspicious_patterns = [
            'union select', 'drop table', 'insert into', 'delete from',
            '<script', 'javascript:', 'onload=', 'onerror=',
            '../', '..\\', '/etc/passwd', 'cmd.exe'
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in suspicious_patterns)
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https://api.anthropic.com; "
                "frame-ancestors 'none'; "
                "base-uri 'self';"
            ),
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        }
        
        for header, value in headers.items():
            response.headers[header] = value