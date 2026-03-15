"""
数据库基类和会话配置
提供 SQLAlchemy Base 声明、引擎和会话管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 声明基类
Base = declarative_base()

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 检测连接是否有效
    pool_recycle=3600,   # 1小时后回收连接
    echo=False           # 生产环境关闭SQL日志
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    数据库会话依赖注入函数

    用于 FastAPI 依赖注入，自动管理会话生命周期
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
