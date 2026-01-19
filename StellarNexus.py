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

# KEEP-ALIVE
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

# PREMIUM WOW STYLING
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@600;700;800&display=swap');

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }

    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        font-family: 'Inter', sans-serif;
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Glassmorphism Header */
    .header-container {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 2rem 3rem;
        text-align: center;
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.3);
        margin: 0 1rem 2.5rem 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }

    .header-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: headerGlow 8s ease-in-out infinite;
    }

    @keyframes headerGlow {
        0%, 100% { transform: translate(0, 0); }
        50% { transform: translate(10%, 10%); }
    }

    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #fff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -1.5px;
        text-shadow: 0 4px 20px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
        animation: titlePulse 3s ease-in-out infinite;
    }

    @keyframes titlePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }

    .subtitle {
        font-size: 1.15rem;
        color: rgba(255, 255, 255, 0.95);
        margin-top: 0.8rem;
        font-weight: 500;
        letter-spacing: 0.5px;
        position: relative;
        z-index: 1;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }

    /* Strategic Intelligence Section */
    .hero-container {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 24px;
        padding: 2.5rem;
        margin: 0 1rem 2.5rem 1rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15),
                    inset 0 1px 0 rgba(255,255,255,0.2);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .hero-title {
        font-family: 'Poppins', sans-serif;
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 2rem;
        text-shadow: 0 4px 15px rgba(0,0,0,0.3);
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .hero-title::after {
        content: '';
        flex: 1;
        height: 3px;
        background: linear-gradient(90deg, rgba(255,255,255,0.5) 0%, transparent 100%);
        border-radius: 10px;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 28px;
    }

    .hero-box {
        background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2.2rem;
        min-height: 320px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .hero-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #10b981, #3b82f6, #f59e0b);
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .hero-box:hover::before {
        opacity: 1;
    }

    .hero-box:hover {
        transform: translateY(-8px) scale(1.01);
        box-shadow: 0 15px 50px rgba(0,0,0,0.2);
        background: linear-gradient(135deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0.15) 100%);
    }

    .hero-box-title {
        font-family: 'Poppins', sans-serif;
        font-weight: 800;
        font-size: 1.3rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid;
        display: inline-block;
        letter-spacing: 1px;
        text-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }

    .hero-content {
        color: rgba(255, 255, 255, 0.95);
        font-size: 0.98rem;
        line-height: 1.9;
        font-weight: 400;
    }

    .hero-content b {
        color: #ffffff;
        font-weight: 700;
        font-size: 1rem;
    }

    .hero-item {
        margin-bottom: 1.5rem;
        padding: 1rem;
        padding-left: 1.2rem;
        border-left: 3px solid rgba(255,255,255,0.3);
        transition: all 0.3s ease;
        border-radius: 0 8px 8px 0;
        background: rgba(255,255,255,0.05);
    }

    .hero-item:hover {
        padding-left: 1.8rem;
        border-left-color: #ffffff;
        background: rgba(255,255,255,0.1);
        transform: translateX(5px);
    }

    /* News Sections - Glassmorphism Cards */
    .col-header {
        padding: 16px 20px;
        border-radius: 16px 16px 0 0;
        color: white;
        font-weight: 800;
        font-size: 1rem;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        backdrop-filter: blur(10px);
        letter-spacing: 0.8px;
        text-transform: uppercase;
        position: relative;
        overflow: hidden;
    }

    .col-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }

    .col-header:hover::before {
        left: 100%;
    }

    .col-header-pink {
        background: linear-gradient(135deg, #ec4899, #db2777, #be185d);
    }
    .col-header-purple {
        background: linear-gradient(135deg, #a78bfa, #8b5cf6, #7c3aed);
    }
    .col-header-green {
        background: linear-gradient(135deg, #34d399, #10b981, #059669);
    }
    .col-header-orange {
        background: linear-gradient(135deg, #fb923c, #f97316, #ea580c);
    }

    .col-body {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 0 0 16px 16px;
        padding: 16px;
        min-height: 520px;
        max-height: 620px;
        overflow-y: auto;
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-top: none;
    }

    .news-card {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
        transition: left 0.5s;
    }

    .news-card:hover::before {
        left: 100%;
    }

    .news-card:hover {
        background: rgba(255, 255, 255, 0.28);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transform: translateY(-3px) translateX(3px);
        border-color: rgba(255, 255, 255, 0.4);
    }

    .news-card-priority {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.25), rgba(5, 150, 105, 0.2));
        border: 2px solid rgba(16, 185, 129, 0.5);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.3);
    }

    .news-card-priority:hover {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.35), rgba(5, 150, 105, 0.3));
        transform: translateY(-3px) translateX(3px);
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.4);
    }

    .news-title {
        color: #ffffff;
        font-size: 0.96rem;
        font-weight: 700;
        line-height: 1.45;
        text-decoration: none;
        display: block;
        margin-bottom: 8px;
        text-shadow: 0 2px 8px rgba(0,0,0,0.2);
        transition: all 0.2s ease;
    }

    .news-title:hover {
        color: #fef3c7;
        text-decoration: none;
        letter-spacing: 0.3px;
    }

    .news-meta {
        font-size: 0.8rem;
        color: rgba(255, 255, 255, 0.85);
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        font-weight: 500;
    }

    .time-hot {
        color: #fef2f2; 
        font-weight: 800; 
        background: rgba(220, 38, 38, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-style: italic;
    }
    .time-warm {
        color: #fed7aa; 
        font-weight: 700;
        background: rgba(234, 88, 12, 0.25);
        padding: 2px 8px;
        border-radius: 6px;
    }
    .time-normal {
        color: rgba(255, 255, 255, 0.8);
    }

    .col-body::-webkit-scrollbar {width: 8px;}
    .col-body::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1); 
        border-radius: 10px;
    }
    .col-body::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3); 
        border-radius: 10px;
        transition: background 0.3s;
    }
    .col-body::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.5);
    }

    /* Loading Animation */
    .loading-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 70vh;
        text-align: center;
    }

    .loading-title {
        font-family: 'Poppins', sans-serif;
        color: #ffffff;
        font-size: 3.2rem;
        font-weight: 900;
        margin-bottom: 1rem;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        animation: loadingPulse 2s ease-in-out infinite;
    }

    @keyframes loadingPulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.05); opacity: 0.9; }
    }

    .loading-subtitle {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.3rem;
        font-weight: 500;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }

    /* Footer */
    .footer-container {
        text-align: center;
        color: rgba(255,255,255,0.95);
        font-size: 0.85rem;
        margin-top: 2rem;
        padding: 20px;
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(15px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 2rem 1rem 1rem 1rem;
    }

    .footer-container strong {
        color: #fef3c7;
        font-weight: 700;
    }

    /* Hide Streamlit Elements */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}

    [data-testid="column"] {padding: 0 10px !important;}

    /* Responsive */
    @media (max-width: 1200px) {
        .hero-grid {grid-template-columns: 1fr;}
        .main-title {font-size: 2.4rem;}
        .hero-title {font-size: 1.8rem;}
    }
</style>
""", unsafe_allow_html=True)

# RSS FEEDS
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

PRIORITY_KWS = ["evergent", "nba", "amdocs", "matrixx", "netcracker", "nec", "csg"]
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean(raw):
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw or ""))).strip()

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200: 
            return items
        
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=14)
        
        for entry in feed.entries[:30]:
            title = clean(entry.get("title", ""))
            if len(title) < 25: 
                continue
            
            summary = clean(entry.get("summary", entry.get("description", "")))
            link = entry.get("link", "")
            
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try: 
                        pub = datetime(*val[:6])
                    except: 
                        pass
                    break
            
            if not pub or pub < CUTOFF: 
                continue
            
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
    if hrs < 1: 
        return "Now"
    if hrs < 6: 
        return f"{hrs}h"
    if hrs < 24: 
        return f"{hrs}h"
    return f"{hrs//24}d"

def get_time_class(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 6: 
        return "time-hot"
    if hrs < 24: 
        return "time-warm"
    return "time-normal"

def render_body(items):
    if not items:
        return """<div class="col-body"><div style="text-align:center;color:rgba(255,255,255,0.8);padding:60px;font-size:1.1rem;">🔍 Scanning signals...</div></div>"""
    
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

# STRATEGIC INTELLIGENCE SECTION
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

# LOAD FEEDS
with st.spinner("🔍 Scanning for latest strategic news..."):
    data = load_feeds()

# NEWS COLUMNS
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
