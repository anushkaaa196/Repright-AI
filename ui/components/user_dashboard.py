"""REPRIGHT AI - Athlete Performance & History Dashboard.

Comprehensive biometric and performance telemetry intelligence dashboard.
Displays lifetime training volume, quality metrics, exercise distribution, and workout archives.
"""

from typing import Optional, Callable
import customtkinter as ctk
from ui import theme
from services.user_session import UserSession
from database.models import User
from database.workout_repository import WorkoutRepository
from ui.components.workout_history import WorkoutHistoryView
from ui.components.user_profile import UserProfileDialog


class UserDashboardDialog(ctk.CTkToplevel):
    """Presentation-grade athlete dashboard modal for REPRIGHT AI."""

    def __init__(
        self,
        master,
        user: Optional[User] = None,
        on_close_callback: Optional[Callable[[], None]] = None,
        workout_repo: Optional[WorkoutRepository] = None
    ):
        super().__init__(master)
        self.user = user or UserSession.get_instance().get_current_user()
        self.on_close_callback = on_close_callback
        self.workout_repo = workout_repo or WorkoutRepository()

        self.title("REPRIGHT AI — Athlete Intelligence Dashboard")
        self.geometry("980x700")
        self.minsize(860, 600)
        self.configure(fg_color=theme.COLOR_BG_DARK)

        self.transient(master)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        self.container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.container.pack(fill="both", expand=True, padx=20, pady=16)

        # ----------------------------------------------------------------------
        # 1. ATHLETE PROFILE HEADER CARD
        # ----------------------------------------------------------------------
        self.profile_card = ctk.CTkFrame(
            self.container,
            fg_color=theme.COLOR_PANEL_BG,
            corner_radius=14,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        self.profile_card.pack(fill="x", pady=(0, 14))

        self._render_profile_card()

        # ----------------------------------------------------------------------
        # 2. LIFETIME PERFORMANCE KPI RIBBON
        # ----------------------------------------------------------------------
        self.kpi_container = ctk.CTkFrame(self.container, fg_color="transparent")
        self.kpi_container.pack(fill="x", pady=(0, 14))
        for i in range(4):
            self.kpi_container.grid_columnconfigure(i, weight=1)

        self._render_kpis()

        # ----------------------------------------------------------------------
        # 3. SAVED WORKOUT HISTORY LOG & DRILLDOWN
        # ----------------------------------------------------------------------
        hist_label = ctk.CTkLabel(
            self.container,
            text="SAVED WORKOUT SESSIONS & TELEMETRY ARCHIVE",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1], weight=theme.FONT_SECTION_HEADER[2]),
            text_color=theme.COLOR_TEXT_MUTED
        )
        hist_label.pack(anchor="w", pady=(0, 6))

        user_id = self.user.id if self.user else 1
        self.history_view = WorkoutHistoryView(
            self.container,
            user_id=user_id,
            workout_repo=self.workout_repo
        )
        self.history_view.pack(fill="both", expand=True, pady=(0, 10))

        # ----------------------------------------------------------------------
        # 4. FOOTER ACTION BAR
        # ----------------------------------------------------------------------
        footer = ctk.CTkFrame(self.container, fg_color="transparent")
        footer.pack(fill="x")

        close_btn = ctk.CTkButton(
            footer,
            text="CLOSE DASHBOARD",
            height=38,
            width=160,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=self._on_close
        )
        close_btn.pack(side="right")

    def _render_profile_card(self):
        for w in self.profile_card.winfo_children():
            w.destroy()

        inner = ctk.CTkFrame(self.profile_card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        # Left Column: Avatar & Name
        left = ctk.CTkFrame(inner, fg_color="transparent")
        left.pack(side="left")

        user_name = self.user.name if self.user else "RepRight Athlete"
        user_email = self.user.email if self.user else "guest@repright.ai"
        goal = self.user.fitness_goal if self.user else "STRENGTH"

        # Badge
        badge = ctk.CTkLabel(
            left,
            text="VERIFIED ATHLETE",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_TEAL,
            fg_color=theme.COLOR_TEAL_MUTED,
            corner_radius=4,
            height=18,
            padx=6
        )
        badge.pack(anchor="w", pady=(0, 2))

        name_lbl = ctk.CTkLabel(
            left,
            text=user_name,
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1] + 6, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        name_lbl.pack(anchor="w")

        email_lbl = ctk.CTkLabel(
            left,
            text=user_email,
            font=ctk.CTkFont(size=theme.FONT_SUBTITLE[1]),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        email_lbl.pack(anchor="w")

        # Right Column: Physical Baseline & Goal Pills
        right = ctk.CTkFrame(inner, fg_color="transparent")
        right.pack(side="right", padx=(20, 0))

        # Goal pill
        pill_frame = ctk.CTkFrame(right, fg_color="transparent")
        pill_frame.pack(anchor="e", pady=(0, 6))

        goal_pill = ctk.CTkLabel(
            pill_frame,
            text=f"GOAL: {goal.replace('_', ' ')}",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_SUCCESS,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=6,
            height=24,
            padx=10
        )
        goal_pill.pack(side="right", padx=(6, 0))

        # Physical stats
        h_val = f"{self.user.height_cm:.0f} cm" if self.user and self.user.height_cm else "—"
        w_val = f"{self.user.weight_kg:.1f} kg" if self.user and self.user.weight_kg else "—"
        bmi_val = f"BMI {self.user.bmi}" if self.user and self.user.bmi else "—"
        stats_str = f"Height: {h_val}  |  Weight: {w_val}  |  {bmi_val}"

        stats_lbl = ctk.CTkLabel(
            right,
            text=stats_str,
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_MUTED
        )
        stats_lbl.pack(anchor="e", pady=(0, 6))

        # Edit Profile Button
        edit_btn = ctk.CTkButton(
            right,
            text="EDIT PROFILE",
            width=110,
            height=28,
            corner_radius=6,
            fg_color=theme.COLOR_CARD_ELEVATED,
            hover_color=theme.COLOR_ACCENT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            font=ctk.CTkFont(size=10, weight="bold"),
            command=self._open_profile_editor
        )
        edit_btn.pack(anchor="e")

    def _render_kpis(self):
        for w in self.kpi_container.winfo_children():
            w.destroy()

        user_id = self.user.id if self.user else 1
        stats = self.workout_repo.get_user_aggregate_stats(user_id)

        clean_pct = f"{stats['clean_ratio']:.0f}% Clean"
        q_color = theme.COLOR_SUCCESS if stats['overall_avg_quality'] >= 85 else (theme.COLOR_WARN if stats['overall_avg_quality'] >= 70 else theme.COLOR_ALERT)

        mins, _ = divmod(stats['total_duration_seconds'], 60)
        time_str = f"{mins} mins" if mins > 0 else f"{stats['total_duration_seconds']}s"

        cards = [
            ("WORKOUTS COMPLETED", f"{stats['total_workouts']}", f"Total Volume: {time_str}", theme.COLOR_TEAL),
            ("REPETITIONS TRACKED", f"{stats['total_reps']}", f"{stats['clean_reps']} Clean ({clean_pct})", theme.COLOR_INFO),
            ("ALL-TIME FORM QUALITY", f"{stats['overall_avg_quality']:.1f}%", f"Consistency: {stats['overall_consistency']:.1f}%", q_color),
            ("PRIMARY FOCUS", stats['best_exercise'], f"Best Rep: {stats['highest_rep_score']:.1f}%", theme.COLOR_SUCCESS)
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

    def _open_profile_editor(self):
        UserProfileDialog(
            self,
            user=self.user,
            on_profile_updated=self._on_profile_updated
        )

    def _on_profile_updated(self, updated_user: User):
        self.user = updated_user
        self._render_profile_card()

    def _on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
