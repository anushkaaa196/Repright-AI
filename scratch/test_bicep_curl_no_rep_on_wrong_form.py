"""Test verification that bicep curl rep counter does NOT increase on wrong form."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import EXERCISE_CONFIGS, CALIBRATION_TARGET_FRAMES
from backend.engine import LimbTracker, WorkoutEngine


def test_bicep_curl_wrong_form_rejection():
    print("--- 1. Testing LimbTracker Strict Rep Qualification ---")
    cfg = EXERCISE_CONFIGS["BICEP_CURL"]
    arm = LimbTracker("Left")

    # 1. Calibrate
    for _ in range(CALIBRATION_TARGET_FRAMES + 2):
        arm.update(140.0, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=8.0)
    assert arm.state == 0, f"Expected state 0 (READY), got {arm.state}"
    assert arm.reps == 0
    assert arm.failed_reps == 0

    # 2. Perform a CLEAN rep (elbows pinned to ribs, shoulder angle ~8 deg)
    for ang in [120.0, 100.0, 80.0, 60.0, 50.0, 50.0, 50.0]:
        arm.update(ang, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=8.0)
    assert arm.state == 2, f"Expected state 2 (PEAK), got {arm.state}"
    assert arm.depth_achieved is True
    assert arm.is_elbow_locked is True
    assert arm.posture_fault_in_rep is False

    rep_done, clean_msg = False, None
    for ang in [80.0, 100.0, 120.0, 135.0, 140.0, 140.0, 140.0]:
        rc, m = arm.update(ang, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=8.0)
        if rc:
            rep_done = True
            clean_msg = m

    assert rep_done is True
    assert arm.reps == 1, f"Clean rep must increment reps! Got {arm.reps}"
    assert arm.failed_reps == 0
    assert arm.last_rep_clean is True
    assert "Clean Rep #1 Counted" in clean_msg
    print(f"  [OK] Clean curl accepted: reps={arm.reps}, msg='{clean_msg}'")

    # 3. Perform a WRONG FORM rep (elbows flare / swing forward to 45 deg)
    for ang in [110.0, 90.0, 70.0, 50.0, 45.0, 45.0, 45.0]:
        arm.update(ang, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=45.0)
    assert arm.state == 2, f"Expected state 2 (PEAK), got {arm.state}"
    assert arm.depth_achieved is True
    assert arm.is_elbow_locked is False, "Elbow lock must be broken"
    assert arm.posture_fault_in_rep is True, "Posture fault must be flagged"

    # Lower weight back to lockout
    fault_done, fault_msg = False, None
    for ang in [80.0, 100.0, 120.0] + [140.0] * 6:
        rc, m = arm.update(ang, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=35.0)
        if rc:
            fault_done = True
            fault_msg = m

    assert fault_done is True
    # CRITICAL CHECK: Rep counter must NOT have increased!
    assert arm.reps == 1, f"CRITICAL: Rep counter increased on wrong form! Expected 1, got {arm.reps}"
    assert arm.failed_reps == 1, f"Failed reps should be 1, got {arm.failed_reps}"
    assert arm.last_rep_clean is False, "last_rep_clean should be False"
    assert "NO REP" in fault_msg, f"Expected 'NO REP' in message, got '{fault_msg}'"
    print(f"  [OK] Wrong form curl rejected: reps={arm.reps} (unchanged!), failed_reps={arm.failed_reps}, msg='{fault_msg}'")

    # 4. Perform an INCOMPLETE ROM curl (curls to 80 deg then gives up, doesn't reach peak <= 65 deg)
    for ang in [110.0, 90.0, 80.0, 80.0, 80.0]:
        arm.update(ang, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=8.0)
    assert arm.state == 1
    assert arm.depth_achieved is False

    # Drops weight back down without reaching apex
    incomp_done, incomp_msg = False, None
    for ang in [100.0, 120.0, 135.0] + [140.0] * 6:
        rc, m = arm.update(ang, cfg, CALIBRATION_TARGET_FRAMES, raw_shoulder_angle=8.0)
        if rc:
            incomp_done = True
            incomp_msg = m

    assert incomp_done is True
    assert arm.reps == 1, f"Clean reps should NOT increase on incomplete curl! Got {arm.reps}"
    assert arm.failed_reps == 2, f"Failed reps should be 2, got {arm.failed_reps}"
    assert "NO REP" in incomp_msg and "Incomplete" in incomp_msg
    print(f"  [OK] Incomplete ROM curl rejected: reps={arm.reps} (unchanged!), failed_reps={arm.failed_reps}, msg='{incomp_msg}'")


def test_workout_engine_stats_integrity():
    print("\n--- 2. Testing WorkoutEngine Stats & Accuracy Calculation ---")
    engine = WorkoutEngine()
    engine.current_exercise = "BICEP_CURL"

    # Simulate Left Arm: 2 clean reps, 1 failed rep
    engine.left_arm.reps = 2
    engine.left_arm.failed_reps = 1

    # Simulate Right Arm: 1 clean rep, 1 failed rep
    engine.right_arm.reps = 1
    engine.right_arm.failed_reps = 1

    engine.clean_reps = engine.left_arm.reps + engine.right_arm.reps  # 3 clean
    engine.failed_posture = engine.left_arm.failed_reps + engine.right_arm.failed_reps  # 2 failed

    stats = engine.get_stats()
    assert stats["clean_reps"] == 3
    assert stats["failed_posture"] == 2
    assert stats["total_attempts"] == 5
    assert stats["accuracy"] == 60  # (3 / 5) * 100 = 60%
    print(f"  [OK] Telemetry integrity verified: Clean={stats['clean_reps']}, Failed={stats['failed_posture']}, Total={stats['total_attempts']}, Acc={stats['accuracy']}%")


if __name__ == "__main__":
    test_bicep_curl_wrong_form_rejection()
    test_workout_engine_stats_integrity()
    print("\n[SUCCESS] All Bicep Curl Form Rejection Tests Passed!")
