from pathlib import Path

path = Path("frontend/src/App.jsx")
code = path.read_text()

if "function SkillsAnalyticsPage(" in code:
    raise SystemExit("Skills Analytics already exists. No changes made.")

changes = [
    (
        '    ["Student Engagement", Award],',
        '    ["Student Engagement", Award],\n    ["Skills Analytics", BookOpen],'
    ),
    (
        '    "Student Engagement":["Student engagement analytics","Explore participation, certifications, and students who may need engagement support."],',
        '    "Student Engagement":["Student engagement analytics","Explore participation, certifications, and students who may need engagement support."],\n    "Skills Analytics":["Skills analytics","Explore technical and communication skills, skill gaps, and student development opportunities."],'
    ),
    (
        '      {page==="Student Engagement" && <EngagementAnalyticsPage data={data} onSelectStudent={s=>{setSelected(s);setPage("Student profile")}} />}\n',
        '      {page==="Student Engagement" && <EngagementAnalyticsPage data={data} onSelectStudent={s=>{setSelected(s);setPage("Student profile")}} />}\n      {page==="Skills Analytics" && <SkillsAnalyticsPage data={data} onSelectStudent={s=>{setSelected(s);setPage("Student profile")}} />}\n'
    ),
]

for old, new in changes:
    if code.count(old) != 1:
        raise SystemExit(
            "Stopped safely: expected exactly one match but found "
            f"{code.count(old)} for:\n{old}"
        )
    code = code.replace(old, new, 1)

marker = "function StudentTable({ students, onSelect }) {"
if code.count(marker) != 1:
    raise SystemExit("Could not safely find StudentTable.")

component = r'''
function SkillsAnalyticsPage({ data, onSelectStudent }) {
  const [search, setSearch] = useState("");
  const [department, setDepartment] = useState("All");
  const [skillLevel, setSkillLevel] = useState("All");
  const [threshold, setThreshold] = useState(50);

  const skills = [
    { key: "technical", label: "Technical skills" },
    { key: "communication", label: "Communication" },
    { key: "coding", label: "Coding" },
    { key: "aptitude", label: "Aptitude" },
    { key: "interview", label: "Mock interview" },
  ];

  const departments = [...new Set(data.map(s => s.department).filter(Boolean))].sort();
  const scoreOf = (s, key) => Math.max(0, Math.min(100, num(s[key])));

  const rows = data.map(s => {
    const gaps = skills.filter(skill => scoreOf(s, skill.key) < threshold);
    return {
      ...s,
      gaps,
      skillAverage: skills.reduce((sum, skill) => sum + scoreOf(s, skill.key), 0) / skills.length,
      skillLevel: gaps.length === 0 ? "Strong" : gaps.length <= 2 ? "Developing" : "Needs support",
    };
  });

  const averageSkill = key => average(rows, key);
  const strongCount = rows.filter(s => s.skillLevel === "Strong").length;
  const developingCount = rows.filter(s => s.skillLevel === "Developing").length;
  const supportCount = rows.filter(s => s.skillLevel === "Needs support").length;

  const departmentData = departments.map(name => {
    const group = rows.filter(s => s.department === name);
    const item = { name, Students: group.length };
    skills.forEach(skill => {
      item[skill.label] = Number(average(group, skill.key).toFixed(1));
    });
    return item;
  });

  const skillData = skills.map(skill => ({
    name: skill.label,
    Average: Number(averageSkill(skill.key).toFixed(1)),
    "Below target": rows.filter(s => scoreOf(s, skill.key) < threshold).length,
  }));

  const filtered = rows.filter(s => {
    const q = search.trim().toLowerCase();
    const matchesSearch =
      !q ||
      String(s.id ?? "").toLowerCase().includes(q) ||
      String(s.department ?? "").toLowerCase().includes(q);
    const matchesDepartment = department === "All" || s.department === department;
    const matchesLevel = skillLevel === "All" || s.skillLevel === skillLevel;
    return matchesSearch && matchesDepartment && matchesLevel;
  }).sort((a, b) => a.skillAverage - b.skillAverage);

  const suggestion = s => {
    const gaps = s.gaps.map(g => g.label);
    if (!gaps.length) return "Maintain current practice and review progress regularly.";
    return gaps.map(g => ({
      "Technical skills": "Practise core concepts and build a practical project.",
      "Communication": "Practise presentations, group discussions, and interview responses.",
      "Coding": "Solve coding problems regularly and revise data structures.",
      "Aptitude": "Practise quantitative, logical, and verbal reasoning.",
      "Mock interview": "Complete mock interviews and practise explaining solutions.",
    }[g])).join(" ");
  };

  const exportCSV = () => {
    const headers = [
      "Student ID", "Department", "Semester", "Skill Level",
      "Technical", "Communication", "Coding", "Aptitude",
      "Mock Interview", "Skill Gaps", "Suggested Development",
    ];
    const records = filtered.map(s => [
      s.id, s.department, s.semester, s.skillLevel,
      s.technical, s.communication, s.coding, s.aptitude, s.interview,
      s.gaps.map(g => g.label).join("; "), suggestion(s),
    ]);
    const escape = v => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const csv = [headers, ...records].map(r => r.map(escape).join(",")).join("\n");
    const blob = new Blob(["\uFEFF" + csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "edupulse_skills_analytics.csv";
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
    background: "#fff,
  };

  return (
    <div style={{ display: "grid", gap: 20 }}>
      <div>
        <h2 style={{ margin: "0 0 6px", fontSize: 22 }}>Skills Analytics</h2>
        <p style={{ margin: 0, color: "#64748b", fontSize: 13 }}>
          Review recorded skills, compare departments, and identify development opportunities.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(165px,1fr))", gap: 14 }}>
        {[
          ["Students analysed", rows.length, "#2563eb"],
          ["Average technical score", averageSkill("technical").toFixed(1), "#7c3aed"],
          ["Average communication", averageSkill("communication").toFixed(1), "#0f766e"],
          ["Strong at current target", strongCount, "#15803d"],
          ["May need support", supportCount, "#dc2626"],
        ].map(([label, value, color]) => (
          <div key={label} style={card}>
            <div style={{ fontSize: 13, color: "#64748b" }}>{label}</div>
            <div style={{ fontSize: 28, fontWeight: 750, color, marginTop: 8 }}>{value}</div>
          </div>
        ))}
      </div>

      <div style={card}>
        <h3 style={{ margin: "0 0 10px", fontSize: 16 }}>Skill target</h3>
        <p style={{ color: "#64748b", fontSize: 12, marginTop: 0 }}>
          Scores below the selected target are flagged for review.
        </p>
        <label style={{ display: "block", maxWidth: 350, fontSize: 13 }}>
          Target score: <b>{threshold}/100</b>
          <input
            type="range" min="30" max="80" step="5" value={threshold}
            onChange={e => setThreshold(Number(e.target.value))}
            style={{ display: "block", width: "100%", marginTop: 10 }}
          />
        </label>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(290px,1fr))", gap: 18 }}>
        <div style={card}>
          <h3 style={{ margin: "0 0 14px", fontSize: 16 }}>Average score by skill</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={skillData} margin={{ top: 5, right: 8, left: -10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="Average" fill={COLORS.blue} radius={[5,5,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div style={card}>
          <h3 style={{ margin: "0 0 14px", fontSize: 16 }}>Students below skill target</h3>
          <div style={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={skillData} margin={{ top: 5, right: 8, left: -10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="Below target" fill={COLORS.purple} radius={[5,5,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div style={card}>
        <h3 style={{ margin: "0 0 14px", fontSize: 16 }}>Department skill comparison</h3>
        <div style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={departmentData} margin={{ top: 5, right: 8, left: -10, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4" />
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="Technical skills" fill={COLORS.blue} />
              <Bar dataKey="Communication" fill={COLORS.teal} />
              <Bar dataKey="Coding" fill={COLORS.purple} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={card}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <div>
            <h3 style={{ margin: "0 0 5px", fontSize: 16 }}>Student skill profiles</h3>
            <p style={{ margin: 0, color: "#64748b", fontSize: 12 }}>{filtered.length} matching students</p>
          </div>
          <button onClick={exportCSV} style={{ border: 0, borderRadius: 8, padding: "10px 14px", background: COLORS.blue, color: "#fff", cursor: "pointer" }}>
            Export CSV
          </button>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 10, margin: "15px 0" }}>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search student ID or department" style={input} />
          <select value={department} onChange={e => setDepartment(e.target.value)} style={input}>
            <option value="All">All departments</option>
            {departments.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
          <select value={skillLevel} onChange={e => setSkillLevel(e.target.value)} style={input}>
            <option value="All">All skill levels</option>
            <option value="Strong">Strong</option>
            <option value="Developing">Developing</option>
            <option value="Needs support">Needs support</option>
          </select>
        </div>

        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", minWidth: 850, borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ textAlign: "left", background: "#f5f7fb" }}>
                {["Student ID", "Department", "Technical", "Communication", "Coding", "Aptitude", "Level", "Skill gaps", "Suggestions", "Profile"].map(h =>
                  <th key={h} style={{ padding: 10, borderBottom: "1px solid #e5eaf2", whiteSpace: "nowrap" }}>{h}</th>
                )}
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 200).map((s, i) => (
                <tr key={`${s.id}-${i}`}>
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{s.id}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{s.department}</td>
                  {[s.technical, s.communication, s.coding, s.aptitude].map((v, j) =>
                    <td key={j} style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{num(v).toFixed(1)}</td>
                  )}
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>{s.skillLevel}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7", minWidth: 150 }}>
                    {s.gaps.length ? s.gaps.map(g => g.label).join(", ") : "None at target"}
                  </td>
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7", minWidth: 220 }}>{suggestion(s)}</td>
                  <td style={{ padding: 10, borderBottom: "1px solid #edf1f7" }}>
                    <button onClick={() => onSelectStudent(s)} style={{ border: "1px solid #dce3ed", borderRadius: 7, padding: "6px 9px", background: "#fff", cursor: "pointer" }}>View</button>
                  </td>
                </tr>
              ))}
              {!filtered.length && <tr><td colSpan={10} style={{ padding: 20, textAlign: "center" }}>No students match these filters.</td></tr>}
            </tbody>
          </table>
        </div>
        {filtered.length > 200 && <p style={{ color: "#64748b", fontSize: 12 }}>Showing the first 200 rows. Export CSV for all matching students.</p>}
      </div>

      <div style={{ background: "#f5f8ff", border: "1px solid #dce7fb", borderRadius: 12, padding: 15 }}>
        <h3 style={{ margin: "0 0 7px", fontSize: 14 }}>How to interpret this page</h3>
        <p style={{ margin: 0, color: "#475569", fontSize: 12, lineHeight: 1.7 }}>
          Skill levels are screening labels based on the selected score target and the five available
          skill indicators. “Strong” means all five scores meet the target; “Developing” means one or
          two fall below it; “Needs support” means three or more fall below it. These are project-level
          rules, not validated psychological or employment assessments. Use them to guide supportive
          conversations rather than as definitive judgments about students.
        </p>
      </div>
    </div>
  );
}

'''

component = component.replace('background: "#fff,', 'background: "#fff",')

code = code.replace(marker, component + marker, 1)
path.write_text(code)
print("Skills Analytics added successfully.")
