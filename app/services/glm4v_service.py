import json
import logging
import base64
from typing import AsyncIterator, Optional, Dict, Any, List
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class GLM4VService:
    def __init__(self):
        self.api_key = settings.GLM4V_API_KEY
        self.api_url = settings.GLM4V_API_URL
        self.model = settings.GLM4V_MODEL
    
    async def analyze_image(
        self,
        image_source: str,
        prompt: str,
        is_base64: bool = False,
        stream: bool = False
    ) -> str:
        messages = self._build_image_message(image_source, prompt, is_base64)
        
        result = ""
        async for chunk in self._chat_completion(messages, stream=stream):
            result += chunk
        
        return result
    
    async def analyze_images(
        self,
        image_sources: List[str],
        prompt: str,
        are_base64: bool = False
    ) -> str:
        content = []

        for source in image_sources:
            url = self._format_image_url(source, are_base64)
            content.append({
                "type": "image_url",
                "image_url": {"url": url}
            })
        
        content.append({"type": "text", "text": prompt})
        
        messages = [{"role": "user", "content": content}]
        
        result = ""
        async for chunk in self._chat_completion(messages, stream=False):
            result += chunk
        
        return result
    
    async def describe_for_vue_generation(
        self,
        image_source: str,
        is_base64: bool = False
    ) -> Dict[str, Any]:
        prompt = self._build_vue_description_prompt()
        
        result = await self.analyze_image(image_source, prompt, is_base64)
        
        return self._parse_vue_description(result)
    
    def _build_vue_description_prompt(self) -> str:
        return """你是一个页面布局分析助手。请分析这张UI设计图/网页截图，仅提取页面的**布局结构和视觉风格**，作为后续页面生成的参考。

【分析重点】
1. 页面整体区域划分（如顶部导航、左侧边栏、右侧内容区等）
2. 各区域内包含的UI组件类型（如表格、表单、搜索栏、图表、卡片列表等）
3. 组件的大致排列方式（横向/纵向、分栏数量等）
4. 页面整体视觉风格（如深色/浅色主题、简洁/商务风格等）

【注意】
- 不要推断业务逻辑、交互行为或技术实现方案
- 不要识别具体文字内容，不要描述像素级样式细节
- 总字数控制在200字以内

请以结构化格式输出：

## 页面布局结构
[用层级缩进描述区域划分及各区域包含的组件，如：
- 顶部导航栏
- 主内容区
  - 左侧：搜索/筛选区（输入框、下拉选择）
  - 右侧：数据表格
  - 底部：分页
]

## 视觉风格
[一句话描述整体风格即可]"""

    def _parse_vue_description(self, result: str) -> Dict[str, Any]:
        return {
            "raw_description": result,
            "success": True
        }
    
    @staticmethod
    def _format_image_url(image_source: str, is_base64: bool) -> str:
        if is_base64:
            if image_source.startswith("data:"):
                return image_source
            return f"data:image/png;base64,{image_source}"
        return image_source

    def _build_image_message(
        self,
        image_source: str,
        prompt: str,
        is_base64: bool
    ) -> List[Dict]:
        content = []
        url = self._format_image_url(image_source, is_base64)
        content.append({
            "type": "image_url",
            "image_url": {"url": url}
        })
        content.append({"type": "text", "text": prompt})
        return [{"role": "user", "content": content}]
    
    async def _chat_completion(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        stream: bool = False
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
        
        async with httpx.AsyncClient(timeout=120.0) as client:
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
    
    @staticmethod
    def image_to_base64(file_path: str) -> str:
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    @staticmethod
    def bytes_to_base64(image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode("utf-8")
