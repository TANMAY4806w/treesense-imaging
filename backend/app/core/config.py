import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

# Project Root (one level above backend/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "TreeSense Imaging API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
        "*"
    ]
    
    # Model Artifacts
    MODEL_DIR: Path = BASE_DIR / "models"
    DEFAULT_MODEL_PT: Path = BASE_DIR / "models" / "best.pt"
    DEFAULT_MODEL_ONNX: Path = BASE_DIR / "models" / "best.onnx"
    
    # External API Keys
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")

    class Config:
        env_file = BASE_DIR / ".env"
        extra = "ignore"

settings = Settings()
