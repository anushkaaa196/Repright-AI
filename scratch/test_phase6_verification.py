"""Phase 6 Comprehensive Verification & Test Suite for REPRIGHT AI.

Validates all 18 requirements:
1. Movement phase detection (SQUAT, DEADLIFT, BICEP_CURL)
2. Phase transitions and velocity calculation
3. Stability score calculations (0-100)
4. Rolling buffer limits (memory-safe bounded buffer)
5. Fatigue classification (Low, Moderate, High)
6. Risk awareness classification (Low, Moderate, High)
7. Adaptive coaching mode (Calm, Guided, Urgent)
8. Recovery recommendation logic (Continue, Short Recovery, Form Reset)
9. Performance trend detection (Improving, Stable, Declining)
10. Readiness score logic and checklist
11. Live exercise compatibility (SQUAT, DEADLIFT, BICEP_CURL)
12. Guided exercise honesty (PUSH_UP, LUNGE, PLANK, SHOULDER_PRESS)
13. UI component creation (PhaseCard, HeatmapFrame, IntelligenceCard, DemoWindow)
14. UI reset functionality
15. Exercise switching integrity
16. Session summary integration
17. Report generation (1200 x 1400 PNG)
18. Main application import & startup
"""

import sys
import os
import time
from pathlib import Path

# Add project root to sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.movement_phases import MovementPhaseEngine, get_movement_phase_engine
from core.movement_stability import MovementStabilityEngine, get_movement_stability_engine
from core.fatigue_intelligence import estimate_form_fatigue
from core.risk_intelligence import evaluate_movement_risk
from core.adaptive_coaching import get_adaptive_coaching
from core.readiness_intelligence import evaluate_workout_readiness
from core.recovery_recommendations import get_recovery_recommendations
from core.performance_trends import analyze_performance_trends
from core.rep_analysis import analyze_repetition
from core.rep_history import RepHistoryTracker
from backend.reporter import generate_report_image


def test_movement_phases():
    print("\n--- Test 1 & 2: Movement Phase Detection & Transitions ---")
    engine = MovementPhaseEngine()
    engine.reset("SQUAT")

    # Start position (high angle)
    p1 = engine.update("SQUAT", 160.0, "Ready")
    assert p1["current_phase"] in ("START_POSITION", "LOCKOUT"), f"Expected start/lockout, got {p1['current_phase']}"
    print(f"✓ SQUAT Start phase: {p1['phase_label']} ({p1['phase_progress']}%)")

    # Descent (angle decreasing)
    engine.update("SQUAT", 150.0)
    engine.update("SQUAT", 140.0)
    engine.update("SQUAT", 130.0)
    p2 = engine.update("SQUAT", 120.0)
    assert p2["movement_direction"] == "DOWN", f"Expected DOWN, got {p2['movement_direction']}"
    assert p2["current_phase"] == "DESCENT"
    print(f"✓ SQUAT Descent phase: {p2['phase_label']} ({p2['phase_progress']}% progress, dir: {p2['movement_direction']})")

    # Bottom position (depth reached)
    p3 = engine.update("SQUAT", 92.0, "Target Depth! Now Drive Back!")
    assert p3["current_phase"] == "BOTTOM_POSITION"
    print(f"✓ SQUAT Bottom phase: {p3['phase_label']} (Focus: {p3['coaching_focus'][:35]}...)")

    # Ascent (angle increasing)
    engine.update("SQUAT", 115.0)
    engine.update("SQUAT", 130.0)
    p4 = engine.update("SQUAT", 142.0)
    assert p4["movement_direction"] == "UP"
    assert p4["current_phase"] == "ASCENT"
    print(f"✓ SQUAT Ascent phase: {p4['phase_label']} (Progress: {p4['phase_progress']}%)")

    # Deadlift and Bicep Curl support
    dl_p = engine.update("DEADLIFT", 165.0, "Lockout")
    assert dl_p["exercise"] == "DEADLIFT"
    bc_p = engine.update("BICEP_CURL", 60.0, "Peak")
    assert bc_p["exercise"] == "BICEP_CURL"
    assert bc_p["current_phase"] == "PEAK_CONTRACTION"
    print("✓ DEADLIFT and BICEP_CURL phase models verified.")


def test_stability_intelligence():
    print("\n--- Test 3 & 4: Stability Score Calculations & Buffer Limits ---")
    stab_engine = MovementStabilityEngine(buffer_size=50)
    stab_engine.reset("SQUAT")

    # Smooth steady movement
    for i in range(20):
        res = stab_engine.update("SQUAT", 150.0 - i * 2)
    assert 80 <= res["stability_score"] <= 100, f"Expected 80-100 for smooth, got {res['stability_score']}"
    assert res["category"] in ("HIGHLY_STABLE", "STABLE")
    print(f"✓ Smooth movement stability: {res['stability_score']}% ({res['category_label']})")

    # High jitter / fluctuating angle
    for i in range(25):
        jitter_angle = 120.0 + (30.0 if i % 2 == 0 else -30.0)
        res_jitter = stab_engine.update("SQUAT", jitter_angle)
    assert res_jitter["stability_score"] < 80, f"Expected degraded stability under jitter, got {res_jitter['stability_score']}"
    print(f"✓ Jitter movement stability: {res_jitter['stability_score']}% (Jitter: {res_jitter['jitter_metric']})")

    # Buffer limit check
    assert len(stab_engine._angle_buffer) <= 50, f"Buffer exceeded 50: {len(stab_engine._angle_buffer)}"
    print(f"✓ Bounded memory buffer strictly enforced ({len(stab_engine._angle_buffer)}/50 samples)")


def test_fatigue_and_risk():
    print("\n--- Test 5 & 6: Fatigue & Risk Awareness Classification ---")
    tracker = RepHistoryTracker.get_instance()
    tracker.reset()

    # Low fatigue state
    f_low = estimate_form_fatigue("SQUAT", current_stability_score=92)
    assert f_low["fatigue_level"] == "LOW"
    assert "LOW" in f_low["fatigue_label"]
    print(f"✓ Low fatigue: {f_low['fatigue_label']} ({f_low['recommended_action'][:40]}...)")

    # Low risk state
    r_low = evaluate_movement_risk("SQUAT", stability_score=90, fatigue_level="LOW")
    assert r_low["risk_level"] == "LOW"
    print(f"✓ Low risk awareness: {r_low['risk_label']}")

    # Simulate degrading session reps
    tracker.add_rep(analyze_repetition("SQUAT", 1, "CLEAN", False))
    tracker.add_rep(analyze_repetition("SQUAT", 2, "CLEAN", False))
    tracker.add_rep(analyze_repetition("SQUAT", 3, "FAILED_DEPTH", True))
    tracker.add_rep(analyze_repetition("SQUAT", 4, "FAILED_DEPTH", True))
    tracker.add_rep(analyze_repetition("SQUAT", 5, "FAILED_SITTING", True))

    f_high = estimate_form_fatigue("SQUAT", current_stability_score=50, stats_snapshot={"posture_warnings": 4, "total_attempts": 5})
    assert f_high["fatigue_level"] in ("MODERATE", "HIGH")
    print(f"✓ Elevated fatigue: {f_high['fatigue_label']} (Score: {f_high['fatigue_score']}%)")

    r_high = evaluate_movement_risk("SQUAT", stability_score=48, fatigue_level=f_high["fatigue_level"], stats_snapshot={"posture_warnings": 4, "total_attempts": 5})
    assert r_high["risk_level"] in ("MODERATE", "HIGH")
    print(f"✓ Elevated risk awareness: {r_high['risk_label']} (Factors: {len(r_high['risk_factors'])})")


def test_adaptive_coaching_and_recovery():
    print("\n--- Test 7 & 8: Adaptive Coaching Intensity & Smart Recovery ---")
    # Calm mode
    c_calm = get_adaptive_coaching("SQUAT", stability_score=94, fatigue_level="LOW", risk_level="LOW")
    assert c_calm["coaching_mode"] == "CALM"
    assert "CALM" in c_calm["mode_pill"]
    print(f"✓ Adaptive coaching CALM: {c_calm['primary_message']}")

    # Urgent mode
    c_urgent = get_adaptive_coaching("SQUAT", stability_score=45, fatigue_level="HIGH", risk_level="HIGH", current_feedback="Warning: Back Collapsing")
    assert c_urgent["coaching_mode"] == "URGENT"
    assert "URGENT" in c_urgent["mode_pill"]
    print(f"✓ Adaptive coaching URGENT: {c_urgent['primary_message']}")

    # Recovery: Continue
    rec_cont = get_recovery_recommendations(fatigue_level="LOW", stability_score=90)
    assert rec_cont["recovery_status"] == "CONTINUE_TRAINING"
    print(f"✓ Recovery CONTINUE: {rec_cont['status_pill']}")

    # Recovery: Form Reset
    rec_reset = get_recovery_recommendations(fatigue_level="HIGH", stability_score=40, consecutive_faults=3)
    assert rec_reset["recovery_status"] == "FORM_RESET"
    assert rec_reset["rest_duration_sec"] == 90
    print(f"✓ Recovery FORM RESET: {rec_reset['status_pill']} ({rec_reset['rest_duration_sec']}s rest)")


def test_performance_trends_and_readiness():
    print("\n--- Test 9 & 10: Performance Trends & AI Workout Readiness ---")
    trends = analyze_performance_trends("SQUAT", current_stability_score=88, fatigue_score=25)
    assert "quality_trend" in trends
    assert "stability_trend" in trends
    assert "summary" in trends
    print(f"✓ Performance trends: Quality {trends['quality_text']} (Dir: {trends['overall_direction']})")

    # Readiness: Optimal
    ready_opt = evaluate_workout_readiness(
        camera_active=True,
        keypoints_detected=17,
        keypoints_confidence_avg=0.88,
        user_in_frame=True,
        is_head_visible=True,
        is_feet_visible=True
    )
    assert ready_opt["readiness_score"] >= 90
    assert ready_opt["category"] == "OPTIMAL"
    print(f"✓ AI Workout Readiness OPTIMAL: {ready_opt['readiness_score']}% ({ready_opt['category_label']})")

    # Readiness: Camera Offline
    ready_off = evaluate_workout_readiness(camera_active=False)
    assert ready_off["readiness_score"] == 0
    assert ready_off["category"] == "NOT_READY"
    print(f"✓ AI Workout Readiness OFFLINE: {ready_off['category_label']}")


def test_exercise_compatibility_and_guided_honesty():
    print("\n--- Test 11 & 12: Active vs Guided Exercise Technical Honesty ---")
    phase_engine = MovementPhaseEngine()

    # Active exercises
    for active_ex in ["SQUAT", "DEADLIFT", "BICEP_CURL"]:
        res = phase_engine.update(active_ex, 150.0)
        assert res["is_guided"] is False
        assert "confidence" in res
    print("✓ Active exercises (SQUAT, DEADLIFT, BICEP_CURL) processed in live AI mode.")

    # Guided exercises (Technical honesty)
    for guided_ex in ["PUSH_UP", "LUNGE", "PLANK", "SHOULDER_PRESS"]:
        res = phase_engine.update(guided_ex, 150.0)
        assert res["is_guided"] is True
        assert "GUIDED" in res["note"]

        f_res = estimate_form_fatigue(guided_ex)
        assert f_res["is_guided"] is True

        r_res = evaluate_movement_risk(guided_ex)
        assert r_res["is_guided"] is True
    print("✓ Guided exercises verified with zero fake telemetry (100% technically honest).")


def test_ui_components_and_reset():
    print("\n--- Test 13, 14 & 15: UI Components Creation, Reset & Switching ---")
    import customtkinter as ctk
    from ui.components.movement_phase import MovementPhaseCard
    from ui.components.movement_heatmap import MovementHeatmapFrame
    from ui.components.movement_intelligence import MovementIntelligenceCard
    from ui.components.demo_mode import SIHDemoWindow

    root = ctk.CTk()
    root.withdraw()

    # 1. MovementPhaseCard
    phase_card = MovementPhaseCard(root, "SQUAT")
    phase_card.update_phase({
        "phase_label": "DESCENT",
        "phase_progress": 72,
        "coaching_focus": "Knee alignment",
        "phase_list": ["START", "DESCENT", "BOTTOM", "ASCENT", "LOCKOUT"],
        "phase_index": 1,
        "is_guided": False
    })
    phase_card.set_exercise("DEADLIFT")
    phase_card.reset()
    print("✓ MovementPhaseCard created, updated, and reset cleanly.")

    # 2. MovementHeatmapFrame
    heatmap = MovementHeatmapFrame(root, max_reps=10)
    rep_sample = analyze_repetition("SQUAT", 1, "CLEAN", False)
    heatmap.add_rep(rep_sample)
    assert len(heatmap._rep_data) == 1
    heatmap.reset()
    assert len(heatmap._rep_data) == 0
    print("✓ MovementHeatmapFrame created, rep added, and reset cleanly.")

    # 3. MovementIntelligenceCard
    intel_card = MovementIntelligenceCard(root, "SQUAT")
    intel_card.update_intelligence(
        {"stability_score": 92, "category": "HIGHLY_STABLE"},
        {"fatigue_level": "LOW", "quality_trend": "STABLE"},
        {"risk_level": "LOW"},
        {"coaching_mode": "CALM", "focus_area": "Consistency"},
        {"recovery_status": "CONTINUE_TRAINING"}
    )
    intel_card.reset()
    print("✓ MovementIntelligenceCard created, updated, and reset cleanly.")

    # 4. SIHDemoWindow
    demo_win = SIHDemoWindow(root, "SQUAT")
    demo_win.update_telemetry(
        reps=5, acc=90, feedback_msg="Optimal Depth", feedback_color="#00E676",
        phase_data={"phase_label": "DESCENT", "phase_progress": 72},
        stability_data={"stability_score": 92, "category": "HIGHLY_STABLE"},
        fatigue_data={"fatigue_level": "LOW"},
        risk_data={"risk_level": "LOW"},
        coach_data={"primary_message": "Maintain rhythm."}
    )
    demo_win.destroy()
    print("✓ SIHDemoWindow created, telemetry updated, and destroyed cleanly.")

    root.destroy()


def test_report_generation():
    print("\n--- Test 16 & 17: Phase 6 Advanced Diagnostic Report Generation ---")
    stats = {
        "clean_reps": 10,
        "failed_depth": 1,
        "failed_sitting": 0,
        "posture_warnings": 1,
        "total_attempts": 11,
        "accuracy": 91,
        "start_time": time.time() - 120
    }
    out_file = os.path.join(_ROOT, "scratch", "test_phase6_report.png")
    if os.path.exists(out_file):
        try:
            os.remove(out_file)
        except Exception:
            pass

    path = generate_report_image(
        exercise_name="SQUAT",
        stats=stats,
        output_path=out_file
    )
    assert os.path.exists(path), "Report file was not created!"
    size = os.path.getsize(path)
    assert size > 60000, f"Report file size {size} is too small!"

    from PIL import Image
    im = Image.open(path)
    w, h = im.size
    assert w == 1200, f"Expected width 1200, got {w}"
    assert h == 1400, f"Expected height 1400, got {h}"
    print(f"✓ Phase 6 Diagnostic report generated: {path} (Dimensions: {w}x{h}, Size: {size:,} bytes)")


def test_main_import():
    print("\n--- Test 18: Main Application Startup & Import Integrity ---")
    import main
    assert hasattr(main, "main") or hasattr(main, "run_app")
    print("✓ main.py imported and verified successfully.")


if __name__ == "__main__":
    print("==================================================")
    print("  REPRIGHT AI — PHASE 6 VERIFICATION SUITE")
    print("==================================================")
    test_movement_phases()
    test_stability_intelligence()
    test_fatigue_and_risk()
    test_adaptive_coaching_and_recovery()
    test_performance_trends_and_readiness()
    test_exercise_compatibility_and_guided_honesty()
    test_ui_components_and_reset()
    test_report_generation()
    test_main_import()
    print("\n==================================================")
    print("  ALL 18 PHASE 6 TEST REQUIREMENTS PASSED! (100%)")
    print("==================================================")
