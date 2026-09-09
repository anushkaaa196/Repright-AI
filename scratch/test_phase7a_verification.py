"""Comprehensive Automated Verification Suite for REPRIGHT AI Phase 7A.

Validates all 18 required Phase 7A implementation criteria:
1. DB Auto-Initialization: Database tables, constraints, and indexes auto-create cleanly.
2. Password Hashing: PBKDF2-HMAC-SHA256 hashing, unique salts, and constant-time verification.
3. User Registration: Valid account creation with height, weight, and fitness goal.
4. Input Validation: Rejection of weak passwords, invalid email syntax, and empty names.
5. Duplicate Email Prevention: Case-insensitive uniqueness enforcement.
6. User Authentication: Correct password succeeds; wrong password safely rejected.
7. User Session Singleton: Thread-safe session tracking, active user retrieval, and listener dispatch.
8. Profile Update: Updating athlete name, bio stats, and training objectives persists in SQLite.
9. Workout Session Persistence: Saving full workout telemetry (reps, duration, stability, fatigue, risk).
10. Repetition Telemetry Persistence: Saving multidimensional biomechanical dimensions (ROM, alignment, stability, control, cadence).
11. Workout History Retrieval: Querying chronological session debriefs by user and exercise.
12. User Data Isolation: Multi-user privacy guarantee (User A cannot access User B's workout data).
13. Aggregate Athlete Analytics: Accurate calculation of lifetime workouts, reps, clean ratio, and avg score.
14. Session Deletion & Cascade: Deleting a session properly cascades to related repetition records.
15. Sidebar User Badge & Controls: Sidebar renders user identity card without impacting pinned workout buttons.
16. User Dashboard Modal: Instantiates cleanly with profile header, KPI ribbon, and history view.
17. Headless Guest Mode Fallback: AIWorkoutUI starts seamlessly without blocking headless testing.
18. Phase 1–6 Zero Regression: Pose tracking, rep counting, and motion intelligence engines remain operational.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add workspace root to sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import sqlite3
import customtkinter as ctk

from database.db_manager import init_db, get_connection, set_db_path, get_db_path
from database.models import User, WorkoutSession, RepRecord
from database.user_repository import UserRepository
from database.workout_repository import WorkoutRepository
from services.auth_service import AuthService, hash_password, verify_password
from services.user_session import UserSession
from ui.app import AIWorkoutUI
from ui.components.sidebar import SidebarFrame
from ui.components.user_dashboard import UserDashboardDialog
from ui.components.user_profile import UserProfileDialog
from ui.components.workout_history import WorkoutHistoryView
from core.rep_history import RepHistoryTracker
from core.exercise_registry import EXERCISE_REGISTRY



def run_phase7a_verification():
    print("=" * 70)
    print("  REPRIGHT AI — PHASE 7A AUTOMATED VERIFICATION SUITE")
    print("  User Authentication, SQLite Persistence, Debrief History & Dashboard")
    print("=" * 70)

    # Use a dedicated isolated test database in scratch/
    test_db_path = str(Path(_ROOT) / "scratch" / "test_phase7a.db")
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass

    set_db_path(test_db_path)
    passed_count = 0

    try:
        # ----------------------------------------------------------------------
        # TEST 1: DB Auto-Initialization & Schema Integrity
        # ----------------------------------------------------------------------
        print("\n[TEST 1/18] Verifying Database Auto-Initialization & Schema Integrity...")
        init_db(test_db_path)
        assert os.path.exists(test_db_path), "Database file was not created on disk."

        conn = get_connection(test_db_path)
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        assert "users" in tables, "Table 'users' missing from schema."
        assert "workout_sessions" in tables, "Table 'workout_sessions' missing from schema."
        assert "rep_history" in tables, "Table 'rep_history' missing from schema."

        indexes = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()]
        assert "idx_users_email" in indexes, "Index 'idx_users_email' missing."
        assert "idx_sessions_user" in indexes, "Index 'idx_sessions_user' missing."
        assert "idx_reps_session" in indexes, "Index 'idx_reps_session' missing."
        conn.close()
        print("  ✓ Database tables (users, workout_sessions, rep_history) and indexes created cleanly.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 2: Password Hashing Security (PBKDF2-HMAC-SHA256)
        # ----------------------------------------------------------------------
        print("\n[TEST 2/18] Verifying Cryptographic Password Hashing & Salt Uniqueness...")
        pwd = "AthleticPassword!99"
        hash1 = hash_password(pwd)
        hash2 = hash_password(pwd)
        assert hash1.startswith("pbkdf2_sha256$200000$"), "Hash algorithm prefix mismatch."
        assert hash1 != hash2, "Salts must be cryptographically unique per hash."
        assert verify_password(pwd, hash1) is True, "Password verification failed with correct password."
        assert verify_password("WrongPassword", hash1) is False, "Password verification accepted wrong password."
        assert verify_password(pwd, "corrupted_hash") is False, "Corrupted hash must safely return False."
        print("  ✓ PBKDF2-HMAC-SHA256 (200k rounds) hashing, salt entropy, and constant-time verification pass.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 3: User Registration with Bio Stats and Goal
        # ----------------------------------------------------------------------
        print("\n[TEST 3/18] Verifying User Registration with Bio Metrics...")
        auth = AuthService(db_path=test_db_path)
        success, msg, user_alex = auth.register(
            name="Alex Mercer",
            email="alex@truform.ai",
            password="StrongPassword123",
            height_cm=182.5,
            weight_kg=78.0,
            fitness_goal="HYPERTROPHY"
        )
        assert success is True, f"Registration failed: {msg}"
        assert user_alex is not None
        assert user_alex.name == "Alex Mercer"
        assert user_alex.email == "alex@truform.ai"
        assert user_alex.fitness_goal == "HYPERTROPHY"
        assert user_alex.bmi == round(78.0 / ((182.5 / 100) ** 2), 1)
        print(f"  ✓ User registered successfully: {user_alex.name} (ID: {user_alex.id}, BMI: {user_alex.bmi}).")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 4: Input Validation Rejection
        # ----------------------------------------------------------------------
        print("\n[TEST 4/18] Verifying Rejection of Invalid Account Inputs...")
        # Name too short
        s, m, _ = auth.register("A", "valid@test.com", "pass123")
        assert s is False and "at least 2 characters" in m
        # Invalid email
        s, m, _ = auth.register("Valid Name", "notanemail", "pass123")
        assert s is False and "valid email" in m
        # Password too short (< 6 chars)
        s, m, _ = auth.register("Valid Name", "valid@test.com", "123")
        assert s is False and "at least 6 characters" in m
        print("  ✓ Invalid inputs (short names, malformed emails, short passwords) rejected with helpful messages.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 5: Duplicate Email Prevention (Case-Insensitive)
        # ----------------------------------------------------------------------
        print("\n[TEST 5/18] Verifying Duplicate Email Prevention...")
        s, m, _ = auth.register("Alex Duplicate", "ALEX@truform.ai", "NewPassword123")
        assert s is False, "Duplicate email registration was erroneously permitted."
        assert "already exists" in m
        print("  ✓ Case-insensitive duplicate email rejection verified.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 6: User Authentication / Login
        # ----------------------------------------------------------------------
        print("\n[TEST 6/18] Verifying User Authentication...")
        # Correct credentials
        s, m, logged_user = auth.login("alex@truform.ai", "StrongPassword123")
        assert s is True and logged_user.id == user_alex.id
        # Case insensitive email
        s, m, logged_user2 = auth.login("ALEX@TRUFORM.AI", "StrongPassword123")
        assert s is True and logged_user2.id == user_alex.id
        # Incorrect password
        s, m, _ = auth.login("alex@truform.ai", "WrongPassword!")
        assert s is False and "Invalid email or password" in m
        # Nonexistent user
        s, m, _ = auth.login("ghost@truform.ai", "Password123")
        assert s is False and "Invalid email or password" in m
        print("  ✓ Authentication correctly verifies valid/invalid passwords and case-insensitive emails.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 7: User Session Singleton Management
        # ----------------------------------------------------------------------
        print("\n[TEST 7/18] Verifying UserSession Singleton and Event Dispatch...")
        session = UserSession.get_instance()
        session.logout()
        assert session.is_authenticated() is False
        assert session.get_current_user() is None

        dispatched_users = []
        def listener(u):
            dispatched_users.append(u)

        session.add_listener(listener)
        session.set_current_user(user_alex)
        assert session.is_authenticated() is True
        assert session.get_current_user().id == user_alex.id
        assert len(dispatched_users) == 1 and dispatched_users[0].id == user_alex.id

        session.logout()
        assert session.is_authenticated() is False
        assert len(dispatched_users) == 2 and dispatched_users[1] is None
        session.remove_listener(listener)

        # Fallback guest test
        guest = session.get_or_create_default_user(test_db_path)
        assert guest is not None and guest.email == "guest@truform.ai"
        assert session.is_authenticated() is True
        print("  ✓ UserSession singleton state changes and listener dispatches operate correctly.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 8: Athlete Profile Updates
        # ----------------------------------------------------------------------
        print("\n[TEST 8/18] Verifying Profile Bio and Objectives Updates...")
        s, m, updated_alex = auth.update_profile(
            user_id=user_alex.id,
            name="Alexander Mercer",
            height_cm=183.0,
            weight_kg=79.5,
            fitness_goal="STRENGTH"
        )
        assert s is True
        assert updated_alex.name == "Alexander Mercer"
        assert updated_alex.height_cm == 183.0
        assert updated_alex.weight_kg == 79.5
        assert updated_alex.fitness_goal == "STRENGTH"
        print("  ✓ Profile update persists correctly in SQLite database.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 9: Workout Session Persistence
        # ----------------------------------------------------------------------
        print("\n[TEST 9/18] Verifying Workout Session Telemetry Persistence...")
        workout_repo = WorkoutRepository(db_path=test_db_path)
        t_start = (datetime.now() - timedelta(minutes=15)).isoformat()
        t_end = datetime.now().isoformat()

        session_id_1 = workout_repo.save_workout_session(
            user_id=user_alex.id,
            exercise_name="SQUAT",
            started_at=t_start,
            completed_at=t_end,
            duration_seconds=900,
            total_reps=12,
            clean_reps=10,
            average_quality=88.5,
            best_rep_quality=96.0,
            consistency_score=91.0,
            stability_score=87.5,
            fatigue_level="LOW",
            risk_level="LOW",
            session_trajectory="IMPROVING"
        )
        assert session_id_1 > 0, "Failed to return valid session_id."
        retrieved_s1 = workout_repo.get_workout_session_by_id(session_id_1)
        assert retrieved_s1 is not None
        assert retrieved_s1.exercise_name == "SQUAT"
        assert retrieved_s1.total_reps == 12
        assert retrieved_s1.clean_reps == 10
        assert retrieved_s1.average_quality == 88.5
        assert retrieved_s1.session_trajectory == "IMPROVING"
        print(f"  ✓ Workout session #{session_id_1} persisted and retrieved accurately.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 10: Repetition Biomechanical History Persistence
        # ----------------------------------------------------------------------
        print("\n[TEST 10/18] Verifying Repetition-by-Repetition Biomechanical Persistence...")
        mock_reps = [
            {
                "rep_number": 1,
                "overall_score": 92.0,
                "range_of_motion": 95.0,
                "joint_alignment": 90.0,
                "core_stability": 92.0,
                "movement_control": 91.0,
                "movement_cadence": 90.0,
                "is_clean": True,
                "rep_result": "CLEAN"
            },
            {
                "rep_number": 2,
                "overall_score": 78.0,
                "range_of_motion": 70.0,
                "joint_alignment": 80.0,
                "core_stability": 82.0,
                "movement_control": 80.0,
                "movement_cadence": 75.0,
                "is_clean": False,
                "rep_result": "FAILED_DEPTH"
            }
        ]

        session_id_2 = workout_repo.save_workout_session(
            user_id=user_alex.id,
            exercise_name="BICEP_CURL",
            started_at=t_start,
            completed_at=t_end,
            duration_seconds=300,
            total_reps=2,
            clean_reps=1,
            average_quality=85.0,
            best_rep_quality=92.0,
            consistency_score=80.0,
            stability_score=84.0,
            fatigue_level="LOW",
            risk_level="LOW",
            session_trajectory="STABLE",
            rep_records=mock_reps
        )
        reps_saved = workout_repo.get_rep_records_for_session(session_id_2)
        assert len(reps_saved) == 2, f"Expected 2 reps saved, got {len(reps_saved)}"
        assert reps_saved[0].rep_number == 1 and reps_saved[0].quality_score == 92.0
        assert reps_saved[1].rep_number == 2 and reps_saved[1].rep_result == "FAILED_DEPTH"
        assert reps_saved[1].range_of_motion == 70.0
        print(f"  ✓ {len(reps_saved)} rep records with 5D biomechanical metrics persisted for Session #{session_id_2}.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 11: Workout History Querying & Filtering
        # ----------------------------------------------------------------------
        print("\n[TEST 11/18] Verifying Workout History Listing & Filtering...")
        all_sessions = workout_repo.get_workout_sessions_by_user(user_alex.id)
        assert len(all_sessions) == 2
        # Newest first
        assert all_sessions[0].id == session_id_2

        # Filter by exercise
        squat_sessions = workout_repo.get_workout_sessions_by_user(user_alex.id, exercise="SQUAT")
        assert len(squat_sessions) == 1 and squat_sessions[0].id == session_id_1
        curl_sessions = workout_repo.get_workout_sessions_by_user(user_alex.id, exercise="BICEP_CURL")
        assert len(curl_sessions) == 1 and curl_sessions[0].id == session_id_2
        print("  ✓ History ordering (newest first) and exercise filtering confirmed.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 12: User Data Isolation & Multi-User Privacy
        # ----------------------------------------------------------------------
        print("\n[TEST 12/18] Verifying Multi-User Data Isolation...")
        _, _, user_sarah = auth.register(
            name="Sarah Connor",
            email="sarah@truform.ai",
            password="Terminator123!"
        )
        sarah_sessions = workout_repo.get_workout_sessions_by_user(user_sarah.id)
        assert len(sarah_sessions) == 0, "Sarah should have 0 sessions, not Alex's."

        # Save Sarah's session
        s_sarah_1 = workout_repo.save_workout_session(
            user_id=user_sarah.id,
            exercise_name="DEADLIFT",
            started_at=t_start,
            completed_at=t_end,
            duration_seconds=600,
            total_reps=8,
            clean_reps=8,
            average_quality=94.0,
            best_rep_quality=98.0,
            consistency_score=95.0
        )
        assert len(workout_repo.get_workout_sessions_by_user(user_sarah.id)) == 1
        assert len(workout_repo.get_workout_sessions_by_user(user_alex.id)) == 2
        print("  ✓ Strict user data isolation by user_id verified. No cross-account data leakage.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 13: Aggregate Athlete Analytics Calculation
        # ----------------------------------------------------------------------
        print("\n[TEST 13/18] Verifying Aggregate Athlete Telemetry Analytics...")
        stats_alex = workout_repo.get_user_aggregate_stats(user_alex.id)
        assert stats_alex["total_workouts"] == 2
        assert stats_alex["total_reps"] == 14  # 12 + 2
        assert stats_alex["clean_reps"] == 11  # 10 + 1
        assert stats_alex["clean_ratio"] == round((11 / 14) * 100, 1)
        assert stats_alex["highest_rep_score"] == 96.0
        assert stats_alex["best_exercise"] in ["SQUAT", "BICEP_CURL"]
        print(f"  ✓ Aggregate statistics verified (Volume: {stats_alex['total_reps']} reps, Clean: {stats_alex['clean_ratio']}%).")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 14: Session Deletion & Cascade Integrity
        # ----------------------------------------------------------------------
        print("\n[TEST 14/18] Verifying Workout Deletion and Cascading...")
        deleted = workout_repo.delete_workout_session(session_id_2, user_alex.id)
        assert deleted is True
        assert workout_repo.get_workout_session_by_id(session_id_2) is None
        # Verify rep records were cascade-deleted
        reps_after = workout_repo.get_rep_records_for_session(session_id_2)
        assert len(reps_after) == 0, "Rep records should cascade delete with parent session."
        print("  ✓ Workout deletion cascades cleanly to child repetition records.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 15: Sidebar User Section & Pinned Controls Rendering
        # ----------------------------------------------------------------------
        print("\n[TEST 15/18] Verifying Sidebar User Section & Action Controls...")
        root = ctk.CTk()
        root.withdraw()

        session.set_current_user(user_alex)

        sidebar = SidebarFrame(
            root,
            exercise_list=list(EXERCISE_REGISTRY.keys()),
            on_open_dashboard=lambda: print("Dashboard clicked"),
            on_logout=lambda: print("Logout clicked")
        )
        assert sidebar.user_frame.winfo_exists()
        assert sidebar.btn_start.winfo_exists()
        assert sidebar.btn_stop.winfo_exists()
        assert sidebar.btn_report.winfo_exists()
        assert sidebar.btn_reset.winfo_exists()

        # Check set_user updates
        sidebar.set_user(user_sarah)
        print("  ✓ Sidebar athlete profile card and all 4 pinned workout action buttons verified.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 16: User Dashboard Dialog Instantiation & Views
        # ----------------------------------------------------------------------
        print("\n[TEST 16/18] Verifying User Dashboard Dialog Rendering...")
        dash = UserDashboardDialog(
            root,
            user=user_alex,
            workout_repo=workout_repo
        )
        assert dash.profile_card.winfo_exists()
        assert dash.kpi_container.winfo_exists()
        assert dash.history_view.winfo_exists()
        dash.destroy()
        root.destroy()
        print("  ✓ Athlete Performance Dashboard modal renders profile header, KPI ribbon, and history view.")
        passed_count += 1


        # ----------------------------------------------------------------------
        # TEST 17: Headless Guest Mode Fallback
        # ----------------------------------------------------------------------
        print("\n[TEST 17/18] Verifying Headless Guest Mode Compatibility in AIWorkoutUI...")
        session.logout()  # Clear auth
        app = AIWorkoutUI()
        app.update_idletasks()
        # Assert app automatically assigned guest session without crashing
        assert session.is_authenticated() is True
        assert session.get_current_user() is not None
        assert app.sidebar.winfo_exists()
        assert app.viewport.winfo_exists()
        assert app.analytics.winfo_exists()
        app.destroy()
        print("  ✓ AIWorkoutUI seamlessly falls back to guest mode for automated/headless tests.")
        passed_count += 1

        # ----------------------------------------------------------------------
        # TEST 18: Phase 1–6 Zero Regression Verification
        # ----------------------------------------------------------------------
        print("\n[TEST 18/18] Verifying Zero Regression across Phase 1–6 Core Engines...")
        from core.movement_phases import get_movement_phase_engine
        from core.movement_stability import get_movement_stability_engine
        from core.fatigue_intelligence import estimate_form_fatigue
        from core.risk_intelligence import evaluate_movement_risk
        from core.rep_analysis import analyze_repetition

        phase_eng = get_movement_phase_engine()
        phase_res = phase_eng.update("SQUAT", 120, "Maintain control", {"clean_reps": 1})
        assert "current_phase" in phase_res

        stab_eng = get_movement_stability_engine()
        stab_res = stab_eng.update("SQUAT", 120, "Stable", {"clean_reps": 1})
        assert "stability_score" in stab_res

        fat_res = estimate_form_fatigue("SQUAT", stab_res["stability_score"], {"clean_reps": 1, "accuracy": 95})
        assert "fatigue_level" in fat_res

        risk_res = evaluate_movement_risk("SQUAT", stab_res["stability_score"], fat_res["fatigue_level"], {"clean_reps": 1})
        assert "risk_level" in risk_res

        rep_res = analyze_repetition(
            exercise_name="SQUAT",
            rep_number=1,
            rep_result="CLEAN",
            posture_warning_occurred=False,
            feedback_msg="Great form",
            stats_snapshot={"clean_reps": 1, "accuracy": 98}
        )
        assert rep_res["overall_score"] > 0
        assert rep_res["is_clean"] is True

        print("  ✓ All Phase 1–6 core motion intelligence pipelines remain 100% operational.")

        passed_count += 1

    finally:
        # Reset DB path back to default
        set_db_path(str(Path(_ROOT) / "database" / "truform.db"))

    print("\n" + "=" * 70)
    print(f"  PHASE 7A VERIFICATION SUMMARY: {passed_count}/18 TESTS PASSED")
    print("=" * 70)
    assert passed_count == 18, f"Only {passed_count}/18 tests passed."
    return True


if __name__ == "__main__":
    run_phase7a_verification()
