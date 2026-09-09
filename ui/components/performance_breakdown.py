"""Biomechanical Performance Breakdown Component for REPRIGHT AI.

Displays multi-dimensional performance scores with progress bars, adapting labels per exercise.
For Guided exercises, cleanly communicates 'Reference Biomechanical Targets' instead of live scores.
"""

from typing import Dict, Any, Optional
import customtkinter as ctk
from ui import theme
from core.rep_analysis import DIMENSION_SCHEMAS
from core.exercise_registry import is_active_ai_supported


class PerformanceBreakdownFrame(ctk.CTkFrame):
    """Visual multi-dimensional biomechanical performance breakdown card."""

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
            text="BIOMECHANICAL QUALITY BREAKDOWN",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight=theme.FONT_STAT_TITLE[2]),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.title_lbl.pack(side="left")

        self.mode_tag = ctk.CTkLabel(
            self.header_row,
            text="AI ESTIMATED",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
            fg_color=theme.COLOR_CARD_INNER,
            text_color=theme.COLOR_ACCENT,
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.mode_tag.pack(side="right")

        # ----------------------------------------------------------------------
        # Container for Dimension Bars
        # ----------------------------------------------------------------------
        self.bars_container = ctk.CTkFrame(self, fg_color="transparent")
        self.bars_container.pack(fill="x", padx=14, pady=(2, 10))
        self.bars_container.grid_columnconfigure(1, weight=1)

        self.dim_keys = ["range_of_motion", "alignment", "stability", "movement_control", "consistency"]
        self.bar_widgets: Dict[str, Dict[str, Any]] = {}

        self._build_dimension_rows()

    def _build_dimension_rows(self):
        """Constructs 5 progress bar rows."""
        for child in self.bars_container.winfo_children():
            child.destroy()
        self.bar_widgets.clear()

        schema = DIMENSION_SCHEMAS.get(self.current_exercise, DIMENSION_SCHEMAS["DEFAULT"])
        is_active = is_active_ai_supported(self.current_exercise)

        if not is_active:
            self.mode_tag.configure(text="REFERENCE TARGETS", text_color=theme.COLOR_INFO, fg_color=theme.COLOR_ACCENT_MUTED)
        else:
            self.mode_tag.configure(text="AI ESTIMATED", text_color=theme.COLOR_ACCENT, fg_color=theme.COLOR_CARD_INNER)

        for i, dim_key in enumerate(self.dim_keys):
            row_f = ctk.CTkFrame(self.bars_container, fg_color="transparent")
            row_f.pack(fill="x", pady=2)
            row_f.grid_columnconfigure(1, weight=1)

            label_text = schema.get(dim_key, dim_key.replace("_", " ").title())
            lbl = ctk.CTkLabel(
                row_f,
                text=label_text,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=theme.COLOR_TEXT_SECONDARY,
                width=125,
                anchor="w"
            )
            lbl.grid(row=0, column=0, sticky="w")

            if is_active:
                prog = ctk.CTkProgressBar(
                    row_f,
                    height=6,
                    corner_radius=3,
                    fg_color=theme.COLOR_CARD_INNER,
                    progress_color=theme.COLOR_SUCCESS
                )
                prog.grid(row=0, column=1, padx=(6, 8), sticky="ew")
                prog.set(1.0)

                val_lbl = ctk.CTkLabel(
                    row_f,
                    text="100%",
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=theme.COLOR_SUCCESS,
                    width=40,
                    anchor="e"
                )
                val_lbl.grid(row=0, column=2, sticky="e")
                self.bar_widgets[dim_key] = {"progress": prog, "val": val_lbl, "label": lbl}

            else:
                # Guided Mode targets
                target_desc_map = {
                    "range_of_motion": "Target Angle: 90° Range",
                    "alignment": "Axis: Laser Neutral",
                    "stability": "Core: Anti-Extension",
                    "movement_control": "Cadence: 2s Controlled",
                    "consistency": "Tempo: Repetition Cadence"
                }
                desc_txt = target_desc_map.get(dim_key, "Target Biomechanical Criteria")
                ref_lbl = ctk.CTkLabel(
                    row_f,
                    text=desc_txt,
                    font=ctk.CTkFont(size=10),
                    text_color=theme.COLOR_INFO,
                    anchor="w"
                )
                ref_lbl.grid(row=0, column=1, padx=6, sticky="w")
                self.bar_widgets[dim_key] = {"ref_lbl": ref_lbl, "label": lbl}

    def update_breakdown(
        self,
        dimension_averages: Dict[str, int],
        exercise_name: Optional[str] = None
    ):
        """Updates dimension bar percentages and dynamic color grades."""
        if exercise_name and exercise_name.upper().strip() != self.current_exercise:
            self.current_exercise = exercise_name.upper().strip()
            self._build_dimension_rows()

        if not is_active_ai_supported(self.current_exercise):
            return  # Kept in reference mode

        for dim_key, widgets in self.bar_widgets.items():
            if "progress" not in widgets:
                continue
            val = dimension_averages.get(dim_key, 100)
            fraction = min(1.0, max(0.0, float(val) / 100.0))

            if val >= 90:
                color = theme.COLOR_SUCCESS
            elif val >= 75:
                color = theme.COLOR_ACCENT
            elif val >= 50:
                color = theme.COLOR_WARN
            else:
                color = theme.COLOR_ALERT

            widgets["progress"].set(fraction)
            widgets["progress"].configure(progress_color=color)
            widgets["val"].configure(text=f"{val}%", text_color=color)

    def set_exercise(self, exercise_name: str):
        """Switches active exercise schema and rebuilds breakdown display."""
        self.current_exercise = exercise_name.upper().strip()
        self._build_dimension_rows()

    def reset(self):
        """Resets bars to 100% baseline."""
        self.update_breakdown({k: 100 for k in self.dim_keys})
