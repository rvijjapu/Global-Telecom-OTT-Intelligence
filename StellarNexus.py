import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# ══════════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE INTELLIGENCE LISTS (Integrated)
# ══════════════════════════════════════════════════════════════════════════════
EVERGENT_CLIENTS = {
    "NBA": ["nba", "national basketball"],
    "Astro": ["astro malaysia", "astro sooka", "astro njoi", "sooka"],
    "Sky NZ": ["sky nz", "sky new zealand", "sky network television"],
    "SonyLIV": ["sonyliv", "sony liv", "sony india"],
    "Shahid": ["shahid", "shahid vip", "mbc shahid"],
    "DirecTV": ["directv", "direct tv"],
    "FanDuel": ["fanduel", "fanduel group", "bally sports"],
    "Telekom Malaysia": ["telekom malaysia", "tm unifi", "unifi tv"],
    "Evergent": ["evergent", "evergent technologies", "vijay sajja"]
}

COMPETITORS = {
    "Amdocs": ["amdocs", "amdocs ltd"],
    "Netcracker": ["netcracker", "nec netcracker"],
    "CSG": ["csg systems", "csg international"],
    "Matrixx": ["matrixx software", "matrixx"],
    "Tecnotree": ["tecnotree"],
    "Cerillion": ["cerillion"]
}

# Key 2026 Strategic Terms
STRATEGIC_TERMS = ["agentic ai", "oss/bss", "churn management", "monetization", "acquisition", "strategic investment"]

# Combined priority list for high-intensity tracking
PRIORITY_KWS = []
for d in [EVERGENT_CLIENTS, COMPETITORS]:
    for names in d.values():
        PRIORITY_KWS.extend(names)
PRIORITY_KWS.extend(STRATEGIC_TERMS)

# ══════════════════════════════════════════════════════════════════════════════
# APP CONFIG & STYLING
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Stellar Nexus | Competitive Intelligence", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #050a14; color: #e2e8f0; font-family: 'Inter', sans-serif; }
    .header-box { background: linear-gradient(90deg, #1e3a8a, #1e40af); padding: 20px; border-radius: 15px; margin-bottom: 25px; text-align: center; border-bottom: 4px solid #3b82f6; }
    .hero-container { background: rgba(15, 23, 42, 0.8); border: 1px solid #1e40af; border-radius: 16px; padding: 20px; margin-bottom: 20px; }
    .news-card { background: #0f172a; border-left: 4px solid #3b82f6; padding: 12px; margin-bottom: 10px; border-radius: 4px; transition: 0.3s; }
    .news-card:hover { background: #1e293b; transform: translateX(5px); }
    .priority-card { background: linear-gradient(135deg, #1e293b 0%, #1e3a8a 100%); border-left: 4px solid #fbbf24; border-radius: 8px; padding: 12px; margin-bottom: 10px; }
    .source-tag { font-size: 0.7rem; color: #94a3b8; font-weight: bold; text-transform: uppercase; }
    .time-tag { font-size: 0.7rem; color: #34d399; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA ENGINE
# ══════════════════════════════════════════════════════════════════════════════
def fetch_feed(name, url, cat):
    items = []
    try:
        resp = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        feed = feedparser.parse(resp.content)
        for entry in feed.entries[:10]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            txt = (title + " " + summary).lower()
            
            # Smart Priority Match
            is_priority = any(kw in txt for kw in PRIORITY_KWS)
            
            # Detect client specific mention
            client_match = next((k for k, v in EVERGENT_CLIENTS.items() if any(n in txt for n in v)), None)
            
            items.append({
                "title": title,
                "link": entry.get("link", ""),
                "source": name,
                "category": cat,
                "priority": is_priority,
                "client": client_match,
                "pub": entry.get("published_parsed", time.gmtime())
            })
    except: pass
    return items

@st.cache_data(ttl=300)
def get_all_data():
    feeds = [
        ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
        ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
        ("Variety", "https://variety.com/feed/", "ott"),
        ("Sports Business", "https://www.sportsbusinessjournal.com/rss", "sports"),
        ("TechCrunch", "https://techcrunch.com/feed/", "tech")
    ]
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_feed, *f) for f in feeds]
        for fut in as_completed(futures):
            results.extend(fut.result())
    return results

# ══════════════════════════════════════════════════════════════════════════════
# UI LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="header-box"><h1>🌐 Global Intelligence Nexus</h1><p>Real-time Client & Competitor Tracking (Jan 2026)</p></div>', unsafe_allow_html=True)

all_news = get_all_data()

# DYNAMIC HIGHLIGHTS (Automated from list matches)
priority_stream = [n for n in all_news if n['priority']]
priority_stream.sort(key=lambda x: x['pub'], reverse=True)

st.markdown('<div class="hero-container"><h3>🚀 STRATEGIC PULSE</h3><div style="display:flex; gap:20px;">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.info("**Top Client Activity**")
    client_news = [n for n in priority_stream if n['client']][:3]
    for n in client_news:
        st.markdown(f"📍 **{n['client']}**: [{n['title']}]({n['link']})")
with c2:
    st.warning("**Competitive Moves**")
    comp_news = [n for n in priority_stream if any(cw in n['title'].lower() for cw in ["amdocs", "netcracker", "csg"])][:3]
    for n in comp_news:
        st.markdown(f"⚔️ **{n['source']}**: [{n['title']}]({n['link']})")
st.markdown('</div></div>', unsafe_allow_html=True)

# MAIN NEWS GRID
cols = st.columns(3)
sections = [("📡 TELCO/BSS", "telco"), ("📺 OTT & MEDIA", "ott"), ("🏆 SPORTS RIGHTS", "sports")]

for i, (label, tag) in enumerate(sections):
    with cols[i]:
        st.subheader(label)
        filtered = [n for n in all_news if n['category'] == tag][:10]
        for n in filtered:
            style = "priority-card" if n['priority'] else "news-card"
            client_tag = f"<span style='color:#fbbf24'>[{n['client']}]</span> " if n['client'] else ""
            st.markdown(f"""
                <div class="{style}">
                    <div class="source-tag">{n['source']}</div>
                    <a href="{n['link']}" target="_blank" style="text-decoration:none; color:#60a5fa; font-weight:600;">
                        {client_tag}{n['title']}
                    </a>
                </div>
            """, unsafe_allow_html=True)

st.markdown('<script>setTimeout(function() {window.location.reload();}, 300000);</script>', unsafe_allow_html=True)
