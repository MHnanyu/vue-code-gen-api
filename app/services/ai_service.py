from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional, Dict


class AIService(ABC):
    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict],
        temperature: float = 1.0,
        stream: bool = False,
        response_format: Optional[Dict[str, str]] = None
    ) -> AsyncIterator[str]:
        pass
    
    async def generate_text(
        self,
        prompt: str,
        context: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        result = ""
        messages = [{"role": "user", "content": prompt}]
        if context:
            messages.insert(0, {"role": "system", "content": context})
        
        async for chunk in self.chat_completion(
            messages,
            temperature=temperature,
            stream=False
        ):
            result += chunk
        
        return result
    
    @abstractmethod
    async def generate_vue_files(
        self,
        prompt: str,
        existing_files: Optional[list[dict]] = None,
        component_lib: str = "Element Plus"
    ) -> dict:
        pass
