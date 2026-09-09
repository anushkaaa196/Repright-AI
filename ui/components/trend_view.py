"""Dedicated Form Quality Trend View for REPRIGHT AI.

Displays an enlarged interactive accuracy trendline canvas, session trajectory indicators
(IMPROVING / STABLE / DECLINING), and historical progression analytics on demand.
"""

from typing import List, Dict, Any, Optional
import tkinter as tk
import customtkinter as ctk
from ui import theme
from core.rep_history import RepHistoryTracker


class TrendView(ctk.CTkFrame):
    """Full-featured on-demand form quality trend visualization."""

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )
        self.trend_points: List[int] = [100]
        self.max_points = 30

        # ----------------------------------------------------------------------
        # Header Banner
        # ----------------------------------------------------------------------
        header_card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        header_card.pack(fill="x", padx=16, pady=(12, 8))

        top_row = ctk.CTkFrame(header_card, fg_color="transparent")
        top_row.pack(fill="x", padx=16, pady=(12, 6))

        title_box = ctk.CTkFrame(top_row, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box,
            text="📉 FORM QUALITY OVER TIME",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=theme.COLOR_ACCENT
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Real-Time Trajectory, Biomechanical Progression & Quality History",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_SECONDARY
        ).pack(anchor="w")

        # KPI Row
        kpi_row = ctk.CTkFrame(header_card, fg_color="transparent")
        kpi_row.pack(fill="x", padx=16, pady=(4, 12))
        kpi_row.grid_columnconfigure((0, 1, 2), weight=1)

        # 1. Trajectory Pill
        p1 = ctk.CTkFrame(kpi_row, fg_color=theme.COLOR_CARD_ALT, corner_radius=8, border_width=1, border_color=theme.COLOR_BORDER)
        p1.grid(row=0, column=0, padx=4, sticky="ew")
        ctk.CTkLabel(p1, text="SESSION TRAJECTORY", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(6, 0))
        self.traj_lbl = ctk.CTkLabel(p1, text="➡ STABLE", font=ctk.CTkFont(size=14, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.traj_lbl.pack(pady=(2, 6))

        # 2. Latest Score
        p2 = ctk.CTkFrame(kpi_row, fg_color=theme.COLOR_CARD_ALT, corner_radius=8, border_width=1, border_color=theme.COLOR_BORDER)
        p2.grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkLabel(p2, text="LATEST ACCURACY", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(6, 0))
        self.latest_lbl = ctk.CTkLabel(p2, text="100%", font=ctk.CTkFont(size=18, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.latest_lbl.pack(pady=(0, 6))

        # 3. Progression Range
        p3 = ctk.CTkFrame(kpi_row, fg_color=theme.COLOR_CARD_ALT, corner_radius=8, border_width=1, border_color=theme.COLOR_BORDER)
        p3.grid(row=0, column=2, padx=4, sticky="ew")
        ctk.CTkLabel(p3, text="RECENT SEQUENCE", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_MUTED).pack(pady=(6, 0))
        self.seq_lbl = ctk.CTkLabel(p3, text="100% → 100%", font=ctk.CTkFont(size=11, weight="bold"), text_color=theme.COLOR_ACCENT)
        self.seq_lbl.pack(pady=(4, 6))

        # ----------------------------------------------------------------------
        # High-Resolution Canvas Container
        # ----------------------------------------------------------------------
        chart_card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        chart_card.pack(fill="both", expand=True, padx=16, pady=4)

        ctk.CTkLabel(
            chart_card,
            text="DYNAMIC FORM ACCURACY TRENDLINE",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(anchor="w", padx=16, pady=(10, 4))

        self.canvas = tk.Canvas(
            chart_card,
            height=150,
            bg=theme.COLOR_CARD_INNER,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=14, pady=(2, 12))
        self.canvas.bind("<Configure>", lambda e: self._draw_canvas())

        # ----------------------------------------------------------------------
        # Stats & Recommendations Breakdown
        # ----------------------------------------------------------------------
        stats_card = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        stats_card.pack(fill="x", padx=16, pady=(6, 12))

        self.stats_desc = ctk.CTkLabel(
            stats_card,
            text="Form trend is stable. Movement efficiency is high with uniform joint kinematics.",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_PRIMARY,
            justify="left"
        )
        self.stats_desc.pack(anchor="w", padx=16, pady=10)

        self._draw_canvas()

    def add_point(self, score: int):
        """Adds a quality score point to the trend history."""
        self.trend_points.append(int(score))
        if len(self.trend_points) > self.max_points:
            self.trend_points.pop(0)
        self._refresh_ui()

    def _draw_canvas(self):
        """Renders the cyber-styled high-res trend line on the canvas."""
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 20 or h < 20:
            return

        # Grid lines at 100%, 75%, 50%
        for pct, lbl in [(1.0, "100%"), (0.75, "75%"), (0.50, "50%")]:
            y = int(h - (pct * (h - 24)) - 12)
            self.canvas.create_line(40, y, w - 10, y, fill=theme.COLOR_BORDER, dash=(2, 4))
            self.canvas.create_text(20, y, text=lbl, fill=theme.COLOR_TEXT_MUTED, font=("Segoe UI", 7))

        pts = self.trend_points
        if not pts:
            return

        n = len(pts)
        dx = (w - 60) / max(1, n - 1) if n > 1 else 0

        coords = []
        for i, val in enumerate(pts):
            x = 45 + (i * dx)
            normalized = max(0.0, min(1.0, float(val) / 100.0))
            y = int(h - (normalized * (h - 24)) - 12)
            coords.append((x, y))

        # Connect lines
        if len(coords) > 1:
            line_pts = []
            for x, y in coords:
                line_pts.extend([x, y])
            self.canvas.create_line(*line_pts, fill=theme.COLOR_ACCENT, width=2, smooth=True)

        # Plot points & labels for key nodes
        for i, (x, y) in enumerate(coords):
            val = pts[i]
            col = theme.COLOR_SUCCESS if val >= 80 else (theme.COLOR_WARN if val >= 50 else theme.COLOR_ALERT)
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=col, outline=theme.COLOR_PANEL_BG, width=1)

    def _refresh_ui(self):
        """Updates summary labels and trajectory status."""
        if not self.trend_points:
            return

        latest = self.trend_points[-1]
        col = theme.COLOR_SUCCESS if latest >= 80 else (theme.COLOR_WARN if latest >= 50 else theme.COLOR_ALERT)
        self.latest_lbl.configure(text=f"{latest}%", text_color=col)

        # Compute trajectory
        if len(self.trend_points) >= 4:
            first_half = sum(self.trend_points[:len(self.trend_points)//2]) / (len(self.trend_points)//2)
            second_half = sum(self.trend_points[len(self.trend_points)//2:]) / (len(self.trend_points) - len(self.trend_points)//2)
            diff = second_half - first_half
            if diff >= 3:
                self.traj_lbl.configure(text="📈 IMPROVING", text_color=theme.COLOR_SUCCESS)
                desc = "Biomechanical precision is increasing. Motor patterns are solidifying as the set progresses."
            elif diff <= -3:
                self.traj_lbl.configure(text="📉 DECLINING", text_color=theme.COLOR_ALERT)
                desc = "Form degradation detected. Fatigue may be impairing stabilizing muscle groups."
            else:
                self.traj_lbl.configure(text="➡ STABLE", text_color=theme.COLOR_ACCENT)
                desc = "Form quality remains consistent across movement iterations."
            self.stats_desc.configure(text=desc)

            # Sequence summary
            recent = self.trend_points[-4:]
            seq = " → ".join(f"{p}%" for p in recent)
            self.seq_lbl.configure(text=seq)

        self._draw_canvas()

    def reset(self):
        """Resets trendline to baseline."""
        self.trend_points = [100]
        self.traj_lbl.configure(text="➡ STABLE", text_color=theme.COLOR_SUCCESS)
        self.latest_lbl.configure(text="100%", text_color=theme.COLOR_SUCCESS)
        self.seq_lbl.configure(text="100% → 100%")
        self.stats_desc.configure(text="Form trend is stable. Movement efficiency is high with uniform joint kinematics.")
        self._draw_canvas()
