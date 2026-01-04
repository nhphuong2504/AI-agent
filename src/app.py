from fastapi import FastAPI
from src.config import APP_ENV

app = FastAPI(title="Banking Analytics Assistant", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok", "env": APP_ENV}

@app.get("/")
def root():
    return {"message": "Banking Analytics Assistant is running"}
