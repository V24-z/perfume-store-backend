from fastapi import APIRouter, HTTPException

from supabaseclient import supabase
from model.category_model import (
    CategoryCreate,
    CategoryUpdate,
)

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

@router.post("/")
def create_category(category: CategoryCreate):

    result = (
        supabase
        .table("categories")
        .insert(category.model_dump())
        .execute()
    )

    return {
        "message": "Category created successfully",
        "data": result.data
    }


@router.get("/")
def get_categories():

    result = (
        supabase
        .table("categories")
        .select("*")
        .execute()
    )

    return result.data


@router.get("/{category_id}")
def get_category(category_id: str):

    result = (
        supabase
        .table("categories")
        .select("*")
        .eq("id", category_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return result.data[0]


@router.put("/{category_id}")
def update_category(
    category_id: str,
    category: CategoryUpdate
):

    update_data = {
        key: value
        for key, value in category.model_dump().items()
        if value is not None
    }

    result = (
        supabase
        .table("categories")
        .update(update_data)
        .eq("id", category_id)
        .execute()
    )

    return {
        "message": "Category updated successfully",
        "data": result.data
    }


@router.delete("/{category_id}")
def delete_category(category_id: str):

    result = (
        supabase
        .table("categories")
        .delete()
        .eq("id", category_id)
        .execute()
    )

    return {
        "message": "Category deleted successfully"
    }


@router.get("/active/list")
def active_categories():

    result = (
        supabase
        .table("categories")
        .select("*")
        .eq("is_active", True)
        .execute()
    )

    return result.data