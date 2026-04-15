# 体验设计 Agent 升级规划

> 从固定 Pipeline 升级为 AI Agent，分三档渐进式改造。
> 整合了内部方案讨论的完整设计。

## 当前架构

```
用户需求 → 固定 4 步 Pipeline → Vue 代码
(附件处理 → 需求标准化 → 代码生成 → UX 优化)
```

**现状问题**：

- 编排逻辑硬编码在 `pipeline.py` 中（`step 0 → 1 → 2 → 3`）
- 分支靠 `if ctx.is_ccui` 决定，不是 Agent 自主判断
- 没有自主决策/推理循环，Pipeline 是预定义的固定流程
- 没有环境交互反馈，Agent 不能"看到"自己生成的页面效果
- 生成的代码好不好，只有用户看到预览才知道

---

## 第一档：轻量 Agent（建议 1-2 周）

### 目标

Pipeline 不动，加一个 LLM 驱动的"调度层"在前面，让 AI 自主决定走哪几步。

### 架构变化

```
用户需求 → [LLM 调度器] → 自主选择工具执行 → 结果验证 → Vue 代码
                ↓
        可用工具集：
        - analyze_image      分析设计稿，提取布局和组件信息
        - normalize_req      将用户需求标准化为 UX 规格文档
        - generate_code      根据 UX 文档生成 Vue 3 组件代码
        - optimize_ux        对代码进行 UX 优化
        - search_doc         查询组件库文档（CcUI/ElementUI）
        - validate_preview   预览代码并验证是否有明显问题
```

LLM 自主决定：有图片就调 `analyze_image`，需求模糊就先 `search_doc`，简单需求直接 `generate_code`。

### 核心改造

#### 1. Tool Calling 调度（新增 `app/agent.py`）

- 用 GLM-5 的 tool calling 能力（OpenAI Function Calling 协议），注册现有 Pipeline 各步骤为工具
- LLM 根据用户需求自主选择调用哪些工具、什么顺序

```python
tools = [
    {"name": "analyze_image", "description": "分析设计稿图片，提取布局和组件信息"},
    {"name": "normalize_requirement", "description": "将用户需求标准化为 UX 规格文档"},
    {"name": "generate_vue_code", "description": "根据 UX 文档生成 Vue 3 组件代码"},
    {"name": "optimize_ux", "description": "对代码进行 UX 优化"},
    {"name": "search_component_doc", "description": "查询组件库文档（CcUI/ElementUI）"},
    {"name": "preview_validate", "description": "预览代码并验证是否有明显问题"},
]
```

#### 2. 反馈循环

```python
while not done:
    action = llm_decide_next_action(context, available_tools)
    result = execute_tool(action)
    context.append(result)

    if action.name == "generate_vue_code":
        issues = llm_review(result)
        if issues:
            context.append(f"生成结果有以下问题：{issues}，请修复")
            continue

    done = llm_judge_done(context)
```

#### 3. Review Agent 自审（增强项）

代码生成后自动触发审查，不通过则重试：

| 审查维度 | 说明 |
|----------|------|
| **结构完整性** | 组件是否闭合、props 是否定义、import 是否齐全 |
| **组件库合规** | 是否用了正确的组件 API（CcUI vs Element Plus） |
| **需求覆盖度** | 对比需求文档，检查是否有遗漏的功能点 |
| **代码质量** | 重复代码、过深的嵌套、缺失的响应式处理 |

输出结构化审查结果：`{ "pass": false, "issues": [...], "severity": "major" }`

#### 4. 新增接口

```
POST /api/generate/agent/stream
```

- SSE 流式返回，事件格式与现有接口兼容
- 额外增加 `thinking` 事件，展示 Agent 的规划过程
- 现有 `/api/generate/initial/stream` 保留，逐步迁移

### 依赖变化

- 可选引入 `openai` SDK（简化 tool calling 解析）
- 其余零新依赖

### 改动文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `app/agent.py` | 新增 | Agent 核心逻辑：工具注册、调度循环、结果解析 |
| `app/tools.py` | 新增 | 工具定义 + 注册表，封装现有 Pipeline 步骤为可调用工具 |
| `app/services/review_service.py` | 新增 | Review Agent：代码审查（4 维度） |
| `app/prompts.py` | 修改 | 新增 Agent system prompt + review prompt |
| `app/routers/generate.py` | 修改 | 新增 `/api/generate/agent/stream` 路由 |
| `app/config.py` | 修改 | 新增 Agent 相关配置项 |

### 前端影响

- SSE 事件格式兼容，前端改动最小
- 可选：展示 Agent 思考过程（`thinking` 事件）

---

## 第二档：标准 Agent（预计 3-4 周）

### 目标

引入 ReAct 推理框架 + 记忆系统 + 视觉反馈闭环，实现真正的自主规划。

### 核心改造

#### 1. ReAct 推理循环

让 LLM 按 **Thought → Action → Observation → Thought...** 循环工作：

```
用户：生成一个带图表的数据看板

Thought: 用户需要数据看板，有图表需求。我应该先查一下 ElementUI 有哪些图表组件。
Action: search_component_doc("ElementUI 图表组件")
Observation: ElementUI 没有内置图表，建议配合 ECharts。

Thought: 好的，需要用 ECharts。先看看用户有没有上传参考图。
Action: check_attachments()
Observation: 用户上传了 dashboard.png

Thought: 先分析参考图获取布局信息。
Action: analyze_image(dashboard.png)
Observation: 图片显示三栏布局，顶部统计卡片，中部折线图+饼图，底部表格...

Thought: 需求足够清晰了，直接生成代码。
Action: generate_vue_code(requirement, layout_info)
Observation: 代码生成成功。

Thought: 生成的代码用了 ECharts，让我检查一下引入是否正确。
Action: preview_validate(code)
Observation: 发现 ECharts 的 responsive 配置缺失。

Thought: 修复这个问题。
Action: fix_code(code, "添加 ECharts responsive 配置")
Observation: 修复完成，预览正常。

Thought: 任务完成。
```

#### 2. 记忆系统

```python
# 短期记忆：当前会话上下文
session_memory = []  # 对话历史 + 工具调用记录

# 长期记忆：用户偏好
# "这个用户喜欢简洁风格"、"之前的项目都用 CcUI"
user_preferences = load_from_db(user_id)

# 注入到 prompt 中
system_prompt = f"""
你是前端设计 Agent。用户偏好：{user_preferences}
可用工具：{tools}
请自主规划步骤完成任务。
"""
```

- **短期记忆**：当前会话的对话历史 + 工具调用链
- **长期记忆**：用户偏好（常用组件库、风格偏好等），存 MongoDB
- 注入 system prompt 中辅助决策

#### 3. 智能迭代

- 分析用户修改意图，而非简单传给 LLM
- 意图模糊时主动追问（如"改好看点" → 追问具体哪些方面）

```python
def auto_improve(code, user_feedback):
    intent = llm.analyze_intent(user_feedback)

    if intent.ambiguous:
        return ask_clarification(intent.ambiguous_points)

    new_code = llm.modify_code(code, intent)

    review = llm.review(new_code, original_code, intent)
    if review.has_regression:
        new_code = llm.modify_code(code, intent, strategy="alternative")

    return new_code
```

#### 4. 视觉反馈闭环（增强项）

生成代码后自动渲染，把**截图**喂给 Agent 做视觉审查：

```
代码生成 → 渲染服务（headless browser）
              │
              ├─ 截图 → Review Agent 看图审
              │         "布局左边距不对，搜索框和表格没对齐"
              │
              └─ 智能修复 → 重新生成 CSS 部分
```

- 部署 headless browser 服务（Playwright / Puppeteer），接收 Vue SFC，返回截图
- 用 GLM-4V 做视觉审查（已有该模型）
- Agent 可以"看到"自己的产出，形成真正的闭环

### 改动文件

| 文件 | 操作 | 说明 |
|------|------|------|
| `app/agent.py` | 重构 | ReAct 循环引擎 |
| `app/memory.py` | 新增 | 记忆管理（短期 + 长期） |
| `app/tools.py` | 扩展 | 更多工具：fix_code、validate、search 等 |
| `app/models/` | 新增 | 用户偏好数据模型 |
| `app/services/render_service.py` | 新增 | Headless browser 渲染服务（可选） |

---

## 第三档：多 Agent 协作（预计 1-2 月）

### 目标

拆分为多个专业 Agent，各司其职，由 Orchestrator 统一调度。

### 架构

```
                ┌──────────────┐
                │ Orchestrator │  ← 总调度 Agent
                └──────┬───────┘
         ┌──────┬──────┼──────┬──────┐
         ▼      ▼      ▼      ▼      ▼
     Design  Code   UX     QA     Doc
     Analyst Gen   Refine Tester Search
     Agent   Agent Agent  Agent  Agent
```

### 各 Agent 职责

| Agent | 职责 | 专用工具 |
|-------|------|---------|
| **Orchestrator** | 总调度、任务分发、结果审核、记忆共享 | dispatch, review_result |
| **Design Analyst** | 分析需求、理解设计稿、查询组件库文档 | analyze_image, extract_layout, search_doc |
| **Code Generator** | 专注写代码，不同组件库用不同 Agent | generate_code, check_component_exists |
| **UX Refiner** | 样式优化、布局调整、响应式处理 | optimize_ux, check_accessibility |
| **QA Tester** | 验证可运行性 + 视觉审查 | validate_syntax, preview_check, lint, visual_review |
| **Doc Search** | 查询组件库文档（RAG） | search_ccui_doc, search_element_doc |

### 记忆共享

- 所有 Agent 共享用户偏好 + 项目上下文
- Orchestrator 维护全局状态，各 Agent 通过消息传递协作
- 可通过 OpenClaw 起不同 Agent 实例

### 技术选型

- 通过 OpenClaw 起不同 Agent 实例（已有集成）
- 或自行实现轻量 Agent 调度框架
- 各 Agent 独立 system prompt + 工具集

---

## 实施路线图

```
Week 1-2   第一档
           → LLM 调度 + 反馈循环 + Review Agent
           → 投入小（200-300 行新代码），见效快

Week 3-6   第二档
           → ReAct 推理 + 记忆系统 + 智能迭代
           → 视觉反馈闭环作为增强项（需部署渲染服务）

Week 7+    第三档
           → 多 Agent 协作
           → 架构级重构，业务验证没问题后再上
```

### 实施建议

1. **第一档优先**：投入小、见效快，80% 的 Agent 感就出来了
2. **保持兼容**：新接口与旧 Pipeline 并行运行，逐步迁移
3. **可观测性**：Agent 的决策过程要能被追踪和调试
4. **前端渐进**：SSE 事件格式保持兼容，前端最小改动

---

*创建时间：2026-04-02*
*维护者：体验设计 Agent 团队*
