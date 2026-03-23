from app.config import settings
from app.services.ai_service import AIService
from app.services.glm5_service import GLM5Service
from app.services.minimax_service import MiniMaxService


class AIServiceFactory:
    @staticmethod
    def create_service() -> AIService:
        provider = settings.AI_PROVIDER.lower()
        
        if provider == "glm5":
            if not settings.GLM5_API_KEY:
                raise ValueError("GLM5_API_KEY is not configured")
            return GLM5Service()
        elif provider == "minimax":
            if not settings.MINIMAX_API_KEY:
                raise ValueError("MINIMAX_API_KEY is not configured")
            return MiniMaxService()
        else:
            raise ValueError(f"Unknown AI provider: {provider}")
    
    @staticmethod
    def get_service() -> AIService:
        return AIServiceFactory.create_service()
