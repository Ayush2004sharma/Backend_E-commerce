# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class SignupIn(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    accessToken: str
    tokenType: str = "bearer"

class UserOut(BaseModel):
    _id: str
    name: str
    email: str
    created_at: datetime