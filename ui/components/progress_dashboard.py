"""Progress Intelligence Dashboard Dialog for REPRIGHT AI.

Displays session-to-session performance trajectories, form quality improvements,
consistency metrics, and multi-workout history without requiring external database dependencies.
"""

from typing import Dict, Any, Optional, List
import customtkinter as ctk
from ui import theme
from core.progress_intelligence import ProgressIntelligenceTracker


class ProgressDashboardDialog(ctk.CTkToplevel):
    """Modern modal dashboard displaying session-to-session progress intelligence."""

    def __init__(self, master, exercise_name: str, **kwargs):
        super().__init__(master, **kwargs)

        self.exercise_name = exercise_name.upper().strip()
        self.tracker = ProgressIntelligenceTracker.get_instance()
        self.summary = self.tracker.get_progress_summary(self.exercise_name)
        self.sessions = self.tracker.get_all_sessions(self.exercise_name)

        self.title("REPRIGHT AI - Long-Term Progress Intelligence")
        self.geometry("740x580")
        self.minsize(660, 480)
        self.configure(fg_color=theme.COLOR_BG_DARK)

        self.transient(master)
        self.after(10, self._center)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ----------------------------------------------------------------------
        # Header
        # ----------------------------------------------------------------------
        self.header = ctk.CTkFrame(self, fg_color=theme.COLOR_PANEL_BG, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="ew")

        h_inner = ctk.CTkFrame(self.header, fg_color="transparent")
        h_inner.pack(fill="x", padx=24, pady=16)

        t_lbl = ctk.CTkLabel(
            h_inner,
            text="📈 PROGRESS INTELLIGENCE DASHBOARD",
            font=ctk.CTkFont(size=theme.FONT_BRAND[1], weight=theme.FONT_BRAND[2]),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        t_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            h_inner,
            text=f"{self.exercise_name} • Multi-Session Performance Progression & Biomechanical Trends",
            font=ctk.CTkFont(size=theme.FONT_SUBTITLE[1]),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # ----------------------------------------------------------------------
        # Scrollable Body
        # ----------------------------------------------------------------------
        self.body = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=theme.COLOR_BORDER,
            scrollbar_button_hover_color=theme.COLOR_BORDER_LIGHT
        )
        self.body.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=1)

        # 1. Progression Highlight Card
        self._build_trend_card()

        # 2. 4-KPI Row (Best Rep, Consistency, Most Improved, Recurring Focus)
        self._build_kpi_row()

        # 3. Recent Sessions Table
        self._build_history_table()

        # ----------------------------------------------------------------------
        # Footer
        # ----------------------------------------------------------------------
        self.footer = ctk.CTkFrame(self, fg_color=theme.COLOR_PANEL_BG, corner_radius=0)
        self.footer.grid(row=2, column=0, sticky="ew")

        f_inner = ctk.CTkFrame(self.footer, fg_color="transparent")
        f_inner.pack(fill="x", padx=24, pady=12)

        btn_close = ctk.CTkButton(
            f_inner,
            text="CLOSE",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
            height=32,
            width=90,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_BORDER_LIGHT,
            text_color=theme.COLOR_TEXT_SECONDARY,
            command=self.destroy
        )
        btn_close.pack(side="right")

    def _center(self):
        try:
            self.update_idletasks()
            master = self.master
            x = master.winfo_x() + (master.winfo_width() - self.winfo_width()) // 2
            y = master.winfo_y() + (master.winfo_height() - self.winfo_height()) // 2
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _build_trend_card(self):
        card = ctk.CTkFrame(self.body, corner_radius=10, fg_color=theme.COLOR_CARD_BG, border_width=1, border_color=theme.COLOR_BORDER)
        card.pack(fill="x", pady=(2, 8))

        t_lbl = ctk.CTkLabel(card, text="SESSION FORM QUALITY TRAJECTORY", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED)
        t_lbl.pack(anchor="w", padx=16, pady=(12, 2))

        # Comparison Text
        prev_acc = self.summary["previous_accuracy"]
        curr_acc = self.summary["current_accuracy"]
        delta = self.summary["delta_accuracy"]

        trend_color = theme.COLOR_SUCCESS if delta >= 0 else theme.COLOR_WARN
        traj_txt = f"{self.summary['trend_icon']} {self.summary['trend_text']}  (Previous: {prev_acc}%  →  Current: {curr_acc}%)"
        traj_lbl = ctk.CTkLabel(card, text=traj_txt, font=ctk.CTkFont(size=13, weight="bold"), text_color=trend_color)
        traj_lbl.pack(anchor="w", padx=16, pady=(0, 12))

    def _build_kpi_row(self):
        row_f = ctk.CTkFrame(self.body, fg_color="transparent")
        row_f.pack(fill="x", pady=4)
        row_f.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")

        items = [
            ("BEST REP QUALITY", f"{self.summary['best_rep']}%", theme.COLOR_SUCCESS),
            ("CONSISTENCY SCORE", f"{self.summary['consistency']}%", theme.COLOR_ACCENT),
            ("MOST IMPROVED AREA", self.summary["most_improved_category"], theme.COLOR_TEXT_PRIMARY),
            ("RECURRING FOCUS", self.summary["recurring_focus"], theme.COLOR_WARN)
        ]

        for i, (title, val, col) in enumerate(items):
            c = ctk.CTkFrame(row_f, corner_radius=8, fg_color=theme.COLOR_CARD_BG, border_width=1, border_color=theme.COLOR_BORDER)
            c.grid(row=0, column=i, padx=3, pady=2, sticky="nsew")

            t = ctk.CTkLabel(c, text=title, font=ctk.CTkFont(size=8, weight="bold"), text_color=theme.COLOR_TEXT_MUTED)
            t.pack(anchor="w", padx=10, pady=(8, 1))

            v = ctk.CTkLabel(c, text=val, font=ctk.CTkFont(size=14, weight="bold"), text_color=col)
            v.pack(anchor="w", padx=10, pady=(0, 8))

    def _build_history_table(self):
        card = ctk.CTkFrame(self.body, corner_radius=10, fg_color=theme.COLOR_CARD_BG, border_width=1, border_color=theme.COLOR_BORDER)
        card.pack(fill="x", pady=8)

        t_lbl = ctk.CTkLabel(card, text="SESSION LOG HISTORY", font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight=theme.FONT_STAT_TITLE[2]), text_color=theme.COLOR_TEXT_PRIMARY)
        t_lbl.pack(anchor="w", padx=16, pady=(10, 6))

        if not self.sessions:
            e_lbl = ctk.CTkLabel(card, text="No completed workout sessions logged yet in runtime.", font=ctk.CTkFont(size=10), text_color=theme.COLOR_TEXT_MUTED)
            e_lbl.pack(padx=16, pady=(0, 12))
            return

        # Headers
        h_row = ctk.CTkFrame(card, fg_color=theme.COLOR_CARD_INNER, corner_radius=4)
        h_row.pack(fill="x", padx=12, pady=2)
        h_row.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        cols = ["Session", "Form Score", "Clean Reps", "Consistency", "Timestamp"]
        for ci, col in enumerate(cols):
            clbl = ctk.CTkLabel(h_row, text=col, font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED)
            clbl.grid(row=0, column=ci, padx=6, pady=4)

        for s in reversed(self.sessions[-8:]):
            s_row = ctk.CTkFrame(card, fg_color="transparent")
            s_row.pack(fill="x", padx=12, pady=1)
            s_row.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

            ctk.CTkLabel(s_row, text=f"#{s.get('session_number', 1)}", font=ctk.CTkFont(size=10), text_color=theme.COLOR_TEXT_PRIMARY).grid(row=0, column=0, padx=6, pady=2)
            
            acc = s.get("accuracy", 100)
            acc_col = theme.COLOR_SUCCESS if acc >= 80 else theme.COLOR_WARN
            ctk.CTkLabel(s_row, text=f"{acc}%", font=ctk.CTkFont(size=10, weight="bold"), text_color=acc_col).grid(row=0, column=1, padx=6, pady=2)

            ctk.CTkLabel(s_row, text=f"{s.get('clean_reps', 0)} / {s.get('total_attempts', 0)}", font=ctk.CTkFont(size=10), text_color=theme.COLOR_TEXT_SECONDARY).grid(row=0, column=2, padx=6, pady=2)
            ctk.CTkLabel(s_row, text=f"{s.get('consistency_score', 100)}%", font=ctk.CTkFont(size=10), text_color=theme.COLOR_ACCENT).grid(row=0, column=3, padx=6, pady=2)
            ctk.CTkLabel(s_row, text=s.get("timestamp", "")[-8:], font=ctk.CTkFont(size=9), text_color=theme.COLOR_TEXT_MUTED).grid(row=0, column=4, padx=6, pady=2)

        ctk.CTkFrame(card, height=8, fg_color="transparent").pack()
