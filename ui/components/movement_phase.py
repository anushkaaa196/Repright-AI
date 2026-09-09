"""Movement Phase Visualization Component for REPRIGHT AI.

Displays active biomechanical movement stages, percentage progression,
and targeted real-time phase coaching cues.
"""

from typing import Dict, Any, Optional, List
import customtkinter as ctk

from ui import theme


class MovementPhaseCard(ctk.CTkFrame):
    """Visualizes live movement phases with glowing active phase indicators."""

    def __init__(self, master, current_exercise: str = "SQUAT", **kwargs):
        super().__init__(
            master,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            corner_radius=10,
            **kwargs
        )
        self.current_exercise = current_exercise.upper().strip()

        # Header Row
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=12, pady=(10, 6))

        title_lbl = ctk.CTkLabel(
            header_row,
            text="AI MOVEMENT PHASE",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_ACCENT
        )
        title_lbl.pack(side="left")

        self.phase_pill = ctk.CTkLabel(
            header_row,
            text="START",
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=theme.COLOR_CARD_ALT,
            text_color=theme.COLOR_ACCENT,
            corner_radius=4,
            padx=8,
            pady=2
        )
        self.phase_pill.pack(side="right")

        # Phase Sequence Row
        self.steps_container = ctk.CTkFrame(self, fg_color="transparent")
        self.steps_container.pack(fill="x", padx=12, pady=(2, 6))
        self.step_widgets: List[ctk.CTkLabel] = []

        # Progress Bar & Percentage
        prog_row = ctk.CTkFrame(self, fg_color="transparent")
        prog_row.pack(fill="x", padx=12, pady=(2, 4))

        self.prog_bar = ctk.CTkProgressBar(
            prog_row,
            height=6,
            corner_radius=3,
            fg_color=theme.COLOR_PROGRESS_BG,
            progress_color=theme.COLOR_ACCENT
        )
        self.prog_bar.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.prog_bar.set(0.2)

        self.pct_lbl = ctk.CTkLabel(
            prog_row,
            text="20%",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY,
            width=36
        )
        self.pct_lbl.pack(side="right")

        # Live Coaching Focus
        self.focus_lbl = ctk.CTkLabel(
            self,
            text="Focus: Brace core and set stable tripod foot stance.",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_SECONDARY,
            wraplength=280,
            justify="left"
        )
        self.focus_lbl.pack(anchor="w", padx=12, pady=(2, 10))

        self.reset()

    def set_exercise(self, exercise_name: str):
        """Switches active exercise schema."""
        self.current_exercise = exercise_name.upper().strip()
        self.reset()

    def update_phase(self, phase_data: Dict[str, Any]):
        """Updates live phase highlighting, progress bar, and coaching focus."""
        if not phase_data:
            return

        active_phase = phase_data.get("phase_label", "START")
        progress = phase_data.get("phase_progress", 0)
        focus = phase_data.get("coaching_focus", "")
        phase_list = phase_data.get("phase_list", ["START", "DESCENT", "BOTTOM", "ASCENT", "LOCKOUT"])
        active_idx = phase_data.get("phase_index", 0)
        is_guided = phase_data.get("is_guided", False)

        # Re-populate step labels if list changed
        if len(self.step_widgets) != len(phase_list):
            for w in self.step_widgets:
                w.destroy()
            self.step_widgets.clear()

            for i, p_name in enumerate(phase_list):
                lbl = ctk.CTkLabel(
                    self.steps_container,
                    text=p_name,
                    font=ctk.CTkFont(size=9, weight="bold"),
                    text_color=theme.COLOR_TEXT_MUTED,
                    fg_color="transparent",
                    padx=3,
                    pady=1
                )
                lbl.pack(side="left", padx=1)
                self.step_widgets.append(lbl)

                if i < len(phase_list) - 1:
                    arrow = ctk.CTkLabel(
                        self.steps_container,
                        text="›",
                        font=ctk.CTkFont(size=9),
                        text_color=theme.COLOR_BORDER,
                        width=8
                    )
                    arrow.pack(side="left")

        # Highlight active phase widget
        for i, lbl in enumerate(self.step_widgets):
            if i == active_idx:
                lbl.configure(
                    text_color=theme.COLOR_ACCENT if not is_guided else theme.COLOR_INFO,
                    font=ctk.CTkFont(size=10, weight="bold")
                )
            else:
                lbl.configure(
                    text_color=theme.COLOR_TEXT_MUTED,
                    font=ctk.CTkFont(size=9, weight="normal")
                )

        # Update pill badge and progress
        if is_guided:
            self.phase_pill.configure(
                text="GUIDED REF",
                text_color=theme.COLOR_INFO,
                fg_color=theme.COLOR_CARD_ALT
            )
            self.prog_bar.set(1.0)
            self.prog_bar.configure(progress_color=theme.COLOR_INFO)
            self.pct_lbl.configure(text="TARGET", text_color=theme.COLOR_INFO)
        else:
            direction_arrow = "↓" if phase_data.get("movement_direction") == "DOWN" else ("↑" if phase_data.get("movement_direction") == "UP" else "●")
            self.phase_pill.configure(
                text=f"{direction_arrow} {active_phase}",
                text_color=theme.COLOR_ACCENT,
                fg_color=theme.COLOR_CARD_ALT
            )
            frac = max(0.0, min(1.0, float(progress) / 100.0))
            self.prog_bar.set(frac)
            self.prog_bar.configure(progress_color=theme.COLOR_ACCENT)
            self.pct_lbl.configure(text=f"{progress}%", text_color=theme.COLOR_TEXT_PRIMARY)

        if focus:
            self.focus_lbl.configure(text=f"Focus: {focus}")

    def reset(self):
        """Resets visual indicators to starting baseline."""
        self.phase_pill.configure(text="START", text_color=theme.COLOR_ACCENT)
        self.prog_bar.set(0.0)
        self.pct_lbl.configure(text="0%")
        self.focus_lbl.configure(text="Focus: Ready to initiate movement cycle.")
        for lbl in self.step_widgets:
            lbl.configure(text_color=theme.COLOR_TEXT_MUTED, font=ctk.CTkFont(size=9, weight="normal"))
