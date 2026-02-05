"""
日志记录辅助函数
提供自动记录操作日志的工具函数
"""
from fastapi import Request
from sqlalchemy.orm import Session

from app.services.operation_log_service import OperationLogService


async def log_operation(
    db: Session,
    user_id: int,
    username: str,
    action_type: str,
    module: str,
    request: Request = None,
    status: int = 1,
    remark: str = None
):
    """
    记录操作日志的辅助函数

    自动从请求中提取 IP 地址和 User-Agent 信息

    Args:
        db: 数据库会话
        user_id: 操作用户ID
        username: 操作用户名
        action_type: 行为类型 (使用 OperationLogService 中的常量)
        module: 操作模块 (使用 OperationLogService 中的常量)
        request: FastAPI 请求对象（可选，用于提取 IP 和 User-Agent）
        status: 操作状态 (1=成功, 0=失败)
        remark: 备注信息

    Example:
        ```python
        # 在端点中使用
        @router.post("/login")
        async def login(
            request: Request,
            login_data: LoginRequest,
            db: Session = Depends(get_db)
        ):
            # ... 业务逻辑 ...

            # 记录登录日志
            await log_operation(
                db=db,
                user_id=user.id,
                username=user.username,
                action_type=OperationLogService.ACTION_LOGIN,
                module=OperationLogService.MODULE_AUTH,
                request=request,
                status=1,
                remark="用户登录成功"
            )
        ```
    """
    # 提取 IP 地址
    ip_address = None
    user_agent = None

    if request:
        # 尝试从各种请求头中获取真实 IP
        ip_address = (
            request.headers.get("X-Forwarded-For") or
            request.headers.get("X-Real-IP") or
            request.headers.get("CF-Connecting-IP") or
            getattr(request, "client", None)
        )
        if ip_address and hasattr(ip_address, "host"):
            ip_address = ip_address.host
        # 如果 X-Forwarded-For 包含多个 IP，取第一个
        if ip_address and "," in str(ip_address):
            ip_address = str(ip_address).split(",")[0].strip()

        # 获取 User-Agent
        user_agent = request.headers.get("User-Agent")

    # 创建日志记录（使用后台任务，不阻塞主流程）
    try:
        OperationLogService.create_log(
            db=db,
            user_id=user_id,
            username=username,
            action_type=action_type,
            module=module,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            remark=remark
        )
    except Exception as e:
        # 日志记录失败不应影响主业务流程
        import logging
        logging.getLogger(__name__).error(f"记录操作日志失败: {str(e)}")
