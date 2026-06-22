from fastapi import APIRouter, HTTPException
from supabaseclient import supabase
from model.product_model import ProductCreate, ProductUpdate

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

@router.post("/")
def create_product(product: ProductCreate):

    category = (
        supabase
        .table("categories")
        .select("id")
        .eq("name", product.category_name)
        .single()
        .execute()
    )

    if not category.data:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    product_data = product.model_dump()

    product_data["category_id"] = category.data["id"]

    # remove category_name because products table doesn't have this column
    product_data.pop("category_name")

    result = (
        supabase
        .table("products")
        .insert(product_data)
        .execute()
    )

    return {
        "message": "Product created successfully",
        "data": result.data
    }
#ALL PRODUCTS + PAGINATION
@router.get("/")
def get_products(
    page: int = 1,
    limit: int = 12
    ):

    start = (page - 1) * limit
    end = start + limit - 1

    result = (
        supabase
        .table("products")
        .select("*,category:categories(name)")
        .range(start, end)
        .execute()
    )

    return result.data

#FILTER API

@router.get("/filter")
def filter_products(
    page: int = 1,
    limit: int = 12,
    category_id: str | None = None,
    brand: str | None = None,
    min_price: float = 0,
    max_price: float = 100000,
    search: str | None = None,
    featured: bool | None = None
    ):

    start = (page - 1) * limit
    end = start + limit - 1

    query = (
        supabase
        .table("products")
        .select("*")
        .gte("price", min_price)
        .lte("price", max_price)
    )

    if category_id:
        query = query.eq(
            "category_id",
            category_id
        )

    if brand:
        query = query.eq(
            "brand",
            brand
        )

    if featured is not None:
        query = query.eq(
            "is_featured",
            featured
        )

    if search:
        query = query.or_(
            f"name.ilike.%{search}%,"
            f"brand.ilike.%{search}%,"
            f"description.ilike.%{search}%,"
            f"fragrance_type.ilike.%{search}%"
        )

    result = (
        query
        .range(start, end)
        .execute()
    )

    return result.data




#BRANDS LIST

@router.get("/brands")
def get_brands():

    result = (
        supabase
        .table("products")
        .select("brand")
        .execute()
    )

    brands = list(
        set(
            item["brand"]
            for item in result.data
            if item["brand"]
        )
    )

    brands.sort()

    return brands    
@router.get("/new-arrivals")
def get_new_arrivals():
    response = (
        supabase.table("products")
        .select("*")
        .eq("is_active", True)
        .order("created_at", desc=True)
        .limit(4)
        .execute()
    )
    
    return response.data



@router.put("/{product_id}")
def update_product(
    product_id: str,
    product: ProductUpdate
):

    update_data = {
        k: v
        for k, v in product.dict().items()
        if v is not None
    }

    result = (
        supabase
        .table("products")
        .update(update_data)
        .eq("id", product_id)
        .execute()
    )

    return {
        "message": "Product updated successfully",
        "data": result.data
    }

@router.delete("/{product_id}")
def delete_product(product_id: str):

    result = (
        supabase
        .table("products")
        .delete()
        .eq("id", product_id)
        .execute()
    )

    return {
        "message": "Product deleted successfully"
    }

@router.get("/featured/list")
def featured_products():

    result = (
        supabase
        .table("products")
        .select("*")
        .eq("is_featured", True)
        .execute()
    )

    return result.data

@router.get("/by-id/{product_id}")

def get_product(product_id: str):

    result = (
        supabase
        .table("products")
        .select("*")
        .eq("id", product_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return result.data[0]

@router.get("/category/{category_id}")
def products_by_category(category_id: str):

    result = (
        supabase
        .table("products")
        .select("*")
        .eq("category_id", category_id)
        .execute()
    )

    return result.data

@router.put("/{product_id}/featured")
def toggle_featured(
    product_id: str,
    is_featured: bool
):

    result = (
        supabase
        .table("products")
        .update({
            "is_featured": is_featured
        })
        .eq("id", product_id)
        .execute()
    )

    return {
        "message": "Featured status updated"
    }
