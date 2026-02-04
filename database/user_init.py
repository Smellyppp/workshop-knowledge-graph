import pymysql

# =========================
# 连接 MySQL（root 用户）
# =========================
conn = pymysql.connect(
    host='127.0.0.1',    # 本地 MySQL
    port=3306,           # 端口
    user='root',         # 用户名
    password='123456',  # root 密码
    charset='utf8mb4',
    autocommit=True       # 自动提交事务
)

cursor = conn.cursor()

# =========================
# 1️⃣ 创建数据库
# =========================
cursor.execute("""
CREATE DATABASE IF NOT EXISTS `workshop` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
""")
cursor.execute("USE `workshop`;")

# =========================
# 2️⃣ 删除旧表
# =========================
cursor.execute("DROP TABLE IF EXISTS `user_manage`;")

# =========================
# 3️⃣ 创建用户管理表
# =========================
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

# =========================
# 4️⃣ 插入管理员和普通用户
# =========================
users = [
    # 管理员
    ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', 1, 1, 1),
    # 普通用户
    ('user1', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 0, 1, 2),
    ('user2', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 0, 1, 3)
]

insert_sql = """
INSERT INTO `user_manage` (`username`, `password`, `user_type`, `status`, `role_id`)
VALUES (%s, %s, %s, %s, %s);
"""

cursor.executemany(insert_sql, users)

# =========================
# 5️⃣ 显示表中记录
# =========================
cursor.execute("SELECT id, username, user_type, status, created_at FROM user_manage;")
for row in cursor.fetchall():
    print(row)

# =========================
# 6️⃣ 关闭连接
# =========================
cursor.close()
conn.close()
