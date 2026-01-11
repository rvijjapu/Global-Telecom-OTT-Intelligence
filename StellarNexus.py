import streamlit as st
import pandas as pd
from datetime import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# 2. PREMIUM CUSTOM CSS
st.markdown("""
<style>
    /* Background Image with optimized overlay */
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
    }
    
    /* Main Content Container: Clean and readable */
    [data-testid="stAppViewBlockContainer"] {
        background-color: rgba(248, 250, 252, 0.05); /* Very subtle overlay */
        padding: 2.5rem;
    }

    /* DARK BLUE HEADER: Professional Visibility */
    .main-header {
        background: rgba(15, 23, 42, 0.95); /* Deep Navy */
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        border-bottom: 4px solid #3b82f6; /* Modern Blue accent */
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .main-header h1 {
        color: #f8fafc !important; /* Crisp white-blue text */
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
        margin: 0;
    }
    .main-header p {
        color: #94a3b8 !important;
        font-size: 1.3rem;
        margin-top: 10px;
    }

    /* HERO SECTION CARDS: Strategic Hits & Tech Pulse */
    .hero-card {
        background: rgba(15, 23, 42, 0.9);
        border-radius: 12px;
        padding: 2rem;
        min-height: 250px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    .hero-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* VERTICAL SECTIONS: Clean & Modular */
    .vertical-section {
        background: rgba(255, 255, 255, 0.98); /* White background for maximum data visibility */
        color: #0f172a; /* Dark text on white for readability */
        padding: 1.5rem;
        border-radius: 12px;
        min-height: 420px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    .vertical-header {
        font-size: 1.1rem;
        font-weight: 800;
        padding-bottom: 10px;
        margin-bottom: 15px;
        border-bottom: 2px solid #e2e8f0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .vertical-list {
        list-style: none;
        padding: 0;
    }
    .vertical-list li {
        margin-bottom: 12px;
        font-size: 0.92rem;
        line-height: 1.5;
        border-left: 3px solid #3b82f6;
        padding-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 3. DARK BLUE MAIN HEADER
st.markdown("""
<div class="main-header">
    <h1>Global Telecom & OTT Stellar Nexus</h1>
    <p>2026 Executive Competitive Briefing | Intelligence Redefined</p>
</div>
""", unsafe_allow_html=True)

# 4. HERO SECTION: STRATEGIC HITS & TECH PULSE
st.markdown("<h2 style='color: white; margin-bottom: 1.5rem;'>🚀 Strategic Baseline</h2>", unsafe_allow_html=True)
col_hits, col_pulse = st.columns(2)

with col_hits:
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title" style="color: #10b981;">🟢 STRATEGIC HITS (JAN 2026)</div>
        <ul style="color: #cbd5e1; font-size: 1rem; line-height: 1.7;">
            <li><b>Netflix-WBD Consolidation:</b> $82.7B board-approved merger enters final regulatory phase. Expected H2 close.</li>
            <li><b>BSS Market Shift:</b> Amdocs finalizes $200M Matrixx acquisition, securing the architecture edge in 5G charging.</li>
            <li><b>JioHotstar IPO:</b> Reliance initiating India's largest tech IPO for H1 2026 launch.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_pulse:
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title" style="color: #f97316;">🟠 TECH PULSE: AGENTIC REALITY</div>
        <ul style="color: #cbd5e1; font-size: 1rem; line-height: 1.7;">
            <li><b>Agentic Baseline:</b> Autonomous AI agents move from "experimental" to "mission-critical" for tier-1 telcos.</li>
            <li><b>Zero-Touch Ops:</b> 40% of BSS workflows now use predictive Agentic AI to resolve billing disputes autonomously.</li>
            <li><b>Inference Edge:</b> Data center power demand peaks as AI inference accounts for 2/3 of compute workloads.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 5. VERTICAL INTELLIGENCE: Professional White Grid
st.markdown("<h2 style='color: white; margin-bottom: 1.5rem;'>📊 Vertical Intelligence</h2>", unsafe_allow_html=True)
v_col1, v_col2, v_col3, v_col4 = st.columns(4)

sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        "Amdocs leverages Matrixx assets to counter NEC/Netcracker's $2.9B expansion.",
        "SaaS-based BSS adoption grows 25% among Tier-2 telcos.",
        "Legacy billing stack decommission rates at record high for 2026."
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        "Netflix-HBO unified tier pilot launches in 5 test markets.",
        "Discovery Global separation successfully partitions linear liabilities.",
        "Ad-tier revenue surpasses subscription-only revenue for major platforms."
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        "WNBA 11-year rights deal begins, valued at ~$200M/year package.",
        "NBA global rights shift to Disney/Amazon officially kicks off.",
        "Fan engagement platforms pivot to real-time generative highlights."
    ]),
    ("⚡ CORE TECHNOLOGY", "#ea580c", [
        "Standalone Gen AI tools lose market share to embedded "passive" AI.",
        "Autonomous AI agent market projected to hit $8.5B by year-end.",
        "Industrial robotics installations reach 5.5M units worldwide."
    ])
]

for idx, (label, color, bullets) in enumerate(sections):
    with [v_col1, v_col2, v_col3, v_col4][idx]:
        bullet_html = "".join([f"<li>{b}</li>" for b in bullets])
        st.markdown(f"""
        <div class="vertical-section">
            <div class="vertical-header" style="color: {color}; border-color: {color};">{label}</div>
            <ul class="vertical-list">{bullet_html}</ul>
        </div>
        """, unsafe_allow_html=True)

# 6. PROFESSIONAL FOOTER
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style='text-align: center; color: #94a3b8; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1);'>
    Confidential Executive Intelligence Portfolio | Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | © 2026 Stellar Nexus
</div>
""", unsafe_allow_html=True)
