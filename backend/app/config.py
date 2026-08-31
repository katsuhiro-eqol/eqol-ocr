from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    google_application_credentials: str = ""
    # Firestore / Firebase Admin
    firebase_credentials_path: str = ""  # サービスアカウントJSONのパス
    firebase_project_id: str = ""
    # True にすると認証スキップ（本番では必ず False）
    dev_mode: bool = False
    # ローカル開発用フォールバック（Firestore未設定時にJSONファイルを使う）
    template_store_path: str = "./data/templates"
    fallback_confidence_threshold: float = 0.5

    class Config:
        env_file = ".env"


settings = Settings()
