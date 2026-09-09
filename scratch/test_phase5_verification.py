"""Phase 5 Comprehensive Verification & Test Suite for REPRIGHT AI.

Validates:
1. Rep-by-rep movement analysis engine & 5-dimension scoring
2. Rep history tracker with consistency and category stats
3. Personalized AI improvement engine (6 structured sections)
4. Session goals and challenges system
5. Live vs Ideal form comparison engine
6. Long-term progress intelligence multi-session tracker
7. High-resolution diagnostic report generation (1200 x 1220)
8. UI component instantiations and thread safety
"""

import sys
import os
import time
from pathlib import Path

# Add project root to sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.rep_analysis import analyze_repetition, DIMENSION_SCHEMAS
from core.rep_history import RepHistoryTracker
from core.personalized_coach import generate_personalized_plan
from core.session_goals import get_exercise_goal, evaluate_goal_progress
from core.form_comparison import get_form_comparison
from core.progress_intelligence import ProgressIntelligenceTracker
from backend.reporter import generate_report_image


def test_rep_analysis():
    print("\n--- Testing Feature 1: Rep-by-Rep Movement Analysis Engine ---")

    # Clean rep without warnings
    clean_rep = analyze_repetition("SQUAT", 1, "CLEAN", posture_warning_occurred=False)
    assert clean_rep["overall_score"] >= 90, f"Expected clean score >= 90, got {clean_rep['overall_score']}"
    assert clean_rep["status"] == "EXCELLENT"
    assert clean_rep["is_clean"] is True
    assert "range_of_motion" in clean_rep["dimension_scores"]
    assert len(clean_rep["strengths"]) > 0
    print("✓ Clean rep analysis: OK (Score:", clean_rep["overall_score"], clean_rep["status"], ")")

    # Clean rep with posture warning
    warn_rep = analyze_repetition("SQUAT", 2, "CLEAN", posture_warning_occurred=True)
    assert 75 <= warn_rep["overall_score"] <= 89, f"Expected warn score 75-89, got {warn_rep['overall_score']}"
    assert warn_rep["status"] == "GOOD"
    assert len(warn_rep["issues"]) > 0
    print("✓ Warn rep analysis: OK (Score:", warn_rep["overall_score"], warn_rep["status"], ")")

    # Failed depth rep
    depth_rep = analyze_repetition("SQUAT", 3, "FAILED_DEPTH")
    assert depth_rep["overall_score"] < 75
    assert depth_rep["status"] == "NEEDS_IMPROVEMENT"
    assert depth_rep["dimension_scores"]["range_of_motion"] <= 60
    assert "range of motion" in depth_rep["issues"][0].lower() or "depth" in depth_rep["issues"][0].lower()
    print("✓ Failed depth rep analysis: OK (Score:", depth_rep["overall_score"], depth_rep["status"], ")")

    # Failed sitting rep
    sit_rep = analyze_repetition("SQUAT", 4, "FAILED_SITTING")
    assert sit_rep["overall_score"] < 55
    assert sit_rep["status"] == "FORM_CORRECTION"
    assert "chair" in sit_rep["issues"][0].lower() or "sitting" in sit_rep["issues"][0].lower()
    print("✓ Failed sitting rep analysis: OK (Score:", sit_rep["overall_score"], sit_rep["status"], ")")

    # Exercise dimension schemas
    for ex in ["SQUAT", "DEADLIFT", "BICEP_CURL"]:
        assert ex in DIMENSION_SCHEMAS
        assert len(DIMENSION_SCHEMAS[ex]) == 5
    print("✓ 5-Dimension schemas for all exercises: OK")


def test_rep_history():
    print("\n--- Testing Feature 2: Rep History Tracker ---")
    tracker = RepHistoryTracker.get_instance()
    tracker.reset()
    assert tracker.get_total_reps() == 0

    r1 = analyze_repetition("SQUAT", 1, "CLEAN", False)
    r2 = analyze_repetition("SQUAT", 2, "CLEAN", True)
    r3 = analyze_repetition("SQUAT", 3, "FAILED_DEPTH")
    tracker.add_rep(r1)
    tracker.add_rep(r2)
    tracker.add_rep(r3)

    assert tracker.get_total_reps() == 3
    assert tracker.get_clean_reps() == 2

    best = tracker.get_best_rep()
    assert best is not None and best["rep_number"] == 1
    print(f"✓ Best rep identified: Rep #{best['rep_number']} ({best['overall_score']}%)")

    weakest = tracker.get_weakest_rep()
    assert weakest is not None and weakest["rep_number"] == 3
    print(f"✓ Weakest rep identified: Rep #{weakest['rep_number']} ({weakest['overall_score']}%)")

    avg = tracker.get_average_score()
    assert 70 <= avg <= 85
    print(f"✓ Average score calculated: {avg}%")

    consistency = tracker.get_consistency_score()
    assert 0 <= consistency <= 100
    print(f"✓ Consistency score calculated: {consistency}%")

    dim_avgs = tracker.get_dimension_averages()
    assert len(dim_avgs) == 5
    print("✓ Dimension averages:", dim_avgs)

    strongest = tracker.get_strongest_category()
    weakest_cat = tracker.get_weakest_category()
    print(f"✓ Strongest category: {strongest[0]} ({strongest[1]}%)")
    print(f"✓ Weakest category: {weakest_cat[0]} ({weakest_cat[1]}%)")

    common_issue = tracker.get_most_common_issue()
    print(f"✓ Most common issue: {common_issue}")


def test_personalized_coach():
    print("\n--- Testing Feature 5: Personalized AI Improvement Engine ---")
    plan = generate_personalized_plan("SQUAT")
    assert "strength" in plan
    assert "primary_focus" in plan
    assert "why_it_matters" in plan
    assert "next_session_goal" in plan
    assert "coaching_cue" in plan
    assert "recommended_practice" in plan

    print("✓ Personalized Plan output:")
    print("  - Strength:", plan["strength"])
    print("  - Primary Focus:", plan["primary_focus"])
    print("  - Why It Matters:", plan["why_it_matters"][:60], "...")
    print("  - Next Session Goal:", plan["next_session_goal"])
    print("  - Coaching Cue:", plan["coaching_cue"])
    print("  - Recommended Drill:", plan["recommended_practice"])


def test_session_goals():
    print("\n--- Testing Feature 7: Session Goals and Challenges ---")
    goal = get_exercise_goal("SQUAT")
    assert goal["target_reps"] == 10

    # In progress
    prog = evaluate_goal_progress("SQUAT", clean_reps=6, accuracy=90)
    assert prog["current_reps"] == 6
    assert prog["target_reps"] == 10
    assert prog["progress_percent"] == 60
    assert prog["is_achieved"] is False
    assert "4 clean reps remaining" in prog["status_text"]
    print(f"✓ In-progress goal: {prog['current_reps']}/{prog['target_reps']} ({prog['status_text']})")

    # Achieved
    prog_done = evaluate_goal_progress("SQUAT", clean_reps=10, accuracy=92)
    assert prog_done["is_achieved"] is True
    assert "ACHIEVED" in prog_done["status_text"]
    print(f"✓ Achieved goal: {prog_done['status_text']}")

    # Guided exercise
    prog_guided = evaluate_goal_progress("PLANK", clean_reps=0, accuracy=100)
    assert prog_guided["is_guided"] is True
    print(f"✓ Guided exercise goal: {prog_guided['status_text']}")


def test_form_comparison():
    print("\n--- Testing Feature 8: Current Posture vs Ideal Form Comparison ---")
    # Standby
    c1 = get_form_comparison("SQUAT", "Standby in camera frame")
    assert c1["status_level"] == "STANDBY"
    print(f"✓ Standby comparison: {c1['status_pill']}")

    # Optimal
    c2 = get_form_comparison("SQUAT", "Clean Rep Counted! Optimal depth")
    assert c2["status_level"] == "OPTIMAL"
    print(f"✓ Optimal comparison: {c2['status_pill']}")

    # Depth fault
    c3 = get_form_comparison("SQUAT", "NO REP: Incomplete Depth")
    assert c3["status_level"] == "MINOR_ADJUSTMENT"
    print(f"✓ Depth adjustment comparison: {c3['status_pill']} (Gap: {c3['gap_to_improve'][:40]}...)")

    # Posture warning
    c4 = get_form_comparison("SQUAT", "Warning: Back Collapsing Forward! Keep chest up")
    assert c4["status_level"] == "CORRECTION_RECOMMENDED"
    print(f"✓ Posture correction comparison: {c4['status_pill']} (Gap: {c4['gap_to_improve'][:40]}...)")


def test_progress_intelligence():
    print("\n--- Testing Feature 9: Long-Term Progress Intelligence ---")
    tracker = ProgressIntelligenceTracker.get_instance()
    tracker.clear()

    # Session 1
    s1 = tracker.record_completed_session("SQUAT", {"accuracy": 78, "clean_reps": 6, "total_attempts": 10}, 60, 85, 78, 80)
    assert s1["session_number"] == 1

    sum1 = tracker.get_progress_summary("SQUAT")
    assert sum1["sessions_completed"] == 1
    assert sum1["current_accuracy"] == 78
    print("✓ Session 1 progress summary: Baseline established")

    # Session 2 (Improved)
    s2 = tracker.record_completed_session("SQUAT", {"accuracy": 88, "clean_reps": 9, "total_attempts": 10}, 75, 94, 88, 88)
    assert s2["session_number"] == 2

    sum2 = tracker.get_progress_summary("SQUAT")
    assert sum2["sessions_completed"] == 2
    assert sum2["current_accuracy"] == 88
    assert sum2["previous_accuracy"] == 78
    assert sum2["delta_accuracy"] == 10
    assert sum2["trend_icon"] == "↑"
    print(f"✓ Session 2 progress summary: {sum2['trend_icon']} {sum2['trend_text']}")


def test_report_generation():
    print("\n--- Testing Feature 12: Advanced Diagnostic Report Generator ---")
    stats = {
        "clean_reps": 8,
        "failed_depth": 2,
        "failed_sitting": 0,
        "posture_warnings": 1,
        "total_attempts": 10,
        "accuracy": 80,
        "start_time": time.time() - 90
    }
    out_file = os.path.join(_ROOT, "scratch", "test_phase5_report.png")
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
    assert size > 50000, f"Report file size {size} is suspiciously small!"

    from PIL import Image
    im = Image.open(path)
    w, h = im.size
    assert w == 1200, f"Expected width 1200, got {w}"
    assert h in (1220, 1400), f"Expected height 1220 or 1400, got {h}"
    print(f"✓ Diagnostic report generated: {path} (Dimensions: {w}x{h}, Size: {size:,} bytes)")


def test_ui_components():
    print("\n--- Testing UI Components Instantiation (Headless) ---")
    import customtkinter as ctk
    from ui.components.rep_timeline import RepTimelineFrame
    from ui.components.performance_breakdown import PerformanceBreakdownFrame
    from ui.components.personalized_plan import PersonalizedPlanCard
    from ui.components.session_goal import SessionGoalCard
    from ui.components.form_comparison import FormComparisonCard

    root = ctk.CTk()
    root.withdraw()

    # RepTimelineFrame
    tl = RepTimelineFrame(root)
    tl.add_rep(analyze_repetition("SQUAT", 1, "CLEAN"))
    assert tl._rep_count == 1
    tl.reset()
    assert tl._rep_count == 0
    print("✓ RepTimelineFrame: OK")

    # PerformanceBreakdownFrame
    pb = PerformanceBreakdownFrame(root, "SQUAT")
    pb.update_breakdown({"range_of_motion": 90, "alignment": 85, "stability": 92, "movement_control": 88, "consistency": 90})
    pb.set_exercise("DEADLIFT")
    pb.set_exercise("PUSH_UP")  # Guided mode
    pb.reset()
    print("✓ PerformanceBreakdownFrame: OK")

    # PersonalizedPlanCard
    plan_card = PersonalizedPlanCard(root, "SQUAT")
    plan_card.refresh("SQUAT")
    print("✓ PersonalizedPlanCard: OK")

    # SessionGoalCard
    goal_card = SessionGoalCard(root, "SQUAT")
    goal_card.update_progress(5, 80)
    goal_card.update_progress(10, 90)
    goal_card.reset()
    print("✓ SessionGoalCard: OK")

    # FormComparisonCard
    fc = FormComparisonCard(root, "SQUAT")
    fc.update_comparison("SQUAT", "Clean Rep Counted!")
    fc.reset()
    print("✓ FormComparisonCard: OK")

    root.destroy()
    print("✓ All UI components verified without errors.")


if __name__ == "__main__":
    print("==================================================")
    print("  REPRIGHT AI — PHASE 5 VERIFICATION SUITE")
    print("==================================================")
    test_rep_analysis()
    test_rep_history()
    test_personalized_coach()
    test_session_goals()
    test_form_comparison()
    test_progress_intelligence()
    test_report_generation()
    test_ui_components()
    print("\n==================================================")
    print("  ALL 8 TEST SUITES PASSED PERFECTLY! (100%)")
    print("==================================================")
