import json
import logging
import os
import shutil
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException

from app.schemas.response import ErrorCode
from app.schemas.generate import GeneratedFile

logger = logging.getLogger(__name__)


def load_stage_output(
    step_number: int,
    stage_name: str,
    session_id: str,
    file_extension: str = "md"
):
    filename = f"step{step_number}_{stage_name}.{file_extension}"

    def _load(filepath):
        try:
            if file_extension == "json":
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                with open(filepath, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception as e:
            logger.error(f"加载步骤缓存失败 {filepath}: {str(e)}")
            return None

    flat_path = os.path.join("output", session_id, filename)
    if os.path.exists(flat_path):
        return _load(flat_path)

    session_output_dir = os.path.join("output", session_id)
    if os.path.isdir(session_output_dir):
        latest_path = None
        latest_mtime = 0
        for entry in os.listdir(session_output_dir):
            entry_path = os.path.join(session_output_dir, entry)
            if os.path.isdir(entry_path):
                candidate = os.path.join(entry_path, filename)
                if os.path.exists(candidate):
                    mtime = os.path.getmtime(candidate)
                    if mtime > latest_mtime:
                        latest_mtime = mtime
                        latest_path = candidate
        if latest_path:
            return _load(latest_path)

    return None


def save_stage_output(
    stage_name: str,
    step_number: int,
    content,
    session_id: str | None = None,
    message_id: str | None = None,
    file_extension: str = "md"
) -> str | None:
    output_dir = "output"
    if session_id and message_id:
        output_dir = os.path.join(output_dir, session_id, message_id)
    elif session_id:
        output_dir = os.path.join(output_dir, session_id)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if session_id:
        filename = f"step{step_number}_{stage_name}.{file_extension}"
    else:
        filename = f"step{step_number}_{stage_name}_{timestamp}.{file_extension}"

    filepath = os.path.join(output_dir, filename)

    try:
        if file_extension == "json":
            with open(filepath, "w", encoding="utf-8") as f:
                if isinstance(content, (dict, list)):
                    json.dump(content, f, ensure_ascii=False, indent=2)
                else:
                    f.write(str(content))
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(content))

        logger.info(f"已保存阶段{step_number}输出到: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"保存阶段{step_number}输出失败: {str(e)}")
        return None


def save_vue_files_from_json(
    files_data: list[dict],
    session_id: str,
    step_number: int,
    stage_name: str,
    message_id: str | None = None
) -> list[str]:
    if not files_data:
        return []

    if message_id:
        output_dir = os.path.join("output", session_id, message_id, f"step{step_number}_{stage_name}_vue")
    else:
        output_dir = os.path.join("output", session_id, f"step{step_number}_{stage_name}_vue")
    os.makedirs(output_dir, exist_ok=True)

    saved_files = []
    used_names = set()

    for idx, file_data in enumerate(files_data):
        file_name = file_data.get("name", f"file{idx}.vue")

        base_name = file_name
        if base_name in used_names:
            name_without_ext = os.path.splitext(file_name)[0]
            ext = os.path.splitext(file_name)[1]
            counter = 1
            while f"{name_without_ext}_{counter}{ext}" in used_names:
                counter += 1
            file_name = f"{name_without_ext}_{counter}{ext}"

        used_names.add(file_name)

        file_path = os.path.join(output_dir, file_name)

        content = file_data.get("content", "")

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            saved_files.append(file_path)
            logger.info(f"已保存Vue文件: {file_path}")
        except Exception as e:
            logger.error(f"保存Vue文件失败 {file_name}: {str(e)}")

    return saved_files


def build_file_path(session_id: str, message_id: str, filename: str) -> str:
    return f"output/{session_id}/{message_id}/{filename}"


def build_step_summary(step_messages: list[dict]) -> str:
    if not step_messages:
        return "生成完成"
    parts = []
    for sm in step_messages:
        if sm.get("status") == "failed":
            parts.append(f"{sm.get('message', '失败')}")
        elif sm.get("status") == "skipped":
            continue
        else:
            parts.append(sm.get("message", ""))
    if not parts:
        return "生成完成"
    return "，".join(parts) + "。"


async def update_session_with_ai_message(
    db,
    session_id: str | None,
    files: list[GeneratedFile],
    ai_message: str,
    failed_step: int | None,
    stages: dict,
    message_id: str | None = None,
    step_messages: list[dict] | None = None,
    retry_message_id: str | None = None,
):
    if session_id is None or db is None:
        return

    from app.schemas.session import Message

    now = datetime.utcnow()
    stage_dump = {k: v.model_dump() if hasattr(v, "model_dump") else v for k, v in stages.items()} if stages else None
    files_dump = [f.model_dump() for f in files]

    if retry_message_id:
        update_result = await db.sessions.update_one(
            {"id": session_id, "messages.id": retry_message_id},
            {
                "$set": {
                    "messages.$.content": ai_message,
                    "messages.$.failedStep": failed_step,
                    "messages.$.stages": stage_dump,
                    "messages.$.stepMessages": step_messages,
                    "messages.$.files": files_dump if files_dump else None,
                    "updatedAt": now,
                    "files": files_dump,
                }
            }
        )
        log_id = retry_message_id
    else:
        ai_msg = Message(
            id=message_id or str(uuid4()),
            role="assistant",
            content=ai_message,
            failedStep=failed_step,
            stages=stage_dump,
            stepMessages=step_messages,
            files=files_dump if files_dump else None,
        )

        update_result = await db.sessions.update_one(
            {"id": session_id},
            {
                "$push": {"messages": ai_msg.model_dump()},
                "$set": {
                    "updatedAt": now,
                    "files": files_dump,
                }
            }
        )
        log_id = ai_msg.id

    if update_result.matched_count == 0:
        logger.error(f"会话不存在 - sessionId: {session_id}")
        raise HTTPException(
            status_code=404,
            detail={"code": ErrorCode.SESSION_NOT_FOUND, "message": "会话不存在", "data": None}
        )

    logger.info(f"会话更新成功（含AI消息）- sessionId: {session_id}, failedStep: {failed_step}, messageId: {log_id}")


async def upsert_session_message(
    db,
    session_id: str,
    message_id: str,
    content: str,
    files: list[dict] | None = None,
    tool_calls: list[dict] | None = None,
    failed_step: int | None = None,
    stages: dict | None = None,
    step_messages: list[dict] | None = None,
):
    """Insert a message on first call, then update in-place on subsequent calls.

    Used for agent mode real-time step persistence: the message is created when
    the first tool completes and updated as more steps finish, avoiding duplicate
    messages on crash-recovery restarts.
    """
    if session_id is None or db is None:
        return

    from app.schemas.session import Message

    now = datetime.utcnow()
    stage_dump = {k: v.model_dump() if hasattr(v, "model_dump") else v for k, v in stages.items()} if stages else None

    existing = await db.sessions.find_one(
        {"id": session_id, "messages.id": message_id},
        {"messages.$": 1},
    )

    if existing:
        update_fields = {
            "messages.$.content": content,
            "messages.$.failedStep": failed_step,
            "messages.$.toolCalls": tool_calls,
            "updatedAt": now,
        }
        if stage_dump is not None:
            update_fields["messages.$.stages"] = stage_dump
        if step_messages is not None:
            update_fields["messages.$.stepMessages"] = step_messages
        if files is not None:
            update_fields["files"] = files
        await db.sessions.update_one(
            {"id": session_id, "messages.id": message_id},
            {"$set": update_fields},
        )
    else:
        ai_msg = Message(
            id=message_id,
            role="assistant",
            content=content,
            failedStep=failed_step,
            stages=stage_dump,
            stepMessages=step_messages,
            toolCalls=tool_calls,
            files=files,
        )
        push_fields: dict = {"messages": ai_msg.model_dump()}
        set_fields: dict = {"updatedAt": now}
        if files is not None:
            set_fields["files"] = files
        await db.sessions.update_one(
            {"id": session_id},
            {"$push": push_fields, "$set": set_fields},
        )

    logger.info(
        "Agent 步骤落表 - sessionId: %s, messageId: %s, toolCalls: %d",
        session_id, message_id, len(tool_calls) if tool_calls else 0,
    )


def _delete_stage_files(output_dir: str, step: int):
    step_files = {
        0: ["step0_final_prompt.md"],
        1: ["step1_requirement.md"],
        2: ["step2_generation.json", "step2_generation_vue"],
        3: ["step3_optimization.json", "step3_optimization_vue"],
    }
    for s in range(step, 4):
        for filename in step_files.get(s, []):
            filepath = os.path.join(output_dir, filename)
            if os.path.isdir(filepath):
                shutil.rmtree(filepath, ignore_errors=True)
                logger.info(f"已清理产物目录: {filepath}")
            elif os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"已清理产物文件: {filepath}")


async def rollback_before_retry(db, session_id: str, from_step: int = 0) -> tuple[str | None, list[dict] | None]:
    if session_id is None or db is None:
        return None, None

    session = await db.sessions.find_one({"id": session_id})
    if not session:
        return None, None

    messages = session.get("messages", [])
    if not messages:
        return None, None

    last_ai_idx = None
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "assistant":
            last_ai_idx = i
            break

    if last_ai_idx is None:
        return None, None

    last_ai_msg = messages[last_ai_idx]
    failed_message_id = last_ai_msg.get("id")

    messages.pop(last_ai_idx)

    restored_files: list[dict] = []
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].get("role") == "assistant":
            prev_files = messages[i].get("files")
            if prev_files is not None:
                restored_files = prev_files
            break

    now = datetime.utcnow()
    await db.sessions.update_one(
        {"id": session_id},
        {
            "$set": {
                "messages": messages,
                "files": restored_files,
                "updatedAt": now,
            }
        }
    )

    logger.info(f"重试回滚完成 - sessionId: {session_id}, 移除消息: {failed_message_id}, 恢复文件数: {len(restored_files)}")

    if failed_message_id:
        output_dir = os.path.join("output", session_id, failed_message_id)
        _delete_stage_files(output_dir, from_step)

    return failed_message_id, restored_files if restored_files else None


async def write_retry_initial_message(
    db,
    session_id: str,
    message_id: str,
    stages: dict,
    step_messages: list[dict],
):
    if session_id is None or db is None:
        return

    from app.schemas.session import Message

    now = datetime.utcnow()
    stage_dump = {k: v.model_dump() if hasattr(v, "model_dump") else v for k, v in stages.items()} if stages else None
    msg = Message(
        id=message_id,
        role="assistant",
        content="正在重试...",
        failedStep=None,
        stages=stage_dump,
        stepMessages=step_messages,
        files=None,
    )

    await db.sessions.update_one(
        {"id": session_id},
        {
            "$push": {"messages": msg.model_dump()},
            "$set": {"updatedAt": now},
        }
    )
    logger.info(f"重试初始消息已写入 - sessionId: {session_id}, messageId: {message_id}, 缓存步骤数: {len(step_messages)}")
