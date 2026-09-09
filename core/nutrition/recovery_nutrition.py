"""REPRIGHT AI - Workout Recovery Nutrition Intelligence.

Analyzes telemetry from completed workout sessions (duration, volume, fatigue, stability)
to provide personalized, non-medical post-workout nutritional recommendations.
"""

from typing import Dict, Any, Optional


def generate_recovery_nutrition_insight(
    exercise_name: str = "SQUAT",
    duration_seconds: int = 600,
    clean_reps: int = 10,
    total_reps: int = 12,
    fatigue_level: str = "LOW",
    stability_score: float = 90.0,
    fitness_goal: str = "GENERAL_FITNESS"
) -> Dict[str, Any]:
    """Synthesizes workout mechanical load into practical post-training nutrition guidance."""
    fat = fatigue_level.upper().strip() if fatigue_level else "LOW"
    goal = fitness_goal.upper().strip() if fitness_goal else "GENERAL_FITNESS"
    ex = exercise_name.upper().strip() if exercise_name else "WORKOUT"

    mins = max(1, duration_seconds // 60)

    # 1. High Metabolic or Neuromuscular Load
    if fat in ("HIGH", "SEVERE") or mins >= 20:
        headline = f"High-Demand {ex} Session: Prioritize Rapid Glycogen & Amino Uptake"
        action = (
            "Your workout produced elevated neuromuscular fatigue. Aim for 25–30g of fast/moderate-digesting "
            "protein (e.g., paneer, eggs, whey, or soy/lentil bowl) paired with 40–50g complex carbohydrates "
            "within 45–60 minutes to rapidly halt muscle protein breakdown."
        )
        hydration = "Rehydrate with 500–750 ml of water. Consider adding lemon and rock salt or fresh coconut water for electrolyte balance."
        focus = "Rapid Glycogen Resynthesis & Cortisol Modulation"
        tag = "CRITICAL RECOVERY"
        tag_color = "#EF4444"
        ratio = "4:1"
        window = 30
        snacks = ["Chilled Sattu Buttermilk with roasted cumin", "Banana with 1 tbsp peanut butter", "Whey or Soy protein isolate shake"]

    # 2. Moderate Load
    elif fat == "MODERATE" or total_reps >= 15 or mins >= 10:
        headline = f"Steady {ex} Performance: Progressive Muscle Protein Synthesis"
        action = (
            "Solid training volume achieved. Include 20–25g protein with your next regular meal "
            "(e.g., moong dal chilla with paneer, dal with roti, or chicken breast with brown rice) "
            "to support steady tissue remodeling."
        )
        hydration = "Drink 500 ml of fresh water over the next hour to restore fluid balance."
        focus = "Steady Protein Synthesis & Cellular Hydration"
        tag = "ACTIVE RECOVERY"
        tag_color = "#14B8A6"
        ratio = "3:1"
        window = 45
        snacks = ["Sprouted Moong & Kala Chana salad", "Low-Fat Paneer Bhurji with 1 Phulka", "Boiled egg whites with black pepper"]

    # 3. Light / Technique Baseline
    else:
        headline = f"Technique-Focused {ex} Session: Maintain Baseline Nutrition"
        action = (
            "Movement stability remained high with minimal fatigue. Continue with your scheduled "
            "daily meal plan without requiring emergency surplus calories."
        )
        hydration = "Drink 300–400 ml of water and continue regular daily hydration pacing."
        focus = "Basal Metabolic Maintenance"
        tag = "OPTIMAL BASELINE"
        tag_color = "#22C55E"
        ratio = "2:1"
        window = 60
        snacks = ["Fresh tender coconut water", "Mixed roasted seeds & almonds", "Curd with pomegranate"]

    return {
        "exercise": ex,
        "exercise_name": ex,
        "duration_minutes": mins,
        "fatigue_level": fat,
        "stability_score": round(stability_score, 1),
        "headline": headline,
        "action_plan": action,
        "hydration_advice": hydration,
        "nutrient_focus": focus,
        "recovery_tag": tag,
        "tag_color": tag_color,
        "carb_to_protein_ratio": ratio,
        "recovery_window_minutes": window,
        "suggested_snacks": snacks,
        "disclaimer": "Educational fitness nutrition recommendation. Not medical or therapeutic advice."
    }
