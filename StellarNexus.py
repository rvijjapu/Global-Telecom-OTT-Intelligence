import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import urllib.parse
import time

# ==============================================================================
# 1. CORE DATA LISTS (GLOBAL SCOPE - DEFINED FIRST TO PREVENT NAMEERROR)
# ==============================================================================

EVERGENT_CLIENTS = {
    "Astro": ["astro malaysia", "sooka", "njoi"],
    "FOX": ["fox sports", "fox corporation", "fox networks"],
    "AT&T": ["at&t", "att inc", "directv"],
    "NBA": ["nba", "national basketball"],
    "Shahid": ["shahid", "shahid vip", "mbc shahid"],
    "Sky": ["sky nz", "sky uk", "sky italia", "sky deutschland"],
    "Sony": ["sony pictures", "sonyliv", "sony entertainment"],
    "Telekom Malaysia": ["telekom malaysia", "tm unifi", "tm"],
    "BBC": ["bbc", "british broadcasting", "bbc iplayer"]
}

COMPETITORS = {
    "Netcracker": ["netcracker", "nec netcracker"],
    "Amdocs": ["amdocs", "amdocs ltd"],
    "CSG": ["csg systems", "csg international"],
    "Oracle": ["oracle communications", "oracle telecom"],
    "Cerillion": ["cerillion", "cerillion plc"],
    "Matrixx": ["matrixx", "matrixx software"],
    "Optiva": ["optiva", "optiva inc"]
}

# Flattens dictionaries for efficient searching
CLIENT_SEARCH_LIST = [name.lower() for sublist in EVERGENT_CLIENTS.values() for name in sublist]
COMPETITOR_SEARCH_LIST = [name.lower() for sublist in COMPETITORS.values() for name in sublist]

# ==============================================================================
# 2. DYNAMIC INTELLIGENCE ALGORITHM
# ==============================================================================

def fetch_strategic_intel(query, category):
    """Fetches live Jan 2026 news and ranks by strategic importance."""
    # Strict 'after:2026-01-01' ensures only current news is fetched
    encoded_query = urllib.parse.quote(f"{query} after:2026-01-01")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    feed = feedparser.parse(rss_url)
    scored_results = []
    
    for entry in feed.entries[:12]:
        title_lower = entry.title.lower()
        score = 0
        
        # 🔹 SIGNAL BOOST LOGIC
        if any(client in title_lower for client in CLIENT_SEARCH_LIST): score += 15
        if any(comp in title_lower for comp in COMPETITOR_SEARCH_LIST): score += 10
        if any(k in title_lower for k in ["merger", "acquisition", "billion", "contract", "agentic"]): score += 5
        
        scored_results.append({
            "title": entry.title,
            "link": entry.link,
            "source": entry.source.title,
            "score": score,
            "category": category,
            "published": entry.published
        })
    return scored_results

# ==============================================================================
# 3. STREAMLIT UI: EXECUTIVE DASHBOARD
# ==============================================================================

st.set_page_config(page_title="Stellar Nexus 2026", layout="wide")

# CEO Brand Styling (Dark Blue & Emerald)
st.markdown("""
<style>
    .stApp { background: #0a192f; color: white; }
    .ceo-card { background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 1.5rem; border-left: 8px solid #10b981; margin-bottom: 2rem; }
    .vertical-card { background: rgba(255, 255, 255, 0.08); padding: 1.2rem; border-radius: 10px; min-height: 550px; border: 1px solid #1e293b; }
    .priority-badge { background: #10b981; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.fragment(run_every=600)
def render_dashboard():
    st.markdown("<h1 style='text-align: center; color: #10b981; font-size: 3.2rem;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)
    
    # Run Algorithm
    queries = {
        "telco": "OSS BSS billing monetization 2026",
        "ott": "streaming OTT platform merger 2026",
        "sports": "sports media rights broadcasting 2026",
        "tech": "agentic AI enterprise software 2026"
    }
    
    all_news = []
    for cat, query in queries.items():
        all_news.extend(fetch_strategic_intel(query, cat))
    df = pd.DataFrame(all_news)

    # 🚀 STRATEGIC HITS (Top 4 Highest Scored News)
    st.markdown("<div class='ceo-card'><h2>🚀 STRATEGIC HITS (Evergent Priority)</h2>", unsafe_allow_html=True)
    top_hits = df.sort_values(by="score", ascending=False).head(4)
    cols = st.columns(4)
    for i, (_, row) in enumerate(top_hits.iterrows()):
        with cols[i]:
            st.markdown(f"**{row['source']}** \n[{row['title']}]({row['link']})")
    st.markdown("</div>", unsafe_allow_html=True)

    # 📊 INDUSTRY VERTICALS
    v_cols = st.columns(4)
    labels = [("📡 TELCO", "telco"), ("📺 OTT", "ott"), ("🏆 SPORTS", "sports"), ("⚡ AI TECH", "tech")]
    
    for i, (label, key) in enumerate(labels):
        with v_cols[i]:
            st.markdown(f"### {label}")
            items = df[df['category'] == key].sort_values(by="score", ascending=False).head(5)
            for _, item in items.iterrows():
                badge = "<span class='priority-badge'>HIGH IMPACT</span>" if item['score'] > 12 else "•"
                st.markdown(f"<div class='vertical-card'>{badge} **{item['source']}**: {item['title']}  \n[Strategic Analysis →]({item['link']})</div>", unsafe_allow_html=True)
                st.divider()

    st.caption(f"Last Intel Sync: {datetime.now().strftime('%H:%M:%S')} | 🚀 Dynamic Sync Active")

render_dashboard()
