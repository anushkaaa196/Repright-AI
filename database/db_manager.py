"""REPRIGHT AI - Database Manager.

Manages SQLite database connection lifecycle, auto-initialization, schema definitions,
and connection pooling for REPRIGHT AI's persistent storage.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional

# Default database location inside project directory: database/truform.db
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = str(_PROJECT_ROOT / "database" / "truform.db")

_CURRENT_DB_PATH: str = DEFAULT_DB_PATH


def set_db_path(path: str) -> None:
    """Overrides the database path (useful for automated testing or in-memory tests)."""
    global _CURRENT_DB_PATH
    _CURRENT_DB_PATH = path


def get_db_path() -> str:
    """Returns the current database file path."""
    return _CURRENT_DB_PATH


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a new SQLite connection configured with Row factory and Pragmas."""
    target_path = db_path or _CURRENT_DB_PATH

    # If file-based and not in-memory, ensure parent directory exists
    if target_path != ":memory:":
        parent_dir = Path(target_path).parent
        parent_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(target_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # Enable SQLite pragmas
    conn.execute("PRAGMA foreign_keys = ON;")
    if target_path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL;")

    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Initializes database tables, constraints, and indexes if they do not exist."""
    conn = get_connection(db_path)
    try:
        with conn:
            # 1. Users Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    height_cm REAL,
                    weight_kg REAL,
                    fitness_goal TEXT DEFAULT 'GENERAL_FITNESS',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

            # 2. Workout Sessions Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workout_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    exercise_name TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    duration_seconds INTEGER DEFAULT 0,
                    total_reps INTEGER DEFAULT 0,
                    clean_reps INTEGER DEFAULT 0,
                    average_quality REAL DEFAULT 0.0,
                    best_rep_quality REAL DEFAULT 0.0,
                    consistency_score REAL DEFAULT 0.0,
                    stability_score REAL DEFAULT 0.0,
                    fatigue_level TEXT DEFAULT 'LOW',
                    risk_level TEXT DEFAULT 'LOW',
                    session_trajectory TEXT DEFAULT 'STABLE',
                    created_at TEXT NOT NULL
                );
            """)

            # 3. Repetition Biomechanical History Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rep_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
                    rep_number INTEGER NOT NULL,
                    quality_score REAL NOT NULL,
                    range_of_motion REAL DEFAULT 100.0,
                    joint_alignment REAL DEFAULT 100.0,
                    core_stability REAL DEFAULT 100.0,
                    movement_control REAL DEFAULT 100.0,
                    movement_cadence REAL DEFAULT 100.0,
                    is_clean INTEGER DEFAULT 1,
                    rep_result TEXT DEFAULT 'CLEAN',
                    created_at TEXT NOT NULL
                );
            """)

            # 4. Nutrition Profiles Table (Phase 7C)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS nutrition_profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    age INTEGER DEFAULT 25,
                    gender TEXT DEFAULT 'MALE',
                    activity_level TEXT DEFAULT 'MODERATELY_ACTIVE',
                    diet_preference TEXT DEFAULT 'VEGETARIAN',
                    restrictions TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)

            # 5. Nutrition Plans Table (Phase 7C)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS nutrition_plans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    calorie_target INTEGER NOT NULL,
                    protein_target REAL NOT NULL,
                    carb_target REAL NOT NULL,
                    fat_target REAL NOT NULL,
                    bmi REAL NOT NULL,
                    bmr REAL NOT NULL,
                    tdee REAL NOT NULL,
                    goal TEXT NOT NULL,
                    meal_plan_json TEXT NOT NULL,
                    generated_at TEXT NOT NULL
                );
            """)

            # 6. Hydration Logs Table (Phase 7C)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS hydration_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    date TEXT NOT NULL,
                    target_ml INTEGER NOT NULL,
                    consumed_ml INTEGER DEFAULT 0,
                    updated_at TEXT NOT NULL,
                    UNIQUE(user_id, date)
                );
            """)

            # Performance Indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON workout_sessions(user_id, created_at);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_reps_session ON rep_history(session_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_nutrition_profile_user ON nutrition_profiles(user_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_nutrition_plans_user ON nutrition_plans(user_id, generated_at);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_hydration_logs_user_date ON hydration_logs(user_id, date);")


    finally:
        conn.close()
