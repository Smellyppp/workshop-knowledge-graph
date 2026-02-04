"""
API 路由主入口
整合所有 API 路由模块
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users

# 创建 API 路由器
api_router = APIRouter()

# 注册认证相关路由
api_router.include_router(auth.router, prefix="/v1/auth", tags=["认证"])

# 注册用户管理相关路由
api_router.include_router(users.router, prefix="/v1/users", tags=["用户管理"])
