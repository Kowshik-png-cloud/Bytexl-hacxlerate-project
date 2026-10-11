from pathlib import Path

path = Path("frontend/src/App.jsx")
code = path.read_text()

changes = [
    (
        '    ["LMS Analytics", Activity],',
        '    ["LMS Analytics", Activity],\n    ["Student Engagement", Award],'
    ),
    (
        '    "LMS Analytics":["LMS analytics","Explore weekly learning platform activity, assignment completion, and student support needs."],',
        '    "LMS Analytics":["LMS analytics","Explore weekly learning platform activity, assignment completion, and student support needs."],\n    "Student Engagement":["Student engagement analytics","Explore participation, certifications, and students who may need engagement support."],'
    ),
    (
        '      {page==="LMS Analytics" && <LMSAnalyticsPage data={data} onSelectStudent={s=>{setSelected(s);setPage("Student profile")}} />}\n',
        '      {page==="LMS Analytics" && <LMSAnalyticsPage data={data} onSelectStudent={s=>{setSelected(s);setPage("Student profile")}} />}\n      {page==="Student Engagement" && <EngagementAnalyticsPage data={data} onSelectStudent={s=>{setSelected(s);setPage("Student profile")}} />}\n'
    ),
]

for old, new in changes:
    count = code.count(old)
    if count != 1:
        raise SystemExit(
            f"Stopped safely: expected exactly one matching location, found {count}:\n{old}"
        )
    code = code.replace(old, new, 1)

if "function EngagementAnalyticsPage(" in code:
    raise SystemExit("EngagementAnalyticsPage already exists; no component was added.")

marker = "function StudentTable({ students, onSelect }) {"
if code.count(marker) != 1:
    raise SystemExit("Could not safely locate StudentTable. No file changes were saved.")

component = r'''
function EngagementAnalyticsPage({ data, onSelectStudent }) {
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("All");
  const [engagement, setEngagement] = useState("All");
  const [eventLimit, setEventLimit] = useState(1);
  const [certLimit, setCertLimit] = useState(0);

  const departments = [...new Set(data.map(s => s.department).filter(Boolean))].sort();

  const rows = data.map(s => ({
    ...s,
    eventCount: Math.max(0, num(s.events)),
    certificationCount: Math.max(0, num(s.certifications)),
  }));

  const lowEvents = rows.filter(s => s.eventCount <= eventLimit).length;
  const lowCerts = rows.filter(s => s.certificationCount <= certLimit).length;
  const avgEvents = average(rows, "eventCount");
  const avgCerts = average(rows, "certificationCount");

  const filtered = rows.filter(s => {
    const query = search.trim().toLowerCase();
    const matchesSearch =
      !query ||
      String(s.id ?? "").toLowerCase().includes(query) ||
      String(s.department ?? "").toLowerCase().includes(query);
    const matchesDepartment =
      department === "All" || s.department === department;
    const matchesEngagement =
      engagement === "All" ||
      (engagement === "Low event participation" && s.eventCount <= eventLimit) ||
      (engagement === "No certifications" && s.certificationCount <= certLimit) ||
      (engagement === "Both concerns" &&
        s.eventCount <= eventLimit &&
        s.certificationCount <= certLimit);

    return matchesSearch && matchesDepartment && matchesEngagement;
  });

  const departmentData = departments.map(name => {
    const group = rows.filter(s => s.department === name);
    return {
      name,
      "Average events": Number(average(group, "eventCount").toFixed(2)),
      "Average certifications": Number(average(group, "certificationCount").toFixed(2)),
    };
  });

  const semesterData = [...new Set(rows.map(s => num(s.semester)))]
    .filter(n => n > 0)
    .sort((a, b) => a - b)
    .map(semester => {
      const group = rows.filter(s => num(s.semester) === semester);
      return {
        semester: `Sem ${semester}`,
        "Average events": Number(average(group, "eventCount").toFixed(2)),
        "Average certifications": Number(average(group, "certificationCount").toFixed(2)),
      };
    });

  const exportCSV = () => {
    const headers = ["Student ID", "Department", "Semester", "Events Participated", "Certifications"];
    const csvRows = filtered.map(s => [
      s.id, s.department, s.semester, s.eventCount, s.certificationCount
    ]);
    const escapeCSV = value =>
      `"${String(value ?? "").replace(/"/g, '""')}"`;
    const csv = [headers, ...csvRows]
      .map(row => row.map(escapeCSV).join(","))
      .join("\n");
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "student_engagement_report.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  const metricStyle = {
    background: "#fff",
    border: "1px solid #e5eaf2",
    borderRadius: 14,
    padding: 18,
    minWidth: 0,
  };
  const inputStyle = {
    padding: "10px 12px",
    border: "1px solid #dce3ed",
    borderRadius: 8,
    background: "#fff",
    minWidth: 0,
    width: "100%",
    boxSizing: "border-box",
  };
  const chartCard = {
    background: "#fff",
    border: "1px solid #e5eaf2",
    borderRadius: 14,
    padding: 18,
    minWidth: 0,
  };

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div>
        <h2 style={{ margin: "0 0 6px", fontSize: 22 }}>Student Engagement Analytics</h2>
        <p style={{ margin: 0, color: "#64748b", fontSize: 13 }}>
          Understand recorded event participation and certification activity.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(190px,1fr))", gap: 14 }}>
        <div style={metricStyle}>
          <div style={{ color: "#64748b", fontSize: 13 }}>Students analysed</div>
          <div style={{ fontSize: 29, fontWeight: 750, marginTop: 8 }}>{rows.length}</div>
        </div>
        <div style={metricStyle}>
          <div style={{ color: "#64748b", fontSize: 13 }}>Average events participated</div>
          <div style={{ fontSize: 29, fontWeight: 750, marginTop: 8 }}>{avgEvents.toFixed(2)}</div>
        </div>
        <div style={metricStyle}>
          <div style={{ color: "#64748b", fontSize: 13 }}>Average certifications</div>
          <div style={{ fontSize: 29, fontWeight: 750, marginTop: 8 }}>{avgCerts.toFixed(2)}</div>
        </div>
        <div style={metricStyle}>
          <div style={{ color: "#64748b", fontSize: 13 }}>Students with low event participation</div>
          <div style={{ fontSize: 29, fontWeight: 750, marginTop: 8 }}>{lowEvents}</div>
          <div style={{ color: "#64748b", fontSize: 12 }}>At or below {eventLimit} recorded event(s)</div>
        </div>
        <div style={metricStyle}>
          <div style={{ color: "#64748b", fontSize: 13 }}>Students with few certifications</div>
          <div style={{ fontSize: 29, fontWeight: 750, marginTop: 8 }}>{lowCerts}</div>
          <div style={{ color: "#64748b", fontSize: 12 }}>At or below {certLimit}</div>
        </div>
      </div>

      <div style={chartCard}>
        <h3 style={{ margin: "0 0 14px", fontSize: 16 }}>Engagement alert thresholds</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(210px,1fr))", gap: 16 }}>
          <label style={{ fontSize: 13, color: "#475569" }}>
            Flag students with event participation at or below
            <select value={eventLimit} onChange={e => setEventLimit(Number(e.target.value))} style={{ ...inputStyle, display: "block", marginTop: 7 }}>
              {[0,1,2,3,4,5].map(n => <option key={n} value={n}>{n} event(s)</option>)}
            </select>
          </label>
          <label style={{ fontSize: 13, color: "#475569" }}>
            Flag students with certifications at or below
            <select value={certLimit} onChange={e => setCertLimit(Number(e.target.value))} style={{ ...inputStyle, display: "block", marginTop: 7 }}>
              {[0,1,2,3,4,5].map(n => <option key={n} value={n}>{n} certification(s)</option>)}
            </select>
          </label>
        </div>
        <p style={{ color: "#64748b", fontSize: 12, margin: "12px 0 0" }}>
          These thresholds are configurable screening rules, not proof that a student is disengaged.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(290px,1fr))", gap: 18 }}>
        <div style={chartCard}>
          <h3 style={{ margin: "0 0 14px", fontSize: 16 }}>Average events by department</h3>
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departmentData} margin={{ top: 5, right: 8, left: -18, bottom: 35 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" interval={0} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="Average events" fill={COLORS.blue} radius={[5,5,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div style={chartCard}>
          <h3 style={{ margin: "0 0 14px", fontSize: 16 }}>Average certifications by department</h3>
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={departmentData} margin={{ top: 5, right: 8, left: -18, bottom: 35 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" interval={0} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="Average certifications" fill={COLORS.purple} radius={[5,5,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div style={chartCard}>
          <h3 style={{ margin: "0 0 14px", fontSize: 16 }}>Engagement by semester</h3>
          <div style={{ height: 280 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={semesterData} margin={{ top: 5, right: 8, left: -18, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4" />
                <XAxis dataKey="semester" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="Average events" fill={COLORS.blue} radius={[5,5,0,0]} />
                <Bar dataKey="Average certifications" fill={COLORS.purple} radius={[5,5,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p style={{ color: "#64748b", fontSize: 12, marginBottom: 0 }}>Blue: events · Purple: certifications</p>
        </div>
      </div>

      <div style={chartCard}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap", marginBottom: 14 }}>
          <div>
            <h3 style={{ margin: "0 0 5px", fontSize: 16 }}>Student engagement review</h3>
            <p style={{ margin: 0, color: "#64748b", fontSize: 12 }}>{filtered.length} students match your filters</p>
          </div>
          <button onClick={exportCSV} style={{ padding: "10px 14px", border: 0, borderRadius: 8, background: COLORS.blue, color: "#fff", cursor: "pointer", fontWeight: 600 }}>
            Export CSV
          </button>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 10, marginBottom: 16 }}>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search student ID or department" style={inputStyle} />
          <select value={department} onChange={e => setDepartment(e.target.value)} style={inputStyle}>
            <option value="All">All departments</option>
            {departments.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
          <select value={engagement} onChange={e => setEngagement(e.target.value)} style={inputStyle}>
            <option value="All">All engagement levels</option>
            <option value="Low event participation">Low event participation</option>
            <option value="No certifications">Few certifications</option>
            <option value="Both concerns">Both concerns</option>
          </select>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, minWidth: 650 }}>
            <thead>
              <tr style={{ background: "#f5f7fb", textAlign: "left" }}>
                {["Student ID","Department","Semester","Events","Certifications","Review","Profile"].map(h =>
                  <th key={h} style={{ padding: "11px 10px", borderBottom: "1px solid #e5eaf2", whiteSpace: "nowrap" }}>{h}</th>
                )}
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 250).map((s, index) => {
                const lowEvent = s.eventCount <= eventLimit;
                const lowCert = s.certificationCount <= certLimit;
                return (
                  <tr key={`${s.id}-${index}`}>
                    <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{s.id}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{s.department}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{s.semester || "—"}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{s.eventCount}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{s.certificationCount}</td>
                    <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>
                      {lowEvent && lowCert ? "Review both" : lowEvent ? "Review events" : lowCert ? "Review certifications" : "No threshold alert"}
                    </td>
                    <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>
                      <button onClick={() => onSelectStudent(s)} style={{ border: "1px solid #dce3ed", borderRadius: 7, padding: "6px 9px", background: "#fff", cursor: "pointer" }}>View</button>
                    </td>
                  </tr>
                );
              })}
              {filtered.length === 0 && <tr><td colSpan={7} style={{ padding: 20, textAlign: "center", color: "#64748b" }}>No students match these filters.</td></tr>}
            </tbody>
          </table>
        </div>
        {filtered.length > 250 && <p style={{ fontSize: 12, color: "#64748b" }}>Showing the first 250 matching students. Export CSV to download all matching records.</p>}
      </div>

      <div style={{ background: "#f5f8ff", border: "1px solid #dce7fb", borderRadius: 12, padding: 15 }}>
        <h3 style={{ margin: "0 0 7px", fontSize: 14 }}>Data coverage and interpretation</h3>
        <p style={{ margin: 0, fontSize: 12, lineHeight: 1.7, color: "#475569" }}>
          This page uses recorded event participation and certification counts in the dataset.
          It does not contain detailed club membership, hackathon participation, event dates,
          attendance at individual events, or a historical engagement timeline. Low counts are
          prompts for supportive follow-up, not definitive evidence of disengagement.
        </p>
      </div>
    </div>
  );
}

'''

code = code.replace(marker, component + marker, 1)
path.write_text(code)
print("Student Engagement Analytics added successfully.")
