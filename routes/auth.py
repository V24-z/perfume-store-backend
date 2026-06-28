from model.model import User,Loginuser,AdminCreate
from fastapi import APIRouter,HTTPException,BackgroundTasks, Depends
from supabaseclient import supabase
from auth import create_access_token
from dependencies import admin_required

import bcrypt
import requests

router=APIRouter()
#______________________   
#=======n8n webhook trigger function=========
#______________________   

def trigger_welcome_email(name: str, email: str):
    print("Triggering n8n webhook for:", name, email)
    response=requests.post(
        "https://task-ocr.app.n8n.cloud/webhook/user-registration",
        json={"name": name, "email": email},
        timeout=5
    )
    print("Status Code:", response.status_code)
    print("Response:", response.text)
#______________________       
#=========SIGNUP==============
#______________________   

@router.post("/signin")
def signin(user:User , background_tasks: BackgroundTasks):


    # Check if email already exists
    response = supabase.table("users").select("*").eq("email", user.email).execute()
    if response.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pass = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    res = supabase.table("users").insert({
        "name": user.name,
        "email": user.email,
        "phon": user.phon,        
        "password": hashed_pass
        # registered date auto-generated
    }).execute()

# Trigger n8n webhook
   # Add background task
    background_tasks.add_task(trigger_welcome_email, user.name, user.email)

    return {
        "message": "Sign up successfully",
        "data": res.data
    }
#______________________     
#========LOGIN=========
#______________________   

@router.post("/login")
def login(user:Loginuser):
    
    response=supabase.table("users").select("*").eq("email",user.email).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="User not found")

    db_user = response.data[0]
     # check password
    is_valid = bcrypt.checkpw(
        user.password.encode("utf-8"),
        db_user["password"].encode("utf-8")
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid password")

    token = create_access_token({
    "id": db_user["id"]
 })
    print("NEW LOGIN ENDPOINT EXECUTED")
    return {
    "message": "Login successful",
    "access_token": token,
    "token_type": "bearer",
    "user": {
        "id": db_user["id"],
        "name": db_user["name"],
        "email": db_user["email"],
        "role": db_user["role"]
    }
}


def mask_email(email):
    if not email or "@" not in email:
        return email

    name, domain = email.split("@")
    return name[:2] + "***@" + domain




#______________________   
#=========GET ALL USERS=========
#______________________   

@router.get("/users")
def get_users(current_user=Depends(admin_required)):

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    response = supabase.table("users").select("*").execute()

    users = response.data

    for user in users:
        if user.get("email"):
            user["email"] = mask_email(user["email"])

    return {
        "message": "Users fetched successfully",
        "data": users
    }

#______________________   
#======ADMIN CREATE USER=========
#______________________   


@router.post("/create-admin")
def create_admin(admin_data: AdminCreate, current_user=Depends(admin_required)):
    # Check if email already exists
    response = (
        supabase.table("users")
        .select("*")
        .eq("email", admin_data.email)
        .execute()
    )

    if response.data:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = bcrypt.hashpw(
        admin_data.password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    result = (
        supabase.table("users")
        .insert({
            "name": admin_data.name,
            "email": admin_data.email,
            "phon": admin_data.phon,
            "password": hashed_password,
            "role": "admin"
        })
        .execute()
    )

    return {
        "message": "Admin created successfully",
        "data": result.data
    }


@router.get("/admins")
def get_admins(current_user=Depends(admin_required)):
    response = (
        supabase.table("users")
        .select("id,name,email,phon,registerd,role")
        .eq("role", "admin")
        .execute()
    )

    return {
        "message": "Admins fetched successfully",
        "data": response.data
    }
    