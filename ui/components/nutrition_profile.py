"""REPRIGHT AI - Nutrition & Lifestyle Profile Dialog.

Enables athletes to configure nutritional parameters (age, biological sex, activity level,
dietary preferences, and food allergies/restrictions) without duplicating Phase 7A bio metrics.
"""

from typing import Callable, Optional
import customtkinter as ctk
from ui import theme
from services.user_session import UserSession
from services.nutrition_service import NutritionService
from database.models import User, NutritionProfile


DIET_PREFERENCES = ["VEGETARIAN", "NON_VEGETARIAN", "VEGAN", "EGGETARIAN"]
ACTIVITY_LEVELS = ["SEDENTARY", "LIGHTLY_ACTIVE", "MODERATELY_ACTIVE", "VERY_ACTIVE"]
GENDERS = ["MALE", "FEMALE"]


class NutritionProfileDialog(ctk.CTkToplevel):
    """Modal dialog for editing dietary parameters, activity, and food restrictions."""

    def __init__(
        self,
        master,
        user: Optional[User] = None,
        on_profile_updated: Optional[Callable[[], None]] = None,
        nutrition_service: Optional[NutritionService] = None
    ):
        super().__init__(master)
        self.user = user or UserSession.get_instance().get_current_user()
        self.on_profile_updated = on_profile_updated
        self.nutrition_service = nutrition_service or NutritionService()

        self.title("REPRIGHT AI — Nutrition Profile Settings")
        self.geometry("520x660")
        self.minsize(460, 580)
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
        header.pack(fill="x", padx=24, pady=(20, 10))

        badge = ctk.CTkLabel(
            header,
            text="NUTRITION INTELLIGENCE ONBOARDING",
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
            text="Dietary & Lifestyle Parameters",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1] + 4, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Calibrated energy expenditure and Indian-adapted meal allocations",
            font=ctk.CTkFont(size=theme.FONT_SUBTITLE[1]),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # Reused Physical Baseline Summary (Read-Only Pill Banner)
        h = f"{self.user.height_cm:.0f} cm" if self.user and self.user.height_cm else "175 cm"
        w = f"{self.user.weight_kg:.1f} kg" if self.user and self.user.weight_kg else "70.0 kg"
        bmi = f"BMI {self.user.bmi}" if self.user and self.user.bmi else "BMI 22.9"
        goal = self.user.fitness_goal if self.user and self.user.fitness_goal else "GENERAL_FITNESS"

        bio_bar = ctk.CTkFrame(container, fg_color=theme.COLOR_CARD_BG, corner_radius=8, border_width=1, border_color=theme.COLOR_BORDER)
        bio_bar.pack(fill="x", padx=24, pady=(0, 12), ipady=6)

        bio_text = f"Athlete Physical Baseline: {h} • {w} • {bmi} • Goal: {goal.replace('_', ' ')}"
        ctk.CTkLabel(
            bio_bar,
            text=bio_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_SECONDARY
        ).pack(anchor="center")

        # Scrollable form for smaller screens
        form = ctk.CTkScrollableFrame(container, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=24, pady=4)

        user_id = self.user.id if self.user else 1
        current_profile = self.nutrition_service.get_or_create_profile(user_id)

        # 1. Age & Biological Sex Row
        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 10))
        row1.grid_columnconfigure(0, weight=1)
        row1.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(row1, text="AGE (YEARS)", font=ctk.CTkFont(size=10, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).grid(row=0, column=0, sticky="w", padx=(0, 6), pady=(0, 2))
        ctk.CTkLabel(row1, text="BIOLOGICAL SEX (FOR BMR)", font=ctk.CTkFont(size=10, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).grid(row=0, column=1, sticky="w", padx=(6, 0), pady=(0, 2))

        self.age_entry = ctk.CTkEntry(
            row1,
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.age_entry.insert(0, str(current_profile.age))
        self.age_entry.grid(row=1, column=0, sticky="ew", padx=(0, 6))

        self.gender_opt = ctk.CTkOptionMenu(
            row1,
            values=GENDERS,
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            button_color=theme.COLOR_CARD_ELEVATED,
            button_hover_color=theme.COLOR_ACCENT,
            dropdown_fg_color=theme.COLOR_CARD_ELEVATED,
            dropdown_hover_color=theme.COLOR_ACCENT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.gender_opt.set(current_profile.gender)
        self.gender_opt.grid(row=1, column=1, sticky="ew", padx=(6, 0))

        # 2. Activity Level
        self._add_label(form, "DAILY ACTIVITY LEVEL")
        self.activity_opt = ctk.CTkOptionMenu(
            form,
            values=ACTIVITY_LEVELS,
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            button_color=theme.COLOR_CARD_ELEVATED,
            button_hover_color=theme.COLOR_ACCENT,
            dropdown_fg_color=theme.COLOR_CARD_ELEVATED,
            dropdown_hover_color=theme.COLOR_ACCENT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.activity_opt.set(current_profile.activity_level)
        self.activity_opt.pack(fill="x", pady=(0, 10))

        # 3. Dietary Preference
        self._add_label(form, "DIETARY PREFERENCE")
        self.diet_opt = ctk.CTkOptionMenu(
            form,
            values=DIET_PREFERENCES,
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            button_color=theme.COLOR_CARD_ELEVATED,
            button_hover_color=theme.COLOR_ACCENT,
            dropdown_fg_color=theme.COLOR_CARD_ELEVATED,
            dropdown_hover_color=theme.COLOR_ACCENT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.diet_opt.set(current_profile.diet_preference)
        self.diet_opt.pack(fill="x", pady=(0, 10))

        # 4. Food Restrictions & Allergies
        self._add_label(form, "FOOD ALLERGIES & RESTRICTIONS (OPTIONAL)")
        self.restrictions_entry = ctk.CTkEntry(
            form,
            placeholder_text="e.g. Peanuts, Lactose, Gluten, Soy, Seafood",
            height=36,
            fg_color=theme.COLOR_CARD_BG,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=8
        )
        self.restrictions_entry.insert(0, current_profile.restrictions)
        self.restrictions_entry.pack(fill="x", pady=(0, 12))

        # Feedback Toast
        self.feedback_label = ctk.CTkLabel(
            form,
            text="",
            font=ctk.CTkFont(size=theme.FONT_FEEDBACK[1], weight="bold"),
            text_color=theme.COLOR_ALERT
        )
        self.feedback_label.pack(fill="x", pady=(0, 8))

        # Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=24, pady=(10, 20))
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
            text="SAVE & REGENERATE PLAN",
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
        user_id = self.user.id if self.user else 1
        age_str = self.age_entry.get().strip()

        try:
            age_val = int(age_str)
            if age_val < 10 or age_val > 110:
                age_val = 25
        except ValueError:
            age_val = 25

        gender_val = self.gender_opt.get()
        activity_val = self.activity_opt.get()
        diet_val = self.diet_opt.get()
        restrictions_val = self.restrictions_entry.get().strip()

        self.nutrition_service.update_profile(
            user_id=user_id,
            age=age_val,
            gender=gender_val,
            activity_level=activity_val,
            diet_preference=diet_val,
            restrictions=restrictions_val
        )

        if self.on_profile_updated:
            self.on_profile_updated()

        self.destroy()
