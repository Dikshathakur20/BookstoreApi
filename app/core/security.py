from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme for Swagger
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Verify error: {e}")
        return False

def get_password_hash(password: str) -> str:
    # Truncate password to 72 characters (bcrypt limit)
    if len(password) > 72:
        password = password[:72]
        print(f"Password truncated to 72 chars")
    
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Hashing error: {e}")
        raise e

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except:
        return {}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        from app.core.supabase import supabase
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return response.data[0]
    
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current active user"""
    return current_user

async def get_current_admin_user(current_user = Depends(get_current_user)):
    """Get current admin user"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user