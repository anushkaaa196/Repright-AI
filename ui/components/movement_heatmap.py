"""Movement Consistency Heatmap Matrix Component for REPRIGHT AI.

Displays a compact, cyber-styled 2D matrix visualizing execution consistency
across biomechanical dimensions for recent repetitions.
"""

from typing import Dict, Any, List, Optional
import customtkinter as ctk

from ui import theme


DIMENSION_ROWS = [
    ("range_of_motion", "DEPTH / ROM"),
    ("alignment", "ALIGNMENT"),
    ("stability", "STABILITY"),
    ("movement_control", "CONTROL"),
    ("consistency", "CADENCE")
]


class MovementHeatmapFrame(ctk.CTkFrame):
    """Horizontal scrollable matrix displaying consistency dots across reps."""

    def __init__(self, master, max_reps: int = 12, **kwargs):
        super().__init__(
            master,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            corner_radius=10,
            **kwargs
        )
        self.max_reps = max_reps
        self._rep_data: List[Dict[str, Any]] = []

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(8, 4))

        title = ctk.CTkLabel(
            header,
            text="MOVEMENT CONSISTENCY MATRIX",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_ACCENT
        )
        title.pack(side="left")

        legend = ctk.CTkLabel(
            header,
            text="● ≥90%  ● 75-89%  ● 50-74%  ● <50%",
            font=ctk.CTkFont(size=9),
            text_color=theme.COLOR_TEXT_MUTED
        )
        legend.pack(side="right")

        # Matrix Canvas Container
        self.matrix_container = ctk.CTkScrollableFrame(
            self,
            orientation="horizontal",
            fg_color="transparent",
            height=110
        )
        self.matrix_container.pack(fill="x", expand=True, padx=8, pady=(0, 8))

        self._render_matrix()

    def add_rep(self, rep_analysis: Dict[str, Any]):
        """Appends a newly analyzed repetition to the consistency matrix."""
        if not rep_analysis:
            return
        self._rep_data.append(rep_analysis)
        if len(self._rep_data) > self.max_reps:
            self._rep_data.pop(0)
        self._render_matrix()

    def reset(self):
        """Clears all repetition data from heatmap."""
        self._rep_data.clear()
        self._render_matrix()

    def _render_matrix(self):
        """Redraws the matrix cells based on active rep data."""
        for child in self.matrix_container.winfo_children():
            child.destroy()

        # Left Header Column (Dimension Names)
        label_col = ctk.CTkFrame(self.matrix_container, fg_color="transparent")
        label_col.pack(side="left", padx=(4, 8), pady=2)

        # Spacer for rep header
        spacer = ctk.CTkLabel(label_col, text="", font=ctk.CTkFont(size=9), height=18)
        spacer.pack()

        for _, row_label in DIMENSION_ROWS:
            lbl = ctk.CTkLabel(
                label_col,
                text=row_label,
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=theme.COLOR_TEXT_SECONDARY,
                anchor="w",
                width=80,
                height=18
            )
            lbl.pack(pady=1)

        # Repetition Columns
        if not self._rep_data:
            empty_lbl = ctk.CTkLabel(
                self.matrix_container,
                text="Awaiting completed repetitions to populate matrix...",
                font=ctk.CTkFont(size=10),
                text_color=theme.COLOR_TEXT_MUTED
            )
            empty_lbl.pack(side="left", padx=20, pady=20)
            return

        for rep in self._rep_data:
            rep_num = rep.get("rep_number", 1)
            dim_scores = rep.get("dimension_scores", {})

            col = ctk.CTkFrame(self.matrix_container, fg_color="transparent", width=28)
            col.pack(side="left", padx=2, pady=2)

            # Column Header (e.g. R1, R2)
            header_lbl = ctk.CTkLabel(
                col,
                text=f"R{rep_num}",
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=theme.COLOR_ACCENT,
                width=24,
                height=18
            )
            header_lbl.pack()

            # Cells for each dimension
            for dim_key, _ in DIMENSION_ROWS:
                score = dim_scores.get(dim_key, 80)
                if score >= 90:
                    color = theme.COLOR_SUCCESS
                    dot = "●"
                elif score >= 75:
                    color = theme.COLOR_ACCENT
                    dot = "●"
                elif score >= 50:
                    color = theme.COLOR_WARN
                    dot = "●"
                else:
                    color = theme.COLOR_ALERT
                    dot = "●"

                cell = ctk.CTkLabel(
                    col,
                    text=dot,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color=color,
                    width=24,
                    height=18
                )
                cell.pack(pady=1)
