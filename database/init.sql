-- 用户管理数据库初始化脚本
-- 数据库：workshop
-- 表：user_manage

-- 如果数据库不存在则创建
CREATE DATABASE IF NOT EXISTS `workshop` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `workshop`;

-- 如果表存在则删除
DROP TABLE IF EXISTS `user_manage`;

-- 创建用户管理表
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

-- 插入默认管理员用户 (用户名: admin, 密码: admin123)
-- 密码已 bcrypt 加密
INSERT INTO `user_manage` (`username`, `password`, `user_type`, `status`, `role_id`)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEmc0i', 1, 1, 1);

-- 插入测试普通用户 (密码: user123)
INSERT INTO `user_manage` (`username`, `password`, `user_type`, `status`, `role_id`)
VALUES
    ('user1', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 0, 1, 2),
    ('user2', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 0, 1, 3);

-- 显示初始化成功信息
SELECT '数据库初始化成功！' AS message;
SELECT id, username, user_type, status, created_at FROM user_manage;
