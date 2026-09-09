"""Advanced Performance Analytics Hub for REPRIGHT AI (Phase 7).

Dedicated on-demand modal window providing a tabbed analytics interface:
- Tab 1: OVERVIEW (KPIs, Session Form Score, Success Rate, Readiness)
- Tab 2: REP PERFORMANCE (Rep-by-rep progression timeline)
- Tab 3: BIOMECHANICS (5-dimension joint kinematics breakdown)
- Tab 4: MOVEMENT CONSISTENCY (Consistency matrix heatmap + AI observation)
- Tab 5: FORM TREND (Dynamic form trajectory & accuracy trendline)
- Tab 6: AI INTELLIGENCE (Stability, Fatigue, Risk, Adaptive Coach, Recovery)
"""

from typing import Dict, Any, List, Optional, Callable
import customtkinter as ctk
from ui import theme
from ui.components.analytics_navigation import AnalyticsNavBar, ANALYTICS_TABS
from ui.components.rep_timeline import RepTimelineFrame
from ui.components.performance_breakdown import PerformanceBreakdownFrame
from ui.components.consistency_view import ConsistencyView
from ui.components.trend_view import TrendView
from core.rep_history import RepHistoryTracker
from core.exercise_registry import is_guided_exercise


class AnalyticsHubDialog(ctk.CTkToplevel):
    """Clean on-demand modal window for detailed workout biomechanics and analytics."""

    def __init__(
        self,
        master,
        current_exercise: str = "SQUAT",
        initial_tab: str = "OVERVIEW",
        stats: Optional[Dict[str, Any]] = None,
        on_export_report: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.current_exercise = current_exercise
        self.stats = stats or {}
        self.on_export_report = on_export_report

        # Configure window
        self.title("REPRIGHT AI — Advanced Performance Analytics")
        self.geometry("880x640")
        self.minsize(800, 580)
        self.configure(fg_color=theme.COLOR_BG)

        # Ensure dialog floats above master and grabs focus gracefully
        self.transient(master)
        self.after(100, self.lift)

        # ----------------------------------------------------------------------
        # Top Header Bar
        # ----------------------------------------------------------------------
        self.header = ctk.CTkFrame(self, fg_color=theme.COLOR_PANEL_BG, corner_radius=0, height=60)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        top_left = ctk.CTkFrame(self.header, fg_color="transparent")
        top_left.pack(side="left", padx=18, pady=10)

        badge_frame = ctk.CTkFrame(top_left, fg_color="transparent")
        badge_frame.pack(anchor="w")

        ctk.CTkLabel(
            badge_frame,
            text="AI BIOMECHANICS CORE",
            font=ctk.CTkFont(size=theme.FONT_BRAND_BADGE[1], weight="bold"),
            text_color=theme.COLOR_ACCENT,
            fg_color=theme.COLOR_ACCENT_MUTED,
            corner_radius=4,
            height=18,
            padx=6
        ).pack(side="left")

        self.ex_badge = ctk.CTkLabel(
            badge_frame,
            text=f"EXERCISE: {self.current_exercise}",
            font=ctk.CTkFont(size=theme.FONT_BRAND_BADGE[1], weight="bold"),
            text_color=theme.COLOR_SUCCESS,
            fg_color=theme.COLOR_SUCCESS_MUTED,
            corner_radius=4,
            height=18,
            padx=6
        )
        self.ex_badge.pack(side="left", padx=(6, 0))

        ctk.CTkLabel(
            top_left,
            text="ADVANCED PERFORMANCE ANALYTICS",
            font=ctk.CTkFont(size=theme.FONT_VIEWPORT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        ).pack(anchor="w", pady=(2, 0))

        # Close button in header
        ctk.CTkButton(
            self.header,
            text="✕",
            width=32,
            height=32,
            corner_radius=6,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_DANGER_HOVER,
            text_color=theme.COLOR_WHITE,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.destroy
        ).pack(side="right", padx=16, pady=14)

        # ----------------------------------------------------------------------
        # Tab Navigation Strip
        # ----------------------------------------------------------------------
        self.nav_bar = AnalyticsNavBar(
            self,
            on_tab_selected=self._on_tab_selected,
            initial_tab=initial_tab
        )
        self.nav_bar.pack(fill="x", padx=16, pady=(10, 6))

        # ----------------------------------------------------------------------
        # Central Content Area
        # ----------------------------------------------------------------------
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True, padx=16, pady=(0, 6))

        # Tab instances dictionary
        self.tab_frames: Dict[str, ctk.CTkFrame] = {}
        self._build_all_tabs()

        # Activate requested tab
        self._on_tab_selected(initial_tab)

        # ----------------------------------------------------------------------
        # Bottom Action Bar
        # ----------------------------------------------------------------------
        self.footer = ctk.CTkFrame(self, fg_color=theme.COLOR_PANEL_BG, corner_radius=0, height=48)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)

        ctk.CTkLabel(
            self.footer,
            text="REPRIGHT AI • 60 FPS Pose Trigonometry • Smart India Hackathon Presentation Edition",
            font=ctk.CTkFont(size=theme.FONT_FOOTER[1]),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(side="left", padx=18)

        btn_row = ctk.CTkFrame(self.footer, fg_color="transparent")
        btn_row.pack(side="right", padx=16)

        if self.on_export_report:
            ctk.CTkButton(
                btn_row,
                text="📥 EXPORT REPORT",
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
                fg_color=theme.COLOR_INFO,
                hover_color=theme.COLOR_INFO_HOVER,
                text_color=theme.COLOR_WHITE,
                height=30,
                corner_radius=6,
                command=self.on_export_report
            ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row,
            text="CLOSE",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
            fg_color=theme.COLOR_SECONDARY_BTN,
            hover_color=theme.COLOR_BORDER_LIGHT,
            text_color=theme.COLOR_TEXT_SECONDARY,
            height=30,
            corner_radius=6,
            command=self.destroy
        ).pack(side="left", padx=4)

    # ==========================================================================
    # TAB BUILDERS
    # ==========================================================================
    def _build_all_tabs(self):
        """Constructs all 6 analytical section views."""
        self._build_tab_overview()
        self._build_tab_rep_performance()
        self._build_tab_biomechanics()
        self._build_tab_movement_consistency()
        self._build_tab_form_trend()
        self._build_tab_ai_intelligence()

    def _build_tab_overview(self):
        """TAB 1: High-level KPI overview and session metrics."""
        f = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        self.tab_frames["OVERVIEW"] = f

        # Exercise specific focus header
        self.overview_focus_card = ctk.CTkFrame(
            f,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        self.overview_focus_card.pack(fill="x", pady=(0, 10))

        self.overview_focus_lbl = ctk.CTkLabel(
            self.overview_focus_card,
            text=self._get_exercise_focus_description(),
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme.COLOR_ACCENT
        )
        self.overview_focus_lbl.pack(anchor="w", padx=16, pady=10)

        # 4 Key Metric Cards (Row 1)
        row1 = ctk.CTkFrame(f, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 8))
        row1.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # 1. Form Score
        c1 = ctk.CTkFrame(row1, fg_color=theme.COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=theme.COLOR_BORDER)
        c1.grid(row=0, column=0, padx=4, sticky="ew")
        ctk.CTkLabel(c1, text="SESSION FORM SCORE", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(10, 0))
        self.ov_score_val = ctk.CTkLabel(c1, text="100%", font=ctk.CTkFont(size=22, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.ov_score_val.pack(pady=(0, 2))
        self.ov_score_tier = ctk.CTkLabel(c1, text="🟢 EXCELLENT", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.ov_score_tier.pack(pady=(0, 10))

        # 2. Clean Reps & Total Attempts
        c2 = ctk.CTkFrame(row1, fg_color=theme.COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=theme.COLOR_BORDER)
        c2.grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkLabel(c2, text="CLEAN REPETITIONS", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(10, 0))
        self.ov_reps_val = ctk.CTkLabel(c2, text="0 / 0", font=ctk.CTkFont(size=22, weight="bold"), text_color=theme.COLOR_ACCENT)
        self.ov_reps_val.pack(pady=(0, 2))
        self.ov_reps_sub = ctk.CTkLabel(c2, text="TOTAL ATTEMPTS: 0", font=ctk.CTkFont(size=9), text_color=theme.COLOR_TEXT_SECONDARY)
        self.ov_reps_sub.pack(pady=(0, 10))

        # 3. Success Rate
        c3 = ctk.CTkFrame(row1, fg_color=theme.COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=theme.COLOR_BORDER)
        c3.grid(row=0, column=2, padx=4, sticky="ew")
        ctk.CTkLabel(c3, text="SUCCESS RATE", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(10, 0))
        self.ov_succ_val = ctk.CTkLabel(c3, text="100%", font=ctk.CTkFont(size=22, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.ov_succ_val.pack(pady=(0, 2))
        ctk.CTkLabel(c3, text="CLEAN VS FAILED RATIO", font=ctk.CTkFont(size=9), text_color=theme.COLOR_TEXT_SECONDARY).pack(pady=(0, 10))

        # 4. Movement Stability
        c4 = ctk.CTkFrame(row1, fg_color=theme.COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=theme.COLOR_BORDER)
        c4.grid(row=0, column=3, padx=4, sticky="ew")
        ctk.CTkLabel(c4, text="CURRENT STABILITY", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(10, 0))
        self.ov_stab_val = ctk.CTkLabel(c4, text="95%", font=ctk.CTkFont(size=22, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.ov_stab_val.pack(pady=(0, 2))
        self.ov_stab_tier = ctk.CTkLabel(c4, text="🟢 HIGHLY STABLE", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.ov_stab_tier.pack(pady=(0, 10))

        # Diagnostics & Fatigue Overview (Row 2)
        row2 = ctk.CTkFrame(f, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 8))
        row2.grid_columnconfigure((0, 1), weight=1)

        d1 = ctk.CTkFrame(row2, fg_color=theme.COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=theme.COLOR_BORDER)
        d1.grid(row=0, column=0, padx=4, sticky="nsew")
        ctk.CTkLabel(d1, text="MOVEMENT DIAGNOSTICS", font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 4))
        self.ov_depth_diag = ctk.CTkLabel(d1, text="✓ Depth / ROM: OPTIMAL", font=ctk.CTkFont(size=11), text_color=theme.COLOR_SUCCESS)
        self.ov_depth_diag.pack(anchor="w", padx=14, pady=2)
        self.ov_align_diag = ctk.CTkLabel(d1, text="✓ Joint Alignment: STABLE", font=ctk.CTkFont(size=11), text_color=theme.COLOR_SUCCESS)
        self.ov_align_diag.pack(anchor="w", padx=14, pady=2)
        self.ov_warn_diag = ctk.CTkLabel(d1, text="✓ Posture Warnings: 0 Detected", font=ctk.CTkFont(size=11), text_color=theme.COLOR_TEXT_MUTED)
        self.ov_warn_diag.pack(anchor="w", padx=14, pady=(2, 10))

        d2 = ctk.CTkFrame(row2, fg_color=theme.COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=theme.COLOR_BORDER)
        d2.grid(row=0, column=1, padx=4, sticky="nsew")
        ctk.CTkLabel(d2, text="FATIGUE & RISK AWARENESS", font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(anchor="w", padx=14, pady=(10, 4))
        self.ov_fatigue_lbl = ctk.CTkLabel(d2, text="🟢 Form Fatigue: LOW (0%)", font=ctk.CTkFont(size=11), text_color=theme.COLOR_SUCCESS)
        self.ov_fatigue_lbl.pack(anchor="w", padx=14, pady=2)
        self.ov_risk_lbl = ctk.CTkLabel(d2, text="🟢 Risk Awareness: LOW RISK", font=ctk.CTkFont(size=11), text_color=theme.COLOR_SUCCESS)
        self.ov_risk_lbl.pack(anchor="w", padx=14, pady=2)
        self.ov_rec_lbl = ctk.CTkLabel(d2, text="Recovery Status: CONTINUE TRAINING", font=ctk.CTkFont(size=11), text_color=theme.COLOR_ACCENT)
        self.ov_rec_lbl.pack(anchor="w", padx=14, pady=(2, 10))

    def _build_tab_rep_performance(self):
        """TAB 2: Repetition timeline and rep-by-rep progression."""
        f = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tab_frames["REP_PERFORMANCE"] = f

        self.rep_timeline = RepTimelineFrame(f)
        self.rep_timeline.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_tab_biomechanics(self):
        """TAB 3: Biomechanical Quality Breakdown."""
        f = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tab_frames["BIOMECHANICS"] = f

        self.breakdown = PerformanceBreakdownFrame(f)
        self.breakdown.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_tab_movement_consistency(self):
        """TAB 4: Dedicated Movement Consistency Matrix."""
        f = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tab_frames["MOVEMENT_CONSISTENCY"] = f

        self.consistency_view = ConsistencyView(f, current_exercise=self.current_exercise)
        self.consistency_view.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_tab_form_trend(self):
        """TAB 5: Form Quality Trendline Canvas."""
        f = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tab_frames["FORM_TREND"] = f

        self.trend_view = TrendView(f)
        self.trend_view.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_tab_ai_intelligence(self):
        """TAB 6: Unified Phase 6 Motion Intelligence Panel."""
        f = ctk.CTkScrollableFrame(self.content_container, fg_color="transparent")
        self.tab_frames["AI_INTELLIGENCE"] = f

        # Row 1: Stability & Fatigue
        row1 = ctk.CTkFrame(f, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        row1.grid_columnconfigure((0, 1), weight=1)

        # Movement Stability Card
        stab_card = ctk.CTkFrame(row1, fg_color=theme.COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=theme.COLOR_BORDER)
        stab_card.grid(row=0, column=0, padx=4, sticky="nsew")
        ctk.CTkLabel(stab_card, text="MOVEMENT STABILITY", font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"), text_color=theme.COLOR_ACCENT).pack(anchor="w", padx=14, pady=(10, 2))
        self.intel_stab_score = ctk.CTkLabel(stab_card, text="95%", font=ctk.CTkFont(size=20, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.intel_stab_score.pack(anchor="w", padx=14)
        self.intel_stab_bar = ctk.CTkProgressBar(stab_card, height=8, corner_radius=4, fg_color=theme.COLOR_CARD_INNER, progress_color=theme.COLOR_SUCCESS)
        self.intel_stab_bar.pack(fill="x", padx=14, pady=(4, 6))
        self.intel_stab_bar.set(0.95)
        self.intel_stab_desc = ctk.CTkLabel(stab_card, text="🟢 HIGHLY STABLE (Jitter: 12.4)", font=ctk.CTkFont(size=10), text_color=theme.COLOR_TEXT_SECONDARY)
        self.intel_stab_desc.pack(anchor="w", padx=14, pady=(0, 10))

        # Form Fatigue Card
        fat_card = ctk.CTkFrame(row1, fg_color=theme.COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=theme.COLOR_BORDER)
        fat_card.grid(row=0, column=1, padx=4, sticky="nsew")
        ctk.CTkLabel(fat_card, text="FORM FATIGUE LEVEL", font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"), text_color=theme.COLOR_ACCENT).pack(anchor="w", padx=14, pady=(10, 2))
        self.intel_fat_score = ctk.CTkLabel(fat_card, text="LOW (0%)", font=ctk.CTkFont(size=20, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.intel_fat_score.pack(anchor="w", padx=14)
        self.intel_fat_bar = ctk.CTkProgressBar(fat_card, height=8, corner_radius=4, fg_color=theme.COLOR_CARD_INNER, progress_color=theme.COLOR_SUCCESS)
        self.intel_fat_bar.pack(fill="x", padx=14, pady=(4, 6))
        self.intel_fat_bar.set(0.0)
        self.intel_fat_desc = ctk.CTkLabel(fat_card, text="Movement quality remains high. Continue steady execution.", font=ctk.CTkFont(size=10), text_color=theme.COLOR_TEXT_SECONDARY)
        self.intel_fat_desc.pack(anchor="w", padx=14, pady=(0, 10))

        # Row 2: Adaptive Coaching & Recovery
        row2 = ctk.CTkFrame(f, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 10))
        row2.grid_columnconfigure((0, 1), weight=1)

        # Adaptive Coach
        coach_card = ctk.CTkFrame(row2, fg_color=theme.COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=theme.COLOR_BORDER)
        coach_card.grid(row=0, column=0, padx=4, sticky="nsew")
        ctk.CTkLabel(coach_card, text="ADAPTIVE AI COACH", font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"), text_color=theme.COLOR_ACCENT).pack(anchor="w", padx=14, pady=(10, 4))
        self.intel_coach_txt = ctk.CTkLabel(
            coach_card,
            text="Maintain controlled movement and neutral alignment through your concentric drive.",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_PRIMARY,
            justify="left",
            wraplength=340
        )
        self.intel_coach_txt.pack(anchor="w", padx=14, pady=(0, 10))

        # Recovery Protocol
        rec_card = ctk.CTkFrame(row2, fg_color=theme.COLOR_CARD_BG, corner_radius=10, border_width=1, border_color=theme.COLOR_BORDER)
        rec_card.grid(row=0, column=1, padx=4, sticky="nsew")
        ctk.CTkLabel(rec_card, text="RECOVERY PROTOCOL", font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"), text_color=theme.COLOR_ACCENT).pack(anchor="w", padx=14, pady=(10, 4))
        self.intel_rec_txt = ctk.CTkLabel(
            rec_card,
            text="🟢 CONTINUE TRAINING — Muscles are operating within safe physiological tolerance limits.",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_SUCCESS,
            justify="left",
            wraplength=340
        )
        self.intel_rec_txt.pack(anchor="w", padx=14, pady=(0, 10))

    # ==========================================================================
    # NAVIGATION & SYNCHRONIZATION
    # ==========================================================================
    def _on_tab_selected(self, tab_key: str):
        """Displays selected tab while hiding all others."""
        for k, frame in self.tab_frames.items():
            if k == tab_key:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    def select_tab(self, tab_key: str):
        """Public method to change active tab."""
        self.nav_bar.set_active_tab(tab_key)

    def _get_exercise_focus_description(self) -> str:
        """Returns exercise-specific focus headline."""
        if is_guided_exercise(self.current_exercise):
            return f"📘 GUIDED EXERCISE: Reference Biomechanical Target Criteria for {self.current_exercise}"
        if self.current_exercise == "SQUAT":
            return "🦵 SQUAT BIOMECHANICS: Knee Valgus Prevention, Parallel Hip Depth & Torso Stability"
        elif self.current_exercise == "DEADLIFT":
            return "🦴 DEADLIFT BIOMECHANICS: Neutral Lumbar Spine, Lat Engagement & Bar Path Verticality"
        elif self.current_exercise == "BICEP_CURL":
            return "💪 BICEP CURL BIOMECHANICS: Elbow Pinning, Supination Control & Minimal Torso Sway"
        return f"🎯 {self.current_exercise} BIOMECHANICAL ANALYSIS"

    def set_exercise(self, exercise_name: str):
        """Updates exercise badge, focus descriptions, and consistency context."""
        self.current_exercise = exercise_name
        self.ex_badge.configure(text=f"EXERCISE: {self.current_exercise}")
        self.overview_focus_lbl.configure(text=self._get_exercise_focus_description())
        self.consistency_view.set_exercise(exercise_name)

    def sync_telemetry(
        self,
        stats: Dict[str, Any],
        stability_data: Optional[Dict[str, Any]] = None,
        fatigue_data: Optional[Dict[str, Any]] = None,
        risk_data: Optional[Dict[str, Any]] = None,
        coach_data: Optional[Dict[str, Any]] = None,
        recovery_data: Optional[Dict[str, Any]] = None
    ):
        """Synchronizes live session telemetry to overview and intelligence tabs."""
        self.stats = stats
        clean_reps = stats.get("clean_reps", 0)
        attempts = stats.get("total_attempts", 0)
        acc = stats.get("form_accuracy", 100)

        # Overview Tab Updates
        col = theme.COLOR_SUCCESS if acc >= 80 else (theme.COLOR_WARN if acc >= 50 else theme.COLOR_ALERT)
        self.ov_score_val.configure(text=f"{acc}%", text_color=col)
        tier_text = "🟢 EXCELLENT" if acc >= 85 else ("🟡 MODERATE" if acc >= 60 else "🔴 ATTENTION")
        self.ov_score_tier.configure(text=tier_text, text_color=col)

        self.ov_reps_val.configure(text=f"{clean_reps} / {attempts}")
        self.ov_reps_sub.configure(text=f"TOTAL ATTEMPTS: {attempts}")

        succ_rate = int((clean_reps / max(1, attempts)) * 100) if attempts > 0 else 100
        self.ov_succ_val.configure(text=f"{succ_rate}%")

        # Diagnostics
        depth_fails = stats.get("depth_fails", 0)
        posture_warns = stats.get("posture_warnings", 0)
        sitting_fails = stats.get("sitting_fails", 0)

        if depth_fails > 0:
            self.ov_depth_diag.configure(text=f"⚠ Depth Control: {depth_fails} FAILS", text_color=theme.COLOR_ALERT)
        else:
            self.ov_depth_diag.configure(text="✓ Depth / ROM: OPTIMAL", text_color=theme.COLOR_SUCCESS)

        if sitting_fails > 0:
            self.ov_align_diag.configure(text=f"⚠ Torso Alignment: {sitting_fails} FAULTS", text_color=theme.COLOR_ALERT)
        else:
            self.ov_align_diag.configure(text="✓ Torso Alignment: STABLE", text_color=theme.COLOR_SUCCESS)

        self.ov_warn_diag.configure(text=f"✓ Posture Warnings: {posture_warns} Detected")

        # Stability sync
        if stability_data:
            stab_score = stability_data.get("stability_score", 95)
            self.ov_stab_val.configure(text=f"{stab_score}%")
            stab_cat = stability_data.get("category", "🟢 HIGHLY STABLE")
            self.ov_stab_tier.configure(text=stab_cat)
            self.intel_stab_score.configure(text=f"{stab_score}%")
            self.intel_stab_bar.set(float(stab_score) / 100.0)
            self.intel_stab_desc.configure(text=f"{stab_cat} (Jitter: {stability_data.get('jitter_score', 0):.1f})")

        # Fatigue sync
        if fatigue_data:
            fat_score = fatigue_data.get("fatigue_score", 0)
            fat_cat = fatigue_data.get("category", "🟢 LOW FORM FATIGUE")
            self.ov_fatigue_lbl.configure(text=f"Form Fatigue: {fat_cat} ({fat_score}%)")
            self.intel_fat_score.configure(text=f"{fat_cat} ({fat_score}%)")
            self.intel_fat_bar.set(float(fat_score) / 100.0)
            self.intel_fat_desc.configure(text=fatigue_data.get("recommendation", "Movement quality high."))

        # Risk sync
        if risk_data:
            risk_cat = risk_data.get("risk_category", "🟢 LOW RISK")
            self.ov_risk_lbl.configure(text=f"Risk Awareness: {risk_cat}")

        # Coach sync
        if coach_data:
            msg = coach_data.get("message", "Maintain controlled movement.")
            self.intel_coach_txt.configure(text=msg)

        # Recovery sync
        if recovery_data:
            rec_status = recovery_data.get("status", "🟢 CONTINUE TRAINING")
            self.ov_rec_lbl.configure(text=f"Recovery Status: {rec_status}")
            self.intel_rec_txt.configure(text=f"{rec_status} — {recovery_data.get('action', 'Safe.')}")

    def add_rep(self, rep_analysis: Dict[str, Any]):
        """Forwards completed repetition to all relevant analytical sub-views."""
        self.rep_timeline.add_rep(rep_analysis)
        self.consistency_view.add_rep(rep_analysis)
        score = rep_analysis.get("score", 100)
        self.trend_view.add_point(score)

    def update_breakdown(self, dimension_averages: Dict[str, int], exercise_name: str = "SQUAT"):
        """Forwards biomechanical breakdown updates."""
        self.breakdown.update_breakdown(dimension_averages, exercise_name)

    def reset_analytics(self):
        """Resets all tabs to baseline state."""
        self.rep_timeline.reset()
        self.breakdown.reset()
        self.consistency_view.reset()
        self.trend_view.reset()
        self.sync_telemetry({"clean_reps": 0, "total_attempts": 0, "form_accuracy": 100})
