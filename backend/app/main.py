import os
import tempfile

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import documents

# --- 認証ファイルのセットアップ ---
# 本番（Railway等）では FIREBASE_CREDENTIALS_JSON に JSON 文字列を設定する。
# ローカルでは GOOGLE_APPLICATION_CREDENTIALS にファイルパスを設定する。
if settings.firebase_credentials_json:
    _tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    )
    _tmp.write(settings.firebase_credentials_json)
    _tmp.close()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _tmp.name
elif settings.google_application_credentials:
    os.environ.setdefault(
        "GOOGLE_APPLICATION_CREDENTIALS",
        settings.google_application_credentials,
    )

app = FastAPI(title="eqol-ocr", version="0.1.0")

app.include_router(documents.router)

_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
