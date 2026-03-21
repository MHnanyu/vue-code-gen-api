import asyncio
import logging
from typing import Optional

from fastapi import Request

logger = logging.getLogger(__name__)


class ClientDisconnectedError(Exception):
    pass


class GenerationCancelledError(Exception):
    pass


_cancel_events: dict[str, asyncio.Event] = {}


def register_cancel(task_id: str) -> asyncio.Event:
    event = asyncio.Event()
    _cancel_events[task_id] = event
    logger.info(f"[Cancel] 注册取消监听 - taskId: {task_id}")
    return event


def unregister_cancel(task_id: str):
    _cancel_events.pop(task_id, None)


def set_cancel(task_id: str):
    event = _cancel_events.get(task_id)
    if event:
        event.set()
        logger.info(f"[Cancel] 触发取消 - taskId: {task_id}")


def is_cancelled(task_id: str) -> bool:
    event = _cancel_events.get(task_id)
    return event is not None and event.is_set()


async def run_with_cancel_check(
    coro,
    request: Request,
    task_id: Optional[str] = None,
    poll_interval: float = 0.5,
):
    task = asyncio.create_task(coro)
    try:
        while not task.done():
            if await request.is_disconnected():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                logger.info("客户端已断开连接，取消生成任务")
                raise ClientDisconnectedError()
            if task_id and is_cancelled(task_id):
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                logger.info(f"用户取消生成任务 - taskId: {task_id}")
                raise GenerationCancelledError()
            await asyncio.sleep(poll_interval)
        return await task
    except asyncio.CancelledError:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        raise ClientDisconnectedError()
