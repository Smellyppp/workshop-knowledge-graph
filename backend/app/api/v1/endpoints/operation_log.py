"""
操作日志 API 端点
提供日志查询、统计等接口，仅管理员可访问
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.models.user import get_db
from app.models.operation_log import OperationLog
from app.schemas.operation_log import (
    OperationLogResponse,
    OperationLogListResponse,
    OperationLogQuery,
    OperationLogStatistics
)
from app.services.operation_log_service import OperationLogService

# 创建路由器
router = APIRouter()


@router.get(
    "/logs",
    response_model=OperationLogListResponse,
    summary="获取操作日志列表",
    description="获取操作日志列表，支持分页和多条件筛选，仅管理员可访问"
)
async def get_operation_logs(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    username: Optional[str] = Query(None, description="按用户名筛选"),
    action_type: Optional[str] = Query(None, description="按行为类型筛选"),
    module: Optional[str] = Query(None, description="按模块筛选"),
    status: Optional[int] = Query(None, ge=0, le=1, description="按状态筛选"),
    start_date: Optional[str] = Query(None, description="开始时间（ISO格式）"),
    end_date: Optional[str] = Query(None, description="结束时间（ISO格式）"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    获取操作日志列表

    权限要求：仅管理员

    支持的分页参数：
    - skip: 跳过的记录数，默认0
    - limit: 返回的记录数，默认10，最大100

    支持的筛选参数：
    - username: 用户名（模糊搜索）
    - action_type: 行为类型（精确匹配）
    - module: 模块（精确匹配）
    - status: 状态（0=失败，1=成功）
    - start_date: 开始时间
    - end_date: 结束时间

    返回格式：
    ```json
    {
        "total": 100,
        "items": [...]
    }
    ```
    """
    from datetime import datetime

    # 构建查询对象
    query = None
    if any([username, action_type, module, status is not None, start_date, end_date]):
        query_data = {}
        if username:
            query_data["username"] = username
        if action_type:
            query_data["action_type"] = action_type
        if module:
            query_data["module"] = module
        if status is not None:
            query_data["status"] = status
        if start_date:
            try:
                query_data["start_date"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                pass
        if end_date:
            try:
                query_data["end_date"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                pass
        query = OperationLogQuery(**query_data)

    # 获取日志列表
    logs, total = OperationLogService.get_logs(db, skip=skip, limit=limit, query=query)

    # 转换为响应模型
    items = [OperationLogResponse.model_validate(log) for log in logs]

    return OperationLogListResponse(total=total, items=items)


@router.get(
    "/logs/{log_id}",
    response_model=OperationLogResponse,
    summary="获取操作日志详情",
    description="根据ID获取操作日志详情，仅管理员可访问"
)
async def get_operation_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    获取操作日志详情

    权限要求：仅管理员

    路径参数：
    - log_id: 日志ID

    返回指定ID的日志详细信息
    """
    log = OperationLogService.get_log_by_id(db, log_id)
    if not log:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志不存在"
        )
    return OperationLogResponse.model_validate(log)


@router.get(
    "/logs/statistics/summary",
    response_model=OperationLogStatistics,
    summary="获取操作日志统计",
    description="获取操作日志的统计信息，包括总数、今日数量、按类型/模块/用户统计，仅管理员可访问"
)
async def get_log_statistics(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    获取操作日志统计信息

    权限要求：仅管理员

    返回统计信息：
    - total_logs: 总日志数
    - today_logs: 今日日志数
    - action_type_stats: 按行为类型统计
    - module_stats: 按模块统计
    - user_stats: 按用户统计（前10名）
    """
    stats = OperationLogService.get_statistics(db)
    return OperationLogStatistics(**stats)


@router.get(
    "/logs/recent",
    response_model=list[OperationLogResponse],
    summary="获取最近操作日志",
    description="获取最近的操作日志，默认10条，仅管理员可访问"
)
async def get_recent_logs(
    limit: int = Query(10, ge=1, le=50, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    获取最近操作日志

    权限要求：仅管理员

    查询参数：
    - limit: 返回记录数，默认10，最大50

    返回最近的操作日志列表，按时间倒序排列
    """
    logs = OperationLogService.get_recent_logs(db, limit=limit)
    return [OperationLogResponse.model_validate(log) for log in logs]
