#app.py
import streamlit.components.v1 as components
import streamlit as st
import tempfile
import os
import base64
import time
from pathlib import Path

st.set_page_config(
    page_title            = "AI Resume Matcher",
    page_icon             = "🎯",
    layout                = "wide",
    initial_sidebar_state = "collapsed",
)

from core import analyze_job, parse_resume, get_match_score, read_resume_file


# ── Load aurora image as base64 ───────────────────────────────────────────────
def _aurora_uri() -> str:
    p = Path(__file__).parent / "aurora_bg.png"
    if not p.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()

AURORA = _aurora_uri()


# ── PART 1: Background layer ──────────────────────────────────────────────────
st.markdown(f"""
<style>
html, body {{
    background: #000000 !important;
    margin: 0 !important;
    padding: 0 !important;
}}

body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background: url('{AURORA}') no-repeat bottom center / cover;
    z-index: 0;
    pointer-events: none;
    animation: auroraPulse 9s ease-in-out infinite alternate;
    transform-origin: bottom center;
}}

@keyframes auroraPulse {{
    0%   {{ opacity:0.80; transform:scale(1.000); filter:brightness(0.85) saturate(0.90) hue-rotate(0deg);  }}
    28%  {{ opacity:1.00; transform:scale(1.048); filter:brightness(1.18) saturate(1.32) hue-rotate(12deg); }}
    62%  {{ opacity:0.92; transform:scale(1.055); filter:brightness(1.08) saturate(1.18) hue-rotate(-8deg); }}
    100% {{ opacity:0.84; transform:scale(1.022); filter:brightness(0.92) saturate(1.00) hue-rotate(5deg);  }}
}}
</style>
""", unsafe_allow_html=True)


# ── PART 2: UI Styling & Translucent Cards ────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

#MainMenu, footer, header,
.stDeployButton, [data-testid="stToolbar"] { visibility: hidden !important; }
*, *::before, *::after { font-family: 'Space Grotesk', sans-serif !important; }

.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stSidebar"],
section.main, section.main > div, section.main > div > div, [data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"], [data-testid="block-container"], div[data-testid="stHorizontalBlock"],
[data-testid="column"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="block-container"] {
    position: relative !important;
    z-index: 10 !important;
    padding: 3.5rem 2rem 5rem !important; 
    max-width: 1250px !important;
    margin: 0 auto !important;
}

/* ── Hero Title ── */
.hero-title {
    text-align: center;
    font-size: clamp(3rem, 5.5vw, 4.8rem);
    font-weight: 800;
    letter-spacing: -1.5px;
    background: linear-gradient(135deg, #f0abfc 0%, #c084fc 35%, #818cf8 65%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    line-height: 1.1;
}
.hero-sub {
    text-align: center;
    color: rgba(220, 200, 255, 0.6);
    font-size: 0.85rem;
    letter-spacing: 5px;
    text-transform: uppercase;
    font-weight: 500;
    margin-bottom: 3.5rem;
}
.s-label {
    display: block;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(230, 180, 255, 0.9);
    margin-bottom: 1.2rem;
}

/* ── Job Description Textarea ── */
.stTextArea textarea {
    background: rgba(21, 21, 26, 0.75) !important;
    border: 1px solid #29292d !important;
    border-radius: 12px !important;
    height: 270px !important;
    min-height: 270px !important;
    padding: 1.5rem !important;
    color: #f1f1f5 !important;
    font-size: 0.92rem !important;
    line-height: 1.6 !important;
    resize: none !important;
    caret-color: #c084fc !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
}
.stTextArea textarea:focus {
    outline: none !important;
    border-color: #43434b !important;
}

/* ═════════════════════════════════════════════════════════════════
   DROPZONE: MATCHING TRANSLUCENT BACKGROUND
   ═════════════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: transparent !important;
    padding: 0 !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: rgba(21, 21, 26, 0.75) !important;
    border: 1px solid #29292d !important;
    border-radius: 12px !important;
    min-height: 270px !important;
    height: 270px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    cursor: pointer !important;
    transition: border-color 0.25s ease !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #43434b !important;
}

/* Eradicate native buttons and residual pills completely */
[data-testid="stFileUploader"] button {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
    position: absolute !important;
    left: -9999px !important;
}

/* Kill default cloud icon */
[data-testid="stFileUploaderDropzone"] svg {
    display: none !important;
}

/* Folder icon */
[data-testid="stFileUploaderDropzoneInstructions"]::before {
    content: '' !important;
    display: block !important;
    width: 50px !important;
    height: 42px !important;
    margin: 0 auto 16px auto !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%234a4a50'%3E%3Cpath d='M19.5 21a3 3 0 0 0 3-3v-4.5a3 3 0 0 0-3-3h-15a3 3 0 0 0-3 3V18a3 3 0 0 0 3 3h15ZM1.5 10.146V6a3 3 0 0 1 3-3h5.379a2.25 2.25 0 0 1 1.59.659l2.122 2.121c.14.141.331.22.53.22H19.5a3 3 0 0 1 3 3v1.146A4.483 4.483 0 0 0 19.5 9h-15a4.483 4.483 0 0 0-3 1.146Z'/%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-size: contain !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
    width: 100% !important;
}

/* Hide native text */
[data-testid="stFileUploaderDropzoneInstructions"] > div > span,
[data-testid="stFileUploaderDropzoneInstructions"] > div > small {
    display: none !important;
}

/* Clean text replacement */
[data-testid="stFileUploaderDropzoneInstructions"] > div::before {
    content: 'Drag & Drop or Click to upload file(s)' !important;
    display: block !important;
    color: #ffffff !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    margin-bottom: 4px !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] > div::after {
    content: 'or, click to browse (200 MB max)' !important;
    display: block !important;
    color: #797982 !important;
    font-size: 0.85rem !important;
    margin-bottom: 4px !important;
}

/* Uploaded file badge */
[data-testid="stUploadedFile"] {
    background: rgba(24, 24, 28, 0.85) !important;
    border: 1px solid #2a2a30 !important;
    border-radius: 8px !important;
    margin-top: 12px !important;
}

/* ── MAIN ANALYSE BUTTON (Protected and Forced Visible) ── */
div.stButton > button {
    display: inline-flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: linear-gradient(135deg, #a855f7 0%, #7c3aed 40%, #4f46e5 80%, #3b82f6 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 1rem 0 !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    box-shadow: 0 8px 30px rgba(147, 51, 234, 0.45) !important;
    transition: all 0.25s ease !important;
}
div.stButton > button:hover {
    box-shadow: 0 12px 40px rgba(147, 51, 234, 0.7) !important;
    transform: translateY(-2px) scale(1.01) !important;
}

/* ── Results Cards ── */
.glass-card {
    background: rgba(14, 6, 30, 0.65);
    border: 1px solid rgba(200, 130, 255, 0.2);
    border-radius: 20px;
    padding: 2.2rem 2.5rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    height: 100%;
}
.i-row {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    padding: 0.65rem 0;
    border-bottom: 1px solid rgba(200, 130, 255, 0.08);
    color: rgba(235, 215, 255, 0.85);
    font-size: 0.95rem;
    line-height: 1.45;
}
.i-icon { min-width: 1.4rem; text-align: center; }
.tags { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.5rem 0 1.2rem; }
.tag {
    display: inline-flex; align-items: center; gap: 0.28rem;
    padding: 0.35rem 0.95rem; border-radius: 20px;
    font-size: 0.8rem; font-weight: 500;
}
.ok { background: rgba(52,211,153,0.12); border: 1px solid rgba(52,211,153,0.35); color: #6ee7b7; }
.no { background: rgba(239,68,68,0.12); border: 1px solid rgba(239,68,68,0.35); color: #fca5a5; }
.verdict {
    background: rgba(120, 40, 220, 0.12);
    border: 1px solid rgba(180, 90, 255, 0.25);
    border-radius: 14px;
    padding: 1.4rem;
    color: rgba(245, 235, 255, 0.9);
    font-size: 0.95rem;
    line-height: 1.7;
    margin-top: 1.5rem;
}
.divider {
    height: 1px; margin: 3.5rem 0; border: none;
    background: linear-gradient(90deg, transparent, rgba(200, 100, 255, 0.4), transparent);
}
</style>
""", unsafe_allow_html=True)


# ── DOM Guardian: ONLY targets the file uploader dropzone button ──────────────
components.html("""
<script>
const killUploaderButton = () => {
    const root = window.parent.document;
    const dropzone = root.querySelector('[data-testid="stFileUploaderDropzone"]');
    if (dropzone) {
        const btns = dropzone.querySelectorAll('button');
        btns.forEach(btn => btn.remove());
    }
};

killUploaderButton();
const observer = new MutationObserver(() => killUploaderButton());
observer.observe(window.parent.document.body, { childList: true, subtree: true });
</script>
""", height=0)


# ── Helper: SVG Score Ring ────────────────────────────────────────────────────
def score_ring(score: float) -> str:
    score = max(0.0, min(100.0, float(score)))
    R   = 78
    C   = 2 * 3.14159265 * R
    off = C * (1 - score / 100)
    if score >= 70: color, label = "#34d399", "Strong Match 🚀"
    elif score >= 45: color, label = "#f59e0b", "Moderate Match ⚡"
    else: color, label = "#f87171", "Weak Match ⚠️"
    return f"""
<div style="display:flex;flex-direction:column;align-items:center;padding:1rem 0 0.5rem;">
  <svg width="215" height="215" viewBox="0 0 200 200">
    <circle cx="100" cy="100" r="{R}" fill="none" stroke="rgba(200,130,255,0.15)" stroke-width="13"/>
    <circle cx="100" cy="100" r="{R}" fill="none" stroke="{color}" stroke-width="13"
            stroke-dasharray="{C:.2f}" stroke-dashoffset="{off:.2f}" stroke-linecap="round"
            transform="rotate(-90 100 100)" style="filter:drop-shadow(0 0 12px {color}); transition:stroke-dashoffset 1.2s ease;"/>
    <text x="100" y="93" text-anchor="middle" font-size="38" font-weight="700" fill="white" font-family="Space Grotesk,sans-serif">{int(score)}%</text>
    <text x="100" y="115" text-anchor="middle" font-size="10" fill="rgba(220,180,255,0.40)" font-family="Space Grotesk,sans-serif" letter-spacing="1.8">MATCH SCORE</text>
  </svg>
  <div style="color:{color};font-size:0.95rem;font-weight:600;letter-spacing:0.8px;margin-top:-0.2rem;">{label}</div>
</div>"""

def tags_html(skills: list, ok: bool) -> str:
    icon, cls = ("✓", "ok") if ok else ("✗", "no")
    pills = "".join(f'<span class="tag {cls}">{icon} {s}</span>' for s in skills)
    return f'<div class="tags">{pills}</div>'


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">LLM-Based Profile Evaluator & Matcher</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">OpenAI GPT-OSS-120B &nbsp;·&nbsp; Pydantic</div>', unsafe_allow_html=True)

# ── Inputs ────────────────────────────────────────────────────────────────────
col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.markdown('<span class="s-label">&nbsp;Upload Resume(s)</span>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "resume",
        type             = ["pdf", "docx"],
        accept_multiple_files = True,
        label_visibility = "collapsed"
    )

with col_r:
    st.markdown('<span class="s-label">&nbsp;Job Description</span>', unsafe_allow_html=True)
    jd_text = st.text_area(
        "jd",
        height           = 270,
        placeholder      = "Paste the full job description here…\n\nTip: Include required skills, experience level, and responsibilities.",
        label_visibility = "collapsed"
    )

st.markdown("<br><br>", unsafe_allow_html=True)

_, btn_col, _ = st.columns([1, 1.2, 1])
with btn_col:
    go = st.button("Analyse Match⚡", use_container_width=True)


# ── Batch Analysis ────────────────────────────────────────────────────────────
if go:
    if not uploaded_files:
        st.error("⚠️Please upload at least one resume (PDF or DOCX).")
    elif not jd_text.strip():
        st.error("⚠️Please paste a job description.")
    else:
        try:
            with st.spinner("Analysing pasted job description...🔍"):
                job = analyze_job(jd_text)

            results = []

            for idx, uploaded_file in enumerate(uploaded_files):
                suffix   = Path(uploaded_file.name).suffix
                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name

                    with st.spinner(f"[{idx+1}/{len(uploaded_files)}] Reading file: {uploaded_file.name}...📖"):
                        raw_text = read_resume_file(tmp_path)
                    
                    with st.spinner(f"[{idx+1}/{len(uploaded_files)}] Parsing candidate profile...⏳"):
                        resume = parse_resume(raw_text)
                    
                    time.sleep(5)
                    
                    with st.spinner(f"[{idx+1}/{len(uploaded_files)}] Calculating match score...🧮"):
                        result = get_match_score(job, resume)
                    
                    time.sleep(5)
                    
                    results.append({
                        "file_name": uploaded_file.name,
                        "resume": resume,
                        "score": float(result.score),
                        "details": result.details
                    })

                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            
            results.sort(key=lambda x: x["score"], reverse=True)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            st.markdown('<span class="s-label">🏆 &nbsp;Candidate Leaderboard</span>', unsafe_allow_html=True)
            leaderboard_html = """
            <div class="glass-card" style="margin-bottom: 3rem;">
                <table style="width: 100%; border-collapse: collapse; color: rgba(235, 215, 255, 0.85); font-size: 0.95rem;">
                    <tr style="border-bottom: 1px solid rgba(200, 130, 255, 0.22); text-align: left;">
                        <th style="padding: 12px; color: rgba(230, 180, 255, 0.9); font-weight: 600; text-transform: uppercase; letter-spacing: 2px; font-size: 0.7rem;">Rank</th>
                        <th style="padding: 12px; color: rgba(230, 180, 255, 0.9); font-weight: 600; text-transform: uppercase; letter-spacing: 2px; font-size: 0.7rem;">Candidate</th>
                        <th style="padding: 12px; color: rgba(230, 180, 255, 0.9); font-weight: 600; text-transform: uppercase; letter-spacing: 2px; font-size: 0.7rem;">Experience</th>
                        <th style="padding: 12px; color: rgba(230, 180, 255, 0.9); font-weight: 600; text-transform: uppercase; letter-spacing: 2px; font-size: 0.7rem;">Score</th>
                    </tr>
            """
            
            for rank, res in enumerate(results, 1):
                c_name = res["details"].get("candidate_name") or res["resume"].name or "Unknown Candidate"
                exp_yrs = res["resume"].total_experience_years
                exp_str = f"{exp_yrs} yrs" if exp_yrs is not None else "N/A"
                score_val = res["score"]
                score_color = "#34d399" if score_val >= 70 else "#f59e0b" if score_val >= 45 else "#f87171"
                
                leaderboard_html += f"""
                    <tr style="border-bottom: 1px solid rgba(200, 130, 255, 0.08);">
                        <td style="padding: 12px; font-weight: bold; color: rgba(230, 180, 255, 0.9);">#{rank}</td>
                        <td style="padding: 12px; font-weight: 500; color: #fff;">{c_name}</td>
                        <td style="padding: 12px;">{exp_str}</td>
                        <td style="padding: 12px; font-weight: bold; color: {score_color};">{int(score_val)}%</td>
                    </tr>
                """
            leaderboard_html += "</table></div>"
            st.markdown(leaderboard_html, unsafe_allow_html=True)

            for rank, res in enumerate(results, 1):
                st.markdown(f'<span class="s-label">🏅 &nbsp;Rank #{rank} Detailed Breakdown</span>', unsafe_allow_html=True)
                
                d = res["details"]
                score = res["score"]
                resume = res["resume"]
                
                res_l, res_r = st.columns([1, 1.6], gap="large")

                with res_l:
                    name    = d.get("candidate_name") or resume.name or "N/A"
                    email   = resume.email  or "N/A"
                    phone   = resume.phone  or "N/A"
                    exp_yrs = resume.total_experience_years
                    exp_met = d.get("experience_met", False)
                    
                    rows_html = "".join([
                        f'<div class="i-row"><span class="i-icon">{icon}</span>{text}</div>' for icon, text in [
                            ("👤", name), ("📧", email), ("📱", phone),
                            ("🕐", f"{exp_yrs} yr(s) experience" if exp_yrs is not None else "Experience not specified"),
                            ("✅" if exp_met else "❌", "Experience requirement met" if exp_met else "Experience requirement not met")
                        ]
                    ])

                    st.markdown(f"""
                    <div class="glass-card">
                        <span class="s-label">🎯 &nbsp;Match Score</span>
                        {score_ring(score)}
                        <br>
                        {rows_html}
                    </div>
                    """, unsafe_allow_html=True)

                with res_r:
                    matching = d.get("matching_skills", [])
                    missing  = d.get("missing_skills",  [])
                    verdict  = d.get("verdict", "")

                    match_sec = f"**Matching Skills**<br>{tags_html(matching, True)}" if matching else ""
                    miss_sec  = f"**Missing Skills**<br>{tags_html(missing, False)}" if missing else ""
                    verd_sec  = f'<div class="verdict">📋 &nbsp;{verdict}</div>' if verdict else ""

                    st.markdown(f"""
                    <div class="glass-card" style="display:flex; flex-direction:column; justify-content:center;">
                        <span class="s-label">🧩 &nbsp;Skill Analysis</span>
                        {match_sec}
                        {miss_sec}
                        {verd_sec}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br><br>", unsafe_allow_html=True)

        except Exception as err:
            st.error(f"Something went wrong: {err}")
