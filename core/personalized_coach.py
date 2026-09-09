"""Personalized AI Improvement Engine for REPRIGHT AI.

Synthesizes rep history telemetry, common biomechanical faults, and dimensional strengths
to generate deterministic, explainable, and actionable personal training plans.
"""

from typing import Dict, Any, Optional
from core.rep_history import RepHistoryTracker


# Educational Biomechanical Explanations
WHY_IT_MATTERS_MAP: Dict[str, str] = {
    "range_of_motion": "Achieving full joint range of motion ensures maximum muscle recruitment, stimulates hypertrophy, and prevents compensatory loading.",
    "alignment": "Proper joint alignment keeps shear forces evenly distributed across joints and minimizes risk of ligament strain.",
    "stability": "Torso and core rigidity protects the spinal column, preventing energy leaks and ensuring efficient power transfer.",
    "movement_control": "Maintaining active muscular tension at the bottom turn eliminates joint jarring and builds explosive concentric power.",
    "consistency": "Consistent movement cadence locks in neuromuscular motor patterns, improving lifting efficiency and long-term endurance."
}

# Exercise-Specific Coaching Cues
COACHING_CUES: Dict[str, Dict[str, str]] = {
    "SQUAT": {
        "range_of_motion": "Think of descending until your hip crease dips just below the top of your patella.",
        "alignment": "Track your knees directly over your second toe; spread the floor apart with your feet.",
        "stability": "Take a deep diaphragmatic breath into your belly and brace your abs before every descent.",
        "movement_control": "Touch the bottom depth and immediately drive upward without relaxing into a chair sit.",
        "consistency": "Count a strict 2-second descent, 1-second ascent on every single repetition."
    },
    "DEADLIFT": {
        "range_of_motion": "Push your hips backward towards the wall behind you until hamstrings load completely.",
        "alignment": "Pack your lats tight and maintain a laser-straight neutral spine from neck to tailbone.",
        "stability": "Brace your midsection and keep the barbell path dragging tight against your shins.",
        "movement_control": "Stand tall at the lockout by squeezing glutes; do not hyperextend your lower back.",
        "consistency": "Reset your breath and foot rooting before starting every individual pull."
    },
    "BICEP_CURL": {
        "range_of_motion": "Lower weights until arms are fully extended at the bottom to stretch the bicep tendon.",
        "alignment": "Pin your elbows strictly against your ribcage; avoid swinging elbows forward.",
        "stability": "Lock your shoulder blades back and down; do not sway your torso to generate momentum.",
        "movement_control": "Control both arms symmetrically with identical ascent and lowering cadence.",
        "consistency": "Squeeze biceps hard for 1 full second at peak contraction on every rep."
    },
    "DEFAULT": {
        "range_of_motion": "Perform complete, unhurried range of motion across every rep cycle.",
        "alignment": "Maintain joint stack and neutral spine throughout.",
        "stability": "Engage core stabilizers to lock body axis in place.",
        "movement_control": "Focus on smooth turnaround and avoid jerky transitions.",
        "consistency": "Maintain strict cadence and posture standards."
    }
}


def generate_personalized_plan(
    exercise_name: str,
    rep_tracker: Optional[RepHistoryTracker] = None,
    stats: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates a personalized training plan based on session rep history and telemetry.
    """
    tracker = rep_tracker or RepHistoryTracker.get_instance()
    ex = exercise_name.upper().strip()
    cues_dict = COACHING_CUES.get(ex, COACHING_CUES["DEFAULT"])

    total_reps = tracker.get_total_reps()
    clean_reps = tracker.get_clean_reps()
    avg_score = tracker.get_average_score()
    consistency = tracker.get_consistency_score()
    most_common_issue = tracker.get_most_common_issue()
    strongest_cat, strong_score = tracker.get_strongest_category()
    weakest_cat, weak_score = tracker.get_weakest_category()

    # Determine Strength
    if strongest_cat == "range_of_motion":
        strength_desc = f"Excellent movement depth and joint range of motion ({strong_score}% score)."
    elif strongest_cat == "alignment":
        strength_desc = f"Solid joint tracking and symmetrical alignment ({strong_score}% score)."
    elif strongest_cat == "stability":
        strength_desc = f"Strong core rigidity and torso posture preservation ({strong_score}% score)."
    elif strongest_cat == "movement_control":
        strength_desc = f"Continuous kinetic tension with zero passive momentum ({strong_score}% score)."
    else:
        strength_desc = f"High movement cadence and execution consistency ({strong_score}% score)."

    if total_reps == 0:
        strength_desc = "Biomechanical tracking profile initialized and ready for practice."

    # Determine Primary Focus
    if weakest_cat == "range_of_motion":
        focus_title = "Depth & Range of Motion"
        recommended_practice = "Perform 2-second paused repetitions at parallel depth using a light load."
    elif weakest_cat == "alignment":
        focus_title = "Joint Alignment & Tracking"
        recommended_practice = "Focus on toe-knee angle alignment; use visual ground cues to prevent knee valgus."
    elif weakest_cat == "stability":
        focus_title = "Torso Rigidity & Core Bracing"
        recommended_practice = "Practice diaphragmatic abdominal bracing before each descent."
    elif weakest_cat == "movement_control":
        focus_title = "Kinetic Tension & Controlled Turnaround"
        recommended_practice = "Eliminate pauses at the bottom; practice continuous smooth touch-and-go tempo."
    else:
        focus_title = "Movement Cadence & Consistency"
        recommended_practice = "Use a metronome tempo (2 seconds down, 1 second pause, 1 second up)."

    why_matters = WHY_IT_MATTERS_MAP.get(weakest_cat, WHY_IT_MATTERS_MAP["alignment"])
    cue = cues_dict.get(weakest_cat, cues_dict["range_of_motion"])

    # Determine Next Session Goal
    if avg_score >= 90:
        next_goal = f"Target {clean_reps + 3} clean repetitions while maintaining 90%+ form score."
    elif avg_score >= 75:
        next_goal = f"Achieve 85%+ form score by eliminating {most_common_issue.lower()}."
    else:
        next_goal = f"Prioritize slow cadence and resolve {focus_title.lower()} over repetition count."

    return {
        "exercise": ex,
        "total_reps": total_reps,
        "clean_reps": clean_reps,
        "average_score": avg_score,
        "consistency_score": consistency,
        "strength": strength_desc,
        "primary_focus": focus_title,
        "weakest_category": weakest_cat,
        "strongest_category": strongest_cat,
        "why_it_matters": why_matters,
        "next_session_goal": next_goal,
        "coaching_cue": f'"{cue}"',
        "recommended_practice": recommended_practice,
        "most_common_issue": most_common_issue
    }
