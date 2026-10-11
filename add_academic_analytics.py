from pathlib import Path

path = Path("frontend/src/App.jsx")
source = path.read_text()

# Prevent accidental duplicate changes.
if '["Academic Analytics", BookOpen]' in source:
    print("Academic Analytics navigation already exists.")
    raise SystemExit(0)

# 1. Add the navigation item.
old_nav = '''    ["Overview", LayoutDashboard], ["Students", Users], ["Academic Risk", ShieldAlert],
    ["Placement Readiness", BriefcaseBusiness], ["Insights", Activity],
    ["Feedback", MessageCircle]'''

new_nav = '''    ["Overview", LayoutDashboard], ["Students", Users], ["Academic Risk", ShieldAlert],
    ["Academic Analytics", BookOpen],
    ["Placement Readiness", BriefcaseBusiness], ["Insights", Activity],
    ["Feedback", MessageCircle]'''

if old_nav not in source:
    raise SystemExit("Could not locate navigation block. No changes were made.")

source = source.replace(old_nav, new_nav, 1)

# 2. Add the page heading.
old_heading = '''    "Academic Risk":["Academic risk monitor","Find students who may need academic support."],
    "Placement Readiness":["Placement readiness","Review success scores and placement-related indicators."],'''

new_heading = '''    "Academic Risk":["Academic risk monitor","Find students who may need academic support."],
    "Academic Analytics":["Academic analytics","Explore internal marks, backlog patterns, and academic risk details."],
    "Placement Readiness":["Placement readiness","Review success scores and placement-related indicators."],'''

if old_heading not in source:
    raise SystemExit("Could not locate heading block. No changes were made.")

source = source.replace(old_heading, new_heading, 1)

# 3. Add the page renderer.
old_renderer = '''      {page==="Placement Readiness" && <>'''

new_renderer = '''      {page==="Academic Analytics" && <AcademicAnalyticsPage data={data} onSelectStudent={s=>{setSelected(s);setPage("Student profile")}} />}
      {page==="Placement Readiness" && <>'''

if old_renderer not in source:
    raise SystemExit("Could not locate page renderer. No changes were made.")

source = source.replace(old_renderer, new_renderer, 1)

# 4. Add the Academic Analytics component before StudentTable.
marker = "function StudentTable({ students, onSelect }) {"

component = r'''
function AcademicAnalyticsPage({ data, onSelectStudent }) {
  const [dept, setDept] = useState("All departments");
  const [risk, setRisk] = useState("All");
  const [query, setQuery] = useState("");

  const departments = [
    "All departments",
    ...new Set(data.map(s => s.department).filter(Boolean))
  ].sort((a, b) =>
    a === "All departments" ? -1 :
    b === "All departments" ? 1 : a.localeCompare(b)
  );

  const students = data.filter(s =>
    (dept === "All departments" || s.department === dept) &&
    (risk === "All" || s.academicRisk === risk) &&
    `${s.id} ${s.department} ${s.semester} ${s.academicReasons}`
      .toLowerCase().includes(query.toLowerCase())
  );

  const withBacklogs = students.filter(s => num(s.backlogs) > 0);
  const totalBacklogs = students.reduce((sum, s) => sum + num(s.backlogs), 0);
  const highRisk = students.filter(s => s.academicRisk === "High").length;
  const avgInternal = average(students, "internal");

  const bands = [
    { label: "Below 40", min: 0, max: 40, color: COLORS.red },
    { label: "40–59", min: 40, max: 60, color: COLORS.orange },
    { label: "60–79", min: 60, max: 80, color: COLORS.blue },
    { label: "80–100", min: 80, max: Infinity, color: COLORS.teal }
  ].map(b => ({
    ...b,
    count: students.filter(s =>
      s.internal >= b.min && s.internal < b.max
    ).length
  }));

  const deptStats = departments
    .filter(d => d !== "All departments")
    .filter(d => dept === "All departments" || d === dept)
    .map(name => {
      const group = students.filter(s => s.department === name);
      return {
        name,
        count: group.length,
        cgpa: average(group, "cgpa"),
        internal: average(group, "internal"),
        backlogStudents: group.filter(s => num(s.backlogs) > 0).length,
        backlogs: group.reduce((sum, s) => sum + num(s.backlogs), 0),
        highRisk: group.filter(s => s.academicRisk === "High").length
      };
    });

  function exportReport() {
    const headers = [
      "Student ID", "Department", "Semester", "CGPA",
      "Internal Marks", "Backlogs", "Academic Risk", "Academic Risk Reasons"
    ];

    const escapeCSV = value =>
      '"' + String(value ?? "").replace(/"/g, '""') + '"';

    const rows = students.map(s => [
      s.id, s.department, s.semester, s.cgpa,
      s.internal, s.backlogs, s.academicRisk, s.academicReasons
    ]);

    const csv = [headers, ...rows]
      .map(row => row.map(escapeCSV).join(","))
      .join("\r\n");

    const blob = new Blob(["\uFEFF", csv], {
      type: "text/csv;charset=utf-8;"
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "edupulse_academic_report.csv";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  return <>
    <div style={filterRow}>
      <div style={searchBox}>
        <Search size={16} color={COLORS.muted}/>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search ID, department or risk reason"
          style={searchInput}
        />
      </div>

      <select value={dept} onChange={e => setDept(e.target.value)} style={selectStyle}>
        {departments.map(d => <option key={d} value={d}>{d}</option>)}
      </select>

      <select value={risk} onChange={e => setRisk(e.target.value)} style={selectStyle}>
        {["All", "High", "Medium", "Low"].map(r =>
          <option key={r} value={r}>
            {r === "All" ? "All risk levels" : `${r} risk`}
          </option>
        )}
      </select>

      <button style={ui.button} onClick={exportReport}>
        Export CSV ({students.length})
      </button>
    </div>

    <div style={grid4}>
      <Metric
        label="Average internal marks"
        value={avgInternal.toFixed(1)}
        note="Out of 100, based on the loaded dataset"
        icon={BookOpen}
      />
      <Metric
        label="Students with backlogs"
        value={withBacklogs.length}
        note="Students with one or more recorded backlogs"
        icon={AlertTriangle}
        tint={COLORS.orangeLight}
        accent={COLORS.orange}
      />
      <Metric
        label="Total recorded backlogs"
        value={totalBacklogs}
        note="Sum of backlog counts"
        icon={GraduationCap}
        tint={COLORS.blueLight}
        accent={COLORS.blue}
      />
      <Metric
        label="High academic risk"
        value={highRisk}
        note="Students classified as high risk"
        icon={ShieldAlert}
        tint={COLORS.redLight}
        accent={COLORS.red}
      />
    </div>

    <div style={grid2}>
      <Card>
        <SectionTitle
          title="Internal marks distribution"
          subtitle={`Marks grouped into ranges · ${students.length} students`}
        />

        {bands.map(b => (
          <div key={b.label} style={{ marginBottom: 19 }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: 13,
              marginBottom: 7
            }}>
              <span>{b.label}</span>
              <b>{b.count} students</b>
            </div>
            <div style={{
              height: 10,
              borderRadius: 10,
              background: "#edf1f7",
              overflow: "hidden"
            }}>
              <div style={{
                height: "100%",
                width: `${students.length ? b.count / students.length * 100 : 0}%`,
                background: b.color,
                borderRadius: 10
              }}/>
            </div>
          </div>
        ))}
      </Card>

      <Card>
        <SectionTitle
          title="Academic risk summary"
          subtitle="Risk classification for the filtered students"
        />

        {["High", "Medium", "Low"].map(level => {
          const count = students.filter(s => s.academicRisk === level).length;
          const color = level === "High" ? COLORS.red :
            level === "Medium" ? COLORS.orange : COLORS.teal;

          return <div key={level} style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "15px 0",
            borderBottom: `1px solid ${COLORS.border}`
          }}>
            <RiskBadge value={level}/>
            <div style={{ textAlign: "right" }}>
              <b style={{ fontSize: 20, color }}>{count}</b>
              <div style={{ fontSize: 11, color: COLORS.muted }}>
                {students.length ? (count / students.length * 100).toFixed(1) : "0.0"}%
              </div>
            </div>
          </div>;
        })}

        <p style={{ fontSize: 12, color: COLORS.muted, lineHeight: 1.6 }}>
          Risk labels come from the dataset or the dashboard's existing fallback
          rules. They indicate records that may need review, not a final academic decision.
        </p>
      </Card>
    </div>

    <Card style={{ marginTop: 20 }}>
      <SectionTitle
        title="Department academic comparison"
        subtitle="CGPA, internal marks and backlog counts for the selected students"
      />

      <div style={{ overflowX: "auto" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              {[
                "Department", "Students", "Average CGPA", "Avg. Internal",
                "Students with Backlogs", "Total Backlogs", "High Risk"
              ].map(label =>
                <th key={label} style={thStyle}>{label}</th>
              )}
            </tr>
          </thead>
          <tbody>
            {deptStats.map(d => (
              <tr key={d.name}>
                <td style={tdStyle}><b>{d.name}</b></td>
                <td style={tdStyle}>{d.count}</td>
                <td style={tdStyle}>{d.cgpa.toFixed(2)}</td>
                <td style={tdStyle}>{d.internal.toFixed(1)}</td>
                <td style={tdStyle}>{d.backlogStudents}</td>
                <td style={tdStyle}>{d.backlogs}</td>
                <td style={tdStyle}>{d.highRisk}</td>
              </tr>
            ))}
            {!deptStats.length && (
              <tr><td style={tdStyle} colSpan={7}>No matching records.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Card>

    <Card style={{ marginTop: 20 }}>
      <SectionTitle
        title="Students requiring academic review"
        subtitle={`${students.length} matching records · Select a student to open their profile`}
      />

      <div style={{ overflowX: "auto" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              {[
                "Student ID", "Department", "Semester", "CGPA",
                "Internal Marks", "Backlogs", "Risk", "Recorded reasons", ""
              ].map(label =>
                <th key={label} style={thStyle}>{label}</th>
              )}
            </tr>
          </thead>
          <tbody>
            {[...students]
              .sort((a, b) =>
                ({ High: 0, Medium: 1, Low: 2 }[a.academicRisk] -
                 { High: 0, Medium: 1, Low: 2 }[b.academicRisk]) ||
                num(b.backlogs) - num(a.backlogs)
              )
              .slice(0, 250)
              .map(s => (
                <tr key={s.id}>
                  <td style={tdStyle}><b>{s.id}</b></td>
                  <td style={tdStyle}>{s.department}</td>
                  <td style={tdStyle}>{s.semester}</td>
                  <td style={tdStyle}>{s.cgpa.toFixed(2)}</td>
                  <td style={tdStyle}>{s.internal.toFixed(1)}</td>
                  <td style={tdStyle}>{s.backlogs}</td>
                  <td style={tdStyle}><RiskBadge value={s.academicRisk}/></td>
                  <td style={{ ...tdStyle, whiteSpace: "normal", minWidth: 180 }}>
                    {s.academicReasons || "No reason recorded"}
                  </td>
                  <td style={tdStyle}>
                    <button
                      style={{ ...ui.button, padding: "7px 10px" }}
                      onClick={() => onSelectStudent(s)}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            {!students.length && (
              <tr><td style={tdStyle} colSpan={9}>No students match these filters.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {students.length > 250 && (
        <p style={{ color: COLORS.muted, fontSize: 12 }}>
          Showing the first 250 matching students. Export CSV to download all {students.length} matching records.
        </p>
      )}
    </Card>

    <Card style={{ marginTop: 20 }}>
      <SectionTitle title="Data coverage note" subtitle="Limitations of the current student dataset"/>
      <p style={{ fontSize: 13, color: COLORS.muted, lineHeight: 1.8, margin: 0 }}>
        This page analyzes the recorded CGPA, internal marks, backlog counts,
        departments and academic risk fields. The current CSV does not contain
        subject-level marks, so subject-wise performance cannot yet be calculated.
        The figures describe the loaded dataset and should be verified against
        official college records before making academic decisions.
      </p>
    </Card>
  </>;
}

'''

if marker not in source:
    raise SystemExit("Could not locate StudentTable insertion point. No changes were made.")

source = source.replace(marker, component + marker, 1)

path.write_text(source)
print("Academic Analytics was added to frontend/src/App.jsx.")
