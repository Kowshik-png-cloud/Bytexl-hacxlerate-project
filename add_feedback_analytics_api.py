from pathlib import Path

path = Path("chatbot_api.py")
code = path.read_text()

if '@app.get("/api/engagement-feedback/all")' in code:
    raise SystemExit("Detailed feedback endpoint already exists.")

marker = '@app.get("/api/engagement-feedback/<student_id>")'

if code.count(marker) != 1:
    raise SystemExit("Could not safely locate the feedback-history endpoint.")

endpoint = r'''
@app.get("/api/engagement-feedback/all")
def all_feedback():
    """Return feedback records for the Feedback Analytics dashboard."""
    try:
        with sqlite3.connect(FEEDBACK_DB) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute("""
                SELECT id, student_id, department, submitter_role,
                       category, rating, comments, created_at
                FROM feedback
                ORDER BY created_at DESC
                LIMIT 5000
            """).fetchall()

        return jsonify({
            "feedback": [dict(row) for row in rows],
            "count": len(rows),
        })
    except Exception:
        app.logger.exception("Could not load detailed feedback")
        return jsonify({"error": "Could not load feedback records."}), 500


'''

code = code.replace(marker, endpoint + marker, 1)
path.write_text(code)
print("Detailed feedback API added successfully.")
