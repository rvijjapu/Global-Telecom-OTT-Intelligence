import streamlit as st
import feedparser
import requests
from datetime import datetime
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus 2026",
    page_icon="🌐",
    layout="wide"
)

# 2026-Specific Queries for RSS Feeds
# Using "when:7d" ensures only fresh 2026 news from the past week is pulled.
SECTION_QUERIES = {
    "telco": "telecom OSS BSS announcements 2026 when:7d",
    "ott": "OTT streaming mergers acquisitions 2026 when:7d",
    "sports": "sports media rights deals 2026 when:7d",
    "technology": "AI cloud computing telecom technology 2026 when:7d"
}

# ══════════════════════════════════════════════════════════════════════════════
# DATA FETCHING ENGINE (RSS)
# ══════════════════════════════════════════════════════════════════════════════

def fetch_google_news_rss(label, query):
    """Fetches and parses Google News RSS for reliable structured data."""
    encoded_query = urllib.parse.quote(query)
    # RSS URL structure for keyword search
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        # Feedparser is recommended for handling RSS XML reliably
        feed = feedparser.parse(rss_url)
        results = []
        
        for entry in feed.entries[:10]:
            results.append({
                "title": entry.title,
                "link": entry.link,
                "date": entry.published,
                "source": entry.source.get('title', 'Global News')
            })
        return label, results
    except Exception:
        return label, []

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD UI & RENDERING
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f1f5f9; }
    .header { text-align: center; padding: 2rem; background: linear-gradient(90deg, #1e40af, #3b82f6); border-radius: 12px; margin-bottom: 2rem; }
    .card { background-color: #1e293b; border-left: 5px solid #3b82f6; border-radius: 8px; padding: 1.2rem; margin-bottom: 1.2rem; }
    .title-link { color: #f8fafc; font-weight: 700; text-decoration: none; font-size: 1rem; }
    .meta { color: #94a3b8; font-size: 0.75rem; margin-top: 8px; }
    .section-title { text-align: center; font-weight: 800; text-transform: uppercase; padding: 10px; border-radius: 6px; margin-bottom: 20px; color: white; }
    .telco-h { background: #db2777; } .ott-h { background: #7c3aed; } 
    .sports-h { background: #059669; } .tech-h { background: #ea580c; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>🌐 Global Telecom & OTT Stellar Nexus</h1><p>2026 Live Executive Briefing</p></div>', unsafe_allow_html=True)

# Use ThreadPoolExecutor for concurrent section loading
with st.spinner("⚡ Fetching 2026 Intelligence..."):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetch_google_news_rss, label, q) for label, q in SECTION_QUERIES.items()]
        results_map = {f.result()[0]: f.result()[1] for f in futures}

# Render columns
cols = st.columns(4)
sections = [
    ("telco", "📡 Telco & OSS/BSS", "telco-h"),
    ("ott", "📺 OTT & Streaming", "ott-h"),
    ("sports", "🏆 Sports Rights", "sports-h"),
    ("technology", "⚡ Technology", "tech-h")
]

for i, (key, label, color_class) in enumerate(sections):
    with cols[i]:
        st.markdown(f'<div class="section-title {color_class}">{label}</div>', unsafe_allow_html=True)
        items = results_map.get(key, [])
        
        if not items:
            st.info("No fresh 2026 alerts found. Checking global nodes...")
        
        for item in items:
            st.markdown(f"""
            <div class="card">
                <a href="{item['link']}" target="_blank" class="title-link">{item['title']}</a>
                <div class="meta">{item['source']} • {item['date']}</div>
            </div>
            """, unsafe_allow_html=True)

# Auto-refresh script (every 10 minutes)
st.markdown("<script>setTimeout(function(){ window.location.reload(); }, 600000);</script>", unsafe_allow_html=True)
