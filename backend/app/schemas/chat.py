"""
智能问答数据模型
"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., min_length=1, description="用户消息内容")
    session_id: str = Field(default="default", description="会话ID，用于保持多轮对话上下文")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str = Field(..., description="AI回复内容")
    session_id: str = Field(..., description="会话ID")
