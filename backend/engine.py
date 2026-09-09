import sys
from pathlib import Path

# Ensure root workspace directory is in sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import time
import threading
from typing import Callable, Optional, Dict, Any, Tuple
import cv2
import numpy as np
import torch
from ultralytics import YOLO

from config import (
    EXERCISE_CONFIGS,
    CALIBRATION_TARGET_FRAMES,
    COUNTDOWN_SECONDS,
    GESTURE_HOLD_THRESHOLD,
    PROFILE_CONF_THRESHOLD,
    POSE_MODEL_PATH,
    POSE_MODEL_IMGSZ
)
from core import (
    LowPassFilter,
    extract_exercise_data,
    classify_sitting,
    check_hands_up_gesture
)
from backend.camera import CameraManager
from backend.reporter import generate_report_image


class LimbTracker:
    """Independent biomechanical state machine and rep tracker for an individual limb."""

    STATE_NAMES = {
        -1: "CALIBRATING",
        0: "READY",
        1: "CURLING UP",
        2: "PEAK CONTRACTION",
        3: "LOWERING"
    }

    def __init__(self, name: str):
        self.name = name
        self.state = -1  # STATE_CALIBRATING
        self.calibration_frames = 0
        self.standing_baseline = None
        self.depth_achieved = False
        self.reps = 0            # Clean reps strictly
        self.failed_reps = 0     # Disqualified / form fault reps
        self.last_rep_clean = True
        self.filter = LowPassFilter(cutoff_samples=5)
        self.current_angle = 180.0
        self.smoothed_angle = 180.0

        # Shoulder / Upper Arm tracking for elbow stability & ribcage locking
        self.shoulder_filter = LowPassFilter(cutoff_samples=5)
        self.standing_shoulder_baseline = None
        self.current_shoulder_angle = 0.0
        self.smoothed_shoulder_angle = 0.0
        self.is_elbow_locked = True
        self.posture_fault_in_rep = False
        self.has_warned_in_rep = False
        self.fault_reason = ""

    def reset(self):
        """Resets limb tracking state and rep counter."""
        self.state = -1
        self.calibration_frames = 0
        self.standing_baseline = None
        self.depth_achieved = False
        self.reps = 0
        self.failed_reps = 0
        self.last_rep_clean = True
        self.filter.clear()
        self.current_angle = 180.0
        self.smoothed_angle = 180.0

        self.shoulder_filter.clear()
        self.standing_shoulder_baseline = None
        self.current_shoulder_angle = 0.0
        self.smoothed_shoulder_angle = 0.0
        self.is_elbow_locked = True
        self.posture_fault_in_rep = False
        self.has_warned_in_rep = False
        self.fault_reason = ""

    def update(
        self,
        raw_angle: float,
        cfg: Dict[str, Any],
        calib_target_frames: int,
        raw_shoulder_angle: Optional[float] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Processes a new raw joint angle for this limb and checks elbow stabilization.
        Returns (rep_counted: bool, message: Optional[str]).
        """
        self.current_angle = raw_angle
        self.smoothed_angle = self.filter.update(raw_angle)

        if raw_shoulder_angle is not None:
            self.current_shoulder_angle = raw_shoulder_angle
            self.smoothed_shoulder_angle = self.shoulder_filter.update(raw_shoulder_angle)

        rep_counted = False
        msg = None

        min_calib = cfg.get("min_calib_angle", 120.0)

        # STATE_CALIBRATING (-1)
        if self.state == -1:
            if self.smoothed_angle > min_calib:
                self.calibration_frames += 1
                self.standing_baseline = (
                    self.smoothed_angle
                    if self.standing_baseline is None
                    else 0.8 * self.standing_baseline + 0.2 * self.smoothed_angle
                )
                if raw_shoulder_angle is not None:
                    self.standing_shoulder_baseline = (
                        self.smoothed_shoulder_angle
                        if self.standing_shoulder_baseline is None
                        else 0.8 * self.standing_shoulder_baseline + 0.2 * self.smoothed_shoulder_angle
                    )
                if self.calibration_frames >= calib_target_frames:
                    self.state = 0  # READY
                    msg = f"{self.name} arm calibrated!"
            else:
                self.calibration_frames = max(0, self.calibration_frames - 1)

        # STATE_STANDING / READY (0)
        elif self.state == 0:
            if self.smoothed_angle < cfg["down_thresh"]:
                self.state = 1  # CURLING UP
                self.depth_achieved = False
                self.posture_fault_in_rep = False
                self.has_warned_in_rep = False
                self.fault_reason = ""

        # Check elbow lock during active curl phases
        if self.state in (1, 2, 3) and cfg.get("check_elbow_lock", True) and raw_shoulder_angle is not None:
            max_drift = cfg.get("max_elbow_drift_angle", 28.0)
            baseline = self.standing_shoulder_baseline if self.standing_shoulder_baseline is not None else 10.0
            drift_above_base = max(0.0, self.smoothed_shoulder_angle - baseline)

            # Flag fault if upper arm swings forward/outward beyond threshold or drifts excessively from rest
            if self.smoothed_shoulder_angle > max_drift or drift_above_base > 18.0:
                self.is_elbow_locked = False
                self.posture_fault_in_rep = True
                self.fault_reason = "Unpinned Elbow"
            else:
                self.is_elbow_locked = True
        else:
            self.is_elbow_locked = True

        # STATE_DESCENDING / CURLING UP (1)
        if self.state == 1:
            if self.smoothed_angle <= cfg["target_angle"]:
                self.depth_achieved = True
                self.state = 2  # PEAK CONTRACTION
            elif self.standing_baseline is not None and self.smoothed_angle > (self.standing_baseline - 10.0):
                self.state = 0  # Released without reaching peak
                self.failed_reps += 1
                self.last_rep_clean = False
                self.posture_fault_in_rep = True
                self.fault_reason = "Incomplete Curl"
                rep_counted = True
                msg = f"NO REP: {self.name} Arm Incomplete Range of Motion! Curl to full peak"

        # STATE_BOTTOM / PEAK CONTRACTION (2)
        elif self.state == 2:
            if self.smoothed_angle > cfg["ascent_hysteresis"]:
                self.state = 3  # LOWERING ARM

        # STATE_ASCENDING / LOWERING ARM (3)
        elif self.state == 3:
            up_ref = cfg.get("up_thresh", 125.0)
            base_ref = (self.standing_baseline - 12.0) if self.standing_baseline is not None else up_ref
            if self.smoothed_angle >= min(up_ref, base_ref):
                self.state = 0  # Full extension return
                if self.depth_achieved:
                    rep_counted = True
                    if self.posture_fault_in_rep:
                        self.failed_reps += 1
                        self.last_rep_clean = False
                        msg = f"NO REP: {self.name} Arm {self.fault_reason or 'Form Fault'} (Keep elbows pinned at sides)"
                    else:
                        self.reps += 1
                        self.last_rep_clean = True
                        msg = f"{self.name} Arm Clean Rep #{self.reps} Counted!"
                self.depth_achieved = False

        return rep_counted, msg


class WorkoutEngine:
    """Core workout tracking and biomechanical analysis engine."""

    # FSM States
    STATE_COUNTDOWN = -2
    STATE_CALIBRATING = -1
    STATE_STANDING = 0
    STATE_DESCENDING = 1
    STATE_BOTTOM = 2
    STATE_ASCENDING = 3

    STATE_NAMES = {
        STATE_COUNTDOWN: "COUNTDOWN",
        STATE_CALIBRATING: "CALIBRATING",
        STATE_STANDING: "READY",
        STATE_DESCENDING: "IN MOTION",
        STATE_BOTTOM: "TARGET REACHED",
        STATE_ASCENDING: "RETURNING"
    }

    def __init__(
        self,
        model_path: str = POSE_MODEL_PATH,
        on_frame_processed: Optional[Callable[[np.ndarray, str, str, Dict[str, Any]], None]] = None
    ):
        self.model = YOLO(model_path)
        self.camera = CameraManager()
        self.on_frame_processed = on_frame_processed

        self.is_running = False
        self._thread: Optional[threading.Thread] = None

        self.current_exercise = "SQUAT"
        self.clean_reps = 0
        self.failed_depth = 0
        self.failed_sitting = 0
        self.failed_posture = 0
        self.posture_warnings = 0
        self.start_time: Optional[float] = None

        # Dual-arm trackers for bicep curls
        self.left_arm = LimbTracker("Left")
        self.right_arm = LimbTracker("Right")

    def set_exercise(self, exercise_name: str):
        """Sets the active exercise and resets current session stats."""
        if exercise_name in EXERCISE_CONFIGS:
            self.current_exercise = exercise_name
            self.reset_metrics()

    def reset_metrics(self):
        """Resets rep counts, error metrics, dual-arm states, and session duration."""
        self.clean_reps = 0
        self.failed_depth = 0
        self.failed_sitting = 0
        self.failed_posture = 0
        self.posture_warnings = 0
        self.start_time = time.time()
        self.left_arm.reset()
        self.right_arm.reset()

    def get_stats(self) -> Dict[str, Any]:
        """Returns the current telemetry metrics dictionary."""
        total = self.clean_reps + self.failed_depth + self.failed_sitting + self.failed_posture
        acc = int((self.clean_reps / max(total, 1)) * 100) if total > 0 else 100
        return {
            "clean_reps": self.clean_reps,
            "failed_depth": self.failed_depth,
            "failed_sitting": self.failed_sitting,
            "failed_posture": self.failed_posture,
            "posture_warnings": self.posture_warnings,
            "total_attempts": total,
            "accuracy": acc,
            "start_time": self.start_time,
            "left_arm_reps": self.left_arm.reps,
            "right_arm_reps": self.right_arm.reps,
            "left_arm_failed": self.left_arm.failed_reps,
            "right_arm_failed": self.right_arm.failed_reps
        }

    def start(self) -> bool:
        """Starts the camera and background processing thread."""
        if self.is_running:
            return True

        if not self.camera.start():
            return False

        self.is_running = True
        self.start_time = time.time()
        self._thread = threading.Thread(target=self._processing_loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        """Stops the processing thread and releases camera resources."""
        self.is_running = False
        if self.camera:
            self.camera.release()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
            self._thread = None

    def export_report(self, output_path: Optional[str] = None) -> str:
        """Exports the diagnostic session summary image."""
        return generate_report_image(self.current_exercise, self.get_stats(), output_path)

    def _processing_loop(self):
        """Worker loop reading frames, running YOLO pose inference, and driving FSM."""
        cfg = EXERCISE_CONFIGS[self.current_exercise]
        angle_filter = LowPassFilter(cutoff_samples=5)

        current_state = self.STATE_COUNTDOWN
        countdown_start = time.time()
        calibration_frames = 0
        standing_baseline = None

        depth_achieved = False
        invalid_sit_flag = False
        posture_fault_in_rep = False
        gesture_start_time = None
        sitting_start_time = None

        while self.is_running and self.camera.is_opened():
            ret, frame = self.camera.read()
            if not ret or frame is None:
                time.sleep(0.01)
                continue

            current_time = time.time()
            with torch.inference_mode():
                results = self.model(frame, imgsz=POSE_MODEL_IMGSZ, verbose=False)
            annotated_frame = frame.copy()
            feedback_msg = "Tracking posture..."
            feedback_color = "#00FFC8"

            # -------------------------------------------------------------
            # 1. PREPARATION COUNTDOWN
            # -------------------------------------------------------------
            if current_state == self.STATE_COUNTDOWN:
                elapsed = current_time - countdown_start
                remaining = COUNTDOWN_SECONDS - elapsed

                if remaining > 0:
                    h, w, _ = annotated_frame.shape
                    cx, cy = w // 2, h // 2

                    radius = 70
                    progress_angle = int((remaining / COUNTDOWN_SECONDS) * 360)
                    cv2.circle(annotated_frame, (cx, cy), radius, (45, 45, 55), 5)
                    cv2.ellipse(
                        annotated_frame, (cx, cy), (radius, radius), 0, -90, -90 + progress_angle, (0, 255, 200), 5
                    )
                    cv2.putText(
                        annotated_frame,
                        str(int(np.ceil(remaining))),
                        (cx - 15, cy + 18),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.8,
                        (255, 255, 255),
                        3
                    )

                    feedback_msg = f"Get Ready: {self.current_exercise} (Position into camera view)"
                    self._emit_frame(annotated_frame, feedback_msg, "#00FFC8")
                    continue
                else:
                    current_state = self.STATE_CALIBRATING

            # -------------------------------------------------------------
            # 2. KEYPOINT EXTRACTION & GESTURES
            # -------------------------------------------------------------
            if (
                results[0].keypoints is not None
                and len(results[0].keypoints.xy) > 0
                and len(results[0].keypoints.xy[0]) >= 17
            ):
                kpts = results[0].keypoints.xy[0].cpu().numpy()
                confs = (
                    results[0].keypoints.conf[0].cpu().numpy()
                    if results[0].keypoints.conf is not None
                    else np.ones(17)
                )

                # Hands-up reset gesture (always active)
                triggered, progress, gesture_start_time = check_hands_up_gesture(
                    kpts, confs, gesture_start_time, current_time, hold_threshold=GESTURE_HOLD_THRESHOLD
                )

                if progress > 0:
                    bar_w = int(220 * progress)
                    cv2.rectangle(
                        annotated_frame,
                        (frame.shape[1] // 2 - 110, 80),
                        (frame.shape[1] // 2 + 110, 100),
                        (35, 35, 42),
                        -1
                    )
                    cv2.rectangle(
                        annotated_frame,
                        (frame.shape[1] // 2 - 110, 80),
                        (frame.shape[1] // 2 - 110 + bar_w, 100),
                        (0, 255, 255),
                        -1
                    )
                    cv2.putText(
                        annotated_frame,
                        "HOLD TO RESET STATS",
                        (frame.shape[1] // 2 - 85, 74),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.45,
                        (0, 255, 255),
                        1
                    )

                if triggered:
                    self.reset_metrics()
                    feedback_msg = "Session Metrics Reset via Gesture!"
                    feedback_color = "#00FFC8"
                    gesture_start_time = None

                # Extract landmarks tailored to the selected exercise
                data = extract_exercise_data(
                    self.current_exercise,
                    kpts,
                    confs,
                    conf_threshold=PROFILE_CONF_THRESHOLD
                )

                if data["valid"]:
                    cfg = EXERCISE_CONFIGS[self.current_exercise]
                    pts = data["points"]

                    # ---------------------------------------------------------
                    # 3A. BICEP CURL DUAL-ARM PIPELINE
                    # ---------------------------------------------------------
                    if self.current_exercise == "BICEP_CURL":
                        l_rep, l_msg = False, None
                        r_rep, r_msg = False, None

                        if data.get("l_valid") and data.get("l_angle") is not None:
                            l_rep, l_msg = self.left_arm.update(
                                data["l_angle"],
                                cfg,
                                CALIBRATION_TARGET_FRAMES,
                                data.get("l_shoulder_angle")
                            )

                        if data.get("r_valid") and data.get("r_angle") is not None:
                            r_rep, r_msg = self.right_arm.update(
                                data["r_angle"],
                                cfg,
                                CALIBRATION_TARGET_FRAMES,
                                data.get("r_shoulder_angle")
                            )

                        # Check for active elbow drift across moving arms
                        active_arms = [arm for arm in (self.left_arm, self.right_arm) if arm.state in (1, 2, 3)]
                        unpinned_arms = [arm for arm in active_arms if not arm.is_elbow_locked]

                        for arm in unpinned_arms:
                            if not arm.has_warned_in_rep:
                                self.posture_warnings += 1
                                arm.has_warned_in_rep = True

                        # Torso stability check for curls (detect cheating body swing / hyperextension)
                        torso_swing_detected = False
                        if cfg.get("check_torso", True) and data.get("torso_angle") is not None and active_arms:
                            max_torso = cfg.get("max_torso_lean_angle", 22.0)
                            if data["torso_angle"] > max_torso:
                                torso_swing_detected = True
                                for arm in active_arms:
                                    arm.posture_fault_in_rep = True
                                    arm.fault_reason = "Torso Swing"
                                    if not arm.has_warned_in_rep:
                                        self.posture_warnings += 1
                                        arm.has_warned_in_rep = True

                        if l_rep or r_rep:
                            # Clean reps count strictly valid, non-faulted repetitions
                            self.clean_reps = self.left_arm.reps + self.right_arm.reps

                            # Determine if any completing arm had a form fault
                            l_fault = l_rep and (not self.left_arm.last_rep_clean)
                            r_fault = r_rep and (not self.right_arm.last_rep_clean)

                            if l_fault or r_fault:
                                fault_arm = self.left_arm if l_fault else self.right_arm
                                if "Incomplete" in (fault_arm.fault_reason or ""):
                                    self.failed_depth += 1
                                else:
                                    self.failed_posture += 1
                                feedback_msg = l_msg if l_fault else r_msg
                                feedback_color = "#FF1744"  # Strong Red Alert
                            else:
                                feedback_msg = l_msg or r_msg or "Clean Rep Counted!"
                                feedback_color = "#00E676"  # Vibrant Green Success
                        else:
                            # Contextual feedback for curls
                            if unpinned_arms:
                                feedback_msg = "Warning: Keep elbows pinned at sides!"
                                feedback_color = "#FF9100"
                            elif torso_swing_detected:
                                feedback_msg = "Warning: Back Swinging! Stand upright and isolate biceps"
                                feedback_color = "#FF9100"
                            else:
                                active_state = max(self.left_arm.state, self.right_arm.state)
                                if active_state == 2:
                                    feedback_msg = "Peak Contraction Reached! Lower weight smoothly"
                                    feedback_color = "#00FFC8"
                                elif active_state == 1:
                                    feedback_msg = "Curling up... Keep elbows locked to ribcage"
                                    feedback_color = "#00FFC8"
                                elif active_state == 0:
                                    feedback_msg = f"Ready! Begin curling. Total Clean Reps: {self.clean_reps}"
                                    feedback_color = "#00E676"
                                elif active_state == -1:
                                    feedback_msg = "Calibrating arm position... Hang arms relaxed"
                                    feedback_color = "#FF9100"

                        self._draw_bicep_curl_overlay(annotated_frame, data, cfg)

                    # ---------------------------------------------------------
                    # 3B. SQUAT / DEADLIFT SINGLE FSM WITH DUAL LIMB DRAWING
                    # ---------------------------------------------------------
                    else:
                        raw_primary = data["angle"]
                        smoothed_angle = angle_filter.update(raw_primary)
                        side = data["side"]
                        min_calib = cfg.get("min_calib_angle", 140.0)

                        if current_state == self.STATE_CALIBRATING:
                            if raw_primary > min_calib:
                                calibration_frames += 1
                                standing_baseline = (
                                    smoothed_angle
                                    if standing_baseline is None
                                    else 0.8 * standing_baseline + 0.2 * smoothed_angle
                                )
                                pct = int((calibration_frames / CALIBRATION_TARGET_FRAMES) * 100)
                                feedback_msg = f"Calibrating posture ({pct}%)... Hold position"
                                if calibration_frames >= CALIBRATION_TARGET_FRAMES:
                                    current_state = self.STATE_STANDING
                                    feedback_msg = f"Calibration Complete! Begin {self.current_exercise}."
                            else:
                                calibration_frames = max(0, calibration_frames - 1)
                                feedback_msg = f"Starting position needed (> {int(min_calib)} deg)..."

                        elif current_state == self.STATE_STANDING:
                            if smoothed_angle < cfg["down_thresh"]:
                                current_state = self.STATE_DESCENDING
                                depth_achieved = False
                                invalid_sit_flag = False
                                posture_fault_in_rep = False
                                sitting_start_time = None
                                feedback_msg = "Movement detected! Drive to depth..."

                        elif current_state == self.STATE_DESCENDING:
                            if cfg.get("check_sitting", False) and "hip" in pts and "knee" in pts and "ankle" in pts:
                                is_sit, _, _ = classify_sitting(pts["hip"], pts["knee"], pts["ankle"])
                                if is_sit:
                                    if sitting_start_time is None:
                                        sitting_start_time = current_time
                                    elif (current_time - sitting_start_time) > cfg.get("max_sit_hold_sec", 2.0):
                                        invalid_sit_flag = True
                                        feedback_msg = "RESTING / CHAIR SITTING (No Rep)"
                                        feedback_color = "#FF1744"
                                else:
                                    sitting_start_time = None

                            reached_depth = (smoothed_angle <= cfg["target_angle"])
                            if self.current_exercise == "SQUAT" and "hip" in pts and "knee" in pts:
                                if pts["hip"][1] >= (pts["knee"][1] - 12):
                                    reached_depth = True

                            if reached_depth and not invalid_sit_flag:
                                depth_achieved = True
                                current_state = self.STATE_BOTTOM
                                feedback_msg = "Target Depth! Now Drive Back!"
                                feedback_color = "#00FFC8"
                            elif standing_baseline is not None and smoothed_angle > (standing_baseline - 10.0):
                                current_state = self.STATE_STANDING
                                self.failed_depth += 1
                                feedback_msg = "NO REP: Incomplete Range of Motion"
                                feedback_color = "#FF9100"

                        elif current_state == self.STATE_BOTTOM:
                            if cfg.get("check_sitting", False) and "hip" in pts and "knee" in pts and "ankle" in pts:
                                is_sit, _, _ = classify_sitting(pts["hip"], pts["knee"], pts["ankle"])
                                if is_sit:
                                    if sitting_start_time is None:
                                        sitting_start_time = current_time
                                    elif (current_time - sitting_start_time) > cfg.get("max_sit_hold_sec", 2.0):
                                        invalid_sit_flag = True
                                        feedback_msg = "RESTING ON CHAIR (No Rep)"
                                        feedback_color = "#FF1744"
                                else:
                                    sitting_start_time = None

                            if smoothed_angle > cfg["ascent_hysteresis"]:
                                current_state = self.STATE_ASCENDING
                                feedback_msg = "Driving up to lockout..."

                        elif current_state == self.STATE_ASCENDING:
                            up_ref = cfg.get("up_thresh", 145.0)
                            baseline_ref = (standing_baseline - 12.0) if standing_baseline is not None else up_ref
                            if smoothed_angle >= min(up_ref, baseline_ref):
                                current_state = self.STATE_STANDING
                                if invalid_sit_flag:
                                    self.failed_sitting += 1
                                    feedback_msg = "REJECTED: Resting / Chair Sitting"
                                    feedback_color = "#FF1744"
                                elif depth_achieved:
                                    self.clean_reps += 1
                                    feedback_msg = f"Clean Rep #{self.clean_reps} Counted!"
                                    feedback_color = "#00E676"
                                else:
                                    self.failed_depth += 1
                                    feedback_msg = "NO REP: Incomplete Depth"
                                    feedback_color = "#FF9100"
                                depth_achieved = False
                                invalid_sit_flag = False
                                sitting_start_time = None

                        if cfg.get("check_torso", False) and current_state in [self.STATE_DESCENDING, self.STATE_BOTTOM]:
                            hip_ang = data.get("hip_angle")
                            if hip_ang is not None and hip_ang < cfg.get("min_torso_angle", 35.0):
                                feedback_msg = "Warning: Back Collapsing Forward! Keep chest up"
                                feedback_color = "#FF9100"
                                if not posture_fault_in_rep:
                                    self.posture_warnings += 1
                                    posture_fault_in_rep = True

                        self._draw_body_overlay(annotated_frame, data, cfg, smoothed_angle, side, current_state)

                        if data.get("is_frontal") and self.current_exercise == "SQUAT":
                            cv2.putText(
                                annotated_frame,
                                "Tip: 45 to 90 deg side profile is best for squat depth",
                                (25, annotated_frame.shape[0] - 25),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 255),
                                1
                            )
                else:
                    feedback_msg = data.get("missing_feedback") or "Position yourself in camera frame"
                    feedback_color = "#FF9100"
            else:
                gesture_start_time = None
                feedback_msg = "Looking for person in camera view..."
                feedback_color = "#FF9100"

            self._emit_frame(annotated_frame, feedback_msg, feedback_color)

        self.camera.release()

    def _draw_bicep_curl_overlay(
        self,
        frame: np.ndarray,
        data: Dict[str, Any],
        cfg: Dict[str, Any]
    ):
        """Renders skeletons, angle gauges, elbow lock status, and rep counts for BOTH arms."""
        pts = data["points"]
        target = int(cfg["target_angle"])

        # Top HUD Panel for Dual Arms (height 100px)
        cv2.rectangle(frame, (15, 15), (480, 100), (25, 25, 32), -1)
        cv2.rectangle(frame, (15, 15), (480, 100), (60, 60, 75), 1)

        # Title
        cv2.putText(
            frame,
            f"BICEP CURL DUAL-ARM TRACKER | Target: <= {target} deg",
            (25, 36),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.46,
            (0, 255, 200),
            1
        )

        l_str = f"L: {int(self.left_arm.smoothed_angle)} deg (Clean: {self.left_arm.reps} | No-Rep: {self.left_arm.failed_reps})" if data.get("l_valid") else "L: Not in view"
        r_str = f"R: {int(self.right_arm.smoothed_angle)} deg (Clean: {self.right_arm.reps} | No-Rep: {self.right_arm.failed_reps})" if data.get("r_valid") else "R: Not in view"

        l_color = (0, 255, 0) if self.left_arm.smoothed_angle <= target else (255, 255, 255)
        r_color = (0, 255, 0) if self.right_arm.smoothed_angle <= target else (255, 255, 255)

        cv2.putText(frame, l_str, (25, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.46, l_color, 1)
        cv2.putText(frame, r_str, (250, 56), cv2.FONT_HERSHEY_SIMPLEX, 0.46, r_color, 1)
        cv2.putText(frame, f"Total Clean Reps: {self.clean_reps} | Form Faults: {self.failed_posture}", (25, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (0, 255, 200), 1)

        # Elbow Lock / Drift Status Indicator
        both_locked = self.left_arm.is_elbow_locked and self.right_arm.is_elbow_locked
        if both_locked:
            lock_text = f"Elbows: PINNED TO RIBS | Form Faults: {self.failed_posture}"
            lock_color = (0, 255, 150)
        else:
            fault_sides = []
            if not self.left_arm.is_elbow_locked:
                fault_sides.append("L-DRIFT")
            if not self.right_arm.is_elbow_locked:
                fault_sides.append("R-DRIFT")
            lock_text = f"Elbows: {' '.join(fault_sides)} (LOCK TO RIBS) | Faults: {self.failed_posture}"
            lock_color = (0, 80, 255)
        cv2.putText(frame, lock_text, (25, 92), cv2.FONT_HERSHEY_SIMPLEX, 0.40, lock_color, 1)

        # Draw Left Arm
        if data.get("l_valid") and "l_shoulder" in pts and "l_elbow" in pts and "l_wrist" in pts:
            sh = (int(pts["l_shoulder"][0]), int(pts["l_shoulder"][1]))
            el = (int(pts["l_elbow"][0]), int(pts["l_elbow"][1]))
            wr = (int(pts["l_wrist"][0]), int(pts["l_wrist"][1]))

            # Forearm color (flexion)
            forearm_color = (0, 255, 0) if self.left_arm.smoothed_angle <= target else (0, 255, 200)

            # Upper arm color (elbow locked vs drifted)
            if not self.left_arm.is_elbow_locked and self.left_arm.state in (1, 2, 3):
                upper_arm_color = (0, 69, 255)  # Bright orange/red warning
                upper_arm_width = 4
                drift_label = f"L SWING ({int(self.left_arm.smoothed_shoulder_angle)} deg)"
            else:
                upper_arm_color = (255, 140, 0)  # Pinned cyan/blue
                upper_arm_width = 3
                drift_label = f"L Pinned ({int(self.left_arm.smoothed_shoulder_angle)} deg)"

            cv2.line(frame, sh, el, upper_arm_color, upper_arm_width)
            cv2.line(frame, el, wr, forearm_color, 3)
            cv2.circle(frame, el, 8, upper_arm_color, -1)
            cv2.circle(frame, wr, 5, forearm_color, -1)
            cv2.putText(
                frame,
                f"L: {int(self.left_arm.smoothed_angle)} deg",
                (el[0] - 65, el[1] - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                forearm_color,
                2
            )
            cv2.putText(
                frame,
                drift_label,
                (sh[0] - 90, (sh[1] + el[1]) // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.38,
                upper_arm_color,
                1
            )

        # Draw Right Arm
        if data.get("r_valid") and "r_shoulder" in pts and "r_elbow" in pts and "r_wrist" in pts:
            sh = (int(pts["r_shoulder"][0]), int(pts["r_shoulder"][1]))
            el = (int(pts["r_elbow"][0]), int(pts["r_elbow"][1]))
            wr = (int(pts["r_wrist"][0]), int(pts["r_wrist"][1]))

            forearm_color = (0, 255, 0) if self.right_arm.smoothed_angle <= target else (0, 255, 200)

            if not self.right_arm.is_elbow_locked and self.right_arm.state in (1, 2, 3):
                upper_arm_color = (0, 69, 255)  # Bright orange/red warning
                upper_arm_width = 4
                drift_label = f"R SWING ({int(self.right_arm.smoothed_shoulder_angle)} deg)"
            else:
                upper_arm_color = (255, 140, 0)  # Pinned cyan/blue
                upper_arm_width = 3
                drift_label = f"R Pinned ({int(self.right_arm.smoothed_shoulder_angle)} deg)"

            cv2.line(frame, sh, el, upper_arm_color, upper_arm_width)
            cv2.line(frame, el, wr, forearm_color, 3)
            cv2.circle(frame, el, 8, upper_arm_color, -1)
            cv2.circle(frame, wr, 5, forearm_color, -1)
            cv2.putText(
                frame,
                f"R: {int(self.right_arm.smoothed_angle)} deg",
                (el[0] + 15, el[1] - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                forearm_color,
                2
            )
            cv2.putText(
                frame,
                drift_label,
                (sh[0] + 15, (sh[1] + el[1]) // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.38,
                upper_arm_color,
                1
            )

    def _draw_body_overlay(
        self,
        frame: np.ndarray,
        data: Dict[str, Any],
        cfg: Dict[str, Any],
        smoothed_angle: float,
        side: str,
        current_state: int
    ):
        """Renders skeletons and telemetry for Squats and Deadlifts."""
        pts = data["points"]
        joint_color = (0, 255, 200)
        accent_color = (255, 140, 0)

        # Draw Left Leg if valid
        if data.get("l_valid") and "l_hip" in pts and "l_knee" in pts:
            hp = (int(pts["l_hip"][0]), int(pts["l_hip"][1]))
            kn = (int(pts["l_knee"][0]), int(pts["l_knee"][1]))
            cv2.line(frame, hp, kn, joint_color, 3)
            cv2.circle(frame, kn, 7, (0, 255, 0), -1)
            if "l_ankle" in pts:
                ak = (int(pts["l_ankle"][0]), int(pts["l_ankle"][1]))
                cv2.line(frame, kn, ak, joint_color, 3)
                cv2.circle(frame, ak, 5, joint_color, -1)

        # Draw Right Leg if valid
        if data.get("r_valid") and "r_hip" in pts and "r_knee" in pts:
            hp = (int(pts["r_hip"][0]), int(pts["r_hip"][1]))
            kn = (int(pts["r_knee"][0]), int(pts["r_knee"][1]))
            cv2.line(frame, hp, kn, joint_color, 3)
            cv2.circle(frame, kn, 7, (0, 255, 0), -1)
            if "r_ankle" in pts:
                ak = (int(pts["r_ankle"][0]), int(pts["r_ankle"][1]))
                cv2.line(frame, kn, ak, joint_color, 3)
                cv2.circle(frame, ak, 5, joint_color, -1)

        # Draw Spine / Torso
        if "shoulder" in pts and "hip" in pts:
            sh = (int(pts["shoulder"][0]), int(pts["shoulder"][1]))
            hp = (int(pts["hip"][0]), int(pts["hip"][1]))
            cv2.line(frame, sh, hp, accent_color, 3)

        # Telemetry HUD Pill
        state_label = self.STATE_NAMES.get(current_state, "TRACKING")
        cv2.rectangle(frame, (15, 15), (380, 75), (25, 25, 32), -1)
        cv2.rectangle(frame, (15, 15), (380, 75), (60, 60, 75), 1)

        cv2.putText(
            frame,
            f"{self.current_exercise} | STATE: {state_label}",
            (25, 38),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 200),
            1
        )

        cv2.putText(
            frame,
            f"{cfg['joint_tracked']} ({side}): {int(smoothed_angle)} deg | Target: <= {int(cfg['target_angle'])} deg",
            (25, 62),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            1
        )

    def _emit_frame(self, frame: np.ndarray, feedback_msg: str, feedback_color: str):
        """Dispatches processed frame and metrics to the registered callback."""
        if self.on_frame_processed:
            self.on_frame_processed(frame, feedback_msg, feedback_color, self.get_stats())
