from fastapi import APIRouter, HTTPException
from supabaseclient import supabase
from model.cart_model import CartCreate, CartUpdate



router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/")
def add_to_cart(cart: CartCreate):

    existing = (
        supabase.table("cart_items")
        .select("*")
        .eq("user_id", cart.user_id)
        .eq("product_id", str(cart.product_id))
        .execute()
    )

    if existing.data:
        item = existing.data[0]

        supabase.table("cart_items").update(
            {
                "quantity": item["quantity"] + cart.quantity
            }
        ).eq("id", item["id"]).execute()

        return {"message": "Cart updated"}

    response = (
        supabase.table("cart_items")
        .insert(cart.model_dump(mode="json"))
        .execute()
    )

    return response.data


@router.get("/{user_id}")
def get_cart(user_id: int):

    response = (
        supabase.table("cart_items")
        .select(
            """
            *,
            products(*)
            """
        )
        .eq("user_id", user_id)
        .execute()
    )

    return response.data


@router.put("/{cart_id}")
def update_cart(cart_id: int, data: CartUpdate):

    response = (
        supabase.table("cart_items")
        .update({"quantity": data.quantity})
        .eq("id", cart_id)
        .execute()
    )

    return response.data