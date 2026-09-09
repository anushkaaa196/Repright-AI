"""Personalized AI Improvement Plan Component for REPRIGHT AI.

Displays the 6-part deterministic training plan (Strength, Focus, Why It Matters,
Next Session Goal, Coaching Cue, Recommended Practice) as both an embedded card and modal dialog.
"""

from typing import Dict, Any, Optional
import customtkinter as ctk
from ui import theme
from core.personalized_coach import generate_personalized_plan
from core.rep_history import RepHistoryTracker


class PersonalizedPlanCard(ctk.CTkFrame):
    """Embedded high-contrast coaching card displaying personalized improvement recommendations."""

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
            text="🧠 PERSONALIZED AI IMPROVEMENT PLAN",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight=theme.FONT_STAT_TITLE[2]),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.title_lbl.pack(side="left")

        self.ex_badge = ctk.CTkLabel(
            self.header_row,
            text=self.current_exercise,
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
            fg_color=theme.COLOR_CARD_INNER,
            text_color=theme.COLOR_ACCENT,
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.ex_badge.pack(side="right")

        # ----------------------------------------------------------------------
        # 6-Part Content Frame
        # ----------------------------------------------------------------------
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="x", padx=14, pady=(4, 12))

        # 1. Strength
        self.strength_lbl = self._create_section("YOUR STRENGTH", "Biomechanical tracking profile active.", theme.COLOR_SUCCESS)

        # 2. Primary Focus
        self.focus_lbl = self._create_section("PRIMARY FOCUS", "Maintain optimal depth and upright chest.", theme.COLOR_WARN)

        # 3. Why It Matters
        self.why_lbl = self._create_section("WHY IT MATTERS", "Proper joint tracking balances forces and maintains joint longevity.", theme.COLOR_TEXT_SECONDARY)

        # 4. Next Session Goal
        self.goal_lbl = self._create_section("NEXT SESSION GOAL", "Complete 10 clean repetitions with consistent alignment.", theme.COLOR_ACCENT)

        # 5. Coaching Cue
        self.cue_lbl = self._create_section("COACHING CUE", '"Drive knees in the same direction as your toes."', theme.COLOR_TEXT_PRIMARY)

        # 6. Recommended Practice
        self.practice_lbl = self._create_section("RECOMMENDED PRACTICE", "Use a 2-second controlled descent with a brief pause at depth.", theme.COLOR_INFO)

    def _create_section(self, header: str, default_text: str, color: str) -> ctk.CTkLabel:
        """Helper to create standard section header + description."""
        t_lbl = ctk.CTkLabel(
            self.content_frame,
            text=header,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        )
        t_lbl.pack(anchor="w", pady=(4, 1))

        d_lbl = ctk.CTkLabel(
            self.content_frame,
            text=default_text,
            font=ctk.CTkFont(size=10),
            text_color=color,
            wraplength=380,
            justify="left"
        )
        d_lbl.pack(anchor="w", pady=(0, 2))
        return d_lbl

    def update_plan(self, plan: Dict[str, Any]):
        """Updates plan card text from a structured plan dictionary."""
        self.current_exercise = plan.get("exercise", self.current_exercise)
        self.ex_badge.configure(text=self.current_exercise)

        self.strength_lbl.configure(text=plan.get("strength", ""))
        self.focus_lbl.configure(text=plan.get("primary_focus", ""))
        self.why_lbl.configure(text=plan.get("why_it_matters", ""))
        self.goal_lbl.configure(text=plan.get("next_session_goal", ""))
        self.cue_lbl.configure(text=plan.get("coaching_cue", ""))
        self.practice_lbl.configure(text=plan.get("recommended_practice", ""))

    def refresh(self, exercise_name: Optional[str] = None):
        """Re-evaluates plan using current RepHistoryTracker."""
        if exercise_name:
            self.current_exercise = exercise_name.upper().strip()
        plan = generate_personalized_plan(self.current_exercise)
        self.update_plan(plan)


class PersonalizedPlanDialog(ctk.CTkToplevel):
    """Modal dialog displaying full personalized AI coaching plan."""

    def __init__(self, master, exercise_name: str, **kwargs):
        super().__init__(master, **kwargs)
        self.title("REPRIGHT AI - Personalized AI Improvement Plan")
        self.geometry("640x560")
        self.minsize(560, 480)
        self.configure(fg_color=theme.COLOR_BG_DARK)

        self.transient(master)
        self.after(10, self._center)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        plan = generate_personalized_plan(exercise_name)

        card = PersonalizedPlanCard(self, current_exercise=exercise_name)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        card.update_plan(plan)

        btn_close = ctk.CTkButton(
            self,
            text="CLOSE",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
            height=32,
            width=100,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_BORDER_LIGHT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=self.destroy
        )
        btn_close.pack(pady=(0, 16))

    def _center(self):
        try:
            self.update_idletasks()
            master = self.master
            x = master.winfo_x() + (master.winfo_width() - self.winfo_width()) // 2
            y = master.winfo_y() + (master.winfo_height() - self.winfo_height()) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass
