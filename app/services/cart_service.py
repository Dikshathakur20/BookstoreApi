# app/services/cart_service.py

from app.core.supabase import supabase
from app.core.exceptions import NotFoundException, BadRequestException
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.services.book_service import BookService

class CartService:
    @staticmethod
    def get_cart(user_id: str):
        response = supabase.table("cart").select("*, books(id, title, author, description, price, stock_quantity, category_id, cover_image_url, rating_avg, rating_count, created_at, updated_at, categories(name))") \
            .eq("user_id", user_id) \
            .execute()
        
        items = response.data
        
        transformed_items = []
        out_of_stock_items = []
        has_out_of_stock = False
        
        for item in items:
            if item.get("books"):
                book = item["books"]
                
                # ✅ Check stock
                stock_quantity = book.get("stock_quantity", 0)
                requested_quantity = item.get("quantity", 1)
                is_in_stock = stock_quantity >= requested_quantity
                
                if not is_in_stock:
                    has_out_of_stock = True
                    out_of_stock_items.append(book.get("title", "Unknown Book"))
                
                # Category name
                if "categories" in book and book["categories"]:
                    book["category_name"] = book["categories"]["name"]
                else:
                    book["category_name"] = None
                
                book.pop("categories", None)
                book["book_id"] = book["id"]
                
                item["book"] = book
                item["in_stock"] = is_in_stock
                item["max_available"] = stock_quantity
                item.pop("books", None)
            
            transformed_items.append(item)
        
        total_items = sum(item["quantity"] for item in transformed_items)
        total_price = sum(
            item["quantity"] * item["book"]["price"] 
            for item in transformed_items if item.get("book") and item.get("in_stock", True)
        )
        
        return {
            "items": transformed_items,
            "total_items": total_items,
            "total_price": total_price,
            "has_out_of_stock_items": has_out_of_stock,
            "out_of_stock_items": out_of_stock_items
        }
    
    @staticmethod
    def add_to_cart(user_id: str, cart_data: CartItemCreate):
        # ✅ Check stock before adding
        book = BookService.get_book(cart_data.book_id)
        
        if book["stock_quantity"] < cart_data.quantity:
            raise BadRequestException(f"Insufficient stock. Only {book['stock_quantity']} available.")
        
        existing = supabase.table("cart").select("*") \
            .eq("user_id", user_id) \
            .eq("book_id", cart_data.book_id) \
            .execute()
        
        if existing.data:
            new_quantity = existing.data[0]["quantity"] + cart_data.quantity
            # ✅ Check if new quantity exceeds stock
            if book["stock_quantity"] < new_quantity:
                raise BadRequestException(f"Cannot add more. Only {book['stock_quantity']} available in stock.")
            
            response = supabase.table("cart").update({
                "quantity": new_quantity
            }).eq("id", existing.data[0]["id"]).execute()
        else:
            response = supabase.table("cart").insert({
                "user_id": user_id,
                "book_id": cart_data.book_id,
                "quantity": cart_data.quantity
            }).execute()
        
        if not response.data:
            raise Exception("Failed to add to cart")
        
        cart_item_id = response.data[0]["id"]
        return CartService.get_cart_item(cart_item_id, user_id)
    
    @staticmethod
    def get_cart_item(cart_item_id: str, user_id: str):
        response = supabase.table("cart").select("*, books(id, title, author, description, price, stock_quantity, category_id, cover_image_url, rating_avg, rating_count, created_at, updated_at, categories(name))") \
            .eq("id", cart_item_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not response.data:
            raise NotFoundException("Cart item not found")
        
        item = response.data[0]
        
        if item.get("books"):
            book = item["books"]
            
            # ✅ Check stock
            stock_quantity = book.get("stock_quantity", 0)
            requested_quantity = item.get("quantity", 1)
            is_in_stock = stock_quantity >= requested_quantity
            
            if "categories" in book and book["categories"]:
                book["category_name"] = book["categories"]["name"]
            else:
                book["category_name"] = None
            book.pop("categories", None)
            book["book_id"] = book["id"]
            
            item["book"] = book
            item["in_stock"] = is_in_stock
            item["max_available"] = stock_quantity
            item.pop("books", None)
        
        return item
    
    @staticmethod
    def update_cart_item(cart_item_id: str, user_id: str, update_data: CartItemUpdate):
        response = supabase.table("cart").select("*, books(*)") \
            .eq("id", cart_item_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not response.data:
            raise NotFoundException("Cart item not found")
        
        item = response.data[0]
        
        # ✅ Check stock before updating
        stock_quantity = item["books"]["stock_quantity"]
        if stock_quantity < update_data.quantity:
            raise BadRequestException(f"Insufficient stock. Only {stock_quantity} available.")
        
        update_response = supabase.table("cart").update({
            "quantity": update_data.quantity
        }).eq("id", cart_item_id).execute()
        
        if not update_response.data:
            raise Exception("Failed to update cart")
        
        return CartService.get_cart_item(cart_item_id, user_id)
    
    @staticmethod
    def remove_from_cart(cart_item_id: str, user_id: str):
        response = supabase.table("cart").delete() \
            .eq("id", cart_item_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not response.data:
            raise NotFoundException("Cart item not found")
        
        return {"message": "Item removed from cart"}
    
    @staticmethod
    def clear_cart(user_id: str):
        supabase.table("cart").delete() \
            .eq("user_id", user_id) \
            .execute()
        
        return {"message": "Cart cleared successfully"}