from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from apps.schemas.role import Role


class UserRegister(BaseModel):
    #id: int
    name: str = Field(min_length=1, max_length=100)
    password: str
    email: EmailStr
    age: int
    role: Role


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    age: int
    role: Role
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str="bearer"
    user: UserResponse
