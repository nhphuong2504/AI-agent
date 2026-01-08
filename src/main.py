from aiohttp import web
import pandas as pd
from src.config import settings
from src.analytics import top_products_by_revenue
from src.llm_client import generate_sql_stub, generate_sql_with_llm, is_sql_safe
from src.sql_executor import run_select_query



async def health(request: web.Request) -> web.Response:
    excel_path = settings.online_retail_csv
    try:
        df = pd.read_excel(excel_path, nrows=3)

        df_converted = df.copy()
        for col in df_converted.columns:
            if str(df_converted[col].dtype).startswith("datetime"):
                df_converted[col] = df_converted[col].astype(str)

        sample = df_converted.to_dict(orient="records")
        status = "ok"
        message = f"Loaded {len(df)} sample rows."
    except Exception as e:
        status = "error"
        message = str(e)
        sample = []

    return web.json_response({
        "status": status,
        "message": message,
        "environment": settings.environment,
        "excel_path": excel_path,
        "sample": sample,
    })

async def top_products(request: web.Request) -> web.Response:
    """
    Return top N products by total revenue as JSON.
    Query parameter: n (default 10).
    """
    # Read n from query string, default to 10
    n_str = request.rel_url.query.get("n", "10")
    try:
        n = int(n_str)
    except ValueError:
        n = 10

    try:
        df = top_products_by_revenue(n=n)
        # Convert DataFrame to list of dicts
        result = df.to_dict(orient="records")
        status = "ok"
        message = f"Top {len(result)} products by revenue."
    except Exception as e:
        status = "error"
        message = str(e)
        result = []

    return web.json_response({
        "status": status,
        "message": message,
        "count": len(result),
        "items": result,
    })

async def debug_sql(request: web.Request) -> web.Response:
    """
    Debug endpoint: given a natural-language question, return
    the LLM prompt and the (stubbed) SQL that would be executed.

    Query parameter:
    - question (required)
    """
    question = request.rel_url.query.get("question")
    if not question:
        return web.json_response(
            {
                "status": "error",
                "message": "Missing 'question' query parameter.",
            },
            status=400,
        )

    try:
        prompt, sql = generate_sql_stub(question)
        status = "ok"
        message = "Generated SQL using stubbed LLM client."
    except Exception as e:
        status = "error"
        message = str(e)
        prompt, sql = "", ""

    return web.json_response(
        {
            "status": status,
            "message": message,
            "question": question,
            "prompt": prompt,
            "sql": sql,
        }
    )
async def run_sql(request: web.Request) -> web.Response:
    """
    Debug endpoint: execute a provided SQL SELECT query and return results.

    This is intended for internal use to test the execution layer.
    In the future, this will be driven by LLM-generated SQL.

    Query parameter:
    - sql (required): the SQL query to execute.
    """
    sql = request.rel_url.query.get("sql")
    if not sql:
        return web.json_response(
            {
                "status": "error",
                "message": "Missing 'sql' query parameter.",
            },
            status=400,
        )

    # Basic safety check
    if not is_sql_safe(sql):
        return web.json_response(
            {
                "status": "error",
                "message": "SQL failed safety checks; potentially unsafe.",
            },
            status=400,
        )

    try:
        df = run_select_query(sql)
        rows = df.to_dict(orient="records")
        status = "ok"
        message = f"Query executed successfully. Returned {len(rows)} rows."
    except Exception as e:
        status = "error"
        message = str(e)
        rows = []

    return web.json_response(
        {
            "status": status,
            "message": message,
            "sql": sql,
            "rows": rows,
        }
    )

async def query(request: web.Request) -> web.Response:
    """
    End-to-end query endpoint:

    1) Takes a natural-language question (?question=...).
    2) Uses the real LLM client to generate SQL (with a fallback to the stub).
    3) Runs the SQL with the safe executor.
    4) Returns prompt, SQL, and rows as JSON.
    """
    question = request.rel_url.query.get("question")
    if not question:
        return web.json_response(
            {
                "status": "error",
                "message": "Missing 'question' query parameter.",
            },
            status=400,
        )

    try:
        # 1) NL → prompt + SQL via real LLM
        try:
            prompt, sql = generate_sql_with_llm(question)
            source = "llm"
        except Exception as e:
            # Optional: fallback to stub on error (e.g., missing API key)
            prompt, sql = generate_sql_stub(question)
            source = f"stub (fallback due to error: {e})"

        # 2) Safety check
        if not is_sql_safe(sql):
            return web.json_response(
                {
                    "status": "error",
                    "message": "Generated SQL failed safety checks.",
                    "question": question,
                    "sql": sql,
                    "source": source,
                },
                status=400,
            )

        # 3) Execute SQL
        df = run_select_query(sql)
        rows = df.to_dict(orient="records")

        status = "ok"
        message = f"Query executed successfully. Returned {len(rows)} rows."
    except Exception as e:
        status = "error"
        message = str(e)
        prompt = ""
        sql = ""
        rows = []
        source = "error"

    return web.json_response(
        {
            "status": status,
            "message": message,
            "question": question,
            "source": source,
            "prompt": prompt,
            "sql": sql,
            "rows": rows,
        }
    )


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/health", health)
    app.router.add_get("/top-products", top_products)  
    app.router.add_get("/debug-sql", debug_sql)
    app.router.add_get("/run-sql", run_sql)
    app.router.add_get("/query", query)
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host=settings.host, port=settings.port)
