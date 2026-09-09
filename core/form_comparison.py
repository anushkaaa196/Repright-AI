"""Current Posture vs Ideal Form Comparison Engine for REPRIGHT AI.

Performs real-time comparison between live AI computer vision observations and
ideal biomechanical reference targets, identifying the precise technical gap.
"""

from typing import Dict, Any, Optional

# Color tokens for form status (self-contained, decoupling core from UI)
STATUS_COLOR_SUCCESS = "#00E676"
STATUS_COLOR_WARN = "#FF9100"
STATUS_COLOR_ALERT = "#FF1744"
STATUS_COLOR_ACCENT = "#00E5FF"
STATUS_COLOR_MUTED = "#94A3B8"


# Ideal Biomechanical Standards per Exercise
IDEAL_STANDARDS: Dict[str, Dict[str, str]] = {
    "SQUAT": {
        "depth": "Thighs parallel or slightly below parallel (knee crease <= 100°).",
        "torso": "Upright chest with spine held in neutral lordotic curve (>= 45°).",
        "knees": "Knees track directly in line with toes, with zero inward valgus collapse.",
        "cadence": "Smooth 2s descent with active kinetic turnaround, avoiding chair resting."
    },
    "DEADLIFT": {
        "hinge": "Pure hip hinge with hips pushed back and knees slightly flexed (110°).",
        "spine": "Rigid neutral spine from occiput to sacrum with locked lats.",
        "bar_path": "Vertical bar path kept tight against shins and thighs.",
        "lockout": "Full hip extension at lockout without backward lumbar hyperextension."
    },
    "BICEP_CURL": {
        "elbow": "Elbows pinned stationary directly below shoulder sockets.",
        "rom": "Full forearm flexion to <= 65° and complete extension to 175°.",
        "torso": "Completely still torso with zero anterior/posterior swing.",
        "symmetry": "Identical bilateral contraction cadence across left and right arms."
    },
    "DEFAULT": {
        "general": "Maintain neutral joint alignment and steady tempo throughout."
    }
}


def get_form_comparison(
    exercise_name: str,
    feedback_msg: str = "",
    feedback_color: Optional[str] = None
) -> Dict[str, Any]:
    """
    Compares current live AI feedback against ideal biomechanical targets.
    Returns structured comparison dictionary.
    """
    ex = exercise_name.upper().strip()
    msg = feedback_msg.strip()
    msg_lower = msg.lower()
    standards = IDEAL_STANDARDS.get(ex, IDEAL_STANDARDS["DEFAULT"])

    # Analyze feedback context
    if not msg or "tracking" in msg_lower or "standby" in msg_lower or "position" in msg_lower:
        status_level = "STANDBY"
        status_pill = "○ READY FOR FORM CHECK"
        status_color = STATUS_COLOR_MUTED
        current_obs = "Awaiting exercise repetition movement in camera frame."
        ideal_target = standards.get("depth", standards.get("general", "Maintain neutral posture."))
        gap = "Initiate repetition to begin real-time posture analysis."

    elif "clean" in msg_lower or "good" in msg_lower or "optimal" in msg_lower or "perfect" in msg_lower or feedback_color == STATUS_COLOR_SUCCESS:
        status_level = "OPTIMAL"
        status_pill = "● OPTIMAL FORM"
        status_color = STATUS_COLOR_SUCCESS
        current_obs = msg
        ideal_target = standards.get("depth", standards.get("general", "Satisfying reference angles."))
        gap = "Zero biomechanical faults detected. Maintain current cadence."

    elif "depth" in msg_lower or "shallow" in msg_lower:
        status_level = "MINOR_ADJUSTMENT"
        status_pill = "▲ DEPTH ADJUSTMENT"
        status_color = STATUS_COLOR_WARN
        current_obs = msg
        ideal_target = standards.get("depth", "Full parallel depth range-of-motion.")
        gap = "Lower 2-3 inches further until thigh reaches parallel with floor."

    elif "back" in msg_lower or "chest" in msg_lower or "torso" in msg_lower or "lean" in msg_lower:
        status_level = "CORRECTION_RECOMMENDED"
        status_pill = "✖ POSTURE CORRECTION"
        status_color = STATUS_COLOR_ALERT
        current_obs = msg
        ideal_target = standards.get("torso", standards.get("spine", "Neutral upright spine alignment."))
        gap = "Elevate chest, pull lats tight, and brace abdominal wall to prevent forward torso lean."

    elif "chair" in msg_lower or "sit" in msg_lower or "rest" in msg_lower:
        status_level = "CORRECTION_RECOMMENDED"
        status_pill = "✖ ACTIVE TENSION FAULT"
        status_color = STATUS_COLOR_ALERT
        current_obs = msg
        ideal_target = standards.get("cadence", "Continuous muscular tension throughout turnaround.")
        gap = "Do not relax onto chair or pause at bottom; perform active touch-and-go reversal."

    elif "swing" in msg_lower or "elbow" in msg_lower or "momentum" in msg_lower:
        status_level = "MINOR_ADJUSTMENT"
        status_pill = "▲ STABILIZATION CUE"
        status_color = STATUS_COLOR_WARN
        current_obs = msg
        ideal_target = standards.get("elbow", "Elbows pinned stationary at ribs.")
        gap = "Eliminate torso sway; use strict bicep contraction without swinging elbows."

    else:
        status_level = "TRACKING"
        status_pill = "● LIVE TRACKING"
        status_color = STATUS_COLOR_ACCENT
        current_obs = msg
        ideal_target = standards.get("general", "Maintain controlled joint cadence.")
        gap = "Continue movement within camera viewing field."

    return {
        "exercise": ex,
        "current_observation": current_obs,
        "ideal_target": ideal_target,
        "gap_to_improve": gap,
        "status_level": status_level,
        "status_pill": status_pill,
        "status_color": status_color
    }
