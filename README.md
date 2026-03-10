# 车间资源知识图谱系统

基于 FastAPI（后端）和 Vue 3（前端）构建的车间资源知识图谱管理系统，集成 MySQL 用户管理系统、Neo4j 图数据库知识图谱可视化、智能问答和操作日志模块。

## 项目简介

本系统是一个车间故障诊断知识图谱平台，通过可视化展示操作、现象、故障部位、原因等实体之间的关系，帮助用户快速定位和解决车间设备故障。系统还提供智能问答功能和完整的操作日志审计。

### 核心功能

- **知识图谱可视化**：交互式图谱展示，支持节点展开/折叠
- **智能检索**：基于 title 字段的关键词搜索
- **节点分类展示**：不同类型节点使用不同颜色区分
- **动态布局**：节点展开时流畅动画，稳定后易于操作
- **用户权限管理**：基于 JWT 的身份认证和角色权限控制
- **智能问答**：基于 Qwen 大模型的 AI 故障诊断助手
- **操作日志**：完整的操作审计和日志管理

## 项目结构

```
WorkshopGraph/
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── api/                     # API 路由
│   │   │   └── v1/
│   │   │       ├── endpoints/       # 接口端点
│   │   │       │   ├── auth.py              # 用户认证
│   │   │       │   ├── users.py             # 用户管理
│   │   │       │   ├── knowledge_graph.py   # 知识图谱
│   │   │       │   ├── chat.py              # 智能问答
│   │   │       │   └── operation_log.py     # 操作日志
│   │   │       └── api.py         # API 路由聚合
│   │   ├── core/                    # 核心功能
│   │   │   ├── config.py            # 配置管理
│   │   │   ├── neo4j_client.py      # Neo4j 客户端
│   │   │   ├── security.py          # JWT 和密码加密
│   │   │   ├── deps.py              # 依赖注入
│   │   │   └── logger_helper.py     # 日志记录辅助
│   │   ├── models/                  # 数据库模型
│   │   │   ├── user.py              # 用户模型
│   │   │   └── operation_log.py     # 操作日志模型
│   │   ├── schemas/                 # Pydantic 数据模型
│   │   │   ├── user.py              # 用户数据模型
│   │   │   ├── knowledge_graph.py   # 知识图谱数据模型
│   │   │   ├── chat.py              # 智能问答数据模型
│   │   │   └── operation_log.py     # 操作日志数据模型
│   │   ├── services/                # 业务逻辑层
│   │   │   ├── user_service.py      # 用户服务
│   │   │   ├── knowledge_graph_service.py  # 知识图谱服务
│   │   │   ├── chat_service.py      # 智能问答服务
│   │   │   └── operation_log_service.py     # 操作日志服务
│   │   └── main.py                  # 应用入口
│   ├── .env                         # 环境配置（不提交）
│   └── .env.example                 # 环境配置示例
│
├── frontend/                        # Vue 3 前端
│   ├── src/
│   │   ├── api/                     # API 调用封装
│   │   │   ├── index.js             # Axios 配置
│   │   │   ├── user.js              # 用户 API
│   │   │   ├── knowledge-graph.js   # 知识图谱 API
│   │   │   ├── chat.js              # 智能问答 API
│   │   │   └── operation-log.js     # 操作日志 API
│   │   ├── components/              # 公共组件
│   │   │   └── GraphVisualization.vue  # 图谱可视化组件
│   │   ├── layouts/                 # 布局组件
│   │   │   └── MainLayout.vue       # 主布局
│   │   ├── router/                  # Vue Router 路由
│   │   │   └── index.js
│   │   ├── stores/                  # Pinia 状态管理
│   │   │   └── auth.js              # 认证状态
│   │   ├── views/                   # 页面组件
│   │   │   ├── Login.vue            # 登录页
│   │   │   ├── Users.vue            # 用户管理页
│   │   │   ├── KnowledgeGraph.vue   # 知识图谱页
│   │   │   ├── Chat.vue             # 智能问答页
│   │   │   └── OperationLogs.vue    # 操作日志页
│   │   ├── App.vue                  # 根组件
│   │   └── main.js                  # 应用入口
│   ├── index.html                   # HTML 入口
│   ├── package.json                 # 前端依赖声明
│   ├── package-lock.json            # 依赖版本锁定（需提交）
│   └── vite.config.js               # Vite 配置
│
├── database/                        # 数据库脚本
│   └── db_init.py                   # 数据库初始化脚本
│
├── requirements.txt                 # Python 依赖
├── .gitignore                       # Git 忽略配置
└── README.md                        # 项目文档
```

## 功能特性

### 知识图谱功能

- **智能搜索**：
  - 支持多字段智能匹配（设备名称、姓名、工艺名称、物料名称、故障现象等）
  - 搜索关键词示例："数控"、"张三"、"焊接"、"电机"
- **节点详情**：
  - 点击节点右侧弹出详情面板
  - 显示节点所有属性信息（设备编号、型号、工位、技能等级等）
- **节点展开/折叠**：
  - 点击节点展开显示邻居节点和关系
  - 再次点击节点折叠移除之前展开的节点
  - 智能依赖清理：折叠时自动清理依赖节点
- **可视化展示**：
  - 节点显示名称而非长ID
  - 不同类型节点使用不同颜色区分
  - 节点展开时流畅动画效果
  - 稳定后自动降低物理模拟，便于点击
  - 支持缩放、拖拽、适配视图等操作
- **图谱统计**：实时显示节点数、关系数、连接状态

### 节点类型与颜色

| 类型 | 颜色 | 说明 |
|------|------|------|
| 设备 | 🔵 蓝色 | 加工/检测/物流/辅助设备 |
| 人员 | 🟢 绿色 | 操作/技术/管理人员 |
| 工艺 | 🟠 橙色 | 加工/检测/装配工艺 |
| 物料 | 🟡 黄色 | 原材料/半成品/成品/辅料 |
| 故障 | 🔴 红色 | 故障记录 |

### 智能问答功能

- **AI 故障诊断**：基于 Qwen 大模型的智能助手
- **对话记忆**：支持多轮对话上下文
- **快捷问题**：预设常用问题模板
- **实时响应**：流式输出 AI 回复
- **对话管理**：支持清除对话历史

### 操作日志功能

- **日志记录**：自动记录所有用户操作
- **统计面板**：显示总日志数、今日日志、活跃用户等
- **多维度筛选**：按用户名、行为类型、模块、状态、时间筛选
- **权限控制**：仅管理员可查看操作日志
- **分页查询**：支持大量日志数据的分页展示

### 用户管理功能

- **身份认证**：基于 JWT 的登录系统
- **用户管理**：完整的 CRUD 操作
- **角色权限**：管理员和普通用户角色
- **状态管理**：启用/禁用用户
- **分页查询**：支持用户列表分页和筛选

## 环境要求

| 组件 | 测试版本 | 说明 |
|------|------|------|
| Python | 3.10 | 后端运行环境 |
| Node.js | v24.14.0 | 前端构建环境 |
| MySQL | 8.0.43 | 用户/日志数据库 |
| Neo4j | - | 图数据库 |

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd WorkshopGraph
```

### 2. 数据库初始化

#### MySQL 初始化

```bash
# 运行 Python 脚本
cd database
python db_init.py
```

#### Neo4j 启动
```bash
# 进入 Neo4j 安装目录
cd "C:\Program Files\Neo4j\bin"

# 启动 Neo4j
neo4j.bat start-console

# 或控制台模式（前台运行）
neo4j.bat console
```

**验证 Neo4j 启动**：
- 访问：http://localhost:7474
- 使用用户名和密码登录

### 3. 后端配置

```bash
# 进入后端目录
cd backend

# 复制环境配置文件
cp .env.example .env

# 编辑 .env 文件，配置数据库连接和 API 密钥
```

`.env` 配置示例：

```env
# =========================
# MySQL 数据库配置
# =========================
DB_HOST=localhost          # MySQL 主机地址
DB_PORT=3306               # MySQL 端口
DB_USER=root               # MySQL 用户名
DB_PASSWORD=123456         # MySQL 密码
DB_NAME=workshop           # 数据库名称

# =========================
# Neo4j 图数据库配置
# =========================
NEO4J_URI=bolt://localhost:7687     # Neo4j 连接地址
NEO4J_USER=neo4j                    # Neo4j 用户名
NEO4J_PASSWORD=12345678             # Neo4j 密码
NEO4J_DATABASE=neo4j                # Neo4j 数据库名称

# =========================
# JWT 认证配置
# =========================
SECRET_KEY=your-secret-key-change-in-production    # JWT 密钥（生产环境请修改）
ALGORITHM=HS256                                    # JWT 加密算法
ACCESS_TOKEN_EXPIRE_MINUTES=1440                   # Token 有效期（分钟，默认 24 小时）

# =========================
# Qwen AI 配置
# =========================
QWEN_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1  # Qwen API 地址
QWEN_API_KEY=your-qwen-api-key-here                            # Qwen API 密钥
QWEN_MODEL=qwen-plus                                            # 模型名称

# =========================
# 前端配置
# =========================
FRONTEND_URL=http://localhost:5173    # 前端地址（用于 CORS 配置）
```

### 4. 安装依赖并启动后端

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 启动 FastAPI 服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端地址：http://localhost:8000
API 文档：http://localhost:8000/docs

### 5. 启动前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端地址：http://localhost:5173

### 6. 默认登录账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | 123456 |
| 普通用户 | user1 | 123456 |
| 普通用户 | user2 | 123456 |

> **提示**：首次使用前请先运行 `database/db_init.py` 初始化数据库。

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
- `POST /api/v1/knowledge-graph/search` - 关键词搜索节点（支持多字段搜索）
- `GET /api/v1/knowledge-graph/graph-data` - 获取图谱数据
- `GET /api/v1/knowledge-graph/neighbors/{node_id}` - 获取节点邻居（展开）

### 智能问答接口
- `POST /api/v1/chat/message` - 发送消息给 AI 助手
- `POST /api/v1/chat/clear` - 清除对话历史

### 操作日志接口（仅管理员）
- `GET /api/v1/logs` - 获取操作日志列表（支持分页和筛选）
- `GET /api/v1/logs/{log_id}` - 获取操作日志详情
- `GET /api/v1/logs/statistics/summary` - 获取操作日志统计信息
- `GET /api/v1/logs/recent` - 获取最近操作日志

## 使用指南

### 知识图谱页面

1. 登录系统后，点击导航菜单中的"知识图谱"
2. 在搜索框输入关键词进行搜索：
   - 支持搜索设备名称、设备型号、姓名、工艺名称、物料名称、故障名称、故障现象等
   - 支持中文关键词模糊匹配
   - 示例关键词："数控"、"张三"、"焊接"、"电机"、"轴承"
3. 点击搜索按钮，系统显示匹配的节点
4. **点击节点**：右侧弹出详情面板，显示该节点的所有属性信息
5. **再次点击节点**：展开/折叠其邻居节点
6. 双击节点可聚焦视图

### 智能问答页面

1. 点击导航菜单中的"智能问答"
2. 在输入框输入故障问题描述
3. 点击发送或按回车，AI 助手会给出诊断建议
4. 点击预设问题可快速提问

### 操作日志页面（仅管理员）

1. 使用管理员账号登录
2. 点击导航菜单中的"操作日志"
3. 查看统计信息和日志列表
4. 可按条件筛选日志

## 技术栈

### 后端技术
- **FastAPI** - 现代化 Web 框架
- **SQLAlchemy** - ORM 框架
- **PyMySQL** - MySQL 驱动
- **Neo4j Driver** - 图数据库驱动
- **LangChain** - AI 应用框架
- **python-jose** - JWT 认证
- **Passlib/Bcrypt** - 密码加密
- **Pydantic** - 数据验证

### 前端技术
- **Vue 3** - 渐进式框架
- **Vite** - 构建工具
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **Element Plus** - UI 组件库
- **vis-network** - 图谱可视化
- **Axios** - HTTP 客户端

## 常见问题

### Neo4j 连接失败
1. 检查 Neo4j 是否已启动
2. 验证 `.env` 中的连接配置（host、port、用户名、密码）
3. 查看 Neo4j 日志

### 前端无法访问后端 API
1. 检查后端是否已启动（http://localhost:8000）
2. 检查浏览器控制台是否有跨域错误
3. 验证 `vite.config.js` 中的代理配置

### AI 问答无法使用
1. 检查 `.env` 中 `QWEN_API_KEY` 是否正确配置
2. 验证网络连接
3. 查看后端日志排查错误

### 数据库连接失败
1. 检查 MySQL/Neo4j 服务是否启动
2. 验证 `.env` 中的数据库配置
3. 运行 `database/db_init.py` 重新初始化数据库

## 更新日志

### v1.4.0 (2026-03-10)
- ✨ 优化知识图谱搜索功能
  - 支持多字段智能匹配（设备名称、姓名、工艺名称、物料名称、故障现象等）
- ✨ 节点显示优化
  - 节点显示名称而非长ID
  - 点击节点右侧弹出详情面板显示所有属性
- ✅ 更新节点类型与颜色映射（适配车间数据：设备、人员、工艺、物料、故障）

### v1.3.0 (2026-03-10)
- ✅ 实现完整的操作审计功能
- ✅ 优化配置管理，所有敏感配置移至 `.env`
- ✅ 完善数据库初始化脚本

### v1.2.0 (2026-02-05)
- ✨ 新增智能问答模块
- ✨ 新增操作日志模块
- ✅ 优化响应拦截器处理
- ✅ 修复前端数据访问路径问题

### v1.1.0 (2025-01-20)
- ✨ 添加节点展开/折叠功能
- ✅ 优化图谱可视化效果
- ✅ 实现展开动画
- ✅ 添加依赖节点清理逻辑

### v1.0.0 (2025-01-05)
- ✨ 初始版本发布
- ✅ 实现知识图谱可视化功能
- ✅ 支持节点搜索
- ✅ 实现用户管理系统
- ✅ 添加节点类型颜色区分

## 许可证

MIT License
