from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "vue_code_gen"
    
    AI_PROVIDER: str = "glm5"
    
    GLM5_API_KEY: Optional[str] = None
    GLM5_API_URL: str = "https://open.bigmodel.cn/api/coding/paas/v4/chat/completions"
    GLM5_MODEL: str = "glm-5"
    
    MINIMAX_API_KEY: Optional[str] = None
    MINIMAX_API_URL: str = ""
    MINIMAX_MODEL: str = ""
    
    class Config:
        env_file = ".env"


settings = Settings()
