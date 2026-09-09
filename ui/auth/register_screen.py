"""REPRIGHT AI - Athlete Registration Screen.

Presentation-grade registration interface consistent with Midnight Navy / Deep Teal theme.
Collects athlete credentials and physical baseline metrics.
"""

from typing import Callable, Optional
import customtkinter as ctk
from ui import theme
from services.auth_service import AuthService, VALID_FITNESS_GOALS
from database.models import User


class RegisterFrame(ctk.CTkFrame):
    """Registration frame embedded within the authentication container."""

    def __init__(
        self,
        master,
        on_success: Optional[Callable[[User], None]] = None,
        on_switch_to_login: Optional[Callable[[], None]] = None,
        auth_service: Optional[AuthService] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=theme.COLOR_PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            **kwargs
        )
        self.on_success = on_success
        self.on_switch_to_login = on_switch_to_login
        self.auth_service = auth_service or AuthService()

        self._build_ui()

    def _build_ui(self):
        # Header Badge & Title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=28, pady=(24, 16))

        badge = ctk.CTkLabel(
            header_frame,
            text="ATHLETE ONBOARDING",
            font=ctk.CTkFont(size=theme.FONT_BRAND_BADGE[1], weight=theme.FONT_BRAND_BADGE[2]),
            text_color=theme.COLOR_TEAL,
            fg_color=theme.COLOR_TEAL_MUTED,
            corner_radius=4,
            height=20,
            padx=8
        )
        badge.pack(anchor="w", pady=(0, 4))

        title = ctk.CTkLabel(
            header_frame,
            text="Create RepRight Profile",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1] + 4, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Personalized biomechanics & performance intelligence",
            font=ctk.CTkFont(size=theme.FONT_SUBTITLE[1]),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # Form Inputs Container (Scrollable if needed on smaller screens)
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=28, pady=4)

        # Full Name
        self._add_label(form, "FULL NAME")
        self.name_entry = self._create_entry(form, "Enter your full name")

        # Email
        self._add_label(form, "EMAIL ADDRESS")
        self.email_entry = self._create_entry(form, "athlete@example.com")

        # Password Row (Grid: Password & Confirm)
        pwd_frame = ctk.CTkFrame(form, fg_color="transparent")
        pwd_frame.pack(fill="x", pady=(0, 8))
        pwd_frame.grid_columnconfigure(0, weight=1)
        pwd_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            pwd_frame,
            text="PASSWORD",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).grid(row=0, column=0, sticky="w", padx=(0, 6), pady=(0, 2))

        ctk.CTkLabel(
            pwd_frame,
            text="CONFIRM PASSWORD",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).grid(row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 2))

        self.pwd_entry = ctk.CTkEntry(
            pwd_frame,
            placeholder_text="At least 6 chars",
            show="*",
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.pwd_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        self.confirm_pwd_entry = ctk.CTkEntry(
            pwd_frame,
            placeholder_text="Re-type password",
            show="*",
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.confirm_pwd_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # Physical Baseline Row (Height & Weight)
        stats_frame = ctk.CTkFrame(form, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 8))
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            stats_frame,
            text="HEIGHT (CM)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).grid(row=0, column=0, sticky="w", padx=(0, 6), pady=(0, 2))

        ctk.CTkLabel(
            stats_frame,
            text="WEIGHT (KG)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).grid(row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 2))

        self.height_entry = ctk.CTkEntry(
            stats_frame,
            placeholder_text="e.g. 175",
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.height_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        self.weight_entry = ctk.CTkEntry(
            stats_frame,
            placeholder_text="e.g. 72.5",
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.weight_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # Fitness Goal Selector
        self._add_label(form, "PRIMARY ATHLETIC GOAL")
        self.goal_opt = ctk.CTkOptionMenu(
            form,
            values=VALID_FITNESS_GOALS,
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            button_color=theme.COLOR_CARD_ELEVATED,
            button_hover_color=theme.COLOR_ACCENT,
            dropdown_fg_color=theme.COLOR_CARD_ELEVATED,
            dropdown_hover_color=theme.COLOR_ACCENT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.goal_opt.pack(fill="x", pady=(0, 12))
        self.goal_opt.set("STRENGTH")

        # Feedback Toast Label
        self.feedback_label = ctk.CTkLabel(
            form,
            text="",
            font=ctk.CTkFont(size=theme.FONT_FEEDBACK[1], weight="bold"),
            text_color=theme.COLOR_ALERT,
            wraplength=380
        )
        self.feedback_label.pack(fill="x", pady=(0, 8))

        # Action Buttons
        self.register_btn = ctk.CTkButton(
            form,
            text="CREATE ATHLETE ACCOUNT",
            height=40,
            corner_radius=8,
            fg_color=theme.COLOR_TEAL,
            hover_color=theme.COLOR_TEAL_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=theme.FONT_BUTTON[1], weight="bold"),
            command=self._handle_register
        )
        self.register_btn.pack(fill="x", pady=(0, 10))

        # Switch to Login
        switch_frame = ctk.CTkFrame(form, fg_color="transparent")
        switch_frame.pack(fill="x", pady=(0, 16))

        switch_label = ctk.CTkLabel(
            switch_frame,
            text="Already registered?",
            font=ctk.CTkFont(size=theme.FONT_BODY[1]),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        switch_label.pack(side="left", padx=(10, 4))

        switch_btn = ctk.CTkButton(
            switch_frame,
            text="Sign In",
            font=ctk.CTkFont(size=theme.FONT_BODY[1], weight="bold"),
            text_color=theme.COLOR_TEAL,
            fg_color="transparent",
            hover=False,
            width=60,
            command=self._switch_login
        )
        switch_btn.pack(side="left")

    def _add_label(self, parent, text: str):
        lbl = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        )
        lbl.pack(anchor="w", pady=(0, 2))

    def _create_entry(self, parent, placeholder: str) -> ctk.CTkEntry:
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        entry.pack(fill="x", pady=(0, 8))
        return entry

    def _switch_login(self):
        if self.on_switch_to_login:
            self.on_switch_to_login()

    def _handle_register(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        pwd = self.pwd_entry.get()
        confirm = self.confirm_pwd_entry.get()
        h_str = self.height_entry.get().strip()
        w_str = self.weight_entry.get().strip()
        goal = self.goal_opt.get()

        if pwd != confirm:
            self.feedback_label.configure(
                text="Passwords do not match.",
                text_color=theme.COLOR_ALERT
            )
            return

        h_val = float(h_str) if h_str else None
        w_val = float(w_str) if w_str else None

        success, msg, user = self.auth_service.register(
            name=name,
            email=email,
            password=pwd,
            height_cm=h_val,
            weight_kg=w_val,
            fitness_goal=goal
        )

        if not success:
            self.feedback_label.configure(text=msg, text_color=theme.COLOR_ALERT)
            return

        from services.user_session import UserSession
        UserSession.get_instance().set_current_user(user)

        self.feedback_label.configure(
            text="Profile created! Initializing platform...",
            text_color=theme.COLOR_SUCCESS
        )

        if self.on_success and user:
            self.after(300, lambda: self.on_success(user))

