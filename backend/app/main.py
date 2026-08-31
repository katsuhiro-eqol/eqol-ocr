import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import documents

# Google Cloud Vision API の認証ファイルパスを環境変数にセット
if settings.google_application_credentials:
    os.environ.setdefault(
        "GOOGLE_APPLICATION_CREDENTIALS",
        settings.google_application_credentials,
    )

app = FastAPI(title="eqol-ocr", version="0.1.0")

app.include_router(documents.router)
#開発時のCORS設定。フロントエンドのドメインに変更すること。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 本番ではフロントのドメインに変更
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
