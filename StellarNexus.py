import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# ══════════════════════════════════════════════════════════════════════════════
# 1. COMPREHENSIVE INTELLIGENCE LISTS (PPT-READY)
# ══════════════════════════════════════════════════════════════════════════════
STRATEGIC_2026_HITS = [
    {
        "title": "NBA Scores Strategic Investment in Evergent; Named Preferred Global Vendor (Jan 14, 2026)", 
        "impact": "CRITICAL",
        "context": "Following a successful 185-country rollout, the NBA has taken an equity stake in Evergent to drive hyper-personalization for League Pass."
    },
    {
        "title": "Amdocs Snaps up Matrixx Software for $200M in Massive BSS Consolidation Move (Jan 6, 2026)", 
        "impact": "HIGH",
        "context": "Amdocs acquires charging leader Matrixx to bolster its 5G portfolio, leaving few independent agile players in the market."
    },
    {
        "title": "Netcracker Expands Long-Term Partnership with T-Mobile for Cloud-Native BSS (Jan 15, 2026)", 
        "impact": "HIGH",
        "context": "T-Mobile Wholesale shifts to Netcracker’s cloud platform to reduce service launch cycles from months to weeks."
    }
]

# Client/Competitor matching lists from your provided data
EVERGENT_CLIENTS = {
    "NBA": ["nba", "national basketball", "league pass"],
    "Astro": ["astro malaysia", "sooka", "njoi"],
    "Shahid": ["shahid vip", "mbc"], "Sky NZ": ["sky nz", "neon"], 
    "Sony": ["sonyliv", "sony india"], "FanDuel": ["fanduel", "bally sports"],
    "Cignal": ["cignal tv", "pldt"], "Telekom Malaysia": ["unifi tv", "tm"],
    "Aha": ["aha ott", "aha telugu"], "Etisalat": ["e&", "etisalat"],
    "DAZN": ["dazn"], "Fox": ["fox sports", "fox networks"]
}

# ══════════════════════════════════════════════════════════════════════════════
# 2. PAGE CONFIG & PREMIUM STYLING
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Stellar Nexus | 2026 Executive Intelligence", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { 
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; 
        background-size: cover;
        font-family: 'Inter', sans-serif; 
    }
    .header-box { background: rgba(30, 64, 175, 0.95); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center; border-bottom: 4px solid #3b82f6; }
    .hero-box { background: rgba(15, 23, 42, 0.95); border: 1px solid #1e40af; border-radius: 12px; padding: 1.2rem; min-height: 220px; box-shadow: 0 4px 25px rgba(0,0,0,0.5); }
    .status-tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: bold; margin-bottom: 8px; text-transform: uppercase; color: white; }
    .news-card { background: rgba(30, 41, 59, 0.95); border-radius: 8px; padding: 12px; margin-bottom: 8px; border-left: 3px solid #3b82f6; transition: 0.3s ease; }
    .news-card:hover { transform: translateX(5px); background: rgba(51, 65, 85, 0.98); }
    .priority-card { background: linear-gradient(90deg, rgba(30, 41, 59, 0.95) 0%, rgba(23, 37, 84, 0.95) 100%); border-left: 4px solid #fbbf24; }
    .impact-tag { color: #fbbf24; font-weight: 800; font-size: 0.75rem; }
    .client-chip { background: #fbbf24; color: #000; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 900; margin-right: 5px; }
    .read-more { color: #60a5fa; font-size: 0.7rem; font-weight: 600; text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 3. 2026 LIVE DATA ENGINE (STRICT JAN 2026 FILTER)
# ══════════════════════════════════════════════════════════════════════════════
def fetch_2026_intel(name, url, cat):
    items = []
    try:
        resp = requests.get(url, timeout=7, headers={"User-Agent": "Mozilla/5.0"})
        feed = feedparser.parse(resp.content)
        for entry in feed.entries:
            pub = entry.get("published_parsed", None)
            if pub and pub.tm_year == 2026 and pub.tm_mon == 1:
                title = entry.get("title", "")
                txt = (title + " " + entry.get("summary", "")).lower()
                
                client_match = next((k for k, v in EVERGENT_CLIENTS.items() if any(n in txt for n in v)), None)
                is_priority = (client_match == "NBA") or ("amdocs" in txt and "matrixx" in txt)
                
                items.append({
                    "title": title, "link": entry.get("link", ""), 
                    "category": cat, "pub": pub, "client": client_match, "priority": is_priority
                })
    except: pass
    return items

@st.cache_data(ttl=600)
def get_jan_2026_data():
    feeds = [
        ("StreamTV Insider", "https://www.streamtvinsider.com/feed", "ott"),
        ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
        ("SportsPro", "https://www.sportspro.com/feed", "sports"),
        ("Variety", "https://variety.com/feed/", "ott"),
        ("CIO AI", "https://www.cio.com/index.rss", "technology")
    ]
    all_data = []
    with ThreadPoolExecutor(max_workers=10) as exc:
        futures = [exc.submit(fetch_2026_intel, *f) for f in feeds]
        for f in as_completed(futures): all_data.extend(f.result())
    return all_data

# ══════════════════════════════════════════════════════════════════════════════
# 4. DASHBOARD RENDER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="header-box">
    <h1 style="margin:0; font-weight:800; color:white; letter-spacing:-1px;">🌐 GLOBAL INTELLIGENCE NEXUS</h1>
    <p style="margin:5px 0 0; opacity:0.9; color:white;">Live Strategic Intelligence | Friday, January 16, 2026</p>
</div>
""", unsafe_allow_html=True)

data = get_jan_2026_data()

# --- HIGHLIGHTS SECTION ---
st.markdown("### 🚀 STRATEGIC BREAKOUTS (JAN 14-16, 2026)")
h1, h2 = st.columns(2)
with h1:
    content = "".join([f"<div style='margin-bottom:12px;'><span class='impact-tag'>[{h['impact']}]</span> <b>{h['title']}</b><br><span style='color:#cbd5e1; font-size:0.8rem;'>{h['context']}</span></div>" for h in STRATEGIC_2026_HITS])
    st.markdown(f'<div class="hero-box" style="border-color:#10b981;"><span class="status-tag" style="background:#10b981; color:#064e3b;">MARKET MOVERS</span><div style="font-size:0.9rem; color:white;">{content}</div></div>', unsafe_allow_html=True)
with h2:
    st.markdown(f"""
    <div class="hero-box" style="border-color:#f97316;">
        <span class="status-tag" style="background:#f97316; color:#7c2d12;">2026 AGENTIC AI PULSE</span>
        <div style="font-size:0.9rem; line-height:1.6; color:white;">
            <b>Jan 14, 2026:</b> The NBA designates Evergent a <b>Preferred Vendor</b>; partnership extension focuses on AI-driven churn reduction and tailored subscription options.<br><br>
            <b>Jan 15, 2026:</b> Evergent CEO Vijay Sajja highlights the move to <b>Agentic AI</b>—autonomous BSS agents that proactively manage subscriber retention journeys.<br><br>
            <b>Jan 16, 2026:</b> DAZN secures FIFA Women’s Champions Cup rights, signaling a massive push into free-to-view intercontinental club football monetization.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- CATEGORY GRID ---
st.write("---")
cols = st.columns(4)
sections = [("📡 TELCO OSS/BSS", "telco"), ("📺 OTT & STREAMING", "ott"), ("🏆 SPORTS MEDIA", "sports"), ("⚡ AI TECHWATCH", "technology")]

for i, (label, tag) in enumerate(sections):
    with cols[i]:
        st.markdown(f"<h3 style='color:white;'>{label}</h3>", unsafe_allow_html=True)
        filtered = [n for n in data if n['category'] == tag]
        filtered.sort(key=lambda x: x['pub'], reverse=True)
        for n in filtered[:12]:
            client_chip = f"<span class='client-chip'>{n['client']}</span>" if n['client'] else ""
            card_class = "news-card priority-card" if n['priority'] else "news-card"
            st.markdown(f"""
            <div class="{card_class}">
                <div class="news-title">{client_chip}{n['title']}</div>
                <div style="margin-top:8px;"><a href="{n['link']}" class="read-more" target="_blank">READ MORE →</a></div>
            </div>
            """, unsafe_allow_html=True)
