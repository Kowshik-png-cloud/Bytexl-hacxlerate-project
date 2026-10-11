from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="EduPulse AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# DATA
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

ANALYTICS_FILE = BASE_DIR / "data" / "student_analytics_1000.csv"
ORIGINAL_FILE = BASE_DIR / "data" / "students_1000.csv"


@st.cache_data
def load_data(file_path, modified_time):
    data = pd.read_csv(file_path)

    numeric_columns = [
        "semester",
        "cgpa",
        "attendance_pct",
        "backlogs",
        "internal_marks",
        "assignment_completion_pct",
        "lms_logins_week",
        "events_participated",
        "certifications",
        "aptitude_score",
        "coding_score",
        "mock_interview_score",
        "technical_skill_score",
        "communication_score",
        "student_success_score",
    ]

    for column in numeric_columns:
        if column in data.columns:
            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

    return data


if ANALYTICS_FILE.exists():
    DATA_FILE = ANALYTICS_FILE
elif ORIGINAL_FILE.exists():
    DATA_FILE = ORIGINAL_FILE
else:
    st.error(
        "Student dataset not found. Run "
        "`python test_1000_students.py` first."
    )
    st.stop()


df = load_data(
    str(DATA_FILE),
    DATA_FILE.stat().st_mtime,
)

if df.empty:
    st.error("The student dataset is empty.")
    st.stop()


# =========================================================
# DEFAULT COLUMNS
# =========================================================

if "student_id" not in df.columns:
    df["student_id"] = [
        f"STU-{i + 1:04d}" for i in range(len(df))
    ]

if "department" not in df.columns:
    df["department"] = "Unknown"

if "semester" not in df.columns:
    df["semester"] = pd.NA

if "student_success_score" not in df.columns:
    df["student_success_score"] = float("nan")

if "academic_risk" not in df.columns:
    df["academic_risk"] = "Insufficient Data"

if "placement_risk" not in df.columns:
    df["placement_risk"] = "Insufficient Data"

if "student_category" not in df.columns:
    df["student_category"] = "Unclassified"


# =========================================================
# THEME
# =========================================================

PURPLE = "#7957F6"
LIGHT_PURPLE = "#E9E2FF"
DARK = "#151720"
GREEN = "#58B88A"
ORANGE = "#F0B85B"
RED = "#E36D7B"
MUTED = "#898995"
BORDER = "#E8E8EF"


st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: #f7f7fb;
        color: #252530;
    }

    [data-testid="stHeader"] {
        background: #f7f7fb;
    }

    [data-testid="stSidebar"] {
        background: #151720;
        border-right: none;
    }

    [data-testid="stSidebar"] * {
        color: #f0f0f7;
    }

    [data-testid="stSidebar"] hr {
        border-color: #30313d;
    }

    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        font-size: 13px;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #7957F6 !important;
        border-color: #7957F6 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="tag"] span {
        color: white !important;
    }

    .brand {
        font-size: 25px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -1px;
        padding-top: 8px;
    }

    .brand-icon {
        color: #a995ff;
    }

    .brand-caption {
        color: #a3a3b2;
        font-size: 9px;
        letter-spacing: 1.7px;
        margin-top: 6px;
        margin-bottom: 27px;
    }

    .faculty-card {
        background: #22232e;
        border: 1px solid #343541;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 20px;
    }

    .faculty-title {
        font-size: 13px;
        font-weight: 700;
        color: white;
    }

    .faculty-caption {
        font-size: 11px;
        color: #a7a7b7;
        margin-top: 4px;
    }

    .topbar {
        background: #ffffff;
        border: 1px solid #ececf2;
        border-radius: 13px;
        padding: 15px 20px;
        margin-bottom: 25px;
    }

    .topbar-title {
        font-size: 14px;
        font-weight: 700;
        color: #252530;
    }

    .topbar-subtitle {
        font-size: 11px;
        color: #9696a1;
        margin-top: 4px;
    }

    .page-title {
        font-size: 28px;
        font-weight: 800;
        color: #242430;
        letter-spacing: -1px;
        margin-bottom: 5px;
    }

    .page-subtitle {
        color: #858591;
        font-size: 12px;
        margin-bottom: 24px;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid #e8e8ef;
        border-radius: 15px;
        padding: 18px;
        min-height: 130px;
        margin-bottom: 12px;
    }

    .metric-label {
        color: #858591;
        font-size: 11px;
        font-weight: 500;
    }

    .metric-value {
        color: #252530;
        font-size: 28px;
        font-weight: 800;
        margin-top: 13px;
        letter-spacing: -1px;
    }

    .metric-note {
        color: #9999a5;
        font-size: 10px;
        margin-top: 8px;
    }

    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #282833;
        margin-top: 10px;
        margin-bottom: 5px;
    }

    .section-caption {
        color: #92929e;
        font-size: 11px;
        margin-bottom: 14px;
    }

    [data-testid="stPlotlyChart"] {
        background: white;
        border: 1px solid #e8e8ef;
        border-radius: 14px;
        padding: 6px;
    }

    [data-testid="stDataFrame"] {
        background: white;
        border: 1px solid #e8e8ef;
        border-radius: 12px;
        overflow: hidden;
    }

    div[data-testid="stDownloadButton"] button {
        background: #7957F6;
        color: white;
        border: 1px solid #7957F6;
        border-radius: 8px;
        font-weight: 600;
    }

    div[data-testid="stDownloadButton"] button:hover {
        background: #6544dc;
        color: white;
        border-color: #6544dc;
    }

    .support-card {
        background: white;
        border: 1px solid #e8e8ef;
        border-left: 4px solid #7957F6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 12px;
    }

    .support-title {
        font-size: 13px;
        font-weight: 700;
        color: #292936;
        margin-bottom: 7px;
    }

    .support-text {
        color: #858591;
        font-size: 12px;
        line-height: 1.6;
    }

    .footer {
        text-align: center;
        color: #a0a0ac;
        font-size: 10px;
        padding: 25px 0;
        margin-top: 25px;
        border-top: 1px solid #e8e8ef;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def section(title, caption=""):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-caption">{caption}</div>
        """,
        unsafe_allow_html=True,
    )


def metric(title, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{title}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def avg(data, column):
    if column not in data.columns:
        return None

    values = pd.to_numeric(
        data[column],
        errors="coerce",
    ).dropna()

    if values.empty:
        return None

    return float(values.mean())


def number(value):
    try:
        value = float(value)
        return value if pd.notna(value) else None
    except (ValueError, TypeError):
        return None


def csv_bytes(data):
    return data.to_csv(index=False).encode("utf-8-sig")


def chart_style(fig, height=300):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Inter, sans-serif",
            size=11,
            color="#72727f",
        ),
        margin=dict(
            l=20,
            r=20,
            t=30,
            b=20,
        ),
        height=height,
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
    )

    fig.update_yaxes(
        gridcolor="#F0F0F5",
        zeroline=False,
    )

    return fig


def recommendations(student):
    result = []

    attendance = number(student.get("attendance_pct"))
    cgpa = number(student.get("cgpa"))
    backlogs = number(student.get("backlogs"))
    assignments = number(
        student.get("assignment_completion_pct")
    )
    aptitude = number(student.get("aptitude_score"))
    coding = number(student.get("coding_score"))
    technical = number(student.get("technical_skill_score"))
    communication = number(student.get("communication_score"))

    if attendance is not None and attendance < 75:
        result.append((
            "High",
            "Attendance improvement",
            "Review attendance barriers and create a recovery plan."
        ))

    if cgpa is not None and cgpa < 6:
        result.append((
            "High",
            "Academic mentoring",
            "Arrange faculty mentoring and weekly subject revision."
        ))

    if backlogs is not None and backlogs >= 2:
        result.append((
            "High",
            "Backlog preparation",
            "Prioritize backlog subjects and practice previous papers."
        ))

    if assignments is not None and assignments < 70:
        result.append((
            "Medium",
            "Assignment completion",
            "Set weekly assignment targets and monitor progress."
        ))

    if aptitude is not None and aptitude < 50:
        result.append((
            "Medium",
            "Aptitude practice",
            "Practice quantitative aptitude and logical reasoning."
        ))

    if coding is not None and coding < 50:
        result.append((
            "Medium",
            "Coding practice",
            "Practice programming problems and review mistakes."
        ))

    if technical is not None and technical < 50:
        result.append((
            "Medium",
            "Technical skills",
            "Strengthen fundamentals and complete a practical project."
        ))

    if communication is not None and communication < 50:
        result.append((
            "Medium",
            "Communication skills",
            "Practice presentations and technical explanations."
        ))

    if not result:
        result.append((
            "Maintain",
            "Continue current progress",
            "Maintain consistent study habits and placement preparation."
        ))

    return result


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            <span class="brand-icon">✦</span> EduPulse
        </div>
        <div class="brand-caption">
            STUDENT SUCCESS PLATFORM
        </div>

        <div class="faculty-card">
            <div class="faculty-title">Faculty Workspace</div>
            <div class="faculty-caption">
                Student analytics and insights
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Student Analytics",
            "Placement Analytics",
            "Risk Analysis",
            "Student Support",
        ],
    )

    st.divider()

    st.markdown("### Filters")

    departments = sorted(
        df["department"].dropna().astype(str).unique()
    )

    selected_departments = st.multiselect(
        "Department",
        departments,
        default=departments,
    )

    semesters = sorted(
        pd.to_numeric(
            df["semester"],
            errors="coerce",
        ).dropna().unique()
    )

    if len(semesters):
        selected_semesters = st.multiselect(
            "Semester",
            semesters,
            default=semesters,
        )
    else:
        selected_semesters = []

    st.divider()

    st.caption("EDUPULSE AI")
    st.caption(f"{len(df):,} student records")


# =========================================================
# FILTER DATA
# =========================================================

filtered = df[
    df["department"]
    .astype(str)
    .isin(selected_departments)
].copy()

if len(semesters):
    filtered = filtered[
        pd.to_numeric(
            filtered["semester"],
            errors="coerce",
        ).isin(selected_semesters)
    ]

if filtered.empty:
    st.warning("No students match your selected filters.")
    st.stop()


# =========================================================
# TOP NAVIGATION BAR
# =========================================================

top_left, top_right = st.columns([4, 1])

with top_left:
    st.markdown(
        """
        <div class="topbar">
            <div class="topbar-title">
                EduPulse AI &nbsp; / &nbsp; Student Intelligence
            </div>
            <div class="topbar-subtitle">
                Academic performance · Placement readiness · Student support
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with top_right:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.button(
        "Faculty",
        use_container_width=True,
        disabled=True,
    )


# =========================================================
# PAGE 1: OVERVIEW
# =========================================================

if page == "Overview":

    st.markdown(
        '<div class="page-title">Student Success Overview</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Monitor performance and identify students who may need support.'
        '</div>',
        unsafe_allow_html=True,
    )

    total = len(filtered)

    score = avg(filtered, "student_success_score")

    academic_high = int(
        filtered["academic_risk"].eq("High").sum()
    )

    placement_high = int(
        filtered["placement_risk"].eq("High").sum()
    )

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        metric(
            "Total Students",
            f"{total:,}",
            "Current selection",
        )

    with k2:
        metric(
            "Average Success Score",
            f"{score:.1f}/100" if score is not None else "N/A",
            "Current scoring model",
        )

    with k3:
        metric(
            "Academic Risk",
            f"{academic_high:,}",
            "High-risk classification",
        )

    with k4:
        metric(
            "Placement Risk",
            f"{placement_high:,}",
            "High-risk classification",
        )

    left, right = st.columns([1.4, 1])

    with left:

        section(
            "Department Performance",
            "Average success score by department.",
        )

        department_summary = (
            filtered.groupby("department")
            .agg(
                Average_Score=(
                    "student_success_score",
                    "mean",
                )
            )
            .reset_index()
            .dropna(subset=["Average_Score"])
            .sort_values("Average_Score")
        )

        if not department_summary.empty:

            fig = px.bar(
                department_summary,
                x="Average_Score",
                y="department",
                orientation="h",
                text="Average_Score",
                color_discrete_sequence=[PURPLE],
            )

            fig.update_traces(
                texttemplate="%{x:.1f}",
                textposition="outside",
                cliponaxis=False,
            )

            fig.update_xaxes(range=[0, 110])

            chart_style(fig, 320)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        else:
            st.info("No valid success scores are available.")

    with right:

        section(
            "Academic Risk",
            "Distribution of current risk classifications.",
        )

        counts = (
            filtered["academic_risk"]
            .fillna("Insufficient Data")
            .value_counts()
            .rename_axis("Risk")
            .reset_index(name="Students")
        )

        fig = px.pie(
            counts,
            names="Risk",
            values="Students",
            hole=0.65,
            color="Risk",
            color_discrete_map={
                "Low": GREEN,
                "Moderate": ORANGE,
                "High": RED,
                "Insufficient Data": MUTED,
            },
        )

        fig.update_traces(
            textinfo="percent",
            textposition="inside",
        )

        chart_style(fig, 320)

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    section(
        "Students Requiring Attention",
        "Students flagged as high academic or placement risk.",
    )

    attention = filtered[
        filtered["academic_risk"].eq("High")
        | filtered["placement_risk"].eq("High")
    ].copy()

    if attention.empty:

        st.success("No high-risk students in the current selection.")

    else:

        columns = [
            "student_id",
            "department",
            "semester",
            "student_success_score",
            "academic_risk",
            "placement_risk",
        ]

        columns = [
            column for column in columns
            if column in attention.columns
        ]

        attention = attention.sort_values(
            "student_success_score",
            ascending=True,
            na_position="first",
        )

        st.dataframe(
            attention[columns],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download Attention Report",
            data=csv_bytes(attention),
            file_name="student_attention_report.csv",
            mime="text/csv",
        )


# =========================================================
# PAGE 2: STUDENT ANALYTICS
# =========================================================

elif page == "Student Analytics":

    st.markdown(
        '<div class="page-title">Student Analytics</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Search and explore individual student profiles.'
        '</div>',
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "Search Student ID",
        placeholder="Enter a student ID",
    )

    ids = filtered["student_id"].astype(str)

    if search.strip():
        ids = ids[
            ids.str.contains(
                search.strip(),
                case=False,
                na=False,
            )
        ]

    options = ids.tolist()

    if not options:

        st.warning("No matching student was found.")

    else:

        selected_id = st.selectbox(
            "Select student",
            options,
        )

        student = filtered[
            filtered["student_id"].astype(str)
            == selected_id
        ].iloc[0]

        score = number(student.get("student_success_score"))
        attendance = number(student.get("attendance_pct"))

        c1, c2, c3 = st.columns(3)

        with c1:
            metric(
                "Student ID",
                selected_id,
                str(student.get("department", "Unknown")),
            )

        with c2:
            metric(
                "Success Score",
                f"{score:.1f}/100" if score is not None else "N/A",
                "Current scoring model",
            )

        with c3:
            metric(
                "Attendance",
                f"{attendance:.1f}%" if attendance is not None else "N/A",
                "Recorded attendance",
            )

        left, right = st.columns(2)

        with left:

            section(
                "Academic Details",
                "Recorded academic indicators.",
            )

            academic_columns = [
                "cgpa",
                "internal_marks",
                "backlogs",
                "attendance_pct",
                "assignment_completion_pct",
                "lms_logins_week",
            ]

            available = [
                col for col in academic_columns
                if col in student.index
            ]

            st.dataframe(
                pd.DataFrame({
                    "Indicator": available,
                    "Value": [
                        student[col] for col in available
                    ],
                }),
                use_container_width=True,
                hide_index=True,
            )

        with right:

            section(
                "Placement Skills",
                "Available career-readiness scores.",
            )

            skill_columns = [
                "aptitude_score",
                "coding_score",
                "mock_interview_score",
                "technical_skill_score",
                "communication_score",
            ]

            values = []

            for column in skill_columns:
                value = number(student.get(column))

                if value is not None:
                    values.append({
                        "Skill": column.replace("_score", "").replace("_", " ").title(),
                        "Score": value,
                    })

            if values:

                fig = px.bar(
                    pd.DataFrame(values),
                    x="Score",
                    y="Skill",
                    orientation="h",
                    color_discrete_sequence=[PURPLE],
                )

                fig.update_xaxes(range=[0, 100])

                chart_style(fig, 300)

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

            else:
                st.info("Placement scores are unavailable.")

        section("Risk Classification")

        r1, r2 = st.columns(2)

        with r1:
            st.info(
                f"Academic Risk: {student.get('academic_risk', 'N/A')}"
            )

        with r2:
            st.info(
                f"Placement Risk: {student.get('placement_risk', 'N/A')}"
            )

        st.download_button(
            "Download Student Profile",
            data=csv_bytes(
                filtered[
                    filtered["student_id"].astype(str) == selected_id
                ]
            ),
            file_name=f"{selected_id}_profile.csv",
            mime="text/csv",
        )


# =========================================================
# PAGE 3: PLACEMENT ANALYTICS
# =========================================================

elif page == "Placement Analytics":

    st.markdown(
        '<div class="page-title">Placement Analytics</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Review aptitude, coding, and career-readiness indicators.'
        '</div>',
        unsafe_allow_html=True,
    )

    skill_columns = [
        ("aptitude_score", "Aptitude"),
        ("coding_score", "Coding"),
        ("mock_interview_score", "Mock Interview"),
        ("technical_skill_score", "Technical Skills"),
        ("communication_score", "Communication"),
    ]

    available = [
        (column, label)
        for column, label in skill_columns
        if column in filtered.columns
    ]

    if not available:

        st.warning("Placement data is unavailable.")

    else:

        cards = st.columns(len(available))

        for widget, (column, label) in zip(cards, available):

            value = avg(filtered, column)

            with widget:
                metric(
                    label,
                    f"{value:.1f}" if value is not None else "N/A",
                    "Average score out of 100",
                )

        section(
            "Department Skill Comparison",
            "Compare average skill scores by department.",
        )

        rows = []

        for department in sorted(
            filtered["department"].dropna().unique()
        ):

            subset = filtered[
                filtered["department"] == department
            ]

            for column, label in available:

                value = avg(subset, column)

                if value is not None:
                    rows.append({
                        "Department": department,
                        "Skill": label,
                        "Average Score": value,
                    })

        if rows:

            fig = px.bar(
                pd.DataFrame(rows),
                x="Department",
                y="Average Score",
                color="Skill",
                barmode="group",
                color_discrete_sequence=[
                    PURPLE,
                    "#A995FF",
                    "#C8BEFF",
                    GREEN,
                    ORANGE,
                ],
            )

            fig.update_yaxes(range=[0, 100])

            chart_style(fig, 380)

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

        section(
            "Students Requiring Placement Support",
            "Students classified as high placement risk.",
        )

        placement = filtered[
            filtered["placement_risk"].eq("High")
        ]

        columns = [
            "student_id",
            "department",
            "semester",
            "aptitude_score",
            "coding_score",
            "mock_interview_score",
            "placement_risk",
        ]

        columns = [
            col for col in columns
            if col in placement.columns
        ]

        st.dataframe(
            placement[columns],
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download Placement Report",
            data=csv_bytes(placement),
            file_name="placement_report.csv",
            mime="text/csv",
        )


# =========================================================
# PAGE 4: RISK ANALYSIS
# =========================================================

elif page == "Risk Analysis":

    st.markdown(
        '<div class="page-title">Risk Analysis</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Review risk categories and find students who may need support.'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    academic_high = int(
        filtered["academic_risk"].eq("High").sum()
    )

    academic_moderate = int(
        filtered["academic_risk"].eq("Moderate").sum()
    )

    placement_high = int(
        filtered["placement_risk"].eq("High").sum()
    )

    with c1:
        metric(
            "High Academic Risk",
            f"{academic_high:,}",
            "Current academic rules",
        )

    with c2:
        metric(
            "Moderate Academic Risk",
            f"{academic_moderate:,}",
            "Requires monitoring",
        )

    with c3:
        metric(
            "High Placement Risk",
            f"{placement_high:,}",
            "Current placement rules",
        )

    risk_type = st.radio(
        "Risk type",
        ["Academic Risk", "Placement Risk"],
        horizontal=True,
    )

    risk_column = (
        "academic_risk"
        if risk_type == "Academic Risk"
        else "placement_risk"
    )

    risk_levels = st.multiselect(
        "Risk levels",
        ["High", "Moderate", "Low", "Insufficient Data"],
        default=["High", "Moderate"],
    )

    risk_data = filtered[
        filtered[risk_column]
        .fillna("Insufficient Data")
        .isin(risk_levels)
    ].copy()

    section("Student Risk Register")

    columns = [
        "student_id",
        "department",
        "semester",
        "student_success_score",
        "academic_risk",
        "placement_risk",
        "academic_risk_reasons",
        "placement_risk_reasons",
    ]

    columns = [
        col for col in columns
        if col in risk_data.columns
    ]

    st.dataframe(
        risk_data[columns],
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download Risk Report",
        data=csv_bytes(risk_data),
        file_name="risk_report.csv",
        mime="text/csv",
    )

    section(
        "Risk by Department",
        "Students classified as high risk.",
    )

    risk_summary = (
        filtered.groupby("department")
        .agg(
            Academic_Risk=(
                "academic_risk",
                lambda x: x.eq("High").sum(),
            ),
            Placement_Risk=(
                "placement_risk",
                lambda x: x.eq("High").sum(),
            ),
        )
        .reset_index()
    )

    long_data = risk_summary.melt(
        id_vars="department",
        var_name="Risk Type",
        value_name="Students",
    )

    fig = px.bar(
        long_data,
        x="department",
        y="Students",
        color="Risk Type",
        barmode="group",
        color_discrete_sequence=[RED, PURPLE],
    )

    chart_style(fig, 350)

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.caption(
        "Risk categories use rule-based screening thresholds. "
        "They are not validated predictions."
    )


# =========================================================
# PAGE 5: STUDENT SUPPORT
# =========================================================

elif page == "Student Support":

    st.markdown(
        '<div class="page-title">Student Support</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Generate suggestions based on individual student indicators.'
        '</div>',
        unsafe_allow_html=True,
    )

    search = st.text_input(
        "Search student ID",
        placeholder="Enter student ID",
    )

    support_data = filtered.copy()

    if search.strip():

        support_data = support_data[
            support_data["student_id"]
            .astype(str)
            .str.contains(
                search.strip(),
                case=False,
                na=False,
            )
        ]

    if support_data.empty:

        st.warning("No matching student was found.")

    else:

        selected_id = st.selectbox(
            "Select student",
            support_data["student_id"].astype(str).tolist(),
        )

        student = support_data[
            support_data["student_id"].astype(str)
            == selected_id
        ].iloc[0]

        score = number(
            student.get("student_success_score")
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            metric(
                "Student",
                selected_id,
                str(student.get("department", "Unknown")),
            )

        with c2:
            metric(
                "Success Score",
                f"{score:.1f}/100" if score is not None else "N/A",
                "Current scoring model",
            )

        with c3:
            metric(
                "Academic Risk",
                str(student.get("academic_risk", "N/A")),
                "Current classification",
            )

        section(
            "Recommended Actions",
            "Suggestions generated from available student data.",
        )

        suggestions = recommendations(student)

        output = []

        for priority, title, description in suggestions:

            output.append({
                "Priority": priority,
                "Recommendation": title,
                "Suggested Action": description,
            })

            st.markdown(
                f"""
                <div class="support-card">
                    <div class="support-title">
                        {title}
                        <span style="color:{RED if priority == 'High' else PURPLE};
                                     font-size:11px;">
                            &nbsp; {priority} priority
                        </span>
                    </div>
                    <div class="support-text">
                        {description}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.download_button(
            "Download Support Plan",
            data=csv_bytes(pd.DataFrame(output)),
            file_name=f"{selected_id}_support_plan.csv",
            mime="text/csv",
        )

        st.caption(
            "These are rule-based suggestions. Faculty should review "
            "them before recommending interventions."
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        EduPulse AI · Student Success Intelligence Platform
        <br><br>
        Hackathon prototype · Demonstration data
    </div>
    """,
    unsafe_allow_html=True,
)