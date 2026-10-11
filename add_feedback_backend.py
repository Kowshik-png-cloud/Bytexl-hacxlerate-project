from pathlib import Path
import ast
import shutil

project = Path(__file__).resolve().parent
backend = project / "chatbot_api.py"
backup = project / "chatbot_api.py.feedback-backup"

source = backend.read_text()

if '@app.post("/api/feedback")' in source:
    print("Feedback API already exists. No changes made.")
    raise SystemExit(0)

if not backup.exists():
    shutil.copy2(backend, backup)

routes = r'''

# ---------------- Feedback module ----------------

import sqlite3
from datetime import datetime, timezone

FEEDBACK_DB = os.path.join(BASE_DIR, "data", "engagement_feedback.db")
FEEDBACK_CATEGORIES = {
    "Student Satisfaction",
    "Teaching Quality",
    "Learning Resources",
    "Course Curriculum",
    "Faculty Feedback",
    "Student Performance",
    "Attendance and Participation",
    "Suggestions",
}


def init_feedback_db():
    os.makedirs(os.path.dirname(FEEDBACK_DB), exist_ok=True)
    with sqlite3.connect(FEEDBACK_DB) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                department TEXT NOT NULL DEFAULT '',
                submitter_role TEXT NOT NULL,
                category TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
                comments TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_student
            ON feedback(student_id)
        """)


init_feedback_db()


@app.post("/api/feedback")
def submit_feedback():
    body = request.get_json(silent=True) or {}

    student_id = str(body.get("student_id", "")).strip().upper()
    role = str(body.get("submitter_role", "")).strip().title()
    category = str(body.get("category", "")).strip()
    comments = str(body.get("comments", "")).strip()

    try:
        rating = int(body.get("rating", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Rating must be an integer from 1 to 5."}), 400

    if not student_id:
        return jsonify({"error": "Student ID is required."}), 400
    if role not in {"Student", "Faculty"}:
        return jsonify({"error": "Submitter role must be Student or Faculty."}), 400
    if category not in FEEDBACK_CATEGORIES:
        return jsonify({"error": "Please select a valid feedback category."}), 400
    if not 1 <= rating <= 5:
        return jsonify({"error": "Rating must be between 1 and 5."}), 400
    if len(comments) > 2000:
        return jsonify({"error": "Comments must be 2000 characters or fewer."}), 400

    try:
        students = load_students()
        student = next(
            (row for row in students
             if str(row.get("student_id", "")).strip().upper() == student_id),
            None
        )
        if student is None:
            return jsonify({"error": "Student ID was not found in the dataset."}), 404

        department = str(student.get("department", ""))
        created_at = datetime.now(timezone.utc).isoformat()

        with sqlite3.connect(FEEDBACK_DB) as connection:
            cursor = connection.execute("""
                INSERT INTO feedback
                (student_id, department, submitter_role, category, rating, comments, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                student_id, department, role, category, rating, comments, created_at
            ))
            feedback_id = cursor.lastrowid

        return jsonify({
            "message": "Feedback submitted successfully.",
            "feedback_id": feedback_id,
            "student_id": student_id,
        }), 201

    except Exception:
        app.logger.exception("Could not save feedback")
        return jsonify({"error": "Could not save feedback."}), 500


@app.get("/api/engagement-feedback/summary")
def feedback_summary():
    try:
        with sqlite3.connect(FEEDBACK_DB) as connection:
            connection.row_factory = sqlite3.Row

            totals = connection.execute("""
                SELECT COUNT(*) AS total,
                       ROUND(AVG(rating), 2) AS average_rating,
                       SUM(CASE WHEN submitter_role = 'Student' THEN 1 ELSE 0 END) AS student_feedback,
                       SUM(CASE WHEN submitter_role = 'Faculty' THEN 1 ELSE 0 END) AS faculty_feedback
                FROM feedback
            """).fetchone()

            categories = connection.execute("""
                SELECT category, COUNT(*) AS responses,
                       ROUND(AVG(rating), 2) AS average_rating
                FROM feedback
                GROUP BY category
                ORDER BY responses DESC, category
            """).fetchall()

            departments = connection.execute("""
                SELECT department, COUNT(*) AS responses,
                       ROUND(AVG(rating), 2) AS average_rating
                FROM feedback
                GROUP BY department
                ORDER BY responses DESC, department
            """).fetchall()

        return jsonify({
            "total_feedback": totals["total"] or 0,
            "average_rating": totals["average_rating"] or 0,
            "student_feedback": totals["student_feedback"] or 0,
            "faculty_feedback": totals["faculty_feedback"] or 0,
            "by_category": [dict(row) for row in categories],
            "by_department": [dict(row) for row in departments],
        })
    except Exception:
        app.logger.exception("Could not summarize feedback")
        return jsonify({"error": "Could not load feedback summary."}), 500


@app.get("/api/engagement-feedback/<student_id>")
def student_feedback_history(student_id):
    student_id = str(student_id).strip().upper()

    try:
        with sqlite3.connect(FEEDBACK_DB) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute("""
                SELECT id, student_id, department, submitter_role,
                       category, rating, comments, created_at
                FROM feedback
                WHERE student_id = ?
                ORDER BY created_at DESC
                LIMIT 100
            """, (student_id,)).fetchall()

        return jsonify({
            "student_id": student_id,
            "feedback": [dict(row) for row in rows],
        })
    except Exception:
        app.logger.exception("Could not load student feedback")
        return jsonify({"error": "Could not load student feedback."}), 500

'''

updated = source.rstrip() + "\n\n" + routes + "\n"

# Validate syntax before writing anything.
ast.parse(updated)
backend.write_text(updated)

print("Feedback backend added successfully.")
print(f"Database will be created at: {project / 'data' / 'engagement_feedback.db'}")
print("Existing backend backup remains available.")
