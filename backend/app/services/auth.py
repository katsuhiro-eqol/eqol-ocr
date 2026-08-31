"""
Firebase Authentication トークン検証。

FastAPI の Depends() で使用する依存関数を提供する。
Authorization: Bearer <Firebase ID Token> ヘッダーを検証し uid を返す。
"""

from firebase_admin import auth
from fastapi import Header, HTTPException

from app.config import settings


async def get_current_uid(authorization: str | None = Header(None)) -> str:
    """Firebase ID Token を検証して uid を返す FastAPI 依存関数。

    DEV_MODE=true の場合は認証をスキップし、開発用の固定 uid を返す。
    """
    if settings.dev_mode:
        return "dev-user"

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="認証トークンが必要です")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        from app.services.firebase import get_app
        get_app()
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="トークンの有効期限が切れています")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="無効なトークンです")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"認証エラー: {e}")
