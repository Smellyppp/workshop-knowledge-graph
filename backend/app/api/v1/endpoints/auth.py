"""
认证接口
处理用户登录、登出和身份验证
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import get_db
from app.schemas.user import LoginRequest, LoginResponse
from app.services.user_service import UserService
from app.core.security import create_access_token
from app.core.deps import get_current_user

# 创建路由器
router = APIRouter()


@router.post("/login", response_model=LoginResponse, summary="用户登录")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    用户登录接口

    Args:
        request: 登录请求数据（用户名和密码）
        db: 数据库会话

    Returns:
        LoginResponse: 包含访问令牌和用户信息

    Raises:
        HTTPException: 用户名或密码错误时返回 401
    """
    user = UserService.authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )

    # 生成访问令牌
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "user_type": user.user_type
        }
    )

    return LoginResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "username": user.username,
            "user_type": user.user_type,
            "status": user.status
        }
    )


@router.get("/me", summary="获取当前用户信息")
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前已登录用户的信息

    Args:
        current_user: 当前已认证用户

    Returns:
        dict: 用户信息
    """
    return current_user


@router.post("/logout", summary="用户登出")
def logout():
    """
    用户登出接口
    注意：客户端需要清除本地存储的令牌
    """
    return {"message": "登出成功"}
