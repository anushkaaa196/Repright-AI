"""Current Posture vs Ideal Form Comparison Card Component for REPRIGHT AI.

Renders side-by-side technical evaluation contrasting live computer vision observations
against ideal biomechanical targets, highlighting the corrective gap.
"""

from typing import Dict, Any, Optional
import customtkinter as ctk
from ui import theme
from core.form_comparison import get_form_comparison


class FormComparisonCard(ctk.CTkFrame):
    """Side-by-side visual comparison card between live observations and ideal targets."""

    def __init__(self, master, current_exercise: str = "SQUAT", **kwargs):
        super().__init__(
            master,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            **kwargs
        )
        self.current_exercise = current_exercise.upper().strip()
        self.grid_columnconfigure(0, weight=1)

        # ----------------------------------------------------------------------
        # Header Row
        # ----------------------------------------------------------------------
        self.header_row = ctk.CTkFrame(self, fg_color="transparent")
        self.header_row.pack(fill="x", padx=14, pady=(10, 4))

        self.title_lbl = ctk.CTkLabel(
            self.header_row,
            text="CURRENT FORM vs IDEAL FORM",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight=theme.FONT_STAT_TITLE[2]),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.title_lbl.pack(side="left")

        self.status_pill = ctk.CTkLabel(
            self.header_row,
            text="○ READY FOR CHECK",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
            fg_color=theme.COLOR_CARD_INNER,
            text_color=theme.COLOR_TEXT_MUTED,
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.status_pill.pack(side="right")

        # ----------------------------------------------------------------------
        # Comparison Rows
        # ----------------------------------------------------------------------
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="x", padx=14, pady=(2, 10))

        # Row 1: Current AI Observation
        self.obs_title = ctk.CTkLabel(
            self.content_frame,
            text="LIVE AI OBSERVATION",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        )
        self.obs_title.pack(anchor="w", pady=(2, 0))

        self.obs_lbl = ctk.CTkLabel(
            self.content_frame,
            text="Awaiting movement in camera frame.",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=360,
            justify="left"
        )
        self.obs_lbl.pack(anchor="w", pady=(0, 4))

        # Row 2: Ideal Biomechanical Target
        self.target_title = ctk.CTkLabel(
            self.content_frame,
            text="IDEAL BIOMECHANICAL TARGET",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_ACCENT
        )
        self.target_title.pack(anchor="w", pady=(2, 0))

        self.target_lbl = ctk.CTkLabel(
            self.content_frame,
            text="Thighs parallel or slightly below parallel (knee crease <= 100°).",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_SECONDARY,
            wraplength=360,
            justify="left"
        )
        self.target_lbl.pack(anchor="w", pady=(0, 4))

        # Row 3: Gap to Improve
        self.gap_title = ctk.CTkLabel(
            self.content_frame,
            text="CORRECTIVE GAP TO IMPROVE",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_INFO
        )
        self.gap_title.pack(anchor="w", pady=(2, 0))

        self.gap_lbl = ctk.CTkLabel(
            self.content_frame,
            text="Initiate repetition to begin real-time posture analysis.",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=360,
            justify="left"
        )
        self.gap_lbl.pack(anchor="w", pady=(0, 2))

    def update_comparison(
        self,
        exercise_name: str,
        feedback_msg: str,
        feedback_color: Optional[str] = None
    ):
        """Updates comparison items using live feedback."""
        self.current_exercise = exercise_name.upper().strip()
        comp = get_form_comparison(self.current_exercise, feedback_msg, feedback_color)

        self.status_pill.configure(
            text=comp["status_pill"],
            text_color=comp["status_color"],
            fg_color=theme.COLOR_CARD_INNER
        )
        self.obs_lbl.configure(text=comp["current_observation"])
        self.target_lbl.configure(text=comp["ideal_target"])
        self.gap_lbl.configure(text=comp["gap_to_improve"])

    def reset(self):
        """Resets comparison card to initial standby state."""
        self.update_comparison(self.current_exercise, "Tracking posture...", theme.COLOR_TEXT_MUTED)
