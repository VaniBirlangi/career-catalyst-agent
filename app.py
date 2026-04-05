import ssl
import os
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context

import streamlit as st
import anthropic
from datetime import datetime
import json

# ─────────────────────────────────────────────
# SECTION 1 — Page setup
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Career Agent – Wins Tracker",
    page_icon="⭐",
    layout="centered"
)

# ─────────────────────────────────────────────
# SECTION 2 — Styling
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 2rem; }

    /* Visible tab styling */
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

    .star-card {
        background: #f8f9fa;
        border-left: 4px solid #185FA5;
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 12px;
        font-size: 14px;
        line-height: 1.7;
    }
    .bullet-card {
        background: #f0f7ee;
        border-left: 4px solid #3B6D11;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 14px;
        line-height: 1.6;
    }
    .yearend-card {
        background: #fff8f0;
        border-left: 4px solid #854F0B;
        border-radius: 6px;
        padding: 14px 16px;
        margin-bottom: 12px;
        font-size: 14px;
        line-height: 1.7;
    }
    .preview-card {
        background: #eef4fb;
        border-left: 3px solid #378ADD;
        border-radius: 6px;
        padding: 12px 14px;
        margin-top: 10px;
        font-size: 13px;
        line-height: 1.6;
    }
    .datapoint-card {
        background: #f5f0fe;
        border-left: 4px solid #534AB7;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 8px;
        font-size: 14px;
        line-height: 1.6;
    }
    .okr-tag {
        background: #FAEEDA;
        color: #633806;
        font-size: 11px;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 8px;
    }
    .okr-version-tag {
        background: #E6F1FB;
        color: #0C447C;
        font-size: 11px;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 500;
        display: inline-block;
        margin-bottom: 6px;
    }
    .mapping-tag {
        background: #EEEDFE;
        color: #3C3489;
        font-size: 11px;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 500;
        display: inline-block;
        margin-top: 6px;
    }
    .star-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 2px;
        margin-top: 8px;
    }
    .s-label { color: #185FA5; }
    .t-label { color: #3B6D11; }
    .a-label { color: #854F0B; }
    .r-label { color: #A32D2D; }
    .warning-box {
        background: #FAEEDA;
        border-left: 4px solid #854F0B;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 13px;
        color: #633806;
        margin-bottom: 16px;
    }
    .info-box {
        background: #E6F1FB;
        border-left: 4px solid #185FA5;
        border-radius: 6px;
        padding: 12px 16px;
        font-size: 13px;
        color: #0C447C;
        margin-bottom: 16px;
    }
    .section-header {
        font-size: 12px;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
        margin-top: 4px;
    }
    .win-pill {
        display: inline-block;
        background: #f0f7ee;
        color: #27500A;
        font-size: 11px;
        padding: 2px 10px;
        border-radius: 12px;
        margin: 2px 4px 2px 0;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECTION 3 — Persistent storage functions
# ─────────────────────────────────────────────
DATA_FILE = "wins.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {
        "profile": {
            "current_role": "Data Engineering Manager",
            "target_role": "Senior EM, Data & AI at Microsoft"
        },
        "okr_sets": [],
        "wins": []
    }

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_active_okr_set(data):
    if data["okr_sets"]:
        return data["okr_sets"][-1]
    return None

# ─────────────────────────────────────────────
# SECTION 4 — Session state + load data
# ─────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "structured_output" not in st.session_state:
    st.session_state.structured_output = None
if "yearend_output" not in st.session_state:
    st.session_state.yearend_output = None
if "show_okr_mapper" not in st.session_state:
    st.session_state.show_okr_mapper = False

data = st.session_state.data

# ─────────────────────────────────────────────
# SECTION 5 — Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Career Agent")
    st.caption("v0.7 · Wins Tracker")
    st.markdown("---")

    api_key = st.text_input(
        "Anthropic API key",
        type="password",
        placeholder="sk-ant-...",
        help="Get yours at console.anthropic.com"
    )

    st.markdown("### Your profile")
    current_role = st.text_input(
        "Current role",
        value=data["profile"].get("current_role", "Data Engineering Manager")
    )
    target_role = st.text_input(
        "Target role",
        value=data["profile"].get("target_role", "Senior EM, Data & AI at Microsoft")
    )

    if (current_role != data["profile"].get("current_role") or
            target_role != data["profile"].get("target_role")):
        data["profile"]["current_role"] = current_role
        data["profile"]["target_role"] = target_role
        save_data(data)

    st.markdown("---")

    # OKR setup — always accessible, independent of wins
    st.markdown("### Goals / OKRs")
    active_okr = get_active_okr_set(data)

    if active_okr:
        st.markdown(
            f'<div class="okr-version-tag">{active_okr["label"]} · {active_okr["date"]}</div>',
            unsafe_allow_html=True
        )
        okr_input = st.text_area(
            "Your current goals",
            value=active_okr["okrs"],
            height=120,
            key="sidebar_okr"
        )
    else:
        okr_input = st.text_area(
            "Paste your goals / OKRs",
            placeholder="e.g.\n1. Build DQ capability\n2. Drive reliability\n3. Enable teams",
            height=120,
            key="sidebar_okr"
        )

    if st.button("Save Goals", use_container_width=True):
        if okr_input.strip():
            new_okr_set = {
                "id": f"okr_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "label": f"OKR Set {len(data['okr_sets']) + 1}",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "okrs": okr_input
            }
            data["okr_sets"].append(new_okr_set)
            save_data(data)
            st.success("Goals saved!")
            st.rerun()
        else:
            st.warning("Please enter your goals first.")

    if len(data["okr_sets"]) > 1:
        with st.expander("Goal version history"):
            for okr_set in reversed(data["okr_sets"]):
                st.markdown(
                    f'<div class="okr-version-tag">{okr_set["label"]} · {okr_set["date"]}</div>',
                    unsafe_allow_html=True
                )
                st.caption(okr_set["okrs"][:80] + "...")

    st.markdown("---")

    total_wins = len(data["wins"])
    if total_wins > 0:
        st.markdown("### Wins logged")
        st.caption(f"{total_wins} win(s) · all time")
        for w in reversed(data["wins"][-4:]):
            st.markdown(
                f'<div class="win-pill">{w["win"][:35]}...</div>',
                unsafe_allow_html=True
            )
        if total_wins > 4:
            st.caption(f"+ {total_wins - 4} more in history below")

    st.markdown("---")
    st.caption("Built with Streamlit + Claude API")

# ─────────────────────────────────────────────
# SECTION 6 — Main area
# ─────────────────────────────────────────────
st.markdown("## Wins Tracker")
st.markdown("Turn your accomplishments into interview stories, promotion bullets and interview prep.")
st.markdown("---")

impact_area = st.selectbox(
    "Impact area",
    [
        "Technical delivery",
        "Leadership & people",
        "Cost savings",
        "Revenue / growth",
        "Process improvement",
        "Data & AI",
        "Other"
    ]
)

win_input = st.text_area(
    "Describe your win",
    placeholder="e.g. Built Enterprise Data Quality Engineering team from the ground up across 8 critical data domains, certified 50% of data products using Educate-Enable-Enforce framework...",
    height=120
)

generate_btn = st.button(
    "Generate career capital",
    type="primary",
    use_container_width=True
)

# ─────────────────────────────────────────────
# SECTION 7 — Prompt builders
# ─────────────────────────────────────────────
def build_prompt(win, role, target, impact):
    return f"""You are a senior career coach specialising in Data & AI leadership roles.

The user is a {role} targeting a {target} role.
Impact area: {impact}
Their accomplishment: "{win}"

Return ONLY a valid JSON object with this exact structure — no markdown, no explanation, just the JSON:

{{
  "star_stories": [
    {{
      "title": "Story title",
      "angle": "e.g. Organizational scale",
      "situation": "...",
      "task": "...",
      "action": "...",
      "result": "..."
    }}
  ],
  "promotion_bullets": [
    "Bullet 1",
    "Bullet 2",
    "Bullet 3",
    "Bullet 4"
  ],
  "interview_questions": [
    {{
      "question": "Interview question text",
      "why_relevant": "One sentence on why this matters for the target role",
      "best_story": "Title of the STAR story that best answers this question"
    }}
  ],
  "data_points": [
    "One crisp data-backed sentence showing impact — e.g. Achieved 50% data product certification across 8 domains",
    "Another crisp data point",
    "Another crisp data point"
  ]
}}

Generate 3 STAR stories (each from a different angle), 4 promotion bullets, 5 interview questions, and 3 crisp data points.
Each interview question must reference one of the 3 STAR story titles in best_story.
Data points must be single punchy sentences — impact first, no filler.
Be specific, senior-level, and concise. Use only metrics the user has provided — do not invent numbers."""


def build_yearend_prompt(wins, role, okrs=""):
    wins_text = "\n".join([
        f"- [{w['impact']}] {w['win']}" for w in wins
    ])

    if okrs.strip():
        return f"""You are a senior career coach helping a {role} write their year-end performance review.

Their OKRs / Goals this year:
{okrs}

Their accomplishments this year:
{wins_text}

Return ONLY a valid JSON object with this exact structure — no markdown, no explanation, just the JSON:

{{
  "okr_mappings": [
    {{
      "okr": "The OKR or goal exactly as written",
      "rating": "Exceeded / Met / Partially Met",
      "evidence": ["win 1 mapped here", "win 2 mapped here"],
      "draft_paragraph": "2-3 punchy sentences. Lead with quantified impact, follow with how. No filler. Executive tone."
    }}
  ],
  "overall_summary": "2 sentences max. Lead with biggest business impact. No adjectives without evidence."
}}

Rules:
- Each win must appear under exactly ONE OKR — the most dominant one. No duplicates.
- Format: [Quantified outcome] + [how achieved] + [why it mattered].
- Use only metrics the user provided — do not invent numbers."""

    else:
        return f"""You are a senior career coach helping a {role} write their year-end performance review.

Their accomplishments this year:
{wins_text}

Return ONLY a valid JSON object with this exact structure — no markdown, no explanation, just the JSON:

{{
  "performance_themes": [
    {{
      "theme": "Theme name",
      "wins": ["relevant win 1", "relevant win 2"],
      "draft_paragraph": "2-3 punchy sentences. Lead with quantified impact, follow with how. No filler. Executive tone."
    }}
  ],
  "overall_summary": "2 sentences max. Lead with biggest business impact. No adjectives without evidence."
}}

Rules:
- Each win must appear under exactly ONE theme. No duplicates.
- Format: [Quantified outcome] + [how achieved] + [why it mattered].
- Group into 3-4 themes. Use only metrics provided — do not invent numbers."""


# ─────────────────────────────────────────────
# SECTION 8 — Claude API call
# ─────────────────────────────────────────────
def call_claude(prompt, api_key):
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text
    return json.loads(raw)


# ─────────────────────────────────────────────
# SECTION 9 — Handle win generation
# ─────────────────────────────────────────────
if generate_btn:
    if not api_key:
        st.warning("Please enter your Anthropic API key in the sidebar to continue.")
    elif not win_input.strip():
        st.warning("Please describe your win before generating.")
    else:
        with st.spinner("Generating your career capital..."):
            try:
                prompt = build_prompt(
                    win_input,
                    current_role,
                    target_role,
                    impact_area
                )
                structured = call_claude(prompt, api_key)
                st.session_state.structured_output = structured
                st.session_state.show_okr_mapper = False
                st.session_state.yearend_output = None

                active_okr = get_active_okr_set(data)
                active_okr_id = active_okr["id"] if active_okr else None

                new_win = {
                    "id": f"win_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "win": win_input,
                    "impact": impact_area,
                    "okr_set_id": active_okr_id,
                    "output": structured
                }
                data["wins"].append(new_win)
                save_data(data)

            except json.JSONDecodeError:
                st.error("Claude returned an unexpected format. Please try again.")
            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

# ─────────────────────────────────────────────
# SECTION 10 — Display output + tabs
# ─────────────────────────────────────────────
if st.session_state.structured_output:
    output_data = st.session_state.structured_output

    st.markdown("---")
    st.markdown("""
    <div class="warning-box">
        <strong>Verify your metrics before using in interviews or reviews.</strong>
        Replace any figures that are not from your actual experience.
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "Year-end Review",
        "Promotion Bullets",
        "Interview Prep",
        "Story Bank"
    ])

    # ── Tab 1: Year-end Review ───────────────
    with tab1:
        st.markdown(
            '<div class="section-header">Your data points for this win</div>',
            unsafe_allow_html=True
        )

        # Show data points immediately — no friction
        data_points = output_data.get("data_points", [])
        if data_points:
            for dp in data_points:
                st.markdown(
                    f'<div class="datapoint-card">{dp}</div>',
                    unsafe_allow_html=True
                )
            all_dp = "\n\n".join(data_points)
            st.download_button(
                label="Download data points",
                data=all_dp,
                file_name="data_points.txt",
                mime="text/plain",
                key="dl_datapoints"
            )

        st.markdown("---")

        # Optional OKR mapping — user decides
        st.markdown(
            '<div class="section-header">Map to your goals (optional)</div>',
            unsafe_allow_html=True
        )

        if not st.session_state.show_okr_mapper:
            st.button(
                "Map this win to my OKRs / Goals →",
                use_container_width=True,
                key="show_mapper_btn",
                on_click=lambda: st.session_state.update({"show_okr_mapper": True})
            )
        else:
            # Full year-end generator
            all_years = sorted(set(
                w["date"][:4] for w in data["wins"]
            ), reverse=True)

            if all_years:
                selected_year = st.selectbox(
                    "Generate review for year",
                    all_years,
                    index=0
                )
                year_wins = [
                    w for w in data["wins"]
                    if w["date"][:4] == selected_year
                ]
                st.caption(f"{len(year_wins)} win(s) logged in {selected_year}")

                active_okr = get_active_okr_set(data)
                okr_text = active_okr["okrs"] if active_okr else ""

                if not okr_text:
                    st.markdown("""
                    <div class="info-box">
                        No goals saved yet. Add them in the sidebar under "Goals / OKRs"
                        and they'll be used here automatically.
                    </div>
                    """, unsafe_allow_html=True)

                yearend_btn = st.button(
                    "Generate year-end review",
                    type="primary",
                    use_container_width=True,
                    key="yearend_btn"
                )

                if yearend_btn:
                    if not api_key:
                        st.warning("Please enter your Anthropic API key in the sidebar.")
                    else:
                        with st.spinner("Generating your year-end review..."):
                            try:
                                prompt = build_yearend_prompt(
                                    year_wins,
                                    current_role,
                                    okr_text
                                )
                                yearend = call_claude(prompt, api_key)
                                st.session_state.yearend_output = yearend
                            except json.JSONDecodeError:
                                st.error("Unexpected format. Please try again.")
                            except Exception as e:
                                st.error(f"Something went wrong: {str(e)}")

            if st.session_state.yearend_output:
                ye = st.session_state.yearend_output

                if "overall_summary" in ye:
                    st.markdown("#### Overall summary")
                    st.markdown(
                        f'<div class="yearend-card">{ye["overall_summary"]}</div>',
                        unsafe_allow_html=True
                    )

                if "okr_mappings" in ye:
                    st.markdown("#### By OKR")
                    for i, okr in enumerate(ye["okr_mappings"]):
                        with st.expander(
                            f"OKR {i+1}: {okr['okr'][:70]}",
                            expanded=(i == 0)
                        ):
                            st.markdown(
                                f'<div class="okr-tag">Rating: {okr["rating"]}</div>',
                                unsafe_allow_html=True
                            )
                            st.markdown("**Evidence:**")
                            for evidence in okr.get("evidence", []):
                                st.markdown(f"- {evidence}")
                            st.markdown("**Draft:**")
                            st.markdown(
                                f'<div class="yearend-card">{okr["draft_paragraph"]}</div>',
                                unsafe_allow_html=True
                            )
                            st.download_button(
                                label="Download",
                                data=f"OKR: {okr['okr']}\nRating: {okr['rating']}\n\n{okr['draft_paragraph']}",
                                file_name=f"okr_{i+1}.txt",
                                mime="text/plain",
                                key=f"dl_okr_{i}"
                            )

                if "performance_themes" in ye:
                    st.markdown("#### By theme")
                    for i, theme in enumerate(ye["performance_themes"]):
                        with st.expander(
                            f"{theme['theme']}",
                            expanded=(i == 0)
                        ):
                            for w in theme.get("wins", []):
                                st.markdown(f"- {w}")
                            st.markdown(
                                f'<div class="yearend-card">{theme["draft_paragraph"]}</div>',
                                unsafe_allow_html=True
                            )
                            st.download_button(
                                label="Download",
                                data=f"Theme: {theme['theme']}\n\n{theme['draft_paragraph']}",
                                file_name=f"theme_{i+1}.txt",
                                mime="text/plain",
                                key=f"dl_theme_{i}"
                            )

                # Full download
                if "okr_mappings" in ye:
                    full = f"OVERALL SUMMARY\n\n{ye['overall_summary']}\n\n---\n\n"
                    for okr in ye["okr_mappings"]:
                        full += f"OKR: {okr['okr']}\nRating: {okr['rating']}\n\n{okr['draft_paragraph']}\n\n---\n\n"
                else:
                    full = f"OVERALL SUMMARY\n\n{ye['overall_summary']}\n\n---\n\n"
                    for theme in ye.get("performance_themes", []):
                        full += f"Theme: {theme['theme']}\n\n{theme['draft_paragraph']}\n\n---\n\n"

                st.download_button(
                    label="Download full year-end review",
                    data=full,
                    file_name=f"yearend_review_{datetime.now().strftime('%Y')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )

    # ── Tab 2: Promotion Bullets ─────────────
    with tab2:
        st.markdown(
            '<div class="section-header">4 promotion bullets · pick the ones that fit your story</div>',
            unsafe_allow_html=True
        )
        for i, bullet in enumerate(output_data.get("promotion_bullets", [])):
            st.markdown(
                f'<div class="bullet-card">{bullet}</div>',
                unsafe_allow_html=True
            )
            st.download_button(
                label="Download this bullet",
                data=bullet,
                file_name=f"bullet_{i+1}.txt",
                mime="text/plain",
                key=f"dl_bullet_{i}"
            )
        all_bullets = "\n\n".join(output_data.get("promotion_bullets", []))
        st.download_button(
            label="Download all bullets",
            data=all_bullets,
            file_name="promotion_bullets.txt",
            mime="text/plain",
            use_container_width=True
        )

    # ── Tab 3: Interview Prep ────────────────
    with tab3:
        st.markdown(
            '<div class="section-header">5 questions · each mapped to your best story</div>',
            unsafe_allow_html=True
        )
        story_lookup = {
            s["title"]: s for s in output_data.get("star_stories", [])
        }
        for i, q in enumerate(output_data.get("interview_questions", [])):
            with st.expander(f"Q{i+1}: {q['question']}", expanded=(i == 0)):
                st.markdown(f"**Why this matters:** {q['why_relevant']}")
                st.markdown(
                    f'<div class="mapping-tag">Best answered with → {q["best_story"]}</div>',
                    unsafe_allow_html=True
                )
                matched_story = story_lookup.get(q["best_story"])
                if matched_story:
                    with st.expander(
                        f"Preview: {matched_story['title']}",
                        expanded=False
                    ):
                        st.markdown('<div class="star-label s-label">Situation</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="preview-card">{matched_story["situation"]}</div>', unsafe_allow_html=True)
                        st.markdown('<div class="star-label t-label">Task</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="preview-card">{matched_story["task"]}</div>', unsafe_allow_html=True)
                        st.markdown('<div class="star-label a-label">Action</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="preview-card">{matched_story["action"]}</div>', unsafe_allow_html=True)
                        st.markdown('<div class="star-label r-label">Result</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="preview-card">{matched_story["result"]}</div>', unsafe_allow_html=True)

    # ── Tab 4: Story Bank ────────────────────
    with tab4:
        st.markdown(
            '<div class="section-header">Full story library · browse · download · practice</div>',
            unsafe_allow_html=True
        )
        for i, story in enumerate(output_data.get("star_stories", [])):
            with st.expander(
                f"Story {i+1}: {story['title']}  ·  {story['angle']}",
                expanded=(i == 0)
            ):
                st.markdown('<div class="star-label s-label">Situation</div>', unsafe_allow_html=True)
                st.markdown(story["situation"])
                st.markdown('<div class="star-label t-label">Task</div>', unsafe_allow_html=True)
                st.markdown(story["task"])
                st.markdown('<div class="star-label a-label">Action</div>', unsafe_allow_html=True)
                st.markdown(story["action"])
                st.markdown('<div class="star-label r-label">Result</div>', unsafe_allow_html=True)
                st.markdown(story["result"])
                story_text = (
                    f"STORY: {story['title']}\n\n"
                    f"Situation: {story['situation']}\n\n"
                    f"Task: {story['task']}\n\n"
                    f"Action: {story['action']}\n\n"
                    f"Result: {story['result']}"
                )
                st.download_button(
                    label="Download this story",
                    data=story_text,
                    file_name=f"story_{i+1}.txt",
                    mime="text/plain",
                    key=f"dl_story_{i}"
                )

# ─────────────────────────────────────────────
# SECTION 11 — Wins history
# ─────────────────────────────────────────────
if data["wins"]:
    st.markdown("---")
    st.markdown("### Wins history")

    all_years = sorted(set(w["date"][:4] for w in data["wins"]), reverse=True)
    filter_year = st.selectbox(
        "Filter by year",
        ["All"] + all_years,
        key="history_filter"
    )

    filtered = data["wins"] if filter_year == "All" else [
        w for w in data["wins"] if w["date"][:4] == filter_year
    ]
    st.caption(f"{len(filtered)} win(s)")

    for w in reversed(filtered):
        with st.expander(f"{w['date']} · {w['impact']} · {w['win'][:60]}..."):
            if w.get("okr_set_id"):
                okr_set = next(
                    (o for o in data["okr_sets"] if o["id"] == w["okr_set_id"]),
                    None
                )
                if okr_set:
                    st.markdown(
                        f'<div class="okr-version-tag">Goals active: {okr_set["label"]} · {okr_set["date"]}</div>',
                        unsafe_allow_html=True
                    )
            st.json(w["output"])
