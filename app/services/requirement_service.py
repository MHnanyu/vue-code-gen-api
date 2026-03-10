import logging
import os
from typing import Optional
import time

from app.services.ai_factory import AIServiceFactory
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class RequirementService:
    def __init__(self):
        self.ai_service: AIService = AIServiceFactory.get_service()
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "prompts",
            "requirement_template.md"
        )
        
        try:
            with open(prompt_path, "r", encoding="utf-8") as f:
                content = f.read()
                logger.info("成功加载需求标准化Prompt模板")
                return content
        except FileNotFoundError:
            logger.error(f"Prompt模板文件不存在: {prompt_path}")
            raise FileNotFoundError(f"Prompt模板文件不存在: {prompt_path}")
        except Exception as e:
            logger.error(f"加载Prompt模板失败: {str(e)}")
            raise
    
    async def standardize_requirement(
        self,
        user_requirement: str,
        temperature: float = 0.2
    ) -> dict:
        start_time = time.time()
        logger.info(f"开始需求标准化 - 输入长度: {len(user_requirement)}")
        
        try:
            prompt = self.prompt_template.replace("{用户输入的需求内容}", user_requirement)
            
            result = ""
            messages = [{"role": "user", "content": prompt}]
            
            async for chunk in self.ai_service.chat_completion(
                messages,
                temperature=temperature,
                stream=False
            ):
                result += chunk
            
            duration = time.time() - start_time
            logger.info(f"需求标准化完成 - 耗时: {duration:.2f}s, 输出长度: {len(result)}")
            
            return {
                "status": "success",
                "duration": round(duration, 2),
                "output": result
            }
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"需求标准化失败: {str(e)}")
            
            return {
                "status": "failed",
                "duration": round(duration, 2),
                "error": str(e),
                "output": None
            }
    
    def extract_requirement_type(self, requirement_doc: str) -> str:
        if len(requirement_doc) > 200:
            return "standard"
        else:
            return "one_sentence"
