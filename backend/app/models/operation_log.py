"""
操作日志数据库模型
用于记录用户的操作行为，包括时间、操作用户、行为类型等信息
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Index

from app.models.user import Base


class OperationLog(Base):
    """
    操作日志表模型
    记录用户在系统中的各种操作行为，便于审计和追踪
    """
    __tablename__ = "operation_log"

    # 主键：日志ID
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="日志ID")

    # 用户ID：关联操作用户
    user_id = Column(BigInteger, nullable=False, index=True, comment="操作用户ID")

    # 用户名：冗余字段，方便查询显示
    username = Column(String(50), nullable=False, index=True, comment="操作用户名")

    # 行为类型：定义操作类型
    # 常见类型：LOGIN, LOGOUT, QUERY, CREATE, UPDATE, DELETE, EXPORT, SEARCH 等
    action_type = Column(String(50), nullable=False, index=True, comment="行为类型")

    # 模块：操作所属的功能模块
    # 例如：用户管理、知识图谱、智能问答等
    module = Column(String(50), nullable=False, index=True, comment="操作模块")

    # IP地址：记录操作来源IP
    ip_address = Column(String(50), nullable=True, comment="操作IP地址")

    # 用户代理：记录客户端信息（浏览器、设备等）
    user_agent = Column(String(500), nullable=True, comment="用户代理信息")

    # 操作时间：记录操作发生的时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="操作时间")

    # 状态：操作是否成功
    # 1=成功，0=失败
    status = Column(Integer, nullable=False, default=1, comment="操作状态：1=成功，0=失败")

    # 备注信息：额外说明（可选）
    remark = Column(String(500), nullable=True, comment="备注信息")

    def to_dict(self):
        """
        将模型转换为字典
        用于API响应序列化
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "action_type": self.action_type,
            "module": self.module,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "status": self.status,
            "remark": self.remark
        }

    def __repr__(self):
        """模型的字符串表示"""
        return (
            f"<OperationLog(id={self.id}, user_id={self.user_id}, "
            f"username='{self.username}', action_type='{self.action_type}', "
            f"module='{self.module}', created_at={self.created_at})>"
        )

    __table_args__ = (
        # 创建复合索引：按用户ID和操作时间查询
        Index('idx_user_time', 'user_id', 'created_at'),
        # 创建复合索引：按模块和操作时间查询
        Index('idx_module_time', 'module', 'created_at'),
        # 创建复合索引：按行为类型和操作时间查询
        Index('idx_action_time', 'action_type', 'created_at'),
    )
