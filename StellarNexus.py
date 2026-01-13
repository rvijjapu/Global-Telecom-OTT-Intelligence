import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time
import streamlit.components.v1 as components

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLING - Fixed layout & containment
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    * { 
        box-sizing: border-box; 
        margin: 0; 
        padding: 0; 
    }
    
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', sans-serif;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }
    
    .header-container {
        background: rgba(255, 255, 255, 0.97);
        padding: 1.6rem 2.2rem;
        text-align: center;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.14);
        margin: 0.8rem 0 2.2rem 0;
        border-bottom: 5px solid #1e40af;
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: #0a192f;
        margin: 0;
        letter-spacing: -0.6px;
    }
    
    .subtitle {
        font-size: 1.15rem;
        color: #475569;
        margin-top: 0.6rem;
        font-weight: 500;
    }
    
    .hero-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2.2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.12);
        border: 1px solid #e2e8f0;
    }
    
    .hero-title {
        color: #0a192f;
        font-size: 1.95rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        border-left: 6px solid #1e40af;
        padding-left: 15px;
    }
    
    .col-header {
        padding: 14px 16px;
        border-radius: 14px 14px 0 0;
        color: white;
        font-weight: 700;
        font-size: 1.05rem;
        text-align: center;
        box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    }
    
    .col-header-pink    { background: linear-gradient(135deg, #ec4899, #db2777); }
    .col-header-purple  { background: linear-gradient(135deg, #a78bfa, #8b5cf6); }
    .col-header-green   { background: linear-gradient(135deg, #34d399, #10b981); }
    .col-header-orange  { background: linear-gradient(135deg, #fb923c, #f97316); }
    
    .section-box {
        background: white;
        border-radius: 0 0 14px 14px;
        box-shadow: 0 6px 24px rgba(0,0,0,0.1);
        overflow: hidden;
        margin-bottom: 1.8rem;
        border: 1px solid #e5e7eb;
    }
    
    .news-container {
        padding: 14px;
        min-height: 420px;
        max-height: 640px;
        overflow-y: auto;
    }
    
    .news-card {
        background: #fafbfc;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 12px;
        transition: all 0.25s ease;
    }
    
    .news-card:hover {
        background: #f8fafc;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    
    .news-card-priority {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border: 2px solid #fbbf24;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    
    .news-title {
        color: #1e40af;
        font-size: 0.95rem;
        font-weight: 600;
        line-height: 1.4;
        text-decoration: none;
        display: block;
        margin-bottom: 8px;
    }
    
    .news-title:hover {
        color: #1d4ed8;
        text-decoration: underline;
    }
    
    .news-meta {
        font-size: 0.78rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
    
    .time-hot    { color: #dc2626; font-weight: 600; }
    .time-warm   { color: #ea580c; font-weight: 600; }
    .time-normal { color: #64748b; }
    
    .news-container::-webkit-scrollbar {
        width: 6px;
    }
    .news-container::-webkit-scrollbar-track {
        background: #f3f4f6;
        border-radius: 10px;
    }
    .news-container::-webkit-scrollbar-thumb {
        background: #9ca3af;
        border-radius: 10px;
    }
    
    #MainMenu, footer, header { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
    
    [data-testid="column"] > div {
        padding: 0 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# RSS FEEDS & CONFIGURATION (your original list)
# ──────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/", "ott"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml", "sports"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("Wired", "https://www.wired.com/feed/rss", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & STREAMING", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "AI TECHWATCH", "style": "col-header-orange"},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# Your filters, keywords, clients, competitors... (keep your original ones)

# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS (your original ones - only showing signature)
# ──────────────────────────────────────────────────────────────────────────────
# clean(), is_content_appropriate(), calculate_relevance_score(), fetch_feed(),
# load_feeds(), get_time_str()  → keep your existing implementations

# ──────────────────────────────────────────────────────────────────────────────
# IMPROVED SECTION RENDERING - Strict containment
# ──────────────────────────────────────────────────────────────────────────────
def render_section(icon, name, style_class, items):
    header = f'''
    <div class="{style_class}">
        {icon} {name}
    </div>
    '''
    
    news_html = ""
    if not items:
        news_html = '''
        <div style="text-align:center; color:#94a3b8; padding:100px 20px; font-size:1.1rem;">
            No recent relevant news
        </div>
        '''
    else:
        for item in items:
            time_str, time_class = get_time_str(item["pub"])
            title = html.escape(item["title"])
            link = html.escape(item["link"])
            source = html.escape(item["source"])
            
            card_class = "news-card-priority" if item.get("priority", False) else "news-card"
            
            news_html += f'''
            <div class="{card_class}">
                <a href="{link}" target="_blank" class="news-title">{title}</a>
                <div class="news-meta">
                    <span class="{time_class}">{time_str}</span>
                    <span>•</span>
                    <span>{source}</span>
                </div>
            </div>
            '''
    
    full_html = f'''
    <div class="section-box">
        {header}
        <div class="news-container">
            {news_html}
        </div>
    </div>
    '''
    
    # Use generous height + scrolling
    components.html(full_html, height=620, scrolling=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION FLOW
# ──────────────────────────────────────────────────────────────────────────────

# Loading screen (optional - your version)
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:70vh; text-align:center;">
            <h1 style="color:#0a192f; font-size:2.9rem; font-weight:800;">⚡ Activating Intelligence Engine...</h1>
            <p style="color:#64748b; font-size:1.25rem; margin-top:1rem;">Collecting latest global telecom & media signals</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)

placeholder.empty()

# Header & Strategic Highlights (your original content)
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time Competitive Intelligence Dashboard • January 2026</p>
</div>
""", unsafe_allow_html=True)

# ... your hero/highlights section ...

# Load data
with st.spinner("Loading latest industry signals..."):
    data = load_feeds()

# Render columns with fixed layout
cols = st.columns(4)

for idx, cat in enumerate(["telco", "ott", "sports", "technology"]):
    sec = SECTIONS[cat]
    items = data.get(cat, [])[:10]
    
    with cols[idx]:
        render_section(
            sec["icon"],
            sec["name"],
            sec["style"],
            items
        )

# Footer
st.markdown(f'''
<div style="text-align:center; color:rgba(255,255,255,0.92); font-size:0.85rem; margin:2.5rem 0 1.5rem; 
            padding:18px; background:linear-gradient(135deg,rgba(10,25,47,0.96),rgba(30,41,59,0.96)); 
            border-radius:12px;">
    <p><strong>🕐 Live Update:</strong> {datetime.now().strftime('%H:%M:%S')} IST</p>
    <p style="margin-top:8px; font-size:0.75rem; opacity:0.88;">
        Powered by Real-time RSS Intelligence Engine
    </p>
</div>
''', unsafe_allow_html=True)

# Auto-refresh
st.markdown('<script>setTimeout(() => {window.location.reload()}, 300000);</script>', unsafe_allow_html=True)
