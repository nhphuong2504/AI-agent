from aiohttp import web
import pandas as pd
from src.config import settings
from src.analytics import top_products_by_revenue


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


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/health", health)
    app.router.add_get("/top-products", top_products)  # <— add this line
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host=settings.host, port=settings.port)
