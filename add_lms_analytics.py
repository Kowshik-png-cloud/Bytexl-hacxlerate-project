from pathlib import Path

path = Path("frontend/src/App.jsx")
source = path.read_text()

if '["LMS Analytics", Activity]' in source:
    print("LMS Analytics navigation already exists.")
    raise SystemExit(0)

old_nav = '''    ["Attendance Analytics", CalendarCheck],
    ["Placement Readiness", BriefcaseBusiness], ["Insights", Activity],'''

new_nav = '''    ["Attendance Analytics", CalendarCheck],
    ["LMS Analytics", Activity],
    ["Placement Readiness", BriefcaseBusiness], ["Insights", Activity],'''

if old_nav not in source:
    raise SystemExit("Navigation block not found. No changes made.")

source = source.replace(old_nav, new_nav, 1)

old_heading = '''    "Attendance Analytics":["Attendance analytics","Monitor attendance levels, identify students needing support, and compare departments."],
    "Placement Readiness":["Placement readiness","Review success scores and placement-related indicators."],'''

new_heading = '''    "Attendance Analytics":["Attendance analytics","Monitor attendance levels, identify students needing support, and compare departments."],
    "LMS Analytics":["LMS analytics","Explore weekly learning platform activity, assignment completion, and student support needs."],
    "Placement Readiness":["Placement readiness","Review success scores and placement-related indicators."],'''

if old_heading not in source:
    raise SystemExit("Heading block not found. No changes made.")

source = source.replace(old_heading, new_heading, 1)

old_renderer = '''      {page==="Placement Readiness" && <>'''

new_renderer = '''      {page==="LMS Analytics" && <LMSAnalyticsPage data={data} onSelectStudent={s=>{setSelected(s);setPage("Student profile")}} />}
      {page==="Placement Readiness" && <>'''

if old_renderer not in source:
    raise SystemExit("Page renderer not found. No changes made.")

source = source.replace(old_renderer, new_renderer, 1)

marker = "function StudentTable({ students, onSelect }) {"

component = r'''
function LMSAnalyticsPage({ data, onSelectStudent }) {
  const [dept, setDept] = useState("All departments");
  const [semester, setSemester] = useState("All semesters");
  const [loginLimit, setLoginLimit] = useState("3");
  const [assignmentLimit, setAssignmentLimit] = useState("60");
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

  const filtered = data.filter(s =>
    (dept === "All departments" || s.department === dept) &&
    (semester === "All semesters" || s.semester === Number(semester)) &&
    `${s.id} ${s.department} ${s.semester}`.toLowerCase().includes(query.toLowerCase())
  );

  const avgLogins = average(filtered, "lms");
  const avgAssignments = average(filtered, "assignments");
  const lowActivity = filtered.filter(s => s.lms <= Number(loginLimit));
  const lowAssignments = filtered.filter(s => s.assignments < Number(assignmentLimit));

  const departmentStats = departments
    .filter(d => d !== "All departments")
    .filter(d => dept === "All departments" || d === dept)
    .map(name => {
      const group = filtered.filter(s => s.department === name);
      return {
        name,
        students: group.length,
        logins: average(group, "lms"),
        assignments: average(group, "assignments"),
        lowActivity: group.filter(s => s.lms <= Number(loginLimit)).length,
        lowAssignments: group.filter(s => s.assignments < Number(assignmentLimit)).length
      };
    });

  const semesterStats = [...new Set(filtered.map(s => s.semester))]
    .sort((a, b) => a - b)
    .map(sem => {
      const group = filtered.filter(s => s.semester === sem);
      return {
        semester: `Sem ${sem}`,
        logins: Number(average(group, "lms").toFixed(1)),
        assignments: Number(average(group, "assignments").toFixed(1)),
        students: group.length
      };
    });

  const loginBands = [
    { label: "0–1 logins/week", min: 0, max: 2, color: COLORS.red },
    { label: "2–3 logins/week", min: 2, max: 4, color: COLORS.orange },
    { label: "4–6 logins/week", min: 4, max: 7, color: COLORS.blue },
    { label: "7+ logins/week", min: 7, max: Infinity, color: COLORS.teal }
  ].map(b => ({
    ...b,
    count: filtered.filter(s => s.lms >= b.min && s.lms < b.max).length
  }));

  function exportReport() {
    const headers = [
      "Student ID", "Department", "Semester",
      "LMS Logins Per Week", "Assignment Completion Percentage",
      "CGPA", "Attendance Percentage", "Low LMS Activity", "Low Assignment Completion"
    ];

    const escapeCSV = value =>
      '"' + String(value ?? "").replace(/"/g, '""') + '"';

    const rows = filtered.map(s => [
      s.id, s.department, s.semester, s.lms, s.assignments,
      s.cgpa, s.attendance,
      s.lms <= Number(loginLimit) ? "Yes" : "No",
      s.assignments < Number(assignmentLimit) ? "Yes" : "No"
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
    link.download = "edupulse_lms_report.csv";
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

      <label style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 12, color: COLORS.muted }}>
        Low-activity limit
        <select value={loginLimit} onChange={e => setLoginLimit(e.target.value)} style={selectStyle}>
          {[1, 2, 3, 4, 5].map(n => <option key={n} value={n}>{n} logins/week</option>)}
        </select>
      </label>

      <label style={{ display: "flex", alignItems: "center", gap: 7, fontSize: 12, color: COLORS.muted }}>
        Assignment alert
        <select value={assignmentLimit} onChange={e => setAssignmentLimit(e.target.value)} style={selectStyle}>
          {[40, 50, 60, 70, 75, 80].map(n => <option key={n} value={n}>{n}%</option>)}
        </select>
      </label>

      <button style={ui.button} onClick={exportReport}>
        Export CSV ({filtered.length})
      </button>
    </div>

    <div style={grid4}>
      <Metric
        label="Average LMS logins"
        value={avgLogins.toFixed(1)}
        note="Recorded logins per week"
        icon={Activity}
        tint={COLORS.blueLight}
        accent={COLORS.blue}
      />
      <Metric
        label="Average assignment completion"
        value={pct(avgAssignments)}
        note="Across filtered students"
        icon={CheckCircle2}
        tint={COLORS.tealLight}
        accent={COLORS.teal}
      />
      <Metric
        label="Low LMS activity"
        value={lowActivity.length}
        note={`At or below ${loginLimit} logins/week`}
        icon={AlertTriangle}
        tint={COLORS.redLight}
        accent={COLORS.red}
      />
      <Metric
        label="Low assignment completion"
        value={lowAssignments.length}
        note={`Below ${assignmentLimit}% completion`}
        icon={BookOpen}
        tint={COLORS.orangeLight}
        accent={COLORS.orange}
      />
    </div>

    <div style={grid2}>
      <Card>
        <SectionTitle
          title="Weekly LMS login distribution"
          subtitle="Students grouped by recorded weekly logins"
        />
        {loginBands.map(b => (
          <div key={b.label} style={{ marginBottom: 17 }}>
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
              height: 9,
              borderRadius: 10,
              background: "#edf1f7",
              overflow: "hidden"
            }}>
              <div style={{
                height: "100%",
                width: `${filtered.length ? b.count / filtered.length * 100 : 0}%`,
                background: b.color,
                borderRadius: 10
              }}/>
            </div>
          </div>
        ))}
      </Card>

      <Card>
        <SectionTitle
          title="Assignment completion"
          subtitle="Students grouped by completion percentage"
        />
        {[
          { label: "Below 40%", min: 0, max: 40, color: COLORS.red },
          { label: "40–59%", min: 40, max: 60, color: COLORS.orange },
          { label: "60–79%", min: 60, max: 80, color: COLORS.blue },
          { label: "80–100%", min: 80, max: Infinity, color: COLORS.teal }
        ].map(b => {
          const count = filtered.filter(s => s.assignments >= b.min && s.assignments < b.max).length;
          return <div key={b.label} style={{ marginBottom: 17 }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              fontSize: 13,
              marginBottom: 7
            }}>
              <span>{b.label}</span><b>{count} students</b>
            </div>
            <div style={{
              height: 9,
              borderRadius: 10,
              background: "#edf1f7",
              overflow: "hidden"
            }}>
              <div style={{
                height: "100%",
                width: `${filtered.length ? count / filtered.length * 100 : 0}%`,
                background: b.color,
                borderRadius: 10
              }}/>
            </div>
          </div>;
        })}
      </Card>
    </div>

    <Card style={{ marginTop: 20 }}>
      <SectionTitle
        title="LMS activity and assignments by department"
        subtitle="Average weekly logins compared with assignment completion"
      />
      <div style={{ height: 300 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={departmentStats}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4"/>
            <XAxis dataKey="name" tick={{ fontSize: 10 }}/>
            <YAxis domain={[0, 100]}/>
            <Tooltip/>
            <Bar dataKey="logins" name="Average logins/week" fill={COLORS.blue} radius={[6, 6, 0, 0]}/>
            <Bar dataKey="assignments" name="Assignment completion %" fill={COLORS.teal} radius={[6, 6, 0, 0]}/>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              {["Department", "Students", "Avg. Logins/Week", "Avg. Assignment Completion", "Low Activity", "Low Assignments"].map(label =>
                <th key={label} style={thStyle}>{label}</th>
              )}
            </tr>
          </thead>
          <tbody>
            {departmentStats.map(d => (
              <tr key={d.name}>
                <td style={tdStyle}><b>{d.name}</b></td>
                <td style={tdStyle}>{d.students}</td>
                <td style={tdStyle}>{d.logins.toFixed(1)}</td>
                <td style={tdStyle}>{pct(d.assignments)}</td>
                <td style={tdStyle}>{d.lowActivity}</td>
                <td style={tdStyle}>{d.lowAssignments}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>

    <Card style={{ marginTop: 20 }}>
      <SectionTitle
        title="Semester LMS comparison"
        subtitle="Recorded login frequency and assignment completion"
      />
      <div style={{ height: 280 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={semesterStats}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e8edf4"/>
            <XAxis dataKey="semester"/>
            <YAxis/>
            <Tooltip/>
            <Bar dataKey="logins" name="Average logins/week" fill={COLORS.blue} radius={[6, 6, 0, 0]}/>
            <Bar dataKey="assignments" name="Assignment completion %" fill={COLORS.teal} radius={[6, 6, 0, 0]}/>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>

    <Card style={{ marginTop: 20 }}>
      <SectionTitle
        title="Students needing LMS support"
        subtitle={`${filtered.filter(s => s.lms <= Number(loginLimit) || s.assignments < Number(assignmentLimit)).length} students meet at least one selected alert condition`}
      />
      <div style={{ overflowX: "auto" }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              {["Student ID", "Department", "Semester", "Logins/Week", "Assignment Completion", "CGPA", "Attendance", "Alert", ""].map(label =>
                <th key={label} style={thStyle}>{label}</th>
              )}
            </tr>
          </thead>
          <tbody>
            {filtered
              .filter(s => s.lms <= Number(loginLimit) || s.assignments < Number(assignmentLimit))
              .sort((a, b) => a.lms - b.lms || a.assignments - b.assignments)
              .slice(0, 250)
              .map(s => {
                const lowLogin = s.lms <= Number(loginLimit);
                const lowAssignment = s.assignments < Number(assignmentLimit);
                return <tr key={s.id}>
                  <td style={tdStyle}><b>{s.id}</b></td>
                  <td style={tdStyle}>{s.department}</td>
                  <td style={tdStyle}>{s.semester}</td>
                  <td style={tdStyle}>{s.lms}</td>
                  <td style={tdStyle}>{pct(s.assignments)}</td>
                  <td style={tdStyle}>{s.cgpa.toFixed(2)}</td>
                  <td style={tdStyle}>{pct(s.attendance)}</td>
                  <td style={tdStyle}>
                    <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
                      {lowLogin && <RiskBadge value="High"/>}
                      {lowAssignment && <span style={{
                        padding: "5px 9px", borderRadius: 20,
                        fontSize: 11, fontWeight: 800,
                        background: COLORS.orangeLight, color: COLORS.orange
                      }}>Assignment</span>}
                    </div>
                  </td>
                  <td style={tdStyle}>
                    <button
                      style={{ ...ui.button, padding: "7px 10px" }}
                      onClick={() => onSelectStudent(s)}
                    >View</button>
                  </td>
                </tr>;
              })}
            {!filtered.some(s => s.lms <= Number(loginLimit) || s.assignments < Number(assignmentLimit)) && (
              <tr><td style={tdStyle} colSpan={9}>No students match the selected alert thresholds.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </Card>

    <Card style={{ marginTop: 20 }}>
      <SectionTitle title="LMS data coverage" subtitle="What the current dataset supports"/>
      <p style={{ fontSize: 13, color: COLORS.muted, lineHeight: 1.8, margin: 0 }}>
        This page uses the recorded weekly LMS login count and assignment completion
        percentage. The dataset does not provide individual login timestamps,
        session duration, assignment-level records, or historical weekly activity.
        Low login frequency is a signal for review, not proof that a student is
        disengaged or struggling.
      </p>
    </Card>
  </>;
}

'''

if marker not in source:
    raise SystemExit("StudentTable insertion point not found. No changes made.")

source = source.replace(marker, component + marker, 1)
path.write_text(source)

print("LMS Analytics added successfully.")
