"""REPRIGHT AI - User Session Management.

Thread-safe Singleton managing the currently authenticated athlete session,
profile event dispatching, and guest mode fallback.
"""

from typing import Optional, Callable, List
import threading
from database.models import User
from database.user_repository import UserRepository
from database.db_manager import init_db


class UserSession:
    """Singleton session controller maintaining active user identity across the application."""

    _instance: Optional["UserSession"] = None
    _lock = threading.Lock()

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._current_user: Optional[User] = None
        self._listeners: List[Callable[[Optional[User]], None]] = []
        self._initialized = True

    @classmethod
    def get_instance(cls) -> "UserSession":
        """Thread-safe singleton accessor."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Resets the singleton instance (useful for unit testing)."""
        with cls._lock:
            cls._instance = None

    def is_authenticated(self) -> bool:
        """Returns True if a user is actively authenticated."""
        return self._current_user is not None

    def get_current_user(self) -> Optional[User]:
        """Returns the currently authenticated User, or None if guest."""
        return self._current_user

    def set_current_user(self, user: Optional[User]) -> None:
        """Sets the active user and dispatches notification to registered listeners."""
        self._current_user = user
        self._notify_listeners()

    def logout(self) -> None:
        """Logs out the active user session."""
        self._current_user = None
        self._notify_listeners()

    def add_listener(self, callback: Callable[[Optional[User]], None]) -> None:
        """Registers a callback invoked whenever the user session changes."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[Optional[User]], None]) -> None:
        """Unregisters a previously added session change callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self) -> None:
        """Invokes all registered callbacks with the new current_user state."""
        for listener in list(self._listeners):
            try:
                listener(self._current_user)
            except Exception as e:
                print(f"[UserSession] Listener dispatch error: {e}")

    def get_or_create_default_user(self, db_path: Optional[str] = None) -> User:
        """Ensures a default athlete user exists in DB and returns it (for guest/headless mode)."""
        init_db(db_path)
        user_repo = UserRepository(db_path)
        guest_email = "guest@truform.ai"
        user = user_repo.get_user_by_email(guest_email)
        if not user:
            from services.auth_service import hash_password
            user = user_repo.create_user(
                name="RepRight Athlete",
                email=guest_email,
                password_hash=hash_password("athlete123"),
                height_cm=175.0,
                weight_kg=72.0,
                fitness_goal="STRENGTH"
            )
        self._current_user = user
        return user
