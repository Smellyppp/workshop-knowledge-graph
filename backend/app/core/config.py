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

    # =========================
    # 数据库配置
    # =========================
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # =========================
    # JWT 配置
    # =========================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # =========================
    # Neo4j 配置
    # =========================
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    NEO4J_DATABASE: str

    # =========================
    # Qwen 大模型配置
    # =========================
    QWEN_API_URL: str
    QWEN_API_KEY: str
    QWEN_MODEL: str
    # 对话记忆轮数限制
    CHAT_MEMORY_LIMIT: int = 3

    # =========================
    # 前端配置
    # =========================
    FRONTEND_URL: str = "http://localhost:5173"

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
