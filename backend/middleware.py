from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
from typing import Dict, Tuple
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter for API endpoints."""
    
    def __init__(self, requests_per_window: int = 100, window_seconds: int = 3600):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if a request is allowed for the given client.
        Returns (is_allowed, remaining_requests)
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] 
            if req_time > window_start
        ]
        
        # Check if under limit
        current_requests = len(self.requests[client_id])
        is_allowed = current_requests < self.requests_per_window
        
        if is_allowed:
            self.requests[client_id].append(now)
        
        remaining = max(0, self.requests_per_window - current_requests)
        return is_allowed, remaining

# Global rate limiter instance
rate_limiter = RateLimiter()

def get_client_id(request: Request) -> str:
    """Extract client identifier from request."""
    # Use X-Forwarded-For if available (for proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Fall back to client host
    return request.client.host if request.client else "unknown"

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/health/detailed"]:
        return await call_next(request)
    
    client_id = get_client_id(request)
    is_allowed, remaining = rate_limiter.is_allowed(client_id)
    
    if not is_allowed:
        logger.warning(f"Rate limit exceeded for client {client_id}")
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": rate_limiter.window_seconds
            },
            headers={
                "X-RateLimit-Limit": str(rate_limiter.requests_per_window),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time() + rate_limiter.window_seconds))
            }
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_window)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time() + rate_limiter.window_seconds))
    
    return response 