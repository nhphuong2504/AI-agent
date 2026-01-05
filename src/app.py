from fastapi import FastAPI
from pydantic import BaseModel

from src.tools.sql import run_sql
from src.config import APP_ENV

app = FastAPI(title="Online Retail Analytics Assistant", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "env": APP_ENV}


@app.get("/")
def root():
    return {"message": "Online Retail Analytics Assistant is running"}


class QueryRequest(BaseModel):
    sql: str


@app.post("/query")
def query(req: QueryRequest):
    df = run_sql(req.sql)
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "data": df.to_dict(orient="records"),
    }
