import pandas as pd


def generate_recommendations(student):
    """
    Generate explainable recommendations from a student's performance data.
    """

    recommendations = []

    cgpa = student.get("cgpa")
    attendance = student.get("attendance_pct")
    coding = student.get("coding_score")
    aptitude = student.get("aptitude_score")
    communication = student.get("communication_score")
    assignments = student.get("assignment_completion_pct")
    technical = student.get("technical_skill_score")
    backlogs = student.get("backlogs")

    # Academic recommendations
    if pd.notna(cgpa) and cgpa < 6.0:
        recommendations.append(
            "Academic improvement: Create a weekly subject revision plan "
            "and practise previous examination questions."
        )

    if pd.notna(backlogs) and backlogs > 0:
        recommendations.append(
            f"Backlog support: Prioritise clearing the {int(backlogs)} "
            "pending backlog(s) with a subject-wise study schedule."
        )

    if pd.notna(attendance) and attendance < 75:
        recommendations.append(
            "Attendance improvement: Attend upcoming classes regularly "
            "and discuss attendance concerns with a faculty mentor."
        )

    # Assignment recommendations
    if pd.notna(assignments) and assignments < 75:
        recommendations.append(
            "Assignment support: Complete pending assignments and set "
            "weekly submission reminders."
        )

    # Placement recommendations
    if pd.notna(coding) and coding < 50:
        recommendations.append(
            "Coding practice: Start with basic programming problems, "
            "then progress to arrays, strings, and problem-solving exercises."
        )

    if pd.notna(aptitude) and aptitude < 50:
        recommendations.append(
            "Aptitude preparation: Practise quantitative aptitude, "
            "logical reasoning, and timed mock tests."
        )

    if pd.notna(communication) and communication < 50:
        recommendations.append(
            "Communication development: Practise spoken explanations, "
            "group discussions, and mock interviews."
        )

    if pd.notna(technical) and technical < 50:
        recommendations.append(
            "Technical skill development: Review core technical concepts "
            "and complete small practical projects."
        )

    if not recommendations:
        recommendations.append(
            "Continue the current learning routine and complete regular "
            "practice tests to maintain progress."
        )

    return recommendations