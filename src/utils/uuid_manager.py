from uuid import uuid4
from queue import Queue
from time import time_ns, sleep as time_sleep
import threading

from .singleton import SingletonMeta
from ..core.logger import *


class UUIDManager(metaclass=SingletonMeta):
    """
    A class to manage UUID generation, validation, and cleanup.
    This class ensures that UUIDs are unique and provides methods to validate and remove them.
    It also includes a cleanup mechanism to remove old UUIDs after a certain period.
    """

    def __init__(self):
        self._id_set = set()
        self._id_queue = Queue()
        self._lock = threading.Lock()
        # Start a background thread to clean up old IDs
        cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        cleanup_thread.start()

    def generate_id(self) -> str:
        """
        Generate a unique UUID4 string.
        """
        new_id = str(uuid4())
        self._id_set.add(new_id)
        self._id_queue.put((new_id, time_ns()))
        log_debug(f"Generated new ID: {new_id}")
        return new_id

    def validate_id(self, id_str: str) -> bool:
        """
        Validate if the given ID exists in the set.
        """
        if id_str not in self._id_set:
            log_warning(f"Invalid ID attempted: {id_str}")
            return False
        return True

    def remove_id(self, id_str: str) -> bool:
        """
        Remove the given ID from the set.
        """
        if id_str in self._id_set:
            self._id_set.remove(id_str)
            log_debug(f"Removed ID: {id_str}")
            return True
        log_warning(f"Attempted to remove non-existent ID: {id_str}")
        return False

    def _cleanup_ids(self, age_limit_ns: int = 300_000_000_000) -> None:
        """
        Cleanup IDs older than the specified age limit in nanoseconds.
        Default is 5 minutes (300 billion nanoseconds).\
        """
        log_debug("Starting cleanup of old IDs")
        current_time = time_ns()
        # Remove IDs from the queue and set if they are older than the age limit or no longer in the set
        while not self._id_queue.empty():
            id_str, timestamp = self._id_queue.queue[0]
            if current_time - timestamp <= age_limit_ns and id_str in self._id_set:
                break  # IDs are within the age limit and still valid
            self._id_queue.get()
            self._id_set.discard(id_str)  # Remove from set if it exists

    def _cleanup_loop(self, interval_ns: int = 60_000_000_000) -> None:
        """
        Continuously cleanup IDs at specified intervals.
        Default interval is 60 seconds (60 billion nanoseconds).
        """
        while True:
            self._cleanup_ids()
            time_sleep(interval_ns / 1_000_000_000)

    def __del__(self):
        log_debug("Cleaning up UUIDManager resources")
        # Ensure thread safety during cleanup and clear all resources
        with self._lock:
            self._id_set.clear()
            while not self._id_queue.empty():
                self._id_queue.get()


# Singleton access functions
def get_uuid_manager() -> UUIDManager:
    """
    Get the singleton instance of UUIDManager.
    """
    return UUIDManager()


def generate_uuid() -> str:
    """
    Generate a unique UUID using the UUIDManager singleton.
    """
    return get_uuid_manager().generate_id()


def validate_uuid(id_str: str) -> bool:
    """
    Validate a UUID using the UUIDManager singleton.
    """
    return get_uuid_manager().validate_id(id_str)


def remove_uuid(id_str: str) -> bool:
    """
    Remove a UUID using the UUIDManager singleton.
    """
    return get_uuid_manager().remove_id(id_str)
