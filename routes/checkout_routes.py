from fastapi import APIRouter, HTTPException
from supabaseclient import supabase
from model.checkout_model import CheckoutRequest

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/checkout")
def checkout(data: CheckoutRequest):

    cart_response = (
        supabase.table("cart_items")
        .select("*")
        .eq("user_id", data.user_id)
        .execute()
    )

    cart_items = cart_response.data

    if not cart_items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total_amount = 0

    for item in cart_items:

        product = (
            supabase.table("products")
            .select("price")
            .eq("id", item["product_id"])
            .single()
            .execute()
        )

        total_amount += (
            float(product.data["price"])
            * item["quantity"]
        )

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

    order_id = order_response.data[0]["id"]

    for item in cart_items:

        product = (
            supabase.table("products")
            .select("price")
            .eq("id", item["product_id"])
            .single()
            .execute()
        )

        (
            supabase.table("order_items")
            .insert({
                "order_id": order_id,
                "product_id": item["product_id"],
                "quantity": item["quantity"],
                "price": product.data["price"]
            })
            .execute()
        )
           # Reduce stock
        new_stock = product["stock_quantity"] - item["quantity"]

        supabase.table("products").update({
            "stock_quantity": new_stock
        }).eq(
            "id",
            product["id"]
        ).execute()

    (
        supabase.table("cart_items")
        .delete()
        .eq("user_id", data.user_id)
        .execute()
    )

    return {
        "message": "Order placed successfully",
        "order_id": order_id,
        "total_amount": total_amount
    }