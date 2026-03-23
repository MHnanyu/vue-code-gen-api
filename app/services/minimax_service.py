import json
import logging
import re
from typing import AsyncIterator, Optional, Dict, Any
import httpx

from app.config import settings
from app.services.ai_service import AIService
from app.utils.json_helper import parse_json_with_repair

logger = logging.getLogger(__name__)


async def summarize_with_minimax(content: str, max_length: int = 200) -> str:
    try:
        service = MiniMaxService()
        prompt = f"""请将以下内容简洁概括为一段话，不超过{max_length}字。
要求：
1. 保留关键信息（处理了什么、生成了什么、优化了什么）
2. 省略具体的技术细节（如CSS类名、行号等）
3. 用简洁的中文表述

原始内容：
{content}"""
        result = await service.generate_text(prompt=prompt, temperature=0.3)
        summarized = result.strip()
        if len(summarized) > max_length * 1.5:
            summarized = summarized[:max_length] + "..."
        return summarized
    except Exception as e:
        logger.warning(f"MiniMax摘要失败，使用原始内容: {str(e)}")
        return content


class MiniMaxService(AIService):
    def __init__(self):
        self.api_key = settings.MINIMAX_API_KEY
        self.api_url = settings.MINIMAX_API_URL
        self.model = settings.MINIMAX_MODEL
    
    async def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 1.0,
        stream: bool = False,
        response_format: Optional[Dict[str, str]] = None
    ) -> AsyncIterator[str]:
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        system_message = None
        filtered_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                filtered_messages.append(msg)
        
        payload = {
            "model": self.model,
            "messages": filtered_messages,
            "max_tokens": 4096,
        }
        
        if system_message:
            payload["system"] = system_message
        
        if stream:
            payload["stream"] = True
        
        async with httpx.AsyncClient(timeout=3000.0) as client:
            if stream:
                async with client.stream(
                    "POST",
                    f"{self.api_url}/v1/messages",
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
                                if data.get("type") == "content_block_delta":
                                    delta = data.get("delta", {})
                                    if delta.get("type") == "text_delta":
                                        content = delta.get("text", "")
                                        if content:
                                            yield content
                            except json.JSONDecodeError:
                                continue
            else:
                response = await client.post(
                    f"{self.api_url}/v1/messages",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                if "content" in data and len(data["content"]) > 0:
                    for block in data["content"]:
                        if block.get("type") == "text":
                            yield block.get("text", "")
    
    async def generate_vue_files(
        self,
        prompt: str,
        existing_files: Optional[list[dict]] = None
    ) -> dict:
        if existing_files:
            system_message = """你是Vue3前端原型图优化助手，目标是修改可预览的UI原型。

【输出格式 - 必须严格遵守】
直接输出纯JSON，不要有任何前缀说明、后缀解释或markdown标记。
不要输出 "我来帮你..." 等任何额外文字，直接以 { 开始，以 } 结束。

返回格式示例：
{"files":[{"id":"xxx","name":"xxx","path":"xxx","type":"file","language":"vue","content":"代码内容"}],"message":"简短说明"}

【重要规则】
1. 输入N个文件，必须输出N个文件，保持一对一映射
2. 每个输出文件的id、name、path必须与输入完全一致
3. 即使文件不需要修改，也必须包含（保持原样）
4. 保持原型极简原则：mock数据即可，不需要真实逻辑
5. 每个文件代码不超过 300 行

【技术栈】
Vue 3 Composition API (<script setup lang="ts">) + Element Plus + Tailwind CSS

【特别注意】
- content 字段中的代码必须正确转义：双引号用 \"，换行用 \n"""
            
            files_context = "\n\n".join([
                f"--- 文件: {f.get('name', 'unknown')} (id: {f.get('id', 'unknown')}) ---\n{f.get('content', '')}"
                for f in existing_files
            ])
            user_message = f"现有代码文件：\n{files_context}\n\n修改需求：{prompt}"
        else:
            system_message = """你是Vue3前端原型图生成助手，目标是生成可预览的UI原型，而非生产代码。

【输出格式 - 必须严格遵守】
直接输出纯JSON，不要有任何前缀说明、后缀解释或markdown标记。
不要输出 "我来帮你..." 等任何额外文字，直接以 { 开始，以 } 结束。

返回格式示例：
{"files":[{"id":"main-page","name":"MainPage.vue","path":"/src/MainPage.vue","type":"file","language":"vue","content":"代码内容"}],"message":"简短说明"}

【生成规则 - 极简原型原则】
1. 尽量只生成 MainPage.vue 一个文件，除非页面确实复杂需要拆分（最多3个文件）
2. template 部分：用 Element Plus 组件 + Tailwind CSS 实现布局和样式，包含完整的UI元素
3. script 部分：极简化，使用硬编码的 mock 数据，不需要 API 调用、表单验证、computed、watch 等逻辑
4. 不要定义 interface/type，不需要复杂的 TypeScript 类型
5. 不要生成 main.ts, App.vue, index.html 等配置文件
6. 每个文件代码不超过 300 行

【技术栈】
Vue 3 Composition API (<script setup lang="ts">) + Element Plus + Tailwind CSS

【特别注意】
- content 字段中的代码必须正确转义：双引号用 \"，换行用 \n
- 这是原型图，重点在于组件位置正确、布局合理、基础样式到位，不需要真实交互逻辑"""
            user_message = prompt
        
        messages = [
            {"role": "user", "content": user_message}
        ]
        
        result = ""
        async for chunk in self.chat_completion(
            messages,
            temperature=0.7,
            stream=False
        ):
            result += chunk
        
        json_match = re.search(r'\{[\s\S]*\}', result)
        json_str = json_match.group(0) if json_match else result
        
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
