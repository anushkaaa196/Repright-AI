"""REPRIGHT AI - Verification Script for Report Text Rendering & Label Clipping Fix.

Tests:
1. Label formatting & normalization (no technical underscores, correct tiers).
2. Multi-line wrapping for compact rep performance cards.
3. Font width fitting (fit_text_to_width) ensuring zero overflow.
4. End-to-end report generation with 5 diverse reps covering all quality tiers:
   - EXCELLENT (>= 90%)
   - GOOD (75-89%)
   - NEEDS IMPROVEMENT (50-74%)
   - FORM CORRECTION REQUIRED (< 50%)
5. Verifies report image dimensions (1200x1400) and file creation.
"""

import os
import sys
import time

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PIL import Image, ImageDraw
from backend.reporter import (
    format_quality_label,
    wrap_rep_status_lines,
    fit_text_to_width,
    draw_right_aligned_text,
    generate_report_image,
    _get_font
)
from core.rep_history import RepHistoryTracker


def test_label_formatting():
    print("--- 1. Testing Label Formatting & Humanization ---")
    
    # Test direct status inputs
    assert format_quality_label("EXCELLENT") == "EXCELLENT"
    assert format_quality_label("GOOD") == "GOOD"
    assert format_quality_label("NEEDS_IMPROVEMENT") == "NEEDS IMPROVEMENT"
    assert format_quality_label("FORM_CORRECTION") == "FORM CORRECTION REQUIRED"
    assert format_quality_label("FORM_CORRECTION_REQUIRED") == "FORM CORRECTION REQUIRED"
    assert format_quality_label("FAILED_DEPTH") == "NEEDS IMPROVEMENT"
    assert format_quality_label("FAILED_SITTING") == "FORM CORRECTION REQUIRED"
    
    # Test score-based inference when status is empty
    assert format_quality_label("", score=95) == "EXCELLENT"
    assert format_quality_label("", score=82) == "GOOD"
    assert format_quality_label("", score=64) == "NEEDS IMPROVEMENT"
    assert format_quality_label("", score=42) == "FORM CORRECTION REQUIRED"
    
    print("✓ format_quality_label passed all test cases!")


def test_label_wrapping():
    print("\n--- 2. Testing Multi-Line Label Wrapping ---")
    
    w_exc = wrap_rep_status_lines("EXCELLENT")
    assert w_exc == ["EXCELLENT"], f"Unexpected: {w_exc}"
    
    w_good = wrap_rep_status_lines("GOOD")
    assert w_good == ["GOOD"], f"Unexpected: {w_good}"
    
    w_needs = wrap_rep_status_lines("NEEDS_IMPROVEMENT")
    assert w_needs == ["NEEDS", "IMPROVEMENT"], f"Unexpected: {w_needs}"
    
    w_corr = wrap_rep_status_lines("FORM_CORRECTION")
    assert w_corr == ["FORM CORRECTION", "REQUIRED"], f"Unexpected: {w_corr}"
    
    w_corr2 = wrap_rep_status_lines("FORM_CORRECTION_REQUIRED")
    assert w_corr2 == ["FORM CORRECTION", "REQUIRED"], f"Unexpected: {w_corr2}"
    
    print("✓ wrap_rep_status_lines passed all test cases!")


def test_font_fitting_and_bounds():
    print("\n--- 3. Testing Text Fitting & Right Alignment ---")
    
    img = Image.new("RGB", (300, 100), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Test fit_text_to_width
    font, text = fit_text_to_width(draw, "FORM CORRECTION", font_size=8, max_width=80, bold=True, min_size=6)
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    assert w <= 80, f"Expected width <= 80, got {w}"
    print(f"✓ 'FORM CORRECTION' fitted inside 80px: rendered width = {w}px (font size: {font.size if hasattr(font, 'size') else 'default'})")
    
    font2, text2 = fit_text_to_width(draw, "IMPROVEMENT", font_size=8, max_width=80, bold=True, min_size=6)
    bbox2 = draw.textbbox((0, 0), text2, font=font2)
    w2 = bbox2[2] - bbox2[0]
    assert w2 <= 80, f"Expected width <= 80, got {w2}"
    print(f"✓ 'IMPROVEMENT' fitted inside 80px: rendered width = {w2}px")
    
    # Test right aligned text
    rendered_w = draw_right_aligned_text(draw, right_x=280, y=10, text="100%", font=_get_font(10, bold=True), fill=(255, 255, 255))
    assert rendered_w > 0
    print(f"✓ Right-aligned text rendered cleanly (width = {rendered_w}px)")


def test_end_to_end_report_generation():
    print("\n--- 4. Testing End-to-End Report Generation with All Rep Quality Tiers ---")
    
    rep_tracker = RepHistoryTracker.get_instance()
    rep_tracker.reset()
    
    # Rep 1: Flawless (95%, EXCELLENT)
    rep_tracker.add_rep({
        "rep_number": 1,
        "exercise": "SQUAT",
        "is_clean": True,
        "rep_result": "CLEAN",
        "overall_score": 95,
        "status": "EXCELLENT",
        "dimension_scores": {
            "range_of_motion": 96, "alignment": 95, "stability": 94, "movement_control": 95, "consistency": 95
        }
    })
    
    # Rep 2: Minor posture adjustment (82%, GOOD)
    rep_tracker.add_rep({
        "rep_number": 2,
        "exercise": "SQUAT",
        "is_clean": True,
        "rep_result": "CLEAN",
        "overall_score": 82,
        "status": "GOOD",
        "dimension_scores": {
            "range_of_motion": 90, "alignment": 78, "stability": 75, "movement_control": 85, "consistency": 82
        }
    })
    
    # Rep 3: Shallow depth (64%, NEEDS_IMPROVEMENT)
    rep_tracker.add_rep({
        "rep_number": 3,
        "exercise": "SQUAT",
        "is_clean": False,
        "rep_result": "FAILED_DEPTH",
        "overall_score": 64,
        "status": "NEEDS_IMPROVEMENT",
        "dimension_scores": {
            "range_of_motion": 52, "alignment": 78, "stability": 75, "movement_control": 70, "consistency": 65
        }
    })
    
    # Rep 4: Passive chair pause (48%, FORM_CORRECTION)
    rep_tracker.add_rep({
        "rep_number": 4,
        "exercise": "SQUAT",
        "is_clean": False,
        "rep_result": "FAILED_SITTING",
        "overall_score": 48,
        "status": "FORM_CORRECTION",
        "dimension_scores": {
            "range_of_motion": 85, "alignment": 50, "stability": 40, "movement_control": 45, "consistency": 50
        }
    })
    
    # Rep 5: Recovered form (92%, EXCELLENT)
    rep_tracker.add_rep({
        "rep_number": 5,
        "exercise": "SQUAT",
        "is_clean": True,
        "rep_result": "CLEAN",
        "overall_score": 92,
        "status": "EXCELLENT",
        "dimension_scores": {
            "range_of_motion": 94, "alignment": 92, "stability": 90, "movement_control": 92, "consistency": 92
        }
    })
    
    stats = {
        "clean_reps": 3,
        "failed_depth": 1,
        "failed_sitting": 1,
        "posture_warnings": 1,
        "accuracy": 76,
        "start_time": time.time() - 95
    }
    
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scratch"))
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "report_test_text_rendering.png")
    
    saved_path = generate_report_image("SQUAT", stats, output_path=out_file)
    assert os.path.exists(saved_path), "Report PNG was not created!"
    
    file_size = os.path.getsize(saved_path)
    assert file_size > 50000, f"Report file size {file_size} is suspiciously small!"
    
    im = Image.open(saved_path)
    w, h = im.size
    assert w == 1200, f"Expected width 1200, got {w}"
    assert h == 1400, f"Expected height 1400, got {h}"
    
    print(f"✓ Generated high-resolution diagnostic report successfully!")
    print(f"  Path: {saved_path}")
    print(f"  Dimensions: {w}x{h} px")
    print(f"  File size: {file_size:,} bytes")


if __name__ == "__main__":
    print("==========================================================")
    print("REPRIGHT AI - REPORT TEXT RENDERING & LABEL VERIFICATION")
    print("==========================================================")
    test_label_formatting()
    test_label_wrapping()
    test_font_fitting_and_bounds()
    test_end_to_end_report_generation()
    print("\n==========================================================")
    print("ALL TEXT RENDERING & LABEL FIX TESTS PASSED SUCCESSFULLY!")
    print("==========================================================")
