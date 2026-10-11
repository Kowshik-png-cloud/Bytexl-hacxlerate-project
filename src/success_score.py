import pandas as pd
import numpy as np


WEIGHTS = {
    "academic": 0.25,
    "attendance": 0.20,
    "placement": 0.20,
    "assignment": 0.10,
    "lms": 0.10,
    "skills": 0.10,
    "engagement": 0.05,
}


def get_number(row, column):
    if column not in row.index:
        return np.nan

    try:
        value = float(row[column])
    except (TypeError, ValueError):
        return np.nan

    if not np.isfinite(value):
        return np.nan

    return value


def bounded_score(value):
    if pd.isna(value) or not 0 <= value <= 100:
        return np.nan

    return float(value)


def weighted_average(values, weights):
    available = [
        (values[key], weight)
        for key, weight in weights.items()
        if pd.notna(values.get(key, np.nan))
    ]

    if not available:
        return np.nan, 0.0

    total_weight = sum(weight for _, weight in available)

    score = sum(
        value * weight for value, weight in available
    ) / total_weight

    coverage = total_weight / sum(weights.values())

    return score, coverage


def calculate_student_score(row):

    # -----------------------------------------------------
    # 1. ACADEMIC PERFORMANCE
    # -----------------------------------------------------

    cgpa = get_number(row, "cgpa")

    cgpa_score = (
        cgpa * 10
        if pd.notna(cgpa) and 0 <= cgpa <= 10
        else np.nan
    )

    internal = bounded_score(
        get_number(row, "internal_marks")
    )

    backlogs = get_number(row, "backlogs")

    if (
        pd.notna(backlogs)
        and backlogs >= 0
        and backlogs.is_integer()
    ):
        backlog_score = max(0, 100 - 25 * backlogs)
    else:
        backlog_score = np.nan

    academic, academic_coverage = weighted_average(
        {
            "cgpa": cgpa_score,
            "internal": internal,
            "backlogs": backlog_score,
        },
        {
            "cgpa": 0.40,
            "internal": 0.35,
            "backlogs": 0.25,
        },
    )

    # -----------------------------------------------------
    # 2. ATTENDANCE
    # -----------------------------------------------------

    attendance = bounded_score(
        get_number(row, "attendance_pct")
    )

    # -----------------------------------------------------
    # 3. ASSIGNMENT COMPLETION
    # -----------------------------------------------------

    assignment = bounded_score(
        get_number(row, "assignment_completion_pct")
    )

    # -----------------------------------------------------
    # 4. LMS ACTIVITY
    # -----------------------------------------------------

    logins = get_number(row, "lms_logins_week")

    lms = (
        min(logins / 10, 1) * 100
        if pd.notna(logins) and logins >= 0
        else np.nan
    )

    # -----------------------------------------------------
    # 5. PLACEMENT READINESS
    # -----------------------------------------------------

    placement_values = {
        "aptitude": bounded_score(
            get_number(row, "aptitude_score")
        ),
        "coding": bounded_score(
            get_number(row, "coding_score")
        ),
        "interview": bounded_score(
            get_number(row, "mock_interview_score")
        ),
    }

    placement, placement_coverage = weighted_average(
        placement_values,
        {
            "aptitude": 1 / 3,
            "coding": 1 / 3,
            "interview": 1 / 3,
        },
    )

    # -----------------------------------------------------
    # 6. TECHNICAL AND COMMUNICATION SKILLS
    # -----------------------------------------------------

    skills, skills_coverage = weighted_average(
        {
            "technical": bounded_score(
                get_number(row, "technical_skill_score")
            ),
            "communication": bounded_score(
                get_number(row, "communication_score")
            ),
        },
        {
            "technical": 0.60,
            "communication": 0.40,
        },
    )

    # -----------------------------------------------------
    # 7. ENGAGEMENT
    # -----------------------------------------------------

    events = get_number(row, "events_participated")
    certifications = get_number(row, "certifications")

    event_score = (
        min(events / 5, 1) * 100
        if pd.notna(events) and events >= 0
        else np.nan
    )

    certification_score = (
        min(certifications / 5, 1) * 100
        if pd.notna(certifications) and certifications >= 0
        else np.nan
    )

    engagement, engagement_coverage = weighted_average(
        {
            "events": event_score,
            "certifications": certification_score,
        },
        {
            "events": 0.50,
            "certifications": 0.50,
        },
    )

    # -----------------------------------------------------
    # COMBINE COMPONENTS
    # -----------------------------------------------------

    components = {
        "academic": (academic, academic_coverage),
        "attendance": (
            attendance,
            1.0 if pd.notna(attendance) else 0.0,
        ),
        "placement": (placement, placement_coverage),
        "assignment": (
            assignment,
            1.0 if pd.notna(assignment) else 0.0,
        ),
        "lms": (
            lms,
            1.0 if pd.notna(lms) else 0.0,
        ),
        "skills": (skills, skills_coverage),
        "engagement": (engagement, engagement_coverage),
    }

    total = 0.0
    available_weight = 0.0

    for category, weight in WEIGHTS.items():
        score, coverage = components[category]

        if pd.notna(score) and coverage > 0:
            effective_weight = weight * coverage
            total += score * effective_weight
            available_weight += effective_weight

    final_score = (
        total / available_weight
        if available_weight > 0
        else np.nan
    )

    # -----------------------------------------------------
    # RETURN EXPLAINABLE RESULTS
    # -----------------------------------------------------

    return pd.Series({
        "student_success_score": (
            round(final_score, 2)
            if pd.notna(final_score)
            else np.nan
        ),

        "score_coverage_pct": round(
            available_weight * 100, 2
        ),

        "academic_component": (
            round(academic, 2)
            if pd.notna(academic)
            else np.nan
        ),

        "attendance_component": (
            round(attendance, 2)
            if pd.notna(attendance)
            else np.nan
        ),

        "placement_component": (
            round(placement, 2)
            if pd.notna(placement)
            else np.nan
        ),

        "assignment_component": (
            round(assignment, 2)
            if pd.notna(assignment)
            else np.nan
        ),

        "lms_component": (
            round(lms, 2)
            if pd.notna(lms)
            else np.nan
        ),

        "skills_component": (
            round(skills, 2)
            if pd.notna(skills)
            else np.nan
        ),

        "engagement_component": (
            round(engagement, 2)
            if pd.notna(engagement)
            else np.nan
        ),
    })


def calculate_success_scores(df):

    result = df.copy()

    output_columns = [
        "student_success_score",
        "score_coverage_pct",
        "academic_component",
        "attendance_component",
        "placement_component",
        "assignment_component",
        "lms_component",
        "skills_component",
        "engagement_component",
    ]

    if result.empty:
        for column in output_columns:
            result[column] = pd.Series(dtype=float)

        return result

    calculated = result.apply(
        calculate_student_score,
        axis=1,
    )

    for column in calculated.columns:
        result[column] = calculated[column]

    return result