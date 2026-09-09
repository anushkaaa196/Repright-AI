"""Sidebar component containing controls, telemetry quick-view, and exercise selection (Phase 7).

Refined for SIH Presentation with a clutter-free two-section responsive layout:
- TOP SECTION: Scrollable content (Branding, Exercise, Quick View, Analytics Shortcuts, Collapsible Goals)
- BOTTOM SECTION: Pinned dedicated workout action controls (START, STOP, EXPORT, RESET)
"""

from typing import Callable, Optional, List
import customtkinter as ctk
from ui import theme
from ui.components.session_goal import SessionGoalCard
from ui.components.collapsible_card import CollapsibleCard
from ui.components.analytics_navigation import QuickAnalyticsMenu


class SidebarFrame(ctk.CTkFrame):
    """Clean AI analytics sidebar with responsive two-part architecture and pinned workout controls."""

    def __init__(
        self,
        master,
        exercise_list: List[str],
        on_exercise_selected: Optional[Callable[[str], None]] = None,
        on_toggle_session: Optional[Callable[[], None]] = None,
        on_start_workout: Optional[Callable[[], None]] = None,
        on_stop_workout: Optional[Callable[[], None]] = None,
        on_export_report: Optional[Callable[[], None]] = None,
        on_reset_metrics: Optional[Callable[[], None]] = None,
        on_explore_library: Optional[Callable[[], None]] = None,
        on_open_analytics_hub: Optional[Callable[[str], None]] = None,
        on_view_plan: Optional[Callable[[], None]] = None,
        on_view_progress: Optional[Callable[[], None]] = None,
        on_open_dashboard: Optional[Callable[[], None]] = None,
        on_open_nutrition: Optional[Callable[[], None]] = None,
        on_logout: Optional[Callable[[], None]] = None,
        on_find_gyms: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            width=290,
            corner_radius=16,
            fg_color=theme.COLOR_PANEL_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            **kwargs
        )

        self.on_exercise_selected = on_exercise_selected
        self.on_toggle_session = on_toggle_session
        self.on_start_workout = on_start_workout
        self.on_stop_workout = on_stop_workout
        self.on_export_report = on_export_report
        self.on_reset_metrics = on_reset_metrics
        self.on_explore_library = on_explore_library
        self.on_open_analytics_hub = on_open_analytics_hub
        self.on_view_plan = on_view_plan
        self.on_view_progress = on_view_progress
        self.on_open_dashboard = on_open_dashboard
        self.on_open_nutrition = on_open_nutrition
        self.on_logout = on_logout
        self.on_find_gyms = on_find_gyms
        self.is_running = False


        # ======================================================================
        # TWO-PART RESPONSIVE LAYOUT CONFIGURATION
        # Row 0: Scrollable content (weight=1)
        # Row 1: Dedicated Workout Controls (weight=0, pinned)
        # ======================================================================
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # ----------------------------------------------------------------------
        # UPPER AREA: SCROLLABLE SIDEBAR CONTENT (Row 0)
        # ----------------------------------------------------------------------
        self.scrollable_area = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scrollable_area.grid(row=0, column=0, sticky="nsew", padx=0, pady=(6, 0))

        # 1. BRANDING & PRODUCT IDENTITY
        self.brand_frame = ctk.CTkFrame(self.scrollable_area, fg_color="transparent")
        self.brand_frame.pack(padx=16, pady=(10, 8), fill="x")

        self.badge_label = ctk.CTkLabel(
            self.brand_frame,
            text="BIOMECHANICS & PERFORMANCE LAB",
            font=ctk.CTkFont(size=theme.FONT_BRAND_BADGE[1], weight=theme.FONT_BRAND_BADGE[2]),
            text_color=theme.COLOR_TEAL,
            fg_color=theme.COLOR_TEAL_MUTED,
            corner_radius=4,
            height=20,
            padx=8
        )
        self.badge_label.pack(anchor="w", pady=(0, 4))

        self.logo_label = ctk.CTkLabel(
            self.brand_frame,
            text="REPRIGHT AI",
            font=ctk.CTkFont(size=theme.FONT_BRAND[1], weight=theme.FONT_BRAND[2]),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.logo_label.pack(anchor="w")

        self.subtitle = ctk.CTkLabel(
            self.brand_frame,
            text="Athletic Motion Intelligence System",
            font=ctk.CTkFont(size=theme.FONT_SUBTITLE[1]),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        self.subtitle.pack(anchor="w", pady=(1, 0))

        # 1.5 ATHLETE PROFILE BADGE
        self.user_frame = ctk.CTkFrame(
            self.scrollable_area,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        self.user_frame.pack(padx=16, pady=(8, 4), fill="x")
        self._build_user_section()

        self._add_divider(self.scrollable_area)

        # 2. EXERCISE CONFIGURATION & QUICK ANALYTICS
        self.exercise_frame = ctk.CTkFrame(self.scrollable_area, fg_color="transparent")
        self.exercise_frame.pack(padx=16, pady=4, fill="x")

        self.sel_label = ctk.CTkLabel(
            self.exercise_frame,
            text="EXERCISE PROTOCOL",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1], weight=theme.FONT_SECTION_HEADER[2]),
            text_color=theme.COLOR_TEXT_MUTED
        )
        self.sel_label.pack(anchor="w", pady=(0, 4))

        self.exercise_opt = ctk.CTkOptionMenu(
            self.exercise_frame,
            values=exercise_list,
            command=self._handle_exercise_change,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=theme.FONT_OPTION_MENU[1], weight=theme.FONT_OPTION_MENU[2]),
            fg_color=theme.COLOR_CARD_BG,
            button_color=theme.COLOR_CARD_ELEVATED,
            button_hover_color=theme.COLOR_ACCENT,
            dropdown_fg_color=theme.COLOR_CARD_ELEVATED,
            dropdown_hover_color=theme.COLOR_ACCENT,
            dropdown_text_color=theme.COLOR_TEXT_PRIMARY,
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.exercise_opt.pack(fill="x", pady=(0, 6))

        # Explore Button
        if self.on_explore_library:
            self.btn_explore = ctk.CTkButton(
                self.exercise_frame,
                text="EXERCISE LIBRARY",
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
                height=28,
                corner_radius=6,
                fg_color=theme.COLOR_CARD_BG,
                hover_color=theme.COLOR_CARD_ELEVATED,
                border_width=1,
                border_color=theme.COLOR_BORDER,
                text_color=theme.COLOR_TEXT_SECONDARY,
                command=self.on_explore_library
            )
            self.btn_explore.pack(fill="x", pady=(0, 6))
        else:
            self.btn_explore = None

        # Gym Locator Button
        if self.on_find_gyms:
            self.btn_gyms = ctk.CTkButton(
                self.exercise_frame,
                text="📍 FIND NEARBY GYMS",
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
                height=28,
                corner_radius=6,
                fg_color=theme.COLOR_CARD_BG,
                hover_color=theme.COLOR_CARD_ELEVATED,
                border_width=1,
                border_color=theme.COLOR_BORDER,
                text_color=theme.COLOR_TEAL,
                command=self.on_find_gyms
            )
            self.btn_gyms.pack(fill="x", pady=(0, 6))
        else:
            self.btn_gyms = None

        # Quick Analytics Dropdown Selector
        self.quick_analytics = QuickAnalyticsMenu(
            self.exercise_frame,
            on_select_analytics=self._handle_quick_analytics
        )
        self.quick_analytics.pack(fill="x", pady=(0, 2))

        self._add_divider(self.scrollable_area)

        # 3. SESSION QUICK VIEW
        self.telemetry_frame = ctk.CTkFrame(self.scrollable_area, fg_color="transparent")
        self.telemetry_frame.pack(padx=16, pady=4, fill="x")

        ctk.CTkLabel(
            self.telemetry_frame,
            text="SESSION QUICK VIEW",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1], weight=theme.FONT_SECTION_HEADER[2]),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))

        self.stats_card = ctk.CTkFrame(
            self.telemetry_frame,
            corner_radius=10,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        self.stats_card.pack(fill="x")

        # Subtle top accent strip for depth
        self.stats_accent = ctk.CTkFrame(
            self.stats_card,
            height=3,
            corner_radius=2,
            fg_color=theme.COLOR_TEAL
        )
        self.stats_accent.pack(fill="x", padx=4, pady=(3, 0))

        q_row = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        q_row.pack(fill="x", padx=12, pady=(6, 4))
        q_row.grid_columnconfigure((0, 1), weight=1)

        # Clean Reps
        c_left = ctk.CTkFrame(q_row, fg_color="transparent")
        c_left.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(c_left, text="Clean Reps", font=ctk.CTkFont(size=9), text_color=theme.COLOR_TEXT_MUTED).pack(anchor="w")
        self.rep_val = ctk.CTkLabel(c_left, text="0", font=ctk.CTkFont(size=20, weight="bold"), text_color=theme.COLOR_TEAL)
        self.rep_val.pack(anchor="w")

        # Form Score
        c_right = ctk.CTkFrame(q_row, fg_color="transparent")
        c_right.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(c_right, text="Form Score", font=ctk.CTkFont(size=9), text_color=theme.COLOR_TEXT_MUTED).pack(anchor="e")
        self.acc_val = ctk.CTkLabel(c_right, text="100%", font=ctk.CTkFont(size=20, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.acc_val.pack(anchor="e")

        self.acc_bar = ctk.CTkProgressBar(
            self.stats_card,
            height=4,
            corner_radius=2,
            fg_color=theme.COLOR_CARD_INNER,
            progress_color=theme.COLOR_SUCCESS
        )
        self.acc_bar.pack(fill="x", padx=12, pady=(2, 8))
        self.acc_bar.set(1.0)

        # Backward compatibility label references
        self.rep_title = ctk.CTkLabel(self.stats_card, text="")
        self.acc_title = ctk.CTkLabel(self.stats_card, text="")
        self.exercise_desc = ctk.CTkLabel(self.exercise_frame, text="")

        self._add_divider(self.scrollable_area)

        # 4. ANALYTICS SHORTCUTS
        self.actions_menu_frame = ctk.CTkFrame(self.scrollable_area, fg_color="transparent")
        self.actions_menu_frame.pack(padx=16, pady=4, fill="x")

        ctk.CTkLabel(
            self.actions_menu_frame,
            text="PERFORMANCE MODULES",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1], weight=theme.FONT_SECTION_HEADER[2]),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(anchor="w", pady=(0, 4))

        self.btn_view_analytics = ctk.CTkButton(
            self.actions_menu_frame,
            text="ANALYTICS HUB",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
            height=30,
            corner_radius=6,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=lambda: self._handle_quick_analytics("OVERVIEW")
        )
        self.btn_view_analytics.pack(fill="x", pady=(0, 4))

        self.intel_row = ctk.CTkFrame(self.actions_menu_frame, fg_color="transparent")
        self.intel_row.pack(fill="x", pady=(0, 4))
        self.intel_row.grid_columnconfigure((0, 1), weight=1)

        self.btn_plan = ctk.CTkButton(
            self.intel_row,
            text="COACHING PLAN",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
            height=28,
            corner_radius=6,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_SECONDARY,
            command=self.on_view_plan
        )
        self.btn_plan.grid(row=0, column=0, padx=(0, 2), sticky="ew")

        self.btn_prog = ctk.CTkButton(
            self.intel_row,
            text="PROGRESSION",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
            height=28,
            corner_radius=6,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_SECONDARY,
            command=self.on_view_progress
        )
        self.btn_prog.grid(row=0, column=1, padx=(2, 0), sticky="ew")

        # 5. COLLAPSIBLE SESSION GOAL
        curr_ex = exercise_list[0] if exercise_list else "SQUAT"
        self.goal_collapse = CollapsibleCard(
            self.scrollable_area,
            title="SESSION GOAL",
            initial_expanded=False,
            badge_text="TARGET: 10 REPS"
        )
        self.goal_collapse.pack(padx=16, pady=6, fill="x")

        self.goal_card = SessionGoalCard(self.goal_collapse.content_frame, current_exercise=curr_ex)
        self.goal_card.pack(fill="x", padx=4, pady=4)

        # ----------------------------------------------------------------------
        # LOWER AREA: PINNED DEDICATED WORKOUT CONTROLS (Row 1)
        # ----------------------------------------------------------------------
        self.controls_frame = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_PANEL_BG,
            corner_radius=0
        )
        self.controls_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 6))

        top_ctrl_divider = ctk.CTkFrame(self.controls_frame, height=1, fg_color=theme.COLOR_DIVIDER)
        top_ctrl_divider.pack(fill="x", padx=16, pady=(2, 6))

        self.ctrl_label = ctk.CTkLabel(
            self.controls_frame,
            text="WORKOUT CONTROLS",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1], weight=theme.FONT_SECTION_HEADER[2]),
            text_color=theme.COLOR_TEXT_MUTED
        )
        self.ctrl_label.pack(anchor="w", padx=16, pady=(0, 6))

        # 1. START WORKOUT (Energetic Emerald)
        self.btn_start = ctk.CTkButton(
            self.controls_frame,
            text="START WORKOUT",
            fg_color=theme.COLOR_BTN_START,
            hover_color=theme.COLOR_BTN_START_HOVER,
            text_color=theme.COLOR_WHITE,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=theme.FONT_BUTTON_MEDIUM[1], weight="bold"),
            command=self._handle_start
        )
        self.btn_start.pack(fill="x", padx=16, pady=(0, 5))

        # 2. STOP WORKOUT (Prominent Red when Active, Subtle Inactive State)
        self.btn_stop = ctk.CTkButton(
            self.controls_frame,
            text="STOP WORKOUT",
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_BTN_STOP_HOVER,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_MUTED,
            height=38,
            corner_radius=8,
            font=ctk.CTkFont(size=theme.FONT_BUTTON_MEDIUM[1], weight="bold"),
            command=self._handle_stop,
            state="disabled"
        )
        self.btn_stop.pack(fill="x", padx=16, pady=(0, 5))

        # 3. EXPORT REPORT (Professional Blue)
        self.btn_report = ctk.CTkButton(
            self.controls_frame,
            text="EXPORT REPORT",
            fg_color=theme.COLOR_BTN_EXPORT,
            hover_color=theme.COLOR_BTN_EXPORT_HOVER,
            text_color=theme.COLOR_WHITE,
            height=34,
            corner_radius=8,
            font=ctk.CTkFont(size=theme.FONT_BUTTON_MEDIUM[1], weight="bold"),
            command=self._handle_report
        )
        self.btn_report.pack(fill="x", padx=16, pady=(0, 5))

        # 4. RESET METRICS (Secondary Outlined Slate)
        self.btn_reset = ctk.CTkButton(
            self.controls_frame,
            text="RESET METRICS",
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            border_width=1,
            border_color=theme.COLOR_BORDER_LIGHT,
            text_color=theme.COLOR_TEXT_SECONDARY,
            height=34,
            corner_radius=8,
            font=ctk.CTkFont(size=theme.FONT_BUTTON_MEDIUM[1], weight="bold"),
            command=self._handle_reset
        )
        self.btn_reset.pack(fill="x", padx=16, pady=(0, 6))

        self.btn_toggle = self.btn_start

        # Footer indicator
        self.footer_label = ctk.CTkLabel(
            self.controls_frame,
            text="REPRIGHT AI • Performance Analytics",
            font=ctk.CTkFont(size=theme.FONT_FOOTER[1]),
            text_color=theme.COLOR_TEXT_MUTED,
            justify="center"
        )
        self.footer_label.pack(fill="x", padx=16, pady=(1, 4))

    def _add_divider(self, parent=None):
        """Adds a subtle horizontal divider line between sections."""
        target = parent or self.scrollable_area
        divider = ctk.CTkFrame(target, height=1, fg_color=theme.COLOR_DIVIDER)
        divider.pack(fill="x", padx=16, pady=4)

    def _handle_exercise_change(self, choice: str):
        if self.on_exercise_selected:
            self.on_exercise_selected(choice)

    def _handle_quick_analytics(self, tab_key: str):
        """Opens the dedicated Analytics Hub to the selected tab."""
        if self.on_open_analytics_hub:
            self.on_open_analytics_hub(tab_key)

    def _handle_start(self):
        """Starts workout session if currently stopped."""
        if not self.is_running:
            if self.on_start_workout:
                self.on_start_workout()
            elif self.on_toggle_session:
                self.on_toggle_session()

    def _handle_stop(self):
        """Stops workout session if currently running."""
        if self.is_running:
            if self.on_stop_workout:
                self.on_stop_workout()
            elif self.on_toggle_session:
                self.on_toggle_session()

    def _handle_toggle(self):
        """Backward-compatible toggle handler."""
        if not self.is_running:
            self._handle_start()
        else:
            self._handle_stop()

    def _handle_report(self):
        if self.on_export_report:
            self.on_export_report()

    def _handle_reset(self):
        self.reset_phase5()
        if self.on_reset_metrics:
            self.on_reset_metrics()

    def set_session_state(self, is_running: bool):
        """Updates start and stop button states and styles."""
        self.is_running = is_running
        if is_running:
            self.btn_start.configure(
                state="disabled",
                fg_color=theme.COLOR_CARD_BG,
                text_color=theme.COLOR_TEXT_MUTED
            )
            self.btn_stop.configure(
                state="normal",
                fg_color=theme.COLOR_BTN_STOP,
                hover_color=theme.COLOR_BTN_STOP_HOVER,
                border_color=theme.COLOR_BTN_STOP,
                text_color=theme.COLOR_WHITE
            )
        else:
            self.btn_start.configure(
                state="normal",
                fg_color=theme.COLOR_BTN_START,
                hover_color=theme.COLOR_BTN_START_HOVER,
                text_color=theme.COLOR_WHITE
            )
            self.btn_stop.configure(
                state="disabled",
                fg_color=theme.COLOR_CARD_BG,
                border_color=theme.COLOR_BORDER,
                text_color=theme.COLOR_TEXT_MUTED
            )
        self.btn_report.configure(state="normal")
        self.btn_reset.configure(state="normal")

    def update_stats(self, reps: int, acc: int):
        """Updates quick view metrics values and progress bar."""
        self.rep_val.configure(text=str(reps))
        acc_color = (
            theme.COLOR_SUCCESS if acc >= 80
            else theme.COLOR_WARN if acc >= 50
            else theme.COLOR_ALERT
        )
        self.acc_val.configure(text=f"{acc}%", text_color=acc_color)
        fraction = max(0.0, min(1.0, float(acc) / 100.0))
        self.acc_bar.set(fraction)
        self.acc_bar.configure(progress_color=acc_color)

    def update_goal_progress(self, clean_reps: int, accuracy: int, exercise_name: Optional[str] = None):
        """Updates the session goal card progress bar."""
        self.goal_card.update_progress(clean_reps, accuracy, exercise_name)
        if clean_reps > 0:
            self.goal_collapse.set_badge(f"{clean_reps}/10 REPS", theme.COLOR_SUCCESS)

    def reset_phase5(self):
        """Resets the goal card progress."""
        self.goal_card.reset()
        self.goal_collapse.set_badge("TARGET: 10 REPS", theme.COLOR_ACCENT)

    def set_exercise_selection(self, exercise_name: str):
        """Programmatically updates the dropdown to display the selected exercise."""
        val = exercise_name.upper().strip()
        if val in self.exercise_opt.cget("values"):
            self.exercise_opt.set(val)
        self.goal_card.reset()
        self.goal_card.update_progress(0, 100, exercise_name)

    def _build_user_section(self):
        """Builds the compact athlete identity card in the sidebar."""
        for w in self.user_frame.winfo_children():
            w.destroy()

        from services.user_session import UserSession
        user = UserSession.get_instance().get_current_user()
        user_name = user.name if user else "Athlete (Guest)"
        goal = user.fitness_goal if user else "GENERAL_FITNESS"

        # Top row: User name & Goal
        top_row = ctk.CTkFrame(self.user_frame, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=(8, 2))

        name_lbl = ctk.CTkLabel(
            top_row,
            text=f"👤 {user_name}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        name_lbl.pack(side="left")

        goal_lbl = ctk.CTkLabel(
            top_row,
            text=goal.replace("_", " "),
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_TEAL,
            fg_color=theme.COLOR_TEAL_MUTED,
            corner_radius=4,
            height=18,
            padx=6
        )
        goal_lbl.pack(side="right")

        # Action row 1: Athlete Hubs (Dashboard & Nutrition)
        act_row1 = ctk.CTkFrame(self.user_frame, fg_color="transparent")
        act_row1.pack(fill="x", padx=10, pady=(4, 2))
        act_row1.grid_columnconfigure(0, weight=1)
        act_row1.grid_columnconfigure(1, weight=1)

        dash_btn = ctk.CTkButton(
            act_row1,
            text="MY DASHBOARD",
            height=26,
            corner_radius=6,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=theme.COLOR_CARD_ELEVATED,
            hover_color=theme.COLOR_ACCENT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=self._handle_open_dashboard
        )
        dash_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))

        nutrition_btn = ctk.CTkButton(
            act_row1,
            text="🥗 NUTRITION",
            height=26,
            corner_radius=6,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=theme.COLOR_CARD_ELEVATED,
            hover_color=theme.COLOR_ACCENT,
            text_color=theme.COLOR_TEAL,
            command=self._handle_open_nutrition
        )
        nutrition_btn.grid(row=0, column=1, sticky="ew", padx=(2, 0))

        # Action row 2: Session Logout
        act_row2 = ctk.CTkFrame(self.user_frame, fg_color="transparent")
        act_row2.pack(fill="x", padx=10, pady=(2, 8))

        logout_btn = ctk.CTkButton(
            act_row2,
            text="LOGOUT",
            height=24,
            corner_radius=6,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=theme.COLOR_PANEL_BG,
            hover_color=theme.COLOR_ALERT,
            text_color=theme.COLOR_TEXT_MUTED,
            command=self._handle_logout
        )
        logout_btn.pack(fill="x")

    def _handle_open_dashboard(self):
        if self.on_open_dashboard:
            self.on_open_dashboard()

    def _handle_open_nutrition(self):
        if self.on_open_nutrition:
            self.on_open_nutrition()

    def _handle_logout(self):
        if self.on_logout:
            self.on_logout()

    def set_user(self, user=None):
        """Refreshes the user profile badge display."""
        self._build_user_section()

