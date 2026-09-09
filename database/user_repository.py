"""REPRIGHT AI - User Repository.

Data Access Object for User authentication, profile configuration, and credentials.
"""

from datetime import datetime
from typing import Optional, List
import sqlite3
from database.db_manager import get_connection
from database.models import User


class UserRepository:
    """Repository managing User records in SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)

    def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        height_cm: Optional[float] = None,
        weight_kg: Optional[float] = None,
        fitness_goal: str = "GENERAL_FITNESS"
    ) -> User:
        """Creates a new user record in the database."""
        now = datetime.now().isoformat()
        clean_email = email.strip().lower()
        clean_name = name.strip()

        conn = self._get_conn()
        try:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO users (name, email, password_hash, height_cm, weight_kg, fitness_goal, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (clean_name, clean_email, password_hash, height_cm, weight_kg, fitness_goal, now, now)
                )
                user_id = cursor.lastrowid
                return User(
                    id=user_id,
                    name=clean_name,
                    email=clean_email,
                    password_hash=password_hash,
                    height_cm=height_cm,
                    weight_kg=weight_kg,
                    fitness_goal=fitness_goal,
                    created_at=now,
                    updated_at=now
                )
        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Fetches a user by their unique primary key ID."""
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            if row:
                return User.from_row(row)
            return None
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Fetches a user by their case-insensitive email address."""
        clean_email = email.strip().lower()
        conn = self._get_conn()
        try:
            row = conn.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (clean_email,)).fetchone()
            if row:
                return User.from_row(row)
            return None
        finally:
            conn.close()

    def update_profile(
        self,
        user_id: int,
        name: str,
        height_cm: Optional[float],
        weight_kg: Optional[float],
        fitness_goal: str
    ) -> bool:
        """Updates user demographic and athletic profile info."""
        now = datetime.now().isoformat()
        conn = self._get_conn()
        try:
            with conn:
                cursor = conn.execute(
                    """
                    UPDATE users
                    SET name = ?, height_cm = ?, weight_kg = ?, fitness_goal = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (name.strip(), height_cm, weight_kg, fitness_goal, now, user_id)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def update_password(self, user_id: int, password_hash: str) -> bool:
        """Updates the password hash for a user."""
        now = datetime.now().isoformat()
        conn = self._get_conn()
        try:
            with conn:
                cursor = conn.execute(
                    "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                    (password_hash, now, user_id)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    def list_users(self) -> List[User]:
        """Returns all registered users."""
        conn = self._get_conn()
        try:
            rows = conn.execute("SELECT * FROM users ORDER BY name ASC").fetchall()
            return [User.from_row(r) for r in rows]
        finally:
            conn.close()

    def delete_user(self, user_id: int) -> bool:
        """Deletes a user and cascades deletion of workouts and telemetry."""
        conn = self._get_conn()
        try:
            with conn:
                cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
                return cursor.rowcount > 0
        finally:
            conn.close()
