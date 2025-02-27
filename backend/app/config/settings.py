from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    CHAT_MODEL: str = "deepseek-r1:7b"
    RAG_MODEL: str = "mistral"
    TAVILY_API_KEY: str
    
    class Config:
        env_file = ".env"

settings = Settings()