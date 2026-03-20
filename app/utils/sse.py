import json
from datetime import datetime, timezone


def sse_event(event_type: str, data: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def make_preview(content: str | None, max_length: int = 500) -> str | None:
    if not content:
        return None
    if len(content) <= max_length:
        return content
    return content[:max_length] + "\n...(截断)"
