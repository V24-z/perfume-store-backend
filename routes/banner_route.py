from fastapi import APIRouter, HTTPException, Depends
from supabaseclient import supabase
from model.bannermodel import BannerCreate, BannerUpdate
# Import the security gatekeeper
from dependencies import require_admin

router = APIRouter(prefix="/banners", tags=["Banners"])


# =========================
# Create Banner (SECURED)
# =========================
@router.post("/")
def create_banner(banner: BannerCreate, admin_user: dict = Depends(require_admin)):

    result = (
        supabase.table("banners")
        .insert(banner.model_dump())
        .execute()
    )

    return {
        "message": "Banner created successfully",
        "data": result.data
    }


# =========================
# Get All Banners (PUBLIC)
# =========================
@router.get("/")
def get_all_banners():
    res = supabase.table("banners").select("*").execute()
    return res.data


# =========================
# Get Single Banner (PUBLIC - Fixed unreachable code block)
# =========================
@router.get("/{banner_id}")
def get_banner_by_id(banner_id: str):
    result = (
        supabase.table("banners")
        .select("*")
        .eq("id", banner_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=404,
            detail="Banner not found"
        )

    return result.data[0]


# =========================
# Update Banner (SECURED)
# =========================
@router.put("/{banner_id}")
def update_banner(
    banner_id: str,
    banner: BannerUpdate,
    admin_user: dict = Depends(require_admin)
):

    update_data = {
        k: v
        for k, v in banner.model_dump().items()  # Using standard .model_dump() instead of deprecated .dict()
        if v is not None
    }

    result = (
        supabase.table("banners")
        .update(update_data)
        .eq("id", banner_id)
        .execute()
    )

    return {
        "message": "Banner updated successfully",
        "data": result.data
    }


# =========================
# Delete Banner (SECURED)
# =========================
@router.delete("/{banner_id}")
def delete_banner(banner_id: str, admin_user: dict = Depends(require_admin)):

    result = (
        supabase.table("banners")
        .delete()
        .eq("id", banner_id)
        .execute()
    )

    return {
        "message": "Banner deleted successfully",
        "data": result.data
    }