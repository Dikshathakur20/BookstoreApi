from app.core.supabase import supabase_service as supabase
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.exceptions import UnauthorizedException, ConflictException
from app.core.logger import logger
from app.schemas.user import UserCreate, UserLogin
import traceback

class AuthService:
    @staticmethod
    def register_user(user_data: UserCreate):
        try:
            logger.info(f"Registering user: {user_data.email}")
            
            # Check if user exists
            existing = supabase.table("users").select("*").eq("email", user_data.email).execute()
            
            if existing.data:
                logger.warning(f"User already exists: {user_data.email}")
                raise ConflictException("Email already exists")
            
            # Hash password
            hashed = get_password_hash(user_data.password)
            
            # Create user
            new_user = {
                "username": user_data.username,
                "email": user_data.email,
                "hashed_password": hashed,
                "role": "user"
            }
            
            logger.debug(f"Inserting user: {new_user['email']}")
            response = supabase.table("users").insert(new_user).execute()
            
            logger.info(f"User registered: {user_data.email}")
            return response.data[0]
            
        except Exception as e:
            logger.error(f"ERROR in register_user: {str(e)}")
            logger.error(f"ERROR TYPE: {type(e).__name__}")
            logger.error(traceback.format_exc())
            raise e
    
    @staticmethod
    def login_user(login_data: UserLogin):
        try:
            logger.info(f"Login attempt: {login_data.email}")
            
            response = supabase.table("users").select("*").eq("email", login_data.email).execute()
            
            if not response.data:
                logger.warning(f"User not found: {login_data.email}")
                raise UnauthorizedException("Invalid credentials")
            
            user = response.data[0]
            
            if not verify_password(login_data.password, user["hashed_password"]):
                logger.warning(f"Invalid password for: {login_data.email}")
                raise UnauthorizedException("Invalid credentials")
            
            token = create_access_token({
                "sub": user["id"],
                "email": user["email"],
                "role": user["role"]
            })
            
            logger.info(f"User logged in: {login_data.email}")
            
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"]
                }
            }
            
        except Exception as e:
            logger.error(f"ERROR in login_user: {str(e)}")
            logger.error(f"ERROR TYPE: {type(e).__name__}")
            logger.error(traceback.format_exc())
            raise e