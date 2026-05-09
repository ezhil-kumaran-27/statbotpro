"""
app.py — StatBot Pro
Professional light-theme Streamlit dashboard.
Autonomous CSV Data Analyst powered by Google Gemini.
API key loaded securely from .env file.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Load API key from .env file
load_dotenv()

from agent import run_agent, AgentResult
from utils import load_csv, dataframe_summary

# ── Must be FIRST Streamlit call ──────────────────────────────────────────────
st.set_page_config(
    page_title="StatBot Pro — CSV Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL LIGHT THEME CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap');

/* ── Root Variables ── */
:root {
    --white:       #ffffff;
    --bg:          #f8fafc;
    --bg2:         #f1f5f9;
    --bg3:         #e8f0fe;
    --border:      #e2e8f0;
    --border2:     #cbd5e1;
    --blue:        #2563eb;
    --blue-light:  #eff6ff;
    --blue-mid:    #dbeafe;
    --blue-dark:   #1e40af;
    --cyan:        #0891b2;
    --green:       #059669;
    --green-light: #ecfdf5;
    --amber:       #d97706;
    --amber-light: #fffbeb;
    --red:         #dc2626;
    --red-light:   #fef2f2;
    --purple:      #7c3aed;
    --text:        #0f172a;
    --text2:       #334155;
    --text3:       #64748b;
    --text4:       #94a3b8;
    --shadow-sm:   0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.06);
    --shadow-md:   0 4px 12px rgba(0,0,0,.08), 0 2px 6px rgba(0,0,0,.05);
    --shadow-lg:   0 10px 30px rgba(0,0,0,.10), 0 4px 12px rgba(0,0,0,.06);
    --radius:      10px;
    --radius-lg:   16px;
}

/* ── Reset & Global ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
    color: var(--text) !important;
    background-color: var(--bg) !important;
}
.block-container {
    padding: 1.75rem 2.25rem 3rem !important;
    max-width: 1440px !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text4); }

/* ════════════════════════════════════════
   SIDEBAR
═════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--white) !important;
    border-right: 1px solid var(--border) !important;
    box-shadow: 2px 0 12px rgba(0,0,0,.04) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 1.5rem !important; }

/* ── Sidebar logo area ── */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: .75rem;
    padding: .5rem 1rem 1.25rem 1rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.25rem;
}
.sidebar-logo .logo-icon {
    width: 40px; height: 40px;
    background: linear-gradient(135deg, var(--blue), var(--cyan));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
    box-shadow: 0 2px 8px rgba(37,99,235,.3);
    flex-shrink: 0;
}
.sidebar-logo .logo-text { line-height: 1.2; }
.sidebar-logo .logo-name {
    font-size: 1rem; font-weight: 700; color: var(--text);
}
.sidebar-logo .logo-sub {
    font-size: .7rem; color: var(--text3); font-weight: 400;
}

/* ── Sidebar section headers ── */
.sidebar-section {
    font-size: .7rem;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--text3);
    padding: .5rem 0 .5rem .25rem;
    margin-top: .25rem;
}

/* ── Sidebar stat cards ── */
.sidebar-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: .5rem;
    margin: .75rem 0;
}
.sidebar-stat {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: .6rem .7rem;
    text-align: center;
}
.sidebar-stat .s-val {
    font-size: 1.15rem; font-weight: 700; color: var(--blue);
}
.sidebar-stat .s-lbl {
    font-size: .65rem; color: var(--text3); margin-top: .1rem;
    text-transform: uppercase; letter-spacing: .06em;
}

/* ════════════════════════════════════════
   HERO / HEADER BANNER
═════════════════════════════════════════ */
.hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 40%, #0e7490 100%);
    border-radius: var(--radius-lg);
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-lg);
}
.hero::after {
    content: '';
    position: absolute;
    right: -40px; top: -40px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,.04);
    border-radius: 50%;
}
.hero::before {
    content: '';
    position: absolute;
    right: 80px; bottom: -60px;
    width: 280px; height: 280px;
    background: rgba(255,255,255,.03);
    border-radius: 50%;
}
.hero-title {
    font-size: 1.9rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 .4rem 0;
    letter-spacing: -.02em;
}
.hero-sub {
    color: rgba(255,255,255,.72);
    font-size: .95rem;
    margin: 0 0 1.2rem 0;
}
.hero-badges { display: flex; gap: .5rem; flex-wrap: wrap; }
.hero-badge {
    background: rgba(255,255,255,.12);
    border: 1px solid rgba(255,255,255,.2);
    color: rgba(255,255,255,.9);
    border-radius: 20px;
    padding: .25rem .75rem;
    font-size: .72rem;
    font-weight: 500;
}

/* ════════════════════════════════════════
   METRIC CARDS (top row)
═════════════════════════════════════════ */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.25rem;
    box-shadow: var(--shadow-sm);
    display: flex;
    align-items: center;
    gap: 1rem;
}
.metric-icon {
    width: 44px; height: 44px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
}
.metric-icon.blue   { background: var(--blue-light); }
.metric-icon.green  { background: var(--green-light); }
.metric-icon.amber  { background: var(--amber-light); }
.metric-icon.purple { background: #f5f3ff; }
.metric-body { min-width: 0; }
.metric-val {
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1.1;
}
.metric-lbl {
    font-size: .72rem;
    color: var(--text3);
    font-weight: 500;
    margin-top: .2rem;
    text-transform: uppercase;
    letter-spacing: .06em;
}

/* ════════════════════════════════════════
   MAIN CARDS / PANELS
═════════════════════════════════════════ */
.panel {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}
.panel-title {
    font-size: .8rem;
    font-weight: 600;
    color: var(--text2);
    letter-spacing: .08em;
    text-transform: uppercase;
    margin: 0 0 1rem 0;
    padding-bottom: .75rem;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: .5rem;
}

/* ════════════════════════════════════════
   QUERY INPUT AREA
═════════════════════════════════════════ */
.stTextArea textarea {
    border: 1.5px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    background: var(--white) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .95rem !important;
    line-height: 1.6 !important;
    transition: border-color .2s, box-shadow .2s !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.12) !important;
    outline: none !important;
}
.stTextInput input {
    border: 1.5px solid var(--border2) !important;
    border-radius: 8px !important;
    background: var(--white) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .9rem !important;
}
.stTextInput input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.12) !important;
}

/* ════════════════════════════════════════
   BUTTONS
═════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, var(--blue), var(--blue-dark)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: .9rem !important;
    padding: .55rem 1.5rem !important;
    letter-spacing: .01em !important;
    box-shadow: 0 2px 8px rgba(37,99,235,.3) !important;
    transition: all .2s !important;
}
.stButton > button:hover {
    box-shadow: 0 4px 14px rgba(37,99,235,.4) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* Secondary button (smaller ones) */
div[data-testid="stHorizontalBlock"] .stButton:not(:first-child) > button {
    background: var(--white) !important;
    color: var(--text2) !important;
    border: 1.5px solid var(--border2) !important;
    box-shadow: var(--shadow-sm) !important;
}
div[data-testid="stHorizontalBlock"] .stButton:not(:first-child) > button:hover {
    border-color: var(--blue) !important;
    color: var(--blue) !important;
    box-shadow: var(--shadow-sm) !important;
    transform: none !important;
}

/* ════════════════════════════════════════
   ANSWER BOX
═════════════════════════════════════════ */
.answer-box {
    background: #f0f7ff;
    border: 1.5px solid #bfdbfe;
    border-left: 4px solid var(--blue);
    border-radius: 0 var(--radius) var(--radius) 0;
    padding: 1.25rem 1.5rem;
    font-family: 'Fira Code', monospace;
    font-size: .87rem;
    line-height: 1.8;
    color: var(--text);
    white-space: pre-wrap;
    word-break: break-word;
    box-shadow: var(--shadow-sm);
}

/* ════════════════════════════════════════
   CODE BOX
═════════════════════════════════════════ */
.code-box {
    background: #1e293b;
    border-radius: var(--radius);
    padding: 1.25rem 1.5rem;
    font-family: 'Fira Code', monospace;
    font-size: .83rem;
    line-height: 1.7;
    color: #93c5fd;
    white-space: pre-wrap;
    word-break: break-all;
    overflow-x: auto;
    box-shadow: var(--shadow-sm);
}

/* ════════════════════════════════════════
   ERROR / SUCCESS ALERTS
═════════════════════════════════════════ */
.alert {
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    font-size: .88rem;
    display: flex;
    align-items: flex-start;
    gap: .75rem;
    margin: .75rem 0;
}
.alert-error {
    background: var(--red-light);
    border: 1px solid #fecaca;
    border-left: 4px solid var(--red);
    color: #7f1d1d;
}
.alert-success {
    background: var(--green-light);
    border: 1px solid #a7f3d0;
    border-left: 4px solid var(--green);
    color: #064e3b;
}
.alert-info {
    background: var(--blue-light);
    border: 1px solid var(--blue-mid);
    border-left: 4px solid var(--blue);
    color: #1e3a8a;
}
.alert-icon { font-size: 1rem; flex-shrink: 0; margin-top: .05rem; }
.alert-body { font-family: 'Fira Code', monospace; white-space: pre-wrap; word-break: break-word; }

/* ════════════════════════════════════════
   SAMPLE QUERY CHIPS
═════════════════════════════════════════ */
.chip-grid {
    display: flex;
    flex-wrap: wrap;
    gap: .4rem;
    margin: .5rem 0;
}
.chip {
    background: var(--bg2);
    border: 1px solid var(--border);
    color: var(--text2);
    border-radius: 20px;
    padding: .3rem .85rem;
    font-size: .75rem;
    font-weight: 500;
    cursor: pointer;
    transition: all .15s;
    white-space: nowrap;
}
.chip:hover {
    background: var(--blue-light);
    border-color: #bfdbfe;
    color: var(--blue-dark);
}

/* ════════════════════════════════════════
   TABS
═════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg2) !important;
    border-radius: 10px !important;
    padding: .25rem !important;
    gap: .2rem !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: .87rem !important;
    color: var(--text3) !important;
    padding: .5rem 1.1rem !important;
    transition: all .15s !important;
}
.stTabs [aria-selected="true"] {
    background: var(--white) !important;
    color: var(--blue) !important;
    font-weight: 600 !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ════════════════════════════════════════
   EXPANDERS
═════════════════════════════════════════ */
details {
    background: var(--white) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    margin-top: .75rem !important;
}
details summary {
    font-weight: 500 !important;
    color: var(--text2) !important;
    padding: .7rem 1rem !important;
    font-size: .88rem !important;
}

/* ════════════════════════════════════════
   FILE UPLOADER
═════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: var(--white) !important;
    border: 2px dashed var(--border2) !important;
    border-radius: var(--radius) !important;
    padding: .5rem !important;
    transition: border-color .2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--blue) !important;
}

/* ════════════════════════════════════════
   DATAFRAME / TABLES
═════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
    overflow: hidden !important;
}

/* ════════════════════════════════════════
   HISTORY ITEMS
═════════════════════════════════════════ */
.history-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin-bottom: .75rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .2s;
}
.history-card:hover { box-shadow: var(--shadow-md); }
.history-q {
    font-weight: 600;
    color: var(--text);
    font-size: .9rem;
    display: flex; align-items: flex-start; gap: .5rem;
}
.history-a {
    font-size: .82rem;
    color: var(--text3);
    margin-top: .4rem;
    font-family: 'Fira Code', monospace;
    line-height: 1.6;
    border-left: 3px solid var(--border);
    padding-left: .75rem;
}

/* ════════════════════════════════════════
   WELCOME / EMPTY STATE
═════════════════════════════════════════ */
.empty-state {
    text-align: center;
    padding: 3.5rem 2rem;
    background: var(--white);
    border: 2px dashed var(--border);
    border-radius: var(--radius-lg);
}
.empty-state .icon { font-size: 3.5rem; margin-bottom: 1rem; }
.empty-state h3 { font-size: 1.3rem; font-weight: 700; color: var(--text); margin: 0 0 .5rem; }
.empty-state p { color: var(--text3); font-size: .9rem; margin: 0; }

/* ════════════════════════════════════════
   FEATURE GRID (welcome screen)
═════════════════════════════════════════ */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 1.5rem;
}
.feature-card {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow .2s, transform .2s;
}
.feature-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
}
.feature-card .fi { font-size: 1.8rem; margin-bottom: .75rem; }
.feature-card h4 {
    font-size: .88rem; font-weight: 600; color: var(--text);
    margin: 0 0 .35rem;
}
.feature-card p { font-size: .8rem; color: var(--text3); margin: 0; line-height: 1.5; }

/* ════════════════════════════════════════
   DIVIDER
═════════════════════════════════════════ */
hr { border: none; border-top: 1px solid var(--border) !important; margin: 1rem 0 !important; }

/* ════════════════════════════════════════
   SPINNER / PROGRESS
═════════════════════════════════════════ */
[data-testid="stSpinner"] {
    color: var(--blue) !important;
}

/* ════════════════════════════════════════
   API KEY INPUT
═════════════════════════════════════════ */
.api-key-box {
    background: var(--amber-light);
    border: 1px solid #fcd34d;
    border-radius: var(--radius);
    padding: .85rem 1rem;
    margin: .5rem 0;
    font-size: .8rem;
    color: #78350f;
}

/* ════════════════════════════════════════
   CHART CONTAINER
═════════════════════════════════════════ */
.chart-wrapper {
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    box-shadow: var(--shadow-sm);
    margin-top: .75rem;
}

/* ════════════════════════════════════════
   FOOTER
═════════════════════════════════════════ */
.footer {
    margin-top: 2.5rem;
    padding-top: 1.25rem;
    border-top: 1px solid var(--border);
    text-align: center;
    font-size: .72rem;
    color: var(--text4);
}

/* ── Streamlit selectbox / radio ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--white) !important;
    border: 1.5px solid var(--border2) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
}
.stRadio label { color: var(--text2) !important; font-size: .88rem !important; }
.stCheckbox label { color: var(--text2) !important; font-size: .88rem !important; }

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumbValue"] {
    background: var(--blue) !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
defaults = {
    "df": None,
    "filename": "",
    "history": [],
    "prefill": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════════════════
# API CALLER
# ═══════════════════════════════════════════════════════════════════════════════
def call_claude(system: str, user: str) -> str:
    """Call Groq API using the Groq SDK. API key loaded from .env file."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. "
            "Please add it to the .env file: GROQ_API_KEY=your-groq-api-key-here"
        )
    
    client = Groq(api_key=api_key)
    
    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=2048,
        temperature=0.7,
    )
    return message.choices[0].message.content


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # Logo
    st.markdown("""
    <div class="sidebar-logo">
      <div class="logo-icon">📊</div>
      <div class="logo-text">
        <div class="logo-name">StatBot Pro</div>
        <div class="logo-sub">Autonomous CSV Analyst</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── File Upload ───────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">📂 Dataset</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        help="Any CSV file. Encoding auto-detected.",
        label_visibility="collapsed",
    )

    if uploaded:
        with st.spinner("Loading dataset..."):
            try:
                df_loaded = load_csv(uploaded)
                st.session_state.df = df_loaded
                st.session_state.filename = uploaded.name
                st.session_state.history = []
                st.success(f"✅ Loaded **{uploaded.name}**")
            except Exception as exc:
                st.error(f"Failed to load: {exc}")

    # Load sample CSV button
    sample_path = Path(__file__).parent / "data" / "sample_sales.csv"
    if sample_path.exists():
        if st.button("📥 Load Sample Dataset", use_container_width=True):
            with open(sample_path, "rb") as f:
                df_sample = load_csv(f)
            st.session_state.df = df_sample
            st.session_state.filename = "sample_sales.csv"
            st.session_state.history = []
            st.success("✅ Sample sales data loaded!")
            st.rerun()

    # ── Dataset stats ─────────────────────────────────────────────────────────
    if st.session_state.df is not None:
        df = st.session_state.df
        st.markdown('<div class="sidebar-section" style="margin-top:.75rem;">📋 Dataset Info</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sidebar-stats">
          <div class="sidebar-stat">
            <div class="s-val">{len(df):,}</div>
            <div class="s-lbl">Rows</div>
          </div>
          <div class="sidebar-stat">
            <div class="s-val">{len(df.columns)}</div>
            <div class="s-lbl">Columns</div>
          </div>
          <div class="sidebar-stat">
            <div class="s-val">{df.select_dtypes('number').shape[1]}</div>
            <div class="s-lbl">Numeric</div>
          </div>
          <div class="sidebar-stat">
            <div class="s-val">{round(df.isna().mean().mean()*100,1)}%</div>
            <div class="s-lbl">Missing</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Sample Queries ────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">💡 Sample Queries</div>', unsafe_allow_html=True)
    SAMPLES = [
        "Show top 5 rows",
        "What is the average of each numeric column?",
        "Plot a bar chart of revenue by region",
        "Show the correlation heatmap",
        "Which category has the highest total revenue?",
        "Plot monthly revenue trend",
        "Show missing values per column",
        "Plot revenue distribution as a histogram",
        "Rank top 5 items by sales",
        "Show a pie chart by category",
        "What is the min, max and mean of Revenue?",
        "Plot scatter: marketing spend vs revenue",
    ]
    for q in SAMPLES:
        if st.button(q, key=f"sq_{q[:15]}", use_container_width=True):
            st.session_state.prefill = q
            st.rerun()

    st.divider()
    st.markdown("""
    <div style="font-size:.68rem; color:#94a3b8; text-align:center; padding:.5rem 0;">
      StatBot Pro · Infotact Solutions<br>AI R&amp;D Wing · Confidential
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════════════════════


# ── Hero Banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">📊 StatBot Pro</div>
  <div class="hero-sub">Autonomous CSV Data Analyst — ask anything about your data in plain English</div>
  <div class="hero-badges">
    <span class="hero-badge">🤖 Powered by Groq Mixtral</span>
    <span class="hero-badge">🛡️ Sandboxed Execution</span>
    <span class="hero-badge">📈 Auto Visualization</span>
    <span class="hero-badge">⚡ Real-time Analysis</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── No file uploaded yet ──────────────────────────────────────────────────────
if st.session_state.df is None:
    st.markdown("""
    <div class="empty-state">
      <div class="icon">⬆️</div>
      <h3>Upload a CSV to get started</h3>
      <p>Use the sidebar to upload your dataset, or click <strong>Load Sample Dataset</strong> to try a demo.</p>
    </div>

    <div class="feature-grid">
      <div class="feature-card">
        <div class="fi">🧠</div>
        <h4>Natural Language Queries</h4>
        <p>Ask questions in plain English — StatBot generates and runs Python/Pandas code automatically.</p>
      </div>
      <div class="feature-card">
        <div class="fi">📊</div>
        <h4>Auto Visualization</h4>
        <p>Charts are generated with Matplotlib and saved as downloadable PNG files instantly.</p>
      </div>
      <div class="feature-card">
        <div class="fi">🛡️</div>
        <h4>Safe Code Execution</h4>
        <p>All generated code is security-validated before execution. No OS access, no file deletion.</p>
      </div>
      <div class="feature-card">
        <div class="fi">🔍</div>
        <h4>Code Transparency</h4>
        <p>See the exact Python code that was generated and executed for every query.</p>
      </div>
      <div class="feature-card">
        <div class="fi">📂</div>
        <h4>Any CSV Format</h4>
        <p>Supports any CSV with automatic encoding detection, date parsing, and type inference.</p>
      </div>
      <div class="feature-card">
        <div class="fi">📜</div>
        <h4>Query History</h4>
        <p>All your queries and results are saved during the session for easy reference.</p>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ── Dataset loaded — show metric row ─────────────────────────────────────────
df = st.session_state.df
num_cols = df.select_dtypes("number").shape[1]
cat_cols = df.select_dtypes("object").shape[1]
null_pct = round(df.isna().mean().mean() * 100, 1)

st.markdown(f"""
<div class="metric-row">
  <div class="metric-card">
    <div class="metric-icon blue">📋</div>
    <div class="metric-body">
      <div class="metric-val">{len(df):,}</div>
      <div class="metric-lbl">Total Rows</div>
    </div>
  </div>
  <div class="metric-card">
    <div class="metric-icon green">📐</div>
    <div class="metric-body">
      <div class="metric-val">{len(df.columns)}</div>
      <div class="metric-lbl">Columns</div>
    </div>
  </div>
  <div class="metric-card">
    <div class="metric-icon amber">🔢</div>
    <div class="metric-body">
      <div class="metric-val">{num_cols}</div>
      <div class="metric-lbl">Numeric Cols</div>
    </div>
  </div>
  <div class="metric-card">
    <div class="metric-icon purple">⚠️</div>
    <div class="metric-body">
      <div class="metric-val">{null_pct}%</div>
      <div class="metric-lbl">Missing Data</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_ask, tab_data, tab_history = st.tabs([
    "🤖  Ask StatBot",
    "🗂️  Explore Data",
    "📜  Query History",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — ASK STATBOT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_ask:
    st.markdown('<div class="panel-title">💬 Ask a Question</div>', unsafe_allow_html=True)

    # Grab prefill from sidebar sample queries
    prefill_val = st.session_state.pop("prefill", "")

    question = st.text_area(
        "Your question:",
        value=prefill_val,
        height=100,
        placeholder=(
            "e.g. What is the total revenue per region? "
            "Plot a monthly trend chart. "
            "Which product sells the most?"
        ),
        label_visibility="collapsed",
    )

    col_run, col_clear, col_space = st.columns([1.2, 1, 5])
    with col_run:
        run_btn = st.button("▶  Analyse", use_container_width=True)
    with col_clear:
        if st.button("🗑  Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    # ── Run pipeline ──────────────────────────────────────────────────────────
    if run_btn:
        q = question.strip()
        if not q:
            st.markdown('<div class="alert alert-info"><span class="alert-icon">ℹ️</span><div class="alert-body">Please enter a question above.</div></div>', unsafe_allow_html=True)
        elif not os.environ.get("GROQ_API_KEY"):
            st.markdown('<div class="alert alert-error"><span class="alert-icon">🔑</span><div class="alert-body">GROQ_API_KEY not found. Add it to the .env file and restart the app.</div></div>', unsafe_allow_html=True)
        else:
            with st.spinner("🤖 StatBot is analysing your data..."):
                result: AgentResult = run_agent(df, q, call_claude)

            if result.success:
                # Answer
                st.markdown("#### 💬 Answer")
                st.markdown(
                    f'<div class="answer-box">{result.answer}</div>',
                    unsafe_allow_html=True,
                )

                # Chart
                if result.chart_bytes:
                    st.markdown("#### 📈 Chart")
                    st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
                    st.image(result.chart_bytes, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                    chart_name = Path(result.chart_path).name if result.chart_path else "chart.png"
                    st.download_button(
                        label="⬇️  Download Chart (.png)",
                        data=result.chart_bytes,
                        file_name=chart_name,
                        mime="image/png",
                    )

                # Generated code expander
                with st.expander("🔍  View Generated Python Code"):
                    st.markdown(
                        f'<div class="code-box">{result.code}</div>',
                        unsafe_allow_html=True,
                    )

                # Warn from error field (e.g. chart save warning)
                if result.error:
                    st.markdown(
                        f'<div class="alert alert-info"><span class="alert-icon">⚠️</span><div class="alert-body">{result.error}</div></div>',
                        unsafe_allow_html=True,
                    )

                # Save to history
                st.session_state.history.append({
                    "q": q,
                    "a": result.answer,
                    "chart": result.chart_bytes,
                    "code": result.code,
                })

            else:
                st.markdown(
                    f'<div class="alert alert-error"><span class="alert-icon">❌</span><div class="alert-body">{result.error}</div></div>',
                    unsafe_allow_html=True,
                )
                if result.code:
                    with st.expander("🔍  View Generated Code (for debugging)"):
                        st.markdown(
                            f'<div class="code-box">{result.code}</div>',
                            unsafe_allow_html=True,
                        )

    # ── Quick query chips ─────────────────────────────────────────────────────
    st.markdown("---")
    st.caption("💡 **Quick queries** — click to pre-fill:")
    chip_queries = [
        "Show first 10 rows",
        "Average of each numeric column",
        "Count of each category",
        "Revenue by region (bar chart)",
        "Correlation heatmap",
        "Distribution histogram",
        "Monthly trend line chart",
        "Top 10 by largest column",
        "Missing values report",
        "Pie chart by category",
    ]
    cols = st.columns(5)
    for i, cq in enumerate(chip_queries):
        with cols[i % 5]:
            if st.button(cq, key=f"chip_{i}", use_container_width=True):
                st.session_state.prefill = cq
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — EXPLORE DATA
# ═══════════════════════════════════════════════════════════════════════════════
with tab_data:
    fname = st.session_state.filename
    if fname:
        st.markdown(
            f'<span style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:20px;'
            f'padding:.25rem .9rem;font-size:.8rem;font-weight:600;color:#1e40af;">📂 {fname}</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")

    sub1, sub2, sub3 = st.tabs(["📄 Data Preview", "📊 Statistics", "🔎 Column Info"])

    with sub1:
        n_rows = st.slider("Rows to preview:", 5, min(500, len(df)), 20, key="prev_slider")
        show_opts = st.multiselect(
            "Select columns to display (leave empty for all):",
            options=list(df.columns),
            default=[],
            key="col_select",
        )
        disp_df = df[show_opts] if show_opts else df
        st.dataframe(disp_df.head(n_rows), use_container_width=True, height=420)

    with sub2:
        num_df = df.describe(include="number").round(4)
        if not num_df.empty:
            st.markdown("**Numeric Columns**")
            st.dataframe(num_df, use_container_width=True)
        cat_df = df.describe(include="object")
        if not cat_df.empty:
            st.markdown("**Categorical Columns**")
            st.dataframe(cat_df, use_container_width=True)

        # Null heatmap
        null_counts = df.isna().sum()
        null_pcts = (df.isna().mean() * 100).round(2)
        null_summary = pd.DataFrame({
            "Missing Count": null_counts,
            "Missing %": null_pcts,
            "Data Type": df.dtypes,
        })
        st.markdown("**Missing Values Summary**")
        st.dataframe(null_summary, use_container_width=True)

    with sub3:
        col_detail = st.selectbox("Select column:", df.columns, key="col_detail_sel")
        col_data = df[col_detail]

        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.metric("Dtype", str(col_data.dtype))
            st.metric("Non-null count", f"{col_data.count():,}")
            st.metric("Null count", f"{col_data.isna().sum():,}")
            st.metric("Unique values", f"{col_data.nunique():,}")
        with info_col2:
            if pd.api.types.is_numeric_dtype(col_data):
                st.metric("Min", f"{col_data.min():,.4g}")
                st.metric("Max", f"{col_data.max():,.4g}")
                st.metric("Mean", f"{col_data.mean():,.4g}")
                st.metric("Std Dev", f"{col_data.std():,.4g}")
            else:
                top5 = col_data.value_counts().head(5)
                st.markdown("**Top 5 values:**")
                st.dataframe(top5.rename("Count"), use_container_width=True)

        st.markdown("**Sample Values:**")
        st.dataframe(col_data.dropna().head(20).to_frame(), use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
with tab_history:
    if not st.session_state.history:
        st.markdown("""
        <div class="empty-state" style="padding:2rem;">
          <div class="icon" style="font-size:2.5rem;">📜</div>
          <h3>No queries yet</h3>
          <p>Your analysis history will appear here after you ask StatBot a question.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption(f"**{len(st.session_state.history)} queries** in this session")
        for i, item in enumerate(reversed(st.session_state.history)):
            idx = len(st.session_state.history) - i
            with st.expander(f"#{idx}  —  {item['q'][:90]}{'...' if len(item['q'])>90 else ''}"):
                st.markdown(
                    f'<div class="answer-box">{item["a"][:800]}{"..." if len(item["a"])>800 else ""}</div>',
                    unsafe_allow_html=True,
                )
                if item.get("chart"):
                    st.image(item["chart"], use_container_width=True)
                    st.download_button(
                        "⬇️ Download Chart",
                        data=item["chart"],
                        file_name=f"chart_query_{idx}.png",
                        mime="image/png",
                        key=f"dl_hist_{idx}",
                    )
                with st.expander("🔍 View Code"):
                    st.markdown(
                        f'<div class="code-box">{item["code"]}</div>',
                        unsafe_allow_html=True,
                    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  StatBot Pro &nbsp;·&nbsp; Infotact Solutions &nbsp;·&nbsp; AI Research &amp; Development Wing
  &nbsp;·&nbsp.
</div>
""", unsafe_allow_html=True)
