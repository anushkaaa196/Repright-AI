"""Live Rep-by-Rep Performance Timeline Component for REPRIGHT AI.

Displays a horizontal scrollable strip of individual completed repetition quality cards,
color-coded by biomechanical quality score with instant status pills and fault indicators.
"""

from typing import List, Dict, Any, Optional
import customtkinter as ctk
from ui import theme


class RepTimelineFrame(ctk.CTkFrame):
    """Horizontal scrollable timeline displaying individual repetition performance cards."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            **kwargs
        )
        self.grid_columnconfigure(0, weight=1)

        # ----------------------------------------------------------------------
        # Header Row
        # ----------------------------------------------------------------------
        self.header_row = ctk.CTkFrame(self, fg_color="transparent")
        self.header_row.pack(fill="x", padx=14, pady=(10, 4))

        self.title_lbl = ctk.CTkLabel(
            self.header_row,
            text="REP PERFORMANCE TIMELINE",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight=theme.FONT_STAT_TITLE[2]),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.title_lbl.pack(side="left")

        self.count_badge = ctk.CTkLabel(
            self.header_row,
            text="0 REPS",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
            fg_color=theme.COLOR_CARD_INNER,
            text_color=theme.COLOR_TEXT_MUTED,
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.count_badge.pack(side="right")

        # ----------------------------------------------------------------------
        # Horizontal Scroll Container
        # ----------------------------------------------------------------------
        self.scroll_strip = ctk.CTkScrollableFrame(
            self,
            orientation="horizontal",
            height=85,
            fg_color="transparent",
            scrollbar_button_color=theme.COLOR_BORDER,
            scrollbar_button_hover_color=theme.COLOR_BORDER_LIGHT
        )
        self.scroll_strip.pack(fill="x", padx=10, pady=(0, 10))

        # Initial Empty State
        self.empty_lbl = ctk.CTkLabel(
            self.scroll_strip,
            text="Awaiting repetitions... Begin movement in frame to record rep-by-rep analytics.",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_MUTED
        )
        self.empty_lbl.pack(pady=22, padx=20)

        self._rep_count = 0

    def add_rep(self, rep: Dict[str, Any]):
        """Appends a new repetition card to the timeline."""
        if self._rep_count == 0 and self.empty_lbl.winfo_exists():
            self.empty_lbl.pack_forget()

        self._rep_count += 1
        self.count_badge.configure(text=f"{self._rep_count} REPS", text_color=theme.COLOR_ACCENT)

        score = rep.get("overall_score", 100)
        rep_num = rep.get("rep_number", self._rep_count)
        status = rep.get("status", "EXCELLENT")

        # Select dynamic color token
        if score >= 90:
            score_color = theme.COLOR_SUCCESS
            border_color = theme.COLOR_SUCCESS
            bg_color = theme.COLOR_CARD_INNER
        elif score >= 75:
            score_color = theme.COLOR_ACCENT
            border_color = theme.COLOR_ACCENT_MUTED
            bg_color = theme.COLOR_CARD_INNER
        elif score >= 50:
            score_color = theme.COLOR_WARN
            border_color = theme.COLOR_WARN
            bg_color = theme.COLOR_CARD_INNER
        else:
            score_color = theme.COLOR_ALERT
            border_color = theme.COLOR_ALERT
            bg_color = theme.COLOR_ALERT_MUTED

        # Card Frame
        card = ctk.CTkFrame(
            self.scroll_strip,
            width=100,
            height=75,
            corner_radius=8,
            fg_color=bg_color,
            border_width=1,
            border_color=border_color
        )
        card.pack(side="left", padx=4, pady=2)
        card.pack_propagate(False)

        # Rep Tag
        t_lbl = ctk.CTkLabel(
            card,
            text=f"REP {rep_num:02d}",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        )
        t_lbl.pack(anchor="w", padx=8, pady=(4, 0))

        # Score Row
        s_row = ctk.CTkFrame(card, fg_color="transparent")
        s_row.pack(fill="x", padx=8, pady=0)

        s_lbl = ctk.CTkLabel(
            s_row,
            text=f"{score}%",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=score_color
        )
        s_lbl.pack(side="left")

        # Status text
        st_lbl = ctk.CTkLabel(
            card,
            text=status.replace("_", " ").upper()[:9],
            font=ctk.CTkFont(size=8, weight="bold"),
            text_color=score_color
        )
        st_lbl.pack(anchor="w", padx=8, pady=(0, 2))

        # Short cue / issue hint
        issues = rep.get("issues", [])
        hint_text = issues[0][:14] if issues else "Optimal"
        hint_lbl = ctk.CTkLabel(
            card,
            text=f"• {hint_text}",
            font=ctk.CTkFont(size=8),
            text_color=theme.COLOR_TEXT_MUTED
        )
        hint_lbl.pack(anchor="w", padx=8, pady=(0, 4))

    def set_reps(self, reps: List[Dict[str, Any]]):
        """Clears and rebuilds timeline with given repetition records."""
        self.reset()
        for r in reps:
            self.add_rep(r)

    def reset(self):
        """Resets timeline to initial empty state."""
        self._rep_count = 0
        self.count_badge.configure(text="0 REPS", text_color=theme.COLOR_TEXT_MUTED)
        for child in self.scroll_strip.winfo_children():
            child.destroy()

        self.empty_lbl = ctk.CTkLabel(
            self.scroll_strip,
            text="Awaiting repetitions... Begin movement in frame to record rep-by-rep analytics.",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_MUTED
        )
        self.empty_lbl.pack(pady=22, padx=20)
