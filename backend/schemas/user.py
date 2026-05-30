from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


# 请求体
class UserRegister(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="用户名，长度3-50"
    )
    password: str = Field(
        ..., min_length=6, max_length=128, description="密码，长度6-128"
    )
    email: EmailStr = Field(..., description="邮箱地址")


class UserLogin(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=50, description="用户名，长度3-50"
    )
    password: str = Field(
        ..., min_length=6, max_length=128, description="密码，长度6-128"
    )


# 响应体
class UserRegisterResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: str = "unknown"
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRegisterResponse


class UserTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
