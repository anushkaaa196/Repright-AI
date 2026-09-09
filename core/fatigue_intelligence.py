"""Fatigue & Form Degradation Detection Engine for REPRIGHT AI.

Performs explainable, heuristic estimation of movement form degradation over time.
Analyzes multi-repetition score trajectories, rising instability, range-of-motion decay,
and correction frequency to identify workout fatigue.

NOTE: This provides educational biomechanical guidance and does NOT provide medical
or clinical fatigue diagnosis.
"""

from typing import Dict, Any, List, Optional
from core.rep_history import RepHistoryTracker
from core.exercise_registry import is_active_ai_supported


def estimate_form_fatigue(
    exercise_name: str,
    current_stability_score: int = 85,
    stats_snapshot: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Estimates form degradation and fatigue based on rep history and current stability.

    Returns:
        FatigueResult dictionary.
    """
    ex = exercise_name.upper().strip()
    is_active = is_active_ai_supported(ex)

    if not is_active:
        return {
            "exercise": ex,
            "fatigue_level": "LOW",
            "fatigue_label": "🟢 LOW FORM FATIGUE",
            "fatigue_score": 15,
            "quality_trend": "STABLE",
            "stability_trend": "STABLE",
            "cadence_trend": "CONSISTENT",
            "recommended_action": "Continue following guided biomechanical reference cues.",
            "details": ["Guided reference training mode active."],
            "is_guided": True,
            "disclaimer": "AI-Estimated Form Fatigue • Educational Guidance"
        }

    tracker = RepHistoryTracker.get_instance()
    reps = tracker.get_all_reps()
    total_reps = len(reps)

    # Base fatigue parameters
    fatigue_points = 10
    details: List[str] = []
    quality_trend = "STABLE"
    stability_trend = "STABLE"
    cadence_trend = "CONSISTENT"

    if total_reps >= 3:
        # Check rep quality trend (first half vs second half or last 3 vs first 3)
        recent_reps = reps[-3:]
        early_reps = reps[:3]

        recent_avg = sum(r["overall_score"] for r in recent_reps) / len(recent_reps)
        early_avg = sum(r["overall_score"] for r in early_reps) / len(early_reps)
        delta_quality = recent_avg - early_avg

        if delta_quality < -10:
            fatigue_points += 35
            quality_trend = "DECLINING"
            details.append(f"Recent repetition scores dropped by {abs(int(delta_quality))}% compared to session start.")
        elif delta_quality > 5:
            quality_trend = "IMPROVING"
        else:
            quality_trend = "STABLE"

        # Check range of motion reduction
        recent_rom = [r.get("dimension_scores", {}).get("range_of_motion", 80) for r in recent_reps]
        if recent_rom and sum(recent_rom) / len(recent_rom) < 70:
            fatigue_points += 20
            details.append("Incomplete range of motion observed in recent repetitions.")

        # Check volume accumulation
        if total_reps >= 20:
            fatigue_points += 25
            details.append("High training volume accumulated (20+ reps).")
        elif total_reps >= 12:
            fatigue_points += 15
            details.append("Moderate training volume completed (12+ reps).")

    # Check stability degradation
    if current_stability_score < 55:
        fatigue_points += 30
        stability_trend = "DECLINING"
        details.append("Elevated movement instability and joint jitter detected.")
    elif current_stability_score < 75:
        fatigue_points += 15
        stability_trend = "VARIABLE"
        details.append("Moderate movement sway observed.")

    # Check warning ratio
    if stats_snapshot:
        warnings = stats_snapshot.get("posture_warnings", 0)
        attempts = max(stats_snapshot.get("total_attempts", 0), 1)
        if (warnings / attempts) > 0.4:
            fatigue_points += 20
            details.append("Frequent posture corrections triggered during movement cycles.")

    fatigue_score = max(10, min(100, fatigue_points))

    # Determine fatigue level
    if fatigue_score >= 65:
        fatigue_level = "HIGH"
        label = "🔴 HIGH FORM FATIGUE"
        action = "Take a 60–90s recovery break. Reset your posture before attempting more sets."
    elif fatigue_score >= 40:
        fatigue_level = "MODERATE"
        label = "🟡 MODERATE FORM FATIGUE"
        action = "Pause for 30 seconds; prioritize depth control over speed."
    else:
        fatigue_level = "LOW"
        label = "🟢 LOW FORM FATIGUE"
        action = "Movement quality remains high. Continue steady training."

    if not details:
        details.append("Movement cadence and biomechanical stability remain consistent.")

    return {
        "exercise": ex,
        "fatigue_level": fatigue_level,
        "fatigue_label": label,
        "fatigue_score": fatigue_score,
        "quality_trend": quality_trend,
        "stability_trend": stability_trend,
        "cadence_trend": cadence_trend,
        "recommended_action": action,
        "details": details,
        "is_guided": False,
        "disclaimer": "AI-Estimated Form Fatigue • Educational Guidance"
    }
