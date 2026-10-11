from pathlib import Path

path = Path("frontend/src/App.jsx")
code = path.read_text()

marker = '      {page==="Placement Readiness" && <>'
if code.count(marker) != 1:
    raise SystemExit("Could not find the existing Placement Readiness page exactly once.")

if "function PlacementAnalyticsPage(" in code:
    raise SystemExit("PlacementAnalyticsPage already exists. Stopping to avoid duplicate code.")

# Replace the existing placement page with the upgraded component.
start = code.index(marker)
end_marker = "\n      {page==="
end = code.find(end_marker, start + len(marker))

if end == -1:
    raise SystemExit("Could not safely identify the end of the existing placement page.")

replacement = '''      {page==="Placement Readiness" && <PlacementAnalyticsPage data={data} onSelectStudent={s=>{setSelected(s);setPage("Student profile")}} />}
'''

code = code[:start] + replacement + code[end:]

component_marker = "function StudentTable({ students, onSelect }) {"
if code.count(component_marker) != 1:
    raise SystemExit("Could not safely find StudentTable.")

component = r"""
function PlacementAnalyticsPage({ data, onSelectStudent }) {
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("All");
  const [readiness, setReadiness] = useState("All");
  const [skillThreshold, setSkillThreshold] = useState(50);

  const departments = [...new Set(data.map(s => s.department).filter(Boolean))].sort();

  const skills = [
    { key: "coding", label: "Coding" },
    { key: "aptitude", label: "Aptitude" },
    { key: "interview", label: "Mock interview" },
    { key: "technical", label: "Technical skills" },
    { key: "communication", label: "Communication" },
  ];

  const scoreOf = (student, key) => Math.max(0, Math.min(100, num(student[key])));

  const classify = student => {
    const score = num(student.score);
    const coding = num(student.coding);
    if (score >= 70 && coding >= 50) return "High";
    if (score >= 45 && coding >= 30) return "Medium";
    return "Low";
  };

  const recommendations = student => {
    const weak = skills
      .filter(skill => scoreOf(student, skill.key) < skillThreshold)
      .map(skill => skill.label);

    if (!weak.length) {
      return "Maintain practice and complete regular mock assessments.";
    }

    return weak.map(skill => {
      const advice = {
        "Coding": "Practise coding problems and data structures.",
        "Aptitude": "Practise quantitative, logical, and verbal aptitude.",
        "Mock interview": "Complete mock interviews and practise explaining solutions.",
        "Technical skills": "Revise core technical concepts and complete practical projects.",
        "Communication": "Practise speaking, group discussions, and interview responses.",
      };
      return `${skill}: ${advice[skill]}`;
    }).join(" ");
  };

  const rows = data.map(student => ({
    ...student,
    placementReadiness: classify(student),
    skillGaps: skills.filter(skill => scoreOf(student, skill.key) < skillThreshold),
  }));

  const averageScore = key => average(rows, key);
  const highCount = rows.filter(s => s.placementReadiness === "High").length;
  const mediumCount = rows.filter(s => s.placementReadiness === "Medium").length;
  const lowCount = rows.filter(s => s.placementReadiness === "Low").length;
  const belowThreshold = rows.filter(s => s.skillGaps.length > 0).length;

  const filtered = rows.filter(s => {
    const query = search.trim().toLowerCase();
    const matchesSearch =
      !query ||
      String(s.id ?? "").toLowerCase().includes(query) ||
      String(s.department ?? "").toLowerCase().includes(query);
    const matchesDepartment = department === "All" || s.department === department;
    const matchesReadiness = readiness === "All" || s.placementReadiness === readiness;
    return matchesSearch && matchesDepartment && matchesReadiness;
  }).sort((a, b) => a.score - b.score);

  const departmentData = departments.map(name => {
    const group = rows.filter(s => s.department === name);
    return {
      name,
      Students: group.length,
      Coding: Number(average(group, "coding").toFixed(1)),
      Aptitude: Number(average(group, "aptitude").toFixed(1)),
      Interview: Number(average(group, "interview").toFixed(1)),
      Technical: Number(average(group, "technical").toFixed(1)),
      Communication: Number(average(group, "communication").toFixed(1)),
      "Success score": Number(average(group, "score").toFixed(1)),
    };
  });

  const skillData = skills.map(skill => ({
    name: skill.label,
    Average: Number(average(rows, skill.key).toFixed(1)),
    "Below threshold": rows.filter(s => scoreOf(s, skill.key) < skillThreshold).length,
  }));

  const exportCSV = () => {
    const headers = [
      "Student ID", "Department", "Semester", "Readiness",
      "Success Score", "Coding", "Aptitude", "Mock Interview",
      "Technical Skills", "Communication", "Skill Gaps", "Recommendations",
    ];
    const records = filtered.map(s => [
      s.id, s.department, s.semester, s.placementReadiness, s.score,
      s.coding, s.aptitude, s.interview, s.technical, s.communication,
      s.skillGaps.map(g => g.label).join("; "),
      recommendations(s),
    ]);
    const escape = value => `"${String(value ?? "").replace(/"/g, '""')}"`;
    const csv = [headers, ...records].map(row => row.map(escape).join(",")).join("\n");
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "edupulse_placement_analytics.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  const card = {
    background: "#fff",
    border: "1px solid #e5eaf2",
    borderRadius: 14,
    padding: 18,
    minWidth: 0,
  };
  const input = {
    width: "100%",
    boxSizing: "border-box",
    padding: "10px 12px",
    border: "1px solid #dce3ed",
    borderRadius: 8,
    background: "#fff",
  };

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div>
        <h2 style={{ margin: "0 0 6px", fontSize: 22 }}>Placement Analytics</h2>
        <p style={{ margin: 0, color: "#64748b", fontSize: 13 }}>
          Review recorded placement indicators, identify skill gaps, and plan student support.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(165px,1fr))", gap: 14 }}>
        {[
          ["Students analysed", rows.length, "#2563eb"],
          ["High readiness", highCount, "#15803d"],
          ["Medium readiness", mediumCount, "#b45309"],
          ["Low readiness", lowCount, "#dc2626"],
          ["Students with skill gaps", belowThreshold, "#7c3aed"],
        ].map(([label, value, color]) => (
          <div key={label} style={card}>
            <div style={{ fontSize: 13, color: "#64748b" }}>{label}</div>
            <div style={{ fontSize: 29, fontWeight: 750, color, marginTop: 8 }}>{value}</div>
          </div>
        ))}
      </div>

      <div style={card}>
        <h3 style={{ margin: "0 0 14px", fontSize: 16 }}>Placement indicator averages</h3>
        <div style={{ display: "grid", gap: 16 }}>
          {[
            ["Overall success score", averageScore("score")],
            ["Coding score", averageScore("coding")],
            ["Aptitude score", averageScore("aptitude")],
            ["Mock interview score", averageScore("interview")],
            ["Technical skill score", averageScore("technical")],
            ["Communication score", averageScore("communication")],
          ].map(([label, value]) => (
            <div key={label}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, fontSize: 13, marginBottom: 7 }}>
                <span>{label}</span><b>{num(value).toFixed(1)} / 100</b>
              </div>
              <div style={{ height: 9, background: "#edf1f7", borderRadius: 20, overflow: "hidden" }}>
                <div style={{ height: "100%", width: `${Math.max(0, Math.min(100, num(value)))}%`, background: COLORS.purple, borderRadius: 20 }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={card}>
        <h3 style={{ margin: "0 0 8px", fontSize: 16 }}>Skill gap analysis</h3>
        <p style={{ margin: "0 0 14px", color: "#64748b", fontSize: 12 }}>
          Adjust the threshold to find students whose recorded scores are below your chosen target.
        </p>
        <label style={{ display: "block", maxWidth: 320, fontSize: 13, color: "#475569", marginBottom: 18 }}>
          Skill target: {skillThreshold}/100
          <input type="range" min="30" max="80" step="5" value={skillThreshold}
            onChange={e => setSkillThreshold(Number(e.target.value))}
            style={{ display: "block", width: "100%", marginTop: 10 }} />
        </label>
        <div style={{ height: 300 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={skillData} margin={{ top: 8, right: 10, left: -12, bottom: 15 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="Below threshold" fill={COLORS.blue} radius={[5,5,0,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p style={{ fontSize: 12, color: "#64748b", marginBottom: 0 }}>
          The chart counts students below the selected target for each skill.
        </p>
      </div>

      <div style={card}>
        <h3 style={{ margin: "0 0 14px", fontSize: 16 }}>Department comparison</h3>
        <div style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={departmentData} margin={{ top: 8, right: 8, left: -10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="Coding" fill={COLORS.blue} />
              <Bar dataKey="Aptitude" fill={COLORS.purple} />
              <Bar dataKey="Interview" fill="#16a34a" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <p style={{ color: "#64748b", fontSize: 12, marginBottom: 0 }}>
          Compare average coding, aptitude, and mock interview scores across departments.
        </p>
      </div>

      <div style={card}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap", marginBottom: 14 }}>
          <div>
            <h3 style={{ margin: "0 0 5px", fontSize: 16 }}>Student placement review</h3>
            <p style={{ margin: 0, fontSize: 12, color: "#64748b" }}>{filtered.length} students match the selected filters</p>
          </div>
          <button onClick={exportCSV} style={{ border: 0, borderRadius: 8, padding: "10px 14px", background: COLORS.blue, color: "#fff", cursor: "pointer", fontWeight: 600 }}>
            Export CSV
          </button>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 10, marginBottom: 15 }}>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search student ID or department" style={input} />
          <select value={department} onChange={e => setDepartment(e.target.value)} style={input}>
            <option value="All">All departments</option>
            {departments.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
          <select value={readiness} onChange={e => setReadiness(e.target.value)} style={input}>
            <option value="All">All readiness levels</option>
            <option value="High">High readiness</option>
            <option value="Medium">Medium readiness</option>
            <option value="Low">Low readiness</option>
          </select>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12, minWidth: 900 }}>
            <thead>
              <tr style={{ textAlign: "left", background: "#f5f7fb" }}>
                {["Student ID", "Department", "Readiness", "Success", "Coding", "Aptitude", "Interview", "Skill gaps", "Recommendations", "Profile"].map(h =>
                  <th key={h} style={{ padding: 10, borderBottom: "1px solid #e5eaf2", whiteSpace: "nowrap" }}>{h}</th>
                )}
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 200).map((s, i) => (
                <tr key={`${s.id}-${i}`}>
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{s.id}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{s.department}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>
                    <span style={{
                      padding: "4px 7px", borderRadius: 6, fontWeight: 600,
                      color: s.placementReadiness === "High" ? "#166534" : s.placementReadiness === "Medium" ? "#92400e" : "#991b1b",
                      background: s.placementReadiness === "High" ? "#dcfce7" : s.placementReadiness === "Medium" ? "#fef3c7" : "#fee2e2"
                    }}>{s.placementReadiness}</span>
                  </td>
                  {[s.score, s.coding, s.aptitude, s.interview].map((v, j) =>
                    <td key={j} style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{num(v).toFixed(1)}</td>
                  )}
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7", minWidth: 150 }}>
                    {s.skillGaps.length ? s.skillGaps.map(g => g.label).join(", ") : "No gaps at current target"}
                  </td>
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7", minWidth: 250 }}>
                    {recommendations(s)}
                  </td>
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>
                    <button onClick={() => onSelectStudent(s)} style={{ border: "1px solid #dce3ed", borderRadius: 7, padding: "6px 9px", background: "#fff", cursor: "pointer" }}>View</button>
                  </td>
                </tr>
              ))}
              {!filtered.length && <tr><td colSpan={10} style={{ padding: 20, textAlign: "center", color: "#64748b" }}>No students match these filters.</td></tr>}
            </tbody>
          </table>
        </div>
        {filtered.length > 200 && <p style={{ color: "#64748b", fontSize: 12 }}>Showing 200 students. Export CSV to download all filtered results.</p>}
      </div>

      <div style={{ background: "#f5f8ff", border: "1px solid #dce7fb", borderRadius: 12, padding: 15 }}>
        <h3 style={{ margin: "0 0 7px", fontSize: 14 }}>How to interpret readiness</h3>
        <p style={{ margin: 0, color: "#475569", fontSize: 12, lineHeight: 1.7 }}>
          This page uses a screening rule based on the dataset's overall success score and coding score:
          High means success score at least 70 and coding at least 50; Medium means success score at least
          45 and coding at least 30 when the High rule is not met; otherwise Low. This is a configurable
          project-level heuristic, not a validated prediction of hiring outcomes. Recommendations are
          suggestions for practice, not guarantees of placement. Actual placement outcomes are not present
          in the current dataset.
        </p>
      </div>
    </div>
  );
}

"""

code = code.replace(component_marker, component + component_marker, 1)
path.write_text(code)
print("Placement Analytics upgraded successfully.")
