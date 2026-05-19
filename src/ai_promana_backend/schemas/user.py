from pydantic import BaseModel, Field
from typing import Optional

class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    full_name: Optional[str]
    role: str
    created_at: str
    updated_at: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TokenData(BaseModel):
    username: Optional[str] = None
