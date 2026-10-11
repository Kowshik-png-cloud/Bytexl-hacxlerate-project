import re
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "student_analytics_1000.csv"

df = pd.read_csv(CSV_PATH)

# Clean column names and prepare common fields.
df.columns = df.columns.str.strip().str.lower()

NUMERIC_COLUMNS = [
    "semester",
    "cgpa",
    "attendance_pct",
    "backlogs",
    "internal_marks",
    "assignment_completion_pct",
    "lms_logins_week",
    "events_participated",
    "certifications",
    "aptitude_score",
    "coding_score",
    "mock_interview_score",
    "technical_skill_score",
    "communication_score",
    "student_success_score",
]

for column in NUMERIC_COLUMNS:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")


# --------------------------------------------------
# QUESTION NORMALIZATION
# --------------------------------------------------

def normalize(text):
    text = text.lower().strip()

    replacements = {
        "second year": "secondyear",
        "2nd year": "secondyear",
        "first year": "firstyear",
        "1st year": "firstyear",
        "third year": "thirdyear",
        "3rd year": "thirdyear",
        "fourth year": "fourthyear",
        "4th year": "fourthyear",
        "attendance percentage": "attendance",
        "success score": "student_success_score",
        "student success score": "student_success_score",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return re.sub(r"\s+", " ", text)


# --------------------------------------------------
# YEAR AND DEPARTMENT FILTERS
# --------------------------------------------------

def filter_year(data, question):
    """
    Assumes a four-year BTech course:
    Year 1 = semesters 1-2
    Year 2 = semesters 3-4
    Year 3 = semesters 5-6
    Year 4 = semesters 7-8
    """

    q = normalize(question)

    year_semesters = {
        "firstyear": [1, 2],
        "secondyear": [3, 4],
        "thirdyear": [5, 6],
        "fourthyear": [7, 8],
    }

    for year, semesters in year_semesters.items():
        if year in q:
            return data[data["semester"].isin(semesters)]

    match = re.search(r"\bsemester\s*(\d+)\b", q)

    if match:
        semester = int(match.group(1))
        return data[data["semester"] == semester]

    return data


def filter_department(data, question):
    q = normalize(question)

    for department in data["department"].dropna().unique():
        if department.lower() in q:
            return data[data["department"].str.lower() == department.lower()]

    return data


# --------------------------------------------------
# DISPLAY HELPERS
# --------------------------------------------------

def format_table(data, columns):
    if data.empty:
        return "No students matched your question."

    available = [c for c in columns if c in data.columns]

    return data[available].to_string(
        index=False,
        max_rows=20,
    )


def top_students(data, metric, limit=10):
    if metric not in data.columns:
        return f"The dataset does not contain the metric '{metric}'."

    result = data.dropna(subset=[metric]).sort_values(
        metric,
        ascending=False,
    ).head(limit)

    columns = [
        "student_id",
        "department",
        "semester",
        "cgpa",
        "attendance_pct",
        "student_success_score",
    ]

    return format_table(result, columns)


# --------------------------------------------------
# MAIN QUESTION ANSWERING ENGINE
# --------------------------------------------------

def answer_question(question):
    q = normalize(question)

    if not q:
        return "Please enter a question about student performance."

    data = filter_year(df, q)
    data = filter_department(data, q)

    if data.empty:
        return "No student records matched those filters."

    # Number of student records
    if any(term in q for term in [
        "how many students",
        "number of students",
        "count students",
        "total students",
    ]):
        return f"Found {len(data)} student records matching your question."

    # Department comparison
    if (
        "department" in q
        and any(term in q for term in [
            "highest cgpa",
            "best cgpa",
            "average cgpa",
            "compare",
        ])
    ):
        stats = (
            data.groupby("department")["cgpa"]
            .mean()
            .sort_values(ascending=False)
            .round(2)
        )

        return "Average CGPA by department:\n\n" + stats.to_string()

    # Top scorers by CGPA
    if any(term in q for term in [
        "top scorer",
        "top student",
        "highest cgpa",
        "best student",
        "rank students",
        "highest scoring",
    ]):
        match = re.search(r"\btop\s+(\d+)\b", q)
        limit = min(int(match.group(1)), 100) if match else 10

        return (
            f"Top {limit} students ranked by CGPA:\n\n"
            + top_students(data, "cgpa", limit)
        )

    # Top students by success score
    if any(term in q for term in [
        "success score ranking",
        "highest success score",
        "top success score",
    ]):
        match = re.search(r"\btop\s+(\d+)\b", q)
        limit = min(int(match.group(1)), 100) if match else 10

        return (
            f"Top students ranked by success score:\n\n"
            + top_students(data, "student_success_score", limit)
        )

    # Low attendance
    if any(term in q for term in [
        "low attendance",
        "below 75",
        "attendance below",
        "attendance less than",
    ]):
        match = re.search(r"(\d+(?:\.\d+)?)\s*%", q)
        threshold = float(match.group(1)) if match else 75.0

        result = data[data["attendance_pct"] < threshold]

        return (
            f"Students with attendance below {threshold}%:\n\n"
            + format_table(
                result.sort_values("attendance_pct"),
                [
                    "student_id",
                    "department",
                    "semester",
                    "attendance_pct",
                    "cgpa",
                    "academic_risk",
                ],
            )
        )

    # Backlogs
    if "backlog" in q:
        match = re.search(r"(?:more than|greater than|above|over)\s+(\d+)", q)
        threshold = int(match.group(1)) if match else 0

        result = data[data["backlogs"] > threshold]

        return (
            f"Students with more than {threshold} backlogs:\n\n"
            + format_table(
                result.sort_values("backlogs", ascending=False),
                [
                    "student_id",
                    "department",
                    "semester",
                    "backlogs",
                    "cgpa",
                    "academic_risk",
                ],
            )
        )

    # Academic risk
    if "academic risk" in q or "at risk" in q:
        risk_level = "High" if "high" in q else None

        if risk_level:
            result = data[data["academic_risk"] == risk_level]
        else:
            result = data[data["academic_risk"] != "Low"]

        return (
            f"Matching academic-risk students: {len(result)}\n\n"
            + format_table(
                result,
                [
                    "student_id",
                    "department",
                    "semester",
                    "cgpa",
                    "attendance_pct",
                    "academic_risk",
                ],
            )
        )

    # General statistics
    if any(term in q for term in [
        "average cgpa",
        "average attendance",
        "average success score",
        "statistics",
        "summarize",
        "summary",
    ]):
        return (
            f"Student statistics for {len(data)} records:\n\n"
            f"Average CGPA: {data['cgpa'].mean():.2f}\n"
            f"Average attendance: {data['attendance_pct'].mean():.2f}%\n"
            f"Average success score: "
            f"{data['student_success_score'].mean():.2f}\n"
            f"Students with backlogs: "
            f"{int((data['backlogs'] > 0).sum())}"
        )

    # Individual student search
    student_match = re.search(r"\bstu\d+\b", q)

    if student_match:
        student_id = student_match.group(0).upper()
        student = df[df["student_id"].str.upper() == student_id]

        if student.empty:
            return f"I couldn't find student {student_id}."

        return (
            f"Student profile for {student_id}:\n\n"
            + format_table(
                student,
                [
                    "student_id",
                    "department",
                    "semester",
                    "cgpa",
                    "attendance_pct",
                    "backlogs",
                    "student_success_score",
                    "academic_risk",
                    "placement_risk",
                ],
            )
        )

    # Help message
    return (
        "I can answer questions about your student dataset.\n\n"
        "Try asking:\n"
        "• Give me the top 10 scorers from 2nd year.\n"
        "• Which students have attendance below 75%?\n"
        "• Show students with more than 2 backlogs.\n"
        "• Which department has the highest average CGPA?\n"
        "• Show students with high academic risk.\n"
        "• Analyse student STU0001.\n"
        "• Give me a summary of student statistics."
    )


# --------------------------------------------------
# TERMINAL CHAT FOR TESTING
# --------------------------------------------------

if __name__ == "__main__":
    print("EduPulse AI — Free Student Analytics Chatbot")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() in {"exit", "quit"}:
            break

        print("\nEduPulse AI:")
        print(answer_question(question))
        print()