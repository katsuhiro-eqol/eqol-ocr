from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    google_application_credentials: str = ""
    # Firestore / Firebase Admin
    firebase_credentials_path: str = ""   # ローカル: サービスアカウントJSONファイルパス
    firebase_credentials_json: str = ""   # 本番: サービスアカウントJSONの文字列（Railway等）
    firebase_project_id: str = ""
    # True にすると認証スキップ（本番では必ず False）
    dev_mode: bool = False
    # ローカル開発用フォールバック（Firestore未設定時にJSONファイルを使う）
    template_store_path: str = "./data/templates"
    fallback_confidence_threshold: float = 0.5
    # 使用回数制限を除外する uid（カンマ区切り）
    unlimited_uids: str = ""
    # CORS 許可オリジン（カンマ区切り）
    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
