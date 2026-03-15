"""
数据导入 API 接口
提供 Excel 文件上传和 Neo4j 知识图谱导入功能
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Request, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.models import get_db, FileUploadRecord
from app.schemas.data_import import (
    FileUploadResponse,
    ImportResult,
    ImportStatistics,
    ImportError,
    FileListItem
)
from app.services.data_import_service import DataImportService
from app.services.operation_log_service import OperationLogService
from app.core.deps import get_current_user, get_current_admin
from app.core.logger_helper import log_operation
import logging

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(tags=["数据导入"])


@router.post("/upload-and-import", response_model=ImportResult, summary="上传并导入 Excel 文件")
async def upload_and_import(
    request: Request,
    file: UploadFile = File(..., description="Excel 文件"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    上传 Excel 文件并导入到 Neo4j（一步完成）

    流程：
    1. 上传文件到服务器
    2. 清空 Neo4j 数据库
    3. 解析 Excel 文件
    4. 创建节点和关系
    5. 返回导入统计信息

    Returns:
        ImportResult: 导入结果，包含统计信息和错误列表
    """
    try:
        # 验证文件类型
        if not file.filename or not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="仅支持 .xlsx 或 .xls 格式的 Excel 文件"
            )

        # 读取文件内容
        file_content = await file.read()

        # 验证文件大小（限制 50MB）
        max_size = 50 * 1024 * 1024
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"文件大小超过限制 ({max_size / 1024 / 1024}MB)"
            )

        # 生成文件ID
        file_id = DataImportService.generate_file_id()

        # 保存文件并创建数据库记录
        _, file_path = DataImportService.save_uploaded_file(
            file_content=file_content,
            original_filename=file.filename,
            file_id=file_id,
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username")
        )

        # 记录上传日志
        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type="UPLOAD",
            module="data_import",
            request=request,
            status=1,
            remark=f"上传并导入文件: {file.filename}"
        )

        # 执行导入
        result = DataImportService.import_from_excel(
            file_path=str(file_path),
            db=db,
            file_id=file_id
        )

        # 转换错误格式
        error_items = [
            ImportError(
                sheet_name=e.get("sheet_name"),
                row=e.get("row"),
                error_type=e.get("error_type", "unknown"),
                message=e.get("message", "")
            )
            for e in result.get("errors", [])
        ]

        import_result = ImportResult(
            success=result["success"],
            file_id=file_id,
            statistics=ImportStatistics(**result["statistics"]),
            errors=error_items,
            message=result["message"]
        )

        # 记录导入完成日志
        status_code = 1 if result["success"] else 0
        remark = f"导入完成: 节点{result['statistics']['total_nodes']}个, 关系{result['statistics']['relation_count']}条"
        if not result["success"]:
            remark = f"导入失败: {result['message']}"

        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type="IMPORT",
            module="data_import",
            request=request,
            status=status_code,
            remark=remark
        )

        return import_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传并导入失败: {e}")
        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type="UPLOAD_IMPORT",
            module="data_import",
            request=request,
            status=0,
            remark=f"操作失败: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"操作失败: {str(e)}"
        )


@router.get("/records", response_model=List[FileListItem], summary="获取上传记录列表")
async def get_upload_records(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    获取数据库中的上传记录列表

    按上传时间倒序排列

    Returns:
        List[FileListItem]: 上传记录列表
    """
    try:
        records = db.query(FileUploadRecord).order_by(
            FileUploadRecord.upload_time.desc()
        ).limit(100).all()

        return [
            FileListItem(
                file_id=record.file_id,
                filename=record.filename,
                file_path=record.file_path,
                file_size=record.file_size,
                upload_time=record.upload_time,
                status=record.import_status
            )
            for record in records
        ]

    except Exception as e:
        logger.error(f"获取上传记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取上传记录失败: {str(e)}"
        )


@router.get("/records/{file_id}", summary="获取上传记录详情")
async def get_upload_record(
    file_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    获取指定文件的上传记录详情

    Args:
        file_id: 文件ID

    Returns:
        上传记录详情
    """
    try:
        record = db.query(FileUploadRecord).filter(
            FileUploadRecord.file_id == file_id
        ).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"上传记录不存在: {file_id}"
            )

        return {
            "id": record.id,
            "file_id": record.file_id,
            "filename": record.filename,
            "file_path": record.file_path,
            "file_size": record.file_size,
            "uploader_id": record.uploader_id,
            "uploader_name": record.uploader_name,
            "import_status": record.import_status,
            "statistics": {
                "device_count": record.device_count,
                "person_count": record.person_count,
                "material_count": record.material_count,
                "process_count": record.process_count,
                "fault_count": record.fault_count,
                "relation_count": record.relation_count,
                "total_nodes": record.total_nodes,
                "duration_seconds": record.duration_seconds
            },
            "error_message": record.error_message,
            "upload_time": record.upload_time,
            "import_time": record.import_time
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取上传记录详情失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取上传记录详情失败: {str(e)}"
        )


@router.delete("/records/{file_id}", summary="删除上传记录和文件")
async def delete_upload_record(
    request: Request,
    file_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    删除指定的上传记录和对应文件

    Args:
        file_id: 要删除的文件ID

    Returns:
        删除结果
    """
    try:
        # 查找记录
        record = db.query(FileUploadRecord).filter(
            FileUploadRecord.file_id == file_id
        ).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"上传记录不存在: {file_id}"
            )

        # 删除文件
        from pathlib import Path
        file_path = Path(record.file_path)
        if file_path.exists():
            file_path.unlink()

        # 删除数据库记录
        db.delete(record)
        db.commit()

        # 记录删除日志
        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type="DELETE",
            module="data_import",
            request=request,
            status=1,
            remark=f"删除文件记录: {record.filename}"
        )

        return {"success": True, "message": "文件记录已删除"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除文件记录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件记录失败: {str(e)}"
        )


@router.post("/reimport/{file_id}", response_model=ImportResult, summary="根据历史记录重新导入")
async def reimport_from_record(
    request: Request,
    file_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """
    根据历史上传记录重新导入数据到 Neo4j（清空重建）

    使用已保存的文件重新执行导入，适用于：
    - 回滚到之前的数据版本
    - 重新导入之前失败但文件正确的情况

    Args:
        file_id: 历史上传记录的文件ID

    Returns:
        ImportResult: 导入结果，包含统计信息和错误列表
    """
    try:
        # 查找记录
        record = db.query(FileUploadRecord).filter(
            FileUploadRecord.file_id == file_id
        ).first()

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"上传记录不存在: {file_id}"
            )

        # 检查文件是否存在
        from pathlib import Path
        file_path = Path(record.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"文件不存在: {record.file_path}"
            )

        # 记录重新导入日志
        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type="REIMPORT",
            module="data_import",
            request=request,
            status=1,
            remark=f"重新导入文件: {record.filename}"
        )

        # 执行导入
        result = DataImportService.import_from_excel(
            file_path=str(file_path),
            db=db,
            file_id=file_id
        )

        # 转换错误格式
        error_items = [
            ImportError(
                sheet_name=e.get("sheet_name"),
                row=e.get("row"),
                error_type=e.get("error_type", "unknown"),
                message=e.get("message", "")
            )
            for e in result.get("errors", [])
        ]

        import_result = ImportResult(
            success=result["success"],
            file_id=file_id,
            statistics=ImportStatistics(**result["statistics"]),
            errors=error_items,
            message=result["message"]
        )

        # 记录导入完成日志
        status_code = 1 if result["success"] else 0
        remark = f"重新导入完成: 节点{result['statistics']['total_nodes']}个, 关系{result['statistics']['relation_count']}条"
        if not result["success"]:
            remark = f"重新导入失败: {result['message']}"

        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type="REIMPORT",
            module="data_import",
            request=request,
            status=status_code,
            remark=remark
        )

        return import_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"重新导入失败: {e}")
        await log_operation(
            db=db,
            user_id=current_user.get("id"),
            username=current_user.get("username"),
            action_type="REIMPORT",
            module="data_import",
            request=request,
            status=0,
            remark=f"重新导入失败: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"重新导入失败: {str(e)}"
        )


@router.get("/health", summary="数据导入模块健康检查")
async def health_check():
    """检查数据导入模块状态"""
    try:
        # 检查数据目录
        DataImportService.ensure_data_dir()

        return {
            "status": "healthy",
            "data_directory": str(DataImportService.DATA_DIR),
            "directory_exists": DataImportService.DATA_DIR.exists()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
