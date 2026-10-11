from pathlib import Path

path = Path("chatbot_api.py")
code = path.read_text()

route = '@app.get("/api/engagement-feedback/all")'

if route in code:
    print("Endpoint already exists in chatbot_api.py.")
    raise SystemExit(0)

marker = '@app.get("/api/engagement-feedback/<student_id>")'

if code.count(marker) != 1:
    raise SystemExit(
        "Could not safely find the feedback history route. No changes made."
    )

endpoint = '''
@app.get("/api/engagement-feedback/all")
def all_feedback():
    """Return recent feedback records for the analytics dashboard."""
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

        records = [dict(row) for row in rows]
        return jsonify({"feedback": records, "count": len(records)})
    except Exception:
        app.logger.exception("Could not load detailed feedback")
        return jsonify({"error": "Could not load feedback records."}), 500


'''

code = code.replace(marker, endpoint + marker, 1)
path.write_text(code)
print("Feedback analytics endpoint added successfully.")
