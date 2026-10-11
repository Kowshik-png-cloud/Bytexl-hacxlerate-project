from pathlib import Path

path = Path("frontend/src/App.jsx")
source = path.read_text()

if '["Attendance Analytics", CalendarCheck]' in source:
    print("Attendance Analytics navigation already exists.")
    raise SystemExit(0)

# Add navigation item.
old_nav = '''    ["Academic Analytics", BookOpen],
    ["Placement Readiness", BriefcaseBusiness], ["Insights", Activity],'''

new_nav = '''    ["Academic Analytics", BookOpen],
    ["Attendance Analytics", CalendarCheck],
    ["Placement Readiness", BriefcaseBusiness], ["Insights", Activity],'''

if old_nav not in source:
    raise SystemExit("Navigation block not found. No changes made.")

source = source.replace(old_nav, new_nav, 1)

# Add page heading.
old_heading = '''    "Academic Analytics":["Academic analytics","Explore internal marks, backlog patterns, and academic risk details."],
    "Placement Readiness":["Placement readiness","Review success scores and placement-related indicators."],'''

new_heading = '''    "Academic Analytics":["Academic analytics","Explore internal marks, backlog patterns, and academic risk details."],
    "Attendance Analytics":["Attendance analytics","Monitor attendance levels, identify students needing support, and compare departments."],
    "Placement Readiness":["Placement readiness","Review success scores and placement-related indicators."],'''

if old_heading not in source:
    raise SystemExit("Heading block not found. No changes made.")

source = source.replace(old_heading, new_heading, 1)

# Add page renderer.
old_renderer = '''      {page==="Placement Readiness" && <>'''

new_renderer = '''      {page==="Attendance Analytics" && <AttendanceAnalyticsPage data={data} onSelectStudent={s=>{setSelected(s);setPage("Student profile")}} />}
      {page==="Placement Readiness" && <>'''

if old_renderer not in source:
    raise SystemExit("Page renderer not found. No changes made.")

source = source.replace(old_renderer, new_renderer, 1)

# Add component before StudentTable.
marker = "function StudentTable({ students, onSelect }) {"

component = r'''
function AttendanceAnalyticsPage({ data, onSelectStudent }) {
  const [dept, setDept] = useState("All departments");
  const [semester, setSemester] = useState("All semesters");
  const [threshold, setThreshold] = useState("75");
  const [query, setQuery] = useState("");

  const departments = [
    "All departments",
    ...new Set(data.map(s => s.department).filter(Boolean))
  ].sort((a, b) =>
    a === "All departments" ? -1 :
    b === "All departments" ? 1 : a.localeCompare(b)
  );

  const semesters = [
    "All semesters",
    ...new Set(data.map(s => s.semester)).values()
  ].sort((a, b) =>
    a === "All semesters" ? -1 :
    b === "All semesters" ? 1 : Number(a) - Number(b)
  );

  const attendanceThreshold = Number(threshold);

  const students = data.filter(s =>
    (dept === "All departments" || s.department === dept) &&
    (semester === "All semesters" || s.semester === Number(semester)) &&
    `${s.id} ${s.department} ${s.semester}`.toLowerCase().includes(query.toLowerCase())
  );

  const avgAttendance = average(students, "attendance");
  const belowThreshold = students.filter(s => s.attendance < attendanceThreshold);
  const atOrAboveThreshold = students.filter(s => s.attendance >= attendanceThreshold);
  const excellent = students.filter(s => s.attendance >= 90).length;

  const departmentStats = departments
    .filter(d => d !== "All departments")
    .filter(d => dept === "All departments" || d === dept)
    .map(name => {
      const group = students.filter(s => s.department === name);
      return {
        name,
        count: group.length,
        attendance: average(group, "attendance"),
        below: group.filter(s => s.attendance < attendanceThreshold).length,
        cgpa: average(group, "cgpa")
      };
    });

  const semesterStats = [...new Set(students.map(s => s.semester))]
    .sort((a, b) => a - b)
    .map(sem => {
      const group = students.filter(s => s.semester === sem);
      return {
        semester: `Sem ${sem}`,
        attendance: Number(average(group, "attendance").toFixed(1)),
        students: group.length,
        below: group.filter(s => s.attendance < attendanceThreshold).length
      };
    });

  const distribution = [
    { label: "Below 50%", min: -Infinity, max: 50, color: COLORS.red },
    { label: "50–64%", min: 50, max: 65, color: COLORS.orange },
    { label: "65–74%", min: 65, max: 75, color: COLORS.purple },
    { label: "75–89%", min: 75, max: 90, color: COLORS.blue },
    { label: "90–100%", min: 90, max: Infinity, color: COLORS.teal }
  ].map(b => ({
    ...b,
    count: students.filter(s => s.attendance >= b.min && s.attendance < b.max).length
  }));

  function exportReport() {
    const headers = [
      "Student ID", "Department", "Semester", "Attendance Percentage",
      "CGPA", "Backlogs", "Academic Risk", "Below Selected Threshold"
    ];

    const escapeCSV = value =>
      '"' + String(value ?? "").replace(/"/g, '""') + '"';

    const rows = students.map(s => [
      s.id, s.department, s.semester, s.attendance,
      s.cgpa, s.backlogs, s.academicRisk,
      s.attendance < attendanceThreshold ? "Yes" : "No"
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
    link.download = "edupulse_attendance_report.csv";
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
          placeholder="Search student ID or department"
          style={searchInput}
        />
      </div>

      <select value={dept} onChange={e => setDept(e.target.value)} style={selectStyle}>
        {departments.map(d => <option key={d} value={d}>{d}</option>)}
      </select>

      <select value={semester} onChange={e => setSemester(e.target.value)} style={selectStyle}>
        {semesters.map(s => (
          <option key={s} value={s}>{s === "All semesters" ? s : `Semester ${s}`}</option>
        ))}
      </select>

      <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: COLORS.muted }}>
        Alert threshold
        <select value={threshold} onChange={e => setThreshold(e.target.value)} style={selectStyle}>
          {[60, 65, 70, 75, 80, 85].map(n => (
            <option key={n} value={n}>{n}%</option>
          ))}
        </select>
      </label>

      <button style={ui.button} onClick={exportReport}>
        Export CSV ({students.length})
      </button>
    </div>

    <div style={grid4}>
      <Metric
        label="Average attendance"
        value={pct(avgAttendance)}
        note="Across filtered students"
        icon={CalendarCheck}
        tint={COLORS.blueLight}
        accent={COLORS.blue}
      />
      <Metric
        label="Below threshold"
        value={belowThreshold.length}
        note={`Attendance below ${attendanceThreshold}%`}
        icon={AlertTriangle}
        tint={COLORS.redLight}
        accent={COLORS.red}
      />
      <Metric
        label="At or above threshold"
        value={atOrAboveThreshold.length}
        note={`Attendance at least ${attendanceThreshold}%`}
        icon={CheckCircle2}
        tint={COLORS.tealLight}
        accent={COLORS.teal}
      />
      <Metric
        label="90% or higher"
        value={excellent}
        note="Students with high recorded attendance"
        icon={Award}
        tint={COLORS.purpleLight}
        accent={COLORS.purple}
      />
    </div>

    <div style={grid2}>
      <Card>
        <SectionTitle
          title="Attendance distribution"
          subtitle={`Students grouped by overall attendance · ${students.length} records`}
        />

        {distribution.map(b => (
          <div key={b.label} style={{ marginBottom: 17 }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: 13,
              marginBottom: 7
            }}>
              <span>{b.label}</span>
              <b>{b.count}</b>
            </div>
            <div style={{
              height: 9,
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
          title="Attendance alerts"
          subtitle={`Students below the selected ${attendanceThreshold}% threshold`}
        />

        <div style={{ fontSize: 30, fontWeight: 800, color: COLORS.red }}>
          {belowThreshold.length}
        </div>
        <p style={{ fontSize: 13, color: COLORS.muted, lineHeight: 1.7 }}>
          Students may need follow-up or support. Check official attendance
          records and your institution's attendance policy before taking action.
        </p>

        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <span style={{
            padding: "7px 10px",
            borderRadius: 9,
            background: COLORS.redLight,
            color: COLORS.red,
            fontSize: 12,
            fontWeight: 700
          }}>
            Below threshold
          </span>
          <span style={{
            padding: "7px 10px",
            borderRadius: 9,
            background: COLORS.tealLight,
            color: COLORS.teal,
            fontSize: 12,
            fontWeight: 700
          }}>
            {atOrAboveThreshold.length} meeting threshold
          </span>
        </div>
      </Card>
    </div>

    <Card style={{ marginTop: 20 }}>
      <SectionTitle
        title="Department attendance comparison"
        subtitle="Average attendance and students below the selected threshold"
      />

      <div style={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={departmentStats}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4"/>
            <XAxis dataKey="name" tick={{ fontSize: 10 }}/>
            <YAxis domain={[0, 100]}/>
            <Tooltip/>
            <Bar dataKey="attendance" name="Average attendance %" fill={COLORS.teal} radius={[6, 6, 0, 0]}/>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              {["Department", "Students", "Average Attendance", "Below Threshold", "Average CGPA"].map(label =>
                <th key={label} style={thStyle}>{label}</th>
              )}
            </tr>
          </thead>
          <tbody>
            {departmentStats.map(d => (
              <tr key={d.name}>
                <td style={tdStyle}><b>{d.name}</b></td>
                <td style={tdStyle}>{d.count}</td>
                <td style={tdStyle}>{pct(d.attendance)}</td>
                <td style={tdStyle}>{d.below}</td>
                <td style={tdStyle}>{d.cgpa.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>

    <Card style={{ marginTop: 20 }}>
      <SectionTitle
        title="Semester attendance comparison"
        subtitle="Average recorded attendance grouped by semester"
      />

      <div style={{ height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={semesterStats}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4"/>
            <XAxis dataKey="semester"/>
            <YAxis domain={[0, 100]}/>
            <Tooltip/>
            <Bar dataKey="attendance" name="Average attendance %" fill={COLORS.blue} radius={[6, 6, 0, 0]}/>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>

    <Card style={{ marginTop: 20 }}>
      <SectionTitle
        title="Students needing attendance review"
        subtitle={`${belowThreshold.length} students below the selected threshold`}
      />

      <div style={{ overflowX: "auto" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              {["Student ID", "Department", "Semester", "Attendance", "CGPA", "Backlogs", "Academic Risk", ""].map(label =>
                <th key={label} style={thStyle}>{label}</th>
              )}
            </tr>
          </thead>
          <tbody>
            {[...belowThreshold]
              .sort((a, b) => a.attendance - b.attendance)
              .slice(0, 250)
              .map(s => (
                <tr key={s.id}>
                  <td style={tdStyle}><b>{s.id}</b></td>
                  <td style={tdStyle}>{s.department}</td>
                  <td style={tdStyle}>{s.semester}</td>
                  <td style={{ ...tdStyle, color: COLORS.red, fontWeight: 800 }}>{pct(s.attendance)}</td>
                  <td style={tdStyle}>{s.cgpa.toFixed(2)}</td>
                  <td style={tdStyle}>{s.backlogs}</td>
                  <td style={tdStyle}><RiskBadge value={s.academicRisk}/></td>
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
            {!belowThreshold.length && (
              <tr><td style={tdStyle} colSpan={8}>No students fall below the selected threshold.</td></tr>
            )}
          </tbody>
        </table>
      </div>

      {belowThreshold.length > 250 && (
        <p style={{ fontSize: 12, color: COLORS.muted }}>
          Showing the first 250 students. Export CSV to download all filtered attendance records.
        </p>
      )}
    </Card>

    <Card style={{ marginTop: 20 }}>
      <SectionTitle title="Attendance data coverage" subtitle="What the current dataset supports"/>
      <p style={{ fontSize: 13, color: COLORS.muted, lineHeight: 1.8, margin: 0 }}>
        This page uses the overall attendance percentage recorded for each student.
        The current CSV does not contain subject-wise attendance, class dates,
        present/absent registers, or attendance history over time. Consequently,
        the charts compare students, departments, and semesters in the loaded
        dataset; they do not represent class-by-class records or historical trends.
      </p>
    </Card>
  </>;
}

'''

if marker not in source:
    raise SystemExit("StudentTable insertion point not found. No changes made.")

source = source.replace(marker, component + marker, 1)
path.write_text(source)

print("Attendance Analytics added successfully.")
