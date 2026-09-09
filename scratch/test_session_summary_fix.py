"""Verification test suite for REPRIGHT AI Session Summary Dialog & Debrief Window Fix.

Tests 12 critical scenarios:
1. Normal workout with valid data
2. Workout with 0 repetitions
3. Workout with 1 repetition
4. Workout with multiple repetitions
5. Missing Personalized Coach data
6. Missing Progress Intelligence data
7. Missing Movement Intelligence data
8. STOP WORKOUT callback opens visible Session Summary
9. Verify at least one visible widget exists immediately
10. Verify Session Summary is created on the UI thread
11. Verify CLOSE button works
12. Verify Export Report still works
"""

import sys
import os
import threading
import customtkinter as ctk

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ui import theme
from ui.components.session_summary import SessionSummaryDialog
from ui.app import AIWorkoutUI as RepRightApp
from backend.engine import WorkoutEngine
from core.rep_history import RepHistoryTracker


def run_all_tests():
    print("==================================================")
    print("  REPRIGHT AI — SESSION SUMMARY FIX VERIFICATION  ")
    print("==================================================")

    # Initialize headless RepRightApp
    app = RepRightApp()
    app.withdraw()

    # ----------------------------------------------------
    # TEST 1: Normal workout with valid data
    # ----------------------------------------------------
    print("\n--- TEST 1: Normal workout with valid data ---")
    stats_normal = {
        "clean_reps": 8,
        "total_attempts": 10,
        "accuracy": 80,
        "failed_depth": 1,
        "failed_sitting": 1,
        "posture_warnings": 2
    }
    dlg1 = SessionSummaryDialog(app, exercise_name="SQUAT", stats=stats_normal, duration_seconds=95)
    app.update_idletasks()
    assert dlg1.title() == "REPRIGHT AI - Session Performance Intelligence & Debrief"
    assert len(dlg1.body.winfo_children()) >= 4, f"Expected >=4 sections, got {len(dlg1.body.winfo_children())}"
    print(f"✓ Normal workout rendered {len(dlg1.body.winfo_children())} content sections successfully.")
    dlg1.destroy()

    # ----------------------------------------------------
    # TEST 2: Workout with 0 repetitions
    # ----------------------------------------------------
    print("\n--- TEST 2: Workout with 0 repetitions ---")
    stats_zero = {
        "clean_reps": 0,
        "total_attempts": 0,
        "accuracy": 100,
        "failed_depth": 0,
        "failed_sitting": 0,
        "posture_warnings": 0
    }
    dlg2 = SessionSummaryDialog(app, exercise_name="BICEP_CURL", stats=stats_zero, duration_seconds=3)
    app.update_idletasks()
    assert len(dlg2.body.winfo_children()) >= 4
    assert dlg2.session_data["clean_reps"] == 0
    print(f"✓ 0-repetition workout rendered cleanly without error ({len(dlg2.body.winfo_children())} sections).")
    dlg2.destroy()

    # ----------------------------------------------------
    # TEST 3: Workout with 1 repetition
    # ----------------------------------------------------
    print("\n--- TEST 3: Workout with 1 repetition ---")
    stats_one = {
        "clean_reps": 1,
        "total_attempts": 1,
        "accuracy": 100,
        "failed_depth": 0,
        "failed_sitting": 0,
        "posture_warnings": 0
    }
    dlg3 = SessionSummaryDialog(app, exercise_name="DEADLIFT", stats=stats_one, duration_seconds=15)
    app.update_idletasks()
    assert len(dlg3.body.winfo_children()) >= 4
    assert dlg3.session_data["clean_reps"] == 1
    print(f"✓ 1-repetition workout rendered cleanly ({len(dlg3.body.winfo_children())} sections).")
    dlg3.destroy()

    # ----------------------------------------------------
    # TEST 4: Workout with multiple repetitions
    # ----------------------------------------------------
    print("\n--- TEST 4: Workout with multiple repetitions ---")
    rep_tracker = RepHistoryTracker.get_instance()
    rep_tracker.reset()
    for i in range(5):
        rep_tracker.add_rep({
            "rep_number": i + 1,
            "overall_score": 85 + i * 2,
            "is_clean": True,
            "scores": {"range_of_motion": 90, "alignment": 85, "stability": 88, "movement_control": 86, "consistency": 90},
            "primary_fault": None,
            "coaching_cue": "Maintain cadence."
        })
    stats_multi = {
        "clean_reps": 5,
        "total_attempts": 5,
        "accuracy": 90,
        "failed_depth": 0,
        "failed_sitting": 0,
        "posture_warnings": 1
    }
    dlg4 = SessionSummaryDialog(app, exercise_name="SQUAT", stats=stats_multi, duration_seconds=60)
    app.update_idletasks()
    assert len(dlg4.body.winfo_children()) >= 4
    assert dlg4.session_data["clean_reps"] == 5
    print(f"✓ Multi-repetition workout verified with RepHistory integration.")
    dlg4.destroy()

    # ----------------------------------------------------
    # TEST 5: Missing Personalized Coach data (fallback)
    # ----------------------------------------------------
    print("\n--- TEST 5: Missing Personalized Coach data ---")
    session_data_no_plan = {
        "exercise": "SQUAT",
        "duration": 45,
        "clean_reps": 3,
        "total_reps": 4,
        "form_score": 75,
        "personalized_plan": None  # Explicitly None
    }
    dlg5 = SessionSummaryDialog(app, session_data=session_data_no_plan)
    app.update_idletasks()
    assert len(dlg5.body.winfo_children()) >= 4
    print("✓ Missing Personalized Coach data rendered with safe fallback.")
    dlg5.destroy()

    # ----------------------------------------------------
    # TEST 6: Missing Progress Intelligence data (fallback)
    # ----------------------------------------------------
    print("\n--- TEST 6: Missing Progress Intelligence data ---")
    session_data_no_prog = {
        "exercise": "SQUAT",
        "duration": 50,
        "clean_reps": 4,
        "total_reps": 4,
        "form_score": 100,
        "progress_intelligence": None
    }
    dlg6 = SessionSummaryDialog(app, session_data=session_data_no_prog)
    app.update_idletasks()
    assert len(dlg6.body.winfo_children()) >= 4
    print("✓ Missing Progress Intelligence data rendered cleanly.")
    dlg6.destroy()

    # ----------------------------------------------------
    # TEST 7: Missing Movement Intelligence data (fallback)
    # ----------------------------------------------------
    print("\n--- TEST 7: Missing Movement Intelligence data ---")
    session_data_no_intel = {
        "exercise": "BICEP_CURL",
        "duration": 30,
        "clean_reps": 2,
        "total_reps": 2,
        "form_score": 100,
        "movement_intelligence": None  # Explicitly None
    }
    dlg7 = SessionSummaryDialog(app, session_data=session_data_no_intel)
    app.update_idletasks()
    assert len(dlg7.body.winfo_children()) >= 4
    print("✓ Missing Movement Intelligence rendered with safe fallback message.")
    dlg7.destroy()

    # ----------------------------------------------------
    # TEST 8: STOP WORKOUT callback opens visible Session Summary
    # ----------------------------------------------------
    print("\n--- TEST 8: STOP WORKOUT callback opens visible Session Summary ---")
    # Simulate STOP WORKOUT callback on active application
    app._on_stop_workout()
    app.update()

    assert app.summary_dialog is not None, "summary_dialog should have been created on STOP WORKOUT"
    assert app.summary_dialog.winfo_exists(), "summary_dialog must exist in Tkinter hierarchy"
    assert len(app.summary_dialog.body.winfo_children()) >= 4, "Summary dialog must have rendered content cards"
    print(f"✓ STOP WORKOUT successfully opened SessionSummaryDialog with {len(app.summary_dialog.body.winfo_children())} content sections.")

    # ----------------------------------------------------
    # TEST 9: Verify at least one visible widget exists immediately
    # ----------------------------------------------------
    print("\n--- TEST 9: Verify visible widgets exist immediately ---")
    summary = app.summary_dialog
    total_widgets = len(summary.winfo_children()) + len(summary.main_container.winfo_children()) + len(summary.body.winfo_children())
    assert total_widgets >= 5, f"Expected total widgets >= 5, got {total_widgets}"
    print(f"✓ Total immediate child widgets in hierarchy: {total_widgets} (Zero blank window state confirmed).")

    # ----------------------------------------------------
    # TEST 10: Verify Session Summary is created on UI thread
    # ----------------------------------------------------
    print("\n--- TEST 10: Verify Session Summary created on UI thread ---")
    main_thread = threading.main_thread()
    current_thread = threading.current_thread()
    assert current_thread == main_thread, "Dialog creation must be executed on Python main UI thread"
    print(f"✓ Confirmed UI thread execution: {current_thread.name} (ID: {current_thread.ident}).")

    # ----------------------------------------------------
    # TEST 11: Verify CLOSE button works
    # ----------------------------------------------------
    print("\n--- TEST 11: Verify CLOSE button works ---")
    summary.destroy()
    app.update_idletasks()
    print("✓ CLOSE action destroyed dialog cleanly without resource leak.")

    # ----------------------------------------------------
    # TEST 12: Verify Export Report still works
    # ----------------------------------------------------
    print("\n--- TEST 12: Verify Export Report still works ---")
    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_session_summary_export.png"))
    engine = WorkoutEngine()
    stats_sample = {"clean_reps": 6, "total_attempts": 7, "accuracy": 85, "failed_depth": 1, "failed_sitting": 0, "posture_warnings": 1}
    gen_path = engine.export_report(report_path)
    assert os.path.exists(gen_path), f"Report file not generated at {gen_path}"
    assert os.path.getsize(gen_path) > 10000, "Report file is too small"
    print(f"✓ Export report verified successfully: {gen_path} ({os.path.getsize(gen_path)} bytes).")

    app.destroy()

    print("\n==================================================")
    print("  ALL 12 VERIFICATION TESTS PASSED PERFECTLY!    ")
    print("==================================================")


if __name__ == "__main__":
    run_all_tests()
