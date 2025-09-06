from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Dict, Any
import asyncio

from ...core.logger import *
from ...models.client import ChzzkClient

router = APIRouter(prefix="/auth", tags=["auth"])
lock = asyncio.Lock()


@router.get("/callback")
async def auth_callback(code: str, state: str = "swoosh") -> Response:
    """
    OAuth callback endpoint to handle CHZZK authentication

    Args:
        code: Authorization code from CHZZK
        state: State parameter to prevent CSRF

    Returns:
        Access token and user information
    """
    client = ChzzkClient()
    try:
        async with lock:
            result = await client.token_exchange(code, state)
            if result == 200:
                return Response(
                    content="Authentication successful. You can close this window.",
                    media_type="text/html",
                )
            return Response(
                content="Authentication failed. Please try again.",
                status_code=400,
                media_type="text/html",
            )
    except Exception as e:
        log_error(f"Error during authentication callback: {e}")
        return Response(
            content="Internal server error during authentication.",
            status_code=500,
            media_type="text/html",
        )
