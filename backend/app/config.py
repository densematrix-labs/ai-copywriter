from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Copywriter"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    TOOL_NAME: str = "ai-copywriter"
    
    # LLM Proxy
    LLM_PROXY_URL: str = "https://llm-proxy.densematrix.ai"
    LLM_PROXY_KEY: str = ""
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Creem Payment
    CREEM_API_KEY: str = ""
    CREEM_WEBHOOK_SECRET: str = ""
    CREEM_API_BASE: str = "https://api.creem.io"
    CREEM_PRODUCT_IDS: str = '{"pack_10": "", "pack_50": "", "pack_200": ""}'
    
    # Free trial
    FREE_GENERATIONS_PER_DEVICE: int = 3
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
