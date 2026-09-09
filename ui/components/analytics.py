"""Live Session Performance Analytics Component for REPRIGHT AI (Phase 7).

Displays a streamlined, clutter-free Compact Session Overview dock on the main dashboard:
- Card 1: SESSION FORM SCORE (Score % + Status Tier)
- Card 2: CLEAN REPS (Clean count, total attempts, success rate)
- Card 3: AI MOVEMENT STATUS (Stability & risk awareness indicators)
- Card 4: ADVANCED ANALYTICS (Direct launcher button for the Analytics Hub)

Advanced charts (Heatmap, Rep Timeline, Breakdown) are moved into the on-demand Analytics Hub.
"""

from typing import Dict, Any, List, Optional, Callable
import tkinter as tk
import customtkinter as ctk
from ui import theme
from ui.components.rep_timeline import RepTimelineFrame
from ui.components.performance_breakdown import PerformanceBreakdownFrame
from ui.components.movement_heatmap import MovementHeatmapFrame


class LiveAnalyticsFrame(ctk.CTkFrame):
    """Compact 4-card session overview dock with launcher for on-demand analytics."""

    def __init__(
        self,
        master,
        on_open_analytics: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=14,
            fg_color=theme.COLOR_PANEL_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            height=92,
            **kwargs
        )
        self.on_open_analytics = on_open_analytics

        # Single row with 4 uniform columns
        self.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="analytics_card")
        self.grid_rowconfigure(0, weight=1)

        # ======================================================================
        # CARD 1: SESSION FORM SCORE (Emerald Accent Strip)
        # ======================================================================
        self.score_card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        self.score_card.grid(row=0, column=0, padx=(10, 5), pady=8, sticky="nsew")

        # Top Accent Strip (Emerald)
        ctk.CTkFrame(
            self.score_card,
            height=3,
            corner_radius=2,
            fg_color=theme.COLOR_SUCCESS
        ).pack(fill="x", padx=4, pady=(3, 0))

        ctk.CTkLabel(
            self.score_card,
            text="SESSION FORM SCORE",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=12, pady=(4, 0))

        score_row = ctk.CTkFrame(self.score_card, fg_color="transparent")
        score_row.pack(fill="x", padx=12, pady=(0, 4))

        self.score_val = ctk.CTkLabel(
            score_row,
            text="100%",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=theme.COLOR_SUCCESS
        )
        self.score_val.pack(side="left")

        self.session_tier = ctk.CTkLabel(
            score_row,
            text="● EXCELLENT",
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=theme.COLOR_SUCCESS_MUTED,
            text_color=theme.COLOR_SUCCESS,
            corner_radius=4,
            padx=6,
            pady=1
        )
        self.session_tier.pack(side="left", padx=(8, 0))

        # ======================================================================
        # CARD 2: CLEAN REPETITIONS (Teal Accent Strip)
        # ======================================================================
        self.rep_card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        self.rep_card.grid(row=0, column=1, padx=5, pady=8, sticky="nsew")

        # Top Accent Strip (Deep Teal)
        ctk.CTkFrame(
            self.rep_card,
            height=3,
            corner_radius=2,
            fg_color=theme.COLOR_TEAL
        ).pack(fill="x", padx=4, pady=(3, 0))

        ctk.CTkLabel(
            self.rep_card,
            text="CLEAN REPS",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=12, pady=(4, 0))

        rep_row = ctk.CTkFrame(self.rep_card, fg_color="transparent")
        rep_row.pack(fill="x", padx=12, pady=(0, 4))

        self.valid_reps_lbl = ctk.CTkLabel(
            rep_row,
            text="0",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=theme.COLOR_TEAL
        )
        self.valid_reps_lbl.pack(side="left")

        self.attempts_lbl = ctk.CTkLabel(
            rep_row,
            text=" / 0 ATTEMPTS",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        self.attempts_lbl.pack(side="left", padx=(4, 0))

        self.success_rate_lbl = ctk.CTkLabel(
            self.rep_card,
            text="Success Rate: 100%",
            font=ctk.CTkFont(size=9),
            text_color=theme.COLOR_TEXT_MUTED
        )
        self.success_rate_lbl.pack(anchor="w", padx=12, pady=(0, 6))

        # ======================================================================
        # CARD 3: AI MOVEMENT STATUS (Blue Accent Strip)
        # ======================================================================
        self.status_card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        self.status_card.grid(row=0, column=2, padx=5, pady=8, sticky="nsew")

        # Top Accent Strip (Professional Blue)
        ctk.CTkFrame(
            self.status_card,
            height=3,
            corner_radius=2,
            fg_color=theme.COLOR_BLUE
        ).pack(fill="x", padx=4, pady=(3, 0))

        ctk.CTkLabel(
            self.status_card,
            text="CURRENT MOVEMENT STATUS",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=12, pady=(4, 0))

        status_row = ctk.CTkFrame(self.status_card, fg_color="transparent")
        status_row.pack(fill="x", padx=12, pady=(2, 2))

        self.status_stab_lbl = ctk.CTkLabel(
            status_row,
            text="● STABLE FORM",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme.COLOR_SUCCESS
        )
        self.status_stab_lbl.pack(side="left")

        self.status_risk_lbl = ctk.CTkLabel(
            status_row,
            text="• LOW RISK",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        self.status_risk_lbl.pack(side="left", padx=(6, 0))

        self.status_detail_lbl = ctk.CTkLabel(
            self.status_card,
            text="Kinematic trajectory within optimal tolerance.",
            font=ctk.CTkFont(size=9),
            text_color=theme.COLOR_TEXT_MUTED
        )
        self.status_detail_lbl.pack(anchor="w", padx=12, pady=(0, 6))

        # ======================================================================
        # CARD 4: ADVANCED ANALYTICS LAUNCHER (Amber Accent Strip)
        # ======================================================================
        self.launcher_card = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        self.launcher_card.grid(row=0, column=3, padx=(5, 10), pady=8, sticky="nsew")

        # Top Accent Strip (Warm Amber)
        ctk.CTkFrame(
            self.launcher_card,
            height=3,
            corner_radius=2,
            fg_color=theme.COLOR_WARN
        ).pack(fill="x", padx=4, pady=(3, 0))

        ctk.CTkLabel(
            self.launcher_card,
            text="ADVANCED ANALYTICS",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=12, pady=(4, 2))

        self.btn_open_analytics = ctk.CTkButton(
            self.launcher_card,
            text="VIEW ANALYTICS →",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=30,
            corner_radius=6,
            fg_color=theme.COLOR_BTN_EXPORT,
            hover_color=theme.COLOR_BTN_EXPORT_HOVER,
            text_color=theme.COLOR_WHITE,
            command=self._handle_open_analytics
        )
        self.btn_open_analytics.pack(fill="x", padx=10, pady=(2, 4))

        ctk.CTkLabel(
            self.launcher_card,
            text="Consistency Matrix & Rep Breakdown",
            font=ctk.CTkFont(size=8),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=12, pady=(0, 4))

        # ======================================================================
        # INTERNAL HEADLESS WIDGETS (Maintained for Backward Compatibility)
        # ======================================================================
        # These are stored internally without cluttering the main screen.
        self._internal_container = ctk.CTkFrame(self)
        self.rep_timeline = RepTimelineFrame(self._internal_container)
        self.breakdown = PerformanceBreakdownFrame(self._internal_container)
        self.movement_heatmap = MovementHeatmapFrame(self._internal_container)
        self.trend_canvas = tk.Canvas(self._internal_container)
        self.rep_progress = ctk.CTkProgressBar(self._internal_container)
        self.depth_diag = ctk.CTkLabel(self._internal_container, text="")
        self.torso_diag = ctk.CTkLabel(self._internal_container, text="")
        self.faults_diag = ctk.CTkLabel(self._internal_container, text="")

    def _handle_open_analytics(self):
        """Dispatches on-demand analytics view request."""
        if self.on_open_analytics:
            self.on_open_analytics()

    def add_rep_to_timeline(self, rep_analysis: Dict[str, Any]):
        """Appends a completed repetition to internal records."""
        self.rep_timeline.add_rep(rep_analysis)
        self.movement_heatmap.add_rep(rep_analysis)

    def update_breakdown(self, dimension_averages: Dict[str, int], exercise_name: str = "SQUAT"):
        """Updates internal biomechanical dimension averages."""
        self.breakdown.update_breakdown(dimension_averages, exercise_name)

    def set_exercise(self, exercise_name: str):
        """Switches active exercise."""
        self.breakdown.set_exercise(exercise_name)

    def reset_phase5(self):
        """Resets Phase 5 telemetry."""
        self.rep_timeline.reset()
        self.breakdown.reset()
        self.movement_heatmap.reset()

    def reset_phase6(self):
        """Resets Phase 6 heatmap."""
        self.movement_heatmap.reset()

    def update_analytics(self, stats: Dict[str, Any], exercise_name: str = "SQUAT"):
        """Updates compact overview cards with real-time stats."""
        reps = stats.get("clean_reps", 0)
        total = stats.get("total_attempts", 0)
        acc = int(stats.get("accuracy", 100))

        # 1. Update Score & Tier
        self.score_val.configure(text=f"{acc}%")
        if acc >= 90:
            score_color = theme.COLOR_SUCCESS
            tier_text = "● EXCELLENT"
            tier_bg = theme.COLOR_SUCCESS_MUTED
        elif acc >= 75:
            score_color = theme.COLOR_ACCENT
            tier_text = "● GOOD"
            tier_bg = theme.COLOR_ACCENT_MUTED
        elif acc >= 50:
            score_color = theme.COLOR_WARN
            tier_text = "● MODERATE"
            tier_bg = theme.COLOR_WARN_MUTED
        else:
            score_color = theme.COLOR_ALERT
            tier_text = "● CORRECTION"
            tier_bg = theme.COLOR_ALERT_MUTED

        self.score_val.configure(text_color=score_color)
        self.session_tier.configure(text=tier_text, text_color=score_color, fg_color=tier_bg)

        # 2. Update Clean Reps & Total Attempts
        self.valid_reps_lbl.configure(text=str(reps))
        self.attempts_lbl.configure(text=f" / {total} ATTEMPTS")
        success_rate = int((reps / max(total, 1)) * 100) if total > 0 else 100
        self.success_rate_lbl.configure(text=f"Success Rate: {success_rate}%")

        # 3. Maintain headless diagnostics for backward compatibility
        if exercise_name == "BICEP_CURL":
            left_reps = stats.get("left_arm_reps", 0)
            right_reps = stats.get("right_arm_reps", 0)
            self.depth_diag.configure(text=f"Left: {left_reps} | Right: {right_reps}")
        else:
            self.depth_diag.configure(text=f"Depth Fails: {stats.get('failed_depth', 0)}")

    def update_status_indicators(
        self,
        stability_data: Optional[Dict[str, Any]] = None,
        risk_data: Optional[Dict[str, Any]] = None,
        fatigue_data: Optional[Dict[str, Any]] = None
    ):
        """Updates the AI status indicators on Card 3."""
        if stability_data:
            cat = stability_data.get("category", "🟢 HIGHLY STABLE")
            self.status_stab_lbl.configure(text=cat)
        if risk_data:
            risk_cat = risk_data.get("risk_category", "🟢 LOW RISK")
            short_risk = "LOW RISK" if "LOW" in risk_cat else ("MODERATE" if "MODERATE" in risk_cat else "ATTENTION")
            self.status_risk_lbl.configure(text=f"• {short_risk}")
        if fatigue_data:
            rec = fatigue_data.get("recommendation", "Kinematic trajectory within optimal tolerance.")
            self.status_detail_lbl.configure(text=rec)

    def reset_analytics(self):
        """Resets compact session overview to baseline values."""
        self.score_val.configure(text="100%", text_color=theme.COLOR_SUCCESS)
        self.session_tier.configure(
            text="● EXCELLENT",
            text_color=theme.COLOR_SUCCESS,
            fg_color=theme.COLOR_SUCCESS_MUTED
        )
        self.valid_reps_lbl.configure(text="0")
        self.attempts_lbl.configure(text=" / 0 ATTEMPTS")
        self.success_rate_lbl.configure(text="Success Rate: 100%")
        self.status_stab_lbl.configure(text="● STABLE FORM", text_color=theme.COLOR_SUCCESS)
        self.status_risk_lbl.configure(text="• LOW RISK", text_color=theme.COLOR_TEXT_SECONDARY)
        self.status_detail_lbl.configure(text="Kinematic trajectory within optimal tolerance.")
        self.reset_phase5()
