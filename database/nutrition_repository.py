"""REPRIGHT AI - Nutrition Repository.

Data Access Object for Athlete Nutrition Profiles, Macro Plans, and Daily Hydration Logs.
Maintains strict user-level data isolation and transaction safety.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
import sqlite3
import json
from database.db_manager import get_connection
from database.models import NutritionProfile, NutritionPlan, HydrationLog


class NutritionRepository:
    """Repository managing Nutrition profiles, plans, and hydration telemetry in SQLite."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path

    def _get_conn(self) -> sqlite3.Connection:
        return get_connection(self.db_path)

    # --------------------------------------------------------------------------
    # 1. Nutrition Profiles
    # --------------------------------------------------------------------------
    def get_profile_by_user_id(self, user_id: int) -> Optional[NutritionProfile]:
        """Fetches an athlete's nutrition profile by user_id."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM nutrition_profiles WHERE user_id = ?",
                (user_id,)
            ).fetchone()
            if row:
                return NutritionProfile.from_row(row)
            return None
        finally:
            conn.close()

    def create_or_update_profile(
        self,
        user_id: int,
        age: int = 25,
        gender: str = "MALE",
        activity_level: str = "MODERATELY_ACTIVE",
        diet_preference: str = "VEGETARIAN",
        restrictions: str = ""
    ) -> NutritionProfile:
        """Upserts an athlete's nutrition parameters."""
        now = datetime.now().isoformat()
        conn = self._get_conn()
        try:
            with conn:
                existing = conn.execute(
                    "SELECT id FROM nutrition_profiles WHERE user_id = ?",
                    (user_id,)
                ).fetchone()

                if existing:
                    conn.execute(
                        """
                        UPDATE nutrition_profiles
                        SET age = ?, gender = ?, activity_level = ?, diet_preference = ?, restrictions = ?, updated_at = ?
                        WHERE user_id = ?
                        """,
                        (age, gender.upper(), activity_level.upper(), diet_preference.upper(), restrictions.strip(), now, user_id)
                    )
                    profile_id = existing["id"]
                else:
                    cursor = conn.execute(
                        """
                        INSERT INTO nutrition_profiles (
                            user_id, age, gender, activity_level, diet_preference, restrictions, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (user_id, age, gender.upper(), activity_level.upper(), diet_preference.upper(), restrictions.strip(), now, now)
                    )
                    profile_id = cursor.lastrowid

                return NutritionProfile(
                    id=profile_id,
                    user_id=user_id,
                    age=age,
                    gender=gender.upper(),
                    activity_level=activity_level.upper(),
                    diet_preference=diet_preference.upper(),
                    restrictions=restrictions.strip(),
                    created_at=now,
                    updated_at=now
                )
        finally:
            conn.close()

    # --------------------------------------------------------------------------
    # 2. Nutrition Plans
    # --------------------------------------------------------------------------
    def save_nutrition_plan(
        self,
        user_id: int,
        calorie_target: int,
        protein_target: float,
        carb_target: float,
        fat_target: float,
        bmi: float,
        bmr: float,
        tdee: float,
        goal: str,
        meal_plan_json: str
    ) -> int:
        """Archives a calculated nutrition plan for the user."""
        now = datetime.now().isoformat()
        conn = self._get_conn()
        try:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO nutrition_plans (
                        user_id, calorie_target, protein_target, carb_target, fat_target,
                        bmi, bmr, tdee, goal, meal_plan_json, generated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        int(calorie_target),
                        round(float(protein_target), 1),
                        round(float(carb_target), 1),
                        round(float(fat_target), 1),
                        round(float(bmi), 1),
                        round(float(bmr), 1),
                        round(float(tdee), 1),
                        goal.upper(),
                        meal_plan_json,
                        now
                    )
                )
                return cursor.lastrowid
        finally:
            conn.close()

    def get_latest_nutrition_plan(self, user_id: int) -> Optional[NutritionPlan]:
        """Fetches the most recently generated nutrition plan for a user."""
        conn = self._get_conn()
        try:
            row = conn.execute(
                """
                SELECT * FROM nutrition_plans
                WHERE user_id = ?
                ORDER BY id DESC LIMIT 1
                """,
                (user_id,)
            ).fetchone()
            if row:
                return NutritionPlan.from_row(row)
            return None
        finally:
            conn.close()

    def get_nutrition_plans_by_user(self, user_id: int, limit: int = 10) -> List[NutritionPlan]:
        """Retrieves history of generated nutrition plans for a given user."""
        conn = self._get_conn()
        try:
            rows = conn.execute(
                """
                SELECT * FROM nutrition_plans
                WHERE user_id = ?
                ORDER BY id DESC LIMIT ?
                """,
                (user_id, limit)
            ).fetchall()
            return [NutritionPlan.from_row(r) for r in rows]
        finally:
            conn.close()

    # --------------------------------------------------------------------------
    # 3. Daily Hydration Tracking
    # --------------------------------------------------------------------------
    def get_or_create_daily_hydration(
        self,
        user_id: int,
        date_str: Optional[str] = None,
        target_ml: int = 2500
    ) -> HydrationLog:
        """Retrieves or initializes today's hydration log for a user."""
        d = date_str or date.today().isoformat()
        now = datetime.now().isoformat()
        conn = self._get_conn()
        try:
            with conn:
                row = conn.execute(
                    "SELECT * FROM hydration_logs WHERE user_id = ? AND date = ?",
                    (user_id, d)
                ).fetchone()

                if row:
                    return HydrationLog.from_row(row)

                cursor = conn.execute(
                    """
                    INSERT INTO hydration_logs (user_id, date, target_ml, consumed_ml, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, d, target_ml, 0, now)
                )
                return HydrationLog(
                    id=cursor.lastrowid,
                    user_id=user_id,
                    date=d,
                    target_ml=target_ml,
                    consumed_ml=0,
                    updated_at=now
                )
        finally:
            conn.close()

    def get_daily_hydration(self, user_id: int, date_str: Optional[str] = None) -> Optional[HydrationLog]:
        """Retrieves hydration log for a specific date if it exists."""
        d = date_str or date.today().isoformat()
        conn = self._get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM hydration_logs WHERE user_id = ? AND date = ?",
                (user_id, d)
            ).fetchone()
            if row:
                return HydrationLog.from_row(row)
            return None
        finally:
            conn.close()

    def add_water_intake(
        self,
        user_id: int,
        amount_ml: int,
        date_str: Optional[str] = None,
        target_ml: int = 2500
    ) -> HydrationLog:
        """Increments today's consumed water intake in milliliters."""
        d = date_str or date.today().isoformat()
        now = datetime.now().isoformat()
        conn = self._get_conn()
        try:
            with conn:
                current = conn.execute(
                    "SELECT * FROM hydration_logs WHERE user_id = ? AND date = ?",
                    (user_id, d)
                ).fetchone()

                if current:
                    new_consumed = max(0, current["consumed_ml"] + amount_ml)
                    conn.execute(
                        "UPDATE hydration_logs SET consumed_ml = ?, updated_at = ? WHERE id = ?",
                        (new_consumed, now, current["id"])
                    )
                    return HydrationLog(
                        id=current["id"],
                        user_id=user_id,
                        date=d,
                        target_ml=current["target_ml"],
                        consumed_ml=new_consumed,
                        updated_at=now
                    )
                else:
                    new_consumed = max(0, amount_ml)
                    cursor = conn.execute(
                        """
                        INSERT INTO hydration_logs (user_id, date, target_ml, consumed_ml, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (user_id, d, target_ml, new_consumed, now)
                    )
                    return HydrationLog(
                        id=cursor.lastrowid,
                        user_id=user_id,
                        date=d,
                        target_ml=target_ml,
                        consumed_ml=new_consumed,
                        updated_at=now
                    )
        finally:
            conn.close()

    def reset_water_intake(
        self,
        user_id: int,
        date_str: Optional[str] = None,
        target_ml: int = 2500
    ) -> HydrationLog:
        """Resets today's water consumption counter to 0."""
        d = date_str or date.today().isoformat()
        now = datetime.now().isoformat()
        conn = self._get_conn()
        try:
            with conn:
                conn.execute(
                    """
                    INSERT INTO hydration_logs (user_id, date, target_ml, consumed_ml, updated_at)
                    VALUES (?, ?, ?, 0, ?)
                    ON CONFLICT(user_id, date) DO UPDATE SET consumed_ml = 0, updated_at = ?
                    """,
                    (user_id, d, target_ml, now, now)
                )
                row = conn.execute(
                    "SELECT * FROM hydration_logs WHERE user_id = ? AND date = ?",
                    (user_id, d)
                ).fetchone()
                return HydrationLog.from_row(row)
        finally:
            conn.close()
