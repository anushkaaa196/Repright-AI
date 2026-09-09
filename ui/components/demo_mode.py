"""SIH Grand Finale Presentation Mode for REPRIGHT AI.

Provides a maximized, high-impact presentation HUD designed specifically for
Smart India Hackathon (SIH) judges and live audience demonstrations.
Features large-format live viewport, real-time biomechanical phase tracking,
stability metrics, and live adaptive coaching telemetry.
"""

from typing import Dict, Any, Optional
import customtkinter as ctk

from ui import theme


class SIHDemoWindow(ctk.CTkToplevel):
    """Maximized SIH Grand Finale demonstration HUD."""

    def __init__(self, parent, exercise_name: str = "SQUAT", on_close_callback=None):
        super().__init__(parent)
        self.title("🏆 REPRIGHT AI — SIH GRAND FINALE PRESENTATION HUD")
        self.geometry("1180x780")
        self.configure(fg_color=theme.COLOR_BG)
        self.on_close_callback = on_close_callback
        self.exercise_name = exercise_name

        # Main Layout: Top Brand Bar, Center Stage (Video + Intelligence HUD), Bottom Trend Bar
        self._create_top_bar()
        self._create_center_stage()
        self._create_bottom_bar()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _create_top_bar(self):
        top_bar = ctk.CTkFrame(self, fg_color=theme.COLOR_PANEL_BG, height=54, corner_radius=0)
        top_bar.pack(fill="x")

        # Branding
        title_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=10)

        ctk.CTkLabel(
            title_box,
            text="🏆 REPRIGHT AI",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=theme.COLOR_ACCENT
        ).pack(side="left")

        ctk.CTkLabel(
            title_box,
            text=" • SIH GRAND FINALE STAGE",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        ).pack(side="left")

        # Right status & exit button
        btn_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        btn_box.pack(side="right", padx=20, pady=10)

        self.ex_badge = ctk.CTkLabel(
            btn_box,
            text=f"ACTIVE: {self.exercise_name.upper()}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=theme.COLOR_CARD_ALT,
            text_color=theme.COLOR_SUCCESS,
            corner_radius=4,
            padx=10,
            pady=4
        )
        self.ex_badge.pack(side="left", padx=(0, 12))

        exit_btn = ctk.CTkButton(
            btn_box,
            text="EXIT DEMO MODE",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=theme.COLOR_SECONDARY_BTN,
            hover_color=theme.COLOR_ALERT,
            command=self._on_close,
            width=130,
            height=32
        )
        exit_btn.pack(side="right")

    def _create_center_stage(self):
        stage = ctk.CTkFrame(self, fg_color="transparent")
        stage.pack(fill="both", expand=True, padx=16, pady=10)
        stage.grid_columnconfigure(0, weight=3)
        stage.grid_columnconfigure(1, weight=2)
        stage.grid_rowconfigure(0, weight=1)

        # 1. Left: Live Camera Viewport (Maximized)
        cam_card = ctk.CTkFrame(stage, fg_color=theme.COLOR_CARD_BG, border_width=1, border_color=theme.COLOR_BORDER, corner_radius=12)
        cam_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=4)

        # Video label
        self.video_lbl = ctk.CTkLabel(cam_card, text="[ LIVE CAMERA STREAM INITIALIZING... ]", text_color=theme.COLOR_TEXT_MUTED)
        self.video_lbl.pack(fill="both", expand=True, padx=8, pady=8)

        # Live Feedback Overlay
        self.feedback_banner = ctk.CTkFrame(cam_card, fg_color=theme.COLOR_PANEL_BG, corner_radius=8, height=44)
        self.feedback_banner.pack(fill="x", padx=12, pady=(0, 10))

        self.feedback_lbl = ctk.CTkLabel(
            self.feedback_banner,
            text="YOLOv8 Pose Estimation Active • Tracking 17 Anatomical Keypoints",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme.COLOR_ACCENT
        )
        self.feedback_lbl.pack(expand=True, pady=8)

        # 2. Right: AI Motion Intelligence Cards
        hud_card = ctk.CTkScrollableFrame(stage, fg_color=theme.COLOR_CARD_BG, border_width=1, border_color=theme.COLOR_BORDER, corner_radius=12)
        hud_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=4)

        # A. Phase Indicator
        phase_box = ctk.CTkFrame(hud_card, fg_color=theme.COLOR_CARD_ALT, corner_radius=8)
        phase_box.pack(fill="x", pady=6, padx=6)
        ctk.CTkLabel(phase_box, text="AI MOVEMENT PHASE", font=ctk.CTkFont(size=11, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w", padx=12, pady=(8, 2))
        self.hud_phase_val = ctk.CTkLabel(phase_box, text="DESCENT — 72%", font=ctk.CTkFont(size=18, weight="bold"), text_color=theme.COLOR_ACCENT)
        self.hud_phase_val.pack(anchor="w", padx=12)
        self.hud_phase_bar = ctk.CTkProgressBar(phase_box, height=8, corner_radius=4, progress_color=theme.COLOR_ACCENT)
        self.hud_phase_bar.pack(fill="x", padx=12, pady=(4, 10))
        self.hud_phase_bar.set(0.72)

        # B. Movement Stability
        stab_box = ctk.CTkFrame(hud_card, fg_color=theme.COLOR_CARD_ALT, corner_radius=8)
        stab_box.pack(fill="x", pady=6, padx=6)
        ctk.CTkLabel(stab_box, text="MOVEMENT STABILITY", font=ctk.CTkFont(size=11, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w", padx=12, pady=(8, 2))
        self.hud_stab_val = ctk.CTkLabel(stab_box, text="92% • HIGHLY STABLE", font=ctk.CTkFont(size=18, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.hud_stab_val.pack(anchor="w", padx=12, pady=(0, 8))

        # C. Form Fatigue & Risk Awareness
        meta_row = ctk.CTkFrame(hud_card, fg_color="transparent")
        meta_row.pack(fill="x", pady=4, padx=6)
        meta_row.grid_columnconfigure((0, 1), weight=1)

        fat_box = ctk.CTkFrame(meta_row, fg_color=theme.COLOR_CARD_ALT, corner_radius=8)
        fat_box.grid(row=0, column=0, padx=(0, 4), sticky="nsew")
        ctk.CTkLabel(fat_box, text="FORM FATIGUE", font=ctk.CTkFont(size=10, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(6, 2))
        self.hud_fat_val = ctk.CTkLabel(fat_box, text="LOW", font=ctk.CTkFont(size=14, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.hud_fat_val.pack(anchor="w", padx=10, pady=(0, 6))

        risk_box = ctk.CTkFrame(meta_row, fg_color=theme.COLOR_CARD_ALT, corner_radius=8)
        risk_box.grid(row=0, column=1, padx=(4, 0), sticky="nsew")
        ctk.CTkLabel(risk_box, text="RISK AWARENESS", font=ctk.CTkFont(size=10, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(6, 2))
        self.hud_risk_val = ctk.CTkLabel(risk_box, text="LOW", font=ctk.CTkFont(size=14, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.hud_risk_val.pack(anchor="w", padx=10, pady=(0, 6))

        # D. Smart Adaptive Coach
        coach_box = ctk.CTkFrame(hud_card, fg_color=theme.COLOR_CARD_ALT, corner_radius=8)
        coach_box.pack(fill="x", pady=6, padx=6)
        ctk.CTkLabel(coach_box, text="ADAPTIVE AI COACH", font=ctk.CTkFont(size=11, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w", padx=12, pady=(8, 2))
        self.hud_coach_msg = ctk.CTkLabel(
            coach_box,
            text="\"Maintain knee alignment and controlled descent tempo.\"",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY,
            wraplength=340,
            justify="left"
        )
        self.hud_coach_msg.pack(anchor="w", padx=12, pady=(2, 10))

    def _create_bottom_bar(self):
        bot_bar = ctk.CTkFrame(self, fg_color=theme.COLOR_PANEL_BG, height=50, corner_radius=0)
        bot_bar.pack(fill="x", side="bottom")

        # Telemetry KPI row
        kpi_box = ctk.CTkFrame(bot_bar, fg_color="transparent")
        kpi_box.pack(fill="x", padx=20, pady=8)

        self.kpi_reps = ctk.CTkLabel(kpi_box, text="CLEAN REPS: 0", font=ctk.CTkFont(size=12, weight="bold"), text_color=theme.COLOR_ACCENT)
        self.kpi_reps.pack(side="left", padx=16)

        self.kpi_acc = ctk.CTkLabel(kpi_box, text="FORM QUALITY: 100%", font=ctk.CTkFont(size=12, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.kpi_acc.pack(side="left", padx=16)

        self.kpi_trend = ctk.CTkLabel(kpi_box, text="TRAJECTORY: 📈 OPTIMAL", font=ctk.CTkFont(size=12, weight="bold"), text_color=theme.COLOR_ACCENT)
        self.kpi_trend.pack(side="left", padx=16)

        ctk.CTkLabel(
            kpi_box,
            text="SMART INDIA HACKATHON EDITION • 100% OFFLINE AI",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(side="right")

    def update_frame(self, ctk_img):
        """Updates live video canvas in demo window."""
        self.video_lbl.configure(image=ctk_img, text="")

    def update_telemetry(
        self,
        reps: int,
        acc: int,
        feedback_msg: str,
        feedback_color: str,
        phase_data: Optional[Dict[str, Any]] = None,
        stability_data: Optional[Dict[str, Any]] = None,
        fatigue_data: Optional[Dict[str, Any]] = None,
        risk_data: Optional[Dict[str, Any]] = None,
        coach_data: Optional[Dict[str, Any]] = None
    ):
        """Updates all HUD cards in real-time."""
        self.kpi_reps.configure(text=f"CLEAN REPS: {reps}")
        acc_color = theme.COLOR_SUCCESS if acc >= 75 else (theme.COLOR_WARN if acc >= 50 else theme.COLOR_ALERT)
        self.kpi_acc.configure(text=f"FORM QUALITY: {acc}%", text_color=acc_color)

        if feedback_msg:
            self.feedback_lbl.configure(text=feedback_msg, text_color=feedback_color)

        if phase_data:
            p_label = phase_data.get("phase_label", "START")
            pct = phase_data.get("phase_progress", 0)
            self.hud_phase_val.configure(text=f"{p_label} — {pct}%")
            self.hud_phase_bar.set(max(0.0, min(1.0, float(pct) / 100.0)))

        if stability_data:
            s_score = stability_data.get("stability_score", 90)
            s_cat = stability_data.get("category", "STABLE").replace("_", " ")
            s_color = theme.COLOR_SUCCESS if s_score >= 85 else (theme.COLOR_WARN if s_score >= 60 else theme.COLOR_ALERT)
            self.hud_stab_val.configure(text=f"{s_score}% • {s_cat}", text_color=s_color)

        if fatigue_data:
            f_lvl = fatigue_data.get("fatigue_level", "LOW")
            f_color = theme.COLOR_SUCCESS if f_lvl == "LOW" else (theme.COLOR_WARN if f_lvl == "MODERATE" else theme.COLOR_ALERT)
            self.hud_fat_val.configure(text=f_lvl, text_color=f_color)

        if risk_data:
            r_lvl = risk_data.get("risk_level", "LOW")
            r_color = theme.COLOR_SUCCESS if r_lvl == "LOW" else (theme.COLOR_WARN if r_lvl == "MODERATE" else theme.COLOR_ALERT)
            self.hud_risk_val.configure(text=r_lvl, text_color=r_color)

        if coach_data:
            self.hud_coach_msg.configure(text=f"\"{coach_data.get('primary_message', 'Maintain control.')}\"")

    def _on_close(self):
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
