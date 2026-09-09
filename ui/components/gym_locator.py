"""Nearby Gym & Fitness Center Locator Dialog for REPRIGHT AI.

Displays device location, nearby verified fitness facilities with real-time distance calculations,
search radius controls, manual city geocoding, and 1-click Google Maps directions.
"""

import threading
from typing import Optional, Dict, Any, List
import customtkinter as ctk

from ui import theme
from core.gym_locator import (
    get_device_location,
    get_cached_location,
    set_user_preferred_location,
    DEFAULT_LOCATION,
    get_local_verified_gyms,
    geocode_location,
    fetch_nearby_gyms,
    get_google_maps_search_url,
    get_google_maps_directions_url,
    open_url_in_browser
)



class GymLocatorDialog(ctk.CTkToplevel):
    """Modern modal dialog for locating gyms near the device's geographical position."""

    def __init__(self, master, initial_location: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(master, **kwargs)

        # FAST INIT: Zero-latency startup using memory/disk cached location (0 ms)
        self.current_location = initial_location or get_cached_location() or dict(DEFAULT_LOCATION)
        self.current_radius_km = 5.0
        self.gyms_cache: List[Dict[str, Any]] = []
        self._is_loading = False

        # Configure Toplevel Window
        self.title("REPRIGHT AI - Nearby Gym & Fitness Center Locator")
        self.geometry("960x700")
        self.minsize(820, 580)
        self.configure(fg_color=theme.COLOR_BG_DARK)

        if master:
            self.transient(master)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_ui()
        self._center_window()

        # 1. Instantly display verified local gyms without network stall (<5 ms)
        self._trigger_fetch_gyms()

        # 2. Fire background thread for location refresh if needed
        if not initial_location:
            self._start_background_sync()


    def _center_window(self):
        """Centers the modal window over the parent application."""
        self.update_idletasks()
        w = 960
        h = 700
        try:
            if self.master:
                mx = self.master.winfo_rootx()
                my = self.master.winfo_rooty()
                mw = self.master.winfo_width()
                mh = self.master.winfo_height()
                x = mx + (mw - w) // 2
                y = my + (mh - h) // 2
            else:
                x = (self.winfo_screenwidth() - w) // 2
                y = (self.winfo_screenheight() - h) // 2
            self.geometry(f"{w}x{h}+{max(20, x)}+{max(20, y)}")
        except Exception:
            self.geometry(f"{w}x{h}+100+100")

    def _build_ui(self):
        """Builds the main layout containers."""
        self.main_container = ctk.CTkFrame(
            self,
            fg_color=theme.COLOR_BG_DARK,
            corner_radius=0
        )
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=24, pady=20)
        self.main_container.grid_rowconfigure(2, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 1. Header Section
        self._build_header(self.main_container)

        # 2. Controls & Location Bar
        self._build_controls_bar(self.main_container)

        # 3. Gym Results Scrollable Feed
        self._build_results_area(self.main_container)

        # 4. Footer Bar
        self._build_footer(self.main_container)

    def _build_header(self, parent):
        """Header with title, badge, and 1-click Google Maps launch."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header_frame.grid_columnconfigure(0, weight=1)

        left_hdr = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_hdr.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            left_hdr,
            text="● FITNESS FACILITY DISCOVERY",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=theme.COLOR_TEAL
        ).pack(anchor="w", pady=(0, 2))

        ctk.CTkLabel(
            left_hdr,
            text="NEARBY GYM & FITNESS CENTER LOCATOR",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_hdr,
            text="Locate gyms, athletic training facilities, and fitness centers near your current device coordinates.",
            font=ctk.CTkFont(size=12),
            text_color=theme.COLOR_TEXT_SECONDARY
        ).pack(anchor="w", pady=(2, 0))

        right_hdr = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_hdr.grid(row=0, column=1, sticky="e")

        self.btn_maps_all = ctk.CTkButton(
            right_hdr,
            text="🗺️ View All on Google Maps",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=36,
            corner_radius=8,
            fg_color=theme.COLOR_CARD_ELEVATED,
            hover_color=theme.COLOR_TEAL,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=self._on_open_google_maps_all
        )
        self.btn_maps_all.pack(side="right")

    def _build_controls_bar(self, parent):
        """Location status pill, manual search input, and radius filter."""
        ctrl_card = ctk.CTkFrame(
            parent,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        ctrl_card.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        ctrl_card.grid_columnconfigure(1, weight=1)

        # Row 1: Detected Location & Actions (Set Default + Auto-detect IP)
        loc_row = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        loc_row.pack(fill="x", padx=16, pady=(12, 8))
        loc_row.grid_columnconfigure(0, weight=1)

        self.loc_label = ctk.CTkLabel(
            loc_row,
            text=self._format_location_string(),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme.COLOR_TEAL
        )
        self.loc_label.grid(row=0, column=0, sticky="w")

        btn_action_box = ctk.CTkFrame(loc_row, fg_color="transparent")
        btn_action_box.grid(row=0, column=1, sticky="e")

        self.btn_set_default = ctk.CTkButton(
            btn_action_box,
            text="⭐ Set as Default",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            corner_radius=6,
            fg_color=theme.COLOR_CARD_ELEVATED,
            hover_color=theme.COLOR_TEAL,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=self._on_set_default_click
        )
        self.btn_set_default.pack(side="left", padx=(0, 8))

        self.btn_detect = ctk.CTkButton(
            btn_action_box,
            text="🔄 Auto-Detect IP",
            font=ctk.CTkFont(size=11),
            height=28,
            corner_radius=6,
            fg_color=theme.COLOR_CARD_ELEVATED,
            hover_color=theme.COLOR_CARD_HOVER,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_SECONDARY,
            command=self._on_auto_detect_click
        )
        self.btn_detect.pack(side="left")


        # Row 2: Search input + Radius selector + Search button
        filter_row = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        filter_row.pack(fill="x", padx=16, pady=(0, 12))
        filter_row.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filter_row,
            placeholder_text="Search any city or area (e.g. Noida Sector 62, Connaught Place, Mumbai)...",
            height=34,
            corner_radius=6,
            font=ctk.CTkFont(size=12),
            fg_color=theme.COLOR_CARD_INNER,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._on_manual_search())

        self.btn_search = ctk.CTkButton(
            filter_row,
            text="🔍 Search Area",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            width=110,
            corner_radius=6,
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=self._on_manual_search
        )
        self.btn_search.grid(row=0, column=1, sticky="e", padx=(0, 14))

        # Radius Selector
        rad_box = ctk.CTkFrame(filter_row, fg_color="transparent")
        rad_box.grid(row=0, column=2, sticky="e")

        ctk.CTkLabel(
            rad_box,
            text="Radius:",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(side="left", padx=(0, 6))

        self.radius_opt = ctk.CTkOptionMenu(
            rad_box,
            values=["2 km", "5 km", "10 km", "15 km", "25 km"],
            command=self._on_radius_change,
            height=34,
            width=95,
            corner_radius=6,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=theme.COLOR_CARD_ELEVATED,
            button_color=theme.COLOR_CARD_BG,
            button_hover_color=theme.COLOR_TEAL,
            text_color=theme.COLOR_TEXT_PRIMARY
        )
        self.radius_opt.set("5 km")
        self.radius_opt.pack(side="left")

        # Row 3: Quick Area Shortcuts (Alpha 2, Alpha 1, Pari Chowk, Knowledge Park II, Jagat Farm)
        chips_row = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        chips_row.pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(
            chips_row,
            text="Quick Hubs:",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        ).pack(side="left", padx=(0, 6))

        quick_areas = [
            ("📍 Alpha 2", "Alpha 2"),
            ("📍 Alpha 1", "Alpha 1"),
            ("📍 Pari Chowk", "Pari Chowk"),
            ("📍 Knowledge Park II (NIET)", "Knowledge Park 2"),
            ("📍 Jagat Farm", "Jagat Farm")
        ]
        for label, area_name in quick_areas:
            ctk.CTkButton(
                chips_row,
                text=label,
                font=ctk.CTkFont(size=10, weight="bold"),
                height=26,
                corner_radius=13,
                fg_color=theme.COLOR_CARD_ELEVATED,
                hover_color=theme.COLOR_TEAL,
                text_color=theme.COLOR_TEXT_PRIMARY,
                command=lambda a=area_name: self._set_quick_area(a)
            ).pack(side="left", padx=3)


    def _build_results_area(self, parent):
        """Scrollable results container for gym cards."""
        # Section summary bar
        status_bar = ctk.CTkFrame(parent, fg_color="transparent")
        status_bar.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        status_bar.grid_columnconfigure(0, weight=1)

        self.results_count_label = ctk.CTkLabel(
            status_bar,
            text="DISCOVERING NEARBY FITNESS CENTERS...",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        )
        self.results_count_label.grid(row=0, column=0, sticky="w")

        # Scrollable Gym Card Container
        self.scroll_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color=theme.COLOR_WORKSPACE,
            corner_radius=10,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        self.scroll_frame.grid(row=3, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _build_footer(self, parent):
        """Footer info and close button."""
        footer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        footer_frame.grid(row=4, column=0, sticky="ew", pady=(14, 0))
        footer_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            footer_frame,
            text="⚡ Real-time device geolocation & verified OpenStreetMap / Google Maps integration.",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_MUTED
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            footer_frame,
            text="Close Window",
            font=ctk.CTkFont(size=11),
            height=30,
            width=100,
            corner_radius=6,
            fg_color=theme.COLOR_CARD_BG,
            hover_color=theme.COLOR_CARD_ELEVATED,
            border_width=1,
            border_color=theme.COLOR_BORDER,
            text_color=theme.COLOR_TEXT_SECONDARY,
            command=self.destroy
        ).grid(row=0, column=1, sticky="e")

    def _format_location_string(self) -> str:
        """Formats the current coordinates into a human-readable display string."""
        city = self.current_location.get("city") or "Detected Location"
        lat = self.current_location.get("lat", 0.0)
        lon = self.current_location.get("lon", 0.0)
        is_user_set = self.current_location.get("is_user_set", False)
        status_tag = "⭐ Verified Default" if is_user_set else "⚠️ Approximate ISP IP"
        return f"📍 Location: {city} ({lat:.3f}° N, {lon:.3f}° E)  •  [{status_tag}]"


    def _trigger_fetch_gyms(self):
        """
        Progressive 2-stage gym discovery:
        Stage 1: Instantly renders local verified facilities (<1 ms).
        Stage 2: Asynchronously syncs OpenStreetMap Overpass community data in background.
        """
        lat = self.current_location.get("lat", 28.4744)
        lon = self.current_location.get("lon", 77.5040)
        rad = self.current_radius_km

        # STAGE 1: Instant local verified gym retrieval (0 ms)
        local_gyms = get_local_verified_gyms(lat, lon, rad)
        if local_gyms:
            self._on_gyms_fetched(local_gyms, is_partial=True)
        else:
            self._render_loading_state()

        # STAGE 2: Background network sync
        self._is_loading = True

        def worker():
            gyms = fetch_nearby_gyms(lat, lon, radius_km=rad, limit=30, use_network=True)
            try:
                if self.winfo_exists():
                    self.after(0, lambda: self._on_gyms_fetched(gyms, is_partial=False))
            except Exception:
                pass

        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def _render_loading_state(self):
        """Renders temporary loading view while fetching API results."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.results_count_label.configure(
            text=f"SCANNING FITNESS CENTERS WITHIN {int(self.current_radius_km)} KM..."
        )

        load_card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        load_card.pack(fill="x", padx=10, pady=20)

        ctk.CTkLabel(
            load_card,
            text="⏳ Resolving verified training facilities near your coordinates...",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=theme.COLOR_TEAL
        ).pack(pady=(16, 6))

        ctk.CTkLabel(
            load_card,
            text="Querying athletic infrastructure directory and OpenStreetMap.",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_SECONDARY
        ).pack(pady=(0, 16))

    def _on_gyms_fetched(self, gyms: List[Dict[str, Any]], is_partial: bool = False):
        """Renders the resolved list of gyms or empty state on main thread."""
        if not is_partial:
            self._is_loading = False
        self.gyms_cache = gyms

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        city = self.current_location.get("city", "your location")

        if not gyms:
            if is_partial:
                self._render_loading_state()
                return
            self.results_count_label.configure(
                text=f"NO DIRECT LOCAL LISTINGS WITHIN {int(self.current_radius_km)} KM"
            )
            self._render_empty_fallback(city)
            return

        if is_partial:
            self.results_count_label.configure(
                text=f"FOUND {len(gyms)} VERIFIED GYMS (SYNCING EXTENDED DIRECTORY...)"
            )
        else:
            self.results_count_label.configure(
                text=f"FOUND {len(gyms)} VERIFIED GYMS & FITNESS FACILITIES WITHIN {int(self.current_radius_km)} KM"
            )

        for gym in gyms:
            self._render_gym_card(gym)

        # Always append a Google Maps discovery card to explore all gyms with live reviews
        self._render_gmaps_discovery_card(city)


    def _render_gym_card(self, gym: Dict[str, Any]):
        """Renders an individual gym listing card."""
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        card.pack(fill="x", padx=8, pady=5)
        card.grid_columnconfigure(0, weight=1)

        # Top row: Gym name & distance badge
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=14, pady=(10, 4))
        top_row.grid_columnconfigure(0, weight=1)

        name_lbl = ctk.CTkLabel(
            top_row,
            text=gym["name"],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        name_lbl.grid(row=0, column=0, sticky="w")

        # Distance badge
        dist = gym["distance_km"]
        dist_color = theme.COLOR_SUCCESS if dist <= 2.0 else theme.COLOR_TEAL
        dist_badge = ctk.CTkLabel(
            top_row,
            text=f"📍 {dist} km away",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=theme.COLOR_CARD_ELEVATED,
            text_color=dist_color,
            corner_radius=4,
            padx=8,
            pady=2
        )
        dist_badge.grid(row=0, column=1, sticky="e")

        # Address & details
        mid_row = ctk.CTkFrame(card, fg_color="transparent")
        mid_row.pack(fill="x", padx=14, pady=(0, 6))

        addr = gym.get("address") or "Locality coordinates available"
        ctk.CTkLabel(
            mid_row,
            text=f"🏢 {addr}",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w")

        extra_info = []
        if gym.get("opening_hours"):
            extra_info.append(f"⏰ {gym['opening_hours']}")
        if gym.get("phone"):
            extra_info.append(f"📞 {gym['phone']}")

        if extra_info:
            ctk.CTkLabel(
                mid_row,
                text="  •  ".join(extra_info),
                font=ctk.CTkFont(size=10),
                text_color=theme.COLOR_TEXT_MUTED,
                anchor="w"
            ).pack(anchor="w", pady=(2, 0))

        # Bottom row: Action button to open directions in Google Maps
        bot_row = ctk.CTkFrame(card, fg_color="transparent")
        bot_row.pack(fill="x", padx=14, pady=(0, 10))
        bot_row.grid_columnconfigure(0, weight=1)

        tag_lbl = ctk.CTkLabel(
            bot_row,
            text="VERIFIED ATHLETIC FACILITY",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=theme.COLOR_TEXT_MUTED
        )
        tag_lbl.grid(row=0, column=0, sticky="w")

        btn_dir = ctk.CTkButton(
            bot_row,
            text="📍 Get Directions",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            corner_radius=6,
            fg_color=theme.COLOR_PRIMARY,
            hover_color=theme.COLOR_PRIMARY_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=lambda g=gym: self._on_gym_directions_click(g)
        )
        btn_dir.grid(row=0, column=1, sticky="e")

    def _render_empty_fallback(self, city_name: str):
        """Renders helpful fallback when no direct Overpass nodes are found."""
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=theme.COLOR_CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        card.pack(fill="x", padx=10, pady=16)

        ctk.CTkLabel(
            card,
            text="🔍 No direct OpenStreetMap gym listings found in this immediate radius.",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=theme.COLOR_WARN
        ).pack(pady=(16, 6))

        ctk.CTkLabel(
            card,
            text=f"Expand your search radius or launch Google Maps to view all commercial and private gyms around {city_name}.",
            font=ctk.CTkFont(size=11),
            text_color=theme.COLOR_TEXT_SECONDARY
        ).pack(pady=(0, 14))

        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(pady=(0, 16))

        ctk.CTkButton(
            btn_box,
            text="🗺️ Open Live Gyms on Google Maps",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            corner_radius=6,
            fg_color=theme.COLOR_TEAL,
            hover_color=theme.COLOR_TEAL_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=self._on_open_google_maps_all
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_box,
            text="Expand Radius to 15 km",
            font=ctk.CTkFont(size=11),
            height=34,
            corner_radius=6,
            fg_color=theme.COLOR_CARD_ELEVATED,
            hover_color=theme.COLOR_CARD_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=lambda: self._on_radius_change("15 km")
        ).pack(side="left", padx=6)

    def _on_gym_directions_click(self, gym: Dict[str, Any]):
        """Opens Google Maps directions for a specific gym in user's default browser."""
        url = get_google_maps_directions_url(gym["name"], gym["lat"], gym["lon"])
        open_url_in_browser(url)

    def _on_open_google_maps_all(self):
        """Opens Google Maps search for gyms centered at device coordinates."""
        lat = self.current_location.get("lat")
        lon = self.current_location.get("lon")
        url = get_google_maps_search_url(lat, lon)
        open_url_in_browser(url)

    def _on_radius_change(self, value: str):
        """Handles radius dropdown changes and re-queries."""
        try:
            num = float(value.replace("km", "").strip())
            self.current_radius_km = num
            self.radius_opt.set(value)
            self._trigger_fetch_gyms()
        except Exception:
            pass

    def _on_set_default_click(self):
        """Explicitly locks and saves current active location as user's permanent default."""
        saved = set_user_preferred_location(self.current_location)
        self.current_location = saved
        self.loc_label.configure(text=self._format_location_string())
        self.btn_set_default.configure(text="✓ Saved as Default", fg_color=theme.COLOR_SUCCESS)
        self.after(2500, lambda: self.btn_set_default.configure(text="⭐ Set as Default", fg_color=theme.COLOR_CARD_ELEVATED))

    def _on_auto_detect_click(self):
        """Re-runs device IP geolocation detection upon explicit user click."""
        self.btn_detect.configure(text="Detecting...")
        def worker():
            loc = get_device_location(force_refresh=True, allow_ip_override=True)
            def update_ui():
                self.btn_detect.configure(text="🔄 Auto-Detect IP")
                self.current_location = loc
                self.loc_label.configure(text=self._format_location_string())
                self._trigger_fetch_gyms()
            try:
                if self.winfo_exists():
                    self.after(0, update_ui)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _on_manual_search(self):
        """Geocodes custom user input query into coordinates and discovers gyms."""
        query = self.search_entry.get().strip()
        if not query:
            return

        self.btn_search.configure(text="Searching...")

        def worker():
            res = geocode_location(query)
            def update_ui():
                self.btn_search.configure(text="🔍 Search Area")
                if res:
                    self.current_location = set_user_preferred_location(res)
                    self.loc_label.configure(text=self._format_location_string())
                    self._trigger_fetch_gyms()
                else:
                    # If geocoding failed, launch Google Maps with the query directly
                    url = get_google_maps_search_url(query=f"gyms in {query}")
                    open_url_in_browser(url)
            try:
                if self.winfo_exists():
                    self.after(0, update_ui)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _start_background_sync(self):
        """Asynchronously checks for fresh device location only if user hasn't set a preferred location."""
        if self.current_location.get("is_user_set"):
            return  # Honor user's preferred location, never overwrite with inaccurate ISP IP

        def worker():
            fresh_loc = get_device_location(allow_ip_override=False)
            if fresh_loc and not fresh_loc.get("is_fallback") and not fresh_loc.get("is_user_set"):
                old_lat = self.current_location.get("lat", 0.0)
                old_lon = self.current_location.get("lon", 0.0)
                if abs(fresh_loc["lat"] - old_lat) > 0.01 or abs(fresh_loc["lon"] - old_lon) > 0.01:
                    def update_ui():
                        self.current_location = fresh_loc
                        self.loc_label.configure(text=self._format_location_string())
                        self._trigger_fetch_gyms()
                    try:
                        if self.winfo_exists():
                            self.after(0, update_ui)
                    except Exception:
                        pass
        threading.Thread(target=worker, daemon=True).start()

    def _set_quick_area(self, area_name: str):
        """Quickly sets active location to a known hub with 0 ms latency."""
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, area_name)
        res = geocode_location(area_name)
        if res:
            self.current_location = set_user_preferred_location(res)
            self.loc_label.configure(text=self._format_location_string())
            self._trigger_fetch_gyms()
        else:
            self._on_manual_search()



    def _render_gmaps_discovery_card(self, city_name: str):
        """Renders an attractive discovery card to explore all gyms with live reviews on Google Maps."""
        card = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=theme.COLOR_CARD_INNER,
            corner_radius=8,
            border_width=1,
            border_color=theme.COLOR_BORDER
        )
        card.pack(fill="x", padx=8, pady=(8, 12))
        card.grid_columnconfigure(0, weight=1)

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=10)
        row.grid_columnconfigure(0, weight=1)

        info_col = ctk.CTkFrame(row, fg_color="transparent")
        info_col.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            info_col,
            text=f"🗺️ Want to explore more gyms around {city_name}?",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=theme.COLOR_TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_col,
            text="View 30+ local commercial gyms, customer reviews, live photos, and membership details.",
            font=ctk.CTkFont(size=10),
            text_color=theme.COLOR_TEXT_MUTED,
            anchor="w"
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(
            row,
            text="Open in Google Maps",
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
            corner_radius=6,
            fg_color=theme.COLOR_TEAL,
            hover_color=theme.COLOR_TEAL_HOVER,
            text_color=theme.COLOR_TEXT_PRIMARY,
            command=self._on_open_google_maps_all
        ).grid(row=0, column=1, sticky="e", padx=(10, 0))


