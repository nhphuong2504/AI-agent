from aiohttp import web
import pandas as pd
from src.config import settings

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


def create_app() -> web.Application:
    app = web.Application()
    app.router.add_get("/health", health)
    return app

if __name__ == "__main__":
    app = create_app()
    web.run_app(app, host=settings.host, port=settings.port)
