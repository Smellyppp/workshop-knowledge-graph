"""
Neo4j 数据库客户端
提供 Neo4j 图数据库的连接和基础操作
"""
from neo4j import GraphDatabase, AsyncGraphDatabase
from typing import Optional, Dict, Any, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j 数据库客户端（同步）"""

    def __init__(self):
        self._driver: Optional[GraphDatabase.driver] = None

    def connect(self) -> None:
        """建立数据库连接"""
        try:
            self._driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # 验证连接
            self._driver.verify_connectivity()
            logger.info("Neo4j 数据库连接成功")
        except Exception as e:
            logger.error(f"Neo4j 数据库连接失败: {e}")
            raise

    def close(self) -> None:
        """关闭数据库连接"""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j 数据库连接已关闭")

    def get_session(self):
        """获取数据库会话"""
        if not self._driver:
            try:
                self.connect()
            except Exception as e:
                logger.error(f"无法获取数据库会话: {e}")
                raise RuntimeError(f"Neo4j 连接失败: {e}")
        return self._driver.session(database=settings.NEO4J_DATABASE)

    def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        执行 Cypher 查询

        Args:
            query: Cypher 查询语句
            parameters: 查询参数

        Returns:
            查询结果列表
        """
        try:
            with self.get_session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise


class AsyncNeo4jClient:
    """Neo4j 数据库客户端（异步）"""

    def __init__(self):
        self._driver: Optional[AsyncGraphDatabase.driver] = None

    async def connect(self) -> None:
        """建立数据库连接"""
        try:
            self._driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            # 验证连接
            await self._driver.verify_connectivity()
            logger.info("Neo4j 异步数据库连接成功")
        except Exception as e:
            logger.error(f"Neo4j 异步数据库连接失败: {e}")
            raise

    async def close(self) -> None:
        """关闭数据库连接"""
        if self._driver:
            await self._driver.close()
            logger.info("Neo4j 异步数据库连接已关闭")

    def get_session(self):
        """获取数据库会话"""
        if not self._driver:
            raise RuntimeError("数据库未连接，请先调用 connect()")
        return self._driver.session(database=settings.NEO4J_DATABASE)

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        执行 Cypher 查询

        Args:
            query: Cypher 查询语句
            parameters: 查询参数

        Returns:
            查询结果列表
        """
        try:
            session = self.get_session()
            async with session:
                result = await session.run(query, parameters or {})
                records = await result.data()
                return records
        except Exception as e:
            logger.error(f"异步查询执行失败: {e}")
            raise


# 创建全局客户端实例
neo4j_client = Neo4jClient()
async_neo4j_client = AsyncNeo4jClient()
