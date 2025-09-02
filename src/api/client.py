import httpx
import json
from ..core.config import settings
from typing import Dict, Any, Optional
from ..utils.logger import *
from ..db.database import database


class ChzzkClient:
    """Client for making requests to CHZZK API"""

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
                f"{settings.CHZZK_OPEN_API_URL}{endpoint}",
                headers=headers,
                params=params,
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
                f"{settings.CHZZK_OPEN_API_URL}{endpoint}",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            log_debug(f"POST {endpoint} response: {response.text}")
            return response.json()

    async def token_exchange(self, code: str, state: str = "swoosh") -> int:
        """
        Exchange authorization code for access token
        """
        data = {
            "grantType": "authorization_code",
            "clientId": settings.CHZZK_CLIENT_ID,
            "clientSecret": settings.CHZZK_CLIENT_SECRET,
            "code": code,
            "state": state,
        }
        response = await self.post("/auth/v1/token", data)

        if response.get("success"):
            if "accessToken" in response and "refreshToken" in response:
                db = database.get_collection("tokens")
                if db is None:
                    log_error("Database connection is not established")
                    return 500
                result = db.insert_one(
                    {
                        "accessToken": response["accessToken"],
                        "refreshToken": response["refreshToken"],
                        "expiresIn": response.get("expiresIn", 3600),
                    }
                )

                if result.acknowledged:
                    log_info(
                        f"Token exchanged successfully for code: {code} to access token: {response['accessToken']}"
                    )
                    return 200
        log_error(f"Token exchange failed: {json.dumps(response)}")
        return 500

    async def token_refresh(self, access_token: str) -> int:
        """
        Refresh access token using refresh token
        """
        db = database.get_collection("tokens")
        if db is None:
            log_error("Database connection is not established")
            return 500
        token_data = db.find_one({"accessToken": access_token})
        if not token_data or "refreshToken" not in token_data:
            log_error("No valid token found for refresh")
            return 401
        refresh_token = token_data["refreshToken"]
        data = {
            "clientId": settings.CHZZK_CLIENT_ID,
            "clientSecret": settings.CHZZK_CLIENT_SECRET,
            "refreshToken": refresh_token,
            "grantType": "refresh_token",
        }
        response = await self.post("/auth/v1/token", data)
        if response.get("success"):
            if "accessToken" in response and "refreshToken" in response:
                result = db.update_one(
                    {"_id": token_data["_id"]},
                    {
                        "$set": {
                            "accessToken": response["accessToken"],
                            "refreshToken": response["refreshToken"],
                            "expiresIn": response.get("expiresIn", 3600),
                        }
                    },
                )
                if result.acknowledged:
                    log_info(
                        f"Token refreshed successfully for access token: {access_token}"
                    )
                    return 200
        log_error(f"Token refresh failed: {json.dumps(response)}")
        return 500

    async def token_revoke(self, access_token: str) -> int:
        """
        Revoke access token
        """
        db = database.get_collection("tokens")
        if db is None:
            log_error("Database connection is not established")
            return 500
        token_data = db.find_one({"accessToken": access_token})
        if not token_data or "refreshToken" not in token_data:
            log_error("No valid token found for revoke")
            return 401
        refresh_token = token_data["refreshToken"]
        data = {
            "clientId": settings.CHZZK_CLIENT_ID,
            "clientSecret": settings.CHZZK_CLIENT_SECRET,
            "token": refresh_token,
            "tokenTypeHint": "refresh_token",
        }
        response = await self.post("/auth/v1/revoke", data)
        if response.get("success"):
            result = db.delete_one({"_id": token_data["_id"]})
            if result.acknowledged:
                log_info(f"Token revoked successfully for access token: {access_token}")
                return 200
        log_error(f"Token revoke failed: {json.dumps(response)}")
        return 500
