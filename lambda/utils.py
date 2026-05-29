REQUIRED_FIELDS = [
    "student_id",
    "weekly_self_study_hours",
    "attendance_percentage",
    "class_participation",
    "total_score",
    "grade",
]


def calculate_performance_category(total_score):
    if total_score >= 90:
        return "Excellent"
    elif total_score >= 75:
        return "Good"
    elif total_score >= 60:
        return "Average"
    else:
        return "Poor"


def validate_record(record):
    missing = [f for f in REQUIRED_FIELDS if f not in record]
    if missing:
        raise ValueError(f"Missing fields: {missing}")
    return True


def is_at_risk(attendance_percentage, total_score):
    return attendance_percentage < 60 or total_score < 50
