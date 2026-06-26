from fastapi import APIRouter, HTTPException
from supabaseclient import supabase
from model.bannermodel import BannerCreate, BannerUpdate

router = APIRouter(prefix="/banners", tags=["Banners"])


@router.post("/")
def create_banner(banner: BannerCreate):

    result = (
        supabase.table("banners")
        .insert(banner.model_dump())
        .execute()
    )

    return {
        "message": "Banner created successfully",
        "data": result.data
    }

@router.get("/")
def banner():
    res=supabase.table("banners").select("*").execute()
    return res.data


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

@router.put("/{banner_id}")
def update_banner(
    banner_id: str,
    banner: BannerUpdate
):

    update_data = {
        k: v
        for k, v in banner.dict().items()
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

@router.delete("/{banner_id}")
def delete_banner(banner_id: str):

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