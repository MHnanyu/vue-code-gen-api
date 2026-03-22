import asyncio
import logging
import os
import json
import time
import uuid
from datetime import datetime
from uuid import uuid4
from collections.abc import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional

from app.database import get_database
from app.schemas.response import Response, ErrorCode
from app.schemas.generate import (
    GenerateInitialRequest, GenerateIterateRequest,
    GeneratedFile, StageResult, Attachment, UploadResponseData,
    ImageAnalyzeRequest, ImageAnalyzeResponseData,
)
from app.utils.sse import (
    make_preview,
    emit_stage_start, emit_stage_progress, emit_stage_complete,
    emit_error, emit_cancelled, emit_done,
)
from app.utils.output import (
    load_stage_output, save_stage_output, save_vue_files_from_json,
    build_file_path, build_step_summary, update_session_with_ai_message,
    rollback_before_retry, write_retry_initial_message,
)
from app.utils.cancellation import (
    run_with_cancel_check, ClientDisconnectedError, GenerationCancelledError,
    register_cancel, unregister_cancel, set_cancel,
)
from app.services.ai_factory import AIServiceFactory
from app.services.requirement_service import RequirementService
from app.services.openclaw_service import OpenclawService
from app.services.glm4v_service import GLM4VService
from app.services.attachment_service import process_attachments, build_attachment_summary
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["generate"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
MARKDOWN_EXTENSIONS = {".md", ".markdown"}
TEXT_EXTENSIONS = {".txt"}

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}

CCUI_GENERATION_PROMPT = """请调用 vue3-ccui-generator skill，基于以下UX规范文档，生成基于 Vue3 + CcUI 组件库的原型页面。

【原型极简原则】
- 这是一次性原型图，不是生产代码
- 尽量只生成 MainPage.vue 一个文件
- script 部分使用硬编码 mock 数据，不需要 API 调用、表单验证等逻辑
- 不要定义 interface/type，不需要复杂 TypeScript
- 每个文件不超过 300 行
- 重点在于组件位置、布局结构、基础样式

输出要求：按照 skill 的要求返回 JSON 格式的结果，且仅输出 JSON 即可。

---
UX规范文档：
"""

CCUI_OPTIMIZATION_PROMPT = """请调用 ccui-ux-guardian skill，基于原始的 Vue 组件，生成符合企业 UI/UX 标准的 Vue 组件。

【注意】
- 保持原型极简原则，优化仅限样式和布局层面
- 不要增加复杂逻辑、API 调用、表单验证等
- 每个文件不超过 300 行

输出要求：按照 skill 的要求返回 JSON 格式的结果，且仅输出 JSON 即可。"""


# ──────────────────────────────────────────────
# Utility helpers
# ──────────────────────────────────────────────

def get_file_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    elif ext in MARKDOWN_EXTENSIONS:
        return "markdown"
    elif ext in TEXT_EXTENSIONS:
        return "text"
    return "text"


def convert_api_files_to_generated(api_files: list[dict]) -> list[GeneratedFile]:
    return [
        GeneratedFile(
            id=file.get("id", f"file-{i}"),
            name=file.get("name", f"file{i}.vue"),
            path=file.get("path", f"/src/{file.get('name', f'file{i}.vue')}"),
            type=file.get("type", "file"),
            language=file.get("language", "vue"),
            content=file.get("content", ""),
            children=file.get("children")
        )
        for i, file in enumerate(api_files)
    ]


def _load_cached_steps_for_session(from_step: int, session_id: str, prev_step_messages: list[dict] | None = None):
    from app.utils.sse import make_preview
    stages = {}
    step_messages = []

    prev_duration_map = {}
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
                sm["outputPreview"] = make_preview(cached)
            elif isinstance(cached, dict) and "files" in cached:
                sm["outputType"] = "vue"
                sm["message"] = f"已加载代码生成结果（{len(cached.get('files', []))} 个文件）"
            step_messages.append(sm)

    return stages, step_messages


def make_error_vue_page(title: str, description: str, prompt: str) -> GeneratedFile:
    escaped_prompt = prompt.replace('"', '\\"')
    return GeneratedFile(
        id="error-page",
        name="MainPage.vue",
        path="/src/MainPage.vue",
        type="file",
        language="vue",
        content=f"""<template>
  <div class="p-6">
    <el-alert
      title="{title}"
      type="error"
      description="{description}"
      show-icon
    />
    <p class="mt-4 text-gray-600">原始需求：{escaped_prompt}</p>
  </div>
</template>

<script setup lang="ts">
import {{ ref }} from 'vue'
</script>"""
    )


# ──────────────────────────────────────────────
# Upload
# ──────────────────────────────────────────────

@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    logger.info(f"收到文件上传请求 - 文件数: {len(files)}")

    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.PARAM_ERROR, "message": "最多支持上传5个文件", "data": None}
        )

    uploaded_files = []

    for file in files:
        file_id = str(uuid.uuid4())
        ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        saved_filename = f"{file_id}{ext}"
        file_path = os.path.join(UPLOAD_DIR, saved_filename)

        content = await file.read()
        file_size = len(content)

        with open(file_path, "wb") as f:
            f.write(content)

        file_type = get_file_type(file.filename or "")

        attachment = Attachment(
            id=file_id,
            url=f"/uploads/{saved_filename}",
            name=file.filename or "unknown",
            type=file_type,
            size=file_size
        )
        uploaded_files.append(attachment)
        logger.info(f"文件上传成功 - id: {file_id}, name: {file.filename}, type: {file_type}, size: {file_size}")

    return Response(data=UploadResponseData(files=uploaded_files))


# ──────────────────────────────────────────────
# Cancel
# ──────────────────────────────────────────────

@router.post("/generate/cancel")
async def cancel_generation(taskId: str):
    set_cancel(taskId)
    return {"code": 0, "message": "取消请求已发送", "data": None}


# ──────────────────────────────────────────────
# SSE stream: initial
# ──────────────────────────────────────────────

@router.post("/generate/initial/stream")
async def generate_initial_stream(body: GenerateInitialRequest, request: Request):
    logger.info(f"[SSE] 收到初始生成请求 - sessionId: {body.sessionId}, prompt长度: {len(body.prompt)}, fromStep: {body.fromStep}")

    from_step = body.fromStep

    if from_step is not None:
        if from_step not in (0, 1, 2, 3):
            raise HTTPException(
                status_code=400,
                detail={"code": ErrorCode.PARAM_ERROR, "message": "fromStep 必须为 0、1、2 或 3", "data": None}
            )
        if not body.sessionId:
            raise HTTPException(
                status_code=400,
                detail={"code": ErrorCode.PARAM_ERROR, "message": "使用 fromStep 重试时必须提供 sessionId", "data": None}
            )

    db = get_database() if body.sessionId else None

    pre_stages, pre_step_msgs = None, None
    if from_step is not None and from_step > 0 and body.sessionId:
        need_reset = False
        if body.attachments and any(a.type == "image" for a in body.attachments):
            cached = load_stage_output(0, "final_prompt", body.sessionId, "md")
            if cached and "图片分析结果" not in cached:
                need_reset = True
        if not need_reset:
            prev_step_messages = None
            if db is not None:
                session = await db.sessions.find_one({"id": body.sessionId}, {"messages": 1})
                if session and "messages" in session:
                    messages = session["messages"]
                    for i in range(len(messages) - 1, -1, -1):
                        if messages[i].get("role") == "assistant":
                            prev_step_messages = messages[i].get("stepMessages")
                            break
            pre_stages, pre_step_msgs = _load_cached_steps_for_session(from_step, body.sessionId, prev_step_messages)

    if from_step is not None and body.sessionId and db is not None:
        await rollback_before_retry(db, body.sessionId)

    message_id = str(uuid4())
    output_session_id = body.sessionId if body.sessionId else f"no_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = os.path.join("output", output_session_id, message_id)
    os.makedirs(output_dir, exist_ok=True)

    retry_message_id = None
    if pre_stages is not None and db is not None:
        await write_retry_initial_message(db, body.sessionId, message_id, pre_stages, pre_step_msgs)
        retry_message_id = message_id

    if body.sessionId is not None and db is None:
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": "数据库未连接", "data": None}
        )

    prev_duration_map: dict[str, float | None] = {}
    if pre_stages:
        for stage_key, stage_result in pre_stages.items():
            if stage_result.duration is not None:
                prev_duration_map[stage_key] = stage_result.duration

    if settings.MOCK_MODE:
        from app.mock.stream_mock import mock_initial_stream
        return StreamingResponse(
            mock_initial_stream(request, body, db, message_id, output_session_id, from_step, retry_message_id),
            media_type="text/event-stream",
            headers=SSE_HEADERS,
        )

    async def event_stream() -> AsyncGenerator[str, None]:
        nonlocal from_step
        register_cancel(message_id)
        stages: dict[str, StageResult] = {}
        step_messages: list[dict] = []
        files: list[GeneratedFile] = []
        ai_message = "生成完成"
        failed_step: int | None = None
        final_prompt = body.prompt
        requirement_doc: str | None = None

        progress_queue: asyncio.Queue[str] = asyncio.Queue()

        stage_name_map = {0: "attachment", 1: "requirement", 2: "generation", 3: "optimization"}

        async def save_cancel_to_db():
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
                logger.error(f"[SSE] 取消时写入 session 失败: {str(e)}")

        async def emit_stage_error(stage: int, stage_name: str, step: int, error_msg: str, duration: float | None):
            stages[stage_name] = StageResult(status="failed", duration=duration, error=error_msg)
            yield emit_stage_complete(
                stage, stage_name, "failed",
                message=f"{stage_name}失败: {error_msg}",
                duration=duration, error=error_msg,
            )
            yield emit_error(ErrorCode.AI_GENERATE_FAILED, error_msg, step, stages)
            try:
                await update_session_with_ai_message(
                    db, body.sessionId, files, f"步骤{step}（{stage_name}）失败: {error_msg}",
                    step, stages, message_id=message_id, step_messages=step_messages,
                    retry_message_id=retry_message_id,
                )
            except Exception as save_err:
                logger.error(f"[SSE] 写入 session 失败: {str(save_err)}")

        try:
            # ====== 步骤0: 附件处理 ======
            failed_step = 0

            if from_step is not None and from_step > 0:
                cached_prompt = load_stage_output(0, "final_prompt", output_session_id, "md")
                if cached_prompt:
                    has_image_in_request = any(
                        a.type == "image" for a in body.attachments
                    ) if body.attachments else False
                    has_image_in_cache = "图片分析结果" in cached_prompt

                    if has_image_in_request and not has_image_in_cache:
                        from_step = 0
                    else:
                        final_prompt = cached_prompt
                        cached_file_path = build_file_path(output_session_id, message_id, "step0_final_prompt.md")
                        save_stage_output("final_prompt", 0, final_prompt, output_session_id, message_id, "md")
                        cached_duration = prev_duration_map.get("attachment")
                        stages["attachment"] = StageResult(status="success", duration=cached_duration)
                        yield emit_stage_complete(
                            0, "attachment", "cached",
                            output_type="markdown", file_path=cached_file_path,
                            output_preview=make_preview(final_prompt),
                        )
                        msg = build_attachment_summary(body.attachments)
                        msg = f"已加载{msg[2:]}" if msg.startswith("已") else msg
                        step_messages.append({
                            "stage": 0, "stageName": "attachment", "message": msg,
                            "status": "cached", "duration": cached_duration,
                            "outputType": "markdown", "filePath": cached_file_path,
                        })
                else:
                    yield emit_error(ErrorCode.PARAM_ERROR, f"找不到步骤0的缓存结果，无法从步骤 {from_step} 开始重试", 0, {})
                    return

            if from_step is None or from_step == 0:
                yield emit_stage_start(0, "attachment", message_id, is_retry=from_step == 0)
                stage0_start = time.time()

                def on_image_progress(idx, total, attachment):
                    progress_queue.put_nowait(emit_stage_progress(
                        0, "attachment",
                        f"正在分析图片 {idx + 1}/{total}: {attachment.name}",
                        int((idx + 1) / total * 100),
                    ))

                try:
                    glm4v_service = GLM4VService()

                    attach_task = asyncio.create_task(
                        process_attachments(body, glm4v_service, on_image_progress=on_image_progress)
                    )

                    while not attach_task.done():
                        try:
                            evt = await asyncio.wait_for(progress_queue.get(), timeout=0.1)
                            yield evt
                        except asyncio.TimeoutError:
                            pass

                    while True:
                        try:
                            evt = progress_queue.get_nowait()
                            yield evt
                        except asyncio.QueueEmpty:
                            break

                    final_prompt = await attach_task

                    save_stage_output("final_prompt", 0, final_prompt, output_session_id, message_id, "md")
                    stage0_duration = round(time.time() - stage0_start, 2)
                    file_path = build_file_path(output_session_id, message_id, "step0_final_prompt.md")
                    msg = build_attachment_summary(body.attachments)
                    stages["attachment"] = StageResult(status="success", duration=stage0_duration)
                    yield emit_stage_complete(
                        0, "attachment", "success", msg,
                        duration=stage0_duration, output_type="markdown",
                        file_path=file_path, output_preview=make_preview(final_prompt),
                    )
                    step_messages.append({
                        "stage": 0, "stageName": "attachment", "message": msg,
                        "status": "success", "duration": stage0_duration,
                        "outputType": "markdown", "filePath": file_path,
                    })
                except (ClientDisconnectedError, GenerationCancelledError):
                    yield emit_cancelled(failed_step, stages)
                    await save_cancel_to_db()
                    return
                except Exception as e:
                    stage0_duration = round(time.time() - stage0_start, 2)
                    async for evt in emit_stage_error(0, "attachment", 0, str(e), stage0_duration):
                        yield evt
                    return

            # ====== 步骤1: 需求标准化 ======
            failed_step = 1

            if from_step is not None and from_step > 1:
                cached_requirement = load_stage_output(1, "requirement", output_session_id, "md")
                if cached_requirement:
                    requirement_doc = cached_requirement
                    cached_file_path = build_file_path(output_session_id, message_id, "step1_requirement.md")
                    save_stage_output("requirement", 1, requirement_doc, output_session_id, message_id, "md")
                    cached_duration = prev_duration_map.get("requirement")
                    stages["requirement"] = StageResult(status="success", duration=cached_duration)
                    yield emit_stage_complete(
                        1, "requirement", "cached",
                        output_type="markdown", file_path=cached_file_path,
                        output_preview=make_preview(requirement_doc),
                    )
                    step_messages.append({
                        "stage": 1, "stageName": "requirement", "message": "已加载需求标准化结果",
                        "outputPreview": make_preview(requirement_doc), "status": "cached",
                        "duration": cached_duration, "outputType": "markdown", "filePath": cached_file_path,
                    })
                else:
                    yield emit_error(ErrorCode.PARAM_ERROR, f"找不到步骤1的缓存结果，无法从步骤 {from_step} 开始重试", 1, stages)
                    return
            else:
                yield emit_stage_start(1, "requirement", message_id, is_retry=from_step is not None)
                stage1_start = time.time()

                try:
                    requirement_service = RequirementService()
                    stage1_result = await run_with_cancel_check(
                        requirement_service.standardize_requirement(
                            user_requirement=final_prompt, temperature=0.2
                        ),
                        request, task_id=message_id,
                    )
                    stage1_duration = stage1_result.get("duration", round(time.time() - stage1_start, 2))

                    if stage1_result["status"] == "failed":
                        error_msg = stage1_result.get("error", "未知错误")
                        async for evt in emit_stage_error(1, "requirement", 1, error_msg, stage1_duration):
                            yield evt
                        return

                    requirement_doc = stage1_result["output"]
                    save_stage_output("requirement", 1, requirement_doc, output_session_id, message_id, "md")
                    file_path = build_file_path(output_session_id, message_id, "step1_requirement.md")
                    stages["requirement"] = StageResult(status="success", duration=stage1_duration)
                    yield emit_stage_complete(
                        1, "requirement", "success", "需求标准化完成",
                        duration=stage1_duration, output_type="markdown",
                        file_path=file_path, output_preview=make_preview(requirement_doc),
                    )
                    step_messages.append({
                        "stage": 1, "stageName": "requirement", "message": "需求标准化完成",
                        "outputPreview": make_preview(requirement_doc), "status": "success",
                        "duration": stage1_duration, "outputType": "markdown", "filePath": file_path,
                    })
                except (ClientDisconnectedError, GenerationCancelledError):
                    yield emit_cancelled(failed_step, stages)
                    await save_cancel_to_db()
                    return
                except Exception as e:
                    stage1_duration = round(time.time() - stage1_start, 2)
                    async for evt in emit_stage_error(1, "requirement", 1, str(e), stage1_duration):
                        yield evt
                    return

            # ====== 步骤2: 代码生成 ======
            failed_step = 2
            assert requirement_doc is not None, "requirement_doc must be set before step 2"

            if from_step is not None and from_step > 2:
                cached_generation = load_stage_output(2, "generation", output_session_id, "json")
                if cached_generation and isinstance(cached_generation, dict):
                    result = cached_generation
                    api_files = result.get("files", [])
                    files = convert_api_files_to_generated(api_files)
                    ai_message = result.get("message", f"代码生成完成（{body.componentLib}）")
                    cached_duration = prev_duration_map.get("generation")
                    stages["generation"] = StageResult(status="success", duration=cached_duration)
                    file_path = build_file_path(output_session_id, message_id, "step2_generation.json")
                    vue_dir_path = build_file_path(output_session_id, message_id, "step2_generation_vue")
                    yield emit_stage_complete(
                        2, "generation", "cached",
                        message=f"已加载代码生成结果（{len(files)} 个文件）",
                        output_type="vue", file_path=file_path, vue_dir_path=vue_dir_path,
                        files=files,
                    )
                    step_messages.append({
                        "stage": 2, "stageName": "generation",
                        "message": f"已加载代码生成结果（{len(files)} 个文件）",
                        "status": "cached", "duration": cached_duration,
                        "outputType": "vue", "filePath": file_path, "vueDirPath": vue_dir_path,
                    })
                else:
                    yield emit_error(ErrorCode.PARAM_ERROR, f"找不到步骤2的缓存结果，无法从步骤 {from_step} 开始重试", 2, stages)
                    return
            else:
                yield emit_stage_start(2, "generation", message_id, is_retry=from_step is not None)
                stage2_start = time.time()

                try:
                    if body.componentLib.lower() == "ccui":
                        openclaw_service = OpenclawService()
                        ccui_prompt = CCUI_GENERATION_PROMPT + requirement_doc
                        result = await run_with_cancel_check(
                            openclaw_service.generate_vue_files(prompt=ccui_prompt, ccui_prompt=""),
                            request, task_id=message_id,
                        )
                    else:
                        ai_service = AIServiceFactory.get_service()
                        result = await run_with_cancel_check(
                            ai_service.generate_vue_files(prompt=requirement_doc, existing_files=None),
                            request, task_id=message_id,
                        )

                    stage2_duration = round(time.time() - stage2_start, 2)
                    api_files = result.get("files", [])
                    ai_message = result.get("message", f"代码生成完成（{body.componentLib}）")
                    files = convert_api_files_to_generated(api_files)

                    if not files:
                        async for evt in emit_stage_error(2, "generation", 2, "未能生成有效的代码文件", stage2_duration):
                            yield evt
                        return

                    save_stage_output("generation", 2, result, output_session_id, message_id, "json")
                    if api_files:
                        save_vue_files_from_json(api_files, output_session_id, 2, "generation", message_id)

                    file_path = build_file_path(output_session_id, message_id, "step2_generation.json")
                    vue_dir_path = build_file_path(output_session_id, message_id, "step2_generation_vue")
                    gen_msg = ai_message if ai_message else f"生成了 {len(files)} 个 Vue 组件文件（{body.componentLib}）"
                    stages["generation"] = StageResult(status="success", duration=stage2_duration)
                    yield emit_stage_complete(
                        2, "generation", "success", gen_msg,
                        duration=stage2_duration, output_type="vue",
                        file_path=file_path, vue_dir_path=vue_dir_path, files=files,
                    )
                    step_messages.append({
                        "stage": 2, "stageName": "generation", "message": gen_msg,
                        "status": "success", "duration": stage2_duration,
                        "outputType": "vue", "filePath": file_path, "vueDirPath": vue_dir_path,
                    })
                except (ClientDisconnectedError, GenerationCancelledError):
                    yield emit_cancelled(failed_step, stages)
                    await save_cancel_to_db()
                    return
                except Exception as e:
                    stage2_duration = round(time.time() - stage2_start, 2)
                    async for evt in emit_stage_error(2, "generation", 2, str(e), stage2_duration):
                        yield evt
                    return

            # ====== 步骤3: UX优化（仅 CcUI） ======
            failed_step = 3
            if body.componentLib.lower() == "ccui":
                if from_step is not None and from_step > 3:
                    stages["optimization"] = StageResult(status="skipped", duration=None)
                    yield emit_stage_complete(3, "optimization", "skipped", message="跳过")
                    step_messages.append({"stage": 3, "stageName": "optimization", "message": "跳过", "status": "skipped", "duration": 0})
                else:
                    yield emit_stage_start(3, "optimization", message_id, is_retry=from_step is not None)
                    stage3_start = time.time()

                    try:
                        openclaw_service = OpenclawService()
                        stage2_files_json = json.dumps([f.model_dump() for f in files], ensure_ascii=False, indent=2)
                        full_prompt = f"{CCUI_OPTIMIZATION_PROMPT}\n\n待优化的文件：\n{stage2_files_json}\n"

                        stage3_result = await run_with_cancel_check(
                            openclaw_service.generate_vue_files(prompt=full_prompt, ccui_prompt=""),
                            request, task_id=message_id,
                        )
                        stage3_duration = round(time.time() - stage3_start, 2)

                        stage3_api_files = stage3_result.get("files", [])
                        stage3_message = stage3_result.get("message", "优化完成")
                        optimized_files = convert_api_files_to_generated(stage3_api_files)

                        if optimized_files:
                            files = optimized_files
                            ai_message = stage3_message

                        save_stage_output("optimization", 3, stage3_result, output_session_id, message_id, "json")
                        if stage3_api_files:
                            save_vue_files_from_json(stage3_api_files, output_session_id, 3, "optimization", message_id)

                        file_path = build_file_path(output_session_id, message_id, "step3_optimization.json")
                        vue_dir_path = build_file_path(output_session_id, message_id, "step3_optimization_vue")
                        opt_msg = stage3_message if stage3_message else (f"UX 优化完成（{len(optimized_files)} 个文件）" if optimized_files else "UX 优化未产出新文件")
                        stages["optimization"] = StageResult(status="success", duration=stage3_duration)
                        yield emit_stage_complete(
                            3, "optimization", "success", opt_msg,
                            duration=stage3_duration, output_type="vue",
                            file_path=file_path, vue_dir_path=vue_dir_path,
                            files=optimized_files if optimized_files else None,
                        )
                        step_messages.append({
                            "stage": 3, "stageName": "optimization", "message": opt_msg,
                            "status": "success", "duration": stage3_duration,
                            "outputType": "vue", "filePath": file_path, "vueDirPath": vue_dir_path,
                        })
                    except (ClientDisconnectedError, GenerationCancelledError):
                        yield emit_cancelled(failed_step, stages)
                        await save_cancel_to_db()
                        return
                    except Exception as e:
                        stage3_duration = round(time.time() - stage3_start, 2)
                        async for evt in emit_stage_error(3, "optimization", 3, str(e), stage3_duration):
                            yield evt
                        return
            else:
                stages["optimization"] = StageResult(status="skipped", duration=0)
                step_messages.append({"stage": 3, "stageName": "optimization", "message": "跳过（仅 CcUI 组件库需要）", "status": "skipped", "duration": 0})

            # ====== 完成 ======
            has_failure = any(v.status == "failed" for v in stages.values()) if stages else False
            if not has_failure:
                failed_step = None
            summary_message = build_step_summary(step_messages) if not has_failure else ai_message
            try:
                await update_session_with_ai_message(
                    db, body.sessionId, files, summary_message, failed_step, stages,
                    message_id=message_id, step_messages=step_messages,
                    retry_message_id=retry_message_id,
                )
            except Exception as e:
                logger.error(f"[SSE] 写入 session 失败: {str(e)}")

            yield emit_done(files, summary_message, stages, failed_step=failed_step, step_messages=step_messages)

        finally:
            unregister_cancel(message_id)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


# ──────────────────────────────────────────────
# SSE stream: iterate
# ──────────────────────────────────────────────

@router.post("/generate/iterate/stream")
async def generate_iterate_stream(body: GenerateIterateRequest, request: Request):
    from_step = body.fromStep
    logger.info(f"[SSE] 收到迭代生成请求 - sessionId: {body.sessionId}, prompt长度: {len(body.prompt)}, 文件数: {len(body.files)}, fromStep: {from_step}")

    if from_step is not None:
        if from_step != 0:
            raise HTTPException(
                status_code=400,
                detail={"code": ErrorCode.PARAM_ERROR, "message": "iterate 的 fromStep 仅支持 0", "data": None}
            )
        if not body.sessionId:
            raise HTTPException(
                status_code=400,
                detail={"code": ErrorCode.PARAM_ERROR, "message": "使用 fromStep 重试时必须提供 sessionId", "data": None}
            )

    db = get_database() if body.sessionId else None

    restored_files = None
    if from_step is not None and body.sessionId and db is not None:
        restored_files = await rollback_before_retry(db, body.sessionId)

    message_id = str(uuid4())
    output_session_id = body.sessionId if body.sessionId else f"no_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = os.path.join("output", output_session_id, message_id)
    os.makedirs(output_dir, exist_ok=True)

    retry_message_id = None
    if from_step is not None and body.sessionId and db is not None:
        await write_retry_initial_message(db, body.sessionId, message_id, {}, [])
        retry_message_id = message_id

    if body.sessionId is not None and db is None:
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": "数据库未连接", "data": None}
        )

    if settings.MOCK_MODE:
        from app.mock.stream_mock import mock_iterate_stream
        return StreamingResponse(
            mock_iterate_stream(request, body, db, message_id, output_session_id, from_step, retry_message_id),
            media_type="text/event-stream",
            headers=SSE_HEADERS,
        )

    async def event_stream() -> AsyncGenerator[str, None]:
        register_cancel(message_id)
        stages: dict[str, StageResult] = {}
        step_messages: list[dict] = []
        files: list[GeneratedFile] = []
        ai_message = "代码生成完成"

        try:
            yield emit_stage_start(0, "iteration", message_id, is_retry=from_step is not None)
            stage_start = time.time()

            try:
                ai_service = AIServiceFactory.get_service()
                existing_files = restored_files if restored_files is not None else [f.model_dump() for f in body.files]
                result = await run_with_cancel_check(
                    ai_service.generate_vue_files(prompt=body.prompt, existing_files=existing_files),
                    request, task_id=message_id,
                )

                api_files = result.get("files", [])
                ai_message = result.get("message", "代码生成完成")
                files = convert_api_files_to_generated(api_files)

                if not files:
                    ai_message = "未能生成有效的代码文件，请尝试更详细的需求描述"

                duration = round(time.time() - stage_start, 2)

                save_stage_output("iteration", 0, {
                    "prompt": body.prompt,
                    "files": [f.model_dump() for f in files],
                    "message": ai_message,
                }, output_session_id, message_id, "json")

                if api_files:
                    save_vue_files_from_json(api_files, output_session_id, 0, "iteration", message_id)

                file_path = build_file_path(output_session_id, message_id, "step0_iteration.json")
                vue_dir_path = build_file_path(output_session_id, message_id, "step0_iteration_vue")
                status = "success" if files else "failed"
                stages["iteration"] = StageResult(
                    status=status, duration=duration,
                    error=None if files else "未能生成有效的代码文件",
                )
                step_messages.append({
                    "stage": 0, "stageName": "iteration", "message": None,
                    "status": status, "duration": duration,
                    "outputType": "vue", "filePath": file_path, "vueDirPath": vue_dir_path,
                })
                yield emit_stage_complete(
                    0, "iteration", status, ai_message,
                    duration=duration, output_type="vue",
                    file_path=file_path, vue_dir_path=vue_dir_path,
                    files=files if files else None,
                    error=None if files else "未能生成有效的代码文件",
                )
            except (ClientDisconnectedError, GenerationCancelledError):
                stages["iteration"] = StageResult(status="cancelled", duration=round(time.time() - stage_start, 2))
                step_messages.append({
                    "stage": 0, "stageName": "iteration", "message": None,
                    "status": "cancelled", "duration": stages["iteration"].duration,
                })
                try:
                    await update_session_with_ai_message(
                        db, body.sessionId, files, "用户取消了生成", 0, stages,
                        message_id=message_id, step_messages=step_messages,
                        retry_message_id=retry_message_id,
                    )
                except Exception:
                    pass
                yield emit_cancelled(0, stages)
                return
            except Exception as e:
                duration = round(time.time() - stage_start, 2)
                stages["iteration"] = StageResult(status="failed", duration=duration, error=str(e))
                step_messages.append({
                    "stage": 0, "stageName": "iteration", "message": None,
                    "status": "failed", "duration": duration,
                })
                yield emit_stage_complete(
                    0, "iteration", "failed",
                    message=f"迭代生成失败: {str(e)}",
                    duration=duration, error=str(e),
                )
                yield emit_error(ErrorCode.AI_GENERATE_FAILED, str(e), 0, stages)
                try:
                    await update_session_with_ai_message(
                        db, body.sessionId, files, f"迭代生成失败: {str(e)}", 0, stages,
                        message_id=message_id, step_messages=step_messages,
                        retry_message_id=retry_message_id,
                    )
                except Exception as save_err:
                    logger.error(f"[SSE] 写入 session 失败: {str(save_err)}")
                return

            try:
                await update_session_with_ai_message(
                    db, body.sessionId, files, ai_message, None, stages,
                    message_id=message_id, step_messages=step_messages,
                    retry_message_id=retry_message_id,
                )
            except Exception as e:
                logger.error(f"[SSE] 写入 session 失败: {str(e)}")

            yield emit_done(files, ai_message, stages)
        finally:
            unregister_cancel(message_id)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


# ──────────────────────────────────────────────
# Image analyze
# ──────────────────────────────────────────────

@router.post("/image/analyze")
async def analyze_image(body: ImageAnalyzeRequest):
    logger.info("收到图片分析请求")

    if not body.imageUrl and not body.imageBase64:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.PARAM_ERROR, "message": "请提供imageUrl或imageBase64", "data": None}
        )

    try:
        glm4v_service = GLM4VService()

        image_source = body.imageBase64 if body.imageBase64 else body.imageUrl
        is_base64 = body.imageBase64 is not None

        if not image_source:
            raise HTTPException(
                status_code=400,
                detail={"code": ErrorCode.PARAM_ERROR, "message": "图片源无效", "data": None}
            )

        if body.prompt:
            result = await glm4v_service.analyze_image(
                image_source=image_source,
                prompt=body.prompt,
                is_base64=is_base64
            )
            return Response(data=ImageAnalyzeResponseData(
                description=result,
                rawDescription=result,
                success=True
            ))
        else:
            result = await glm4v_service.describe_for_vue_generation(
                image_source=image_source,
                is_base64=is_base64
            )

            return Response(data=ImageAnalyzeResponseData(
                description=result["raw_description"],
                rawDescription=result["raw_description"],
                success=result["success"]
            ))

    except Exception as e:
        import traceback
        logger.error(f"图片分析失败: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": f"图片分析失败: {str(e)}", "data": None}
        )


@router.post("/image/analyze-file")
async def analyze_image_file(
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None)
):
    logger.info(f"收到图片文件分析请求 - filename: {file.filename}")

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.PARAM_ERROR, "message": "请上传图片文件", "data": None}
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.PARAM_ERROR, "message": f"不支持的文件类型: {ext}", "data": None}
        )

    try:
        content = await file.read()
        image_base64 = GLM4VService.bytes_to_base64(content)

        glm4v_service = GLM4VService()

        if prompt:
            result = await glm4v_service.analyze_image(
                image_source=image_base64,
                prompt=prompt,
                is_base64=True
            )
            return Response(data=ImageAnalyzeResponseData(
                description=result,
                rawDescription=result,
                success=True
            ))
        else:
            result = await glm4v_service.describe_for_vue_generation(
                image_source=image_base64,
                is_base64=True
            )

            return Response(data=ImageAnalyzeResponseData(
                description=result["raw_description"],
                rawDescription=result["raw_description"],
                success=result["success"]
            ))

    except Exception as e:
        import traceback
        logger.error(f"图片文件分析失败: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": f"图片文件分析失败: {str(e)}", "data": None}
        )
