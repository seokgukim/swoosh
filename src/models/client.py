import httpx
import json
from typing import Dict, Any, Optional

from ..core.config import *
from ..core.logger import *
from ..db.database import database


class ChzzkClient:
    """
    Client for making requests to CHZZK Open API
    """

    def __init__(self):
        """
        Initialize with authentication cookies
        """
        self.headers = {
            "Content-Type": "application/json",
        }

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make GET request to CHZZK API"""
        async with httpx.AsyncClient() as client:
            headers = self.headers.copy()
            if additional_headers is not None:
                headers.update(additional_headers)
            response = await client.get(
                f"{CHZZK_OPEN_API_URL()}{endpoint}",
                headers=headers,
                params=params if params is not None else {},
            )
            response.raise_for_status()
            log_debug(f"GET {endpoint} response: {response.text}")
            return response.json()

    async def post(
        self,
        endpoint: str,
        data: Dict[str, Any],
        additional_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make POST request to CHZZK API"""
        async with httpx.AsyncClient() as client:
            headers = self.headers.copy()
            if additional_headers is not None:
                headers.update(additional_headers)
            response = await client.post(
                f"{CHZZK_OPEN_API_URL()}{endpoint}",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            log_debug(f"POST {endpoint} response: {response.text}")
            return response.json()

    async def token_exchange(
        self, code: str, state: str = "swoosh"
    ) -> tuple[int, Optional[Dict[str, Any]]]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from CHZZK
            state: State parameter to prevent CSRF
        Returns:
            Status code and token data if successful
        """
        data = {
            "grantType": "authorization_code",
            "clientId": CHZZK_CLIENT_ID(),
            "clientSecret": CHZZK_CLIENT_SECRET(),
            "code": code,
            "state": state,
        }

        response = await self.post("/auth/v1/token", data)
        if response.get("code") != 200:
            log_error(f"Token exchange error: {json.dumps(response)}")
            return response.get("code", 500), None

        content = response.get("content", {})

        if "accessToken" in content and "refreshToken" in content:
            token_data = {
                "accessToken": content.get("accessToken"),
                "refreshToken": content.get("refreshToken"),
                "expiresIn": content.get("expiresIn", 3600),
                "state": state,
            }

            return 200, token_data

        log_error(f"token exchange failed: {json.dumps(response)}")
        return 500, None

    async def token_refresh(
        self, token_data: Dict[str, Any]
    ) -> tuple[int, Optional[Dict[str, Any]]]:
        """
        Refresh access token using refresh token

        Args:
            token_data: Dictionary containing the current token data
        Returns:
            Status code and refreshed token data if successful
        """
        if not token_data or "refreshToken" not in token_data:
            log_error("no valid token found for refresh")
            return 401, None

        refresh_token = token_data.get("refreshToken")
        data = {
            "clientId": CHZZK_CLIENT_ID(),
            "clientSecret": CHZZK_CLIENT_SECRET(),
            "refreshToken": refresh_token,
            "grantType": "refresh_token",
        }

        response = await self.post("/auth/v1/token", data)
        if response.get("code") != 200:
            log_error(f"token refresh error: {json.dumps(response)}")
            return response.get("code", 500)
        content = response.get("content", {})

        if "accessToken" in content and "refreshToken" in content:
            refreshed_token_data = {
                "accessToken": content.get("accessToken"),
                "refreshToken": content.get("refreshToken"),
                "expiresIn": content.get("expiresIn", 3600),
                "state": token_data.get("state", "swoosh"),
            }

            return 200, refreshed_token_data

        log_error(f"token refresh failed: {json.dumps(response)}")
        return 500, None

    async def token_revoke(self, token_data: Dict[str, Any]) -> int:
        """
        Revoke access token

        Args:
            token_data: Dictionary containing the current token data
        Returns:
            Status code indicating success or failure
        """
        if not token_data or "refreshToken" not in token_data:
            log_error("No valid token found for revoke")
            return 401

        refresh_token = token_data.get("refreshToken")
        data = {
            "clientId": CHZZK_CLIENT_ID(),
            "clientSecret": CHZZK_CLIENT_SECRET(),
            "token": refresh_token,
            "tokenTypeHint": "refresh_token",
        }

        response = await self.post("/auth/v1/revoke", data)
        if response.get("code") != 200:
            log_error(f"Token revoke error: {json.dumps(response)}")
            return response.get("code", 500)

        return 200
