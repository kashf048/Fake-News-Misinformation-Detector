"""
Rate Limiting Middleware
Request rate limiting and throttling
"""

import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter for API requests"""

    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)

    def is_allowed(self, client_id: str) -> Tuple[bool, Dict]:
        """Check if request is allowed"""
        current_time = time.time()
        minute_ago = current_time - 60

        # Clean old requests
        if client_id in self.requests:
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > minute_ago
            ]

        # Check limit
        request_count = len(self.requests[client_id])

        if request_count >= self.requests_per_minute:
            return False, {
                "limit": self.requests_per_minute,
                "current": request_count,
                "reset_in": 60
            }

        # Add current request
        self.requests[client_id].append(current_time)

        return True, {
            "limit": self.requests_per_minute,
            "current": request_count + 1,
            "remaining": self.requests_per_minute - request_count - 1
        }

    def get_client_id(self, request: Request) -> str:
        """Extract client ID from request"""
        # Try to get from X-Forwarded-For header (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        # Fall back to client IP
        return request.client.host if request.client else "unknown"


class RequestLogger:
    """Middleware for logging requests"""

    @staticmethod
    async def log_request(request: Request, call_next):
        """Log incoming request"""
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
            }
        )

        response = await call_next(request)

        # Log response
        duration = time.time() - start_time
        logger.info(
            f"Response: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration * 1000,
            }
        )

        response.headers["X-Process-Time"] = str(duration)
        return response


class ErrorHandler:
    """Middleware for handling errors"""

    @staticmethod
    async def handle_errors(request: Request, call_next):
        """Handle errors in requests"""
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Unhandled error: {str(e)}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "error_type": type(e).__name__,
                }
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=100)


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Skip rate limiting for health check
    if request.url.path in ["/api/health", "/api/status", "/"]:
        return await call_next(request)

    client_id = rate_limiter.get_client_id(request)
    allowed, info = rate_limiter.is_allowed(client_id)

    if not allowed:
        logger.warning(
            f"Rate limit exceeded for {client_id}",
            extra={"client_id": client_id, "info": info}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(info["reset_in"]),
            }
        )

    response = await call_next(request)

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(info["limit"])
    response.headers["X-RateLimit-Remaining"] = str(info["remaining"])

    return response
