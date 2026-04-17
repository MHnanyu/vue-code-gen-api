import asyncio
import json
import logging
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field

from fastapi import Request

from app.schemas.generate import GeneratedFile, StageResult
from app.schemas.response import ErrorCode
from app.utils.sse import (
    emit_stage_start, emit_stage_progress, emit_stage_complete,
    emit_error, emit_cancelled, emit_done,
)
from app.utils.output import (
    load_stage_output, save_stage_output, save_vue_files_from_json,
    build_file_path, build_step_summary, update_session_with_ai_message,
)
from app.utils.cancellation import (
    run_with_cancel_check, ClientDisconnectedError, GenerationCancelledError,
    register_cancel, unregister_cancel,
)
from app.services.ai_factory import AIServiceFactory
from app.services.requirement_service import RequirementService
from app.services.openclaw_service import OpenclawService
from app.services.glm4v_service import GLM4VService
from app.services.attachment_service import process_attachments, build_attachment_summary
from app.prompts import get_generation_prompt, get_optimization_prompt

logger = logging.getLogger(__name__)

STAGE_NAME_MAP = {0: "attachment", 1: "requirement", 2: "generation", 3: "optimization"}


def convert_api_files_to_generated(api_files: list[dict]) -> list[GeneratedFile]:
    return [
        GeneratedFile(
            id=file.get("id", f"file-{i}"),
            name=file.get("name", f"file{i}.vue"),
            path=file.get("path", f"/src/{file.get('name', f'file{i}.vue')}"),
            type=file.get("type", "file"),
            language=file.get("language", "vue"),
            content=file.get("content", ""),
            children=file.get("children"),
        )
        for i, file in enumerate(api_files)
    ]


@dataclass
class PipelineContext:
    db: object | None
    session_id: str | None
    message_id: str
    output_session_id: str
    request: Request
    component_lib: str
    from_step: int | None
    retry_message_id: str | None
    stages: dict[str, StageResult] = field(default_factory=dict)
    step_messages: list[dict] = field(default_factory=list)
    files: list[GeneratedFile] = field(default_factory=list)
    ai_message: str = "生成完成"
    failed_step: int | None = None
    final_prompt: str = ""
    requirement_doc: str | None = None

    @property
    def is_ccui(self) -> bool:
        return self.component_lib.lower() == "ccui"


def _load_cached_steps_for_session(
    from_step: int,
    session_id: str,
    prev_step_messages: list[dict] | None = None,
) -> tuple[dict[str, StageResult] | None, list[dict] | None]:
    stages: dict[str, StageResult] = {}
    step_messages: list[dict] = []

    prev_duration_map: dict[str, float | None] = {}
    if prev_step_messages:
        for sm in prev_step_messages:
            stage_key = sm.get("stageName")
            duration = sm.get("duration")
            if stage_key and duration is not None:
                prev_duration_map[stage_key] = duration

    configs = [
        (0, "final_prompt", "md", "attachment", "已加载附件处理结果"),
        (1, "requirement", "md", "requirement", "已加载需求标准化结果"),
        (2, "generation", "json", "generation", "已加载代码生成结果"),
    ]

    for step_num, stage_name, ext, stage_key, message in configs:
        if from_step > step_num:
            cached = load_stage_output(step_num, stage_name, session_id, ext)
            if cached is None:
                return None, None
            cached_duration = prev_duration_map.get(stage_key)
            stages[stage_key] = StageResult(status="success", duration=cached_duration)
            sm = {
                "stage": step_num, "stageName": stage_key,
                "message": message, "status": "cached", "duration": cached_duration,
            }
            if isinstance(cached, str):
                sm["outputType"] = "markdown"
            elif isinstance(cached, dict) and "files" in cached:
                sm["outputType"] = "vue"
                sm["message"] = f"已加载代码生成结果（{len(cached.get('files', []))} 个文件）"
            step_messages.append(sm)

    return stages, step_messages


class StepExecutor:
    def __init__(self, ctx: PipelineContext, body):
        self.ctx = ctx
        self.body = body
        self._progress_queue: asyncio.Queue[str] = asyncio.Queue()

    def _record_step(
        self,
        step: int,
        stage_name: str,
        status: str,
        message: str,
        duration: float | None = None,
        output_type: str | None = None,
        file_path: str | None = None,
        error: str | None = None,
    ):
        self.ctx.stages[stage_name] = StageResult(status=status, duration=duration, error=error)
        entry = {
            "stage": step, "stageName": stage_name, "message": message,
            "status": status, "duration": duration,
        }
        if output_type:
            entry["outputType"] = output_type
        if file_path:
            entry["filePath"] = file_path
        self.ctx.step_messages.append(entry)

    async def save_cancel_to_db(self):
        ctx = self.ctx
        if ctx.failed_step is not None:
            current_stage_name = STAGE_NAME_MAP.get(ctx.failed_step)
            if current_stage_name and current_stage_name not in ctx.stages:
                ctx.stages[current_stage_name] = StageResult(status="cancelled")
        try:
            await update_session_with_ai_message(
                ctx.db, ctx.session_id, ctx.files, "用户取消了生成", ctx.failed_step, ctx.stages,
                message_id=ctx.message_id, step_messages=ctx.step_messages,
                retry_message_id=ctx.retry_message_id,
            )
        except Exception as e:
            logger.error(f"[SSE] 取消时写入 session 失败: {str(e)}")

    async def emit_stage_error(
        self, stage: int, stage_name: str, step: int, error_msg: str, duration: float | None
    ) -> AsyncGenerator[str, None]:
        self.ctx.stages[stage_name] = StageResult(status="failed", duration=duration, error=error_msg)
        yield emit_stage_complete(
            stage, stage_name, "failed",
            message=f"{stage_name}失败: {error_msg}",
            duration=duration, error=error_msg,
        )
        yield emit_error(ErrorCode.AI_GENERATE_FAILED, error_msg, step, self.ctx.stages)
        try:
            await update_session_with_ai_message(
                self.ctx.db, self.ctx.session_id, self.ctx.files,
                f"步骤{step}（{stage_name}）失败: {error_msg}",
                step, self.ctx.stages, message_id=self.ctx.message_id,
                step_messages=self.ctx.step_messages, retry_message_id=self.ctx.retry_message_id,
            )
        except Exception as save_err:
            logger.error(f"[SSE] 写入 session 失败: {str(save_err)}")

    async def execute_attachment_step(self) -> AsyncGenerator[str, None]:
        ctx = self.ctx
        from_step = ctx.from_step

        if from_step is not None and from_step > 0:
            cached_prompt = load_stage_output(0, "final_prompt", ctx.output_session_id, "md")
            if cached_prompt:
                has_image_in_request = any(
                    a.type == "image" for a in self.body.attachments
                ) if self.body.attachments else False
                has_image_in_cache = "图片分析结果" in cached_prompt

                if has_image_in_request and not has_image_in_cache:
                    ctx.from_step = 0
                    async for evt in self.execute_attachment_step():
                        yield evt
                    return

                ctx.final_prompt = cached_prompt
                cached_file_path = build_file_path(ctx.output_session_id, ctx.message_id, "step0_final_prompt.md")
                save_stage_output("final_prompt", 0, ctx.final_prompt, ctx.output_session_id, ctx.message_id, "md")
                ctx.stages["attachment"] = StageResult(status="success", duration=None)
                yield emit_stage_complete(
                    0, "attachment", "cached",
                    output_type="markdown", file_path=cached_file_path,
                )
                msg = build_attachment_summary(self.body.attachments)
                msg = f"已加载{msg[2:]}" if msg.startswith("已") else msg
                self._record_step(0, "attachment", "cached", msg, output_type="markdown", file_path=cached_file_path)
            else:
                yield emit_error(ErrorCode.PARAM_ERROR, f"找不到步骤0的缓存结果，无法从步骤 {from_step} 开始重试", 0, {})
                return
            return

        yield emit_stage_start(0, "attachment", ctx.message_id, is_retry=from_step == 0)
        stage_start = time.time()

        def on_image_progress(idx, total, attachment):
            self._progress_queue.put_nowait(emit_stage_progress(
                0, "attachment",
                f"正在分析图片 {idx + 1}/{total}: {attachment.name}",
                int((idx + 1) / total * 100),
            ))

        try:
            glm4v_service = GLM4VService()
            attach_task = asyncio.create_task(
                process_attachments(self.body, glm4v_service, on_image_progress=on_image_progress)
            )

            while not attach_task.done():
                try:
                    evt = await asyncio.wait_for(self._progress_queue.get(), timeout=0.1)
                    yield evt
                except asyncio.TimeoutError:
                    pass

            while True:
                try:
                    evt = self._progress_queue.get_nowait()
                    yield evt
                except asyncio.QueueEmpty:
                    break

            ctx.final_prompt = await attach_task

            save_stage_output("final_prompt", 0, ctx.final_prompt, ctx.output_session_id, ctx.message_id, "md")
            duration = round(time.time() - stage_start, 2)
            file_path = build_file_path(ctx.output_session_id, ctx.message_id, "step0_final_prompt.md")
            msg = build_attachment_summary(self.body.attachments)
            ctx.stages["attachment"] = StageResult(status="success", duration=duration)
            yield emit_stage_complete(0, "attachment", "success", msg, duration=duration, output_type="markdown", file_path=file_path)
            self._record_step(0, "attachment", "success", msg, duration=duration, output_type="markdown", file_path=file_path)
        except (ClientDisconnectedError, GenerationCancelledError):
            yield emit_cancelled(ctx.failed_step, ctx.stages)
            await self.save_cancel_to_db()
        except Exception as e:
            duration = round(time.time() - stage_start, 2)
            async for evt in self.emit_stage_error(0, "attachment", 0, str(e), duration):
                yield evt

    async def execute_requirement_step(self) -> AsyncGenerator[str, None]:
        ctx = self.ctx
        from_step = ctx.from_step

        if from_step is not None and from_step > 1:
            cached_requirement = load_stage_output(1, "requirement", ctx.output_session_id, "md")
            if cached_requirement:
                ctx.requirement_doc = cached_requirement
                cached_file_path = build_file_path(ctx.output_session_id, ctx.message_id, "step1_requirement.md")
                save_stage_output("requirement", 1, ctx.requirement_doc, ctx.output_session_id, ctx.message_id, "md")
                ctx.stages["requirement"] = StageResult(status="success", duration=None)
                yield emit_stage_complete(1, "requirement", "cached", output_type="markdown", file_path=cached_file_path)
                self._record_step(1, "requirement", "cached", "已加载需求标准化结果", output_type="markdown", file_path=cached_file_path)
            else:
                yield emit_error(ErrorCode.PARAM_ERROR, f"找不到步骤1的缓存结果，无法从步骤 {from_step} 开始重试", 1, ctx.stages)
            return

        yield emit_stage_start(1, "requirement", ctx.message_id, is_retry=from_step is not None)
        stage_start = time.time()

        try:
            requirement_service = RequirementService()
            stage1_result = await run_with_cancel_check(
                requirement_service.standardize_requirement(user_requirement=ctx.final_prompt, temperature=0.2),
                ctx.request, task_id=ctx.message_id,
            )
            duration = stage1_result.get("duration", round(time.time() - stage_start, 2))

            if stage1_result["status"] == "failed":
                error_msg = stage1_result.get("error", "未知错误")
                async for evt in self.emit_stage_error(1, "requirement", 1, error_msg, duration):
                    yield evt
                return

            ctx.requirement_doc = stage1_result["output"]
            save_stage_output("requirement", 1, ctx.requirement_doc, ctx.output_session_id, ctx.message_id, "md")
            file_path = build_file_path(ctx.output_session_id, ctx.message_id, "step1_requirement.md")
            ctx.stages["requirement"] = StageResult(status="success", duration=duration)
            yield emit_stage_complete(1, "requirement", "success", "需求标准化完成", duration=duration, output_type="markdown", file_path=file_path)
            self._record_step(1, "requirement", "success", "需求标准化完成", duration=duration, output_type="markdown", file_path=file_path)
        except (ClientDisconnectedError, GenerationCancelledError):
            yield emit_cancelled(ctx.failed_step, ctx.stages)
            await self.save_cancel_to_db()
        except Exception as e:
            duration = round(time.time() - stage_start, 2)
            async for evt in self.emit_stage_error(1, "requirement", 1, str(e), duration):
                yield evt

    async def execute_generation_step(self) -> AsyncGenerator[str, None]:
        ctx = self.ctx
        from_step = ctx.from_step
        assert ctx.requirement_doc is not None

        if from_step is not None and from_step > 2:
            cached_generation = load_stage_output(2, "generation", ctx.output_session_id, "json")
            if cached_generation and isinstance(cached_generation, dict):
                result = cached_generation
                api_files = result.get("files", [])
                ctx.files = convert_api_files_to_generated(api_files)
                ctx.ai_message = result.get("message", f"代码生成完成（{ctx.component_lib}）")
                ctx.stages["generation"] = StageResult(status="success", duration=None)
                file_path = build_file_path(ctx.output_session_id, ctx.message_id, "step2_generation.json")
                yield emit_stage_complete(2, "generation", "cached", message=f"已加载代码生成结果（{len(ctx.files)} 个文件）", output_type="vue", file_path=file_path)
                self._record_step(2, "generation", "cached", f"已加载代码生成结果（{len(ctx.files)} 个文件）", output_type="vue", file_path=file_path)
            else:
                yield emit_error(ErrorCode.PARAM_ERROR, f"找不到步骤2的缓存结果，无法从步骤 {from_step} 开始重试", 2, ctx.stages)
            return

        yield emit_stage_start(2, "generation", ctx.message_id, is_retry=from_step is not None)
        stage_start = time.time()

        try:
            if ctx.is_ccui:
                openclaw_service = OpenclawService()
                prompt = get_generation_prompt(ctx.component_lib, ctx.requirement_doc)
                result = await run_with_cancel_check(
                    openclaw_service.generate_vue_files(prompt=prompt, ccui_prompt=""),
                    ctx.request, task_id=ctx.message_id,
                )
            else:
                ai_service = AIServiceFactory.get_service()
                result = await run_with_cancel_check(
                    ai_service.generate_vue_files(prompt=ctx.requirement_doc, existing_files=None, component_lib=ctx.component_lib),
                    ctx.request, task_id=ctx.message_id,
                )

            duration = round(time.time() - stage_start, 2)
            api_files = result.get("files", [])
            ctx.ai_message = result.get("message", f"代码生成完成（{ctx.component_lib}）")
            ctx.files = convert_api_files_to_generated(api_files)

            if not ctx.files:
                async for evt in self.emit_stage_error(2, "generation", 2, "未能生成有效的代码文件", duration):
                    yield evt
                return

            save_stage_output("generation", 2, result, ctx.output_session_id, ctx.message_id, "json")
            if api_files:
                save_vue_files_from_json(api_files, ctx.output_session_id, 2, "generation", ctx.message_id)

            file_path = build_file_path(ctx.output_session_id, ctx.message_id, "step2_generation.json")
            gen_msg = ctx.ai_message or f"生成了 {len(ctx.files)} 个 Vue 组件文件（{ctx.component_lib}）"
            ctx.stages["generation"] = StageResult(status="success", duration=duration)
            yield emit_stage_complete(2, "generation", "success", gen_msg, duration=duration, output_type="vue", file_path=file_path)
            self._record_step(2, "generation", "success", gen_msg, duration=duration, output_type="vue", file_path=file_path)
        except (ClientDisconnectedError, GenerationCancelledError):
            yield emit_cancelled(ctx.failed_step, ctx.stages)
            await self.save_cancel_to_db()
        except Exception as e:
            duration = round(time.time() - stage_start, 2)
            async for evt in self.emit_stage_error(2, "generation", 2, str(e), duration):
                yield evt

    async def execute_optimization_step(self) -> AsyncGenerator[str, None]:
        ctx = self.ctx
        from_step = ctx.from_step

        if from_step is not None and from_step > 3:
            ctx.stages["optimization"] = StageResult(status="skipped", duration=None)
            yield emit_stage_complete(3, "optimization", "skipped", message="跳过")
            self._record_step(3, "optimization", "skipped", "跳过")
            return

        yield emit_stage_start(3, "optimization", ctx.message_id, is_retry=from_step is not None)
        stage_start = time.time()

        try:
            openclaw_service = OpenclawService()
            stage2_files_json = json.dumps([f.model_dump() for f in ctx.files], ensure_ascii=False, indent=2)
            optimization_prompt = get_optimization_prompt(ctx.component_lib)
            full_prompt = f"{optimization_prompt}\n\n待优化的文件：\n{stage2_files_json}\n"

            stage3_result = await run_with_cancel_check(
                openclaw_service.generate_vue_files(prompt=full_prompt, ccui_prompt=""),
                ctx.request, task_id=ctx.message_id,
            )
            duration = round(time.time() - stage_start, 2)

            stage3_api_files = stage3_result.get("files", [])
            stage3_message = stage3_result.get("message", "优化完成")
            optimized_files = convert_api_files_to_generated(stage3_api_files)

            if optimized_files:
                ctx.files = optimized_files
                ctx.ai_message = stage3_message

            save_stage_output("optimization", 3, stage3_result, ctx.output_session_id, ctx.message_id, "json")
            if stage3_api_files:
                save_vue_files_from_json(stage3_api_files, ctx.output_session_id, 3, "optimization", ctx.message_id)

            file_path = build_file_path(ctx.output_session_id, ctx.message_id, "step3_optimization.json")
            opt_msg = stage3_message or (
                f"UX 优化完成（{len(optimized_files)} 个文件）" if optimized_files else "UX 优化未产出新文件"
            )
            ctx.stages["optimization"] = StageResult(status="success", duration=duration)
            yield emit_stage_complete(3, "optimization", "success", opt_msg, duration=duration, output_type="vue", file_path=file_path)
            self._record_step(3, "optimization", "success", opt_msg, duration=duration, output_type="vue", file_path=file_path)
        except (ClientDisconnectedError, GenerationCancelledError):
            yield emit_cancelled(ctx.failed_step, ctx.stages)
            await self.save_cancel_to_db()
        except Exception as e:
            duration = round(time.time() - stage_start, 2)
            async for evt in self.emit_stage_error(3, "optimization", 3, str(e), duration):
                yield evt
