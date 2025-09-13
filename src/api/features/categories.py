from fastapi import APIRouter, Depends, Response
import asyncio

from ...core.config import *
from ...core.logger import *
from ...models.client import ChzzkClient
from ...models.jwt_manager import oauth2_scheme, get_decoded_info

router = APIRouter(prefix="/categories", tags=["categories"])
lock = asyncio.Lock()


@router.get("/")
async def get_categories(
    token: str = Depends(oauth2_scheme), size: int = 20, query: str = ""
) -> Response:
    """
    Get categories from CHZZK API, requires valid user token in headers.

    Args:
        token (str): User token from request headers.
        size (int): Number of categories to fetch. Default is 20.
        query (str): Search query for categories. Default is empty string.

    Returns:
        A dictionary containing category information in format:
        data: [
            {
                "categoryType": "string",
                "categoryId": "string",
                "categoryValue": "string",
                "posterImageUrl": "string",
            },
            ...
        ]
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
            params = {"size": size, "query": query}
            categories_info = await client.get(
                "/categories",
                params=params,
                additional_headers={"Authorization": f"Bearer {chzzk_token}"},
            )
            if "content" not in categories_info:
                return Response(
                    content="Failed to fetch categories info",
                    status_code=500,
                    media_type="Application/json",
                )
            return Response(
                content=categories_info.get("content"),
                status_code=200,
                media_type="Application/json",
            )
    except Exception as e:
        log_error(f"Error fetching categories info: {e}")
        return Response(
            content="Internal server error",
            status_code=500,
            media_type="Application/json",
        )
