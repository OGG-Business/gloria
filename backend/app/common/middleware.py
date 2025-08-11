"""
Custom middleware for Banking Transfer Platform
"""

import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import structlog

from app.common.database import get_db_context
from app.audit.models import AuditLog

logger = structlog.get_logger()

class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware for audit logging"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate trace ID
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        
        # Log request start
        start_time = time.time()
        
        logger.info(
            "Request started",
            trace_id=trace_id,
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log request completion
            logger.info(
                "Request completed",
                trace_id=trace_id,
                status_code=response.status_code,
                process_time=process_time
            )
            
            # Add trace ID to response headers
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log sensitive actions to database
            await self._log_sensitive_action(request, response, trace_id, process_time)
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(
                "Request failed",
                trace_id=trace_id,
                error=str(e),
                process_time=time.time() - start_time
            )
            raise
    
    async def _log_sensitive_action(self, request: Request, response: Response, trace_id: str, process_time: float):
        """Log sensitive actions to database"""
        try:
            # Define sensitive endpoints
            sensitive_endpoints = [
                "/auth/login",
                "/auth/logout",
                "/transfers/",
                "/accounts/",
                "/kyc/",
                "/admin/"
            ]
            
            # Check if this is a sensitive endpoint
            is_sensitive = any(endpoint in request.url.path for endpoint in sensitive_endpoints)
            
            if is_sensitive and response.status_code < 400:
                # Create audit log entry
                audit_log = AuditLog(
                    id=str(uuid.uuid4()),
                    trace_id=trace_id,
                    user_id=getattr(request.state, 'user_id', None),
                    action=f"{request.method} {request.url.path}",
                    resource=request.url.path,
                    status="success",
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    metadata={
                        "method": request.method,
                        "query_params": dict(request.query_params),
                        "response_status": response.status_code,
                        "process_time": process_time
                    }
                )
                
                # Save to database
                with get_db_context() as db:
                    db.add(audit_log)
                    db.commit()
                    
        except Exception as e:
            logger.error(f"Failed to log sensitive action: {e}")

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security checks"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Basic security checks
        await self._security_checks(request)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response = self._add_security_headers(response)
        
        return response
    
    async def _security_checks(self, request: Request):
        """Perform security checks"""
        # Check User-Agent
        user_agent = request.headers.get("user-agent", "")
        if not user_agent or len(user_agent) < 10:
            logger.warning(f"Suspicious User-Agent: {user_agent}")
        
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=413, detail="Request too large")
        
        # Check allowed methods
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        if request.method not in allowed_methods:
            raise HTTPException(status_code=405, detail="Method not allowed")
    
    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rate_limits = {}  # In production, use Redis
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not self._check_rate_limit(client_ip, request.url.path):
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded"}
            )
        
        # Process request
        response = await call_next(request)
        return response
    
    def _check_rate_limit(self, client_ip: str, path: str) -> bool:
        """Check if request is within rate limit"""
        # Simple in-memory rate limiting (use Redis in production)
        key = f"{client_ip}:{path}"
        current_time = time.time()
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Remove old requests (older than 1 minute)
        self.rate_limits[key] = [
            req_time for req_time in self.rate_limits[key]
            if current_time - req_time < 60
        ]
        
        # Check limit (60 requests per minute)
        if len(self.rate_limits[key]) >= 60:
            return False
        
        # Add current request
        self.rate_limits[key].append(current_time)
        return True