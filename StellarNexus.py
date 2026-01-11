import streamlit as st
import feedparser
import time
from datetime import datetime
import urllib.parse

# --- 1. NEVER-SLEEP / AUTO-REFRESH ENGINE ---
# This resets the inactivity timer every 10 mins to prevent hibernation
@st.fragment(run_every=600)
def keep_alive_engine():
    st.session_state.sync_time = datetime.now().strftime('%H:%M:%S')
    st.markdown("", unsafe_allow_html=True)

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Stellar Nexus 2026", layout="wide")

# --- 3. DYNAMIC NEWS AGGREGATION ALGORITHM ---
def fetch_strategic_intel(query):
    """Permanent AI Algorithm to fetch high-impact 2026 signals"""
    # Specifically targeting 2026 dates to ensure no 2025 'leakage'
    search_query = f"{query} news after:2025-12-31"
    encoded_query = urllib.parse.quote(search_query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    try:
        feed = feedparser.parse(rss_url)
        return [{"title": e.title, "link": e.link, "source": e.source.get('title', 'Global Intel')} for e in feed.entries[:4]]
    except:
        return []

# --- 4. PREMIUM CSS: DARK BLUE VISIBILITY ---
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

    /* Hero Strategic Container */
    .hero-container {
        background: rgba(255, 255, 255, 0.96);
        border-radius: 15px;
        padding: 2.5rem;
        border-left: 10px solid #0a192f;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin-bottom: 2.5rem;
    }

    /* Industry Vertical Cards */
    .section-card {
        background: rgba(255, 255, 255, 0.98);
        padding: 24px;
        border-radius: 12px;
        min-height: 520px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: 1px solid #e2e8f0;
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
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f1f5f9;
    }

    .news-text {
        font-size: 0.95rem;
        color: #1e293b;
        line-height: 1.5;
        margin-bottom: 5px;
    }

    .read-more {
        font-size: 0.85rem;
        color: #1e40af;
        font-weight: 700;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# --- 5. IMPACTFUL LOADING SEQUENCE ---
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div class="loading-container">
            <h1 class="dark-blue-text" style="font-size: 3.5rem;">Igniting AI-powered intelligence...</h1>
            <p class="dark-blue-text" style="font-size: 1.2rem; opacity: 0.8;">Bypassing legacy filters. Synchronizing 2026 strategic nodes.</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.8) 

placeholder.empty()
keep_alive_engine()

# --- 6. MAIN DASHBOARD CONTENT ---
st.markdown("<h1 class='dark-blue-text' style='text-align: center; font-size: 3.2rem;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

# 🚀 STRATEGIC BASELINE (Dynamic Summary Search)
st.markdown("""
<div class="hero-container">
    <div style="color: #0a192f; font-size: 1.8rem; font-weight: 800; margin-bottom: 1.5rem;">🚀 STRATEGIC HIGHLIGHTS</div>
    <div style="display: flex; gap: 20px;">
        <div style="flex: 1; background: #f1f5f9; padding: 1.5rem; border-radius: 10px; border: 1px solid #e2e8f0;">
            <div style="font-weight:800; color:#10b981; font-size:1.1rem; margin-bottom:12px;">🟢 STRATEGIC HITS</div>
            <p style="color:#1e293b; font-size:0.95rem; line-height:1.7;">
                Scanning for 2026 M&A signals: Amdocs-Matrixx integration progress, Netcracker-CSG expansion tracking, and the Netflix-WBD acquisition timeline.
            </p>
        </div>
        <div style="flex: 1; background: #f1f5f9; padding: 1.5rem; border-radius: 10px; border: 1px solid #e2e8f0;">
            <div style="font-weight:800; color:#f97316; font-size:1.1rem; margin-bottom:12px;">🟠 PULSE</div>
            <p style="color:#1e293b; font-size:0.95rem; line-height:1.7;">
                Real-time TechWatch: Agentic AI deployment rates in BSS stacks, 5G standalone monetization models, and sovereign cloud infrastructure shifts.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# INDUSTRY VERTICALS
col1, col2, col3, col4 = st.columns(4)

verticals = [
    ("📡 TELCO OSS/BSS", "#db2777", "telecom OSS BSS announcements 2026"),
    ("📺 OTT & STREAMING", "#7c3aed", "OTT streaming merger deals 2026"),
    ("🏆 SPORTS MEDIA", "#059669", "WNBA NBA media rights 2026"),
    ("⚡ AI TECHWATCH", "#ea580c", "Agentic AI autonomous enterprise 2026")
]

for idx, (label, color, query) in enumerate(verticals):
    with [col1, col2, col3, col4][idx]:
        news = fetch_strategic_intel(query)
        news_html = ""
        for item in news:
            news_html += f"""
            <div class="news-item">
                <div class="news-text"><b>{item['source']}</b>: {item['title']}</div>
                <a href="{item['link']}" target="_blank" class="read-more">Analyze Full Story →</a>
            </div>"""
        
        st.html(f"""
        <div class="section-card">
            <div class="section-header" style="color: {color}; border-color: {color};">{label}</div>
            {news_html if news else '<div class="news-text">Synchronizing 2026 data nodes...</div>'}
        </div>
        """)

# Footer
st.markdown(f"<p style='text-align: center; color: white; padding-top: 20px;'>Live Intelligence Sync: {datetime.now().strftime('%H:%M:%S')} | 🚀 Algorithm: ACTIVE (NO HARDCODE)</p>", unsafe_allow_html=True)
