from app.core.supabase import supabase
from app.core.exceptions import NotFoundException, BadRequestException
from app.schemas.cart import CartItemCreate, CartItemUpdate
from app.services.book_service import BookService

class CartService:
    @staticmethod
    def get_cart(user_id: str):
        response = supabase.table("cart").select("*, books(*)") \
            .eq("user_id", user_id) \
            .execute()
        
        items = response.data
        total_items = sum(item["quantity"] for item in items)
        total_price = sum(
            item["quantity"] * item["books"]["price"] 
            for item in items if item.get("books")
        )
        
        return {
            "items": items,
            "total_items": total_items,
            "total_price": total_price
        }
    
    @staticmethod
    def add_to_cart(user_id: str, cart_data: CartItemCreate):
        book = BookService.get_book(cart_data.book_id)
        
        if book["stock_quantity"] < cart_data.quantity:
            raise BadRequestException("Insufficient stock")
        
        existing = supabase.table("cart").select("*") \
            .eq("user_id", user_id) \
            .eq("book_id", cart_data.book_id) \
            .execute()
        
        if existing.data:
            new_quantity = existing.data[0]["quantity"] + cart_data.quantity
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
        
        return response.data[0]
    
    @staticmethod
    def update_cart_item(cart_item_id: str, user_id: str, update_data: CartItemUpdate):
        response = supabase.table("cart").select("*, books(*)") \
            .eq("id", cart_item_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not response.data:
            raise NotFoundException("Cart item not found")
        
        item = response.data[0]
        
        if item["books"]["stock_quantity"] < update_data.quantity:
            raise BadRequestException("Insufficient stock")
        
        update_response = supabase.table("cart").update({
            "quantity": update_data.quantity
        }).eq("id", cart_item_id).execute()
        
        if not update_response.data:
            raise Exception("Failed to update cart")
        
        return update_response.data[0]
    
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