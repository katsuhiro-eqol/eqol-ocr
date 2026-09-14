"""
Firebase Authentication トークン検証 / デバイスID匿名アクセス。

優先順位:
  1. DEV_MODE=true → 認証スキップ（dev-user）
  2. Authorization: Bearer <Firebase ID Token> → 登録ユーザー（制限なし）
  3. X-Device-Id ヘッダー → 匿名ユーザー（回数制限あり）
  4. どちらもなし → 401

uid の形式:
  - 登録ユーザー: firebase の uid 文字列
  - 匿名ユーザー: "anon_{device_id}"
  - 開発モード:   "dev-user"
"""

from firebase_admin import auth
from fastapi import Header, HTTPException

from app.config import settings


async def get_current_uid(
    authorization: str | None = Header(None),
    x_device_id: str | None = Header(None, alias="X-Device-Id"),
) -> str:
    if settings.dev_mode:
        return "dev-user"

    if authorization and authorization.startswith("Bearer "):
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

    if x_device_id:
        if len(x_device_id) > 128:
            raise HTTPException(status_code=400, detail="X-Device-Id が長すぎます")
        return f"anon_{x_device_id}"

    raise HTTPException(status_code=401, detail="認証が必要です（X-Device-Id ヘッダーを送信してください）")


def is_anonymous(uid: str) -> bool:
    return uid.startswith("anon_")


def device_id_from_uid(uid: str) -> str:
    return uid.removeprefix("anon_")
