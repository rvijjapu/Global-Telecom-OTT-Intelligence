import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime, timedelta
import urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==========================================
# 1. CORE INTELLIGENCE LISTS (WATCHLISTS)
# ==========================================
# No news content is stored here—only the entities to monitor.
WATCHLIST = {
    "CLIENTS": ["AT&T", "Verizon", "T-Mobile", "Sony", "NBA", "WNBA", "BBC", "Sky", "Jio", "Shahid", "Netflix", "WBD", "Disney"],
    "COMPETITORS": ["Netcracker", "Amdocs", "CSG", "Oracle", "Ericsson", "Nokia", "Huawei", "Cerillion", "Matrixx"],
    "TRENDS": ["merger", "acquisition", "deal", "billion", "agentic", "monetization", "rights", "5G-Advanced", "micro-drama"]
}

# 2. DYNAMIC SEARCH QUERIES (URL GENERATOR)
# Generates live search strings based on your 2026 parameters.
def get_rss_url(topic):
    base = "https://news.google.com/rss/search?q="
    # Query logic: (Topic) + (2026 Filter) - (2025 Noise)
    query = f"{topic} after:2026-01-01 exclude:2025"
    return base + urllib.parse.quote(query) + "&hl=en-US&gl=US&ceid=US:en"

# 3. THE AI SCORING ALGORITHM
def process_entry(entry, category):
    title = entry.title.lower()
    score = 0
    # Priority 1: Evergent Clients (+15)
    if any(c.lower() in title for c in WATCHLIST["CLIENTS"]): score += 15
    # Priority 2: Competitors (+10)
    if any(comp.lower() in title for comp in WATCHLIST["COMPETITORS"]): score += 10
    # Priority 3: Strategic Keywords (+5)
    if any(t.lower() in title for t in WATCHLIST["TRENDS"]): score += 5
    
    return {
        "title": entry.title,
        "link": entry.link,
        "source": entry.source.title if 'source' in entry else "Global Intel",
        "score": score,
        "category": category,
        "published": entry.published
    }

# 4. MULTI-THREADED DATA INGESTION
@st.cache_data(ttl=300)
def fetch_real_time_data():
    categories = {
        "telco": "telecom OSS BSS 5G-A monetization",
        "ott": "OTT streaming platform merger acquisition",
        "sports": "sports media rights broadcast deal",
        "tech": "enterprise agentic AI platform autonomous"
    }
    
    all_results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(lambda p: (p[0], feedparser.parse(get_rss_url(p[1]))), (cat, q)) 
                   for cat, q in categories.items()]
        for future in as_completed(futures):
            cat, feed = future.result()
            for entry in feed.entries[:15]:
                all_results.append(process_entry(entry, cat))
    
    return pd.DataFrame(all_results)

# 5. UI RENDERING (STREAMLIT)
st.set_page_config(page_title="Stellar Nexus 2026", layout="wide")

# CEO Dark-Blue Branding
st.markdown("""
<style>
    .stApp { background-color: #0a192f; color: white; }
    .card { background: rgba(255,255,255,0.05); padding: 1.5rem; border-radius: 12px; border-left: 5px solid #10b981; margin-bottom: 1rem; }
    .priority-badge { background: #10b981; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("📡 Global Telecom & OTT Stellar Nexus")
st.subheader("CEO Strategic Intelligence Dashboard | Real-Time 2026 Nodes")

df = fetch_real_time_data()

# 6. DASHBOARD LAYOUT
# Strategic Hits (Top Scored)
st.markdown("### 🚀 STRATEGIC HITS")
hits_df = df.sort_values(by="score", ascending=False).head(4)
hit_cols = st.columns(4)
for i, (_, row) in enumerate(hits_df.iterrows()):
    with hit_cols[i]:
        st.markdown(f"""<div class="card"><b>{row['source']}</b><br><a href="{row['link']}" style="color:white; text-decoration:none;">{row['title']}</a></div>""", unsafe_allow_html=True)

# Industry Vertical Columns
st.write("---")
cols = st.columns(4)
sections = [("📡 TELCO", "telco"), ("📺 OTT", "ott"), ("🏆 SPORTS", "sports"), ("⚡ AI TECH", "tech")]

for i, (label, key) in enumerate(sections):
    with cols[i]:
        st.markdown(f"#### {label}")
        items = df[df['category'] == key].sort_values(by="score", ascending=False).head(6)
        for _, item in items.iterrows():
            badge = "<span class='priority-badge'>PRIORITY</span>" if item['score'] > 12 else ""
            st.markdown(f"{badge} **{item['source']}**: {item['title']}  \n[Source]({item['link']})")
            st.divider()

st.caption(f"Last Intelligence Sync: {datetime.now().strftime('%H:%M:%S')} | Engine: Gemini 3 Flash")
