import streamlit as st
import pandas as pd
from datetime import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# 2. UPDATED LIGHT-THEME & PROFESSIONAL CSS
st.markdown("""
<style>
    /* Professional Light Background */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    /* NAVY BLUE HEADER: Impactful & Clean */
    .main-header {
        background: #0a192f; /* Solid Navy for high visibility */
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: #ffffff !important;
        font-size: 3rem !important;
        font-weight: 800 !important;
        margin: 0;
    }

    /* STRATEGIC BASELINE: DARK FONT ON LIGHT BACKGROUND */
    .hero-container {
        background: #ffffff;
        border-radius: 15px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-bottom: 2.5rem;
    }
    .hero-title {
        color: #0f172a !important;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        border-left: 6px solid #1e40af;
        padding-left: 15px;
    }
    .hero-card {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 1.5rem;
        min-height: 220px;
        border: 1px solid #e2e8f0;
    }

    /* VERTICAL SECTIONS: CLEAN CARDS */
    .vertical-section {
        background: #ffffff;
        padding: 1.8rem;
        border-radius: 12px;
        min-height: 450px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    .vertical-header {
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 3px solid #3b82f6;
        text-transform: uppercase;
    }
    .news-item {
        margin-bottom: 18px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f1f5f9;
    }
    .news-text {
        font-size: 0.95rem;
        color: #334155;
        line-height: 1.5;
        margin-bottom: 5px;
    }
    .read-more {
        font-size: 0.85rem;
        color: #1e40af;
        font-weight: 600;
        text-decoration: none;
    }
    .read-more:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# 3. IMPACTFUL HEADER
st.markdown("""
<div class="main-header">
    <h1>Global Telecom & OTT Stellar Nexus</h1>
</div>
""", unsafe_allow_html=True)

# 4. STRATEGIC BASELINE
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🚀 STRATEGIC BASELINE</div>
    <div style="display: flex; gap: 20px;">
        <div class="hero-card" style="flex: 1;">
            <div style="font-weight:800; color:#10b981; margin-bottom:10px;">🟢 STRATEGIC HITS (JAN 2026)</div>
            <div class="news-text"><b>Netflix-WBD Merger:</b> Netflix board moves to finalize the $82.7B acquisition of Warner Bros. Discovery studios and HBO Max to counter rising competition.</div>
            <div class="news-text"><b>NEC-CSG Expansion:</b> NEC completes $2.9B acquisition of CSG Systems, scaling Netcracker's footprint in North America.</div>
            <div class="news-text"><b>Amdocs Market Dominance:</b> Following the Matrixx acquisition, Amdocs secures 23% of the global 5G charging market.</div>
        </div>
        <div class="hero-card" style="flex: 1;">
            <div style="font-weight:800; color:#f97316; margin-bottom:10px;">🟠 TECH PULSE: AGENTIC REALITY</div>
            <div class="news-text"><b>Agentic BSS:</b> 40% of Tier-1 operators have transitioned to Agentic AI for autonomous revenue management.</div>
            <div class="news-text"><b>Quantum Commercialization:</b> D-Wave's acquisition of QCI signals the move of quantum-gate systems into enterprise fintech.</div>
            <div class="news-text"><b>Sovereign AI Infrastructure:</b> Shift toward regionally compliant data centers peaks due to geopolitical cloud fragmentation.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 5. VERTICAL INTELLIGENCE WITH HYPERLINKS
st.markdown("<h2 style='color: #0f172a; margin-bottom: 1.5rem;'>📊 Vertical Intelligence</h2>", unsafe_allow_html=True)
v_col1, v_col2, v_col3, v_col4 = st.columns(4)

sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        {"t": "NEC/Netcracker scales North American operations via $2.9B CSG deal.", "l": "https://www.telecoms.com"},
        {"t": "Amdocs integrates Matrixx cloud-native charging for 5G edge use cases.", "l": "https://www.lightreading.com"},
        {"t": "SaaS BSS adoption surges as telcos decommission legacy on-prem stacks.", "l": "https://www.vanillaplus.com"}
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        {"t": "Netflix board approves $82.7B WBD merger to secure HBO content library.", "l": "https://www.variety.com"},
        {"t": "Discovery Global spin-off finalized to partition legacy linear debt.", "l": "https://www.hollywoodreporter.com"},
        {"t": "Ad-supported revenue overtakes traditional subs for top OTT platforms.", "l": "https://www.digitaltveurope.com"}
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        {"t": "WNBA 11-year rights deal begins, elevating package value to $200M/year.", "l": "https://www.espn.com"},
        {"t": "NBA domestic rights officially transition to Disney and Amazon.", "l": "https://www.sportspromedia.com"},
        {"t": "Live generative highlights become standard for fan engagement platforms.", "l": "https://www.sportico.com"}
    ]),
    ("⚡ CORE TECHNOLOGY", "#ea580c", [
        {"t": "Autonomous AI agent market projected to hit $8.5B by end of 2026.", "l": "https://www.techcrunch.com"},
        {"t": "Embedded 'Passive' AI begins replacing standalone GenAI productivity tools.", "l": "https://www.wired.com"},
        {"t": "Industrial robotics installations reach new 5.5M global unit record.", "l": "https://www.venturebeat.com"}
    ])
]

for idx, (label, color, news) in enumerate(sections):
    with [v_col1, v_col2, v_col3, v_col4][idx]:
        st.markdown(f'<div class="vertical-section"><div class="vertical-header" style="color: {color}; border-color: {color};">{label}</div>', unsafe_allow_html=True)
        for item in news:
            st.markdown(f"""
            <div class="news-item">
                <div class="news-text">{item['t']}</div>
                <a href="{item['l']}" target="_blank" class="read-more">Read Full Story →</a>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# 6. MINIMALIST REFRESH
st.markdown(f"<div style='text-align: center; color: #94a3b8; padding: 20px;'>Live Sync: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
