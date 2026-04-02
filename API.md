# Design AI - 后端 API 接口文档

## 概述

本文档定义了 Design AI（体验设计 Agent）前端项目所需的后端 API 接口。

### 基础信息

| 项目 | 说明 |
|------|------|
| Base URL | `http://localhost:8000` |
| 交互式文档 | `http://localhost:8000/docs`（Swagger UI） |
| ReDoc 文档 | `http://localhost:8000/redoc` |
| 响应格式 | JSON（普通接口） / SSE（流式接口） |
| 跨域 | 已配置 CORS，允许所有来源 |

### 统一响应格式

**成功响应**

```json
{
  "code": 0,
  "data": { "...": "..." },
  "message": "success"
}
```

**错误响应**（HTTP 状态码 400/404/500）

> 注意：HTTP 错误响应外层有 `detail` 包裹（FastAPI 默认行为），与普通 JSON 接口的响应结构不同。

```json
{
  "detail": {
    "code": 1001,
    "data": null,
    "message": "错误描述"
  }
}
```

### 错误码定义

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 参数错误 |
| 1002 | 会话不存在 |
| 1003 | AI 设计生成失败 |
| 1004 | 请求超时 |
| 2001 | 未授权（预留） |
| 2002 | Token 过期（预留） |
| 5000 | 服务器内部错误 |

---

### 环境配置

通过 `.env` 文件或环境变量进行配置（参见 `.env.example`）。

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `MONGODB_URL` | 否 | `mongodb://localhost:27017` | MongoDB 连接地址 |
| `DATABASE_NAME` | 否 | `vue_code_gen` | 数据库名称 |
| `AI_PROVIDER` | 否 | `glm5` | 代码生成 AI 提供者：`glm5` / `minimax`（仅影响非 CcUI 的 generation 步骤） |
| `GLM5_API_KEY` | 否 | `""` | GLM-5 API Key |
| `GLM5_API_URL` | 否 | `https://open.bigmodel.cn/api/coding/paas/v4/chat/completions` | GLM-5 API 地址 |
| `GLM5_MODEL` | 否 | `glm-5` | GLM-5 模型名称 |
| `GLM4V_API_KEY` | 否 | `""` | GLM-4V（图片分析）API Key |
| `GLM4V_API_URL` | 否 | `https://open.bigmodel.cn/api/paas/v4/chat/completions` | GLM-4V API 地址 |
| `GLM4V_MODEL` | 否 | `glm-4.6v-flashx` | GLM-4V 模型名称 |
| `MINIMAX_API_KEY` | 否 | `""` | MiniMax API Key（用于摘要生成） |
| `MINIMAX_API_URL` | 否 | `https://api.minimaxi.com/anthropic` | MiniMax API 地址 |
| `MINIMAX_MODEL` | 否 | `MiniMax-M2.7` | MiniMax 模型名称 |
| `OPENCLAW_API_URL` | 否 | `http://127.0.0.1:18789/v1/responses` | OpenClaw Agent API 地址（用于 CcUI 代码生成和 UX 优化） |
| `OPENCLAW_TOKEN` | 否 | `""` | OpenClaw 认证 Token |
| `OPENCLAW_AGENT_ID` | 否 | `main` | OpenClaw Agent ID |
| `OPENCLAW_MODEL` | 否 | `openclaw` | OpenClaw 模型名称 |
| `MOCK_MODE` | 否 | `false` | Mock 模式（开启后 SSE 接口返回模拟数据，无需真实 AI 调用） |

---

## 1. 基础接口

### 1.1 服务信息

```
GET /
```

**响应**

```json
{
  "message": "Vue Code Gen API",
  "version": "1.0.0"
}
```

### 1.2 健康检查

```
GET /health
```

**响应**

```json
{
  "status": "ok",
  "mongodb": "connected"
}
```

> 当 MongoDB 断连时，返回 `"status": "error", "mongodb": "disconnected"`，并附带 `error` 字段。

---

## 2. 文件上传

### 2.1 上传设计素材

上传图片、Markdown 或文本文件，最多 5 个。上传后的附件信息可在后续生成请求中通过 `attachments` 字段传入。

```
POST /api/upload
Content-Type: multipart/form-data
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| files | file[] | 是 | 文件列表，最多 5 个。支持的类型：图片（png/jpg/jpeg/gif/webp/svg）、Markdown（md/markdown）、文本（txt） |

**响应**

```json
{
  "code": 0,
  "data": {
    "files": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "url": "/uploads/550e8400-e29b-41d4-a716-446655440000.png",
        "name": "design.png",
        "type": "image",
        "size": 102400
      }
    ]
  },
  "message": "success"
}
```

**Attachment 结构**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 文件唯一标识（UUID） |
| url | string | 文件访问路径 |
| name | string | 原始文件名 |
| type | string | 文件类型：`image` / `text` / `markdown` |
| size | int / null | 文件大小（字节） |

---

## 3. 设计生成（SSE 流式接口）

设计生成接口均返回 **Server-Sent Events（SSE）** 流，前端需使用 `EventSource` 或 `fetch` + `ReadableStream` 接收。

> SSE 响应头：`Content-Type: text/event-stream`、`Cache-Control: no-cache`、`X-Accel-Buffering: no`

### 3.1 初始设计生成

根据用户需求描述（支持文本 + 图片/文档附件）进行全新设计生成，走四阶段 Pipeline。

```
POST /api/generate/initial/stream
```

**请求体**

```json
{
  "prompt": "生成一个登录页面，包含用户名密码输入框、记住我选项和第三方登录",
  "sessionId": "会话ID（可选，传入时自动保存到会话）",
  "componentLib": "ElementUI",
  "attachments": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "/uploads/xxx.png",
      "name": "design.png",
      "type": "image",
      "size": 102400
    }
  ],
  "debug": false,
  "fromStep": null
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| prompt | string | 是 | - | 用户需求描述 |
| sessionId | string | 否 | null | 会话 ID，传入时将生成结果保存到会话 |
| componentLib | string | 否 | `ElementUI` | 组件库：`ElementUI` / `aui` / `ccui` |
| attachments | Attachment[] | 否 | null | 已上传的附件列表（通过 `/api/upload` 获取） |
| debug | bool | 否 | false | 调试模式（暂未启用额外输出） |
| fromStep | int | 否 | null | 从指定步骤重试（0/1/2/3），跳过之前已成功的步骤。传入时必须同时提供 `sessionId` |

**fromStep 取值说明**

| 值 | 含义 |
|----|------|
| 0 | 重新执行附件处理 |
| 1 | 跳过附件处理，从需求标准化开始 |
| 2 | 跳过前两步，从代码生成开始 |
| 3 | 跳过前三步，从 UX 优化开始 |
| null | 正常执行全部步骤 |

**SSE 事件流**

```
event: stage_start
data: {"stage": 0, "stageName": "attachment", "isRetry": false, "taskId": "xxx", "timestamp": "..."}

event: stage_progress
data: {"stage": 0, "stageName": "attachment", "message": "正在分析图片 1/2: design.png", "progress": 50, "timestamp": "..."}

event: stage_complete
data: {"stage": 0, "stageName": "attachment", "status": "success", "message": "已处理1张图片", "duration": 3.21, "outputType": "markdown", "filePath": "/output/xxx/xxx/step0_final_prompt.md", "timestamp": "..."}

event: stage_start
data: {"stage": 1, "stageName": "requirement", ...}

event: stage_complete
data: {"stage": 1, "stageName": "requirement", "status": "success", ...}

event: stage_start
data: {"stage": 2, "stageName": "generation", ...}

event: stage_complete
data: {"stage": 2, "stageName": "generation", "status": "success", ...}

event: stage_start
data: {"stage": 3, "stageName": "optimization", ...}

event: stage_complete
data: {"stage": 3, "stageName": "optimization", "status": "success", ...}

event: done
data: {"message": "已为您生成登录页面...", "stages": {...}, "failedStep": null, "stepMessages": [...], "timestamp": "..."}
```

**四阶段 Pipeline 说明**

| 步骤 | stageName | 说明 | 产出类型 |
|------|-----------|------|----------|
| 0 | attachment | 附件处理：图片经 GLM-4V 分析布局，文本/MD 直接读取，合并为 final_prompt | markdown |
| 1 | requirement | 需求标准化：AI 将原始需求规范化为结构化 UX 规格文档 | markdown |
| 2 | generation | 代码生成：根据需求文档生成 Vue 3 组件代码。CcUI 走 OpenClaw Agent，ElementUI/aui 走 GLM-5/MiniMax | vue |
| 3 | optimization | UX 优化：OpenClaw Agent 对生成代码进行样式和布局优化 | vue |

---

### 3.2 迭代设计修改

基于已有代码进行修改，支持多轮对话迭代。不走多阶段 Pipeline，直接调用 AI 服务。

```
POST /api/generate/iterate/stream
```

**请求体**

```json
{
  "prompt": "给登录页面添加一个注册按钮",
  "sessionId": "会话ID（可选）",
  "files": [
    {
      "id": "main-page",
      "name": "MainPage.vue",
      "path": "/src/MainPage.vue",
      "type": "file",
      "language": "vue",
      "content": "<template>...</template>"
    }
  ],
  "fromStep": null
}
```

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| prompt | string | 是 | - | 修改需求描述 |
| sessionId | string | 否 | null | 会话 ID |
| files | GeneratedFile[] | 是 | - | 当前文件列表（上一次生成的结果） |
| fromStep | int | 否 | null | 仅支持 `0`，表示回滚上次失败的迭代后重新执行 |

**SSE 事件流**

迭代只有单阶段（`iteration`），事件格式与初始生成一致：

```
event: stage_start
data: {"stage": 0, "stageName": "iteration", "isRetry": false, "taskId": "xxx", "timestamp": "..."}

event: stage_complete
data: {"stage": 0, "stageName": "iteration", "status": "success", "message": "已为您添加注册按钮", "duration": 8.52, "outputType": "vue", "filePath": "/output/xxx/xxx/step0_iteration.json", "timestamp": "..."}

event: done
data: {"message": "已为您添加注册按钮", "stages": {"iteration": {"status": "success", "duration": 8.52}}, "failedStep": null, "timestamp": "..."}
```

---

### 3.3 取消生成任务

取消正在进行的生成任务。

```
POST /api/generate/cancel?taskId=xxx
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| taskId | string | 是 | 任务 ID（来自 SSE `stage_start` 事件中的 `taskId`） |

**响应**

```json
{
  "code": 0,
  "message": "取消请求已发送",
  "data": null
}
```

> 取消后，SSE 流将发送 `cancelled` 事件并关闭。

---

### 3.4 SSE 事件类型参考

所有 SSE 事件的通用字段：`timestamp`（ISO 8601 UTC 时间）。

#### stage_start — 阶段开始

```json
{
  "stage": 0,
  "stageName": "attachment",
  "isRetry": false,
  "taskId": "550e8400-...",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| stage | int | 阶段编号 |
| stageName | string | 阶段名称：`attachment` / `requirement` / `generation` / `optimization` / `iteration` |
| isRetry | bool | 是否为重试 |
| taskId | string | 任务 ID，可用于取消 |

#### stage_progress — 阶段进度

```json
{
  "stage": 0,
  "stageName": "attachment",
  "message": "正在分析图片 1/2: design.png",
  "progress": 50,
  "timestamp": "..."
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| stage | int | 阶段编号 |
| stageName | string | 阶段名称 |
| message | string | 进度描述 |
| progress | int / null | 进度百分比（0-100），可能不存在 |

#### stage_complete — 阶段完成

```json
{
  "stage": 2,
  "stageName": "generation",
  "status": "success",
  "message": "生成了 1 个 Vue 组件文件（ElementUI）",
  "duration": 5.67,
  "outputType": "vue",
  "filePath": "/output/xxx/step2_generation.json",
  "error": null,
  "timestamp": "..."
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| stage | int | 阶段编号 |
| stageName | string | 阶段名称 |
| status | string | 状态：`success` / `failed` / `skipped` / `cached` |
| message | string / null | 阶段摘要 |
| duration | float / null | 耗时（秒） |
| outputType | string / null | 产出类型：`markdown` / `json` / `vue` |
| filePath | string / null | 产出文件路径 |
| error | string / null | 错误信息（status 为 failed 时有值） |

#### done — 全部完成

```json
{
  "message": "已为您生成登录页面，包含用户名密码输入框等组件",
  "stages": {
    "attachment": { "status": "success", "duration": 3.21 },
    "requirement": { "status": "success", "duration": 1.23 },
    "generation": { "status": "success", "duration": 5.67 },
    "optimization": { "status": "success", "duration": 4.56 }
  },
  "failedStep": null,
  "stepMessages": [
    { "stage": 0, "stageName": "attachment", "message": "已处理1张图片", "status": "success", "duration": 3.21, "outputType": "markdown", "filePath": "/output/..." },
    { "stage": 1, "stageName": "requirement", "message": "需求标准化完成", "status": "success", "duration": 1.23, "outputType": "markdown", "filePath": "/output/..." },
    { "stage": 2, "stageName": "generation", "message": "生成了 1 个 Vue 组件文件", "status": "success", "duration": 5.67, "outputType": "vue", "filePath": "/output/..." },
    { "stage": 3, "stageName": "optimization", "message": "UX 优化完成", "status": "success", "duration": 4.56, "outputType": "vue", "filePath": "/output/..." }
  ],
  "timestamp": "..."
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| message | string | AI 生成的摘要描述 |
| stages | object | 各阶段执行结果（key 为 stageName，value 为 StageResult） |
| failedStep | int / null | 失败的步骤编号，可直接作为 `fromStep` 重试；`null` 表示全部成功 |
| stepMessages | array / null | 各步骤摘要信息，可用于前端逐步展示进度 |

#### error — 发生错误

> SSE `error` 事件的数据结构与 HTTP 错误响应不同，没有 `detail` 包裹层。

```json
{
  "code": 1003,
  "message": "GLM-5 API 调用失败: timeout",
  "failedStep": 2,
  "stages": {
    "attachment": { "status": "success", "duration": 3.21 },
    "requirement": { "status": "success", "duration": 1.23 },
    "generation": { "status": "failed", "duration": 5.01, "error": "GLM-5 API 调用失败: timeout" }
  },
  "timestamp": "..."
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| code | int | 错误码 |
| message | string | 错误描述 |
| failedStep | int / null | 失败步骤编号，可直接作为 `fromStep` 重试 |
| stages | object | 截止失败时各阶段的执行状态 |

#### cancelled — 任务取消

```json
{
  "cancelledAtStep": 2,
  "stages": {
    "attachment": { "status": "success", "duration": 3.21 },
    "requirement": { "status": "success", "duration": 1.23 }
  },
  "timestamp": "..."
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| cancelledAtStep | int / null | 取消时正在执行的步骤 |
| stages | object | 已完成的阶段状态 |

---

## 4. 图片分析

### 4.1 通过 URL 或 Base64 分析图片

```
POST /api/image/analyze
```

**请求体**

```json
{
  "imageUrl": "https://example.com/design.png",
  "imageBase64": null,
  "prompt": null
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| imageUrl | string | 否* | 图片 URL（与 imageBase64 二选一） |
| imageBase64 | string | 否* | 图片 Base64 编码（与 imageUrl 二选一） |
| prompt | string | 否 | 自定义分析 Prompt。不传时使用内置的 Vue 生成专用 Prompt |

**响应**

```json
{
  "code": 0,
  "data": {
    "description": "该页面包含顶部导航栏...",
    "rawDescription": "该页面包含顶部导航栏...",
    "success": true
  },
  "message": "success"
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| description | string | 分析结果描述 |
| rawDescription | string | 原始分析结果 |
| success | bool | 分析是否成功 |

### 4.2 通过上传文件分析图片

```
POST /api/image/analyze-file
Content-Type: multipart/form-data
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | file | 是 | 图片文件（支持 png/jpg/jpeg/gif/webp/svg） |
| prompt | string | 否 | 自定义分析 Prompt |

**响应**

与 4.1 相同。

---

## 5. 会话管理

### 5.1 创建会话

```
POST /api/sessions
```

**请求体**

```json
{
  "title": "登录页面设计",
  "componentLib": "ElementUI"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 会话标题 |
| componentLib | string | 否 | 组件库：`ElementUI` / `aui` / `ccui` |

**响应**

```json
{
  "code": 0,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "userId": null,
    "title": "登录页面设计",
    "componentLib": "ElementUI",
    "messages": [],
    "files": [],
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-01-15T10:30:00Z"
  },
  "message": "success"
}
```

### 5.2 获取会话列表

```
GET /api/sessions?page=1&pageSize=20
```

**查询参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | int | 否 | 1 | 页码（>= 1） |
| pageSize | int | 否 | 20 | 每页数量（1-100） |

> 按 `updatedAt` 降序排列。

**响应**

```json
{
  "code": 0,
  "data": {
    "total": 100,
    "list": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "userId": null,
        "title": "登录页面设计",
        "componentLib": "ElementUI",
        "createdAt": "2025-01-15T10:30:00Z",
        "updatedAt": "2025-01-15T10:35:00Z"
      }
    ]
  },
  "message": "success"
}
```

> 列表项不包含 `messages` 和 `files` 字段，以减少数据传输量。

### 5.3 获取会话详情

```
GET /api/sessions/{sessionId}
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话 ID |

**响应**

```json
{
  "code": 0,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "userId": null,
    "title": "登录页面设计",
    "componentLib": "ElementUI",
    "messages": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "role": "user",
        "content": "生成一个登录页面",
        "attachments": null,
        "failedStep": null,
        "stages": null,
        "stepMessages": null,
        "files": null,
        "timestamp": "2025-01-15T10:30:00Z"
      },
      {
        "id": "660e8400-e29b-41d4-a716-446655440002",
        "role": "assistant",
        "content": "已为您生成登录页面...",
        "attachments": null,
        "failedStep": null,
        "stages": {
          "attachment": { "status": "success", "duration": 3.21 },
          "requirement": { "status": "success", "duration": 1.23 },
          "generation": { "status": "success", "duration": 5.67 },
          "optimization": { "status": "success", "duration": 4.56 }
        },
        "stepMessages": [
          { "stage": 0, "stageName": "attachment", "message": "已处理1张图片", "status": "success", "duration": 3.21, "outputType": "markdown", "filePath": "/output/..." },
          { "stage": 1, "stageName": "requirement", "message": "需求标准化完成", "status": "success", "duration": 1.23, "outputType": "markdown", "filePath": "/output/..." },
          { "stage": 2, "stageName": "generation", "message": "生成了 1 个 Vue 组件文件", "status": "success", "duration": 5.67, "outputType": "vue", "filePath": "/output/..." },
          { "stage": 3, "stageName": "optimization", "message": "UX 优化完成", "status": "success", "duration": 4.56, "outputType": "vue", "filePath": "/output/..." }
        ],
        "files": [
          {
            "id": "main-page",
            "name": "MainPage.vue",
            "path": "/src/MainPage.vue",
            "type": "file",
            "language": "vue",
            "content": "<template>...</template>",
            "children": null
          }
        ],
        "timestamp": "2025-01-15T10:30:05Z"
      }
    ],
    "files": [
      {
        "id": "main-page",
        "name": "MainPage.vue",
        "path": "/src/MainPage.vue",
        "type": "file",
        "language": "vue",
        "content": "<template>...</template>",
        "children": null
      }
    ],
    "createdAt": "2025-01-15T10:30:00Z",
    "updatedAt": "2025-01-15T10:30:05Z"
  },
  "message": "success"
}
```

### 5.4 删除会话

```
DELETE /api/sessions/{sessionId}
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话 ID |

**响应**

```json
{
  "code": 0,
  "data": null,
  "message": "删除成功"
}
```

### 5.5 更新会话标题

```
PATCH /api/sessions/{sessionId}
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话 ID |

**请求体**

```json
{
  "title": "新的会话标题"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 新标题 |

**响应**

```json
{
  "code": 0,
  "data": null,
  "message": "更新成功"
}
```

### 5.6 更新会话文件

```
PATCH /api/sessions/{sessionId}/files
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话 ID |

**请求体**

```json
{
  "files": [
    {
      "id": "main-page",
      "name": "MainPage.vue",
      "path": "/src/MainPage.vue",
      "type": "file",
      "language": "vue",
      "content": "<template>...</template>",
      "children": null
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| files | CodeFile[] | 是 | 文件列表 |

**响应**

```json
{
  "code": 0,
  "data": null,
  "message": "更新成功"
}
```

---

## 6. 消息管理

### 6.1 添加消息

```
POST /api/sessions/{sessionId}/messages
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话 ID |

**请求体**

```json
{
  "role": "user",
  "content": "帮我添加一个注册按钮",
  "attachments": null
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| role | string | 是 | 角色：`user` / `assistant` |
| content | string | 是 | 消息内容 |
| attachments | Attachment[] | 否 | 附件列表 |

**响应**

```json
{
  "code": 0,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440003",
    "role": "user",
    "content": "帮我添加一个注册按钮",
    "attachments": null,
    "failedStep": null,
    "stages": null,
    "stepMessages": null,
    "files": null,
    "timestamp": "2025-01-15T10:35:00Z"
  },
  "message": "success"
}
```

### 6.2 删除消息

```
DELETE /api/sessions/{sessionId}/messages/{messageId}
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话 ID |
| messageId | string | 消息 ID |

**响应**

```json
{
  "code": 0,
  "data": null,
  "message": "删除成功"
}
```

---

## 7. 静态文件

| 路径 | 说明 |
|------|------|
| `/uploads/{filename}` | 访问上传的设计素材文件 |
| `/output/{sessionId}/{messageId}/{filename}` | 访问生成的产出文件（Prompt、JSON、Vue 文件等） |

---

## 8. 数据模型

### Session（会话）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 会话唯一标识（UUID） |
| userId | string / null | 用户 ID（预留，当前为 null） |
| title | string / null | 会话标题 |
| componentLib | string / null | 组件库：`ElementUI` / `aui` / `ccui` |
| messages | Message[] | 消息列表 |
| files | CodeFile[] | 最新生成的文件快照 |
| createdAt | datetime (UTC) | 创建时间 |
| updatedAt | datetime (UTC) | 更新时间 |

> 会话列表接口返回的 `SessionListItem` 不包含 `messages` 和 `files` 字段。

### Message（消息）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 消息唯一标识（UUID） |
| role | string | 角色：`user` / `assistant` |
| content | string | 消息内容 |
| attachments | Attachment[] / null | 附件列表 |
| failedStep | int / null | 失败的步骤编号，可直接作为 `fromStep` 重试 |
| stages | object / null | 各阶段执行状态（key 为 stageName，value 为 StageResult） |
| stepMessages | StepMessage[] / null | 各步骤摘要信息，前端可逐步展示 |
| files | CodeFile[] / null | 该消息关联的文件快照，用于重试时回滚 |
| timestamp | datetime (UTC) | 消息时间 |

### StepMessage（步骤消息）

| 字段 | 类型 | 说明 |
|------|------|------|
| stage | int | 步骤编号（0=附件处理, 1=需求标准化, 2=代码生成, 3=UX优化） |
| stageName | string | 步骤名称 |
| message | string / null | 该步骤的摘要/说明 |
| status | string / null | 执行状态：`success` / `failed` / `skipped` / `cached` |
| outputType | string / null | 产出类型：`markdown` / `json` / `vue` |
| filePath | string / null | 产出文件路径 |
| duration | float / null | 执行耗时（秒） |

### Attachment（附件）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 文件唯一标识（UUID） |
| url | string | 文件访问路径（如 `/uploads/xxx.png`） |
| name | string | 原始文件名 |
| type | string | 文件类型：`image` / `text` / `markdown` |
| size | int / null | 文件大小（字节） |

### CodeFile（代码文件）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 文件唯一标识 |
| name | string | 文件名（如 `MainPage.vue`） |
| path | string | 文件路径（如 `/src/MainPage.vue`） |
| type | string | 固定值 `file` |
| language | string / null | 固定值 `vue` |
| content | string / null | Vue SFC 代码内容 |
| children | CodeFile[] / null | 嵌套文件结构 |

### GeneratedFile（生成文件）

与 CodeFile 结构相同，用于 SSE `done` 事件和生成请求中的文件传递。

### StageResult（阶段结果）

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 状态：`success` / `failed` / `skipped` / `cached` / `cancelled` |
| duration | float / null | 耗时（秒） |
| output | string / null | 产出内容（debug 用） |
| error | string / null | 错误信息 |

---

## 9. 接口实现状态

### 已实现

| 接口 | 说明 |
|------|------|
| `GET /` | 服务信息 |
| `GET /health` | 健康检查 |
| `POST /api/upload` | 上传设计素材 |
| `POST /api/generate/initial/stream` | SSE 初始设计生成（四阶段 Pipeline） |
| `POST /api/generate/iterate/stream` | SSE 迭代设计修改 |
| `POST /api/generate/cancel` | 取消生成任务 |
| `POST /api/image/analyze` | 图片分析（URL/Base64） |
| `POST /api/image/analyze-file` | 图片分析（上传文件） |
| `POST /api/sessions` | 创建会话 |
| `GET /api/sessions` | 获取会话列表（分页） |
| `GET /api/sessions/{sessionId}` | 获取会话详情 |
| `DELETE /api/sessions/{sessionId}` | 删除会话 |
| `PATCH /api/sessions/{sessionId}` | 更新会话标题 |
| `PATCH /api/sessions/{sessionId}/files` | 更新会话文件 |
| `POST /api/sessions/{sessionId}/messages` | 添加消息 |
| `DELETE /api/sessions/{sessionId}/messages/{messageId}` | 删除消息 |

### 预留未实现

| 接口 | 说明 |
|------|------|
| `POST /api/auth/login` | 用户登录 |
| `POST /api/auth/register` | 用户注册 |
| `GET /api/auth/me` | 获取当前用户 |

---

## 10. 联调说明

### 启动服务

```bash
python -m uvicorn app.main:app --reload --port 8000
```

### Mock 模式

设置环境变量 `MOCK_MODE=True` 后，所有 SSE 生成接口将返回模拟数据，无需真实 AI 调用：

```env
MOCK_MODE=True
```

### 前端 SSE 接入示例

```typescript
// 使用 fetch 接收 SSE 流
async function* streamGenerate(url: string, body: object) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  const reader = response.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    let eventType = ''
    let eventData = ''
    for (const line of lines) {
      if (line.startsWith('event: ')) eventType = line.slice(7)
      if (line.startsWith('data: ')) eventData = line.slice(6)
    }

    if (eventType && eventData) {
      yield { event: eventType, data: JSON.parse(eventData) }
    }
  }
}

// 使用示例
for await (const { event, data } of streamGenerate('/api/generate/initial/stream', {
  prompt: '生成登录页面',
  sessionId: 'xxx',
  componentLib: 'ElementUI',
})) {
  switch (event) {
    case 'stage_start':
      console.log(`阶段开始: ${data.stageName}`)
      break
    case 'stage_complete':
      console.log(`阶段完成: ${data.stageName} - ${data.status}`)
      break
    case 'done':
      console.log(`全部完成: ${data.message}`)
      break
    case 'error':
      console.error(`生成失败: ${data.message}，可从步骤 ${data.failedStep} 重试`)
      break
    case 'cancelled':
      console.log(`已取消`)
      break
  }
}
```
