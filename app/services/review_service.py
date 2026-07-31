from app.core.supabase import supabase
from app.core.exceptions import NotFoundException, BadRequestException
from app.schemas.review import ReviewCreate, ReviewUpdate

class ReviewService:
    @staticmethod
    def get_book_reviews(book_id: str, page: int = 1, limit: int = 10):
        offset = (page - 1) * limit
        
        count_response = supabase.table("reviews").select("*", count="exact") \
            .eq("book_id", book_id) \
            .execute()
        
        total = count_response.count
        
        response = supabase.table("reviews").select("*, users(*)") \
            .eq("book_id", book_id) \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        return {
            "items": response.data,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "limit": limit
        }
    
    @staticmethod
    def create_review(user_id: str, review_data: ReviewCreate):
        existing = supabase.table("reviews").select("*") \
            .eq("user_id", user_id) \
            .eq("book_id", review_data.book_id) \
            .execute()
        
        if existing.data:
            raise BadRequestException("You have already reviewed this book")
        
        review_dict = review_data.model_dump()
        review_dict["user_id"] = user_id
        
        response = supabase.table("reviews").insert(review_dict).execute()
        
        if not response.data:
            raise Exception("Failed to create review")
        
        return response.data[0]
    
    @staticmethod
    def update_review(review_id: str, user_id: str, review_data: ReviewUpdate):
        response = supabase.table("reviews").select("*") \
            .eq("id", review_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not response.data:
            raise NotFoundException("Review not found")
        
        update_dict = review_data.model_dump(exclude_unset=True)
        update_response = supabase.table("reviews").update(update_dict) \
            .eq("id", review_id) \
            .execute()
        
        if not update_response.data:
            raise Exception("Failed to update review")
        
        return update_response.data[0]
    
    @staticmethod
    def delete_review(review_id: str, user_id: str):
        response = supabase.table("reviews").delete() \
            .eq("id", review_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not response.data:
            raise NotFoundException("Review not found")
        
        return {"message": "Review deleted successfully"}