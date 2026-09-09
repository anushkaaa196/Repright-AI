"""REPRIGHT AI Database Layer.

Provides persistent SQLite storage for user authentication, athlete profiles,
workout session debriefs, and rep-by-rep biomechanical telemetry.
"""

from database.db_manager import init_db, get_connection, set_db_path, get_db_path
from database.models import User, WorkoutSession, RepRecord, NutritionProfile, NutritionPlan, HydrationLog
from database.user_repository import UserRepository
from database.workout_repository import WorkoutRepository
from database.nutrition_repository import NutritionRepository

__all__ = [
    "init_db",
    "get_connection",
    "set_db_path",
    "get_db_path",
    "User",
    "WorkoutSession",
    "RepRecord",
    "NutritionProfile",
    "NutritionPlan",
    "HydrationLog",
    "UserRepository",
    "WorkoutRepository",
    "NutritionRepository",
]

