from fastapi import APIRouter, Depends, Response
import asyncio

from ...core.config import *
from ...core.logger import *
from ...models.client import ChzzkClient
from ...models.jwt_manager import oauth2_scheme, get_decoded_info

router = APIRouter(prefix="/users", tags=["users"])
lock = asyncio.Lock()


@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Response:
    """
    Get current authenticated user information from CHZZK API, requires valid user token in headers.

    Args:
        None

    Returns:
        A dictionary containing user information of corresponding the token in format:
        data: {
                "channelId": "string",
                "channelName": "string",
            }
    """
    client = ChzzkClient()
    # Get user token in request headers
    decoded_info = get_decoded_info(token)
    if decoded_info is None or "accessToken" not in decoded_info:
        return Response(
            content="Invalid token", status_code=401, media_type="Application/json"
        )
    chzzk_token = decoded_info.get("accessToken")

    try:
        async with lock:
            user_info = await client.get(
                "/users/me",
                additional_headers={"Authorization": f"Bearer {chzzk_token}"},
            )
            if "content" not in user_info:
                return Response(
                    content="Failed to fetch user info",
                    status_code=500,
                    media_type="Application/json",
                )
            return Response(
                content=user_info.get("content"),
                status_code=200,
                media_type="Application/json",
            )
    except Exception as e:
        log_error(f"Error fetching user info: {e}")
        return Response(
            content="Internal server error",
            status_code=500,
            media_type="Application/json",
        )
