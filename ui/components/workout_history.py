"""REPRIGHT AI - Workout History Component.

Renders responsive workout session debrief cards with multidimensional biomechanical indicators,
exercise filtering, and rep-by-rep inspection capabilities.
"""

from typing import Callable, Optional, List, Dict, Any
from datetime import datetime
import customtkinter as ctk
from ui import theme
from database.models import WorkoutSession, RepRecord
from database.workout_repository import WorkoutRepository


class SessionDetailDialog(ctk.CTkToplevel):
    """Detailed breakdown modal for an archived workout session."""

    def __init__(self, master, session: WorkoutSession):
        super().__init__(master)
        self.session = session

        self.title(f"REPRIGHT AI — Session #{session.id} Telemetry Breakdown")
        self.geometry("720x580")
        self.minsize(640, 480)
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
        container.pack(fill="both", expand=True, padx=16, pady=16)

        # Header
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(16, 12))

        badge = ctk.CTkLabel(
            header,
            text=f"SESSION ARCHIVE #{self.session.id}",
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
            text=f"{self.session.exercise_name} Performance Intelligence",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1] + 2, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        title.pack(anchor="w")

        date_str = self.session.started_at[:16].replace("T", " ") if self.session.started_at else "Unknown Date"
        mins, secs = divmod(self.session.duration_seconds, 60)
        meta_str = f"Date: {date_str}  |  Duration: {mins}m {secs}s  |  Reps: {self.session.clean_reps}/{self.session.total_reps} Clean"
        ctk.CTkLabel(
            header,
            text=meta_str,
            font=ctk.CTkFont(size=theme.FONT_SUBTITLE[1]),
            text_color=theme.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 0))

        # KPI Metrics Cards (4 boxes)
        kpi_frame = ctk.CTkFrame(container, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=20, pady=(0, 14))
        for col in range(4):
            kpi_frame.grid_columnconfigure(col, weight=1)

        kpis = [
            ("AVG FORM SCORE", f"{self.session.average_quality:.1f}%", theme.COLOR_SUCCESS if self.session.average_quality >= 85 else theme.COLOR_WARN),
            ("CONSISTENCY", f"{self.session.consistency_score:.1f}%", theme.COLOR_TEAL),
            ("STABILITY", f"{self.session.stability_score:.1f}%", theme.COLOR_INFO),
            ("FATIGUE LEVEL", self.session.fatigue_level, theme.COLOR_SUCCESS if self.session.fatigue_level == "LOW" else theme.COLOR_ALERT)
        ]

        for idx, (label, val, color) in enumerate(kpis):
            box = ctk.CTkFrame(kpi_frame, fg_color=theme.COLOR_CARD_BG, corner_radius=8, border_width=1, border_color=theme.COLOR_BORDER)
            box.grid(row=0, column=idx, padx=4, sticky="nsew", ipady=6)
            ctk.CTkLabel(box, text=label, font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(anchor="center", pady=(4, 0))
            ctk.CTkLabel(box, text=val, font=ctk.CTkFont(size=14, weight="bold"), text_color=color).pack(anchor="center", pady=(0, 4))

        # Repetition Telemetry Table / Scroll Area
        table_label = ctk.CTkLabel(
            container,
            text="REPETITION-BY-REPETITION TELEMETRY",
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1], weight=theme.FONT_SECTION_HEADER[2]),
            text_color=theme.COLOR_TEXT_MUTED
        )
        table_label.pack(anchor="w", padx=20, pady=(0, 4))

        scroll = ctk.CTkScrollableFrame(container, fg_color=theme.COLOR_BG_DARK, corner_radius=8)
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 14))

        if not self.session.reps:
            ctk.CTkLabel(
                scroll,
                text="No granular rep telemetry records saved for this session.",
                font=ctk.CTkFont(size=theme.FONT_BODY[1]),
                text_color=theme.COLOR_TEXT_MUTED
            ).pack(pady=24)
        else:
            # Header Row
            hdr = ctk.CTkFrame(scroll, fg_color=theme.COLOR_CARD_ELEVATED, corner_radius=4)
            hdr.pack(fill="x", pady=(0, 4))
            hdr.grid_columnconfigure(0, weight=1)
            hdr.grid_columnconfigure(1, weight=1)
            hdr.grid_columnconfigure(2, weight=1)
            hdr.grid_columnconfigure(3, weight=1)
            hdr.grid_columnconfigure(4, weight=1)

            cols = ["Rep #", "Overall Quality", "ROM Score", "Alignment", "Stability"]
            for ci, ctitle in enumerate(cols):
                ctk.CTkLabel(
                    hdr,
                    text=ctitle,
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color=theme.COLOR_TEXT_SECONDARY
                ).grid(row=0, column=ci, padx=8, pady=4, sticky="w")

            for rep in self.session.reps:
                row = ctk.CTkFrame(scroll, fg_color=theme.COLOR_CARD_BG, corner_radius=4)
                row.pack(fill="x", pady=2)
                row.grid_columnconfigure(0, weight=1)
                row.grid_columnconfigure(1, weight=1)
                row.grid_columnconfigure(2, weight=1)
                row.grid_columnconfigure(3, weight=1)
                row.grid_columnconfigure(4, weight=1)

                q_col = theme.COLOR_SUCCESS if rep.quality_score >= 85 else (theme.COLOR_WARN if rep.quality_score >= 70 else theme.COLOR_ALERT)

                ctk.CTkLabel(row, text=f"Rep #{rep.rep_number}", font=ctk.CTkFont(size=11, weight="bold"), text_color=theme.COLOR_TEXT_PRIMARY).grid(row=0, column=0, padx=8, pady=4, sticky="w")
                ctk.CTkLabel(row, text=f"{rep.quality_score:.1f}% ({rep.rep_result})", font=ctk.CTkFont(size=11, weight="bold"), text_color=q_col).grid(row=0, column=1, padx=8, pady=4, sticky="w")
                ctk.CTkLabel(row, text=f"{rep.range_of_motion:.1f}%", font=ctk.CTkFont(size=11), text_color=theme.COLOR_TEXT_SECONDARY).grid(row=0, column=2, padx=8, pady=4, sticky="w")
                ctk.CTkLabel(row, text=f"{rep.joint_alignment:.1f}%", font=ctk.CTkFont(size=11), text_color=theme.COLOR_TEXT_SECONDARY).grid(row=0, column=3, padx=8, pady=4, sticky="w")
                ctk.CTkLabel(row, text=f"{rep.core_stability:.1f}%", font=ctk.CTkFont(size=11), text_color=theme.COLOR_TEXT_SECONDARY).grid(row=0, column=4, padx=8, pady=4, sticky="w")

        # Close Button
        close_btn = ctk.CTkButton(
            container,
            text="CLOSE BREAKDOWN",
            height=36,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=self.destroy
        )
        close_btn.pack(anchor="e", padx=20, pady=(0, 16))


class WorkoutHistoryView(ctk.CTkFrame):
    """Component listing past workouts with filtering and drill-down cards."""

    def __init__(
        self,
        master,
        user_id: int,
        workout_repo: Optional[WorkoutRepository] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )
        self.user_id = user_id
        self.workout_repo = workout_repo or WorkoutRepository()
        self.current_filter: Optional[str] = None

        self._build_ui()
        self.refresh_history()

    def _build_ui(self):
        # Filter Bar
        filter_bar = ctk.CTkFrame(self, fg_color="transparent")
        filter_bar.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            filter_bar,
            text="FILTER BY EXERCISE:",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(side="left", padx=(0, 8))

        from config import EXERCISE_CONFIGS
        ex_options = ["ALL EXERCISES"] + list(EXERCISE_CONFIGS.keys())

        self.filter_opt = ctk.CTkOptionMenu(
            filter_bar,
            values=ex_options,
            command=self._on_filter_changed,
            height=28,
            width=160,
            fg_color=theme.COLOR_CARD_BG,
            button_color=theme.COLOR_CARD_ELEVATED,
            button_hover_color=theme.COLOR_ACCENT,
            dropdown_fg_color=theme.COLOR_CARD_ELEVATED,
            dropdown_hover_color=theme.COLOR_ACCENT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=6
        )
        self.filter_opt.set("ALL EXERCISES")
        self.filter_opt.pack(side="left")

        # Scrollable Cards Area
        self.scroll_cards = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_cards.pack(fill="both", expand=True)

    def _on_filter_changed(self, value: str):
        self.current_filter = None if value == "ALL EXERCISES" else value
        self.refresh_history()

    def refresh_history(self):
        """Fetches workouts from repository and redraws session cards."""
        for w in self.scroll_cards.winfo_children():
            w.destroy()

        sessions = self.workout_repo.get_workout_sessions_by_user(
            user_id=self.user_id,
            limit=40,
            exercise=self.current_filter
        )

        if not sessions:
            empty_box = ctk.CTkFrame(self.scroll_cards, fg_color=theme.COLOR_PANEL_BG, corner_radius=12, border_width=1, border_color=theme.COLOR_BORDER)
            empty_box.pack(fill="x", pady=20, padx=10, ipady=20)
            ctk.CTkLabel(
                empty_box,
                text="No Saved Workout Sessions",
                font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1], weight="bold"),
                text_color=theme.COLOR_TEXT_PRIMARY
            ).pack(pady=(0, 4))
            ctk.CTkLabel(
                empty_box,
                text="Start and complete a workout on the main dashboard to archive telemetry here.",
                font=ctk.CTkFont(size=theme.FONT_SUBTITLE[1]),
                text_color=theme.COLOR_TEXT_SECONDARY
            ).pack()
            return

        for s in sessions:
            self._render_session_card(s)

    def _render_session_card(self, session: WorkoutSession):
        card = ctk.CTkFrame(
            self.scroll_cards,
            fg_color=theme.COLOR_PANEL_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        card.pack(fill="x", pady=5, padx=4)

        # Header Row
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(12, 6))

        # Exercise badge
        ex_label = ctk.CTkLabel(
            hdr,
            text=session.exercise_name,
            font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1], weight="bold"),
            text_color=theme.COLOR_TEAL
        )
        ex_label.pack(side="left")

        # Timestamp
        date_str = session.started_at[:16].replace("T", " ") if session.started_at else ""
        date_label = ctk.CTkLabel(
            hdr,
            text=date_str,
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_MUTED
        )
        date_label.pack(side="right")

        # Metrics Row
        m_row = ctk.CTkFrame(card, fg_color="transparent")
        m_row.pack(fill="x", padx=14, pady=(0, 10))

        mins, secs = divmod(session.duration_seconds, 60)
        dur_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"

        q_color = theme.COLOR_SUCCESS if session.average_quality >= 85 else (theme.COLOR_WARN if session.average_quality >= 70 else theme.COLOR_ALERT)

        items = [
            ("Duration", dur_str, theme.COLOR_TEXT_PRIMARY),
            ("Reps", f"{session.clean_reps}/{session.total_reps} Clean", theme.COLOR_TEXT_PRIMARY),
            ("Form Score", f"{session.average_quality:.1f}%", q_color),
            ("Stability", f"{session.stability_score:.1f}%", theme.COLOR_INFO),
            ("Fatigue", session.fatigue_level, theme.COLOR_SUCCESS if session.fatigue_level == "LOW" else theme.COLOR_ALERT)
        ]

        for label, val, color in items:
            col_f = ctk.CTkFrame(m_row, fg_color="transparent")
            col_f.pack(side="left", padx=(0, 16))
            ctk.CTkLabel(col_f, text=label.upper(), font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(anchor="w")
            ctk.CTkLabel(col_f, text=val, font=ctk.CTkFont(size=12, weight="bold"), text_color=color).pack(anchor="w")

        # Action button
        inspect_btn = ctk.CTkButton(
            m_row,
            text="DETAILS",
            width=70,
            height=26,
            corner_radius=6,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=theme.COLOR_CARD_ELEVATED,
            hover_color=theme.COLOR_ACCENT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=lambda s_id=session.id: self._open_session_detail(s_id)
        )
        inspect_btn.pack(side="right")

    def _open_session_detail(self, session_id: int):
        full_session = self.workout_repo.get_workout_session_by_id(session_id, include_reps=True)
        if full_session:
            SessionDetailDialog(self.winfo_toplevel(), full_session)
