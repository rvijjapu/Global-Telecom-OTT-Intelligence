import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import time
import re

# ==========================================
# 1. CORE DATA & KEYWORDS (CEO VISION)
# ==========================================
# (Your provided EVERGENT_CLIENTS and COMPETITORS lists go here)
# For brevity, we use a flattened list for matching
ALL_CLIENTS = [item for sublist in EVERGENT_CLIENTS.values() for item in sublist]
ALL_COMPETITORS = [item for sublist in COMPETITORS.values() for item in sublist]

# Strategic Keywords for "Hits" vs "Pulse"
STRATEGIC_HITS_KEYWORDS = ["merger", "acquisition", "deal", "billion", "million", "partnership", "contract"]
PULSE_KEYWORDS = ["ai", "agent", "5g", "streaming", "launch", "trend", "innovation"]

# ==========================================
# 2. DYNAMIC FETCHING ALGORITHM
# ==========================================
def fetch_news_intelligence():
    # Example feeds - can be expanded to any RSS URL
    feeds = [
        "https://news.google.com/rss/search?q=telecom+OSS+BSS+merger+2026",
        "https://news.google.com/rss/search?q=OTT+streaming+deal+2026",
        "https://news.google.com/rss/search?q=sports+media+rights+2026"
    ]
    
    all_articles = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.title.lower()
            
            # Identify if it mentions a Client or Competitor
            involved_client = next((c for c in ALL_CLIENTS if c in title), None)
            involved_competitor = next((comp for comp in ALL_COMPETITORS if comp in title), None)
            
            # Scoring for relevance
            score = 0
            if involved_client: score += 50
            if involved_competitor: score += 30
            if any(k in title for k in STRATEGIC_HITS_KEYWORDS): score += 20
            
            all_articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": entry.published,
                "score": score,
                "type": "Hit" if any(k in title for k in STRATEGIC_HITS_KEYWORDS) else "Pulse"
            })
            
    # Return top 20 most impactful articles
    return pd.DataFrame(all_articles).sort_values(by="score", ascending=False).head(20)

# ==========================================
# 3. STREAMLIT UI & AUTO-REFRESH
# ==========================================
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# Custom CSS for Dark Blue Executive Branding
st.markdown("""
<style>
    .stApp { background-color: #0a192f; color: white; }
    .card { background-color: #112240; padding: 20px; border-radius: 10px; border-left: 5px solid #64ffda; margin-bottom: 15px; }
    .hit-title { color: #64ffda; font-weight: bold; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

st.title("📡 Global Telecom & OTT Stellar Nexus")
st.subheader("CEO Strategic Intelligence Dashboard")

# Auto-refresh every 10 minutes
if "last_fetch" not in st.session_state or (time.time() - st.session_state.last_fetch > 600):
    st.session_state.news_df = fetch_news_intelligence()
    st.session_state.last_fetch = time.time()

df = st.session_state.news_df

# RENDER SECTIONS
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🟢 STRATEGIC HITS (M&A & High-Value Deals)")
    hits = df[df['type'] == 'Hit']
    for _, row in hits.iterrows():
        st.markdown(f"""<div class="card"><div class="hit-title">{row['title']}</div>
                    <a href="{row['link']}" target="_blank">Read Full Analysis</a></div>""", unsafe_allow_html=True)

with col2:
    st.markdown("### 🟠 MARKET PULSE (Trends & Innovations)")
    pulse = df[df['type'] == 'Pulse']
    for _, row in pulse.iterrows():
        st.markdown(f"""<div class="card"><div>{row['title']}</div>
                    <small>{row['published']}</small><br>
                    <a href="{row['link']}" target="_blank">View Insight</a></div>""", unsafe_allow_html=True)

st.caption(f"Last Intelligence Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
