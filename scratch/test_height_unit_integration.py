"""Verification test for Athlete Height Unit Selector (cm / ft)."""

import os
import sys
import tempfile
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.units import (
    parse_height_to_cm,
    convert_cm_to_ft_display,
    convert_height_between_units,
    format_height,
)
from services.auth_service import AuthService
from database.db_manager import init_db
from database.user_repository import UserRepository


def test_core_units_parsing():
    print("[TEST] 1. Testing core.units parsing...")
    cases = [
        ("175", "cm", 175.0),
        ("180.5", "cm", 180.5),
        ("175 cm", "cm", 175.0),
        ("5'9\"", "ft", 175.3),
        ("5'10\"", "ft", 177.8),
        ("5'11\"", "ft", 180.3),
        ("6'0\"", "ft", 182.9),
        ("5.9", "ft", 175.3),
        ("5.10", "ft", 177.8),
        ("5.11", "ft", 180.3),
        ("6.0", "ft", 182.9),
        ("6", "ft", 182.9),
        ("5ft 9in", "ft", 175.3),
        ("5ft9", "ft", 175.3),
        ("5-9", "ft", 175.3),
        ("5 9", "ft", 175.3),
        ("invalid", "cm", None),
        ("invalid", "ft", None),
        ("", "cm", None),
        (None, "ft", None),
    ]

    for val_str, unit, expected in cases:
        result = parse_height_to_cm(val_str, unit)
        assert result == expected, f"Failed for {val_str} ({unit}): got {result}, expected {expected}"
        print(f"  [OK] {str(val_str):>10} ({unit}) -> {result}")


def test_conversions_and_formatting():
    print("\n[TEST] 2. Testing conversions and display formatting...")
    # cm to ft display
    assert convert_cm_to_ft_display(175.0) == "5'9\""
    assert convert_cm_to_ft_display(183.0) == "6'0\""
    assert convert_cm_to_ft_display(165.0) == "5'5\""
    print("  [OK] convert_cm_to_ft_display verified")

    # between units conversion
    assert convert_height_between_units("175", "cm", "ft") == "5'9\""
    assert convert_height_between_units("5'9\"", "ft", "cm") == "175.3"
    print("  [OK] convert_height_between_units verified")

    # format_height
    assert format_height(175.0) == "175 cm (5'9\")"
    assert format_height(None) == "—"
    print("  [OK] format_height verified")


def test_auth_service_with_parsed_height():
    print("\n[TEST] 3. Testing database integration with feet input...")
    # Use temporary db
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        test_db_path = f.name

    try:
        init_db(test_db_path)
        repo = UserRepository(db_path=test_db_path)
        auth = AuthService(user_repo=repo)

        # Simulate athlete registering in feet: "5'10\""
        ft_input = "5'10\""
        parsed_cm = parse_height_to_cm(ft_input, "ft")
        assert parsed_cm == 177.8

        success, msg, user = auth.register(
            name="Sarah Connor",
            email="sarah@skynet.com",
            password="StrongPassword123!",
            height_cm=parsed_cm,
            weight_kg=62.0,
            fitness_goal="ENDURANCE"
        )
        assert success, f"Registration failed: {msg}"
        assert user.height_cm == 177.8
        print(f"  [OK] Registered Sarah with 5'10\" -> saved as {user.height_cm} cm in SQLite")

        # Simulate profile update in feet: "5.11"
        new_ft_input = "5.11"
        updated_cm = parse_height_to_cm(new_ft_input, "ft")
        assert updated_cm == 180.3

        up_success, up_msg, updated_user = auth.update_profile(
            user_id=user.id,
            name="Sarah Connor",
            height_cm=updated_cm,
            weight_kg=63.0,
            fitness_goal="MUSCLE_HYPERTROPHY"
        )
        assert up_success, f"Profile update failed: {up_msg}"
        assert updated_user.height_cm == 180.3
        print(f"  [OK] Updated profile with 5.11 -> updated to {updated_user.height_cm} cm in SQLite")

    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)


def test_ui_widget_instantiation():
    print("\n[TEST] 4. Testing RegisterScreen and UserProfile UI structure...")
    import customtkinter as ctk
    from ui.auth.register_screen import RegisterFrame
    from ui.components.user_profile import UserProfileDialog
    from database.models import User

    root = ctk.CTk()
    root.withdraw()

    reg_frame = RegisterFrame(root)
    assert hasattr(reg_frame, "height_entry")
    assert hasattr(reg_frame, "height_unit_opt")
    assert reg_frame.height_unit_opt.get() == "cm"
    assert reg_frame.height_entry.cget("placeholder_text") == "e.g. 175"

    # Simulate typing 175 in cm
    reg_frame.height_entry.insert(0, "175")
    # Simulate user changing dropdown to ft
    reg_frame.height_unit_opt.set("ft")
    reg_frame._on_height_unit_changed("ft")
    assert reg_frame.height_entry.get() == "5'9\""
    assert reg_frame.height_entry.cget("placeholder_text") == "e.g. 5'9\""

    # Simulate changing back to cm
    reg_frame.height_unit_opt.set("cm")
    reg_frame._on_height_unit_changed("cm")
    assert reg_frame.height_entry.get() == "175.3"
    assert reg_frame.height_entry.cget("placeholder_text") == "e.g. 175"
    print("  [OK] RegisterFrame dynamic height unit conversion works seamlessly")

    # Test UserProfileDialog
    mock_user = User(
        id=1,
        name="Test Athlete",
        email="test@athlete.com",
        password_hash="hash",
        height_cm=183.0,
        weight_kg=75.0,
        fitness_goal="STRENGTH"
    )
    dialog = UserProfileDialog(root, user=mock_user)
    assert hasattr(dialog, "height_entry")
    assert hasattr(dialog, "height_unit_opt")
    assert dialog.height_entry.get() == "183"

    # Switch to ft
    dialog.height_unit_opt.set("ft")
    dialog._on_height_unit_changed("ft")
    assert dialog.height_entry.get() == "6'0\""
    print("  [OK] UserProfileDialog dynamic height unit conversion works seamlessly")

    dialog.destroy()
    root.destroy()


if __name__ == "__main__":
    test_core_units_parsing()
    test_conversions_and_formatting()
    test_auth_service_with_parsed_height()
    test_ui_widget_instantiation()
    print("\n[SUCCESS] All height unit selector and conversion tests passed!")
