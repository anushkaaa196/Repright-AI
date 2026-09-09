"""AI Movement Intelligence Dashboard Component for REPRIGHT AI.

Displays the 5 primary real-time motion intelligence metrics:
1. Movement Stability
2. AI-Estimated Form Fatigue
3. AI Movement Risk Awareness
4. Adaptive Coaching Intensity Mode
5. Smart Recovery Guidance
"""

from typing import Dict, Any, Optional
import customtkinter as ctk

from ui import theme


class MovementIntelligenceCard(ctk.CTkFrame):
    """Compact live card displaying the 5 Phase 6 movement intelligence indicators."""

    def __init__(self, master, current_exercise: str = "SQUAT", **kwargs):
        super().__init__(
            master,
            fg_color=theme.COLOR_CARD_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            corner_radius=10,
            **kwargs
        )
        self.current_exercise = current_exercise

        # Title
        title_row = ctk.CTkFrame(self, fg_color="transparent")
        title_row.pack(fill="x", padx=12, pady=(10, 6))

        title = ctk.CTkLabel(
            title_row,
            text="AI MOTION INTELLIGENCE",
            font=ctk.CTkFont(size=theme.FONT_STAT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_ACCENT
        )
        title.pack(side="left")

        badge = ctk.CTkLabel(
            title_row,
            text="ADAPTIVE",
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=theme.COLOR_CARD_ALT,
            text_color=theme.COLOR_ACCENT,
            corner_radius=4,
            padx=6,
            pady=1
        )
        badge.pack(side="right")

        # 5 Metrics Grid
        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.pack(fill="x", padx=12, pady=(2, 10))
        grid_frame.grid_columnconfigure((0, 1), weight=1)

        # 1. Movement Stability
        stab_card = ctk.CTkFrame(grid_frame, fg_color=theme.COLOR_CARD_ALT, corner_radius=6, border_width=1, border_color=theme.COLOR_BORDER)
        stab_card.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")

        ctk.CTkLabel(stab_card, text="STABILITY", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w", padx=8, pady=(4, 0))
        self.stab_val = ctk.CTkLabel(stab_card, text="92%", font=ctk.CTkFont(size=14, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.stab_val.pack(anchor="w", padx=8)
        self.stab_pill = ctk.CTkLabel(stab_card, text="HIGHLY STABLE", font=ctk.CTkFont(size=8, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.stab_pill.pack(anchor="w", padx=8, pady=(0, 4))

        # 2. Form Fatigue
        fat_card = ctk.CTkFrame(grid_frame, fg_color=theme.COLOR_CARD_ALT, corner_radius=6, border_width=1, border_color=theme.COLOR_BORDER)
        fat_card.grid(row=0, column=1, padx=3, pady=3, sticky="nsew")

        ctk.CTkLabel(fat_card, text="FORM FATIGUE", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w", padx=8, pady=(4, 0))
        self.fat_val = ctk.CTkLabel(fat_card, text="LOW", font=ctk.CTkFont(size=14, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.fat_val.pack(anchor="w", padx=8)
        self.fat_sub = ctk.CTkLabel(fat_card, text="STABLE CADENCE", font=ctk.CTkFont(size=8, weight="bold"), text_color=theme.COLOR_TEXT_MUTED)
        self.fat_sub.pack(anchor="w", padx=8, pady=(0, 4))

        # 3. Risk Awareness
        risk_card = ctk.CTkFrame(grid_frame, fg_color=theme.COLOR_CARD_ALT, corner_radius=6, border_width=1, border_color=theme.COLOR_BORDER)
        risk_card.grid(row=1, column=0, padx=3, pady=3, sticky="nsew")

        ctk.CTkLabel(risk_card, text="RISK AWARENESS", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w", padx=8, pady=(4, 0))
        self.risk_val = ctk.CTkLabel(risk_card, text="LOW", font=ctk.CTkFont(size=14, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.risk_val.pack(anchor="w", padx=8)
        self.risk_sub = ctk.CTkLabel(risk_card, text="WITHIN TARGETS", font=ctk.CTkFont(size=8, weight="bold"), text_color=theme.COLOR_TEXT_MUTED)
        self.risk_sub.pack(anchor="w", padx=8, pady=(0, 4))

        # 4. Adaptive Coaching Mode
        coach_card = ctk.CTkFrame(grid_frame, fg_color=theme.COLOR_CARD_ALT, corner_radius=6, border_width=1, border_color=theme.COLOR_BORDER)
        coach_card.grid(row=1, column=1, padx=3, pady=3, sticky="nsew")

        ctk.CTkLabel(coach_card, text="COACH MODE", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(anchor="w", padx=8, pady=(4, 0))
        self.coach_val = ctk.CTkLabel(coach_card, text="CALM", font=ctk.CTkFont(size=14, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.coach_val.pack(anchor="w", padx=8)
        self.coach_sub = ctk.CTkLabel(coach_card, text="OPTIMAL RHYTHM", font=ctk.CTkFont(size=8, weight="bold"), text_color=theme.COLOR_TEXT_MUTED)
        self.coach_sub.pack(anchor="w", padx=8, pady=(0, 4))

        # 5. Recovery Status Bar (Row 2, full width)
        rec_frame = ctk.CTkFrame(grid_frame, fg_color=theme.COLOR_CARD_ALT, corner_radius=6, border_width=1, border_color=theme.COLOR_BORDER)
        rec_frame.grid(row=2, column=0, columnspan=2, padx=3, pady=3, sticky="nsew")

        rec_row = ctk.CTkFrame(rec_frame, fg_color="transparent")
        rec_row.pack(fill="x", padx=8, pady=4)

        ctk.CTkLabel(rec_row, text="RECOVERY PROTOCOL:", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(side="left")
        self.rec_lbl = ctk.CTkLabel(rec_row, text="CONTINUE TRAINING", font=ctk.CTkFont(size=9, weight="bold"), text_color=theme.COLOR_SUCCESS)
        self.rec_lbl.pack(side="right")

    def update_intelligence(
        self,
        stability_data: Dict[str, Any],
        fatigue_data: Dict[str, Any],
        risk_data: Dict[str, Any],
        coach_data: Dict[str, Any],
        recovery_data: Dict[str, Any]
    ):
        """Updates all 5 metrics with fresh intelligence telemetry."""
        # 1. Stability
        stab_score = stability_data.get("stability_score", 90)
        stab_color = theme.COLOR_SUCCESS if stab_score >= 90 else (theme.COLOR_ACCENT if stab_score >= 75 else (theme.COLOR_WARN if stab_score >= 50 else theme.COLOR_ALERT))
        self.stab_val.configure(text=f"{stab_score}%", text_color=stab_color)
        self.stab_pill.configure(text=stability_data.get("category", "STABLE").replace("_", " "), text_color=stab_color)

        # 2. Fatigue
        fat_level = fatigue_data.get("fatigue_level", "LOW")
        fat_color = theme.COLOR_SUCCESS if fat_level == "LOW" else (theme.COLOR_WARN if fat_level == "MODERATE" else theme.COLOR_ALERT)
        self.fat_val.configure(text=fat_level, text_color=fat_color)
        self.fat_sub.configure(text=fatigue_data.get("quality_trend", "STABLE"), text_color=theme.COLOR_TEXT_MUTED)

        # 3. Risk Awareness
        risk_level = risk_data.get("risk_level", "LOW")
        risk_color = theme.COLOR_SUCCESS if risk_level == "LOW" else (theme.COLOR_WARN if risk_level == "MODERATE" else theme.COLOR_ALERT)
        self.risk_val.configure(text=risk_level, text_color=risk_color)
        self.risk_sub.configure(text="WITHIN TARGETS" if risk_level == "LOW" else "ATTENTION REQ", text_color=risk_color)

        # 4. Coach Mode
        mode = coach_data.get("coaching_mode", "CALM")
        mode_color = theme.COLOR_SUCCESS if mode == "CALM" else (theme.COLOR_ACCENT if mode == "GUIDED" else theme.COLOR_ALERT)
        self.coach_val.configure(text=mode, text_color=mode_color)
        self.coach_sub.configure(text=coach_data.get("focus_area", "Consistency"), text_color=theme.COLOR_TEXT_MUTED)

        # 5. Recovery
        rec_status = recovery_data.get("recovery_status", "CONTINUE_TRAINING").replace("_", " ")
        rec_color = theme.COLOR_SUCCESS if "CONTINUE" in rec_status else (theme.COLOR_WARN if "SHORT" in rec_status else theme.COLOR_ALERT)
        self.rec_lbl.configure(text=rec_status, text_color=rec_color)

    def reset(self):
        """Resets all metrics to optimal starting state."""
        self.stab_val.configure(text="92%", text_color=theme.COLOR_SUCCESS)
        self.stab_pill.configure(text="HIGHLY STABLE", text_color=theme.COLOR_SUCCESS)
        self.fat_val.configure(text="LOW", text_color=theme.COLOR_SUCCESS)
        self.risk_val.configure(text="LOW", text_color=theme.COLOR_SUCCESS)
        self.coach_val.configure(text="CALM", text_color=theme.COLOR_SUCCESS)
        self.rec_lbl.configure(text="CONTINUE TRAINING", text_color=theme.COLOR_SUCCESS)


class MovementIntelligenceDialog(ctk.CTkToplevel):
    """Detailed modal dialog displaying complete motion intelligence analytics."""

    def __init__(
        self,
        parent,
        exercise_name: str = "SQUAT",
        stability_data: Optional[Dict[str, Any]] = None,
        fatigue_data: Optional[Dict[str, Any]] = None,
        risk_data: Optional[Dict[str, Any]] = None,
        coach_data: Optional[Dict[str, Any]] = None,
        recovery_data: Optional[Dict[str, Any]] = None
    ):
        super().__init__(parent)
        self.title(f"REPRIGHT AI — Motion Intelligence Debrief ({exercise_name})")
        self.geometry("640x620")
        self.configure(fg_color=theme.COLOR_BG)
        self.transient(parent)
        self.grab_set()

        # Scrollable container
        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        header = ctk.CTkLabel(
            body,
            text="ADVANCED MOVEMENT INTELLIGENCE SUMMARY",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=theme.COLOR_ACCENT
        )
        header.pack(anchor="w", pady=(0, 10))

        # Cards for each dimension
        stab = stability_data or {}
        fat = fatigue_data or {}
        risk = risk_data or {}
        coach = coach_data or {}
        rec = recovery_data or {}

        self._create_card(body, "1. MOVEMENT STABILITY", f"{stab.get('stability_score', 90)}% • {stab.get('category_label', 'STABLE')}", stab.get("description", "Stable movement."), theme.COLOR_SUCCESS)
        self._create_card(body, "2. AI-ESTIMATED FORM FATIGUE", f"{fat.get('fatigue_label', 'LOW')}", fat.get("recommended_action", "Steady pacing."), theme.COLOR_WARN if fat.get("fatigue_level") == "MODERATE" else theme.COLOR_SUCCESS)
        self._create_card(body, "3. MOVEMENT RISK AWARENESS", f"{risk.get('risk_label', 'LOW')}", "\n".join(risk.get("recommendations", ["Within targets."])), theme.COLOR_ALERT if risk.get("risk_level") == "HIGH" else theme.COLOR_SUCCESS)
        self._create_card(body, "4. ADAPTIVE COACHING INTENSITY", f"{coach.get('mode_pill', 'CALM')}", f"Primary: {coach.get('primary_message', 'Optimal control.')}\nAction: {coach.get('recommended_action', 'Continue.')}", theme.COLOR_ACCENT)
        self._create_card(body, "5. SMART RECOVERY PROTOCOL", f"{rec.get('status_pill', 'CONTINUE')}", rec.get("suggested_action", "Maintain cadence."), theme.COLOR_SUCCESS)

        # Disclaimer
        disc = ctk.CTkLabel(
            body,
            text="Educational AI movement analysis — not clinical or medical diagnosis.",
            font=ctk.CTkFont(size=9),
            text_color=theme.COLOR_TEXT_MUTED
        )
        disc.pack(anchor="w", pady=(10, 6))

        # Close button
        btn = ctk.CTkButton(
            body,
            text="CLOSE INTELLIGENCE DASHBOARD",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=theme.COLOR_BUTTON_PRIMARY,
            command=self.destroy,
            height=36
        )
        btn.pack(fill="x", pady=(8, 4))

    def _create_card(self, parent, title: str, status: str, details: str, accent_color: str):
        card = ctk.CTkFrame(parent, fg_color=theme.COLOR_CARD_BG, border_width=1, border_color=theme.COLOR_BORDER, corner_radius=8)
        card.pack(fill="x", pady=5)

        h_row = ctk.CTkFrame(card, fg_color="transparent")
        h_row.pack(fill="x", padx=12, pady=(8, 2))

        ctk.CTkLabel(h_row, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color=theme.COLOR_TEXT_SECONDARY).pack(side="left")
        ctk.CTkLabel(h_row, text=status, font=ctk.CTkFont(size=11, weight="bold"), text_color=accent_color).pack(side="right")

        ctk.CTkLabel(card, text=details, font=ctk.CTkFont(size=10), text_color=theme.COLOR_TEXT_PRIMARY, wraplength=560, justify="left").pack(anchor="w", padx=12, pady=(2, 8))
