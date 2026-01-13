import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time
import streamlit.components.v1 as components

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Telecom & OTT Intelligence Nexus",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ──────────────────────────────────────────────────────────────────────────────
# PROFESSIONAL LIGHT THEME STYLING (beautiful wow UI)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', sans-serif;
        padding-top: 1rem;
    }
    
    .header-container {
        background: rgba(255, 255, 255, 0.97);
        padding: 2rem 2.5rem;
        text-align: center;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        margin: 0 0 2.5rem 0;
        border-bottom: 5px solid #1e40af;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        color: #0a192f;
        margin: 0;
        letter-spacing: -0.8px;
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: #475569;
        margin-top: 0.7rem;
        font-weight: 500;
    }
    
    .hero-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2.5rem;
        box-shadow: 0 12px 40px rgba(0,0,0,0.12);
        border: 1px solid #e2e8f0;
    }
    
    .hero-title {
        color: #0a192f;
        font-size: 1.9rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        border-left: 6px solid #1e40af;
        padding-left: 16px;
    }
    
    .hero-box {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.6rem;
        border: 1px solid #e2e8f0;
        min-height: 220px;
    }
    
    .hero-box-title {
        font-weight: 800;
        font-size: 1.2rem;
        margin-bottom: 0.9rem;
        color: #0a192f;
    }
    
    .hero-content {
        color: #1e293b;
        font-size: 0.98rem;
        line-height: 1.7;
    }
    
    .col-header {
        padding: 14px 16px;
        border-radius: 14px 14px 0 0;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        box-shadow: 0 5px 16px rgba(0,0,0,0.15);
    }
    
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #7c3aed);}
    .col-header-green {background: linear-gradient(135deg, #10b981, #059669);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #ea580c);}
    
    .section-box {
        background: white;
        border-radius: 0 0 14px 14px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        overflow: hidden;
        margin-bottom: 2rem;
        border: 1px solid #e5e7eb;
    }
    
    .news-container {
        padding: 1.4rem;
        min-height: 440px;
        max-height: 720px;
        overflow-y: auto;
    }
    
    .news-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.3rem;
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(0,0,0,0.1);
        background: #f1f5f9;
    }
    
    .news-card-priority {
        background: linear-gradient(135deg, #fefce8, #fef3c7);
        border: 2px solid #fbbf24;
    }
    
    .news-title {
        color: #1e40af;
        font-size: 1.05rem;
        font-weight: 600;
        line-height: 1.4;
        text-decoration: none;
        display: block;
        margin-bottom: 0.7rem;
    }
    
    .news-title:hover { color: #1d4ed8; text-decoration: underline; }
    
    .news-meta {
        font-size: 0.85rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    
    .time-hot {color: #dc2626; font-weight: 700;}
    .time-warm {color: #ea580c; font-weight: 700;}
    .time-normal {color: #64748b;}
    
    .news-container::-webkit-scrollbar {width: 7px;}
    .news-container::-webkit-scrollbar-track {background: #f3f4f6; border-radius: 12px;}
    .news-container::-webkit-scrollbar-thumb {background: #9ca3af; border-radius: 12px;}
    
    #MainMenu, footer, header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# RSS FEEDS CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
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

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=5)
        if resp.status_code != 200:
            return items
        
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=3)
        
        for entry in feed.entries[:8]:
            title = clean(entry.get("title", ""))
            if len(title) < 20:
                continue
            
            summary = clean(entry.get("summary", ""))
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
            
            # Priority detection
            priority_keywords = ["amdocs", "netcracker", "matrixx", "evergent", "oss", "bss", "merger", "acquisition"]
            is_priority = any(kw in title.lower() or kw in summary.lower() for kw in priority_keywords)
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary,
                "category": category,
                "priority": is_priority
            })
    except:
        pass
    
    return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {
        "telco": [],
        "ott": [],
        "sports": [],
        "technology": []
    }
    
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [
            executor.submit(fetch_feed, source, url, cat)
            for source, url, cat in RSS_FEEDS
        ]
        
        for future in as_completed(futures):
            items = future.result()
            for item in items:
                categorized[item["category"]].append(item)
    
    # Sort by date
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1:
        return "Now", "time-hot"
    if hrs < 6:
        return f"{hrs}h", "time-hot"
    if hrs < 24:
        return f"{hrs}h", "time-warm"
    return f"{hrs//24}d", "time-normal"

def render_body(items):
    """Render news cards - using components to avoid raw HTML display"""
    if not items:
        return """<div class="col-body"><div style="text-align:center;color:#94a3b8;padding:40px;">No recent news</div></div>"""
    
    cards = []
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        title = html.escape(item["title"])
        link = html.escape(item["link"])
        source = html.escape(item["source"])
        
        card_class = "news-card-priority" if item["priority"] else "news-card"
        
        # Build card HTML without f-strings to avoid display issues
        card_parts = [
            '<div class="' + card_class + '">',
            '<a href="' + link + '" target="_blank" class="news-title">' + title + '</a>',
            '<div class="news-meta">',
            '<span class="' + time_class + '">' + time_str + '</span>',
            '<span>•</span>',
            '<span>' + source + '</span>',
            '</div>',
            '</div>'
        ]
        
        cards.append(''.join(card_parts))
    
    body_parts = ['<div class="col-body">']
    body_parts.extend(cards)
    body_parts.append('</div>')
    
    return ''.join(body_parts)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

# Loading Screen
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:70vh;text-align:center;">
            <h1 style="color:#0a192f;font-size:2.8rem;font-weight:800;">⚡ Igniting AI-powered intelligence...</h1>
            <p style="color:#64748b;font-size:1.2rem;">Synchronizing global news nodes</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)

placeholder.empty()

# Header
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI Powered Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Strategic Highlights Section
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🚀 HIGHLIGHTS</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div class="hero-box">
            <div class="hero-box-title" style="color: #10b981;">🟢 STRATEGIC HITS</div>
            <div class="hero-content">
                <b>Amdocs-Matrixx Deal:</b> Amdocs completes its $200M acquisition of charging leader Matrixx Software to dominate the Tier-1 5G billing market.<br><br>
                <b>Disney-Hulu Merger:</b> Disney officially begins phasing out the standalone Hulu app to integrate all content into a unified Disney+ hub.<br><br>
                <b>NEC Expansion:</b> Japan's NEC finalizes the acquisition of CSG, significantly scaling Netcracker's North American SaaS footprint.
            </div>
        </div>
        <div class="hero-box">
            <div class="hero-box-title" style="color: #f97316;">🟠 PULSE</div>
            <div class="hero-content">
                <b>Agentic AI Core:</b> By EOY 2026, autonomous AI agents are expected to handle roughly 40% of standard BSS operational tasks.<br><br>
                <b>Satellite Breakout:</b> Direct-to-consumer satellite broadband moves from niche to mainstream as a primary fiber competitor.<br><br>
                <b>Physical AI:</b> Amazon deploys its 1-millionth robot, integrated with DeepFleet AI for a 10% gain in warehouse efficiency.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Fetch Real-Time News
with st.spinner(""):
    data = load_feeds()

# Render News Columns
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])[:10]
    
    with cols[idx]:
        # Render header
        header_parts = [
            '<div class="',
            sec["style"],
            '">',
            sec["icon"],
            ' ',
            sec["name"],
            '</div>'
        ]
        st.markdown(''.join(header_parts), unsafe_allow_html=True)
        
        # Render body
        st.markdown(render_body(items), unsafe_allow_html=True)

# Footer
footer_parts = [
    '<div style="text-align:center;color:rgba(255,255,255,0.95);font-size:0.8rem;margin-top:20px;padding:16px;background:linear-gradient(135deg,rgba(10,25,47,0.95),rgba(30,41,59,0.95));border-radius:10px;">',
    '<p><strong>🕐 Live:</strong> ' + datetime.now().strftime('%H:%M:%S'),
    ' | <strong>🔄 Auto-refresh:</strong> Every 5 minutes</p>',
    '<p style="margin-top:6px;font-size:0.7rem;opacity:0.85;">Powered by Real-time RSS Intelligence</p>',
    '</div>'
]

st.markdown(''.join(footer_parts), unsafe_allow_html=True)

# Auto-refresh
st.markdown('<script>setTimeout(function() {window.location.reload();}, 300000);</script>', unsafe_allow_html=True)

keep_alive()
