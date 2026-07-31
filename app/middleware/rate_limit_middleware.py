import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

# In-memory store for rate limiting (use Redis in production)
rate_limit_store = defaultdict(list)
RATE_LIMIT = 100  # Requests per minute

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit requests per IP"""
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host
        
        # Get current timestamp
        current_time = time.time()
        minute_ago = current_time - 60
        
        # Clean old requests
        rate_limit_store[client_ip] = [
            timestamp for timestamp in rate_limit_store[client_ip]
            if timestamp > minute_ago
        ]
        
        # Check rate limit
        if len(rate_limit_store[client_ip]) >= RATE_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many requests. Limit: {RATE_LIMIT} requests per minute"
            )
        
        # Add current request
        rate_limit_store[client_ip].append(current_time)
        
        return await call_next(request)