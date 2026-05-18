from pydantic import BaseModel, Field
from typing import Optional


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: Optional[str] = Field(None, max_length=255, description="邮箱地址")
    phone: Optional[str] = Field(None, pattern=r"^1[3-9]\d{9}$", description="手机号码")
    password: str = Field(..., min_length=6, description="密码")
    full_name: Optional[str] = Field(None, max_length=100, description="真实姓名")


class AuthLoginRequest(BaseModel):
    username: str = Field(..., description="用户名/邮箱/手机号")
    password: str = Field(..., description="密码")
    rememberMe: bool = Field(default=False, description="是否记住我")
    loginType: str = Field(default="password", description="登录方式")
    deviceId: Optional[str] = Field(default=None, description="设备标识")
    clientType: Optional[str] = Field(default="web", description="客户端类型")


class RefreshTokenRequest(BaseModel):
    refreshToken: str = Field(..., description="刷新令牌")
