"""REPRIGHT AI - Nutrition & Diet Intelligence Package.

Provides personalized caloric, macronutrient, Indian meal planning,
hydration tracking, and workout recovery nutrition algorithms.
"""

from core.nutrition.calorie_engine import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    calculate_daily_calorie_target,
    ACTIVITY_MULTIPLIERS,
    GOAL_CALORIE_MODIFIERS
)
from core.nutrition.macro_calculator import calculate_macronutrients
from core.nutrition.meal_recommender import generate_meal_plan, MEAL_CATALOG
from core.nutrition.hydration_engine import (
    calculate_hydration_target,
    format_hydration_display
)
from core.nutrition.recovery_nutrition import generate_recovery_nutrition_insight
from core.nutrition.nutrition_calculator import compute_complete_nutrition_intelligence

calculate_target_calories = calculate_daily_calorie_target
recommend_daily_meals = generate_meal_plan

__all__ = [
    "calculate_bmi",
    "calculate_bmr",
    "calculate_tdee",
    "calculate_daily_calorie_target",
    "calculate_target_calories",
    "calculate_macronutrients",
    "generate_meal_plan",
    "recommend_daily_meals",
    "calculate_hydration_target",
    "format_hydration_display",
    "generate_recovery_nutrition_insight",
    "compute_complete_nutrition_intelligence",
    "ACTIVITY_MULTIPLIERS",
    "GOAL_CALORIE_MODIFIERS",
    "MEAL_CATALOG"
]
