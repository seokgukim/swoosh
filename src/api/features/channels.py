from fastapi import APIRouter, Depends, Response
import asyncio

from ...core.config import *
from ...core.logger import *
from ...models.client import ChzzkClient
from ...models.jwt_manager import oauth2_scheme, get_decoded_info

router = APIRouter(prefix="/channels", tags=["channels"])
lock = asyncio.Lock()


@router.get("/")
async def get_channels(
    token: str = Depends(oauth2_scheme), channelId: list[str] = []
) -> Response:
    """
    Get channels from CHZZK API, requires valid user token in headers.

    Args:
        token (str): User token from request headers.
        channelId (list[str]): List of channel IDs to fetch. If empty, do nothing.
    Returns:
        A dictionary containing channel information in format:
        data: {
            "channelId": "string",
            "channelName": "string",
            "channelImageUrl": "string",
            "followerCount": int,
            "verifiedMark": bool,
            }
    """
    if not channelId:
        return Response(
            content="No channel IDs provided",
            status_code=400,
            media_type="Application/json",
        )
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
            params = {"channelId": channelId}
            channels_info = await client.get(
                "/channels",
                params=params,
                additional_headers={"Authorization": f"Bearer {chzzk_token}"},
            )
            if "content" not in channels_info:
                return Response(
                    content="Failed to fetch channels info",
                    status_code=500,
                    media_type="Application/json",
                )
            return Response(
                content=channels_info.get("content"),
                status_code=200,
                media_type="Application/json",
            )
    except Exception as e:
        log_error(f"Error fetching channels info: {e}")
        return Response(
            content="Internal server error",
            status_code=500,
            media_type="Application/json",
        )


@router.get("/streaming-roles")
async def get_streaming_roles(token: str = Depends(oauth2_scheme)) -> Response:
    """
    Get streaming roles from CHZZK API, requires valid user token in headers.

    Args:
        token (str): User token from request headers.
    Returns:
        A dictionary containing streaming roles information corresponding to the token in format:
        data: {
                "managerChannelId": "string",
                "managerChannelName": "string",
                "userRole": "string"
                "createdDate": "datetime"
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
            roles_info = await client.get(
                "/channels/streaming-roles",
                additional_headers={"Authorization": f"Bearer {chzzk_token}"},
            )
            if "content" not in roles_info:
                return Response(
                    content="Failed to fetch streaming roles info",
                    status_code=500,
                    media_type="Application/json",
                )
            return Response(
                content=roles_info.get("content"),
                status_code=200,
                media_type="Application/json",
            )
    except Exception as e:
        log_error(f"Error fetching streaming roles info: {e}")
        return Response(
            content="Internal server error",
            status_code=500,
            media_type="Application/json",
        )


@router.get("/followers")
async def get_channel_followers(
    token: str = Depends(oauth2_scheme), page: int = 0, pageSize: int = 30
) -> Response:
    """
    Get channel followers from CHZZK API, requires valid user token in headers.

    Args:
        token (str): User token from request headers.
        page (int): Page number for pagination. Default is 0.
        pageSize (int): Number of items per page. Default is 30.
    Returns:
        A dictionary containing channel followers information corresponding to the token in format:
        data: {
            "channelId": "string",
            "channelName": "string",
            "createdDate": "datetime:
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
            params = {"page": page, "pageSize": pageSize}
            followers_info = await client.get(
                "/channels/followers",
                params=params,
                additional_headers={"Authorization": f"Bearer {chzzk_token}"},
            )
            if "content" not in followers_info:
                return Response(
                    content="Failed to fetch channel followers info",
                    status_code=500,
                    media_type="Application/json",
                )
            return Response(
                content=followers_info.get("content"),
                status_code=200,
                media_type="Application/json",
            )
    except Exception as e:
        log_error(f"Error fetching channel followers info: {e}")
        return Response(
            content="Internal server error",
            status_code=500,
            media_type="Application/json",
        )


@router.get("/subscribers")
async def get_channel_subscribers(
    token: str = Depends(oauth2_scheme), page: int = 0, pageSize: int = 30
) -> Response:
    """
    Get channel subscribers from CHZZK API, requires valid user token in headers.

    Args:
        token (str): User token from request headers.
        page (int): Page number for pagination. Default is 0.
        pageSize (int): Number of items per page. Default is 30.
    Returns:
        A dictionary containing channel subscribers information corresponding to the token in format:
        data: {
            "channelId": "string",
            "channelName": "string",
            "month": int,
            "tierNo": int,
            "createdDate": "datetime"
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
            params = {"page": page, "pageSize": pageSize}
            subscribers_info = await client.get(
                "/channels/subscribers",
                params=params,
                additional_headers={"Authorization": f"Bearer {chzzk_token}"},
            )
            if "content" not in subscribers_info:
                return Response(
                    content="Failed to fetch channel subscribers info",
                    status_code=500,
                    media_type="Application/json",
                )
            return Response(
                content=subscribers_info.get("content"),
                status_code=200,
                media_type="Application/json",
            )
    except Exception as e:
        log_error(f"Error fetching channel subscribers info: {e}")
        return Response(
            content="Internal server error",
            status_code=500,
            media_type="Application/json",
        )
