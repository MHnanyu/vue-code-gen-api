"""
Agent 核心循环：LLM 自主决策 + Tool Calling + 结果回传。
参考 SuperDesign 的 customAgentService.ts:query() 方法。
SuperDesign 使用 Vercel AI SDK 的 streamText({ maxSteps: 10 })，
我们用 httpx 手动实现等价的 while + tool_call 循环。
"""
import asyncio
import json
import logging
import os
from typing import AsyncGenerator

import httpx

from app.agent.tools import ToolRegistry, _load_saved_vue_files, _build_file_summary
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

DEFAULT_MAX_STEPS = 10
TOOL_RESULT_MAX_CHARS = 4000
TOOL_CONCURRENCY_LIMIT = 3


class AgentCore:

    def __init__(
        self,
        tool_registry: ToolRegistry,
        component_lib: str = "ElementUI",
        max_steps: int | None = None,
    ):
        self.tool_registry = tool_registry
        self.component_lib = component_lib
        self.max_steps = max_steps or settings.AGENT_MAX_STEPS
        self._required_tools = tool_registry.get_required_tool_names()
        self._called_required: set[str] = set()
        self._tool_results: dict[str, str] = {}
        self._pruned_checkpoints: set[str] = set()

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
        output_session_id: str | None = None,
        message_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        self._output_session_id = output_session_id
        self._message_id = message_id
        self._called_required = set()
        self._tool_results = {}
        self._pruned_checkpoints = set()
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

        async with httpx.AsyncClient(timeout=120.0) as llm_client:
            try:
                async for event in asyncio.wait_for(
                    self._run_loop(
                        messages, tools, llm_client,
                        user_prompt, session_context, task_id,
                        output_session_id, message_id,
                    ),
                    timeout=settings.AGENT_TIMEOUT,
                ):
                    yield event
            except asyncio.TimeoutError:
                logger.error("Agent 执行超时 (%d 秒)", settings.AGENT_TIMEOUT)
                yield emit_error(
                    code=500,
                    message=f"Agent 执行超时 ({settings.AGENT_TIMEOUT} 秒)",
                    failed_step=self.max_steps,
                    stages={},
                )

    async def _run_loop(
        self,
        messages: list[dict],
        tools: list[dict],
        llm_client: httpx.AsyncClient,
        user_prompt: str,
        session_context: dict | None,
        task_id: str | None,
        output_session_id: str | None,
        message_id: str | None,
    ) -> AsyncGenerator[str, None]:
        for step in range(self.max_steps):
            if task_id and is_cancelled(task_id):
                from app.utils.sse import emit_agent_cancelled
                yield emit_agent_cancelled(step)
                return

            response = await self._call_llm(messages, tools, client=llm_client)

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
                yield emit_agent_thinking(content_text, step, task_id=task_id)

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

            tool_events, tool_exec_results = await self._execute_tools_parallel(tool_calls, step)
            for ev in tool_events:
                yield ev
            for tc, result, result_json in tool_exec_results:
                tc_id = tc.get("id", "")
                tool_name = tc.get("function", {}).get("name", "")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": result_json,
                })

                self._tool_results[tool_name] = result_json

            messages = self._maybe_prune(messages, step)

        missing = set(self._required_tools) - self._called_required
        if missing:
            missing_names = ", ".join(sorted(missing))
            logger.warning("Agent 达到最大步数 (%d)，未调用必须工具: %s", self.max_steps, missing_names)
            files = self._extract_files(messages)
            if files:
                yield emit_agent_done(files=files)
            else:
                yield emit_error(
                    code=500,
                    message=f"Agent 达到最大步数限制 ({self.max_steps})，且未完成必须步骤: {missing_names}",
                    failed_step=self.max_steps,
                    stages={},
                )
        else:
            logger.warning("Agent 达到最大步数限制 (%d)，已调用所有必须工具", self.max_steps)
            yield emit_agent_done(files=self._extract_files(messages))

    async def _execute_tools_parallel(
        self,
        tool_calls: list[dict],
        step: int,
    ) -> tuple[list[str], list[tuple[dict, dict, str]]]:
        semaphore = asyncio.Semaphore(TOOL_CONCURRENCY_LIMIT)

        async def _run_single(tc: dict) -> tuple[dict, dict, str, str | None]:
            async with semaphore:
                tc_id = tc.get("id", "")
                func = tc.get("function", {})
                tool_name = func.get("name", "")

            try:
                arguments = json.loads(func.get("arguments", "{}"))
            except json.JSONDecodeError:
                arguments = {}

            try:
                result = await self.tool_registry.execute(tool_name, arguments)
            except Exception as e:
                result = {"error": str(e)}
                logger.error("工具执行失败: %s - %s", tool_name, e)

            if (
                tool_name in self._required_tools
                and not (isinstance(result, dict) and "error" in result)
            ):
                self._called_required.add(tool_name)

            result_json = json.dumps(result, ensure_ascii=False)
            if len(result_json) > TOOL_RESULT_MAX_CHARS:
                result_json = (
                    result_json[:TOOL_RESULT_MAX_CHARS]
                    + f"\n\n[结果已截断，原始长度 {len(result_json)} 字符]"
                )

            output_info = self._build_output_info(tool_name)

            return tc, result, result_json, output_info
        results = await asyncio.gather(*[_run_single(tc) for tc in tool_calls])
        events: list[str] = []

        for tc, result, _, output_info in results:
            tool_name = tc.get("function", {}).get("name", "")
            events.append(emit_tool_call_result(
                tool_name=tool_name,
                result=result,
                step=step,
                output_info=output_info,
            ))

        return events, [(tc, res, rj) for tc, res, rj, _ in results]

    _TOOL_OUTPUT_MAP = {
        "normalize_requirement": ("step1_requirement.md", "file", "file"),
        "generate_vue_code": ("step2_generation_vue", "directory", "files"),
        "optimize_ux": ("step3_optimization_vue", "directory", "files"),
    }

    def _build_output_info(self, tool_name: str) -> tuple[list[str], str] | None:
        pattern = self._TOOL_OUTPUT_MAP.get(tool_name)
        if not pattern:
            return None
        if not self._output_session_id or not self._message_id:
            return None
        relative, kind, output_type = pattern
        base = f"output/{self._output_session_id}/{self._message_id}"
        if kind == "file":
            return [f"{base}/{relative}"], output_type
        dir_path = os.path.join(base, relative).replace("\\", "/")
        if not os.path.isdir(dir_path):
            return None
        urls = [f"{dir_path}/{fname}" for fname in sorted(os.listdir(dir_path))]
        return (urls, output_type) if urls else None

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

    def _estimate_messages_chars(self, messages: list[dict]) -> int:
        return sum(len(json.dumps(m, ensure_ascii=False)) for m in messages)

    def _maybe_prune(self, messages: list[dict], step: int) -> list[dict]:
        both_ready = (
            "normalize_requirement" in self._called_required
            and "generate_vue_code" in self._called_required
        )

        if both_ready and "after_generate" not in self._pruned_checkpoints:
            messages = self._prune_after_generate(messages)
            self._pruned_checkpoints.add("after_normalize")
            self._pruned_checkpoints.add("after_generate")
            return messages

        if "normalize_requirement" in self._called_required and "after_normalize" not in self._pruned_checkpoints:
            messages = self._prune_after_normalize(messages)
            self._pruned_checkpoints.add("after_normalize")

        return messages

    def _prune_after_normalize(self, messages: list[dict]) -> list[dict]:
        req = self._tool_results.get("normalize_requirement", "")
        if not req:
            return messages
        before = self._estimate_messages_chars(messages)
        pruned = [
            messages[0],
            {"role": "user", "content": f"需求标准化已完成。以下是结构化 UX 文档：\n\n{req}"},
        ]
        after = self._estimate_messages_chars(pruned)
        logger.info("上下文裁剪 [检查点 1]: %d → %d 字符 (移除原始输入和图片分析，保留标准化需求)", before, after)
        return pruned

    def _prune_after_generate(self, messages: list[dict]) -> list[dict]:
        code = self._tool_results.get("generate_vue_code", "")
        if not code:
            return messages
        before = self._estimate_messages_chars(messages)
        pruned = [
            messages[0],
            {"role": "user", "content": f"代码生成已完成。以下是文件信息：\n\n{code}"},
        ]
        after = self._estimate_messages_chars(pruned)
        logger.info("上下文裁剪 [检查点 2]: %d → %d 字符 (移除需求文档和规范查询，保留代码文件引用)", before, after)
        return pruned

    async def _call_llm(
        self, messages: list[dict], tools: list[dict], client: httpx.AsyncClient
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

        max_retries = 3
        for attempt in range(max_retries):
            try:
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
                logger.error("LLM HTTP 错误 (第 %d/%d 次): %s - %s", attempt + 1, max_retries, e.response.status_code, e.response.text)
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    return None
            except Exception as e:
                logger.error("LLM 调用异常 (第 %d/%d 次): %s", attempt + 1, max_retries, e)
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                else:
                    return None
        return None

    def _extract_files(self, messages: list[dict]) -> list[dict]:
        if self._output_session_id and self._message_id:
            disk_files = _load_saved_vue_files(self._output_session_id, self._message_id)
            if disk_files:
                return disk_files

        seen: dict[str, dict] = {}
        for msg in messages:
            if msg.get("role") != "tool":
                continue
            try:
                content = msg.get("content", "")
                result = json.loads(content)
                if isinstance(result, dict) and "files" in result:
                    for f in result["files"]:
                        if isinstance(f, dict) and f.get("name"):
                            if f.get("content"):
                                seen[f["name"]] = _build_file_summary(f)
                            elif f.get("lines") is not None:
                                seen[f["name"]] = f
            except (json.JSONDecodeError, TypeError):
                continue

        return list(seen.values())
