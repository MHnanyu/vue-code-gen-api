import json
from datetime import datetime, timezone
from typing import Any

from app.schemas.generate import GeneratedFile, StageResult


def _sse_event(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_preview(content: str | None, max_length: int = 500) -> str | None:
    if not content:
        return None
    if len(content) <= max_length:
        return content
    return content[:max_length] + "\n...(截断)"


def _dump_stages(stages: dict[str, StageResult]) -> dict[str, Any]:
    return {k: v.model_dump() for k, v in stages.items()}


def emit_stage_start(
    stage: int,
    stage_name: str,
    task_id: str,
    is_retry: bool = False,
) -> str:
    return _sse_event("stage_start", {
        "stage": stage,
        "stageName": stage_name,
        "isRetry": is_retry,
        "taskId": task_id,
        "timestamp": _now_iso(),
    })


def emit_stage_progress(
    stage: int,
    stage_name: str,
    message: str,
    progress: int | None = None,
) -> str:
    data: dict[str, Any] = {
        "stage": stage,
        "stageName": stage_name,
        "message": message,
        "timestamp": _now_iso(),
    }
    if progress is not None:
        data["progress"] = progress
    return _sse_event("stage_progress", data)


def emit_stage_complete(
    stage: int,
    stage_name: str,
    status: str,
    message: str | None = None,
    duration: float | None = None,
    output_type: str | None = None,
    file_path: str | None = None,
    vue_dir_path: str | None = None,
    output_preview: str | None = None,
    files: list[GeneratedFile] | None = None,
    error: str | None = None,
) -> str:
    data: dict[str, Any] = {
        "stage": stage,
        "stageName": stage_name,
        "status": status,
        "timestamp": _now_iso(),
    }
    if message is not None:
        data["message"] = message
    if duration is not None:
        data["duration"] = duration
    if output_type is not None:
        data["outputType"] = output_type
    if file_path is not None:
        data["filePath"] = file_path
    if vue_dir_path is not None:
        data["vueDirPath"] = vue_dir_path
    if output_preview is not None:
        data["outputPreview"] = output_preview
    if files is not None:
        data["files"] = [f.model_dump() for f in files]
    if error is not None:
        data["error"] = error
    return _sse_event("stage_complete", data)


def emit_error(
    code: int,
    message: str,
    failed_step: int | None,
    stages: dict[str, StageResult],
) -> str:
    return _sse_event("error", {
        "code": code,
        "message": message,
        "failedStep": failed_step,
        "stages": _dump_stages(stages),
        "timestamp": _now_iso(),
    })


def emit_cancelled(
    cancelled_at_step: int | None,
    stages: dict[str, StageResult],
) -> str:
    return _sse_event("cancelled", {
        "cancelledAtStep": cancelled_at_step,
        "stages": _dump_stages(stages),
        "timestamp": _now_iso(),
    })


def emit_done(
    files: list[GeneratedFile],
    message: str,
    stages: dict[str, StageResult],
    failed_step: int | None = None,
    step_messages: list[dict] | None = None,
) -> str:
    data: dict[str, Any] = {
        "files": [f.model_dump() for f in files],
        "message": message,
        "stages": _dump_stages(stages),
        "failedStep": failed_step,
        "timestamp": _now_iso(),
    }
    if step_messages is not None:
        data["stepMessages"] = step_messages
    return _sse_event("done", data)
