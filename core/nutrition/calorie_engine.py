"""REPRIGHT AI - Calorie & Energy Expenditure Engine.

Calculates Body Mass Index (BMI), Basal Metabolic Rate (BMR using Mifflin-St Jeor),
Total Daily Energy Expenditure (TDEE), and goal-adjusted daily caloric targets.
All values are designated as non-medical educational fitness estimates.
"""

from typing import Dict, Any, Optional, Tuple


ACTIVITY_MULTIPLIERS = {
    "SEDENTARY": 1.2,          # Desk job, little/no formal exercise
    "LIGHTLY_ACTIVE": 1.375,   # Light exercise 1-3 days/week
    "MODERATELY_ACTIVE": 1.55, # Moderate exercise 3-5 days/week
    "VERY_ACTIVE": 1.725       # Heavy training 6-7 days/week
}

GOAL_CALORIE_MODIFIERS = {
    "WEIGHT_LOSS": -450,       # Moderate fat-loss deficit
    "FAT_LOSS": -450,
    "HYPERTROPHY": 350,        # Moderate lean surplus
    "MUSCLE_GAIN": 350,
    "MUSCLE_BUILDING": 350,
    "STRENGTH": 200,           # Slight recovery surplus
    "ENDURANCE": 100,          # High-output fuel replenishment
    "GENERAL_FITNESS": 0,      # Maintenance
    "MOBILITY": 0,
    "REHABILITATION": 0
}


def calculate_bmi(height_cm: float, weight_kg: float) -> Tuple[float, str]:
    """Calculates BMI and returns (bmi_value, category_label)."""
    if height_cm <= 0 or weight_kg <= 0:
        return 0.0, "UNKNOWN"

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)

    if bmi < 18.5:
        category = "UNDERWEIGHT"
    elif bmi < 25.0:
        category = "NORMAL"
    elif bmi < 30.0:
        category = "OVERWEIGHT"
    else:
        category = "OBESE"

    return bmi, category


def calculate_bmr(height_cm: float, weight_kg: float, age: int = 25, gender: str = "MALE") -> float:
    """Calculates Basal Metabolic Rate using the clinical Mifflin-St Jeor equation.

    Men:   BMR = 10 * weight(kg) + 6.25 * height(cm) - 5 * age + 5
    Women: BMR = 10 * weight(kg) + 6.25 * height(cm) - 5 * age - 161
    """
    if height_cm <= 0 or weight_kg <= 0 or age <= 0:
        return 0.0

    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    g = gender.upper().strip() if gender else "MALE"

    if g == "FEMALE":
        bmr = base - 161.0
    elif g == "MALE":
        bmr = base + 5.0
    else:
        # Neutral midpoint
        bmr = base - 78.0

    return round(bmr, 1)


def calculate_tdee(bmr: float, activity_level: str = "MODERATELY_ACTIVE") -> float:
    """Calculates Total Daily Energy Expenditure by applying the activity multiplier."""
    act_key = activity_level.upper().strip() if activity_level else "MODERATELY_ACTIVE"
    multiplier = ACTIVITY_MULTIPLIERS.get(act_key, 1.55)
    tdee = bmr * multiplier
    return round(tdee, 1)


def calculate_daily_calorie_target(
    tdee: float,
    fitness_goal: str = "GENERAL_FITNESS",
    gender: str = "MALE"
) -> Tuple[int, int, str]:
    """Calculates personalized daily calorie intake recommendation based on training objective.

    Returns:
        (target_calories, delta_calories, rationale)
    """
    if tdee <= 0:
        return 2000, 0, "Default maintenance baseline."

    goal_key = fitness_goal.upper().strip() if fitness_goal else "GENERAL_FITNESS"
    delta = GOAL_CALORIE_MODIFIERS.get(goal_key, 0)
    target = int(round(tdee + delta))

    # Safe biological minimums to avoid aggressive starvation deficits
    min_floor = 1200 if gender.upper().strip() == "FEMALE" else 1500
    if target < min_floor:
        target = min_floor
        delta = target - int(round(tdee))

    if delta < 0:
        rationale = f"Moderate caloric deficit ({abs(delta)} kcal) to promote sustainable fat loss while preserving lean mass."
    elif delta > 0:
        rationale = f"Controlled caloric surplus (+{delta} kcal) to optimize progressive overload and muscular hypertrophy."
    else:
        rationale = "Energy balance maintained at TDEE baseline for athletic conditioning and metabolic stability."

    return target, delta, rationale
