"""
用户管理接口
处理用户的增删改查操作
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from app.models.user import get_db, UserManage
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services.user_service import UserService
from app.services.operation_log_service import OperationLogService
from app.core.deps import get_current_user, get_current_admin
from app.core.logger_helper import log_operation

# 创建路由器
router = APIRouter()


@router.get("", response_model=UserListResponse, summary="获取用户列表")
async def get_users(
    request: Request,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="每页记录数"),
    username: Optional[str] = Query(None, description="用户名筛选"),
    user_type: Optional[int] = Query(None, ge=0, le=1, description="用户类型筛选"),
    status: Optional[int] = Query(None, ge=0, le=1, description="状态筛选"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取用户列表（支持分页和筛选）

    Args:
        skip: 跳过的记录数
        limit: 每页返回的记录数（最多100）
        username: 按用户名模糊查询
        user_type: 按用户类型筛选（0=普通用户，1=管理员）
        status: 按状态筛选（0=禁用，1=启用）
        db: 数据库会话
        current_user: 当前已认证用户

    Returns:
        UserListResponse: 包含总数和用户列表
    """
    # 非管理员只能查看自己
    if current_user.get("user_type") != 1:
        user = UserService.get_user_by_id(db, current_user.get("id"))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return UserListResponse(total=1, items=[user])

    users, total = UserService.get_users(db, skip, limit, username, user_type, status)
    items = [UserResponse.model_validate(user) for user in users]

    # 记录查询日志
    await log_operation(
        db=db,
        user_id=current_user.get("id"),
        username=current_user.get("username"),
        action_type=OperationLogService.ACTION_QUERY,
        module=OperationLogService.MODULE_USER_MANAGEMENT,
        request=request,
        status=1
    )

    return UserListResponse(total=total, items=items)


@router.get("/{user_id}", response_model=UserResponse, summary="获取用户详情")
async def get_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    根据 ID 获取用户信息

    Args:
        user_id: 用户 ID
        db: 数据库会话
        current_user: 当前已认证用户

    Returns:
        UserResponse: 用户信息

    Raises:
        HTTPException: 用户不存在或权限不足
    """
    # 非管理员只能查看自己
    if current_user.get("user_type") != 1 and current_user.get("id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )

    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 记录查询日志
    await log_operation(
        db=db,
        user_id=current_user.get("id"),
        username=current_user.get("username"),
        action_type=OperationLogService.ACTION_QUERY,
        module=OperationLogService.MODULE_USER_MANAGEMENT,
        request=request,
        status=1,
        remark=f"查询用户: {user.username}"
    )

    return UserResponse.model_validate(user)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="创建用户")
async def create_user(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    创建新用户（仅管理员）

    Args:
        user_data: 用户创建数据
        db: 数据库会话
        current_user: 当前已认证管理员

    Returns:
        UserResponse: 创建的用户信息

    Raises:
        HTTPException: 用户名已存在或权限不足
    """
    if UserService.username_exists(db, user_data.username):
        # 记录创建失败日志
        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type=OperationLogService.ACTION_CREATE,
            module=OperationLogService.MODULE_USER_MANAGEMENT,
            request=request,
            status=0,
            remark=f"创建用户失败: 用户名 {user_data.username} 已存在"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    user = UserService.create_user(
        db,
        username=user_data.username,
        password=user_data.password,
        user_type=user_data.user_type
    )

    # 记录创建成功日志
    await log_operation(
        db=db,
        user_id=current_user.get("id"),
        username=current_user.get("username"),
        action_type=OperationLogService.ACTION_CREATE,
        module=OperationLogService.MODULE_USER_MANAGEMENT,
        request=request,
        status=1,
        remark=f"创建用户: {user.username}"
    )

    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse, summary="更新用户")
async def update_user(
    request: Request,
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    更新用户信息

    - 管理员可以更新任何用户的密码和状态
    - 普通用户只能更新自己的密码

    Args:
        user_id: 用户 ID
        user_data: 用户更新数据
        db: 数据库会话
        current_user: 当前已认证用户

    Returns:
        UserResponse: 更新后的用户信息

    Raises:
        HTTPException: 用户不存在或权限不足
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 检查权限
    is_admin = current_user.get("user_type") == 1
    is_self = current_user.get("id") == user_id

    if not is_admin and not is_self:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )

    # 普通用户只能更新自己的密码
    if not is_admin and user_data.status is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，无法修改状态"
        )

    # 更新密码
    if user_data.password:
        user = UserService.update_user_password(db, user_id, user_data.password)

    # 更新状态（仅管理员）
    if user_data.status is not None and is_admin:
        user = UserService.update_user_status(db, user_id, user_data.status)

    # 记录更新日志
    await log_operation(
        db=db,
        user_id=current_user.get("id"),
        username=current_user.get("username"),
        action_type=OperationLogService.ACTION_UPDATE,
        module=OperationLogService.MODULE_USER_MANAGEMENT,
        request=request,
        status=1,
        remark=f"更新用户: {user.username}"
    )

    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="删除用户")
async def delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    删除用户（仅管理员）

    Args:
        user_id: 用户 ID
        db: 数据库会话
        current_user: 当前已认证管理员

    Raises:
        HTTPException: 用户不存在或权限不足
    """
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    username = user.username
    UserService.delete_user(db, user_id)

    # 记录删除日志
    await log_operation(
        db=db,
        user_id=current_user.get("id"),
        username=current_user.get("username"),
        action_type=OperationLogService.ACTION_DELETE,
        module=OperationLogService.MODULE_USER_MANAGEMENT,
        request=request,
        status=1,
        remark=f"删除用户: {username}"
    )

    return None
