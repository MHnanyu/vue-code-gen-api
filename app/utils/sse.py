import json
from datetime import datetime, timezone
from typing import Any

from app.schemas.generate import StageResult


def _sse_event(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    message: str,
    stages: dict[str, StageResult],
    failed_step: int | None = None,
    step_messages: list[dict] | None = None,
) -> str:
    data: dict[str, Any] = {
        "message": message,
        "stages": _dump_stages(stages),
        "failedStep": failed_step,
        "timestamp": _now_iso(),
    }
    if step_messages is not None:
        data["stepMessages"] = step_messages
    return _sse_event("done", data)


def emit_agent_thinking(content: str, step: int, task_id: str | None = None) -> str:
    data: dict[str, Any] = {
        "content": content,
        "step": step,
        "timestamp": _now_iso(),
    }
    if task_id is not None:
        data["taskId"] = task_id
    return _sse_event("agent_thinking", data)


def emit_tool_call_start(
    tool_name: str,
    arguments: str,
    step: int,
) -> str:
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
    output_info: tuple[list[str], str] | None = None,
) -> str:
    data: dict[str, Any] = {
        "toolName": tool_name,
        "result": result,
        "step": step,
        "timestamp": _now_iso(),
    }
    if output_info is not None:
        urls, output_type = output_info
        data["outputUrls"] = urls
        data["outputType"] = output_type
    return _sse_event("tool_call_result", data)


def emit_agent_done(files: list | None = None) -> str:
    data: dict[str, Any] = {"timestamp": _now_iso()}
    if files:
        data["files"] = files
    return _sse_event("agent_done", data)


def emit_agent_cancelled(cancelled_at_step: int) -> str:
    return _sse_event("agent_cancelled", {
        "cancelledAtStep": cancelled_at_step,
        "timestamp": _now_iso(),
    })


def emit_agent_files(files: list[dict]) -> str:
    return _sse_event("agent_files", {
        "files": files,
        "timestamp": _now_iso(),
    })
