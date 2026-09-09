"""Advanced Performance Trend Analysis Engine for REPRIGHT AI.

Evaluates intra-session performance trajectories across repetitions:
calculating delta quality, stability drift, fatigue accumulation, and execution consistency.
"""

from typing import Dict, Any, List, Optional
from core.rep_history import RepHistoryTracker


def analyze_performance_trends(
    exercise_name: str,
    current_stability_score: int = 85,
    fatigue_score: int = 20
) -> Dict[str, Any]:
    """
    Analyzes progression trends across recent repetitions in the active workout session.

    Returns:
        PerformanceTrendResult dictionary.
    """
    ex = exercise_name.upper().strip()
    tracker = RepHistoryTracker.get_instance()
    reps = tracker.get_all_reps()
    total_reps = len(reps)

    if total_reps < 2:
        return {
            "exercise": ex,
            "total_reps": total_reps,
            "quality_trend": "STABLE",
            "quality_icon": "➡",
            "quality_text": "Establishing baseline session telemetry",
            "stability_trend": "STABLE",
            "stability_icon": "➡",
            "stability_text": f"{current_stability_score}% Current Stability",
            "fatigue_trend": "STABLE",
            "consistency_trend": "STABLE",
            "overall_direction": "STABLE",
            "summary": "Complete 2 or more repetitions to activate performance trajectory analytics."
        }

    # Compare first half vs second half or last 3 vs first 3
    if total_reps >= 4:
        split_point = total_reps // 2
        early_reps = reps[:split_point]
        recent_reps = reps[split_point:]
    else:
        early_reps = [reps[0]]
        recent_reps = [reps[-1]]

    early_quality = int(sum(r["overall_score"] for r in early_reps) / len(early_reps))
    recent_quality = int(sum(r["overall_score"] for r in recent_reps) / len(recent_reps))
    delta_quality = recent_quality - early_quality

    if delta_quality >= 4:
        q_trend = "IMPROVING"
        q_icon = "📈"
        q_text = f"{early_quality}% → {recent_quality}% (+{delta_quality}%)"
    elif delta_quality <= -4:
        q_trend = "DECLINING"
        q_icon = "📉"
        q_text = f"{early_quality}% → {recent_quality}% ({delta_quality}%)"
    else:
        q_trend = "STABLE"
        q_icon = "➡"
        q_text = f"{early_quality}% → {recent_quality}% (Consistent)"

    # Stability Trend
    early_stability = int(sum(r.get("dimension_scores", {}).get("stability", 85) for r in early_reps) / len(early_reps))
    recent_stability = int(sum(r.get("dimension_scores", {}).get("stability", current_stability_score) for r in recent_reps) / len(recent_reps))
    delta_stab = recent_stability - early_stability

    if delta_stab >= 4:
        s_trend = "IMPROVING"
        s_icon = "📈"
        s_text = f"{early_stability}% → {recent_stability}% (+{delta_stab}%)"
    elif delta_stab <= -4:
        s_trend = "DECLINING"
        s_icon = "📉"
        s_text = f"{early_stability}% → {recent_stability}% ({delta_stab}%)"
    else:
        s_trend = "STABLE"
        s_icon = "➡"
        s_text = f"{early_stability}% → {recent_stability}% (Consistent)"

    # Fatigue Trend
    if fatigue_score > 60:
        f_trend = "INCREASING"
    elif fatigue_score < 30:
        f_trend = "MINIMAL"
    else:
        f_trend = "MODERATE"

    # Consistency Trend
    consistency_score = tracker.get_consistency_score()
    c_trend = "HIGH" if consistency_score >= 80 else ("MODERATE" if consistency_score >= 65 else "LOW")

    # Overall direction
    if delta_quality > 0 and delta_stab >= 0:
        overall = "IMPROVING"
        summary = f"Positive movement trajectory! Quality has improved by +{delta_quality}% across repetitions."
    elif delta_quality < -5 or delta_stab < -8:
        overall = "DECLINING"
        summary = f"Technique degradation observed ({delta_quality}% quality shift). Consider taking a recovery break."
    else:
        overall = "STABLE"
        summary = "Movement execution is consistent with steady joint velocity and posture alignment."

    return {
        "exercise": ex,
        "total_reps": total_reps,
        "quality_trend": q_trend,
        "quality_icon": q_icon,
        "quality_text": q_text,
        "stability_trend": s_trend,
        "stability_icon": s_icon,
        "stability_text": s_text,
        "fatigue_trend": f_trend,
        "consistency_trend": c_trend,
        "overall_direction": overall,
        "summary": summary
    }
