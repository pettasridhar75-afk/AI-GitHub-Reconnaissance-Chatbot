import streamlit as st
import sys
import os
import html

# ============================================================
# PROJECT PATH
# ============================================================

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# ============================================================
# IMPORTS
# ============================================================

from collectors.github_search import search_repositories

from collectors.github_repository import (
    get_repository_details,
    get_branches,
    get_recent_commits,
    get_repository_files,
)

from analyzers.file_analyzer import analyze_files
from ai.analyzer import analyze_repository_with_ai

from database.database import (
    initialize_database,
    save_repository,
    save_security_finding,
    get_saved_repositories,
    get_security_findings,
)

# ============================================================
# DATABASE
# ============================================================

initialize_database()

# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="AI GitHub Reconnaissance Chatbot",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# DESIGN
# ============================================================

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #061226;
        --panel: rgba(8, 29, 58, 0.82);
        --panel-2: rgba(10, 38, 75, 0.72);
        --line: rgba(53, 169, 255, 0.36);
        --line-soft: rgba(100, 173, 230, 0.20);
        --cyan: #20d9ff;
        --blue: #1687ff;
        --violet: #7b4dff;
        --text: #f4f9ff;
        --muted: #a9c3df;
        --danger: #ff5b68;
    }

    /* --------------------------------------------------------
       GLOBAL
       -------------------------------------------------------- */

    html,
    body,
    .stApp,
    [data-testid="stApp"],
    [data-testid="stHeader"],
    [data-testid="stMain"],
    [data-testid="stAppViewContainer"],
    [data-testid="stBottom"],
    [data-testid="stBottomBlockContainer"] {
        background: transparent !important;
    }

    .stApp {
        font-family: 'Inter', sans-serif !important;
        color: var(--text) !important;
    }

    [data-testid="stAppViewContainer"] {
        position: relative;
        min-height: 100vh;
        overflow-x: hidden;
    }

    /* Requested technology / big-data background */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(
                180deg,
                rgba(3, 14, 34, 0.52),
                rgba(2, 11, 28, 0.82)
            ),
            url("https://www.shutterstock.com/image-illustration/technology-abstract-background-big-data-600nw-1706459290.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        filter: saturate(1.08) brightness(0.82);
        transform: scale(1.02);
        z-index: 0;
        pointer-events: none;
    }

    [data-testid="stAppViewContainer"]::after {
        content: "";
        position: fixed;
        inset: 0;
        background:
            radial-gradient(
                circle at 75% 14%,
                rgba(0, 184, 255, 0.16),
                transparent 30%
            ),
            radial-gradient(
                circle at 15% 78%,
                rgba(88, 73, 255, 0.13),
                transparent 30%
            ),
            rgba(1, 8, 22, 0.10);
        z-index: 1;
        pointer-events: none;
    }

    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        position: relative;
        z-index: 2;
        background: transparent !important;
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1220px !important;
        padding-top: 1.25rem !important;
        padding-bottom: 4rem !important;
        margin: 0 auto !important;
    }

    [data-testid="stHeader"],
    [data-testid="stToolbar"] {
        background: transparent !important;
        z-index: 5;
    }

    /* --------------------------------------------------------
       TEXT
       -------------------------------------------------------- */

    h1, h2, h3, h4, h5, h6 {
        color: #f6fbff !important;
        font-weight: 700 !important;
        text-shadow: 0 3px 18px rgba(0, 0, 0, 0.45);
    }

    h1 {
        font-size: 2.35rem !important;
        letter-spacing: -1.1px !important;
        margin-bottom: 0.15rem !important;
    }

    h2 {
        font-size: 1.55rem !important;
    }

    h3 {
        font-size: 1.2rem !important;
    }

    .stMarkdown p,
    .stMarkdown li,
    label {
        color: rgba(235, 246, 255, 0.90) !important;
    }

    .stCaption {
        color: rgba(180, 210, 235, 0.72) !important;
    }

    /* --------------------------------------------------------
       HERO
       -------------------------------------------------------- */

    .hero {
        padding: 18px 4px 16px 4px;
    }

    .hero-title {
        display: flex;
        align-items: center;
        gap: 14px;
        font-size: 2.35rem;
        font-weight: 800;
        letter-spacing: -1px;
        color: #f7fbff;
        text-shadow: 0 4px 24px rgba(0, 0, 0, 0.55);
    }

    .github-mark {
        width: 46px;
        height: 46px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: rgba(255,255,255,0.94);
        color: #081b35;
        font-size: 27px;
        box-shadow: 0 0 26px rgba(38, 175, 255, 0.22);
    }

    .hero-title .accent {
        color: #45d8ff;
    }

    .hero-subtitle {
        margin-left: 61px;
        color: #c0d8ef;
        font-size: 0.96rem;
        margin-top: 3px;
    }

    .hero-powered {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 15px;
        border-radius: 14px;
        border: 1px solid rgba(52, 185, 255, 0.48);
        background: rgba(8, 36, 72, 0.68);
        color: #dff7ff;
        box-shadow: 0 8px 28px rgba(0, 110, 210, 0.20);
        backdrop-filter: blur(14px);
        font-size: 0.85rem;
        font-weight: 600;
    }

    .gemini-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
        background: linear-gradient(135deg, #35e6ff, #8f5cff);
        box-shadow: 0 0 12px rgba(61, 211, 255, 0.8);
    }

    /* --------------------------------------------------------
       SEARCH PANEL
       -------------------------------------------------------- */

    .search-panel {
        padding: 18px 20px 20px;
        border-radius: 16px;
        border: 1px solid rgba(40, 178, 255, 0.58);
        background: linear-gradient(
            135deg,
            rgba(4, 35, 72, 0.88),
            rgba(6, 25, 54, 0.80)
        );
        box-shadow:
            0 16px 45px rgba(0, 0, 0, 0.30),
            inset 0 1px 0 rgba(255,255,255,0.07);
        backdrop-filter: blur(15px);
        margin-bottom: 15px;
    }

    .section-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(
            135deg,
            rgba(12, 148, 255, 0.85),
            rgba(67, 70, 235, 0.85)
        );
        box-shadow: 0 0 24px rgba(21, 151, 255, 0.25);
        font-size: 22px;
        margin-right: 10px;
        vertical-align: middle;
    }

    .panel-title {
        color: #effaff;
        font-size: 1.12rem;
        font-weight: 700;
        vertical-align: middle;
    }

    .panel-subtitle {
        color: #a9c8e4;
        font-size: 0.82rem;
        margin-top: 4px;
        margin-left: 54px;
    }

    div[data-baseweb="input"] {
        background: rgba(3, 20, 43, 0.86) !important;
        border: 1px solid rgba(49, 157, 247, 0.62) !important;
        border-radius: 10px !important;
        box-shadow:
            inset 0 1px 0 rgba(255,255,255,0.04),
            0 5px 20px rgba(0,0,0,0.18);
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #30bfff !important;
        box-shadow:
            0 0 0 1px rgba(48, 191, 255, 0.18),
            0 0 25px rgba(25, 157, 255, 0.14);
    }

    div[data-baseweb="input"] input {
        color: #eff9ff !important;
        background: transparent !important;
        font-size: 0.95rem !important;
    }

    div[data-baseweb="input"] input::placeholder {
        color: #7596b8 !important;
    }

    /* --------------------------------------------------------
       BUTTONS
       -------------------------------------------------------- */

    .stButton > button,
    .stLinkButton > a {
        border-radius: 10px !important;
        border: 1px solid rgba(69, 194, 255, 0.40) !important;
        background: linear-gradient(
            135deg,
            #0789f7,
            #246df4 48%,
            #7447ed
        ) !important;
        color: #ffffff !important;
        font-weight: 650 !important;
        box-shadow:
            0 9px 25px rgba(4, 98, 201, 0.28),
            inset 0 1px 0 rgba(255,255,255,0.10);
        transition: all 0.18s ease !important;
    }

    .stButton > button:hover,
    .stLinkButton > a:hover {
        transform: translateY(-1px);
        border-color: rgba(132, 221, 255, 0.72) !important;
        box-shadow:
            0 13px 30px rgba(10, 119, 232, 0.34),
            0 0 20px rgba(65, 117, 255, 0.16);
    }

    /* --------------------------------------------------------
       FEATURE CARDS
       -------------------------------------------------------- */

    .feature-card {
        min-height: 145px;
        padding: 18px 17px;
        border-radius: 13px;
        border: 1px solid rgba(46, 159, 234, 0.35);
        background: linear-gradient(
            145deg,
            rgba(5, 35, 69, 0.88),
            rgba(5, 22, 48, 0.78)
        );
        box-shadow:
            0 12px 30px rgba(0,0,0,0.22),
            inset 0 1px 0 rgba(255,255,255,0.04);
        backdrop-filter: blur(12px);
    }

    .feature-icon {
        width: 39px;
        height: 39px;
        border-radius: 11px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(
            135deg,
            rgba(8, 154, 247, 0.88),
            rgba(87, 74, 230, 0.90)
        );
        font-size: 20px;
        margin-bottom: 12px;
    }

    .feature-title {
        color: #f0f8ff;
        font-size: 0.92rem;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .feature-text {
        color: #9eb9d5;
        font-size: 0.76rem;
        line-height: 1.48;
    }

    /* --------------------------------------------------------
       GLASS PANELS
       -------------------------------------------------------- */

    .glass-panel {
        border-radius: 14px;
        border: 1px solid rgba(43, 164, 242, 0.38);
        background: linear-gradient(
            145deg,
            rgba(5, 30, 62, 0.91),
            rgba(4, 20, 43, 0.82)
        );
        box-shadow:
            0 16px 40px rgba(0,0,0,0.25),
            inset 0 1px 0 rgba(255,255,255,0.045);
        backdrop-filter: blur(14px);
        padding: 17px;
    }

    .repo-card {
        padding: 15px;
        margin: 8px 0;
        border-radius: 11px;
        border: 1px solid rgba(89, 153, 205, 0.22);
        background: rgba(7, 32, 62, 0.68);
        transition: all 0.16s ease;
    }

    .repo-card:hover {
        border-color: rgba(44, 181, 255, 0.60);
        background: rgba(9, 42, 79, 0.76);
        transform: translateY(-1px);
    }

    .repo-name {
        color: #4ed9ff;
        font-weight: 700;
        font-size: 0.92rem;
    }

    .repo-desc {
        color: #a8c1da;
        font-size: 0.75rem;
        line-height: 1.45;
        margin-top: 5px;
    }

    .repo-meta {
        color: #8eacc9;
        font-size: 0.70rem;
        margin-top: 9px;
    }

    .repo-meta strong {
        color: #dbeeff;
    }

    /* --------------------------------------------------------
       DETAIL HEADER
       -------------------------------------------------------- */

    .detail-header {
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(63, 164, 235, 0.26);
        background: rgba(6, 29, 58, 0.62);
        margin-bottom: 12px;
    }

    .detail-name {
        color: #f4fbff;
        font-size: 1.15rem;
        font-weight: 750;
    }

    .detail-description {
        color: #a9c2da;
        font-size: 0.78rem;
        line-height: 1.5;
        margin-top: 4px;
    }

    .detail-link {
        color: #42d6ff !important;
        font-size: 0.73rem;
    }

    /* --------------------------------------------------------
       METRICS
       -------------------------------------------------------- */

    [data-testid="stMetric"] {
        background: rgba(6, 30, 59, 0.72) !important;
        border: 1px solid rgba(61, 157, 222, 0.22) !important;
        border-radius: 11px !important;
        padding: 10px 12px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.035);
        backdrop-filter: blur(10px);
    }

    [data-testid="stMetricLabel"] {
        color: #89abc8 !important;
        font-size: 0.70rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #edf8ff !important;
        font-size: 1.18rem !important;
    }

    /* --------------------------------------------------------
       TABS
       -------------------------------------------------------- */

    button[data-baseweb="tab"] {
        color: #9db8d2 !important;
        background: transparent !important;
        border-radius: 8px 8px 0 0 !important;
        font-size: 0.76rem !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        background: rgba(18, 105, 192, 0.45) !important;
        box-shadow: inset 0 -2px 0 #29c5ff;
    }

    [data-baseweb="tab-highlight"] {
        background: #28c8ff !important;
    }

    /* --------------------------------------------------------
       EXPANDERS / ALERTS
       -------------------------------------------------------- */

    [data-testid="stExpander"] {
        background: rgba(5, 26, 52, 0.66) !important;
        border: 1px solid rgba(67, 148, 204, 0.20) !important;
        border-radius: 11px !important;
        backdrop-filter: blur(10px);
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p {
        color: #edf8ff !important;
        font-weight: 600 !important;
    }

    [data-testid="stAlert"] {
        border-radius: 10px !important;
        backdrop-filter: blur(10px);
    }

    /* --------------------------------------------------------
       HISTORY
       -------------------------------------------------------- */

    .history-row {
        padding: 12px;
        border: 1px solid rgba(69, 151, 207, 0.22);
        background: rgba(5, 26, 51, 0.65);
        border-radius: 10px;
        margin: 7px 0;
    }

    .history-name {
        color: #eaf8ff;
        font-weight: 700;
        font-size: 0.82rem;
    }

    .history-small {
        color: #91afc9;
        font-size: 0.70rem;
    }

    /* --------------------------------------------------------
       FOOTER
       -------------------------------------------------------- */

    .project-footer {
        margin-top: 35px;
        padding: 22px 10px;
        text-align: center;
        border-top: 1px solid rgba(75, 158, 216, 0.18);
        color: #7896b2 !important;
        font-size: 0.72rem;
    }

    hr {
        border-color: rgba(68, 150, 210, 0.17) !important;
    }

    a {
        color: #54d9ff !important;
    }

    /* Hide default Streamlit branding */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    @media (max-width: 900px) {
        .hero-title {
            font-size: 1.8rem;
        }

        .hero-subtitle {
            margin-left: 0;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "results": [],
    "search_error": None,
    "selected_repo": None,
    "analyzed_repo": None,
    "show_history": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# SAFE HELPERS
# ============================================================

def safe_text(value, fallback="Not available"):
    if value is None or value == "":
        return fallback
    return html.escape(str(value))


def run_collector(function, *args, default=None):
    """
    Prevent one interrupted GitHub request from crashing the UI.
    """
    try:
        result = function(*args)
        return result if result is not None else default
    except Exception as error:
        return default


def analyze_selected_repository(repo):
    owner = repo.get("owner")
    repository_name = repo.get("name")

    if not owner or not repository_name:
        st.error("Repository information is incomplete.")
        return

    with st.spinner(f"Analyzing {repo.get('full_name', repository_name)}..."):

        details = run_collector(
            get_repository_details,
            owner,
            repository_name,
            default={"error": "Unable to retrieve repository details."},
        )

        branches = run_collector(
            get_branches,
            owner,
            repository_name,
            default=[],
        )

        commits = run_collector(
            get_recent_commits,
            owner,
            repository_name,
            default=[],
        )

        files = run_collector(
            get_repository_files,
            owner,
            repository_name,
            default=[],
        )

        security_findings = run_collector(
            analyze_files,
            files,
            default=[],
        )

        repository_data = {
            **details,
            "owner": repo.get("owner"),
            "url": repo.get("url"),
        }

        repository_id = None

        try:
            if "error" not in details:
                repository_id = save_repository(repository_data)

                for finding in security_findings:
                    save_security_finding(
                        repository_id,
                        finding,
                    )
        except Exception as error:
            st.warning(f"Database save warning: {error}")

        ai_result = analyze_repository_with_ai(
            repository=repository_data,
            branches=branches,
            commits=commits,
            files=files,
            findings=security_findings,
        )

    st.session_state.selected_repo = repo

    st.session_state.analyzed_repo = {
        "repo": repo,
        "details": details,
        "branches": branches,
        "commits": commits,
        "files": files,
        "security_findings": security_findings,
        "repository_id": repository_id,
        "ai_analysis": ai_result,
    }


# ============================================================
# HERO
# ============================================================

hero_left, hero_right = st.columns([5.5, 1.5])

with hero_left:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-title">
                <span class="github-mark">●</span>
                <span>AI GitHub <span class="accent">Reconnaissance</span> Chatbot</span>
            </div>
            <div class="hero-subtitle">
                Search &nbsp;•&nbsp; Analyze &nbsp;•&nbsp; Detect &nbsp;•&nbsp; Get AI Insights
            </div>
            <div class="hero-subtitle">
                Explore public repositories with AI-powered security analysis
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with hero_right:
    st.markdown(
        """
        <div style="text-align:right; padding-top:18px;">
            <div class="hero-powered">
                <span class="gemini-dot"></span>
                Powered by Gemini
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# SEARCH PANEL
# ============================================================

st.markdown(
    """
    <div class="search-panel">
        <div>
            <span class="section-icon">⌕</span>
            <span class="panel-title">Search GitHub Repositories</span>
        </div>
        <div class="panel-subtitle">
            Enter a company name, technology, or keyword to find relevant public repositories
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

search_col, button_col = st.columns([6, 1])

with search_col:
    company = st.text_input(
        "GitHub search",
        placeholder="e.g. microsoft, openai, cybersecurity, react",
        label_visibility="collapsed",
    )

with button_col:
    search_clicked = st.button(
        "🔎 Search",
        use_container_width=True,
        key="main_search",
    )

if search_clicked:
    if not company.strip():
        st.warning("Please enter a company name, technology, or keyword.")
    else:
        with st.spinner("Searching public GitHub repositories..."):
            try:
                results = search_repositories(company.strip())

                if isinstance(results, dict) and "error" in results:
                    st.session_state.results = []
                    st.session_state.search_error = results["error"]
                else:
                    st.session_state.results = results or []
                    st.session_state.search_error = None
                    st.session_state.selected_repo = None
                    st.session_state.analyzed_repo = None

            except Exception as error:
                st.session_state.results = []
                st.session_state.search_error = (
                    "GitHub search connection failed. "
                    "Please try again."
                )

if st.session_state.search_error:
    st.error(st.session_state.search_error)

# ============================================================
# FEATURE CARDS
# ============================================================

feature_cols = st.columns(4)

features = [
    (
        "🗄️",
        "Repository Analysis",
        "Get detailed repository information, branches, commits, and file structure.",
    ),
    (
        "🛡️",
        "Security Scanning",
        "Detect secret-like patterns and potential security findings.",
    ),
    (
        "🧠",
        "AI-Powered Insights",
        "Generate intelligent analysis and defensive review recommendations.",
    ),
    (
        "📊",
        "Save & Track",
        "Store analysis records and track security findings over time.",
    ),
]

for col, (icon, title, description) in zip(feature_cols, features):
    with col:
        st.markdown(
            f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-text">{description}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ============================================================
# RESULTS + DETAILS
# ============================================================

results = st.session_state.results

if results:

    left, right = st.columns([0.93, 1.45], gap="medium")

    # --------------------------------------------------------
    # LEFT: SEARCH RESULTS
    # --------------------------------------------------------

    with left:

        st.markdown(
            f"""
            <div class="glass-panel">
                <div>
                    <span class="section-icon">⌕</span>
                    <span class="panel-title">Search Results</span>
                </div>
                <div class="panel-subtitle">
                    Found {len(results)} repositories for your query
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for index, repo in enumerate(results):

            name = safe_text(repo.get("full_name"))
            description = safe_text(
                repo.get("description"),
                "No description available.",
            )
            language = safe_text(
                repo.get("language"),
                "Unknown",
            )

            st.markdown(
                f"""
                <div class="repo-card">
                    <div class="repo-name">{name}</div>
                    <div class="repo-desc">{description}</div>
                    <div class="repo-meta">
                        ⭐ <strong>{repo.get("stars") or 0}</strong>
                        &nbsp;&nbsp;•&nbsp;&nbsp;
                        🍴 <strong>{repo.get("forks") or 0}</strong>
                        &nbsp;&nbsp;•&nbsp;&nbsp;
                        💻 <strong>{language}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            action_col1, action_col2 = st.columns([1, 1])

            with action_col1:
                if st.button(
                    "Select",
                    key=f"select_{index}_{repo.get('full_name')}",
                    use_container_width=True,
                ):
                    st.session_state.selected_repo = repo
                    st.session_state.analyzed_repo = None
                    st.rerun()

            with action_col2:
                if st.button(
                    "Analyze",
                    key=f"analyze_{index}_{repo.get('full_name')}",
                    use_container_width=True,
                ):
                    analyze_selected_repository(repo)
                    st.rerun()

    # --------------------------------------------------------
    # RIGHT: REPOSITORY DETAILS
    # --------------------------------------------------------

    with right:

        selected = st.session_state.selected_repo
        analysis = st.session_state.analyzed_repo

        if analysis:
            selected = analysis["repo"]

        if not selected:
            st.markdown(
                """
                <div class="glass-panel" style="min-height:480px;
                    display:flex; align-items:center; justify-content:center;">
                    <div style="text-align:center;">
                        <div style="font-size:42px;">📦</div>
                        <div style="color:#dcefff; font-size:1.05rem;
                            font-weight:700; margin-top:10px;">
                            Repository Details
                        </div>
                        <div style="color:#8faec9; font-size:0.78rem;
                            margin-top:5px;">
                            Select a repository from the search results
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            details = (
                analysis["details"]
                if analysis
                else selected
            )

            stars = details.get("stars") or selected.get("stars") or 0
            forks = details.get("forks") or selected.get("forks") or 0
            language = (
                details.get("language")
                or selected.get("language")
                or "Unknown"
            )
            branch = details.get("default_branch") or "Unknown"
            updated = details.get("updated_at") or "Unknown"

            st.markdown(
                """
                <div class="glass-panel">
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="detail-header">
                    <div class="detail-name">
                        📦 {safe_text(selected.get("full_name"))}
                    </div>
                    <div class="detail-description">
                        {safe_text(
                            details.get("description"),
                            "No description available."
                        )}
                    </div>
                    <div class="detail-link">
                        {safe_text(
                            selected.get("url"),
                            ""
                        )}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            m1, m2, m3, m4 = st.columns(4)

            with m1:
                st.metric("⭐ Stars", stars)

            with m2:
                st.metric("🍴 Forks", forks)

            with m3:
                st.metric("💻 Language", language)

            with m4:
                st.metric("🌿 Branch", branch)

            tab_overview, tab_branches, tab_commits, tab_files, tab_security, tab_ai = st.tabs(
                [
                    "📊 Overview",
                    "🌿 Branches",
                    "📝 Commits",
                    "📄 Files",
                    "🛡️ Security",
                    "✨ AI Analysis",
                ]
            )

            # ------------------------------------------------
            # OVERVIEW
            # ------------------------------------------------

            with tab_overview:

                created = details.get("created_at") or "Unknown"
                license_name = details.get("license") or "Not specified"
                issues = details.get("open_issues") or 0

                overview_cols = st.columns(2)

                with overview_cols[0]:
                    st.markdown(
                        f"""
                        **📅 Created At**  
                        `{safe_text(created)}`

                        **📜 License**  
                        `{safe_text(license_name)}`
                        """
                    )

                with overview_cols[1]:
                    st.markdown(
                        f"""
                        **🐛 Open Issues**  
                        `{issues}`

                        **🕐 Last Updated**  
                        `{safe_text(updated)}`
                        """
                    )

                if selected.get("url"):
                    st.link_button(
                        "🌐 Open Repository",
                        selected["url"],
                        use_container_width=True,
                    )

                st.markdown(
                    "<div style='height:6px'></div>",
                    unsafe_allow_html=True,
                )

                if not analysis:
                    st.info(
                        "Select **Analyze** on the left to collect branches, "
                        "commits, files, security findings, and AI insights."
                    )
                else:
                    st.success(
                        "Repository analysis collected and saved."
                    )

            # ------------------------------------------------
            # BRANCHES
            # ------------------------------------------------

            with tab_branches:

                branches = (
                    analysis["branches"]
                    if analysis
                    else []
                )

                if branches:
                    for branch_item in branches:
                        st.write(f"🌿 `{branch_item}`")
                else:
                    st.info(
                        "No branch information is currently available."
                    )

            # ------------------------------------------------
            # COMMITS
            # ------------------------------------------------

            with tab_commits:

                commits = (
                    analysis["commits"]
                    if analysis
                    else []
                )

                if commits:
                    for commit in commits:

                        st.markdown(
                            f"**{safe_text(
                                commit.get("message"),
                                "Commit message unavailable."
                            )}**"
                        )

                        st.caption(
                            f"Author: {commit.get('author') or 'Unknown'}"
                            f"  •  "
                            f"Date: {commit.get('date') or 'Unknown'}"
                        )

                        if commit.get("url"):
                            st.link_button(
                                "View Commit",
                                commit["url"],
                                use_container_width=True,
                            )

                        st.divider()
                else:
                    st.info(
                        "Analyze the repository to retrieve recent commits."
                    )

            # ------------------------------------------------
            # FILES
            # ------------------------------------------------

            with tab_files:

                files = (
                    analysis["files"]
                    if analysis
                    else []
                )

                if files:
                    for file_item in files:
                        icon = (
                            "📁"
                            if file_item.get("type") == "dir"
                            else "📄"
                        )

                        st.write(
                            f"{icon} `{file_item.get('path', 'Unknown')}`"
                        )
                else:
                    st.info(
                        "Analyze the repository to retrieve files."
                    )

            # ------------------------------------------------
            # SECURITY
            # ------------------------------------------------

            with tab_security:

                findings = (
                    analysis["security_findings"]
                    if analysis
                    else []
                )

                if not analysis:
                    st.info(
                        "Analyze the repository to run the security scanner."
                    )

                elif not findings:
                    st.success(
                        "✅ No potential secret-like patterns were detected "
                        "in the collected file contents."
                    )

                else:

                    st.warning(
                        f"⚠️ {len(findings)} potential security finding(s) detected."
                    )

                    for index, finding in enumerate(
                        findings,
                        start=1,
                    ):

                        severity = (
                            finding.get("severity", "Medium")
                            .strip()
                            .upper()
                        )

                        if severity == "HIGH":
                            st.error(
                                f"🚨 HIGH — Finding #{index}"
                            )
                        elif severity == "MEDIUM":
                            st.warning(
                                f"⚠️ MEDIUM — Finding #{index}"
                            )
                        else:
                            st.info(
                                f"ℹ️ {severity} — Finding #{index}"
                            )

                        st.write(
                            f"**Type:** {finding.get('category', 'Unknown')}"
                        )

                        st.write(
                            f"**File:** `{finding.get('file', 'Unknown file')}`"
                        )

                        # Never expose a detected secret.
                        st.write("**Evidence:** `[REDACTED]`")

                        if finding.get("url"):
                            st.link_button(
                                "🌐 View Public File",
                                finding["url"],
                                use_container_width=True,
                            )

                        st.divider()

            # ------------------------------------------------
            # AI
            # ------------------------------------------------

            with tab_ai:

                if not analysis:
                    st.info(
                        "Analyze the repository to generate Gemini-powered insights."
                    )

                else:

                    ai_result = analysis.get("ai_analysis")

                    if not ai_result:
                        st.warning(
                            "AI analysis was not generated."
                        )

                    elif ai_result.get("status") == "success":

                        st.markdown(
                            "### 🧠 Gemini Security & Repository Insights"
                        )

                        st.markdown(
                            ai_result.get(
                                "analysis",
                                "No AI analysis returned.",
                            )
                        )

                    elif ai_result.get("status") == "ready":

                        st.info(
                            "The AI prompt is ready, but no LLM response "
                            "was returned yet."
                        )

                        with st.expander(
                            "View generated AI prompt"
                        ):
                            st.code(
                                ai_result.get("prompt", ""),
                                language="text",
                            )

                    else:

                        st.error(
                            "🤖 AI analysis could not be generated: "
                            + ai_result.get(
                                "message",
                                "Unknown error",
                            )
                        )

                        st.caption(
                            "Check your Gemini configuration in .env "
                            "and try again."
                        )

            st.markdown(
                "</div>",
                unsafe_allow_html=True,
            )

# ============================================================
# ANALYSIS HISTORY
# ============================================================

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

history_col1, history_col2 = st.columns([5, 1])

with history_col1:
    st.markdown(
        """
        <div class="glass-panel">
            <span class="section-icon">◷</span>
            <span class="panel-title">Analysis History</span>
            <div class="panel-subtitle">
                Previously analyzed public repositories
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with history_col2:
    if st.button(
        "📚 History",
        key="history_toggle",
        use_container_width=True,
    ):
        st.session_state.show_history = (
            not st.session_state.show_history
        )
        st.rerun()

if st.session_state.show_history:

    saved_repositories = get_saved_repositories()

    if not saved_repositories:
        st.info(
            "No repository analyses have been saved yet."
        )

    else:

        for saved in saved_repositories:

            saved_data = dict(saved)

            findings = get_security_findings(
                saved_data["id"]
            )

            c1, c2, c3, c4, c5 = st.columns(
                [3.1, 1, 1, 1.6, 1.3]
            )

            with c1:
                st.markdown(
                    f"""
                    <div class="history-row">
                        <div class="history-name">
                            📦 {safe_text(saved_data.get("full_name"))}
                        </div>
                        <div class="history-small">
                            {safe_text(
                                saved_data.get("description"),
                                "No description available."
                            )}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c2:
                st.metric(
                    "⭐ Stars",
                    saved_data.get("stars") or 0,
                )

            with c3:
                st.metric(
                    "🔐 Findings",
                    len(findings),
                )

            with c4:
                st.caption("Language")
                st.write(
                    saved_data.get("language")
                    or "Unknown"
                )

            with c5:
                if saved_data.get("url"):
                    st.link_button(
                        "View",
                        saved_data["url"],
                        use_container_width=True,
                    )

            st.caption(
                f"Analyzed: {saved_data.get('analyzed_at') or 'Unknown'}"
            )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="project-footer">
        <strong>AI GitHub Reconnaissance Chatbot</strong><br>
        Public-source analysis for educational and authorized security research
        &nbsp;•&nbsp;
        🔎 Discover
        &nbsp;•&nbsp;
        📊 Analyze
        &nbsp;•&nbsp;
        🛡️ Detect
        &nbsp;•&nbsp;
        🧠 AI Insights
        &nbsp;•&nbsp;
        🗄️ Record
    </div>
    """,
    unsafe_allow_html=True,
)
