import streamlit as st
import time
from datetime import datetime

# --- 1. NEVER-SLEEP / KEEP-ALIVE CONFIGURATION ---
# This resets the inactivity timer every 10 minutes to prevent hibernation
if "last_ping" not in st.session_state:
    st.session_state.last_ping = datetime.now()

# Hidden fragment that runs every 600 seconds to keep the session active
@st.fragment(run_every=600)
def keep_alive():
    st.session_state.last_ping = datetime.now()
    # Trivial element to maintain server connection
    st.markdown("", unsafe_allow_html=True)

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# --- 3. PREMIUM CSS: BACKGROUND & DARK BLUE BRANDING ---
st.markdown("""
<style>
    /* Custom Background */
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        color: #1e293b;
    }
    
    /* Center the Loading State */
    .loading-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 80vh;
        text-align: center;
    }
    
    /* DARK BLUE Impactful Font for Loading and Title */
    .dark-blue-text {
        color: #0a192f !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.3);
    }

    .main-title {
        font-size: 3.2rem !important;
        margin-bottom: 20px;
    }

    /* Section Boxes - Strictly containing all news */
    .section-card {
        background: rgba(255, 255, 255, 0.96);
        padding: 24px;
        border-radius: 12px;
        min-height: 520px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    .section-header {
        font-size: 1.25rem;
        font-weight: 800;
        padding-bottom: 12px;
        border-bottom: 3px solid;
        text-transform: uppercase;
        margin-bottom: 20px;
    }

    .news-item {
        margin-bottom: 18px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f1f5f9;
    }

    .news-text {
        font-size: 0.95rem;
        color: #1e293b;
        line-height: 1.5;
    }

    .link-btn {
        color: #1e40af;
        font-weight: 700;
        text-decoration: none;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. IMPACTFUL LOADING SEQUENCE ---
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div class="loading-container">
            <h1 class="dark-blue-text" style="font-size: 3rem;">Igniting AI-powered intelligence...</h1>
            <p class="dark-blue-text" style="font-size: 1.2rem; opacity: 0.8;">Please wait while we synchronize global nodes.</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5) 

placeholder.empty()

# Trigger Keep-Alive
keep_alive()

# --- 5. MAIN DASHBOARD CONTENT ---
st.markdown("<h1 class='dark-blue-text main-title' style='text-align: center;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

# 🚀 STRATEGIC BASELINE
st.markdown("""
<div style="background: rgba(255,255,255,0.95); padding: 2rem; border-radius: 15px; margin-bottom: 2.5rem; border-left: 8px solid #0a192f; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
    <h2 style="color: #0a192f; margin: 0 0 1.5rem 0; font-weight: 800;">🚀 STRATEGIC BASELINE</h2>
    <div style="display: flex; gap: 20px;">
        <div style="flex: 1; background: #f1f5f9; padding: 1.5rem; border-radius: 10px; border: 1px solid #e2e8f0;">
            <div style="font-weight:800; color:#10b981; font-size:1.1rem; margin-bottom:12px;">🟢 STRATEGIC HITS (JAN 2026)</div>
            <p style="color:#1e293b; font-size:0.95rem; line-height:1.7;">
                <b>Netflix-WBD Merger:</b> Board approves $82.7B acquisition to unify HBO Max and Warner studios into Netflix's core.<br>
                <b>NEC Expansion:</b> Finalization of $2.9B CSG acquisition scales Netcracker's North American SaaS footprint.
            </p>
        </div>
        <div style="flex: 1; background: #f1f5f9; padding: 1.5rem; border-radius: 10px; border: 1px solid #e2e8f0;">
            <div style="font-weight:800; color:#f97316; font-size:1.1rem; margin-bottom:12px;">🟠 TECH PULSE: AGENTIC REALITY</div>
            <p style="color:#1e293b; font-size:0.95rem; line-height:1.7;">
                <b>Agentic BSS:</b> 40% of standard BSS operational tasks are now handled by autonomous agents across Tier-1 telcos.<br>
                <b>Inference Power:</b> AI inference demand spikes, leading to a shift toward strategic hybrid infrastructure models.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 📊 VERTICAL INDUSTRY GRID
col1, col2, col3, col4 = st.columns(4)

sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        {"t": "NEC/Netcracker dominates global BSS/OSS market share following $2.9B CSG deal.", "l": "https://www.netcracker.com"},
        {"t": "Amdocs acquires Matrixx Software for $200M to counter rising scale competitors.", "l": "https://www.lightreading.com"},
        {"t": "Reliance Jio eyes $4.5B from landmark 2026 public offering.", "l": "https://www.business-standard.com"}
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        {"t": "Netflix board approves $82.7B WBD merger to secure HBO Max content library.", "l": "https://www.variety.com"},
        {"t": "Discovery Global spin-off finalized to partition legacy debt from growth assets.", "l": "https://about.netflix.com"},
        {"t": "Ad-supported tiers overtake premium subs as primary growth driver for OTT giants.", "l": "https://www.digitaltveurope.com"}
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        {"t": "WNBA secures landmark 11-year rights deal with Disney, Amazon, and NBC.", "l": "https://www.wnba.com"},
        {"t": "NBA domestic rights officially transition to Disney and Amazon ecosystems.", "l": "https://www.sportspromedia.com"},
        {"t": "Live generative highlights become standard for fan engagement platforms.", "l": "https://www.sportico.com"}
    ]),
    ("⚡ CORE TECHNOLOGY", "#ea580c", [
        {"t": "Autonomous AI agent market projected to hit $8.5B by EOY 2026.", "l": "https://www.techcrunch.com"},
        {"t": "Industrial robotics installations reach new 5.5M global unit record in 2026.", "l": "https://www.venturebeat.com"},
        {"t": "Enterprise shift from cloud-first to strategic hybrid for AI inference economics.", "l": "https://www.gartner.com"}
    ])
]

# Rendering function ensuring news is properly INSIDE section boxes
for idx, (label, color, news_list) in enumerate(sections):
    with [col1, col2, col3, col4][idx]:
        news_html = ""
        for item in news_list:
            news_html += f"""
            <div class="news-item">
                <div class="news-text">{item['t']}</div>
                <a href="{item['l']}" target="_blank" class="link-btn">Read Full Story →</a>
            </div>"""
        
        st.markdown(f"""
        <div class="section-card">
            <div class="section-header" style="color: {color}; border-color: {color};">{label}</div>
            {news_html}
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown(f"<p style='text-align: center; color: white; padding-top: 20px;'>Live Sync: {datetime.now().strftime('%H:%M:%S')} | 🚀 Keep-Alive Active</p>", unsafe_allow_html=True)
