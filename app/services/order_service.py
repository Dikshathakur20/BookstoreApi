from app.core.supabase import supabase
from app.core.exceptions import NotFoundException, BadRequestException
from app.schemas.order import OrderCreate, OrderUpdateStatus
from app.services.cart_service import CartService
from app.services.book_service import BookService
from datetime import datetime, timedelta

class OrderService:
    @staticmethod
    def place_order(user_id: str, order_data: OrderCreate):
        cart = CartService.get_cart(user_id)
        
        if not cart["items"]:
            raise BadRequestException("Cart is empty")
        
        total_amount = 0
        order_items = []
        
        for item in cart["items"]:
            book = item.get("book")
            if not book:
                raise BadRequestException("Book data not found in cart item")
            
            book_id = item.get("book_id")
            quantity = item.get("quantity", 0)
            
            if book["stock_quantity"] < quantity:
                raise BadRequestException(f"Insufficient stock for {book['title']}")
            
            total_amount += quantity * book["price"]
            order_items.append({
                "book_id": book_id,
                "quantity": quantity,
                "price_at_time": book["price"]
            })
        
        order_data_dict = order_data.model_dump()
        order_data_dict["user_id"] = user_id
        order_data_dict["total_amount"] = total_amount
        order_data_dict["status"] = "pending"
        order_data_dict["payment_status"] = "pending"
        
        # ✅ Insert order
        order_response = supabase.table("orders").insert(order_data_dict).execute()
        
        if not order_response.data:
            raise Exception("Failed to create order")
        
        order = order_response.data[0]
        print(f"✅ Order created: {order['id']}")  # Debug log
        
        # ✅ Insert order items - ONE BY ONE with proper error handling
        for item in order_items:
            item["order_id"] = order["id"]
            print(f"📦 Inserting order item: {item}")  # Debug log
            
            try:
                item_response = supabase.table("order_items").insert(item).execute()
                if not item_response.data:
                    print(f"❌ Failed to insert item: {item}")
                else:
                    print(f"✅ Item inserted: {item_response.data[0]['id']}")
            except Exception as e:
                print(f"❌ Error inserting item: {e}")
                # Don't raise, continue with other items
        
        # ✅ Update stock
        for item in cart["items"]:
            book_id = item.get("book_id")
            quantity = item.get("quantity", 0)
            try:
                BookService.update_stock(book_id, -quantity)
            except Exception as e:
                print(f"❌ Error updating stock for {book_id}: {e}")
        
        # ✅ Clear cart
        try:
            CartService.clear_cart(user_id)
        except Exception as e:
            print(f"❌ Error clearing cart: {e}")
        
        # ✅ Return order with items
        return OrderService.get_order(order["id"], user_id)
    
    @staticmethod
    def get_order(order_id: str, user_id: str):
        # ✅ First get order
        order_response = supabase.table("orders").select("*") \
            .eq("id", order_id) \
            .execute()
        
        if not order_response.data:
            raise NotFoundException("Order not found")
        
        order = order_response.data[0]
        
        # ✅ Then get order items with book data
        items_response = supabase.table("order_items").select("*, books(*)") \
            .eq("order_id", order_id) \
            .execute()
        
        order["order_items"] = items_response.data if items_response.data else []
        
        # ✅ Calculate estimated delivery
        created_at = order.get("created_at")
        if created_at:
            if isinstance(created_at, str):
                created_at_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_at_dt = created_at
            order["estimated_delivery"] = created_at_dt + timedelta(days=3)
        else:
            order["estimated_delivery"] = datetime.now() + timedelta(days=3)
        
        # ✅ Transform order items with book data
        if "order_items" in order and order["order_items"]:
            for item in order["order_items"]:
                if "books" in item and item["books"]:
                    book = item["books"]
                    item["book_name"] = book.get("title")
                    
                    if "categories" in book and book["categories"]:
                        book["category_name"] = book["categories"]["name"]
                        book.pop("categories", None)
                    
                    book["book_id"] = book["id"]
                    item["book"] = book
                    item.pop("books", None)
                    
                    if created_at:
                        if isinstance(created_at, str):
                            created_at_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            created_at_dt = created_at
                        item["delivery_date"] = created_at_dt + timedelta(days=3)
                    else:
                        item["delivery_date"] = datetime.now() + timedelta(days=3)
        
        return order
    
    @staticmethod
    def get_user_orders(user_id: str, page: int = 1, limit: int = 10):
        offset = (page - 1) * limit
        
        # ✅ Get count
        count_response = supabase.table("orders").select("*", count="exact") \
            .eq("user_id", user_id) \
            .execute()
        
        total = count_response.count
        
        # ✅ Get orders with pagination
        orders_response = supabase.table("orders").select("*") \
            .eq("user_id", user_id) \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        # ✅ For each order, fetch items
        items = []
        for order in orders_response.data:
            # ✅ Get order items
            items_response = supabase.table("order_items").select("*, books(*)") \
                .eq("order_id", order["id"]) \
                .execute()
            
            order["order_items"] = items_response.data if items_response.data else []
            
            # ✅ Calculate estimated delivery
            created_at = order.get("created_at")
            if created_at:
                if isinstance(created_at, str):
                    created_at_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                else:
                    created_at_dt = created_at
                order["estimated_delivery"] = created_at_dt + timedelta(days=3)
            else:
                order["estimated_delivery"] = datetime.now() + timedelta(days=3)
            
            # ✅ Transform order items
            if "order_items" in order and order["order_items"]:
                for item in order["order_items"]:
                    if "books" in item and item["books"]:
                        book = item["books"]
                        item["book_name"] = book.get("title")
                        
                        if "categories" in book and book["categories"]:
                            book["category_name"] = book["categories"]["name"]
                            book.pop("categories", None)
                        
                        book["book_id"] = book["id"]
                        item["book"] = book
                        item.pop("books", None)
                        
                        if created_at:
                            if isinstance(created_at, str):
                                created_at_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            else:
                                created_at_dt = created_at
                            item["delivery_date"] = created_at_dt + timedelta(days=3)
                        else:
                            item["delivery_date"] = datetime.now() + timedelta(days=3)
            
            items.append(order)
        
        return {
            "items": items,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 1,
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