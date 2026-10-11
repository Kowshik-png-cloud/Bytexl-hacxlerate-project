import csv
import random
from pathlib import Path

# Reproducible sample data
random.seed(42)

# Project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_FILE = DATA_DIR / "students_1000.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# Engineering departments
departments = ["CSE", "IT", "ECE", "EEE", "Mechanical", "Civil"]

# Generate 1,000 synthetic students
students = []

for i in range(1, 1001):

    department = random.choice(departments)
    semester = random.randint(1, 8)

    # Different performance profiles
    profile = random.choices(
        ["high", "average", "low"],
        weights=[30, 45, 25],
        k=1
    )[0]

    if profile == "high":
        cgpa = round(random.uniform(7.5, 10.0), 2)
        attendance = random.randint(85, 100)
        backlogs = random.choices([0, 1], weights=[90, 10])[0]
        internal_marks = random.randint(70, 100)
        assignments = random.randint(80, 100)
        aptitude = random.randint(70, 100)
        coding = random.randint(70, 100)
        interview = random.randint(65, 100)
        technical = random.randint(70, 100)
        communication = random.randint(65, 100)

    elif profile == "average":
        cgpa = round(random.uniform(6.0, 8.0), 2)
        attendance = random.randint(70, 95)
        backlogs = random.choices([0, 1, 2], weights=[45, 40, 15])[0]
        internal_marks = random.randint(45, 80)
        assignments = random.randint(50, 85)
        aptitude = random.randint(45, 80)
        coding = random.randint(40, 80)
        interview = random.randint(40, 80)
        technical = random.randint(45, 85)
        communication = random.randint(45, 85)

    else:
        cgpa = round(random.uniform(4.0, 6.5), 2)
        attendance = random.randint(40, 78)
        backlogs = random.randint(1, 5)
        internal_marks = random.randint(20, 55)
        assignments = random.randint(20, 60)
        aptitude = random.randint(20, 55)
        coding = random.randint(10, 55)
        interview = random.randint(15, 55)
        technical = random.randint(20, 60)
        communication = random.randint(25, 65)

    student = {
        "student_id": f"STU{i:04d}",
        "department": department,
        "semester": semester,
        "cgpa": cgpa,
        "attendance_pct": attendance,
        "backlogs": backlogs,
        "internal_marks": internal_marks,
        "assignment_completion_pct": assignments,
        "lms_logins_week": random.randint(0, 10),
        "events_participated": random.randint(0, 5),
        "certifications": random.randint(0, 5),
        "aptitude_score": aptitude,
        "coding_score": coding,
        "mock_interview_score": interview,
        "technical_skill_score": technical,
        "communication_score": communication,
    }

    students.append(student)

# Write the CSV
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=students[0].keys()
    )
    writer.writeheader()
    writer.writerows(students)

print("SUCCESS: Synthetic student dataset created!")
print(f"Total students: {len(students)}")
print(f"Departments: {len(departments)}")
print(f"Output file: {OUTPUT_FILE}")
print("Original sample_students.csv was not changed.")