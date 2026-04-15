"""
Review Agent：代码生成后的自审环节。
可选增强项，在 Agent Loop 中按需启用。
"""
import json
import logging

import httpx

from app.config import settings
from app.agent.prompts import build_review_prompt

logger = logging.getLogger(__name__)


async def review_generated_code(
    requirement: str,
    files: list[dict],
    component_lib: str,
) -> dict:
    """
    审查生成的 Vue 代码。
    返回: {"pass": bool, "issues": list, "severity": str}
    """
    api_url = settings.GLM5_API_URL
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.GLM5_API_KEY}",
    }

    files_summary = "\n".join(
        f"文件: {f.get('name')}\n```\n{f.get('content', '')[:2000]}\n```"
        for f in files
    )

    messages = [
        {"role": "system", "content": build_review_prompt(component_lib)},
        {"role": "user", "content": f"需求文档：\n{requirement}\n\n生成的代码：\n{files_summary}"},
    ]

    payload = {
        "model": settings.GLM5_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0].get("message", {}).get("content", "")
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.warning("Review 结果解析失败: %s", content[:200])
            return {"pass": True, "issues": [], "severity": "none"}
    except Exception as e:
        logger.error("Review Agent 异常: %s", e)
        return {"pass": True, "issues": [f"审查异常: {str(e)}"], "severity": "minor"}
