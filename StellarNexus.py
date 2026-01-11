import streamlit as st
import feedparser
import time
from datetime import datetime
import re

# --- 1. CONFIGURATION & PERMANENT AI ALGORITHM ---
# Dynamic RSS Feeds for 2026 Intelligence
RSS_FEEDS = {
    "telco": "https://news.google.com/rss/search?q=OSS+BSS+telecom+monetization+2026",
    "ott": "https://news.google.com/rss/search?q=OTT+streaming+merger+partnership+2026",
    "sports": "https://news.google.com/rss/search?q=sports+broadcasting+rights+streaming+2026",
    "technology": "https://news.google.com/rss/search?q=enterprise+AI+agentic+cloud+2026"
}

# Evergent Client/Competitor Watchlist for "Strategic Hits" Filtering
STRATEGIC_WATCH = ["Amdocs", "Netcracker", "NEC", "Netflix", "WBD", "Disney", "AT&T", "Jio"]

def fetch_dynamic_news(category):
    """Permanent AI Algorithm: Fetches and cleans live 2026 news nodes."""
    try:
        feed = feedparser.parse(RSS_FEEDS[category])
        results = []
        for entry in feed.entries[:5]:
            # Simple deduplication and cleaning
            title = re.sub(r'<[^>]+>', '', entry.title)
            results.append({"title": title, "link": entry.link})
        return results
    except:
        return [{"title": "Synchronizing global nodes...", "link": "#"}]

def generate_strategic_highlights(all_news):
    """AI Logic: Extracts 'Hits' and 'Pulse' based on priority keywords."""
    hits = []
    pulse = []
    for section in all_news.values():
        for item in section:
            if any(key.lower() in item['title'].lower() for key in STRATEGIC_WATCH):
                hits.append(item['title'])
            elif "AI" in item['title'] or "Agent" in item['title'] or "Cloud" in item['title']:
                pulse.append(item['title'])
    return list(set(hits))[:3], list(set(pulse))[:3]

# --- 2. PAGE CONFIGURATION & CSS ---
st.set_page_config(page_title="Stellar Nexus CEO Dashboard", layout="wide")

# (Insert your provided CSS here)
st.markdown("""<style>...</style>""", unsafe_allow_html=True)

# --- 3. DYNAMIC REFRESH FRAGMENT (The "Never-Sleep" Engine) ---
@st.fragment(run_every=300) # Auto-refreshes every 5 minutes (300 seconds)
def render_dashboard():
    # A. Fetch Live Data
    news_data = {cat: fetch_dynamic_news(cat) for cat in RSS_FEEDS.keys()}
    hits, pulse = generate_strategic_highlights(news_data)

    # B. Header & Highlights
    st.markdown("<h1 class='dark-blue-text' style='text-align: center;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)
    
    hits_html = "".join([f"• {h}<br>" for h in hits]) if hits else "Scanning for strategic moves..."
    pulse_html = "".join([f"• {p}<br>" for p in pulse]) if pulse else "Monitoring market pulse..."

    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-title">🚀 HIGHLIGHTS</div>
        <div style="display: flex; gap: 20px;">
            <div class="hero-box" style="flex: 1;">
                <div style="font-weight:800; color:#10b981; font-size:1.1rem; margin-bottom:12px;">🟢 STRATEGIC HITS</div>
                <div style="color:#1e293b; font-size:0.95rem; line-height:1.7;">{hits_html}</div>
            </div>
            <div class="hero-box" style="flex: 1;">
                <div style="font-weight:800; color:#f97316; font-size:1.1rem; margin-bottom:12px;">🟠 PULSE</div>
                <div style="color:#1e293b; font-size:0.95rem; line-height:1.7;">{pulse_html}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # C. Industry Vertical Grid
    cols = st.columns(4)
    verticals = [
        ("📡 TELCO OSS/BSS", "#db2777", "telco"),
        ("📺 OTT & STREAMING", "#7c3aed", "ott"),
        ("🏆 SPORTS MEDIA", "#059669", "sports"),
        ("⚡ AI TECHWATCH", "#ea580c", "technology")
    ]

    for idx, (label, color, key) in enumerate(verticals):
        with cols[idx]:
            items_html = "".join([
                f'<div class="news-item"><div class="news-text">• {n["title"]}</div>'
                f'<a href="{n["link"]}" target="_blank" style="color:#1e40af; font-size:0.8rem;">Read Full Story →</a></div>' 
                for n in news_data[key]
            ])
            st.markdown(f"""
            <div class="section-card">
                <div class="section-header" style="color: {color}; border-color: {color};">{label}</div>
                {items_html}
            </div>
            """, unsafe_allow_html=True)

    st.markdown(f"<p style='text-align: center; color: white;'>Live Sync: {datetime.now().strftime('%H:%M:%S')} | 🚀 Never-Sleep Active</p>", unsafe_allow_html=True)

# 4. START DASHBOARD
render_dashboard()
