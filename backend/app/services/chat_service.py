"""
智能问答服务
使用LangChain集成Qwen大模型，支持对话记忆
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from typing import Dict
import logging

from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


class ChatService:
    """智能问答服务类"""

    def __init__(self):
        """初始化聊天服务"""
        # 初始化Qwen模型 (使用ChatOpenAI兼容接口)
        self.llm = ChatOpenAI(
            model=settings.QWEN_MODEL,
            api_key=settings.QWEN_API_KEY,
            base_url=settings.QWEN_API_URL,
            temperature=0.7
        )

        # 系统提示词
        self.system_prompt = """你是一个专业的车间故障诊断助手，基于知识图谱帮助用户解决车间设备故障问题。

你的职责：
1. 根据用户的故障描述，提供专业的诊断建议
2. 帮助用户分析故障原因和解决方案
3. 提供操作指导和预防措施
4. 如果需要更详细的信息，可以建议用户使用知识图谱进行可视化查询

请用简洁、专业的语言回答，注重实用性。"""

        # 创建提示模板
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # 创建对话链
        self.chain = self.prompt | self.llm

        # 对话历史存储（生产环境建议使用Redis）
        self.histories: Dict[str, InMemoryChatMessageHistory] = {}

        # 记忆轮数限制
        self.memory_limit = 3

    def _get_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """获取或创建对话历史"""
        if session_id not in self.histories:
            self.histories[session_id] = InMemoryChatMessageHistory()
        return self.histories[session_id]

    async def chat(self, message: str, session_id: str = "default") -> dict:
        """
        处理用户消息

        Args:
            message: 用户消息
            session_id: 会话ID

        Returns:
            包含AI回复和会话ID的字典
        """
        try:
            # 获取对话历史
            history = self._get_history(session_id)

            # 限制历史记录为最近3轮
            self._limit_history(history)

            # 构建输入
            input_data = {
                "input": message,
                "history": history.messages
            }

            # 调用模型
            response = await self.chain.ainvoke(input_data)

            # 获取响应内容
            response_content = response.content if hasattr(response, 'content') else str(response)

            # 验证响应不为空
            if not response_content or response_content.strip() == "":
                raise ValueError("AI响应为空")

            # 更新历史记录
            history.add_message(HumanMessage(content=message))
            history.add_message(AIMessage(content=response_content))

            return {
                "message": response_content,
                "session_id": session_id
            }

        except Exception as e:
            logger.error(f"聊天服务异常: {str(e)}", exc_info=True)
            # 返回友好的错误消息
            return {
                "message": f"抱歉，服务暂时不可用：{str(e)}",
                "session_id": session_id
            }

    def _limit_history(self, history: InMemoryChatMessageHistory) -> None:
        """
        限制对话历史为最近3轮（6条消息：3个用户消息 + 3个AI消息）

        Args:
            history: 对话历史对象
        """
        messages = history.messages

        # 如果超过3轮对话（6条消息），保留最近的3轮
        if len(messages) > self.memory_limit * 2:
            # 清空历史并保留最近的消息
            recent_messages = messages[-self.memory_limit * 2:]
            history.clear()
            for msg in recent_messages:
                history.add_message(msg)

    def clear_history(self, session_id: str = None) -> None:
        """
        清除对话历史

        Args:
            session_id: 会话ID，如果为None则清除默认会话
        """
        if session_id is None:
            session_id = "default"

        if session_id in self.histories:
            del self.histories[session_id]
