from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from supabaseclient import supabase
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


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

        print("DB Response:", response.data)

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