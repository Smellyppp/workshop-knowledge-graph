"""
数据导入服务
处理 Excel 文件解析和 Neo4j 知识图谱导入
采用全局删除、重新构建的方式

宽松模式：
- 不约束节点子类型，Excel 中的任何子类型都会被接受
- 不约束关系类型，任何关系类型都可以创建
- 只验证节点 ID 是否存在，不验证关系的合法性
"""
import os
import uuid
import shutil
import time
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
import logging

from app.core.neo4j_client import neo4j_client
from app.models.file_upload_record import FileUploadRecord

logger = logging.getLogger(__name__)


# ==================== 数据配置 ====================
# 各工作表的唯一标识列（宽松模式：不再约束节点类型和关系类型）
UNIQUE_ID_COLUMNS = {
    "设备台账": "设备编号",
    "人员台账": "工号",
    "工艺台账": "工艺编号",
    "物料台账": "物料编号",
    "故障台账": "故障编号"
}


class DataImportService:
    """数据导入服务类"""

    # 文件存储目录（相对于项目根目录）
    DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "database" / "data"

    @classmethod
    def ensure_data_dir(cls) -> Path:
        """确保数据目录存在"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        return cls.DATA_DIR

    @classmethod
    def generate_file_id(cls) -> str:
        """生成唯一文件ID"""
        return str(uuid.uuid4())

    @classmethod
    def save_uploaded_file(
        cls,
        file_content: bytes,
        original_filename: str,
        file_id: str,
        db: Session,
        user_id: int,
        username: str
    ) -> Tuple[str, Path]:
        """
        保存上传的文件并记录到数据库

        Args:
            file_content: 文件内容（字节）
            original_filename: 原始文件名
            file_id: 生成的文件ID
            db: 数据库会话
            user_id: 上传者用户ID
            username: 上传者用户名

        Returns:
            tuple: (file_id, file_path)
        """
        cls.ensure_data_dir()

        # 生成安全的文件名（保留原始文件名，添加ID前缀）
        safe_filename = f"{file_id}_{original_filename}"
        file_path = cls.DATA_DIR / safe_filename

        # 写入文件
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # 创建数据库记录
        record = FileUploadRecord(
            file_id=file_id,
            filename=original_filename,
            file_path=str(file_path),
            file_size=len(file_content),
            uploader_id=user_id,
            uploader_name=username,
            import_status="pending"
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        logger.info(f"文件已保存并记录: {file_path} (记录ID: {record.id})")
        return file_id, file_path

    @classmethod
    def get_file_info(cls, file_id: str) -> Optional[Dict[str, Any]]:
        """
        根据文件ID获取文件信息

        Args:
            file_id: 文件ID

        Returns:
            文件信息字典，如果未找到则返回 None
        """
        cls.ensure_data_dir()

        # 查找匹配的文件
        for file_path in cls.DATA_DIR.glob(f"{file_id}_*"):
            stat = file_path.stat()
            return {
                "file_id": file_id,
                "filename": file_path.name.replace(f"{file_id}_", ""),
                "file_path": str(file_path),
                "file_size": stat.st_size,
                "upload_time": datetime.fromtimestamp(stat.st_ctime)
            }
        return None

    @classmethod
    def read_excel_with_encoding(cls, file_path: str) -> Optional[Dict[str, pd.DataFrame]]:
        """
        读取 Excel 文件，处理中文编码

        Args:
            file_path: Excel 文件路径

        Returns:
            包含各工作表的字典，key 为工作表名，value 为 DataFrame
        """
        try:
            # 使用 openpyxl 引擎读取，支持中文
            excel_file = pd.ExcelFile(file_path, engine='openpyxl')
            sheets = {}

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')
                sheets[sheet_name] = df
                logger.info(f"读取工作表 '{sheet_name}': {len(df)} 行")

            return sheets

        except Exception as e:
            logger.error(f"读取 Excel 文件失败: {e}")
            return None

    @classmethod
    def clear_neo4j_database(cls) -> bool:
        """
        清空 Neo4j 数据库（全局删除）

        Returns:
            是否成功
        """
        try:
            # 使用 Cypher 语句删除所有节点和关系
            neo4j_client.execute_query("MATCH (n) DETACH DELETE n")
            logger.info("Neo4j 数据库已清空")
            return True
        except Exception as e:
            logger.error(f"清空 Neo4j 数据库失败: {e}")
            return False

    @classmethod
    def create_indexes(cls) -> None:
        """创建 Neo4j 索引以提高查询性能"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (n:设备) ON (n.设备编号)",
            "CREATE INDEX IF NOT EXISTS FOR (n:人员) ON (n.工号)",
            "CREATE INDEX IF NOT EXISTS FOR (n:物料) ON (n.物料编号)",
            "CREATE INDEX IF NOT EXISTS FOR (n:工艺) ON (n.工艺编号)",
            "CREATE INDEX IF NOT EXISTS FOR (n:故障) ON (n.故障编号)"
        ]
        for index in indexes:
            try:
                neo4j_client.execute_query(index)
            except Exception as e:
                logger.warning(f"创建索引失败（可能已存在）: {e}")

    @classmethod
    def _import_device_sheet(cls, df: pd.DataFrame) -> Tuple[int, Dict[str, str]]:
        """
        导入设备工作表

        Args:
            df: 设备数据 DataFrame

        Returns:
            tuple: (导入数量, 节点ID映射)
        """
        count = 0
        node_id_map = {}
        error_count = 0

        for idx, row in df.iterrows():
            try:
                properties = {}
                for col, val in row.items():
                    if pd.notna(val):
                        # 处理故障率百分比
                        if col == '故障率' and isinstance(val, str):
                            try:
                                val = float(val.replace('%', '')) / 100
                            except:
                                pass
                        properties[col] = val

                device_type = properties.get('设备类型', '')
                device_id = properties.get('设备编号')

                if not device_id:
                    logger.warning(f"设备台账第 {idx+2} 行缺少设备编号，跳过")
                    error_count += 1
                    continue

                # 构建节点标签（宽松模式：不检查子类型是否合法）
                labels = ['设备']
                if device_type:
                    labels.append(device_type)

                # 创建节点
                element_id = cls._create_node(labels, properties)
                if element_id:
                    node_id_map[device_id] = element_id
                    count += 1
                else:
                    logger.warning(f"设备 {device_id} 创建节点失败")
                    error_count += 1

            except Exception as e:
                error_count += 1
                logger.warning(f"导入设备行 {idx+2} 失败: {e}")

        logger.info(f"导入设备节点: {count} 个，失败: {error_count} 个")
        return count, node_id_map

    @classmethod
    def _import_person_sheet(cls, df: pd.DataFrame) -> Tuple[int, Dict[str, str]]:
        """导入人员工作表"""
        count = 0
        node_id_map = {}
        error_count = 0

        for idx, row in df.iterrows():
            try:
                properties = {}
                for col, val in row.items():
                    if pd.notna(val):
                        properties[col] = val

                person_type = properties.get('人员类型', '')
                work_id = properties.get('工号')

                if not work_id:
                    logger.warning(f"人员台账第 {idx+2} 行缺少工号，跳过")
                    error_count += 1
                    continue

                # 构建节点标签（宽松模式：不检查子类型是否合法）
                labels = ['人员']
                if person_type:
                    labels.append(person_type)

                element_id = cls._create_node(labels, properties)
                if element_id:
                    node_id_map[work_id] = element_id
                    count += 1
                else:
                    logger.warning(f"人员 {work_id} 创建节点失败")
                    error_count += 1

            except Exception as e:
                error_count += 1
                logger.warning(f"导入人员行 {idx+2} 失败: {e}")

        logger.info(f"导入人员节点: {count} 个，失败: {error_count} 个")
        return count, node_id_map

    @classmethod
    def _import_material_sheet(cls, df: pd.DataFrame) -> Tuple[int, Dict[str, str]]:
        """导入物料工作表"""
        count = 0
        node_id_map = {}
        error_count = 0

        for idx, row in df.iterrows():
            try:
                properties = {}
                for col, val in row.items():
                    if pd.notna(val):
                        properties[col] = val

                material_type = properties.get('物料类型', '')
                material_id = properties.get('物料编号')

                if not material_id:
                    logger.warning(f"物料台账第 {idx+2} 行缺少物料编号，跳过")
                    error_count += 1
                    continue

                # 构建节点标签（宽松模式：不检查子类型是否合法）
                labels = ['物料']
                if material_type:
                    labels.append(material_type)

                element_id = cls._create_node(labels, properties)
                if element_id:
                    node_id_map[material_id] = element_id
                    count += 1
                else:
                    logger.warning(f"物料 {material_id} 创建节点失败")
                    error_count += 1

            except Exception as e:
                error_count += 1
                logger.warning(f"导入物料行 {idx+2} 失败: {e}")

        logger.info(f"导入物料节点: {count} 个，失败: {error_count} 个")
        return count, node_id_map

    @classmethod
    def _import_process_sheet(cls, df: pd.DataFrame) -> Tuple[int, Dict[str, str]]:
        """导入工艺工作表"""
        count = 0
        node_id_map = {}
        error_count = 0

        for idx, row in df.iterrows():
            try:
                properties = {}
                for col, val in row.items():
                    if pd.notna(val):
                        properties[col] = val

                process_type = properties.get('工艺类型', '')
                process_id = properties.get('工艺编号')

                if not process_id:
                    logger.warning(f"工艺台账第 {idx+2} 行缺少工艺编号，跳过")
                    error_count += 1
                    continue

                # 构建节点标签（宽松模式：不检查子类型是否合法）
                labels = ['工艺']
                if process_type:
                    labels.append(process_type)

                element_id = cls._create_node(labels, properties)
                if element_id:
                    node_id_map[process_id] = element_id
                    count += 1
                else:
                    logger.warning(f"工艺 {process_id} 创建节点失败")
                    error_count += 1

            except Exception as e:
                error_count += 1
                logger.warning(f"导入工艺行 {idx+2} 失败: {e}")

        logger.info(f"导入工艺节点: {count} 个，失败: {error_count} 个")
        return count, node_id_map

    @classmethod
    def _import_fault_sheet(cls, df: pd.DataFrame) -> Tuple[int, Dict[str, str]]:
        """导入故障工作表"""
        count = 0
        node_id_map = {}
        error_count = 0

        for idx, row in df.iterrows():
            try:
                properties = {}
                for col, val in row.items():
                    if pd.notna(val):
                        properties[col] = val

                fault_id = properties.get('故障编号')

                if not fault_id:
                    logger.warning(f"故障台账第 {idx+2} 行缺少故障编号，跳过")
                    error_count += 1
                    continue

                element_id = cls._create_node(['故障'], properties)
                if element_id:
                    node_id_map[fault_id] = element_id
                    count += 1
                else:
                    logger.warning(f"故障 {fault_id} 创建节点失败")
                    error_count += 1

            except Exception as e:
                error_count += 1
                logger.warning(f"导入故障行 {idx+2} 失败: {e}")

        logger.info(f"导入故障节点: {count} 个，失败: {error_count} 个")
        return count, node_id_map

    @classmethod
    def _create_node(cls, labels: List[str], properties: Dict[str, Any]) -> Optional[str]:
        """
        创建节点

        Args:
            labels: 节点标签列表
            properties: 节点属性

        Returns:
            节点的 elementId，失败返回 None
        """
        try:
            # 构建 Cypher 语句
            labels_str = ':' + ':'.join(labels) if labels else ''

            # 构建属性字符串（使用 $参数语法）
            # 正确的 Cypher 语法：CREATE (n:Label {key1: $key1, key2: $key2})
            if properties:
                props_str = ', '.join([f"`{k}`: ${k}" for k in properties.keys()])
                query = f"CREATE (n{labels_str} {{{props_str}}}) RETURN elementId(n) as id"
            else:
                query = f"CREATE (n{labels_str}) RETURN elementId(n) as id"

            result = neo4j_client.execute_query(query, properties)

            if result and len(result) > 0:
                return result[0].get('id')
        except Exception as e:
            # 提供更详细的错误信息
            id_prop = properties.get('设备编号') or properties.get('工号') or properties.get('物料编号') or properties.get('工艺编号') or properties.get('故障编号') or 'unknown'
            logger.error(f"创建节点失败 [{labels}][ID:{id_prop}]: {e}")
        return None

    @classmethod
    def _create_relationship(cls, source_element_id: str, target_element_id: str, rel_type: str) -> bool:
        """
        创建关系

        Args:
            source_element_id: 源节点 elementId
            target_element_id: 目标节点 elementId
            rel_type: 关系类型

        Returns:
            是否成功
        """
        try:
            query = """
            MATCH (a), (b)
            WHERE elementId(a) = $source_id AND elementId(b) = $target_id
            CREATE (a)-[r:$REL_TYPE]->(b)
            RETURN elementId(r) as id
            """.replace('$REL_TYPE', rel_type)

            result = neo4j_client.execute_query(
                query,
                {"source_id": source_element_id, "target_id": target_element_id}
            )

            # 添加调试日志
            if result and len(result) > 0:
                logger.debug(f"创建关系成功: {source_element_id} -[{rel_type}]-> {target_element_id}")
            else:
                logger.warning(f"创建关系返回空结果: {source_element_id} -[{rel_type}]-> {target_element_id}")

            return result is not None and len(result) > 0
        except Exception as e:
            logger.error(f"创建关系失败 ({source_element_id} -[{rel_type}]-> {target_element_id}): {e}")
            return False

    @classmethod
    def _import_triple_sheet(cls, df: pd.DataFrame, node_id_map: Dict[str, str]) -> Tuple[int, List[Dict[str, Any]]]:
        """
        导入三元组关系工作表

        Args:
            df: 三元组数据 DataFrame
            node_id_map: 节点ID映射字典

        Returns:
            tuple: (导入数量, 错误列表)
        """
        count = 0
        errors = []

        # 输出列名和行数用于调试
        logger.info(f"三元组关系表列名: {list(df.columns)}, 行数: {len(df)}")
        logger.info(f"node_id_map 包含的节点数: {len(node_id_map)}, 示例: {list(node_id_map.keys())[:5]}")

        # 统计三元组中的实体ID，帮助调试
        head_entities = set()
        tail_entities = set()
        for _, row in df.iterrows():
            head = row.get('头实体')
            tail = row.get('尾实体')
            if pd.notna(head):
                head_entities.add(str(head).strip())
            if pd.notna(tail):
                tail_entities.add(str(tail).strip())

        logger.info(f"三元组中的头实体数量: {len(head_entities)}, 样本: {sorted(list(head_entities))[:10]}")
        logger.info(f"三元组中的尾实体数量: {len(tail_entities)}, 样本: {sorted(list(tail_entities))[:10]}")

        # 检查有多少实体能在node_id_map中找到
        matched_heads = sum(1 for h in head_entities if h in node_id_map)
        matched_tails = sum(1 for t in tail_entities if t in node_id_map)
        logger.info(f"头实体匹配数: {matched_heads}/{len(head_entities)}")
        logger.info(f"尾实体匹配数: {matched_tails}/{len(tail_entities)}")

        # 如果匹配率很低，输出未匹配的实体
        if matched_heads < len(head_entities) * 0.5:
            unmatched_heads = sorted([h for h in head_entities if h not in node_id_map])[:20]
            logger.warning(f"未匹配的头实体样本 (前20个): {unmatched_heads}")

        if matched_tails < len(tail_entities) * 0.5:
            unmatched_tails = sorted([t for t in tail_entities if t not in node_id_map])[:20]
            logger.warning(f"未匹配的尾实体样本 (前20个): {unmatched_tails}")

        for idx, row in df.iterrows():
            try:
                head = row.get('头实体')
                rel_type = row.get('对象属性')
                tail = row.get('尾实体')

                # 跳过空行
                if pd.isna(head) or pd.isna(rel_type) or pd.isna(tail):
                    continue

                head = str(head).strip() if head else ''
                rel_type = str(rel_type).strip() if rel_type else ''
                tail = str(tail).strip() if tail else ''

                if not all([head, rel_type, tail]):
                    continue

                source_id = node_id_map.get(head)
                target_id = node_id_map.get(tail)

                if not source_id or not target_id:
                    errors.append({
                        "row": idx + 2,  # Excel 行号（从1开始，加上表头）
                        "error_type": "missing_node",
                        "message": f"节点不存在: 头实体='{head}' ({'✓' if source_id else '✗'}), 尾实体='{tail}' ({'✓' if target_id else '✗'})"
                    })
                    continue

                # 宽松模式：不验证关系类型，直接创建关系
                if cls._create_relationship(source_id, target_id, rel_type):
                    count += 1

            except Exception as e:
                errors.append({
                    "row": idx + 2,
                    "error_type": "processing_error",
                    "message": str(e)
                })

        logger.info(f"导入关系: {count} 条，错误: {len(errors)} 条")
        return count, errors

    @classmethod
    def import_from_excel(
        cls,
        file_path: str,
        db: Session,
        file_id: str
    ) -> Dict[str, Any]:
        """
        从 Excel 文件导入数据到 Neo4j
        采用全局删除、重新构建的方式，并更新数据库记录

        Args:
            file_path: Excel 文件路径
            db: 数据库会话
            file_id: 文件ID（用于更新数据库记录）

        Returns:
            导入结果字典，包含统计信息和错误列表
        """
        start_time = time.time()
        statistics = {
            "device_count": 0,
            "person_count": 0,
            "material_count": 0,
            "process_count": 0,
            "fault_count": 0,
            "relation_count": 0,
            "total_nodes": 0
        }
        all_errors = []

        # 获取数据库记录
        record = db.query(FileUploadRecord).filter(FileUploadRecord.file_id == file_id).first()
        if record:
            record.import_status = "importing"
            db.commit()

        try:
            # 1. 读取 Excel 文件
            logger.info(f"开始导入 Excel 文件: {file_path}")
            sheets = cls.read_excel_with_encoding(file_path)
            if not sheets:
                raise ValueError("无法读取 Excel 文件或文件为空")

            # 输出所有sheet名称用于调试
            logger.info(f"Excel 文件包含的工作表: {list(sheets.keys())}")

            # 2. 清空现有数据库
            logger.info("清空 Neo4j 数据库...")
            if not cls.clear_neo4j_database():
                raise RuntimeError("清空数据库失败")

            # 3. 创建索引
            cls.create_indexes()

            # 4. 导入各工作表的节点
            node_id_map = {}

            # 设备台账
            if "设备台账" in sheets:
                statistics["device_count"], device_map = cls._import_device_sheet(sheets["设备台账"])
                node_id_map.update(device_map)

            # 人员台账
            if "人员台账" in sheets:
                statistics["person_count"], person_map = cls._import_person_sheet(sheets["人员台账"])
                node_id_map.update(person_map)

            # 物料台账
            if "物料台账" in sheets:
                statistics["material_count"], material_map = cls._import_material_sheet(sheets["物料台账"])
                node_id_map.update(material_map)

            # 工艺台账
            if "工艺台账" in sheets:
                statistics["process_count"], process_map = cls._import_process_sheet(sheets["工艺台账"])
                node_id_map.update(process_map)

            # 故障台账
            if "故障台账" in sheets:
                statistics["fault_count"], fault_map = cls._import_fault_sheet(sheets["故障台账"])
                node_id_map.update(fault_map)

            statistics["total_nodes"] = sum([
                statistics["device_count"],
                statistics["person_count"],
                statistics["material_count"],
                statistics["process_count"],
                statistics["fault_count"]
            ])

            # 5. 导入三元组关系
            logger.info(f"检查三元组关系工作表... 可用的工作表: {list(sheets.keys())}")
            logger.info(f"node_id_map 中已导入的节点数: {len(node_id_map)}")

            # 显示node_id_map中的ID样本，帮助调试
            if node_id_map:
                sample_ids = sorted(list(node_id_map.keys()))[:20]
                logger.info(f"node_id_map 中的ID样本: {sample_ids}")

            # 检查可能的sheet名称
            triple_sheet_name = None
            for possible_name in ["三元组关系", "三元组", "关系", "关系表"]:
                if possible_name in sheets:
                    triple_sheet_name = possible_name
                    break

            if triple_sheet_name:
                logger.info(f"找到三元组工作表: '{triple_sheet_name}'")
                relation_count, errors = cls._import_triple_sheet(sheets[triple_sheet_name], node_id_map)
                statistics["relation_count"] = relation_count
                all_errors.extend(errors)
                logger.info(f"三元组关系导入完成: 成功 {relation_count} 条，错误 {len(errors)} 条")
            else:
                logger.warning(f"未找到三元组关系工作表，可用的工作表: {list(sheets.keys())}")

            duration = time.time() - start_time
            statistics["duration_seconds"] = round(duration, 2)

            logger.info(f"导入完成！耗时: {duration:.2f} 秒")
            logger.info(f"节点总数: {statistics['total_nodes']}, 关系数: {statistics['relation_count']}")

            # 更新数据库记录
            if record:
                record.import_status = "success"
                record.device_count = statistics["device_count"]
                record.person_count = statistics["person_count"]
                record.material_count = statistics["material_count"]
                record.process_count = statistics["process_count"]
                record.fault_count = statistics["fault_count"]
                record.relation_count = statistics["relation_count"]
                record.total_nodes = statistics["total_nodes"]
                record.duration_seconds = statistics["duration_seconds"]
                record.error_message = None
                record.import_time = datetime.now()
                db.commit()

            return {
                "success": True,
                "statistics": statistics,
                "errors": all_errors,
                "message": "导入成功"
            }

        except Exception as e:
            logger.error(f"导入失败: {e}")
            error_msg = str(e)

            # 更新数据库记录为失败状态
            if record:
                record.import_status = "failed"
                record.error_message = error_msg[:1000] if len(error_msg) > 1000 else error_msg
                record.import_time = datetime.now()
                db.commit()

            return {
                "success": False,
                "statistics": statistics,
                "errors": all_errors,
                "message": f"导入失败: {error_msg}"
            }
