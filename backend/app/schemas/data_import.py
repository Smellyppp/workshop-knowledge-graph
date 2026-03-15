"""
数据导入相关的数据模型和 Schema 定义
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class FileUploadResponse(BaseModel):
    """文件上传响应"""
    file_id: str = Field(..., description="文件唯一ID")
    filename: str = Field(..., description="原始文件名")
    file_path: str = Field(..., description="文件存储路径")
    file_size: int = Field(..., description="文件大小（字节）")
    upload_time: datetime = Field(default_factory=datetime.now, description="上传时间")


class ImportStatus(BaseModel):
    """导入状态响应"""
    status: str = Field(..., description="状态: pending, processing, completed, failed")
    message: str = Field(..., description="状态消息")
    file_id: Optional[str] = Field(None, description="关联的文件ID")
    progress: Optional[float] = Field(None, description="进度百分比 (0-100)")


class ImportStatistics(BaseModel):
    """导入统计信息"""
    device_count: int = Field(0, description="导入的设备节点数")
    person_count: int = Field(0, description="导入的人员节点数")
    material_count: int = Field(0, description="导入的物料节点数")
    process_count: int = Field(0, description="导入的工艺节点数")
    fault_count: int = Field(0, description="导入的故障节点数")
    relation_count: int = Field(0, description="导入的关系数")
    total_nodes: int = Field(0, description="总节点数")
    duration_seconds: float = Field(0, description="导入耗时（秒）")


class ImportError(BaseModel):
    """导入错误信息"""
    sheet_name: Optional[str] = Field(None, description="出错的工作表名")
    row: Optional[int] = Field(None, description="出错的行号")
    error_type: str = Field(..., description="错误类型")
    message: str = Field(..., description="错误消息")


class ImportResult(BaseModel):
    """导入结果"""
    success: bool = Field(..., description="是否成功")
    file_id: str = Field(..., description="文件ID")
    statistics: ImportStatistics = Field(..., description="导入统计")
    errors: list[ImportError] = Field(default_factory=list, description="错误列表")
    message: str = Field(..., description="结果消息")


class FileListItem(BaseModel):
    """已上传文件列表项"""
    file_id: str
    filename: str
    file_path: str
    file_size: int
    upload_time: Optional[datetime] = None
    status: str = Field(..., description="文件状态: pending, imported, failed")
