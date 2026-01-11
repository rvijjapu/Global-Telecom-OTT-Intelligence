import streamlit as st
import time
from datetime import datetime

# --- 1. NEVER-SLEEP / KEEP-ALIVE FRAGMENT ---
# Resets inactivity timer every 10 minutes to prevent hibernation
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# --- 3. PREMIUM CSS: BACKGROUND & DARK BLUE BRANDING ---
st.markdown("""
<style>
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
    }
    
    .loading-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 80vh;
        text-align: center;
    }
    
    /* IMPACTFUL DARK BLUE FONTS */
    .dark-blue-text {
        color: #0a192f !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.4);
    }

    .main-title {
        font-size: 3.2rem !important;
        margin-bottom: 25px;
    }

    /* Professional Content Containers */
    .hero-container {
        background: rgba(255, 255, 255, 0.96);
        padding: 2.5rem;
        border-radius: 15px;
        margin-bottom: 2.5rem;
        border-left: 10px solid #0a192f;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }

    .section-card {
        background: rgba(255, 255, 255, 0.96);
        padding: 24px;
        border-radius: 12px;
        min-height: 420px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: 1px solid #e2e8f0;
    }

    .section-header {
        font-size: 1.25rem;
        font-weight: 800;
        padding-bottom: 12px;
        border-bottom: 3px solid;
        text-transform: uppercase;
        margin-bottom: 15px;
    }

    .news-text {
        font-size: 0.95rem;
        color: #1e293b;
        line-height: 1.6;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f1f5f9;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. IMPACTFUL LOADING SEQUENCE ---
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div class="loading-container">
            <h1 class="dark-blue-text" style="font-size: 3.5rem;">Igniting AI-powered intelligence...</h1>
            <p class="dark-blue-text" style="font-size: 1.2rem; opacity: 0.8;">Synchronizing global strategic nodes. Please wait.</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.8) 

placeholder.empty()
keep_alive()

# --- 5. MAIN DASHBOARD CONTENT ---
st.markdown("<h1 class='dark-blue-text' style='text-align: center; font-size: 3.2rem;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

# --- TOP SECTION: STRATEGIC HITS & AGENTIC REALITY ---
st.markdown("""
<div class="hero-container">
    <div style="color: #0a192f; font-size: 1.8rem; font-weight: 800; margin-bottom: 1.5rem;">🚀 STRATEGIC BASELINE</div>
    <div style="display: flex; gap: 20px;">
        <div style="flex: 1; background: #f1f5f9; padding: 1.5rem; border-radius: 10px; border: 1px solid #e2e8f0;">
            <div style="font-weight:800; color:#10b981; font-size:1.1rem; margin-bottom:12px;">🟢 STRATEGIC HITS (JAN 2026)</div>
            <div style="color:#1e293b; font-size:0.95rem; line-height:1.7;">
                <b>Netflix-WBD Merger:</b> Board approves $82.7B acquisition to unify HBO Max and Warner studios into Netflix's core ecosystem.<br><br>
                <b>NEC Expansion:</b> Finalization of $2.9B CSG acquisition scales Netcracker's North American SaaS footprint.
            </div>
        </div>
        <div style="flex: 1; background: #f1f5f9; padding: 1.5rem; border-radius: 10px; border: 1px solid #e2e8f0;">
            <div style="font-weight:800; color:#f97316; font-size:1.1rem; margin-bottom:12px;">🟠 TECH PULSE: AGENTIC REALITY</div>
            <div style="color:#1e293b; font-size:0.95rem; line-height:1.7;">
                <b>Agentic BSS:</b> 40% of standard BSS operational tasks are now handled by autonomous agents across Tier-1 telcos.<br><br>
                <b>Inference Power:</b> AI inference demand spikes, leading to a shift toward strategic hybrid infrastructure models.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- INDUSTRY VERTICALS ---
col1, col2, col3, col4 = st.columns(4)

sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        "Amdocs completes $200M Matrixx acquisition to dominate cloud-native 5G charging.",
        "NEC (Netcracker) scales global BSS market share following $2.9B CSG acquisition.",
        "Reliance Jio initiates 2026 IPO documentation for landmark public offering."
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        "Netflix board rejects Paramount tender offer in favor of $82.7B WBD combination.",
        "Discovery Global spin-off finalized to partition legacy debt from growth assets.",
        "Ad-tier revenue officially overtakes premium subs for top OTT platforms."
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        "WNBA secures landmark 11-year rights deal with Disney, Amazon, and NBCUniversal.",
        "NBA domestic rights officially transition to Disney and Amazon ecosystems.",
        "Amazon Prime Video secures exclusive WNBA Finals rights through 2036."
    ]),
    ("⚡ CORE TECHNOLOGY", "#ea580c", [
        "Autonomous AI agent market projected to hit $8.5B by EOY 2026.",
        "Industrial robotics reach new 5.5M global unit record in early 2026.",
        "Enterprises shift from cloud-first to strategic hybrid for AI inference economics."
    ])
]

for idx, (label, color, news_list) in enumerate(sections):
    with [col1, col2, col3, col4][idx]:
        news_html = "".join([f'<div class="news-text">• {item}</div>' for item in news_list])
        st.html(f"""
        <div class="section-card">
            <div class="section-header" style="color: {color}; border-color: {color};">{label}</div>
            {news_html}
        </div>
        """)

# --- FOOTER ---
st.markdown(f"<p style='text-align: center; color: white; padding-top: 20px;'>Live Sync: {datetime.now().strftime('%H:%M:%S')} | 🚀 Never-Sleep Active</p>", unsafe_allow_html=True)
