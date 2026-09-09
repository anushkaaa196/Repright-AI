"""Session Goals & Challenges System for REPRIGHT AI.

Provides goal targets, live progress evaluation, and milestone achievements
based strictly on real telemetry (clean reps and form accuracy).
"""

from typing import Dict, Any, Optional


GOAL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "SQUAT": {
        "title": "Complete 10 Clean Repetitions",
        "description": "Achieve 10 validated repetitions with parallel depth and torso stability.",
        "target_reps": 10,
        "target_accuracy": 80,
        "mode": "ACTIVE"
    },
    "DEADLIFT": {
        "title": "Complete 8 Hip Hinge Repetitions",
        "description": "Maintain rigid lumbar spine neutrality and complete 8 clean pulls.",
        "target_reps": 8,
        "target_accuracy": 80,
        "mode": "ACTIVE"
    },
    "BICEP_CURL": {
        "title": "Complete 12 Symmetrical Arm Curls",
        "description": "Maintain bilateral arm symmetry and elbow stabilization for 12 clean reps.",
        "target_reps": 12,
        "target_accuracy": 80,
        "mode": "ACTIVE"
    },
    "PUSH_UP": {
        "title": "Guided Practice: 10 Standard Push-Ups",
        "description": "Follow posture reference: maintain 180° plank line and 90° elbow depth.",
        "target_reps": 10,
        "target_accuracy": 0,
        "mode": "GUIDED"
    },
    "LUNGE": {
        "title": "Guided Practice: 10 Alternating Lunges",
        "description": "Follow posture reference: vertical shin and 90° front/rear knee flexion.",
        "target_reps": 10,
        "target_accuracy": 0,
        "mode": "GUIDED"
    },
    "PLANK": {
        "title": "Guided Practice: 60s Core Isometric Hold",
        "description": "Follow posture reference: maintain continuous 180° horizontal spine axis.",
        "target_reps": 1,
        "target_accuracy": 0,
        "mode": "GUIDED"
    },
    "SHOULDER_PRESS": {
        "title": "Guided Practice: 8 Overhead Presses",
        "description": "Follow posture reference: straight vertical press path and neutral ribs down.",
        "target_reps": 8,
        "target_accuracy": 0,
        "mode": "GUIDED"
    }
}


def get_exercise_goal(exercise_name: str) -> Dict[str, Any]:
    """Retrieves session goal definition for given exercise."""
    ex = exercise_name.upper().strip()
    return GOAL_CONFIGS.get(ex, GOAL_CONFIGS["SQUAT"])


def evaluate_goal_progress(
    exercise_name: str,
    clean_reps: int = 0,
    accuracy: int = 100,
    stats: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluates current progress towards session goal.
    Returns structured progress metrics dictionary.
    """
    goal = get_exercise_goal(exercise_name)
    target = goal["target_reps"]
    mode = goal["mode"]

    if mode == "GUIDED":
        return {
            "exercise": exercise_name.upper().strip(),
            "goal_title": goal["title"],
            "goal_description": goal["description"],
            "target_reps": target,
            "current_reps": 0,
            "progress_fraction": 1.0,
            "progress_percent": 100,
            "status_text": "GUIDED LEARNING MODE • PRACTICE TARGET",
            "is_achieved": False,
            "is_guided": True
        }

    current = min(clean_reps, target)
    fraction = min(1.0, max(0.0, current / target if target > 0 else 1.0))
    percent = int(fraction * 100)
    is_achieved = (clean_reps >= target)

    if is_achieved:
        status_text = "🎉 SESSION GOAL ACHIEVED!"
    else:
        remaining = target - clean_reps
        status_text = f"{remaining} clean rep{'s' if remaining != 1 else ''} remaining"

    return {
        "exercise": exercise_name.upper().strip(),
        "goal_title": goal["title"],
        "goal_description": goal["description"],
        "target_reps": target,
        "current_reps": clean_reps,
        "progress_fraction": fraction,
        "progress_percent": percent,
        "status_text": status_text,
        "is_achieved": is_achieved,
        "is_guided": False
    }
