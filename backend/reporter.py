"""REPRIGHT AI - Diagnostics & Exercise Performance Report Generator.

Generates high-resolution, presentation-grade biomechanical reports for Smart India Hackathon
showcasing real-time computer vision pose estimation, telemetry diagnostics, and actionable coaching.
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from core.session_insights import generate_session_insights
from core.rep_history import RepHistoryTracker
from core.personalized_coach import generate_personalized_plan
from core.progress_intelligence import ProgressIntelligenceTracker
from core.rep_analysis import DIMENSION_SCHEMAS
from core.fatigue_intelligence import estimate_form_fatigue
from core.risk_intelligence import evaluate_movement_risk
from core.adaptive_coaching import get_adaptive_coaching
from core.recovery_recommendations import get_recovery_recommendations
from core.performance_trends import analyze_performance_trends
from core.movement_stability import get_movement_stability_engine


# ==============================================================================
# COLOR PALETTE (Midnight Navy + Deep Teal + Emerald + Amber + Blue Theme)
# ==============================================================================
COLOR_BG = (11, 18, 32)              # #0B1220 Midnight Navy canvas
COLOR_PANEL = (22, 35, 56)           # #162338 Secondary card surface
COLOR_PANEL_ALT = (17, 28, 46)       # #111C2E Primary panel surface
COLOR_PANEL_ELEVATED = (27, 42, 66)  # #1B2A42 Elevated card
COLOR_BORDER = (38, 56, 82)          # #263852 Subtle border
COLOR_BORDER_LIGHT = (53, 80, 111)   # #35506F Hover border
COLOR_DIVIDER = (30, 44, 66)         # #1E2C42 Divider line

# Accents (Deep Teal & Professional Blue)
COLOR_ACCENT = (20, 184, 166)        # #14B8A6 Deep Teal Primary
COLOR_ACCENT_MUTED = (15, 56, 56)    # #0F3838 Soft Teal background
COLOR_ACCENT_HOVER = (13, 148, 136)  # #0D9488 Teal hover
COLOR_SUCCESS = (34, 197, 94)        # #22C55E Vibrant Emerald
COLOR_SUCCESS_MUTED = (13, 51, 34)   # #0D3322 Success badge background
COLOR_WARN = (245, 158, 11)          # #F59E0B Warm Amber Warning
COLOR_WARN_MUTED = (61, 40, 8)       # #3D2808 Warning badge background
COLOR_ALERT = (239, 68, 68)          # #EF4444 Refined Red Alert
COLOR_ALERT_MUTED = (61, 20, 24)     # #3D1418 Alert badge background
COLOR_INFO = (59, 130, 246)          # #3B82F6 Professional Blue

# Typography Colors
COLOR_TEXT_PRIMARY = (248, 250, 252) # #F8FAFC Clean crisp white
COLOR_TEXT_SECONDARY = (148, 163, 184) # #94A3B8 Cool slate gray
COLOR_TEXT_MUTED = (100, 116, 139)   # #64748B Muted slate


def _get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Loads crisp system TrueType fonts with seamless fallback to default."""
    font_candidates = (
        ["segoeuib.ttf", "arialbd.ttf", "segoeui.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"]
        if bold else
        ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]
    )
    for font_name in font_candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def format_quality_label(status: str, score: Optional[float] = None) -> str:
    """Format and humanize rep quality labels cleanly without technical underscores or truncation.

    Supported standard labels:
      - EXCELLENT (≥ 90%)
      - GOOD (75–89%)
      - NEEDS IMPROVEMENT (50–74%)
      - FORM CORRECTION REQUIRED (< 50%)
    """
    raw = (status or "").replace("_", " ").strip().upper()

    # Check explicitly recognized patterns
    if "EXCELLENT" in raw:
        return "EXCELLENT"
    if raw in ("GOOD", "PASS", "CLEAN"):
        return "GOOD"
    if "IMPROV" in raw or "FAILED DEPTH" in raw:
        return "NEEDS IMPROVEMENT"
    if "CORRECT" in raw or "FAILED SITTING" in raw or "FAIL" in raw or "ALERT" in raw or "WARN" in raw:
        return "FORM CORRECTION REQUIRED"

    # If raw status was generic or empty, infer from score if available
    if score is not None:
        if score >= 90:
            return "EXCELLENT"
        elif score >= 75:
            return "GOOD"
        elif score >= 50:
            return "NEEDS IMPROVEMENT"
        else:
            return "FORM CORRECTION REQUIRED"

    # Fallback to humanized string if non-empty, else "GOOD"
    return raw if raw else "GOOD"


def wrap_rep_status_lines(status: str, score: Optional[float] = None) -> List[str]:
    """Split rep quality labels into clean multi-line segments for compact card display.

    Returns:
      - ["EXCELLENT"]
      - ["GOOD"]
      - ["NEEDS", "IMPROVEMENT"]
      - ["FORM CORRECTION", "REQUIRED"]
    """
    label = format_quality_label(status, score)
    if label == "NEEDS IMPROVEMENT":
        return ["NEEDS", "IMPROVEMENT"]
    elif label == "FORM CORRECTION REQUIRED":
        return ["FORM CORRECTION", "REQUIRED"]
    elif " " in label:
        words = label.split()
        if len(words) == 2:
            return words
        mid = len(words) // 2
        return [" ".join(words[:mid]), " ".join(words[mid:])]
    return [label]


def fit_text_to_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_size: int,
    max_width: int,
    bold: bool = False,
    min_size: int = 7
) -> Tuple[ImageFont.ImageFont, str]:
    """Dynamically scales down font size until text fits within max_width without truncation."""
    curr_size = font_size
    while curr_size >= min_size:
        f = _get_font(curr_size, bold=bold)
        bbox = draw.textbbox((0, 0), text, font=f)
        if (bbox[2] - bbox[0]) <= max_width:
            return f, text
        curr_size -= 1
    return _get_font(min_size, bold=bold), text


def draw_right_aligned_text(
    draw: ImageDraw.ImageDraw,
    right_x: int,
    y: int,
    text: str,
    font: ImageFont.ImageFont,
    fill: Tuple[int, int, int]
) -> int:
    """Draws right-aligned text ending precisely at right_x. Returns rendered width."""
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    draw.text((right_x - w, y), text, font=font, fill=fill)
    return w


def _wrap_text(text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    """Wraps text cleanly within a maximum pixel width."""
    words = text.split()
    lines: List[str] = []
    current: List[str] = []
    for word in words:
        test_line = " ".join(current + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
                current = [word]
            else:
                lines.append(word)
                current = []
    if current:
        lines.append(" ".join(current))
    return lines


def _get_exercise_guidance(exercise_name: str) -> List[Tuple[str, str]]:
    """Returns verified exercise-specific biomechanical guidance points."""
    normalized = exercise_name.upper().strip()
    if normalized == "SQUAT":
        return [
            ("Spine & Torso", "Keep your spine in a neutral position with an upright chest."),
            ("Knee Tracking", "Keep knees aligned with your toes; avoid inward knee collapse."),
            ("Foot Placement", "Maintain stable tripod foot contact (heel, big toe, pinky toe)."),
            ("Depth Control", "Lower with control until thighs reach parallel with the floor."),
            ("Stability", "Avoid passive chair resting or sudden uncontrolled motion.")
        ]
    elif normalized == "DEADLIFT":
        return [
            ("Spine & Torso", "Maintain a rigid neutral spine throughout the entire lift."),
            ("Hip Hinge", "Drive the movement through your hips; avoid rounding lower back."),
            ("Balance & Path", "Keep weight balanced across midfoot with stable body posture."),
            ("Lockout", "Complete repetition with full hip extension without hyperextending back."),
            ("Cadence", "Maintain smooth, controlled eccentric lowering back to the floor.")
        ]
    elif normalized == "BICEP_CURL":
        return [
            ("Elbow Stability", "Keep your elbows pinned at your sides without swinging forward."),
            ("Torso Position", "Avoid body momentum or leaning backward to heave the weight."),
            ("Range of Motion", "Squeeze at peak contraction (flexion) and fully extend at bottom."),
            ("Symmetrical Control", "Maintain symmetrical tempo across both left and right arms."),
            ("Smooth Motion", "Lower the weight with a controlled eccentric tempo.")
        ]
    else:
        return [
            ("Alignment", "Maintain consistent posture and neutral spinal alignment."),
            ("Cadence", "Control motion tempo evenly during lifting and lowering phases."),
            ("Range of Motion", "Achieve target joint angle depth on every repetition cycle."),
            ("Stability", "Avoid relying on momentum or excessive secondary body sway."),
            ("Breathing", "Exhale during the concentric effort; inhale during the descent.")
        ]


def generate_report_image(
    exercise_name: str,
    stats: Dict[str, Any],
    output_path: Optional[str] = None
) -> str:
    """
    Generates and exports an off-screen session diagnostics report image.
    Transforms raw session telemetry into a high-resolution, SIH presentation-grade report.

    Parameters:
        exercise_name (str): The active exercise (e.g. SQUAT, DEADLIFT, BICEP_CURL).
        stats (Dict[str, Any]): Session telemetry dictionary from WorkoutEngine.
        output_path (str, optional): Target file path for saving PNG.

    Returns:
        str: The saved report image file path.
    """
    # --------------------------------------------------------------------------
    # 1. Parse Telemetry Data
    # --------------------------------------------------------------------------
    clean_reps = stats.get("clean_reps", 0)
    failed_depth = stats.get("failed_depth", 0)
    failed_sitting = stats.get("failed_sitting", 0)
    posture_warnings = stats.get("posture_warnings", 0)
    start_time = stats.get("start_time")

    total = clean_reps + failed_depth + failed_sitting
    # Use engine's calculated accuracy if available, else standard fallback
    if "accuracy" in stats and stats["accuracy"] is not None:
        acc = int(stats["accuracy"])
    else:
        acc = int((clean_reps / max(total, 1)) * 100) if total > 0 else 100

    duration_sec = time.time() - (start_time if start_time else time.time())
    duration_str = f"{int(duration_sec // 60):02d}:{int(duration_sec % 60):02d}"
    now_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --------------------------------------------------------------------------
    # 2. Performance Grade & Classification
    # --------------------------------------------------------------------------
    if acc >= 90:
        grade_label = "EXCELLENT FORM"
        grade_color = COLOR_SUCCESS
        grade_bg = COLOR_SUCCESS_MUTED
        coach_recommendation = (
            "Excellent movement quality detected. Continue maintaining controlled movement, "
            "consistent alignment, and proper exercise technique throughout each repetition."
        )
        focus_tone = "TARGET: SUSTAIN NEUROMUSCULAR CONTROL & POSTURAL CONSISTENCY"
    elif acc >= 75:
        grade_label = "GOOD FORM"
        grade_color = COLOR_ACCENT
        grade_bg = COLOR_ACCENT_MUTED
        coach_recommendation = (
            "Good overall movement quality detected. Focus on maintaining consistent posture "
            "and controlled movement throughout the complete exercise."
        )
        focus_tone = "TARGET: REFINE MOTION CADENCE & FULL RANGE-OF-MOTION LOCKOUT"
    elif acc >= 50:
        grade_label = "NEEDS IMPROVEMENT"
        grade_color = COLOR_WARN
        grade_bg = COLOR_WARN_MUTED
        coach_recommendation = (
            "Your exercise form shows areas for improvement. Slow down the movement and focus on "
            "maintaining proper alignment and controlled motion."
        )
        focus_tone = "TARGET: SLOW CADENCE DOWN & FOCUS ON JOINT ALIGNMENT"
    else:
        grade_label = "HIGH CORRECTION REQUIRED"
        grade_color = COLOR_ALERT
        grade_bg = COLOR_ALERT_MUTED
        coach_recommendation = (
            "Significant form improvement is recommended. Perform the movement slowly and carefully "
            "while focusing on proper alignment and controlled technique."
        )
        focus_tone = "TARGET: RESET TO BASELINE STANCE & PRACTICE CONTROLLED MOVEMENT"

    # --------------------------------------------------------------------------
    # 3. Canvas Setup & Typography (1200 x 1400 High-Resolution)
    # --------------------------------------------------------------------------
    WIDTH, HEIGHT = 1200, 1400
    img = Image.new("RGB", (WIDTH, HEIGHT), COLOR_BG)
    draw = ImageDraw.Draw(img)

    # Fonts
    font_badge = _get_font(10, bold=True)
    font_brand = _get_font(24, bold=True)
    font_sub = _get_font(11, bold=False)
    font_report_title = _get_font(18, bold=True)
    font_meta = _get_font(10, bold=False)

    font_kpi_label = _get_font(10, bold=True)
    font_kpi_val_big = _get_font(26, bold=True)
    font_kpi_val_med = _get_font(17, bold=True)
    font_kpi_sub = _get_font(9, bold=False)

    font_section_title = _get_font(12, bold=True)
    font_body = _get_font(11, bold=False)
    font_body_bold = _get_font(11, bold=True)
    font_footer = _get_font(9, bold=False)

    # Margins
    LEFT, RIGHT = 40, WIDTH - 40
    USABLE_WIDTH = RIGHT - LEFT

    # ==========================================================================
    # SECTION 1: REPORT HEADER
    # ==========================================================================
    header_top = 30

    # Top pill badge
    draw.rounded_rectangle(
        [LEFT, header_top, LEFT + 245, header_top + 22],
        radius=5,
        fill=COLOR_ACCENT_MUTED,
        outline=COLOR_BORDER
    )
    draw.text((LEFT + 10, header_top + 4), "● BIOMECHANICS & MOVEMENT LAB", font=font_badge, fill=COLOR_ACCENT)

    # Brand Title & Subtitle
    draw.text((LEFT, header_top + 30), "REPRIGHT AI", font=font_brand, fill=COLOR_TEXT_PRIMARY)
    draw.text((LEFT, header_top + 64), "SPORTS BIOMECHANICS & ATHLETIC PERFORMANCE INTELLIGENCE", font=font_sub, fill=COLOR_TEXT_SECONDARY)

    # Right side: Main Title & Meta Info
    title_text = "EXERCISE PERFORMANCE REPORT"
    bbox_t = draw.textbbox((0, 0), title_text, font=font_report_title)
    w_t = bbox_t[2] - bbox_t[0]
    draw.text((RIGHT - w_t, header_top + 16), title_text, font=font_report_title, fill=COLOR_ACCENT)

    tech_sub = "COMPUTER VISION • POSE ESTIMATION • BIOMECHANICS"
    bbox_tech = draw.textbbox((0, 0), tech_sub, font=font_badge)
    w_tech = bbox_tech[2] - bbox_tech[0]
    draw.text((RIGHT - w_tech, header_top + 45), tech_sub, font=font_badge, fill=COLOR_TEXT_MUTED)

    meta_str = f"Date: {now_dt}   |   Session Duration: {duration_str}"
    bbox_m = draw.textbbox((0, 0), meta_str, font=font_meta)
    w_m = bbox_m[2] - bbox_m[0]
    draw.text((RIGHT - w_m, header_top + 64), meta_str, font=font_meta, fill=COLOR_TEXT_SECONDARY)

    # Header Separator
    draw.line([LEFT, 116, RIGHT, 116], fill=COLOR_DIVIDER, width=1)

    # ==========================================================================
    # SECTION 2: SESSION SUMMARY (4 KPI Analytics Cards)
    # ==========================================================================
    kpi_top = 130
    kpi_height = 100
    gap = 16
    kpi_width = (USABLE_WIDTH - (3 * gap)) // 4

    focus_map = {
        "SQUAT": "Knee & Torso Angles",
        "DEADLIFT": "Hip Hinge & Spine",
        "BICEP_CURL": "Dual Elbow Flexion"
    }
    exercise_focus = focus_map.get(exercise_name.upper(), "Joint Biomechanics")

    kpi_cards = [
        {
            "label": "EXERCISE",
            "val": exercise_name.upper(),
            "val_color": COLOR_ACCENT,
            "sub": exercise_focus,
            "is_big": False
        },
        {
            "label": "CLEAN REPETITIONS",
            "val": str(clean_reps),
            "val_color": COLOR_SUCCESS,
            "sub": f"Total Attempts: {total}",
            "is_big": True
        },
        {
            "label": "FORM QUALITY SCORE",
            "val": f"{acc}%",
            "val_color": grade_color,
            "sub": grade_label,
            "is_big": True
        },
        {
            "label": "SESSION DURATION",
            "val": duration_str,
            "val_color": COLOR_TEXT_PRIMARY,
            "sub": "Active Movement",
            "is_big": False
        }
    ]

    for i, card in enumerate(kpi_cards):
        cx0 = LEFT + i * (kpi_width + gap)
        cx1 = cx0 + kpi_width
        cy0 = kpi_top
        cy1 = cy0 + kpi_height

        draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=10, fill=COLOR_PANEL, outline=COLOR_BORDER, width=1)
        draw.text((cx0 + 16, cy0 + 12), card["label"], font=font_kpi_label, fill=COLOR_TEXT_MUTED)

        val_font = font_kpi_val_big if card["is_big"] else font_kpi_val_med
        draw.text((cx0 + 16, cy0 + 34), card["val"], font=val_font, fill=card["val_color"])
        draw.text((cx0 + 16, cy0 + 74), card["sub"], font=font_kpi_sub, fill=COLOR_TEXT_SECONDARY)

    # ==========================================================================
    # SECTION 3: PERFORMANCE SCORECARD & BIOMECHANICAL DIAGNOSTICS
    # ==========================================================================
    sec3_top = 246
    sec3_height = 145
    split_gap = 18
    col_w = (USABLE_WIDTH - split_gap) // 2

    # Left Card: Scorecard with Visual Progress Bar
    l_x0, l_y0 = LEFT, sec3_top
    l_x1, l_y1 = l_x0 + col_w, l_y0 + sec3_height
    draw.rounded_rectangle([l_x0, l_y0, l_x1, l_y1], radius=10, fill=COLOR_PANEL, outline=COLOR_BORDER, width=1)
    draw.text((l_x0 + 18, l_y0 + 14), "FORM QUALITY SCORECARD", font=font_section_title, fill=COLOR_TEXT_PRIMARY)

    bbox_bg = draw.textbbox((0, 0), grade_label, font=font_badge)
    bg_w = bbox_bg[2] - bbox_bg[0] + 16
    draw.rounded_rectangle([l_x1 - 18 - bg_w, l_y0 + 12, l_x1 - 18, l_y0 + 32], radius=4, fill=grade_bg, outline=COLOR_BORDER)
    draw.text((l_x1 - 18 - bg_w + 8, l_y0 + 16), grade_label, font=font_badge, fill=grade_color)

    bar_x0 = l_x0 + 18
    bar_x1 = l_x1 - 18
    bar_w = bar_x1 - bar_x0
    bar_y0 = l_y0 + 58
    bar_y1 = bar_y0 + 14

    draw.rounded_rectangle([bar_x0, bar_y0, bar_x1, bar_y1], radius=6, fill=COLOR_PANEL_ALT, outline=COLOR_BORDER)
    fill_w = max(10, int(bar_w * max(0.0, min(1.0, acc / 100.0))))
    draw.rounded_rectangle([bar_x0, bar_y0, bar_x0 + fill_w, bar_y1], radius=6, fill=grade_color)

    draw.text((bar_x0, bar_y0 + 20), "0%", font=font_kpi_sub, fill=COLOR_TEXT_MUTED)
    draw.text((bar_x0 + int(bar_w * 0.5) - 30, bar_y0 + 20), "50% High Correction", font=font_kpi_sub, fill=COLOR_TEXT_MUTED)
    draw.text((bar_x0 + int(bar_w * 0.75) - 25, bar_y0 + 20), "75% Needs Imprv", font=font_kpi_sub, fill=COLOR_TEXT_MUTED)
    draw.text((bar_x1 - 65, bar_y0 + 20), "90% Excellent", font=font_kpi_sub, fill=COLOR_TEXT_MUTED)

    draw.text(
        (bar_x0, l_y1 - 28),
        f"Verified Quality Index: {acc}% • Calculated strictly from validated camera repetitions.",
        font=font_sub,
        fill=COLOR_TEXT_SECONDARY
    )

    # Right Card: Biomechanical Repetition Diagnostics
    r_x0, r_y0 = l_x1 + split_gap, sec3_top
    r_x1, r_y1 = RIGHT, r_y0 + sec3_height
    draw.rounded_rectangle([r_x0, r_y0, r_x1, r_y1], radius=10, fill=COLOR_PANEL, outline=COLOR_BORDER, width=1)
    draw.text((r_x0 + 18, r_y0 + 14), "BIOMECHANICAL REPETITION DIAGNOSTICS", font=font_section_title, fill=COLOR_TEXT_PRIMARY)

    diag_items = [
        ("Total Movement Cycles Attempted", str(total), COLOR_TEXT_PRIMARY),
        ("Incomplete Range of Motion (Failed Depth)", str(failed_depth), COLOR_WARN if failed_depth > 0 else COLOR_TEXT_MUTED),
        ("Passive Sitting / Chair Disqualifications", str(failed_sitting), COLOR_ALERT if failed_sitting > 0 else COLOR_TEXT_MUTED),
        ("Torso Alignment / Spine Lean Warnings", str(posture_warnings), COLOR_WARN if posture_warnings > 0 else COLOR_TEXT_MUTED)
    ]

    row_y = r_y0 + 44
    for label, val_str, val_col in diag_items:
        draw.text((r_x0 + 18, row_y), f"•  {label}", font=font_sub, fill=COLOR_TEXT_SECONDARY)
        draw_right_aligned_text(draw, r_x1 - 20, row_y, val_str, font_body_bold, val_col)
        row_y += 22

    # ==========================================================================
    # SECTION 4: REP-BY-REP TIMELINE & BIOMECHANICAL QUALITY BREAKDOWN (PHASE 5)
    # ==========================================================================
    sec4_top = 405
    sec4_height = 150

    rep_tracker = RepHistoryTracker.get_instance()
    reps_data = rep_tracker.get_all_reps()
    dim_avgs = rep_tracker.get_dimension_averages()
    schema = DIMENSION_SCHEMAS.get(exercise_name.upper(), DIMENSION_SCHEMAS["DEFAULT"])

    # Left: Rep-by-Rep Performance Timeline
    rep_x0, rep_y0 = LEFT, sec4_top
    rep_x1, rep_y1 = rep_x0 + col_w, rep_y0 + sec4_height
    draw.rounded_rectangle([rep_x0, rep_y0, rep_x1, rep_y1], radius=10, fill=COLOR_PANEL, outline=COLOR_BORDER, width=1)
    draw.text((rep_x0 + 18, rep_y0 + 14), "REP-BY-REP PERFORMANCE LOG", font=font_section_title, fill=COLOR_ACCENT)

    if reps_data:
        # Display up to 5 recent reps horizontally
        display_reps = reps_data[-5:]
        rep_box_w = (col_w - 36 - ((len(display_reps) - 1) * 8)) // max(1, len(display_reps))
        rx = rep_x0 + 18
        max_card_text_w = rep_box_w - 16

        for r_idx, r_item in enumerate(display_reps):
            r_num = r_item.get("rep_number", r_idx + 1)
            r_score = r_item.get("overall_score", 100)
            r_status = r_item.get("status", "")
            r_col = (
                COLOR_SUCCESS if r_score >= 90 else
                COLOR_ACCENT if r_score >= 75 else
                COLOR_WARN if r_score >= 50 else
                COLOR_ALERT
            )

            card_y0 = rep_y0 + 44
            card_y1 = rep_y1 - 18
            draw.rounded_rectangle([rx, card_y0, rx + rep_box_w, card_y1], radius=6, fill=COLOR_PANEL_ALT, outline=COLOR_BORDER)
            draw.text((rx + 8, card_y0 + 8), f"REP #{r_num:02d}", font=font_kpi_sub, fill=COLOR_TEXT_MUTED)
            draw.text((rx + 8, card_y0 + 24), f"{r_score}%", font=font_body_bold, fill=r_col)

            # Multi-line wrapped quality label (Never clipped or sliced)
            status_lines = wrap_rep_status_lines(r_status, r_score)
            if len(status_lines) == 1:
                f_st, _ = fit_text_to_width(draw, status_lines[0], font_size=8, max_width=max_card_text_w, bold=True, min_size=7)
                draw.text((rx + 8, card_y0 + 46), status_lines[0], font=f_st, fill=r_col)
            else:
                for sl_idx, s_line in enumerate(status_lines):
                    f_st, _ = fit_text_to_width(draw, s_line, font_size=8, max_width=max_card_text_w, bold=True, min_size=7)
                    draw.text((rx + 8, card_y0 + 44 + (sl_idx * 13)), s_line, font=f_st, fill=r_col)

            rx += rep_box_w + 8
    else:
        draw.text((rep_x0 + 18, rep_y0 + 55), "Movement tracking active. Rep-by-rep telemetry recorded on completion.", font=font_body, fill=COLOR_TEXT_MUTED)

    draw.text((rep_x0 + 18, rep_y1 - 16), "AI-Estimated Biomechanical Quality • Individual Repetition Analysis", font=font_footer, fill=COLOR_TEXT_MUTED)

    # Right: Biomechanical Performance Breakdown (5 Dimensions)
    bd_x0, bd_y0 = l_x1 + split_gap, sec4_top
    bd_x1, bd_y1 = RIGHT, bd_y0 + sec4_height
    draw.rounded_rectangle([bd_x0, bd_y0, bd_x1, bd_y1], radius=10, fill=COLOR_PANEL, outline=COLOR_BORDER, width=1)
    draw.text((bd_x0 + 18, bd_y0 + 14), "BIOMECHANICAL QUALITY BREAKDOWN", font=font_section_title, fill=COLOR_TEXT_PRIMARY)

    dims_order = ["range_of_motion", "alignment", "stability", "movement_control", "consistency"]
    by = bd_y0 + 40
    for dk in dims_order:
        d_name = schema.get(dk, dk.replace("_", " ").title())
        d_val = dim_avgs.get(dk, acc)
        d_col = COLOR_SUCCESS if d_val >= 90 else COLOR_ACCENT if d_val >= 75 else COLOR_WARN if d_val >= 50 else COLOR_ALERT

        draw.text((bd_x0 + 18, by), d_name, font=font_kpi_sub, fill=COLOR_TEXT_SECONDARY)
        # Mini bar
        mb_x0 = bd_x0 + 160
        mb_w = 260
        mb_fill = int(mb_w * max(0.0, min(1.0, d_val / 100.0)))
        draw.rounded_rectangle([mb_x0, by + 2, mb_x0 + mb_w, by + 10], radius=3, fill=COLOR_PANEL_ALT, outline=COLOR_BORDER)
        draw.rounded_rectangle([mb_x0, by + 2, mb_x0 + mb_fill, by + 10], radius=3, fill=d_col)
        draw_right_aligned_text(draw, bd_x1 - 18, by - 1, f"{d_val}%", font_kpi_sub, d_col)
        by += 20

    # ==========================================================================
    # SECTION 5: AI FORM ASSESSMENT & PERSONALIZED TRAINING PLAN (PHASE 5)
    # ==========================================================================
    sec5_top = 570
    sec5_height = 160

    insights = generate_session_insights(exercise_name, stats, int(duration_sec))
    plan = generate_personalized_plan(exercise_name, rep_tracker, stats)

    # Left: AI Form Assessment
    a_x0, a_y0 = LEFT, sec5_top
    a_x1, a_y1 = a_x0 + col_w, a_y0 + sec5_height
    draw.rounded_rectangle([a_x0, a_y0, a_x1, a_y1], radius=10, fill=COLOR_PANEL, outline=COLOR_BORDER, width=1)
    draw.text((a_x0 + 18, a_y0 + 14), "AI FORM ASSESSMENT", font=font_section_title, fill=COLOR_ACCENT)

    if failed_depth > 0 and failed_sitting > 0:
        diag_statement = f"Detected {failed_depth} shallow repetition(s) and {failed_sitting} passive chair pause(s)."
    elif failed_depth > 0:
        diag_statement = f"{failed_depth} repetition(s) failed to satisfy target joint range-of-motion depth."
    elif failed_sitting > 0:
        diag_statement = f"{failed_sitting} repetition(s) disqualified due to passive sitting posture."
    elif clean_reps > 0:
        diag_statement = "All completed repetitions satisfied biomechanical depth and stability standards."
    else:
        diag_statement = "Session recorded without full movement cycles completed."

    assessment_bullets = [
        ("• Pose Tracking:", "YOLOv8 neural network verified 17 anatomical keypoints in real time."),
        ("• Performance:", f"{insights['tier_badge']} ({clean_reps} clean / {total} total attempts)."),
        ("• Motion Analysis:", diag_statement),
        ("• Primary Focus:", f"{insights['primary_focus']} target identified.")
    ]

    ay = a_y0 + 44
    for b_title, b_desc in assessment_bullets:
        draw.text((a_x0 + 18, ay), b_title, font=font_body_bold, fill=COLOR_TEXT_PRIMARY)
        # Wrap description if needed
        wrapped = _wrap_text(b_desc, font_body, col_w - 150, draw)
        for line in wrapped:
            draw.text((a_x0 + 140, ay), line, font=font_body, fill=COLOR_TEXT_SECONDARY)
            ay += 18
        ay += 4

    # Right: Personalized AI Improvement Plan
    p_x0, p_y0 = l_x1 + split_gap, sec5_top
    p_x1, p_y1 = RIGHT, p_y0 + sec5_height
    draw.rounded_rectangle([p_x0, p_y0, p_x1, p_y1], radius=10, fill=COLOR_PANEL, outline=COLOR_BORDER, width=1)
    draw.text((p_x0 + 18, p_y0 + 14), "PERSONALIZED AI IMPROVEMENT PLAN", font=font_section_title, fill=grade_color)

    py_plan = p_y0 + 44
    for s_line in _wrap_text(f"• Strength: {plan['strength']}", font_body, col_w - 36, draw):
        draw.text((p_x0 + 18, py_plan), s_line, font=font_body, fill=COLOR_SUCCESS)
        py_plan += 17
    for f_line in _wrap_text(f"• Focus: {plan['primary_focus']}", font_body_bold, col_w - 36, draw):
        draw.text((p_x0 + 18, py_plan), f_line, font=font_body_bold, fill=COLOR_TEXT_PRIMARY)
        py_plan += 17
    for cline in _wrap_text(f"• Coaching Cue: {plan['coaching_cue']}", font_body, col_w - 36, draw):
        draw.text((p_x0 + 18, py_plan), cline, font=font_body, fill=COLOR_ACCENT)
        py_plan += 17
    for g_line in _wrap_text(f"• Goal: {plan['next_session_goal']}", font_body, col_w - 36, draw):
        draw.text((p_x0 + 18, py_plan), g_line, font=font_body, fill=COLOR_TEXT_SECONDARY)
        py_plan += 17

    draw.text((p_x0 + 18, p_y1 - 22), "Educational & Training Guidance • Not a medical diagnostic device.", font=font_footer, fill=COLOR_TEXT_MUTED)

    # ==========================================================================
    # SECTION 6: HOW TO IMPROVE YOUR FORM & BIOMECHANICAL STANDARDS
    # ==========================================================================
    sec6_top = 745
    sec6_height = 235

    draw.rounded_rectangle([LEFT, sec6_top, RIGHT, sec6_top + sec6_height], radius=10, fill=COLOR_PANEL, outline=COLOR_BORDER, width=1)
    draw.text((LEFT + 18, sec6_top + 14), "HOW TO IMPROVE YOUR FORM", font=font_section_title, fill=COLOR_TEXT_PRIMARY)
    draw_right_aligned_text(draw, RIGHT - 18, sec6_top + 16, focus_tone, font_badge, grade_color)
    draw.line([LEFT + 18, sec6_top + 38, RIGHT - 18, sec6_top + 38], fill=COLOR_DIVIDER, width=1)

    col1_x0 = LEFT + 18
    col1_w = (USABLE_WIDTH // 2) - 24
    col2_x0 = col1_x0 + col1_w + 24

    draw.text((col1_x0, sec6_top + 48), f"BIOMECHANICAL STANDARDS ({exercise_name.upper()})", font=font_badge, fill=COLOR_ACCENT)
    guidance_items = _get_exercise_guidance(exercise_name)
    gy = sec6_top + 70
    for title, desc in guidance_items[:4]:
        draw.line([(col1_x0, gy + 6), (col1_x0 + 4, gy + 11), (col1_x0 + 11, gy + 2)], fill=COLOR_SUCCESS, width=2)
        draw.text((col1_x0 + 18, gy), f"{title}:", font=font_body_bold, fill=COLOR_TEXT_PRIMARY)
        desc_wrapped = _wrap_text(desc, font_body, col1_w - 140, draw)
        for idx, d_line in enumerate(desc_wrapped):
            draw.text((col1_x0 + 135, gy + idx * 16), d_line, font=font_body, fill=COLOR_TEXT_SECONDARY)
        gy += max(20, len(desc_wrapped) * 16 + 4)

    draw.text((col2_x0, sec6_top + 48), "NEXT SESSION STRATEGY & ACTION PLAN", font=font_badge, fill=COLOR_ACCENT)
    action_plan = [
        ("1. Stance Calibration:", "Stand still in camera frame for 2 seconds before rep 1 to calibrate baseline."),
        ("2. Cadence & Tempo:", "Use a 2-second eccentric descent and a 1-second upward concentric drive."),
        ("3. Range of Motion:", "Prioritize depth precision over speed; lockout completely at top."),
        ("4. Live Audio & Visuals:", "Watch live coach banner cues to fix form errors before rep finishes.")
    ]
    py = sec6_top + 70
    for step_title, step_desc in action_plan:
        draw.text((col2_x0, py), step_title, font=font_body_bold, fill=COLOR_TEXT_PRIMARY)
        wrapped_step = _wrap_text(step_desc, font_body, col1_w - 150, draw)
        for idx, s_line in enumerate(wrapped_step):
            draw.text((col2_x0 + 145, py + idx * 16), s_line, font=font_body, fill=COLOR_TEXT_SECONDARY)
        py += max(20, len(wrapped_step) * 16 + 4)

    # ==========================================================================
    # SECTION 7: MULTI-SESSION PROGRESS INTELLIGENCE (PHASE 5)
    # ==========================================================================
    sec7_top = 995
    sec7_height = 105
    draw.rounded_rectangle([LEFT, sec7_top, RIGHT, sec7_top + sec7_height], radius=10, fill=COLOR_PANEL, outline=COLOR_BORDER, width=1)
    draw.text((LEFT + 18, sec7_top + 14), "MULTI-SESSION PROGRESS INTELLIGENCE", font=font_section_title, fill=COLOR_ACCENT)

    prog_summary = ProgressIntelligenceTracker.get_instance().get_progress_summary(exercise_name)
    best_rep_val = rep_tracker.get_best_rep()
    best_score_str = f"{best_rep_val['overall_score']}%" if best_rep_val else f"{acc}%"

    p_boxes = [
        ("SESSION FORM TRAJECTORY", f"{prog_summary['trend_icon']} {prog_summary['trend_text']}", COLOR_SUCCESS if prog_summary['delta_accuracy'] >= 0 else COLOR_WARN),
        ("BEST REP QUALITY", best_score_str, COLOR_SUCCESS),
        ("CONSISTENCY SCORE", f"{rep_tracker.get_consistency_score()}%", COLOR_ACCENT),
        ("RECURRING FOCUS", prog_summary["recurring_focus"], COLOR_WARN)
    ]

    p_gap = 16
    p_w = (USABLE_WIDTH - (3 * p_gap) - 36) // 4
    for pi, (plabel, pval, pcol) in enumerate(p_boxes):
        px0 = LEFT + 18 + pi * (p_w + p_gap)
        py0 = sec7_top + 40
        draw.rounded_rectangle([px0, py0, px0 + p_w, py0 + 52], radius=6, fill=COLOR_PANEL_ALT, outline=COLOR_BORDER)
        draw.text((px0 + 10, py0 + 6), plabel, font=font_footer, fill=COLOR_TEXT_MUTED)
        f_val, _ = fit_text_to_width(draw, pval, font_size=11, max_width=p_w - 20, bold=True, min_size=8)
        draw.text((px0 + 10, py0 + 24), pval, font=f_val, fill=pcol)

    # ==========================================================================
    # SECTION 8: ADVANCED MOVEMENT INTELLIGENCE & ADAPTIVE STABILITY (PHASE 6)
    # ==========================================================================
    sec8_top = 1115
    sec8_height = 155
    draw.rounded_rectangle([LEFT, sec8_top, RIGHT, sec8_top + sec8_height], radius=10, fill=COLOR_PANEL, outline=COLOR_BORDER, width=1)
    draw.text((LEFT + 18, sec8_top + 14), "ADVANCED MOVEMENT INTELLIGENCE & ADAPTIVE STABILITY ANALYSIS", font=font_section_title, fill=COLOR_ACCENT)
    draw.text((RIGHT - 370, sec8_top + 16), "AI-generated educational analysis. Not medical diagnosis.", font=font_footer, fill=COLOR_TEXT_MUTED)

    # Compute Phase 6 metrics
    stab_engine = get_movement_stability_engine()
    stability_data = stab_engine.update(exercise_name, stats_snapshot=stats)
    fatigue_data = estimate_form_fatigue(exercise_name, stability_data["stability_score"], stats)
    risk_data = evaluate_movement_risk(exercise_name, stability_data["stability_score"], fatigue_data["fatigue_level"], stats)
    coach_data = get_adaptive_coaching(exercise_name, stability_data["stability_score"], fatigue_data["fatigue_level"], risk_data["risk_level"], stats_snapshot=stats)
    recovery_data = get_recovery_recommendations(fatigue_data["fatigue_level"], stability_data["stability_score"], total_reps=clean_reps)
    trend_data = analyze_performance_trends(exercise_name, stability_data["stability_score"], fatigue_data["fatigue_score"])

    # 4 KPI boxes for Phase 6
    stab_val = stability_data["stability_score"]
    stab_col = COLOR_SUCCESS if stab_val >= 85 else (COLOR_WARN if stab_val >= 60 else COLOR_ALERT)

    fat_lvl = fatigue_data["fatigue_level"]
    fat_col = COLOR_SUCCESS if fat_lvl == "LOW" else (COLOR_WARN if fat_lvl == "MODERATE" else COLOR_ALERT)

    risk_lvl = risk_data["risk_level"]
    risk_col = COLOR_SUCCESS if risk_lvl == "LOW" else (COLOR_WARN if risk_lvl == "MODERATE" else COLOR_ALERT)

    trend_val = trend_data["quality_trend"]
    trend_col = COLOR_SUCCESS if trend_val == "IMPROVING" else (COLOR_ACCENT if trend_val == "STABLE" else COLOR_WARN)

    risk_label_clean = risk_data.get("risk_label", "LOW RISK").replace("_", " ").strip()
    stab_cat = stability_data.get("category", "STABLE").replace("_", " ").strip()
    p6_boxes = [
        ("MOVEMENT STABILITY", f"{stab_val}% • {stab_cat}", stab_col),
        ("AI-ESTIMATED FORM FATIGUE", f"{fat_lvl} ({fatigue_data.get('quality_trend', 'STABLE')})", fat_col),
        ("AI MOVEMENT RISK AWARENESS", risk_label_clean, risk_col),
        ("PERFORMANCE TRAJECTORY", f"{trend_data.get('quality_icon', '➡')} {trend_val}", trend_col)
    ]

    for pi, (plabel, pval, pcol) in enumerate(p6_boxes):
        px0 = LEFT + 18 + pi * (p_w + p_gap)
        py0 = sec8_top + 40
        draw.rounded_rectangle([px0, py0, px0 + p_w, py0 + 48], radius=6, fill=COLOR_PANEL_ALT, outline=COLOR_BORDER)
        draw.text((px0 + 10, py0 + 6), plabel, font=font_footer, fill=COLOR_TEXT_MUTED)
        f_val, _ = fit_text_to_width(draw, pval, font_size=11, max_width=p_w - 20, bold=True, min_size=8)
        draw.text((px0 + 10, py0 + 22), pval, font=f_val, fill=pcol)

    # Narrative row
    weakest_rep_val = rep_tracker.get_weakest_rep()
    best_rep_str = f"Rep #{best_rep_val['rep_number']} ({best_rep_val['overall_score']}%)" if best_rep_val else "Rep #1 (Optimal)"
    weakest_rep_str = f"Rep #{weakest_rep_val['rep_number']} ({weakest_rep_val['overall_score']}%)" if weakest_rep_val else "None (Consistent)"

    narrative_y = sec8_top + 96
    draw.text((LEFT + 18, narrative_y), f"• Best Rep: {best_rep_str}  |  Most Challenging Rep: {weakest_rep_str}", font=font_body_bold, fill=COLOR_TEXT_PRIMARY)
    draw.text((LEFT + 18, narrative_y + 18), f"• Adaptive Coaching: \"{coach_data.get('primary_message', 'Maintain control.')}\" (Mode: {coach_data.get('coaching_mode', 'CALM')})", font=font_body, fill=COLOR_ACCENT)
    draw.text((LEFT + 18, narrative_y + 36), f"• Smart Recovery Protocol: {recovery_data.get('suggested_action', 'Continue training.')}", font=font_body, fill=COLOR_TEXT_SECONDARY)

    # ==========================================================================
    # SECTION 9: TECHNOLOGY & ANALYTICS FOOTER
    # ==========================================================================
    footer_y = 1290
    draw.line([LEFT, footer_y, RIGHT, footer_y], fill=COLOR_DIVIDER, width=1)

    foot_line1 = "Generated by REPRIGHT AI • Real-Time AI Biomechanics & Exercise Form Learning Platform"
    foot_line2 = "Smart India Hackathon Edition • YOLOv8 Pose Estimation • Adaptive Motion Intelligence"
    draw.text((LEFT, footer_y + 10), foot_line1, font=font_footer, fill=COLOR_TEXT_SECONDARY)
    draw.text((LEFT, footer_y + 24), foot_line2, font=font_footer, fill=COLOR_TEXT_MUTED)

    right_line1 = f"Verification Signature: #{abs(hash(str(start_time) + exercise_name)) % 1000000:06d}"
    right_line2 = "Evaluation Record • Confidential Telemetry Summary"
    bbox_r1 = draw.textbbox((0, 0), right_line1, font=font_footer)
    bbox_r2 = draw.textbbox((0, 0), right_line2, font=font_footer)
    draw.text((RIGHT - (bbox_r1[2] - bbox_r1[0]), footer_y + 10), right_line1, font=font_footer, fill=COLOR_TEXT_SECONDARY)
    draw.text((RIGHT - (bbox_r2[2] - bbox_r2[0]), footer_y + 24), right_line2, font=font_footer, fill=COLOR_TEXT_MUTED)

    # --------------------------------------------------------------------------
    # 4. Save and Return Output Path
    # --------------------------------------------------------------------------
    if output_path is None:
        try:
            from services.user_session import UserSession
            user = UserSession.get_instance().get_current_user()
            if user:
                user_dir = os.path.join("reports", f"user_{user.id}")
                os.makedirs(user_dir, exist_ok=True)
                output_path = os.path.join(user_dir, f"report_{exercise_name}_{int(time.time())}.png")
            else:
                output_path = f"report_{exercise_name}_{int(time.time())}.png"
        except Exception:
            output_path = f"report_{exercise_name}_{int(time.time())}.png"
    else:
        # Ensure parent dir exists if output_path includes subdirectories
        out_parent = os.path.dirname(output_path)
        if out_parent:
            os.makedirs(out_parent, exist_ok=True)

    img.save(output_path, format="PNG", optimize=True)
    return output_path

