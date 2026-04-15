# vue-code-gen-api Agent 化改造方案

> 参考 [SuperDesign](https://github.com/superdesigndev/superdesign) 的 Agent 架构，将现有固定 Pipeline 升级为 Agent 模式。
本地 SuperDesign](D:\code\idea\superdesign-main)

---

## 1. 现状分析

### 1.1 当前架构

```
用户输入（文本 + 附件）
        │
        ▼
┌─────────────────────────────────┐
│  Step 0: 附件处理 (attachment)    │  ← process_attachments()
│  · 图片 -> GLM-4V 视觉分析        │
│  · 文本/MD -> 直接读取             │
│  输出: final_prompt.md            │
└─────────────────────────────────┘
        │  硬编码顺序，不可跳步
        ▼
┌─────────────────────────────────┐
│  Step 1: 需求标准化 (requirement)  │  ← RequirementService
│  · AI 驱动的 UX 需求规范化         │
│  输出: requirement.md             │
└─────────────────────────────────┘
        │  if ctx.is_ccui 分支
        ▼
┌─────────────────────────────────┐
│  Step 2: 代码生成 (generation)     │  ← OpenClawService / GLM5Service
│  · CcUI -> OpenClaw Agent         │
│  · ElementUI/aui -> GLM-5         │
│  输出: generation.json + .vue     │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  Step 3: UX 优化 (optimization)   │  ← OpenClawService
│  · ccui-ux-guardian Skill         │
│  · enterprise-vue-refiner Skill   │
│  输出: optimization.json + .vue   │
└─────────────────────────────────┘
        │
        ▼
   固定完成 (done)
```

### 1.2 核心问题

| 问题 | 位置 | 说明 |
|------|------|------|
| 编排硬编码 | `pipeline.py:162-167` | `step_generators` 列表固定 4 步，不能跳步、回退、动态选择 |
| 分支靠 if | `pipeline.py:333` | `if ctx.is_ccui` 决定走哪个 AI 服务，不是 Agent 自主判断 |
| 无自主决策 | 全局 | LLM 只是每步的执行者，不是调度者 |
| 无反馈闭环 | 全局 | 生成结果不经过审查，直接输出 |
| 工具无定义 | 全局 | Pipeline 步骤是 Python 函数，没有 Tool Calling Schema |
| 组件库硬编码 | `prompts.py` | Prompt 写死了组件库用法，不能动态查询文档 |

### 1.3 SuperDesign 的 Agent 架构（参考）

```
用户 Prompt
    │
    ▼
┌──────────────────────────────────────┐
│  Agent Loop (AI SDK maxSteps=10)      │
│                                       │
│  ┌──────────────────────────────┐     │
│  │ LLM 自主决策下一步：           │     │
│  │ · 调用哪个工具？               │     │
│  │ · 参数是什么？                 │     │
│  │ · 还需要继续吗？               │     │
│  └──────────────────────────────┘     │
│         │                             │
│         ▼                             │
│  ┌──────────────────────────────┐     │
│  │ 工具执行 (tool execute)       │     │
│  │ · read / write / edit         │     │
│  │ · bash / glob / grep          │     │
│  │ · generateTheme               │     │
│  └──────────────────────────────┘     │
│         │                             │
│         ▼                             │
│  结果回传 LLM → 继续循环或结束        │
└──────────────────────────────────────┘
    │
    ▼
  最终输出
```

**关键差异**：SuperDesign 的 LLM 是决策者，工具是可选的、LLM 自主决定调用哪些。我们的 Pipeline 中 LLM 是执行者，步骤是预定义的。

---

## 2. 改造目标

将现有 Pipeline 改造为 Agent 模式，核心变化：

```
改造前: 用户需求 → 固定 4 步 Pipeline → Vue 代码
改造后: 用户需求 → Agent 自主规划 → 选择工具执行 → 反馈审查 → Vue 代码
```

### 2.1 设计原则

1. **渐进式改造**：新接口与旧 Pipeline 并存，逐步迁移
2. **复用现有能力**：所有现有服务（GLM-5、GLM-4V、OpenClaw）封装为工具
3. **SSE 事件兼容**：前端改动最小，新增 `thinking`、`tool_call` 事件类型
4. **保留回退能力**：旧接口继续可用，出问题随时切回
5. **核心质量步骤不可跳过**：需求标准化和 UX 优化是质量保障的底线，Agent 不能跳过。Agent 的自主性体现在**灵活组合**（如先分析图片再标准化、多次优化迭代），而非跳过质量步骤

---

## 3. 架构设计

### 3.1 整体架构

```
                          ┌─────────────────────────┐
 用户请求 ──SSE─────────▶ │  /api/generate/agent     │  新接口（并行运行）
 (文本+附件)              │         /stream          │
                          └────────────┬────────────┘
                                       │
                          ┌────────────▼────────────┐
                          │    AgentCore (新)        │
                          │                         │
                          │  ┌───────────────────┐  │
                          │  │ Agent Loop        │  │
                          │  │ (while + tool call)│  │
                          │  └───────┬───────────┘  │
                          │          │              │
                          │  ┌───────▼───────────┐  │
                          │  │ Tool Registry     │  │
                          │  │ · analyze_image   │  │
                          │  │ · normalize_req   │  │  ← 必须
                          │  │ · query_ux_spec   │  │  ← 新增
                          │  │ · generate_code   │  │  ← 必须
                          │  │ · optimize_ux     │  │  ← 必须
                          │  │ · search_doc      │  │
                          │  │ · read_file       │  │
                          │  │ · write_file      │  │
                          │  └───────────────────┘  │
                          │                         │
                          │  ┌───────────────────┐  │
                          │  │ System Prompt     │  │
                          │  │ (动态组装)         │  │
                          │  └───────────────────┘  │
                          └────────────┬────────────┘
                                       │ 调用
                          ┌────────────▼────────────┐
                          │  现有服务（复用，不改）     │
                          │  · GLM5Service           │
                          │  · GLM4VService          │
                          │  · OpenclawService       │
                          │  · RequirementService    │
                          │  · AIServiceFactory      │
                          └─────────────────────────┘
```

### 3.2 Agent 核心流程

```python
# 伪代码 — Agent Loop 核心逻辑
messages = [system_prompt, user_message]

for step in range(max_steps):
    # 1. 调用 LLM（Tool Calling）
    response = await llm.chat_completion(messages, tools=tool_definitions)

    # 2. 没有 tool_calls = Agent 认为任务完成
    if not response.tool_calls:
        break

    # 3. 流式推送给前端（SSE）
    await emit("thinking", response.content)
    await emit("tool_calls", response.tool_calls)

    # 4. 执行工具
    for tool_call in response.tool_calls:
        result = await tool_registry.execute(
            tool_call.name, tool_call.arguments
        )
        # 5. 结果回传 LLM
        messages.append(tool_result(tool_call.id, result))

    # 6. （可选）Review Agent 自审
    if should_review():
        review = await review_agent.check(last_result)
        if review.has_issues:
            messages.append(review_feedback)
            continue  # 让 Agent 修复
```

---

## 4. 新增文件与改动清单

### 4.1 文件结构

```
app/
├── agent/                      # 新增：Agent 模块
│   ├── __init__.py
│   ├── core.py                 # Agent Loop 核心逻辑
│   ├── tools.py                # 工具定义 + 注册表
│   ├── prompts.py              # Agent System Prompt
│   └── review.py               # Review Agent（可选，增强项）
│
├── pipeline.py                 # 保留不动（旧接口继续可用）
├── routers/
│   └── generate.py             # 修改：新增 /api/generate/agent/stream
├── utils/
│   └── sse.py                  # 修改：新增 thinking、tool_call 事件类型
├── services/                   # 全部保留不动
│   ├── glm5_service.py
│   ├── glm4v_service.py
│   ├── openclaw_service.py
│   ├── requirement_service.py
│   └── ...
└── config.py                   # 修改：新增 Agent 相关配置
```

### 4.2 新增文件详情

#### `app/agent/core.py` — Agent Loop 核心

```python
"""
Agent 核心循环：LLM 自主决策 + Tool Calling + 结果回传
参考 SuperDesign 的 customAgentService.ts:query() 方法
"""
import json
import logging
from typing import Any, AsyncGenerator
from openai import AsyncOpenAI

from app.agent.tools import ToolRegistry
from app.config import settings
from app.utils.sse import (
    emit_agent_thinking, emit_tool_call_start,
    emit_tool_call_result, emit_agent_done, emit_error,
)
from app.utils.cancellation import is_cancelled

logger = logging.getLogger(__name__)

MAX_STEPS = 10
TOOL_RESULT_MAX_CHARS = 4000  # 单次 tool result 回传 LLM 的最大字符数（约 2000 token）


class AgentCore:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        component_lib: str = "ElementUI",
    ):
        self.tool_registry = tool_registry
        self.component_lib = component_lib
        self.client = AsyncOpenAI(
            api_key=settings.GLM5_API_KEY,
            base_url=settings.GLM5_API_URL.replace("/chat/completions", ""),
        )

    async def run(
        self,
        user_prompt: str,
        attachments: list | None = None,
        session_context: dict | None = None,
        request: Request | None = None,
        task_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """
        Agent 主循环。
        对应 SuperDesign 中的 streamText({ maxSteps: 10 })
        """
        messages = self._build_messages(user_prompt, session_context)
        tools = self.tool_registry.get_openai_tools()

        for step in range(MAX_STEPS):
            # 检查取消
            if task_id and is_cancelled(task_id):
                yield emit_agent_cancelled(step)
                return

            # 调用 LLM（Tool Calling）
            response = await self._call_llm(messages, tools)

            # 推送 Agent 思考过程
            if response.content:
                yield emit_agent_thinking(response.content, step)

            # 没有 tool_calls = 任务完成
            if not response.tool_calls:
                break

            # 推送工具调用信息
            for tc in response.tool_calls:
                yield emit_tool_call_start(
                    tool_name=tc.function.name,
                    arguments=tc.function.arguments,
                    step=step,
                )

            # 执行工具并回传结果
            messages.append(response.message)
            for tc in response.tool_calls:
                try:
                    result = await self.tool_registry.execute(
                        tc.function.name,
                        json.loads(tc.function.arguments),
                    )
                    yield emit_tool_call_result(
                        tool_name=tc.function.name,
                        result=result,
                        step=step,
                    )
                except Exception as e:
                    result = {"error": str(e)}
                    logger.error(f"工具执行失败: {tc.function.name} - {e}")

                # Token 安全网：截断过大的 tool result
                result_json = json.dumps(result, ensure_ascii=False)
                if len(result_json) > TOOL_RESULT_MAX_CHARS:
                    result_json = result_json[:TOOL_RESULT_MAX_CHARS] + f"\n\n[结果已截断，原始长度 {len(result_json)} 字符]"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result_json,
                })

        yield emit_agent_done(files=extract_files_from_messages(messages))

    def _build_messages(self, user_prompt: str, context: dict | None) -> list[dict]:
        system_prompt = self._build_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]

        # 注入历史上下文
        if context and context.get("history"):
            messages.extend(context["history"])

        messages.append({"role": "user", "content": user_prompt})
        return messages

    def _build_system_prompt(self) -> str:
        """动态组装 System Prompt"""
        from app.agent.prompts import build_agent_system_prompt
        return build_agent_system_prompt(
            component_lib=self.component_lib,
            available_tools=self.tool_registry.get_tool_descriptions(),
        )

    async def _call_llm(self, messages, tools):
        """调用 LLM，返回包含 tool_calls 的响应"""
        response = await self.client.chat.completions.create(
            model=settings.GLM5_AGENT_MODEL or settings.GLM5_MODEL,
            messages=messages,
            tools=tools,
            temperature=0.3,
        )
        return response.choices[0].message
```

#### `app/agent/tools.py` — 工具定义 + 注册表

```python
"""
工具定义与注册表。
参考 SuperDesign 的 tools/ 目录，每个工具用 Zod Schema 定义。
这里用 Python dict 定义 OpenAI Tool Calling Schema。
"""
import json
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class ToolDefinition:
    """工具定义，对应 SuperDesign 中 tool({ description, parameters, execute })"""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,      # JSON Schema
        execute: Callable,     # async def (args) -> result
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.execute = execute

    def to_openai_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition):
        self._tools[tool.name] = tool

    def get_openai_tools(self) -> list[dict]:
        return [t.to_openai_tool() for t in self._tools.values()]

    def get_tool_descriptions(self) -> str:
        return "\n".join(
            f"- {t.name}: {t.description}"
            for t in self._tools.values()
        )

    async def execute(self, name: str, arguments: dict) -> Any:
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"未知工具: {name}"}

        logger.info(f"执行工具: {name}, 参数: {json.dumps(arguments, ensure_ascii=False)[:200]}")
        try:
            result = await tool.execute(arguments)
            logger.info(f"工具完成: {name}")
            return result
        except Exception as e:
            logger.error(f"工具异常: {name} - {e}")
            return {"error": str(e)}


def create_tool_registry(
    component_lib: str,
    output_session_id: str,
    message_id: str,
    request=None,
) -> ToolRegistry:
    """
    创建工具注册表，封装现有 Pipeline 步骤为 Agent 工具。
    这是改造的核心：把 pipeline.py 的每个 StepExecutor 方法包装为工具。
    """
    from app.services.glm4v_service import GLM4VService
    from app.services.requirement_service import RequirementService
    from app.services.openclaw_service import OpenclawService
    from app.services.ai_factory import AIServiceFactory
    from app.prompts import get_generation_prompt, get_optimization_prompt
    from app.utils.output import save_stage_output

    registry = ToolRegistry()

    # ── 工具 1: 分析图片 ──
    # 对应 pipeline.py execute_attachment_step 中的图片分析逻辑
    async def analyze_image(args: dict) -> dict:
        """分析设计稿图片，提取布局和组件信息"""
        glm4v = GLM4VService()
        result = await glm4v.describe_for_vue_generation(
            image_source=args["image_source"],
            is_base64=args.get("is_base64", False),
        )
        return result

    registry.register(ToolDefinition(
        name="analyze_image",
        description="分析设计稿图片，提取 UI 布局结构和组件信息。当用户上传了设计稿截图时应调用此工具。",
        parameters={
            "type": "object",
            "properties": {
                "image_source": {
                    "type": "string",
                    "description": "图片 URL 或 Base64 数据",
                },
                "is_base64": {
                    "type": "boolean",
                    "description": "是否为 Base64 格式（默认 false）",
                },
            },
            "required": ["image_source"],
        },
        execute=analyze_image,
    ))

    # ── 工具 2: 需求标准化 ──
    # 对应 pipeline.py execute_requirement_step
    async def normalize_requirement(args: dict) -> dict:
        """将用户需求标准化为 UX 规格文档"""
        service = RequirementService()
        result = await service.standardize_requirement(
            user_requirement=args["requirement"],
            temperature=0.2,
        )
        if result["status"] == "failed":
            return {"error": result.get("error"), "requirement": None}
        return {"requirement": result["output"]}

    registry.register(ToolDefinition(
        name="normalize_requirement",
        description="【必须步骤】将用户的自然语言需求标准化为结构化的 UX 规格文档。无论需求是详细文档还是一句话描述，都必须经过标准化处理：去噪（去除权限/API等技术细节）、结构化（统一为页面概览+页面结构+交互说明格式）、补全（合理推导缺失的组件和字段）。"
        parameters={
            "type": "object",
            "properties": {
                "requirement": {
                    "type": "string",
                    "description": "用户的原始需求描述（可能包含图片分析结果）",
                },
            },
            "required": ["requirement"],
        },
        execute=normalize_requirement,
    ))

    # ── 工具 3: 生成 Vue 代码 ──
    # 对应 pipeline.py execute_generation_step
    # 参考 SuperDesign 的 write-tool：写操作只返回元数据，不回传完整内容
    async def generate_vue_code(args: dict) -> dict:
        """根据 UX 文档生成 Vue 3 组件代码"""
        prompt = args["requirement"]
        existing_files = args.get("existing_files")

        if component_lib.lower() == "ccui":
            service = OpenclawService()
            full_prompt = get_generation_prompt(component_lib, prompt)
            result = await service.generate_vue_files(prompt=full_prompt)
        else:
            service = AIServiceFactory.get_service()
            result = await service.generate_vue_files(
                prompt=prompt,
                existing_files=existing_files,
            )

        files = result.get("files", [])
        message = result.get("message", "代码生成完成")

        # 保存到文件系统（复用现有逻辑）
        save_stage_output(
            "generation", 2, result,
            output_session_id, message_id, "json",
        )

        # 只返回摘要，不回传完整代码（参考 SuperDesign write-tool 设计）
        # Agent 不需要看到自己刚生成的代码全文，只需知道生成了什么
        file_summaries = []
        for f in files:
            content = f.get("content", "")
            file_summaries.append({
                "name": f.get("name", "unknown"),
                "path": f.get("path", ""),
                "lines": content.count("\n") + 1 if content else 0,
                "size_bytes": len(content.encode("utf-8")) if content else 0,
            })

        return {
            "status": "success",
            "file_count": len(files),
            "files": file_summaries,
            "message": message,
        }

    registry.register(ToolDefinition(
        name="generate_vue_code",
        description="根据 UX 规格文档生成 Vue 3 组件代码（SFC 格式）。生成后会自动保存。当需求足够清晰时应调用此工具。",
        parameters={
            "type": "object",
            "properties": {
                "requirement": {
                    "type": "string",
                    "description": "UX 规格文档或详细需求描述",
                },
                "existing_files": {
                    "type": "array",
                    "description": "已有的 Vue 文件（迭代修改时传入）",
                    "items": {"type": "object"},
                },
            },
            "required": ["requirement"],
        },
        execute=generate_vue_code,
    ))

    # ── 工具 4: UX 优化 ──
    # 对应 pipeline.py execute_optimization_step
    # 参考 SuperDesign 的 edit-tool：只返回元数据，不回传完整代码
    async def optimize_ux(args: dict) -> dict:
        """对已生成的 Vue 代码进行 UX 优化"""
        openclaw = OpenclawService()
        opt_prompt = get_optimization_prompt(component_lib)
        files_json = json.dumps(args["files"], ensure_ascii=False, indent=2)
        full_prompt = f"{opt_prompt}\n\n待优化的文件：\n{files_json}\n"

        result = await openclaw.generate_vue_files(prompt=full_prompt)

        optimized_files = result.get("files", [])
        save_stage_output(
            "optimization", 3, result,
            output_session_id, message_id, "json",
        )

        # 只返回摘要，不回传完整代码
        file_summaries = []
        for f in optimized_files:
            content = f.get("content", "")
            file_summaries.append({
                "name": f.get("name", "unknown"),
                "path": f.get("path", ""),
                "lines": content.count("\n") + 1 if content else 0,
                "size_bytes": len(content.encode("utf-8")) if content else 0,
            })

        return {
            "status": "success",
            "file_count": len(optimized_files),
            "files": file_summaries,
            "message": result.get("message", "UX 优化完成"),
        }

    registry.register(ToolDefinition(
        name="optimize_ux",
        description="【必须步骤】对已生成的 Vue 代码进行 UX 样式和布局优化。通过 ccui-ux-guardian / enterprise-vue-refiner Skill 执行，Skill 内含 CSV 规范文件（颜色、字体、间距、阴影、圆角、组件规则等 Design Tokens），确保代码符合企业 UX 标准。代码生成后必须调用此工具。"
        parameters={
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "description": "待优化的 Vue 文件列表",
                    "items": {"type": "object"},
                },
            },
            "required": ["files"],
        },
        execute=optimize_ux,
    ))

    # ── 工具 5: 查询 UX 规范 ──（新增能力）
    # Pipeline 中没有，Agent 模式新增
    # 数据源：Skill 目录下的 CSV 规范文件
    #   - CcUI: ccui-ux-guardian/data/{foundation,component,global-layout}-rules.csv
    #   - ElementUI: enterprise-vue-refiner/data/{foundation,component,global-layout}-rules.csv
    #   - 通用: enterprise-ui-ux-refiner/data/tailwind-token-mapping.csv
    async def query_ux_spec(args: dict) -> dict:
        """查询企业 UX 设计规范（Design Tokens）"""
        spec_type = args["spec_type"]  # foundation / component / layout / token_mapping
        topic = args.get("topic", "")  # 可选：按主题过滤（如 color、spacing、table）
        max_rules = args.get("max_rules", 20)  # 默认最多返回 20 条，防止 token 膨胀
        return await _query_ux_spec_files(component_lib, spec_type, topic, max_rules)

    registry.register(ToolDefinition(
        name="query_ux_spec",
        description="查询企业 UX 设计规范（Design Tokens），包括颜色、字体、间距、阴影、圆角、组件规则、布局规则等。数据来自 Skill 的 CSV 规范文件。生成代码前或优化时调用此工具，确保代码符合企业 UX 标准。",
        parameters={
            "type": "object",
            "properties": {
                "spec_type": {
                    "type": "string",
                    "enum": ["foundation", "component", "layout", "token_mapping"],
                    "description": "规范类型：foundation=基础样式（颜色/字体/间距/阴影/圆角）、component=组件规则（表格/表单/按钮等）、layout=全局布局（安全边距/页面背景/导航）、token_mapping=Tailwind Token 映射",
                },
                "topic": {
                    "type": "string",
                    "description": "可选。按主题关键词过滤规则（如 'color'、'spacing'、'table'、'form'、'button'）。留空返回该类型全部规则。",
                },
                "max_rules": {
                    "type": "integer",
                    "description": "可选。返回规则的最大条数（默认 20），防止 token 消耗过大。只在需要全面了解某类规范时才调大此值。",
                },
            },
            "required": ["spec_type"],
        },
        execute=query_ux_spec,
    ))

    # ── 工具 6: 查询组件库文档 ──（新增能力）
    # 数据源：Skill 目录下的组件 MD 文档
    #   - CcUI: vue3-ccui-generator/references/{component}.md（60+ 组件文档）
    #   - ElementUI: 内网文档 API 或 Element Plus 官方文档
    async def search_component_doc(args: dict) -> dict:
        """查询组件库文档，获取组件用法和属性"""
        query = args["query"]
        lib = args.get("component_lib", component_lib)
        return await _query_component_library(lib, query)

    registry.register(ToolDefinition(
        name="search_component_doc",
        description="查询组件库文档，获取组件的用法、属性、示例代码。CcUI 组件文档来自 vue3-ccui-generator Skill 的 references/ 目录（60+ 组件 MD 文件）。不确定组件用法时应先查询。",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "要查询的组件名称或关键词（如 '表格'、'表单验证'、'日期选择器'）",
                },
                "component_lib": {
                    "type": "string",
                    "enum": ["CcUI", "ElementUI", "aui"],
                    "description": "要查询的组件库（默认使用当前组件库）",
                },
            },
            "required": ["query"],
        },
        execute=search_component_doc,
    ))

    return registry


# ── UX 规范查询实现 ──

# Skill CSV 文件路径映射
_SKILL_DATA_DIR = os.path.expanduser("~/.openclaw/skills")
_UX_SPEC_PATHS = {
    "ccui": {
        "foundation": os.path.join(_SKILL_DATA_DIR, "ccui-ux-guardian/data/foundation-rules.csv"),
        "component": os.path.join(_SKILL_DATA_DIR, "ccui-ux-guardian/data/component-rules.csv"),
        "layout": os.path.join(_SKILL_DATA_DIR, "ccui-ux-guardian/data/global-layout-rules.csv"),
    },
    "elementui": {
        "foundation": os.path.join(_SKILL_DATA_DIR, "enterprise-vue-refiner/data/foundation-rules.csv"),
        "component": os.path.join(_SKILL_DATA_DIR, "enterprise-vue-refiner/data/component-rules.csv"),
        "layout": os.path.join(_SKILL_DATA_DIR, "enterprise-vue-refiner/data/global-layout-rules.csv"),
    },
}
_TOKEN_MAPPING_PATH = os.path.join(_SKILL_DATA_DIR, "enterprise-ui-ux-refiner/data/tailwind-token-mapping.csv")


async def _query_ux_spec_files(
    component_lib: str,
    spec_type: str,
    topic: str = "",
    max_rules: int = 20,
) -> dict:
    """
    从 Skill CSV 文件查询 UX 规范。
    返回匹配的规则列表，每条规则包含 rule_id、title、preferred_pattern、anti_pattern、tailwind_ref。
    max_rules 限制返回条数，防止 tool result 过大导致 token 膨胀。
    """
    import csv
    import io

    if spec_type == "token_mapping":
        csv_path = _TOKEN_MAPPING_PATH
    else:
        lib_key = "ccui" if component_lib.lower() == "ccui" else "elementui"
        csv_path = _UX_SPEC_PATHS.get(lib_key, {}).get(spec_type)

    if not csv_path or not os.path.exists(csv_path):
        return {"error": f"规范文件不存在: {spec_type}", "rules": []}

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rules = []
            for row in reader:
                # 按主题关键词过滤
                if topic and topic.lower() not in row.get("topic", "").lower() \
                          and topic.lower() not in row.get("title", "").lower():
                    continue
                rules.append({
                    "rule_id": row.get("rule_id", ""),
                    "topic": row.get("topic", ""),
                    "title": row.get("title", ""),
                    "requirement": row.get("requirement", ""),
                    "preferred_pattern": row.get("preferred_pattern", ""),
                    "anti_pattern": row.get("anti_pattern", ""),
                    "tailwind_ref": row.get("tailwind_ref", ""),
                })

            # 限制返回条数，防止 token 膨胀
            truncated = len(rules) > max_rules
            rules = rules[:max_rules]

        return {
            "spec_type": spec_type,
            "component_lib": component_lib,
            "topic_filter": topic or "(全部)",
            "total_rules": len(rules),
            "truncated": truncated,
            "rules": rules,
        }
    except Exception as e:
        return {"error": str(e), "rules": []}


# ── 组件库文档查询实现 ──

# CcUI 组件文档路径（vue3-ccui-generator Skill 的 references/ 目录）
_CCUI_DOCS_DIR = os.path.join(_SKILL_DATA_DIR, "vue3-ccui-generator/references")


async def _query_component_library(component_lib: str, query: str) -> dict:
    """
    查询组件库文档。
    CcUI: 从 vue3-ccui-generator/references/ 读取对应组件 MD 文件
    ElementUI/aui: 可接入内网文档 API 或其他文档源
    """
    if component_lib.lower() == "ccui":
        return await _query_ccui_doc(query)
    else:
        # ElementUI / aui：可接入内网文档 API
        return await _query_element_doc(component_lib, query)


async def _query_ccui_doc(query: str) -> dict:
    """查询 CcUI 组件文档（遍历 references/ 目录模糊匹配，返回结构化摘要）"""
    import re

    if not os.path.isdir(_CCUI_DOCS_DIR):
        return {
            "component_lib": "CcUI",
            "query": query,
            "found": False,
            "message": f"组件文档目录不存在: {_CCUI_DOCS_DIR}",
        }

    # 遍历 references/ 目录，模糊匹配文件名
    query_lower = query.lower().strip()
    matched_files = []
    for filename in os.listdir(_CCUI_DOCS_DIR):
        if not filename.endswith(".md"):
            continue
        # 去掉 .md 后缀，用文件名做模糊匹配
        doc_name = filename[:-3]
        if query_lower in doc_name.lower() or doc_name.lower() in query_lower:
            matched_files.append((doc_name, os.path.join(_CCUI_DOCS_DIR, filename)))

    if not matched_files:
        # 列出所有可用组件供 LLM 参考
        all_components = sorted(f[:-3] for f in os.listdir(_CCUI_DOCS_DIR) if f.endswith(".md"))
        return {
            "component_lib": "CcUI",
            "query": query,
            "found": False,
            "message": f"未找到组件 '{query}' 的文档。可用的组件包括: {', '.join(all_components[:30])}",
        }

    # 取最匹配的第一个文件（精确匹配优先）
    exact_match = next((d for d, _ in matched_files if d.lower() == query_lower), None)
    doc_name, doc_path = matched_files[0] if not exact_match else (exact_match, os.path.join(_CCUI_DOCS_DIR, f"{exact_match}.md"))

    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 返回结构化摘要而非截断原文，减少 token 消耗
        # 提取：组件名 + 用途描述（第一个 ## 段落）+ 核心属性表格（前 10 个）+ 示例代码（前 30 行）
        summary = _extract_doc_summary(content, doc_name, max_chars=3000)

        return {
            "component_lib": "CcUI",
            "query": query,
            "component_name": doc_name,
            "found": True,
            "summary": summary,
        }
    except Exception as e:
        return {"component_lib": "CcUI", "query": query, "found": False, "error": str(e)}


def _extract_doc_summary(content: str, component_name: str, max_chars: int = 3000) -> str:
    """从 MD 文档中提取结构化摘要：组件概述 + 核心属性 + 简要用法"""
    import re

    sections = [f"## 组件: {component_name}"]

    # 提取第一个标题段落作为概述（到下一个 ## 之前）
    first_section = re.split(r"\n## ", content, maxsplit=2)
    if len(first_section) >= 2:
        overview = first_section[1].strip()
        if len(overview) > 800:
            overview = overview[:800] + "\n...(概述已截断)"
        sections.append(overview)

    # 提取属性表格（Props 表格的前 15 行）
    props_match = re.search(r"(#+\s*(?:Props|属性|Attributes).*?\n)(\|.+\|(\n\|[-:\s|]+\|)?\n(\|.+?\|\n){0,15})", content, re.IGNORECASE | re.DOTALL)
    if props_match:
        sections.append("\n### 核心属性\n" + props_match.group(2).strip()[:600])

    summary_text = "\n\n".join(sections)
    if len(summary_text) > max_chars:
        summary_text = summary_text[:max_chars] + "\n\n...(文档摘要已截断)"
    return summary_text


async def _query_element_doc(component_lib: str, query: str) -> dict:
    """查询 ElementUI / aui 文档（占位，可接入内网文档 API）"""
    # TODO: 接入内网文档 API
    return {
        "component_lib": component_lib,
        "query": query,
        "found": False,
        "message": f"{component_lib} 文档查询暂未接入，建议参考官方文档。",
    }
```

#### `app/agent/prompts.py` — Agent System Prompt

```python
"""
Agent System Prompt。
参考 SuperDesign 的 getSystemPrompt() 方法，但面向 Vue 代码生成场景重写。
"""


def build_agent_system_prompt(
    component_lib: str,
    available_tools: str,
) -> str:
    return f"""# Role
你是一个专业的 Vue 3 前端原型设计 Agent，集成在 Design AI 后端服务中。
你的目标是通过理解用户需求，自主规划步骤，生成高质量的 Vue 3 原型页面代码。

# Context
- 当前组件库: {component_lib}
- 工作模式: Agent 模式（自主决策）
- 输出格式: Vue 3 SFC (.vue 文件)

# Available Tools
{available_tools}

# Instructions

## 工作流程
你应该始终执行以下核心步骤，但可以根据输入情况灵活组合和调整执行方式：

1. **分析输入**：检查用户是否上传了图片、需求描述的完整度
2. **需求标准化**（必须）：将用户需求转换为结构化 UX 文档
   - 有图片时：先调用 analyze_image 分析布局，将图片信息整合进需求再标准化
   - 需求模糊时：标准化过程会自动补全合理推导（标注※）
   - 需求已详细时：标准化过程会去噪、结构化、统一格式
   - 无论需求长短，标准化都能产出更清晰的描述，为后续生成提供质量保障
3. **查询规范和文档**（可选，按需）：
   - 调用 query_ux_spec 查询企业 UX 规范（Design Tokens），在生成时就遵循规范
   - 调用 search_component_doc 查询组件用法，确保使用正确的组件 API
4. **代码生成**（必须）：根据标准化后的 UX 文档生成 Vue 3 代码
   - 如果生成结果有问题，可以重新调用 generate_vue_code 生成
5. **UX 优化**（必须）：调用 optimize_ux 对代码进行样式优化
   - 优化 Skill 会根据 CSV 规范文件自动修正不符合企业 UX 标准的样式
   - 如果优化后仍有问题，可以多次调用 optimize_ux 迭代优化
6. **自审**（可选）：审查生成结果，如有遗漏则补充修改

## Agent 的自主性
你的自主性体现在以下方面（而非跳过步骤）：
- ✅ 灵活组合：先分析图片再标准化，或标准化后查询组件文档再生成
- ✅ 多次执行：对同一个工具可以多次调用（如重新生成、多次优化）
- ✅ 动态插入：在标准化和生成之间插入文档查询、规范查询等辅助步骤
- ✅ 自主修复：发现生成结果有问题时，自主决定重试策略
- ❌ 不可跳过：需求标准化和 UX 优化是质量底线，不能跳过

## 代码生成规范
- Vue 3 Composition API（`<script setup lang="ts">`）
- 原型极简原则：mock 数据，不需要 API 调用、表单验证等复杂逻辑
- 每个文件不超过 300 行
- 尽量只生成 MainPage.vue 一个文件（除非页面复杂需要拆分）
- 不要生成 main.ts、App.vue、index.html 等配置文件
- 使用了 Element Plus 图标时必须在 script 中显式导入

## 输出格式
- 代码生成结果为 JSON 格式：{{"files": [...], "message": "说明"}}
- 每个文件包含 id、name、path、type、language、content 字段
- content 字段中的代码必须正确转义

## 与旧 Pipeline 的区别
- 你不是固定执行 4 步，而是自主组合工具、灵活调整执行顺序
- 你可以多次调用同一个工具（比如先生成、再修改、再优化）
- 你可以在任何阶段查询组件库文档和 UX 规范
- 需求标准化和 UX 优化是必须步骤，但你可以在中间插入其他辅助步骤
- 你可以根据生成结果质量决定是否需要重新生成或多次优化

## 注意事项
- 如果 generate_vue_code 返回的代码有错误，尝试分析原因并重新生成
- 如果 optimize_ux 返回空文件，尝试用不同的参数再次调用，或直接返回生成结果并说明
- 生成代码前可以先调用 query_ux_spec 了解企业 UX 规范，减少后续优化的工作量
- 始终以用户原始需求为最终标准，不要偏离用户意图
"""


def build_review_prompt(component_lib: str) -> str:
    """Review Agent 的 System Prompt（可选增强项）"""
    return f"""你是一个 Vue 3 代码审查专家，负责审查 {component_lib} 组件库的原型代码。

审查维度：
1. **结构完整性**：组件是否闭合、props 是否定义、import 是否齐全
2. **组件库合规**：是否使用了正确的组件 API（{component_lib}）
3. **需求覆盖度**：对比需求文档，检查是否有遗漏的功能点
4. **代码质量**：重复代码、过深的嵌套、缺失的响应式处理

输出格式：
{{"pass": true/false, "issues": ["问题1", "问题2"], "severity": "major/minor"}}
"""
```

#### `app/agent/review.py` — Review Agent（可选增强项）

```python
"""
Review Agent：代码生成后的自审环节。
对应 AGENT_UPGRADE_PLAN.md 中的 "Review Agent 自审"。
"""
import json
import logging
from openai import AsyncOpenAI

from app.config import settings
from app.agent.prompts import build_review_prompt

logger = logging.getLogger(__name__)


async def review_generated_code(
    requirement: str,
    files: list[dict],
    component_lib: str,
) -> dict:
    """
    审查生成的 Vue 代码。
    返回: {"pass": bool, "issues": list, "severity": str}
    """
    client = AsyncOpenAI(
        api_key=settings.GLM5_API_KEY,
        base_url=settings.GLM5_API_URL.replace("/chat/completions", ""),
    )

    files_summary = "\n".join(
        f"文件: {f.get('name')}\n```\n{f.get('content', '')[:2000]}\n```"
        for f in files
    )

    messages = [
        {"role": "system", "content": build_review_prompt(component_lib)},
        {"role": "user", "content": f"需求文档：\n{requirement}\n\n生成的代码：\n{files_summary}"},
    ]

    response = await client.chat.completions.create(
        model=settings.GLM5_MODEL,
        messages=messages,
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.warning(f"Review 结果解析失败: {content[:200]}")
        return {"pass": True, "issues": [], "severity": "none"}
```

### 4.3 修改文件详情

#### `app/utils/sse.py` — 新增 SSE 事件类型

在现有事件基础上，新增 Agent 专用事件：

```python
# ── 新增以下函数 ──

def emit_agent_thinking(content: str, step: int) -> str:
    """Agent 思考过程（LLM 输出的推理文本）"""
    return _sse_event("agent_thinking", {
        "content": content,
        "step": step,
        "timestamp": _now_iso(),
    })


def emit_tool_call_start(
    tool_name: str,
    arguments: str,
    step: int,
) -> str:
    """Agent 决定调用工具"""
    return _sse_event("tool_call_start", {
        "toolName": tool_name,
        "arguments": arguments,
        "step": step,
        "timestamp": _now_iso(),
    })


def emit_tool_call_result(
    tool_name: str,
    result: dict,
    step: int,
) -> str:
    """工具执行结果"""
    return _sse_event("tool_call_result", {
        "toolName": tool_name,
        "result": result,
        "step": step,
        "timestamp": _now_iso(),
    })


def emit_agent_done(files: list | None = None) -> str:
    """Agent 任务完成"""
    data = {"timestamp": _now_iso()}
    if files:
        data["files"] = files
    return _sse_event("agent_done", data)


def emit_agent_cancelled(cancelled_at_step: int) -> str:
    """Agent 任务被取消"""
    return _sse_event("agent_cancelled", {
        "cancelledAtStep": cancelled_at_step,
        "timestamp": _now_iso(),
    })
```

#### `app/routers/generate.py` — 新增 Agent 路由

在现有路由旁新增：

```python
# ── 新增以下代码 ──

from app.agent.core import AgentCore
from app.agent.tools import create_tool_registry
from app.utils.sse import (
    emit_agent_thinking, emit_tool_call_start,
    emit_tool_call_result, emit_agent_done, emit_agent_cancelled,
    emit_done,
)


@router.post("/generate/agent/stream")
async def generate_agent_stream(body: GenerateInitialRequest, request: Request):
    """
    Agent 模式的流式生成接口。
    与 /generate/initial/stream 并行运行，前端可切换使用。
    """
    logger.info(f"[Agent SSE] 收到 Agent 生成请求 - componentLib: {body.componentLib}")

    output_session_id = body.sessionId or f"no_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    message_id = str(uuid4())
    output_dir = os.path.join("output", output_session_id, message_id)
    os.makedirs(output_dir, exist_ok=True)

    db = get_database() if body.sessionId else None
    register_cancel(message_id)

    tool_registry = create_tool_registry(
        component_lib=body.componentLib,
        output_session_id=output_session_id,
        message_id=message_id,
        request=request,
    )

    agent = AgentCore(
        tool_registry=tool_registry,
        component_lib=body.componentLib,
    )

    async def event_stream():
        try:
            # 处理附件（如有图片则提取 base64）
            user_prompt = body.prompt or ""

            # 构建附件上下文
            if body.attachments:
                for att in body.attachments:
                    if att.type == "image" and att.url.startswith("/uploads/"):
                        local_path = att.url[1:]
                        if os.path.exists(local_path):
                            with open(local_path, "rb") as f:
                                user_prompt += f"\n\n[附件图片: {att.name}]"
                            # 图片信息传给 Agent，Agent 自主决定是否调用 analyze_image

            async for event in agent.run(
                user_prompt=user_prompt,
                attachments=[a.model_dump() for a in body.attachments] if body.attachments else None,
                task_id=message_id,
            ):
                yield event

            # 保存会话（复用现有逻辑）
            # TODO: 从 Agent 执行结果中提取 files 并保存

        finally:
            unregister_cancel(message_id)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
```

#### `app/config.py` — 新增配置项

```python
# 在 Settings 类中新增以下字段：

# Agent 配置
AGENT_MAX_STEPS: int = 10
AGENT_ENABLE_REVIEW: bool = False
GLM5_AGENT_MODEL: Optional[str] = ""  # Agent 专用模型（留空则使用 GLM5_MODEL）
```

---

## 5. SSE 事件对照表

| 事件类型 | 阶段 | 说明 | 新增/保留 |
|----------|------|------|-----------|
| `stage_start` | 旧 Pipeline | 阶段开始 | 保留 |
| `stage_progress` | 旧 Pipeline | 阶段进度 | 保留 |
| `stage_complete` | 旧 Pipeline | 阶段完成 | 保留 |
| `agent_thinking` | Agent | Agent 思考过程（LLM 推理文本） | **新增** |
| `tool_call_start` | Agent | Agent 决定调用工具 | **新增** |
| `tool_call_result` | Agent | 工具执行结果 | **新增** |
| `agent_done` | Agent | Agent 任务完成 | **新增** |
| `agent_cancelled` | Agent | Agent 任务取消 | **新增** |
| `done` | 通用 | 全部完成 | 保留 |
| `error` | 通用 | 错误 | 保留 |
| `cancelled` | 通用 | 取消 | 保留 |

**前端影响**：旧接口事件格式完全不变。新接口新增 4 个事件类型，前端需监听处理。

---

## 6. 旧 Pipeline vs Agent 模式对比

### 6.1 执行流程对比

**场景：用户上传一张 Dashboard 设计稿**

| 步骤 | 旧 Pipeline | Agent 模式 |
|------|-------------|------------|
| 1 | Step 0: 分析图片（固定执行） | Agent 判断有图片 → 调用 `analyze_image` |
| 2 | Step 1: 需求标准化（固定执行） | Agent 将图片分析结果整合进需求 → 调用 `normalize_requirement` 标准化 |
| 3 | Step 2: 代码生成（固定执行） | Agent 调用 `query_ux_spec("foundation")` 查询颜色/间距规范 |
| 4 | — | Agent 不确定 Form 组件用法 → 调用 `search_component_doc("Form")` 查询组件文档 |
| 5 | Step 2: 代码生成 | Agent 调用 `generate_vue_code` 生成代码（已参考规范和组件文档） |
| 6 | Step 3: UX 优化（固定执行） | Agent 调用 `optimize_ux` 按 CSV 规范精修 |
| 7 | 固定完成 | Agent 审查结果满意 → 结束 |

**场景：用户说"做一个登录页"**

| 步骤 | 旧 Pipeline | Agent 模式 |
|------|-------------|------------|
| 1 | Step 0: 无附件，直接传 prompt | Agent 判断无图片，直接进入标准化 |
| 2 | Step 1: 需求标准化（固定执行） | Agent 调用 `normalize_requirement` → 得到结构化登录页文档（字段、组件、交互） |
| 3 | Step 2: 代码生成（固定执行） | Agent 调用 `generate_vue_code` 生成代码 |
| 4 | Step 3: UX 优化（固定执行） | Agent 调用 `optimize_ux` 确保样式符合规范 |
| 5 | 固定完成 | 结束（4 步 vs 旧 4 步，但中间可灵活插入规范查询） |

> **关键区别**：Agent 模式不会跳过标准化和 UX 优化，但可以动态插入 `query_ux_spec`、`search_component_doc` 等辅助步骤，并在生成/优化结果不理想时自主重试。

### 6.2 能力对比

| 能力 | 旧 Pipeline | Agent 模式 |
|------|-------------|------------|
| 固定 4 步执行 | 是 | 否（灵活组合） |
| 跳过核心质量步骤 | 不支持 | **不支持**（标准化和 UX 优化不可跳过） |
| 重复调用同一步骤 | 不支持 | 支持（如多次生成、多次优化） |
| 动态查询组件库文档 | 不支持 | 支持（search_component_doc，读取 Skill references/ MD 文件） |
| 动态查询 UX 规范 | 不支持 | 支持（query_ux_spec，读取 Skill CSV 规范文件） |
| 代码自审 + 自动修复 | 不支持 | 支持（Review Agent） |
| 灵活处理异常 | from_step 断点重试 | Agent 自主决定重试策略 |
| SSE 实时进度 | stage 事件 | thinking + tool_call 事件 |
| 前端兼容性 | 完全兼容 | 需监听新事件类型 |

---

## 7. SuperDesign 关键参考点

以下是 SuperDesign 中值得参考的具体实现：

| 参考点 | SuperDesign 文件 | 在我们项目中的对应 |
|--------|-------------------|-------------------|
| Agent Loop | `customAgentService.ts:659-916` | `app/agent/core.py` |
| 工具定义格式 | `tools/read-tool.ts` (Zod Schema) | `app/agent/tools.py` (JSON Schema) |
| System Prompt | `customAgentService.ts:184-585` | `app/agent/prompts.py` |
| 工具执行上下文 | `types/agent.ts` ExecutionContext | `ToolRegistry` 构造参数 |
| 流式工具调用 | `customAgentService.ts:779-868` | `sse.py` 新增事件 |
| maxSteps 控制 | `customAgentService.ts:689` | `config.py` AGENT_MAX_STEPS |
| 多模型切换 | `customAgentService.ts:83-181` getModel() | `AIServiceFactory`（已有） |

---

## 8. Skill 调用链路

Agent 模式下，多个工具通过 OpenClaw 与 Skill 交互。以下是完整的调用链路和数据源说明：

### 8.1 调用链路图

```
Agent (LLM + Tool Calling)
  │
  ├── normalize_requirement
  │     └── RequirementService → GLM-5 → requirement_template.md → 结构化 UX 文档
  │
  ├── query_ux_spec  ← 新增工具
  │     └── 直接读取 Skill CSV 文件（不经过 OpenClaw）
  │           ├── ccui-ux-guardian/data/foundation-rules.csv    (FDN: 颜色/字体/间距/阴影/圆角)
  │           ├── ccui-ux-guardian/data/component-rules.csv     (CMP: 表格/表单/按钮等组件规则)
  │           ├── ccui-ux-guardian/data/global-layout-rules.csv (LAY: 安全边距/页面背景/导航)
  │           └── enterprise-ui-ux-refiner/data/tailwind-token-mapping.csv (CSS 变量→Tailwind 映射)
  │
  ├── search_component_doc
  │     └── 直接读取 Skill MD 文件（CcUI）/ 内网 API（ElementUI）
  │           └── vue3-ccui-generator/references/*.md  (60+ 组件文档：table, form, input, select...)
  │
  ├── generate_vue_code
  │     ├── CcUI → OpenclawService → OpenClaw Agent → vue3-ccui-generator Skill
  │     └── ElementUI/aui → AIServiceFactory → GLM-5 直接生成
  │
  └── optimize_ux
        └── OpenclawService → OpenClaw Agent
              ├── CcUI → ccui-ux-guardian Skill（读取 CSV 规范修正样式）
              └── ElementUI → enterprise-vue-refiner Skill（读取 CSV 规范修正样式）
```

### 8.2 数据源说明

| 数据 | 位置 | 格式 | 用途 |
|------|------|------|------|
| 基础样式规范 | `ccui-ux-guardian/data/foundation-rules.csv` | CSV (FDN-001~014) | 颜色、字体、间距、阴影、圆角的 Design Tokens |
| 组件规则 | `ccui-ux-guardian/data/component-rules.csv` | CSV (CMP-001~033) | 表格/表单/按钮/下拉框等组件的规范用法 |
| 全局布局规则 | `ccui-ux-guardian/data/global-layout-rules.csv` | CSV (LAY-001~010) | 安全边距、页面背景、导航、卡片等布局规范 |
| Tailwind Token 映射 | `enterprise-ui-ux-refiner/data/tailwind-token-mapping.csv` | CSV | CSS 变量（如 `--ccui-space-xs`）→ Tailwind 类名（如 `space-1`）的映射 |
| CcUI 组件文档 | `vue3-ccui-generator/references/*.md` | MD (60+ 文件) | 每个组件的用法、属性、示例代码 |
| 需求标准化模板 | `app/prompts/requirement_template.md` | MD | 标准化 Prompt 模板，定义输出格式 |

### 8.3 设计要点

- **`query_ux_spec` 直接读 CSV**：不走 OpenClaw Agent，直接在 Python 层读取 CSV 文件，减少一次 LLM 调用，速度更快
- **`search_component_doc` 直接读 MD**：CcUI 组件文档同样直接读取本地 MD 文件，不走 OpenClaw
- **`generate_vue_code` 和 `optimize_ux` 走 OpenClaw**：需要 Skill 的完整推理能力（加载 CSV、逐项修正），必须通过 OpenClaw Agent 调用
- **Agent 可提前感知规范**：通过 `query_ux_spec` 在生成前就了解规范，让 `generate_vue_code` 产出更合规的代码，减轻 `optimize_ux` 的修正压力

---

## 9. 实施步骤

### Phase 1：基础 Agent（1-2 周）

```
Week 1
├── Day 1-2: 创建 app/agent/ 目录，实现 core.py + tools.py
│   ├── Agent Loop（while + tool calling）
│   └── 6 个工具定义（封装现有服务 + query_ux_spec + search_component_doc）
│
├── Day 3-4: 实现 prompts.py + SSE 事件扩展
│   ├── Agent System Prompt
│   └── sse.py 新增 4 个事件类型
│
├── Day 5: 新增 /api/generate/agent/stream 路由
│   └── 与旧接口并行，前端可切换
│
Week 2
├── Day 1-2: 联调测试
│   ├── 纯文本需求（简单场景）
│   ├── 图片 + 文本需求（复杂场景）
│   └── 迭代修改场景
│
├── Day 3-4: 接入 Skill 数据源
│   ├── 实现 query_ux_spec 的 CSV 文件读取
│   └── 实现 search_component_doc 的 CcUI MD 文件读取
│
└── Day 5: Bug 修复 + 边界 case 处理
    ├── 工具执行超时
    ├── LLM 不调用工具直接回复
    └── 连续调用同一工具的防护
```

### Phase 2：增强 Agent（2-3 周）

```
├── Review Agent 自审（代码生成后自动审查）
├── 流式 Tool Calling（LLM 输出工具参数时实时推送）
├── 上下文管理（对话过长时自动裁剪）
└── Agent 执行日志可视化（每步决策可追踪）
```

### Phase 3：多 Agent 协作（长期）

```
├── Orchestrator Agent（总调度）
├── Design Analyst Agent（需求分析专家）
├── Code Generator Agent（代码生成专家）
├── UX Refiner Agent（样式优化专家）
└── Doc Search Agent（组件库文档专家）
```

---

## 10. 风险与应对

| 风险 | 说明 | 应对 |
|------|------|------|
| LLM 不按预期调用工具 | GLM-5 的 Tool Calling 能力未经充分验证 | 1. 提前测试 Tool Calling 稳定性 2. System Prompt 中明确指引调用时机 |
| Token 消耗增加 | Agent Loop 多轮对话，tool result 作为 tool message 回传 LLM 全部参与计费 | 1. 设置 maxSteps 上限（10） 2. **generate_vue_code / optimize_ux 只返回元数据摘要**（文件名+行数），不回传完整代码（参考 SuperDesign write-tool 设计） 3. **query_ux_spec 默认最多 20 条规则**，有 max_rules 参数可控 4. **search_component_doc 返回结构化摘要**（概述+核心属性），不回传完整 MD 原文 5. **Agent Loop 全局安全网**：单次 tool result 超 4000 字符自动截断 |
| 执行时间变长 | Agent 需要多轮 LLM 调用 | 1. SSE 实时推送进度，用户体验不变 2. query_ux_spec/search_component_doc 直接读文件（毫秒级），不增加耗时 |
| 前端改动 | 需要监听新事件类型 | 1. 旧接口继续可用 2. 新接口渐进式切换 |
| 旧接口废弃 | 团队习惯旧 Pipeline | 1. 两套并行运行 2. 验证 Agent 稳定后再逐步迁移 |

---

## 11. 依赖变化

### 新增依赖

```
openai>=1.0.0    # OpenAI Python SDK（用于 Tool Calling + 流式）
```

仅新增一个依赖。`openai` SDK 原生支持 Tool Calling，智谱 GLM-5 API 兼容 OpenAI 协议，无需其他 SDK。

### 移除依赖

无。旧 Pipeline 代码完整保留。

---

*创建时间：2026-04-15*
*参考项目：SuperDesign (https://github.com/superdesigndev/superdesign)*
*基于：vue-code-gen-api 现有代码库 + AGENT_UPGRADE_PLAN.md*
