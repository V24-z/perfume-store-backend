from fastapi import APIRouter, HTTPException
from supabaseclient import supabase
from model.checkout_model import CheckoutRequest,UpdateOrderStatus
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
            .select("id, price, stock_quantity")
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

        # handle null stock safely
        stock = product["stock_quantity"] or 0

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

        # insert order item
        supabase.table("order_items").insert({
            "order_id": order_id,
            "product_id": item["product_id"],
            "quantity": item["quantity"],
            "price": product["price"]
        }).execute()

        # safe stock calculation
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

#===get all order===
@router.get("/all")
def get_all_orders():

    response = (
        supabase.table("orders")
        .select("*, users(*)")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data

#===order by order id====
@router.get("/{order_id}")
def get_order(order_id: int):

    order = (
        supabase.table("orders")
        .select(
            """
            *,
            users(*),
            order_items(
                *,
                products(*)
            )
            """
        )
        .eq("id", order_id)
        .single()
        .execute()
    )

    return order.data


#===order status update ===

@router.put("/{order_id}")
def update_order_status(order_id: int, data: UpdateOrderStatus):

    # 1. Get current order first (IMPORTANT)
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

    # 2. Update order
    response = (
        supabase.table("orders")
        .update({"status": data.status})
        .eq("id", order_id)
        .execute()
    )

    updated_order = response.data[0]

    # 3. Trigger invoice ONLY on status change: pending → confirmed
    if old_status != "confirmed" and data.status == "confirmed":
        try:
            requests.post(
                N8N_WEBHOOK_URL,
                json={
                    "order_id": updated_order["id"],
                    "email": updated_order["email"],
                    "amount": updated_order["total_amount"]
                },
                timeout=5
            )
        except Exception as e:
            print("n8n trigger failed:", e)

    return {
        "message": "status updated",
        "order": updated_order
    }