import json
import logging
import re
from typing import AsyncIterator, Optional, Dict, Any
import httpx

from app.config import settings
from app.services.ai_service import AIService
from app.utils.json_helper import parse_json_with_repair

logger = logging.getLogger(__name__)


async def summarize_with_minimax(content: str, max_length: int = 200) -> str:
    try:
        service = MiniMaxService()
        prompt = f"""请将以下内容简洁概括为一段话，不超过{max_length}字。
要求：
1. 保留关键信息（处理了什么、生成了什么、优化了什么）
2. 省略具体的技术细节（如CSS类名、行号等）
3. 用简洁的中文表述

原始内容：
{content}"""
        result = await service.generate_text(prompt=prompt, temperature=0.3)
        summarized = result.strip()
        if len(summarized) > max_length * 1.5:
            summarized = summarized[:max_length] + "..."
        return summarized
    except Exception as e:
        logger.warning(f"MiniMax摘要失败，使用原始内容: {str(e)}")
        return content


class MiniMaxService(AIService):
    def __init__(self):
        self.api_key = settings.MINIMAX_API_KEY
        self.api_url = settings.MINIMAX_API_URL
        self.model = settings.MINIMAX_MODEL

    @staticmethod
    def _ccui_tail_guard(is_ccui: bool) -> str:
        if not is_ccui:
            return ""
        return """【最后提醒 - 违反即失败】
当前组件库是 CcUI，不是 Element Plus！
- 绝对禁止使用 <el-xxx> 标签，必须全部用 <cc-xxx>
- 绝对禁止 import Element Plus 组件
- 绝对禁止在 message 中说 "Element Plus"
- 必须用 cc-table、cc-button、cc-tag、cc-card、cc-icon 等"""
    
    async def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 1.0,
        stream: bool = False,
        response_format: Optional[Dict[str, str]] = None
    ) -> AsyncIterator[str]:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        system_message = None
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                filtered_messages.append(msg)
        
        payload = {
            "model": self.model,
            "messages": filtered_messages,
            "max_tokens": 4096,
        }
        
        if system_message:
            payload["system"] = system_message
        
        if stream:
            payload["stream"] = True
        
        async with httpx.AsyncClient(timeout=3000.0) as client:
            if stream:
                async with client.stream(
                    "POST",
                    f"{self.api_url}/v1/messages",
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if data.get("type") == "content_block_delta":
                                    delta = data.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        content = delta.get("text", "")
                                        if content:
                                            yield content
                            except json.JSONDecodeError:
                                continue
            else:
                response = await client.post(
                    f"{self.api_url}/v1/messages",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                if "content" in data and len(data["content"]) > 0:
                    for block in data["content"]:
                        if block.get("type") == "text":
                            yield block.get("text", "")
    
    def _build_system_prompt(self, component_lib: str, is_modify: bool = False) -> str:
        lib_name = component_lib or "Element Plus"
        is_ccui = lib_name.lower() == "ccui"

        if is_ccui:
            tech_stack = "Vue 3 Composition API (<script setup lang=\"ts\">) + CcUI 组件库 + Tailwind CSS"
            template_hint = "用 CcUI 组件实现布局和样式，包含完整的UI元素"
            icon_hint = "- CcUI 图标组件为 <cc-icon>，使用方式：<cc-icon :icon=\"Search\" />，图标需从 '@element-plus/icons-vue' 导入（如 import { Search } from '@element-plus/icons-vue'）"
        else:
            tech_stack = "Vue 3 Composition API (<script setup lang=\"ts\">) + Element Plus + Tailwind CSS"
            template_hint = "用 Element Plus 组件 + Tailwind CSS 实现布局和样式，包含完整的UI元素"
            icon_hint = "- 使用了 Element Plus 图标组件（如 Plus、Edit、Delete、Search 等）时，必须在 script 中显式导入：import { Plus } from '@element-plus/icons-vue'"

        ccui_hint = ""
        if is_ccui:
            ccui_hint = """
【CcUI 组件库规则 - 必须严格遵守】
- CcUI 组件标签统一使用 cc- 前缀（kebab-case），例如：cc-table、cc-statistic、cc-tag、cc-button、cc-input、cc-form、cc-select、cc-dialog、cc-card、cc-icon、cc-pagination、cc-tabs 等
- 禁止使用 el-* 组件（如 el-table、el-form、el-button、el-input 等），所有 Element Plus 组件必须替换为对应的 CcUI 组件
- 禁止使用 <el-icon>，必须使用 <cc-icon :icon=\"IconName\" />
- CcUI 模板组件是全局注册的，不需要在 script 中 import，直接在 template 中使用即可
- 常用组件映射：el-table → cc-table, el-table-column → cc-table-column, el-statistic → cc-statistic, el-tag → cc-tag, el-button → cc-button, el-input → cc-input, el-form → cc-form, el-form-item → cc-form-item, el-select → cc-select, el-option → cc-option, el-dialog → cc-dialog, el-pagination → cc-pagination, el-card → cc-card, el-tabs → cc-tabs, el-tab-pane → cc-tab-pane, el-date-picker → cc-date-picker, el-switch → cc-switch, el-checkbox → cc-checkbox, el-radio → cc-radio, el-tooltip → cc-tooltip, el-popover → cc-popover, el-dropdown → cc-dropdown, el-drawer → cc-drawer, el-upload → cc-upload, el-tree → cc-tree, el-menu → cc-menu, el-row → cc-row, el-col → cc-col, el-descriptions → cc-descriptions, el-descriptions-item → cc-descriptions-item, el-badge → cc-badge, el-avatar → cc-avatar, el-divider → cc-divider, el-steps → cc-steps, el-step → cc-step, el-result → cc-result, el-image → cc-image, el-link → cc-link, el-space → cc-space, el-collapse → cc-collapse, el-collapse-item → cc-collapse-item, el-timeline → cc-timeline, el-timeline-item → cc-timeline-item, el-breadcrumb → cc-breadcrumb, el-breadcrumb-item → cc-breadcrumb-item"""

        if is_modify:
            return f"""你是Vue3前端原型图优化助手，目标是修改可预览的UI原型。

【输出格式 - 必须严格遵守】
直接输出纯JSON，不要有任何前缀说明、后缀解释或markdown标记。
不要输出 "我来帮你..." 等任何额外文字，直接以 {{ 开始，以 }} 结束。

返回格式示例：
{{"files":[{{"id":"xxx","name":"xxx","path":"xxx","type":"file","language":"vue","content":"代码内容"}}],"message":"简短说明"}}

【重要规则】
1. 输入N个文件，必须输出N个文件，保持一对一映射
2. 每个输出文件的id、name、path必须与输入完全一致
3. 即使文件不需要修改，也必须包含（保持原样）
4. 保持原型极简原则：mock数据即可，不需要真实逻辑
5. 每个文件代码不超过 300 行

【技术栈】
{tech_stack}
{ccui_hint}
【特别注意】
- content 字段中的代码必须正确转义：双引号用 \\"，换行用 \\n
{icon_hint}
{self._ccui_tail_guard(is_ccui)}"""
        else:
            return f"""你是Vue3前端原型图生成助手，目标是生成可预览的UI原型，而非生产代码。

【输出格式 - 必须严格遵守】
直接输出纯JSON，不要有任何前缀说明、后缀解释或markdown标记。
不要输出 "我来帮你..." 等任何额外文字，直接以 {{ 开始，以 }} 结束。

返回格式示例：
{{"files":[{{"id":"main-page","name":"MainPage.vue","path":"/src/MainPage.vue","type":"file","language":"vue","content":"代码内容"}}],"message":"简短说明"}}

【生成规则 - 极简原型原则】
1. 尽量只生成 MainPage.vue 一个文件，除非页面确实复杂需要拆分（最多3个文件）
2. template 部分：{template_hint}
3. script 部分：极简化，使用硬编码的 mock 数据，不需要 API 调用、表单验证、computed、watch 等逻辑
4. 不要定义 interface/type，不需要复杂的 TypeScript 类型
5. 不要生成 main.ts, App.vue, index.html 等配置文件
6. 每个文件代码不超过 300 行

【技术栈】
{tech_stack}
{ccui_hint}
【特别注意】
- content 字段中的代码必须正确转义：双引号用 \\"，换行用 \\n
- 这是原型图，重点在于组件位置正确、布局合理、基础样式到位，不需要真实交互逻辑
{self._ccui_tail_guard(is_ccui)}"""

    async def generate_vue_files(
        self,
        prompt: str,
        existing_files: Optional[list[dict]] = None,
        component_lib: str = "Element Plus"
    ) -> dict:
        data = await self._do_generate_vue_files(prompt, existing_files, component_lib)

        is_ccui = (component_lib or "").lower() == "ccui"
        if is_ccui and data.get("files"):
            data = await self._validate_and_retry_ccui(data, prompt, existing_files, component_lib)

        return data

    async def _do_generate_vue_files(
        self,
        prompt: str,
        existing_files: Optional[list[dict]] = None,
        component_lib: str = "Element Plus",
        retry_hint: str = "",
    ) -> dict:
        if existing_files:
            system_message = self._build_system_prompt(component_lib, is_modify=True)
            
            files_context = "\n\n".join([
                f"--- 文件: {f.get('name', 'unknown')} (id: {f.get('id', 'unknown')}) ---\n{f.get('content', '')}"
                for f in existing_files
            ])
            user_message = f"现有代码文件：\n{files_context}\n\n修改需求：{prompt}"
        else:
            system_message = self._build_system_prompt(component_lib, is_modify=False)
            user_message = prompt

        if retry_hint:
            user_message = f"{retry_hint}\n\n{user_message}"
        
        messages = [
            {"role": "user", "content": user_message}
        ]
        
        result = ""
        async for chunk in self.chat_completion(
            messages,
            temperature=0.7,
            stream=False
        ):
            result += chunk
        
        json_match = re.search(r'\{[\s\S]*\}', result)
        json_str = json_match.group(0) if json_match else result
        
        data, error = parse_json_with_repair(json_str)
        
        if error or data is None:
            logger.error(f"JSON解析失败 - error: {error}, 原始输出: {result[:500]}")
            return {
                "files": [],
                "message": f"JSON解析失败。原始输出：{result}"
            }
        
        if "files" not in data:
            logger.error(f"AI返回格式错误 - 缺少files字段。原始输出: {result[:500]}")
            return {
                "files": [],
                "message": f"返回格式错误。原始输出：{result}"
            }
        
        return data

    async def _validate_and_retry_ccui(
        self,
        data: dict,
        prompt: str,
        existing_files: Optional[list[dict]],
        component_lib: str,
    ) -> dict:
        el_pattern = re.compile(r"<el-")
        for f in data.get("files", []):
            content = f.get("content", "")
            if el_pattern.search(content):
                found = el_pattern.findall(content)
                logger.warning(
                    "CcUI 校验失败：检测到 %d 个 el- 组件标签（%s），将重试生成",
                    len(found), content[:200],
                )
                hint = (
                    "【严重错误】你上一次生成的代码中使用了 Element Plus 的 el-* 组件，"
                    "但要求使用 CcUI 组件库。所有 el-* 必须替换为 cc-* 前缀："
                    "el-table→cc-table, el-button→cc-button, el-tag→cc-tag, "
                    "el-icon→cc-icon, el-input→cc-input, el-form→cc-form, "
                    "el-select→cc-select, el-dialog→cc-dialog, el-card→cc-card 等。"
                    "请严格按照要求重新生成。"
                )
                data = await self._do_generate_vue_files(prompt, existing_files, component_lib, retry_hint=hint)
                break
        return data
