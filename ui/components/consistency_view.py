"""Dedicated Movement Consistency Matrix View for REPRIGHT AI.

Displays the 5-dimension repetition consistency heatmap, overall consistency score,
and AI-generated biomechanical stability observations on demand.
"""

from typing import Dict, Any, List, Optional
import customtkinter as ctk
from ui import theme
from ui.components.movement_heatmap import MovementHeatmapFrame
from core.rep_history import RepHistoryTracker


class ConsistencyView(ctk.CTkFrame):
    """Full-featured on-demand movement consistency dashboard."""

    def __init__(self, master, current_exercise: str = "SQUAT", **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )
        self.current_exercise = current_exercise

        # ----------------------------------------------------------------------
        # Header Banner
        # ----------------------------------------------------------------------
        header_card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        header_card.pack(fill="x", padx=16, pady=(12, 8))

        top_row = ctk.CTkFrame(header_card, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(12, 6))

        title_box = ctk.CTkFrame(top_row, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="🔥 MOVEMENT CONSISTENCY MATRIX",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=theme.COLOR_ACCENT
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Biomechanical Execution Variance Across Repetitions",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_SECONDARY
        ).pack(anchor="w")

        # KPI Pills Row
        kpi_row = ctk.CTkFrame(header_card, fg_color="transparent")
        kpi_row.pack(fill="x", padx=16, pady=(4, 12))
        kpi_row.grid_columnconfigure((0, 1, 2), weight=1)

        # 1. Consistency Score
        p1 = ctk.CTkFrame(kpi_row, fg_color=theme.COLOR_CARD_ALT, corner_radius=8, border_width=1, border_color=theme.COLOR_BORDER)
        p1.grid(row=0, column=0, padx=4, sticky="ew")
        ctk.CTkLabel(p1, text="CONSISTENCY SCORE", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(6, 0))
        self.score_lbl = ctk.CTkLabel(p1, text="100%", font=ctk.CTkFont(size=18, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.score_lbl.pack(pady=(0, 6))

        # 2. Status Tier
        p2 = ctk.CTkFrame(kpi_row, fg_color=theme.COLOR_CARD_ALT, corner_radius=8, border_width=1, border_color=theme.COLOR_BORDER)
        p2.grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkLabel(p2, text="EXECUTION TIER", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(6, 0))
        self.tier_lbl = ctk.CTkLabel(p2, text="🟢 HIGHLY CONSISTENT", font=ctk.CTkFont(size=12, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.tier_lbl.pack(pady=(4, 6))

        # 3. Reps Evaluated
        p3 = ctk.CTkFrame(kpi_row, fg_color=theme.COLOR_CARD_ALT, corner_radius=8, border_width=1, border_color=theme.COLOR_BORDER)
        p3.grid(row=0, column=2, padx=4, sticky="ew")
        ctk.CTkLabel(p3, text="REPS EVALUATED", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(6, 0))
        self.reps_lbl = ctk.CTkLabel(p3, text="0 REPS", font=ctk.CTkFont(size=18, weight="bold"), text_color=theme.COLOR_ACCENT)
        self.reps_lbl.pack(pady=(0, 6))

        # ----------------------------------------------------------------------
        # Embedded Heatmap Matrix Container
        # ----------------------------------------------------------------------
        matrix_wrapper = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        matrix_wrapper.pack(fill="both", expand=True, padx=16, pady=4)

        self.heatmap = MovementHeatmapFrame(matrix_wrapper, max_reps=12)
        self.heatmap.pack(fill="both", expand=True, padx=8, pady=8)

        # ----------------------------------------------------------------------
        # AI Biomechanical Observation Card
        # ----------------------------------------------------------------------
        obs_card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        obs_card.pack(fill="x", padx=16, pady=(8, 12))

        ctk.CTkLabel(
            obs_card,
            text="AI BIOMECHANICAL OBSERVATION",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_ACCENT
        ).pack(anchor="w", padx=14, pady=(10, 4))

        self.obs_lbl = ctk.CTkLabel(
            obs_card,
            text="Movement consistency is baseline calibrated. Complete repetitions to evaluate joint alignment and depth variance.",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_PRIMARY,
            justify="left",
            wraplength=650
        )
        self.obs_lbl.pack(anchor="w", padx=14, pady=(0, 10))

    def add_rep(self, rep_analysis: Dict[str, Any]):
        """Adds repetition to the heatmap and updates consistency summary."""
        self.heatmap.add_rep(rep_analysis)
        self._refresh_summary()

    def _refresh_summary(self):
        """Calculates consistency score and dynamic narrative."""
        tracker = RepHistoryTracker.get_instance()
        reps = tracker.get_all_reps()
        count = len(reps)
        self.reps_lbl.configure(text=f"{count} REPS")

        if count == 0:
            self.score_lbl.configure(text="100%", text_color=theme.COLOR_SUCCESS)
            self.tier_lbl.configure(text="🟢 BASELINE CALIBRATED", text_color=theme.COLOR_SUCCESS)
            self.obs_lbl.configure(
                text="Movement consistency is baseline calibrated. Perform repetitions to detect stability variance."
            )
            return

        score = tracker.get_consistency_score()
        col = theme.COLOR_SUCCESS if score >= 85 else (theme.COLOR_WARN if score >= 65 else theme.COLOR_ALERT)
        self.score_lbl.configure(text=f"{score}%", text_color=col)

        if score >= 85:
            tier_text = "🟢 HIGHLY CONSISTENT"
            obs_text = (
                f"Outstanding cadence and joint trajectory stability detected for {self.current_exercise}. "
                "Rep-to-rep biomechanical variance remained within the 5% optimal threshold."
            )
        elif score >= 65:
            tier_text = "🟡 MODERATE VARIANCE"
            obs_text = (
                f"Movement consistency remained acceptable during early repetitions. "
                "Minor stability and depth variances emerged in later movement cycles."
            )
        else:
            tier_text = "🔴 HIGH VARIANCE"
            obs_text = (
                f"Elevated movement inconsistency observed across repetitions. "
                "Focus on a strict 2-second eccentric cadence and controlled joint turnaround."
            )

        self.tier_lbl.configure(text=tier_text, text_color=col)
        self.obs_lbl.configure(text=obs_text)

    def set_exercise(self, exercise_name: str):
        """Switches current exercise."""
        self.current_exercise = exercise_name
        self._refresh_summary()

    def reset(self):
        """Resets heatmap and metrics to baseline."""
        self.heatmap.reset()
        self._refresh_summary()
