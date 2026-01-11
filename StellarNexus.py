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
    
    /* Main Content Container: Minimalist and Professional */
    [data-testid="stAppViewBlockContainer"] {
        background-color: rgba(248, 250, 252, 0.02); /* Very subtle overlay */
        padding: 2.5rem;
    }

    /* DARK BLUE HEADER: Professional Executive Visibility */
    .main-header {
        background: rgba(10, 25, 47, 0.98); /* Deep Navy */
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        border-bottom: 5px solid #1e40af; /* Blue accent */
        margin-bottom: 2.5rem;
        box-shadow: 0 12px 40px rgba(0,0,0,0.6);
    }
    .main-header h1 {
        color: #f8fafc !important; /* Crisp white-blue text */
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

    /* STRATEGIC BASELINE: DARK FONT HERO SECTION */
    .hero-container {
        background: rgba(255, 255, 255, 0.95); /* Light Background */
        border-radius: 15px;
        padding: 2.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 3rem;
    }
    .hero-title {
        color: #0f172a !important; /* DARK FONT for Strategic Baseline */
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        border-left: 6px solid #1e40af;
        padding-left: 15px;
    }
    .hero-card {
        background: #f1f5f9; /* Soft Light Gray */
        border-radius: 10px;
        padding: 1.5rem;
        min-height: 200px;
        border: 1px solid #e2e8f0;
    }
    .hero-card-header {
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }

    /* VERTICAL SECTIONS: LIGHT THEME & DARK FONT */
    .vertical-section {
        background: #ffffff; /* CLEAN WHITE */
        color: #1e293b; /* DARK TEXT for Visibility */
        padding: 1.8rem;
        border-radius: 12px;
        min-height: 400px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: 1px solid #f1f5f9;
    }
    .vertical-header {
        font-size: 1.15rem;
        font-weight: 800;
        padding-bottom: 12px;
        margin-bottom: 15px;
        border-bottom: 3px solid #3b82f6;
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
        border-left: 4px solid #cbd5e1; /* Subtle gray accent */
        padding-left: 12px;
        color: #334155; /* Dark gray text */
    }
</style>
""", unsafe_allow_html=True)

# 3. DARK BLUE MAIN HEADER
st.markdown("""
<div class="main-header">
    <h1>Global Telecom & OTT Stellar Nexus</h1>
    <p>Executive Competitive Briefing | 2026 Strategic Intelligence Portfolio</p>
</div>
""", unsafe_allow_html=True)

# 4. STRATEGIC BASELINE: LIGHT THEME HERO WITH DARK FONTS
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🚀 STRATEGIC BASELINE</div>
    <div style="display: flex; gap: 20px;">
        <div class="hero-card" style="flex: 1;">
            <div class="hero-card-header" style="color: #10b981;">🟢 STRATEGIC HITS (JAN 2026)</div>
            <ul style="color: #334155; font-size: 1rem; line-height: 1.7; padding-left: 20px;">
                <li><b>Netflix-WBD Merger:</b> $82.7B board-approved consolidation deal enters final regulatory phase. Expected H2 close.</li>
                <li><b>BSS Market Shift:</b> Amdocs finalizes $200M Matrixx acquisition, securing architecture edge in 5G charging.</li>
                <li><b>JioHotstar IPO:</b> Reliance initiating India's largest tech IPO for H1 2026 launch.</li>
            </ul>
        </div>
        <div class="hero-card" style="flex: 1;">
            <div class="hero-card-header" style="color: #f97316;">🟠 TECH PULSE: AGENTIC REALITY</div>
            <ul style="color: #334155; font-size: 1rem; line-height: 1.7; padding-left: 20px;">
                <li><b>Agentic Baseline:</b> Autonomous AI agents move from "experimental" to "mission-critical" for tier-1 telcos.</li>
                <li><b>Zero-Touch Ops:</b> 40% of BSS workflows now use predictive Agentic AI to resolve billing disputes autonomously.</li>
                <li><b>Inference Edge:</b> Data center power demand peaks as AI inference accounts for 2/3 of compute workloads.</li>
            </ul>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. VERTICAL INTELLIGENCE: LIGHT THEME & DARK FONT
st.markdown("<h2 style='color: white; margin-bottom: 1.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);'>📊 Vertical Intelligence</h2>", unsafe_allow_html=True)
v_col1, v_col2, v_col3, v_col4 = st.columns(4)

sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        "Amdocs leverages Matrixx assets to counter NEC/Netcracker's $2.9B expansion.",
        "SaaS-based BSS adoption grows 25% among Tier-2 digital-first operators.",
        "Legacy billing stack decommission rates at record high for Jan 2026."
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        "Netflix-HBO unified tier pilot launches in 5 strategic test markets.",
        "Discovery Global separation successfully partitions linear liabilities.",
        "Ad-tier revenue surpasses subscription-only revenue for top-3 platforms."
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        "WNBA 11-year rights deal begins, valued at ~$200M/year package.",
        "NBA global rights shift to Disney/Amazon officially goes live.",
        "Fan engagement platforms pivot to real-time generative highlights."
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

# 6. PROFESSIONAL FOOTER
st.markdown("<br>")
st.markdown(f"""
<div style='text-align: center; color: #f1f5f9; padding: 20px; border-top: 1px solid rgba(255,255,255,0.1); font-weight: 500;'>
    Confidential Executive Intelligence Portfolio | Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | © 2026 Stellar Nexus
</div>
""", unsafe_allow_html=True)
