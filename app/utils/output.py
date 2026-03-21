import json
import logging
import os
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
    step_messages: list[dict] | None = None
):
    if session_id is None or db is None:
        return

    from app.schemas.session import Message

    now = datetime.utcnow()
    ai_msg = Message(
        id=message_id or str(uuid4()),
        role="assistant",
        content=ai_message,
        failedStep=failed_step,
        stages={k: v.model_dump() if hasattr(v, "model_dump") else v for k, v in stages.items()} if stages else None,
        stepMessages=step_messages
    )

    update_result = await db.sessions.update_one(
        {"id": session_id},
        {
            "$push": {"messages": ai_msg.model_dump()},
            "$set": {
                "updatedAt": now,
                "files": [f.model_dump() for f in files]
            }
        }
    )

    if update_result.matched_count == 0:
        logger.error(f"会话不存在 - sessionId: {session_id}")
        raise HTTPException(
            status_code=404,
            detail={"code": ErrorCode.SESSION_NOT_FOUND, "message": "会话不存在", "data": None}
        )

    logger.info(f"会话更新成功（含AI消息）- sessionId: {session_id}, failedStep: {failed_step}, messageId: {ai_msg.id}")
