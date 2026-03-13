# Vue3 Page Generator - 后端 API 接口文档

## 概述

本文档定义了 Vue3 Page Generator 前端项目所需的后端 API 接口。

### 基础信息

| 项目 | 说明 |
|------|------|
| Base URL | `http://localhost:8000` |
| API 文档 | `http://localhost:8000/docs` |
| 响应格式 | JSON |

---

## 0. 健康检查

### 0.1 服务健康检查

**请求**

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

---

## 1. AI 代码生成

### 1.1 初始生成代码（新会话）

根据用户需求描述生成 Vue3 组件代码，走三阶段流程（需求标准化 → 代码生成 → UX优化）。

**重要说明**：
- 此接口用于**新会话首次生成**，不传已有文件
- 走三步骤流程：步骤1 需求标准化 → 步骤2 代码生成 → 步骤3 UX优化（仅 CcUI）
  - ElementUI/aui：走步骤1 需求标准化 → 步骤2 代码生成
  - CcUI：走步骤1 需求标准化 → 步骤2 代码生成 → 步骤3 UX优化
- 后续迭代修改请使用 `/api/generate/iterate` 接口

**请求**

```
POST /api/generate/initial
```

**请求体**

```json
{
  "prompt": "生成一个登录页面，包含用户名密码输入框、记住我选项和第三方登录",
  "sessionId": "会话ID，可选",
  "componentLib": "ElementUI",
  "debug": false
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 用户需求描述 |
| sessionId | string | 否 | 会话ID，可选，为空时不保存到数据库 |
| componentLib | string | 否 | 组件库选择，可选值：`ElementUI`、`aui`、`ccui`，默认 `ElementUI` |
| debug | boolean | 否 | 是否返回调试信息（各阶段耗时、中间输出），默认 false |

**响应**

```json
{
  "code": 0,
  "data": {
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
    "message": "代码生成完成",
    "stages": {
      "requirement": {
        "status": "success",
        "duration": 1.23
      },
      "generation": {
        "status": "success",
        "duration": 5.67
      },
      "optimization": {
        "status": "skipped",
        "duration": 0.01
      }
    }
  }
}
```

**stages 字段说明（仅 debug=true 时返回）**

| 阶段 | 字段 | 说明 |
|------|------|------|
| requirement | status, duration, output, error | 步骤1：需求标准化 |
| generation | status, duration, output, error | 步骤2：代码生成 |
| optimization | status, duration, output, error | 步骤3：UX优化 |

---

### 1.2 迭代修改代码（多轮对话）

基于现有代码进行修改，支持多轮对话迭代。

**重要说明**：
- 此接口用于**二次或多轮对话修改**，必须传入当前文件列表
- 直接调用 AI 生成，不走三步骤流程
- files 为必填参数

**请求**

```
POST /api/generate/iterate
```

**请求体**

```json
{
  "prompt": "给登录页面添加一个注册按钮",
  "sessionId": "会话ID，可选",
  "files": [
    {
      "id": "main-page",
      "name": "MainPage.vue",
      "path": "/src/MainPage.vue",
      "type": "file",
      "language": "vue",
      "content": "<template>...</template>"
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 修改需求描述 |
| sessionId | string | 否 | 会话ID，可选，为空时不保存到数据库 |
| files | array | 是 | 当前文件列表，必填 |

**响应**

```json
{
  "code": 0,
  "data": {
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
    "message": "已为您添加注册按钮"
  }
}
```

**文件结构说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 文件唯一标识 |
| name | string | 文件名 |
| path | string | 文件路径 |
| type | string | 类型：file（始终为 file） |
| language | string | 语言：vue（始终为 vue） |
| content | string | 文件内容 |

**前端使用示例**

```typescript
import { generateInitial, generateIterate } from '@/api'
import { buildProjectFiles } from '@/templates/project-template'

// 首次生成
async function handleFirstGenerate(prompt: string, sessionId: string) {
  const result = await generateInitial({ 
    prompt, 
    sessionId,
    debug: false 
  })
  
  const mainPageContent = result.files[0].content
  const extraFiles = result.files.slice(1)
  const projectFiles = buildProjectFiles(mainPageContent, extraFiles)
  
  return { projectFiles, generatedFiles: result.files }
}

// 二次修改
async function handleModify(prompt: string, sessionId: string, previousFiles: File[]) {
  const result = await generateIterate({ 
    prompt, 
    sessionId,
    files: previousFiles
  })
  
  const mainPageContent = result.files[0].content
  const extraFiles = result.files.slice(1)
  const projectFiles = buildProjectFiles(mainPageContent, extraFiles)
  
  return { projectFiles, generatedFiles: result.files }
}
```

---

## 2. 会话管理

### 2.1 创建会话

**请求**

```
POST /api/sessions
```

**请求体**

```json
{
  "title": "登录页面生成",
  "componentLib": "ElementUI"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 会话标题 |
| componentLib | string | 否 | 选择的组件库，可选值：`ElementUI`、`aui`、`ccui` |

**响应**

```json
{
  "code": 0,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "userId": null,
    "title": "登录页面生成",
    "componentLib": "ElementUI",
    "messages": [],
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  }
}
```

### 2.2 获取会话列表

**请求**

```
GET /api/sessions?page=1&pageSize=20
```

**查询参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认 1 |
| pageSize | int | 否 | 每页数量，默认 20 |

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
        "title": "登录页面生成",
        "componentLib": "ElementUI",
        "createdAt": "2024-01-15T10:30:00Z",
        "updatedAt": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

### 2.3 获取会话详情

**请求**

```
GET /api/sessions/:sessionId
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话ID |

**响应**

```json
{
  "code": 0,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "userId": null,
    "title": "登录页面生成",
    "messages": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "role": "user",
        "content": "生成一个登录页面",
        "timestamp": "2024-01-15T10:30:00Z"
      },
      {
        "id": "660e8400-e29b-41d4-a716-446655440002",
        "role": "assistant",
        "content": "我已根据您的需求生成了登录页面代码...",
        "timestamp": "2024-01-15T10:30:05Z"
      }
    ],
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:05Z"
  }
}
```

### 2.4 删除会话

**请求**

```
DELETE /api/sessions/:sessionId
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话ID |

**响应**

```json
{
  "code": 0,
  "data": null,
  "message": "删除成功"
}
```

### 2.5 更新会话标题

**请求**

```
PATCH /api/sessions/:sessionId
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话ID |

**请求体**

```json
{
  "title": "新的会话标题"
}
```

**响应**

```json
{
  "code": 0,
  "data": null,
  "message": "更新成功"
}
```

### 2.6 更新会话文件

**请求**

```
PATCH /api/sessions/:sessionId/files
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话ID |

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
      "content": "<template>...</template>"
    }
  ]
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| files | array | 是 | 文件列表 |

**文件结构说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 文件唯一标识 |
| name | string | 文件名 |
| path | string | 文件路径 |
| type | string | 类型：file（始终为 file） |
| language | string | 语言：vue（始终为 vue） |
| content | string | 文件内容 |

**响应**

```json
{
  "code": 0,
  "data": null,
  "message": "更新成功"
}
```

---

## 3. 消息管理

### 3.1 添加消息

**请求**

```
POST /api/sessions/:sessionId/messages
```

**路径参数**

| 参数 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话ID |

**请求体**

```json
{
  "role": "user",
  "content": "帮我添加一个注册按钮"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| role | string | 是 | 角色：user / assistant |
| content | string | 是 | 消息内容 |

**响应**

```json
{
  "code": 0,
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440003",
    "role": "user",
    "content": "帮我添加一个注册按钮",
    "timestamp": "2024-01-15T10:35:00Z"
  }
}
```

---

## 4. 统一响应格式

### 成功响应

```json
{
  "code": 0,
  "data": { ... },
  "message": "success"
}
```

### 错误响应

```json
{
  "code": 1001,
  "data": null,
  "message": "错误描述"
}
```

### 错误码定义

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 参数错误 |
| 1002 | 会话不存在 |
| 1003 | AI 生成失败 |
| 1004 | 请求超时 |
| 2001 | 未授权 |
| 2002 | Token 过期 |
| 5000 | 服务器内部错误 |

---

## 5. 用户认证（预留，未实现）

### 5.1 登录

```
POST /api/auth/login
```

```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**响应**

```json
{
  "code": 0,
  "data": {
    "token": "jwt-token-xxx",
    "user": {
      "id": "user-xxx",
      "username": "user@example.com",
      "nickname": "用户昵称"
    }
  }
}
```

### 5.2 注册

```
POST /api/auth/register
```

```json
{
  "username": "user@example.com",
  "password": "password123",
  "nickname": "用户昵称"
}
```

### 5.3 获取当前用户信息

```
GET /api/auth/me
Header: Authorization: Bearer <token>
```

---

## 6. 接口实现状态

### 已实现 ✅

| 接口 | 说明 |
|------|------|
| `GET /health` | 健康检查 |
| `POST /api/generate/initial` | 初始生成代码（新会话，三步骤流程） |
| `POST /api/generate/iterate` | 迭代修改代码（多轮对话） |
| `POST /api/sessions` | 创建会话 |
| `GET /api/sessions` | 获取会话列表 |
| `GET /api/sessions/:sessionId` | 获取会话详情 |
| `DELETE /api/sessions/:sessionId` | 删除会话 |
| `PATCH /api/sessions/:sessionId` | 更新会话标题 |
| `PATCH /api/sessions/:sessionId/files` | 更新会话文件 |
| `POST /api/sessions/:sessionId/messages` | 添加消息 |

### 待实现 🚧

| 接口 | 说明 |
|------|------|
| `POST /api/auth/login` | 用户登录 |
| `POST /api/auth/register` | 用户注册 |
| `GET /api/auth/me` | 获取当前用户 |

### 已废弃 ❌

| 接口 | 说明 |
|------|------|
| `POST /api/generate` | 已拆分为 `/api/generate/initial` 和 `/api/generate/iterate` |
| `POST /api/generate-v2` | 已重命名为 `/api/generate/initial` |

---

## 7. 数据模型

### Session 会话

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 会话唯一标识 (UUID) |
| userId | string | 用户ID（当前为 null） |
| title | string | 会话标题 |
| componentLib | string | 选择的组件库，可选值：`ElementUI`、`aui`、`ccui` |
| messages | Message[] | 消息列表 |
| files | File[] | 生成的文件列表 |
| createdAt | datetime | 创建时间 |
| updatedAt | datetime | 更新时间 |

### Message 消息

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | 消息唯一标识 (UUID) |
| role | string | 角色：user / assistant |
| content | string | 消息内容 |
| timestamp | datetime | 消息时间 |

---

## 8. 联调说明

### 启动服务

```bash
conda activate python310
python -m uvicorn app.main:app --reload --port 8000
```

### 测试地址

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 跨域配置

已配置 CORS，允许所有来源访问：
```
allow_origins: ["*"]
allow_methods: ["*"]
allow_headers: ["*"]
```
