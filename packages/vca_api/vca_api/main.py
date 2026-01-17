import logging

import uvicorn
from fastapi import FastAPI
from vca_core.exceptions import NotFoundError

from vca_api.exception_handlers import not_found_exception_handler
from vca_api.routes.auth import router as auth_router
from vca_api.settings import server_settings

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(name)s - %(message)s",
)

app = FastAPI(
    title="VCA Server",
    version="0.1.0",
)

# 例外ハンドラ登録
app.add_exception_handler(NotFoundError, not_found_exception_handler)

app.include_router(auth_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


def run_server():
    uvicorn.run(
        "vca_api.main:app",
        host=server_settings.HOST,
        port=server_settings.PORT,
        reload=server_settings.reload,
        workers=server_settings.workers,
    )
