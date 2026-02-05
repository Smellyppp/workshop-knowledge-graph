"""
知识图谱 API 接口
提供知识图谱关键词检索和可视化功能
"""
from fastapi import APIRouter, HTTPException, status, Query
from app.schemas.knowledge_graph import (
    GraphDataResponse,
    GraphStatistics
)
from app.services.knowledge_graph_service import KnowledgeGraphService

# 创建路由器
router = APIRouter()


@router.get("/statistics", response_model=GraphStatistics, summary="获取图谱统计信息")
def get_statistics():
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
def search_nodes(
    keyword: str = Query(..., description="搜索关键词", min_length=1),
    limit: int = Query(100, ge=1, le=1000, description="最大返回结果数")
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
        return result

    except Exception as e:
        import traceback
        import logging
        logging.error(f"搜索失败详细错误: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索失败: {str(e)}"
        )


@router.get("/graph-data", summary="获取图谱数据用于可视化")
def get_graph_data(
    limit: int = Query(100, ge=1, le=1000, description="最大节点数")
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
def get_node_neighbors(
    node_id: str,
    depth: int = Query(1, ge=1, le=3, description="扩展深度")
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
        return result
    except Exception as e:
        import traceback
        import logging
        logging.error(f"获取节点邻居失败: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取节点邻居失败: {str(e)}"
        )
