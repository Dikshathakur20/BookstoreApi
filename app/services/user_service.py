from app.core.supabase import supabase
from app.core.security import get_password_hash, verify_password
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.schemas.user import UserUpdate, ChangePassword

class UserService:
    @staticmethod
    def get_user(user_id: str):
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if not response.data:
            raise NotFoundException("User not found")
        return response.data[0]
    
    @staticmethod
    def update_user(user_id: str, update_data: UserUpdate):
        user = UserService.get_user(user_id)
        
        if update_data.email:
            existing = supabase.table("users").select("*").eq("email", update_data.email).neq("id", user_id).execute()
            if existing.data:
                raise ConflictException("Email already taken")
        
        if update_data.username:
            existing = supabase.table("users").select("*").eq("username", update_data.username).neq("id", user_id).execute()
            if existing.data:
                raise ConflictException("Username already taken")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        response = supabase.table("users").update(update_dict).eq("id", user_id).execute()
        
        if not response.data:
            raise Exception("Failed to update user")
        
        return response.data[0]
    
    @staticmethod
    def change_password(user_id: str, password_data: ChangePassword):
        user = UserService.get_user(user_id)
        
        if not verify_password(password_data.old_password, user["hashed_password"]):
            raise BadRequestException("Incorrect old password")
        
        hashed_password = get_password_hash(password_data.new_password)
        response = supabase.table("users").update({"hashed_password": hashed_password}).eq("id", user_id).execute()
        
        if not response.data:
            raise Exception("Failed to update password")
        
        return {"message": "Password updated successfully"}