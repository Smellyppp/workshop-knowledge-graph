"""
FastAPI 应用程序入口
用户管理系统
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

# 创建 FastAPI 应用实例
app = FastAPI(
    title="车间资源系统 API",
    description="基于 FastAPI 和 MySQL 的车间资源管理系统",
    version="1.0.0"
)

# 配置 CORS 中间件（跨域资源共享）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # 允许的前端地址
    allow_credentials=True,  # 允许携带凭证
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 注册 API 路由
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    """根路径接口"""
    return {"message": "车间资源系统 API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    """健康检查接口"""
    return {"status": "healthy"}
