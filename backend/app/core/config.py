"""
应用程序配置模块
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # 数据库配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "workshop"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-in-production"  # 生产环境请修改
    ALGORITHM: str = "HS256"  # JWT 加密算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 访问令牌有效期（24小时）

    # Neo4j 配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "1314520gyf"
    NEO4J_DATABASE: str = "neo4j"

    @property
    def DATABASE_URL(self) -> str:
        """生成数据库连接 URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"  # 环境变量文件


# 创建全局配置实例
settings = Settings()
