import streamlit as st
import feedparser
import requests
import time
from datetime import datetime
import urllib.parse
import re

# --- 1. CONFIGURATION & PERMANENT KEYWORDS ---
# These ensure the AI only pulls relevant news
SECTION_QUERIES = {
    "telco": "(OSS OR BSS OR 'revenue management' OR '5G billing') telecom",
    "ott": "(OTT OR streaming OR SVOD OR 'content licensing') platform",
    "sports": "('media rights' OR broadcasting OR streaming) sports",
    "technology": "('enterprise AI' OR SaaS OR 'cloud platform') technology"
}

# --- 2. DYNAMIC NEWS FETCHING ALGORITHM ---
def fetch_live_signals(query, limit=5):
    """Fetches real-time 2026 signals from Google News RSS."""
    # Strict 2026 filter to ensure current relevance
    encoded_query = urllib.parse.quote(f"{query} after:2026-01-01")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    try:
        feed = feedparser.parse(rss_url)
        results = []
        for entry in feed.entries[:limit]:
            results.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "source": entry.get("source", {}).get("title", "Global Intel"),
                "date": entry.get("published", "")
            })
        return results
    except Exception as e:
        return []

# --- 3. AI AGENT FOR STRATEGIC SUMMARIZATION ---
def generate_ceo_brief(news_data):
    """
    Simulated AI logic to identify 'Strategic Hits' & 'Pulse' from dynamic data.
    In a live app, you would pass this news_data to Groq/Llama-3.3.
    """
    all_headlines = [item['title'] for section in news_data.values() for item in section]
    
    # AI Logic: Filter for M&A, billion-dollar deals, and breakthrough trends
    hits = [h for h in all_headlines if any(x in h.lower() for x in ['merger', 'acquisition', 'billion', '$'])]
    pulse = [h for h in all_headlines if any(x in h.lower() for x in ['ai', 'agent', 'future', 'trend'])]
    
    return hits[:3], pulse[:3]

# --- 4. STREAMLIT UI & AUTO-REFRESH ---
st.set_page_config(page_title="Stellar Nexus CEO 2026", layout="wide")

# Persistent state for 5-minute auto-refresh
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()

# REFRESH FRAGMENT: Runs every 300 seconds (5 minutes)
@st.fragment(run_every=300)
def dynamic_dashboard():
    # A. FETCH DATA DYNAMICALLY
    data = {k: fetch_live_signals(v) for k, v in SECTION_QUERIES.items()}
    hits, pulse = generate_ceo_brief(data)
    
    # B. RENDER STRATEGIC TOP SECTION
    st.markdown("<h1 style='color: #0a192f; text-align: center;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)
    
    col_h, col_p = st.columns(2)
    with col_h:
        st.info("### 🟢 STRATEGIC HITS\n" + "\n".join([f"- {h}" for h in hits]))
    with col_p:
        st.warning("### 🟠 PULSE\n" + "\n".join([f"- {p}" for p in pulse]))

    # C. RENDER INDUSTRY VERTICALS
    cols = st.columns(4)
    sections = [("telco", "📡 TELCO"), ("ott", "📺 OTT"), ("sports", "🏆 SPORTS"), ("technology", "⚡ TECH")]
    
    for idx, (key, label) in enumerate(sections):
        with cols[idx]:
            st.subheader(label)
            for item in data[key]:
                st.markdown(f"**{item['source']}**: {item['title']}\n[Read Full Story]({item['link']})")
                st.divider()

    st.caption(f"Last Intelligence Sync: {datetime.now().strftime('%H:%M:%S')}")

dynamic_dashboard()
