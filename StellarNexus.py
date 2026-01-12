import streamlit as st
import feedparser
import time
from datetime import datetime
import urllib.parse
import pandas as pd

# ==========================================
# 1. COMPREHENSIVE INTELLIGENCE LISTS (GLOBAL)
# ==========================================
# (Variables populated from your comprehensive shared lists)
CLIENT_NAMES = [name.lower() for sub in EVERGENT_CLIENTS.values() for name in sub]
COMP_NAMES = [name.lower() for sub in COMPETITORS.values() for name in sub]

# ==========================================
# 2. DYNAMIC SEARCH & SCORING AGENT
# ==========================================
def fetch_strategic_intel(query, category):
    encoded_query = urllib.parse.quote(f"{query} after:2026-01-01")
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    
    results = []
    for entry in feed.entries[:15]:
        title = entry.title.lower()
        score = 0
        
        # 🔹 CEO SIGNAL BOOST LOGIC
        if any(c in title for c in CLIENT_NAMES): score += 12 # Priority Client
        if any(comp in title for comp in COMP_NAMES): score += 8 # Competitor Alert
        if any(k in title for k in ["merger", "billion", "acquisition", "agentic"]): score += 5
        
        results.append({
            "title": entry.title, "link": entry.link, "source": entry.source.title,
            "score": score, "category": category, "pub": entry.published
        })
    return results

# ==========================================
# 3. CEO "WOW" DASHBOARD UI
# ==========================================
st.set_page_config(page_title="Stellar Nexus CEO Hub", layout="wide")
st.markdown("<style>.stApp { background: #0a192f; color: white; } .hit-card { background: rgba(255,255,255,0.08); padding: 2rem; border-radius: 15px; border-left: 10px solid #10b981; margin-bottom: 2rem; }</style>", unsafe_allow_html=True)

@st.fragment(run_every=600)
def render_nexus():
    st.markdown("<h1 style='text-align:center; color:#10b981; font-size:3.5rem;'>Stellar Nexus CEO Hub</h1>", unsafe_allow_html=True)
    
    # Run Dynamic Intelligence Gathering
    queries = {"telco": "OSS BSS billing 2026", "ott": "streaming OTT merger 2026", "sports": "sports media rights 2026", "tech": "agentic AI enterprise 2026"}
    all_data = []
    for cat, query in queries.items(): all_data.extend(fetch_strategic_intel(query, cat))
    df = pd.DataFrame(all_data)

    # 🚀 STRATEGIC HITS
    st.markdown("<div class='hit-card'><h2>🚀 STRATEGIC HITS (Jan 12, 2026)</h2>", unsafe_allow_html=True)
    top_hits = df.sort_values(by="score", ascending=False).head(4)
    cols = st.columns(4)
    for i, (_, row) in enumerate(top_hits.iterrows()):
        with cols[i]: st.markdown(f"**{row['source']}**\n\n[{row['title']}]({row['link']})")
    st.markdown("</div>", unsafe_allow_html=True)

    # 📊 VERTICALS
    v_cols = st.columns(4)
    labels = [("📡 TELCO", "telco"), ("📺 OTT", "ott"), ("🏆 SPORTS", "sports"), ("⚡ AI TECH", "tech")]
    for i, (label, key) in enumerate(labels):
        with v_cols[i]:
            st.markdown(f"### {label}")
            items = df[df['category'] == key].sort_values(by="score", ascending=False).head(6)
            for _, item in items.iterrows():
                badge = "⭐ " if item['score'] > 10 else "• "
                st.markdown(f"{badge}**{item['source']}**: {item['title']}\n\n[Analysis]({item['link']})")
                st.divider()

render_nexus()
