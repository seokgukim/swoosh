# Manages JWT token creation and verification for user authentication.
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from datetime import datetime, timedelta

from ..core.config import *
from ..db.database import database  # Use the existing database connection to MongoDB
from ..core.logger import log_error

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_token(data: dict, expires_delta: timedelta = timedelta(days=1)) -> str:
    """
    Create a JWT token.

    Args:
        data: Data to encode in the token
        expires_delta: Expiration time (defaults to 1 day if not provided)
    Returns:
        Encoded JWT token as a string
    """
    to_encode = data.copy()
    now = datetime.now()
    expire = now + expires_delta

    # Add standard claims
    to_encode.update({"exp": expire, "iat": now, "nbf": now})

    encoded_jwt = jwt.encode(to_encode, APP_SECRET(), algorithm=JWT_ALGORITHM())
    return encoded_jwt


def create_refresh_token(
    data: dict, expires_delta: timedelta = timedelta(days=7)
) -> str:
    """
    Create a refresh JWT token.

    Args:
        data: Data to encode in the token
        expires_delta: Expiration time (defaults to 7 days if not provided)
    Returns:
        Encoded JWT refresh token as a string
    """
    to_encode = data.copy()
    now = datetime.now()
    expire = now + expires_delta

    # Add standard claims
    to_encode.update({"exp": expire, "iat": now, "nbf": now})

    encoded_jwt = jwt.encode(to_encode, APP_SECRET(), algorithm=JWT_ALGORITHM())
    return encoded_jwt


def verify_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Verify the JWT token and return the payload.

    Args:
        token: JWT token from the Authorization header
    Returns:
        Decoded token payload if valid, else error message
    """
    db = database.get_collection("revoked_tokens")
    if db is None:
        log_error("Database connection error")
        return {"error": "Could not validate credentials"}
    if db.find_one({"token": token}):
        return {"error": "Token has been revoked"}
    try:
        payload = jwt.decode(token, APP_SECRET(), algorithms=[JWT_ALGORITHM()])
        return payload
    except Exception as e:
        log_error(f"Token verification failed: {e}")
        return {"error": "Could not validate credentials"}


def verify_refresh_token(token: str) -> dict:
    """
    Verify the JWT refresh token and return the payload.

    Args:
        token: JWT refresh token
    Returns:
        Decoded token payload if valid, else error message
    """
    try:
        payload = jwt.decode(token, APP_SECRET(), algorithms=[JWT_ALGORITHM()])
        return payload
    except Exception as e:
        log_error(f"Refresh token verification failed: {e}")
        return {"error": "Could not validate credentials"}


def revoke_token(token: str) -> bool:
    """
    Revoke a JWT token (placeholder function).

    Args:
        token: JWT token to revoke
    Returns:
        True if revocation is successful, else False
    """
    db = database.get_collection("revoked_tokens")
    if db is None:
        log_error("Database connection error")
        return False
    try:
        db.insert_one({"token": token})
        return True
    except Exception as e:
        log_error(f"Failed to revoke token: {e}")
        return False


def get_decoded_info(token) -> dict | None:
    """
    Extract the CHZZK access token from the JWT token.

    Args:
        token: JWT token from the Authorization header
    Returns:
        Decoded information (containing access token) if valid, else None
    """
    try:
        payload = jwt.decode(token, APP_SECRET(), algorithms=[JWT_ALGORITHM()])
        return payload
    except Exception as e:
        log_error(f"Failed to decode JWT: {e}")
        return None
