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

    @staticmethod
    def search_all_nodes(keyword: str, limit: int = 100) -> Dict[str, Any]:
        """
        根据 title 字段搜索节点，并返回相关的关系数据

        Args:
            keyword: 关键词
            limit: 最大返回结果数

        Returns:
            包含节点和关系的字典
        """
        # 搜索匹配的节点，使用显式投影返回完整的节点信息
        search_query = """
        MATCH (n)
        WHERE toLower(toString(n.title)) CONTAINS toLower($keyword)
        RETURN elementId(n) as id, labels(n) as labels, properties(n) as properties
        LIMIT $limit
        """

        try:
            # 搜索节点
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

            # 获取这些节点之间的关系
            edges = []
            if node_ids:
                batch_size = 100
                for i in range(0, len(node_ids), batch_size):
                    batch = node_ids[i:i + batch_size]
                    rel_query = """
                    MATCH (a)-[r]-(b)
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

            logger.info(f"搜索 '{keyword}' 找到 {len(nodes)} 个节点, {len(edges)} 条关系")
            return {
                "nodes": nodes,
                "edges": edges
            }

        except Exception as e:
            logger.error(f"搜索节点失败: {e}")
            raise

    @staticmethod
    def get_node_neighbors(node_id: str, depth: int = 1) -> Dict[str, Any]:
        """
        获取指定节点的邻居节点和关系

        Args:
            node_id: 节点的 elementId
            depth: 扩展深度（默认为1，即直接邻居）

        Returns:
            包含邻居节点和关系的字典
        """
        try:
            # 查询指定节点的邻居
            neighbor_query = f"""
            MATCH (n)-[r]-(neighbor)
            WHERE elementId(n) = $node_id
            RETURN elementId(n) as center_id,
                   elementId(neighbor) as id,
                   labels(neighbor) as labels,
                   properties(neighbor) as properties,
                   elementId(r) as rel_id,
                   type(r) as rel_type,
                   startNode(r) as start_node,
                   endNode(r) as end_node
            """

            results = neo4j_client.execute_query(
                neighbor_query,
                {"node_id": node_id}
            )

            nodes = {}
            edges = []

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

                # 添加关系
                rel_id = record.get("rel_id")
                rel_type = record.get("rel_type", "")

                if rel_id is not None:
                    # 确定关系的方向
                    start_node = record.get("start_node")
                    end_node = record.get("end_node")

                    # Neo4j 返回的节点对象，需要提取 elementId
                    if start_node and end_node:
                        if isinstance(start_node, dict):
                            from_id = start_node.get("identity") or start_node.get("id")
                        else:
                            from_id = getattr(start_node, "id", None)

                        if isinstance(end_node, dict):
                            to_id = end_node.get("identity") or end_node.get("id")
                        else:
                            to_id = getattr(end_node, "id", None)

                        # 如果无法提取，使用节点ID
                        if not from_id or not to_id:
                            from_id = node_id
                            to_id = neighbor_id

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
            edges = []
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
            if node_ids:
                batch_size = 100
                for i in range(0, len(node_ids), batch_size):
                    batch = node_ids[i:i + batch_size]
                    rel_query = """
                    MATCH (a)-[r]-(b)
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
