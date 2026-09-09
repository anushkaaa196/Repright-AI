"""REPRIGHT AI - Nutrition Service.

High-level business logic orchestrating athletic dietary calculations,
profile management, macro balance, hydration logs, and post-workout nutrition insights.
"""

from typing import Optional, Dict, Any, Tuple
import json
from datetime import date
from database.models import User, NutritionProfile, NutritionPlan, HydrationLog
from database.user_repository import UserRepository
from database.nutrition_repository import NutritionRepository
from core.nutrition import (
    compute_complete_nutrition_intelligence,
    calculate_hydration_target,
    generate_recovery_nutrition_insight
)


class NutritionService:
    """Service handling personalized nutrition planning, macros, and hydration tracking."""

    def __init__(
        self,
        nutrition_repo: Optional[NutritionRepository] = None,
        user_repo: Optional[UserRepository] = None,
        db_path: Optional[str] = None
    ):
        self.nutrition_repo = nutrition_repo or NutritionRepository(db_path=db_path)
        self.user_repo = user_repo or UserRepository(db_path=db_path)
        self.db_path = db_path
        self._latest_recovery_cache: Dict[int, Dict[str, Any]] = {}

    def get_or_create_profile(self, user_id: int) -> NutritionProfile:
        """Fetches or creates a default athletic nutrition profile for a user."""
        profile = self.nutrition_repo.get_profile_by_user_id(user_id)
        if not profile:
            profile = self.nutrition_repo.create_or_update_profile(
                user_id=user_id,
                age=25,
                gender="MALE",
                activity_level="MODERATELY_ACTIVE",
                diet_preference="VEGETARIAN",
                restrictions=""
            )
        return profile

    def update_profile(
        self,
        user_id: int,
        age: int = 25,
        gender: str = "MALE",
        activity_level: str = "MODERATELY_ACTIVE",
        diet_preference: str = "VEGETARIAN",
        restrictions: str = ""
    ) -> NutritionProfile:
        """Updates user nutrition preferences and refreshes active plan."""
        profile = self.nutrition_repo.create_or_update_profile(
            user_id=user_id,
            age=age,
            gender=gender,
            activity_level=activity_level,
            diet_preference=diet_preference,
            restrictions=restrictions
        )
        # Recompute and persist updated plan
        self.generate_and_save_plan(user_id)
        return profile

    def generate_and_save_plan(self, user_id: int) -> Tuple[NutritionPlan, Dict[str, Any]]:
        """Computes a complete, validated nutrition plan and archives it to SQLite."""
        user = self.user_repo.get_user_by_id(user_id)
        profile = self.get_or_create_profile(user_id)

        # Baseline physical metrics with safe defaults
        h = user.height_cm if user and user.height_cm else 175.0
        w = user.weight_kg if user and user.weight_kg else 70.0
        goal = user.fitness_goal if user and user.fitness_goal else "GENERAL_FITNESS"

        intelligence = compute_complete_nutrition_intelligence(
            height_cm=h,
            weight_kg=w,
            fitness_goal=goal,
            age=profile.age,
            gender=profile.gender,
            activity_level=profile.activity_level,
            diet_preference=profile.diet_preference,
            restrictions=profile.restrictions
        )

        ee = intelligence["energy_expenditure"]
        macros = intelligence["macronutrients"]
        meal_json = json.dumps(intelligence["meal_plan"])

        plan_id = self.nutrition_repo.save_nutrition_plan(
            user_id=user_id,
            calorie_target=ee["calorie_target"],
            protein_target=macros["protein_g"],
            carb_target=macros["carbs_g"],
            fat_target=macros["fat_g"],
            bmi=ee["bmi"],
            bmr=ee["bmr"],
            tdee=ee["tdee"],
            goal=goal,
            meal_plan_json=meal_json
        )

        plan = self.nutrition_repo.get_latest_nutrition_plan(user_id)
        return plan, intelligence

    def get_current_plan(self, user_id: int) -> Tuple[NutritionPlan, Dict[str, Any]]:
        """Returns the active plan, generating one automatically if none exists."""
        plan = self.nutrition_repo.get_latest_nutrition_plan(user_id)
        if not plan:
            return self.generate_and_save_plan(user_id)

        # Parse stored meal plan or recompute full payload
        try:
            meal_dict = json.loads(plan.meal_plan_json)
        except Exception:
            return self.generate_and_save_plan(user_id)

        user = self.user_repo.get_user_by_id(user_id)
        profile = self.get_or_create_profile(user_id)
        h = user.height_cm if user and user.height_cm else 175.0
        w = user.weight_kg if user and user.weight_kg else 70.0

        full_payload = {
            "user_metrics": {
                "height_cm": h,
                "weight_kg": w,
                "age": profile.age,
                "gender": profile.gender,
                "fitness_goal": plan.goal,
                "activity_level": profile.activity_level,
                "diet_preference": profile.diet_preference,
                "restrictions": profile.restrictions
            },
            "energy_expenditure": {
                "bmi": plan.bmi,
                "bmr": plan.bmr,
                "tdee": plan.tdee,
                "calorie_target": plan.calorie_target
            },
            "macronutrients": {
                "daily_calories": plan.calorie_target,
                "protein_g": plan.protein_target,
                "carbs_g": plan.carb_target,
                "fat_g": plan.fat_target,
                "protein_calories": plan.protein_target * 4,
                "carbs_calories": plan.carb_target * 4,
                "fat_calories": plan.fat_target * 9
            },
            "meal_plan": meal_dict,
            "hydration_target_ml": calculate_hydration_target(w)
        }
        return plan, full_payload

    # --------------------------------------------------------------------------
    # Hydration
    # --------------------------------------------------------------------------
    def get_daily_hydration(self, user_id: int) -> HydrationLog:
        """Fetches or initializes today's hydration log based on user weight."""
        user = self.user_repo.get_user_by_id(user_id)
        w = user.weight_kg if user and user.weight_kg else 70.0
        target = calculate_hydration_target(w)
        return self.nutrition_repo.get_or_create_daily_hydration(user_id, target_ml=target)

    def log_water(self, user_id: int, amount_ml: int) -> HydrationLog:
        """Adds water consumption to today's log."""
        user = self.user_repo.get_user_by_id(user_id)
        w = user.weight_kg if user and user.weight_kg else 70.0
        target = calculate_hydration_target(w)
        return self.nutrition_repo.add_water_intake(user_id, amount_ml=amount_ml, target_ml=target)

    def reset_water(self, user_id: int) -> HydrationLog:
        """Resets today's water counter to 0."""
        user = self.user_repo.get_user_by_id(user_id)
        w = user.weight_kg if user and user.weight_kg else 70.0
        target = calculate_hydration_target(w)
        return self.nutrition_repo.reset_water_intake(user_id, target_ml=target)

    # --------------------------------------------------------------------------
    # Workout Recovery Nutrition
    # --------------------------------------------------------------------------
    def record_workout_recovery_insight(
        self,
        user_id: int,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates and caches recovery insight from completed workout debrief."""
        user = self.user_repo.get_user_by_id(user_id)
        goal = user.fitness_goal if user and user.fitness_goal else "GENERAL_FITNESS"

        exercise = session_data.get("exercise", "SQUAT")
        dur = session_data.get("duration", 600)
        clean = session_data.get("clean_reps", 10)
        total = session_data.get("total_reps", 12)

        mv = session_data.get("movement_intelligence") or {}
        fat = mv.get("fatigue", {}).get("fatigue_level", "LOW")
        stab = mv.get("stability", {}).get("stability_score", 90.0)

        insight = generate_recovery_nutrition_insight(
            exercise_name=exercise,
            duration_seconds=dur,
            clean_reps=clean,
            total_reps=total,
            fatigue_level=fat,
            stability_score=stab,
            fitness_goal=goal
        )
        self._latest_recovery_cache[user_id] = insight
        return insight

    def get_latest_recovery_insight(self, user_id: int) -> Dict[str, Any]:
        """Returns cached recovery insight or a general baseline suggestion."""
        if user_id in self._latest_recovery_cache:
            return self._latest_recovery_cache[user_id]

        user = self.user_repo.get_user_by_id(user_id)
        goal = user.fitness_goal if user and user.fitness_goal else "GENERAL_FITNESS"
        return generate_recovery_nutrition_insight(
            exercise_name="DAILY TRAINING",
            duration_seconds=900,
            clean_reps=10,
            total_reps=12,
            fatigue_level="LOW",
            stability_score=90.0,
            fitness_goal=goal
        )
