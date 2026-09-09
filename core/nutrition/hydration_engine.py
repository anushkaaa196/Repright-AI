"""REPRIGHT AI - Hydration Intelligence Engine.

Computes athletic daily water targets and progress tracking:
    Baseline Target (ml) = Body Weight (kg) * 35 ml/kg
    Workout Supplement = +500 ml for session rehydration
"""

from typing import Dict, Any, Tuple


def calculate_hydration_target(weight_kg: float, had_workout_today: bool = False) -> int:
    """Calculates daily hydration target in milliliters."""
    w = max(40.0, float(weight_kg)) if weight_kg else 70.0
    base_ml = w * 35.0

    if had_workout_today:
        base_ml += 500.0

    # Minimum 2000 ml (2.0L), maximum 4500 ml (4.5L) safe bounds
    target = int(round(max(2000.0, min(4500.0, base_ml))))
    return target


def format_hydration_display(consumed_ml: int, target_ml: int) -> Dict[str, Any]:
    """Generates formatted strings and progress metrics for UI display."""
    target = max(1, target_ml)
    consumed = max(0, consumed_ml)
    fraction = min(1.0, consumed / float(target))
    pct = int(round(fraction * 100.0))

    consumed_l = consumed / 1000.0
    target_l = target / 1000.0

    if fraction >= 1.0:
        status_msg = "Daily hydration target achieved! Optimal muscular and cellular hydration."
        badge_color = "#22C55E" # Emerald
    elif fraction >= 0.6:
        status_msg = "Good hydration pace. Continue drinking consistently through the evening."
        badge_color = "#14B8A6" # Teal
    else:
        status_msg = "Hydration below baseline. Drink a glass of water now to maintain performance."
        badge_color = "#F59E0B" # Amber

    return {
        "consumed_ml": consumed,
        "target_ml": target,
        "consumed_liters": round(consumed_l, 1),
        "target_liters": round(target_l, 1),
        "percentage": pct,
        "fraction": fraction,
        "display_text": f"{consumed_l:.1f} L / {target_l:.1f} L ({pct}%)",
        "status_message": status_msg,
        "badge_color": badge_color
    }
