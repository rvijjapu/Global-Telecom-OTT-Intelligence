import streamlit as st
import time
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Global Telecom & OTT Stellar Nexus", layout="wide")

# 2. Custom CSS for Professional Dark Blue Styling & Background
st.markdown("""
<style>
    /* Custom Background */
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
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
    
    /* Dark Blue Impactful Font for Loading and Title */
    .dark-blue-title {
        color: #0a192f !important;
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
        margin-bottom: 0px;
    }

    /* Card Containers for News */
    .section-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 24px;
        border-radius: 12px;
        min-height: 450px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    .section-header {
        font-size: 1.25rem;
        font-weight: 800;
        padding-bottom: 12px;
        border-bottom: 3px solid;
        text-transform: uppercase;
        margin-bottom: 15px;
    }

    .news-item {
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f1f5f9;
    }

    .news-text {
        font-size: 0.95rem;
        color: #334155;
        line-height: 1.5;
        margin-bottom: 5px;
    }

    .link-btn {
        color: #1e40af;
        font-weight: 700;
        text-decoration: none;
        font-size: 0.85rem;
    }
    .link-btn:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# 3. IMPACTFUL LOADING SCREEN
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div class="loading-container">
            <h1 class="dark-blue-title">Igniting AI-powered intelligence...</h1>
            <p style="color: #0a192f; font-weight: 600;">Synchronizing global strategic nodes</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.8) # Quick delay for effect

# Replace loading screen with main content
placeholder.empty()

# 4. MAIN DASHBOARD CONTENT
st.markdown("<h1 class='dark-blue-title' style='text-align: center;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

# Industry Sections Layout
col1, col2, col3, col4 = st.columns(4)

sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        {"t": "Amdocs completes $200M Matrixx acquisition to dominate cloud-native 5G charging.", "l": "https://www.lightreading.com"},
        {"t": "NEC scales Netcracker's footprint via $2.9B CSG acquisition.", "l": "https://www.netcracker.com"},
        {"t": "SaaS BSS adoption surges 25% as legacy billing stacks are decommissioned.", "l": "https://www.vanillaplus.com"}
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        {"t": "Netflix board moves to finalize $82.7B WBD merger, securing HBO and Warner studios.", "l": "https://www.variety.com"},
        {"t": "Discovery Global spin-off finalized to partition legacy debt from growth assets.", "l": "https://www.hollywoodreporter.com"},
        {"t": "Ad-supported revenue overtakes premium subscriptions for top OTT giants.", "l": "https://www.digitaltveurope.com"}
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        {"t": "WNBA historic 11-year rights deal begins, elevating package value to $200M/year.", "l": "https://www.espn.com"},
        {"t": "NBA domestic rights officially transition to Disney and Amazon ecosystems.", "l": "https://www.sportspromedia.com"},
        {"t": "FanDuel and DraftKings expand real-time fan engagement through AI highlights.", "l": "https://www.sportico.com"}
    ]),
    ("⚡ CORE TECHNOLOGY", "#ea580c", [
        {"t": "Agentic AI market projected to hit $8.5B by EOY 2026.", "l": "https://www.techcrunch.com"},
        {"t": "Industrial robotics reach new 5.5M global unit record as automation peaks.", "l": "https://www.venturebeat.com"},
        {"t": "NVIDIA and AWS launch sovereign AI infrastructure for regional data compliance.", "l": "https://www.zdnet.com"}
    ])
]

# Rendering function to keep news INSIDE cards
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
st.markdown(f"<p style='text-align: center; color: white;'>Sync Time: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
