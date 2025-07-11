from typing import Optional
from pydantic import BaseModel, Field

class RegisterSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=6)
    role: str = Field(default="user")  # Optional role field (default: user)

class LoginSchema(BaseModel):
    username: str
    password: str

class AdminLoginSchema(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
