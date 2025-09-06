# FastAPI dependencies for common tasks
# Includes token authentication, pagination, and filtering
from typing import Optional
from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from ..core.config import *
from ..db.database import database  # Use the existing database connection to MongoDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Verify the JWT token and return the payload.

    Args:
        token: JWT token from the Authorization header
    Returns:
        Decoded token payload if valid, Internal server error if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, APP_SECRET(), algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return Response(
            content="Could not validate credentials",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_pagination_params(skip: int = 0, limit: int = 10) -> dict:
    """
    Get pagination parameters.

    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
    Returns:
        Dictionary with skip and limit values
    """
    return {"skip": skip, "limit": limit}


def get_filter_params(
    search: Optional[str] = None, sort_by: Optional[str] = None
) -> dict:
    """
    Get filtering parameters.

    Args:
        search: Search term for filtering
        sort_by: Field to sort the results by
    Returns:
        Dictionary with search and sort_by values
    """
    return {"search": search, "sort_by": sort_by}

