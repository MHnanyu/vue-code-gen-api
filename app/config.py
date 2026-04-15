from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "vue_code_gen"
    
    AI_PROVIDER: str = "glm5"
    
    GLM5_API_KEY: Optional[str] = ""
    GLM5_API_URL: str = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"
    GLM5_MODEL: str = "glm-5"
    
    GLM4V_API_KEY: Optional[str] = ""
    GLM4V_API_URL: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    GLM4V_MODEL: str = "glm-4.6v-flashx"
    
    MINIMAX_API_KEY: Optional[str] = ""
    MINIMAX_API_URL: str = "https://api.minimaxi.com/anthropic"
    MINIMAX_MODEL: str = "MiniMax-M2.7"
    
    OPENCLAW_API_URL: str = "http://127.0.0.1:18789/v1/responses"
    OPENCLAW_TOKEN: Optional[str] = ""
    OPENCLAW_AGENT_ID: str = "main"
    OPENCLAW_MODEL: str = "openclaw"
    
    MOCK_MODE: bool = False

    AGENT_MAX_STEPS: int = 10
    AGENT_ENABLE_REVIEW: bool = False
    GLM5_AGENT_MODEL: Optional[str] = ""
    
    class Config:
        env_file = ".env"


settings = Settings()
