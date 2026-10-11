import pandas as pd


def analyze_academic_risk(df):
    """
    Identify academic risk while preserving all existing columns.
    """

    result = df.copy()

    required_columns = [
        "attendance_pct",
        "cgpa",
        "backlogs",
        "internal_marks",
    ]

    for column in required_columns:
        if column not in result.columns:
            result["academic_risk"] = "Insufficient Data"
            result["academic_risk_reasons"] = [
                "Missing required academic data."
            ] * len(result)
            return result

    risk_levels = []
    risk_reasons = []

    for _, student in result.iterrows():

        reasons = []
        valid_indicators = 0

        attendance = pd.to_numeric(
            pd.Series([student["attendance_pct"]]),
            errors="coerce",
        ).iloc[0]

        cgpa = pd.to_numeric(
            pd.Series([student["cgpa"]]),
            errors="coerce",
        ).iloc[0]

        backlogs = pd.to_numeric(
            pd.Series([student["backlogs"]]),
            errors="coerce",
        ).iloc[0]

        internal_marks = pd.to_numeric(
            pd.Series([student["internal_marks"]]),
            errors="coerce",
        ).iloc[0]

        if pd.notna(attendance):
            valid_indicators += 1

            if attendance < 75:
                reasons.append("Attendance below 75%")

        if pd.notna(cgpa):
            valid_indicators += 1

            if cgpa < 6:
                reasons.append("CGPA below 6.0")

        if pd.notna(backlogs):
            valid_indicators += 1

            if backlogs >= 2:
                reasons.append("Two or more backlogs")

        if pd.notna(internal_marks):
            valid_indicators += 1

            if internal_marks < 40:
                reasons.append("Internal marks below 40")

        if valid_indicators < 2:
            risk = "Insufficient Data"

        elif len(reasons) >= 3:
            risk = "High"

        elif len(reasons) >= 1:
            risk = "Moderate"

        else:
            risk = "Low"

        risk_levels.append(risk)

        if reasons:
            risk_reasons.append(reasons)
        elif risk == "Insufficient Data":
            risk_reasons.append(
                ["Insufficient academic information."]
            )
        else:
            risk_reasons.append(
                ["No major academic warning indicators."]
            )

    result["academic_risk"] = risk_levels
    result["academic_risk_reasons"] = risk_reasons

    return result


def analyze_placement_risk(df):
    """
    Identify placement risk while preserving all existing columns.
    """

    result = df.copy()

    required_columns = [
        "aptitude_score",
        "coding_score",
        "mock_interview_score",
        "technical_skill_score",
        "communication_score",
    ]

    for column in required_columns:
        if column not in result.columns:
            result["placement_risk"] = "Insufficient Data"
            result["placement_risk_reasons"] = [
                "Missing required placement data."
            ] * len(result)
            return result

    risk_levels = []
    risk_reasons = []

    for _, student in result.iterrows():

        reasons = []
        valid_indicators = 0

        indicators = {
            "aptitude_score": "Low aptitude score",
            "coding_score": "Low coding score",
            "mock_interview_score": "Low mock interview score",
            "technical_skill_score": "Low technical skill score",
            "communication_score": "Low communication score",
        }

        for column, description in indicators.items():

            value = pd.to_numeric(
                pd.Series([student[column]]),
                errors="coerce",
            ).iloc[0]

            if pd.notna(value):
                valid_indicators += 1

                if value < 50:
                    reasons.append(description)

        if valid_indicators < 3:
            risk = "Insufficient Data"

        elif len(reasons) >= 3:
            risk = "High"

        elif len(reasons) >= 1:
            risk = "Moderate"

        else:
            risk = "Low"

        risk_levels.append(risk)

        if reasons:
            risk_reasons.append(reasons)
        elif risk == "Insufficient Data":
            risk_reasons.append(
                ["Insufficient placement information."]
            )
        else:
            risk_reasons.append(
                ["No major placement warning indicators."]
            )

    result["placement_risk"] = risk_levels
    result["placement_risk_reasons"] = risk_reasons

    return result