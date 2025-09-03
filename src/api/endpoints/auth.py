from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Dict, Any
import asyncio

from ...utils.logger import *
from ..client import ChzzkClient

router = APIRouter(prefix="/auth", tags=["auth"])
lock = asyncio.Lock()


@router.get("/callback")
async def auth_callback(
    code: str,
    state: str,
) -> Response:
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
                    status_code=200,
                    content="Authentication successful. You can close this window.",
                )
            return Response(
                status_code=result, content="Authentication failed. Please try again."
            )
    except Exception as e:
        log_error(f"Error during authentication callback: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
