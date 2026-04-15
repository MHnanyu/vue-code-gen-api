"""
Agent 核心循环：LLM 自主决策 + Tool Calling + 结果回传。
参考 SuperDesign 的 customAgentService.ts:query() 方法。
SuperDesign 使用 Vercel AI SDK 的 streamText({ maxSteps: 10 })，
我们用 httpx 手动实现等价的 while + tool_call 循环。
"""
import json
import logging
from typing import Any, AsyncGenerator

import httpx

from app.agent.tools import ToolRegistry
from app.config import settings
from app.utils.sse import (
    emit_agent_thinking,
    emit_tool_call_start,
    emit_tool_call_result,
    emit_agent_done,
    emit_error,
)
from app.utils.cancellation import is_cancelled

logger = logging.getLogger(__name__)

MAX_STEPS = 10
TOOL_RESULT_MAX_CHARS = 4000


class AgentCore:

    def __init__(
        self,
        tool_registry: ToolRegistry,
        component_lib: str = "ElementUI",
    ):
        self.tool_registry = tool_registry
        self.component_lib = component_lib
        self._required_tools = tool_registry.get_required_tool_names()
        self._called_required: set[str] = set()

    def _get_base_url(self) -> str:
        url = settings.GLM5_API_URL
        if url.endswith("/chat/completions"):
            return url[: -len("/chat/completions")]
        return url

    def _get_model(self) -> str:
        return settings.GLM5_AGENT_MODEL or settings.GLM5_MODEL

    async def run(
        self,
        user_prompt: str,
        attachments: list[dict] | None = None,
        session_context: dict | None = None,
        task_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        messages = self._build_messages(user_prompt, session_context)
        tools = self.tool_registry.get_openai_tools()

        if not tools:
            yield emit_error(
                code=500,
                message="Agent 没有可用工具",
                failed_step=0,
                stages={},
            )
            return

        for step in range(MAX_STEPS):
            if task_id and is_cancelled(task_id):
                from app.utils.sse import emit_agent_cancelled
                yield emit_agent_cancelled(step)
                return

            response = await self._call_llm(messages, tools)

            if response is None:
                yield emit_error(
                    code=500,
                    message=f"LLM 调用失败（步骤 {step}）",
                    failed_step=step,
                    stages={},
                )
                return

            content_text = response.get("content", "")
            tool_calls = response.get("tool_calls", [])
            finish_reason = response.get("finish_reason", "")

            if content_text:
                yield emit_agent_thinking(content_text, step)

            if not tool_calls:
                logger.info(
                    "Agent 完成（步骤 %d, finish_reason=%s）", step, finish_reason,
                )
                yield emit_agent_done(files=self._extract_files(messages))
                return

            for tc in tool_calls:
                func = tc.get("function", {})
                yield emit_tool_call_start(
                    tool_name=func.get("name", ""),
                    arguments=func.get("arguments", "{}"),
                    step=step,
                )

            messages.append({
                "role": "assistant",
                "content": content_text or None,
                "tool_calls": tool_calls,
            })

            for tc in tool_calls:
                tc_id = tc.get("id", "")
                func = tc.get("function", {})
                tool_name = func.get("name", "")

                try:
                    arguments = json.loads(func.get("arguments", "{}"))
                except json.JSONDecodeError:
                    arguments = {}

                if tool_name in self._required_tools:
                    self._called_required.add(tool_name)

                try:
                    result = await self.tool_registry.execute(tool_name, arguments)
                except Exception as e:
                    result = {"error": str(e)}
                    logger.error("工具执行失败: %s - %s", tool_name, e)

                yield emit_tool_call_result(
                    tool_name=tool_name,
                    result=result,
                    step=step,
                )

                result_json = json.dumps(result, ensure_ascii=False)
                if len(result_json) > TOOL_RESULT_MAX_CHARS:
                    result_json = (
                        result_json[:TOOL_RESULT_MAX_CHARS]
                        + f"\n\n[结果已截断，原始长度 {len(result_json)} 字符]"
                    )

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": result_json,
                })

            if self._required_tools and self._called_required >= set(self._required_tools):
                if finish_reason == "tool_calls":
                    pass
                else:
                    logger.info(
                        "Agent 所有必须工具已调用完毕（步骤 %d），等待 LLM 最终回复",
                        step,
                    )

        logger.warning("Agent 达到最大步数限制 (%d)", MAX_STEPS)
        missing = set(self._required_tools) - self._called_required
        if missing:
            logger.warning("Agent 未调用必须工具: %s", missing)

        yield emit_agent_done(files=self._extract_files(messages))

    def _build_messages(self, user_prompt: str, context: dict | None) -> list[dict]:
        system_prompt = self._build_system_prompt()
        messages: list[dict] = [{"role": "system", "content": system_prompt}]

        if context and context.get("history"):
            messages.extend(context["history"])

        if context and context.get("requirement_doc"):
            messages.append({
                "role": "user",
                "content": f"以下是之前已标准化的需求文档，请基于此文档继续生成代码：\n\n{context['requirement_doc']}",
            })
        elif user_prompt:
            messages.append({"role": "user", "content": user_prompt})

        return messages

    def _build_system_prompt(self) -> str:
        from app.agent.prompts import build_agent_system_prompt
        return build_agent_system_prompt(
            component_lib=self.component_lib,
            available_tools=self.tool_registry.get_tool_descriptions(),
            required_tools=self._required_tools,
        )

    async def _call_llm(
        self, messages: list[dict], tools: list[dict]
    ) -> dict | None:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.GLM5_API_KEY}",
        }

        payload = {
            "model": self._get_model(),
            "messages": messages,
            "tools": tools if tools else None,
            "temperature": 0.3,
            "stream": False,
        }

        base_url = self._get_base_url()
        api_url = f"{base_url}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(api_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

            if "choices" not in data or len(data["choices"]) == 0:
                logger.error("LLM 返回空 choices: %s", data)
                return None

            message = data["choices"][0].get("message", {})
            return {
                "content": message.get("content", ""),
                "tool_calls": message.get("tool_calls") or [],
                "finish_reason": data["choices"][0].get("finish_reason", ""),
            }
        except httpx.HTTPStatusError as e:
            logger.error("LLM HTTP 错误: %s - %s", e.response.status_code, e.response.text)
            return None
        except Exception as e:
            logger.error("LLM 调用异常: %s", e)
            return None

    def _extract_files(self, messages: list[dict]) -> list[dict]:
        files = []
        for msg in messages:
            if msg.get("role") != "tool":
                continue
            try:
                content = msg.get("content", "")
                result = json.loads(content)
                if isinstance(result, dict) and "files" in result:
                    for f in result["files"]:
                        if isinstance(f, dict) and f.get("name"):
                            files.append(f)
            except (json.JSONDecodeError, TypeError):
                continue
        return files
