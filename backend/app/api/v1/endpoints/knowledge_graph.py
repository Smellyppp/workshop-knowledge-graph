"""
知识图谱 API 接口
提供知识图谱关键词检索和可视化功能
"""
from fastapi import APIRouter, HTTPException, status, Query, Request, Depends
from sqlalchemy.orm import Session

from app.models.user import get_db
from app.schemas.knowledge_graph import (
    GraphDataResponse,
    GraphStatistics
)
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.operation_log_service import OperationLogService
from app.core.deps import get_current_user
from app.core.logger_helper import log_operation

# 创建路由器
router = APIRouter()


@router.get("/statistics", response_model=GraphStatistics, summary="获取图谱统计信息")
async def get_statistics():
    """
    获取知识图谱的统计信息

    Returns:
        GraphStatistics: 统计信息
    """
    try:
        stats = KnowledgeGraphService.get_graph_statistics()
        return GraphStatistics(**stats)
    except Exception as e:
        # 即使出错也返回基本的统计结构
        return GraphStatistics(
            node_count=None,
            relationship_count=None,
            labels=[],
            relationship_types=[]
        )


@router.post("/search", summary="关键词搜索")
async def search_nodes(
    request: Request,
    keyword: str = Query(..., description="搜索关键词", min_length=1),
    limit: int = Query(100, ge=1, le=1000, description="最大返回结果数"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    根据 title 字段搜索节点，返回节点和关系用于可视化

    Args:
        keyword: 搜索关键词
        limit: 最大返回节点数

    Returns:
        包含节点和关系的数据
    """
    try:
        result = KnowledgeGraphService.search_all_nodes(
            keyword=keyword,
            limit=limit
        )

        # 记录搜索日志（不记录搜索的具体内容）
        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type=OperationLogService.ACTION_SEARCH,
            module=OperationLogService.MODULE_KNOWLEDGE_GRAPH,
            request=request,
            status=1,
            remark="执行关键词搜索"
        )

        return result

    except Exception as e:
        # 记录搜索失败日志
        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type=OperationLogService.ACTION_SEARCH,
            module=OperationLogService.MODULE_KNOWLEDGE_GRAPH,
            request=request,
            status=0,
            remark=f"搜索失败: {str(e)}"
        )

        import traceback
        import logging
        logging.error(f"搜索失败详细错误: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}"
        )


@router.get("/graph-data", summary="获取图谱数据用于可视化")
async def get_graph_data(
    request: Request,
    limit: int = Query(100, ge=1, le=1000, description="最大节点数"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取图谱数据（节点和关系）用于可视化展示

    Args:
        limit: 最大返回节点数

    Returns:
        包含节点和关系的数据
    """
    try:
        data = KnowledgeGraphService.get_graph_data(limit=limit)

        # 记录查询日志
        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type=OperationLogService.ACTION_QUERY,
            module=OperationLogService.MODULE_KNOWLEDGE_GRAPH,
            request=request,
            status=1,
            remark=f"获取图谱数据，限制: {limit}"
        )

        return data
    except Exception as e:
        import traceback
        import logging
        logging.error(f"获取图谱数据失败: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取图谱数据失败: {str(e)}"
        )


@router.get("/health", summary="知识图谱模块健康检查")
def health_check():
    """检查 Neo4j 连接状态"""
    try:
        stats = KnowledgeGraphService.get_graph_statistics()
        return {
            "status": "healthy" if stats.get("connected") else "unhealthy",
            "neo4j_connected": stats.get("connected", False),
            "details": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "neo4j_connected": False,
            "error": str(e)
        }


@router.get("/neighbors/{node_id}", summary="获取节点的邻居")
async def get_node_neighbors(
    request: Request,
    node_id: str,
    depth: int = Query(1, ge=1, le=3, description="扩展深度"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取指定节点的邻居节点和关系，用于点击展开

    Args:
        node_id: 节点的 elementId
        depth: 扩展深度（1-3，默认为1）

    Returns:
        包含邻居节点和关系的数据
    """
    try:
        result = KnowledgeGraphService.get_node_neighbors(
            node_id=node_id,
            depth=depth
        )

        # 记录查询日志
        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type=OperationLogService.ACTION_QUERY,
            module=OperationLogService.MODULE_KNOWLEDGE_GRAPH,
            request=request,
            status=1,
            remark=f"获取节点邻居，节点ID: {node_id}"
        )

        return result
    except Exception as e:
        import traceback
        import logging
        logging.error(f"获取节点邻居失败: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取节点邻居失败: {str(e)}"
        )
