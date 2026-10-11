from pathlib import Path

path = Path("frontend/src/App.jsx")
code = path.read_text()

start_marker = "function FeedbackPage({ students }) {"
end_marker = "\nexport default function App() {"

if start_marker not in code or end_marker not in code:
    raise SystemExit("Could not locate FeedbackPage safely. No changes made.")

start = code.index(start_marker)
end = code.index(end_marker, start)

if "Feedback Analytics Dashboard" in code[start:end]:
    raise SystemExit("Feedback analytics upgrade already exists. No changes made.")

replacement = r'''
function FeedbackPage({ students }) {
  const [role, setRole] = useState("Student");
  const [studentId, setStudentId] = useState("");
  const [category, setCategory] = useState("Student Satisfaction");
  const [rating, setRating] = useState(5);
  const [comments, setComments] = useState("");
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [allFeedback, setAllFeedback] = useState([]);
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [analyticsLoading, setAnalyticsLoading] = useState(true);
  const [filterCategory, setFilterCategory] = useState("All");
  const [filterRole, setFilterRole] = useState("All");
  const [filterDepartment, setFilterDepartment] = useState("All");
  const [filterRating, setFilterRating] = useState("All");
  const [feedbackSearch, setFeedbackSearch] = useState("");

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

  const panel = {
    background: COLORS.white,
    border: `1px solid ${COLORS.border}`,
    borderRadius: 16,
    padding: 22,
    boxShadow: "0 5px 18px rgba(23,43,77,0.04)",
    minWidth: 0
  };

  const field = {
    width: "100%",
    padding: "11px 12px",
    borderRadius: 9,
    border: `1px solid ${COLORS.border}`,
    font: "inherit",
    boxSizing: "border-box",
    background: COLORS.white,
    color: COLORS.ink,
    minWidth: 0
  };

  const label = {
    display: "grid",
    gap: 7,
    fontSize: 13,
    fontWeight: 700,
    color: COLORS.ink
  };

  async function loadSummary() {
    const response = await fetch(
      "http://127.0.0.1:5001/api/engagement-feedback/summary"
    );
    if (!response.ok) throw new Error("Could not load feedback summary.");
    setSummary(await response.json());
  }

  async function loadAllFeedback() {
    setAnalyticsLoading(true);
    try {
      const response = await fetch(
        "http://127.0.0.1:5001/api/engagement-feedback/all"
      );
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "Could not load feedback analytics.");
      }
      setAllFeedback(Array.isArray(payload.feedback) ? payload.feedback : []);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setAnalyticsLoading(false);
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

  async function refreshAnalytics() {
    try {
      await Promise.all([loadSummary(), loadAllFeedback()]);
    } catch (error) {
      setMessage(error.message);
    }
  }

  useEffect(() => {
    refreshAnalytics();
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
      await refreshAnalytics();
      await loadHistory(studentId);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setSaving(false);
    }
  }

  const departments = [...new Set(allFeedback.map(item => item.department).filter(Boolean))].sort();
  const filteredFeedback = allFeedback.filter(item => {
    const matchesCategory = filterCategory === "All" || item.category === filterCategory;
    const matchesRole = filterRole === "All" || item.submitter_role === filterRole;
    const matchesDepartment = filterDepartment === "All" || item.department === filterDepartment;
    const matchesRating = filterRating === "All" || String(item.rating) === filterRating;
    const searchable = `${item.student_id || ""} ${item.department || ""} ${item.category || ""} ${item.comments || ""} ${item.submitter_role || ""}`.toLowerCase();
    return matchesCategory && matchesRole && matchesDepartment && matchesRating &&
      searchable.includes(feedbackSearch.toLowerCase().trim());
  });

  const ratingDistribution = [1, 2, 3, 4, 5].map(star => ({
    rating: `${star} star${star === 1 ? "" : "s"}`,
    responses: filteredFeedback.filter(item => Number(item.rating) === star).length
  }));

  const categoryRatings = categories.map(name => {
    const entries = filteredFeedback.filter(item => item.category === name);
    return {
      category: name.length > 19 ? `${name.slice(0, 17)}…` : name,
      fullCategory: name,
      average: entries.length
        ? Number((entries.reduce((sum, item) => sum + Number(item.rating || 0), 0) / entries.length).toFixed(2))
        : 0,
      responses: entries.length
    };
  });

  const roleComparison = ["Student", "Faculty"].map(name => {
    const entries = filteredFeedback.filter(item => item.submitter_role === name);
    return {
      role: name,
      responses: entries.length,
      average: entries.length
        ? Number((entries.reduce((sum, item) => sum + Number(item.rating || 0), 0) / entries.length).toFixed(2))
        : 0
    };
  });

  const trendMap = {};
  filteredFeedback.forEach(item => {
    const day = String(item.created_at || "").slice(0, 10);
    if (!day) return;
    trendMap[day] = (trendMap[day] || 0) + 1;
  });
  const trendData = Object.entries(trendMap)
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-30)
    .map(([date, submissions]) => ({ date: date.slice(5), submissions }));

  const filteredAverage = filteredFeedback.length
    ? (filteredFeedback.reduce((sum, item) => sum + Number(item.rating || 0), 0) / filteredFeedback.length).toFixed(2)
    : "—";

  function exportCSV() {
    const columns = ["student_id", "department", "submitter_role", "category", "rating", "comments", "created_at"];
    const escapeCSV = value => `"${String(value ?? "").replace(/"/g, '""')}"`;
    const rows = [
      columns.join(","),
      ...filteredFeedback.map(item => columns.map(column => escapeCSV(item[column])).join(","))
    ];
    const blob = new Blob(["\uFEFF" + rows.join("\r\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "edupulse_feedback_analytics.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  const chartTooltip = {
    background: COLORS.white,
    border: `1px solid ${COLORS.border}`,
    borderRadius: 8
  };

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <section style={{ ...panel, background: "linear-gradient(120deg,#123b52,#167d83)", color: "#fff" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 14, flexWrap: "wrap" }}>
          <div>
            <div style={{ fontSize: 12, letterSpacing: 1.5, opacity: 0.8, fontWeight: 800 }}>EDUPULSE AI · CATEGORY 7</div>
            <h1 style={{ margin: "8px 0", fontSize: 27 }}>Feedback Analytics Dashboard</h1>
            <p style={{ margin: 0, opacity: 0.85, fontSize: 13 }}>Understand satisfaction, compare feedback, and track trends.</p>
          </div>
          <button type="button" onClick={refreshAnalytics} style={{ ...ui.button, background: "#fff", color: "#123b52" }}>
            ↻ Refresh analytics
          </button>
        </div>
      </section>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(170px,1fr))", gap: 14 }}>
        {[
          ["Total feedback", summary?.total_feedback ?? "—"],
          ["Overall average", summary?.total_feedback ? `${summary.average_rating}/5` : "—"],
          ["Student responses", summary?.student_feedback ?? "—"],
          ["Faculty responses", summary?.faculty_feedback ?? "—"],
          ["Filtered responses", filteredFeedback.length],
          ["Filtered average", filteredAverage === "—" ? "—" : `${filteredAverage}/5`]
        ].map(([title, value]) => (
          <div key={title} style={panel}>
            <div style={{ color: COLORS.muted, fontSize: 12, marginBottom: 10 }}>{title}</div>
            <div style={{ fontSize: 27, fontWeight: 800, color: COLORS.ink }}>{value}</div>
          </div>
        ))}
      </div>

      <section style={panel}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <div>
            <h2 style={{ margin: "0 0 6px", fontSize: 19 }}>Explore feedback</h2>
            <p style={{ margin: 0, color: COLORS.muted, fontSize: 13 }}>Filters apply to the charts, summary, and records below.</p>
          </div>
          <button type="button" onClick={exportCSV} disabled={!filteredFeedback.length} style={{ ...ui.button, opacity: filteredFeedback.length ? 1 : 0.5 }}>
            ↓ Export CSV ({filteredFeedback.length})
          </button>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(175px,1fr))", gap: 12, marginTop: 18 }}>
          <label style={label}>Search
            <input style={field} value={feedbackSearch} onChange={e => setFeedbackSearch(e.target.value)} placeholder="Student ID or comment" />
          </label>
          <label style={label}>Department
            <select style={field} value={filterDepartment} onChange={e => setFilterDepartment(e.target.value)}>
              <option value="All">All departments</option>
              {departments.map(item => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label style={label}>Category
            <select style={field} value={filterCategory} onChange={e => setFilterCategory(e.target.value)}>
              <option value="All">All categories</option>
              {categories.map(item => <option key={item} value={item}>{item}</option>)}
            </select>
          </label>
          <label style={label}>Submitted by
            <select style={field} value={filterRole} onChange={e => setFilterRole(e.target.value)}>
              <option value="All">All roles</option>
              <option value="Student">Student</option>
              <option value="Faculty">Faculty</option>
            </select>
          </label>
          <label style={label}>Rating
            <select style={field} value={filterRating} onChange={e => setFilterRating(e.target.value)}>
              <option value="All">All ratings</option>
              {[5, 4, 3, 2, 1].map(value => <option key={value} value={value}>{value} star{value === 1 ? "" : "s"}</option>)}
            </select>
          </label>
          <div style={{ display: "flex", alignItems: "end" }}>
            <button type="button" style={{ ...ui.button, width: "100%", justifyContent: "center" }} onClick={() => {
              setFilterCategory("All");
              setFilterRole("All");
              setFilterDepartment("All");
              setFilterRating("All");
              setFeedbackSearch("");
            }}>Clear filters</button>
          </div>
        </div>
        {analyticsLoading && <p style={{ color: COLORS.muted, fontSize: 13 }}>Loading feedback analytics…</p>}
      </section>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(300px,1fr))", gap: 20 }}>
        <section style={panel}>
          <h2 style={{ margin: "0 0 5px", fontSize: 18 }}>Rating distribution</h2>
          <p style={{ margin: "0 0 14px", color: COLORS.muted, fontSize: 12 }}>Number of responses for each star rating.</p>
          <div style={{ width: "100%", height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ratingDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="rating" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip contentStyle={chartTooltip} />
                <Bar dataKey="responses" name="Responses" fill={COLORS.teal} radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section style={panel}>
          <h2 style={{ margin: "0 0 5px", fontSize: 18 }}>Student vs Faculty</h2>
          <p style={{ margin: "0 0 14px", color: COLORS.muted, fontSize: 12 }}>Submission volume and average rating.</p>
          <div style={{ width: "100%", height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={roleComparison}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="role" />
                <YAxis allowDecimals={false} />
                <Tooltip contentStyle={chartTooltip} />
                <Bar dataKey="responses" name="Responses" fill="#6b8afd" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          {roleComparison.map(item => (
            <div key={item.role} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: `1px solid ${COLORS.border}`, fontSize: 13 }}>
              <span>{item.role} average rating</span><b>{item.responses ? `${item.average}/5` : "—"}</b>
            </div>
          ))}
        </section>
      </div>

      <section style={panel}>
        <h2 style={{ margin: "0 0 5px", fontSize: 18 }}>Category-wise satisfaction</h2>
        <p style={{ margin: "0 0 14px", color: COLORS.muted, fontSize: 12 }}>Average rating out of 5. Categories with no matching feedback show zero.</p>
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={categoryRatings} margin={{ bottom: 25, left: 0, right: 10 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="category" angle={-18} textAnchor="end" interval={0} height={70} tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 5]} />
              <Tooltip contentStyle={chartTooltip} formatter={(value, name) => [value, name]} labelFormatter={labelText => categoryRatings.find(item => item.category === labelText)?.fullCategory || labelText} />
              <Bar dataKey="average" name="Average rating" fill="#d98735" radius={[5, 5, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section style={panel}>
        <h2 style={{ margin: "0 0 5px", fontSize: 18 }}>Feedback submission trend</h2>
        <p style={{ margin: "0 0 14px", color: COLORS.muted, fontSize: 12 }}>Daily submissions for the latest 30 dates with matching feedback.</p>
        {trendData.length ? (
          <div style={{ width: "100%", height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip contentStyle={chartTooltip} />
                <Bar dataKey="submissions" name="Submissions" fill="#7c65c1" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : <p style={{ color: COLORS.muted, fontSize: 13 }}>No dated feedback records match the current filters.</p>}
      </section>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(290px,1fr))", gap: 20, alignItems: "start" }}>
        <section style={panel}>
          <h2 style={{ margin: "0 0 7px", fontSize: 19 }}>Submit feedback</h2>
          <p style={{ color: COLORS.muted, fontSize: 13, marginTop: 0 }}>Share a satisfaction rating or feedback about a student's learning.</p>
          <form onSubmit={submit} style={{ display: "grid", gap: 16 }}>
            <label style={label}>Feedback submitted by
              <select style={field} value={role} onChange={e => setRole(e.target.value)}>
                <option value="Student">Student</option>
                <option value="Faculty">Faculty</option>
              </select>
            </label>
            <label style={label}>Student ID
              <input style={field} value={studentId} onChange={e => setStudentId(e.target.value.toUpperCase())} placeholder="e.g. STU0001" required />
            </label>
            <label style={label}>Feedback category
              <select style={field} value={category} onChange={e => setCategory(e.target.value)}>
                {categories.map(item => <option key={item} value={item}>{item}</option>)}
              </select>
            </label>
            <div style={label}>Rating
              <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
                {[1, 2, 3, 4, 5].map(value => (
                  <button key={value} type="button" aria-label={`Rate ${value} out of 5`} onClick={() => setRating(value)} style={{
                    border: `1px solid ${rating >= value ? "#d98735" : COLORS.border}`,
                    background: rating >= value ? "#fff3e5" : COLORS.white,
                    borderRadius: 9, padding: "9px 12px", cursor: "pointer",
                    color: rating >= value ? "#d98735" : COLORS.muted, fontSize: 19
                  }}>★</button>
                ))}
                <span style={{ color: COLORS.muted, fontSize: 13 }}>{rating}/5</span>
              </div>
            </div>
            <label style={label}>Comments or suggestions
              <textarea style={{ ...field, minHeight: 110, resize: "vertical" }} value={comments} onChange={e => setComments(e.target.value)} maxLength={2000} placeholder="Share feedback or suggestions..." />
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

      <section style={panel}>
        <h2 style={{ margin: "0 0 7px", fontSize: 19 }}>Feedback records</h2>
        <p style={{ margin: "0 0 12px", color: COLORS.muted, fontSize: 12 }}>Showing {filteredFeedback.length} matching records, from up to 5,000 recent submissions.</p>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12, textAlign: "left" }}>
            <thead><tr>
              {["Date", "Student ID", "Department", "Role", "Category", "Rating", "Comments"].map(name => (
                <th key={name} style={{ padding: 10, borderBottom: `1px solid ${COLORS.border}`, color: COLORS.muted, whiteSpace: "nowrap" }}>{name}</th>
              ))}
            </tr></thead>
            <tbody>
              {filteredFeedback.slice(0, 100).map(item => (
                <tr key={item.id}>
                  <td style={{ padding: 10, borderBottom: `1px solid ${COLORS.border}`, whiteSpace: "nowrap" }}>{item.created_at ? new Date(item.created_at).toLocaleDateString() : "—"}</td>
                  <td style={{ padding: 10, borderBottom: `1px solid ${COLORS.border}` }}>{item.student_id || "—"}</td>
                  <td style={{ padding: 10, borderBottom: `1px solid ${COLORS.border}` }}>{item.department || "—"}</td>
                  <td style={{ padding: 10, borderBottom: `1px solid ${COLORS.border}` }}>{item.submitter_role}</td>
                  <td style={{ padding: 10, borderBottom: `1px solid ${COLORS.border}` }}>{item.category}</td>
                  <td style={{ padding: 10, borderBottom: `1px solid ${COLORS.border}`, whiteSpace: "nowrap" }}>{item.rating}/5 ★</td>
                  <td style={{ padding: 10, borderBottom: `1px solid ${COLORS.border}`, maxWidth: 260 }}>{item.comments || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filteredFeedback.length > 100 && <p style={{ color: COLORS.muted, fontSize: 12 }}>For readability, the table shows the first 100 matches. CSV export includes all filtered matches.</p>}
        {!filteredFeedback.length && <p style={{ color: COLORS.muted, fontSize: 13 }}>No feedback records match these filters.</p>}
      </section>
    </div>
  );
}
'''

path.write_text(code[:start] + replacement + code[end:])
print("Feedback Analytics Dashboard added.")
