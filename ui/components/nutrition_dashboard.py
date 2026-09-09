"""REPRIGHT AI - Nutrition & Diet Intelligence Dashboard.

Displays athlete dietary calculations, daily macronutrient targets,
interactive hydration logging, Indian-adapted meal plans, and post-workout recovery insights.
"""

from typing import Optional, Callable, Dict, Any
import customtkinter as ctk
from ui import theme
from services.user_session import UserSession
from database.models import User, NutritionProfile, NutritionPlan, HydrationLog
from services.nutrition_service import NutritionService
from ui.components.nutrition_profile import NutritionProfileDialog


class NutritionDashboardDialog(ctk.CTkToplevel):
    """Presentation-grade athlete nutrition & diet intelligence dashboard modal."""

    def __init__(
        self,
        master,
        user: Optional[User] = None,
        on_close_callback: Optional[Callable[[], None]] = None,
        nutrition_service: Optional[NutritionService] = None
    ):
        super().__init__(master)
        self.user = user or UserSession.get_instance().get_current_user()
        self.on_close_callback = on_close_callback
        self.nutrition_service = nutrition_service or NutritionService()

        self.title("REPRIGHT AI — Personalized Nutrition & Diet Intelligence")
        self.geometry("1000x740")
        self.minsize(880, 640)
        self.configure(fg_color=theme.COLOR_BG_DARK)

        self.transient(master)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        # Main scrollable canvas container to ensure seamless fit across monitor scaling
        self.scroll_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_container.pack(fill="both", expand=True, padx=20, pady=16)

        # 1. Athlete Header Card
        self.header_card = ctk.CTkFrame(
            self.scroll_container,
            fg_color=theme.COLOR_PANEL_BG,
            corner_radius=14,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        self.header_card.pack(fill="x", pady=(0, 14))

        # 2. Calorie & Macronutrient KPI Ribbon
        self.kpi_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.kpi_container.pack(fill="x", pady=(0, 14))
        for i in range(4):
            self.kpi_container.grid_columnconfigure(i, weight=1)

        # 3. Middle Section (Hydration Tracker & Recovery Insights)
        self.middle_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.middle_container.pack(fill="x", pady=(0, 14))
        self.middle_container.grid_columnconfigure(0, weight=1)
        self.middle_container.grid_columnconfigure(1, weight=1)

        # 4. Meal Plan Section
        self.meals_header_label = ctk.CTkLabel(
            self.scroll_container,
            text="PERSONALIZED DAILY MEAL PLAN (INDIAN ATHLETIC NUTRITION)",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1], weight=theme.FONT_SECTION_HEADER[2]),
            text_color=theme.COLOR_TEXT_MUTED
        )
        self.meals_header_label.pack(anchor="w", pady=(0, 8))

        self.meals_container = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        self.meals_container.pack(fill="x", pady=(0, 14))
        self.meals_container.grid_columnconfigure(0, weight=1)
        self.meals_container.grid_columnconfigure(1, weight=1)

        # 5. Non-Medical Disclaimer Banner
        self._render_disclaimer()

        # 6. Action Bar
        footer = ctk.CTkFrame(self.scroll_container, fg_color="transparent")
        footer.pack(fill="x", pady=(4, 10))

        regen_btn = ctk.CTkButton(
            footer,
            text="↺ REGENERATE PLAN",
            height=36,
            width=170,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_ELEVATED,
            hover_color=theme.COLOR_ACCENT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=theme.FONT_BUTTON[1], weight="bold"),
            command=self._regenerate_plan
        )
        regen_btn.pack(side="left")

        close_btn = ctk.CTkButton(
            footer,
            text="CLOSE DASHBOARD",
            height=36,
            width=160,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=self._on_close
        )
        close_btn.pack(side="right")

        # Initial Render
        self._refresh_all_views()

    def _refresh_all_views(self):
        user_id = self.user.id if self.user else 1
        self.plan, self.intelligence = self.nutrition_service.get_current_plan(user_id)
        self.profile = self.nutrition_service.get_or_create_profile(user_id)
        self.hydration = self.nutrition_service.get_daily_hydration(user_id)
        self.recovery_insight = self.nutrition_service.get_latest_recovery_insight(user_id)

        self._render_header()
        self._render_kpis()
        self._render_middle_section()
        self._render_meal_plans()

    # --------------------------------------------------------------------------
    # 1. Header Card
    # --------------------------------------------------------------------------
    def _render_header(self):
        for w in self.header_card.winfo_children():
            w.destroy()

        inner = ctk.CTkFrame(self.header_card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        # Left Info
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left", fill="y")

        badge = ctk.CTkLabel(
            left,
            text="ATHLETE NUTRITION INTELLIGENCE",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_TEAL,
            fg_color=theme.COLOR_TEAL_MUTED,
            corner_radius=4,
            height=18,
            padx=6
        )
        badge.pack(anchor="w", pady=(0, 2))

        user_name = self.user.name if self.user else "RepRight Athlete"
        user_email = self.user.email if self.user else "athlete@repright.ai"

        name_lbl = ctk.CTkLabel(
            left,
            text=user_name,
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1] + 4, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        name_lbl.pack(anchor="w")

        email_lbl = ctk.CTkLabel(
            left,
            text=f"{user_email} • Age {self.profile.age} • {self.profile.gender.title()}",
            font=ctk.CTkFont(size=theme.FONT_SUBTITLE[1]),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        email_lbl.pack(anchor="w")

        # Right Badges & Edit Button
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", padx=(20, 0))

        # Pills Row
        pill_row = ctk.CTkFrame(right, fg_color="transparent")
        pill_row.pack(anchor="e", pady=(0, 6))

        goal_text = (self.user.fitness_goal or "GENERAL_FITNESS").replace("_", " ") if self.user else "GENERAL FITNESS"
        diet_icon = "🌱 " if self.profile.diet_preference in ["VEGETARIAN", "VEGAN"] else "🍗 "
        diet_text = f"{diet_icon}{self.profile.diet_preference.replace('_', ' ')}"

        ctk.CTkLabel(
            pill_row,
            text=f"GOAL: {goal_text}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_SUCCESS,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=6,
            height=24,
            padx=10
        ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            pill_row,
            text=diet_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEAL,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=6,
            height=24,
            padx=10
        ).pack(side="left", padx=(0, 6))

        bmi_val = self.intelligence.get("energy_expenditure", {}).get("bmi", 22.5)
        bmi_cat = "Normal" if bmi_val < 25 else "Above Target"
        ctk.CTkLabel(
            pill_row,
            text=f"BMI {bmi_val:.1f} ({bmi_cat})",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_INFO,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=6,
            height=24,
            padx=10
        ).pack(side="left")

        # Profile Button
        edit_btn = ctk.CTkButton(
            right,
            text="⚙️ EDIT DIET & LIFESTYLE PROFILE",
            width=190,
            height=28,
            corner_radius=6,
            fg_color=theme.COLOR_CARD_ELEVATED,
            hover_color=theme.COLOR_ACCENT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=10, weight="bold"),
            command=self._open_profile_editor
        )
        edit_btn.pack(anchor="e")

    # --------------------------------------------------------------------------
    # 2. Macronutrient & Calorie KPI Ribbon
    # --------------------------------------------------------------------------
    def _render_kpis(self):
        for w in self.kpi_container.winfo_children():
            w.destroy()

        ee = self.intelligence.get("energy_expenditure", {})
        macros = self.intelligence.get("macronutrients", {})

        cal = ee.get("calorie_target", 2200)
        tdee = ee.get("tdee", 2200)
        p_g = macros.get("protein_g", 130)
        c_g = macros.get("carbs_g", 250)
        f_g = macros.get("fat_g", 65)

        total_cals = (p_g * 4) + (c_g * 4) + (f_g * 9)
        p_pct = (p_g * 4 / total_cals * 100) if total_cals > 0 else 25
        c_pct = (c_g * 4 / total_cals * 100) if total_cals > 0 else 50
        f_pct = (f_g * 9 / total_cals * 100) if total_cals > 0 else 25

        diff = cal - tdee
        diff_str = f"Deficit {-diff} kcal" if diff < -50 else (f"Surplus +{diff} kcal" if diff > 50 else "Maintenance Target")

        cards = [
            ("DAILY TARGET CALORIES", f"{cal:,} kcal", f"TDEE: {tdee:,} • {diff_str}", theme.COLOR_TEAL),
            ("PROTEIN TARGET", f"{p_g} g", f"{p_g*4} kcal • {p_pct:.0f}% of energy", theme.COLOR_SUCCESS),
            ("CARBOHYDRATE TARGET", f"{c_g} g", f"{c_g*4} kcal • {c_pct:.0f}% of energy", theme.COLOR_WARN),
            ("HEALTHY FATS TARGET", f"{f_g} g", f"{f_g*9} kcal • {f_pct:.0f}% of energy", theme.COLOR_ALERT)
        ]

        for idx, (label, val, sub, col) in enumerate(cards):
            card = ctk.CTkFrame(
                self.kpi_container,
                fg_color=theme.COLOR_PANEL_BG,
                corner_radius=12,
                border_width=1,
                border_color=theme.COLOR_BORDER
            )
            card.grid(row=0, column=idx, padx=4, sticky="nsew", ipady=6)

            ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=theme.COLOR_TEXT_MUTED
            ).pack(anchor="center", pady=(6, 2))

            ctk.CTkLabel(
                card,
                text=val,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=col
            ).pack(anchor="center", pady=(0, 2))

            ctk.CTkLabel(
                card,
                text=sub,
                font=ctk.CTkFont(size=10),
                text_color=theme.COLOR_TEXT_SECONDARY
            ).pack(anchor="center", pady=(0, 6))

    # --------------------------------------------------------------------------
    # 3. Middle Section: Hydration Tracker & Post-Workout Recovery
    # --------------------------------------------------------------------------
    def _render_middle_section(self):
        for w in self.middle_container.winfo_children():
            w.destroy()

        # Left: Daily Hydration Tracker
        hydration_card = ctk.CTkFrame(
            self.middle_container,
            fg_color=theme.COLOR_PANEL_BG,
            corner_radius=14,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        hydration_card.grid(row=0, column=0, padx=(0, 6), sticky="nsew", ipady=8)

        # Hydration Header
        h_head = ctk.CTkFrame(hydration_card, fg_color="transparent")
        h_head.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            h_head,
            text="💧 DAILY HYDRATION TRACKER",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme.COLOR_TEAL
        ).pack(side="left")

        target_badge = ctk.CTkLabel(
            h_head,
            text=f"Target: {self.hydration.target_ml} ml",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_SECONDARY,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=4,
            padx=6,
            height=20
        )
        target_badge.pack(side="right")

        # Hydration Metrics
        pct = min(100.0, (self.hydration.consumed_ml / max(1, self.hydration.target_ml)) * 100)
        m_frame = ctk.CTkFrame(hydration_card, fg_color="transparent")
        m_frame.pack(fill="x", padx=16, pady=(2, 4))

        ctk.CTkLabel(
            m_frame,
            text=f"{self.hydration.consumed_ml} ml Logged",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        ).pack(side="left")

        ctk.CTkLabel(
            m_frame,
            text=f"{pct:.0f}% Completed",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme.COLOR_SUCCESS if pct >= 100 else theme.COLOR_TEAL
        ).pack(side="right")

        # Progress Bar
        self.water_bar = ctk.CTkProgressBar(
            hydration_card,
            height=10,
            corner_radius=5,
            fg_color=theme.COLOR_CARD_BG,
            progress_color=theme.COLOR_TEAL
        )
        self.water_bar.pack(fill="x", padx=16, pady=(4, 10))
        self.water_bar.set(min(1.0, self.hydration.consumed_ml / max(1, self.hydration.target_ml)))

        # Quick Log Actions
        act_row = ctk.CTkFrame(hydration_card, fg_color="transparent")
        act_row.pack(fill="x", padx=16, pady=(0, 6))
        act_row.grid_columnconfigure(0, weight=1)
        act_row.grid_columnconfigure(1, weight=1)
        act_row.grid_columnconfigure(2, weight=1)

        glass_btn = ctk.CTkButton(
            act_row,
            text="+250 ml Glass",
            height=30,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            text_color=theme.COLOR_TEAL,
            command=lambda: self._log_water(250)
        )
        glass_btn.grid(row=0, column=0, padx=(0, 4), sticky="ew")

        bottle_btn = ctk.CTkButton(
            act_row,
            text="+500 ml Bottle",
            height=30,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            text_color=theme.COLOR_TEAL,
            command=lambda: self._log_water(500)
        )
        bottle_btn.grid(row=0, column=1, padx=2, sticky="ew")

        reset_btn = ctk.CTkButton(
            act_row,
            text="↺ Reset",
            height=30,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            text_color=theme.COLOR_TEXT_MUTED,
            command=self._reset_water
        )
        reset_btn.grid(row=0, column=2, padx=(4, 0), sticky="ew")

        # Tip
        ctk.CTkLabel(
            hydration_card,
            text="Active athletic hydration sustains joint synovial fluid and muscle recovery.",
            font=ctk.CTkFont(size=9),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=16, pady=(4, 8))

        # Right: Post-Workout Recovery Nutrition
        recovery_card = ctk.CTkFrame(
            self.middle_container,
            fg_color=theme.COLOR_PANEL_BG,
            corner_radius=14,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        recovery_card.grid(row=0, column=1, padx=(6, 0), sticky="nsew", ipady=8)

        # Recovery Header
        r_head = ctk.CTkFrame(recovery_card, fg_color="transparent")
        r_head.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            r_head,
            text="⚡ POST-WORKOUT RECOVERY NUTRITION",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme.COLOR_WARN
        ).pack(side="left")

        ex_name = self.recovery_insight.get("exercise_name", "TRAINING")
        ex_badge = ctk.CTkLabel(
            r_head,
            text=f"Session: {ex_name}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_WARN,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=4,
            padx=6,
            height=20
        )
        ex_badge.pack(side="right")

        # Ratio & Window
        ratio_str = self.recovery_insight.get("carb_to_protein_ratio", "3:1")
        window_str = self.recovery_insight.get("recovery_window_minutes", 45)

        r_sub = ctk.CTkLabel(
            recovery_card,
            text=f"Metabolic Window: Within {window_str} mins • Target Ratio: {ratio_str} (Carbs : Protein)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        r_sub.pack(anchor="w", padx=16, pady=(2, 4))

        # Hydration & Electrolyte Tip
        hydro_tip = self.recovery_insight.get("hydration_advice", "Rehydrate with 500ml water + electrolytes.")
        ctk.CTkLabel(
            recovery_card,
            text=f"Hydration Tip: {hydro_tip}",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_SECONDARY,
            wraplength=420,
            justify="left"
        ).pack(anchor="w", padx=16, pady=(0, 6))

        # Recommended Recovery Options
        snacks = self.recovery_insight.get("suggested_snacks", [])
        snacks_text = " • ".join(snacks[:3]) if snacks else "Sattu buttermilk • Banana with peanut butter • Whey protein"

        snack_box = ctk.CTkFrame(recovery_card, fg_color=theme.COLOR_CARD_BG, corner_radius=8, border_width=1, border_color=theme.COLOR_BORDER)
        snack_box.pack(fill="x", padx=16, pady=(0, 8), ipady=4)

        ctk.CTkLabel(
            snack_box,
            text="RECOMMENDED POST-SESSION FUEL:",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=8, pady=(2, 0))

        ctk.CTkLabel(
            snack_box,
            text=snacks_text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_SUCCESS,
            wraplength=410,
            justify="left"
        ).pack(anchor="w", padx=8, pady=(1, 4))

    # --------------------------------------------------------------------------
    # 4. Indian-Adapted Meal Plan Grid (4 Cards: Breakfast, Lunch, Snack, Dinner)
    # --------------------------------------------------------------------------
    def _render_meal_plans(self):
        for w in self.meals_container.winfo_children():
            w.destroy()

        meal_plan = self.intelligence.get("meal_plan", {})
        meal_types = [
            ("breakfast", "BREAKFAST", "Morning Energy Boost (~25%)", 0, 0),
            ("lunch", "LUNCH", "Mid-Day Power Meal (~35%)", 0, 1),
            ("snacks", "EVENING SNACK", "Pre/Post Training Fuel (~15%)", 1, 0),
            ("dinner", "DINNER", "Night-Time Tissue Repair (~25%)", 1, 1)
        ]

        for key, title, subtitle, r, c in meal_types:
            meal_data = meal_plan.get(key, {})
            primary = meal_data.get("primary", {})
            alt = meal_data.get("alternative", {})

            card = ctk.CTkFrame(
                self.meals_container,
                fg_color=theme.COLOR_PANEL_BG,
                corner_radius=14,
                border_width=1,
                border_color=theme.COLOR_BORDER
            )
            card.grid(row=r, column=c, padx=4, pady=4, sticky="nsew", ipady=8)

            # Card Header
            chead = ctk.CTkFrame(card, fg_color="transparent")
            chead.pack(fill="x", padx=16, pady=(10, 4))

            ctk.CTkLabel(
                chead,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=theme.COLOR_TEAL
            ).pack(side="left")

            ctk.CTkLabel(
                chead,
                text=subtitle,
                font=ctk.CTkFont(size=9),
                text_color=theme.COLOR_TEXT_MUTED
            ).pack(side="right")

            # Primary Item
            name = primary.get("name", "Nutritious Indian Athletic Dish")
            portion = primary.get("portion", "Standard 1 portion")
            p_val = primary.get("protein_g", 25)
            cal_val = primary.get("calories", 450)
            notes = primary.get("notes", "Clean whole food nutrition")

            p_box = ctk.CTkFrame(card, fg_color=theme.COLOR_CARD_BG, corner_radius=8, border_width=1, border_color=theme.COLOR_BORDER)
            p_box.pack(fill="x", padx=16, pady=(2, 6), ipady=4)

            p_title_row = ctk.CTkFrame(p_box, fg_color="transparent")
            p_title_row.pack(fill="x", padx=8, pady=(4, 2))

            ctk.CTkLabel(
                p_title_row,
                text=name,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=theme.COLOR_TEXT_PRIMARY,
                wraplength=260,
                justify="left"
            ).pack(side="left")

            badges_right = ctk.CTkFrame(p_title_row, fg_color="transparent")
            badges_right.pack(side="right")

            ctk.CTkLabel(
                badges_right,
                text=f"{p_val}g Protein",
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=theme.COLOR_SUCCESS,
                fg_color=theme.COLOR_PANEL_BG,
                corner_radius=4,
                padx=6,
                height=18
            ).pack(side="left", padx=(0, 4))

            ctk.CTkLabel(
                badges_right,
                text=f"{cal_val} kcal",
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=theme.COLOR_TEXT_MUTED,
                fg_color=theme.COLOR_PANEL_BG,
                corner_radius=4,
                padx=6,
                height=18
            ).pack(side="left")

            ctk.CTkLabel(
                p_box,
                text=f"Portion: {portion}",
                font=ctk.CTkFont(size=10),
                text_color=theme.COLOR_TEXT_SECONDARY
            ).pack(anchor="w", padx=8, pady=(0, 2))

            ctk.CTkLabel(
                p_box,
                text=f"Highlight: {notes}",
                font=ctk.CTkFont(size=9),
                text_color=theme.COLOR_INFO
            ).pack(anchor="w", padx=8, pady=(0, 4))

            # Alternative Item
            alt_name = alt.get("name", "Alternative Option")
            alt_prot = alt.get("protein_g", 20)
            alt_cal = alt.get("calories", 400)

            alt_frame = ctk.CTkFrame(card, fg_color="transparent")
            alt_frame.pack(fill="x", padx=16, pady=(0, 4))

            ctk.CTkLabel(
                alt_frame,
                text=f"Option B: {alt_name} ({alt_prot}g P • {alt_cal} kcal)",
                font=ctk.CTkFont(size=9),
                text_color=theme.COLOR_TEXT_MUTED,
                wraplength=420,
                justify="left"
            ).pack(anchor="w")

    # --------------------------------------------------------------------------
    # 5. Non-Medical Disclaimer Banner
    # --------------------------------------------------------------------------
    def _render_disclaimer(self):
        disc_box = ctk.CTkFrame(
            self.scroll_container,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        disc_box.pack(fill="x", pady=(4, 12), ipady=6)

        ctk.CTkLabel(
            disc_box,
            text="⚠️ EDUCATIONAL ATHLETIC WELLNESS RECOMMENDATION",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_WARN
        ).pack(anchor="w", padx=14, pady=(4, 2))

        ctk.CTkLabel(
            disc_box,
            text=(
                "All caloric estimations, macronutrient allocations, and meal suggestions are generated for general athletic conditioning "
                "and lifestyle optimization. They do not constitute medical diagnosis, prescription, or clinical nutritional therapy. "
                "Individuals with metabolic conditions, diabetes, allergies, or gastrointestinal disorders should consult a licensed physician or registered sports dietitian."
            ),
            font=ctk.CTkFont(size=9),
            text_color=theme.COLOR_TEXT_MUTED,
            wraplength=920,
            justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 4))

    # --------------------------------------------------------------------------
    # Actions & Callbacks
    # --------------------------------------------------------------------------
    def _log_water(self, amount_ml: int):
        user_id = self.user.id if self.user else 1
        self.hydration = self.nutrition_service.log_water(user_id, amount_ml)
        self._render_middle_section()

    def _reset_water(self):
        user_id = self.user.id if self.user else 1
        self.hydration = self.nutrition_service.reset_water(user_id)
        self._render_middle_section()

    def _open_profile_editor(self):
        NutritionProfileDialog(
            self,
            user=self.user,
            on_profile_updated=self._on_profile_updated,
            nutrition_service=self.nutrition_service
        )

    def _on_profile_updated(self):
        self._refresh_all_views()

    def _regenerate_plan(self):
        user_id = self.user.id if self.user else 1
        self.nutrition_service.generate_and_save_plan(user_id)
        self._refresh_all_views()

    def _on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
