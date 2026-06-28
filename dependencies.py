from fastapi import HTTPException, Security, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# Import your configured supabase client from your project
from supabaseclient import supabase 
from auth import decode_access_token  # Assuming token decoding is in auth.py

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Extracts the token, decodes it, and retrieves the complete user profile 
    dynamically from the public.users database table.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired credentials."
        )
    
    user_email = payload.get("sub") # Assuming email or subject is stored in 'sub'
    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing user identity."
        )

    # Dynamically query your public.users table using the schema columns
    response = supabase.table("users").select("id, name, email, role").eq("email", user_email).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account not found."
        )
        
    return response.data[0] # Returns the user dictionary containing the role

def require_admin(current_user: dict = Depends(get_current_user)):
    """
    Enforces role-based restriction. Bypasses any hardcoded string checks 
    and relies strictly on the database 'role' column.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Administrator privileges required."
        )
    return current_user