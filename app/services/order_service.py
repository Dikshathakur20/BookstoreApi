from app.core.supabase import supabase
from app.core.exceptions import NotFoundException, BadRequestException
from app.schemas.order import OrderCreate, OrderUpdateStatus
from app.services.cart_service import CartService
from app.services.book_service import BookService

class OrderService:
    @staticmethod
    def place_order(user_id: str, order_data: OrderCreate):
        cart = CartService.get_cart(user_id)
        
        if not cart["items"]:
            raise BadRequestException("Cart is empty")
        
        total_amount = 0
        order_items = []
        
        for item in cart["items"]:
            book = item["books"]
            
            if book["stock_quantity"] < item["quantity"]:
                raise BadRequestException(f"Insufficient stock for {book['title']}")
            
            total_amount += item["quantity"] * book["price"]
            order_items.append({
                "book_id": item["book_id"],
                "quantity": item["quantity"],
                "price_at_time": book["price"]
            })
        
        order_data_dict = order_data.model_dump()
        order_data_dict["user_id"] = user_id
        order_data_dict["total_amount"] = total_amount
        order_data_dict["status"] = "pending"
        order_data_dict["payment_status"] = "pending"
        
        order_response = supabase.table("orders").insert(order_data_dict).execute()
        
        if not order_response.data:
            raise Exception("Failed to create order")
        
        order = order_response.data[0]
        
        for item in order_items:
            item["order_id"] = order["id"]
            supabase.table("order_items").insert(item).execute()
        
        for item in cart["items"]:
            BookService.update_stock(item["book_id"], -item["quantity"])
        
        CartService.clear_cart(user_id)
        
        return OrderService.get_order(order["id"], user_id)
    
    @staticmethod
    def get_order(order_id: str, user_id: str):
        response = supabase.table("orders").select("*, order_items(*, books(*))") \
            .eq("id", order_id) \
            .execute()
        
        if not response.data:
            raise NotFoundException("Order not found")
        
        return response.data[0]
    
    @staticmethod
    def get_user_orders(user_id: str, page: int = 1, limit: int = 10):
        offset = (page - 1) * limit
        
        count_response = supabase.table("orders").select("*", count="exact") \
            .eq("user_id", user_id) \
            .execute()
        
        total = count_response.count
        
        response = supabase.table("orders").select("*, order_items(*, books(*))") \
            .eq("user_id", user_id) \
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
    def update_order_status(order_id: str, status_data: OrderUpdateStatus):
        response = supabase.table("orders").select("*") \
            .eq("id", order_id) \
            .execute()
        
        if not response.data:
            raise NotFoundException("Order not found")
        
        update_response = supabase.table("orders").update({
            "status": status_data.status
        }).eq("id", order_id).execute()
        
        if not update_response.data:
            raise Exception("Failed to update order status")
        
        return update_response.data[0]
    
    @staticmethod
    def cancel_order(order_id: str, user_id: str):
        order = OrderService.get_order(order_id, user_id)
        
        if order["status"] in ["shipped", "delivered"]:
            raise BadRequestException("Cannot cancel shipped or delivered order")
        
        if order["status"] == "cancelled":
            raise BadRequestException("Order already cancelled")
        
        response = supabase.table("orders").update({
            "status": "cancelled"
        }).eq("id", order_id).execute()
        
        order_items = supabase.table("order_items").select("*") \
            .eq("order_id", order_id) \
            .execute()
        
        for item in order_items.data:
            BookService.update_stock(item["book_id"], item["quantity"])
        
        return {"message": "Order cancelled successfully"}