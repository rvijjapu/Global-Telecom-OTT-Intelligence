import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import pandas as pd

# ══════════════════════════════════════════════════════════════════════════════
# CEO WATCHLISTS (FOR RANKING & BOOSTING)
# ══════════════════════════════════════════════════════════════════════════════
CLIENTS = ["Astro", "AT&T", "FOX", "NBA", "Shahid", "MBC", "Sony", "Sky", "BBC", "Telekom Malaysia"]
COMPETITORS = ["Netcracker", "Amdocs", "CSG", "Oracle", "Ericsson", "Nokia", "Cerillion", "Matrixx"]
STRATEGIC_KEYWORDS = ["merger", "acquisition", "deal", "billion", "contract win", "partnership", "agentic", "monetization"]

# ══════════════════════════════════════════════════════════════════════════════
# UI & BRANDING
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Stellar Nexus CEO Hub", layout="wide")

st.markdown("""
<style>
    .stApp { background: #0a192f; color: #ffffff; }
    .hero-container { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; border-left: 10px solid #10b981; margin-bottom: 25px; }
    .news-card { background: rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px; margin-bottom: 12px; border: 1px solid #1e293b; transition: 0.3s; }
    .news-card:hover { border-color: #3b82f6; background: rgba(255, 255, 255, 0.15); }
    .priority-tag { background: #10b981; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; margin-bottom: 5px; display: inline-block; }
    .source-tag { color: #94a3b8; font-size: 0.75rem; font-weight: 500; }
    .section-header { font-size: 1.2rem; font-weight: 800; border-bottom: 2px solid #3b82f6; padding-bottom: 5px; margin-bottom: 15px; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INTELLIGENCE ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def score_article(title, summary):
    text = (title + " " + summary).lower()
    score = 0
    if any(client.lower() in text for client in CLIENTS): score += 20
    if any(comp.lower() in text for comp in COMPETITORS): score += 15
    if any(kw.lower() in text for kw in STRATEGIC_KEYWORDS): score += 10
    return score

def fetch_feed(category, url):
    items = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            score = score_article(title, summary)
            
            # Filter for 2026 relevance
            if "2024" in title or "2025" in title: continue
            
            items.append({
                "category": category,
                "title": title,
                "link": entry.get('link', '#'),
                "score": score,
                "source": entry.get('source', {}).get('title', 'Global News')
            })
    except Exception: pass
    return items

@st.cache_data(ttl=600)
def load_all_intelligence():
    urls = {
        "telco": "https://news.google.com/rss/search?q=telecom+OSS+BSS+merger+2026",
        "ott": "https://news.google.com/rss/search?q=streaming+OTT+merger+Disney+Netflix+2026",
        "sports": "https://news.google.com/rss/search?q=sports+broadcasting+rights+deal+2026",
        "tech": "https://news.google.com/rss/search?q=agentic+AI+enterprise+software+2026"
    }
    
    all_news = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetch_feed, cat, url) for cat, url in urls.items()]
        for future in as_completed(futures):
            all_news.extend(future.result())
    
    return pd.DataFrame(all_news)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

df = load_all_intelligence()

# Top Hero Section: Strategic Hits
st.markdown("<div class='hero-container'>", unsafe_allow_html=True)
st.markdown("### 🚀 CEO STRATEGIC HITS (JANUARY 12, 2026)")
top_hits = df.sort_values(by='score', ascending=False).head(3)
cols = st.columns(3)
for i, (_, row) in enumerate(top_hits.iterrows()):
    with cols[i]:
        st.markdown(f"**{row['source']}**")
        st.markdown(f"[{row['title']}]({row['link']})")
st.markdown("</div>", unsafe_allow_html=True)

# Main Grid
col1, col2, col3, col4 = st.columns(4)

sections = [
    (col1, "telco", "📡 OSS / BSS"),
    (col2, "ott", "📺 OTT & STREAMING"),
    (col3, "sports", "🏆 SPORTS MEDIA"),
    (col4, "tech", "⚡ AI & TECH")
]

for col, cat, title in sections:
    with col:
        st.markdown(f"<div class='section-header'>{title}</div>", unsafe_allow_html=True)
        cat_df = df[df['category'] == cat].sort_values(by='score', ascending=False).head(8)
        for _, item in cat_df.iterrows():
            priority = "<div class='priority-tag'>HIGH IMPACT</div>" if item['score'] >= 25 else ""
            st.markdown(f"""
            <div class='news-card'>
                {priority}
                <div class='source-tag'>{item['source']}</div>
                <a href='{item['link']}' target='_blank' style='text-decoration:none; color:#3b82f6; font-size:0.85rem; font-weight:700;'>
                    {item['title'][:80]}...
                </a>
            </div>
            """, unsafe_allow_html=True)

st.caption(f"Last Intelligence Sync: {datetime.now().strftime('%H:%M:%S')} | Engine: Stellar-Nexus-V4")
