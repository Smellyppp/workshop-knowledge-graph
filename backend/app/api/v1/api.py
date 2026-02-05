"""
API 路由主入口
整合所有 API 路由模块
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, knowledge_graph

# 创建 API 路由器
api_router = APIRouter()

# 注册认证相关路由
api_router.include_router(auth.router, prefix="/v1/auth", tags=["认证"])

# 注册用户管理相关路由
api_router.include_router(users.router, prefix="/v1/users", tags=["用户管理"])

# 注册知识图谱相关路由
api_router.include_router(knowledge_graph.router, prefix="/v1/knowledge-graph", tags=["知识图谱"])
