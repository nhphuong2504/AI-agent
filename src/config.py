import os
from dotenv import load_dotenv

load_dotenv()

def get_env(key: str, default: str | None = None) -> str:
    val = os.getenv(key, default)
    if val is None:
        raise RuntimeError(f"Missing environment variable: {key}")
    return val

APP_ENV = os.getenv("APP_ENV", "dev")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
