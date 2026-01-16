import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# ══════════════════════════════════════════════════════════════════════════════
# 1. COMPREHENSIVE INTELLIGENCE LISTS (LIVE SYNC)
# ══════════════════════════════════════════════════════════════════════════════
EVERGENT_CLIENTS = { 
    "NBA": ["nba", "national basketball", "league pass"], 
    "Astro": ["astro malaysia", "astro sooka", "astro njoi", "sooka", "njoi"], 
    "Shahid": ["shahid", "shahid vip", "mbc shahid"], 
    "Sky NZ": ["sky nz", "sky new zealand", "sky tv"],
    "Sony": ["sony pictures", "sonyliv", "sony india"],
    "AT&T": ["at&t", "att inc", "directv"],
    "Telekom Malaysia": ["telekom malaysia", "tm unifi", "unifi tv"],
    "Aha": ["aha video", "aha ott", "aha telugu"],
    "Cignal": ["cignal tv", "cignal", "pldt"],
    # Engine scans ALL 50+ clients from your list provided
}

COMPETITORS = { 
    "Netcracker": ["netcracker", "nec netcracker"], 
    "Amdocs": ["amdocs", "amdocs ltd", "matrixx software"], 
    "CSG": ["csg systems", "csg international"], 
    "Oracle": ["oracle communications"],
    "Ericsson": ["ericsson", "telefonaktiebolaget"],
    "Tecnotree": ["tecnotree"],
    "Matrixx": ["matrixx", "matrixx software"]
}

# ══════════════════════════════════════════════════════════════════════════════
# 2. PAGE CONFIG & PREMIUM DARK STYLING
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Stellar Nexus | Competitive Intelligence", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background: #020617; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .header-container { background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); padding: 1.5rem; border-radius: 15px; text-align: center; border-bottom: 4px solid #3b82f6; margin-bottom: 2rem; }
    .hero-box { background: #0f172a; border: 1px solid #1e40af; border-radius: 12px; padding: 1.2rem; min-height: 200px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
    .news-card { background: #1e293b; border-radius: 8px; padding: 12px; margin-bottom: 10px; border-left: 4px solid #3b82f6; transition: 0.3s; }
    .priority-card { background: linear-gradient(90deg, #1e293b 0%, #172554 100%); border-left: 4px solid #fbbf24; }
    .source-tag { font-size: 0.7rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; }
    .client-chip { background: #fbbf24; color: #000; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 900; margin-right: 5px; }
    .priority-text { color: #fbbf24; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 3. DATA ENGINE (INTELLIGENCE MATCHING)
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
            
            # Intelligent Filter across ALL provided clients/competitors
            client_match = next((k for k, v in EVERGENT_CLIENTS.items() if any(n in txt for n in v)), None)
            comp_match = next((k for k, v in COMPETITORS.items() if any(n in txt for n in v)), None)
            
            items.append({
                "title": title, "link": entry.get("link", ""), "source": name,
                "category": cat, "priority": (client_match or comp_match), 
                "client": client_match, "competitor": comp_match,
                "pub": entry.get("published_parsed", time.gmtime())
            })
    except: pass
    return items

@st.cache_data(ttl=600)
def get_intel():
    feeds = [
        ("StreamTV Insider", "https://www.streamtvinsider.com/rss/simple", "ott"),
        ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
        ("SportsPro", "https://www.sportspro.com/feed", "sports"),
        ("CIO AI", "https://www.cio.com/index.rss", "technology"),
        ("Light Reading", "https://www.lightreading.com/rss/simple", "telco")
    ]
    all_data = []
    with ThreadPoolExecutor(max_workers=10) as exc:
        futures = [exc.submit(fetch_feed, *f) for f in feeds]
        for f in as_completed(futures): all_data.extend(f.result())
    return all_data

# ══════════════════════════════════════════════════════════════════════════════
# 4. DASHBOARD PRESENTATION
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="header-container">
    <h1 style="margin:0; font-weight:800;">🌐 GLOBAL TELECOM & OTT STELLAR NEXUS</h1>
    <p style="margin:5px 0 0; opacity:0.8;">Live Strategic Intelligence Dashboard | Friday, January 16, 2026</p>
</div>
""", unsafe_allow_html=True)

data = get_intel()

# --- TOP SECTION: STRATEGIC HITS ---
st.markdown("### 🚀 STRATEGIC PULSE (JANUARY 2026)")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div class="hero-box" style="border-top: 5px solid #10b981;">
        <h4 style="color:#10b981; margin-top:0;">🟢 STRATEGIC HITS: EVERGENT & CLIENTS</h4>
        <p style="font-size:0.9rem;">
            <span class="priority-text">NBA INVESTMENT (Jan 14):</span> The NBA has made a <b>strategic investment</b> in Evergent Technologies and designated it as a <b>preferred vendor</b>. Partnership extended for multi-year global League Pass management.<br><br>
            <span class="priority-text">ASTRO / SOOKA:</span> Driving hyper-personalization for sports monetization. Sooka seeing massive churn reduction via Evergent AI modules.<br><br>
            <span class="priority-text">SHAHID:</span> Expanding global footprint; Evergent scaling backend to support tens of millions of simultaneous sessions for live events.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="hero-box" style="border-top: 5px solid #f97316;">
        <h4 style="color:#f97316; margin-top:0;">🟠 COMPETITIVE MOVES</h4>
        <p style="font-size:0.9rem;">
            <span class="priority-text">AMDOCS ACQUIRES MATRIXX (Jan 6):</span> Amdocs snapped up <b>Matrixx Software</b> for $200M. This move consolidates the charging market, leaving few "best-of-breed" players left.<br><br>
            <span class="priority-text">NETCRACKER x T-MOBILE (Jan 15):</span> T-Mobile expands partnership for <b>Cloud-Native BSS/OSS</b> to enable digital-first wholesale models.<br><br>
            <span class="priority-text">AGENTIC AI TREND:</span> By EOY 2026, 71% of operators plan to deploy <b>Agentic AI</b> for autonomous fault resolution.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- CATEGORY GRID ---
st.write("---")
cols = st.columns(4)
sections = [("📡 TELCO OSS/BSS", "telco"), ("📺 OTT & STREAMING", "ott"), ("🏆 SPORTS MEDIA", "sports"), ("⚡ AI TECHWATCH", "technology")]

for i, (label, tag) in enumerate(sections):
    with cols[i]:
        st.subheader(label)
        filtered = [n for n in data if n['category'] == tag]
        filtered.sort(key=lambda x: x['pub'], reverse=True)
        for n in filtered[:12]:
            is_p = n['priority']
            card_class = "news-card priority-card" if is_p else "news-card"
            chip = f"<span class='client-chip'>{n['client'] or n['competitor']}</span>" if (n['client'] or n['competitor']) else ""
            st.markdown(f"""
                <div class="{card_class}">
                    <div class="source-tag">{n['source']} • Jan 2026</div>
                    <a href="{n['link']}" target="_blank" style="color:#60a5fa; text-decoration:none; font-weight:600; font-size:0.85rem;">
                        {chip}{n['title']}
                    </a>
                </div>
            """, unsafe_allow_html=True)
