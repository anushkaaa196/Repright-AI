"""Automated verification suite for Gym Locator service and UI dialog."""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.gym_locator import (
    calculate_distance,
    get_device_location,
    get_google_maps_search_url,
    get_google_maps_directions_url,
    DEFAULT_LOCATION
)


def run_tests():
    print("============================================================")
    print("RUNNING GYM LOCATOR VERIFICATION TESTS")
    print("============================================================")

    # TEST 1: Distance Calculation (Haversine)
    print("\n--- TEST 1: Distance Calculation (Haversine) ---")
    # Distance between Greater Noida (28.4744, 77.5040) and Connaught Place, New Delhi (28.6315, 77.2167)
    d = calculate_distance(28.4744, 77.5040, 28.6315, 77.2167)
    print(f"Calculated distance: {d} km (Expected approx 32.5 km)")
    assert 30.0 <= d <= 35.0, f"Distance {d} out of expected range"

    # Same location distance is 0.0
    d_zero = calculate_distance(28.4744, 77.5040, 28.4744, 77.5040)
    assert d_zero == 0.0, f"Distance between identical points should be 0, got {d_zero}"
    print("[PASSED] TEST 1 PASSED: Haversine distance calculations verified.")

    # TEST 2: Device Location Detection
    print("\n--- TEST 2: Device Location Resolution ---")
    loc = get_device_location()
    print(f"Resolved Location: {loc.get('city')}, {loc.get('region')}, {loc.get('country')}")
    print(f"Coordinates: lat={loc.get('lat')}, lon={loc.get('lon')}")
    print(f"Is Fallback: {loc.get('is_fallback')}")

    assert "lat" in loc and isinstance(loc["lat"], (int, float))
    assert "lon" in loc and isinstance(loc["lon"], (int, float))
    assert "city" in loc
    assert "country" in loc
    print("[PASSED] TEST 2 PASSED: Device location payload strictly verified.")

    # TEST 3: Google Maps Link Generation
    print("\n--- TEST 3: Google Maps URL Generation ---")
    search_url = get_google_maps_search_url(28.4744, 77.5040)
    print(f"Search URL: {search_url}")
    assert "google.com/maps/search/gyms" in search_url
    assert "28.474400" in search_url
    assert "77.504000" in search_url

    dir_url = get_google_maps_directions_url("Gold's Gym", 28.4800, 77.5100)
    print(f"Directions URL: {dir_url}")
    assert "google.com/maps/dir" in dir_url
    assert "28.480000" in dir_url
    assert "77.510000" in dir_url
    print("[PASSED] TEST 3 PASSED: Maps URL formatting verified.")

    # TEST 4: UI Dialog Instantiation (Headless)
    print("\n--- TEST 4: GymLocatorDialog Instantiation ---")
    import customtkinter as ctk
    from ui.components.gym_locator import GymLocatorDialog

    root = ctk.CTk()
    root.withdraw()  # headless

    dialog = GymLocatorDialog(root, initial_location=DEFAULT_LOCATION)
    assert dialog.winfo_exists()
    assert dialog.current_radius_km == 5.0
    assert dialog.loc_label is not None
    assert dialog.search_entry is not None
    assert dialog.radius_opt is not None
    assert dialog.scroll_frame is not None
    assert dialog.btn_maps_all is not None

    # Test rendering dummy gym card
    dummy_gym = {
        "id": 12345,
        "name": "RepRight Test Athletic Club",
        "lat": 28.4790,
        "lon": 77.5090,
        "distance_km": 0.85,
        "address": "Knowledge Park II, Greater Noida",
        "opening_hours": "06:00 - 22:00",
        "phone": "+91 98765 43210",
        "website": "https://example.com"
    }
    dialog._render_gym_card(dummy_gym)
    children = dialog.scroll_frame.winfo_children()
    assert len(children) > 0
    print(f"Rendered dummy gym card, scroll frame children: {len(children)}")

    # Test empty fallback rendering
    dialog._render_empty_fallback("Greater Noida")
    dialog._render_gmaps_discovery_card("Greater Noida")

    dialog.destroy()
    root.destroy()
    print("[PASSED] TEST 4 PASSED: GymLocatorDialog successfully instantiated and tested headlessly.")

    # TEST 5: Alpha 2 Geocoding & Gym Discovery
    print("\n--- TEST 5: Alpha 2 Geocoding & Gym Discovery ---")
    from core.gym_locator import geocode_location, fetch_nearby_gyms
    alpha_loc = geocode_location("alpha 2")
    assert alpha_loc is not None, "Failed to resolve 'alpha 2'"
    print(f"Alpha 2 resolved: {alpha_loc['city']} ({alpha_loc['lat']}, {alpha_loc['lon']})")
    assert round(alpha_loc["lat"], 2) == 28.48, f"Unexpected lat: {alpha_loc['lat']}"

    alpha_gyms = fetch_nearby_gyms(alpha_loc["lat"], alpha_loc["lon"], radius_km=2.0)
    print(f"Found {len(alpha_gyms)} gyms within 2km of Alpha 2:")
    for g in alpha_gyms[:5]:
        print(f"  * {g['name']} ({g['distance_km']} km)")

    assert len(alpha_gyms) >= 5, f"Expected at least 5 gyms in Alpha 2, got {len(alpha_gyms)}"
    # Verify closest gym is within 0.5km
    assert alpha_gyms[0]["distance_km"] <= 0.5, f"Closest gym too far: {alpha_gyms[0]['distance_km']} km"
    print("[PASSED] TEST 5 PASSED: Alpha 2 location and nearby gyms fully verified.")

    print("\n============================================================")
    print("ALL 5 GYM LOCATOR TESTS PASSED!")
    print("============================================================")



if __name__ == "__main__":
    run_tests()
