# 车间资源知识图谱系统

基于 FastAPI（后端）和 Vue 3（前端）构建的车间资源知识图谱管理系统，集成 MySQL 用户管理系统和 Neo4j 图数据库知识图谱可视化。

## 项目简介

本系统是一个车间故障诊断知识图谱平台，通过可视化展示操作、现象、故障部位、原因等实体之间的关系，帮助用户快速定位和解决车间设备故障。

### 核心功能

- **知识图谱可视化**：交互式图谱展示，支持节点展开/折叠
- **智能检索**：基于 title 字段的关键词搜索
- **节点分类展示**：不同类型节点使用不同颜色区分
- **动态布局**：节点展开时流畅动画，稳定后易于操作
- **用户权限管理**：基于 JWT 的身份认证和角色权限控制

## 项目结构

```
test/
├── backend/                      # FastAPI 后端
│   ├── app/
│   │   ├── api/                 # API 路由
│   │   │   └── v1/
│   │   │       ├── endpoints/   # 接口端点
│   │   │       │   ├── auth.py              # 用户认证
│   │   │       │   ├── users.py             # 用户管理
│   │   │       │   └── knowledge_graph.py   # 知识图谱
│   │   │       └── api.py       # API 路由聚合
│   │   ├── core/                # 核心功能
│   │   │   ├── config.py        # 配置管理
│   │   │   ├── neo4j_client.py  # Neo4j 客户端
│   │   │   ├── security.py      # JWT 和密码加密
│   │   │   └── deps.py          # 依赖注入
│   │   ├── models/              # 数据库模型
│   │   │   └── user.py          # 用户模型
│   │   ├── schemas/             # Pydantic 数据模型
│   │   │   ├── user.py          # 用户数据模型
│   │   │   └── knowledge_graph.py  # 知识图谱数据模型
│   │   ├── services/            # 业务逻辑层
│   │   │   ├── user_service.py  # 用户服务
│   │   │   └── knowledge_graph_service.py  # 知识图谱服务
│   │   ├── main.py              # 应用入口
│   │   └── init_db.py           # 数据库初始化
│   └── tests/                   # 后端测试
│       ├── test_knowledge_graph.py    # 图谱测试
│       └── test_node_neighbors.py      # 节点展开测试
│
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── api/                 # API 调用封装
│   │   │   ├── index.js         # Axios 配置
│   │   │   ├── user.js          # 用户 API
│   │   │   └── knowledge-graph.js  # 知识图谱 API
│   │   ├── components/          # 公共组件
│   │   │   └── GraphVisualization.vue  # 图谱可视化组件
│   │   ├── layouts/             # 布局组件
│   │   │   └── MainLayout.vue   # 主布局
│   │   ├── router/              # Vue Router 路由
│   │   │   └── index.js
│   │   ├── views/               # 页面组件
│   │   │   ├── Login.vue        # 登录页
│   │   │   ├── Users.vue        # 用户管理页
│   │   │   └── KnowledgeGraph.vue  # 知识图谱页
│   │   ├── App.vue              # 根组件
│   │   └── main.js              # 应用入口
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── database/                    # 数据库脚本
│   └── init.sql                 # MySQL 初始化脚本
│
├── requirements.txt             # Python 依赖
└── README.md                    # 项目文档
```

## 功能特性

### 知识图谱功能

- **关键词搜索**：根据节点 title 字段进行模糊匹配搜索
- **节点展开/折叠**：
  - 第一次点击节点：展开显示邻居节点和关系
  - 第二次点击节点：折叠移除之前展开的节点
  - 智能依赖清理：折叠时自动清理依赖节点
- **可视化展示**：
  - 不同类型节点使用不同颜色区分
  - 节点展开时流畅动画效果
  - 稳定后自动降低物理模拟，便于点击
  - 支持缩放、拖拽、适配视图等操作
- **图谱统计**：实时显示节点数、关系数、连接状态

### 节点类型与颜色

| 类型 | 颜色 | 说明 |
|------|------|------|
| Errorid | 🔴 红色 (#FF6B6B) | 错误ID |
| Caozuo | 🟢 青绿色 (#4ECDC4) | 操作 |
| Xianxiang | 🟠 橙色 (#FFA07A) | 现象 |
| GuzhangBuwei | 🟣 紫色 (#DDA0DD) | 故障部位 |
| Yuanyin | 🟡 黄色 (#F0E68C) | 原因 |

### 用户管理功能

- **身份认证**：基于 JWT 的登录系统
- **用户管理**：完整的 CRUD 操作
- **角色权限**：管理员和普通用户角色
- **状态管理**：启用/禁用用户
- **分页查询**：支持用户列表分页和筛选

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 普通用户 | user1 | user123 |
| 普通用户 | user2 | user123 |

## 数据库配置

### MySQL 数据库
- **主机**：localhost
- **端口**：3306
- **用户名**：root
- **密码**：123456
- **数据库**：workshop
- **数据表**：user_manage

### Neo4j 图数据库
- **URI**：bolt://localhost:7687
- **用户名**：neo4j
- **密码**：1314520gyf
- **数据库**：neo4j

## 快速开始

### 1. 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Neo4j 5.0+

### 2. 数据库初始化

#### MySQL 初始化
```bash
# 方式一：直接执行 SQL 脚本
mysql -u root -p123456 < database/init.sql

# 方式二：运行 Python 脚本（从 backend 目录）
cd backend
python init_db.py
```

#### Neo4j 启动（后台 Console 方式）

**Windows 系统**：
```bash
# 进入 Neo4j 安装目录
cd "C:\Program Files\Neo4j\bin"

# 后台启动 Neo4j
neo4j.bat start-console

# 或直接启动（前台运行）
neo4j.bat console
```

**Linux/Mac 系统**：
```bash
# 进入 Neo4j 安装目录
cd /path/to/neo4j/bin

# 后台启动 Neo4j
./neo4j start

# 或控制台模式启动
./neo4j console
```

**验证 Neo4j 启动**：
- 访问 Neo4j Browser：http://localhost:7474
- 使用用户名 `neo4j` 和密码 `1314520gyf` 登录

**停止 Neo4j**：
```bash
# Windows
neo4j.bat stop

# Linux/Mac
./neo4j stop
```

### 3. 启动后端

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 进入后端目录
cd backend

# 启动 FastAPI 服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端地址：http://localhost:8000
API 文档（Swagger）：http://localhost:8000/docs

### 4. 启动前端

```bash
# 进入前端目录
cd frontend

# 安装 Node.js 依赖
npm install

# 启动开发服务器
npm run dev
```

前端地址：http://localhost:5173

### 5. 测试知识图谱功能

```bash
# 进入后端目录
cd backend

# 运行知识图谱测试
python tests/test_knowledge_graph.py

# 运行节点展开测试
python tests/test_node_neighbors.py
```

## API 接口

### 认证接口
- `POST /api/v1/auth/login` - 用户登录
- `GET /api/v1/auth/me` - 获取当前用户信息
- `POST /api/v1/auth/logout` - 用户登出

### 用户管理接口
- `GET /api/v1/users` - 获取用户列表（支持分页和筛选）
- `GET /api/v1/users/{id}` - 根据 ID 获取用户
- `POST /api/v1/users` - 创建新用户（仅管理员）
- `PUT /api/v1/users/{id}` - 更新用户信息
- `DELETE /api/v1/users/{id}` - 删除用户（仅管理员）

### 知识图谱接口
- `GET /api/v1/knowledge-graph/health` - Neo4j 健康检查
- `GET /api/v1/knowledge-graph/statistics` - 获取图谱统计信息
- `POST /api/v1/knowledge-graph/search` - 关键词搜索节点
- `GET /api/v1/knowledge-graph/graph-data` - 获取图谱数据
- `GET /api/v1/knowledge-graph/neighbors/{node_id}` - 获取节点邻居（展开）

## 使用指南

### 知识图谱页面使用流程

1. **登录系统**：使用默认账号登录
2. **访问知识图谱**：点击导航菜单中的"知识图谱"
3. **搜索节点**：
   - 在搜索框输入关键词（如"重新开机"）
   - 点击搜索按钮或按回车
   - 系统显示匹配的节点
4. **展开节点**：
   - 点击任意节点，展开显示其邻居节点
   - 不同类型节点显示不同颜色
   - 节点展开时会有流畅动画效果
5. **折叠节点**：
   - 再次点击已展开的节点
   - 系统移除之前展开的节点和关系
6. **操作提示**：
   - 双击节点：适配视图聚焦到该节点
   - 工具栏：支持放大、缩小、适配视图

### 可视化操作

- **拖拽节点**：按住节点拖动调整位置
- **缩放图谱**：使用鼠标滚轮或工具栏按钮
- **选择节点**：点击节点进行选择
- **拖拽画布**：按住空白区域拖动画布

## 技术栈

### 后端技术
- **FastAPI** 0.104.1 - 现代化 Web 框架
- **SQLAlchemy** 2.0.23 - ORM 框架
- **PyMySQL** 1.1.2 - MySQL 驱动
- **Neo4j Driver** 5.x - 图数据库驱动
- **python-jose** 3.3.0 - JWT 认证
- **Passlib/Bcrypt** - 密码加密
- **Pydantic** 2.5.0 - 数据验证

### 前端技术
- **Vue 3** 3.3.8 - 渐进式框架
- **Vite** 5.0.4 - 构建工具
- **Vue Router** 4.2.5 - 路由管理
- **Pinia** 2.1.7 - 状态管理
- **Element Plus** 2.4.4 - UI 组件库
- **vis-network** 10.0.2 - 图谱可视化
- **Axios** 1.6.2 - HTTP 客户端

## 开发指南

### 配置修改

- **后端配置**：`backend/app/core/config.py`
  - MySQL 连接信息
  - Neo4j 连接信息
  - JWT 密钥配置

- **前端 API 配置**：`frontend/src/api/index.js`
  - API 基础路径
  - 请求拦截器
  - 响应拦截器

### 添加新功能

1. **后端接口**：
   - 在 `backend/app/api/v1/endpoints/` 创建新的接口文件
   - 在 `backend/app/schemas/` 添加数据模型
   - 在 `backend/app/services/` 添加业务逻辑
   - 在 `backend/app/api/v1/api.py` 注册路由

2. **前端页面**：
   - 在 `frontend/src/views/` 创建新页面组件
   - 在 `frontend/src/api/` 添加 API 调用
   - 在 `frontend/src/router/index.js` 添加路由

### 测试

- **后端测试**：位于 `backend/tests/` 目录
- **运行测试**：`python backend/tests/test_*.py`

## 常见问题

### Neo4j 连接失败
1. 检查 Neo4j 是否已启动
2. 验证连接配置（host、port、用户名、密码）
3. 查看 Neo4j 日志：`logs/neo4j.log`

### 前端无法访问后端 API
1. 检查后端是否已启动
2. 验证 API 地址配置
3. 检查网络连接和防火墙设置

### 节点颜色显示不正确
1. 确认节点类型标签是否正确
2. 检查颜色映射配置
3. 刷新浏览器缓存

## 更新日志

### v1.0.0 (2025-01-05)
- ✨ 初始版本发布
- ✅ 实现知识图谱可视化功能
- ✅ 支持节点搜索、展开/折叠
- ✅ 实现用户管理系统
- ✅ 添加节点类型颜色区分
- ✅ 实现展开动画效果

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。
