from fastapi import APIRouter, HTTPException
from supabaseclient import supabase
from model.cart_model import CartCreate, CartUpdate

router = APIRouter(prefix="/cart", tags=["Cart"])


# ─── ADD TO CART ───
@router.post("/")
def add_to_cart(cart: CartCreate):

    if not cart.user_id or not cart.product_id:
        raise HTTPException(status_code=400, detail="Missing fields")

    existing = (
        supabase.table("cart_items")
        .select("*")
        .eq("user_id", cart.user_id)
        .eq("product_id", cart.product_id)
        .execute()
    )

    if existing.data:
        item = existing.data[0]

        updated = (
            supabase.table("cart_items")
            .update({
                "quantity": item["quantity"] + cart.quantity
            })
            .eq("id", item["id"])
            .execute()
        )

        return {"message": "Cart updated", "data": updated.data}

    response = (
        supabase.table("cart_items")
        .insert({
            "user_id": cart.user_id,
            "product_id": cart.product_id,
            "quantity": cart.quantity,
        })
        .execute()
    )

    return {"message": "Added", "data": response.data}


# ─── UPDATE CART ───
@router.put("/{cart_id}")
def update_cart(cart_id: int, data: CartUpdate):

    response = (
        supabase.table("cart_items")
        .update({
            "quantity": data.quantity
        })
        .eq("id", cart_id)
        .execute()
    )

    return response.data


# ─── DELETE ITEM ───
@router.delete("/{cart_id}")
def delete_cart(cart_id: int):

    response = (
        supabase.table("cart_items")
        .delete()
        .eq("id", cart_id)
        .execute()
    )

    return {
        "message": "Deleted",
        "data": response.data
    }


# ─── CLEAR CART ───
@router.delete("/clear/{user_id}")
def clear_cart(user_id: int):

    supabase.table("cart_items") \
        .delete() \
        .eq("user_id", user_id) \
        .execute()

    return {"message": "Cart cleared"}

# ─── GET CART ───
@router.get("/{user_id}")
def get_cart(user_id: int):

    response = (
        supabase.table("cart_items")
        .select("*, products(*)")
        .eq("user_id", user_id)
        .execute()
    )

    return response.data

@router.get("/all_cart")
def get_all_carts():

    response = (
        supabase.table("cart_items")
        .select("*, products(*), users(*)")
        .execute()
    )

    return response.data    

@router.get("/cart_by_users")
def get_users_with_carts():

    response = (
        supabase.table("cart_items")
        .select("user_id")
        .execute()
    )

    users = list({item["user_id"] for item in response.data})

    return users


