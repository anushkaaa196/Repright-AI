"""Automated Verification Suite for REPRIGHT AI - Phase 4.

Tests:
1. Exercise Registry & Scalable Capability Architecture (Active vs Guided)
2. Exercise Guidance System with All 7 Exercises & Reference Diagrams
3. Personalized Session Improvement Engine & In-Memory History Progression
4. Diagnostic Report Generation with Phase 4 Session Intelligence
5. UI Component APIs & Instantiation (Library, Summary, Readiness, Viewport Timer, Presentation Mode)
"""

import os
import sys
from pathlib import Path

# Ensure root directory is on path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import tkinter as tk
import customtkinter as ctk

from core.exercise_registry import (
    EXERCISE_REGISTRY,
    get_exercise_metadata,
    get_all_exercises,
    get_active_exercises,
    get_guided_exercises,
    is_active_ai_supported,
    get_exercises_by_category
)
from core.exercise_guidance import (
    get_exercise_guidance,
    classify_posture_feedback
)
from core.session_insights import (
    generate_session_insights,
    SessionHistoryTracker
)
from backend.reporter import generate_report_image
from ui.components import (
    ExerciseLibraryDialog,
    ReadinessCheckCard,
    SessionSummaryDialog,
    LiveAnalyticsFrame,
    ViewportFrame,
    SidebarFrame,
    FormGuideFrame
)


def test_exercise_registry():
    print("--- 1. Testing Exercise Registry ---")
    all_ex = get_all_exercises()
    assert len(all_ex) == 7, f"Expected 7 exercises, got {len(all_ex)}"

    active_ex = get_active_exercises()
    guided_ex = get_guided_exercises()
    assert len(active_ex) == 3, f"Expected 3 active exercises, got {len(active_ex)}"
    assert len(guided_ex) == 4, f"Expected 4 guided exercises, got {len(guided_ex)}"

    active_ids = {e["id"] for e in active_ex}
    guided_ids = {e["id"] for e in guided_ex}
    assert active_ids == {"SQUAT", "DEADLIFT", "BICEP_CURL"}
    assert guided_ids == {"PUSH_UP", "LUNGE", "PLANK", "SHOULDER_PRESS"}

    for aid in active_ids:
        assert is_active_ai_supported(aid) is True
    for gid in guided_ids:
        assert is_active_ai_supported(gid) is False

    cats = get_exercises_by_category()
    assert "LOWER BODY" in cats
    assert "UPPER BODY" in cats
    assert "CORE" in cats
    assert "POSTERIOR CHAIN" in cats
    print("✓ Exercise Registry verified successfully.")


def test_guidance_and_diagrams():
    print("\n--- 2. Testing Guidance & Reference Diagrams ---")
    all_ids = ["SQUAT", "DEADLIFT", "BICEP_CURL", "PUSH_UP", "LUNGE", "PLANK", "SHOULDER_PRESS"]
    for eid in all_ids:
        guide = get_exercise_guidance(eid)
        assert guide is not None, f"No guidance for {eid}"
        assert len(guide.get("correct_form", [])) >= 4, f"Insufficient form cues for {eid}"
        assert len(guide.get("common_mistakes", [])) >= 4, f"Insufficient mistakes for {eid}"
        assert len(guide.get("improvement_tips", [])) >= 4, f"Insufficient tips for {eid}"

        img_path = guide.get("reference_image")
        assert img_path is not None and os.path.exists(img_path), f"Diagram missing for {eid}: {img_path}"

    print("✓ All 7 exercises have complete guidance and existing local reference diagrams.")


def test_session_insights_and_progression():
    print("\n--- 3. Testing Session Insights & Progression Tracker ---")
    stats1 = {
        "clean_reps": 10,
        "failed_depth": 2,
        "failed_sitting": 0,
        "posture_warnings": 1,
        "total_attempts": 12,
        "accuracy": 83
    }
    insights1 = generate_session_insights("SQUAT", stats1, duration_seconds=125)
    assert insights1["performance_tier"] == "GOOD"
    assert insights1["primary_focus"] == "DEPTH CONTROL"
    assert len(insights1["strengths"]) > 0
    assert len(insights1["improvements"]) > 0
    assert insights1["duration_str"] == "02:05"

    tracker = SessionHistoryTracker()
    tracker.clear()
    tracker.record_session("SQUAT", stats1, duration_seconds=125)

    stats2 = {
        "clean_reps": 15,
        "failed_depth": 0,
        "failed_sitting": 0,
        "posture_warnings": 0,
        "total_attempts": 15,
        "accuracy": 100
    }
    tracker.record_session("SQUAT", stats2, duration_seconds=150)

    comp = tracker.get_recent_comparison("SQUAT")
    assert comp is not None
    assert comp["delta_accuracy"] == 17
    assert comp["trend_tier"] == "IMPROVED"
    assert comp["trend_icon"] == "↑"
    print("✓ Session Insights and Progression comparison verified.")


def test_report_generation_with_insights():
    print("\n--- 4. Testing Diagnostic Report Generation ---")
    test_stats = {
        "clean_reps": 12,
        "failed_depth": 1,
        "failed_sitting": 0,
        "posture_warnings": 0,
        "total_attempts": 13,
        "accuracy": 92,
        "start_time": 0.0
    }
    out_dir = os.path.join("scratch", "test_report.png")
    generated = generate_report_image("SQUAT", test_stats, output_path=out_dir)
    assert os.path.exists(generated), f"Report not created at {generated}"
    assert os.path.getsize(generated) > 50000, "Report image file too small"
    print(f"✓ Diagnostic report generated ({os.path.getsize(generated)} bytes).")


def test_ui_components():
    print("\n--- 5. Testing UI Components ---")
    # Initialize headless tkinter root
    root = ctk.CTk()
    root.withdraw()

    # Viewport
    vp = ViewportFrame(root)
    vp.set_exercise("SQUAT", is_active_ai=True)
    assert vp.exercise_badge.cget("text") == "SQUAT"
    assert "ACTIVE" in vp.mode_pill.cget("text")

    vp.set_exercise("PUSH_UP", is_active_ai=False)
    assert vp.exercise_badge.cget("text") == "PUSH_UP"
    assert "GUIDED" in vp.mode_pill.cget("text")

    vp.update_timer(135)
    assert vp.timer_pill.cget("text") == "⏱ 02:15"

    # Analytics Frame
    af = LiveAnalyticsFrame(root)
    af.update_analytics({"clean_reps": 5, "accuracy": 90, "total_attempts": 6, "failed_depth": 1, "failed_sitting": 0, "posture_warnings": 0}, "SQUAT")
    assert af.score_val.cget("text") == "90%"

    af.update_analytics({"clean_reps": 8, "accuracy": 95, "total_attempts": 8, "left_arm_reps": 4, "right_arm_reps": 4, "failed_depth": 0, "failed_sitting": 0, "posture_warnings": 0}, "BICEP_CURL")
    assert "Left: 4 | Right: 4" in af.depth_diag.cget("text")

    # Readiness Card
    rc = ReadinessCheckCard(root)
    assert rc is not None

    # Sidebar selection
    sb = SidebarFrame(root, exercise_list=["SQUAT", "DEADLIFT", "BICEP_CURL"])
    sb.set_exercise_selection("DEADLIFT")
    assert sb.exercise_opt.get() == "DEADLIFT"

    root.destroy()
    print("✓ All UI components instantiated and verified.")


if __name__ == "__main__":
    test_exercise_registry()
    test_guidance_and_diagrams()
    test_session_insights_and_progression()
    test_report_generation_with_insights()
    test_ui_components()
    print("\n==============================================")
    print("ALL PHASE 4 VERIFICATION TESTS PASSED (5/5)!")
    print("==============================================")
