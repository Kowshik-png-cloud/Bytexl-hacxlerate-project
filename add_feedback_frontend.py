from pathlib import Path
import ast

app = Path("frontend/src/App.jsx")
source = app.read_text()

if '"Feedback", MessageCircle' in source:
    print("Feedback navigation already exists.")
    raise SystemExit(0)

# Add Feedback to the existing sidebar navigation.
old_nav = '''    ["Placement Readiness", BriefcaseBusiness], ["Insights", Activity]
  ];'''

new_nav = '''    ["Placement Readiness", BriefcaseBusiness], ["Insights", Activity],
    ["Feedback", MessageCircle]
  ];'''

if old_nav not in source:
    raise SystemExit("Could not find the expected navigation block. No changes made.")

source = source.replace(old_nav, new_nav, 1)

# Add the page heading.
old_heading = '''    Insights:["Performance insights","Compare departments and semester-level patterns."]
  }[page]'''

new_heading = '''    Insights:["Performance insights","Compare departments and semester-level patterns."],
    Feedback:["Student satisfaction and faculty feedback","Collect feedback and review satisfaction ratings."]
  }[page]'''

if old_heading not in source:
    raise SystemExit("Could not find the expected page heading block. No changes made.")

source = source.replace(old_heading, new_heading, 1)

# Add a dedicated Feedback component before the main App component.
marker = "export default function App()"
component = r'''
function FeedbackPage({ students }) {
  const [role, setRole] = useState("Student");
  const [studentId, setStudentId] = useState("");
  const [category, setCategory] = useState("Student Satisfaction");
  const [rating, setRating] = useState(5);
  const [comments, setComments] = useState("");
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);

  const categories = [
    "Student Satisfaction",
    "Teaching Quality",
    "Learning Resources",
    "Course Curriculum",
    "Faculty Feedback",
    "Student Performance",
    "Attendance and Participation",
    "Suggestions"
  ];

  async function loadSummary() {
    try {
      const response = await fetch("http://127.0.0.1:5001/api/engagement-feedback/summary");
      if (!response.ok) throw new Error("Could not load feedback summary.");
      setSummary(await response.json());
    } catch (error) {
      setMessage(error.message);
    }
  }

  async function loadHistory(id) {
    if (!id.trim()) {
      setHistory([]);
      return;
    }
    try {
      const response = await fetch(
        `http://127.0.0.1:5001/api/engagement-feedback/${encodeURIComponent(id.trim())}`
      );
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "Could not load history.");
      setHistory(payload.feedback || []);
    } catch (error) {
      setMessage(error.message);
    }
  }

  useEffect(() => {
    loadSummary();
  }, []);

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      const response = await fetch("http://127.0.0.1:5001/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: studentId,
          submitter_role: role,
          category,
          rating,
          comments
        })
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "Feedback submission failed.");
      setMessage("Feedback submitted successfully.");
      setComments("");
      await loadSummary();
      await loadHistory(studentId);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  const panel = {
    background: COLORS.white,
    border: `1px solid ${COLORS.border}`,
    borderRadius: 16,
    padding: 22,
    boxShadow: "0 5px 18px rgba(23,43,77,0.04)"
  };
  const field = {
    width: "100%",
    padding: "11px 12px",
    borderRadius: 9,
    border: `1px solid ${COLORS.border}`,
    font: "inherit",
    boxSizing: "border-box",
    background: COLORS.white,
    color: COLORS.ink
  };
  const label = { display: "grid", gap: 7, fontSize: 13, fontWeight: 700, color: COLORS.ink };

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 14 }}>
        {[
          ["Total feedback", summary?.total_feedback ?? "—"],
          ["Average satisfaction", summary?.total_feedback ? `${summary.average_rating}/5` : "—"],
          ["Student responses", summary?.student_feedback ?? "—"],
          ["Faculty responses", summary?.faculty_feedback ?? "—"]
        ].map(([title, value]) => (
          <div key={title} style={panel}>
            <div style={{ color: COLORS.muted, fontSize: 12, marginBottom: 10 }}>{title}</div>
            <div style={{ fontSize: 28, fontWeight: 800, color: COLORS.ink }}>{value}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(290px,1fr))", gap: 20, alignItems: "start" }}>
        <section style={panel}>
          <h2 style={{ margin: "0 0 7px", fontSize: 19 }}>Submit feedback</h2>
          <p style={{ color: COLORS.muted, fontSize: 13, marginTop: 0 }}>
            Share a satisfaction rating or feedback about a student's learning.
          </p>
          <form onSubmit={submit} style={{ display: "grid", gap: 16 }}>
            <label style={label}>
              Feedback submitted by
              <select style={field} value={role} onChange={e => setRole(e.target.value)}>
                <option value="Student">Student</option>
                <option value="Faculty">Faculty</option>
              </select>
            </label>
            <label style={label}>
              Student ID
              <input
                style={field}
                value={studentId}
                onChange={e => setStudentId(e.target.value.toUpperCase())}
                placeholder="e.g. STU0001"
                required
              />
            </label>
            <label style={label}>
              Feedback category
              <select style={field} value={category} onChange={e => setCategory(e.target.value)}>
                {categories.map(item => <option key={item} value={item}>{item}</option>)}
              </select>
            </label>
            <div style={label}>
              Rating
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                {[1, 2, 3, 4, 5].map(value => (
                  <button
                    key={value}
                    type="button"
                    aria-label={`Rate ${value} out of 5`}
                    onClick={() => setRating(value)}
                    style={{
                      border: `1px solid ${rating >= value ? "#d98735" : COLORS.border}`,
                      background: rating >= value ? "#fff3e5" : COLORS.white,
                      borderRadius: 9,
                      padding: "9px 12px",
                      cursor: "pointer",
                      color: rating >= value ? "#d98735" : COLORS.muted,
                      fontSize: 19
                    }}
                  >★</button>
                ))}
                <span style={{ color: COLORS.muted, fontSize: 13 }}>{rating}/5</span>
              </div>
            </div>
            <label style={label}>
              Comments or suggestions
              <textarea
                style={{ ...field, minHeight: 110, resize: "vertical" }}
                value={comments}
                onChange={e => setComments(e.target.value)}
                maxLength={2000}
                placeholder="Share feedback or suggestions..."
              />
            </label>
            <button type="submit" disabled={saving} style={{ ...ui.button, justifyContent: "center", background: COLORS.teal, color: "#fff", opacity: saving ? 0.7 : 1 }}>
              {saving ? "Submitting..." : "Submit feedback"}
            </button>
          </form>
          {message && <p role="status" style={{ fontSize: 13, color: message.toLowerCase().includes("success") ? COLORS.teal : COLORS.red }}>{message}</p>}
        </section>

        <div style={{ display: "grid", gap: 20 }}>
          <section style={panel}>
            <h2 style={{ margin: "0 0 14px", fontSize: 19 }}>Department-wise feedback</h2>
            {!summary?.by_department?.length ? (
              <p style={{ color: COLORS.muted, fontSize: 13 }}>No feedback has been submitted yet.</p>
            ) : summary.by_department.map(item => (
              <div key={item.department} style={{ padding: "12px 0", borderBottom: `1px solid ${COLORS.border}` }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10, fontSize: 13 }}>
                  <b>{item.department || "Unspecified"}</b>
                  <span>{item.average_rating ?? 0}/5 · {item.responses} responses</span>
                </div>
              </div>
            ))}
          </section>

          <section style={panel}>
            <h2 style={{ margin: "0 0 7px", fontSize: 19 }}>Student feedback history</h2>
            <p style={{ color: COLORS.muted, fontSize: 13 }}>Enter a student ID to review submitted feedback.</p>
            <div style={{ display: "flex", gap: 8 }}>
              <input style={field} value={studentId} onChange={e => setStudentId(e.target.value.toUpperCase())} placeholder="Student ID" />
              <button type="button" style={ui.button} onClick={() => loadHistory(studentId)}>Search</button>
            </div>
            <div style={{ display: "grid", gap: 10, marginTop: 14 }}>
              {history.map(item => (
                <article key={item.id} style={{ padding: 12, borderRadius: 10, background: COLORS.bg }}>
                  <div style={{ display: "flex", justifyContent: "space-between", gap: 8, fontSize: 12 }}>
                    <b>{item.category}</b><b>{item.rating}/5 ★</b>
                  </div>
                  <div style={{ color: COLORS.muted, fontSize: 12, marginTop: 5 }}>{item.submitter_role} · {new Date(item.created_at).toLocaleString()}</div>
                  {item.comments && <p style={{ fontSize: 13, marginBottom: 0, whiteSpace: "pre-wrap" }}>{item.comments}</p>}
                </article>
              ))}
              {history.length === 0 && <p style={{ color: COLORS.muted, fontSize: 13 }}>No feedback loaded for this student.</p>}
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

'''

if marker not in source:
    raise SystemExit("Could not find App component. No changes made.")

source = source.replace(marker, component + marker, 1)

# Add Feedback page rendering immediately before Insights rendering.
insights_marker = '      {page==="Insights"'
if insights_marker not in source:
    raise SystemExit("Could not find Insights page rendering. No changes made.")

source = source.replace(
    insights_marker,
    '      {page==="Feedback" && <FeedbackPage students={data} />}\n' + insights_marker,
    1
)

app.write_text(source)
print("Feedback page added to frontend.")
