import streamlit as st
import time
from datetime import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# 2. CUSTOM CSS FOR BACKGROUND & PROFESSIONAL STYLING
st.markdown("""
<style>
    /* Custom Background Image */
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
    }
    
    /* Center the Loading Text Container */
    .loading-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 80vh;
        text-align: center;
    }
    
    /* Professional Dark Blue Font for Titles */
    .dark-blue-text {
        color: #0a192f !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.3);
    }

    .main-title {
        font-size: 3rem !important;
        margin-bottom: 25px;
    }

    /* Section Box Styling */
    .section-box {
        background: rgba(255, 255, 255, 0.96);
        padding: 24px;
        border-radius: 12px;
        min-height: 480px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
    }

    .box-header {
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

    .read-more-link {
        color: #1e40af;
        font-weight: 700;
        text-decoration: none;
        font-size: 0.85rem;
    }
    .read-more-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# 3. IMPACTFUL LOADING SCREEN
# Placeholder allows us to swap the loading screen for the dashboard
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div class="loading-container">
            <h1 class="dark-blue-text" style="font-size: 2.8rem;">Igniting AI-powered intelligence...</h1>
            <p class="dark-blue-text" style="font-size: 1.1rem; opacity: 0.8;">Please wait while we synchronize global nodes.</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5) # Millisecond loading simulation

placeholder.empty()

# 4. MAIN DASHBOARD CONTENT
st.markdown("<h1 class='dark-blue-text main-title' style='text-align: center;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

# INDUSTRY DATA DEFINITIONS
sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        {"t": "NEC (Netcracker) completes $2.9B CSG acquisition to dominate global BSS/OSS market share.", "l": "https://www.netcracker.com"},
        {"t": "Amdocs acquires Matrixx Software for $200M to counter rising competitor scaling.", "l": "https://www.lightreading.com"},
        {"t": "Reliance Jio eyes $4.5B from public offering as IPO documentation enters advanced phase.", "l": "https://www.business-standard.com"}
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        {"t": "Netflix board approves $82.7B WBD merger to secure HBO content library.", "l": "https://www.variety.com"},
        {"t": "Warner Bros. Discovery separation into Discovery Global expected in Q3 2026.", "l": "https://about.netflix.com"},
        {"t": "Consolidation risks in Asian markets grow as major platforms merge content.", "l": "https://www.outlookindia.com"}
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        {"t": "WNBA secures landmark 11-year rights deal with Disney, Amazon, and NBCUniversal.", "l": "https://www.wnba.com"},
        {"t": "NBA domestic rights officially transition to Disney and Amazon ecosystems.", "l": "https://www.sportspromedia.com"},
        {"t": "Amazon Prime Video secures exclusive WNBA Finals rights through 2036.", "l": "https://www.amazon.com"}
    ]),
    ("⚡ CORE TECHNOLOGY", "#ea580c", [
        {"t": "Autonomous AI agent market projected to hit $8.5B by end of 2026.", "l": "https://www.techcrunch.com"},
        {"t": "Enterprises shift from cloud-first to strategic hybrid for AI inference economics.", "l": "https://www.gartner.com"},
        {"t": "Industrial robotics installations reach new 5.5M global unit record in 2026.", "l": "https://www.deloitte.com"}
    ])
]

# RENDER COLUMNS
cols = st.columns(4)
for idx, (label, color, news_list) in enumerate(sections):
    with cols[idx]:
        # Generate the HTML string without newlines to avoid rendering bugs
        news_html = ""
        for item in news_list:
            news_html += f"""<div class="news-item"><div class="news-text">{item['t']}</div><a href="{item['l']}" target="_blank" class="read-more-link">Read Full Story →</a></div>"""
        
        # Wrapping in st.html for best rendering results
        st.html(f"""<div class="section-box"><div class="box-header" style="color: {color}; border-color: {color};">{label}</div>{news_html}</div>""")

# Footer with Live Sync Time
st.markdown(f"<p style='text-align: center; color: white; padding: 20px;'>Live Sync: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
