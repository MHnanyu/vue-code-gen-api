"""
Agent 工具定义与注册表。
参考 SuperDesign 的 tools/ 目录，每个工具用 JSON Schema 定义参数。
将现有 Pipeline 步骤封装为 Agent 可调用的工具。
"""
import csv
import json
import logging
import os
import re
from typing import Any, Callable

logger = logging.getLogger(__name__)


class ToolDefinition:

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,
        execute: Callable,
        required: bool = False,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.execute = execute
        self.required = required

    def to_openai_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition):
        self._tools[tool.name] = tool

    def get_openai_tools(self) -> list[dict]:
        return [t.to_openai_tool() for t in self._tools.values()]

    def get_tool_descriptions(self) -> str:
        lines = []
        for t in self._tools.values():
            req = "【必须】" if t.required else ""
            lines.append(f"- {t.name}: {t.description} {req}")
        return "\n".join(lines)

    def get_required_tool_names(self) -> list[str]:
        return [t.name for t in self._tools.values() if t.required]

    async def execute(self, name: str, arguments: dict) -> Any:
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"未知工具: {name}"}

        logger.info(
            "执行工具: %s, 参数: %s",
            name,
            json.dumps(arguments, ensure_ascii=False)[:200],
        )
        try:
            result = await tool.execute(arguments)
            logger.info("工具完成: %s", name)
            return result
        except Exception as e:
            logger.error("工具异常: %s - %s", name, e)
            return {"error": str(e)}


def _build_file_summary(f: dict) -> dict:
    content = f.get("content", "")
    return {
        "name": f.get("name", "unknown"),
        "path": f.get("path", ""),
        "lines": content.count("\n") + 1 if content else 0,
        "size_bytes": len(content.encode("utf-8")) if content else 0,
    }


def _load_saved_vue_files(output_session_id: str, message_id: str) -> list[dict] | None:
    base_dir = os.path.join("output", output_session_id, message_id)
    if not os.path.isdir(base_dir):
        return None

    candidates = []
    try:
        for entry in os.listdir(base_dir):
            entry_path = os.path.join(base_dir, entry)
            if os.path.isdir(entry_path) and entry.endswith("_vue"):
                candidates.append(entry_path)
    except OSError:
        return None

    if not candidates:
        return None

    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    latest_dir = candidates[0]

    files = []
    for filename in os.listdir(latest_dir):
        if not filename.endswith(".vue"):
            continue
        filepath = os.path.join(latest_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            files.append({
                "name": filename,
                "path": f"/src/{filename}",
                "type": "file",
                "language": "vue",
                "content": content,
            })
        except Exception as e:
            logger.warning("读取 Vue 文件失败 %s: %s", filepath, e)

    return files if files else None


def create_tool_registry(
    component_lib: str,
    output_session_id: str,
    message_id: str,
    request=None,
) -> ToolRegistry:
    from app.services.glm4v_service import GLM4VService
    from app.services.requirement_service import RequirementService
    from app.services.ai_factory import AIServiceFactory
    from app.utils.output import save_stage_output, save_vue_files_from_json

    registry = ToolRegistry()

    # ── 工具 1: 分析图片 ──
    async def analyze_image(args: dict) -> dict:
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
    async def normalize_requirement(args: dict) -> dict:
        service = RequirementService()
        result = await service.standardize_requirement(
            user_requirement=args["requirement"],
            temperature=0.2,
        )
        if result["status"] == "failed":
            return {"error": result.get("error"), "requirement": None}
        save_stage_output(
            "requirement", 1, result["output"],
            output_session_id, message_id, "md",
        )
        return {"requirement": result["output"], "duration": result["duration"]}

    registry.register(ToolDefinition(
        name="normalize_requirement",
        description="【必须步骤】将用户的自然语言需求标准化为结构化的 UX 规格文档。无论需求是详细文档还是一句话描述，都必须经过标准化处理：去噪（去除权限/API等技术细节）、结构化（统一为页面概览+页面结构+交互说明格式）、补全（合理推导缺失的组件和字段）。",
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
        required=True,
    ))

    # ── 工具 3: 生成 Vue 代码 ──
    async def generate_vue_code(args: dict) -> dict:
        prompt = args["requirement"]
        existing_files = args.get("existing_files")

        service = AIServiceFactory.get_service()
        result = await service.generate_vue_files(
            prompt=prompt,
            existing_files=existing_files,
        )

        files = result.get("files", [])
        message = result.get("message", "代码生成完成")

        save_stage_output(
            "generation", 2, result,
            output_session_id, message_id, "json",
        )
        save_vue_files_from_json(
            files, output_session_id, 2, "generation", message_id,
        )

        file_summaries = [_build_file_summary(f) for f in files]

        return {
            "status": "success",
            "file_count": len(files),
            "files": file_summaries,
            "message": message,
        }

    registry.register(ToolDefinition(
        name="generate_vue_code",
        description="【必须步骤】根据 UX 规格文档生成 Vue 3 组件代码（SFC 格式）。生成后会自动保存。当需求足够清晰时应调用此工具。",
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
        required=True,
    ))

    # ── 工具 4: 查询 UX 规范 ──
    async def query_ux_spec(args: dict) -> dict:
        return await _query_ux_spec_files(
            component_lib,
            args["spec_type"],
            args.get("topic", ""),
            args.get("max_rules", 20),
        )

    registry.register(ToolDefinition(
        name="query_ux_spec",
        description="查询企业 UX 设计规范（Design Tokens），包括颜色、字体、间距、阴影、圆角、组件规则、布局规则等。数据来自 Skill 的 CSV 规范文件。生成代码前调用此工具，确保代码符合企业 UX 标准。",
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
                    "description": "可选。返回规则的最大条数（默认 20），防止 token 消耗过大。",
                },
            },
            "required": ["spec_type"],
        },
        execute=query_ux_spec,
    ))

    # ── 工具 5: 查询组件库文档 ──
    async def search_component_doc(args: dict) -> dict:
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

_CCUI_DOCS_DIR = os.path.join(_SKILL_DATA_DIR, "vue3-ccui-generator/references")


async def _query_component_library(component_lib: str, query: str) -> dict:
    if component_lib.lower() == "ccui":
        return await _query_ccui_doc(query)
    return await _query_element_doc(component_lib, query)


async def _query_ccui_doc(query: str) -> dict:
    if not os.path.isdir(_CCUI_DOCS_DIR):
        return {
            "component_lib": "CcUI",
            "query": query,
            "found": False,
            "message": f"组件文档目录不存在: {_CCUI_DOCS_DIR}",
        }

    query_lower = query.lower().strip()
    matched_files = []
    for filename in os.listdir(_CCUI_DOCS_DIR):
        if not filename.endswith(".md"):
            continue
        doc_name = filename[:-3]
        if query_lower in doc_name.lower() or doc_name.lower() in query_lower:
            matched_files.append((doc_name, os.path.join(_CCUI_DOCS_DIR, filename)))

    if not matched_files:
        all_components = sorted(f[:-3] for f in os.listdir(_CCUI_DOCS_DIR) if f.endswith(".md"))
        return {
            "component_lib": "CcUI",
            "query": query,
            "found": False,
            "message": f"未找到组件 '{query}' 的文档。可用的组件包括: {', '.join(all_components[:30])}",
        }

    exact_match = next((d for d, _ in matched_files if d.lower() == query_lower), None)
    if exact_match:
        doc_name = exact_match
        doc_path = os.path.join(_CCUI_DOCS_DIR, f"{exact_match}.md")
    else:
        doc_name, doc_path = matched_files[0]

    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
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
    sections = [f"## 组件: {component_name}"]

    first_section = re.split(r"\n## ", content, maxsplit=2)
    if len(first_section) >= 2:
        overview = first_section[1].strip()
        if len(overview) > 800:
            overview = overview[:800] + "\n...(概述已截断)"
        sections.append(overview)

    props_match = re.search(
        r"(#+\s*(?:Props|属性|Attributes).*?\n)(\|.+\|(\n\|[-:\s|]+\|)?\n(\|.+?\|\n){0,15})",
        content,
        re.IGNORECASE | re.DOTALL,
    )
    if props_match:
        sections.append("\n### 核心属性\n" + props_match.group(2).strip()[:600])

    summary_text = "\n\n".join(sections)
    if len(summary_text) > max_chars:
        summary_text = summary_text[:max_chars] + "\n\n...(文档摘要已截断)"
    return summary_text


async def _query_element_doc(component_lib: str, query: str) -> dict:
    return {
        "component_lib": component_lib,
        "query": query,
        "found": False,
        "message": f"{component_lib} 文档查询暂未接入，建议参考官方文档。",
    }
