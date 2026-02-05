"""
操作日志数据模型（Pydantic）
用于请求数据验证和响应数据序列化
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class OperationLogCreate(BaseModel):
    """
    操作日志创建请求模型
    用于内部服务创建日志记录
    """
    user_id: int = Field(..., description="操作用户ID")
    username: str = Field(..., min_length=1, max_length=50, description="操作用户名")
    action_type: str = Field(..., min_length=1, max_length=50, description="行为类型")
    module: str = Field(..., min_length=1, max_length=50, description="操作模块")
    ip_address: Optional[str] = Field(None, max_length=50, description="操作IP地址")
    user_agent: Optional[str] = Field(None, max_length=500, description="用户代理信息")
    status: int = Field(default=1, ge=0, le=1, description="操作状态：1=成功，0=失败")
    remark: Optional[str] = Field(None, max_length=500, description="备注信息")

    class Config:
        """配置类"""
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "admin",
                "action_type": "LOGIN",
                "module": "认证",
                "ip_address": "127.0.0.1",
                "user_agent": "Mozilla/5.0",
                "status": 1,
                "remark": "用户登录成功"
            }
        }


class OperationLogResponse(BaseModel):
    """
    操作日志响应模型
    用于返回日志详情
    """
    id: int = Field(..., description="日志ID")
    user_id: int = Field(..., description="操作用户ID")
    username: str = Field(..., description="操作用户名")
    action_type: str = Field(..., description="行为类型")
    module: str = Field(..., description="操作模块")
    ip_address: Optional[str] = Field(None, description="操作IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理信息")
    created_at: datetime = Field(..., description="操作时间")
    status: int = Field(..., description="操作状态：1=成功，0=失败")
    remark: Optional[str] = Field(None, description="备注信息")

    class Config:
        """配置类"""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "username": "admin",
                "action_type": "LOGIN",
                "module": "认证",
                "ip_address": "127.0.0.1",
                "user_agent": "Mozilla/5.0",
                "created_at": "2026-02-05T12:00:00",
                "status": 1,
                "remark": "用户登录成功"
            }
        }


class OperationLogQuery(BaseModel):
    """
    操作日志查询参数模型
    用于日志列表的筛选和分页
    """
    username: Optional[str] = Field(None, description="按用户名筛选")
    action_type: Optional[str] = Field(None, description="按行为类型筛选")
    module: Optional[str] = Field(None, description="按模块筛选")
    status: Optional[int] = Field(None, ge=0, le=1, description="按状态筛选")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")

    class Config:
        """配置类"""
        json_schema_extra = {
            "example": {
                "username": "admin",
                "action_type": "LOGIN",
                "module": "认证",
                "status": 1,
                "start_date": "2026-02-01T00:00:00",
                "end_date": "2026-02-05T23:59:59"
            }
        }


class OperationLogListResponse(BaseModel):
    """
    操作日志列表响应模型
    用于返回分页的日志列表
    """
    total: int = Field(..., description="总记录数")
    items: list[OperationLogResponse] = Field(..., description="日志列表")

    class Config:
        """配置类"""
        json_schema_extra = {
            "example": {
                "total": 100,
                "items": []
            }
        }


class OperationLogStatistics(BaseModel):
    """
    操作日志统计响应模型
    用于返回日志统计数据
    """
    total_logs: int = Field(..., description="总日志数")
    today_logs: int = Field(..., description="今日日志数")
    action_type_stats: dict[str, int] = Field(..., description="按行为类型统计")
    module_stats: dict[str, int] = Field(..., description="按模块统计")
    user_stats: dict[str, int] = Field(..., description="按用户统计（前10名）")

    class Config:
        """配置类"""
        json_schema_extra = {
            "example": {
                "total_logs": 1000,
                "today_logs": 50,
                "action_type_stats": {"LOGIN": 100, "QUERY": 500},
                "module_stats": {"认证": 100, "用户管理": 200, "知识图谱": 300},
                "user_stats": {"admin": 500, "user1": 300}
            }
        }
