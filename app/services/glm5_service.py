import json
import logging
from typing import AsyncIterator, Optional, Dict, Any
import httpx

from app.config import settings
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class GLM5Service(AIService):
    def __init__(self):
        self.api_key = settings.GLM5_API_KEY
        self.api_url = settings.GLM5_API_URL
        self.model = settings.GLM5_MODEL
    
    async def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 1.0,
        stream: bool = False,
        response_format: Optional[Dict[str, str]] = None
    ) -> AsyncIterator[str]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        async with httpx.AsyncClient(timeout=600.0) as client:
            if stream:
                async with client.stream(
                    "POST",
                    self.api_url,
                    headers=headers,
                    json=payload
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        yield content
                            except json.JSONDecodeError:
                                continue
            else:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    yield data["choices"][0]["message"]["content"]
    
    async def generate_vue_files(
        self,
        prompt: str,
        existing_files: Optional[list[dict]] = None
    ) -> dict:
        system_message = """你是一个Vue3前端开发助手。根据用户需求生成Vue3组件代码。

生成规则：
1. 只生成必要的Vue组件文件（MainPage.vue及其他自定义组件）
2. 不要生成 main.ts, App.vue, index.html 等配置文件

技术栈：
- Vue 3 Composition API (<script setup lang="ts">)
- TypeScript
- Element Plus (el-开头组件)
- Tailwind CSS (class样式)

返回JSON格式：
{
  "files": [
    {
      "id": "main-page",
      "name": "MainPage.vue",
      "path": "/src/MainPage.vue",
      "type": "file",
      "language": "vue",
      "content": "<template>...</template><script setup lang=\"ts\">...</script><style scoped>...</style>"
    }
  ],
  "message": "生成说明"
}"""

        user_message = prompt
        if existing_files:
            files_context = "\n\n".join([
                f"文件: {f.get('name', 'unknown')}\n{f.get('content', '')}"
                for f in existing_files[:2]
            ])
            user_message = f"已有代码：\n{files_context}\n\n修改需求：{prompt}"
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        result = ""
        async for chunk in self.chat_completion(
            messages,
            temperature=0.7,
            stream=False,
            response_format={"type": "json_object"}
        ):
            result += chunk
        
        try:
            data = json.loads(result)
            if "files" not in data:
                logger.error(f"AI返回格式错误 - 缺少files字段。原始输出: {result[:500]}")
                return {
                    "files": [],
                    "message": f"返回格式错误。原始输出：{result}"
                }
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败 - error: {e}, 原始输出: {result[:500]}")
            return {
                "files": [],
                "message": f"JSON解析失败。原始输出：{result}"
            }
