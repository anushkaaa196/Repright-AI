"""AI Workout Readiness Intelligence Engine for REPRIGHT AI.

Evaluates observable pre-workout conditions to generate an objective AI Workout Readiness Score.
Analyzes camera frame availability, keypoint detection confidence, full-body framing,
and workspace positioning.
"""

from typing import Dict, Any, List, Optional


def evaluate_workout_readiness(
    camera_active: bool = True,
    keypoints_detected: int = 17,
    keypoints_confidence_avg: float = 0.85,
    user_in_frame: bool = True,
    is_head_visible: bool = True,
    is_feet_visible: bool = True
) -> Dict[str, Any]:
    """
    Computes an objective AI Workout Readiness Score (0-100) based strictly
    on observable camera and computer vision conditions.

    Returns:
        ReadinessResult dictionary.
    """
    if not camera_active:
        return {
            "readiness_score": 0,
            "category": "NOT_READY",
            "category_label": "🔴 CAMERA OFFLINE",
            "checklist": {
                "camera_framing": False,
                "body_visibility": False,
                "pose_detection": False,
                "workspace_positioning": False
            },
            "status_text": "Camera device is offline or disconnected.",
            "recommendation": "Connect camera and ensure adequate room lighting."
        }

    score = 40.0
    checklist = {
        "camera_framing": False,
        "body_visibility": False,
        "pose_detection": False,
        "workspace_positioning": False
    }

    # 1. Camera active
    score += 15.0
    checklist["camera_framing"] = True

    # 2. Keypoints detected count (out of 17 YOLO pose keypoints)
    if keypoints_detected >= 14:
        score += 20.0
        checklist["pose_detection"] = True
    elif keypoints_detected >= 8:
        score += 10.0

    # 3. Keypoints detection confidence
    if keypoints_confidence_avg >= 0.75:
        score += 10.0
    elif keypoints_confidence_avg >= 0.5:
        score += 5.0

    # 4. Full-body framing
    if user_in_frame:
        checklist["body_visibility"] = True
        if is_head_visible and is_feet_visible:
            score += 15.0
            checklist["workspace_positioning"] = True
        elif is_head_visible or is_feet_visible:
            score += 8.0

    readiness_score = max(20, min(100, int(score)))

    # Categorization
    if readiness_score >= 90:
        cat = "OPTIMAL"
        label = "🟢 OPTIMAL READINESS"
        status_text = "Full body visible; excellent keypoint confidence."
        rec = "You are in optimal position. Ready to start workout!"
    elif readiness_score >= 75:
        cat = "READY"
        label = "🔵 READY TO TRAIN"
        status_text = "Adequate framing and pose tracking confirmed."
        rec = "Step into center frame and begin exercise."
    elif readiness_score >= 50:
        cat = "NEEDS_ADJUSTMENT"
        label = "🟡 NEEDS ADJUSTMENT"
        status_text = "Partial body detection; some keypoints obscured."
        rec = "Step back 2-3 feet so entire body is visible from head to feet."
    else:
        cat = "NOT_READY"
        label = "🔴 NOT READY"
        status_text = "Cannot reliably detect human pose keypoints."
        rec = "Check room lighting and ensure camera is pointed at exercise area."

    return {
        "readiness_score": readiness_score,
        "category": cat,
        "category_label": label,
        "checklist": checklist,
        "status_text": status_text,
        "recommendation": rec,
        "disclaimer": "AI-Estimated Workout Readiness • Computer Vision Telemetry"
    }
