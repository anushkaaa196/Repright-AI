"""Adaptive Real-Time Coaching Intensity Engine for REPRIGHT AI.

Dynamically modulates the AI coach's communication intensity between CALM, GUIDED,
and URGENT modes based on live stability, form fatigue, and posture risk.
"""

from typing import Dict, Any, Optional
from core.exercise_registry import is_active_ai_supported


def get_adaptive_coaching(
    exercise_name: str,
    stability_score: int = 85,
    fatigue_level: str = "LOW",
    risk_level: str = "LOW",
    current_feedback: str = "",
    stats_snapshot: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Determines adaptive coaching intensity and generates prioritized coaching directives.

    Returns:
        AdaptiveCoachingResult dictionary.
    """
    ex = exercise_name.upper().strip()
    is_active = is_active_ai_supported(ex)

    if not is_active:
        return {
            "exercise": ex,
            "coaching_mode": "GUIDED",
            "mode_pill": "🔵 GUIDED PRACTICE",
            "primary_message": f"Follow visual {ex} biomechanical standards.",
            "secondary_message": "Reference posture target loaded in Form Guide.",
            "focus_area": "Technical Alignment",
            "recommended_action": "Execute steady, controlled repetitions.",
            "is_guided": True
        }

    # Evaluate intensity triggers
    if risk_level == "HIGH" or fatigue_level == "HIGH" or stability_score < 50:
        mode = "URGENT"
        mode_pill = "🔴 URGENT INTERVENTION"
        focus_area = "Form Safety & Posture Reset"

        if "back" in current_feedback.lower() or "chest" in current_feedback.lower():
            pri_msg = "Pause and reset your spine before the next repetition!"
            sec_msg = "Elevate chest and pull lats tight to eliminate excessive forward lean."
        elif "depth" in current_feedback.lower():
            pri_msg = "Stop short-cutting depth. Reset starting stance."
            sec_msg = "Descend with control until thighs reach true parallel."
        else:
            pri_msg = "Form degradation detected. Reset your setup."
            sec_msg = "Take 5 seconds to brace core and establish stable footing."

        rec_action = "Pause session briefly; re-engage starting posture."

    elif risk_level == "MODERATE" or fatigue_level == "MODERATE" or stability_score < 75 or (current_feedback and "warning" in current_feedback.lower()):
        mode = "GUIDED"
        mode_pill = "🔵 GUIDED CORRECTION"
        focus_area = "Cadence & Alignment"

        if current_feedback and "rep" not in current_feedback.lower():
            pri_msg = current_feedback
        elif ex == "SQUAT":
            pri_msg = "Keep knees aligned with toes during the next descent."
        elif ex == "DEADLIFT":
            pri_msg = "Keep bar tracking tight against your shins."
        elif ex == "BICEP_CURL":
            pri_msg = "Pin elbows directly under shoulders; avoid swinging."
        else:
            pri_msg = "Maintain controlled speed throughout turnaround."

        sec_msg = "Controlled 2-second eccentric descent recommended."
        rec_action = "Execute next repetition with deliberate tempo."

    else:
        mode = "CALM"
        mode_pill = "🟢 CALM • OPTIMAL RHYTHM"
        focus_area = "Movement Consistency"
        pri_msg = "Excellent control. Maintain your rhythm."
        sec_msg = "Biomechanical joint alignment and stability are optimal."
        rec_action = "Continue steady repetitions."

    return {
        "exercise": ex,
        "coaching_mode": mode,
        "mode_pill": mode_pill,
        "primary_message": pri_msg,
        "secondary_message": sec_msg,
        "focus_area": focus_area,
        "recommended_action": rec_action,
        "is_guided": False
    }
