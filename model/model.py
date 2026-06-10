from pydantic import BaseModel,EmailStr

class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    phon: str   

class Loginuser(BaseModel):
    email: EmailStr
    password:str    