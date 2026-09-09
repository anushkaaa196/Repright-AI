"""Test verification script for Bicep Curl Elbow-to-Ribcage Locking and Drift Detection."""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import EXERCISE_CONFIGS, CALIBRATION_TARGET_FRAMES
from core.geometry import extract_exercise_data, calculate_angle
from core.exercise_guidance import classify_posture_feedback
from core.rep_analysis import analyze_repetition
from core.session_insights import generate_session_insights
from backend.engine import LimbTracker


def run_tests():
    print("============================================================")
    print("RUNNING BICEP CURL ELBOW LOCK & DRIFT VERIFICATION TESTS")
    print("============================================================")

    # --------------------------------------------------------------------------
    # TEST 1: Geometry extraction - Pinned vs Drifted Upper Arm Angles
    # --------------------------------------------------------------------------
    print("\n--- TEST 1: Geometry Extraction (Pinned vs Drifted) ---")
    kpts = np.zeros((17, 2), dtype=float)
    confs = np.ones(17, dtype=float)

    # Left side: Pinned elbow
    # Shoulder at (200, 100), Hip at (200, 300) -> torso is vertical downward
    # Elbow at (205, 220) -> upper arm hangs directly downward beside torso (pinned)
    # Wrist at (205, 340) -> hanging down at full extension
    kpts[5] = [200.0, 100.0]  # L Shoulder
    kpts[7] = [205.0, 220.0]  # L Elbow (pinned beside ribcage)
    kpts[9] = [205.0, 340.0]  # L Wrist
    kpts[11] = [200.0, 300.0] # L Hip (torso anchor)

    # Right side: Swung / flared elbow
    # Shoulder at (300, 100), Hip at (300, 300)
    # Elbow swung forward / flared outward at (380, 180) -> high drift angle
    kpts[6] = [300.0, 100.0]  # R Shoulder
    kpts[8] = [380.0, 180.0]  # R Elbow (swung forward / flared away from ribcage)
    kpts[10] = [380.0, 100.0] # R Wrist
    kpts[12] = [300.0, 300.0] # R Hip

    data = extract_exercise_data("BICEP_CURL", kpts, confs)
    assert data["valid"] is True
    assert data["l_valid"] is True
    assert data["r_valid"] is True

    l_drift = data["l_shoulder_angle"]
    r_drift = data["r_shoulder_angle"]
    print(f"Left upper-arm angle (Pinned): {l_drift:.1f} deg")
    print(f"Right upper-arm angle (Drifted): {r_drift:.1f} deg")

    assert l_drift < 15.0, f"Expected pinned arm angle < 15, got {l_drift}"
    assert r_drift > 35.0, f"Expected drifted arm angle > 35, got {r_drift}"
    print("✓ TEST 1 PASSED: Upper arm shoulder drift angles accurately computed.")

    # --------------------------------------------------------------------------
    # TEST 2: LimbTracker - Pinned Curl Rep Lifecycle
    # --------------------------------------------------------------------------
    print("\n--- TEST 2: LimbTracker Pinned Rep (Clean Form) ---")
    cfg = EXERCISE_CONFIGS["BICEP_CURL"]
    tracker = LimbTracker("Left")

    # Step A: Calibration with arm pinned (elbow flex 170 deg, shoulder angle 8 deg)
    for _ in range(CALIBRATION_TARGET_FRAMES + 2):
        tracker.update(170.0, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=8.0)
    assert tracker.state == 0, f"Expected state 0 (READY), got {tracker.state}"
    assert tracker.standing_shoulder_baseline is not None
    print(f"Calibrated baseline shoulder angle: {tracker.standing_shoulder_baseline:.1f} deg")

    # Step B: Curl upward with elbow pinned (shoulder angle stays ~8-12 deg)
    for flex_ang in [140.0, 120.0, 100.0, 80.0] + [60.0] * 6:  # reaches target <= 65
        tracker.update(flex_ang, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=10.0)
    assert tracker.state == 2, f"Expected state 2 (PEAK CONTRACTION), got {tracker.state}"
    assert tracker.depth_achieved is True
    assert tracker.is_elbow_locked is True
    assert tracker.posture_fault_in_rep is False
    print("Peak contraction reached with elbow locked to ribcage.")

    # Step C: Lower arm back down
    rep_counted = False
    msg = None
    for flex_ang in [80.0, 100.0, 120.0] + [140.0] * 6:
        rc, m = tracker.update(flex_ang, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=8.0)
        if rc:
            rep_counted = True
            msg = m

    assert rep_counted is True
    assert tracker.reps == 1
    assert tracker.posture_fault_in_rep is False
    assert "Clean Rep" in msg
    print(f"Rep completed successfully: '{msg}'")
    print("✓ TEST 2 PASSED: Pinned curl counted as Clean Rep without warnings.")

    # --------------------------------------------------------------------------
    # TEST 3: LimbTracker - Unpinned / Swinging Elbow Curl
    # --------------------------------------------------------------------------
    print("\n--- TEST 3: LimbTracker Unpinned / Drifted Rep ---")
    # Step A: Initiate curl, but elbow swings forward (shoulder angle 42 deg)
    for flex_ang in [120.0, 110.0, 100.0, 95.0]:
        tracker.update(flex_ang, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=15.0)  # state -> 1
    assert tracker.state == 1, f"Expected state 1 (CURLING UP), got {tracker.state}"

    # Now user swings elbow forward to heave the weight up (shoulder angle jumps to 45 deg)
    for flex_ang in [85.0, 75.0] + [60.0] * 6:
        tracker.update(flex_ang, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=45.0)

    assert tracker.state == 2, f"Expected state 2 (PEAK), got {tracker.state}"
    assert tracker.is_elbow_locked is False, "Expected is_elbow_locked == False"
    assert tracker.posture_fault_in_rep is True, "Expected posture_fault_in_rep == True"
    print(f"Elbow drift detected! is_elbow_locked={tracker.is_elbow_locked}, fault={tracker.posture_fault_in_rep}")

    # Lower weight back to lockout
    rep_counted = False
    msg = None
    for flex_ang in [80.0, 100.0, 120.0] + [140.0] * 6:
        rc, m = tracker.update(flex_ang, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=30.0)
        if rc:
            rep_counted = True
            msg = m

    assert rep_counted is True
    assert tracker.reps == 1, f"Clean reps should NOT increase on wrong form! Got {tracker.reps}"
    assert tracker.failed_reps == 1, f"Expected 1 failed rep, got {tracker.failed_reps}"
    assert tracker.last_rep_clean is False, "Expected last_rep_clean == False"
    assert "NO REP" in msg and "Unpinned" in msg
    print(f"Rep rejected with posture warning: '{msg}'")
    print("✓ TEST 3 PASSED: Unpinned curl is rejected (no clean rep counted) with posture warning.")

    # --------------------------------------------------------------------------
    # TEST 4: Posture Feedback Classification
    # --------------------------------------------------------------------------
    print("\n--- TEST 4: Posture Feedback Classification ---")
    # Clean rep:
    c_clean = classify_posture_feedback("BICEP_CURL", "Left Arm Clean Rep #1 Counted!", "#00E676")
    assert c_clean["category"] == "CORRECT"
    assert c_clean["status_label"] == "OPTIMAL FORM"

    # Warning during movement:
    c_warn = classify_posture_feedback("BICEP_CURL", "Warning: Keep elbows pinned at sides!", "#FF9100")
    assert c_warn["category"] == "WARNING"
    assert c_warn["status_label"] == "ADJUST FORM"
    assert c_warn["body_focus"] == "ELBOWS"
    assert "ribcage" in c_warn["action"].lower() or "elbows" in c_warn["action"].lower()

    # Rep completed with warning:
    c_rep_warn = classify_posture_feedback("BICEP_CURL", "NO REP: Left Arm Unpinned Elbow (Keep elbows pinned at sides)", "#FF1744")
    assert c_rep_warn["body_focus"] == "ELBOWS"
    print("✓ TEST 4 PASSED: Feedback messages correctly map to ADJUST FORM / ELBOWS.")

    # --------------------------------------------------------------------------
    # TEST 5: Rep Analysis - Scoring Penalty on Unpinned Rep
    # --------------------------------------------------------------------------
    print("\n--- TEST 5: Rep Analysis Scoring ---")
    r_clean = analyze_repetition(
        exercise_name="BICEP_CURL",
        rep_number=1,
        rep_result="CLEAN",
        posture_warning_occurred=False
    )
    r_warn = analyze_repetition(
        exercise_name="BICEP_CURL",
        rep_number=2,
        rep_result="CLEAN",
        posture_warning_occurred=True
    )

    print(f"Clean Rep score: {r_clean['overall_score']} | Alignment: {r_clean['dimension_scores']['alignment']}")
    print(f"Unpinned Rep score: {r_warn['overall_score']} | Alignment: {r_warn['dimension_scores']['alignment']}")
    print(f"Unpinned Rep issues: {r_warn['issues']}")
    print(f"Unpinned Rep primary focus: {r_warn['primary_focus']}")

    assert r_warn["overall_score"] < r_clean["overall_score"], "Score must be penalized"
    assert r_warn["dimension_scores"]["alignment"] < r_clean["dimension_scores"]["alignment"], "Elbow stability must be penalized"
    assert any("elbow" in issue.lower() for issue in r_warn["issues"]), "Expected elbow issue in rep analysis"
    print("✓ TEST 5 PASSED: Rep analysis accurately penalizes unpinned elbow rep.")

    # --------------------------------------------------------------------------
    # TEST 6: Session Insights - Bicep Curl Elbow Recommendations
    # --------------------------------------------------------------------------
    print("\n--- TEST 6: Session Insights ---")
    stats_clean = {
        "clean_reps": 10,
        "total_attempts": 10,
        "accuracy": 100,
        "failed_depth": 0,
        "failed_sitting": 0,
        "posture_warnings": 0
    }
    stats_faulty = {
        "clean_reps": 8,
        "total_attempts": 8,
        "accuracy": 100,
        "failed_depth": 0,
        "failed_sitting": 0,
        "posture_warnings": 3
    }

    insights_clean = generate_session_insights("BICEP_CURL", stats_clean, 60)
    insights_faulty = generate_session_insights("BICEP_CURL", stats_faulty, 60)

    assert any("elbow" in s.lower() for s in insights_clean["strengths"])
    print(f"Clean session strength: {insights_clean['strengths'][0]}")

    assert any("elbow" in imp.lower() for imp in insights_faulty["improvements"])
    assert insights_faulty["primary_focus"] == "ELBOW STABILITY"
    print(f"Faulty session focus: {insights_faulty['primary_focus']}")
    print(f"Faulty session recommendation: {insights_faulty['recommendation']}")
    print("✓ TEST 6 PASSED: Session insights tailor focus to ELBOW STABILITY.")

    print("\n============================================================")
    print("ALL 6 TESTS PASSED SUCCESSFULLY!")
    print("============================================================")


if __name__ == "__main__":
    run_tests()
