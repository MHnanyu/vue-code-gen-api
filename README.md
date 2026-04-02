# Design AI - Backend Service

> **体验设计 Agent（Design AI）后端服务**

Design AI 是一款 AI 驱动的体验设计智能体，能够理解自然语言需求（文本描述、UI 截图、产品文档），自动完成从需求理解到 Vue 3 原型页面代码生成的全流程。后端基于多步 AI Pipeline 架构，集成多个 AI 模型协同工作，支持多组件库（ElementUI、CcUI、aui），并通过 SSE 实时推送设计生成进度。

---

## 目录

- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [数据库初始化](#数据库初始化)
- [核心功能](#核心功能)
- [代码生成 Pipeline](#代码生成-pipeline)
- [API 接口概览](#api-接口概览)
- [数据模型](#数据模型)
- [AI 服务架构](#ai-服务架构)
- [SSE 事件类型](#sse-事件类型)
- [Mock 模式](#mock-模式)
- [详细 API 文档](#详细-api-文档)

---

## 技术栈

| 分类 | 技术 | 说明 |
|------|------|------|
| 语言 | Python 3.10+ | |
| Web 框架 | FastAPI >= 0.115.0 | 异步 ASGI 框架 |
| ASGI 服务器 | Uvicorn >= 0.30.0 | |
| 数据库 | MongoDB | 通过 Motor 异步驱动 |
| 数据校验 | Pydantic >= 2.10.0 | 请求/响应模型 |
| 配置管理 | pydantic-settings + python-dotenv | 从 .env 加载配置 |
| HTTP 客户端 | httpx >= 0.27.0 | 异步调用 AI API |
| 文件上传 | python-multipart >= 0.0.9 | |
| 唯一标识 | uuid6 | UUID6 生成 |

### AI 模型集成

| 模型 | 用途 |
|------|------|
| GLM-5（智谱 AI） | 主力代码生成模型 |
| GLM-4V-FlashX（智谱 AI） | 图片/视觉分析，提取 UI 布局结构 |
| MiniMax-M2.7 | 备选代码生成，结果摘要 |
| OpenClaw | Agent 模式代码生成与 UX 优化（CcUI / ElementUI 专用 Skill） |

---

## 项目结构

```
vue-code-gen-api/
├── .env.example              # 环境变量模板
├── .gitignore
├── requirements.txt          # Python 依赖
├── API.md                    # 详细 API 文档（中文）
│
├── app/                      # 主应用包
│   ├── __init__.py
│   ├── main.py               # FastAPI 应用入口、生命周期、CORS、静态文件
│   ├── config.py             # Pydantic Settings 配置管理
│   ├── database.py           # Motor 异步 MongoDB 连接管理
│   ├── pipeline.py           # 多步代码生成 Pipeline（核心逻辑）
│   ├── prompts.py            # CcUI / ElementUI 生成与优化 Prompt
│   │
│   ├── prompts/              # Prompt 模板文件
│   │   └── requirement_template.md  # 需求标准化 Prompt（154 行）
│   │
│   ├── routers/              # API 路由
│   │   ├── generate.py       # 代码生成相关接口（上传、初始生成、迭代、取消）
│   │   └── sessions.py       # 会话与消息管理接口
│   │
│   ├── schemas/              # Pydantic 数据模型
│   │   ├── generate.py       # 生成请求/响应模型、SSE 事件模型
│   │   ├── session.py        # Session、Message、StepMessage 模型
│   │   ├── message.py        # MessageCreate、CodeFile 模型
│   │   └── response.py       # 通用 Response[T]、ErrorResponse、ErrorCode
│   │
│   ├── services/             # 业务逻辑 / AI 服务
│   │   ├── ai_service.py     # AIService 抽象基类
│   │   ├── ai_factory.py     # AI 服务工厂（根据配置创建实例）
│   │   ├── glm5_service.py   # GLM-5 实现（智谱 AI）
│   │   ├── glm4v_service.py  # GLM-4V 视觉模型实现
│   │   ├── minimax_service.py # MiniMax 实现 + 摘要工具函数
│   │   ├── openclaw_service.py # OpenClaw Agent 服务实现
│   │   ├── requirement_service.py  # 需求标准化服务
│   │   └── attachment_service.py   # 文件/图片/文本附件处理
│   │
│   ├── utils/                # 工具模块
│   │   ├── sse.py            # SSE 事件发送器
│   │   ├── output.py         # 文件输出/保存、会话 DB 更新、回滚逻辑
│   │   ├── cancellation.py   # 任务取消（asyncio.Event + 客户端断连检测）
│   │   └── json_helper.py    # JSON 解析与自动修复（处理 AI 输出格式异常）
│   │
│   └── mock/                 # Mock 模式（开发/测试用）
│       ├── generate_mock.py  # 模拟 Vue 组件文件数据
│       └── stream_mock.py    # 模拟 SSE 流式生成过程
│
├── scripts/
│   └── init_db.py            # 数据库初始化脚本（创建集合与索引）
│
├── uploads/                  # 上传文件存储目录（gitignored）
└── output/                   # 生成结果存储目录（gitignored）
```

---

## 快速开始

### 前置条件

- Python 3.10+
- MongoDB（本地运行或远程连接）
- AI 服务 API Key（至少配置一个）

### 安装与运行

```bash
# 1. 克隆项目
git clone <repository-url>
cd vue-code-gen-api

# 2. 创建虚拟环境并激活
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填入必要的 API Key

# 5. 初始化数据库（创建索引）
python scripts/init_db.py

# 6. 启动服务
python -m uvicorn app.main:app --reload --port 8000
```

服务启动后：

| 地址 | 说明 |
|------|------|
| http://localhost:8000 | 服务根路径 |
| http://localhost:8000/docs | Swagger UI 交互式文档 |
| http://localhost:8000/redoc | ReDoc 文档 |
| http://localhost:8000/health | 健康检查（含 MongoDB 连通状态） |

---

## 环境配置

复制 `.env.example` 为 `.env` 并按需配置：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB 连接地址 |
| `DATABASE_NAME` | `vue_code_gen` | 数据库名称 |
| `AI_PROVIDER` | `glm5` | 当前代码生成 AI 提供商（`glm5` / `minimax`） |
| `GLM5_API_KEY` | （必填） | 智谱 AI GLM-5 API Key |
| `GLM5_API_URL` | `https://open.bigmodel.cn/api/coding/paas/v4/chat/completions` | GLM-5 API 地址 |
| `GLM5_MODEL` | `glm-5` | GLM-5 模型名称 |
| `MINIMAX_API_KEY` | （空） | MiniMax API Key |
| `MINIMAX_API_URL` | （空） | MiniMax API 地址 |
| `MINIMAX_MODEL` | `MiniMax-M2.7` | MiniMax 模型名称 |
| `GLM4V_API_KEY` | （空） | GLM-4V 视觉模型 API Key |
| `GLM4V_API_URL` | `https://open.bigmodel.cn/api/paas/v4/chat/completions` | GLM-4V API 地址 |
| `GLM4V_MODEL` | `glm-4.6v-flashx` | GLM-4V 模型名称 |
| `OPENCLAW_API_URL` | `http://127.0.0.1:18789/v1/responses` | OpenClaw Agent 服务地址 |
| `OPENCLAW_TOKEN` | （空） | OpenClaw 认证 Token |
| `OPENCLAW_AGENT_ID` | `main` | OpenClaw Agent ID |
| `OPENCLAW_MODEL` | `openclaw` | OpenClaw 模型名称 |
| `MOCK_MODE` | `False` | 是否启用 Mock 模式（开发调试用） |

---

## 数据库初始化

运行初始化脚本创建必要的集合和索引：

```bash
python scripts/init_db.py
```

创建的索引：

| 集合 | 索引字段 | 类型 |
|------|----------|------|
| `sessions` | `id` | Unique |
| `sessions` | `userId` | 普通 |
| `sessions` | `updatedAt` | 降序 |
| `users` | `id` | Unique |
| `users` | `username` | Unique |

---

## 核心功能

1. **AI 驱动的需求理解**：将自然语言描述（一句话或完整文档）自动规范化为结构化 UX 需求规格，标注原始内容与 AI 推断内容
2. **多模态设计输入**：支持文本描述、UI 截图/设计稿（GLM-4V 视觉分析提取布局）、产品文档（Markdown/文本）等多种输入形式
3. **多步设计 Pipeline**：4 阶段流水线（附件处理 -> 需求标准化 -> 代码生成 -> UX 优化），通过 SSE 实时推送各阶段进度
4. **多 AI 模型协同**：GLM-5（代码生成）、GLM-4V（视觉理解）、MiniMax（备选生成 + 摘要）、OpenClaw Agent（专属 Skill 生成/优化），工厂模式按配置切换
5. **多组件库适配**：针对 ElementUI、CcUI、aui 提供专属 Prompt 和优化 Skill，生成符合各组件库规范的原型代码
6. **多轮对话式设计迭代**：通过自然语言对话持续修改和优化设计，完整保留会话历史与文件快照
7. **智能重试与容错**：失败任务可从任意 Pipeline 步骤重试（`fromStep`），自动缓存已成功步骤；JSON 解析自修复处理 AI 输出格式异常
8. **实时取消与中断**：通过 API 端点主动取消，或自动检测客户端断连中断任务
9. **会话持久化**：MongoDB 存储完整对话历史，每条消息附带文件快照以支持回滚和上下文延续
10. **Mock 模式**：支持无 AI 调用的开发/测试模式，方便前端联调

---

## 设计生成 Pipeline

### 初始生成（`/api/generate/initial/stream`）

```
用户输入（文本 + 附件）
        │
        ▼
┌─────────────────────────────────┐
│  Step 0: 附件处理 (attachment)    │
│  · 图片 -> GLM-4V 视觉分析        │
│  · 文本/MD -> 直接读取内容         │
│  · 合并为 final_prompt            │
│  输出: step0_final_prompt.md      │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  Step 1: 需求标准化 (requirement)  │
│  · AI 驱动的 UX 需求规范化         │
│  · 区分标准文档 vs 一句话描述       │
│  · 标注 [✓] 原始 / [※] 推断内容    │
│  输出: step1_requirement.md       │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  Step 2: 代码生成 (generation)     │
│  CcUI -> OpenClaw Agent           │
│  ElementUI/aui -> GLM-5/MiniMax   │
│  · Vue 3 Composition API          │
│  · <script setup lang="ts">       │
│  · 纯 JSON 输出格式                │
│  输出: step2_generation.json + .vue│
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  Step 3: UX 优化 (optimization)   │
│  · OpenClaw Agent                │
│  CcUI -> ccui-ux-guardian Skill  │
│  ElementUI -> enterprise-vue-refiner│
│  · 仅优化样式和布局                │
│  输出: step3_optimization.json + .vue│
└─────────────────────────────────┘
        │
        ▼
   生成完成 (done)
```

### 迭代设计（`/api/generate/iterate/stream`）

单步流程：直接将用户修改请求 + 已有设计文件发送给 AI 服务，生成修改后的代码。支持一对一文件映射，保留所有已有文件，实现对话式设计迭代。

---

## API 接口概览

### 基础接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 服务信息（名称、版本） |
| `GET` | `/health` | 健康检查（含 MongoDB 连通状态） |

### 代码生成

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/upload` | 上传设计素材（图片/Markdown/文本，最多 5 个） |
| `POST` | `/api/generate/initial/stream` | SSE 流式初始设计生成（4 步 Pipeline） |
| `POST` | `/api/generate/iterate/stream` | SSE 流式迭代设计修改 |
| `POST` | `/api/generate/cancel` | 取消进行中的设计任务 |
| `POST` | `/api/image/analyze` | 分析设计图片（URL 或 Base64）提取 UI 布局 |
| `POST` | `/api/image/analyze-file` | 分析上传的设计图片文件 |

### 会话管理

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/sessions` | 创建会话 |
| `GET` | `/api/sessions` | 获取会话列表（分页：`page`、`pageSize`） |
| `GET` | `/api/sessions/{sessionId}` | 获取会话详情（含所有消息） |
| `DELETE` | `/api/sessions/{sessionId}` | 删除会话 |
| `PATCH` | `/api/sessions/{sessionId}` | 更新会话标题 |
| `PATCH` | `/api/sessions/{sessionId}/files` | 更新会话文件 |
| `POST` | `/api/sessions/{sessionId}/messages` | 添加消息 |
| `DELETE` | `/api/sessions/{sessionId}/messages/{messageId}` | 删除消息 |

### 静态文件

| 路径 | 说明 |
|------|------|
| `/uploads/*` | 上传文件访问 |
| `/output/*` | 生成结果文件访问 |

### 错误码

| 错误码 | 说明 |
|--------|------|
| `0` | 成功 |
| `1001` | 参数错误 |
| `1002` | 会话不存在 |
| `1003` | AI 设计生成失败 |
| `1004` | 请求超时 |
| `2001` | 未授权（预留） |
| `2002` | Token 过期（预留） |
| `5000` | 服务器内部错误 |

---

## 数据模型

### Session（会话）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string (UUID) | 唯一标识 |
| `userId` | string / null | 用户 ID（预留） |
| `title` | string / null | 会话标题 |
| `componentLib` | string | 组件库：`ElementUI` / `aui` / `ccui` |
| `messages` | Message[] | 消息列表（内嵌文档） |
| `files` | CodeFile[] | 最新生成文件快照 |
| `createdAt` | datetime (UTC) | 创建时间 |
| `updatedAt` | datetime (UTC) | 更新时间 |

### Message（消息）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string (UUID) | 唯一标识 |
| `role` | string | `user` 或 `assistant` |
| `content` | string | 消息内容 |
| `attachments` | Attachment[] / null | 附件列表 |
| `failedStep` | int / null | 失败步骤编号（用于重试） |
| `stages` | object / null | Pipeline 各阶段结果 |
| `stepMessages` | StepMessage[] / null | 步骤进度信息 |
| `files` | CodeFile[] / null | 该消息点的文件快照 |
| `timestamp` | datetime (UTC) | 消息时间 |

### Attachment（附件）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 文件标识 |
| `url` | string | 文件 URL 路径 |
| `name` | string | 原始文件名 |
| `type` | string | `image` / `text` / `markdown` |
| `size` | int / null | 文件大小（字节） |

### CodeFile（代码文件）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 文件标识 |
| `name` | string | 文件名（如 `MainPage.vue`） |
| `path` | string | 文件路径（如 `/src/MainPage.vue`） |
| `type` | string | 固定值 `file` |
| `language` | string / null | 固定值 `vue` |
| `content` | string / null | Vue SFC 代码内容 |
| `children` | CodeFile[] / null | 嵌套文件结构 |

---

## AI 服务架构

```
AIServiceFactory
├── GLM5Service        # 智谱 GLM-5（代码生成）
├── MiniMaxService     # MiniMax M2.7（代码生成 + 摘要）
├── GLM4VService       # 智谱 GLM-4V（图片分析）
└── OpenClawService    # OpenClaw Agent（Agent 模式生成/优化）
```

- `AIService` 抽象基类定义了 `chat_completion` 和 `generate_vue_files` 接口
- `AIServiceFactory` 根据 `.env` 中的 `AI_PROVIDER` 配置创建对应实例
- OpenClaw 独立于工厂，由 Pipeline 直接调用，支持 `vue3-ccui-generator`、`ccui-ux-guardian`、`enterprise-vue-refiner` 等专属 Skill

---

## SSE 事件类型

生成过程中通过 Server-Sent Events 实时推送以下事件：

| 事件 | 说明 | 关键字段 |
|------|------|----------|
| `stage_start` | 阶段开始 | `stage`, `stageName`, `isRetry`, `taskId` |
| `stage_progress` | 阶段进度更新 | `stage`, `stageName`, `message`, `progress` |
| `stage_complete` | 阶段完成 | `stage`, `stageName`, `status`, `duration`, `outputType`, `filePath` |
| `done` | 全部完成 | `message`, `stages`, `failedStep`, `stepMessages` |
| `error` | 发生错误 | `code`, `message`, `failedStep`, `stages` |
| `cancelled` | 任务取消 | `cancelledAtStep`, `stages` |

---

## Mock 模式

开发/测试时可启用 Mock 模式，无需真实 AI 调用：

```env
MOCK_MODE=True
```

- 使用 `app/mock/` 下的模拟数据替代 AI 响应
- SSE 流使用 `stream_mock.py` 生成模拟事件
- 适合前端联调和 CI 环境测试

---

## 详细 API 文档

完整的请求/响应示例和字段说明请参阅 [API.md](./API.md)。
