"""Exercise Library Modal Dialog Component.

Displays categorized exercise cards, capability state badges (Live AI Analysis vs Guided Mode),
muscle targets, and allows one-click switching of active or learning exercises.
"""

from typing import Callable, Optional, List, Dict, Any
import customtkinter as ctk
from ui import theme
from core.exercise_registry import (
    get_all_exercises,
    get_exercises_by_category,
    get_exercise_metadata
)


class ExerciseLibraryDialog(ctk.CTkToplevel):
    """Modern modal dialog for browsing the full exercise catalog and capability tiers."""

    def __init__(
        self,
        master,
        current_exercise: str,
        on_select_exercise: Callable[[str], None],
        **kwargs
    ):
        super().__init__(master, **kwargs)

        self.on_select_exercise = on_select_exercise
        self.current_exercise = current_exercise.upper().strip()
        self.selected_category = "ALL"

        self.title("REPRIGHT AI - Exercise Intelligence Library")
        self.geometry("820x660")
        self.minsize(720, 520)
        self.configure(fg_color=theme.COLOR_BG_DARK)

        # Center on parent window
        self.transient(master)
        self.after(10, self._center_on_master)

        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # ======================================================================
        # 1. HEADER SECTION
        # ======================================================================
        self.header_frame = ctk.CTkFrame(self, fg_color=theme.COLOR_PANEL_BG, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_content = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.header_content.pack(fill="x", padx=24, pady=16)

        self.title_label = ctk.CTkLabel(
            self.header_content,
            text="EXERCISE INTELLIGENCE LIBRARY",
            font=ctk.CTkFont(size=theme.FONT_BRAND[1], weight=theme.FONT_BRAND[2]),
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.title_label.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.header_content,
            text="Explore active real-time AI analysis models and guided biomechanical technique references.",
            font=ctk.CTkFont(size=theme.FONT_SUBTITLE[1]),
            text_color=theme.COLOR_TEXT_SECONDARY
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        # ======================================================================
        # 2. CATEGORY FILTER TABS
        # ======================================================================
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.grid(row=1, column=0, padx=24, pady=(12, 6), sticky="ew")

        categories = ["ALL", "LOWER BODY", "POSTERIOR CHAIN", "UPPER BODY", "CORE"]
        self.filter_buttons: Dict[str, ctk.CTkButton] = {}

        for cat in categories:
            btn = ctk.CTkButton(
                self.filter_frame,
                text=cat,
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
                height=30,
                corner_radius=8,
                fg_color=theme.COLOR_ACCENT_MUTED if cat == "ALL" else theme.COLOR_CARD_BG,
                hover_color=theme.COLOR_BORDER_LIGHT,
                text_color=theme.COLOR_ACCENT if cat == "ALL" else theme.COLOR_TEXT_SECONDARY,
                command=lambda c=cat: self._on_filter_changed(c)
            )
            btn.pack(side="left", padx=(0, 8))
            self.filter_buttons[cat] = btn

        # ======================================================================
        # 3. SCROLLABLE CATALOG CARDS
        # ======================================================================
        self.scroll_cards = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=theme.COLOR_BORDER,
            scrollbar_button_hover_color=theme.COLOR_BORDER_LIGHT
        )
        self.scroll_cards.grid(row=2, column=0, padx=20, pady=6, sticky="nsew")
        self.scroll_cards.grid_columnconfigure(0, weight=1)

        # ======================================================================
        # 4. FOOTER CONTROLS
        # ======================================================================
        self.footer_frame = ctk.CTkFrame(self, fg_color=theme.COLOR_PANEL_BG, corner_radius=0)
        self.footer_frame.grid(row=3, column=0, sticky="ew")

        self.footer_inner = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.footer_inner.pack(fill="x", padx=24, pady=12)

        self.footer_note = ctk.CTkLabel(
            self.footer_inner,
            text="* Live AI Analysis features YOLOv8 tracking. Guided Mode provides reference biomechanics & coaching cues.",
            font=ctk.CTkFont(size=theme.FONT_FOOTER[1]),
            text_color=theme.COLOR_TEXT_MUTED
        )
        self.footer_note.pack(side="left")

        self.btn_close = ctk.CTkButton(
            self.footer_inner,
            text="CLOSE",
            font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
            height=32,
            width=100,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_BORDER_LIGHT,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=self.destroy
        )
        self.btn_close.pack(side="right")

        # Initial card population
        self._populate_cards()

    def _center_on_master(self):
        """Centers the dialog over the parent application window."""
        try:
            self.update_idletasks()
            master = self.master
            mx = master.winfo_x()
            my = master.winfo_y()
            mw = master.winfo_width()
            mh = master.winfo_height()
            w = self.winfo_width()
            h = self.winfo_height()
            x = mx + max(0, (mw - w) // 2)
            y = my + max(0, (mh - h) // 2)
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _on_filter_changed(self, category: str):
        """Updates the category filter buttons and repopulates cards."""
        self.selected_category = category
        for cat, btn in self.filter_buttons.items():
            if cat == category:
                btn.configure(fg_color=theme.COLOR_ACCENT_MUTED, text_color=theme.COLOR_ACCENT)
            else:
                btn.configure(fg_color=theme.COLOR_CARD_BG, text_color=theme.COLOR_TEXT_SECONDARY)
        self._populate_cards()

    def _populate_cards(self):
        """Builds exercise card widgets based on the active category filter."""
        for child in self.scroll_cards.winfo_children():
            child.destroy()

        all_exercises = get_all_exercises()
        if self.selected_category != "ALL":
            filtered = [ex for ex in all_exercises if ex.get("category", "").upper() == self.selected_category]
        else:
            filtered = all_exercises

        for ex in filtered:
            ex_id = ex["id"]
            is_current = (ex_id == self.current_exercise)
            is_active = (ex["analysis_status"] == "ACTIVE")

            card = ctk.CTkFrame(
                self.scroll_cards,
                corner_radius=12,
                fg_color=theme.COLOR_CARD_BG,
                border_width=2 if is_current else 1,
                border_color=theme.COLOR_ACCENT if is_current else theme.COLOR_BORDER
            )
            card.pack(fill="x", padx=4, pady=6)
            card.grid_columnconfigure(0, weight=1)

            # Top Row: Title + Category Tag + Capability Badge
            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.pack(fill="x", padx=16, pady=(12, 4))

            left_group = ctk.CTkFrame(top_row, fg_color="transparent")
            left_group.pack(side="left")

            name_lbl = ctk.CTkLabel(
                left_group,
                text=ex["display_name"],
                font=ctk.CTkFont(size=theme.FONT_SECTION_HEADER[1], weight=theme.FONT_SECTION_HEADER[2]),
                text_color=theme.COLOR_TEXT_PRIMARY
            )
            name_lbl.pack(side="left", padx=(0, 10))

            cat_badge = ctk.CTkLabel(
                left_group,
                text=f"{ex.get('category', '').upper()} • {ex.get('difficulty', '').upper()}",
                font=ctk.CTkFont(size=9, weight="bold"),
                fg_color=theme.COLOR_CARD_INNER,
                text_color=theme.COLOR_TEXT_MUTED,
                corner_radius=4,
                padx=6,
                pady=2
            )
            cat_badge.pack(side="left")

            # Capability Pill on right
            status_color = theme.COLOR_SUCCESS if is_active else theme.COLOR_INFO
            status_bg = theme.COLOR_SUCCESS_MUTED if is_active else theme.COLOR_ACCENT_MUTED
            status_pill = ctk.CTkLabel(
                top_row,
                text=ex["status_label"],
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
                fg_color=status_bg,
                text_color=status_color,
                corner_radius=6,
                padx=10,
                pady=3
            )
            status_pill.pack(side="right")

            # Description
            desc_lbl = ctk.CTkLabel(
                card,
                text=ex.get("description", ""),
                font=ctk.CTkFont(size=11),
                text_color=theme.COLOR_TEXT_SECONDARY,
                wraplength=720,
                justify="left"
            )
            desc_lbl.pack(anchor="w", padx=16, pady=(2, 6))

            # Bottom Specs & Select Button Row
            bottom_row = ctk.CTkFrame(card, fg_color="transparent")
            bottom_row.pack(fill="x", padx=16, pady=(4, 12))

            specs_text = f"Primary Joint: {ex.get('primary_joint', '')}  •  Target: {ex.get('target_angle', '')}  •  Muscles: {', '.join(ex.get('primary_muscles', []))}"
            specs_lbl = ctk.CTkLabel(
                bottom_row,
                text=specs_text,
                font=ctk.CTkFont(size=10),
                text_color=theme.COLOR_TEXT_MUTED
            )
            specs_lbl.pack(side="left")

            # Select Button
            if is_current:
                btn_text = "CURRENTLY ACTIVE"
                btn_color = theme.COLOR_ACCENT_MUTED
                btn_hover = theme.COLOR_ACCENT_MUTED
                text_color = theme.COLOR_ACCENT
            elif is_active:
                btn_text = "SELECT AI TRAINING"
                btn_color = theme.COLOR_PRIMARY
                btn_hover = theme.COLOR_BORDER_LIGHT
                text_color = theme.COLOR_TEXT_PRIMARY
            else:
                btn_text = "VIEW GUIDED MODE"
                btn_color = theme.COLOR_CARD_INNER
                btn_hover = theme.COLOR_BORDER_LIGHT
                text_color = theme.COLOR_INFO

            btn_select = ctk.CTkButton(
                bottom_row,
                text=btn_text,
                font=ctk.CTkFont(size=theme.FONT_BADGE[1], weight=theme.FONT_BADGE[2]),
                height=30,
                corner_radius=6,
                fg_color=btn_color,
                hover_color=btn_hover,
                text_color=text_color,
                command=lambda eid=ex_id: self._select_and_close(eid)
            )
            btn_select.pack(side="right")

    def _select_and_close(self, exercise_id: str):
        """Executes callback to activate selected exercise and closes dialog."""
        self.on_select_exercise(exercise_id)
        self.destroy()
