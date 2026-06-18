from fastapi import APIRouter, HTTPException
from supabaseclient import supabase

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("/search")
def search_products(q: str):

    response = (
        supabase.table("products")
        .select("*")
        .or_(
            f"name.ilike.%{q}%,"
            f"brand.ilike.%{q}%,"
            f"fragrance_type.ilike.%{q}%,"
            f"description.ilike.%{q}%"
        )
        .limit(10)
        .execute()
    )

    return response.data