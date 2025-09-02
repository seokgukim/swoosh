from ..utils.singleton import SingletonMeta
from ..db.database import database
from ..api.client import ChzzkClient
from socketio import AsyncClient


class ChzzkSession:
    """
    A simple session management class to store and retrieve session data.
    """

    def __init__(self):
        self.session_data = {}

    def set(self, key, value):
        self.session_data[key] = value

    def get(self, key, default=None):
        return self.session_data.get(key, default)

    def clear(self):
        self.session_data.clear()

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

            if "url" not in response:
                return 401

        elif data.get("scope") == "client":
            return 200
        else:
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
