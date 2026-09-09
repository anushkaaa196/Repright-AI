"""Dynamic Movement Risk Awareness Engine for REPRIGHT AI.

Evaluates recurring posture faults and movement instability patterns to generate
educational risk awareness classifications.

IMPORTANT: This system provides educational biomechanical guidance only.
It is NOT a medical diagnosis system and does NOT predict clinical injury.
"""

from typing import Dict, Any, List, Optional
from core.rep_history import RepHistoryTracker
from core.exercise_registry import is_active_ai_supported


def evaluate_movement_risk(
    exercise_name: str,
    stability_score: int = 85,
    fatigue_level: str = "LOW",
    stats_snapshot: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluates biomechanical risk awareness based on recurring posture corrections.

    Returns:
        RiskAwarenessResult dictionary.
    """
    ex = exercise_name.upper().strip()
    is_active = is_active_ai_supported(ex)

    if not is_active:
        return {
            "exercise": ex,
            "risk_level": "LOW",
            "risk_label": "🟢 LOW RISK AWARENESS",
            "risk_score": 10,
            "risk_factors": ["Guided exercise reference mode."],
            "recommendations": ["Follow standard reference posture guidelines."],
            "is_guided": True,
            "disclaimer": "Educational AI movement guidance — not medical diagnosis."
        }

    tracker = RepHistoryTracker.get_instance()
    reps = tracker.get_all_reps()
    total_reps = len(reps)

    risk_points = 5
    risk_factors: List[str] = []
    recommendations: List[str] = []

    # 1. Evaluate Posture Warnings Frequency
    if stats_snapshot:
        warnings = stats_snapshot.get("posture_warnings", 0)
        attempts = max(stats_snapshot.get("total_attempts", 0), 1)
        warning_rate = warnings / attempts

        if warnings >= 3 or warning_rate > 0.4:
            risk_points += 35
            risk_factors.append("Repeated spinal alignment or torso lean corrections detected.")
            recommendations.append("Brace abdominal wall and maintain a proud chest throughout movement.")
        elif warnings > 0:
            risk_points += 15
            risk_factors.append("Occasional posture deviation noted during movement cycles.")

    # 2. Evaluate Movement Instability
    if stability_score < 50:
        risk_points += 35
        risk_factors.append("High movement instability and rapid joint trajectory shifts.")
        recommendations.append("Reduce movement speed; perform 2-second controlled descents.")
    elif stability_score < 70:
        risk_points += 15
        risk_factors.append("Moderate movement sway or joint jitter observed.")

    # 3. Evaluate Fatigue Correlation
    if fatigue_level == "HIGH":
        risk_points += 30
        risk_factors.append("High form fatigue accumulating across multiple repetitions.")
        recommendations.append("Take a rest break to prevent technique breakdown.")
    elif fatigue_level == "MODERATE":
        risk_points += 15

    # 4. Rep History Fault Patterns
    if total_reps >= 3:
        consecutive_faults = 0
        for r in reversed(reps):
            if not r.get("is_clean", True):
                consecutive_faults += 1
            else:
                break
        if consecutive_faults >= 2:
            risk_points += 20
            risk_factors.append(f"{consecutive_faults} consecutive repetitions completed with form faults.")
            recommendations.append("Pause and reset starting stance before next repetition.")

    risk_score = max(5, min(100, risk_points))

    # Categorization
    if risk_score >= 60:
        risk_level = "HIGH"
        label = "🔴 HIGH ATTENTION REQUIRED"
        if not recommendations:
            recommendations.append("Pause session and reset alignment before resuming.")
    elif risk_score >= 35:
        risk_level = "MODERATE"
        label = "🟡 MODERATE ATTENTION"
        if not recommendations:
            recommendations.append("Refine posture control and maintain steady cadence.")
    else:
        risk_level = "LOW"
        label = "🟢 LOW RISK"
        risk_factors.append("Movement is currently within acceptable form targets.")
        recommendations.append("Maintain current cadence and stable breathing.")

    return {
        "exercise": ex,
        "risk_level": risk_level,
        "risk_label": label,
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "recommendations": recommendations,
        "is_guided": False,
        "disclaimer": "Educational AI movement guidance — not medical diagnosis."
    }
