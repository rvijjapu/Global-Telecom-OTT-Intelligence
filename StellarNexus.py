import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime
import time

# 1. Page Configuration
st.set_page_config(page_title="AI Strategic Intelligence", layout="wide")

# 2. Intelligence Configuration
WATCHLIST = {
    "CLIENTS": ["AT&T", "Verizon", "Sony", "NBA", "Disney", "Netflix"],
    "COMPETITORS": ["Amdocs", "Netcracker", "Oracle", "Nokia", "Ericsson"],
    "STRATEGIC_KEYWORDS": ["merger", "acquisition", "billion", "agentic", "monetization", "deal"]
}

RSS_FEEDS = {
    "Telco": "https://news.google.com/rss/search?q=telecom+OSS+BSS+merger+2026",
    "OTT": "https://news.google.com/rss/search?q=OTT+streaming+merger+2026",
    "AI/Tech": "https://news.google.com/rss/search?q=enterprise+AI+platform+2026"
}

# 3. AI Scoring Logic
def calculate_strategic_score(title, summary):
    """Simple AI scoring based on strategic density."""
    text = (title + " " + summary).lower()
    score = 0
    # Boost for specific entities
    score += sum(15 for c in WATCHLIST["CLIENTS"] if c.lower() in text)
    score += sum(10 for comp in WATCHLIST["COMPETITORS"] if comp.lower() in text)
    # Boost for strategic intent
    score += sum(5 for kw in WATCHLIST["STRATEGIC_KEYWORDS"] if kw.lower() in text)
    return score

# 4. News Fetching Engine
def fetch_live_intelligence():
    all_news = []
    for category, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:10]:
            score = calculate_strategic_score(entry.title, getattr(entry, 'summary', ''))
            all_news.append({
                "Category": category,
                "Title": entry.title,
                "Link": entry.link,
                "Score": score,
                "Source": entry.source.title if 'source' in entry else "Global Intel"
            })
    return pd.DataFrame(all_news).sort_values(by="Score", ascending=False)

# 5. Permanent Auto-Refresh Fragment
@st.fragment(run_every="5m")  # Refreshes this block every 5 minutes
def news_feed_fragment():
    st.subheader("🚀 Live Strategic Intelligence (Auto-refreshes every 5m)")
    df = fetch_live_intelligence()
    
    # Display top high-impact news
    top_news = df.head(5)
    for _, row in top_news.iterrows():
        with st.container(border=True):
            st.markdown(f"**[{row['Category']}]** {row['Title']}")
            st.caption(f"Source: {row['Source']} | Strategic Score: {row['Score']}")
            st.link_button("View Analysis", row['Link'])

# 6. Main Dashboard UI
st.title("🌐 Stellar Nexus: Dynamic AI Dashboard")
st.sidebar.header("Intelligence Controls")
st.sidebar.info("Dashboard is active and permanently auto-refreshing.")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📊 Market Metrics")
    st.metric("Strategic Hits (24h)", "14", "+2")
    st.metric("Competitor Activity", "Low", "-5%")

with col2:
    # This block updates independently from the sidebar or metrics
    news_feed_fragment()

st.caption(f"Last Intelligence Sync: {datetime.now().strftime('%H:%M:%S')} | Engine: Stellar-Nexus-V4")
