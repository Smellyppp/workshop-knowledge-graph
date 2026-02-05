"""
测试节点展开功能
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.neo4j_client import neo4j_client
from app.services.knowledge_graph_service import KnowledgeGraphService
import json


def test_get_node_neighbors():
    """测试获取节点邻居功能"""
    print("=" * 60)
    print("测试：获取节点邻居（节点展开功能）")
    print("=" * 60)

    # 步骤1：先搜索一个节点
    keyword = "重新开机"
    print(f"\n步骤1：搜索关键词 '{keyword}'")

    search_result = KnowledgeGraphService.search_all_nodes(keyword, limit=1)

    if not search_result['nodes']:
        print(f"[ERROR] 未找到包含 '{keyword}' 的节点")
        return False

    # 获取第一个节点的ID
    node = search_result['nodes'][0]
    node_id = node['id']
    node_title = node['properties'].get('title', 'Unknown')

    print(f"[OK] 找到节点: {node_title}")
    print(f"     ID: {node_id}")
    print(f"     标签: {node['labels']}")

    # 步骤2：获取该节点的邻居
    print(f"\n步骤2：获取节点的邻居")

    try:
        neighbors_result = KnowledgeGraphService.get_node_neighbors(node_id, depth=1)

        print(f"[OK] 成功获取邻居节点")
        print(f"     找到 {len(neighbors_result['nodes'])} 个邻居节点")
        print(f"     找到 {len(neighbors_result['edges'])} 条关系")

        # 显示邻居节点详情
        if neighbors_result['nodes']:
            print("\n邻居节点列表:")
            print("-" * 60)
            for i, neighbor in enumerate(neighbors_result['nodes'], 1):
                print(f"\n邻居 {i}:")
                print(f"  ID: {neighbor['id']}")
                print(f"  标签: {neighbor['labels']}")
                print(f"  属性:")
                for key, value in neighbor['properties'].items():
                    print(f"    {key}: {value}")
            print("-" * 60)

        # 显示关系详情
        if neighbors_result['edges']:
            print("\n关系列表:")
            print("-" * 60)
            for i, edge in enumerate(neighbors_result['edges'], 1):
                print(f"\n关系 {i}:")
                print(f"  ID: {edge['id']}")
                print(f"  类型: {edge['type']}")
                print(f"  从节点: {edge['from_node']}")
                print(f"  到节点: {edge['to_node']}")
            print("-" * 60)

        # 显示完整的 JSON 结果
        print("\n完整结果 (JSON格式):")
        print("-" * 60)
        print(json.dumps(neighbors_result, ensure_ascii=False, indent=2))
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n[ERROR] 获取邻居节点失败！")
        print(f"错误信息: {e}")
        print(f"错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("知识图谱节点展开功能测试")
    print("=" * 60)

    # 执行测试
    test_result = False

    try:
        test_result = test_get_node_neighbors()
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

    status = "[OK] 通过" if test_result else "[ERROR] 失败"
    print(f"节点展开功能测试: {status}")

    if test_result:
        print("\n[SUCCESS] 节点展开功能运行正常！")
        print("\nAPI 端点: GET /api/v1/knowledge-graph/neighbors/{node_id}")
        return 0
    else:
        print("\n[WARNING] 节点展开功能测试失败，请检查错误信息。")
        return 1


if __name__ == "__main__":
    exit(main())
