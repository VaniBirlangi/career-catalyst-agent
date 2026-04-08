import ssl
import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context

import streamlit as st
import anthropic
from datetime import datetime, date
import json

st.set_page_config(
    page_title="Career Capital Agent",
    page_icon="⭐",
    layout="centered"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: #f1efe8;
        padding: 4px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 500;
        color: #5f5e5a;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ffffff !important;
        color: #185FA5 !important;
        border-bottom: none !important;
    }
    .metric-card { border-radius: 10px 10px 0 0; padding: 18px 12px 14px; text-align: center; }
    .metric-number { font-size: 32px; font-weight: 700; line-height: 1.2; }
    .metric-label  { font-size: 13px; margin-top: 6px; font-weight: 600; }
    .card-green { background: #EAF3DE; } .num-green { color: #27500A; } .lbl-green { color: #3B6D11; }
    .card-blue1 { background: #E6F1FB; } .num-blue1 { color: #0C447C; } .lbl-blue1 { color: #185FA5; }
    .card-blue2 { background: #B5D4F4; } .num-blue2 { color: #0C447C; } .lbl-blue2 { color: #0C447C; }
    .card-blue3 { background: #378ADD; } .num-blue3 { color: #ffffff; } .lbl-blue3 { color: #E6F1FB; }
    .card-gray  { background: #F1EFE8; } .num-gray  { color: #444441; } .lbl-gray  { color: #5F5E5A; }
    /* Card action buttons — coloured bottom strip, seamlessly attached to card */
    .card-btn-green div[data-testid="stButton"] button {
        background: #C0DD97 !important; color: #27500A !important; border: none !important;
        border-radius: 0 0 10px 10px !important; font-weight: 600 !important; font-size: 12px !important;
        min-height: 30px !important; margin-top: -4px !important;
    }
    .card-btn-green div[data-testid="stButton"] button:hover { background: #A8CC76 !important; }
    .card-btn-green-active div[data-testid="stButton"] button {
        background: #27500A !important; color: #ffffff !important; border: none !important;
        border-radius: 0 0 10px 10px !important; font-weight: 700 !important; font-size: 12px !important;
        min-height: 30px !important; margin-top: -4px !important;
    }
    .card-btn-blue div[data-testid="stButton"] button {
        background: #B5D4F4 !important; color: #0C447C !important; border: none !important;
        border-radius: 0 0 10px 10px !important; font-weight: 600 !important; font-size: 12px !important;
        min-height: 30px !important; margin-top: -4px !important;
    }
    .card-btn-blue div[data-testid="stButton"] button:hover { background: #8CBDE8 !important; }
    .card-btn-blue-active div[data-testid="stButton"] button {
        background: #185FA5 !important; color: #ffffff !important; border: none !important;
        border-radius: 0 0 10px 10px !important; font-weight: 700 !important; font-size: 12px !important;
        min-height: 30px !important; margin-top: -4px !important;
    }
    .card-btn-gray div[data-testid="stButton"] button {
        background: #E0DDD5 !important; color: #5F5E5A !important; border: none !important;
        border-radius: 0 0 10px 10px !important; font-weight: 600 !important; font-size: 12px !important;
        min-height: 30px !important; margin-top: -4px !important;
    }
    .card-btn-gray div[data-testid="stButton"] button:hover { background: #C8C4BA !important; }
    .card-btn-gray-active div[data-testid="stButton"] button {
        background: #5F5E5A !important; color: #ffffff !important; border: none !important;
        border-radius: 0 0 10px 10px !important; font-weight: 700 !important; font-size: 12px !important;
        min-height: 30px !important; margin-top: -4px !important;
    }
    .bullet-card { background: #f0f7ee; border-left: 4px solid #3B6D11; border-radius: 6px; padding: 12px 16px; margin-bottom: 8px; font-size: 14px; line-height: 1.6; }
    .yearend-card { background: #fff8f0; border-left: 4px solid #854F0B; border-radius: 6px; padding: 12px 16px; margin-bottom: 8px; font-size: 14px; line-height: 1.7; }
    .preview-card { background: #eef4fb; border-left: 3px solid #378ADD; border-radius: 6px; padding: 10px 14px; margin-top: 8px; font-size: 13px; line-height: 1.6; }
    .datapoint-card { background: #f5f0fe; border-left: 4px solid #534AB7; border-radius: 6px; padding: 10px 16px; margin-bottom: 8px; font-size: 14px; line-height: 1.6; }
    .star-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 4px; margin-top: 12px; }
    .s-label { color: #185FA5; } .t-label { color: #3B6D11; } .a-label { color: #854F0B; } .r-label { color: #A32D2D; }
    .okr-coverage-wrap { background: #EAF3DE; border-radius: 10px; padding: 16px 20px; margin-bottom: 16px; }
    .okr-coverage-title { font-size: 16px; font-weight: 700; color: #27500A; margin-bottom: 4px; }
    .okr-coverage-sub { font-size: 13px; color: #3B6D11; margin-bottom: 10px; }
    .okr-coverage-bar { background: #C0DD97; border-radius: 4px; height: 10px; width: 100%; margin-top: 6px; }
    .okr-coverage-fill { background: #3B6D11; border-radius: 4px; height: 10px; }
    .okr-version-tag { background: #E6F1FB; color: #0C447C; font-size: 11px; padding: 2px 10px; border-radius: 12px; font-weight: 500; display: inline-block; margin-bottom: 6px; }
    .mapping-tag { background: #EEEDFE; color: #3C3489; font-size: 11px; padding: 2px 10px; border-radius: 12px; font-weight: 500; display: inline-block; margin-top: 6px; }
    .warning-box { background: #FAEEDA; border-left: 4px solid #854F0B; border-radius: 6px; padding: 10px 16px; font-size: 13px; color: #633806; margin-bottom: 12px; }
    .info-box { background: #E6F1FB; border-left: 4px solid #185FA5; border-radius: 6px; padding: 10px 16px; font-size: 13px; color: #0C447C; margin-bottom: 12px; }
    .empty-state { text-align: center; padding: 2rem; color: #6c757d; font-size: 13px; background: #f8f9fa; border-radius: 8px; margin-bottom: 12px; }
    .section-header { font-size: 12px; font-weight: 600; color: #6c757d; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px; margin-top: 4px; }
    .grid-table { width: 100%; border-collapse: collapse; font-size: 13px; }
    .grid-table th { text-align: left; padding: 8px 12px; background: #f1efe8; color: #5f5e5a; font-weight: 600; }
    .grid-table td { padding: 10px 12px; border-bottom: 0.5px solid #e9ecef; vertical-align: top; color: #3d3d3a; line-height: 1.7; }
    .col-header { font-size: 11px; font-weight: 600; color: #6c757d; text-transform: uppercase; letter-spacing: 0.05em; padding-bottom: 6px; }
    div[data-testid="stButton"] button { min-height: 36px !important; }
    .icon-btn-wrap div[data-testid="stButton"] button {
        min-height: 32px !important;
        height: 32px !important;
        padding: 0 !important;
        font-size: 15px !important;
        line-height: 32px !important;
        border: 1px solid #e0ddd5 !important;
        background: #ffffff !important;
        border-radius: 6px !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }
    .icon-btn-wrap div[data-testid="stButton"] button:hover {
        border-color: #185FA5 !important;
        background: #E6F1FB !important;
    }
    .icon-btn-wrap div[data-testid="stButton"] button p {
        margin: 0 !important;
        line-height: 1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Demo mode flag ────────────────────────────
IS_DEMO = os.environ.get("IS_DEMO", "false").lower() == "true"

# ── Storage ───────────────────────────────────
DATA_FILE = "wins.json"

DEFAULT_DATA = {
    "profile": {"current_role": "", "target_role": ""},
    "okr_sets": [], "wins": []
}

def load_data():
    if IS_DEMO:
        # Session-based — no file, each visitor gets clean isolated data
        if "persistent_data" not in st.session_state:
            st.session_state.persistent_data = {
                "profile": {"current_role": "", "target_role": ""},
                "okr_sets": [], "wins": []
            }
        return st.session_state.persistent_data
    else:
        # File-based — permanent local storage
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return {
            "profile": {"current_role": "Data Engineering Manager", "target_role": "Senior EM, Data & AI at Microsoft"},
            "okr_sets": [], "wins": []
        }

def save_data(data):
    if IS_DEMO:
        # Save to session state only — no file write
        st.session_state.persistent_data = data
    else:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

def get_active_okr_set(data):
    return data["okr_sets"][-1] if data["okr_sets"] else None

# ── Session state ─────────────────────────────
for k, v in {
    "data": None, "show_log_win": False, "editing_win_id": None,
    "structured_output": None, "yearend_output": None,
    "show_okr_mapper": False, "dashboard_filter": "all",
    "custom_start": None, "custom_end": None, "wins_expanded": False, "yearend_year": None
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

if st.session_state.data is None:
    st.session_state.data = load_data()

data = st.session_state.data

# Auto-load latest win output
if not st.session_state.structured_output and data["wins"]:
    latest = data["wins"][-1]
    if latest.get("output"):
        st.session_state.structured_output = latest["output"]

# ── Prompts ───────────────────────────────────
def build_win_prompt(win, role, target, impact):
    return f"""You are a senior career coach specialising in Data & AI leadership roles.

The user is a {role} targeting a {target} role.
Impact area: {impact}
Their accomplishment: "{win}"

Return ONLY a valid JSON object with this exact structure — no markdown, no explanation, just the JSON:

{{
  "star_stories": [
    {{"title": "Story title", "angle": "e.g. Organizational scale", "situation": "...", "task": "...", "action": "...", "result": "..."}}
  ],
  "promotion_bullets": ["Bullet 1", "Bullet 2"],
  "interview_questions": [
    {{"question": "Question text", "why_relevant": "One sentence", "best_story": "Story title"}}
  ],
  "data_points": ["Crisp impact sentence 1"]
}}

Rules:
- Generate only as many STAR stories as are genuinely distinct and relevant — different angles only if they add real value. One strong story is better than three weak ones.
- Generate only promotion bullets that are truly impactful and differentiated. Skip generic ones.
- Generate only interview questions that are directly and meaningfully relevant to this specific accomplishment.
- Generate only data points that are crisp, metric-led, and genuinely useful for a year-end review.
- Each interview question must reference one of the story titles in best_story.
- Use only metrics provided — do not invent numbers.
- Quality over quantity in everything."""

def build_yearend_prompt(wins, role, okrs=""):
    wins_text = "\n".join([f"- [{w['impact']}] {w['win']}" for w in wins])
    if okrs.strip():
        return f"""You are a senior career coach helping a {role} write their year-end performance review.

OKRs / Goals:
{okrs}

Accomplishments:
{wins_text}

Return ONLY valid JSON — no markdown, no explanation:

{{
  "okr_mappings": [
    {{"okr": "Short OKR label max 8 words", "key_results": ["Impact-first sentence max 25 words", "Another result"]}}
  ]
}}

Rules: Each win under ONE OKR only. No duplicates. Impact first. No invented numbers. No summary."""
    else:
        return f"""You are a senior career coach helping a {role} write their year-end performance review.

Accomplishments:
{wins_text}

Return ONLY valid JSON — no markdown, no explanation:

{{
  "performance_themes": [
    {{"theme": "Theme name max 5 words", "key_results": ["Impact-first sentence max 25 words", "Another result"]}}
  ]
}}

Rules: Each win under ONE theme. No duplicates. 3-4 themes. Impact first. No invented numbers. No summary."""

def call_claude(prompt, key):
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(msg.content[0].text)

# ── Sidebar ───────────────────────────────────
with st.sidebar:
    st.markdown("## Career Agent")
    st.caption("v1.3 · Career Capital Agent")
    st.markdown("---")
    api_key = st.text_input("Anthropic API key", type="password", placeholder="sk-ant-...")
    st.markdown("### Your profile")
    current_role = st.text_input("Current role", value=data["profile"].get("current_role", "Data Engineering Manager"))
    target_role  = st.text_input("Target role",  value=data["profile"].get("target_role",  "Senior EM, Data & AI at Microsoft"))
    if current_role != data["profile"].get("current_role") or target_role != data["profile"].get("target_role"):
        data["profile"]["current_role"] = current_role
        data["profile"]["target_role"]  = target_role
        save_data(data)
    st.markdown("---")
    st.markdown("### Goals / OKRs")
    active_okr = get_active_okr_set(data)
    if active_okr:
        st.markdown(f'<div class="okr-version-tag">{active_okr["label"]} · {active_okr["date"]}</div>', unsafe_allow_html=True)
        okr_input = st.text_area("Your current goals", value=active_okr["okrs"], height=120, key="sidebar_okr")
    else:
        okr_input = st.text_area("Paste your goals / OKRs", placeholder="e.g.\n1. Build DQ capability\n2. Drive reliability", height=120, key="sidebar_okr")
    if st.button("Save Goals", use_container_width=True):
        if okr_input.strip():
            data["okr_sets"].append({"id": f"okr_{datetime.now().strftime('%Y%m%d_%H%M%S')}", "label": f"OKR Set {len(data['okr_sets'])+1}", "date": datetime.now().strftime("%Y-%m-%d"), "okrs": okr_input})
            save_data(data)
            st.success("Goals saved!")
            st.rerun()
        else:
            st.warning("Please enter your goals first.")
    if len(data["okr_sets"]) > 1:
        with st.expander("Goal version history"):
            for o in reversed(data["okr_sets"]):
                st.markdown(f'<div class="okr-version-tag">{o["label"]} · {o["date"]}</div>', unsafe_allow_html=True)
                st.caption(o["okrs"][:80] + "...")
    st.markdown("---")
    st.caption("Built with Streamlit + Claude API")

# ── Main ──────────────────────────────────────
st.markdown("## Career Capital Agent")
st.markdown("Turn your daily wins into promotion bullets, interview stories, and year-end reviews — before you forget them.")

if IS_DEMO:
    st.info("🔒 **Live demo** — your data resets when you close the browser. To save your wins permanently, [clone the repo and run locally](https://github.com/VaniBirlangi/career-catalyst-agent).")
st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)

# ── Log a Win ─────────────────────────────────
log_btn_label = "✏️  Update win" if st.session_state.editing_win_id else "＋  Log a Win"
col_log, _ = st.columns([2, 3])
with col_log:
    if st.button(log_btn_label, use_container_width=True, type="primary"):
        st.session_state.show_log_win = not st.session_state.show_log_win
        if not st.session_state.show_log_win:
            st.session_state.editing_win_id = None
        st.rerun()

if st.session_state.show_log_win:
    with st.container(border=True):
        impact_options = ["Technical delivery", "Leadership & people", "Cost savings", "Revenue / growth", "Process improvement", "Data & AI", "Other"]
        editing_win    = next((w for w in data["wins"] if w["id"] == st.session_state.editing_win_id), None) if st.session_state.editing_win_id else None
        default_impact = editing_win["impact"] if editing_win else "Technical delivery"
        default_win    = editing_win["win"]    if editing_win else ""
        impact_area = st.selectbox("Impact area", impact_options, index=impact_options.index(default_impact), key="log_impact")
        win_input   = st.text_area("Describe your win", value=default_win, placeholder="e.g. Built Enterprise Data Quality Engineering team from the ground up...", height=120, key="log_win_text")
        if st.button("Generate career capital", type="primary", use_container_width=True, key="log_generate"):
            if not api_key:
                st.warning("Please enter your Anthropic API key in the sidebar.")
            elif not win_input.strip():
                st.warning("Please describe your win before generating.")
            else:
                with st.spinner("Generating your career capital..."):
                    try:
                        structured = call_claude(build_win_prompt(win_input, current_role, target_role, impact_area), api_key)
                        st.session_state.structured_output = structured
                        st.session_state.show_okr_mapper   = False
                        st.session_state.yearend_output    = None
                        if editing_win:
                            for w in data["wins"]:
                                if w["id"] == editing_win["id"]:
                                    w["win"] = win_input; w["impact"] = impact_area; w["output"] = structured; break
                            st.session_state.editing_win_id = None
                        else:
                            active_okr_now = get_active_okr_set(data)
                            data["wins"].append({"id": f"win_{datetime.now().strftime('%Y%m%d_%H%M%S')}", "date": datetime.now().strftime("%Y-%m-%d %H:%M"), "win": win_input, "impact": impact_area, "okr_set_id": active_okr_now["id"] if active_okr_now else None, "output": structured})
                        save_data(data)
                        st.session_state.data = data
                        st.session_state.show_log_win = False
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("Claude returned an unexpected format. Please try again.")
                    except Exception as e:
                        st.error(f"Something went wrong: {str(e)}")
        if st.session_state.editing_win_id:
            if st.button("Cancel edit", use_container_width=True):
                st.session_state.editing_win_id = None
                st.session_state.show_log_win   = False
                st.rerun()

st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

all_wins = data["wins"]
now = datetime.now()
current_month  = now.strftime("%Y-%m")
q_start        = ((now.month-1)//3)*3+1
quarter_months = [f"{now.year}-{str(m).zfill(2)}" for m in range(q_start, q_start+3)]
current_year   = str(now.year)
wins_month     = [w for w in all_wins if w["date"][:7] == current_month]
wins_quarter   = [w for w in all_wins if w["date"][:7] in quarter_months]
wins_year      = [w for w in all_wins if w["date"][:4] == current_year]
wins_custom    = []
if st.session_state.custom_start and st.session_state.custom_end:
    wins_custom = [w for w in all_wins if st.session_state.custom_start.strftime("%Y-%m-%d") <= w["date"][:10] <= st.session_state.custom_end.strftime("%Y-%m-%d")]

# ── Metric cards ──────────────────────────────
active = st.session_state.dashboard_filter
col1, col2, col3, col4, col5 = st.columns(5)

def metric_card(col, card_class, num_class, lbl_class, count, label, filter_key, btn_base, btn_active):
    with col:
        is_active = active == filter_key
        btn_css   = btn_active if is_active else btn_base
        btn_label = f"✓ Viewing" if is_active else "View"
        if label == "Custom" and not is_active:
            btn_label = "Pick dates"
        st.markdown(
            f'<div class="metric-card {card_class}">'
            f'<div class="metric-number {num_class}">{count}</div>'
            f'<div class="metric-label {lbl_class}">{label}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown(f'<div class="{btn_css}">', unsafe_allow_html=True)
        if st.button(btn_label, key=f"btn_{filter_key}", use_container_width=True):
            st.session_state.dashboard_filter = filter_key
            st.session_state.wins_expanded = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

metric_card(col1, "card-green", "num-green", "lbl-green", len(all_wins),    "Total wins",   "all",     "card-btn-green",  "card-btn-green-active")
metric_card(col2, "card-blue1", "num-blue1", "lbl-blue1", len(wins_month),  "This month",   "month",   "card-btn-blue",   "card-btn-blue-active")
metric_card(col3, "card-blue2", "num-blue2", "lbl-blue2", len(wins_quarter),"This quarter", "quarter", "card-btn-blue",   "card-btn-blue-active")
metric_card(col4, "card-blue3", "num-blue3", "lbl-blue3", len(wins_year),   "This year",    "year",    "card-btn-blue",   "card-btn-blue-active")
metric_card(col5, "card-gray",  "num-gray",  "lbl-gray",  len(wins_custom) if active=="custom" else "—", "Custom", "custom", "card-btn-gray", "card-btn-gray-active")

if active == "custom":
    cc1, cc2 = st.columns(2)
    with cc1:
        start = st.date_input("From", value=st.session_state.custom_start or date(now.year,1,1))
        st.session_state.custom_start = start
    with cc2:
        end = st.date_input("To", value=st.session_state.custom_end or date.today())
        st.session_state.custom_end = end
    wins_custom = [w for w in all_wins if start.strftime("%Y-%m-%d") <= w["date"][:10] <= end.strftime("%Y-%m-%d")]

filter_map   = {"all": all_wins, "month": wins_month, "quarter": wins_quarter, "year": wins_year, "custom": wins_custom}
filter_label = {"all": "All wins", "month": "This month", "quarter": "This quarter", "year": "This year", "custom": "Custom range"}
filtered_wins = filter_map[active]

st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

# ── All Wins — collapsible, auto-expands on filter click ────
with st.expander(f"{filter_label[active]} — {len(filtered_wins)} win(s)", expanded=st.session_state.wins_expanded):
    st.session_state.wins_expanded = False  # reset after render so manual close works
    if filtered_wins:
        h1, h2, h3, h4 = st.columns([2, 2, 4.5, 1.5])
        with h1: st.markdown('<div class="col-header">Impact area</div>', unsafe_allow_html=True)
        with h2: st.markdown('<div class="col-header">Date</div>', unsafe_allow_html=True)
        with h3: st.markdown('<div class="col-header">Win</div>', unsafe_allow_html=True)
        with h4: st.markdown('<div class="col-header"></div>', unsafe_allow_html=True)
        st.markdown('<div style="border-bottom:1px solid #e9ecef;margin-bottom:4px;"></div>', unsafe_allow_html=True)
        for w in reversed(filtered_wins):
            c1, c2, c3, c4 = st.columns([2, 2, 4.5, 1.5])
            with c1: st.markdown(f'<div style="font-size:12px;color:#185FA5;font-weight:500;padding:6px 0;">{w["impact"]}</div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div style="font-size:12px;color:#6c757d;padding:6px 0;">{w["date"][:10]}</div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div style="font-size:13px;color:#3d3d3a;padding:6px 0;">{w["win"][:90]}{"..." if len(w["win"])>90 else ""}</div>', unsafe_allow_html=True)
            with c4:
                st.markdown('<div class="icon-btn-wrap">', unsafe_allow_html=True)
                ec, dc = st.columns(2)
                with ec:
                    if st.button("✏️", key=f"edit_{w['id']}", help="Edit", use_container_width=True):
                        st.session_state.editing_win_id = w["id"]
                        st.session_state.show_log_win   = True
                        st.rerun()
                with dc:
                    if st.button("🗑", key=f"del_{w['id']}", help="Delete", use_container_width=True):
                        data["wins"] = [x for x in data["wins"] if x["id"] != w["id"]]
                        save_data(data)
                        st.session_state.data = data
                        st.session_state.structured_output = data["wins"][-1]["output"] if data["wins"] else None
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div style="border-bottom:0.5px solid #f1efe8;"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-state">No wins in this period yet</div>', unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)

# ── Career Capital tabs ───────────────────────
st.markdown("---")
st.markdown("### Your career capital")

tab1, tab2, tab3, tab4 = st.tabs(["Year-end Review", "Promotion Bullets", "Interview Prep", "Story Bank"])

# ── Tab 1: Year-end Review ───────────────────
with tab1:
    active_okr_ye = get_active_okr_set(data)
    if active_okr_ye and all_wins:
        okr_lines_ye  = [l.strip() for l in active_okr_ye["okrs"].split("\n") if l.strip()]
        wins_w_okr_ye = [w for w in all_wins if w.get("okr_set_id") == active_okr_ye["id"]]
        covered_ye    = min(len(wins_w_okr_ye), len(okr_lines_ye))
        pct_ye        = int((covered_ye / len(okr_lines_ye)) * 100) if okr_lines_ye else 0
        st.markdown(f"""<div class="okr-coverage-wrap">
            <div class="okr-coverage-title">OKR Coverage — {pct_ye}%</div>
            <div class="okr-coverage-sub">{covered_ye} of {len(okr_lines_ye)} goals have wins logged{"  ·  "+str(len(okr_lines_ye)-covered_ye)+" goal(s) still need wins" if pct_ye < 100 else "  ·  All goals covered!"}</div>
            <div class="okr-coverage-bar"><div class="okr-coverage-fill" style="width:{pct_ye}%"></div></div>
        </div>""", unsafe_allow_html=True)

    all_data_points = []
    all_dp_rows = ""
    all_dp_text = ""
    for w in reversed(data["wins"]):
        dps = w.get("output", {}).get("data_points", [])
        for didx, dp in enumerate(dps):
            bg = "#ffffff" if didx % 2 == 0 else "#f8f9fa"
            all_dp_rows += f'<tr><td style="padding:8px 12px;border-bottom:0.5px solid #e9ecef;font-size:12px;color:#6c757d;vertical-align:top;width:28%;background:{bg};">{w["win"][:55]}{"..." if len(w["win"])>55 else ""}<br><span style="font-size:11px;color:#B4B2A9;">{w["date"][:10]}</span></td><td style="padding:8px 12px;border-bottom:0.5px solid #e9ecef;font-size:13px;color:#3d3d3a;line-height:1.6;background:{bg};">{dp}</td></tr>'
            all_dp_text += f"{dp}\n\n"
            all_data_points.append(dp)
    if all_data_points:
        total_dp_count = len(all_data_points)
        with st.expander(f"Data Points for your Year-end Performance Review — {total_dp_count} across all wins", expanded=False):
            st.markdown(f'<table class="grid-table"><thead><tr><th>Win</th><th>Year-end data point</th></tr></thead><tbody>{all_dp_rows}</tbody></table>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("Download all data points", data=all_dp_text.strip(), file_name="all_data_points.txt", mime="text/plain", key="dl_dp")

    if not all_wins:
        st.markdown('<div class="empty-state">Log your first win to generate your year-end review</div>', unsafe_allow_html=True)
    else:
        active_okr_check = get_active_okr_set(data)
        if not st.session_state.show_okr_mapper:
            btn_label_ye = "Map wins to my OKRs → generate year-end review" if active_okr_check else "Group wins by theme → generate year-end review"
            if st.button(btn_label_ye, type="primary", use_container_width=True):
                st.session_state.show_okr_mapper = True
                st.rerun()
        else:
            active_okr = get_active_okr_set(data)
            okr_text   = active_okr["okrs"] if active_okr else ""
            if active_okr:
                st.markdown(f'<div class="okr-version-tag">Using: {active_okr["label"]} · {active_okr["date"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">No goals saved yet. Add them in the sidebar.</div>', unsafe_allow_html=True)
            all_years     = sorted(set(w["date"][:4] for w in data["wins"]), reverse=True)
            selected_year = st.selectbox("Generate review for year", all_years)
            year_wins     = [w for w in data["wins"] if w["date"][:4] == selected_year]
            st.caption(f"{len(year_wins)} win(s) in {selected_year}")
            if st.button("Generate year-end review", type="primary", use_container_width=True, key="ye_btn"):
                if not api_key:
                    st.warning("Please enter your API key in the sidebar.")
                else:
                    with st.spinner("Generating..."):
                        try:
                            ye = call_claude(build_yearend_prompt(year_wins, current_role, okr_text), api_key)
                            st.session_state.yearend_output = ye
                            st.session_state.yearend_year = selected_year
                        except Exception as e:
                            st.error(f"Something went wrong: {str(e)}")

        if st.session_state.yearend_output:
            ye   = st.session_state.yearend_output
            rows = ""
            full = ""
            mappings = ye.get("okr_mappings") or ye.get("performance_themes") or []
            key_name = "okr" if "okr_mappings" in ye else "theme"
            col_header = "OKR / Goal" if "okr_mappings" in ye else "Theme"
            for idx, item in enumerate(mappings):
                goal    = item.get(key_name, "")
                results = item.get("key_results", [])
                for ridx, result in enumerate(results):
                    bg        = "#ffffff" if idx % 2 == 0 else "#f8f9fa"
                    goal_cell = f'<td style="padding:10px 12px;border-bottom:0.5px solid #e9ecef;vertical-align:top;font-weight:500;color:#185FA5;width:30%;background:{bg};">{goal}</td>' if ridx == 0 else f'<td style="padding:2px 12px 10px;border-bottom:0.5px solid #e9ecef;background:{bg};"></td>'
                    rows += f'<tr>{goal_cell}<td style="padding:10px 12px;border-bottom:0.5px solid #e9ecef;color:#3d3d3a;line-height:1.7;background:{bg};">{result}</td></tr>'
                    full += f"{goal}: {result}\n"
            review_year = st.session_state.get("yearend_year", str(now.year))
            if rows:
                st.markdown(f'<table class="grid-table"><thead><tr><th>{col_header}</th><th>Key results</th></tr></thead><tbody>{rows}</tbody></table>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button("Download year-end review", data=full, file_name=f"yearend_{review_year}.txt", mime="text/plain", use_container_width=True)

# ── Tab 2: Promotion Bullets ─────────────────
with tab2:
    all_bullets_rows = ""
    all_bullets_text = ""
    has_bullets = False
    for w in reversed(data["wins"]):
        for bidx, bullet in enumerate(w.get("output", {}).get("promotion_bullets", [])):
            has_bullets = True
            bg = "#ffffff" if bidx % 2 == 0 else "#f8f9fa"
            all_bullets_rows += f'<tr><td style="padding:8px 12px;border-bottom:0.5px solid #e9ecef;font-size:12px;color:#6c757d;vertical-align:top;width:28%;background:{bg};">{w["win"][:55]}{"..." if len(w["win"])>55 else ""}<br><span style="font-size:11px;color:#B4B2A9;">{w["date"][:10]}</span></td><td style="padding:8px 12px;border-bottom:0.5px solid #e9ecef;font-size:13px;color:#3d3d3a;line-height:1.6;background:{bg};">{bullet}</td></tr>'
            all_bullets_text += f"{bullet}\n\n"
    if has_bullets:
        with st.expander(f"All promotion bullets — {sum(len(w.get('output',{}).get('promotion_bullets',[])) for w in data['wins'])} bullets", expanded=False):
            st.markdown(f'<table class="grid-table"><thead><tr><th>Win</th><th>Promotion bullet</th></tr></thead><tbody>{all_bullets_rows}</tbody></table>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button("Download all bullets", data=all_bullets_text, file_name="all_promotion_bullets.txt", mime="text/plain", use_container_width=True)
    else:
        st.markdown('<div class="empty-state">Log a win to see your promotion bullets here</div>', unsafe_allow_html=True)

# ── Tab 3: Interview Prep ─────────────────────
with tab3:
    output_data = st.session_state.structured_output
    if not output_data or not output_data.get("interview_questions"):
        st.markdown('<div class="empty-state">Log a win to generate interview questions</div>', unsafe_allow_html=True)
    else:
        story_lookup = {s["title"]: s for s in output_data.get("star_stories", [])}
        st.markdown('<div class="section-header">Questions mapped to your best story — latest win</div>', unsafe_allow_html=True)
        for i, q in enumerate(output_data.get("interview_questions", [])):
            with st.expander(f"Q{i+1}: {q['question']}", expanded=False):
                st.markdown(f"**Why this matters:** {q['why_relevant']}")
                st.markdown(f'<div class="mapping-tag">Best answered with → {q["best_story"]}</div>', unsafe_allow_html=True)
                matched = story_lookup.get(q["best_story"])
                if matched:
                    with st.expander(f"Preview: {matched['title']}", expanded=False):
                        for label, key, cls in [("Situation","situation","s-label"),("Task","task","t-label"),("Action","action","a-label"),("Result","result","r-label")]:
                            st.markdown(f'<div class="star-label {cls}">{label}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="preview-card">{matched[key]}</div>', unsafe_allow_html=True)

# ── Tab 4: Story Bank ─────────────────────────
with tab4:
    all_stories = []
    for w in reversed(data["wins"]):
        for s in w.get("output", {}).get("star_stories", []):
            all_stories.append({"win_date": w["date"][:10], "win_impact": w["impact"], "win_title": w["win"], **s})
    if all_stories:
        st.markdown(f'<div class="section-header">{len(all_stories)} STAR stories across all wins</div>', unsafe_allow_html=True)
        for i, story in enumerate(all_stories):
            with st.expander(f"{story['title']}  ·  {story['angle']}  ·  {story['win_date']}", expanded=False):
                for label, key, cls in [("Situation","situation","s-label"),("Task","task","t-label"),("Action","action","a-label"),("Result","result","r-label")]:
                    st.markdown(f'<div class="star-label {cls}">{label}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="preview-card">{story[key]}</div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                story_text = f"STORY: {story['title']}\nAngle: {story['angle']}\nDate: {story['win_date']}\n\nSituation: {story['situation']}\n\nTask: {story['task']}\n\nAction: {story['action']}\n\nResult: {story['result']}"
                st.download_button("Download this story", data=story_text, file_name=f"story_{i+1}.txt", mime="text/plain", key=f"dl_story_{i}")
    else:
        st.markdown('<div class="empty-state">Log a win to build your story library</div>', unsafe_allow_html=True)
