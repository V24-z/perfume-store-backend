from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from supabaseclient import supabase
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

security = HTTPBearer()


def get_current_user(credentials=Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        print("Payload:", payload)
        response = (
            supabase.table("users")
            .select("*")
            .eq("id", payload["id"])
            .single()
            .execute()
        )
        print("Supabase response:", response)

        if not response.data:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return response.data

    except JWTError as e:
        print(e)
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


def admin_required(current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user