"""REPRIGHT AI - Athlete Profile Editor Dialog.

Allows the user to inspect and update demographic measurements, athletic parameters,
and training objectives with real-time BMI estimation.
"""

from typing import Callable, Optional
import customtkinter as ctk
from ui import theme
from services.auth_service import AuthService, VALID_FITNESS_GOALS
from services.user_session import UserSession
from database.models import User


class UserProfileDialog(ctk.CTkToplevel):
    """Modal dialog for modifying athlete baseline parameters and goals."""

    def __init__(
        self,
        master,
        user: Optional[User] = None,
        on_profile_updated: Optional[Callable[[User], None]] = None,
        auth_service: Optional[AuthService] = None
    ):
        super().__init__(master)
        self.user = user or UserSession.get_instance().get_current_user()
        self.on_profile_updated = on_profile_updated
        self.auth_service = auth_service or AuthService()

        self.title("REPRIGHT AI — Athlete Profile Settings")
        self.geometry("480x560")
        self.resizable(False, False)
        self.configure(fg_color=theme.COLOR_BG_DARK)

        self.transient(master)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_PANEL_BG,
            corner_radius=16,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 14))

        badge = ctk.CTkLabel(
            header,
            text="ATHLETE SETTINGS",
            font=ctk.CTkFont(size=theme.FONT_BRAND_BADGE[1], weight=theme.FONT_BRAND_BADGE[2]),
            text_color=theme.COLOR_TEAL,
            fg_color=theme.COLOR_TEAL_MUTED,
            corner_radius=4,
            height=20,
            padx=8
        )
        badge.pack(anchor="w", pady=(0, 4))

        title = ctk.CTkLabel(
            header,
            text="Personal Bio & Objectives",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1] + 2, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        title.pack(anchor="w")

        # Form
        form = ctk.CTkFrame(container, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=4)

        # Email (Read-Only)
        self._add_label(form, "ACCOUNT EMAIL (READ ONLY)")
        self.email_entry = ctk.CTkEntry(
            form,
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_MUTED,
            corner_radius=8
        )
        self.email_entry.insert(0, self.user.email if self.user else "guest@repright.ai")
        self.email_entry.configure(state="disabled")
        self.email_entry.pack(fill="x", pady=(0, 10))

        # Full Name
        self._add_label(form, "ATHLETE NAME")
        self.name_entry = ctk.CTkEntry(
            form,
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.name_entry.insert(0, self.user.name if self.user else "Athlete")
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Height & Weight
        stats_frame = ctk.CTkFrame(form, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 10))
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
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        if self.user and self.user.height_cm:
            self.height_entry.insert(0, str(self.user.height_cm))
        self.height_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        self.weight_entry = ctk.CTkEntry(
            stats_frame,
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        if self.user and self.user.weight_kg:
            self.weight_entry.insert(0, str(self.user.weight_kg))
        self.weight_entry.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # Fitness Goal
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
        current_goal = self.user.fitness_goal if self.user else "STRENGTH"
        self.goal_opt.set(current_goal)
        self.goal_opt.pack(fill="x", pady=(0, 14))

        # Feedback Toast
        self.feedback_label = ctk.CTkLabel(
            form,
            text="",
            font=ctk.CTkFont(size=theme.FONT_FEEDBACK[1], weight="bold"),
            text_color=theme.COLOR_ALERT
        )
        self.feedback_label.pack(fill="x", pady=(0, 8))

        # Buttons
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(8, 0))
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="CANCEL",
            height=38,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            text_color=theme.COLOR_TEXT_SECONDARY,
            command=self.destroy
        )
        cancel_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        save_btn = ctk.CTkButton(
            btn_frame,
            text="SAVE CHANGES",
            height=38,
            corner_radius=8,
            fg_color=theme.COLOR_TEAL,
            hover_color=theme.COLOR_TEAL_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=theme.FONT_BUTTON[1], weight="bold"),
            command=self._handle_save
        )
        save_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

    def _add_label(self, parent, text: str):
        lbl = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        )
        lbl.pack(anchor="w", pady=(0, 2))

    def _handle_save(self):
        if not self.user:
            self.destroy()
            return

        name = self.name_entry.get().strip()
        h_str = self.height_entry.get().strip()
        w_str = self.weight_entry.get().strip()
        goal = self.goal_opt.get()

        h_val = float(h_str) if h_str else None
        w_val = float(w_str) if w_str else None

        success, msg, updated_user = self.auth_service.update_profile(
            user_id=self.user.id,
            name=name,
            height_cm=h_val,
            weight_kg=w_val,
            fitness_goal=goal
        )

        if not success or not updated_user:
            self.feedback_label.configure(text=msg, text_color=theme.COLOR_ALERT)
            return

        UserSession.get_instance().set_current_user(updated_user)
        if self.on_profile_updated:
            self.on_profile_updated(updated_user)

        self.destroy()
