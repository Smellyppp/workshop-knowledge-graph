"""
操作日志服务
提供日志记录、查询、统计等功能
"""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc

from app.models.operation_log import OperationLog
from app.schemas.operation_log import OperationLogCreate, OperationLogQuery


class OperationLogService:
    """
    操作日志服务类
    封装所有与操作日志相关的业务逻辑
    """

    # 行为类型枚举
    ACTION_LOGIN = "LOGIN"
    ACTION_LOGOUT = "LOGOUT"
    ACTION_QUERY = "QUERY"
    ACTION_CREATE = "CREATE"
    ACTION_UPDATE = "UPDATE"
    ACTION_DELETE = "DELETE"
    ACTION_EXPORT = "EXPORT"
    ACTION_SEARCH = "SEARCH"

    # 模块枚举
    MODULE_AUTH = "认证"
    MODULE_USER_MANAGEMENT = "用户管理"
    MODULE_KNOWLEDGE_GRAPH = "知识图谱"
    MODULE_CHAT = "智能问答"
    MODULE_SYSTEM = "系统"

    @staticmethod
    def create_log(
        db: Session,
        user_id: int,
        username: str,
        action_type: str,
        module: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: int = 1,
        remark: Optional[str] = None
    ) -> OperationLog:
        """
        创建操作日志记录

        Args:
            db: 数据库会话
            user_id: 操作用户ID
            username: 操作用户名
            action_type: 行为类型
            module: 操作模块
            ip_address: 操作IP地址
            user_agent: 用户代理信息
            status: 操作状态（1=成功，0=失败）
            remark: 备注信息

        Returns:
            OperationLog: 创建的日志对象
        """
        log = OperationLog(
            user_id=user_id,
            username=username,
            action_type=action_type,
            module=module,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            remark=remark
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def create_log_from_schema(
        db: Session,
        log_data: OperationLogCreate
    ) -> OperationLog:
        """
        从 Schema 创建操作日志记录

        Args:
            db: 数据库会话
            log_data: 日志创建数据

        Returns:
            OperationLog: 创建的日志对象
        """
        return OperationLogService.create_log(
            db=db,
            user_id=log_data.user_id,
            username=log_data.username,
            action_type=log_data.action_type,
            module=log_data.module,
            ip_address=log_data.ip_address,
            user_agent=log_data.user_agent,
            status=log_data.status,
            remark=log_data.remark
        )

    @staticmethod
    def get_logs(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        query: Optional[OperationLogQuery] = None
    ) -> tuple[List[OperationLog], int]:
        """
        获取操作日志列表（支持分页和筛选）

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            query: 查询条件

        Returns:
            tuple: (日志列表, 总记录数)
        """
        # 构建查询
        q = db.query(OperationLog)

        # 应用筛选条件
        if query:
            filters = []

            # 按用户名筛选
            if query.username:
                filters.append(OperationLog.username.like(f"%{query.username}%"))

            # 按行为类型筛选
            if query.action_type:
                filters.append(OperationLog.action_type == query.action_type)

            # 按模块筛选
            if query.module:
                filters.append(OperationLog.module == query.module)

            # 按状态筛选
            if query.status is not None:
                filters.append(OperationLog.status == query.status)

            # 按时间范围筛选
            if query.start_date:
                filters.append(OperationLog.created_at >= query.start_date)
            if query.end_date:
                filters.append(OperationLog.created_at <= query.end_date)

            # 应用所有筛选条件
            if filters:
                q = q.filter(and_(*filters))

        # 获取总数
        total = q.count()

        # 分页查询，按时间倒序排列
        logs = q.order_by(desc(OperationLog.created_at)).offset(skip).limit(limit).all()

        return logs, total

    @staticmethod
    def get_log_by_id(db: Session, log_id: int) -> Optional[OperationLog]:
        """
        根据 ID 获取操作日志

        Args:
            db: 数据库会话
            log_id: 日志ID

        Returns:
            Optional[OperationLog]: 日志对象，不存在则返回 None
        """
        return db.query(OperationLog).filter(OperationLog.id == log_id).first()

    @staticmethod
    def get_statistics(db: Session) -> Dict:
        """
        获取操作日志统计信息

        Args:
            db: 数据库会话

        Returns:
            dict: 统计信息字典
        """
        # 总日志数
        total_logs = db.query(func.count(OperationLog.id)).scalar()

        # 今日日志数
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_logs = db.query(func.count(OperationLog.id)).filter(
            OperationLog.created_at >= today_start
        ).scalar()

        # 按行为类型统计
        action_type_stats = {}
        action_type_results = db.query(
            OperationLog.action_type,
            func.count(OperationLog.id)
        ).group_by(OperationLog.action_type).all()
        for action_type, count in action_type_results:
            action_type_stats[action_type] = count

        # 按模块统计
        module_stats = {}
        module_results = db.query(
            OperationLog.module,
            func.count(OperationLog.id)
        ).group_by(OperationLog.module).all()
        for module, count in module_results:
            module_stats[module] = count

        # 按用户统计（前10名）
        user_stats = {}
        user_results = db.query(
            OperationLog.username,
            func.count(OperationLog.id)
        ).group_by(OperationLog.username).order_by(
            desc(func.count(OperationLog.id))
        ).limit(10).all()
        for username, count in user_results:
            user_stats[username] = count

        return {
            "total_logs": total_logs or 0,
            "today_logs": today_logs or 0,
            "action_type_stats": action_type_stats,
            "module_stats": module_stats,
            "user_stats": user_stats
        }

    @staticmethod
    def get_user_logs(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> tuple[List[OperationLog], int]:
        """
        获取指定用户的操作日志

        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过记录数
            limit: 返回记录数

        Returns:
            tuple: (日志列表, 总记录数)
        """
        q = db.query(OperationLog).filter(OperationLog.user_id == user_id)
        total = q.count()
        logs = q.order_by(desc(OperationLog.created_at)).offset(skip).limit(limit).all()
        return logs, total

    @staticmethod
    def get_recent_logs(
        db: Session,
        limit: int = 10
    ) -> List[OperationLog]:
        """
        获取最近的操作日志

        Args:
            db: 数据库会话
            limit: 返回记录数

        Returns:
            list: 日志列表
        """
        return db.query(OperationLog).order_by(
            desc(OperationLog.created_at)
        ).limit(limit).all()

    @staticmethod
    def delete_old_logs(db: Session, days: int = 90) -> int:
        """
        删除指定天数之前的旧日志

        Args:
            db: 数据库会话
            days: 保留天数，默认90天

        Returns:
            int: 删除的记录数
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted = db.query(OperationLog).filter(
            OperationLog.created_at < cutoff_date
        ).delete()
        db.commit()
        return deleted
