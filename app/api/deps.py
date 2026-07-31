from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.supabase import supabase
from app.core.security import decode_token

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=401, detail="User not found")
        
        return response.data[0]
    
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

async def get_current_active_user(current_user = Depends(get_current_user)):
    return current_user

async def get_current_admin_user(current_user = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user