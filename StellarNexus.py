import streamlit as st
import pandas as pd
from datetime import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# 2. UPDATED PROFESSIONAL CSS
st.markdown("""
<style>
    /* Background Image */
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
    }
    
    /* Main Content Container overlay for professionalism */
    [data-testid="stAppViewBlockContainer"] {
        background-color: rgba(255, 255, 255, 0.02); 
        padding: 2rem;
    }

    /* DARK BLUE HEADER: Professional & Clean Visibility */
    .main-header {
        background: rgba(10, 25, 47, 0.96); /* Elegant Deep Navy */
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        border-bottom: 5px solid #1e40af; /* Blue accent */
        margin-bottom: 2.5rem;
        box-shadow: 0 12px 40px rgba(0,0,0,0.6);
    }
    .main-header h1 {
        color: #e2e8f0 !important; /* Soft white-blue */
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
        margin: 0;
    }
    .main-header p {
        color: #94a3b8 !important;
        font-size: 1.3rem;
        margin-top: 10px;
        font-weight: 500;
    }

    /* HERO SECTION CARDS: Strategic Hits & Tech Pulse */
    .hero-card {
        background: rgba(10, 25, 47, 0.92);
        border-radius: 12px;
        padding: 2rem;
        min-height: 250px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 30px rgba(0,0,0,0.5);
    }
    .hero-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
    }

    /* VERTICAL SECTIONS: Clean & Professional */
    .vertical-section {
        background: rgba(255, 255, 255, 0.98); 
        color: #0f172a; 
        padding: 1.5rem;
        border-radius: 12px;
        min-height: 420px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .vertical-header {
        font-size: 1.15rem;
        font-weight: 800;
        padding-bottom: 12px;
        margin-bottom: 15px;
        border-bottom: 3px solid #1e40af;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .vertical-list {
        list-style: none;
        padding: 0;
    }
    .vertical-list li {
        margin-bottom: 14px;
        font-size: 0.95rem;
        line-height: 1.6;
        border-left: 4px solid #3b82f6;
        padding-left: 12px;
    }
</style>
""", unsafe_allow_html=True)

# 3. DARK BLUE MAIN HEADER
st.markdown("""
<div class="main-header">
    <h1>Global Telecom & OTT Stellar Nexus</h1>
    <p>Executive Competitive Intelligence Portfolio | 2026 Strategic Briefing</p>
</div>
""", unsafe_allow_html=True)

# 4. HERO SECTION: STRATEGIC HITS & TECH PULSE FIRST
st.markdown("<h2 style='color: white; margin-bottom: 1.5rem;'>🚀 Strategic Baseline</h2>", unsafe_allow_html=True)
col_hits, col_pulse = st.columns(2)

with col_hits:
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title" style="color: #10b981;">🟢 STRATEGIC HITS (JAN 2026)</div>
        <ul style="color: #cbd5e1; font-size: 1.05rem; line-height: 1.8;">
            <li><b>Netflix-WBD Merger:</b> Board finalizes $82.7B consolidation deal. Integration begins in Q3 2026.</li>
            <li><b>Amdocs-Matrixx Deal:</b> Amdocs secures dominance in 5G charging with Matrixx acquisition completion.</li>
            <li><b>JioHotstar Synergy:</b> Massive user base migration initiates India's largest OTT ecosystem.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_pulse:
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title" style="color: #f97316;">🟠 TECH PULSE: AGENTIC REALITY</div>
        <ul style="color: #cbd5e1; font-size: 1.05rem; line-height: 1.8;">
            <li><b>Agentic Integration:</b> AI agents now manage 40% of Tier-1 BSS operational workflows autonomously.</li>
            <li><b>Inference Optimization:</b> Compute shift toward strategic hybrid models for real-time AI decisioning.</li>
            <li><b>Edge Dominance:</b> 5G network slicing now serves 200+ specialized enterprise AI use cases.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# 5. VERTICAL INTELLIGENCE: Modular & Clean
st.markdown("<h2 style='color: white; margin-bottom: 1.5rem;'>📊 Vertical Intelligence</h2>", unsafe_allow_html=True)
v_col1, v_col2, v_col3, v_col4 = st.columns(4)

sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        "Amdocs leverages Matrixx assets to counter global competitor expansion.",
        "SaaS-based BSS adoption grows 25% among digital-first operators.",
        "Legacy billing decommissioning rates reach record high for Jan 2026."
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        "Netflix-HBO unified tier pilot launches in strategic global markets.",
        "Discovery Global separation partitions legacy linear liabilities successfully.",
        "Ad-tier revenue surpasses standard subscriptions for top-3 platforms."
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        "WNBA 11-year rights deal initiates historic sports media valuation surge.",
        "NBA global rights shift to Disney/Amazon officially goes live.",
        "Fan engagement platforms pivot to real-time generative highlight reels."
    ]),
    ("⚡ CORE TECHNOLOGY", "#ea580c", [
        "Standalone Gen AI tools lose market share to embedded 'passive' AI.",
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

# 6. FOOTER
st.markdown("<br><br>")
st.markdown(f"<p style='text-align: center; color: #94a3b8;'>Last Synced: {datetime.now().strftime('%H:%M:%S')} | Confidential Portfolio Briefing © 2026</p>", unsafe_allow_html=True)
