from fastapi import APIRouter
from supabaseclient import supabase

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.get("/search")
def search_products(q: str):

    q = q.strip()

    # First search exact brand matches
    brand_response = (
        supabase.table("products")
        .select("id,name,brand")
        .ilike("brand", f"%{q}%")
        .limit(10)
        .execute()
    )

    # Then search product name matches
    product_response = (
        supabase.table("products")
        .select("*")
        .ilike("name", f"%{q}%")
        .limit(10)
        .execute()
    )

    brand_results = brand_response.data or []
    product_results = product_response.data or []

    # Remove duplicates
    seen = set()
    results = []

    for item in brand_results + product_results:
        if item["id"] not in seen:
            seen.add(item["id"])
            results.append(item)

    return results