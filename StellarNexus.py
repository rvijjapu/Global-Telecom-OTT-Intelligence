import streamlit as st
import pandas as pd
from datetime import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# 2. BEAUTIFUL CUSTOM CSS & BACKGROUND
st.markdown("""
<style>
    /* Background Image */
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        color: #f8fafc;
    }
    
    /* Transparent Background for main container */
    [data-testid="stAppViewBlockContainer"] {
        background-color: rgba(15, 23, 42, 0.85); /* Dark slate overlay for readability */
        padding: 2rem;
        border-radius: 20px;
        margin-top: 2rem;
    }

    /* Header Styling */
    .header-box { 
        text-align: center; 
        padding-bottom: 2rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Card Styling */
    .news-card { 
        background: rgba(30, 41, 59, 0.95); 
        border-left: 5px solid #3b82f6; 
        border-radius: 10px; 
        padding: 1.5rem; 
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .hit-card { 
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.9), rgba(30, 41, 59, 0.9));
        border-left: 5px solid #10b981;
    }
    .pulse-card { 
        background: linear-gradient(135deg, rgba(88, 28, 135, 0.9), rgba(30, 41, 59, 0.9));
        border-left: 5px solid #f97316;
    }
</style>
""", unsafe_allow_html=True)

# 3. HEADER
st.markdown("""
<div class="header-box">
    <h1 style='font-size: 3rem; font-weight: 800; margin-bottom: 0;'>Global Telecom & OTT Stellar Nexus</h1>
    <p style='color: #94a3b8; font-size: 1.2rem;'>2026 Executive Intelligence Dashboard | Live Updates</p>
</div>
""", unsafe_allow_html=True)

# 4. TOP SECTION: STRATEGIC HITS & TECH PULSE
st.markdown("### 🚀 Strategic Baseline")
col_hits, col_pulse = st.columns(2)

with col_hits:
    st.markdown("""
    <div class="news-card hit-card">
        <h4 style='color: #10b981; margin:0;'>STRATEGIC HITS (JAN 2026)</h4>
        <ul style='font-size: 0.95rem; line-height: 1.6;'>
            <li><b>Netflix-WBD Merger:</b> Board reaffirms commitment to the $82.7B merger despite Paramount's $108B hostile bid. Expected close: Q3 2026.</li>
            <li><b>Amdocs Acquires Matrixx:</b> Amdocs finalizes $200M deal for Matrixx Software, consolidating 23% of the charging market.</li>
            <li><b>JioHotstar Dominance:</b> Emerging as the leader in India OTT, forcing global players to rethink local licensing.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_pulse:
    st.markdown("""
    <div class="news-card pulse-card">
        <h4 style='color: #f97316; margin:0;'>TECH PULSE: AGENTIC REALITY</h4>
        <ul style='font-size: 0.95rem; line-height: 1.6;'>
            <li><b>Agentic Baseline:</b> Autonomous AI agents are now the default for enterprise speed, moving from "tools" to "core components."</li>
            <li><b>Gen UI Discovery:</b> AI digital assistants are replacing traditional menus, allowing users to express "intent" to navigate content.</li>
            <li><b>Sovereign AI:</b> Increasing geopolitical tension is driving a shift toward regionally compliant, sovereign cloud platforms.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# 5. BOTTOM SECTION: INDUSTRY DEEP-DIVES
st.markdown("### 📊 Vertical Intelligence")
col1, col2, col3, col4 = st.columns(4)

sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        "NEC finalizes $2.9B CSG acquisition to bolster Netcracker's global position.",
        "Consolidation wave: BSS market shrinks as major vendors absorb specialized players.",
        "Matrixx architecture remains a favorite for MVNOs under Amdocs ownership."
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        "Warner Bros. film studio and HBO Max to unify under Netflix's premium tier.",
        "Discovery Global separation remains on track for Q3 2026 completion.",
        "Theater revenues under pressure as Netflix tests 'OTT-first' movie launches."
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        "VERSANT (NBCU spin-off) secures 11-year WNBA rights starting in 2026.",
        "USA Network to broadcast 50+ WNBA games annually with primetime doubleheaders.",
        "Sky Sports to distribute all NBCU-NBA/WNBA games across international markets."
    ]),
    ("⚡ CORE TECH", "#ea580c", [
        "Relational foundation models (SAP-RPT-1) now optimize ERP/Finance ops.",
        "World models grounded in real-world physics unlock advanced digital twins.",
        "ESim-enabled AR glasses launch at CES 2026, merging mobility and wearable AI."
    ])
]

for idx, (label, color, bullets) in enumerate(sections):
    with [col1, col2, col3, col4][idx]:
        bullet_html = "".join([f"<li style='margin-bottom:10px;'>{b}</li>" for b in bullets])
        st.markdown(f"""
        <div style='background: rgba(30, 41, 59, 0.9); border-top: 4px solid {color}; padding: 1rem; border-radius: 0 0 10px 10px; min-height: 400px;'>
            <h5 style='color: {color}; margin-top: 0;'>{label}</h5>
            <ul style='font-size: 0.85rem; padding-left: 1rem;'>{bullet_html}</ul>
        </div>
        """, unsafe_allow_html=True)

# 6. FOOTER
st.markdown("---")
st.markdown(f"<p style='text-align: center; color: #64748b;'>Dashboard Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data Sources: Light Reading, Advanced TV, WNBA, SAP News</p>", unsafe_allow_html=True)
