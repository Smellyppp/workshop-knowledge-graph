"""
知识图谱相关的数据模型和 Schema 定义
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class Neo4jNode(BaseModel):
    """Neo4j 节点"""
    id: int
    labels: List[str]
    properties: Dict[str, Any]

    class Config:
        from_attributes = True


class Relationship(BaseModel):
    """关系"""
    id: int
    from_node: int
    to_node: int
    type: str


class GraphDataResponse(BaseModel):
    """图谱数据响应"""
    nodes: List[Neo4jNode]
    edges: List[Relationship]


class GraphStatistics(BaseModel):
    """图谱统计信息"""
    node_count: Optional[int] = None
    relationship_count: Optional[int] = None
    labels: Optional[List[str]] = None
    relationship_types: Optional[List[str]] = None
    connected: Optional[bool] = None
    error: Optional[str] = None
