import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import random
from datetime import datetime, timedelta

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="F1 Analytics Platform",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=JetBrains+Mono:wght@300;400;500&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --red:    #E10600;
    --red-dk: #A00400;
    --gold:   #FFC906;
    --bg:     #0A0A0F;
    --bg2:    #111118;
    --bg3:    #1A1A24;
    --border: #2A2A38;
    --text:   #E8E8F0;
    --muted:  #6B6B82;
    --green:  #00C87A;
    --blue:   #3A8DFF;
}

html, body, [data-testid="stApp"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Remove default padding */
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Headers */
h1, h2, h3 {
    font-family: 'Orbitron', monospace !important;
    letter-spacing: 0.05em;
}
h1 { color: var(--red) !important; }
h2 { color: var(--gold) !important; font-size: 1.1rem !important; }
h3 { color: var(--text) !important; font-size: 0.95rem !important; }

/* Metric cards */
[data-testid="stMetric"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px;
    padding: 0.75rem 1rem !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    color: var(--muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
[data-testid="stMetricValue"] {
    font-family: 'Orbitron', monospace !important;
    font-size: 1.4rem !important;
    color: var(--gold) !important;
}
[data-testid="stMetricDelta"] svg { display: none; }

/* Tabs */
[data-testid="stTabs"] button {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted) !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
}

/* Buttons */
.stButton > button {
    background: var(--red) !important;
    color: white !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em;
    border: none !important;
    border-radius: 3px !important;
    padding: 0.5rem 1.2rem !important;
    transition: background 0.2s;
}
.stButton > button:hover { background: var(--red-dk) !important; }

/* Progress */
.stProgress > div > div { background: var(--red) !important; }

/* Selectbox / widgets */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}

/* Code / mono text */
code, pre { font-family: 'JetBrains Mono', monospace !important; }

/* Custom cards */
.card {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.card-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--muted);
    margin-bottom: 0.25rem;
}
.card-value {
    font-family: 'Orbitron', monospace;
    font-size: 1.5rem;
    color: var(--gold);
}

/* Pipeline step */
.pipe-step {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.6rem 1rem;
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 4px;
    margin-bottom: 0.35rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
}
.pipe-dot-ok   { width: 8px; height: 8px; border-radius: 50%; background: var(--green); flex-shrink: 0; }
.pipe-dot-run  { width: 8px; height: 8px; border-radius: 50%; background: var(--gold); flex-shrink: 0; animation: pulse 1s infinite; }
.pipe-dot-idle { width: 8px; height: 8px; border-radius: 50%; background: var(--border); flex-shrink: 0; }

@keyframes pulse {
    0%,100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* Tag badges */
.badge {
    display: inline-block;
    padding: 0.15rem 0.5rem;
    border-radius: 3px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    margin-right: 0.3rem;
}
.badge-spark   { background: #E25A1C22; color: #E25A1C; border: 1px solid #E25A1C44; }
.badge-snow    { background: #3A8DFF22; color: var(--blue); border: 1px solid #3A8DFF44; }
.badge-python  { background: #FFD84422; color: var(--gold); border: 1px solid #FFD84444; }
.badge-dbt     { background: #FF6B6B22; color: #FF6B6B; border: 1px solid #FF6B6B44; }
.badge-looker  { background: #00C87A22; color: var(--green); border: 1px solid #00C87A44; }

.section-header {
    font-family: 'Orbitron', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    border-bottom: 1px solid var(--border);
    padding-bottom: 0.4rem;
    margin: 1.2rem 0 0.75rem;
}

.log-line {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    line-height: 1.7;
    color: #9090AA;
}
.log-ok   { color: var(--green); }
.log-warn { color: var(--gold); }
.log-err  { color: var(--red); }
.log-info { color: var(--blue); }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convert #RRGGBB to Plotly-safe rgba()."""
    hex_color = str(hex_color).strip().lstrip("#")
    if len(hex_color) != 6:
        return f"rgba(255,255,255,{alpha})"
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    except ValueError:
        return f"rgba(255,255,255,{alpha})"


def safe_metric(label, value):
    st.metric(label, value)


# ─── SYNTHETIC DATA GENERATION ────────────────────────────────────────────────
@st.cache_data
def generate_f1_data():
    random.seed(42)
    np.random.seed(42)

    drivers = [
        ("HAM", "Lewis Hamilton",    "Mercedes", 44, 7),
        ("VER", "Max Verstappen",    "Red Bull", 1, 4),
        ("SCH", "Michael Schumacher","Ferrari",  3, 7),
        ("SEN", "Ayrton Senna",      "McLaren", 12, 3),
        ("VET", "Sebastian Vettel",  "Red Bull", 5, 4),
        ("ALO", "Fernando Alonso",   "Renault", 14, 2),
        ("PRO", "Alain Prost",       "McLaren", 8, 4),
        ("RAI", "Kimi Räikkönen",    "Ferrari", 7, 1),
        ("NOR", "Lando Norris",      "McLaren", 4, 0),
        ("LEC", "Charles Leclerc",   "Ferrari", 16, 0),
    ]

    seasons = list(range(2010, 2025))
    tracks = [
        "Monaco", "Silverstone", "Monza", "Spa",
        "Suzuka", "Abu Dhabi", "Bahrain", "Melbourne",
        "Zandvoort", "Interlagos", "COTA", "Singapore"
    ]

    rows = []
    points_map = [25,18,15,12,10,8,6,4,2,1,0,0,0,0,0,0,0,0,0,0]

    for season in seasons:
        for i, track in enumerate(tracks[:10]):
            for d_idx, (code, name, team, num, champs) in enumerate(drivers):
                base = d_idx * 1.65 + random.gauss(0, 2.2)
                pos = max(1, min(20, int(base + 1)))
                rows.append({
                    "season": season,
                    "round": i + 1,
                    "track": track,
                    "driver_code": code,
                    "driver_name": name,
                    "team": team,
                    "position": pos,
                    "points": max(0, points_map[min(pos - 1, 19)]),
                    "fastest_lap": round(random.uniform(75, 105), 3),
                    "pit_stops": random.randint(1, 3),
                    "grid": max(1, min(20, pos + random.randint(-5, 5))),
                    "status": random.choices(["Finished", "DNF", "+1 Lap"], [0.88, 0.07, 0.05])[0],
                })

    races_df = pd.DataFrame(rows)

    standings = (
        races_df.groupby(["season", "driver_code", "driver_name", "team"])["points"]
        .sum()
        .reset_index()
    )
    standings = standings.sort_values(["season", "points"], ascending=[True, False])
    standings["rank"] = (
        standings.groupby("season")["points"]
        .rank(ascending=False, method="first")
        .astype(int)
    )

    constructors = (
        races_df.groupby(["season", "team"])["points"]
        .sum()
        .reset_index()
        .sort_values(["season", "points"], ascending=[True, False])
    )

    lap_rows = []
    for season in [2020, 2021, 2022, 2023, 2024]:
        for d_code, d_name, team, _, _ in drivers[:5]:
            for lap in range(1, 55):
                base_time = 82 + random.gauss(0, 0.8)
                fuel_delta = -0.03 * lap
                lap_rows.append({
                    "season": season,
                    "driver_code": d_code,
                    "team": team,
                    "lap": lap,
                    "lap_time": round(base_time + fuel_delta + random.gauss(0, 0.4), 3),
                    "sector1": round(27 + random.gauss(0, 0.2), 3),
                    "sector2": round(29 + random.gauss(0, 0.2), 3),
                    "sector3": round(26 + random.gauss(0, 0.2), 3),
                })

    laps_df = pd.DataFrame(lap_rows)

    ingestion_log = [
        ("2024-01-15 08:00:01", "races.csv",         "raw",       150_000,  "SUCCESS"),
        ("2024-01-15 08:00:03", "drivers.csv",       "raw",         2_340,  "SUCCESS"),
        ("2024-01-15 08:00:05", "constructors.csv",  "raw",           420,  "SUCCESS"),
        ("2024-01-15 08:00:07", "lap_times.csv",     "raw",     4_280_000,  "SUCCESS"),
        ("2024-01-15 08:00:12", "results.csv",       "raw",       520_000,  "SUCCESS"),
        ("2024-01-15 08:00:18", "qualifying.csv",    "raw",        85_000,  "SUCCESS"),
        ("2024-01-15 08:00:22", "pit_stops.csv",     "raw",       310_000,  "SUCCESS"),
        ("2024-01-15 08:00:25", "circuits.csv",      "raw",         1_800,  "SUCCESS"),
        ("2024-01-15 08:01:00", "race_spark_clean",  "staged",  4_800_000,  "SUCCESS"),
        ("2024-01-15 08:03:30", "dim_drivers",       "warehouse",   2_340,  "SUCCESS"),
        ("2024-01-15 08:03:45", "dim_constructors",  "warehouse",     420,  "SUCCESS"),
        ("2024-01-15 08:04:10", "fact_race_results", "warehouse", 520_000,  "SUCCESS"),
        ("2024-01-15 08:05:00", "fact_lap_times",    "warehouse",4_280_000, "SUCCESS"),
        ("2024-01-15 08:06:15", "agg_season_points", "mart",       28_000,  "SUCCESS"),
        ("2024-01-15 08:06:30", "agg_driver_trends", "mart",       12_000,  "SUCCESS"),
    ]
    log_df = pd.DataFrame(ingestion_log, columns=["timestamp", "table", "layer", "rows", "status"])

    return races_df, standings, constructors, laps_df, log_df


races_df, standings_df, constructors_df, laps_df, log_df = generate_f1_data()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem;'>
        <div style='font-family: Orbitron, monospace; font-size: 1.3rem; color: #E10600; font-weight: 900; letter-spacing: 0.1em;'>F1 ANALYTICS</div>
        <div style='font-family: JetBrains Mono, monospace; font-size: 0.65rem; color: #6B6B82; letter-spacing: 0.15em; margin-top: 0.2rem;'>PLATFORM v2.4.1</div>
        <hr style='border-color:#2A2A38; margin: 0.75rem 0;'>
    </div>
    """, unsafe_allow_html=True)

    page = st.selectbox(
        "NAVIGATION",
        [
            "🏠  Platform Overview",
            "🔌  Ingestion Layer",
            "⚡  Spark Transforms",
            "❄️  Warehouse Model",
            "📊  BI Dashboards",
            "🏆  Driver Analytics",
            "🔧  Constructor Intel",
            "⏱️  Lap Performance"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    season_filter = st.selectbox("Season", list(range(2024, 2009, -1)), index=0)
    driver_filter = st.multiselect(
        "Drivers",
        ["HAM", "VER", "SCH", "SEN", "VET", "ALO", "PRO", "RAI", "NOR", "LEC"],
        default=["HAM", "VER", "VET"]
    )

    st.divider()
    st.markdown("""
    <div style='font-family: JetBrains Mono, monospace; font-size: 0.65rem; color: #6B6B82; line-height: 1.8;'>
    <span style='color:#00C87A'>●</span> Ingestion: LIVE<br>
    <span style='color:#00C87A'>●</span> Spark Cluster: 8 nodes<br>
    <span style='color:#00C87A'>●</span> Snowflake: Connected<br>
    <span style='color:#FFC906'>●</span> dbt: Scheduled 06:00<br>
    <span style='color:#3A8DFF'>●</span> Looker: Synced 2h ago
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style='font-family: JetBrains Mono, monospace; font-size: 0.6rem; color: #44445A; text-align:center; line-height:1.6;'>
    Built for portfolio demonstration<br>
    Ergast F1 Dataset · 1950–2024
    </div>
    """, unsafe_allow_html=True)

# ─── PLOTLY THEME ─────────────────────────────────────────────────────────────
LAYOUT = dict(
    paper_bgcolor="#111118",
    plot_bgcolor="#0A0A0F",
    font=dict(family="JetBrains Mono, monospace", color="#9090AA", size=11),
    xaxis=dict(gridcolor="#1E1E2E", linecolor="#2A2A38", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#1E1E2E", linecolor="#2A2A38", tickfont=dict(size=10)),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(
        bgcolor="#111118",
        bordercolor="#2A2A38",
        borderwidth=1,
        font=dict(size=10)
    ),
)
COLORS = [
    "#E10600", "#FFC906", "#3A8DFF", "#00C87A", "#FF6B6B",
    "#A78BFA", "#F97316", "#22D3EE", "#EC4899", "#84CC16"
]

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PLATFORM OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "🏠  Platform Overview":
    st.markdown("""
    <div style='padding: 1.5rem 0 0.5rem;'>
      <div style='font-family: Orbitron, monospace; font-size: 2rem; font-weight: 900; color: #E10600; letter-spacing: 0.05em;'>
        F1 ANALYTICS PLATFORM
      </div>
      <div style='font-family: JetBrains Mono, monospace; font-size: 0.8rem; color: #6B6B82; margin-top: 0.3rem; letter-spacing: 0.08em;'>
        END-TO-END DATA ENGINEERING · INGESTION → SPARK → SNOWFLAKE → BI
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: safe_metric("Race Records", "520K")
    with c2: safe_metric("Lap Times", "4.28M")
    with c3: safe_metric("Seasons", "75")
    with c4: safe_metric("Drivers", "857")
    with c5: safe_metric("Circuits", "77")
    with c6: safe_metric("Pipeline SLA", "99.7%")

    st.markdown("#### 🔁 Architecture Pipeline")

    stages = [
        ("📥 SOURCE",        ["Ergast API", "CSV Exports", "Live Timing", "Telemetry Feed"], "#6B6B82"),
        ("🐍 INGESTION",     ["Python Scripts", "Batch Loader", "Schema Validation", "Raw Landing"], "#3A8DFF"),
        ("⚡ TRANSFORM",     ["Spark Jobs", "Databricks", "Deduplication", "Type Casting"], "#E25A1C"),
        ("❄️ WAREHOUSE",    ["Snowflake", "dim_drivers", "fact_results", "Marts"], "#3A8DFF"),
        ("📊 BI / REPORTS", ["Looker Studio", "dbt Models", "Live Dashboards", "Exports"], "#00C87A"),
    ]
    arch_cols = st.columns(len(stages))
    for col_obj, (label, items, color) in zip(arch_cols, stages):
        with col_obj:
            st.markdown(f"**{label}**")
            for item in items:
                st.caption(f"· {item}")

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("---")
        st.markdown("**Table Inventory — Warehouse Layer**")
        tables = pd.DataFrame([
            {"Table": "fact_race_results",   "Layer": "Fact",      "Rows": "520,000",   "Grain": "race + driver",      "Updated": "2h ago"},
            {"Table": "fact_lap_times",      "Layer": "Fact",      "Rows": "4,280,000", "Grain": "race + driver + lap","Updated": "2h ago"},
            {"Table": "fact_qualifying",     "Layer": "Fact",      "Rows": "85,000",    "Grain": "race + driver",      "Updated": "2h ago"},
            {"Table": "fact_pit_stops",      "Layer": "Fact",      "Rows": "310,000",   "Grain": "race + driver + stop","Updated": "2h ago"},
            {"Table": "dim_drivers",         "Layer": "Dimension", "Rows": "857",       "Grain": "driver_id",          "Updated": "1d ago"},
            {"Table": "dim_constructors",    "Layer": "Dimension", "Rows": "210",       "Grain": "constructor_id",     "Updated": "1d ago"},
            {"Table": "dim_circuits",        "Layer": "Dimension", "Rows": "77",        "Grain": "circuit_id",         "Updated": "1d ago"},
            {"Table": "agg_season_points",   "Layer": "Mart",      "Rows": "28,000",    "Grain": "season + driver",    "Updated": "2h ago"},
            {"Table": "agg_constructor_pts", "Layer": "Mart",      "Rows": "8,400",     "Grain": "season + team",      "Updated": "2h ago"},
        ])
        st.dataframe(
            tables,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Layer": st.column_config.TextColumn(width=90),
                "Rows": st.column_config.TextColumn(width=90),
            }
        )

    with col2:
        st.markdown("**Technology Stack**")
        stack_items = [
            ("🐍 Python 3.11",      "Ingestion & orchestration"),
            ("⚡ Apache Spark 3.4", "Distributed transforms"),
            ("🧱 Databricks",       "Cluster compute platform"),
            ("❄️ Snowflake",        "Cloud data warehouse"),
            ("🔧 dbt Core",         "SQL transformations & docs"),
            ("📊 Looker Studio",    "BI dashboards & delivery"),
            ("🗄️ Delta Lake",       "ACID storage format"),
            ("🌀 Airflow",          "Pipeline orchestration"),
        ]
        stack_df = pd.DataFrame(stack_items, columns=["Technology", "Role"])
        st.dataframe(stack_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**Recent Pipeline Executions**")
    runs = pd.DataFrame([
        {"Run ID": "dag_f1_2024_r0041", "Triggered": "2024-01-15 08:00", "Duration": "6m 32s", "Records": "5.4M", "Status": "✅ SUCCESS"},
        {"Run ID": "dag_f1_2024_r0040", "Triggered": "2024-01-14 08:00", "Duration": "6m 18s", "Records": "5.4M", "Status": "✅ SUCCESS"},
        {"Run ID": "dag_f1_2024_r0039", "Triggered": "2024-01-13 08:00", "Duration": "8m 12s", "Records": "5.4M", "Status": "⚠️ WARN"},
        {"Run ID": "dag_f1_2024_r0038", "Triggered": "2024-01-12 08:00", "Duration": "6m 45s", "Records": "5.4M", "Status": "✅ SUCCESS"},
        {"Run ID": "dag_f1_2024_r0037", "Triggered": "2024-01-11 08:00", "Duration": "—",      "Records": "—",   "Status": "❌ FAILED"},
    ])
    st.dataframe(runs, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: INGESTION LAYER
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔌  Ingestion Layer":
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 1.5rem; font-weight:700; color: #3A8DFF; margin-bottom: 0.25rem;'>
    INGESTION LAYER
    </div>
    <div style='font-family: JetBrains Mono, monospace; font-size: 0.72rem; color: #6B6B82; margin-bottom: 1rem;'>
    Raw source ingest · Schema validation · Landing zone writes
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: safe_metric("Source Tables", "8")
    with c2: safe_metric("Total Rows Loaded", "5.44M")
    with c3: safe_metric("Avg Load Time", "1.8s")
    with c4: safe_metric("Validation Pass", "99.3%")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("---")
        st.markdown("**Live Pipeline Run**")
        if st.button("▶  RUN INGESTION PIPELINE"):
            steps = [
                ("Connecting to Ergast API...", 0.20),
                ("Downloading races.csv (150K rows)...", 0.20),
                ("Downloading drivers.csv (2,340 rows)...", 0.15),
                ("Downloading lap_times.csv (4.28M rows)...", 0.25),
                ("Downloading results.csv (520K rows)...", 0.20),
                ("Schema validation — races.csv...", 0.15),
                ("Schema validation — lap_times.csv...", 0.15),
                ("Writing to raw landing zone (S3)...", 0.20),
                ("Registering metadata in catalog...", 0.15),
                ("Triggering downstream Spark job...", 0.15),
            ]
            log_box = st.empty()
            prog = st.progress(0)
            logs = []

            for i, (msg, delay) in enumerate(steps):
                time.sleep(delay)
                ts = datetime.now().strftime("%H:%M:%S.%f")[:12]
                logs.append(
                    f'<span class="log-info">[{ts}]</span> '
                    f'<span class="log-line">{msg}</span>'
                )
                suffix = ""
                if i == len(steps) - 1:
                    suffix = '<br><span class="log-ok">✓ Pipeline complete — 5.44M rows ingested in 6m 32s</span>'

                log_html = (
                    "<div style='background:#0A0A0F;border:1px solid #2A2A38;"
                    "border-radius:4px;padding:0.75rem 1rem;height:220px;overflow-y:auto;'>"
                    + "<br>".join(logs)
                    + suffix
                    + "</div>"
                )
                log_box.markdown(log_html, unsafe_allow_html=True)
                prog.progress((i + 1) / len(steps))

            st.success("✅ Ingestion complete — 5,440,000 rows processed")

    with col2:
        st.markdown("---")
        st.markdown("**Ingestion Log — Latest Run**")
        st.dataframe(
            log_df.rename(columns={
                "timestamp": "Timestamp",
                "table": "Table",
                "layer": "Layer",
                "rows": "Rows",
                "status": "Status"
            }),
            use_container_width=True,
            hide_index=True,
            column_config={"Rows": st.column_config.NumberColumn(format="%d")}
        )

    st.markdown("**Source Schema — fact_race_results**")
    schema = [
        ("race_id",          "INTEGER",     "PK — Unique race identifier"),
        ("season",           "SMALLINT",    "Championship year"),
        ("round",            "TINYINT",     "Race number in season"),
        ("circuit_id",       "INTEGER",     "FK → dim_circuits"),
        ("driver_id",        "INTEGER",     "FK → dim_drivers"),
        ("constructor_id",   "INTEGER",     "FK → dim_constructors"),
        ("grid_position",    "TINYINT",     "Starting grid slot"),
        ("finish_position",  "TINYINT",     "Final race position"),
        ("points",           "FLOAT",       "Championship points awarded"),
        ("laps_completed",   "TINYINT",     "Laps before finish/DNF"),
        ("status",           "VARCHAR(32)", "Finished / DNF / +N Lap"),
        ("fastest_lap_time", "FLOAT",       "Fastest lap in seconds"),
    ]
    schema_df = pd.DataFrame(schema, columns=["Column", "Type", "Description"])
    st.dataframe(schema_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("**Data Quality Checks**")
    dq = pd.DataFrame([
        {"Check": "NULL driver_id in race_results",    "Expectation": "= 0",   "Actual": "0",     "Pass": "✅"},
        {"Check": "position range [1,20]",             "Expectation": "100%",  "Actual": "100%",  "Pass": "✅"},
        {"Check": "points match position mapping",     "Expectation": "100%",  "Actual": "99.8%", "Pass": "⚠️"},
        {"Check": "lap_time > 60s (physical minimum)", "Expectation": "100%",  "Actual": "100%",  "Pass": "✅"},
        {"Check": "Duplicate race+driver keys",        "Expectation": "= 0",   "Actual": "0",     "Pass": "✅"},
        {"Check": "season range [1950, 2024]",         "Expectation": "100%",  "Actual": "100%",  "Pass": "✅"},
        {"Check": "FK integrity — constructor_id",     "Expectation": "100%",  "Actual": "97.2%", "Pass": "❌"},
    ])
    st.dataframe(dq, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: SPARK TRANSFORMS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚡  Spark Transforms":
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 1.5rem; font-weight:700; color: #E25A1C; margin-bottom: 0.25rem;'>
    SPARK / DATABRICKS LAYER
    </div>
    <div style='font-family: JetBrains Mono, monospace; font-size: 0.72rem; color: #6B6B82; margin-bottom: 1rem;'>
    Distributed transformation · Delta Lake writes · Schema enforcement
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: safe_metric("Cluster Nodes", "8")
    with c2: safe_metric("vCores Total", "64")
    with c3: safe_metric("Avg Job Duration", "4m 12s")
    with c4: safe_metric("Delta Tables", "12")

    tab1, tab2, tab3 = st.tabs(["JOB EXECUTION", "TRANSFORMATION CODE", "CLUSTER METRICS"])

    with tab1:
        st.markdown("---")
        st.markdown("**Spark Job DAG**")
        jobs = [
            ("Stage 1", "raw_ingest_races",         "COMPLETE", "0:42", "150K",  8),
            ("Stage 2", "raw_ingest_lap_times",     "COMPLETE", "1:18", "4.28M", 24),
            ("Stage 3", "deduplicate_results",      "COMPLETE", "0:28", "518K",  8),
            ("Stage 4", "normalize_lap_times",      "COMPLETE", "0:55", "4.28M", 32),
            ("Stage 5", "join_driver_constructor",  "COMPLETE", "0:38", "520K", 16),
            ("Stage 6", "compute_season_agg",       "COMPLETE", "0:22", "28K",   8),
            ("Stage 7", "write_delta_fact_results", "COMPLETE", "0:31", "520K",  8),
            ("Stage 8", "write_delta_lap_times",    "COMPLETE", "1:02", "4.28M", 32),
        ]
        jobs_df = pd.DataFrame(jobs, columns=["Stage", "Job Name", "Status", "Duration", "Records", "Tasks"])
        st.dataframe(jobs_df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("---")
        st.markdown("**Transformation Logic — Python + PySpark**")
        code_snippets = {
            "01_ingest_raw.py": """from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, trim, upper

spark = SparkSession.builder \\
    .appName("f1_ingestion") \\
    .config("spark.databricks.delta.schema.autoMerge.enabled", "true") \\
    .getOrCreate()

RAW_PATH   = "s3://f1-datalake/raw/"
STAGE_PATH = "s3://f1-datalake/staged/"

def ingest_races(source: str) -> None:
    df = spark.read.option("header", True).csv(f"{RAW_PATH}{source}")

    df_clean = (df
        .withColumn("season", col("year").cast("integer"))
        .withColumn("round", col("round").cast("integer"))
        .withColumn("race_date", to_date(col("date"), "yyyy-MM-dd"))
        .withColumn("name", trim(col("name")))
        .dropDuplicates(["raceId"])
        .filter(col("season").between(1950, 2024))
    )

    df_clean.write.format("delta") \\
        .mode("overwrite") \\
        .option("overwriteSchema", "true") \\
        .save(f"{STAGE_PATH}races/")

    print(f"Races ingested: {df_clean.count():,} rows")

ingest_races("races.csv")
""",
            "02_transform_results.py": """from pyspark.sql.functions import (
    col, when, coalesce, lit, rank, dense_rank
)
from pyspark.sql.window import Window

POINTS_MAP = {1:25, 2:18, 3:15, 4:12, 5:10,
              6:8,  7:6,  8:4,  9:2,  10:1}

def transform_results(spark) -> None:
    results = spark.read.format("delta").load(f"{STAGE_PATH}results/")
    drivers = spark.read.format("delta").load(f"{STAGE_PATH}drivers/")

    df = results.join(drivers, on="driverId", how="left")

    point_expr = when(col("position").isin(list(POINTS_MAP)), 
                      col("points")).otherwise(lit(0))

    season_win = Window.partitionBy("season") \\
                       .orderBy(col("total_points").desc())

    df_enriched = (df
        .withColumn("clean_points", point_expr)
        .groupBy("season", "driverId", "code", "constructorId")
        .agg({"clean_points": "sum", "position": "count"})
        .withColumnRenamed("sum(clean_points)", "total_points")
        .withColumn("season_rank", rank().over(season_win))
    )

    df_enriched.write.format("delta") \\
        .mode("overwrite") \\
        .partitionBy("season") \\
        .save(f"{STAGE_PATH}agg_season_points/")
""",
            "03_warehouse_load.py": """import os
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

def load_to_snowflake(df, table: str, schema: str = "ANALYTICS") -> None:
    conn = snowflake.connector.connect(
        account   = os.environ["SNOWFLAKE_ACCOUNT"],
        user      = os.environ["SNOWFLAKE_USER"],
        password  = os.environ["SNOWFLAKE_PASSWORD"],
        warehouse = "F1_WH",
        database  = "F1_ANALYTICS",
        schema    = schema,
    )

    success, chunks, rows, _ = write_pandas(
        conn, df, table,
        overwrite=False,
        auto_create_table=True,
        use_logical_type=True,
    )

    print(f"Loaded {rows:,} rows into {schema}.{table}")
    conn.close()
"""
        }
        sel = st.selectbox("Script", list(code_snippets.keys()))
        st.code(code_snippets[sel], language="python")

    with tab3:
        st.markdown("---")
        st.markdown("**Cluster Resource Utilisation**")
        mins = list(range(0, 8))
        cpu = [12, 45, 88, 92, 85, 78, 62, 15]
        mem = [30, 55, 70, 72, 68, 65, 60, 32]
        net = [5, 40, 80, 85, 70, 60, 45, 8]

        fig = go.Figure()
        for name, vals, color in [
            ("CPU %", cpu, "#E10600"),
            ("Memory %", mem, "#3A8DFF"),
            ("Network MB/s (scaled)", net, "#FFC906"),
        ]:
            fig.add_trace(go.Scatter(
                x=mins,
                y=vals,
                name=name,
                line=dict(color=color, width=2),
                fill="tozeroy",
                fillcolor=hex_to_rgba(color, 0.18)
            ))

        fig.update_layout(
            **LAYOUT,
            title="8-node cluster · last job run",
            height=260,
            xaxis_title="minutes",
            yaxis_title="%"
        )
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: WAREHOUSE MODEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "❄️  Warehouse Model":
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 1.5rem; font-weight:700; color: #3A8DFF; margin-bottom: 0.25rem;'>
    SNOWFLAKE WAREHOUSE MODEL
    </div>
    <div style='font-family: JetBrains Mono, monospace; font-size: 0.72rem; color: #6B6B82; margin-bottom: 1rem;'>
    Kimball star schema · dbt-managed · Incremental refresh
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: safe_metric("Fact Tables", "4")
    with c2: safe_metric("Dimension Tables", "5")
    with c3: safe_metric("Mart Tables", "8")
    with c4: safe_metric("dbt Models", "31")

    tab1, tab2 = st.tabs(["SCHEMA DIAGRAM", "DBT MODELS"])

    with tab1:
        st.markdown("**Star Schema — F1_ANALYTICS Database**")

        d1, d2, d3, d4 = st.columns(4)
        dim_tables = [
            ("DIM_CIRCUITS",     ["🔑 circuit_id", "circuit_name", "country", "location", "lat / lng"]),
            ("DIM_DRIVERS",      ["🔑 driver_id", "code (3-char)", "forename / surname", "nationality", "dob"]),
            ("DIM_SEASONS",      ["🔑 season_year", "total_races", "rule_era", "engine_era", "url"]),
            ("DIM_CONSTRUCTORS", ["🔑 constructor_id", "name", "nationality", "first_entry_year", "championships_won"]),
        ]
        for col_obj, (tname, tcols) in zip([d1, d2, d3, d4], dim_tables):
            with col_obj:
                st.markdown(f"**{tname}**")
                for c in tcols:
                    st.caption(c)

        st.markdown("---")
        f1, f2 = st.columns([2, 1])
        with f1:
            st.markdown("**🏁 FACT_RACE_RESULTS** *(central fact table)*")
            fact_cols = [
                "🔑 result_id", "🔗 race_id", "🔗 driver_id", "🔗 constructor_id", "🔗 circuit_id",
                "grid_position", "finish_position", "points", "laps_completed", "status",
                "fastest_lap_ms", "pit_stops", "time_ms"
            ]
            cols_a, cols_b = st.columns(2)
            for i, c in enumerate(fact_cols):
                (cols_a if i % 2 == 0 else cols_b).caption(c)

        with f2:
            st.markdown("**📦 FACT_LAP_TIMES**")
            for c in [
                "🔑 lap_id", "🔗 race_id", "🔗 driver_id", "lap_number",
                "lap_time_ms", "sector1_ms", "sector2_ms", "sector3_ms"
            ]:
                st.caption(c)

        st.markdown("---")
        st.markdown("**📊 Data Marts**")
        m1, m2, m3, m4 = st.columns(4)
        marts = [
            ("MART_SEASON_STANDINGS",  ["season", "driver", "total_pts", "season_rank", "wins", "podiums"]),
            ("MART_DRIVER_CAREER",     ["driver", "seasons", "races", "wins", "podiums", "championships"]),
            ("MART_LAP_PERFORMANCE",   ["driver", "race", "avg_lap_ms", "fastest_lap", "consistency_pct"]),
            ("MART_CONSTRUCTOR_TREND", ["constructor", "season", "pts", "rank", "yoy_delta"]),
        ]
        for col_obj, (mname, mcols) in zip([m1, m2, m3, m4], marts):
            with col_obj:
                st.markdown(f"**{mname}**")
                for c in mcols:
                    st.caption(f"· {c}")

    with tab2:
        st.markdown("---")
        st.markdown("**dbt Model SQL — mart_season_standings**")
        st.code("""-- models/marts/mart_season_standings.sql
-- @description: Season-level driver standings with cumulative metrics
-- @materialization: incremental (unique_key = season || '_' || driver_id)
-- @schedule: After fact_race_results refresh

{{ config(
    materialized  = 'incremental',
    unique_key    = ['season', 'driver_id'],
    on_schema_change = 'sync_all_columns',
    tags          = ['mart', 'standings', 'daily']
) }}

WITH base AS (
    SELECT
        r.season,
        r.driver_id,
        d.code                              AS driver_code,
        d.forename || ' ' || d.surname      AS driver_name,
        r.constructor_id,
        c.name                              AS constructor_name,
        SUM(r.points)                       AS total_points,
        COUNT(*)                            AS total_races,
        COUNTIF(r.finish_position = 1)      AS wins,
        COUNTIF(r.finish_position <= 3)     AS podiums,
        COUNTIF(r.finish_position <= 10)    AS points_finishes,
        COUNTIF(r.grid_position = 1)        AS pole_positions,
        MIN(r.fastest_lap_ms) / 1000.0      AS best_lap_sec,
        AVG(r.finish_position)              AS avg_finish_pos
    FROM {{ ref('fact_race_results') }}     r
    JOIN {{ ref('dim_drivers') }}           d USING (driver_id)
    JOIN {{ ref('dim_constructors') }}      c USING (constructor_id)
    {% if is_incremental() %}
        WHERE r.season >= (SELECT MAX(season) - 1 FROM {{ this }})
    {% endif %}
    GROUP BY 1,2,3,4,5,6
),

ranked AS (
    SELECT *,
        RANK() OVER (PARTITION BY season ORDER BY total_points DESC) AS season_rank,
        LAG(total_points) OVER (PARTITION BY driver_id ORDER BY season) AS prev_season_pts,
        total_points - LAG(total_points) OVER (
            PARTITION BY driver_id ORDER BY season
        )                                                               AS pts_yoy_delta
    FROM base
)

SELECT * FROM ranked
ORDER BY season DESC, season_rank ASC
""", language="sql")

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: BI DASHBOARDS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📊  BI Dashboards":
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 1.5rem; font-weight:700; color: #00C87A; margin-bottom: 0.25rem;'>
    BI DASHBOARD LAYER
    </div>
    <div style='font-family: JetBrains Mono, monospace; font-size: 0.72rem; color: #6B6B82; margin-bottom: 1rem;'>
    Looker Studio · Live Snowflake queries · Stakeholder delivery
    </div>
    """, unsafe_allow_html=True)

    season_data = standings_df[standings_df["season"] == season_filter].sort_values("rank")
    top10 = season_data.head(10)

    c1, c2, c3, c4 = st.columns(4)
    if len(top10):
        champ = top10.iloc[0]
        with c1: safe_metric("Champion", champ["driver_code"])
        with c2: safe_metric("Champion Points", int(champ["points"]))
        with c3: safe_metric("Drivers in Season", len(season_data))
        with c4: safe_metric("Constructors", season_data["team"].nunique())

    col1, col2 = st.columns([3, 2])

    with col1:
        fig = go.Figure(go.Bar(
            x=top10["driver_code"],
            y=top10["points"],
            marker_color=[COLORS[i % len(COLORS)] for i in range(len(top10))],
            text=top10["points"],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color="#E8E8F0")
        ))
        fig.update_layout(
            **LAYOUT,
            title=f"{season_filter} Championship — Top 10 Drivers",
            height=300,
            showlegend=False,
            xaxis_title="Driver",
            yaxis_title="Points"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        team_pts = season_data.groupby("team")["points"].sum().sort_values(ascending=False).head(6)
        fig2 = go.Figure(go.Pie(
            labels=team_pts.index,
            values=team_pts.values,
            hole=0.55,
            marker=dict(colors=COLORS[:len(team_pts)]),
            textfont=dict(family="JetBrains Mono", size=9),
        ))
        fig2.update_layout(
            **LAYOUT,
            title=f"{season_filter} Constructor Share",
            height=300,
            showlegend=True
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("**Championship Points — Multi-Season Trend**")
    trend_df = standings_df[standings_df["driver_code"].isin(driver_filter)]
    if not driver_filter:
        st.warning("Select at least one driver to view multi-season trends.")
    else:
        fig3 = go.Figure()
        for i, d in enumerate(driver_filter):
            dd = trend_df[trend_df["driver_code"] == d].sort_values("season")
            if len(dd):
                fig3.add_trace(go.Scatter(
                    x=dd["season"],
                    y=dd["points"],
                    name=d,
                    mode="lines+markers",
                    line=dict(color=COLORS[i % len(COLORS)], width=2),
                    marker=dict(size=5)
                ))
        fig3.update_layout(
            **LAYOUT,
            title="Season Points Trajectory",
            height=300,
            xaxis_title="Season",
            yaxis_title="Points"
        )
        st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DRIVER ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏆  Driver Analytics":
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 1.5rem; font-weight:700; color: #FFC906; margin-bottom: 0.25rem;'>
    DRIVER ANALYTICS
    </div>
    <div style='font-family: JetBrains Mono, monospace; font-size: 0.72rem; color: #6B6B82; margin-bottom: 1rem;'>
    Career statistics · Performance benchmarking · Historical comparison
    </div>
    """, unsafe_allow_html=True)

    career = races_df.groupby(["driver_code", "driver_name", "team"]).agg(
        races=("position", "count"),
        wins=("position", lambda x: (x == 1).sum()),
        podiums=("position", lambda x: (x <= 3).sum()),
        points=("points", "sum"),
        avg_pos=("position", "mean"),
    ).reset_index().sort_values("points", ascending=False)

    career["avg_pos"] = career["avg_pos"].round(1)
    career["win_rate"] = (career["wins"] / career["races"] * 100).round(1)
    career.columns = ["Code", "Driver", "Last Team", "Races", "Wins", "Podiums", "Points", "Avg Pos", "Win %"]

    st.markdown("---")
    st.markdown("**All-Time Career Rankings**")
    st.dataframe(
        career,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Points": st.column_config.ProgressColumn(
                format="%d",
                min_value=0,
                max_value=int(career["Points"].max())
            ),
            "Win %": st.column_config.NumberColumn(format="%.1f%%"),
        }
    )

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(go.Bar(
            x=career["Code"][:8],
            y=career["Wins"][:8],
            marker_color=COLORS[:8],
            text=career["Wins"][:8],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color="#E8E8F0")
        ))
        fig.update_layout(**LAYOUT, title="All-Time Race Wins (top 8)", height=280, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure(go.Bar(
            x=career["Code"][:8],
            y=career["Podiums"][:8],
            marker_color=[hex_to_rgba(c, 0.65) for c in COLORS[:8]],
            text=career["Podiums"][:8],
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color="#E8E8F0")
        ))
        fig2.update_layout(**LAYOUT, title="All-Time Podiums (top 8)", height=280, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("**Performance Radar — Top 3 Drivers**")
    metrics = ["Wins", "Podiums", "Points", "Races", "Win %"]
    fig3 = go.Figure()

    top3 = career.head(3).reset_index(drop=True)
    for i, row in top3.iterrows():
        vals = [
            row["Wins"] / career["Wins"].max() * 100 if career["Wins"].max() else 0,
            row["Podiums"] / career["Podiums"].max() * 100 if career["Podiums"].max() else 0,
            row["Points"] / career["Points"].max() * 100 if career["Points"].max() else 0,
            row["Races"] / career["Races"].max() * 100 if career["Races"].max() else 0,
            row["Win %"] / career["Win %"].max() * 100 if career["Win %"].max() else 0,
        ]
        vals += [vals[0]]

        fig3.add_trace(go.Scatterpolar(
            r=vals,
            theta=metrics + [metrics[0]],
            name=row["Code"],
            fill="toself",
            line=dict(color=COLORS[i % len(COLORS)], width=2),
            fillcolor=hex_to_rgba(COLORS[i % len(COLORS)], 0.22),
            opacity=0.7,
        ))

    fig3.update_layout(
        **LAYOUT,
        polar=dict(
            bgcolor="#0A0A0F",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1E1E2E", tickfont=dict(size=9)),
            angularaxis=dict(gridcolor="#1E1E2E", tickfont=dict(size=9, color="#9090AA"))
        ),
        title="Normalised Performance Index",
        height=350
    )
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CONSTRUCTOR INTEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔧  Constructor Intel":
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 1.5rem; font-weight:700; color: #A78BFA; margin-bottom: 0.25rem;'>
    CONSTRUCTOR INTELLIGENCE
    </div>
    <div style='font-family: JetBrains Mono, monospace; font-size: 0.72rem; color: #6B6B82; margin-bottom: 1rem;'>
    Team performance · Era analysis · Competitive trends
    </div>
    """, unsafe_allow_html=True)

    con_sel = constructors_df[constructors_df["season"] == season_filter].sort_values("points", ascending=False)

    c1, c2, c3, c4 = st.columns(4)
    if len(con_sel):
        points_gap = int(con_sel.iloc[0]["points"] - con_sel.iloc[1]["points"]) if len(con_sel) > 1 else 0
        with c1: safe_metric("Champions", con_sel.iloc[0]["team"])
        with c2: safe_metric("Winning Points", int(con_sel.iloc[0]["points"]))
        with c3: safe_metric("Teams", len(con_sel))
        with c4: safe_metric("Points Gap", points_gap if len(con_sel) > 1 else "—")

    col1, col2 = st.columns([2, 3])
    with col1:
        fig = go.Figure(go.Bar(
            x=con_sel["points"].head(8),
            y=con_sel["team"].head(8),
            orientation="h",
            marker_color=COLORS[:8],
            text=con_sel["points"].head(8),
            textposition="outside",
            textfont=dict(family="JetBrains Mono", size=10, color="#E8E8F0"),
        ))
        fig.update_layout(
            **LAYOUT,
            title=f"{season_filter} Constructor Standings",
            height=320,
            showlegend=False,
            xaxis_title="Points",
            yaxis=dict(
                autorange="reversed",
                gridcolor="#1E1E2E",
                linecolor="#2A2A38",
                tickfont=dict(size=10)
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        top_teams = constructors_df.groupby("team")["points"].sum().nlargest(5).index.tolist()
        fig2 = go.Figure()
        for i, team in enumerate(top_teams):
            td = constructors_df[constructors_df["team"] == team].sort_values("season")
            fig2.add_trace(go.Scatter(
                x=td["season"],
                y=td["points"],
                name=team,
                mode="lines+markers",
                line=dict(color=COLORS[i % len(COLORS)], width=2),
                marker=dict(size=4)
            ))
        fig2.update_layout(
            **LAYOUT,
            title="Constructor Points — 2010–2024",
            height=320,
            xaxis_title="Season",
            yaxis_title="Points"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("**Season Rank Heatmap — Top 5 Teams**")
    pivot = constructors_df[constructors_df["team"].isin(top_teams)].pivot_table(
        index="team", columns="season", values="points", aggfunc="sum"
    ).fillna(0)

    fig3 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[str(c) for c in pivot.columns],
        y=list(pivot.index),
        colorscale=[[0, "#0A0A0F"], [0.5, "#E10600"], [1, "#FFC906"]],
        text=pivot.values.astype(int),
        texttemplate="%{text}",
        textfont=dict(family="JetBrains Mono", size=9),
    ))
    fig3.update_layout(**LAYOUT, title="Points by Team & Season", height=260)
    st.plotly_chart(fig3, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE: LAP PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⏱️  Lap Performance":
    st.markdown("""
    <div style='font-family: Orbitron, monospace; font-size: 1.5rem; font-weight:700; color: #22D3EE; margin-bottom: 0.25rem;'>
    LAP TIME PERFORMANCE
    </div>
    <div style='font-family: JetBrains Mono, monospace; font-size: 0.72rem; color: #6B6B82; margin-bottom: 1rem;'>
    Sector analysis · Fuel-adjusted pace · Consistency metrics
    </div>
    """, unsafe_allow_html=True)

    sel_season = st.selectbox("Select Season", [2024, 2023, 2022, 2021, 2020])
    lap_season = laps_df[laps_df["season"] == sel_season]

    c1, c2, c3, c4 = st.columns(4)
    with c1: safe_metric("Fastest Lap", f"{lap_season['lap_time'].min():.3f}s")
    with c2: safe_metric("Avg Lap", f"{lap_season['lap_time'].mean():.3f}s")
    with c3: safe_metric("Laps Sampled", f"{len(lap_season):,}")
    with c4: safe_metric("Drivers", lap_season["driver_code"].nunique())

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        top_drivers = lap_season["driver_code"].unique()[:5]
        for i, d in enumerate(top_drivers):
            dd = lap_season[lap_season["driver_code"] == d].sort_values("lap")
            fig.add_trace(go.Scatter(
                x=dd["lap"],
                y=dd["lap_time"],
                name=d,
                mode="lines",
                line=dict(color=COLORS[i % len(COLORS)], width=1.5)
            ))
        fig.update_layout(
            **LAYOUT,
            title="Lap Time Progression",
            height=290,
            xaxis_title="Lap",
            yaxis_title="Time (s)"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        dist_data = []
        for i, d in enumerate(top_drivers):
            dd = lap_season[lap_season["driver_code"] == d]["lap_time"]
            dist_data.append(go.Violin(
                y=dd,
                name=d,
                line=dict(color=COLORS[i % len(COLORS)], width=1.5),
                fillcolor=hex_to_rgba(COLORS[i % len(COLORS)], 0.22),
                box_visible=True,
                meanline_visible=True
            ))
        fig2 = go.Figure(dist_data)
        fig2.update_layout(
            **LAYOUT,
            title="Lap Time Distribution",
            height=290,
            showlegend=False,
            yaxis_title="Time (s)"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.markdown("**Average Sector Times by Driver**")
    sector_agg = lap_season.groupby("driver_code")[["sector1", "sector2", "sector3"]].mean().reset_index()

    fig3 = go.Figure()
    for j, sec in enumerate(["sector1", "sector2", "sector3"]):
        fig3.add_trace(go.Bar(
            x=sector_agg["driver_code"],
            y=sector_agg[sec],
            name=f"S{j + 1}",
            marker_color=COLORS[j % len(COLORS)]
        ))
    fig3.update_layout(
        **LAYOUT,
        barmode="stack",
        title="Sector Time Composition",
        height=280,
        xaxis_title="Driver",
        yaxis_title="Seconds"
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.markdown("**Lap-Time Consistency Index (lower = more consistent)**")
    consistency = lap_season.groupby("driver_code")["lap_time"].std().reset_index()
    consistency.columns = ["Driver", "Std Dev (s)"]
    consistency = consistency.sort_values("Std Dev (s)")

    fig4 = go.Figure(go.Bar(
        x=consistency["Driver"],
        y=consistency["Std Dev (s)"],
        marker_color=[COLORS[i % len(COLORS)] for i in range(len(consistency))],
        text=consistency["Std Dev (s)"].round(3),
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=10, color="#E8E8F0")
    ))
    fig4.update_layout(
        **LAYOUT,
        title="Lap Time Std Deviation",
        height=250,
        showlegend=False,
        xaxis_title="Driver",
        yaxis_title="Std Dev (s)"
    )
    st.plotly_chart(fig4, use_container_width=True)
