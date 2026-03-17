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
            if are_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": source}
                })
            else:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": source}
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
        return """你是一个专业的前端开发助手。请分析这张UI设计图/网页截图，为后续生成Vue3代码提供详细描述。

分析要求：
1. **页面结构**：描述页面的整体布局（头部、侧边栏、主内容区等）
2. **组件识别**：识别所有UI组件（按钮、输入框、表格、卡片、导航等）
3. **布局细节**：描述组件的位置关系、间距、对齐方式
4. **样式信息**：颜色、字体大小、边框、阴影等视觉样式
5. **交互元素**：识别可点击、可输入等交互元素
6. **数据展示**：识别展示的数据类型和格式

请以结构化的方式输出，便于后续代码生成。格式如下：

## 页面概述
[一句话描述页面用途]

## 布局结构
- 整体布局类型：[flex/grid/混合]
- 主要区域划分：[列出区域]

## 组件清单
1. 组件名称：[名称]
   - 类型：[按钮/输入框/表格等]
   - 位置：[顶部/左侧/中央等]
   - 样式特征：[颜色/大小/边框等]
   - 交互行为：[点击/悬停等]

## 样式规范
- 主色调：[颜色]
- 背景色：[颜色]
- 字体：[描述]
- 间距规律：[描述]

## 建议的组件结构
[列出建议的Vue组件拆分方案]"""

    def _parse_vue_description(self, result: str) -> Dict[str, Any]:
        return {
            "raw_description": result,
            "success": True
        }
    
    def _build_image_message(
        self,
        image_source: str,
        prompt: str,
        is_base64: bool
    ) -> List[Dict]:
        content = []
        
        if is_base64:
            content.append({
                "type": "image_url",
                "image_url": {"url": image_source}
            })
        else:
            content.append({
                "type": "image_url",
                "image_url": {"url": image_source}
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
