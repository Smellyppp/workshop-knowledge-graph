"""
智能问答接口
提供基于Qwen大模型的对话功能
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.models.user import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.services.operation_log_service import OperationLogService
from app.core.deps import get_current_user
from app.core.logger_helper import log_operation

# 创建路由器
router = APIRouter()

# 创建聊天服务实例
chat_service = ChatService()


@router.post("/message", response_model=ChatResponse, summary="发送消息")
async def send_message(
    req: Request,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    发送消息给AI助手

    - **message**: 用户消息内容
    - **session_id**: 会话ID（可选，用于保持多轮对话上下文）
    """
    response = await chat_service.chat(request.message, request.session_id)

    # 记录问答日志（不记录消息的具体内容）
    await log_operation(
        db=db,
        user_id=current_user.get("id"),
        username=current_user.get("username"),
        action_type=OperationLogService.ACTION_QUERY,
        module=OperationLogService.MODULE_CHAT,
        request=req,
        status=1,
        remark="发送消息给AI助手"
    )

    return ChatResponse(
        message=response["message"],
        session_id=response["session_id"]
    )


@router.post("/clear", summary="清除对话历史")
async def clear_history(
    req: Request,
    session_id: str = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    清除指定会话的对话历史

    - **session_id**: 会话ID（可选，不提供则清除默认会话）
    """
    chat_service.clear_history(session_id)

    # 记录清除对话历史日志
    await log_operation(
        db=db,
        user_id=current_user.get("id"),
        username=current_user.get("username"),
        action_type=OperationLogService.ACTION_DELETE,
        module=OperationLogService.MODULE_CHAT,
        request=req,
        status=1,
        remark="清除对话历史"
    )

    return {"message": "对话历史已清除"}
