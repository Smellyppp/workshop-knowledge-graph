"""
文件上传记录模型
存储用户上传的 Excel 文件记录和导入状态
"""
from datetime import datetime
from sqlalchemy import Column, BigInteger, String, Integer, Float, DateTime, Text

from app.models.base import Base


class FileUploadRecord(Base):
    """
    文件上传记录表
    记录每次上传的Excel文件及其导入状态和结果
    """
    __tablename__ = "file_upload_record"

    # 主键：记录ID
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="记录ID")

    # 文件信息
    file_id = Column(String(64), unique=True, nullable=False, index=True, comment="文件唯一ID（UUID）")
    filename = Column(String(255), nullable=False, comment="原始文件名")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_size = Column(BigInteger, nullable=False, comment="文件大小（字节）")

    # 上传信息
    uploader_id = Column(BigInteger, nullable=False, index=True, comment="上传者用户ID")
    uploader_name = Column(String(50), nullable=False, comment="上传者用户名")

    # 导入状态
    import_status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
        comment="导入状态: pending=待导入, importing=导入中, success=成功, failed=失败"
    )

    # 导入统计（成功后填写）
    device_count = Column(Integer, default=0, comment="设备节点数")
    person_count = Column(Integer, default=0, comment="人员节点数")
    material_count = Column(Integer, default=0, comment="物料节点数")
    process_count = Column(Integer, default=0, comment="工艺节点数")
    fault_count = Column(Integer, default=0, comment="故障节点数")
    relation_count = Column(Integer, default=0, comment="关系数量")
    total_nodes = Column(Integer, default=0, comment="总节点数")
    duration_seconds = Column(Float, default=0, comment="导入耗时（秒）")

    # 错误信息
    error_message = Column(Text, comment="错误信息")

    # 时间戳
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False, comment="上传时间")
    import_time = Column(DateTime, comment="导入完成时间")

    def to_dict(self):
        """将模型转换为字典"""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "uploader_id": self.uploader_id,
            "uploader_name": self.uploader_name,
            "import_status": self.import_status,
            "device_count": self.device_count,
            "person_count": self.person_count,
            "material_count": self.material_count,
            "process_count": self.process_count,
            "fault_count": self.fault_count,
            "relation_count": self.relation_count,
            "total_nodes": self.total_nodes,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "import_time": self.import_time.isoformat() if self.import_time else None
        }

    def __repr__(self):
        """模型的字符串表示"""
        return (
            f"<FileUploadRecord(id={self.id}, file_id={self.file_id}, "
            f"filename={self.filename}, status={self.import_status})>"
        )
