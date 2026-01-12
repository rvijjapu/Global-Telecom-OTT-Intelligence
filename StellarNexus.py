import streamlit as st
import feedparser
import time
from datetime import datetime
import urllib.parse

# 1. CORE SEARCH NODES (Direct 2026 Search Strings)
# These nodes find LIVE news; nothing is stored in the code.
SECTION_QUERIES = {
    "telco": "OSS BSS 5G billing monetization after:2026-01-01",
    "ott": "OTT streaming platform merger acquisition after:2026-01-01",
    "sports": "sports media rights broadcast deal after:2026-01-01",
    "technology": "agentic AI autonomous enterprise software after:2026-01-01"
}

# 2. DYNAMIC FETCHING ALGORITHM
def fetch_live_signals(query, limit=5):
    """
    Scans the Google News RSS node for 2026 strategic events.
    """
    encoded_query = urllib.parse.quote(query)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        feed = feedparser.parse(rss_url)
        results = []
        for entry in feed.entries[:limit]:
            results.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "source": entry.get("source", {}).get("title", "Global Intel"),
                "score": 100 if any(word in entry.title.lower() for word in ['merger', 'acquisition', 'billion', 'deal']) else 0
            })
        return results
    except Exception:
        return []

# 3. DASHBOARD UI & AUTO-REFRESH (Every 5 Minutes)
st.set_page_config(page_title="Stellar Nexus CEO Hub", layout="wide")

@st.fragment(run_every=300)
def render_live_dashboard():
    # Fetch Data Dynamically
    news_data = {k: fetch_live_signals(v) for k, v in SECTION_QUERIES.items()}

    # Header Styling
    st.markdown("<h1 style='color:#0a192f; text-align:center;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

    # DYNAMIC HIGHLIGHTS (Calculated from fetched results)
    col_h, col_p = st.columns(2)
    
    with col_h:
        st.markdown("""<div style='background:#f1f5f9; padding:20px; border-radius:12px; border-left:8px solid #10b981;'>
            <h3 style='color:#10b981;'>🟢 STRATEGIC HITS</h3>""", unsafe_allow_html=True)
        # Find highest scored items dynamically
        all_hits = sorted([it for sub in news_data.values() for it in sub], key=lambda x: x['score'], reverse=True)
        for hit in all_hits[:3]:
            st.write(f"• **{hit['title']}**")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_p:
        st.markdown("""<div style='background:#f1f5f9; padding:20px; border-radius:12px; border-left:8px solid #f97316;'>
            <h3 style='color:#f97316;'>🟠 PULSE</h3>""", unsafe_allow_html=True)
        # Show latest entries across all categories
        for key in news_data:
            if news_data[key]:
                st.write(f"• **{news_data[key][0]['title']}**")
        st.markdown("</div>", unsafe_allow_html=True)

    # INDUSTRY VERTICALS
    st.write("---")
    cols = st.columns(4)
    verticals = [("📡 TELCO OSS/BSS", "telco"), ("📺 OTT", "ott"), ("🏆 SPORTS", "sports"), ("⚡ AI TECH", "technology")]
    
    for idx, (label, key) in enumerate(verticals):
        with cols[idx]:
            st.subheader(label)
            for item in news_data[key]:
                st.markdown(f"**{item['source']}**: {item['title']}")
                st.markdown(f"[Source Article]({item['link']})")
                st.write("---")

    st.caption(f"Last Intelligence Sync: {datetime.now().strftime('%H:%M:%S')} | 🚀 Engine Active")

# 4. START ENGINE
render_live_dashboard()
