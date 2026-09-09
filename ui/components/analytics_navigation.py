"""Analytics Navigation & Quick Launch Component for REPRIGHT AI.

Provides the horizontal tab navigation bar for the Advanced Analytics Hub and the
compact quick-selector for the sidebar.
"""

from typing import Callable, Optional, Dict
import customtkinter as ctk
from ui import theme


ANALYTICS_TABS = [
    "OVERVIEW",
    "REP_PERFORMANCE",
    "BIOMECHANICS",
    "MOVEMENT_CONSISTENCY",
    "FORM_TREND",
    "AI_INTELLIGENCE"
]

TAB_CONFIGS = [
    ("OVERVIEW", "OVERVIEW"),
    ("REP_PERFORMANCE", "REPETITIONS"),
    ("BIOMECHANICS", "BIOMECHANICS"),
    ("MOVEMENT_CONSISTENCY", "CONSISTENCY"),
    ("FORM_TREND", "FORM TREND"),
    ("AI_INTELLIGENCE", "INTELLIGENCE")
]

DROPDOWN_CHOICES = [
    "Session Overview",
    "Rep Performance",
    "Biomechanical Breakdown",
    "Movement Consistency Matrix",
    "Form Quality Trend",
    "AI Movement Intelligence"
]

DROPDOWN_MAP = {
    "Session Overview": "OVERVIEW",
    "Rep Performance": "REP_PERFORMANCE",
    "Biomechanical Breakdown": "BIOMECHANICS",
    "Movement Consistency Matrix": "MOVEMENT_CONSISTENCY",
    "Form Quality Trend": "FORM_TREND",
    "AI Movement Intelligence": "AI_INTELLIGENCE"
}


class AnalyticsNavBar(ctk.CTkFrame):
    """Horizontal cyber tab navigation strip for the Analytics Hub."""

    def __init__(
        self,
        master,
        on_tab_selected: Optional[Callable[[str], None]] = None,
        initial_tab: str = "OVERVIEW",
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=theme.COLOR_PANEL_BG,
            corner_radius=10,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            **kwargs
        )
        self.on_tab_selected = on_tab_selected
        self.active_tab = initial_tab
        self.buttons: Dict[str, ctk.CTkButton] = {}

        # Configure columns equally
        self.grid_rowconfigure(0, weight=1)
        for i in range(len(TAB_CONFIGS)):
            self.grid_columnconfigure(i, weight=1)

        for idx, (tab_key, label) in enumerate(TAB_CONFIGS):
            btn = ctk.CTkButton(
                self,
                text=label,
                font=ctk.CTkFont(size=11, weight="bold"),
                height=34,
                corner_radius=6,
                fg_color=theme.COLOR_PRIMARY if tab_key == initial_tab else theme.COLOR_CARD_BG,
                hover_color=theme.COLOR_PRIMARY_HOVER if tab_key == initial_tab else theme.COLOR_BORDER_LIGHT,
                text_color=theme.COLOR_TEXT_PRIMARY if tab_key == initial_tab else theme.COLOR_TEXT_SECONDARY,
                command=lambda k=tab_key: self.select_tab(k)
            )
            btn.grid(row=0, column=idx, padx=3, pady=4, sticky="ew")
            self.buttons[tab_key] = btn

    def select_tab(self, tab_key: str):
        """Switches active tab and triggers callback."""
        if tab_key not in self.buttons:
            return
        self.active_tab = tab_key
        for k, btn in self.buttons.items():
            if k == tab_key:
                btn.configure(
                    fg_color=theme.COLOR_PRIMARY,
                    hover_color=theme.COLOR_PRIMARY_HOVER,
                    text_color=theme.COLOR_TEXT_PRIMARY
                )
            else:
                btn.configure(
                    fg_color=theme.COLOR_CARD_BG,
                    hover_color=theme.COLOR_BORDER_LIGHT,
                    text_color=theme.COLOR_TEXT_SECONDARY
                )
        if self.on_tab_selected:
            self.on_tab_selected(tab_key)

    def set_active_tab(self, tab_key: str):
        """Programmatically sets the active tab without re-triggering user events."""
        self.select_tab(tab_key)


class QuickAnalyticsMenu(ctk.CTkFrame):
    """Compact analytics quick launcher for the left sidebar."""

    def __init__(
        self,
        master,
        on_select_analytics: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_select_analytics = on_select_analytics

        self.opt_menu = ctk.CTkOptionMenu(
            self,
            values=DROPDOWN_CHOICES,
            command=self._handle_choice,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
            fg_color=theme.COLOR_CARD_BG,
            button_color=theme.COLOR_CARD_HOVER,
            button_hover_color=theme.COLOR_BORDER_LIGHT,
            dropdown_fg_color=theme.COLOR_CARD_BG,
            dropdown_hover_color=theme.COLOR_CARD_HOVER,
            dropdown_text_color=theme.COLOR_TEXT_PRIMARY,
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.opt_menu.pack(fill="x")
        self.opt_menu.set("ANALYTICS HUB ▼")

    def _handle_choice(self, choice: str):
        tab_key = DROPDOWN_MAP.get(choice, "OVERVIEW")
        if self.on_select_analytics:
            self.on_select_analytics(tab_key)
        # Reset display text
        self.opt_menu.set("ANALYTICS HUB ▼")
