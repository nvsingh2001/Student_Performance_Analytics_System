def print_student_table(items, title="Student Performance Records"):
    """
    Helper function to print a formatted table of student records.
    """
    print(f"\n--- {title} ---")
    print(
        f"{'Student ID':<15} | {'Study Hours':<12} | {'Attendance %':<12} | {'Participation':<13} | {'Total Score':<11} | {'Grade':<5} | {'Category':<15}"
    )
    print("-" * 100)
    for item in items:
        sid = item.get("student_id", "N/A")
        hours = str(item.get("weekly_self_study_hours", "N/A"))
        attnd = str(item.get("attendance_percentage", "N/A"))
        part = str(item.get("class_participation", "N/A"))
        score = str(item.get("total_score", "N/A"))
        grade = item.get("grade", "N/A")
        cat = item.get("performance_category", "N/A")
        print(
            f"{sid:<15} | {hours:<12} | {attnd:<12} | {part:<13} | {score:<11} | {grade:<5} | {cat:<15}"
        )
    print("-" * 100)
