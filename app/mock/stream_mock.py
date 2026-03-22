import asyncio
import logging
import random
from collections.abc import AsyncGenerator

from fastapi import Request

from app.mock.generate_mock import (
    MOCK_INITIAL_FILES, MOCK_INITIAL_MESSAGE,
    MOCK_ITERATE_FILES, MOCK_ITERATE_MESSAGE,
)
from app.schemas.generate import GeneratedFile, StageResult
from app.utils.cancellation import (
    register_cancel, unregister_cancel,
    run_with_cancel_check, ClientDisconnectedError, GenerationCancelledError,
)
from app.utils.sse import (
    emit_stage_start, emit_stage_progress, emit_stage_complete,
    emit_done, emit_cancelled, make_preview,
)
from app.utils.output import (
    save_stage_output, save_vue_files_from_json,
    build_file_path, build_step_summary,
    update_session_with_ai_message,
)

logger = logging.getLogger(__name__)


async def mock_initial_stream(
    request: Request,
    body,
    db,
    message_id: str,
    output_session_id: str,
    from_step: int | None,
    retry_message_id: str | None = None,
) -> AsyncGenerator[str, None]:
    register_cancel(message_id)
    stages: dict[str, StageResult] = {}
    step_messages: list[dict] = []
    files = MOCK_INITIAL_FILES
    mock_requirement = (
        "# 需求文档\n\n## 概述\n"
        "这是一个基于 Element Plus 的仪表盘页面，包含统计卡片、图表区域和动态时间线。\n\n"
        "## 功能模块\n1. 统计卡片展示（用户总数、订单数量、销售额、转化率）\n"
        "2. 销售趋势图表\n3. 最新动态时间线"
    )
    failed_step: int | None = None

    async def mock_sleep(seconds: float) -> bool:
        try:
            await run_with_cancel_check(
                asyncio.sleep(seconds), request, task_id=message_id, poll_interval=0.2,
            )
        except (ClientDisconnectedError, GenerationCancelledError):
            return False
        return True

    stage_name_map = {0: "attachment", 1: "requirement", 2: "generation", 3: "optimization"}

    async def on_cancelled():
        if failed_step is not None:
            current_stage_name = stage_name_map.get(failed_step)
            if current_stage_name and current_stage_name not in stages:
                stages[current_stage_name] = StageResult(status="cancelled")
        try:
            await update_session_with_ai_message(
                db, body.sessionId, files, "用户取消了生成", failed_step, stages,
                message_id=message_id, step_messages=step_messages,
                retry_message_id=retry_message_id,
            )
        except Exception as e:
            logger.error(f"[SSE Mock] 取消时写入 session 失败: {str(e)}")
        yield emit_cancelled(cancelled_at_step=failed_step, stages=stages)

    try:
        start_steps = from_step if from_step is not None else 0

        if start_steps > 0:
            mock_prompt = f"用户需求：\n{body.prompt}"
            save_stage_output("final_prompt", 0, mock_prompt, output_session_id, message_id, "md")
            cached_duration = round(random.uniform(5, 7), 2)
            stages["attachment"] = StageResult(status="success", duration=cached_duration)
            cached_file_path = build_file_path(output_session_id, message_id, "step0_final_prompt.md")
            yield emit_stage_complete(
                0, "attachment", "cached",
                output_type="markdown", file_path=cached_file_path,
            )
            step_messages.append({
                "stage": 0, "stageName": "attachment", "message": "已加载附件处理结果",
                "status": "cached", "duration": cached_duration,
                "outputType": "markdown", "filePath": cached_file_path,
            })

        if start_steps <= 0:
            failed_step = 0
            yield emit_stage_start(0, "attachment", message_id, is_retry=from_step is not None)
            yield emit_stage_progress(0, "attachment", "正在分析附件...", 50)
            if not await mock_sleep(random.uniform(5, 7)):
                async for evt in on_cancelled():
                    yield evt
                return
            stage0_duration = round(random.uniform(5, 7), 2)
            mock_prompt = f"用户需求：\n{body.prompt}"
            save_stage_output("final_prompt", 0, mock_prompt, output_session_id, message_id, "md")
            file_path = build_file_path(output_session_id, message_id, "step0_final_prompt.md")
            stages["attachment"] = StageResult(status="success", duration=stage0_duration)
            yield emit_stage_complete(
                0, "attachment", "success", "已处理用户需求",
                duration=stage0_duration, output_type="markdown",
                file_path=file_path, output_preview=make_preview(mock_prompt),
            )
            step_messages.append({
                "stage": 0, "stageName": "attachment", "message": "已处理用户需求",
                "status": "success", "duration": stage0_duration,
                "outputType": "markdown", "filePath": file_path,
            })

        if start_steps > 1:
            save_stage_output("requirement", 1, mock_requirement, output_session_id, message_id, "md")
            cached_duration = round(random.uniform(5, 7), 2)
            stages["requirement"] = StageResult(status="success", duration=cached_duration)
            cached_file_path = build_file_path(output_session_id, message_id, "step1_requirement.md")
            yield emit_stage_complete(
                1, "requirement", "cached",
                output_type="markdown", file_path=cached_file_path,
                output_preview=make_preview(mock_requirement),
            )
            step_messages.append({
                "stage": 1, "stageName": "requirement", "message": "已加载需求标准化结果",
                "outputPreview": make_preview(mock_requirement), "status": "cached",
                "duration": cached_duration, "outputType": "markdown", "filePath": cached_file_path,
            })

        if start_steps <= 1:
            failed_step = 1
            yield emit_stage_start(1, "requirement", message_id, is_retry=from_step is not None)
            yield emit_stage_progress(1, "requirement", "正在标准化需求文档...", 50)
            if not await mock_sleep(random.uniform(5, 7)):
                async for evt in on_cancelled():
                    yield evt
                return
            stage1_duration = round(random.uniform(5, 7), 2)
            save_stage_output("requirement", 1, mock_requirement, output_session_id, message_id, "md")
            file_path = build_file_path(output_session_id, message_id, "step1_requirement.md")
            stages["requirement"] = StageResult(status="success", duration=stage1_duration)
            yield emit_stage_complete(
                1, "requirement", "success", "需求标准化完成",
                duration=stage1_duration, output_type="markdown",
                file_path=file_path, output_preview=make_preview(mock_requirement),
            )
            step_messages.append({
                "stage": 1, "stageName": "requirement", "message": "需求标准化完成",
                "outputPreview": make_preview(mock_requirement), "status": "success",
                "duration": stage1_duration, "outputType": "markdown", "filePath": file_path,
            })

        if start_steps > 2:
            save_stage_output(
                "generation", 2,
                {"files": [f.model_dump() for f in files], "message": MOCK_INITIAL_MESSAGE},
                output_session_id, message_id, "json",
            )
            save_vue_files_from_json([f.model_dump() for f in files], output_session_id, 2, "generation", message_id)
            cached_duration = round(random.uniform(5, 7), 2)
            stages["generation"] = StageResult(status="success", duration=cached_duration)
            cached_file_path = build_file_path(output_session_id, message_id, "step2_generation.json")
            cached_vue_dir = build_file_path(output_session_id, message_id, "step2_generation_vue")
            yield emit_stage_complete(
                2, "generation", "cached",
                message=f"已加载代码生成结果（{len(files)} 个文件）",
                output_type="vue", file_path=cached_file_path, vue_dir_path=cached_vue_dir,
                files=files,
            )
            step_messages.append({
                "stage": 2, "stageName": "generation",
                "message": f"已加载代码生成结果（{len(files)} 个文件）",
                "status": "cached", "duration": cached_duration,
                "outputType": "vue", "filePath": cached_file_path, "vueDirPath": cached_vue_dir,
            })

        if start_steps <= 2:
            failed_step = 2
            yield emit_stage_start(2, "generation", message_id, is_retry=from_step is not None)
            yield emit_stage_progress(2, "generation", "正在生成 Vue 组件代码...", 50)
            if not await mock_sleep(random.uniform(5, 7)):
                async for evt in on_cancelled():
                    yield evt
                return
            stage2_duration = round(random.uniform(5, 7), 2)
            save_stage_output(
                "generation", 2,
                {"files": [f.model_dump() for f in files], "message": MOCK_INITIAL_MESSAGE},
                output_session_id, message_id, "json",
            )
            save_vue_files_from_json([f.model_dump() for f in files], output_session_id, 2, "generation", message_id)
            file_path = build_file_path(output_session_id, message_id, "step2_generation.json")
            vue_dir_path = build_file_path(output_session_id, message_id, "step2_generation_vue")
            stages["generation"] = StageResult(status="success", duration=stage2_duration)
            yield emit_stage_complete(
                2, "generation", "success",
                f"生成了 {len(files)} 个 Vue 组件文件（Mock 数据）",
                duration=stage2_duration, output_type="vue",
                file_path=file_path, vue_dir_path=vue_dir_path, files=files,
            )
            step_messages.append({
                "stage": 2, "stageName": "generation",
                "message": f"生成了 {len(files)} 个 Vue 组件文件（Mock 数据）",
                "status": "success", "duration": stage2_duration,
                "outputType": "vue", "filePath": file_path, "vueDirPath": vue_dir_path,
            })

        if start_steps <= 3:
            if body.componentLib.lower() == "ccui":
                failed_step = 3
                yield emit_stage_start(3, "optimization", message_id)
                yield emit_stage_progress(3, "optimization", "正在优化 UX...", 50)
                if not await mock_sleep(random.uniform(5, 7)):
                    async for evt in on_cancelled():
                        yield evt
                    return
                stage3_duration = round(random.uniform(5, 7), 2)
                save_stage_output(
                    "optimization", 3,
                    {"files": [f.model_dump() for f in files], "message": "UX 优化完成（Mock 数据）"},
                    output_session_id, message_id, "json",
                )
                save_vue_files_from_json([f.model_dump() for f in files], output_session_id, 3, "optimization", message_id)
                file_path = build_file_path(output_session_id, message_id, "step3_optimization.json")
                vue_dir_path = build_file_path(output_session_id, message_id, "step3_optimization_vue")
                stages["optimization"] = StageResult(status="success", duration=stage3_duration)
                yield emit_stage_complete(
                    3, "optimization", "success", "UX 优化完成（Mock 数据）",
                    duration=stage3_duration, output_type="vue",
                    file_path=file_path, vue_dir_path=vue_dir_path, files=files,
                )
                step_messages.append({
                    "stage": 3, "stageName": "optimization",
                    "message": "UX 优化完成（Mock 数据）",
                    "status": "success", "duration": stage3_duration,
                    "outputType": "vue", "filePath": file_path, "vueDirPath": vue_dir_path,
                })
            else:
                stages["optimization"] = StageResult(status="skipped", duration=0)
                step_messages.append({
                    "stage": 3, "stageName": "optimization",
                    "message": "跳过（仅 CcUI 组件库需要）", "status": "skipped", "duration": 0,
                })

        summary_message = build_step_summary(step_messages)
        try:
            await update_session_with_ai_message(
                db, body.sessionId, files, summary_message, None, stages,
                message_id=message_id, step_messages=step_messages,
                retry_message_id=retry_message_id,
            )
        except Exception as e:
            logger.error(f"[SSE Mock] 写入 session 失败: {str(e)}")

        yield emit_done(files, summary_message, stages, step_messages=step_messages)
    finally:
        unregister_cancel(message_id)


async def mock_iterate_stream(
    request: Request,
    body,
    db,
    message_id: str,
    output_session_id: str,
    from_step: int | None = None,
    retry_message_id: str | None = None,
) -> AsyncGenerator[str, None]:
    register_cancel(message_id)
    stages: dict[str, StageResult] = {}
    step_messages: list[dict] = []
    files = MOCK_ITERATE_FILES
    ai_message = MOCK_ITERATE_MESSAGE

    async def mock_sleep(seconds: float) -> bool:
        try:
            await run_with_cancel_check(
                asyncio.sleep(seconds), request, task_id=message_id, poll_interval=0.2,
            )
        except (ClientDisconnectedError, GenerationCancelledError):
            return False
        return True

    async def on_cancelled():
        stages["iteration"] = StageResult(status="cancelled")
        step_messages.append({
            "stage": 0, "stageName": "iteration", "message": None,
            "status": "cancelled", "duration": None,
        })
        try:
            await update_session_with_ai_message(
                db, body.sessionId, files, "用户取消了生成", 0, stages,
                message_id=message_id, step_messages=step_messages,
                retry_message_id=retry_message_id,
            )
        except Exception:
            pass
        yield emit_cancelled(cancelled_at_step=0, stages=stages)

    try:
        yield emit_stage_start(0, "iteration", message_id, is_retry=from_step is not None)
        yield emit_stage_progress(0, "iteration", "正在迭代生成代码...", 40)
        if not await mock_sleep(random.uniform(5, 7)):
            async for evt in on_cancelled():
                yield evt
            return
        yield emit_stage_progress(0, "iteration", "正在迭代生成代码...", 80)
        if not await mock_sleep(random.uniform(5, 7)):
            async for evt in on_cancelled():
                yield evt
            return

        duration = round(random.uniform(5, 7), 2)
        save_stage_output("iteration", 0, {
            "prompt": body.prompt,
            "files": [f.model_dump() for f in files],
            "message": ai_message,
        }, output_session_id, message_id, "json")
        save_vue_files_from_json([f.model_dump() for f in files], output_session_id, 0, "iteration", message_id)

        file_path = build_file_path(output_session_id, message_id, "step0_iteration.json")
        vue_dir_path = build_file_path(output_session_id, message_id, "step0_iteration_vue")
        stages["iteration"] = StageResult(status="success", duration=duration)
        step_messages.append({
            "stage": 0, "stageName": "iteration", "message": None,
            "status": "success", "duration": duration,
            "outputType": "vue", "filePath": file_path, "vueDirPath": vue_dir_path,
        })
        yield emit_stage_complete(
            0, "iteration", "success", ai_message,
            duration=duration, output_type="vue",
            file_path=file_path, vue_dir_path=vue_dir_path, files=files,
        )

        try:
            await update_session_with_ai_message(
                db, body.sessionId, files, ai_message, None, stages,
                message_id=message_id, step_messages=step_messages,
                retry_message_id=retry_message_id,
            )
        except Exception as e:
            logger.error(f"[SSE Mock] 写入 session 失败: {str(e)}")

        yield emit_done(files, ai_message, stages)
    finally:
        unregister_cancel(message_id)
