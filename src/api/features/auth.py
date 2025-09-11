from fastapi import APIRouter, Depends, HTTPException, Response
from typing import Dict, Any
import asyncio

from ...core.config import *
from ...core.logger import *
from ...db.database import database
from ...models.jwt_manager import create_token, create_refresh_token
from ...models.client import ChzzkClient
from ...utils.uuid_manager import generate_uuid, validate_uuid, remove_uuid

router = APIRouter(prefix="/auth", tags=["auth"])
lock = asyncio.Lock()


@router.get("/login")
async def auth_login() -> Response:
    """
    OAuth login endpoint to initiate CHZZK Authentication

    Returns:
        302 Redirect to CHZZK authorization URL
    """
    state = generate_uuid()
    auth_url = f"{CHZZK_AUTH_URL()}?clientId={CHZZK_CLIENT_ID()}&redirectUri={CHZZK_REDIRECT_URI()}&state={state}"
    return Response(status_code=302, headers={"Location": auth_url})


@router.get("/callback")
async def auth_callback(code: str, state: str = "swoosh") -> Response:
    """
    OAuth callback endpoint to handle CHZZK authentication

    Args:
        code: Authorization code from CHZZK
        state: State parameter to prevent CSRF

    Returns:
        A Response indicating success or failure of authentication

    Note:
        When you call this endpoint, make sure to include the `code` and `state` parameters in the query string.
        the `state` parameter is optional and defaults to "swoosh".
        but you can set it to any value you want to help prevent CSRF attacks.
    """
    if not validate_uuid(state):
        return Response(
            content="Invalid state parameter. Possible CSRF attack.",
            status_code=400,
            media_type="text/html",
        )
    remove_uuid(state)

    client = ChzzkClient()
    try:
        async with lock:
            result, token = await client.token_exchange(code, state)
            if result == 200:
                jwt_token = create_token({"access_token": token["accessToken"]}, expires_delta=timedelta(seconds=token["expiresIn"]))

                response Response(
                    content="Authentication successful. You can close this window.",
                    media_type="text/html",
                )
                response.set_cookie(
                    key="swoosh_token",
                    value=jwt_token,
                    httponly=True,
                    secure=!DEBUG(),
                    samesite="lax",
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
