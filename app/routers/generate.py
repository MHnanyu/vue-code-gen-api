import asyncio
import logging
import os
import time
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from app.database import get_database
from app.schemas.response import Response, ErrorCode
from app.schemas.generate import (
    GenerateInitialRequest, GenerateIterateRequest,
    GeneratedFile, StageResult, Attachment, UploadResponseData,
    ImageAnalyzeRequest, ImageAnalyzeResponseData,
)
from app.utils.sse import (
    emit_stage_start, emit_stage_complete,
    emit_error, emit_cancelled, emit_done,
    emit_agent_thinking, emit_tool_call_start,
    emit_tool_call_result, emit_agent_done, emit_agent_cancelled,
    emit_agent_files,
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
from app.services.glm4v_service import GLM4VService
from app.services.minimax_service import summarize_with_minimax
from app.config import settings
from app.pipeline import (
    PipelineContext, StepExecutor, convert_api_files_to_generated,
    _load_cached_steps_for_session, STAGE_NAME_MAP,
)
from app.agent.core import AgentCore
from app.agent.tools import create_tool_registry

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


def _get_file_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return "image"
    if ext in MARKDOWN_EXTENSIONS:
        return "markdown"
    return "text"


def _build_prev_duration_map(pre_stages: dict) -> dict[str, float | None]:
    return {
        k: v.duration for k, v in pre_stages.items() if v.duration is not None
    }


def _make_error_vue_page(title: str, description: str, prompt: str) -> GeneratedFile:
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
</script>""",
    )


def _load_final_files_as_generated(output_dir: str) -> list[GeneratedFile]:
    """Read final Vue files from disk (prefer optimization over generation)."""
    from app.agent.tools import _load_saved_vue_files

    parts = output_dir.replace("\\", "/").split("/")
    if len(parts) >= 3:
        session_id = parts[-2]
        msg_id = parts[-1]
    else:
        return []

    disk_files = _load_saved_vue_files(session_id, msg_id)
    if not disk_files:
        return []

    result = []
    for f in disk_files:
        result.append(GeneratedFile(
            id=str(uuid4()),
            name=f.get("name", "unknown"),
            path=f.get("path", ""),
            type="file",
            language="vue",
            content=f.get("content", ""),
        ))
    return result


def _scan_latest_vue_files(output_dir: str) -> list[dict]:
    """Scan the latest Vue output directory and return file list with download URLs."""
    if not os.path.isdir(output_dir):
        return []

    candidates = []
    try:
        for entry in os.listdir(output_dir):
            entry_path = os.path.join(output_dir, entry)
            if os.path.isdir(entry_path) and entry.endswith("_vue"):
                candidates.append(entry_path)
    except OSError:
        return []

    if not candidates:
        return []

    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    latest_dir = candidates[0]

    rel_dir = latest_dir.replace("\\", "/")
    if rel_dir.startswith("/"):
        rel_dir = rel_dir[1:]

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
                "downloadUrl": f"/output/{rel_dir}/{filename}",
                "lines": content.count("\n") + 1,
                "sizeBytes": len(content.encode("utf-8")),
            })
        except Exception as e:
            logger.warning("[Agent] 读取 Vue 文件失败 %s: %s", filepath, e)

    return files


async def _build_initial_context(
    body: GenerateInitialRequest, request: Request, db,
) -> PipelineContext:
    from_step = body.fromStep
    session_id = body.sessionId
    output_session_id = session_id or f"no_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    if session_id and db is None:
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": "数据库未连接", "data": None},
        )

    pre_stages, pre_step_msgs = None, None
    if from_step is not None and from_step > 0 and session_id:
        need_reset = False
        if body.attachments and any(a.type == "image" for a in body.attachments):
            cached = load_stage_output(0, "final_prompt", session_id, "md")
            if cached and "图片分析结果" not in cached:
                need_reset = True
        if not need_reset:
            prev_step_messages = None
            if db is not None:
                session = await db.sessions.find_one({"id": session_id}, {"messages": 1})
                if session and "messages" in session:
                    messages = session["messages"]
                    for i in range(len(messages) - 1, -1, -1):
                        if messages[i].get("role") == "assistant":
                            prev_step_messages = messages[i].get("stepMessages")
                            break
            pre_stages, pre_step_msgs = _load_cached_steps_for_session(from_step, session_id, prev_step_messages)

    existing_message_id = None
    if from_step is not None and session_id and db is not None:
        existing_message_id, _ = await rollback_before_retry(db, session_id, from_step)

    message_id = existing_message_id or str(uuid4())
    output_dir = os.path.join("output", output_session_id, message_id)
    os.makedirs(output_dir, exist_ok=True)

    retry_message_id = None
    if pre_stages is not None and db is not None:
        await write_retry_initial_message(db, session_id, message_id, pre_stages, pre_step_msgs)
        retry_message_id = message_id

    ctx = PipelineContext(
        db=db,
        session_id=session_id,
        message_id=message_id,
        output_session_id=output_session_id,
        request=request,
        component_lib=body.componentLib,
        from_step=from_step,
        retry_message_id=retry_message_id,
        final_prompt=body.prompt,
    )
    return ctx


def _initial_event_stream(ctx: PipelineContext, body: GenerateInitialRequest) -> AsyncGenerator[str, None]:
    executor = StepExecutor(ctx, body)
    step_generators = [
        (0, executor.execute_attachment_step),
        (1, executor.execute_requirement_step),
        (2, executor.execute_generation_step),
        (3, executor.execute_optimization_step),
    ]

    async def stream():
        register_cancel(ctx.message_id)
        try:
            for step_num, step_fn in step_generators:
                ctx.failed_step = step_num
                async for evt in step_fn():
                    yield evt
                if ctx.stages.get(STAGE_NAME_MAP[step_num]) and ctx.stages[STAGE_NAME_MAP[step_num]].status in ("failed", "cancelled"):
                    return

            has_failure = any(v.status == "failed" for v in ctx.stages.values()) if ctx.stages else False
            if not has_failure:
                ctx.failed_step = None
            summary_message = build_step_summary(ctx.step_messages) if not has_failure else ctx.ai_message
            if not has_failure:
                summary_message = await summarize_with_minimax(summary_message)
            try:
                await update_session_with_ai_message(
                    ctx.db, ctx.session_id, ctx.files, summary_message, ctx.failed_step, ctx.stages,
                    message_id=ctx.message_id, step_messages=ctx.step_messages,
                    retry_message_id=ctx.retry_message_id,
                )
            except Exception as e:
                logger.error(f"[SSE] 写入 session 失败: {str(e)}")

            yield emit_done(summary_message, ctx.stages, failed_step=ctx.failed_step, step_messages=ctx.step_messages)
        finally:
            unregister_cancel(ctx.message_id)

    return stream()


async def _build_iterate_context(
    body: GenerateIterateRequest, request: Request, db,
) -> PipelineContext:
    from_step = body.fromStep
    session_id = body.sessionId

    if session_id and db is None:
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": "数据库未连接", "data": None},
        )

    existing_message_id = None
    restored_files = None
    if from_step is not None and session_id and db is not None:
        existing_message_id, restored_files = await rollback_before_retry(db, session_id, from_step or 0)

    message_id = existing_message_id or str(uuid4())
    output_session_id = session_id or f"no_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_dir = os.path.join("output", output_session_id, message_id)
    os.makedirs(output_dir, exist_ok=True)

    retry_message_id = None
    if from_step is not None and session_id and db is not None:
        await write_retry_initial_message(db, session_id, message_id, {}, [])
        retry_message_id = message_id

    return PipelineContext(
        db=db,
        session_id=session_id,
        message_id=message_id,
        output_session_id=output_session_id,
        request=request,
        component_lib="ElementUI",
        from_step=from_step,
        retry_message_id=retry_message_id,
        ai_message="代码生成完成",
    )


def _iterate_event_stream(ctx: PipelineContext, body: GenerateIterateRequest, restored_files) -> AsyncGenerator[str, None]:
    async def stream():
        register_cancel(ctx.message_id)
        stages = {}
        step_messages = []
        files = []

        try:
            yield emit_stage_start(0, "iteration", ctx.message_id, is_retry=ctx.from_step is not None)
            stage_start = time.time()

            try:
                import time as _time
                ai_service = AIServiceFactory.get_service()
                existing_files = restored_files if restored_files is not None else [f.model_dump() for f in body.files]
                result = await run_with_cancel_check(
                    ai_service.generate_vue_files(prompt=body.prompt, existing_files=existing_files, component_lib=ctx.component_lib),
                    ctx.request, task_id=ctx.message_id,
                )

                api_files = result.get("files", [])
                ai_message = result.get("message", "代码生成完成")
                files = convert_api_files_to_generated(api_files)

                if not files:
                    ai_message = "未能生成有效的代码文件，请尝试更详细的需求描述"

                duration = round(_time.time() - stage_start, 2)

                save_stage_output("iteration", 0, {
                    "prompt": body.prompt,
                    "files": [f.model_dump() for f in files],
                    "message": ai_message,
                }, ctx.output_session_id, ctx.message_id, "json")

                if api_files:
                    save_vue_files_from_json(api_files, ctx.output_session_id, 0, "iteration", ctx.message_id)

                file_path = build_file_path(ctx.output_session_id, ctx.message_id, "step0_iteration.json")
                status = "success" if files else "failed"
                stages["iteration"] = StageResult(
                    status=status, duration=duration,
                    error=None if files else "未能生成有效的代码文件",
                )
                step_messages.append({
                    "stage": 0, "stageName": "iteration", "message": None,
                    "status": status, "duration": duration,
                    "outputType": "vue", "filePath": file_path,
                })
                yield emit_stage_complete(
                    0, "iteration", status, ai_message,
                    duration=duration, output_type="vue",
                    file_path=file_path,
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
                        ctx.db, ctx.session_id, files, "用户取消了生成", 0, stages,
                        message_id=ctx.message_id, step_messages=step_messages,
                        retry_message_id=ctx.retry_message_id,
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
                        ctx.db, ctx.session_id, files, f"迭代生成失败: {str(e)}", 0, stages,
                        message_id=ctx.message_id, step_messages=step_messages,
                        retry_message_id=ctx.retry_message_id,
                    )
                except Exception as save_err:
                    logger.error(f"[SSE] 写入 session 失败: {str(save_err)}")
                return

            try:
                await update_session_with_ai_message(
                    ctx.db, ctx.session_id, files, ai_message, None, stages,
                    message_id=ctx.message_id, step_messages=step_messages,
                    retry_message_id=ctx.retry_message_id,
                )
            except Exception as e:
                logger.error(f"[SSE] 写入 session 失败: {str(e)}")

            if len(ai_message) > 200:
                ai_message = await summarize_with_minimax(ai_message)
            yield emit_done(ai_message, stages)
        finally:
            unregister_cancel(ctx.message_id)

    return stream()


# ──────────────────────────────────────────────
# Upload
# ──────────────────────────────────────────────

@router.post("/upload")
async def upload_files(files: list[UploadFile] = File(...)):
    logger.info(f"收到文件上传请求 - 文件数: {len(files)}")

    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.PARAM_ERROR, "message": "最多支持上传5个文件", "data": None},
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

        file_type = _get_file_type(file.filename or "")
        attachment = Attachment(
            id=file_id,
            url=f"/uploads/{saved_filename}",
            name=file.filename or "unknown",
            type=file_type,
            size=file_size,
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
                detail={"code": ErrorCode.PARAM_ERROR, "message": "fromStep 必须为 0、1、2 或 3", "data": None},
            )
        if not body.sessionId:
            raise HTTPException(
                status_code=400,
                detail={"code": ErrorCode.PARAM_ERROR, "message": "使用 fromStep 重试时必须提供 sessionId", "data": None},
            )

    db = get_database() if body.sessionId else None
    ctx = await _build_initial_context(body, request, db)

    if settings.MOCK_MODE:
        from app.mock.stream_mock import mock_initial_stream
        return StreamingResponse(
            mock_initial_stream(request, body, db, ctx.message_id, ctx.output_session_id, ctx.from_step, ctx.retry_message_id),
            media_type="text/event-stream",
            headers=SSE_HEADERS,
        )

    return StreamingResponse(
        _initial_event_stream(ctx, body),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


# ──────────────────────────────────────────────
# SSE stream: iterate
# ──────────────────────────────────────────────

@router.post("/generate/iterate/stream")
async def generate_iterate_stream(body: GenerateIterateRequest, request: Request):
    logger.info(f"[SSE] 收到迭代生成请求 - sessionId: {body.sessionId}, prompt长度: {len(body.prompt)}, 文件数: {len(body.files)}, fromStep: {body.fromStep}")

    from_step = body.fromStep
    if from_step is not None:
        if from_step != 0:
            raise HTTPException(
                status_code=400,
                detail={"code": ErrorCode.PARAM_ERROR, "message": "iterate 的 fromStep 仅支持 0", "data": None},
            )
        if not body.sessionId:
            raise HTTPException(
                status_code=400,
                detail={"code": ErrorCode.PARAM_ERROR, "message": "使用 fromStep 重试时必须提供 sessionId", "data": None},
            )

    db = get_database() if body.sessionId else None
    ctx = await _build_iterate_context(body, request, db)

    restored_files = None
    if from_step is not None and body.sessionId and db is not None:
        _, restored_files = await rollback_before_retry(db, body.sessionId, from_step or 0)

    if settings.MOCK_MODE:
        from app.mock.stream_mock import mock_iterate_stream
        return StreamingResponse(
            mock_iterate_stream(request, body, db, ctx.message_id, ctx.output_session_id, from_step, ctx.retry_message_id),
            media_type="text/event-stream",
            headers=SSE_HEADERS,
        )

    return StreamingResponse(
        _iterate_event_stream(ctx, body, restored_files),
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
            detail={"code": ErrorCode.PARAM_ERROR, "message": "请提供imageUrl或imageBase64", "data": None},
        )

    try:
        glm4v_service = GLM4VService()
        image_source = body.imageBase64 if body.imageBase64 else body.imageUrl
        is_base64 = body.imageBase64 is not None

        if body.prompt:
            result = await glm4v_service.analyze_image(
                image_source=image_source, prompt=body.prompt, is_base64=is_base64,
            )
            return Response(data=ImageAnalyzeResponseData(description=result, rawDescription=result, success=True))
        else:
            result = await glm4v_service.describe_for_vue_generation(
                image_source=image_source, is_base64=is_base64,
            )
            return Response(data=ImageAnalyzeResponseData(
                description=result["raw_description"], rawDescription=result["raw_description"], success=result["success"],
            ))
    except Exception as e:
        import traceback
        logger.error(f"图片分析失败: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": f"图片分析失败: {str(e)}", "data": None},
        )


@router.post("/image/analyze-file")
async def analyze_image_file(file: UploadFile = File(...), prompt: Optional[str] = Form(None)):
    logger.info(f"收到图片文件分析请求 - filename: {file.filename}")

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.PARAM_ERROR, "message": "请上传图片文件", "data": None},
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={"code": ErrorCode.PARAM_ERROR, "message": f"不支持的文件类型: {ext}", "data": None},
        )

    try:
        content = await file.read()
        image_base64 = GLM4VService.bytes_to_base64(content)
        glm4v_service = GLM4VService()

        if prompt:
            result = await glm4v_service.analyze_image(
                image_source=image_base64, prompt=prompt, is_base64=True,
            )
            return Response(data=ImageAnalyzeResponseData(description=result, rawDescription=result, success=True))
        else:
            result = await glm4v_service.describe_for_vue_generation(
                image_source=image_base64, is_base64=True,
            )
            return Response(data=ImageAnalyzeResponseData(
                description=result["raw_description"], rawDescription=result["raw_description"], success=result["success"],
            ))
    except Exception as e:
        import traceback
        logger.error(f"图片文件分析失败: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"code": ErrorCode.INTERNAL_ERROR, "message": f"图片文件分析失败: {str(e)}", "data": None},
        )


# ──────────────────────────────────────────────
# SSE stream: agent mode
# ──────────────────────────────────────────────

@router.post("/generate/agent/stream")
async def generate_agent_stream(body: GenerateInitialRequest, request: Request):
    logger.info(
        "[Agent SSE] 收到 Agent 生成请求 - sessionId: %s, componentLib: %s, prompt长度: %d",
        body.sessionId, body.componentLib, len(body.prompt),
    )

    output_session_id = body.sessionId or f"no_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    message_id = str(uuid4())
    output_dir = os.path.join("output", output_session_id, message_id)
    os.makedirs(output_dir, exist_ok=True)

    db = get_database() if body.sessionId else None

    import base64 as _base64

    attachment_info = []
    user_prompt = body.prompt or ""

    if body.attachments:
        for att in body.attachments:
            if att.type == "image":
                local_path = None
                if att.url.startswith("/uploads/"):
                    local_path = att.url[1:]
                if local_path and os.path.exists(local_path):
                    with open(local_path, "rb") as f:
                        b64 = _base64.b64encode(f.read()).decode("utf-8")
                    attachment_info.append({
                        "name": att.name,
                        "type": "image",
                        "base64": b64,
                    })
                    user_prompt += f"\n\n[附件图片: {att.name} - 可调用 analyze_image 工具分析此图片，传入 image_name=\"{att.name}\"]"
                else:
                    attachment_info.append({
                        "name": att.name,
                        "type": "image",
                        "url": att.url,
                    })
                    user_prompt += f"\n\n[附件图片: {att.name} - 可调用 analyze_image 工具分析此图片]"
            elif att.type == "markdown":
                local_path = att.url[1:] if att.url.startswith("/") else att.url
                md_content = ""
                if os.path.exists(local_path):
                    with open(local_path, "r", encoding="utf-8") as f:
                        md_content = f.read()
                attachment_info.append({
                    "name": att.name,
                    "type": "markdown",
                    "content": md_content,
                })
                if md_content:
                    user_prompt += f"\n\n[附件文档: {att.name}]\n{md_content}"

    tool_registry = create_tool_registry(
        component_lib=body.componentLib,
        output_session_id=output_session_id,
        message_id=message_id,
        request=request,
        attachments=attachment_info if attachment_info else None,
    )

    agent = AgentCore(
        tool_registry=tool_registry,
        component_lib=body.componentLib,
    )

    async def event_stream():
        register_cancel(message_id)
        try:
            all_files: list[GeneratedFile] = []
            step_messages: list[dict] = []

            _HEARTBEAT_INTERVAL = 30
            _DONE = object()
            _HEARTBEAT = ": ping\n\n"
            queue: asyncio.Queue[object] = asyncio.Queue()

            async def feed_agent():
                try:
                    async for event in agent.run(
                        user_prompt=user_prompt,
                        task_id=message_id,
                        output_session_id=output_session_id,
                        message_id=message_id,
                    ):
                        await queue.put(event)
                finally:
                    await queue.put(_DONE)

            async def send_heartbeat():
                while True:
                    await asyncio.sleep(_HEARTBEAT_INTERVAL)
                    await queue.put(_HEARTBEAT)

            agent_task = asyncio.create_task(feed_agent())
            hb_task = asyncio.create_task(send_heartbeat())

            try:
                while True:
                    item = await queue.get()
                    if item is _DONE:
                        break
                    yield item
            finally:
                hb_task.cancel()
                agent_task.cancel()

            vue_file_urls = _scan_latest_vue_files(output_dir)
            if vue_file_urls:
                yield emit_agent_files(vue_file_urls)

            all_files = _load_final_files_as_generated(output_dir)

            step_messages.append({
                "stage": 0,
                "stageName": "agent",
                "message": "Agent 执行完成",
                "status": "success",
            })

            if db and body.sessionId:
                try:
                    await update_session_with_ai_message(
                        db=db,
                        session_id=body.sessionId,
                        files=all_files,
                        ai_message="Agent 模式生成完成",
                        failed_step=None,
                        stages={"agent": StageResult(status="success")},
                        message_id=message_id,
                        step_messages=step_messages,
                    )
                except Exception as e:
                    logger.error("[Agent SSE] 写入 session 失败: %s", str(e))

        except Exception as e:
            logger.error("[Agent SSE] Agent 执行异常: %s", str(e), exc_info=True)
            yield emit_error(
                code=ErrorCode.INTERNAL_ERROR,
                message=f"Agent 执行异常: {str(e)}",
                failed_step=None,
                stages={},
            )
        finally:
            unregister_cancel(message_id)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )
