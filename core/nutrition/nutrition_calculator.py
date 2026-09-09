"""REPRIGHT AI - Unified Nutrition Intelligence Calculator.

Orchestrates BMI, BMR (Mifflin-St Jeor), TDEE, caloric targets, macronutrient balance,
Indian-adapted meal recommendations, and daily hydration estimates.
"""

from typing import Dict, Any, Optional
from core.nutrition.calorie_engine import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    calculate_daily_calorie_target
)
from core.nutrition.macro_calculator import calculate_macronutrients
from core.nutrition.meal_recommender import generate_meal_plan
from core.nutrition.hydration_engine import calculate_hydration_target


def compute_complete_nutrition_intelligence(
    height_cm: float,
    weight_kg: float,
    fitness_goal: str = "GENERAL_FITNESS",
    age: int = 25,
    gender: str = "MALE",
    activity_level: str = "MODERATELY_ACTIVE",
    diet_preference: str = "VEGETARIAN",
    restrictions: str = ""
) -> Dict[str, Any]:
    """Generates complete, verified personalized nutritional recommendations."""
    # 1. Body Mass Index
    bmi_val, bmi_cat = calculate_bmi(height_cm, weight_kg)

    # 2. Basal Metabolic Rate
    bmr_val = calculate_bmr(height_cm, weight_kg, age=age, gender=gender)

    # 3. Total Daily Energy Expenditure
    tdee_val = calculate_tdee(bmr_val, activity_level=activity_level)

    # 4. Goal-Aligned Calorie Target
    target_cals, cal_delta, cal_rationale = calculate_daily_calorie_target(
        tdee_val, fitness_goal=fitness_goal, gender=gender
    )

    # 5. Macronutrient Distribution
    macros = calculate_macronutrients(
        weight_kg=weight_kg,
        daily_calories=target_cals,
        fitness_goal=fitness_goal,
        activity_level=activity_level
    )

    # 6. Practical Indian Meal Plan
    meal_plan = generate_meal_plan(
        diet_preference=diet_preference,
        fitness_goal=fitness_goal,
        daily_calories=target_cals,
        protein_target_g=macros["protein_g"],
        restrictions=restrictions
    )

    # 7. Estimated Hydration Target
    hydration_ml = calculate_hydration_target(weight_kg, had_workout_today=False)

    return {
        "user_metrics": {
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "age": age,
            "gender": gender,
            "fitness_goal": fitness_goal,
            "activity_level": activity_level,
            "diet_preference": diet_preference,
            "restrictions": restrictions
        },
        "energy_expenditure": {
            "bmi": bmi_val,
            "bmi_category": bmi_cat,
            "bmr": bmr_val,
            "tdee": tdee_val,
            "calorie_target": target_cals,
            "calorie_delta": cal_delta,
            "rationale": cal_rationale
        },
        "macronutrients": macros,
        "meal_plan": meal_plan,
        "hydration_target_ml": hydration_ml,
        "disclaimer": "AI-estimated athletic nutrition intelligence for educational guidance. Not medical or therapeutic advice."
    }
