"""Application-wide configurations, biomechanical exercise thresholds, and constants."""

EXERCISE_CONFIGS = {
    "SQUAT": {
        "joint_tracked": "Knee",
        "down_thresh": 145.0,
        "target_angle": 100.0,       # Reachable parallel depth
        "ascent_hysteresis": 115.0,  # Commences upward drive
        "up_thresh": 148.0,          # Complete lockout return
        "min_calib_angle": 140.0,    # Natural standing threshold
        "check_torso": True,
        "min_torso_angle": 35.0,
        "check_sitting": True,
        "max_sit_hold_sec": 2.0      # Must rest on seat > 2.0s to disqualify
    },
    "DEADLIFT": {
        "joint_tracked": "Hip",
        "down_thresh": 145.0,
        "target_angle": 110.0,
        "ascent_hysteresis": 120.0,
        "up_thresh": 150.0,
        "min_calib_angle": 140.0,
        "check_torso": True,
        "min_torso_angle": 30.0,
        "check_sitting": False
    },
    "BICEP_CURL": {
        "joint_tracked": "Elbow",
        "down_thresh": 125.0,        # Starts curling upward
        "target_angle": 65.0,        # Natural peak contraction apex (was 45.0)
        "ascent_hysteresis": 85.0,   # Opening arm back downward
        "up_thresh": 125.0,          # Full extension lockout return
        "min_calib_angle": 120.0,    # Natural relaxed arm hang calibration
        "check_torso": True,         # Validate upper-body stability
        "max_torso_lean_angle": 22.0,# Max backward torso lean before flagging cheat curl
        "check_elbow_lock": True,    # Require elbows locked to ribcage
        "max_elbow_drift_angle": 28.0,  # Max allowed upper arm drift (deg) from ribcage
        "check_sitting": False
    }
}

# Calibration and gesture parameters
CALIBRATION_TARGET_FRAMES = 15       # Responsive 0.5s calibration (was 25)
COUNTDOWN_SECONDS = 5.0
GESTURE_HOLD_THRESHOLD = 1.5
PROFILE_CONF_THRESHOLD = 0.30        # Tolerant of webcam lighting and partial visibility

# Camera defaults
DEFAULT_CAMERA_WIDTH = 640
DEFAULT_CAMERA_HEIGHT = 480
DEFAULT_CAMERA_BUFFER_SIZE = 1

# Pose Detection Model & Inference Performance
POSE_MODEL_PATH = "yolov8n-pose.pt"
POSE_MODEL_IMGSZ = 320               # 320x320 optimal for real-time CPU performance (3x faster than 640)

# UI Performance & Telemetry Throttling
UI_TELEMETRY_THROTTLE_SEC = 0.25     # 4 Hz refresh for heavy text/guidance cards to eliminate GUI lag

