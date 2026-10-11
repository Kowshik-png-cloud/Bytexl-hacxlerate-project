from pathlib import Path
import sys
import pandas as pd

# --------------------------------------------------
# PROJECT PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

DATA_FILE = BASE_DIR / "data" / "students_1000.csv"
OUTPUT_FILE = BASE_DIR / "data" / "student_analytics_1000.csv"

# --------------------------------------------------
# IMPORT PROJECT MODULES
# --------------------------------------------------

from src.success_score import calculate_success_scores
from src.risk_analysis import (
    analyze_academic_risk,
    analyze_placement_risk,
)
from src.student_segmentation import segment_students


# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------

def print_section(title):
    print("\n" + "=" * 65)
    print(title)
    print("=" * 65)


def check_required_columns(df, columns):
    missing = [column for column in columns if column not in df.columns]

    if missing:
        print(f"Missing columns: {missing}")
        return False

    return True


# --------------------------------------------------
# STEP 1: LOAD DATASET
# --------------------------------------------------

def load_dataset():
    print_section("STEP 1: LOADING STUDENT DATA")

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}\n"
            "Run generate_students.py first."
        )

    df = pd.read_csv(DATA_FILE)

    print(f"Dataset loaded successfully.")
    print(f"Total student records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    if df.empty:
        raise ValueError("The dataset is empty.")

    if "student_id" not in df.columns:
        raise ValueError("The dataset must contain a student_id column.")

    return df


# --------------------------------------------------
# STEP 2: VALIDATE DATASET
# --------------------------------------------------

def validate_dataset(df):
    print_section("STEP 2: DATASET VALIDATION")

    required_columns = [
        "student_id",
        "department",
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
    ]

    if not check_required_columns(df, required_columns):
        raise ValueError(
            "The dataset is missing required columns. "
            "Check generate_students.py."
        )

    duplicate_count = df["student_id"].duplicated().sum()
    missing_count = df.isnull().sum().sum()

    print(f"Expected records: 1000")
    print(f"Actual records: {len(df)}")
    print(f"Duplicate student IDs: {duplicate_count}")
    print(f"Missing data cells: {missing_count}")

    print("\nDepartment distribution:")
    print(df["department"].value_counts().to_string())

    if duplicate_count > 0:
        print("\nWarning: Duplicate student IDs were found.")

    print("\nDataset validation completed.")


# --------------------------------------------------
# STEP 3: CALCULATE STUDENT SUCCESS SCORES
# --------------------------------------------------

def calculate_scores(df):
    print_section("STEP 3: CALCULATING STUDENT SUCCESS SCORES")

    result = calculate_success_scores(df.copy())

    if not isinstance(result, pd.DataFrame):
        raise TypeError(
            "calculate_success_scores() must return a pandas DataFrame."
        )

    if len(result) != len(df):
        raise ValueError(
            "The scoring function changed the number of student records."
        )

    if "student_success_score" not in result.columns:
        raise KeyError(
            "student_success_score was not created by "
            "calculate_success_scores(). Check src/success_score.py."
        )

    # Preserve the original student records and calculated scores.
    # This also protects against a scoring function that accidentally
    # returns a DataFrame without the original columns.
    for column in df.columns:
        if column not in result.columns:
            result[column] = df[column].values

    result["student_success_score"] = pd.to_numeric(
        result["student_success_score"],
        errors="coerce",
    )

    valid_scores = result["student_success_score"].dropna()

    print(f"Records processed: {len(result)}")
    print(f"Valid success scores: {len(valid_scores)}")

    if not valid_scores.empty:
        print(f"Average success score: {valid_scores.mean():.2f}")
        print(f"Minimum success score: {valid_scores.min():.2f}")
        print(f"Maximum success score: {valid_scores.max():.2f}")

    print("\nSuccess score calculation completed.")

    return result


# --------------------------------------------------
# STEP 4: ANALYZE ACADEMIC RISK
# --------------------------------------------------

def calculate_academic_risk(df):
    print_section("STEP 4: ACADEMIC RISK ANALYSIS")

    original_scores = df["student_success_score"].copy()

    result = analyze_academic_risk(df.copy())

    if not isinstance(result, pd.DataFrame):
        raise TypeError(
            "analyze_academic_risk() must return a pandas DataFrame."
        )

    if len(result) != len(df):
        raise ValueError(
            "Academic risk analysis changed the number of records."
        )

    # Keep the calculated score if a risk function accidentally removes it.
    if "student_success_score" not in result.columns:
        result["student_success_score"] = original_scores.values

    if "academic_risk" not in result.columns:
        raise KeyError(
            "academic_risk was not created. Check src/risk_analysis.py."
        )

    print("Academic risk distribution:")
    print(result["academic_risk"].value_counts(dropna=False).to_string())

    print("\nAcademic risk analysis completed.")

    return result


# --------------------------------------------------
# STEP 5: ANALYZE PLACEMENT RISK
# --------------------------------------------------

def calculate_placement_risk(df):
    print_section("STEP 5: PLACEMENT RISK ANALYSIS")

    original_scores = df["student_success_score"].copy()

    result = analyze_placement_risk(df.copy())

    if not isinstance(result, pd.DataFrame):
        raise TypeError(
            "analyze_placement_risk() must return a pandas DataFrame."
        )

    if len(result) != len(df):
        raise ValueError(
            "Placement risk analysis changed the number of records."
        )

    # Preserve scores if the placement function accidentally removes them.
    if "student_success_score" not in result.columns:
        result["student_success_score"] = original_scores.values

    if "placement_risk" not in result.columns:
        raise KeyError(
            "placement_risk was not created. Check src/risk_analysis.py."
        )

    print("Placement risk distribution:")
    print(result["placement_risk"].value_counts(dropna=False).to_string())

    print("\nPlacement risk analysis completed.")

    return result


# --------------------------------------------------
# STEP 6: SEGMENT STUDENTS
# --------------------------------------------------

def categorize_students(df):
    print_section("STEP 6: STUDENT SEGMENTATION")

    if "student_success_score" not in df.columns:
        raise KeyError(
            "student_success_score is missing before segmentation."
        )

    result = segment_students(df.copy())

    if not isinstance(result, pd.DataFrame):
        raise TypeError(
            "segment_students() must return a pandas DataFrame."
        )

    if len(result) != len(df):
        raise ValueError(
            "Student segmentation changed the number of records."
        )

    if "student_category" not in result.columns:
        raise KeyError(
            "student_category was not created. "
            "Check src/student_segmentation.py."
        )

    print("Student category distribution:")
    print(result["student_category"].value_counts(dropna=False).to_string())

    print("\nStudent segmentation completed.")

    return result


# --------------------------------------------------
# STEP 7: GENERATE FINAL REPORT
# --------------------------------------------------

def generate_report(df):
    print_section("STEP 7: FINAL STUDENT ANALYTICS REPORT")

    report_columns = [
        "student_id",
        "department",
        "semester",
        "cgpa",
        "attendance_pct",
        "student_success_score",
        "academic_risk",
        "placement_risk",
        "student_category",
    ]

    available_columns = [
        column for column in report_columns if column in df.columns
    ]

    print(f"Total students analyzed: {len(df)}")

    print("\nAverage success score by department:")

    if "department" in df.columns:
        print(
            df.groupby("department")["student_success_score"]
            .mean()
            .round(2)
            .sort_values(ascending=False)
            .to_string()
        )

    print("\nAcademic risk by department:")

    if {"department", "academic_risk"}.issubset(df.columns):
        print(
            pd.crosstab(
                df["department"],
                df["academic_risk"],
            ).to_string()
        )

    print("\nPlacement risk by department:")

    if {"department", "placement_risk"}.issubset(df.columns):
        print(
            pd.crosstab(
                df["department"],
                df["placement_risk"],
            ).to_string()
        )

    print("\nFirst 10 student records:")
    print(
        df[available_columns]
        .head(10)
        .to_string(index=False)
    )

    print(
        "\nNote: The terminal displays only a sample of the records. "
        "The complete dataset will be saved to CSV."
    )


# --------------------------------------------------
# STEP 8: SAVE ALL STUDENT RECORDS
# --------------------------------------------------

def save_results(df):
    print_section("STEP 8: SAVING COMPLETE ANALYTICS DATASET")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    # Verify that the saved file contains all processed records.
    saved_df = pd.read_csv(OUTPUT_FILE)

    if len(saved_df) != len(df):
        raise ValueError(
            f"Export verification failed: expected {len(df)} records, "
            f"but saved {len(saved_df)}."
        )

    print("Analytics dataset saved successfully.")
    print(f"Total student records saved: {len(saved_df)}")
    print(f"Total columns saved: {len(saved_df.columns)}")
    print(f"File location: {OUTPUT_FILE}")


# --------------------------------------------------
# MAIN PROGRAM
# --------------------------------------------------

def main():
    try:
        # Load and validate the original dataset.
        df = load_dataset()
        validate_dataset(df)

        # Calculate scores and analyze risk.
        df = calculate_scores(df)
        df = calculate_academic_risk(df)
        df = calculate_placement_risk(df)
        df = categorize_students(df)

        # Generate a summary and export every student.
        generate_report(df)
        save_results(df)

        print_section("SUCCESS")
        print("All student analytics steps completed successfully.")
        print("All processed student records are available in the CSV file.")

    except Exception as error:
        print_section("ERROR")
        print(f"{type(error).__name__}: {error}")
        print("\nCheck the error message and the relevant module.")
        raise


if __name__ == "__main__":
    main()