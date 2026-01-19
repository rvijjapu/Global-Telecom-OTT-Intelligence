import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# PAGE CONFIG
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# COMPREHENSIVE INTELLIGENCE LISTS (used for priority detection)
EVERGENT_CLIENTS = {
    "Astro": ["astro malaysia", "astro sooka", "astro njoi", "astro", "sooka", "njoi"],
    "NBA": ["nba", "national basketball"],
    "FOX": ["fox sports", "fox corporation", "fox networks", "fox"],
    "AT&T": ["at&t", "att inc", "att wireless", "directv"],
    "Shahid": ["shahid", "shahid vip", "mbc shahid"],
    "MBC": ["mbc group", "mbc", "middle east broadcasting"],
    "Sony": ["sony pictures", "sony entertainment", "sonyliv", "sony india"],
    "BBC": ["bbc", "british broadcasting", "bbc iplayer"],
    "Sky": ["sky nz", "sky new zealand", "sky tv", "sky uk", "sky italia"],
    "DAZN": ["dazn"],
    "FanDuel": ["fanduel", "fanduel group", "flutter"],
    "Bally Sports": ["bally sports", "bally regional", "diamond sports"],
    "Premier League": ["premier league"],
    "StarHub": ["starhub"],
}

COMPETITORS = {
    "Netcracker": ["netcracker", "netcracker technology", "nec netcracker"],
    "Amdocs": ["amdocs", "amdocs ltd", "amdocs inc"],
    "CSG": ["csg systems", "csg international", "csg"],
    "MATRIXX": ["matrixx", "matrixx software"],
    "Oracle": ["oracle communications", "oracle corporation"],
    "Ericsson": ["ericsson"],
    "Nokia": ["nokia", "nokia networks"],
}

PRIORITY_KWS = ["evergent", "nba", "amdocs", "matrixx", "netcracker", "nec", "csg"]
ALL_COMPANY_KWS = []
for d in [EVERGENT_CLIENTS, COMPETITORS]:
    for names in d.values():
        ALL_COMPANY_KWS.extend(names)
ALL_COMPANY_KWS = list(set([kw.lower() for kw in ALL_COMPANY_KWS]))

# KEEP-ALIVE
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

# ULTRA PREMIUM GLASSMORPHISM STYLING (from your first version - most polished)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@600;700;800;900&display=swap');
    * { margin: 0; padding: 0; box-sizing: border-box; }
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', sans-serif;
        padding-top: 0.5rem;
        position: relative;
    }
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.5) 100%);
        z-index: 0;
        pointer-events: none;
    }
    [data-testid="stAppViewContainer"] > .main { position: relative; z-index: 1; }
    /* ... (keep your full CSS from the first pasted block here - header-container, hero-container, hero-grid, hero-box, col-header, news-card, etc.) */
    /* For brevity in this response, assume you paste your complete <style> block from the first version here */
    /* Key classes: .header-container, .main-title, .hero-container, .hero-grid, .hero-box, .col-header-*, .news-card, .news-card-priority, etc. */
</style>
""", unsafe_allow_html=True)

# RSS FEEDS (unchanged)
RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/", "ott"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml", "sports"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("Wired", "https://www.wired.com/feed/rss", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & STREAMING", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "AI TECHWATCH", "style": "col-header-orange"},
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean(raw):
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw or ""))).strip()

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200: return items
        
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=14)
        
        for entry in feed.entries[:30]:
            title = clean(entry.get("title", ""))
            if len(title) < 25: continue
            
            summary = clean(entry.get("summary", entry.get("description", "")))
            link = entry.get("link", "")
            
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try: pub = datetime(*val[:6])
                    except: pass
                    break
            
            if not pub or pub < CUTOFF: continue
            
            full_text = (title + " " + summary).lower()
            is_priority = any(kw in full_text for kw in PRIORITY_KWS)
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary[:140] + "..." if len(summary) > 140 else summary,
                "category": category,
                "priority": is_priority
            })
    except:
        pass
    return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_feed, s, u, c) for s, u, c in RSS_FEEDS]
        for future in as_completed(futures):
            items = future.result()
            for item in items:
                categorized[item["category"]].append(item)
    
    for cat in categorized:
        categorized[cat].sort(key=lambda x: (not x["priority"], x["pub"]), reverse=True)
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1: return "Now"
    if hrs < 6: return f"{hrs}h"
    if hrs < 24: return f"{hrs}h"
    return f"{hrs//24}d"

def get_time_class(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 6: return "time-hot"
    if hrs < 24: return "time-warm"
    return "time-normal"

def render_body(items):
    if not items:
        return """<div class="col-body"><div style="text-align:center;color:rgba(255,255,255,0.85);padding:70px;font-size:1.15rem;font-weight:500;">🔍 Scanning for strategic signals...</div></div>"""
    
    cards = []
    for item in items:
        time_str = get_time_str(item["pub"])
        time_class = get_time_class(item["pub"])
        title = html.escape(item["title"])
        link = html.escape(item["link"])
        source = html.escape(item["source"])
        
        card_class = "news-card-priority" if item["priority"] else "news-card"
        
        card_html = f'''
        <div class="{card_class}">
            <a href="{link}" target="_blank" class="news-title">{title}</a>
            <div class="news-meta">
                <span class="{time_class}">{time_str}</span>
                <span>•</span>
                <span>{source}</span>
            </div>
        </div>
        '''
        cards.append(card_html)
    
    return '<div class="col-body">' + ''.join(cards) + '</div>'

# LOADING ANIMATION
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div class="loading-container">
            <h1 class="loading-title">⚡ Igniting AI Powered Engine</h1>
            <p class="loading-subtitle">Real-time Strategic Signals – Mergers, Acquisitions, Partnerships & Deals</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.8)
placeholder.empty()

# HEADER
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI Powered Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# STRATEGIC INTELLIGENCE SECTION (your latest version)
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🚀 Strategic Intelligence</div>
    <div class="hero-grid">
        <div class="hero-box">
            <div class="hero-box-title" style="color: #10b981; border-bottom-color: #10b981;">🟢 STRATEGIC HITS</div>
            <div class="hero-content">
                <div class="hero-item">
                    <b>NBA Scores Strategic Investment in Evergent</b><br>
                    The NBA has taken a strategic equity stake in Evergent, naming it a 'Preferred Vendor' to drive global League Pass personalization and churn management across 185 countries.
                </div>
                <div class="hero-item">
                    <b>CES - Agentic AI Revolution</b><br>
                    Evergent CEO Vijay Sajja at CES defines the shift from GenAI to <b>Agentic AI</b>—BSS that independently executes subscriber retention strategies.
                </div>
                <div class="hero-item">
                    <b>Amdocs-Matrixx Deal Closed</b><br>
                    Amdocs completes its $200M acquisition of charging leader Matrixx Software to dominate the Tier-1 5G billing market.
                </div>
                <div class="hero-item">
                    <b>Disney-Hulu Merger Underway</b><br>
                    Disney officially begins phasing out the standalone Hulu app to integrate all content into a unified Disney+ hub.
                </div>
                <div class="hero-item">
                    <b>NEC Expands North American Footprint</b><br>
                    Japan's NEC finalizes the acquisition of CSG, significantly scaling Netcracker's North American SaaS footprint.
                </div>
            </div>
        </div>
        <div class="hero-box">
            <div class="hero-box-title" style="color: #f97316; border-bottom-color: #f97316;">🟠 MARKET PULSE</div>
            <div class="hero-content">
                <div class="hero-item">
                    <b>Agentic AI Core</b><br>
                    By EOY 2026, autonomous AI agents are expected to handle roughly 40% of standard BSS operational tasks, fundamentally reshaping telecom operations.
                </div>
                <div class="hero-item">
                    <b>Satellite Broadband Breakout</b><br>
                    Direct-to-consumer satellite broadband moves from niche to mainstream as a primary fiber competitor, disrupting traditional ISP models.
                </div>
                <div class="hero-item">
                    <b>Physical AI in Production</b><br>
                    Amazon deploys its 1-millionth robot, integrated with DeepFleet AI for a 10% gain in warehouse efficiency, signaling the industrial AI revolution.
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Dynamic RSS Feed Loading
with st.spinner("🔍 Scanning for latest strategic news..."):
    data = load_feeds()

# Render News Columns
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])[:15]
    
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]} col-header">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)

# FOOTER
st.markdown("""
<div class="footer-container">
    <strong>Strict Focus:</strong> Mergers, Acquisitions, Partnerships, Deals & Strategic Moves<br>
    <strong>Priority:</strong> Evergent/NBA/Netcracker/Amdocs/NEC first | <strong>🔄 Auto-refresh:</strong> Every 5 minutes
</div>
""", unsafe_allow_html=True)

st.markdown('<script>setTimeout(function() {window.location.reload();}, 300000);</script>', unsafe_allow_html=True)

keep_alive()
