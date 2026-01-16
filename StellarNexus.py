import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# ══════════════════════════════════════════════════════════════════════════════
# 1. 2026 INTELLIGENCE CONSTANTS (PURGED OF 2025)
# ══════════════════════════════════════════════════════════════════════════════
STRATEGIC_2026_HITS = [
    {"source": "Telecoms.com", "title": "T-Mobile Taps Netcracker for Cloud-Native BSS/OSS Transition (Jan 15, 2026)", "impact": "High"},
    {"source": "PR Newswire", "title": "Mycom & Groundhog Launch First Agent-to-Agent OSS Integration (Jan 15, 2026)", "impact": "Critical"},
    {"source": "SportsPro", "title": "FanDuel Sports Network Inks New Local Rights Deals with 9 MLB Teams (Jan 15, 2026)", "impact": "High"}
]

PULSE_2026 = [
    "NBA Viewership surges 18% under new 2026 broadcast framework.",
    "Agentic AI replaces GenAI as the primary Telecom OPEX reduction driver.",
    "Direct-to-Device (D2D) satellite services hit 1% revenue uplift for early MNO adopters."
]

# ══════════════════════════════════════════════════════════════════════════════
# 2. APP CONFIG & PREMIUM STYLING
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Stellar Nexus | 2026 Intelligence", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    .stApp { background: #020617; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .header-box { background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center; border-bottom: 3px solid #3b82f6; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
    .hero-box { background: #0f172a; border: 1px solid #1e40af; border-radius: 12px; padding: 1.2rem; min-height: 200px; }
    .status-tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.65rem; font-weight: bold; margin-bottom: 5px; text-transform: uppercase; }
    .news-card { background: #1e293b; border-radius: 8px; padding: 12px; margin-bottom: 8px; border-left: 3px solid #3b82f6; }
    .priority-card { background: linear-gradient(90deg, #1e293b 0%, #172554 100%); border-left: 4px solid #fbbf24; }
    .news-title { font-size: 0.85rem; font-weight: 600; color: #e2e8f0; text-decoration: none; }
    .news-meta { font-size: 0.7rem; color: #94a3b8; margin-top: 4px; display: flex; justify-content: space-between; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 3. 2026 REAL-TIME DATA ENGINE (NO PAST NEWS)
# ══════════════════════════════════════════════════════════════════════════════
def fetch_2026_data(name, url, cat):
    items = []
    try:
        resp = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
        feed = feedparser.parse(resp.content)
        # ONLY items from Jan 2026
        for entry in feed.entries:
            pub_date = entry.get("published_parsed", None)
            if pub_date and pub_date.tm_year == 2026 and pub_date.tm_mon == 1:
                items.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "source": name,
                    "category": cat,
                    "pub": pub_date
                })
    except: pass
    return items

@st.cache_data(ttl=600)
def get_jan_2026_intel():
    feeds = [
        ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
        ("SportsPro", "https://www.sportspro.com/feed", "sports"),
        ("Variety", "https://variety.com/feed/", "ott"),
        ("CIO / AI Tech", "https://www.cio.com/index.rss", "technology")
    ]
    all_data = []
    with ThreadPoolExecutor(max_workers=8) as exc:
        futures = [exc.submit(fetch_2026_data, *f) for f in feeds]
        for f in as_completed(futures): all_data.extend(f.result())
    return all_data

# ══════════════════════════════════════════════════════════════════════════════
# 4. DASHBOARD RENDER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="header-box">
    <h1 style="margin:0; font-weight:800; letter-spacing:-1px;">🌐 GLOBAL INTELLIGENCE NEXUS</h1>
    <p style="margin:5px 0 0; opacity:0.8;">Live Strategic Intelligence Dashboard | Friday, January 16, 2026</p>
</div>
""", unsafe_allow_html=True)

data = get_jan_2026_intel()

# --- HIGHLIGHTS SECTION ---
st.markdown("### 🚀 2026 STRATEGIC HIGHLIGHTS")
h1, h2 = st.columns(2)
with h1:
    content = "".join([f"<b>{h['source']}:</b> {h['title']}<br><br>" for h in STRATEGIC_2026_HITS])
    st.markdown(f'<div class="hero-box" style="border-color:#10b981;"><span class="status-tag" style="background:#10b981; color:#064e3b;">MARKET MOVERS</span><div style="font-size:0.9rem;">{content}</div></div>', unsafe_allow_html=True)
with h2:
    content = "".join([f"• {p}<br><br>" for p in PULSE_2026])
    st.markdown(f'<div class="hero-box" style="border-color:#f97316;"><span class="status-tag" style="background:#f97316; color:#7c2d12;">2026 TREND PULSE</span><div style="font-size:0.9rem;">{content}</div></div>', unsafe_allow_html=True)

# --- CATEGORY GRID ---
st.write("---")
cols = st.columns(4)
sections = [("📡 TELCO OSS/BSS", "telco"), ("📺 OTT & STREAMING", "ott"), ("🏆 SPORTS MEDIA", "sports"), ("⚡ AI TECHWATCH", "technology")]

for i, (label, tag) in enumerate(sections):
    with cols[i]:
        st.markdown(f"### {label}")
        filtered = [n for n in data if n['category'] == tag]
        filtered.sort(key=lambda x: x['pub'], reverse=True)
        for n in filtered[:10]:
            st.markdown(f"""
            <div class="news-card">
                <a href="{n['link']}" target="_blank" class="news-title">{n['title']}</a>
                <div class="news-meta"><span>{n['source']}</span><span>Jan 2026</span></div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('<script>setTimeout(function() {window.location.reload();}, 300000);</script>', unsafe_allow_html=True)
