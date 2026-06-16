from fastapi import APIRouter, HTTPException
from supabaseclient import supabase
from model.checkout_model import CheckoutRequest

router = APIRouter(prefix="/checkout", tags=["Checkout"])

@router.post("/")
def checkout(data: CheckoutRequest):

    if not data.items:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty"
        )

    total_amount = 0
    order_items = []

    for item in data.items:

        product = (
            supabase.table("products")
            .select("*")
            .eq("id", item.product_id)
            .execute()
        )

        if not product.data:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found"
            )

        product_data = product.data[0]

        price = product_data["price"]

        total_amount += price * item.quantity

        order_items.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": price
        })

    order = (
        supabase.table("orders")
        .insert({
            "user_id": data.user_id,
            "total_amount": total_amount,
            "status": "pending"
        })
        .execute()
    )

    order_id = order.data[0]["id"]

    for item in order_items:
        supabase.table("order_items").insert({
            "order_id": order_id,
            "product_id": item["product_id"],
            "quantity": item["quantity"],
            "price": item["price"]
        }).execute()

    return {
        "message": "Order created successfully",
        "order_id": order_id,
        "total_amount": total_amount
    }