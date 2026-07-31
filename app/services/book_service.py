from typing import Optional
from app.core.supabase import supabase
from app.core.exceptions import NotFoundException
from app.schemas.book import BookCreate, BookUpdate

class BookService:
    @staticmethod
    def get_books(
        q: Optional[str] = None,
        category_id: Optional[str] = None,
        author: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        page: int = 1,
        limit: int = 10
    ):
        query = supabase.table("books").select("*, categories(*)")
        
        if q:
            query = query.ilike("title", f"%{q}%")
        if category_id:
            query = query.eq("category_id", category_id)
        if author:
            query = query.ilike("author", f"%{author}%")
        if min_price is not None:
            query = query.gte("price", min_price)
        if max_price is not None:
            query = query.lte("price", max_price)
        
        count_response = query.execute()
        total = len(count_response.data)
        
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        return {
            "items": response.data,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit,
            "limit": limit
        }
    
    @staticmethod
    def get_book(book_id: str):
        response = supabase.table("books").select("*, categories(*)") \
            .eq("id", book_id) \
            .execute()
        
        if not response.data:
            raise NotFoundException("Book not found")
        
        return response.data[0]
    
    @staticmethod
    def create_book(book_data: BookCreate):
        response = supabase.table("books").insert(book_data.model_dump()).execute()
        
        if not response.data:
            raise Exception("Failed to create book")
        
        return response.data[0]
    
    @staticmethod
    def update_book(book_id: str, book_data: BookUpdate):
        BookService.get_book(book_id)
        
        update_dict = book_data.model_dump(exclude_unset=True)
        response = supabase.table("books").update(update_dict) \
            .eq("id", book_id) \
            .execute()
        
        if not response.data:
            raise Exception("Failed to update book")
        
        return response.data[0]
    
    @staticmethod
    def delete_book(book_id: str):
        BookService.get_book(book_id)
        
        response = supabase.table("books").delete() \
            .eq("id", book_id) \
            .execute()
        
        if not response.data:
            raise Exception("Failed to delete book")
        
        return {"message": "Book deleted successfully"}
    
    @staticmethod
    def update_stock(book_id: str, quantity: int):
        book = BookService.get_book(book_id)
        new_stock = book["stock_quantity"] + quantity
        
        if new_stock < 0:
            raise Exception("Insufficient stock")
        
        response = supabase.table("books").update({
            "stock_quantity": new_stock
        }).eq("id", book_id).execute()
        
        if not response.data:
            raise Exception("Failed to update stock")
        
        return response.data[0]