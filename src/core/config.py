from dotenv import load_dotenv
import os
from functools import lru_cache

load_dotenv()


@lru_cache(maxsize=1)
def PROJECT_NAME() -> str:
    return "Swoosh"


@lru_cache(maxsize=1)
def PROJECT_VERSION() -> str:
    return os.getenv("PROJECT_VERSION", "0.1.0")


@lru_cache(maxsize=1)
def DEBUG() -> bool:
    return os.getenv("DEBUG", "False").lower() in ("true", "1", "t")


@lru_cache(maxsize=1)
def LOG_PATH() -> str:
    return os.getenv("LOG_PATH", "./logs")


@lru_cache(maxsize=1)
def APP_URL() -> str:
    return os.getenv("APP_URL", "http://localhost")


@lru_cache(maxsize=1)
def PORT() -> int:
    return int(os.getenv("PORT", 8000))


def APP_SECRET() -> str:
    return os.getenv("APP_SECRET", "your_default_secret_key")


@lru_cache(maxsize=1)
def JWT_ALGORITHM() -> str:
    return os.getenv("JWT_ALGORITHM", "HS256")


@lru_cache(maxsize=1)
def MONGO_URI() -> str:
    return os.getenv("MONGO_URI", "mongodb://localhost:27017")


@lru_cache(maxsize=1)
def DATABASE_NAME() -> str:
    return os.getenv("DATABASE_NAME", "swoosh_db")


@lru_cache(maxsize=1)
def ALLOWED_HOSTS() -> list:
    hosts = os.getenv("ALLOWED_HOSTS", "")
    return hosts.split(",") if hosts else []


@lru_cache(maxsize=1)
def CHZZK_AUTH_URL() -> str:
    return os.getenv("CHZZK_AUTH_URL", "https://chzzk.naver.com/account-interlock")


@lru_cache(maxsize=1)
def CHZZK_CLIENT_ID() -> str:
    return os.getenv("CHZZK_CLIENT_ID", "your_client_id")


def CHZZK_CLIENT_SECRET() -> str:
    return os.getenv("CHZZK_CLIENT_SECRET", "your_client_secret")


@lru_cache(maxsize=1)
def CHZZK_REDIRECT_URI() -> str:
    return APP_URL() + "/auth/callback"


@lru_cache(maxsize=1)
def CHZZK_OPEN_API_URL() -> str:
    return os.getenv("CHZZK_OPEN_API_URL", "https://openapi.chzzk.naver.com")
