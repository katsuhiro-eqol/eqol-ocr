"""
Firebase Admin SDK の初期化とクライアント取得。

FIREBASE_CREDENTIALS_JSON（JSON文字列）または
FIREBASE_CREDENTIALS_PATH（サービスアカウントJSONファイルパス）または
GOOGLE_APPLICATION_CREDENTIALS（ADC）で認証する。
"""

import firebase_admin
from firebase_admin import credentials, firestore

from app.config import settings

_app: firebase_admin.App | None = None


def get_app() -> firebase_admin.App:
    global _app
    if _app is not None:
        return _app

    if settings.firebase_credentials_json:
        import json
        cert_dict = json.loads(settings.firebase_credentials_json)
        cred = credentials.Certificate(cert_dict)
        kwargs = {}
    elif settings.firebase_credentials_path:
        cred = credentials.Certificate(settings.firebase_credentials_path)
        kwargs = {}
    else:
        # Application Default Credentials（Cloud Run 等）
        cred = credentials.ApplicationDefault()
        kwargs = {"projectId": settings.firebase_project_id} if settings.firebase_project_id else {}

    _app = firebase_admin.initialize_app(cred, kwargs)
    return _app


def get_db() -> firestore.Client:
    get_app()
    return firestore.client()
