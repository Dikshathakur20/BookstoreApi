from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import decode_token

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate JWT token on every request"""
    
    async def dispatch(self, request: Request, call_next):
        # Public routes (no authentication needed)
        public_paths = ["/", "/health", "/api/docs", "/api/redoc", "/api/openapi.json"]
        
        if request.url.path in public_paths:
            return await call_next(request)
        
        # Check if route starts with /api/v1/auth (public auth routes)
        if request.url.path.startswith("/api/v1/auth"):
            return await call_next(request)
        
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization token"
            )
        
        try:
            # Extract token
            token = auth_header.replace("Bearer ", "")
            
            # Validate token
            payload = decode_token(token)
            
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Add user info to request state
            request.state.user_id = payload.get("sub")
            request.state.user_role = payload.get("role")
            
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return await call_next(request)