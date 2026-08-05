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
        # ✅ Sirf category name fetch karo (categories(name))
        query = supabase.table("books").select("*, categories(name)")
        
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
        
        # ✅ Count ke liye alag query (kyunki range() count affect karti hai)
        count_query = supabase.table("books").select("*", count="exact")
        if q:
            count_query = count_query.ilike("title", f"%{q}%")
        if category_id:
            count_query = count_query.eq("category_id", category_id)
        if author:
            count_query = count_query.ilike("author", f"%{author}%")
        if min_price is not None:
            count_query = count_query.gte("price", min_price)
        if max_price is not None:
            count_query = count_query.lte("price", max_price)
        
        count_response = count_query.execute()
        total = count_response.count if hasattr(count_response, 'count') else len(count_response.data)
        
        offset = (page - 1) * limit
        query = query.range(offset, offset + limit - 1)
        
        response = query.execute()
        
        # ✅ Data transform karo - category_name extract karo
        items = []
        for item in response.data:
            # Category name extract karo
            if "categories" in item and item["categories"]:
                item["category_name"] = item["categories"]["name"]
            else:
                item["category_name"] = None
            
            # Categories object hata do (optional)
            item.pop("categories", None)
            
            items.append(item)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 1,
            "limit": limit
        }
    
    @staticmethod
    def get_book(book_id: str):
        # ✅ Sirf category name fetch karo
        response = supabase.table("books").select("*, categories(name)") \
            .eq("id", book_id) \
            .execute()
        
        if not response.data:
            raise NotFoundException("Book not found")
        
        book = response.data[0]
        
        # ✅ Category name extract karo
        if "categories" in book and book["categories"]:
            book["category_name"] = book["categories"]["name"]
        else:
            book["category_name"] = None
        
        # Categories object hata do
        book.pop("categories", None)
        
        return book
    
    @staticmethod
    def create_book(book_data: BookCreate):
        response = supabase.table("books").insert(book_data.model_dump()).execute()
        
        if not response.data:
            raise Exception("Failed to create book")
        
        # ✅ Created book ko fetch karo with category name
        book_id = response.data[0]["id"]
        return BookService.get_book(book_id)
    
    @staticmethod
    def update_book(book_id: str, book_data: BookUpdate):
        # Check if book exists
        BookService.get_book(book_id)
        
        update_dict = book_data.model_dump(exclude_unset=True)
        response = supabase.table("books").update(update_dict) \
            .eq("id", book_id) \
            .execute()
        
        if not response.data:
            raise Exception("Failed to update book")
        
        # ✅ Updated book ko fetch karo with category name
        return BookService.get_book(book_id)
    
    @staticmethod
    def delete_book(book_id: str):
        # Check if book exists
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
        
        # ✅ Updated book ko fetch karo with category name
        return BookService.get_book(book_id)