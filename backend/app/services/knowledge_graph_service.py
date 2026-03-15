"""
知识图谱服务
提供知识图谱的关键词检索和可视化数据获取功能
"""
from typing import Dict, Any, List
from app.core.neo4j_client import neo4j_client
import logging

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """知识图谱服务类"""

    # 宽松模式：搜索所有节点属性，不再限制特定字段
    # 任何包含关键词的属性都会被匹配（包括维护周期、出厂日期等）

    @staticmethod
    def search_all_nodes(keyword: str, limit: int = 100) -> Dict[str, Any]:
        """
        宽松模式：搜索节点的所有属性字段

        任何属性包含关键词的节点都会被返回
        例如：搜索"10天"可以找到维护周期为10天的设备

        Args:
            keyword: 关键词
            limit: 最大返回结果数

        Returns:
            包含节点和关系的字典
        """
        if not keyword or not keyword.strip():
            return {"nodes": [], "edges": []}

        keyword = keyword.strip()

        try:
            nodes, node_ids = KnowledgeGraphService._search_by_multiple_fields(keyword, limit)

            # 获取这些节点之间的关系
            edges = []
            if node_ids:
                edges = KnowledgeGraphService._get_relations_between_nodes(node_ids)

            logger.info(f"搜索 '{keyword}' 找到 {len(nodes)} 个节点, {len(edges)} 条关系")
            return {
                "nodes": nodes,
                "edges": edges
            }

        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return {"nodes": [], "edges": []}

    @staticmethod
    def _search_by_multiple_fields(keyword: str, limit: int) -> tuple:
        """
        宽松模式：搜索节点的所有属性字段
        不再限制特定字段，任何属性包含关键词都会被匹配

        Returns:
            tuple: (节点列表, 节点ID列表)
        """
        # 宽松模式：搜索所有属性字段
        # 使用 any() + WHERE 语法检查节点的任何属性是否包含关键词
        search_query = """
        MATCH (n)
        WHERE any(key IN keys(n) WHERE toString(n[key]) CONTAINS $keyword)
        RETURN elementId(n) as id, labels(n) as labels, properties(n) as properties
        LIMIT $limit
        """

        results = neo4j_client.execute_query(
            search_query,
            {"keyword": keyword, "limit": limit}
        )

        nodes = []
        node_ids = []

        for record in results:
            node_id = record.get("id")
            node_labels = record.get("labels", [])
            node_properties = record.get("properties", {})

            if node_id is not None:
                node_ids.append(node_id)
                nodes.append({
                    "id": node_id,
                    "labels": node_labels if isinstance(node_labels, list) else [],
                    "properties": node_properties if isinstance(node_properties, dict) else {}
                })

        return nodes, node_ids

    @staticmethod
    def _get_relations_between_nodes(node_ids: list) -> list:
        """
        获取指定节点列表之间的关系（保留方向）

        使用有向模式 (a)-[r]->(b) 确保从头实体指向尾实体

        Args:
            node_ids: 节点ID列表

        Returns:
            list: 关系列表
        """
        edges = []
        batch_size = 100

        for i in range(0, len(node_ids), batch_size):
            batch = node_ids[i:i + batch_size]
            # 使用有向关系模式，并直接在 Cypher 中获取起始和结束节点的 elementId
            rel_query = """
            MATCH (a)-[r]->(b)
            WHERE elementId(a) IN $node_ids AND elementId(b) IN $node_ids
            RETURN elementId(a) as from_node, elementId(b) as to_node, type(r) as type, elementId(r) as rel_id
            """

            rel_results = neo4j_client.execute_query(rel_query, {"node_ids": batch})
            for rel_record in rel_results:
                from_id = rel_record.get("from_node")
                to_id = rel_record.get("to_node")
                rel_id = rel_record.get("rel_id")
                rel_type = rel_record.get("type", "")

                if from_id and to_id and rel_id is not None:
                    edges.append({
                        "id": rel_id,
                        "from_node": from_id,
                        "to_node": to_id,
                        "type": rel_type
                    })

        return edges

    @staticmethod
    def get_node_neighbors(node_id: str, depth: int = 1) -> Dict[str, Any]:
        """
        获取指定节点的邻居节点和关系（保留方向）

        Args:
            node_id: 节点的 elementId
            depth: 扩展深度（默认为1，即直接邻居）

        Returns:
            包含邻居节点和关系的字典
        """
        try:
            # 使用有向关系模式查询邻居，同时获取出边和入边
            # 查询出边：中心节点 -> 邻居
            outgoing_query = """
            MATCH (n)-[r]->(neighbor)
            WHERE elementId(n) = $node_id
            RETURN elementId(n) as center_id,
                   elementId(neighbor) as id,
                   labels(neighbor) as labels,
                   properties(neighbor) as properties,
                   elementId(r) as rel_id,
                   type(r) as rel_type,
                   elementId(n) as from_node,
                   elementId(neighbor) as to_node
            """

            # 查询入边：邻居 -> 中心节点
            incoming_query = """
            MATCH (neighbor)-[r]->(n)
            WHERE elementId(n) = $node_id
            RETURN elementId(n) as center_id,
                   elementId(neighbor) as id,
                   labels(neighbor) as labels,
                   properties(neighbor) as properties,
                   elementId(r) as rel_id,
                   type(r) as rel_type,
                   elementId(neighbor) as from_node,
                   elementId(n) as to_node
            """

            nodes = {}
            edges = []

            # 处理出边
            results = neo4j_client.execute_query(outgoing_query, {"node_id": node_id})
            for record in results:
                neighbor_id = record.get("id")
                neighbor_labels = record.get("labels", [])
                neighbor_properties = record.get("properties", {})

                if neighbor_id and neighbor_id not in nodes:
                    nodes[neighbor_id] = {
                        "id": neighbor_id,
                        "labels": neighbor_labels if isinstance(neighbor_labels, list) else [],
                        "properties": neighbor_properties if isinstance(neighbor_properties, dict) else {}
                    }

                rel_id = record.get("rel_id")
                rel_type = record.get("rel_type", "")
                from_id = record.get("from_node")
                to_id = record.get("to_node")

                if rel_id is not None and from_id and to_id:
                    edges.append({
                        "id": rel_id,
                        "from_node": from_id,
                        "to_node": to_id,
                        "type": rel_type
                    })

            # 处理入边
            results = neo4j_client.execute_query(incoming_query, {"node_id": node_id})
            for record in results:
                neighbor_id = record.get("id")
                neighbor_labels = record.get("labels", [])
                neighbor_properties = record.get("properties", {})

                if neighbor_id and neighbor_id not in nodes:
                    nodes[neighbor_id] = {
                        "id": neighbor_id,
                        "labels": neighbor_labels if isinstance(neighbor_labels, list) else [],
                        "properties": neighbor_properties if isinstance(neighbor_properties, dict) else {}
                    }

                rel_id = record.get("rel_id")
                rel_type = record.get("rel_type", "")
                from_id = record.get("from_node")
                to_id = record.get("to_node")

                if rel_id is not None and from_id and to_id:
                    edges.append({
                        "id": rel_id,
                        "from_node": from_id,
                        "to_node": to_id,
                        "type": rel_type
                    })

            logger.info(f"节点 {node_id} 的邻居: {len(nodes)} 个节点, {len(edges)} 条关系")
            return {
                "nodes": list(nodes.values()),
                "edges": edges
            }

        except Exception as e:
            logger.error(f"获取节点邻居失败: {e}")
            raise

    @staticmethod
    def get_graph_data(limit: int = 100) -> Dict[str, Any]:
        """
        获取图谱数据（节点和关系）用于可视化

        Args:
            limit: 最大返回节点数

        Returns:
            包含节点和关系的字典
        """
        # 获取节点，使用显式投影返回完整的节点信息
        nodes_query = """
        MATCH (n)
        RETURN elementId(n) as id, labels(n) as labels, properties(n) as properties
        LIMIT $limit
        """

        try:
            # 获取节点
            results = neo4j_client.execute_query(nodes_query, {"limit": limit})

            nodes = []
            node_ids = []

            for record in results:
                node_id = record.get("id")
                node_labels = record.get("labels", [])
                node_properties = record.get("properties", {})

                if node_id is not None:
                    node_ids.append(node_id)
                    nodes.append({
                        "id": node_id,
                        "labels": node_labels if isinstance(node_labels, list) else [],
                        "properties": node_properties if isinstance(node_properties, dict) else {}
                    })

            # 获取这些节点之间的关系
            edges = KnowledgeGraphService._get_relations_between_nodes(node_ids)

            logger.info(f"获取图谱数据成功: {len(nodes)} 个节点, {len(edges)} 条关系")
            return {
                "nodes": nodes,
                "edges": edges
            }

        except Exception as e:
            logger.error(f"获取图谱数据失败: {e}")
            raise

    @staticmethod
    def get_graph_statistics() -> Dict[str, Any]:
        """
        获取图谱统计信息

        Returns:
            包含节点数、关系数等统计信息
        """
        stats = {
            "node_count": None,
            "relationship_count": None,
            "labels": [],
            "relationship_types": [],
            "connected": False
        }

        try:
            # 尝试连接并查询
            results = neo4j_client.execute_query("MATCH (n) RETURN count(n) as count")
            if results:
                stats["node_count"] = results[0].get("count")
                stats["connected"] = True

            results = neo4j_client.execute_query("MATCH ()-[r]->() RETURN count(r) as count")
            if results:
                stats["relationship_count"] = results[0].get("count")

            results = neo4j_client.execute_query("CALL db.labels() YIELD label RETURN collect(label) as labels")
            if results:
                stats["labels"] = results[0].get("labels", [])

            results = neo4j_client.execute_query("CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types")
            if results:
                stats["relationship_types"] = results[0].get("types", [])

        except Exception as e:
            logger.warning(f"获取统计信息失败: {e}")
            stats["connected"] = False
            stats["error"] = str(e)

        return stats
