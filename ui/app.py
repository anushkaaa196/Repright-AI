import sys
from pathlib import Path

# Ensure root workspace directory is in sys.path
_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import time
import threading
from typing import Dict, Any, Optional
import cv2
import numpy as np
from PIL import Image
import customtkinter as ctk

from config import EXERCISE_CONFIGS, UI_TELEMETRY_THROTTLE_SEC
from backend import WorkoutEngine
from core.exercise_registry import is_active_ai_supported
from core.rep_analysis import analyze_repetition
from core.rep_history import RepHistoryTracker
from core.movement_phases import get_movement_phase_engine
from core.movement_stability import get_movement_stability_engine
from core.fatigue_intelligence import estimate_form_fatigue
from core.risk_intelligence import evaluate_movement_risk
from core.adaptive_coaching import get_adaptive_coaching
from core.recovery_recommendations import get_recovery_recommendations
from core.performance_trends import analyze_performance_trends
from core.gym_locator import warm_gym_locator_cache
from ui import theme

from ui.components import (
    SidebarFrame,
    ViewportFrame,
    FormGuideFrame,
    LiveAnalyticsFrame,
    ExerciseLibraryDialog,
    SessionSummaryDialog,
    PersonalizedPlanDialog,
    ProgressDashboardDialog,
    MovementIntelligenceDialog,
    SIHDemoWindow,
    AnalyticsHubDialog,
    UserDashboardDialog,
    UserProfileDialog,
    NutritionDashboardDialog,
    GymLocatorDialog,
)
from ui.auth import AuthDialog
from database.db_manager import init_db
from database.workout_repository import WorkoutRepository
from services.user_session import UserSession



class AIWorkoutUI(ctk.CTk):
    """Main application controller and graphical user interface.

    Coordinates between CustomTkinter presentation widgets, the Form Guide reference system,
    the Live Performance Analytics dashboard, and the backend WorkoutEngine.
    """

    def __init__(self):
        super().__init__()

        theme.setup_theme()

        self.title("TRUFORM AI - Real-Time Biomechanics & Exercise Form Learning Platform")
        self.geometry("1400x890")
        self.minsize(1140, 720)
        self.configure(fg_color=theme.COLOR_BG_DARK)

        # Configure root layout grid:
        # Col 0: Sidebar (280px fixed)
        # Col 1: Live Viewport (weight 1, expands)
        # Col 2: Form Guide Panel (320px fixed)
        # Row 0: Main Experience Workspace (weight 1)
        # Row 1: Live Performance Analytics Dock (weight 0)
        self.grid_columnconfigure(0, weight=0, minsize=280)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=320)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # Presentation mode and session timer state
        self.is_presentation_mode = False
        self.session_seconds = 0
        self._timer_after_id: Optional[str] = None

        # Phase 5 Rep Tracking state variables
        self._last_clean_reps = 0
        self._last_total_attempts = 0
        self._last_posture_warnings = 0
        self._last_sitting_fails = 0
        self._last_depth_fails = 0
        self._posture_fault_in_active_rep = False

        # Phase 6 Motion Intelligence state
        self.demo_window: Optional[SIHDemoWindow] = None
        self._last_phase_data: Dict[str, Any] = {}
        self._last_stability_data: Dict[str, Any] = {}
        self._last_fatigue_data: Dict[str, Any] = {}
        self._last_risk_data: Dict[str, Any] = {}
        self._last_coach_data: Dict[str, Any] = {}
        self.analytics_hub: Optional[AnalyticsHubDialog] = None

        # Phase 7 User Authentication, Dashboard, Nutrition & Gym Locator
        self.user_dashboard: Optional[UserDashboardDialog] = None
        self.nutrition_dashboard: Optional[NutritionDashboardDialog] = None
        self.auth_dialog: Optional[AuthDialog] = None
        self.gym_dialog: Optional[GymLocatorDialog] = None

        # Performance & Telemetry throttling state (prevents Tkinter GUI backlog)
        self._ui_update_in_progress: bool = False
        self._last_telemetry_time: float = 0.0

        # Pre-warm device location and gym cache asynchronously for 0 ms opening
        threading.Thread(target=warm_gym_locator_cache, daemon=True).start()

        # Initialize SQLite database
        init_db()

        # Ensure an active user session exists (fallback to guest for tests)
        if not UserSession.get_instance().is_authenticated():
            UserSession.get_instance().get_or_create_default_user()

        # Listen for authentication/session changes
        UserSession.get_instance().add_listener(self._on_user_session_changed)

        # Initialize Backend Engine with frame processing callback
        self.engine = WorkoutEngine(on_frame_processed=self._on_frame_processed)

        initial_exercise = list(EXERCISE_CONFIGS.keys())[0] if EXERCISE_CONFIGS else "SQUAT"

        # 1. Left Sidebar
        self.sidebar = SidebarFrame(
            self,
            exercise_list=list(EXERCISE_CONFIGS.keys()),
            on_exercise_selected=self._on_exercise_selected,
            on_toggle_session=self._on_toggle_session,
            on_start_workout=self._on_start_workout,
            on_stop_workout=self._on_stop_workout,
            on_export_report=self._on_export_report,
            on_reset_metrics=self._on_reset_metrics,
            on_explore_library=self._on_explore_library,
            on_open_analytics_hub=self._open_analytics_hub,
            on_view_plan=self._open_personalized_plan_dialog,
            on_view_progress=self._open_progress_dashboard_dialog,
            on_open_dashboard=self._open_user_dashboard,
            on_open_nutrition=self._open_nutrition_dashboard,
            on_logout=self._handle_logout,
            on_find_gyms=self._open_gym_locator_dialog
        )
        self.sidebar.grid(row=0, column=0, padx=(16, 6), pady=(16, 10), sticky="nsew")


        # 2. Main Live Viewport with Posture Correction Console
        self.viewport = ViewportFrame(
            self,
            on_toggle_guide=self._on_toggle_guide,
            on_toggle_presentation=self._on_toggle_presentation,
            on_toggle_demo_mode=self._on_toggle_demo_mode
        )
        self.viewport.grid(row=0, column=1, padx=6, pady=(16, 10), sticky="nsew")
        self.viewport.set_exercise(initial_exercise, is_active_ai=True)

        # 3. Right-Side Form Guide Panel with Body Focus & Smart Coach
        self.form_guide_visible = True
        self.form_guide = FormGuideFrame(
            self,
            current_exercise=initial_exercise,
            on_close=self._on_toggle_guide
        )
        self.form_guide.grid(row=0, column=2, padx=(6, 16), pady=(16, 10), sticky="nsew")

        # 4. Bottom Compact Session Overview Dock (Phase 7)
        self.analytics_visible = True
        self.analytics = LiveAnalyticsFrame(
            self,
            on_open_analytics=lambda: self._open_analytics_hub("OVERVIEW")
        )
        self.analytics.grid(row=1, column=0, columnspan=3, padx=16, pady=(0, 10), sticky="ew")

        # Set initial toggle state on viewport header button
        self.viewport.set_guide_toggle_state(True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _on_toggle_guide(self):
        """Toggles visibility of the right-side Form Guide reference panel."""
        if self.form_guide_visible:
            self.form_guide.grid_remove()
            self.grid_columnconfigure(2, minsize=0)
            self.form_guide_visible = False
            self.viewport.set_guide_toggle_state(False)
        else:
            self.grid_columnconfigure(2, weight=0, minsize=320)
            self.form_guide.grid(row=0, column=2, padx=(6, 16), pady=(16, 10), sticky="nsew")
            self.form_guide_visible = True
            self.viewport.set_guide_toggle_state(True)

    def _ensure_form_guide_visible(self):
        """Ensures the Form Guide panel is open."""
        if not self.form_guide_visible:
            self._on_toggle_guide()

    def _on_toggle_presentation(self):
        """Toggles SIH Presentation Mode to maximize camera viewport space."""
        if not self.is_presentation_mode:
            self.sidebar.grid_remove()
            self.grid_columnconfigure(0, minsize=0)
            self.is_presentation_mode = True
            self.viewport.set_presentation_state(True)
        else:
            self.grid_columnconfigure(0, minsize=280)
            self.sidebar.grid(row=0, column=0, padx=(16, 6), pady=(16, 10), sticky="nsew")
            self.is_presentation_mode = False
            self.viewport.set_presentation_state(False)

    def _on_explore_library(self):
        """Opens the Exercise Intelligence Library modal dialog."""
        ExerciseLibraryDialog(
            self,
            current_exercise=self.engine.current_exercise,
            on_select_exercise=self._on_exercise_selected_from_library
        )

    def _on_exercise_selected_from_library(self, exercise_id: str):
        """Handles exercise selection from the full library dialog."""
        is_active = is_active_ai_supported(exercise_id)
        if is_active:
            self.sidebar.set_exercise_selection(exercise_id)
            self._on_exercise_selected(exercise_id)
        else:
            # Guided learning mode exercise
            self.viewport.set_exercise(exercise_id, is_active_ai=False)
            self.form_guide.set_exercise(exercise_id)
            self._ensure_form_guide_visible()
            self.viewport.update_feedback(
                f"🔵 Guided Training Mode: {exercise_id} reference posture loaded.",
                theme.COLOR_INFO,
                exercise_id
            )

    def _open_personalized_plan_dialog(self):
        """Opens the personalized AI improvement plan modal dialog."""
        PersonalizedPlanDialog(self, exercise_name=self.engine.current_exercise)

    def _open_progress_dashboard_dialog(self):
        """Opens the multi-session progress intelligence dashboard."""
        ProgressDashboardDialog(self, exercise_name=self.engine.current_exercise)

    def _open_movement_intelligence_dialog(self):
        """Opens the movement intelligence modal dialog."""
        MovementIntelligenceDialog(
            self,
            exercise_name=self.engine.current_exercise,
            stability_data=self._last_stability_data,
            fatigue_data=self._last_fatigue_data,
            risk_data=self._last_risk_data,
            coach_data=self._last_coach_data,
            recovery_data=self._last_recovery_data
        )

    def _open_gym_locator_dialog(self):
        """Opens or focuses the nearby gym and fitness facility locator modal dialog."""
        if self.gym_dialog and self.gym_dialog.winfo_exists():
            self.gym_dialog.lift()
            self.gym_dialog.focus_force()
            return
        self.gym_dialog = GymLocatorDialog(self)


    def _open_analytics_hub(self, initial_tab: str = "OVERVIEW"):
        """Opens or focuses the dedicated Advanced Performance Analytics Hub."""
        if self.analytics_hub and self.analytics_hub.winfo_exists():
            self.analytics_hub.select_tab(initial_tab)
            self.analytics_hub.lift()
            self.analytics_hub.focus_force()
            return

        self.analytics_hub = AnalyticsHubDialog(
            self,
            current_exercise=self.engine.current_exercise,
            initial_tab=initial_tab,
            stats=self.engine.get_stats(),
            on_export_report=self._on_export_report
        )
        # Populate with existing reps from tracker
        tracker = RepHistoryTracker.get_instance()
        for rep in tracker.get_all_reps():
            self.analytics_hub.add_rep(rep)

        # Sync latest breakdown and telemetry
        dim_avgs = tracker.get_dimension_averages()
        if dim_avgs:
            self.analytics_hub.update_breakdown(dim_avgs, self.engine.current_exercise)

        self.analytics_hub.sync_telemetry(
            stats=self.engine.get_stats(),
            stability_data=getattr(self, "_last_stability_data", {}),
            fatigue_data=getattr(self, "_last_fatigue_data", {}),
            risk_data=getattr(self, "_last_risk_data", {}),
            coach_data=getattr(self, "_last_coach_data", {}),
            recovery_data=getattr(self, "_last_recovery_data", {})
        )

    def _on_toggle_demo_mode(self):
        """Toggles the SIH Grand Finale presentation window."""
        if self.demo_window is None:
            self.demo_window = SIHDemoWindow(
                self,
                exercise_name=self.engine.current_exercise,
                on_close_callback=self._on_demo_window_closed
            )
        else:
            self.demo_window.lift()
            self.demo_window.focus()

    def _on_demo_window_closed(self):
        self.demo_window = None

    def _on_exercise_selected(self, exercise_name: str):
        """Switches active exercise and synchronizes engine, viewport, form guide, and analytics."""
        self.engine.set_exercise(exercise_name)
        self.sidebar.update_stats(0, 100)
        self.viewport.set_exercise(exercise_name, is_active_ai=True)
        self.form_guide.set_exercise(exercise_name)
        self.analytics.reset_analytics()
        self.analytics.set_exercise(exercise_name)
        if self.analytics_hub and self.analytics_hub.winfo_exists():
            self.analytics_hub.set_exercise(exercise_name)
            self.analytics_hub.reset_analytics()
        self.viewport.reset_feedback()

        # Reset Phase 5 and 6 tracking states
        RepHistoryTracker.get_instance().reset()
        get_movement_phase_engine().reset(exercise_name)
        get_movement_stability_engine().reset(exercise_name)
        self._last_clean_reps = 0
        self._last_total_attempts = 0
        self._last_posture_warnings = 0
        self._last_sitting_fails = 0
        self._last_depth_fails = 0
        self._posture_fault_in_active_rep = False
        self.sidebar.update_goal_progress(0, 100, exercise_name)
        self.analytics.reset_phase6()
        self.form_guide.reset_phase6()

    def _start_timer(self):
        """Starts live session timer."""
        self._stop_timer()
        self.session_seconds = 0
        self._tick_timer()

    def _tick_timer(self):
        """Ticks session timer every second during active workouts."""
        if self.engine.is_running:
            self.session_seconds += 1
            self.viewport.update_timer(self.session_seconds)
            self._timer_after_id = self.after(1000, self._tick_timer)

    def _stop_timer(self):
        """Cancels active timer ticker."""
        if self._timer_after_id:
            try:
                self.after_cancel(self._timer_after_id)
            except Exception:
                pass
            self._timer_after_id = None

    def _on_start_workout(self):
        """Starts the workout session if currently idle."""
        if not self.engine.is_running:
            self._on_toggle_session()

    def _on_stop_workout(self):
        """Stops active workout session and opens the Session Performance Debrief dialog."""
        if self.engine.is_running:
            self._on_toggle_session()
        else:
            final_stats = self.engine.get_stats()
            session_data = self._prepare_session_summary_data(final_stats, self.session_seconds)
            self.after(0, lambda: self._open_session_summary_dialog(session_data))

    def _on_toggle_session(self):
        """Toggles workout session state between active and stopped with thread-safe debrief."""
        if not self.engine.is_running:
            success = self.engine.start()
            if success:
                self.sidebar.set_session_state(True)
                self.viewport.set_active_state(True)
                self._start_timer()
                self.viewport.update_feedback(
                    "Camera initialized. Begin exercise in frame.",
                    theme.COLOR_ACCENT,
                    self.engine.current_exercise
                )
            else:
                self.viewport.update_feedback(
                    "Error: Unable to initialize camera device.",
                    theme.COLOR_ALERT,
                    self.engine.current_exercise
                )
        else:
            # STOP WORKOUT SEQUENCE:
            # 1. Capture snapshot of final stats and duration
            final_stats = self.engine.get_stats()
            final_duration = self.session_seconds

            # 2. Stop camera processing & pose tracking thread
            self.engine.stop()

            # 3. Stop session workout timer
            self._stop_timer()

            # 4. Update UI states
            self.sidebar.set_session_state(False)
            self.viewport.set_active_state(False)
            self.viewport.update_feedback(
                "Workout completed. Review session debrief or click START WORKOUT.",
                theme.COLOR_TEXT_MUTED,
                self.engine.current_exercise
            )

            # 5. Prepare complete unified session_data payload
            session_data = self._prepare_session_summary_data(final_stats, final_duration)

            # 6. Dispatch Session Summary Dialog on the main UI thread
            self.after(
                0,
                lambda: self._open_session_summary_dialog(session_data)
            )

    def _prepare_session_summary_data(self, stats: Optional[Dict[str, Any]], duration: int) -> Dict[str, Any]:
        """Gathers, validates, and packages complete telemetry into one fail-safe payload."""
        stats = stats or {}
        exercise_name = getattr(self.engine, "current_exercise", "SQUAT")
        clean_reps = stats.get("clean_reps", 0)
        total_reps = stats.get("total_attempts", clean_reps)
        form_score = stats.get("accuracy", 100)

        best_rep = None
        avg_quality = form_score
        consistency_score = 100
        rep_history = []
        try:
            from core.rep_history import RepHistoryTracker
            rep_tracker = RepHistoryTracker.get_instance()
            best_rep = rep_tracker.get_best_rep()
            rep_history = rep_tracker.get_all_reps()
            if rep_tracker.get_total_reps() > 0:
                avg_quality = rep_tracker.get_average_score()
                consistency_score = rep_tracker.get_consistency_score()
        except Exception as e:
            print(f"[APP] RepHistory preparation note: {e}")

        personalized_plan = None
        try:
            from core.personalized_coach import generate_personalized_plan
            from core.rep_history import RepHistoryTracker
            personalized_plan = generate_personalized_plan(exercise_name, RepHistoryTracker.get_instance(), stats)
        except Exception as e:
            print(f"[APP] PersonalizedPlan preparation note: {e}")

        # Progress Intelligence
        progress_data = None
        try:
            from core.progress_intelligence import ProgressIntelligenceTracker
            progress_data = ProgressIntelligenceTracker.get_instance().get_progress_summary(exercise_name)
        except Exception as e:
            print(f"[APP] ProgressIntelligence preparation note: {e}")

        movement_data = None
        try:
            from core.movement_stability import get_movement_stability_engine
            from core.fatigue_intelligence import estimate_form_fatigue
            from core.risk_intelligence import evaluate_movement_risk
            from core.performance_trends import analyze_performance_trends
            from core.adaptive_coaching import get_adaptive_coaching
            from core.recovery_recommendations import get_recovery_recommendations

            stab_engine = get_movement_stability_engine()
            stab = stab_engine.update(exercise_name, stats_snapshot=stats)
            fat = estimate_form_fatigue(exercise_name, stab.get("stability_score", 90), stats)
            risk = evaluate_movement_risk(exercise_name, stab.get("stability_score", 90), fat.get("fatigue_level", "LOW"), stats)
            trend = analyze_performance_trends(exercise_name, stab.get("stability_score", 90), fat.get("fatigue_score", 0))
            coach = get_adaptive_coaching(
                exercise_name=exercise_name,
                stability_score=stab.get("stability_score", 90),
                fatigue_level=fat.get("fatigue_level", "LOW"),
                risk_level=risk.get("risk_level", "LOW"),
                current_feedback="",
                stats_snapshot=stats
            )
            rec = get_recovery_recommendations(
                fatigue_level=fat.get("fatigue_level", "LOW"),
                stability_score=stab.get("stability_score", 90),
                consecutive_faults=0,
                total_reps=total_reps
            )

            movement_data = {
                "stability": stab,
                "fatigue": fat,
                "risk": risk,
                "trend": trend,
                "coach": coach,
                "recovery": rec
            }
        except Exception as e:
            print(f"[APP] MovementIntelligence preparation note: {e}")

        return {
            "exercise": exercise_name,
            "duration": duration,
            "clean_reps": clean_reps,
            "total_reps": total_reps,
            "form_score": form_score,
            "best_rep": best_rep,
            "average_quality": avg_quality,
            "consistency_score": consistency_score,
            "rep_history": rep_history,
            "personalized_plan": personalized_plan,
            "progress_intelligence": progress_data,
            "movement_intelligence": movement_data,
            "stats": stats
        }

    def _open_session_summary_dialog(self, session_data: Dict[str, Any]):
        """Creates and renders the SessionSummaryDialog on the main UI thread and persists to DB."""
        try:
            session_id = self._save_session_to_database(session_data)
            if session_id:
                session_data["session_id"] = session_id
        except Exception as e:
            print(f"[APP] Session auto-save note: {e}")

        try:
            self.summary_dialog = SessionSummaryDialog(
                self,
                session_data=session_data,
                on_export_report=self._on_export_report,
                on_review_guide=self._ensure_form_guide_visible,
                on_view_plan=self._open_personalized_plan_dialog,
                on_view_progress=self._open_progress_dashboard_dialog,
                on_view_intelligence=self._open_movement_intelligence_dialog
            )
        except Exception as e:
            print(f"[APP ERROR] Could not open SessionSummaryDialog: {e}")

    def _save_session_to_database(self, session_data: Dict[str, Any]) -> Optional[int]:
        """Persists the completed workout debrief into SQLite database."""
        try:
            user = UserSession.get_instance().get_current_user()
            if not user:
                user = UserSession.get_instance().get_or_create_default_user()

            exercise_name = session_data.get("exercise", getattr(self.engine, "current_exercise", "SQUAT"))
            duration = session_data.get("duration", self.session_seconds)
            clean_reps = session_data.get("clean_reps", 0)
            total_reps = session_data.get("total_reps", clean_reps)
            form_score = session_data.get("form_score", 100.0)
            avg_quality = session_data.get("average_quality", form_score)
            best_rep = session_data.get("best_rep")
            best_quality = best_rep.get("overall_score", avg_quality) if best_rep else avg_quality
            consistency = session_data.get("consistency_score", 100.0)

            mv = session_data.get("movement_intelligence") or {}
            stab_data = mv.get("stability") or {}
            fat_data = mv.get("fatigue") or {}
            risk_data = mv.get("risk") or {}
            trend_data = mv.get("trend") or {}

            stability_score = stab_data.get("stability_score", 90.0)
            fatigue_level = fat_data.get("fatigue_level", "LOW")
            risk_level = risk_data.get("risk_level", "LOW")
            trajectory = trend_data.get("quality_trend", "STABLE")

            from datetime import datetime, timedelta
            now = datetime.now()
            started_at = (now - timedelta(seconds=duration)).isoformat()
            completed_at = now.isoformat()

            rep_records = session_data.get("rep_history") or []

            repo = WorkoutRepository()
            session_id = repo.save_workout_session(
                user_id=user.id,
                exercise_name=exercise_name,
                started_at=started_at,
                completed_at=completed_at,
                duration_seconds=duration,
                total_reps=total_reps,
                clean_reps=clean_reps,
                average_quality=avg_quality,
                best_rep_quality=best_quality,
                consistency_score=consistency,
                stability_score=stability_score,
                fatigue_level=fatigue_level,
                risk_level=risk_level,
                session_trajectory=trajectory,
                rep_records=rep_records
            )
            print(f"[TRUFORM DB] Workout session #{session_id} saved for {user.name} (user_id={user.id})")

            # Phase 7C: Record post-workout recovery nutrition insight
            try:
                from services.nutrition_service import NutritionService
                NutritionService().record_workout_recovery_insight(user.id, session_data)
            except Exception as nut_err:
                print(f"[TRUFORM NUTRITION] Post-workout recovery cache note: {nut_err}")

            return session_id
        except Exception as e:
            print(f"[TRUFORM DB ERROR] Failed to persist workout session: {e}")
            return None

    def _open_user_dashboard(self):
        """Opens the Athlete Performance & History Dashboard."""
        if self.user_dashboard and self.user_dashboard.winfo_exists():
            self.user_dashboard.lift()
            self.user_dashboard.focus_force()
            return

        user = UserSession.get_instance().get_current_user()
        if not user:
            user = UserSession.get_instance().get_or_create_default_user()

        self.user_dashboard = UserDashboardDialog(
            self,
            user=user,
            on_close_callback=lambda: setattr(self, "user_dashboard", None)
        )

    def _open_nutrition_dashboard(self):
        """Opens the Personalized Nutrition & Diet Intelligence Dashboard."""
        if hasattr(self, "nutrition_dashboard") and self.nutrition_dashboard and self.nutrition_dashboard.winfo_exists():
            self.nutrition_dashboard.lift()
            self.nutrition_dashboard.focus_force()
            return

        user = UserSession.get_instance().get_current_user()
        if not user:
            user = UserSession.get_instance().get_or_create_default_user()

        self.nutrition_dashboard = NutritionDashboardDialog(
            self,
            user=user,
            on_close_callback=lambda: setattr(self, "nutrition_dashboard", None)
        )

    def _handle_logout(self):
        """Safely logs out active athlete session and displays the authentication dialog."""
        if self.engine.is_running:
            self.engine.stop()
            self._stop_timer()
            self.sidebar.set_session_state(False)
            self.viewport.set_active_state(False)

        self._on_reset_metrics()
        UserSession.get_instance().logout()

        if self.user_dashboard and self.user_dashboard.winfo_exists():
            try:
                self.user_dashboard.destroy()
            except Exception:
                pass
            self.user_dashboard = None

        if hasattr(self, "nutrition_dashboard") and self.nutrition_dashboard and self.nutrition_dashboard.winfo_exists():
            try:
                self.nutrition_dashboard.destroy()
            except Exception:
                pass
            self.nutrition_dashboard = None

        if hasattr(self, "gym_dialog") and self.gym_dialog and self.gym_dialog.winfo_exists():
            try:
                self.gym_dialog.destroy()
            except Exception:
                pass
            self.gym_dialog = None

        self.auth_dialog = AuthDialog(
            self,
            on_authenticated=self._on_user_authenticated
        )

    def _on_user_authenticated(self, user):
        """Callback invoked when user logs in or switches profile."""
        self.sidebar.set_user(user)
        self.viewport.update_feedback(
            f"Athlete profile active: {user.name}. Ready to train.",
            theme.COLOR_TEAL,
            self.engine.current_exercise
        )

    def _on_user_session_changed(self, user):
        """Updates UI elements when user session changes."""
        try:
            self.sidebar.set_user(user)
        except Exception:
            pass


    def _on_export_report(self):
        """Exports session summary image and displays confirmation toast."""
        filename = self.engine.export_report()
        self.viewport.update_feedback(
            f"Diagnostic report exported: {filename}",
            theme.COLOR_SUCCESS,
            self.engine.current_exercise
        )

    def _on_reset_metrics(self):
        """Resets telemetry stats in backend, UI widgets, analytics, and coaching guidance."""
        self.engine.reset_metrics()
        self._stop_timer()
        self.session_seconds = 0
        self.viewport.update_timer(0)
        self.sidebar.set_session_state(False)
        self.sidebar.update_stats(0, 100)
        self.sidebar.reset_phase5()
        self.viewport.reset_feedback()
        self.analytics.reset_analytics()
        self.analytics.reset_phase5()
        self.analytics.reset_phase6()
        self.form_guide.reset_coaching()
        self.form_guide.reset_phase5()
        self.form_guide.reset_phase6()

        # Reset Phase 5 and 6 tracking states
        RepHistoryTracker.get_instance().reset()
        get_movement_phase_engine().reset(self.engine.current_exercise)
        get_movement_stability_engine().reset(self.engine.current_exercise)
        self._last_clean_reps = 0
        self._last_total_attempts = 0
        self._last_posture_warnings = 0
        self._last_sitting_fails = 0
        self._last_depth_fails = 0
        self._posture_fault_in_active_rep = False
        self._last_phase_data = {}
        self._last_stability_data = {}
        self._last_fatigue_data = {}
        self._last_risk_data = {}
        self._last_coach_data = {}
        self._last_recovery_data = {}
        self.sidebar.update_goal_progress(0, 100, self.engine.current_exercise)

        if self.analytics_hub and self.analytics_hub.winfo_exists():
            self.analytics_hub.reset_analytics()

        self.viewport.update_feedback(
            "Telemetry reset to baseline.",
            theme.COLOR_ACCENT,
            self.engine.current_exercise
        )

    def _on_frame_processed(
        self,
        frame: np.ndarray,
        feedback_msg: str,
        feedback_color: str,
        stats: Dict[str, Any]
    ):
        """Converts frame to CTkImage in background thread with backlog protection."""
        # 1. Backlog Protection: drop frame if GUI thread is still rendering previous frame
        if self._ui_update_in_progress:
            return

        # 2. Fast vectorized C++ resize in OpenCV (1 ms vs 6 ms in PIL)
        resized = cv2.resize(frame, (720, 480), interpolation=cv2.INTER_LINEAR)
        img = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img)
        ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(720, 480))

        self._ui_update_in_progress = True

        # Schedule thread-safe main loop update
        self.after(
            0,
            self._apply_ui_updates,
            ctk_img,
            stats["clean_reps"],
            stats["accuracy"],
            feedback_msg,
            feedback_color,
            stats
        )

    def _apply_ui_updates(
        self,
        ctk_img: ctk.CTkImage,
        reps: int,
        acc: int,
        feedback_msg: str,
        feedback_color: str,
        stats: Optional[Dict[str, Any]] = None
    ):
        """Applies visual updates strictly on the Tkinter main thread with throttled telemetry."""
        try:
            # 1. High-framerate video and primary HUD updates (every processed frame)
            self.sidebar.update_stats(reps, acc)
            self.viewport.update_frame(ctk_img)
            self.viewport.update_feedback(feedback_msg, feedback_color, self.engine.current_exercise)

            # Update SIH Demo Window video frame if open
            if self.demo_window:
                self.demo_window.update_frame(ctk_img)

            curr_clean = stats.get("clean_reps", reps) if stats else reps
            curr_total = stats.get("total_attempts", reps) if stats else reps
            curr_warn = stats.get("posture_warnings", 0) if stats else 0
            curr_sitting = stats.get("failed_sitting", 0) if stats else 0
            curr_depth = stats.get("failed_depth", 0) if stats else 0

            # Detect intra-rep posture warning
            warning_triggered = False
            if curr_warn > self._last_posture_warnings:
                self._posture_fault_in_active_rep = True
                self._last_posture_warnings = curr_warn
                warning_triggered = True

            # Detect repetition completion
            rep_completed = False
            rep_result = "CLEAN"

            if curr_total > self._last_total_attempts:
                rep_completed = True
                if curr_clean > self._last_clean_reps:
                    rep_result = "CLEAN"
                elif curr_sitting > self._last_sitting_fails:
                    rep_result = "FAILED_SITTING"
                else:
                    rep_result = "FAILED_DEPTH"
            elif curr_clean > self._last_clean_reps:
                rep_completed = True
                rep_result = "CLEAN"

            # 2. Telemetry Throttling: Run heavy motion intelligence & reconfigure cards at 4 Hz (250ms)
            # OR immediately if a rep completes or a warning is triggered
            now = time.time()
            time_due = (now - self._last_telemetry_time) >= UI_TELEMETRY_THROTTLE_SEC
            should_update_telemetry = rep_completed or warning_triggered or time_due

            if should_update_telemetry:
                self._last_telemetry_time = now

                # Motion Intelligence Calculations
                phase_engine = get_movement_phase_engine()
                phase_data = phase_engine.update(
                    self.engine.current_exercise,
                    getattr(self.engine, "current_angle", None),
                    feedback_msg,
                    stats
                )
                self._last_phase_data = phase_data

                stab_engine = get_movement_stability_engine()
                stability_data = stab_engine.update(
                    self.engine.current_exercise,
                    getattr(self.engine, "current_angle", None),
                    feedback_msg,
                    stats
                )
                self._last_stability_data = stability_data

                fatigue_data = estimate_form_fatigue(
                    self.engine.current_exercise,
                    stability_data["stability_score"],
                    stats
                )
                self._last_fatigue_data = fatigue_data

                risk_data = evaluate_movement_risk(
                    self.engine.current_exercise,
                    stability_data["stability_score"],
                    fatigue_data["fatigue_level"],
                    stats
                )
                self._last_risk_data = risk_data

                coach_data = get_adaptive_coaching(
                    self.engine.current_exercise,
                    stability_data["stability_score"],
                    fatigue_data["fatigue_level"],
                    risk_data["risk_level"],
                    feedback_msg,
                    stats
                )
                self._last_coach_data = coach_data

                recovery_data = get_recovery_recommendations(
                    fatigue_data["fatigue_level"],
                    stability_data["stability_score"],
                    total_reps=reps
                )
                self._last_recovery_data = recovery_data

                # Update Form Guide Phase 6 cards
                if self.form_guide_visible:
                    self.form_guide.update_movement_phase(phase_data)
                    self.form_guide.update_movement_intelligence(
                        stability_data, fatigue_data, risk_data, coach_data, recovery_data
                    )

                # Update SIH Demo Window telemetry if open
                if self.demo_window:
                    self.demo_window.update_telemetry(
                        reps, acc, feedback_msg, feedback_color,
                        phase_data, stability_data, fatigue_data, risk_data, coach_data
                    )

                # Update Live Performance Analytics and Rep-by-Rep Intelligence
                self.analytics.update_status_indicators(stability_data, risk_data, fatigue_data)

                # Synchronize Analytics Hub if open
                if self.analytics_hub and self.analytics_hub.winfo_exists():
                    self.analytics_hub.sync_telemetry(
                        stats=stats if stats else {"clean_reps": reps, "accuracy": acc, "total_attempts": reps},
                        stability_data=stability_data,
                        fatigue_data=fatigue_data,
                        risk_data=risk_data,
                        coach_data=coach_data,
                        recovery_data=recovery_data
                    )

                if stats:
                    self.analytics.update_analytics(stats, self.engine.current_exercise)
                else:
                    self.analytics.update_analytics({"clean_reps": reps, "accuracy": acc, "total_attempts": reps}, self.engine.current_exercise)

                # Synchronize Body Focus avatar, Smart Coach, Form Comparison, and checklist highlight
                if self.form_guide_visible and feedback_msg:
                    self.form_guide.update_ai_coaching(feedback_msg, feedback_color)
                    self.form_guide.update_form_comparison(self.engine.current_exercise, feedback_msg, feedback_color)

            # Rep completion processing (always runs immediately when rep completes)
            if rep_completed and stats:
                rep_num = curr_total if curr_total > 0 else curr_clean
                rep_analysis = analyze_repetition(
                    exercise_name=self.engine.current_exercise,
                    rep_number=rep_num,
                    rep_result=rep_result,
                    posture_warning_occurred=self._posture_fault_in_active_rep,
                    feedback_msg=feedback_msg,
                    stats_snapshot=stats
                )
                RepHistoryTracker.get_instance().add_rep(rep_analysis)

                # Dispatch updates to Phase 5 and Phase 6 UI components (timeline + heatmap)
                self.analytics.add_rep_to_timeline(rep_analysis)
                self.analytics.update_breakdown(
                    RepHistoryTracker.get_instance().get_dimension_averages(),
                    self.engine.current_exercise
                )
                self.sidebar.update_goal_progress(curr_clean, acc, self.engine.current_exercise)
                self.form_guide.update_personalized_plan(self.engine.current_exercise)

                # Dispatch rep to open Analytics Hub
                if self.analytics_hub and self.analytics_hub.winfo_exists():
                    self.analytics_hub.add_rep(rep_analysis)
                    self.analytics_hub.update_breakdown(
                        RepHistoryTracker.get_instance().get_dimension_averages(),
                        self.engine.current_exercise
                    )

                # Synchronize SIH Demo Window
                if self.demo_window:
                    self.demo_window.add_rep(rep_analysis)

                # Reset intra-rep tracking
                self._last_clean_reps = curr_clean
                self._last_total_attempts = curr_total
                self._last_sitting_fails = curr_sitting
                self._last_depth_fails = curr_depth
                self._posture_fault_in_active_rep = False

        except Exception as e:
            print(f"[APP UI ERROR] {e}")
        finally:
            self._ui_update_in_progress = False

    def on_close(self):
        """Tears down backend engine and closes window safely."""
        try:
            UserSession.get_instance().remove_listener(self._on_user_session_changed)
        except Exception:
            pass
        if self.demo_window:
            try:
                self.demo_window.destroy()
            except Exception:
                pass
        if self.analytics_hub:
            try:
                self.analytics_hub.destroy()
            except Exception:
                pass
        if self.user_dashboard:
            try:
                self.user_dashboard.destroy()
            except Exception:
                pass
        if self.auth_dialog:
            try:
                self.auth_dialog.destroy()
            except Exception:
                pass
        self.engine.stop()
        self.destroy()



def run_app(require_auth: bool = False):
    """Application runner. If require_auth is True and no user is authenticated, launches AuthWindow."""
    init_db()
    if require_auth and not UserSession.get_instance().is_authenticated():
        from ui.auth import AuthWindow
        def start_main(user):
            app = AIWorkoutUI()
            app.mainloop()

        auth_win = AuthWindow(on_authenticated=start_main)
        auth_win.mainloop()
    else:
        app = AIWorkoutUI()
        app.mainloop()


if __name__ == "__main__":
    run_app()

