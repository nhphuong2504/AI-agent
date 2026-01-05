from fastapi import FastAPI
from pydantic import BaseModel

from src.tools.sql import run_sql
from src.config import APP_ENV
from src.tools.text2sql import question_to_sql

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

class AskRequest(BaseModel):
    question: str

@app.post("/ask")
def ask(req: AskRequest):
    sql = question_to_sql(req.question)
    df = run_sql(sql)
    return {
        "question": req.question,
        "sql": sql,
        "rows": len(df),
        "columns": list(df.columns),
        "data": df.to_dict(orient="records"),
    }