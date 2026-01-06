from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.config import APP_ENV
from src.tools.sql import run_sql
from src.tools.text2sql import question_to_sql
from src.tools.chart import make_chart

# 1️⃣ Create the app
app = FastAPI(title="Banking Analytics Assistant", version="0.1.0")

# 2️⃣ Mount static files (charts)
app.mount(
    "/charts",
    StaticFiles(directory="data/charts"),
    name="charts"
)

# 3️⃣ Basic routes
@app.get("/")
def root():
    return {"message": "Banking Analytics Assistant is running"}

@app.get("/health")
def health():
    return {"status": "ok", "env": APP_ENV}

# 4️⃣ Request models
class AskRequest(BaseModel):
    question: str

# 5️⃣ Main Text2SQL endpoint
@app.post("/ask")
def ask(req: AskRequest):
    sql = question_to_sql(req.question)
    df = run_sql(sql)

    chart_path = make_chart(df, title=req.question)
    chart_url = f"/charts/{chart_path.name}" if chart_path else None

    return {
        "question": req.question,
        "sql": sql,
        "rows": len(df),
        "columns": list(df.columns),
        "data": df.to_dict(orient="records"),
        "chart_url": chart_url,
    }
