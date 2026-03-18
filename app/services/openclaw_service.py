import httpx
import json
import logging
import re
from app.config import settings
from app.utils.json_helper import parse_json_with_repair

logger = logging.getLogger(__name__)


class OpenclawService:
    def __init__(self):
        self.api_url = settings.OPENCLAW_API_URL
        self.token = settings.OPENCLAW_TOKEN
        self.agent_id = settings.OPENCLAW_AGENT_ID
        self.model = settings.OPENCLAW_MODEL
    
    async def generate_vue_files(
        self,
        prompt: str,
        ccui_prompt: str = ""
    ) -> dict:
        final_prompt = f"{ccui_prompt}\n\n{prompt}" if ccui_prompt else prompt
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "x-openclaw-agent-id": self.agent_id
        }
        
        payload = {
            "model": self.model,
            "input": final_prompt
        }
        
        logger.info(f"调用 Openclaw API - URL: {self.api_url}, Agent: {self.agent_id}")
        
        async with httpx.AsyncClient(timeout=3000.0) as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Openclaw API 错误: {response.status_code} - {response.text}")
                raise Exception(f"Openclaw API 调用失败: {response.status_code}")
            
            result = response.json()
            logger.info(f"Openclaw API 响应成功")
            
            return self._parse_response(result)
    
    def _parse_response(self, response: dict) -> dict:
        content = ""
        output = response.get("output", [])
        if isinstance(output, list) and len(output) > 0:
            message = output[0]
            if isinstance(message, dict):
                message_content = message.get("content", [])
                if isinstance(message_content, list) and len(message_content) > 0:
                    content = message_content[0].get("text", "")
        
        if not content:
            content = response.get("content", "") or response.get("response", "")
        
        if not content:
            logger.warning("Openclaw 返回空内容")
            return {"files": [], "message": "生成失败：API返回空内容"}
        
        if isinstance(content, str):
            content = content.strip()
        
        # 使用通用的JSON解析和修复工具
        parsed, error = parse_json_with_repair(content)
        
        if error or parsed is None:
            logger.error(f"解析 Openclaw 响应失败: {error}")
            # 如果解析失败，将原始内容作为单个文件返回
            return {
                "files": [{
                    "id": "main-page",
                    "name": "MainPage.vue",
                    "path": "/src/MainPage.vue",
                    "type": "file",
                    "language": "vue",
                    "content": content if isinstance(content, str) else str(content)
                }],
                "message": "生成完成（原始格式）"
            }
        
        files = parsed.get("files", [])
        message = parsed.get("message", "代码生成完成")
        
        return {"files": files, "message": message}
