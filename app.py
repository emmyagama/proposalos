"""
ProposalOS — Structured proposal intelligence for consulting and service firms.
Streamlit application with five-screen progressive disclosure flow.
"""

import streamlit as st
from datetime import datetime
from config.language_registry import (
    LANGUAGE_REGISTRY,
    PROPOSAL_TYPES,
    BUDGET_RANGES,
    TIMELINES,
    PROPOSAL_TONES,
)
from engine.prompt_builder import generate_proposal
from utils.pdf_export import generate_pdf


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="ProposalOS",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": "ProposalOS — Structured proposal intelligence for consulting and service firms."
    }
)

# =============================================================================
# CUSTOM CSS — Moves Streamlit away from "data dashboard" toward "professional tool"
# =============================================================================

st.markdown("""
<style>
    /* Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container width control */
    .block-container {
        max-width: 780px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Headers */
    h1 {
        font-weight: 700;
        font-size: 2rem;
        color: #1a1a1a;
        margin-bottom: 0.25rem;
    }
    h3 {
        font-weight: 600;
        font-size: 1.25rem;
        color: #2a2a2a;
        margin-top: 2rem;
        margin-bottom: 0.75rem;
    }

    /* Subtitle */
    .subtitle {
        color: #6b6b6b;
        font-size: 1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }

    /* Card-style containers */
    .card {
        background: #fafaf8;
        border: 1px solid #e8e5e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Proposal type cards */
    .type-card {
        background: #fafaf8;
        border: 1.5px solid #e8e5e0;
        border-radius: 10px;
        padding: 1.25rem 1rem;
        text-align: center;
        cursor: pointer;
        transition: border-color 0.2s, background 0.2s;
        height: 100%;
    }
    .type-card:hover {
        border-color: #c4b998;
        background: #f5f3ef;
    }
    .type-card.selected {
        border-color: #8B7355;
        background: #f5f0e8;
    }
    .type-card-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: #2a2a2a;
        margin-bottom: 0.25rem;
    }
    .type-card-desc {
        font-size: 0.8rem;
        color: #7a7a7a;
        line-height: 1.4;
    }

    /* Back link */
    .back-link {
        margin-bottom: 1.5rem;
    }
    .back-link a {
        color: #8B7355;
        text-decoration: none;
        font-size: 0.9rem;
    }
    .back-link a:hover {
        color: #6b5a45;
        text-decoration: underline;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"] {
        background-color: #2a2a2a;
        border-color: #2a2a2a;
        color: white;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1a1a1a;
        border-color: #1a1a1a;
    }

        /* Progress indicator — horizontal on all screens */
    .progress-container {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin: 1.5rem 0 2rem 0;
        flex-wrap: nowrap;
        overflow-x: auto;
    }
    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 44px;
        flex-shrink: 0;
    }
    .progress-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #e0dcd5;
        margin-bottom: 4px;
    }
    .progress-dot.active {
        background: #8B7355;
    }
    .progress-dot.done {
        background: #6b5a45;
    }
    .progress-label {
        font-size: 0.65rem;
        color: #8b8b8b;
        white-space: nowrap;
    }

    /* Output container */
    .proposal-output {
        background: #fdfdfc;
        border: 1px solid #e8e5e0;
        border-radius: 10px;
        padding: 2rem;
        line-height: 1.8;
    }

    /* CTA box */
    .cta-box {
        background: #f5f3ef;
        border-left: 4px solid #8B7355;
        padding: 1.25rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin-top: 2rem;
    }
    .cta-box h4 {
        margin-top: 0;
        color: #2a2a2a;
    }
    .cta-box p {
        margin-bottom: 0;
        color: #5a5a5a;
    }

    .cta-button {
        display: inline-block;
        background: #2a2a2a;
        color: white;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 500;
        font-size: 0.9rem;
        margin-top: 0.75rem;
        transition: background 0.2s;
    }
    .cta-button:hover {
        background: #1a1a1a;
        text-decoration: none;
        color: white;
    }

    /* Checkbox cards */
    .checkbox-card {
        background: #fafaf8;
        border: 1px solid #e8e5e0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }

    /* Dividers */
    hr {
        border-color: #e8e5e0;
        margin: 1.5rem 0;
    }
            
        /* Hide Streamlit footer */
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

if "proposalos" not in st.session_state:
    st.session_state.proposalos = {
        "current_screen": 1,
        "industry": None,
        "proposal_type": None,
        "tone": "Executive",
        "sender_name": "",              # NEW
        "sender_credentials": "",       # NEW
        "client_name": "",              # RENAMED from business_name
        "client_problem": "",
        "deliverables": [],
        "custom_deliverables": "",
        "budget_range": None,
        "timeline": None,
        "selected_sections": [],
        "proposal_text": "",
        "generation_complete": False,
    }

# Convenience accessor
state = st.session_state.proposalos


# =============================================================================
# HELPER: Progress Indicator
# =============================================================================

def render_progress(current):
    """Renders the 5-dot progress indicator. Stays horizontal on mobile."""
    labels = ["Context", "Situation", "Engagement", "Review", "Output"]
    
    dots_html = ""
    for i, label in enumerate(labels, 1):
        if i < current:
            dot_class = "done"
        elif i == current:
            dot_class = "active"
        else:
            dot_class = ""
        dots_html += f"""
        <div class="progress-step">
            <div class="progress-dot {dot_class}"></div>
            <span class="progress-label">{label}</span>
        </div>"""

    st.markdown(f"""
    <div class="progress-container">
        {dots_html}
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# SCREEN 1: Context Setup
# =============================================================================

def render_screen_1():
    st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
    st.markdown("### What type of engagement are you proposing?")

    # Proposal type cards — 5 columns
    card_cols = st.columns(5, gap="small")

    type_descriptions = {
        "Strategy Advisory": "High-level guidance, positioning, growth paths",
        "Implementation": "Hands-on delivery, process build, execution",
        "Diagnostic": "Assessment, audit, gap analysis, findings",
        "Transformation": "Large-scale change, restructure, turnaround",
        "Program Design": "Workshop series, training, capability build",
    }

    for i, (col, ptype) in enumerate(zip(card_cols, PROPOSAL_TYPES)):
        with col:
            is_selected = state["proposal_type"] == ptype
            card_class = "type-card selected" if is_selected else "type-card"
            desc = type_descriptions.get(ptype, "")

            # Using a button styled as a card
            if st.button(
                f"{ptype}\n\n{desc}",
                key=f"type_{ptype}",
                use_container_width=True,
                help=f"Select {ptype}",
            ):
                state["proposal_type"] = ptype

    st.markdown("<br>", unsafe_allow_html=True)

    # Industry dropdown
    st.markdown("### Your industry")
    industry = st.selectbox(
        "Select the industry that best describes your firm or client",
        options=[""] + list(LANGUAGE_REGISTRY.keys()),
        index=0,
        label_visibility="collapsed",
        placeholder="Select industry...",
    )
    if industry:
        state["industry"] = industry

    # Tone selector — compact radio
    st.markdown("### Proposal tone")
    tone = st.radio(
        "Select the writing tone for your proposal",
        options=PROPOSAL_TONES,
        index=PROPOSAL_TONES.index(state["tone"]),
        horizontal=True,
        label_visibility="collapsed",
    )
    state["tone"] = tone

    # Continue button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Continue →", type="primary", use_container_width=True):
            if not state["proposal_type"]:
                st.error("Please select a proposal type.")
            elif not state["industry"]:
                st.error("Please select an industry.")
            else:
                state["current_screen"] = 2
                st.rerun()


# =============================================================================
# SCREEN 2: Client Situation
# =============================================================================

def render_screen_2():
    # Back link
    if st.button("← Back", key="back_from_2"):
        state["current_screen"] = 1
        st.rerun()

    st.markdown("### Who is sending this proposal?")

    col1, col2 = st.columns(2)
    with col1:
        sender_name = st.text_input(
            "Your firm name",
            value=state["sender_name"],
            placeholder="e.g., Sterling Consulting, Adeola & Co.",
        )
        state["sender_name"] = sender_name
    with col2:
        sender_credentials = st.text_input(
            "Brief credentials (optional)",
            value=state["sender_credentials"],
            placeholder="e.g., 12 years in financial services strategy",
        )
        state["sender_credentials"] = sender_credentials

    st.markdown("---")
    st.markdown("### Who is the proposal for?")

    client_name = st.text_input(
        "Client or business name",
        value=state["client_name"],
        placeholder="e.g., Zenith Bank HR Division, Dangote Group Procurement",
    )
    state["client_name"] = client_name

    # Client problem
    st.markdown("### What's happening in their business?")
    st.markdown(
        '<p style="color:#8b8b8b;font-size:0.85rem;margin-top:-0.5rem;">'
        'Describe the situation. The more specific, the better the output.</p>',
        unsafe_allow_html=True,
    )

    # Show industry-relevant example
    if state["industry"]:
        lang = LANGUAGE_REGISTRY.get(state["industry"], LANGUAGE_REGISTRY["Business Services"])
        example_symptom = lang["operational_symptoms"][0] if lang["operational_symptoms"] else ""
        with st.expander("See example"):
            st.markdown(
                f"*Example for {state['industry']}:*\n\n"
                f"*\"{example_symptom}\"*"
            )

    client_problem = st.text_area(
        "Client problem or need",
        value=state["client_problem"],
        placeholder="Describe the client's current situation, challenges, and what's at stake...",
        height=150,
        label_visibility="collapsed",
    )
    state["client_problem"] = client_problem

    # Continue
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Continue →", key="continue_2", type="primary", use_container_width=True):
            if not state["sender_name"].strip():
                st.error("Please enter your firm name.")
            elif not state["client_name"].strip():
                st.error("Please enter a client name.")
            elif not state["client_problem"].strip():
                st.error("Please describe the client's situation.")
            else:
                state["current_screen"] = 3
                st.rerun()


# =============================================================================
# SCREEN 3: Engagement Shape
# =============================================================================

def render_screen_3():
    # Back link
    if st.button("← Back", key="back_from_3"):
        state["current_screen"] = 2
        st.rerun()

    st.markdown("### What are you proposing to deliver?")

    # Deliverables from registry
    if state["industry"]:
        lang = LANGUAGE_REGISTRY.get(state["industry"], LANGUAGE_REGISTRY["Business Services"])
        available_deliverables = lang.get("common_deliverables", [])
    else:
        available_deliverables = []

    if available_deliverables:
        st.markdown(
            '<p style="color:#8b8b8b;font-size:0.85rem;">'
            'Select from common deliverables for your industry:</p>',
            unsafe_allow_html=True,
        )
        selected = []
        for item in available_deliverables:
            if st.checkbox(item, value=item in state["deliverables"], key=f"del_{item}"):
                selected.append(item)
        state["deliverables"] = selected

    # Custom deliverables
    st.markdown("<br>", unsafe_allow_html=True)
    custom = st.text_input(
        "Add custom deliverables (optional)",
        value=state["custom_deliverables"],
        placeholder="e.g., Executive strategy session, Team training workshop...",
        label_visibility="visible",
    )
    state["custom_deliverables"] = custom

    st.markdown("<br>", unsafe_allow_html=True)

    # Budget and timeline
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Budget range")
        budget = st.selectbox(
            "Budget range",
            options=[""] + BUDGET_RANGES,
            index=0 if not state["budget_range"] else BUDGET_RANGES.index(state["budget_range"]) + 1,
            label_visibility="collapsed",
            placeholder="Select budget range...",
        )
        if budget:
            state["budget_range"] = budget

    with col2:
        st.markdown("### Timeline")
        timeline = st.selectbox(
            "Timeline",
            options=[""] + TIMELINES,
            index=0 if not state["timeline"] else TIMELINES.index(state["timeline"]) + 1,
            label_visibility="collapsed",
            placeholder="Select timeline...",
        )
        if timeline:
            state["timeline"] = timeline

    # Continue
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Continue →", key="continue_3", type="primary", use_container_width=True):
            if not state["budget_range"]:
                st.error("Please select a budget range.")
            elif not state["timeline"]:
                st.error("Please select a timeline.")
            else:
                state["current_screen"] = 4
                st.rerun()


# =============================================================================
# SCREEN 4: Structure Review
# =============================================================================

# Default sections for all proposals
DEFAULT_SECTIONS = [
    "Executive Summary",
    "Understanding Your Situation",
    "Proposed Solution",
    "Scope of Work",
    "Timeline",
    "Investment & Value Justification",
    "Next Steps",
    "Follow-Up Message",
]


def render_screen_4():
    # Back link
    if st.button("← Back", key="back_from_4"):
        state["current_screen"] = 3
        st.rerun()

    st.markdown("### Review proposal structure")
    st.markdown(
        '<p style="color:#8b8b8b;font-size:0.85rem;">'
        'All sections are included by default. Toggle off any you don\'t need.</p>',
        unsafe_allow_html=True,
    )

    # Initialize selected sections if empty
    if not state["selected_sections"]:
        state["selected_sections"] = DEFAULT_SECTIONS.copy()

    selected = []
    for section in DEFAULT_SECTIONS:
        if st.checkbox(
            section,
            value=section in state["selected_sections"],
            key=f"section_{section}",
        ):
            selected.append(section)
    state["selected_sections"] = selected

    # Validation: must have at least Executive Summary
    if "Executive Summary" not in state["selected_sections"]:
        st.warning("Executive Summary is required and will be included.")
        state["selected_sections"] = ["Executive Summary"] + state["selected_sections"]

    st.markdown("<br>", unsafe_allow_html=True)

    # Generate button
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button("Generate Proposal", type="primary", use_container_width=True):
            state["current_screen"] = 5
            state["generation_complete"] = False
            st.rerun()


# =============================================================================
# SCREEN 5: Output & Export
# =============================================================================

def render_screen_5():
    # If not yet generated, run generation
    if not state["generation_complete"]:
        with st.spinner("Crafting your proposal... This takes 10–20 seconds."):
            # Prepare deliverables string
            all_deliverables = state["deliverables"].copy()
            if state["custom_deliverables"].strip():
                all_deliverables.append(state["custom_deliverables"].strip())
            deliverables_str = ", ".join(all_deliverables) if all_deliverables else ""

            proposal = generate_proposal(
    industry=state["industry"],
    proposal_type=state["proposal_type"],
    tone=state["tone"],
    sender_name=state["sender_name"],          # NEW
    sender_credentials=state["sender_credentials"],  # NEW
    client_name=state["client_name"],           # RENAMED
    client_problem=state["client_problem"],
    deliverables=deliverables_str,
    budget_range=state["budget_range"],
    timeline=state["timeline"],
    sections=state["selected_sections"],  # ← pass selected sections
)
            state["proposal_text"] = proposal
            state["generation_complete"] = True
        st.rerun()

    # Success header
    st.markdown("### Your proposal is ready")
    st.markdown(
        f'<p style="color:#8b8b8b;">Prepared for: {state["client_name"]}</p>',
        unsafe_allow_html=True,
    )

    # Action buttons
    col1, col2, col3, col4 = st.columns([1.2, 1, 1, 1])
    with col1:
        try:
            pdf_bytes = generate_pdf(
    state["proposal_text"],
    state["client_name"],
    state["proposal_type"],
    state["sender_name"]
)
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=f"Proposal_{state['client_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.warning(f"PDF unavailable: {e}")

    with col2:
        if st.button("🔄 Regenerate", use_container_width=True):
            state["generation_complete"] = False
            st.rerun()

    with col3:
        if st.button("✕ Start New", use_container_width=True):
            # Reset state
            for key in st.session_state.proposalos:
                if key == "current_screen":
                    st.session_state.proposalos[key] = 1
                elif key == "tone":
                    st.session_state.proposalos[key] = "Executive"
                elif isinstance(st.session_state.proposalos[key], list):
                    st.session_state.proposalos[key] = []
                elif isinstance(st.session_state.proposalos[key], bool):
                    st.session_state.proposalos[key] = False
                else:
                    st.session_state.proposalos[key] = "" if key != "industry" else None
            st.rerun()

    st.markdown("---")

    # Proposal output
    st.markdown('<div class="proposal-output">', unsafe_allow_html=True)
    st.markdown(state["proposal_text"])
    st.markdown("</div>", unsafe_allow_html=True)

    # Follow-up message
    st.markdown("---")
    st.markdown("### 📱 Follow-Up Message")
    st.info(
    "The Follow-Up Message is displayed above. Copy it directly to use in your email. "
    "The downloadable PDF contains the proposal."
    )

    # CTA
    st.markdown("""
<div class="cta-box">
    <h4>Want proposals that consistently win higher-value clients?</h4>
    <p>
    ProposalOS is only the starting point.
    We help consulting and service firms improve proposal positioning,
    pricing communication, client workflows, and operational delivery systems.
    </p>
    <p>
    Book a free proposal review session to identify gaps, strengthen positioning,
    and improve how your firm converts opportunities into revenue.
    </p>
    <a href="https://calendar.app.google/2B5LnxjDK7H18gzx5" target="_blank" class="cta-button">
        Book Free Proposal Review
    </a>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# MAIN APP — Screen Router
# =============================================================================

# Header (visible on all screens except output)
if state["current_screen"] < 5:
    st.title("ProposalOS")
    st.markdown(
        '<p class="subtitle">Structured proposal intelligence for consulting and service firms.</p>',
        unsafe_allow_html=True,
    )
    render_progress(state["current_screen"])
    st.markdown("<hr>", unsafe_allow_html=True)

# Route to current screen
if state["current_screen"] == 1:
    render_screen_1()
elif state["current_screen"] == 2:
    render_screen_2()
elif state["current_screen"] == 3:
    render_screen_3()
elif state["current_screen"] == 4:
    render_screen_4()
elif state["current_screen"] == 5:
    # Clean header for output screen
    st.title("ProposalOS")
    render_progress(state["current_screen"])
    st.markdown("<hr>", unsafe_allow_html=True)
    render_screen_5()