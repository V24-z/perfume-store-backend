from model.model import User,Loginuser
from fastapi import APIRouter,HTTPException,BackgroundTasks
from supabaseclient import supabase
import bcrypt
import requests

router=APIRouter()
def trigger_welcome_email(name: str, email: str):
    print("Triggering n8n webhook for:", name, email)
    response=requests.post(
        "https://n8n-task.app.n8n.cloud/webhook/user-registration",
        json={"name": name, "email": email},
        timeout=5
    )
    print("Status Code:", response.status_code)
    print("Response:", response.text)

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

    return {"message": "Login successful",
            "id": db_user["id"], 
            "name":db_user["name"],
            "email":db_user["email"],
            "phon":db_user["phon"],
            "role":db_user["role"],
            "registerd":db_user["registerd"]}

@router.get("/users")
def get_users():
    response = supabase.table("users").select("*").execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="No users found")

    return {
        "message": "Users fetched successfully",
        "data": response.data
    }