import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# ══════════════════════════════════════════════════════════════════════════════
# 1. 2026 STRATEGIC INTELLIGENCE (PPT-READY)
# ══════════════════════════════════════════════════════════════════════════════
STRATEGIC_2026_HITS = [
    {
        "title": "NBA Scores Strategic Investment in Evergent; Named Preferred Global Vendor (Jan 14, 2026)", 
        "impact": "CRITICAL",
        "context": "Following work on NBA League Pass, the NBA has made a strategic investment in Evergent Technologies to drive hyper-personalization across 185 countries."
    },
    {
        "title": "Amdocs Snaps up Matrixx Software for $200M in Massive BSS Consolidation Move (Jan 6, 2026)", 
        "impact": "HIGH",
        "context": "Amdocs acquires charging leader Matrixx to bolster its 5G portfolio, forcing legacy consolidation while Evergent maintains agile independent leadership."
    },
    {
        "title": "Netcracker Expands Partnership with T-Mobile for Cloud-Native BSS (Jan 15, 2026)", 
        "impact": "HIGH",
        "context": "T-Mobile Wholesale shifts to Netcracker’s cloud platform to reduce service launch cycles, enabling digital-first business models for the 2026 season."
    }
]

# Intelligence Dictionary for Automated Priority Matching
EVERGENT_CLIENTS = {
    "NBA": ["nba", "national basketball", "league pass"],
    "Astro": ["astro malaysia", "sooka", "njoi"],
    "Shahid": ["shahid vip", "mbc"], "Sky NZ": ["sky nz", "neon"], 
    "Sony": ["sonyliv", "sony india"], "FanDuel": ["fanduel", "bally sports"],
    "Cignal": ["cignal tv", "pldt"], "Telekom Malaysia": ["unifi tv", "tm"],
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
    
    /* Global Visibility Enhancements */
    .header-box { background: rgba(30, 64, 175, 0.98); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center; border-bottom: 4px solid #3b82f6; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .header-box h1 { margin: 0; font-weight: 800; color: #ffffff !important; letter-spacing: -1px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }

    /* Hero Containers */
    .hero-box { background: rgba(15, 23, 42, 0.97); border: 2px solid #1e40af; border-radius: 12px; padding: 1.5rem; min-height: 240px; box-shadow: 0 4px 25px rgba(0,0,0,0.6); }
    .hero-box h4 { color: #fbbf24 !important; font-weight: 800; }
    
    /* News Section */
    .section-title { color: #ffffff !important; font-weight: 800; text-shadow: 1px 1px 3px rgba(0,0,0,0.8); margin-bottom: 10px; background: rgba(0,0,0,0.4); padding: 5px 10px; border-radius: 5px; }
    .news-card { background: rgba(30, 41, 59, 0.98); border-radius: 8px; padding: 12px; margin-bottom: 10px; border-left: 4px solid #3b82f6; transition: 0.3s ease; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .news-card:hover { transform: translateX(5px); background: rgba(51, 65, 85, 1); border-left: 4px solid #fbbf24; }
    .priority-card { background: linear-gradient(90deg, rgba(30, 41, 59, 0.98) 0%, rgba(23, 37, 84, 0.98) 100%); border-left: 4px solid #fbbf24; }
    
    /* Font Styling */
    .news-title { font-size: 0.92rem; font-weight: 700; color: #f8fafc !important; line-height: 1.4; }
    .impact-tag { color: #fbbf24; font-weight: 800; font-size: 0.8rem; }
    .client-chip { background: #fbbf24; color: #000; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 900; margin-right: 6px; }
    .read-more-link { color: #60a5fa !important; font-size: 0.75rem; font-weight: 700; text-decoration: none; display: inline-block; margin-top: 8px; }
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
            # HARD FILTER: Only news from Jan 2026
            if pub and pub.tm_year == 2026 and pub.tm_mon == 1:
                title = entry.get("title", "")
                txt = (title + " " + entry.get("summary", "")).lower()
                client_match = next((k for k, v in EVERGENT_CLIENTS.items() if any(n in txt for n in v)), None)
                is_priority = (client_match == "NBA") or ("agentic" in txt)
                
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
            <b style="color:#fbbf24;">NBA Vision:</b> Head of NBA Investments confirms data-driven engagement as the #1 driver for the <b>Evergent</b> equity stake (Jan 14, 2026).<br><br>
            <b style="color:#fbbf24;">Agentic AI Core:</b> Shift from simple copilots to autonomous <b>Agentic AI</b> systems that resolve billing and churn in real-time without human input (Jan 15, 2026).<br><br>
            <b style="color:#fbbf24;">Humanoid Manufacturing:</b> Boston Dynamics begins factory implementation of AI robots (Atlas) for automotive supply chain sorting (Jan 2026).
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- DYNAMIC GRID ---
st.markdown("<hr style='opacity:0.2'>", unsafe_allow_html=True)
cols = st.columns(4)
sections = [("📡 TELCO OSS/BSS", "telco"), ("📺 OTT & STREAMING", "ott"), ("🏆 SPORTS MEDIA", "sports"), ("⚡ AI TECHWATCH", "technology")]

for i, (label, tag) in enumerate(sections):
    with cols[i]:
        st.markdown(f"<h3 class='section-title'>{label}</h3>", unsafe_allow_html=True)
        filtered = [n for n in data if n['category'] == tag]
        filtered.sort(key=lambda x: x['pub'], reverse=True)
        
        for n in filtered[:12]:
            client_chip = f"<span class='client-chip'>{n['client']}</span>" if n['client'] else ""
            card_class = "news-card priority-card" if n['priority'] else "news-card"
            st.markdown(f"""
            <div class="{card_class}">
                <div class="news-title">{client_chip}{n['title']}</div>
                <div><a href="{n['link']}" class="read-more-link" target="_blank">READ MORE →</a></div>
            </div>
            """, unsafe_allow_html=True)
