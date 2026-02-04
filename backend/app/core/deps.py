"""
路由依赖模块
用于认证和授权检查
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_access_token

# HTTP Bearer 认证方案
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    获取当前已认证的用户

    Args:
        credentials: HTTP Bearer 凭证

    Returns:
        dict: 用户信息字典

    Raises:
        HTTPException: 认证失败时抛出 401 错误
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: Optional[int] = payload.get("sub")
    username: Optional[str] = payload.get("username")
    user_type: Optional[int] = payload.get("user_type")

    if user_id is None or username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": user_id,
        "username": username,
        "user_type": user_type
    }


async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    验证当前用户是否为管理员

    Args:
        current_user: 当前已认证用户

    Returns:
        dict: 用户信息字典

    Raises:
        HTTPException: 非管理员时抛出 403 错误
    """
    if current_user.get("user_type") != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限"
        )
    return current_user
