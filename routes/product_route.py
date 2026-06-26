from fastapi import APIRouter, HTTPException
from supabaseclient import supabase
from model.product_model import ProductCreate, ProductUpdate

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# =========================
# Create Product
# =========================
@router.post("/")
def create_product(product: ProductCreate):
    print("Category from frontend:", product.category_name)
    category_name = product.category_name.strip()
    try:
        category = (
            supabase
            .table("categories")
            .select("id")
            .eq("name", category_name)
            .single()
            .execute()
        )
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    

    product_data = product.model_dump()
    
    product_data["category_id"] = category.data["id"]
    print(product_data)
    product_data.pop("created_at", None)
    # Remove field not present in products table
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


# =========================
# Get Products + Filters
# =========================
@router.get("/")
def get_products(
    search: str = None,
    category_id: str = None,
    brand: str = None,
    max_price: float = None,
    sort: str = None,
    is_featured: bool = None,
    page: int = 1,
    limit: int = 12,
):

    start = (page - 1) * limit
    end = start + limit - 1

    query = (
        supabase
        .table("products")
        .select("*, category:categories(name)")
        .eq("is_active", True)
    )

    # Search Product Name
    if search:
        query = query.ilike(
            "name",
            f"{search}%"
        )

    # Category Filter
    if category_id:
        query = query.eq(
            "category_id",
            category_id
        )

    # Brand Filter
    if brand:
        query = query.ilike(
            "brand",
            f"%{brand}%"
        )

    # Price Filter
    if max_price:
        query = query.lte(
            "price",
            max_price
        )

    # Featured Filter
    if is_featured is not None:
        query = query.eq(
            "is_featured",
            is_featured
        )

    # Sorting
    if sort == "low":
        query = query.order(
            "price",
            desc=False
        )

    elif sort == "high":
        query = query.order(
            "price",
            desc=True
        )

    # Pagination
    query = query.range(
        start,
        end
    )
    print("CATEGORY_ID:", category_id)
    print("SORT:", sort)

    result = query.execute()
    print("TOTAL PRODUCTS:", len(result.data))
    print(result.data)
    return result.data
    


# =========================
# New Arrivals
# =========================
@router.get("/new-arrivals")
def get_new_arrivals():

    result = (
        supabase
        .table("products")
        .select("*")
        .eq("is_active", True)
        .order("created_at", desc=True)
        .limit(4)
        .execute()
    )

    return result.data


# =========================
# Featured Products
# =========================
@router.get("/featured/list")
def featured_products():

    result = (
        supabase
        .table("products")
        .select("*")
        .eq("is_active", True)
        .eq("is_featured", True)
        .execute()
    )

    return result.data


# =========================
# Get Single Product
# =========================
@router.get("/by-id/{product_id}")
def get_product(product_id: str):

    result = (
        supabase
        .table("products")
        .select("*, category:categories(name)")
        .eq("id", product_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return result.data


# =========================
# Products By Category
# =========================
"""@router.get("/category/{category_id}")
def products_by_category(category_id: str):

    result = (
        supabase
        .table("products")
        .select("*")
        .eq("category_id", category_id)
        .eq("is_active", True)
        .execute()
    )

    return result.data"""


# =========================
# Update Product
# =========================
@router.put("/{product_id}")
def update_product(
    product_id: str,
    product: ProductUpdate
):

    update_data = {
        key: value
        for key, value in product.model_dump().items()
        if value is not None
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


# =========================
# Delete Product
# =========================
@router.delete("/{product_id}")
def delete_product(product_id: str):

    (
        supabase
        .table("products")
        .delete()
        .eq("id", product_id)
        .execute()
    )

    return {
        "message": "Product deleted successfully"
    }


# =========================
# Toggle Featured
# =========================
"""@router.put("/{product_id}/featured")
def toggle_featured(
    product_id: str,
    is_featured: bool
):

    (
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
    }"""