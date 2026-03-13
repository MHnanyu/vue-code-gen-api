# Vue Code Gen API

Vue3 Page Generator 后端 API 服务，基于 FastAPI + MongoDB 实现。

## 项目简介

本项目是 [Vue Code Gen](https://github.com/your-repo/vue-code-gen) 前端项目的后端 API 服务，提供以下核心功能：

- **AI 代码生成**：根据用户自然语言描述，生成 Vue3 项目代码（目前返回 Mock 数据，后续接入真实 AI）
- **会话管理**：管理用户对话会话，支持多轮对话上下文
- **消息存储**：保存对话历史记录，支持会话持久化

### 与前端项目的关系

```
┌─────────────────────────────────────┐     ┌─────────────────────────────────────┐
│        vue-code-gen (前端)          │     │     vue-code-gen-api (后端)         │
│                                     │     │                                     │
│  ┌─────────────┐  ┌─────────────┐  │     │  ┌─────────────┐  ┌─────────────┐  │
│  │   Chat UI   │  │  Code View  │  │     │  │  FastAPI    │  │  MongoDB    │  │
│  │             │  │             │  │     │  │  Routers    │  │  Database   │  │
│  └─────────────┘  └─────────────┘  │     │  └─────────────┘  └─────────────┘  │
│                                     │     │                                     │
│  用户输入需求 ──────────────────────────────→ 生成 Vue 代码                   │
│                                     │     │                                     │
│  ←────────────────────────────── 返回代码文件  │                                     │
│                                     │     │                                     │
└─────────────────────────────────────┘     └─────────────────────────────────────┘
```

### 核心流程

1. 用户在前端输入需求描述（如"生成一个登录页面"）
2. 前端调用 `/api/generate/initial` 接口（首次生成）或 `/api/generate/iterate` 接口（迭代修改）
3. 后端生成 Vue3 项目代码（MainPage.vue、HelloWorld.vue 等）
4. 前端使用 `buildProjectFiles()` 组合完整项目结构
5. 用户可在前端预览、编辑生成的代码

## 技术栈

- Python 3.10+
- FastAPI
- MongoDB 8.x
- Motor (异步 MongoDB 驱动)

## 前置条件

### 1. 安装 MongoDB

**Windows:**

1. 访问 [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. 下载 Windows msi 安装包
3. 运行安装程序，选择 "Complete" 安装类型
4. 勾选 "Install MongoDB as a Service"（作为 Windows 服务运行）
5. 安装完成后，将 `C:\Program Files\MongoDB\Server\8.2\bin` 添加到系统环境变量 PATH

**验证安装:**

```bash
mongod --version
```

**验证服务运行:**

```bash
# Windows
sc query MongoDB

# 或连接测试（需安装 mongosh）
mongosh
```

### 2. 安装 Python

推荐使用 Conda 管理 Python 环境：

```bash
# 创建虚拟环境
conda create -n python310 python=3.10

# 激活环境
conda activate python310
```

## 安装

```bash
# 激活 conda 环境
conda activate python310

# 安装依赖
pip install -r requirements.txt
```

## 配置

创建 `.env` 文件（可选，使用默认配置则无需创建）：

```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=vue_code_gen
```

## 数据库初始化

### 数据库设计

**数据库名称：** `vue_code_gen`

#### 1. sessions - 会话表

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 会话唯一标识 (UUID) |
| userId | string | 否 | 用户ID（P3 阶段使用，当前可为 null） |
| title | string | 否 | 会话标题 |
| componentLib | string | 否 | 选择的组件库，可选值：ElementUI、aui、ccui |
| messages | array | 否 | 消息列表（嵌入式文档） |
| files | array | 否 | 生成的文件列表 |
| createdAt | datetime | 是 | 创建时间 |
| updatedAt | datetime | 是 | 更新时间 |

**messages 嵌入式文档结构：**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 消息唯一标识 (UUID) |
| role | string | 是 | 角色：user / assistant |
| content | string | 是 | 消息内容 |
| timestamp | datetime | 是 | 消息时间 |

**索引：**
- `id`: 唯一索引
- `userId`: 普通索引
- `updatedAt`: 降序索引（用于列表排序）

#### 2. users - 用户表（预留，P3 优先级）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | string | 是 | 用户唯一标识 (UUID) |
| username | string | 是 | 用户名/邮箱 |
| password | string | 是 | 密码（加密存储） |
| nickname | string | 否 | 昵称 |
| createdAt | datetime | 是 | 创建时间 |
| updatedAt | datetime | 是 | 更新时间 |

**索引：**
- `id`: 唯一索引
- `username`: 唯一索引

### 执行初始化

```bash
# 确保已激活 conda 环境且 MongoDB 服务正在运行
conda activate python310

# 执行数据库初始化脚本
python scripts/init_db.py
```

初始化完成后会输出：
```
数据库初始化完成!
- 创建数据库: vue_code_gen
- 创建集合: sessions, users
- 创建索引: sessions.id(唯一), sessions.userId, sessions.updatedAt, users.id(唯一), users.username(唯一)
```

## 运行

```bash
# 确保已激活 conda 环境
conda activate python310

# 启动开发服务器
python -m uvicorn app.main:app --reload --port 8000
```

启动成功后访问：
- API 文档 (Swagger UI): http://localhost:8000/docs
- API 文档 (ReDoc): http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health
- 根路径: http://localhost:8000/

## 项目结构

```
vue-code-gen-api/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI 应用入口
│   ├── config.py         # 配置管理
│   ├── database.py       # MongoDB 连接
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── sessions.py   # 会话管理 API
│   │   └── generate.py   # 代码生成 API
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── response.py   # 统一响应格式
│   │   ├── session.py    # 会话数据模型
│   │   ├── message.py    # 消息数据模型
│   │   └── generate.py   # 生成请求/响应模型
│   ├── models/
│   │   └── __init__.py
│   └── services/
│       └── __init__.py
├── scripts/
│   └── init_db.py        # 数据库初始化脚本
├── requirements.txt
├── API.md                # API 接口文档
└── README.md
```

## API 接口

### 会话管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/sessions | 创建会话 |
| GET | /api/sessions | 获取会话列表 |
| GET | /api/sessions/{sessionId} | 获取会话详情 |
| DELETE | /api/sessions/{sessionId} | 删除会话 |
| PATCH | /api/sessions/{sessionId} | 更新会话标题 |
| PATCH | /api/sessions/{sessionId}/files | 更新会话文件 |
| POST | /api/sessions/{sessionId}/messages | 添加消息 |

### 代码生成

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/generate/initial | 初始生成代码（新会话） |
| POST | /api/generate/iterate | 迭代修改代码（多轮对话） |

详细接口说明请参考 [API.md](./API.md)

## 开发

### 运行开发服务器

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 生产环境

```bash
# 使用 gunicorn + uvicorn worker
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 部署到新服务器

```bash
# 1. 安装 MongoDB 并启动服务

# 2. 克隆代码
git clone <repository-url>
cd vue-code-gen-api

# 3. 创建并激活 Python 环境
conda create -n python310 python=3.10
conda activate python310

# 4. 安装依赖
pip install -r requirements.txt

# 5. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件，修改数据库连接信息

# 6. 初始化数据库
python scripts/init_db.py

# 7. 启动服务
python -m uvicorn app.main:app --port 8000
```

## 常见问题

### MongoDB 连接失败

1. 确认 MongoDB 服务正在运行：`sc query MongoDB`
2. 如果服务未运行，启动服务：`net start MongoDB`
3. 检查 `.env` 中的 `MONGODB_URL` 配置是否正确

### 端口被占用

修改启动命令中的 `--port` 参数：

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### 数据库初始化失败

1. 确认 MongoDB 服务正在运行
2. 确认已安装依赖：`pip install -r requirements.txt`
3. 检查 `.env` 中的数据库连接配置
