"""Viewport component displaying the video stream and live coach feedback banner.

Features a cyber-slate container, live AI status telemetry header, high-contrast video frame,
and dynamic feedback console with colored state tags.
"""

from typing import Optional, Dict, Any
import customtkinter as ctk
from ui import theme
from .posture_correction import PostureCorrectionCard


class ViewportFrame(ctk.CTkFrame):
    """Main video viewing area with live posture analysis feed and dynamic AI coach console."""

    STANDBY_MESSAGE = (
        "REPRIGHT BIOMECHANICAL VISION SYSTEM\n\n"
        "[ OPTICAL CAPTURE STANDBY ]\n\n"
        "• Position subject with full kinetic chain visible in frame\n"
        "• Maintain 6 to 8 feet distance from the optical sensor\n"
        "• Select an exercise protocol and click 'START WORKOUT' to initialize"
    )

    def __init__(
        self,
        master,
        on_toggle_guide: Optional[callable] = None,
        on_toggle_presentation: Optional[callable] = None,
        on_toggle_demo_mode: Optional[callable] = None,
        **kwargs
    ):
        super().__init__(
            master,
            corner_radius=12,
            fg_color=theme.COLOR_PANEL_BG,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            **kwargs
        )
        self.on_toggle_guide = on_toggle_guide
        self.on_toggle_presentation = on_toggle_presentation
        self.on_toggle_demo_mode = on_toggle_demo_mode
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ======================================================================
        # 1. TOP HEADER STATUS BAR
        # ======================================================================
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(14, 8), sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        # Left: Title + Active Exercise Tag + Capability Pill + Session Timer
        self.title_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_group.grid(row=0, column=0, sticky="w")

        self.header_title = ctk.CTkLabel(
            self.title_group,
            text="REAL-TIME BIOMECHANICAL ANALYSIS",
            font=ctk.CTkFont(size=theme.FONT_VIEWPORT_TITLE[1], weight="bold"),
            text_color=theme.COLOR_TEAL
        )
        self.header_title.pack(side="left", padx=(0, 10))

        self.exercise_badge = ctk.CTkLabel(
            self.title_group,
            text="SQUAT",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
            fg_color=theme.COLOR_CARD_ELEVATED,
            text_color=theme.COLOR_TEXT_PRIMARY,
            corner_radius=4,
            padx=8,
            pady=2
        )
        self.exercise_badge.pack(side="left", padx=(0, 6))

        # Capability Mode Pill
        self.mode_pill = ctk.CTkLabel(
            self.title_group,
            text="● ACTIVE AI",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
            fg_color=theme.COLOR_SUCCESS_MUTED,
            text_color=theme.COLOR_SUCCESS,
            corner_radius=4,
            padx=8,
            pady=2
        )
        self.mode_pill.pack(side="left", padx=(0, 6))

        # Live Session Timer
        self.timer_pill = ctk.CTkLabel(
            self.title_group,
            text="⏱ 00:00",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
            fg_color=theme.COLOR_CARD_BG,
            text_color=theme.COLOR_TEXT_SECONDARY,
            corner_radius=4,
            padx=8,
            pady=2
        )
        self.timer_pill.pack(side="left")

        # Right: Action controls & Live Stream Status Indicator Pill
        self.right_group = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.right_group.grid(row=0, column=2, sticky="e")

        if self.on_toggle_demo_mode:
            self.btn_demo_mode = ctk.CTkButton(
                self.right_group,
                text="DEMO LAB",
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
                height=28,
                corner_radius=6,
                fg_color=theme.COLOR_CARD_BG,
                hover_color=theme.COLOR_CARD_ELEVATED,
                border_width=1,
                border_color=theme.COLOR_BORDER,
                text_color=theme.COLOR_TEXT_SECONDARY,
                command=self.on_toggle_demo_mode
            )
            self.btn_demo_mode.pack(side="left", padx=(0, 8))
        else:
            self.btn_demo_mode = None

        if self.on_toggle_presentation:
            self.btn_presentation = ctk.CTkButton(
                self.right_group,
                text="PRESENTATION",
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
                height=28,
                corner_radius=6,
                fg_color=theme.COLOR_CARD_BG,
                hover_color=theme.COLOR_CARD_ELEVATED,
                border_width=1,
                border_color=theme.COLOR_BORDER,
                text_color=theme.COLOR_TEXT_SECONDARY,
                command=self.on_toggle_presentation
            )
            self.btn_presentation.pack(side="left", padx=(0, 8))
        else:
            self.btn_presentation = None

        if self.on_toggle_guide:
            self.btn_guide_toggle = ctk.CTkButton(
                self.right_group,
                text="FORM GUIDE",
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
                height=28,
                corner_radius=6,
                fg_color=theme.COLOR_CARD_BG,
                hover_color=theme.COLOR_CARD_ELEVATED,
                border_width=1,
                border_color=theme.COLOR_BORDER,
                text_color=theme.COLOR_TEXT_SECONDARY,
                command=self.on_toggle_guide
            )
            self.btn_guide_toggle.pack(side="left", padx=(0, 8))
        else:
            self.btn_guide_toggle = None

        self.status_pill = ctk.CTkLabel(
            self.right_group,
            text="○ STANDBY",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight="bold"),
            fg_color=theme.COLOR_CARD_BG,
            text_color=theme.COLOR_TEXT_MUTED,
            corner_radius=6,
            padx=10,
            pady=4
        )
        self.status_pill.pack(side="left")

        # ======================================================================
        # 2. VIDEO STREAM DISPLAY CARD
        # ======================================================================
        self.video_container = ctk.CTkFrame(
            self,
            corner_radius=12,
            fg_color=theme.COLOR_CARD_INNER,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        self.video_container.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.video_container.grid_columnconfigure(0, weight=1)
        self.video_container.grid_rowconfigure(0, weight=1)

        # Main video image display
        self.video_label = ctk.CTkLabel(
            self.video_container,
            text=self.STANDBY_MESSAGE,
            font=ctk.CTkFont(size=12),
            text_color=theme.COLOR_TEXT_MUTED,
            corner_radius=10,
            justify="center"
        )
        self.video_label.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")

        # ======================================================================
        # 3. AI POSTURE CORRECTION CONSOLE
        # ======================================================================
        self.posture_card = PostureCorrectionCard(self)
        self.posture_card.grid(row=2, column=0, padx=20, pady=(0, 14), sticky="ew")
        self.status_bar = self.posture_card  # Backwards compatibility

    def update_frame(self, ctk_img: ctk.CTkImage):
        """Updates the video display image with processed OpenCV frame."""
        self.video_label.configure(image=ctk_img, text="")

    def update_feedback(
        self,
        message: str,
        color: Optional[str] = None,
        exercise_name: str = "SQUAT"
    ) -> Dict[str, Any]:
        """Updates the AI posture correction console and returns structured classification data."""
        text_color = color or theme.COLOR_ACCENT
        return self.posture_card.update_correction(exercise_name, message, text_color)

    def set_active_state(self, is_running: bool):
        """Updates the stream status badge in the header."""
        if is_running:
            self.status_pill.configure(
                text="● LIVE AI ANALYSIS",
                text_color=theme.COLOR_SUCCESS,
                fg_color=theme.COLOR_SUCCESS_MUTED
            )
        else:
            self.status_pill.configure(
                text="○ SYSTEM STANDBY",
                text_color=theme.COLOR_TEXT_MUTED,
                fg_color=theme.COLOR_CARD_BG
            )
            self.posture_card.reset()

    def set_exercise(self, exercise_name: str, is_active_ai: bool = True):
        """Updates the active exercise badge and capability mode tag."""
        self.exercise_badge.configure(text=exercise_name.upper())
        self.set_exercise_mode(is_active_ai)

    def set_exercise_mode(self, is_active_ai: bool):
        """Updates the capability pill between Live AI Analysis and Guided Training Mode."""
        if is_active_ai:
            self.mode_pill.configure(
                text="● ACTIVE AI",
                text_color=theme.COLOR_SUCCESS,
                fg_color=theme.COLOR_SUCCESS_MUTED
            )
        else:
            self.mode_pill.configure(
                text="● GUIDED MODE",
                text_color=theme.COLOR_BLUE,
                fg_color=theme.COLOR_BLUE_MUTED
            )

    def update_timer(self, seconds: int):
        """Updates the session timer display."""
        mins = seconds // 60
        secs = seconds % 60
        self.timer_pill.configure(text=f"⏱ {mins:02d}:{secs:02d}")

    def set_presentation_state(self, is_presentation: bool):
        """Updates Presentation Mode toggle button styling."""
        if self.btn_presentation:
            if is_presentation:
                self.btn_presentation.configure(
                    text="✕ EXIT PRESENTATION",
                    fg_color=theme.COLOR_WARN_MUTED,
                    text_color=theme.COLOR_WARN
                )
            else:
                self.btn_presentation.configure(
                    text="🖥️ PRESENTATION",
                    fg_color=theme.COLOR_CARD_BG,
                    text_color=theme.COLOR_TEXT_SECONDARY
                )

    def set_guide_toggle_state(self, is_open: bool):
        """Updates guide toggle button label and accent styling."""
        if self.btn_guide_toggle:
            if is_open:
                self.btn_guide_toggle.configure(
                    text="✕ HIDE GUIDE",
                    fg_color=theme.COLOR_ACCENT_MUTED,
                    text_color=theme.COLOR_ACCENT
                )
            else:
                self.btn_guide_toggle.configure(
                    text="📖 FORM GUIDE",
                    fg_color=theme.COLOR_CARD_BG,
                    text_color=theme.COLOR_TEXT_SECONDARY
                )

    def show_standby(self):
        """Restores the initial standby message in the video viewport."""
        self.video_label.configure(image=None, text=self.STANDBY_MESSAGE)
        self.posture_card.reset()

    def reset_feedback(self):
        """Resets posture correction card to initial standby state."""
        self.posture_card.reset()



