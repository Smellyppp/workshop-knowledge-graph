"""
应用程序配置模块
"""
from pydantic_settings import BaseSettings
from pathlib import Path


# 获取项目根目录（backend目录）
# config.py 在 backend/app/core/ 下，需要往上3层到 backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent


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

    # Qwen 大模型配置
    # 注意：QWEN_API_KEY 需要在 .env 文件中配置，不要在此处显示
    QWEN_API_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    QWEN_API_KEY: str  # 从环境变量读取
    QWEN_MODEL: str = "qwen-plus"
    # 对话记忆轮数限制
    CHAT_MEMORY_LIMIT: int = 3

    @property
    def DATABASE_URL(self) -> str:
        """生成数据库连接 URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        # 使用绝对路径，确保从任何目录运行都能找到 .env 文件
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


# 创建全局配置实例
settings = Settings()
