"""Collapsible Card Component for REPRIGHT AI.

Provides a clean, modular collapsible container to keep secondary dashboards and details
compact until the user explicitly expands them.
"""

from typing import Optional
import customtkinter as ctk
from ui import theme


class CollapsibleCard(ctk.CTkFrame):
    """Container frame featuring a toggleable header and expandable body."""

    def __init__(
        self,
        master,
        title: str,
        initial_expanded: bool = False,
        badge_text: Optional[str] = None,
        badge_color: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            **kwargs
        )
        self.is_expanded = initial_expanded

        # ----------------------------------------------------------------------
        # Header Row (Clickable Frame)
        # ----------------------------------------------------------------------
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=8,
            height=34
        )
        self.header_frame.pack(fill="x", padx=4, pady=(4, 2))

        # Toggle Button
        self.toggle_btn = ctk.CTkButton(
            self.header_frame,
            text="▼" if self.is_expanded else "▶",
            font=ctk.CTkFont(size=9, weight="bold"),
            width=22,
            height=22,
            corner_radius=4,
            fg_color=theme.COLOR_CARD_INNER,
            hover_color=theme.COLOR_BORDER_LIGHT,
            text_color=theme.COLOR_ACCENT,
            command=self.toggle
        )
        self.toggle_btn.pack(side="left", padx=(6, 4), pady=4)

        # Title Label
        self.title_lbl = ctk.CTkLabel(
            self.header_frame,
            text=title,
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.title_lbl.pack(side="left", padx=4, pady=4)

        # Header click binding
        self.header_frame.bind("<Button-1>", lambda e: self.toggle())
        self.title_lbl.bind("<Button-1>", lambda e: self.toggle())

        # Optional Badge
        if badge_text:
            self.badge_lbl = ctk.CTkLabel(
                self.header_frame,
                text=badge_text,
                font=ctk.CTkFont(size=8, weight="bold"),
                fg_color=theme.COLOR_CARD_INNER,
                text_color=badge_color or theme.COLOR_ACCENT,
                corner_radius=4,
                padx=6,
                pady=1
            )
            self.badge_lbl.pack(side="right", padx=6, pady=4)
        else:
            self.badge_lbl = None

        # ----------------------------------------------------------------------
        # Expandable Content Frame
        # ----------------------------------------------------------------------
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        if self.is_expanded:
            self.content_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def toggle(self):
        """Toggles expanded/collapsed state."""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self):
        """Expands the card body."""
        self.is_expanded = True
        self.toggle_btn.configure(text="▼")
        self.content_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def collapse(self):
        """Collapses the card body."""
        self.is_expanded = False
        self.toggle_btn.configure(text="▶")
        self.content_frame.pack_forget()

    def set_badge(self, text: str, color: Optional[str] = None):
        """Updates or sets header badge text."""
        if self.badge_lbl:
            self.badge_lbl.configure(text=text)
            if color:
                self.badge_lbl.configure(text_color=color)
