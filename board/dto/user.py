from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    id: int
    username: str
    email: EmailStr
    profile_pic: Optional[str] = None
    intro: Optional[str] = ""

class UserResponse(BaseModel):
    message: str
    user_id: int

    class Config:
        from_attributes = True
