"""REPRIGHT AI - Measurement and Unit Conversion Intelligence.

Provides standardized, bidirectional conversions between metric (cm, kg)
and imperial (ft, in, lbs) measurement systems with flexible input parsing.
"""

from typing import Optional, Tuple
import re


def parse_height_to_cm(val_str: Optional[str], unit: str = "cm") -> Optional[float]:
    """Parse a user-entered height string into centimeters.

    Supports both metric ('cm') and imperial ('ft') inputs.
    For imperial, seamlessly handles:
        - Word notations: "5ft 9in", "5 ft 9", "5ft9"
        - Feet-inch notations: "5'9\"", "5'10\"", "5' 9\"", "5-9", "5 9"
        - Gym shorthand decimals: "5.9" (5'9"), "5.10" (5'10"), "5.11" (5'11")
        - Pure/decimal feet: "6", "6.0", "5.75"

    Returns:
        float: Height in cm rounded to 1 decimal place, or None if invalid.
    """
    if val_str is None:
        return None
    
    clean = str(val_str).strip().lower()
    if not clean:
        return None

    try:
        if unit.lower() == "cm":
            # Remove any trailing "cm" or whitespace
            clean = clean.replace("cm", "").strip()
            val = float(clean)
            return round(val, 1) if val > 0 else None

        # Unit is ft / imperial
        clean = (
            clean.replace("feet", "ft")
            .replace("foot", "ft")
            .replace("inches", "in")
            .replace("inch", "in")
            .replace('”', '"')
            .replace('’', "'")
        )

        # 1. Explicit 'ft' indicator (e.g. "5ft 9in", "5ft 9", "5ft9", "6ft")
        if "ft" in clean:
            parts = clean.split("ft")
            feet_str = parts[0].strip()
            inch_str = parts[1].replace("in", "").replace('"', "").strip() if len(parts) > 1 else ""
            feet = float(feet_str) if feet_str else 0.0
            inches = float(inch_str) if inch_str else 0.0
            total_inches = (feet * 12.0) + inches
            return round(total_inches * 2.54, 1) if total_inches > 0 else None

        # Strip remaining "in" and quote marks
        clean = clean.replace("in", "").replace('"', "").strip()

        # 2. Foot symbol ' (e.g. 5'9", 5'9, 5' 9)
        if "'" in clean:
            parts = clean.split("'")
            feet = float(parts[0].strip() or 0)
            inches = float(parts[1].strip() or 0) if len(parts) > 1 and parts[1].strip() else 0.0
            total_inches = (feet * 12.0) + inches
            return round(total_inches * 2.54, 1) if total_inches > 0 else None

        # 3. Hyphen separated (e.g. 5-9, 5-10)
        if "-" in clean:
            parts = clean.split("-")
            if len(parts) == 2:
                feet = float(parts[0].strip() or 0)
                inches = float(parts[1].strip() or 0)
                total_inches = (feet * 12.0) + inches
                return round(total_inches * 2.54, 1) if total_inches > 0 else None

        # 4. Space separated (e.g. "5 9", "5 10")
        if " " in clean:
            parts = clean.split()
            if len(parts) == 2:
                feet = float(parts[0].strip() or 0)
                inches = float(parts[1].strip() or 0)
                total_inches = (feet * 12.0) + inches
                return round(total_inches * 2.54, 1) if total_inches > 0 else None

        # 5. Decimal notations (e.g. 5.9, 5.10, 5.11 vs 6.0, 5.75)
        if "." in clean:
            parts = clean.split(".")
            feet = float(parts[0] or 0)
            dec = parts[1].strip()
            # Gym/fitness shorthand convention: .10 and .11, or single digit .1-.9 -> inches
            if dec in ("10", "11") or len(dec) == 1:
                inches = float(dec)
                total_inches = (feet * 12.0) + inches
                return round(total_inches * 2.54, 1) if total_inches > 0 else None
            else:
                # True decimal feet (e.g. 5.75 ft)
                val = float(clean) * 30.48
                return round(val, 1) if val > 0 else None

        # 6. Pure integer feet (e.g. "6")
        val = float(clean) * 30.48
        return round(val, 1) if val > 0 else None

    except (ValueError, TypeError, IndexError):
        return None


def convert_cm_to_ft_display(cm_val: Optional[float]) -> str:
    """Convert centimeters into a standard feet-inches display string (e.g. 5'9\").

    Args:
        cm_val: Height in centimeters.

    Returns:
        Formatted string like "5'9\"", or empty string if invalid.
    """
    if cm_val is None or cm_val <= 0:
        return ""
    try:
        total_inches = cm_val / 2.54
        feet = int(total_inches // 12)
        inches = round(total_inches % 12)
        if inches >= 12:
            feet += 1
            inches = 0
        return f"{feet}'{inches}\""
    except (ValueError, TypeError):
        return ""


def convert_height_between_units(val_str: str, from_unit: str, to_unit: str) -> str:
    """Convert a height input string directly between 'cm' and 'ft' display formats.

    Args:
        val_str: The current user-entered value string.
        from_unit: Either 'cm' or 'ft'.
        to_unit: Either 'cm' or 'ft'.

    Returns:
        Formatted converted string, or original trimmed string if unparseable.
    """
    if not val_str or not val_str.strip():
        return ""
    
    clean = val_str.strip()
    if from_unit.lower() == to_unit.lower():
        return clean

    cm_val = parse_height_to_cm(clean, unit=from_unit)
    if cm_val is None:
        return clean

    if to_unit.lower() == "ft":
        return convert_cm_to_ft_display(cm_val)
    else:  # to_unit is cm
        # If integer cm, return as integer string
        if cm_val.is_integer():
            return str(int(cm_val))
        return f"{cm_val:.1f}"


def format_height(cm_val: Optional[float], include_ft: bool = True) -> str:
    """Format height in cm with optional feet-inches secondary label.

    Example:
        format_height(175.0) -> "175 cm (5'9\")"
    """
    if cm_val is None or cm_val <= 0:
        return "—"
    base = f"{cm_val:.0f} cm"
    if include_ft:
        ft_disp = convert_cm_to_ft_display(cm_val)
        if ft_disp:
            return f"{base} ({ft_disp})"
    return base

