"""2D geometry, joint trigonometry, and exercise-aware landmark extraction."""

import numpy as np
from typing import Dict, Tuple, Optional, Any


def calculate_angle(a: Any, b: Any, c: Any) -> float:
    """Calculates interior 2D angle between 3 points [0, 180]."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return float(360 - angle if angle > 180.0 else angle)


def extract_valid_profile(
    kpts: np.ndarray,
    confs: np.ndarray,
    conf_threshold: float = 0.30
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Legacy side profile selector (kept for backward compatibility)."""
    left_ids = [5, 7, 9, 11, 13, 15]   # Shoulder, Elbow, Wrist, Hip, Knee, Ankle
    right_ids = [6, 8, 10, 12, 14, 16]

    l_conf = float(np.mean([confs[i] for i in left_ids]))
    r_conf = float(np.mean([confs[i] for i in right_ids]))

    chosen_ids = left_ids if l_conf >= r_conf else right_ids
    chosen_conf = max(l_conf, r_conf)

    if chosen_conf < conf_threshold:
        return None, None

    side = "Left" if l_conf >= r_conf else "Right"
    pts = {
        "shoulder": kpts[chosen_ids[0]],
        "elbow": kpts[chosen_ids[1]],
        "wrist": kpts[chosen_ids[2]],
        "hip": kpts[chosen_ids[3]],
        "knee": kpts[chosen_ids[4]],
        "ankle": kpts[chosen_ids[5]],
        "side": side,
        "conf": chosen_conf
    }
    return pts, side


def extract_exercise_data(
    exercise: str,
    kpts: np.ndarray,
    confs: np.ndarray,
    conf_threshold: float = 0.30
) -> Dict[str, Any]:
    """
    Exercise-specific landmark extractor that tracks BOTH arms and BOTH legs independently.
    Works with partial body visibility and detects both limbs simultaneously.
    """
    # Keypoint indices:
    # 5: L_shoulder, 6: R_shoulder
    # 7: L_elbow,    8: R_elbow
    # 9: L_wrist,   10: R_wrist
    # 11: L_hip,    12: R_hip
    # 13: L_knee,   14: R_knee
    # 15: L_ankle,  16: R_ankle

    result = {
        "valid": False,
        "angle": None,
        "hip_angle": None,
        "side": None,
        "is_frontal": False,
        "l_valid": False,
        "r_valid": False,
        "l_angle": None,
        "r_angle": None,
        "points": {},
        "missing_feedback": None
    }

    # Detect body orientation (Frontal vs Profile) based on shoulder distance
    sh_diff_x = abs(kpts[5][0] - kpts[6][0])
    if confs[5] > 0.3 and confs[6] > 0.3 and sh_diff_x > 90:
        result["is_frontal"] = True

    if exercise == "BICEP_CURL":
        # Extract Left and Right arms independently
        l_conf = min(confs[5], confs[7], confs[9])
        r_conf = min(confs[6], confs[8], confs[10])

        l_valid = bool(l_conf >= conf_threshold)
        r_valid = bool(r_conf >= conf_threshold)

        if not l_valid and not r_valid:
            result["missing_feedback"] = "Position arm(s) in frame (shoulder, elbow, wrist)"
            return result

        l_angle = calculate_angle(kpts[5], kpts[7], kpts[9]) if l_valid else None
        r_angle = calculate_angle(kpts[6], kpts[8], kpts[10]) if r_valid else None

        # Torso anchor points to measure elbow-to-ribcage lock and drift
        l_hip = kpts[11] if confs[11] >= 0.20 else np.array([kpts[5][0], kpts[5][1] + 200.0])
        r_hip = kpts[12] if confs[12] >= 0.20 else np.array([kpts[6][0], kpts[6][1] + 200.0])

        # Upper arm angle relative to torso (angle Hip - Shoulder - Elbow)
        # When elbows are pinned to ribcage, angle is typically 5-20 deg.
        # When elbows swing forward or flare out, angle increases beyond 28-30 deg.
        l_shoulder_angle = calculate_angle(l_hip, kpts[5], kpts[7]) if l_valid else None
        r_shoulder_angle = calculate_angle(r_hip, kpts[6], kpts[8]) if r_valid else None

        result["valid"] = True
        result["l_valid"] = l_valid
        result["r_valid"] = r_valid
        result["l_angle"] = l_angle
        result["r_angle"] = r_angle
        result["l_shoulder_angle"] = l_shoulder_angle
        result["r_shoulder_angle"] = r_shoulder_angle
        result["shoulder_angle"] = l_shoulder_angle if l_valid else r_shoulder_angle

        # Torso inclination angle from vertical (to detect excessive backward body swing/momentum cheating)
        chosen_sh = kpts[5] if l_valid else kpts[6]
        chosen_hp = l_hip if l_valid else r_hip
        dx = float(chosen_sh[0] - chosen_hp[0])
        dy = float(chosen_sh[1] - chosen_hp[1])
        result["torso_angle"] = abs(float(np.degrees(np.arctan2(dx, -dy))))

        if l_valid and r_valid:
            result["side"] = "Both"
        elif l_valid:
            result["side"] = "Left"
        else:
            result["side"] = "Right"

        valid_angles = [a for a in [l_angle, r_angle] if a is not None]
        result["angle"] = min(valid_angles) if valid_angles else 180.0

        # Points for both arms and torso anchors
        result["points"] = {
            "l_shoulder": kpts[5],
            "l_elbow": kpts[7],
            "l_wrist": kpts[9],
            "l_hip": l_hip,
            "r_shoulder": kpts[6],
            "r_elbow": kpts[8],
            "r_wrist": kpts[10],
            "r_hip": r_hip,
            # Fallbacks for generic single-limb drawing
            "shoulder": kpts[5] if l_valid else kpts[6],
            "elbow": kpts[7] if l_valid else kpts[8],
            "wrist": kpts[9] if l_valid else kpts[10],
            "hip": l_hip if l_valid else r_hip
        }
        return result

    elif exercise == "SQUAT":
        # Extract Left and Right legs independently
        l_conf = min(confs[11], confs[13])
        r_conf = min(confs[12], confs[14])

        l_valid = bool(l_conf >= conf_threshold)
        r_valid = bool(r_conf >= conf_threshold)

        if not l_valid and not r_valid:
            result["missing_feedback"] = "Step back: Hips and knees must be visible"
            return result

        l_ankle = kpts[15] if confs[15] >= 0.20 else np.array([kpts[13][0], kpts[13][1] + 120])
        r_ankle = kpts[16] if confs[16] >= 0.20 else np.array([kpts[14][0], kpts[14][1] + 120])

        l_knee_angle = calculate_angle(kpts[11], kpts[13], l_ankle) if l_valid else None
        r_knee_angle = calculate_angle(kpts[12], kpts[14], r_ankle) if r_valid else None

        result["valid"] = True
        result["l_valid"] = l_valid
        result["r_valid"] = r_valid
        result["l_angle"] = l_knee_angle
        result["r_angle"] = r_knee_angle

        if l_valid and r_valid:
            result["side"] = "Both"
            result["angle"] = min(l_knee_angle, r_knee_angle)
        elif l_valid:
            result["side"] = "Left"
            result["angle"] = l_knee_angle
        else:
            result["side"] = "Right"
            result["angle"] = r_knee_angle

        chosen_sh = kpts[5] if (confs[5] >= confs[6]) else kpts[6]
        chosen_hip = kpts[11] if l_valid else kpts[12]
        chosen_knee = kpts[13] if l_valid else kpts[14]
        result["hip_angle"] = calculate_angle(chosen_sh, chosen_hip, chosen_knee)

        result["points"] = {
            "l_hip": kpts[11],
            "l_knee": kpts[13],
            "l_ankle": l_ankle,
            "r_hip": kpts[12],
            "r_knee": kpts[14],
            "r_ankle": r_ankle,
            "shoulder": chosen_sh,
            "hip": chosen_hip,
            "knee": chosen_knee,
            "ankle": l_ankle if l_valid else r_ankle
        }
        return result

    elif exercise == "DEADLIFT":
        # Extract Left and Right profiles
        l_conf = min(confs[5], confs[11], confs[13])
        r_conf = min(confs[6], confs[12], confs[14])

        l_valid = bool(l_conf >= conf_threshold)
        r_valid = bool(r_conf >= conf_threshold)

        if not l_valid and not r_valid:
            result["missing_feedback"] = "Step back: Upper body, hips, and knees must be visible"
            return result

        l_ankle = kpts[15] if confs[15] >= 0.20 else np.array([kpts[13][0], kpts[13][1] + 100])
        r_ankle = kpts[16] if confs[16] >= 0.20 else np.array([kpts[14][0], kpts[14][1] + 100])

        l_hip_angle = calculate_angle(kpts[5], kpts[11], kpts[13]) if l_valid else None
        r_hip_angle = calculate_angle(kpts[6], kpts[12], kpts[14]) if r_valid else None

        result["valid"] = True
        result["l_valid"] = l_valid
        result["r_valid"] = r_valid
        result["l_angle"] = l_hip_angle
        result["r_angle"] = r_hip_angle

        if l_valid and r_valid:
            result["side"] = "Both"
            result["angle"] = min(l_hip_angle, r_hip_angle)
        elif l_valid:
            result["side"] = "Left"
            result["angle"] = l_hip_angle
        else:
            result["side"] = "Right"
            result["angle"] = r_hip_angle

        result["hip_angle"] = result["angle"]
        chosen_offset = 0 if l_valid else 1
        result["points"] = {
            "l_shoulder": kpts[5],
            "l_hip": kpts[11],
            "l_knee": kpts[13],
            "l_ankle": l_ankle,
            "r_shoulder": kpts[6],
            "r_hip": kpts[12],
            "r_knee": kpts[14],
            "r_ankle": r_ankle,
            "shoulder": kpts[5 + chosen_offset],
            "hip": kpts[11 + chosen_offset],
            "knee": kpts[13 + chosen_offset],
            "ankle": l_ankle if l_valid else r_ankle
        }
        return result

    return result
