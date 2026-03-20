from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "vue_code_gen"
    
    AI_PROVIDER: str = "glm5"
    
    GLM5_API_KEY: Optional[str] = "18e01db229da420594690b3df6e82ad1.kORJ3a6BGXeusXK6"
    GLM5_API_URL: str = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"
    GLM5_MODEL: str = "glm-5"
    
    GLM4V_API_KEY: Optional[str] = "18e01db229da420594690b3df6e82ad1.kORJ3a6BGXeusXK6"
    GLM4V_API_URL: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    GLM4V_MODEL: str = "glm-4.6v-flashx"
    
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_API_URL: str = ""
    MINIMAX_MODEL: str = ""
    
    OPENCLAW_API_URL: str = "http://127.0.0.1:18789/v1/responses"
    OPENCLAW_TOKEN: Optional[str] = "510f2865a47ed702447b493359d83214beeb5d4b1576097c"
    OPENCLAW_AGENT_ID: str = "main"
    OPENCLAW_MODEL: str = "openclaw"
    
    MOCK_MODE: bool = True
    
    class Config:
        env_file = ".env"


settings = Settings()
