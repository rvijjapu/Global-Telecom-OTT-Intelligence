import streamlit as st
import time
from datetime import datetime

# --- 1. NEVER-SLEEP / KEEP-ALIVE FRAGMENT ---
# This silently refreshes a hidden part of the app every 10 mins to prevent hibernation
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# --- 3. PREMIUM CSS: BACKGROUND & DARK BLUE STYLING ---
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
    
    .dark-blue-text {
        color: #0a192f !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.4);
    }

    /* Section Box Styling */
    .section-card {
        background: rgba(255, 255, 255, 0.96);
        padding: 24px;
        border-radius: 12px;
        min-height: 480px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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
</style>
""", unsafe_allow_html=True)

# --- 4. IMPACTFUL LOADING SCREEN ---
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div class="loading-container">
            <h1 class="dark-blue-text" style="font-size: 3.5rem;">Igniting AI-powered intelligence...</h1>
            <p class="dark-blue-text" style="font-size: 1.2rem; opacity: 0.8;">Synchronizing global strategic nodes. Please wait.</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.8) # Effect for CEO impact

placeholder.empty()

# Initialize Keep-Alive logic
keep_alive()

# --- 5. MAIN DASHBOARD ---
st.markdown("<h1 class='dark-blue-text' style='text-align: center; font-size: 3.2rem;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

# Industry Data Mapping
sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        {"t": "NEC/Netcracker scales North American operations via $2.9B CSG deal.", "l": "https://www.netcracker.com"},
        {"t": "Amdocs completes $200M Matrixx acquisition to dominate cloud-native charging.", "l": "https://www.lightreading.com"},
        {"t": "Reliance Jio eyes $4.5B from landmark 2026 public offering.", "l": "https://www.business-standard.com"}
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        {"t": "Netflix board approves $82.7B WBD merger to secure HBO content library.", "l": "https://www.variety.com"},
        {"t": "Discovery Global spin-off finalized to partition legacy debt from growth assets.", "l": "https://about.netflix.com"},
        {"t": "Ad-supported revenue overtakes premium subs for top OTT giants.", "l": "https://www.digitaltveurope.com"}
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        {"t": "WNBA secures landmark 11-year rights deal with Disney, Amazon, and NBC.", "l": "https://www.wnba.com"},
        {"t": "NBA domestic rights officially transition to Disney and Amazon ecosystems.", "l": "https://www.sportspromedia.com"},
        {"t": "Amazon Prime Video secures exclusive WNBA Finals rights through 2036.", "l": "https://www.amazon.com"}
    ]),
    ("⚡ CORE TECHNOLOGY", "#ea580c", [
        {"t": "Agentic AI market projected to hit $8.5B by EOY 2026.", "l": "https://www.techcrunch.com"},
        {"t": "Industrial robotics reach new 5.5M global unit record in 2026.", "l": "https://www.venturebeat.com"},
        {"t": "Enterprises shift from cloud-first to strategic hybrid for AI inference economics.", "l": "https://www.gartner.com"}
    ])
]

# --- 6. RENDER COLUMNS ---
col1, col2, col3, col4 = st.columns(4)

for idx, (label, color, news_list) in enumerate(sections):
    with [col1, col2, col3, col4][idx]:
        news_html = ""
        for item in news_list:
            news_html += f"""
            <div class="news-item">
                <div class="news-text">{item['t']}</div>
                <a href="{item['l']}" target="_blank" class="link-btn">Read Full Story →</a>
            </div>"""
        
        # Using st.html ensures raw tags are rendered correctly
        st.html(f"""
        <div class="section-card">
            <div class="section-header" style="color: {color}; border-color: {color};">{label}</div>
            {news_html}
        </div>
        """)

# Minimalist Sync Info
st.markdown(f"<p style='text-align: center; color: white; padding-top: 20px;'>Live Sync: {datetime.now().strftime('%H:%M:%S')} | 🚀 Never-Sleep Active</p>", unsafe_allow_html=True)
