from ..utils.singleton import SingletonMeta
from ..db.database import database
from ..api.client import ChzzkClient
from ..core.config import *
from socketio import AsyncClient
from ..utils.logger import *
import json


class InvalidMessage(object):
    def __init__(self, message="Invalid message"):
        self.check_valid = False
        self.message = message


class ChzzkSession:
    """
    A simple session management class to store and retrieve session data.
    """

    # Initialize session data storage
    def __init__(self):
        self.session_data = {}

    # Methods to set, get, and clear session data
    def set(self, key, value):
        self.session_data[key] = value

    def get(self, key, default=None):
        return self.session_data.get(key, default)

    async def socket_disconnect(self):
        socket = self.session_data.get("socket")

        if not isinstance(socket, AsyncClient):
            log_error(
                f"[session {self.get('token', 'unknown')}] Invalid socket instance"
            )
            return

        if socket.connected:
            await socket.disconnect()
            log_info(f"[session {self.get('token', 'unknown')}] Disconnected socket")

        del self.session_data["socket"]

    def clear(self):
        if "socket" in self.session_data:
            import asyncio

            asyncio.run(self.socket_disconnect())
        self.session_data.clear()

    # Message loaders and validators
    def load_system_message(self, message):
        # System message validation
        try:
            msg_json = json.loads(message)
            if "type" not in msg_json or msg_json.get("type") not in [
                "connected",
                "subscribed",
                "unsubscribed",
                "revoked",
            ]:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Unknown system message type: {message}"
                )
                return InvalidMessage()
            if "data" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] System message missing data field: {message}"
                )
                return InvalidMessage()

            if msg_json.get("type") is "connected":
                if "sessionKey" not in msg_json.get("data"):
                    log_error(
                        f"[session {self.get('token', 'unknown')}] Connected message missing sessionKey: {message}"
                    )
                    return InvalidMessage()
            else:
                if "eventType" not in msg_json.get("data") or msg_json.get("data").get("eventType") not in ["CHAT", "DONATION", "SUBSCRIPTION"]:
                    log_error(
                        f"[session {self.get('token', 'unknown')}] System message with unknown event type: {message}"
                    )
                    return InvalidMessage()
                if "channelId" not in msg_json.get("data"):
                    log_error(
                        f"[session {self.get('token', 'unknown')}] System message missing channelId: {message}"
                    )
                    return InvalidMessage()

            return msg_json
        except json.JSONDecodeError:
            log_error(
                f"[session {self.get('token', 'unknown')}] Failed to decode system message: {message}"
            )
            return InvalidMessage()

    def load_chat_message(self, message):
        # Chat message validation
        try:
            msg_json = json.loads(message)
            if "channelId" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Chat message missing channelId: {message}"
                )
                return InvalidMessage()
            if "senderChannelId" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Chat message missing senderChannelId: {message}"
                )
                return InvalidMessage()
            if "profile" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Chat message missing profile: {message}"
                )
                return InvalidMessage()
            for field in ["nickname", "badges", "verifiedMark"]:
                if field not in msg_json.get("profile"):
                    log_error(
                        f"[session {self.get('token', 'unknown')}] Chat message profile missing {field}: {message}"
                    )
                    return InvalidMessage()
            if "userRoleCode" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Chat message missing userRoleCode: {message}"
                )
                return InvalidMessage()
            if msg_json.get("userRoleCode") not in [
                "streamer",
                "common_user",
                "streaming_channel_manager",
                "streaming_chat_manager",
            ]:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Chat message with unknown userRoleCode: {message}"
                )
                return InvalidMessage()
            if "content" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Chat message missing content: {message}"
                )
                return InvalidMessage()
            if "emojis" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Chat message missing emojis: {message}"
                )
                return InvalidMessage()
            for emoji in msg_json.get("emojis"):
                for field in ["key", "value"]:
                    if field not in emoji:
                        log_error(
                            f"[session {self.get('token', 'unknown')}] Chat message emoji missing {field}: {message}"
                        )
                        return InvalidMessage()
            if "messageTime" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Chat message missing messageTime: {message}"
                )
                return InvalidMessage()

            return msg_json
        except json.JSONDecodeError:
            log_error(
                f"[session {self.get('token', 'unknown')}] Failed to decode chat message: {message}"
            )
            return InvalidMessage()

    def load_donation_message(self, message):
        # Donation message validation
        try:
            msg_json = json.loads(message)
            if "donationType" not in msg_json or msg_json.get("donationType") not in [
                "CHAT",
                "VIDEO",
            ]:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Donation message with unknown donationType: {message}"
                )
                return InvalidMessage()
            if "channelId" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Donation message missing channelId: {message}"
                )
                return InvalidMessage()
            if "donatorChannelId" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Donation message missing donatorChannelId: {message}"
                )
                return InvalidMessage()
            if "donatorNickname" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Donation message missing donatorNickname: {message}"
                )
                return InvalidMessage()
            if "payAmount" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Donation message missing payAmount: {message}"
                )
                return InvalidMessage()
            if "donationText" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Donation message missing donationText: {message}"
                )
                return InvalidMessage()
            if "emojis" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Donation message missing emojis: {message}"
                )
                return InvalidMessage()
            for emoji in msg_json.get("emojis"):
                for field in ["key", "value"]:
                    if field not in emoji:
                        log_error(
                            f"[session {self.get('token', 'unknown')}] Donation message emoji missing {field}: {message}"
                        )
                        return InvalidMessage()
            return msg_json
        except json.JSONDecodeError:
            log_error(
                f"[session {self.get('token', 'unknown')}] Failed to decode donation message: {message}"
            )
            return InvalidMessage()

    def load_subscription_message(self, message):
        # Subscription message validation
        try:
            msg_json = json.loads(message)
            if "channelId" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Subscription message missing channelId: {message}"
                )
                return InvalidMessage()
            if "subscriberChannelId" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Subscription message missing subscriberChannelId: {message}"
                )
                return InvalidMessage()
            if "subscriberNickname" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Subscription message missing subscriberNickname: {message}"
                )
                return InvalidMessage()
            if "tierNo" not in msg_json or msg_json.get("tierNo") not in [1, 2, 3]:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Subscription message with unknown tierNo: {message}"
                )
                return InvalidMessage()
            if "tierName" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Subscription message missing tierName: {message}"
                )
                return InvalidMessage()
            if "month" not in msg_json:
                log_error(
                    f"[session {self.get('token', 'unknown')}] Subscription message missing month: {message}"
                )
                return InvalidMessage()
            return msg_json
        except json.JSONDecodeError:
            log_error(
                f"[session {self.get('token', 'unknown')}] Failed to decode subscription message: {message}"
            )
            return InvalidMessage()

    # Handlers for different message types
    async def handle_system_message(self, message):
        # Handle system messages here
        msg_json = self.load_system_message(message)
        if msg_json.isinstance(InvalidMessage):
            return

        if msg_json.get("type") == "connected":
            # Handle connected message
            self.set("sessionKey", msg_json.get("data").get("sessionKey"))
            log_info(
                f"[session {self.get('token', 'unknown')}] Connected with sessionKey: {self.get('sessionKey')}"
            )

        elif msg_json.get("type") == "subscribed":
            # Handle subscribed message
            event_type = msg_json.get("data").get("eventType")
            channel_id = msg_json.get("data").get("channelId")
            self.set(f"subscribed_{event_type}", True)
            log_info(
                f"[session {self.get("token", "unknown")}] Subscribed to {event_type} on channel {channel_id}"
            )

        elif msg_json.get("type") == "unsubscribed":
            # Handle unsubscribed message
            event_type = msg_json.get("data").get("eventType")
            channel_id = msg_json.get("data").get("channelId")
            self.set(f"subscribed_{event_type}", False)
            log_info(
                f"[session {self.get("token", "unknown")}] Unsubscribed from {event_type} on channel {channel_id}"
            )
        elif msg_json.get("type") == "revoked":
            # Handle revoked message
            event_type = msg_json.get("data").get("eventType")
            channel_id = msg_json.get("data").get("channelId")
            self.set(f"subscribed_{event_type}", False)
            log_warning(
                f"[session {self.get("token", "unknown")}] Subscription revoked for {event_type} on channel {channel_id}"
            )

    async def handle_chat_message(self, message):
        # Handle chat messages here
        msg_json = self.load_chat_message(message)
        if msg_json.isinstance(InvalidMessage):
            return
        log_info(
            f"[session {self.get('token', 'unknown')}] Chat message received: {msg_json}"
        )

    async def handle_donation_message(self, message):
        # Handle donation messages here
        msg_json = self.load_donation_message(message)
        if msg_json.isinstance(InvalidMessage):
            return
        log_info(
            f"[session {self.get('token', 'unknown')}] Donation message received: {msg_json}"
        )

    async def handle_subscription_message(self, message):
        # Handle subscription messages here
        msg_json = self.load_subscription_message(message)
        if msg_json.isinstance(InvalidMessage):
            return
        log_info(
            f"[session {self.get('token', 'unknown')}] Subscription message received: {msg_json}"
        )

    async def session_connect(self, data):
        # Connect a session with data
        db = database.get_collection("tokens")
        if db is None:
            return 500

        if "scope" not in data:
            return 400

        if data.get("scope") == "user":
            if "token" not in data:
                return 400

            token_data = db.find_one({"accessToken": data.get("token")})
            if not token_data:
                return 401

            client = ChzzkClient()
            additional_headers = {"Authorization": f"Bearer {data.get('token')}"}
            response = await client.get(
                "/open/v1/sessions/auth", additional_headers=additional_headers
            )

            if response.get("code") != 200:
                log_error(
                    f"[session {data.get('token')}] Failed to authenticate token: {response}"
                )
                return response.get("code", 500)

            content = response.get("content", {})

            socket = AsyncClient()
            socket.on("SYSTEM", self.handle_system_message)
            socket.on("CHAT", self.handle_chat_message)
            socket.on("DONATION", self.handle_donation_message)
            socket.on("SUBSCRIPTION", self.handle_subscription_message)
            log_info(
                f"[session {data.get('token')}] Connecting to {content.get('url')}..."
            )

            self.set("socket", socket)
            self.set("token", data.get("token"))
            self.set("scope", "user")

            try:
                log_info(
                    f"[session {data.get('token')}] Attempting to connect to socket..."
                )
                await socket.connect(content.get("url"), transports=["websocket"])
            except Exception as e:
                log_error(
                    f"[session {data.get('token')}] Failed to connect to socket: {e}"
                )
                await self.socket_disconnect()
                return 500

            return 200
        elif data.get("scope") == "client":
            additional_headers = {
                "Client-Id": CHZZK_CLIENT_ID(),
                "Client-Secret": CHZZK_CLIENT_SECRET(),
            }
            client = ChzzkClient()
            response = await client.get(
                "/open/v1/sessions/auth/client", additional_headers=additional_headers
            )

            if response.get("code") != 200:
                log_error(f"[session client] Failed to authenticate client: {response}")
                return response.get("code", 500)

            content = response.get("content", {})

            socket = AsyncClient()
            socket.on("SYSTEM", self.handle_system_message)
            socket.on("CHAT", self.handle_chat_message)
            socket.on("DONATION", self.handle_donation_message)
            socket.on("SUBSCRIPTION", self.handle_subscription_message)
            log_info(f"[session client] Connecting to {content.get('url')}...")

            self.set("socket", socket)
            self.set("scope", "client")

            try:
                log_info(f"[session client] Attempting to connect to socket...")
                await socket.connect(content.get("url"), transports=["websocket"])
            except Exception as e:
                log_error(f"[session client] Failed to connect to socket: {e}")
                await self.socket_disconnect()
                return 500

            return 200

        return 400


class SessionManager(metaclass=SingletonMeta):
    """
    Singleton class to manage session instances.
    """

    def __init__(self):
        self.sessions = {}

    def get_session(self, session_id):
        if session_id not in self.sessions:
            self.sessions[session_id] = ChzzkSession()
        return self.sessions[session_id]

    def clear_session(self, session_id):
        if session_id in self.sessions:
            self.sessions[session_id].clear()
            del self.sessions[session_id]
