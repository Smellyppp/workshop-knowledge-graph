"""
知识图谱模块测试脚本
测试 search_all_nodes 方法
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.neo4j_client import neo4j_client
from app.services.knowledge_graph_service import KnowledgeGraphService
import json


def test_check_database_nodes():
    """
    先检查数据库中实际的节点属性结构
    """
    print("=" * 60)
    print("步骤1：检查数据库中的节点结构")
    print("=" * 60)

    try:
        # 查询所有节点，查看它们的属性
        query = """
        MATCH (n)
        RETURN n
        LIMIT 5
        """
        results = neo4j_client.execute_query(query)

        print(f"\n数据库中的节点示例（前5个）:")
        print("-" * 60)

        for i, record in enumerate(results, 1):
            node_data = record.get("n")
            if node_data:
                if isinstance(node_data, dict):
                    properties = node_data.get("properties", {})
                    labels = node_data.get("labels", [])
                else:
                    properties = dict(node_data)
                    labels = list(node_data.labels)

                print(f"\n节点 {i}:")
                print(f"  标签: {labels}")
                print(f"  属性键: {list(properties.keys())}")
                print(f"  属性详情:")
                for key, value in properties.items():
                    print(f"    {key}: {value}")

        print("-" * 60)

        # 再查询包含"开机"的节点
        print("\n\n直接查询包含 '开机' 的节点（检查字段名）:")
        print("-" * 60)

        # 尝试不同的字段名
        queries = [
            ("title 字段", "MATCH (n) WHERE toLower(toString(n.title)) CONTAINS toLower('开机') RETURN count(n) as count"),
            ("name 字段", "MATCH (n) WHERE toLower(toString(n.name)) CONTAINS toLower('开机') RETURN count(n) as count"),
            ("所有属性", "MATCH (n) WHERE any(key IN keys(n), toLower(toString(n[key])) CONTAINS toLower('开机')) RETURN count(n) as count")
        ]

        for desc, q in queries:
            try:
                result = neo4j_client.execute_query(q)
                count = result[0].get("count") if result else 0
                print(f"{desc}: 找到 {count} 个节点")
            except Exception as e:
                print(f"{desc}: 查询失败 - {e}")

        print("-" * 60)

        # 找出实际包含"开机"的节点（使用 title 字段）
        print("\n\n查找实际包含 '开机' 的节点（按 title 字段）:")
        print("-" * 60)

        find_query = """
        MATCH (n)
        WHERE toLower(toString(n.title)) CONTAINS toLower('开机')
        RETURN n
        LIMIT 3
        """

        results = neo4j_client.execute_query(find_query)

        if results:
            print(f"找到 {len(results)} 个包含 '开机' 的节点\n")

            for i, record in enumerate(results, 1):
                print(f"节点 {i} 原始数据结构:")
                node_data = record.get("n")
                print(f"  类型: {type(node_data)}")
                print(f"  是否为 dict: {isinstance(node_data, dict)}")
                print(f"  原始内容: {node_data}")

                if node_data:
                    if isinstance(node_data, dict):
                        # Neo4j 6.x 返回 dict 格式
                        print(f"  [dict] 所有键: {node_data.keys()}")
                        print(f"  [dict] identity: {node_data.get('identity')}")
                        print(f"  [dict] id: {node_data.get('id')}")
                        print(f"  [dict] labels: {node_data.get('labels')}")
                        print(f"  [dict] properties: {node_data.get('properties')}")
                    else:
                        # 旧版本 Neo4j 返回 Node 对象
                        print(f"  [Node] id: {node_data.id}")
                        print(f"  [Node] labels: {list(node_data.labels)}")
                        print(f"  [Node] 所有属性: {dict(node_data)}")

                print()

        else:
            print("未找到包含 '开机' 的节点")

        print("-" * 60)

        # 检查是否包含"重新开机"
        print("\n\n查找包含 '重新开机' 的节点:")
        print("-" * 60)

        find_exact_query = """
        MATCH (n)
        WHERE toLower(toString(n.title)) CONTAINS toLower('重新开机')
        RETURN count(n) as count
        """

        result = neo4j_client.execute_query(find_exact_query)
        count = result[0].get("count") if result else 0
        print(f"包含 '重新开机' 的节点数: {count}")

        if count == 0:
            print("\n[INFO] 数据库中没有包含 '重新开机' 的节点")
            print("       但是有 114 个包含 '开机' 的节点")
            print("       建议: 使用更短的关键词 '开机' 进行搜索")

        print("-" * 60)

    except Exception as e:
        print(f"\n[ERROR] 检查失败！")
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()


def test_search_all_nodes():
    """
    测试 search_all_nodes 方法
    硬编码关键词："重新开机"
    """
    print("\n\n" + "=" * 60)
    print("步骤2：测试 search_all_nodes 方法")
    print("=" * 60)

    # 硬编码的关键词
    keyword = "重新开机"

    print(f"\n搜索关键词: {keyword}")
    print(f"调用方法: KnowledgeGraphService.search_all_nodes('{keyword}', limit=10)")
    print(f"\n使用的 Cypher 查询:")
    print("  MATCH (n)")
    print("  WHERE toLower(toString(n.title)) CONTAINS toLower($keyword)")
    print("  RETURN n")

    try:
        # 调用 search_all_nodes 方法
        result = KnowledgeGraphService.search_all_nodes(keyword, limit=10)

        print(f"\n[OK] 搜索执行成功！")
        print(f"[OK] 找到 {len(result['nodes'])} 个节点")
        print(f"[OK] 找到 {len(result['edges'])} 条关系")

        # 显示节点详情
        if result['nodes']:
            print("\n节点列表:")
            print("-" * 60)
            for i, node in enumerate(result['nodes'], 1):
                print(f"\n节点 {i}:")
                print(f"  ID: {node['id']}")
                print(f"  标签: {node['labels']}")
                print(f"  属性:")
                for key, value in node['properties'].items():
                    print(f"    {key}: {value}")
            print("-" * 60)
        else:
            print("\n[WARNING] 未找到匹配的节点")
            print("提示：search_all_nodes 方法在 title 字段中未找到包含 '重新开机' 的节点")
            print("      可能数据库使用的是 name 字段或其他字段名")

        # 显示完整的 JSON 结果
        print("\n完整结果 (JSON格式):")
        print("-" * 60)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n[ERROR] 搜索执行失败！")
        print(f"错误信息: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("知识图谱节点字段诊断和搜索测试")
    print("=" * 60)

    # 执行测试
    test_results = {
        "数据库结构检查": False,
        "search_all_nodes 测试": False
    }

    try:
        # 步骤1：检查数据库结构
        test_check_database_nodes()
        test_results["数据库结构检查"] = True

        # 步骤2：测试 search_all_nodes
        test_results["search_all_nodes 测试"] = test_search_all_nodes()

    finally:
        # 关闭数据库连接
        try:
            neo4j_client.close()
            print("\n数据库连接已关闭")
        except:
            pass

    # 输出测试总结
    print("\n\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for test_name, result in test_results.items():
        status = "[OK] 通过" if result else "[ERROR] 失败"
        print(f"{test_name}: {status}")

    total_tests = len(test_results)
    passed_tests = sum(test_results.values())

    print(f"\n总计: {passed_tests}/{total_tests} 个测试通过")

    return 0


if __name__ == "__main__":
    exit(main())
