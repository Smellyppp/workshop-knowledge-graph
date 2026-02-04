"""
用户服务层
处理用户相关的业务逻辑
"""
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

from app.models.user import UserManage
from app.core.security import verify_password, get_password_hash


class UserService:
    """用户服务类"""

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[UserManage]:
        """
        通过用户名和密码认证用户

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码

        Returns:
            Optional[UserManage]: 认证成功返回用户对象，失败返回 None
        """
        user = db.query(UserManage).filter(UserManage.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        if user.status != 1:
            return None
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[UserManage]:
        """
        根据 ID 获取用户

        Args:
            db: 数据库会话
            user_id: 用户 ID

        Returns:
            Optional[UserManage]: 用户对象或 None
        """
        return db.query(UserManage).filter(UserManage.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[UserManage]:
        """
        根据用户名获取用户

        Args:
            db: 数据库会话
            username: 用户名

        Returns:
            Optional[UserManage]: 用户对象或 None
        """
        return db.query(UserManage).filter(UserManage.username == username).first()

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        username: Optional[str] = None,
        user_type: Optional[int] = None,
        status: Optional[int] = None
    ) -> Tuple[List[UserManage], int]:
        """
        获取用户列表（支持分页和筛选）

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            username: 用户名筛选（模糊匹配）
            user_type: 用户类型筛选
            status: 状态筛选

        Returns:
            Tuple[List[UserManage], int]: 用户列表和总数
        """
        query = db.query(UserManage)

        # 用户名模糊查询
        if username:
            query = query.filter(UserManage.username.like(f"%{username}%"))
        # 用户类型筛选
        if user_type is not None:
            query = query.filter(UserManage.user_type == user_type)
        # 状态筛选
        if status is not None:
            query = query.filter(UserManage.status == status)

        total = query.count()
        users = query.offset(skip).limit(limit).all()
        return users, total

    @staticmethod
    def create_user(db: Session, username: str, password: str, user_type: int = 0) -> UserManage:
        """
        创建新用户

        Args:
            db: 数据库会话
            username: 用户名
            password: 密码
            user_type: 用户类型

        Returns:
            UserManage: 创建的用户对象
        """
        hashed_password = get_password_hash(password)
        db_user = UserManage(
            username=username,
            password=hashed_password,
            user_type=user_type,
            status=1
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user_password(db: Session, user_id: int, new_password: str) -> Optional[UserManage]:
        """
        更新用户密码

        Args:
            db: 数据库会话
            user_id: 用户 ID
            new_password: 新密码

        Returns:
            Optional[UserManage]: 更新后的用户对象
        """
        user = db.query(UserManage).filter(UserManage.id == user_id).first()
        if user:
            user.password = get_password_hash(new_password)
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def update_user_status(db: Session, user_id: int, status: int) -> Optional[UserManage]:
        """
        更新用户状态

        Args:
            db: 数据库会话
            user_id: 用户 ID
            status: 新状态（0=禁用，1=启用）

        Returns:
            Optional[UserManage]: 更新后的用户对象
        """
        user = db.query(UserManage).filter(UserManage.id == user_id).first()
        if user:
            user.status = status
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        删除用户

        Args:
            db: 数据库会话
            user_id: 用户 ID

        Returns:
            bool: 删除成功返回 True
        """
        user = db.query(UserManage).filter(UserManage.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

    @staticmethod
    def username_exists(db: Session, username: str, exclude_id: Optional[int] = None) -> bool:
        """
        检查用户名是否已存在

        Args:
            db: 数据库会话
            username: 用户名
            exclude_id: 排除的用户 ID（用于更新时检查）

        Returns:
            bool: 用户名存在返回 True
        """
        query = db.query(UserManage).filter(UserManage.username == username)
        if exclude_id:
            query = query.filter(UserManage.id != exclude_id)
        return query.first() is not None
