from ..utils.singleton import SingletonMeta
from ..db.database import database


class SessionError(Exception):
    """Custom exception for session-related errors."""

    pass


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
