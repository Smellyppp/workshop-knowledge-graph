"""
用户数据库模型
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 声明基类
Base = declarative_base()

# 创建数据库引擎
engine = create_engine(settings.DATABASE_URL)
# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UserManage(Base):
    """用户管理表模型"""
    __tablename__ = "user_manage"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="用户ID")
    user_type = Column(Integer, nullable=False, default=0, comment="用户类型：1=管理员，0=普通用户")
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    password = Column(String(255), nullable=False, comment="加密后的密码")
    status = Column(Integer, nullable=False, default=1, comment="状态：1=启用，0=禁用")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

    def to_dict(self):
        """将模型转换为字典"""
        return {
            "id": self.id,
            "user_type": self.user_type,
            "username": self.username,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


def get_db():
    """数据库会话依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
