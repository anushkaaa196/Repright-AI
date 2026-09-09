"""REPRIGHT AI - Athlete Authentication Screen.

Hosts the Login and Register views with seamless switching, modern Midnight Navy & Deep Teal styling,
and instant Guest Mode access for Smart India Hackathon demonstrations.
"""

from typing import Callable, Optional
import customtkinter as ctk
from ui import theme
from services.auth_service import AuthService
from services.user_session import UserSession
from database.models import User


class LoginFrame(ctk.CTkFrame):
    """Login card containing email, password, and sign-in controls."""

    def __init__(
        self,
        master,
        on_success: Optional[Callable[[User], None]] = None,
        on_switch_to_register: Optional[Callable[[], None]] = None,
        on_guest_login: Optional[Callable[[], None]] = None,
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
        self.on_switch_to_register = on_switch_to_register
        self.on_guest_login = on_guest_login
        self.auth_service = auth_service or AuthService()

        self._build_ui()

    def _build_ui(self):
        # Header Badge & Title
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=28, pady=(28, 20))

        badge = ctk.CTkLabel(
            header_frame,
            text="AI BIOMECHANICS & PERFORMANCE LAB",
            font=ctk.CTkFont(size=theme.FONT_BRAND_BADGE[1], weight=theme.FONT_BRAND_BADGE[2]),
            text_color=theme.COLOR_TEAL,
            fg_color=theme.COLOR_TEAL_MUTED,
            corner_radius=4,
            height=20,
            padx=8
        )
        badge.pack(anchor="w", pady=(0, 6))

        title = ctk.CTkLabel(
            header_frame,
            text="Welcome to REPRIGHT AI",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1] + 6, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header_frame,
            text="Sign in to access your workout telemetry & progress dashboard",
            font=ctk.CTkFont(size=theme.FONT_SUBTITLE[1]),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # Form Inputs
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(fill="x", padx=28, pady=6)

        # Email Entry
        self._add_label(form, "ATHLETE EMAIL")
        self.email_entry = ctk.CTkEntry(
            form,
            placeholder_text="athlete@example.com",
            height=38,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.email_entry.pack(fill="x", pady=(0, 14))

        # Password Entry
        self._add_label(form, "PASSWORD")
        self.pwd_entry = ctk.CTkEntry(
            form,
            placeholder_text="••••••••",
            show="*",
            height=38,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.pwd_entry.pack(fill="x", pady=(0, 6))

        # Show Password Toggle
        self.show_pwd_var = ctk.BooleanVar(value=False)
        self.show_pwd_cb = ctk.CTkCheckBox(
            form,
            text="Show Password",
            variable=self.show_pwd_var,
            command=self._toggle_pwd_visibility,
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_SECONDARY,
            fg_color=theme.COLOR_TEAL,
            hover_color=theme.COLOR_TEAL_HOVER,
            border_color=theme.COLOR_BORDER,
            corner_radius=4,
            width=16,
            height=16
        )
        self.show_pwd_cb.pack(anchor="w", pady=(0, 14))

        # Feedback Toast Label
        self.feedback_label = ctk.CTkLabel(
            form,
            text="",
            font=ctk.CTkFont(size=theme.FONT_FEEDBACK[1], weight="bold"),
            text_color=theme.COLOR_ALERT,
            wraplength=380
        )
        self.feedback_label.pack(fill="x", pady=(0, 10))

        # Sign In Button
        self.login_btn = ctk.CTkButton(
            form,
            text="SIGN IN TO PLATFORM",
            height=42,
            corner_radius=8,
            fg_color=theme.COLOR_TEAL,
            hover_color=theme.COLOR_TEAL_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=theme.FONT_BUTTON[1], weight="bold"),
            command=self._handle_login
        )
        self.login_btn.pack(fill="x", pady=(0, 10))

        # Guest Access Button
        self.guest_btn = ctk.CTkButton(
            form,
            text="CONTINUE AS GUEST / DEMO",
            height=38,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_SECONDARY,
            font=ctk.CTkFont(size=theme.FONT_BODY[1], weight="bold"),
            command=self._handle_guest
        )
        self.guest_btn.pack(fill="x", pady=(0, 16))

        # Switch to Register
        switch_frame = ctk.CTkFrame(form, fg_color="transparent")
        switch_frame.pack(fill="x", pady=(0, 20))

        switch_label = ctk.CTkLabel(
            switch_frame,
            text="Don't have an athlete account?",
            font=ctk.CTkFont(size=theme.FONT_BODY[1]),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        switch_label.pack(side="left", padx=(10, 4))

        switch_btn = ctk.CTkButton(
            switch_frame,
            text="Create Profile",
            font=ctk.CTkFont(size=theme.FONT_BODY[1], weight="bold"),
            text_color=theme.COLOR_TEAL,
            fg_color="transparent",
            hover=False,
            width=80,
            command=self._switch_register
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

    def _toggle_pwd_visibility(self):
        if self.show_pwd_var.get():
            self.pwd_entry.configure(show="")
        else:
            self.pwd_entry.configure(show="*")

    def _switch_register(self):
        if self.on_switch_to_register:
            self.on_switch_to_register()

    def _handle_guest(self):
        session = UserSession.get_instance()
        guest_user = session.get_or_create_default_user()
        session.set_current_user(guest_user)
        if self.on_guest_login:
            self.on_guest_login()
        elif self.on_success:
            self.on_success(guest_user)

    def _handle_login(self):
        email = self.email_entry.get().strip()
        pwd = self.pwd_entry.get()

        success, msg, user = self.auth_service.login(email, pwd)
        if not success:
            self.feedback_label.configure(text=msg, text_color=theme.COLOR_ALERT)
            return

        self.feedback_label.configure(text="Authentication successful.", text_color=theme.COLOR_SUCCESS)
        UserSession.get_instance().set_current_user(user)

        if self.on_success and user:
            self.after(300, lambda: self.on_success(user))


class AuthWindow(ctk.CTk):
    """Standalone launcher window for REPRIGHT AI user authentication."""

    def __init__(self, on_authenticated: Optional[Callable[[User], None]] = None):
        super().__init__()
        self.on_authenticated = on_authenticated

        theme.setup_theme()
        self.title("REPRIGHT AI — Athlete Authentication")
        self.geometry("480x640")
        self.minsize(440, 580)
        self.configure(fg_color=theme.COLOR_BG_DARK)

        # Center on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - 480) // 2)
        y = max(0, (screen_h - 640) // 2)
        self.geometry(f"480x640+{x}+{y}")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.login_view = LoginFrame(
            self.container,
            on_success=self._on_auth_success,
            on_switch_to_register=self._show_register,
            on_guest_login=self._on_guest_access
        )
        self.login_view.pack(fill="both", expand=True)

        self.register_view: Optional[ctk.CTkFrame] = None

    def _show_register(self):
        from ui.auth.register_screen import RegisterFrame
        if self.login_view:
            self.login_view.pack_forget()

        if self.register_view is None:
            self.register_view = RegisterFrame(
                self.container,
                on_success=self._on_auth_success,
                on_switch_to_login=self._show_login
            )
        self.register_view.pack(fill="both", expand=True)

    def _show_login(self):
        if self.register_view:
            self.register_view.pack_forget()
        if self.login_view:
            self.login_view.pack(fill="both", expand=True)

    def _on_guest_access(self):
        guest = UserSession.get_instance().get_or_create_default_user()
        self._on_auth_success(guest)

    def _on_auth_success(self, user: User):
        UserSession.get_instance().set_current_user(user)
        cb = self.on_authenticated
        self.destroy()
        if cb:
            cb(user)


class AuthDialog(ctk.CTkToplevel):
    """Modal authentication dialog when invoked from an existing active application window."""

    def __init__(self, master, on_authenticated: Optional[Callable[[User], None]] = None):
        super().__init__(master)
        self.on_authenticated = on_authenticated

        self.title("REPRIGHT AI — Switch Athlete Profile")
        self.geometry("480x640")
        self.configure(fg_color=theme.COLOR_BG_DARK)

        self.transient(master)
        self.grab_set()

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=20, pady=20)

        self.login_view = LoginFrame(
            self.container,
            on_success=self._on_auth_success,
            on_switch_to_register=self._show_register,
            on_guest_login=self._on_guest_access
        )
        self.login_view.pack(fill="both", expand=True)
        self.register_view: Optional[ctk.CTkFrame] = None

    def _show_register(self):
        from ui.auth.register_screen import RegisterFrame
        if self.login_view:
            self.login_view.pack_forget()
        if self.register_view is None:
            self.register_view = RegisterFrame(
                self.container,
                on_success=self._on_auth_success,
                on_switch_to_login=self._show_login
            )
        self.register_view.pack(fill="both", expand=True)

    def _show_login(self):
        if self.register_view:
            self.register_view.pack_forget()
        if self.login_view:
            self.login_view.pack(fill="both", expand=True)

    def _on_guest_access(self):
        guest = UserSession.get_instance().get_or_create_default_user()
        self._on_auth_success(guest)

    def _on_auth_success(self, user: User):
        UserSession.get_instance().set_current_user(user)
        if self.on_authenticated:
            self.on_authenticated(user)
        self.destroy()
