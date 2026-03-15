"""
数据导入模块测试代码

测试文件上传、Excel 解析和 Neo4j 导入功能
"""
import os
import sys
import io
import pytest
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from app.services.data_import_service import DataImportService
from app.core.neo4j_client import neo4j_client


# ==================== 测试配置 ====================
# 测试用的 Excel 文件路径
TEST_EXCEL_PATH = project_root.parent / "database" / "data" / "数据台账.xlsx"


class TestDataImportService:
    """数据导入服务测试类"""

    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        print("\n" + "=" * 60)
        print("数据导入模块测试")
        print("=" * 60)

        # 确保 Neo4j 连接
        try:
            neo4j_client.connect()
            print("✓ Neo4j 连接成功")
        except Exception as e:
            print(f"✗ Neo4j 连接失败: {e}")
            raise

    @classmethod
    def teardown_class(cls):
        """测试类清理"""
        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)
        neo4j_client.close()

    def test_01_data_directory(self):
        """测试 1: 数据目录创建"""
        print("\n[测试 1] 数据目录创建")
        data_dir = DataImportService.ensure_data_dir()
        assert data_dir.exists(), "数据目录不存在"
        print(f"✓ 数据目录: {data_dir}")

    def test_02_generate_file_id(self):
        """测试 2: 文件ID生成"""
        print("\n[测试 2] 文件ID生成")
        file_id = DataImportService.generate_file_id()
        assert file_id, "文件ID生成失败"
        assert isinstance(file_id, str), "文件ID应为字符串"
        print(f"✓ 生成文件ID: {file_id}")

    def test_03_save_uploaded_file(self):
        """测试 3: 文件保存"""
        print("\n[测试 3] 文件保存")
        # 创建测试文件内容
        test_content = b"Test file content for data import"
        file_id = DataImportService.generate_file_id()
        original_filename = "test_data.xlsx"

        # 保存文件
        saved_id, file_path = DataImportService.save_uploaded_file(
            file_content=test_content,
            original_filename=original_filename,
            file_id=file_id
        )

        assert saved_id == file_id, "文件ID不匹配"
        assert file_path.exists(), "文件未保存成功"

        # 清理测试文件
        file_path.unlink()

        print(f"✓ 文件保存成功: {file_path}")

    def test_04_get_file_info(self):
        """测试 4: 获取文件信息"""
        print("\n[测试 4] 获取文件信息")
        # 先创建一个测试文件
        test_content = b"Test content"
        file_id = DataImportService.generate_file_id()
        original_filename = "test_info.xlsx"

        saved_id, file_path = DataImportService.save_uploaded_file(
            file_content=test_content,
            original_filename=original_filename,
            file_id=file_id
        )

        # 获取文件信息
        file_info = DataImportService.get_file_info(file_id)
        assert file_info is not None, "文件信息获取失败"
        assert file_info["file_id"] == file_id, "文件ID不匹配"
        assert file_info["filename"] == original_filename, "文件名不匹配"

        # 清理
        file_path.unlink()

        print(f"✓ 文件信息获取成功: {file_info}")

    def test_05_clear_database(self):
        """测试 5: 清空数据库"""
        print("\n[测试 5] 清空数据库")
        success = DataImportService.clear_neo4j_database()
        assert success, "清空数据库失败"
        print("✓ 数据库已清空")

        # 验证数据库确实为空
        result = neo4j_client.execute_query("MATCH (n) RETURN count(n) as count")
        node_count = result[0]["count"] if result else 0
        assert node_count == 0, "数据库未完全清空"
        print(f"✓ 验证节点数: {node_count}")

    def test_06_create_indexes(self):
        """测试 6: 创建索引"""
        print("\n[测试 6] 创建索引")
        DataImportService.create_indexes()
        print("✓ 索引创建完成")

    def test_07_read_excel_with_encoding(self):
        """测试 7: 读取 Excel 文件（中文编码）"""
        print("\n[测试 7] 读取 Excel 文件")

        if not TEST_EXCEL_PATH.exists():
            print(f"⊘ 跳过测试: 测试文件不存在 ({TEST_EXCEL_PATH})")
            return

        sheets = DataImportService.read_excel_with_encoding(str(TEST_EXCEL_PATH))
        assert sheets is not None, "读取 Excel 失败"
        assert len(sheets) > 0, "Excel 文件为空"

        print(f"✓ 读取成功，包含 {len(sheets)} 个工作表:")
        for sheet_name, df in sheets.items():
            print(f"  - {sheet_name}: {len(df)} 行")

    def test_08_import_from_excel(self):
        """测试 8: 完整导入流程"""
        print("\n[测试 8] 完整导入流程")

        if not TEST_EXCEL_PATH.exists():
            print(f"⊘ 跳过测试: 测试文件不存在 ({TEST_EXCEL_PATH})")
            return

        print(f"导入文件: {TEST_EXCEL_PATH}")

        # 执行导入
        result = DataImportService.import_from_excel(str(TEST_EXCEL_PATH))

        print(f"\n导入结果:")
        print(f"  成功: {result['success']}")
        print(f"  消息: {result['message']}")

        stats = result["statistics"]
        print(f"\n统计信息:")
        print(f"  设备节点: {stats['device_count']}")
        print(f"  人员节点: {stats['person_count']}")
        print(f"  物料节点: {stats['material_count']}")
        print(f"  工艺节点: {stats['process_count']}")
        print(f"  故障节点: {stats['fault_count']}")
        print(f"  总节点数: {stats['total_nodes']}")
        print(f"  关系数: {stats['relation_count']}")
        print(f"  耗时: {stats['duration_seconds']} 秒")

        if result["errors"]:
            print(f"\n错误信息 (最多显示前 10 条):")
            for error in result["errors"][:10]:
                print(f"  - 行 {error.get('row')}: {error.get('message')}")

        assert result["success"], f"导入失败: {result['message']}"
        assert stats["total_nodes"] > 0, "没有导入任何节点"

        print("\n✓ 导入测试通过")

    def test_09_validate_relation(self):
        """测试 9: 关系验证"""
        print("\n[测试 9] 关系验证")

        # 合法的关系
        valid, msg = DataImportService._validate_relation(
            source_labels=["设备", "加工设备"],
            rel_type="适配工艺",
            target_labels=["工艺", "加工工艺"]
        )
        assert valid, f"合法关系被判定为非法: {msg}"
        print(f"✓ 合法关系验证通过")

        # 非法的关系
        invalid, msg = DataImportService._validate_relation(
            source_labels=["人员"],
            rel_type="适配工艺",
            target_labels=["工艺"]
        )
        assert not invalid, "非法关系被判定为合法"
        print(f"✓ 非法关系验证通过: {msg}")

    def test_10_node_type_detection(self):
        """测试 10: 节点类型识别"""
        print("\n[测试 10] 节点类型识别")

        main_type, sub_type = DataImportService._get_node_type(["设备", "加工设备"])
        assert main_type == "设备", "主类型识别错误"
        assert sub_type == "加工设备", "子类型识别错误"
        print(f"✓ 节点类型识别: {main_type} / {sub_type}")

        main_type, sub_type = DataImportService._get_node_type(["人员", "管理人员"])
        assert main_type == "人员", "主类型识别错误"
        assert sub_type == "管理人员", "子类型识别错误"
        print(f"✓ 节点类型识别: {main_type} / {sub_type}")


# ==================== 独立测试脚本 ====================
def run_standalone_tests():
    """
    运行独立测试脚本（不依赖 pytest）
    适用于快速测试和调试
    """
    print("\n" + "=" * 60)
    print("数据导入模块 - 独立测试脚本")
    print("=" * 60)

    # 初始化
    try:
        neo4j_client.connect()
        print("✓ Neo4j 连接成功\n")
    except Exception as e:
        print(f"✗ Neo4j 连接失败: {e}\n")
        return

    # 创建测试实例
    test = TestDataImportService()
    test.setup_class()

    # 运行测试
    tests = [
        ("数据目录创建", test.test_01_data_directory),
        ("文件ID生成", test.test_02_generate_file_id),
        ("文件保存", test.test_03_save_uploaded_file),
        ("获取文件信息", test.test_04_get_file_info),
        ("清空数据库", test.test_05_clear_database),
        ("创建索引", test.test_06_create_indexes),
        ("读取Excel", test.test_07_read_excel_with_encoding),
        ("完整导入", test.test_08_import_from_excel),
        ("关系验证", test.test_09_validate_relation),
        ("节点类型识别", test.test_10_node_type_detection),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ 测试失败 [{name}]: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ 测试错误 [{name}]: {e}")
            failed += 1

    # 清理
    test.teardown_class()

    # 输出结果
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)


# ==================== API 测试脚本 ====================
def test_api_with_requests():
    """
    API 接口测试脚本
    使用 requests 库测试 FastAPI 接口

    需要先启动后端服务: uvicorn app.main:app --reload
    """
    print("\n" + "=" * 60)
    print("数据导入 API 测试")
    print("=" * 60)

    import requests

    # API 基础地址
    BASE_URL = "http://localhost:8000/api/v1"

    # 测试文件路径
    test_file = TEST_EXCEL_PATH

    if not test_file.exists():
        print(f"⊘ 测试文件不存在: {test_file}")
        return

    try:
        # 1. 首先登录获取 token
        print("\n[1] 登录...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "123456"}
        )
        login_response.raise_for_status()
        token = login_response.json()["access_token"]
        print(f"✓ 登录成功, Token: {token[:20]}...")

        headers = {"Authorization": f"Bearer {token}"}

        # 2. 上传文件
        print("\n[2] 上传文件...")
        with open(test_file, "rb") as f:
            upload_response = requests.post(
                f"{BASE_URL}/data-import/upload",
                headers=headers,
                files={"file": (test_file.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        upload_response.raise_for_status()
        upload_result = upload_response.json()
        file_id = upload_result["file_id"]
        print(f"✓ 文件上传成功")
        print(f"  文件ID: {file_id}")
        print(f"  文件名: {upload_result['filename']}")
        print(f"  文件大小: {upload_result['file_size']} 字节")

        # 3. 执行导入
        print("\n[3] 执行导入...")
        import_response = requests.post(
            f"{BASE_URL}/data-import/import/{file_id}",
            headers=headers
        )
        import_response.raise_for_status()
        import_result = import_response.json()
        print(f"✓ 导入完成")
        print(f"  成功: {import_result['success']}")
        stats = import_result["statistics"]
        print(f"  节点数: {stats['total_nodes']}")
        print(f"  关系数: {stats['relation_count']}")

        # 4. 获取文件列表
        print("\n[4] 获取文件列表...")
        list_response = requests.get(
            f"{BASE_URL}/data-import/files",
            headers=headers
        )
        list_response.raise_for_status()
        files = list_response.json()
        print(f"✓ 文件列表获取成功，共 {len(files)} 个文件")

        # 5. 健康检查
        print("\n[5] 健康检查...")
        health_response = requests.get(f"{BASE_URL}/data-import/health")
        health_response.raise_for_status()
        health = health_response.json()
        print(f"✓ 健康状态: {health['status']}")

        print("\n" + "=" * 60)
        print("API 测试全部通过！")
        print("=" * 60)

    except requests.exceptions.RequestException as e:
        print(f"\n✗ API 请求失败: {e}")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")


# ==================== 使用说明 ====================
def print_usage():
    """打印使用说明"""
    print("""
数据导入模块测试使用说明
========================

1. 使用 pytest 运行完整测试套件:
   pytest backend/tests/test_data_import.py -v

2. 运行独立测试脚本（不需要 pytest）:
   python -m backend.tests.test_data_import

3. 运行 API 接口测试（需要先启动后端服务）:
   python -c "from backend.tests.test_data_import import test_api_with_requests; test_api_with_requests()"

4. 在代码中直接使用:
   from backend.tests.test_data_import import run_standalone_tests
   run_standalone_tests()

注意事项:
- 运行测试前确保 Neo4j 服务已启动
- 运行 API 测试前确保后端服务已启动（uvicorn app.main:app --reload）
- 测试会清空 Neo4j 数据库，请勿在生产环境运行
""")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据导入模块测试")
    parser.add_argument("--mode", choices=["unit", "api", "help"], default="unit",
                       help="测试模式: unit=单元测试, api=API测试, help=显示帮助")

    args = parser.parse_args()

    if args.mode == "help":
        print_usage()
    elif args.mode == "api":
        test_api_with_requests()
    else:
        run_standalone_tests()
