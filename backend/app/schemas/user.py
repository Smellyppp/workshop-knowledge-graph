"""
用户数据模型（Pydantic）
用于请求数据验证和响应数据序列化
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_serializer


class LoginRequest(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., minlength=6, description="密码")


class LoginResponse(BaseModel):
    """用户登录响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserCreate(BaseModel):
    """用户创建请求模型"""
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    password: str = Field(..., minlength=6, description="密码")
    user_type: int = Field(default=0, ge=0, le=1, description="用户类型：0=普通用户，1=管理员")


class UserUpdate(BaseModel):
    """用户更新请求模型"""
    password: Optional[str] = Field(None, min_length=6, description="新密码")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态：0=禁用，1=启用")


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    user_type: int
    status: int
    created_at: datetime
    updated_at: datetime

    @field_serializer('created_at', 'updated_at')
    def datetime_to_iso(self, dt: datetime) -> str:
        """将日期时间转换为 ISO 格式字符串"""
        return dt.isoformat() if dt else None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应模型"""
    total: int
    items: list[UserResponse]
