from app.core.supabase import supabase
from app.core.exceptions import NotFoundException, ConflictException
from app.schemas.book import CategoryBase

class CategoryService:
    @staticmethod
    def get_categories():
        response = supabase.table("categories").select("*").execute()
        return response.data
    
    @staticmethod
    def get_category(category_id: str):
        response = supabase.table("categories").select("*") \
            .eq("id", category_id) \
            .execute()
        
        if not response.data:
            raise NotFoundException("Category not found")
        
        return response.data[0]
    
    @staticmethod
    def create_category(category_data: CategoryBase):
        existing = supabase.table("categories").select("*") \
            .eq("name", category_data.name) \
            .execute()
        
        if existing.data:
            raise ConflictException("Category already exists")
        
        response = supabase.table("categories").insert(
            category_data.model_dump()
        ).execute()
        
        if not response.data:
            raise Exception("Failed to create category")
        
        return response.data[0]
    
    @staticmethod
    def update_category(category_id: str, category_data: CategoryBase):
        CategoryService.get_category(category_id)
        
        response = supabase.table("categories").update(
            category_data.model_dump()
        ).eq("id", category_id).execute()
        
        if not response.data:
            raise Exception("Failed to update category")
        
        return response.data[0]
    
    @staticmethod
    def delete_category(category_id: str):
        CategoryService.get_category(category_id)
        
        response = supabase.table("categories").delete() \
            .eq("id", category_id) \
            .execute()
        
        if not response.data:
            raise Exception("Failed to delete category")
        
        return {"message": "Category deleted successfully"}