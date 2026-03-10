"""
数据库初始化脚本
功能：创建数据库、表结构，并初始化管理员和测试用户（密码自动加密）
"""
import sys
import io
from pathlib import Path

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import pymysql
from passlib.context import CryptContext
from dotenv import load_dotenv

# =========================
# 加载环境变量
# =========================
# 获取 backend 目录下的 .env 文件
BASE_DIR = Path(__file__).parent.parent / "backend"
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE)

# =========================
# 数据库配置（从环境变量读取）
# =========================
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'charset': 'utf8mb4'
}

# 默认用户配置
DEFAULT_USERS = [
    {'username': 'admin', 'password': '123456', 'user_type': 1, 'role_id': 1},
    {'username': 'user1', 'password': '123456', 'user_type': 0, 'role_id': 2},
    {'username': 'user2', 'password': '123456', 'user_type': 0, 'role_id': 3},
]

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """对密码进行 bcrypt 加密"""
    password_bytes = password.encode('utf-8')[:72]
    return pwd_context.hash(password_bytes)


def init_database():
    """初始化数据库"""
    print("=" * 60)
    print("开始初始化数据库...")
    print("=" * 60)

    # 连接 MySQL
    conn = pymysql.connect(**DB_CONFIG, autocommit=True)
    cursor = conn.cursor()

    try:
        # =========================
        # 1. 创建数据库
        # =========================
        print("\n[1/5] 创建数据库...")
        db_name = os.getenv('DB_NAME', 'workshop')
        cursor.execute(f"""
            CREATE DATABASE IF NOT EXISTS `{db_name}`
            DEFAULT CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci;
        """)
        cursor.execute(f"USE `{db_name}`;")
        print(f"✓ 数据库 '{db_name}' 已就绪")

        # =========================
        # 2. 删除旧表
        # =========================
        print("\n[2/5] 清理旧表...")
        cursor.execute("DROP TABLE IF EXISTS `operation_log`;")
        cursor.execute("DROP TABLE IF EXISTS `user_manage`;")
        print("✓ 旧表已清理")

        # =========================
        # 3. 创建用户管理表
        # =========================
        print("\n[3/5] 创建用户管理表...")
        create_table_sql = """
            CREATE TABLE `user_manage` (
                `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
                `role_id` BIGINT DEFAULT NULL COMMENT '角色ID',
                `user_type` TINYINT NOT NULL DEFAULT 0 COMMENT '用户类型: 1=管理员, 0=普通用户',
                `username` VARCHAR(50) NOT NULL COMMENT '用户名',
                `password` VARCHAR(255) NOT NULL COMMENT '加密密码',
                `status` TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 1=启用, 0=禁用',
                `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                PRIMARY KEY (`id`),
                UNIQUE KEY `uk_username` (`username`),
                KEY `idx_user_type` (`user_type`),
                KEY `idx_status` (`status`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户管理表';
        """
        cursor.execute(create_table_sql)
        print("✓ user_manage 表已创建")

        # =========================
        # 4. 创建操作日志表
        # =========================
        print("\n[4/5] 创建操作日志表...")
        log_table_sql = """
            CREATE TABLE `operation_log` (
                `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '日志ID',
                `user_id` BIGINT NOT NULL COMMENT '操作用户ID',
                `username` VARCHAR(50) NOT NULL COMMENT '操作用户名',
                `action_type` VARCHAR(50) NOT NULL COMMENT '行为类型',
                `module` VARCHAR(50) NOT NULL COMMENT '操作模块',
                `ip_address` VARCHAR(50) DEFAULT NULL COMMENT '操作IP地址',
                `user_agent` VARCHAR(500) DEFAULT NULL COMMENT '用户代理信息',
                `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
                `status` TINYINT NOT NULL DEFAULT 1 COMMENT '操作状态: 1=成功, 0=失败',
                `remark` VARCHAR(500) DEFAULT NULL COMMENT '备注信息',
                PRIMARY KEY (`id`),
                KEY `idx_user_id` (`user_id`),
                KEY `idx_username` (`username`),
                KEY `idx_action_type` (`action_type`),
                KEY `idx_module` (`module`),
                KEY `idx_created_at` (`created_at`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';
        """
        cursor.execute(log_table_sql)
        print("✓ operation_log 表已创建")

        # =========================
        # 5. 插入默认用户（密码加密）
        # =========================
        print("\n[5/5] 插入默认用户...")
        insert_sql = """
            INSERT INTO `user_manage` (`username`, `password`, `user_type`, `status`, `role_id`)
            VALUES (%s, %s, %s, 1, %s);
        """

        for user in DEFAULT_USERS:
            hashed_password = get_password_hash(user['password'])
            cursor.execute(insert_sql, (
                user['username'],
                hashed_password,
                user['user_type'],
                user['role_id']
            ))
            user_type_str = "管理员" if user['user_type'] == 1 else "普通用户"
            print(f"  ✓ {user['username']} ({user_type_str}) - 密码: {user['password']}")

        # =========================
        # 6. 显示结果
        # =========================
        print("\n" + "=" * 60)
        print("数据库初始化完成！")
        print("=" * 60)

        cursor.execute("SELECT id, username, user_type, status, created_at FROM user_manage;")
        print("\n当前用户列表：")
        print("-" * 60)
        for row in cursor.fetchall():
            user_type_str = "管理员" if row[2] == 1 else "普通用户"
            status_str = "启用" if row[3] == 1 else "禁用"
            print(f"  ID: {row[0]} | 用户名: {row[1]} | 类型: {user_type_str} | 状态: {status_str}")

        print("\n" + "=" * 60)
        print("默认登录信息：")
        print("-" * 60)
        for user in DEFAULT_USERS:
            print(f"  {user['username']}: {user['password']}")
        print("=" * 60)

    except Exception as e:
        print(f"\n初始化失败: {e}")
        raise

    finally:
        cursor.close()
        conn.close()
        print("\n数据库连接已关闭。")


if __name__ == "__main__":
    import os
    init_database()
