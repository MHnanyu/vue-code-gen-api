import json
import logging
import re
from typing import AsyncIterator, Optional, Dict, Any
import httpx

from app.config import settings
from app.services.ai_service import AIService
from app.utils.json_helper import parse_json_with_repair

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
        
        async with httpx.AsyncClient(timeout=3000.0) as client:
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
        if existing_files:
            system_message = """你是Vue3前端代码优化助手。

【输出格式 - 必须严格遵守】
直接输出纯JSON，不要有任何前缀说明、后缀解释或markdown标记。
不要输出 "我来帮你..." 等任何额外文字，直接以 { 开始，以 } 结束。

返回格式示例：
{"files":[{"id":"xxx","name":"xxx","path":"xxx","type":"file","language":"vue","content":"代码内容"}],"message":"简短说明"}

【重要规则】
1. 输入N个文件，必须输出N个文件，保持一对一映射
2. 每个输出文件的id、name、path必须与输入完全一致
3. 即使文件不需要修改，也必须包含（保持原样）

【技术栈】
Vue 3 Composition API (<script setup lang="ts">) + TypeScript + Element Plus + Tailwind CSS"""
            
            files_context = "\n\n".join([
                f"--- 文件: {f.get('name', 'unknown')} (id: {f.get('id', 'unknown')}) ---\n{f.get('content', '')}"
                for f in existing_files
            ])
            user_message = f"现有代码文件：\n{files_context}\n\n修改需求：{prompt}"
        else:
            system_message = """你是Vue3前端开发助手。

【输出格式 - 必须严格遵守】
直接输出纯JSON，不要有任何前缀说明、后缀解释或markdown标记。
不要输出 "我来帮你..." 等任何额外文字，直接以 { 开始，以 } 结束。

返回格式示例：
{"files":[{"id":"main-page","name":"MainPage.vue","path":"/src/MainPage.vue","type":"file","language":"vue","content":"代码内容"}],"message":"简短说明"}

【生成规则】
1. 只生成必要的Vue组件（MainPage.vue及自定义组件）
2. 不要生成 main.ts, App.vue, index.html 等配置文件

【技术栈】
Vue 3 Composition API (<script setup lang="ts">) + TypeScript + Element Plus + Tailwind CSS"""
            user_message = prompt
        
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
        
        json_match = re.search(r'\{[\s\S]*\}', result)
        json_str = json_match.group(0) if json_match else result
        
        # 使用通用的JSON解析和修复工具
        data, error = parse_json_with_repair(json_str)
        
        if error or data is None:
            logger.error(f"JSON解析失败 - error: {error}, 原始输出: {result[:500]}")
            return {
                "files": [],
                "message": f"JSON解析失败。原始输出：{result}"
            }
        
        if "files" not in data:
            logger.error(f"AI返回格式错误 - 缺少files字段。原始输出: {result[:500]}")
            return {
                "files": [],
                "message": f"返回格式错误。原始输出：{result}"
            }
        
        return data
