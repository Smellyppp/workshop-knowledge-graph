"""
认证接口
处理用户登录、登出和身份验证
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.models.user import get_db
from app.schemas.user import LoginRequest, LoginResponse
from app.services.user_service import UserService
from app.services.operation_log_service import OperationLogService
from app.core.security import create_access_token
from app.core.deps import get_current_user
from app.core.logger_helper import log_operation

# 创建路由器
router = APIRouter()


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录接口

    Args:
        request: FastAPI 请求对象
        login_data: 登录请求数据（用户名和密码）
        db: 数据库会话

    Returns:
        LoginResponse: 包含访问令牌和用户信息

    Raises:
        HTTPException: 用户名或密码错误时返回 401
    """
    user = UserService.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        # 记录登录失败日志
        await log_operation(
            db=db,
            user_id=0,  # 未知用户
            username=login_data.username,
            action_type=OperationLogService.ACTION_LOGIN,
            module=OperationLogService.MODULE_AUTH,
            request=request,
            status=0,  # 失败
            remark="用户名或密码错误"
        )
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

    # 记录登录成功日志
    await log_operation(
        db=db,
        user_id=user.id,
        username=user.username,
        action_type=OperationLogService.ACTION_LOGIN,
        module=OperationLogService.MODULE_AUTH,
        request=request,
        status=1,  # 成功
        remark="用户登录成功"
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
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    用户登出接口
    注意：客户端需要清除本地存储的令牌
    """
    # 记录登出日志
    await log_operation(
        db=db,
        user_id=current_user.get("id"),
        username=current_user.get("username"),
        action_type=OperationLogService.ACTION_LOGOUT,
        module=OperationLogService.MODULE_AUTH,
        request=request,
        status=1,
        remark="用户登出成功"
    )

    return {"message": "登出成功"}
