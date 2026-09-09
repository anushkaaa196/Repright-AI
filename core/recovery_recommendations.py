"""Smart Recovery & Rest Recommendations Engine for REPRIGHT AI.

Generates educational rest intervals, posture resetting drills, and recovery pacing
based on form fatigue, stability scores, and correction frequency.

NOTE: This is educational workout guidance, not medical advice.
"""

from typing import Dict, Any, List, Optional


def get_recovery_recommendations(
    fatigue_level: str = "LOW",
    stability_score: int = 85,
    consecutive_faults: int = 0,
    total_reps: int = 0
) -> Dict[str, Any]:
    """
    Computes actionable recovery status and suggested rest protocols.

    Returns:
        RecoveryRecommendationResult dictionary.
    """
    if fatigue_level == "HIGH" or consecutive_faults >= 3 or stability_score < 48:
        status = "FORM_RESET"
        pill = "🔴 FORM RESET ADVISED"
        rest_sec = 90
        action = "Stop temporarily, take deep diaphragmatic breaths, and review technique before restarting."
        tips = [
            "Step out of camera view and relax spinal erectors for 60-90 seconds.",
            "Re-read the primary biomechanical standards in the Form Guide.",
            "When resuming, perform 2 deliberate warm-up repetitions with 3-second descent tempo."
        ]

    elif fatigue_level == "MODERATE" or consecutive_faults >= 2 or stability_score < 72:
        status = "SHORT_RECOVERY"
        pill = "🟡 SHORT RECOVERY ADVISED"
        rest_sec = 45
        action = "Pause for 30–60 seconds to reset joint alignment and clear active fatigue."
        tips = [
            "Shake out legs and roll shoulders backward to eliminate upper trapezius tension.",
            "Re-focus on driving knees outward in line with toes.",
            "Take 3 deep breaths before initiating the next repetition."
        ]

    else:
        status = "CONTINUE_TRAINING"
        pill = "🟢 CONTINUE TRAINING"
        rest_sec = 0
        action = "Movement quality and neuromuscular stability remain optimal. Continue training."
        tips = [
            "Maintain current movement cadence and consistent depth.",
            "Ensure full joint extension at lockout before beginning next cycle."
        ]

    return {
        "recovery_status": status,
        "status_pill": pill,
        "suggested_action": action,
        "rest_duration_sec": rest_sec,
        "recovery_tips": tips,
        "disclaimer": "Educational AI workout guidance — not medical diagnosis or prescription."
    }
