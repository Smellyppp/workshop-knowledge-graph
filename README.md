# 车间资源系统

基于 FastAPI（后端）和 Vue 3（前端）构建的全栈车间资源管理系统，使用 MySQL 数据库。

## 项目结构

```
test/
├── backend/                  # FastAPI 后端
│   └── app/
│       ├── api/             # API 路由
│       │   └── v1/
│       │       ├── endpoints/   # 认证和用户管理接口
│       │       └── api.py       # API 路由器
│       ├── core/            # 核心功能
│       │   ├── config.py        # 配置文件
│       │   ├── security.py      # JWT 和密码加密
│       │   └── deps.py          # 依赖注入
│       ├── models/          # 数据库模型
│       │   └── user.py          # 用户模型
│       ├── schemas/         # Pydantic 数据模型
│       │   └── user.py          # 用户数据模型
│       ├── services/        # 业务逻辑层
│       │   └── user_service.py  # 用户服务
│       ├── main.py          # 应用入口
│       └── init_db.py       # 数据库初始化脚本
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── api/            # API 调用封装
│   │   ├── layouts/        # 布局组件
│   │   ├── router/         # Vue Router 路由
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── views/          # 页面组件
│   │   ├── App.vue         # 根组件
│   │   └── main.js         # 入口文件
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── database/                # 数据库脚本
│   └── init.sql            # SQL 初始化脚本
└── requirements.txt         # Python 依赖
```

## 功能特性

- **身份认证**：基于 JWT 的登录系统
- **用户管理**：完整的 CRUD 操作（创建、读取、更新、删除）
- **角色权限控制**：管理员和普通用户角色
- **用户状态管理**：启用/禁用用户
- **密码安全**：Bcrypt 加密加盐存储
- **分页查询**：支持用户列表分页和筛选
- **响应式界面**：使用 Element Plus 组件库
- **API 文档**：FastAPI 自动生成的 Swagger 文档
- **健康检查**：提供系统健康状态检查接口
- **智能问答**：预留智能问答功能模块（开发中）

## 默认账号

| 角色     | 用户名 | 密码     |
|----------|--------|----------|
| 管理员   | admin  | admin123 |
| 普通用户 | user1  | user123  |
| 普通用户 | user2  | user123  |

## 数据库配置

- **主机**：localhost
- **端口**：3306
- **用户名**：root
- **密码**：123456
- **数据库**：workshop
- **数据表**：user_manage

## 安装运行

### 1. 数据库初始化

```bash
# 方式一：直接执行 SQL 脚本
mysql -u root -p123456 < database/init.sql

# 方式二：运行 Python 脚本（从 backend 目录）
cd backend
python init_db.py
```

### 2. 启动后端

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 启动 FastAPI 服务器
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端地址：http://localhost:8000
API 文档（Swagger）：http://localhost:8000/docs

### 3. 启动前端

```bash
# 安装 Node.js 依赖
cd frontend
npm install

# 启动开发服务器
npm run dev
```

前端地址：http://localhost:5173

## API 接口

### 基础接口

- `GET /` - 根路径接口
- `GET /health` - 健康检查接口

### 认证接口

- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息
- `POST /api/v1/auth/logout` - 用户登出

### 用户管理接口

- `GET /api/v1/users` - 获取用户列表（支持分页、按用户名/用户类型/状态筛选）
- `GET /api/v1/users/{id}` - 根据 ID 获取用户
- `POST /api/v1/users` - 创建新用户（仅管理员）
- `PUT /api/v1/users/{id}` - 更新用户信息（管理员可更新密码和状态，普通用户只能更新自己的密码）
- `DELETE /api/v1/users/{id}` - 删除用户（仅管理员）

## 技术栈

### 后端技术
- FastAPI - 现代化 Web 框架
- SQLAlchemy - ORM 框架
- PyMySQL - MySQL 驱动
- JWT (python-jose) - 身份认证
- Passlib/Bcrypt - 密码加密
- Pydantic - 数据验证

### 前端技术
- Vue 3 - 渐进式框架
- Vite - 构建工具
- Vue Router - 路由管理
- Pinia - 状态管理
- Element Plus - UI 组件库
- Axios - HTTP 客户端
