"""Session Goal & Challenge Card Component for REPRIGHT AI.

Displays active workout goals, live repetition progress bars, and achievement badges.
"""

from typing import Dict, Any, Optional
import customtkinter as ctk
from ui import theme
from core.session_goals import evaluate_goal_progress


class SessionGoalCard(ctk.CTkFrame):
    """Visual challenge and milestone progress card."""

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
        self.header_row.pack(fill="x", padx=14, pady=(10, 2))

        self.title_lbl = ctk.CTkLabel(
            self.header_row,
            text="🎯 TODAY'S AI GOAL",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight=theme.FONT_STAT_TITLE[2]),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.title_lbl.pack(side="left")

        self.status_pill = ctk.CTkLabel(
            self.header_row,
            text="IN PROGRESS",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
            fg_color=theme.COLOR_ACCENT_MUTED,
            text_color=theme.COLOR_ACCENT,
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.status_pill.pack(side="right")

        # ----------------------------------------------------------------------
        # Goal Details & Progress
        # ----------------------------------------------------------------------
        self.goal_name_lbl = ctk.CTkLabel(
            self,
            text="Complete 10 Clean Repetitions",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        self.goal_name_lbl.pack(fill="x", padx=14, pady=(2, 0))

        self.goal_desc_lbl = ctk.CTkLabel(
            self,
            text="Achieve 10 validated repetitions with parallel depth and torso stability.",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w",
            wraplength=250,
            justify="left"
        )
        self.goal_desc_lbl.pack(fill="x", padx=14, pady=(0, 6))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=6,
            corner_radius=3,
            fg_color=theme.COLOR_CARD_INNER,
            progress_color=theme.COLOR_ACCENT
        )
        self.progress_bar.pack(fill="x", padx=14, pady=(0, 4))
        self.progress_bar.set(0.0)

        # Bottom Counter & Status
        self.counter_row = ctk.CTkFrame(self, fg_color="transparent")
        self.counter_row.pack(fill="x", padx=14, pady=(0, 10))

        self.reps_counter = ctk.CTkLabel(
            self.counter_row,
            text="0 / 10 Reps (0%)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        self.reps_counter.pack(side="left")

        self.remaining_lbl = ctk.CTkLabel(
            self.counter_row,
            text="10 reps remaining",
            font=ctk.CTkFont(size=9),
            text_color=theme.COLOR_TEXT_MUTED
        )
        self.remaining_lbl.pack(side="right")

        self.update_progress(0, 100, self.current_exercise)

    def update_progress(
        self,
        clean_reps: int,
        accuracy: int,
        exercise_name: Optional[str] = None
    ):
        """Evaluates goal criteria and updates UI progress bar and status."""
        if exercise_name:
            self.current_exercise = exercise_name.upper().strip()

        eval_res = evaluate_goal_progress(self.current_exercise, clean_reps, accuracy)
        self.goal_name_lbl.configure(text=eval_res["goal_title"])
        self.goal_desc_lbl.configure(text=eval_res["goal_description"])

        if eval_res["is_guided"]:
            self.status_pill.configure(text="GUIDED MODE", fg_color=theme.COLOR_CARD_INNER, text_color=theme.COLOR_INFO)
            self.progress_bar.set(1.0)
            self.progress_bar.configure(progress_color=theme.COLOR_INFO)
            self.reps_counter.configure(text="Reference Practice Goal", text_color=theme.COLOR_INFO)
            self.remaining_lbl.configure(text="Technique Reference Active")
            return

        fraction = eval_res["progress_fraction"]
        is_achieved = eval_res["is_achieved"]

        self.progress_bar.set(fraction)
        if is_achieved:
            self.status_pill.configure(text="COMPLETED", fg_color=theme.COLOR_SUCCESS_MUTED, text_color=theme.COLOR_SUCCESS)
            self.progress_bar.configure(progress_color=theme.COLOR_SUCCESS)
            self.reps_counter.configure(text=f"{clean_reps} / {eval_res['target_reps']} Reps (100%)", text_color=theme.COLOR_SUCCESS)
            self.remaining_lbl.configure(text="🎉 GOAL ACHIEVED!", text_color=theme.COLOR_SUCCESS)
        else:
            self.status_pill.configure(text="IN PROGRESS", fg_color=theme.COLOR_ACCENT_MUTED, text_color=theme.COLOR_ACCENT)
            self.progress_bar.configure(progress_color=theme.COLOR_ACCENT)
            self.reps_counter.configure(text=f"{clean_reps} / {eval_res['target_reps']} Reps ({eval_res['progress_percent']}%)", text_color=theme.COLOR_TEXT_SECONDARY)
            self.remaining_lbl.configure(text=eval_res["status_text"], text_color=theme.COLOR_TEXT_MUTED)

    def reset(self):
        """Resets goal progress to baseline."""
        self.update_progress(0, 100, self.current_exercise)
