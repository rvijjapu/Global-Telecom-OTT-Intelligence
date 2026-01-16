import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# ══════════════════════════════════════════════════════════════════════════════
# 1. COMPREHENSIVE INTELLIGENCE LISTS (2026 PPT SYNC)
# ══════════════════════════════════════════════════════════════════════════════
STRATEGIC_2026_HITS = [
    {
        "title": "NBA Scores Strategic Investment in Evergent; Named Preferred Global Vendor (Jan 14, 2026)", 
        "impact": "CRITICAL",
        "context": "Following a successful 185-country rollout, the NBA has taken an equity stake in Evergent to drive hyper-personalization for League Pass via AI-driven churn management."
    },
    {
        "title": "Amdocs Snaps up Matrixx Software for $200M in Massive BSS Consolidation Move (Jan 6, 2026)", 
        "impact": "HIGH",
        "context": "Amdocs acquires charging leader Matrixx to protect its Tier-1 accounts, leaving Evergent as the leading independent agile choice in the market."
    },
    {
        "title": "Netcracker Expands Partnership with T-Mobile for Cloud-Native Wholesale BSS (Jan 15, 2026)", 
        "impact": "HIGH",
        "context": "T-Mobile Wholesale shifts to Netcracker’s cloud platform to reduce service launch cycles from months to weeks, enabling digital-first business models."
    }
]

# Client/Competitor matching engine (includes ALL names from your prompt)
EVERGENT_CLIENTS = {
    "NBA": ["nba", "national basketball", "league pass"],
    "Astro": ["astro malaysia", "sooka", "njoi"],
    "Shahid": ["shahid vip", "mbc"], "Sky NZ": ["sky nz", "neon"], 
    "Sony": ["sonyliv", "sony india"], "FanDuel": ["fanduel", "bally sports"],
    "Cignal": ["cignal tv", "pldt"], "Telekom Malaysia": ["unifi tv", "tm"],
    "Aha": ["aha ott", "aha telugu"], "Etisalat": ["e&", "etisalat"],
    "DAZN": ["dazn"], "Fox": ["fox sports", "fox networks"],
    "BBC": ["bbc", "wimbledon"], "StarHub": ["starhub"]
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
    
    /* Header Visibility */
    .header-box { background: rgba(30, 64, 175, 0.98); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center; border-bottom: 4px solid #3b82f6; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .header-box h1 { margin: 0; font-weight: 800; color: #ffffff !important; letter-spacing: -1px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    .header-box p { margin: 5px 0 0; font-weight: 600; color: #e2e8f0 !important; }

    /* Hero Containers */
    .hero-box { background: rgba(15, 23, 42, 0.97); border: 2px solid #1e40af; border-radius: 12px; padding: 1.5rem; min-height: 240px; box-shadow: 0 4px 25px rgba(0,0,0,0.6); }
    .hero-box h4 { color: #fbbf24 !important; font-weight: 800; margin-top: 0; }
    .status-tag { display: inline-block; padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; font-weight: 800; margin-bottom: 12px; text-transform: uppercase; color: white; }
    
    /* News Section visibility */
    .section-title { color: #ffffff !important; font-weight: 800; text-shadow: 1px 1px 3px rgba(0,0,0,0.8); margin-bottom: 10px; background: rgba(0,0,0,0.4); padding: 5px 10px; border-radius: 5px; }
    .news-card { background: rgba(30, 41, 59, 0.98); border-radius: 8px; padding: 12px; margin-bottom: 10px; border-left: 4px solid #3b82f6; transition: 0.3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .news-card:hover { transform: translateX(5px); background: rgba(51, 65, 85, 1); border-left: 4px solid #fbbf24; }
    .priority-card { background: linear-gradient(90deg, rgba(30, 41, 59, 0.98) 0%, rgba(23, 37, 84, 0.98) 100%); border-left: 4px solid #fbbf24; }
    
    /* Font Visibility */
    .news-title { font-size: 0.92rem; font-weight: 700; color: #f8fafc !important; line-height: 1.4; }
    .impact-tag { color: #fbbf24; font-weight: 800; font-size: 0.8rem; }
    .client-chip { background: #fbbf24; color: #000; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 900; margin-right: 6px; }
    .read-more-link { color: #60a5fa !important; font-size: 0.75rem; font-weight: 700; text-decoration: none; display: inline-block; margin-top: 8px; }
    .read-more-link:hover { text-decoration: underline; color: #93c5fd !important; }
    
    hr { border: 0; height: 1px; background: rgba(255,255,255,0.2); margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 3. 2026 LIVE DATA ENGINE (JANUARY 1-16)
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
                is_priority = (client_match == "NBA") or ("amdocs" in txt and "matrixx" in txt) or ("netcracker" in txt and "t-mobile" in txt)
                
                items.append({
                    "title": title, "link": entry.get("link", ""), 
                    "category": cat, "pub": pub, "client": client_match, "priority": is_priority
                })
    except: pass
    return items

@st.cache_data(ttl=300)
def get_jan_2026_data():
    feeds = [
        ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
        ("SportsPro", "https://www.sportspro.com/feed", "sports"),
        ("StreamTV Insider", "https://www.streamtvinsider.com/feed", "ott"),
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
    <h1>🌐 GLOBAL INTELLIGENCE NEXUS</h1>
    <p>Live Competitive Strategy Dashboard | January 16, 2026</p>
</div>
""", unsafe_allow_html=True)

data = get_jan_2026_data()

# --- TOP HIGHLIGHTS ---
st.markdown("<h3 class='section-title'>🚀 STRATEGIC BREAKOUTS (JAN 14-16, 2026)</h3>", unsafe_allow_html=True)
h1, h2 = st.columns(2)
with h1:
    content = "".join([f"<div style='margin-bottom:12px;'><span class='impact-tag'>[{h['impact']}]</span> <b style='color:white;'>{h['title']}</b><br><span style='color:#cbd5e1; font-size:0.85rem; line-height:1.4;'>{h['context']}</span></div>" for h in STRATEGIC_2026_HITS])
    st.markdown(f'<div class="hero-box" style="border-color:#10b981;"><span class="status-tag" style="background:#10b981;">MARKET MOVERS</span><div style="font-size:0.95rem; color:white;">{content}</div></div>', unsafe_allow_html=True)
with h2:
    st.markdown(f"""
    <div class="hero-box" style="border-color:#f97316;">
        <span class="status-tag" style="background:#f97316;">2026 AGENTIC AI PULSE</span>
        <div style="font-size:0.95rem; line-height:1.7; color:white;">
            <b style="color:#fbbf24;">Autonomous Retention:</b> Industry shift from Generative AI to <b>Agentic AI</b> where autonomous agents independently manage churn and billing (CES 2026 Keynote).<br><br>
            <b style="color:#fbbf24;">NBA Vision:</b> David Lee (NBA Investments) confirms personalization and data-driven engagement as the #1 driver for the <b>Evergent</b> equity stake (Jan 14).<br><br>
            <b style="color:#fbbf24;">Sovereign Cloud:</b> AWS and Google Cloud (Jan 15) accelerate European Sovereign Cloud rollouts to meet Tier-1 telco data privacy demands.
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- DYNAMIC GRID ---
st.markdown("<hr>", unsafe_allow_html=True)
cols = st.columns(4)
sections = [("📡 TELCO OSS/BSS", "telco"), ("📺 OTT & STREAMING", "ott"), ("🏆 SPORTS MEDIA", "sports"), ("⚡ AI TECHWATCH", "technology")]

for i, (label, tag) in enumerate(sections):
    with cols[i]:
        st.markdown(f"<h3 class='section-title'>{label}</h3>", unsafe_allow_html=True)
        filtered = [n for n in data if n['category'] == tag]
        filtered.sort(key=lambda x: x['pub'], reverse=True)
        
        if not filtered:
            st.markdown("<div class='news-card' style='color:#94a3b8;'>Monitoring live feeds...</div>", unsafe_allow_html=True)
        
        for n in filtered[:12]:
            client_chip = f"<span class='client-chip'>{n['client']}</span>" if n['client'] else ""
            card_class = "news-card priority-card" if n['priority'] else "news-card"
            st.markdown(f"""
            <div class="{card_class}">
                <div class="news-title">{client_chip}{n['title']}</div>
                <div><a href="{n['link']}" class="read-more-link" target="_blank">READ MORE →</a></div>
            </div>
            """, unsafe_allow_html=True)
