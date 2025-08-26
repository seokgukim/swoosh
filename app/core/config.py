from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Swoosh"
    PROJECT_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    APP_URL: str = os.getenv("APP_URL", "http://localhost")
    PORT: int = int(os.getenv("PORT", 8000))
    APP_SECRET: str = os.getenv("APP_SECRET", "your_default_secret_key")

    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "swoosh_db")

    ALLOWED_HOSTS: list = (
        os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else []
    )

    CHZZK_AUTH_URL: str = os.getenv(
        "CHZZK_AUTH_URL", "https://chzzk.naver.com/account-interlock"
    )
    CHZZK_CLIENT_ID: str = os.getenv("CHZZK_CLIENT_ID", "your_client_id")
    CHZZK_CLIENT_SECRET: str = os.getenv("CHZZK_CLIENT_SECRET", "your_client_secret")
    CHZZK_REDIRECT_URI: str = APP_URL + "/auth/callback"
    CHZZK_OPEN_API_URL: str = os.getenv(
        "CHZZK_OPEN_API_URL", "https://openapi.chzzk.naver.com"
    )


settings = Settings()

