import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Data
    online_retail_csv: str = os.getenv("ONLINE_RETAIL_CSV", "./data/online_retail.xlsx")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/online_retail.db")

    # OpenAI / LLM
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Environment / server
    environment: str = os.getenv("ENVIRONMENT", "development")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 3978))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
