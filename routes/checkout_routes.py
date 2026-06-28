from fastapi import APIRouter, HTTPException
from supabaseclient import supabase
from model.checkout_model import CheckoutRequest, UpdateOrderStatus
import requests

N8N_WEBHOOK_URL = "https://task-ocr.app.n8n.cloud/webhook/generate-invoice"
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/checkout")
def checkout(data: CheckoutRequest):

    # ─── 1. GET CART ITEMS ───
    cart_response = (
        supabase.table("cart_items")
        .select("*")
        .eq("user_id", data.user_id)
        .execute()
    )

    cart_items = cart_response.data

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    # ─── 2. FETCH PRODUCTS + CALCULATE TOTAL ───
    total_amount = 0
    product_cache = {}

    for item in cart_items:

        product_res = (
            supabase.table("products")
            .select("id, name, price, stock_quantity")
            .eq("id", item["product_id"])
            .single()
            .execute()
        )

        if not product_res.data:
            raise HTTPException(
                status_code=404,
                detail=f"Product not found: {item['product_id']}"
            )

        product = product_res.data
        product_cache[item["product_id"]] = product
        total_amount += float(product["price"]) * item["quantity"]

    # ─── 3. CREATE ORDER ───
    order_response = (
        supabase.table("orders")
        .insert({
            "user_id": data.user_id,
            "total_amount": total_amount,
            "shipping_address": data.shipping_address,
            "phone_number": data.phone_number,
            "status": "pending",
            "payment_method": "cod",
            "payment_status": "pending"
        })
        .execute()
    )

    if not order_response.data:
        raise HTTPException(status_code=500, detail="Failed to create order")

    order_id = order_response.data[0]["id"]

    # ─── 4. CREATE ORDER ITEMS + UPDATE STOCK ───
    for item in cart_items:

        product = product_cache[item["product_id"]]

        supabase.table("order_items").insert({
            "order_id": order_id,
            "product_id": item["product_id"],
            "quantity": item["quantity"],
            "price": product["price"]
        }).execute()

        current_stock = product["stock_quantity"] or 0
        new_stock = current_stock - item["quantity"]

        if new_stock < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {item['product_id']}"
            )

        supabase.table("products").update({
            "stock_quantity": new_stock
        }).eq("id", product["id"]).execute()

    # ─── 5. CLEAR CART ───
    supabase.table("cart_items").delete().eq("user_id", data.user_id).execute()

    # ─── 6. RESPONSE ───
    return {
        "message": "Order placed successfully",
        "order_id": order_id,
        "total_amount": total_amount
    }


# === get all orders ===
@router.get("/all")
def get_all_orders():
    response = (
        supabase.table("orders")
        .select("*, users(*)")
        .order("created_at", desc=True)
        .execute()
    )
    return response.data

# Get all orders of logged in user
@router.get("/user/{user_id}")
def get_user_orders(user_id: int):

    response = (
        supabase.table("orders")
        .select("""
            *,
            users(*),
            order_items(
                *,
                products(*)
            )
        """)
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data

# === DEBUG: call this to diagnose empty customer details ===
@router.get("/debug/{order_id}")
def debug_order(order_id: int):

    order_raw = (
        supabase.table("orders")
        .select("*")
        .eq("id", order_id)
        .single()
        .execute()
    )

    if not order_raw.data:
        return {"error": "Order not found"}

    user_id = order_raw.data.get("user_id")

    user_raw = (
        supabase.table("users")
        .select("*")
        .eq("id", user_id)
        .single()
        .execute()
    )

    items_raw = (
        supabase.table("order_items")
        .select("*, products(id, name, price)")
        .eq("order_id", order_id)
        .execute()
    )

    return {
        "raw_order": order_raw.data,
        "raw_user": user_raw.data,
        "raw_items": items_raw.data
    }


# === order by order id ===
@router.get("/{order_id}")
def get_order(order_id: int):
    order = (
        supabase.table("orders")
        .select("""
            *,
            users(*),
            order_items(
                *,
                products(*)
            )
        """)
        .eq("id", order_id)
        .single()
        .execute()
    )
    return order.data


# === order status update ===
@router.put("/{order_id}")
def update_order_status(order_id: int, data: UpdateOrderStatus):

    # 1. Get current order (already has phone_number + shipping_address)
    existing = (
        supabase.table("orders")
        .select("*")
        .eq("id", order_id)
        .single()
        .execute()
    )

    if not existing.data:
        raise HTTPException(status_code=404, detail="Order not found")

    old_status = existing.data["status"]

    # 2. Update status
    response = (
        supabase.table("orders")
        .update({"status": data.status})
        .eq("id", order_id)
        .execute()
    )

    updated_order = response.data[0]

    # 3. Trigger invoice ONLY on: pending → confirmed
    if old_status != "confirmed" and data.status == "confirmed":
        try:
            order_data = existing.data
            user_id = order_data.get("user_id")

            # Fetch user separately
            user_res = (
                supabase.table("users")
                .select("id, name, email")
                .eq("id", user_id)
                .single()
                .execute()
            )
            user = user_res.data
            print("USER DATA:", user)

            if not user:
                raise Exception(f"User not found for user_id: {user_id}")

            # Fetch order items with product names
            items_res = (
                supabase.table("order_items")
                .select("quantity, price, products(id, name)")
                .eq("order_id", order_id)
                .execute()
            )
            order_items = items_res.data
            print("ORDER ITEMS:", order_items)

            items_payload = [
                {
                    "name": oi["products"]["name"] if oi.get("products") else "Unknown Item",
                    "quantity": oi["quantity"],
                    "price": float(oi["price"])
                }
                for oi in (order_items or [])
            ]

            payload = {
                "order_id":         str(order_id),
                "customer_name":    user.get("name", ""),
                "email":            user.get("email", ""),
                "phone_number":     order_data.get("phone_number", ""),      # ✅ from orders table
                "shipping_address": order_data.get("shipping_address", ""),  # ✅ from orders table
                "order_date":       order_data.get("created_at", "")[:10],
                "payment_method":   order_data.get("payment_method", "COD").upper(),
                "payment_status":   order_data.get("payment_status", ""),
                "items":            items_payload,
                "subtotal":         float(order_data.get("total_amount", 0)),
                "tax":              0,
                "discount":         0,
                "total_amount":     float(order_data.get("total_amount", 0))
            }

            print("✅ Sending to n8n:", payload)

            n8n_response = requests.post(
                N8N_WEBHOOK_URL,
                json=payload,
                timeout=10
            )
            print("n8n status:", n8n_response.status_code)
            print("n8n response:", n8n_response.text[:300])

        except Exception as e:
            print("❌ n8n trigger failed:", e)

    return {
        "message": "status updated",
        "order": updated_order
    }


