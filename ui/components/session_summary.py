"""AI Session Summary Modal Dialog Component for REPRIGHT AI.

Displays comprehensive post-workout debriefing: verified repetition counts, accuracy score,
strengths, targeted improvement areas, next session goal, movement intelligence telemetry,
and actionable coaching guidance with fail-safe component-level error isolation.
"""

from typing import Callable, Optional, Dict, Any, List
import customtkinter as ctk

from ui import theme
from core.session_insights import generate_session_insights, SessionHistoryTracker
from core.rep_history import RepHistoryTracker
from core.personalized_coach import generate_personalized_plan
from core.progress_intelligence import ProgressIntelligenceTracker
from core.fatigue_intelligence import estimate_form_fatigue
from core.risk_intelligence import evaluate_movement_risk
from core.performance_trends import analyze_performance_trends
from core.movement_stability import get_movement_stability_engine
from core.adaptive_coaching import get_adaptive_coaching
from core.recovery_recommendations import get_recovery_recommendations


class SessionSummaryDialog(ctk.CTkToplevel):
    """Post-workout debriefing modal dialog with fail-safe architecture."""

    def __init__(
        self,
        master,
        exercise_name: Optional[Any] = None,
        stats: Optional[Dict[str, Any]] = None,
        duration_seconds: int = 0,
        session_data: Optional[Dict[str, Any]] = None,
        on_export_report: Optional[Callable[[], None]] = None,
        on_review_guide: Optional[Callable[[], None]] = None,
        on_view_plan: Optional[Callable[[], None]] = None,
        on_view_progress: Optional[Callable[[], None]] = None,
        on_view_intelligence: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)

        # 1. Handle dual signature (session_data dict vs legacy arguments)
        if isinstance(exercise_name, dict) and session_data is None:
            session_data = exercise_name
            exercise_name = session_data.get("exercise", "SQUAT")

        self.on_export_report = on_export_report
        self.on_review_guide = on_review_guide
        self.on_view_plan = on_view_plan
        self.on_view_progress = on_view_progress
        self.on_view_intelligence = on_view_intelligence

        # 2. Normalize and assemble complete session_data payload with safe fallbacks
        self.session_data = self._normalize_session_data(
            session_data=session_data,
            exercise_name=exercise_name,
            stats=stats,
            duration_seconds=duration_seconds
        )

        # 3. Configure Toplevel Window
        self.title("REPRIGHT AI - Session Performance Intelligence & Debrief")
        self.geometry("1100x750")
        self.minsize(850, 620)
        self.configure(fg_color=theme.COLOR_BG_DARK)

        if master:
            self.transient(master)

        # Grid configuration on Toplevel: single container cell
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 4. Create Main Container Frame
        self.main_container = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_BG_DARK,
            corner_radius=0
        )
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=0)  # Header
        self.main_container.grid_rowconfigure(1, weight=1)  # Scrollable Body
        self.main_container.grid_rowconfigure(2, weight=0)  # Footer Actions

        # 5. Build Header, Scrollable Body, and Footer
        self._build_header()
        self._build_scrollable_body()
        self._build_footer()

        # 6. Build Content with Component-Level Error Isolation
        self._build_all_sections()

        # 7. Validate Widget Creation & Finalize Rendering
        self._validate_and_finalize()

    def _normalize_session_data(
        self,
        session_data: Optional[Dict[str, Any]],
        exercise_name: Optional[Any],
        stats: Optional[Dict[str, Any]],
        duration_seconds: int
    ) -> Dict[str, Any]:
        """Safely gathers, resolves, and validates all session telemetry."""
        payload = dict(session_data) if session_data else {}

        ex_name = (
            payload.get("exercise")
            or (exercise_name if isinstance(exercise_name, str) else None)
            or "SQUAT"
        ).upper().strip()

        st = payload.get("stats") or stats or {}
        dur = payload.get("duration", duration_seconds or 0)
        clean_reps = payload.get("clean_reps", st.get("clean_reps", 0))
        total_reps = payload.get("total_reps", st.get("total_attempts", clean_reps))
        form_score = payload.get("form_score", st.get("accuracy", 100))

        # Rep history metrics
        best_rep = payload.get("best_rep")
        avg_quality = payload.get("average_quality", form_score)
        consistency_score = payload.get("consistency_score", 100)
        common_issue = "None (Optimal Form Maintained)"
        strongest_cat = "movement_control"
        weakest_cat = "range_of_motion"

        try:
            rep_tracker = RepHistoryTracker.get_instance()
            if best_rep is None and rep_tracker.get_total_reps() > 0:
                best_rep = rep_tracker.get_best_rep()
            if "average_quality" not in payload and rep_tracker.get_total_reps() > 0:
                avg_quality = rep_tracker.get_average_score()
            if "consistency_score" not in payload and rep_tracker.get_total_reps() > 0:
                consistency_score = rep_tracker.get_consistency_score()
            common_issue = rep_tracker.get_most_common_issue()
            strongest_cat, _ = rep_tracker.get_strongest_category()
            weakest_cat, _ = rep_tracker.get_weakest_category()
        except Exception as e:
            print(f"[SESSION SUMMARY] RepHistory resolution note: {e}")

        # Session Insights & History Tracker
        insights = payload.get("insights")
        comparison = payload.get("comparison")
        try:
            tracker = SessionHistoryTracker.get_instance()
            if insights is None:
                insights = tracker.record_session(ex_name, st, dur)
            if comparison is None:
                comparison = tracker.get_recent_comparison(ex_name)
        except Exception as e:
            print(f"[SESSION SUMMARY] Insights resolution note: {e}")
            insights = {
                "exercise": ex_name,
                "clean_reps": clean_reps,
                "total_attempts": total_reps,
                "accuracy": form_score,
                "duration_str": f"{dur // 60:02d}:{dur % 60:02d}",
                "timestamp": "Now",
                "tier": "EXCELLENT" if form_score >= 90 else ("GOOD" if form_score >= 75 else "NEEDS_IMPROVEMENT"),
                "tier_badge": "🟢 EXCELLENT SESSION" if form_score >= 90 else ("🟡 GOOD SESSION" if form_score >= 75 else "🔴 NEEDS IMPROVEMENT"),
                "tier_summary": "Solid movement execution with biomechanical tracking.",
                "strengths": ["Movement cadence maintained"],
                "improvements": ["Continue regular practice"],
                "primary_focus": "Form Consistency",
                "recommendation": "Maintain controlled tempo and focus on joint alignment.",
                "next_session_goal": f"Target {clean_reps + 2} clean reps."
            }
            comparison = None

        # Multi-session Progress Intelligence Tracker
        try:
            ProgressIntelligenceTracker.get_instance().record_completed_session(
                exercise_name=ex_name,
                stats=st,
                duration_seconds=dur,
                best_rep_score=best_rep.get("overall_score", form_score) if best_rep else form_score,
                avg_rep_score=avg_quality,
                consistency_score=consistency_score,
                most_common_issue=common_issue,
                strongest_cat=strongest_cat,
                weakest_cat=weakest_cat
            )
        except Exception as e:
            print(f"[SESSION SUMMARY] ProgressTracker recording note: {e}")

        # Personalized Coach Plan
        personalized_plan = payload.get("personalized_plan")
        if personalized_plan is None:
            try:
                rep_tracker = RepHistoryTracker.get_instance()
                personalized_plan = generate_personalized_plan(ex_name, rep_tracker, st)
            except Exception as e:
                print(f"[SESSION SUMMARY] Personalized plan generation note: {e}")
                personalized_plan = None

        # Movement Intelligence
        movement_intel = payload.get("movement_intelligence")
        if movement_intel is None:
            try:
                stab_engine = get_movement_stability_engine()
                stability_data = stab_engine.update(ex_name, stats_snapshot=st)
                fatigue_data = estimate_form_fatigue(ex_name, stability_data.get("stability_score", 90), st)
                risk_data = evaluate_movement_risk(ex_name, stability_data.get("stability_score", 90), fatigue_data.get("fatigue_level", "LOW"), st)
                trend_data = analyze_performance_trends(ex_name, stability_data.get("stability_score", 90), fatigue_data.get("fatigue_score", 0))
                coach_data = get_adaptive_coaching(
                    exercise_name=ex_name,
                    stability_score=stability_data.get("stability_score", 90),
                    fatigue_level=fatigue_data.get("fatigue_level", "LOW"),
                    risk_level=risk_data.get("risk_level", "LOW"),
                    current_feedback="",
                    stats_snapshot=st
                )
                rec_data = get_recovery_recommendations(
                    fatigue_level=fatigue_data.get("fatigue_level", "LOW"),
                    stability_score=stability_data.get("stability_score", 90),
                    consecutive_faults=0,
                    total_reps=total_reps
                )
                movement_intel = {
                    "stability": stability_data,
                    "fatigue": fatigue_data,
                    "risk": risk_data,
                    "trend": trend_data,
                    "coach": coach_data,
                    "recovery": rec_data
                }
            except Exception as e:
                print(f"[SESSION SUMMARY] Movement intelligence note: {e}")
                movement_intel = None

        return {
            "exercise": ex_name,
            "duration": dur,
            "duration_str": insights.get("duration_str", f"{dur // 60:02d}:{dur % 60:02d}"),
            "timestamp": insights.get("timestamp", "Now"),
            "clean_reps": clean_reps,
            "total_reps": total_reps,
            "form_score": form_score,
            "best_rep": best_rep,
            "average_quality": avg_quality,
            "consistency_score": consistency_score,
            "insights": insights,
            "comparison": comparison,
            "personalized_plan": personalized_plan,
            "movement_intelligence": movement_intel,
            "stats": st
        }

    # ==========================================================================
    # CONTAINER SETUP
    # ==========================================================================

    def _build_header(self):
        """Constructs the top persistent banner containing session meta & form score."""
        self.header_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=theme.COLOR_PANEL_BG,
            corner_radius=0
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")

        h_inner = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        h_inner.pack(fill="x", padx=24, pady=16)

        # Left Column: Trophy Badge, Exercise Title, Meta details
        left_box = ctk.CTkFrame(h_inner, fg_color="transparent")
        left_box.pack(side="left", fill="y", expand=False)

        top_tag = ctk.CTkLabel(
            left_box,
            text="● SESSION COMPLETE — PERFORMANCE DEBRIEF",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_ACCENT
        )
        top_tag.pack(anchor="w")

        ex_lbl = ctk.CTkLabel(
            left_box,
            text=f"{self.session_data['exercise']} PERFORMANCE DEBRIEF",
            font=ctk.CTkFont(size=theme.FONT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        ex_lbl.pack(anchor="w", pady=(2, 0))

        meta_txt = (
            f"Exercise: {self.session_data['exercise']}   •   "
            f"Duration: {self.session_data['duration_str']}   •   "
            f"Completed: {self.session_data['timestamp']}"
        )
        meta_lbl = ctk.CTkLabel(
            left_box,
            text=meta_txt,
            font=ctk.CTkFont(size=theme.FONT_SUBTITLE[1]),
            text_color=theme.COLOR_TEXT_MUTED
        )
        meta_lbl.pack(anchor="w", pady=(2, 0))

        # Right Column: Big Form Score Card
        score_val = self.session_data["form_score"]
        score_color = theme.COLOR_SUCCESS if score_val >= 80 else (theme.COLOR_WARN if score_val >= 60 else theme.COLOR_ALERT)

        score_box = ctk.CTkFrame(
            h_inner,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        score_box.pack(side="right")

        score_num = ctk.CTkLabel(
            score_box,
            text=f"{score_val}%",
            font=ctk.CTkFont(size=theme.FONT_HERO[1] - 4, weight="bold"),
            text_color=score_color
        )
        score_num.pack(padx=20, pady=(6, 0))

        score_sub = ctk.CTkLabel(
            score_box,
            text="OVERALL FORM QUALITY",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1] - 1, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        )
        score_sub.pack(padx=20, pady=(0, 6))

    def _build_scrollable_body(self):
        """Constructs the scrollable content canvas."""
        self.body = ctk.CTkScrollableFrame(
            self.main_container,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=theme.COLOR_BORDER,
            scrollbar_button_hover_color=theme.COLOR_BORDER_LIGHT
        )
        self.body.grid(row=1, column=0, padx=24, pady=12, sticky="nsew")

    def _build_footer(self):
        """Constructs the bottom persistent action button bar."""
        self.footer = ctk.CTkFrame(
            self.main_container,
            fg_color=theme.COLOR_PANEL_BG,
            corner_radius=0
        )
        self.footer.grid(row=2, column=0, sticky="ew")

        f_inner = ctk.CTkFrame(self.footer, fg_color="transparent")
        f_inner.pack(fill="x", padx=24, pady=12)

        if self.on_export_report:
            btn_export = ctk.CTkButton(
                f_inner,
                text="EXPORT REPORT",
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
                height=36,
                corner_radius=8,
                fg_color=theme.COLOR_BTN_EXPORT,
                hover_color=theme.COLOR_BTN_EXPORT_HOVER,
                text_color=theme.COLOR_WHITE,
                command=self._on_export_clicked
            )
            btn_export.pack(side="left", padx=(0, 8))

        if self.on_view_plan:
            btn_plan = ctk.CTkButton(
                f_inner,
                text="AI PLAN",
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
                height=36,
                corner_radius=8,
                fg_color=theme.COLOR_CARD_ELEVATED,
                hover_color=theme.COLOR_BORDER_LIGHT,
                text_color=theme.COLOR_TEXT_PRIMARY,
                command=self.on_view_plan
            )
            btn_plan.pack(side="left", padx=(0, 8))

        if self.on_view_progress:
            btn_progress = ctk.CTkButton(
                f_inner,
                text="PROGRESS",
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
                height=36,
                corner_radius=8,
                fg_color=theme.COLOR_CARD_ELEVATED,
                hover_color=theme.COLOR_BORDER_LIGHT,
                text_color=theme.COLOR_TEXT_PRIMARY,
                command=self.on_view_progress
            )
            btn_progress.pack(side="left", padx=(0, 8))

        if self.on_view_intelligence:
            btn_intel = ctk.CTkButton(
                f_inner,
                text="INTELLIGENCE",
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
                height=36,
                corner_radius=8,
                fg_color=theme.COLOR_CARD_ELEVATED,
                hover_color=theme.COLOR_BORDER_LIGHT,
                text_color=theme.COLOR_TEXT_PRIMARY,
                command=self.on_view_intelligence
            )
            btn_intel.pack(side="left", padx=(0, 8))

        if self.on_review_guide:
            btn_guide = ctk.CTkButton(
                f_inner,
                text="FORM GUIDE",
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
                height=36,
                corner_radius=8,
                fg_color=theme.COLOR_CARD_ELEVATED,
                hover_color=theme.COLOR_BORDER_LIGHT,
                text_color=theme.COLOR_TEXT_SECONDARY,
                command=self._on_guide_clicked
            )
            btn_guide.pack(side="left")

        btn_close = ctk.CTkButton(
            f_inner,
            text="CLOSE",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
            height=36,
            width=90,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_BORDER_LIGHT,
            text_color=theme.COLOR_TEXT_SECONDARY,
            command=self.destroy
        )
        btn_close.pack(side="right")

    # ==========================================================================
    # SECTION BUILDERS (WITH COMPONENT-LEVEL ISOLATION)
    # ==========================================================================

    def _build_all_sections(self):
        """Builds each debrief card with isolated exception containment."""
        # 1. KPI Cards Row
        try:
            self._build_kpi_section()
        except Exception as e:
            print(f"[SESSION SUMMARY ERROR] KPI section: {e}")
            self._show_section_error("KPI data unavailable for this session")

        # 2. Session Performance Tier Card
        try:
            self._build_performance_tier_section()
        except Exception as e:
            print(f"[SESSION SUMMARY ERROR] Performance tier section: {e}")
            self._show_section_error("Session performance analysis unavailable")

        # 3. Personalized AI Improvement Plan
        try:
            self._build_personalized_plan_section()
        except Exception as e:
            print(f"[SESSION SUMMARY ERROR] Personalized plan section: {e}")
            self._show_section_error("Personalized coaching data is being prepared.")

        # 4. Movement Intelligence Section
        try:
            self._build_movement_intelligence_section()
        except Exception as e:
            print(f"[SESSION SUMMARY ERROR] Movement intelligence section: {e}")
            self._show_section_error("Movement intelligence data unavailable for this session.")

        # 5. Runtime Progression Comparison Card (if applicable)
        try:
            if self.session_data.get("comparison"):
                self._build_comparison_section()
        except Exception as e:
            print(f"[SESSION SUMMARY ERROR] Progression comparison section: {e}")

        # 6. Biomechanical Diagnostic Observations & Strengths
        try:
            self._build_insights_section()
        except Exception as e:
            print(f"[SESSION SUMMARY ERROR] Biomechanical insights section: {e}")
            self._show_section_error("Biomechanical observation notes unavailable")

    def _build_kpi_section(self):
        """Renders the 5 primary KPI cards: Clean Reps, Attempts, Best Rep, Avg Quality, Consistency."""
        kpi_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(2, 10))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1, uniform="kpi")

        clean_reps = self.session_data.get("clean_reps", 0)
        total_reps = self.session_data.get("total_reps", 0)
        best_rep = self.session_data.get("best_rep")
        best_str = f"{best_rep['overall_score']}%" if (best_rep and "overall_score" in best_rep) else f"{self.session_data.get('form_score', 100)}%"
        avg_quality = self.session_data.get("average_quality", 100)
        consistency = self.session_data.get("consistency_score", 100)

        cards = [
            ("CLEAN REPS", str(clean_reps), theme.COLOR_ACCENT),
            ("TOTAL ATTEMPTS", str(total_reps), theme.COLOR_TEXT_PRIMARY),
            ("BEST REP", best_str, theme.COLOR_SUCCESS),
            ("AVG REP QUALITY", f"{avg_quality}%", theme.COLOR_ACCENT),
            ("CONSISTENCY SCORE", f"{consistency}%", theme.COLOR_SUCCESS if consistency >= 80 else theme.COLOR_WARN),
        ]

        for i, (title, val, color) in enumerate(cards):
            c = ctk.CTkFrame(
                kpi_frame,
                corner_radius=10,
                fg_color=theme.COLOR_CARD_BG,
                border_width=1,
                border_color=theme.COLOR_BORDER
            )
            c.grid(row=0, column=i, padx=3, pady=2, sticky="nsew")

            t = ctk.CTkLabel(
                c,
                text=title,
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=theme.COLOR_TEXT_MUTED
            )
            t.pack(anchor="w", padx=10, pady=(8, 1))

            v = ctk.CTkLabel(
                c,
                text=val,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=color
            )
            v.pack(anchor="w", padx=10, pady=(0, 8))

    def _build_performance_tier_section(self):
        """Renders the session performance classification: EXCELLENT / GOOD / NEEDS IMPROVEMENT."""
        score = self.session_data.get("form_score", 100)
        if score >= 90:
            tier_badge = "🟢 EXCELLENT SESSION"
            tier_color = theme.COLOR_SUCCESS
            tier_desc = "Outstanding movement quality, optimal joint alignment, and rhythmic consistency throughout."
        elif score >= 75:
            tier_badge = "🟡 GOOD SESSION"
            tier_color = theme.COLOR_WARN
            tier_desc = "Solid overall execution with minor posture deviations or depth adjustments to refine."
        else:
            tier_badge = "🔴 NEEDS IMPROVEMENT"
            tier_color = theme.COLOR_ALERT
            tier_desc = "Form adjustments recommended. Focus on range of motion and joint tracking before increasing cadence."

        card = ctk.CTkFrame(
            self.body,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        card.pack(fill="x", pady=6)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x")

        ctk.CTkLabel(
            top_row,
            text="SESSION PERFORMANCE RATING",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(side="left")

        badge = ctk.CTkLabel(
            top_row,
            text=f"  {tier_badge}  ",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=tier_color,
            fg_color=theme.COLOR_CARD_ALT,
            corner_radius=6
        )
        badge.pack(side="right")

        ctk.CTkLabel(
            inner,
            text=tier_desc,
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=760,
            justify="left"
        ).pack(anchor="w", pady=(6, 0))

    def _build_personalized_plan_section(self):
        """Renders the Personalized AI Improvement Plan with 6 actionable dimensions."""
        plan = self.session_data.get("personalized_plan")

        card = ctk.CTkFrame(
            self.body,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        card.pack(fill="x", pady=6)

        header = ctk.CTkLabel(
            card,
            text="🧠 PERSONALIZED AI IMPROVEMENT PLAN",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_ACCENT
        )
        header.pack(anchor="w", padx=16, pady=(12, 6))

        if not plan:
            # Safe fallback if engine data is missing
            fallback_lbl = ctk.CTkLabel(
                card,
                text="Personalized coaching data is being prepared.",
                font=ctk.CTkFont(size=11),
                text_color=theme.COLOR_TEXT_MUTED
            )
            fallback_lbl.pack(anchor="w", padx=16, pady=(0, 12))
            return

        strength = plan.get("strength", "Biomechanical tracking profile active.")
        focus = plan.get("primary_focus", "Depth & Range of Motion")
        why = plan.get("why_it_matters", "Proper form prevents joint strain and optimizes target muscle recruitment.")
        next_goal = plan.get("next_session_goal", "Maintain 90%+ form score.")
        cue = plan.get("coaching_cue", '"Keep chest proud and brace core."')
        drill = plan.get("recommended_practice", "Practice paused reps using controlled bodyweight.")

        # Strength
        st_lbl = ctk.CTkLabel(
            card,
            text=f"• Your Strength: {strength}",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_SUCCESS,
            wraplength=760,
            justify="left"
        )
        st_lbl.pack(anchor="w", padx=16, pady=2)

        # Primary Focus & Why
        foc_lbl = ctk.CTkLabel(
            card,
            text=f"• Primary Focus: {focus} — {why}",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=760,
            justify="left"
        )
        foc_lbl.pack(anchor="w", padx=16, pady=2)

        # Tactical Coaching Cue
        cue_lbl = ctk.CTkLabel(
            card,
            text=f"• Tactical Coaching Cue: {cue}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_ACCENT,
            wraplength=760,
            justify="left"
        )
        cue_lbl.pack(anchor="w", padx=16, pady=2)

        # Next Session Goal & Recommended Drill
        rec_lbl = ctk.CTkLabel(
            card,
            text=f"• Recommended Drill: {drill} (Goal: {next_goal})",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_SECONDARY,
            wraplength=760,
            justify="left"
        )
        rec_lbl.pack(anchor="w", padx=16, pady=(2, 12))

    def _build_movement_intelligence_section(self):
        """Renders Phase 6 Movement Intelligence telemetry with fallback containment."""
        intel = self.session_data.get("movement_intelligence")

        card = ctk.CTkFrame(
            self.body,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        card.pack(fill="x", pady=6)

        header = ctk.CTkLabel(
            card,
            text="⚡ ADVANCED MOVEMENT INTELLIGENCE SUMMARY",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_ACCENT
        )
        header.pack(anchor="w", padx=16, pady=(12, 6))

        if not intel:
            fallback_lbl = ctk.CTkLabel(
                card,
                text="Movement intelligence data unavailable for this session.",
                font=ctk.CTkFont(size=11),
                text_color=theme.COLOR_TEXT_MUTED
            )
            fallback_lbl.pack(anchor="w", padx=16, pady=(0, 12))
            return

        stab = intel.get("stability") or {}
        fat = intel.get("fatigue") or {}
        risk = intel.get("risk") or {}
        trend = intel.get("trend") or {}
        coach = intel.get("coach") or {}
        rec = intel.get("recovery") or {}

        # 6 Metric Pills in Grid
        grid_f = ctk.CTkFrame(card, fg_color="transparent")
        grid_f.pack(fill="x", padx=16, pady=(4, 8))
        grid_f.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="intel_pill")

        stab_score = stab.get("stability_score", 90)
        stab_col = theme.COLOR_SUCCESS if stab_score >= 85 else (theme.COLOR_WARN if stab_score >= 60 else theme.COLOR_ALERT)

        fat_lvl = fat.get("fatigue_level", "LOW")
        fat_col = theme.COLOR_SUCCESS if fat_lvl == "LOW" else (theme.COLOR_WARN if fat_lvl == "MODERATE" else theme.COLOR_ALERT)

        risk_lvl = risk.get("risk_level", "LOW")
        risk_col = theme.COLOR_SUCCESS if risk_lvl == "LOW" else (theme.COLOR_WARN if risk_lvl == "MODERATE" else theme.COLOR_ALERT)

        trend_txt = trend.get("quality_trend", "STABLE")
        trend_col = theme.COLOR_SUCCESS if trend_txt == "IMPROVING" else (theme.COLOR_ACCENT if trend_txt == "STABLE" else theme.COLOR_WARN)

        coach_mode = coach.get("mode_pill", "CALM")
        coach_col = theme.COLOR_SUCCESS if coach_mode == "CALM" else theme.COLOR_ACCENT

        rec_status = rec.get("status_pill", "CONTINUE")
        rec_col = theme.COLOR_SUCCESS if "CONTINUE" in rec_status else theme.COLOR_WARN

        pills = [
            ("STABILITY", f"{stab_score}%", stab_col),
            ("FORM FATIGUE", fat_lvl, fat_col),
            ("RISK AWARENESS", risk_lvl, risk_col),
            ("TRAJECTORY", trend_txt, trend_col),
            ("COACH MODE", coach_mode, coach_col),
            ("RECOVERY", rec_status, rec_col),
        ]

        for i, (k, v, c) in enumerate(pills):
            p = ctk.CTkFrame(
                grid_f,
                fg_color=theme.COLOR_CARD_ALT,
                corner_radius=6,
                border_width=1,
                border_color=theme.COLOR_BORDER
            )
            p.grid(row=0, column=i, padx=2, sticky="ew")
            ctk.CTkLabel(p, text=k, font=ctk.CTkFont(size=8, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(pady=(4, 0))
            ctk.CTkLabel(p, text=v, font=ctk.CTkFont(size=10, weight="bold"), text_color=c).pack(pady=(0, 4))

        # Action notes
        c_msg = coach.get("primary_message", "Excellent torso stability and consistent turnaround cadence.")
        r_act = rec.get("suggested_action", "Maintain cadence and regular rest intervals.")

        note_txt = f"• Adaptive Coaching Insight: {c_msg}\n• Smart Recovery Recommendation: {r_act}"
        ctk.CTkLabel(
            card,
            text=note_txt,
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=760,
            justify="left"
        ).pack(anchor="w", padx=16, pady=(2, 10))

    def _build_comparison_section(self):
        """Renders Smart Progression comparison if a previous session exists."""
        comp = self.session_data.get("comparison")
        if not comp:
            return

        card = ctk.CTkFrame(
            self.body,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_INNER,
            border_width=1,
            border_color=theme.COLOR_ACCENT_MUTED
        )
        card.pack(fill="x", pady=6)

        t_lbl = ctk.CTkLabel(
            card,
            text="SMART RUNTIME PROGRESSION",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_ACCENT
        )
        t_lbl.pack(anchor="w", padx=16, pady=(8, 2))

        txt = (
            f"{comp.get('trend_icon', '↑')} {comp.get('trend_text', 'Progress')}  •  "
            f"Previous Session: {comp.get('previous_accuracy', 0)}%  →  "
            f"Current Session: {comp.get('current_accuracy', 0)}%"
        )
        desc = ctk.CTkLabel(
            card,
            text=txt,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme.COLOR_SUCCESS if comp.get("delta_accuracy", 0) >= 0 else theme.COLOR_WARN
        )
        desc.pack(anchor="w", padx=16, pady=(0, 8))

    def _build_insights_section(self):
        """Renders verified biomechanical diagnostic observations and form corrections."""
        insights = self.session_data.get("insights") or {}
        strengths = insights.get("strengths", ["Biomechanical tracking calibrated"])
        improvements = insights.get("improvements", ["Maintain controlled movement tempo"])

        card = ctk.CTkFrame(
            self.body,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        card.pack(fill="x", pady=6)

        header = ctk.CTkLabel(
            card,
            text="AI BIOMECHANICAL OBSERVATIONS & STRENGTHS",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        header.pack(anchor="w", padx=16, pady=(12, 6))

        for s in strengths:
            r = ctk.CTkFrame(card, fg_color="transparent")
            r.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(r, text="✓", font=ctk.CTkFont(size=11, weight="bold"), text_color=theme.COLOR_SUCCESS, width=16).pack(side="left")
            ctk.CTkLabel(r, text=s, font=ctk.CTkFont(size=10), text_color=theme.COLOR_TEXT_PRIMARY).pack(side="left", padx=6)

        for imp in improvements:
            r = ctk.CTkFrame(card, fg_color="transparent")
            r.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(r, text="⚠", font=ctk.CTkFont(size=11, weight="bold"), text_color=theme.COLOR_WARN, width=16).pack(side="left")
            ctk.CTkLabel(r, text=imp, font=ctk.CTkFont(size=10), text_color=theme.COLOR_TEXT_SECONDARY).pack(side="left", padx=6)

        ctk.CTkFrame(card, height=6, fg_color="transparent").pack()

    def _show_section_error(self, message: str):
        """Renders an elegant, non-intrusive fallback card for an isolated section error."""
        err_card = ctk.CTkFrame(
            self.body,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        err_card.pack(fill="x", pady=4)
        lbl = ctk.CTkLabel(
            err_card,
            text=f"ℹ {message}",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_MUTED
        )
        lbl.pack(anchor="w", padx=16, pady=8)

    # ==========================================================================
    # VALIDATION, CENTERING & INTERACTIONS
    # ==========================================================================

    def _validate_and_finalize(self):
        """Ensures widgets are instantiated, forces layout update, and displays window."""
        try:
            # If body is somehow empty, add emergency status card
            if len(self.body.winfo_children()) == 0:
                self._show_section_error("Session debrief completed.")

            self.update_idletasks()
            self.lift()
            self.focus_force()
            self.after(0, self._center_on_master)
        except Exception as e:
            print(f"[SESSION SUMMARY] Finalize layout note: {e}")

    def _center_on_master(self):
        """Centers the dialog over the master window."""
        try:
            self.update_idletasks()
            master = self.master
            if master and master.winfo_exists():
                mx = master.winfo_x()
                my = master.winfo_y()
                mw = master.winfo_width()
                mh = master.winfo_height()
                w = self.winfo_width()
                h = self.winfo_height()
                x = mx + max(0, (mw - w) // 2)
                y = my + max(0, (mh - h) // 2)
                self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _on_export_clicked(self):
        if self.on_export_report:
            self.on_export_report()
            self.destroy()

    def _on_guide_clicked(self):
        if self.on_review_guide:
            self.on_review_guide()
            self.destroy()
