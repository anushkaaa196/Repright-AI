"""REPRIGHT AI - Macronutrient Intelligence Engine.

Computes mathematically balanced, goal-aligned daily targets for Protein, Carbohydrates,
and Healthy Fats with guaranteed internal caloric consistency:
    (Protein * 4) + (Carbohydrates * 4) + (Fats * 9) ≈ Daily Caloric Target
"""

from typing import Dict, Any


def calculate_macronutrients(
    weight_kg: float,
    daily_calories: int,
    fitness_goal: str = "GENERAL_FITNESS",
    activity_level: str = "MODERATELY_ACTIVE"
) -> Dict[str, Any]:
    """Calculates macro distributions aligned with athletic exercise research."""
    goal_key = fitness_goal.upper().strip() if fitness_goal else "GENERAL_FITNESS"
    w = max(40.0, float(weight_kg)) if weight_kg else 70.0
    cals = max(1200, int(daily_calories))

    # 1. Protein Target (g per kg body weight)
    if goal_key in ("HYPERTROPHY", "MUSCLE_GAIN", "MUSCLE_BUILDING", "STRENGTH"):
        protein_multiplier = 2.0  # High MPS (muscle protein synthesis) threshold
    elif goal_key in ("WEIGHT_LOSS", "FAT_LOSS"):
        protein_multiplier = 1.8  # Satiety & lean tissue preservation during caloric deficit
    elif goal_key == "ENDURANCE":
        protein_multiplier = 1.5  # Muscular repair for sustained oxidative stress
    else:
        protein_multiplier = 1.6  # Optimal athletic baseline

    raw_protein_g = round(w * protein_multiplier, 1)
    prot_int = int(round(raw_protein_g))
    protein_calories = prot_int * 4

    # 2. Healthy Fats (25% - 28% of total daily energy for hormonal & joint integrity)
    if goal_key in ("WEIGHT_LOSS", "FAT_LOSS"):
        fat_pct = 0.25
    elif goal_key in ("HYPERTROPHY", "MUSCLE_GAIN", "MUSCLE_BUILDING", "STRENGTH"):
        fat_pct = 0.26
    else:
        fat_pct = 0.27

    raw_fat_calories = cals * fat_pct
    fat_int = int(round(raw_fat_calories / 9.0))
    fat_calories = fat_int * 9

    # 3. Carbohydrates (Remainder of caloric allocation to fuel kinetic power)
    remaining_calories = cals - (protein_calories + fat_calories)
    carb_int = max(30, int(round(remaining_calories / 4.0)))
    carb_calories = carb_int * 4

    computed_cals = protein_calories + carb_calories + fat_calories

    # Percentage breakdown of energy
    p_energy_pct = round((prot_int * 4 / computed_cals) * 100.0, 1) if computed_cals > 0 else 25.0
    c_energy_pct = round((carb_int * 4 / computed_cals) * 100.0, 1) if computed_cals > 0 else 50.0
    f_energy_pct = round((fat_int * 9 / computed_cals) * 100.0, 1) if computed_cals > 0 else 25.0

    return {
        "daily_calories": cals,
        "computed_calories": computed_cals,
        "protein_g": prot_int,
        "carbs_g": carb_int,
        "fat_g": fat_int,
        "protein_calories": prot_int * 4,
        "carbs_calories": carb_int * 4,
        "fat_calories": fat_int * 9,
        "protein_multiplier": protein_multiplier,
        "protein_energy_pct": p_energy_pct,
        "carbs_energy_pct": c_energy_pct,
        "fat_energy_pct": f_energy_pct,
        "consistency_delta": abs(computed_cals - cals)
    }
