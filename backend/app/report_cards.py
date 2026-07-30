"""Report Card Grading and GPA Engine.

Provides configurable grading rules, GPA calculation, and report generation
logic that can be customized per school (multi-tenant).
"""
import math
import json
from typing import List, Dict, Optional, Tuple


# ========== DEFAULT GRADING RULES ==========

DEFAULT_GRADING_RULES = [
    {"min": 91, "max": 100, "grade": "A+", "grade_point": 10.0, "description": "Outstanding"},
    {"min": 81, "max": 90, "grade": "A", "grade_point": 9.0, "description": "Excellent"},
    {"min": 71, "max": 80, "grade": "B+", "grade_point": 8.0, "description": "Very Good"},
    {"min": 61, "max": 70, "grade": "B", "grade_point": 7.0, "description": "Good"},
    {"min": 51, "max": 60, "grade": "C+", "grade_point": 6.0, "description": "Above Average"},
    {"min": 41, "max": 50, "grade": "C", "grade_point": 5.0, "description": "Average"},
    {"min": 33, "max": 40, "grade": "D", "grade_point": 4.0, "description": "Below Average"},
    {"min": 0, "max": 32, "grade": "F", "grade_point": 0.0, "description": "Fail"},
]

DEFAULT_4_POINT_SCALE = [
    {"min": 90, "max": 100, "grade": "A", "grade_point": 4.0},
    {"min": 80, "max": 89, "grade": "B", "grade_point": 3.0},
    {"min": 70, "max": 79, "grade": "C", "grade_point": 2.0},
    {"min": 60, "max": 69, "grade": "D", "grade_point": 1.0},
    {"min": 0, "max": 59, "grade": "F", "grade_point": 0.0},
]

DEFAULT_5_POINT_SCALE = [
    {"min": 90, "max": 100, "grade": "A", "grade_point": 5.0},
    {"min": 80, "max": 89, "grade": "B", "grade_point": 4.0},
    {"min": 70, "max": 79, "grade": "C", "grade_point": 3.0},
    {"min": 60, "max": 69, "grade": "D", "grade_point": 2.0},
    {"min": 0, "max": 59, "grade": "F", "grade_point": 0.0},
]

GRADING_SCALES = {
    "10_point": DEFAULT_GRADING_RULES,
    "4_point": DEFAULT_4_POINT_SCALE,
    "5_point": DEFAULT_5_POINT_SCALE,
}


def get_grade_and_point(percentage: float, grading_rules: List[Dict]) -> Tuple[str, float]:
    """Determine grade and grade point based on percentage and grading rules."""
    if not grading_rules:
        grading_rules = DEFAULT_GRADING_RULES
    
    for rule in grading_rules:
        if rule["min"] <= percentage <= rule["max"]:
            return rule["grade"], rule["grade_point"]
    
    return "F", 0.0


def calculate_gpa(subject_grades: List[Dict], grading_scale: str = "10_point", custom_rules: Optional[List[Dict]] = None) -> float:
    """Calculate GPA from subject grades.
    
    Args:
        subject_grades: List of dicts with 'grade_point' and 'max_marks' keys
        grading_scale: One of '10_point', '4_point', '5_point', or 'custom'
        custom_rules: Custom grading rules (required if grading_scale is 'custom')
    
    Returns:
        GPA value
    """
    if not subject_grades:
        return 0.0
    
    # Get max possible GPA based on scale
    rules = custom_rules if grading_scale == "custom" else GRADING_SCALES.get(grading_scale, DEFAULT_GRADING_RULES)
    max_gp = max(r["grade_point"] for r in rules) if rules else 10.0
    
    # Calculate weighted average of grade points
    total_weight = 0
    total_gp_weighted = 0
    
    for sg in subject_grades:
        gp = sg.get("grade_point", 0)
        max_marks = sg.get("max_marks", 100)
        total_gp_weighted += gp * max_marks
        total_weight += max_marks
    
    if total_weight == 0:
        return 0.0
    
    weighted_gpa = total_gp_weighted / total_weight
    
    # Normalize to the scale (e.g., 10-point scale max is 10)
    return round(weighted_gpa, 2)


def calculate_overall_grade(gpa: float, grading_scale: str = "10_point", custom_rules: Optional[List[Dict]] = None) -> str:
    """Determine overall grade from GPA."""
    rules = custom_rules if grading_scale == "custom" else GRADING_SCALES.get(grading_scale, DEFAULT_GRADING_RULES)
    
    if not rules:
        return "N/A"
    
    max_gp = max(r["grade_point"] for r in rules)
    
    # Convert GPA back to percentage-like scale for grade mapping
    percentage = (gpa / max_gp) * 100
    
    for rule in rules:
        if rule["min"] <= percentage <= rule["max"]:
            return rule["grade"]
    
    return "F"


def determine_result_status(subject_grades: List[Dict], pass_percentage: float = 33.0) -> str:
    """Determine if student PASSED or FAILED.
    
    Args:
        subject_grades: List of dicts with 'percentage' key
        pass_percentage: Minimum percentage required to pass
    
    Returns:
        'PASS', 'FAIL', 'PROMOTED', or 'DETENTION'
    """
    if not subject_grades:
        return "FAIL"
    
    failed_subjects = sum(1 for sg in subject_grades if sg.get("percentage", 0) < pass_percentage)
    total_subjects = len(subject_grades)
    
    if failed_subjects == 0:
        # Check overall percentage for promotion
        overall_pct = sum(sg.get("percentage", 0) for sg in subject_grades) / total_subjects
        if overall_pct >= 60:
            return "PROMOTED"
        return "PASS"
    elif failed_subjects <= total_subjects * 0.3:  # Less than 30% subjects failed
        return "DETENTION"
    else:
        return "FAIL"


def generate_verification_id() -> str:
    """Generate a unique, non-sequential verification ID for QR code."""
    import uuid
    import hashlib
    import time
    
    unique_str = f"{uuid.uuid4()}-{time.time_ns()}"
    hash_obj = hashlib.sha256(unique_str.encode())
    # Take first 16 chars of hex digest for a reasonably short unique ID
    return hash_obj.hexdigest()[:16]


def calculate_attendance_percentage(present_days: int, working_days: int) -> float:
    """Calculate attendance percentage."""
    if working_days == 0:
        return 0.0
    return round((present_days / working_days) * 100, 2)


def get_default_grade_rules_json() -> str:
    """Return default grading rules as JSON string for storage."""
    return json.dumps(DEFAULT_GRADING_RULES)


def get_grade_point_for_percentage(percentage: float, rules_json: Optional[str] = None) -> Tuple[str, float]:
    """Get grade and grade point from percentage using stored JSON rules."""
    if rules_json:
        try:
            rules = json.loads(rules_json)
        except (json.JSONDecodeError, TypeError):
            rules = DEFAULT_GRADING_RULES
    else:
        rules = DEFAULT_GRADING_RULES
    
    return get_grade_and_point(percentage, rules)