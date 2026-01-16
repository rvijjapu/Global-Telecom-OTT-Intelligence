import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG & KEEP-ALIVE
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Global Telecom & OTT Stellar Nexus", page_icon="🌐", layout="wide", initial_sidebar_state="collapsed")

@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STYLING
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp { background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; font-family: 'Inter', sans-serif; padding-top: 0.5rem; }
    
    .header-container { background: rgba(255,255,255,0.96); padding: 1.5rem 2rem; text-align: center; border-radius: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.15); margin: 0 0 2rem 0; border-bottom: 4px solid #1e40af; }
    .main-title { font-size: 2.6rem; font-weight: 800; color: #0a192f; margin: 0; letter-spacing: -0.8px; }
    .subtitle { font-size: 1.1rem; color: #475569; margin-top: 0.6rem; font-weight: 500; }
    
    .hero-container { background: rgba(255,255,255,0.98); border-radius: 16px; padding: 2rem; margin-bottom: 2rem; box-shadow: 0 10px 35px rgba(0,0,0,0.12); border: 1px solid #e2e8f0; }
    .hero-title { color: #0a192f; font-size: 1.85rem; font-weight: 800; margin-bottom: 1.5rem; border-left: 6px solid #1e40af; padding-left: 15px; }
    
    .hero-box { background: #f1f5f9; border-radius: 12px; padding: 1.5rem; min-height: 220px; border: 1px solid #e2e8f0; }
    .hero-box-title { font-weight: 800; font-size: 1.1rem; margin-bottom: 12px; }
    .hero-content { color: #1e293b; font-size: 0.95rem; line-height: 1.7; }
    .hero-content b { color: #0a192f; font-weight: 700; }
    
    .col-header { padding: 12px 16px; border-radius: 14px 14px 0 0; color: white; font-weight: 700; font-size: 0.95rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #8b5cf6);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #10b981);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #f97316);}
    
    .col-body { background: white; border-radius: 0 0 14px 14px; padding: 12px; min-height: 480px; max-height: 580px; overflow-y: auto; box-shadow: 0 6px 20px rgba(0,0,0,0.08); margin-bottom: 1rem; }
    
    .news-card, .news-card-priority { background: #fafbfc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 10px; transition: all 0.3s ease; }
    .news-card:hover, .news-card-priority:hover { background: #f1f5f9; box-shadow: 0 6px 16px rgba(0,0,0,0.08); transform: translateY(-1px); }
    .news-card-priority { background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%); border: 2px solid #fbbf24; }
    .news-card-priority:hover { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); box-shadow: 0 8px 20px rgba(251,191,36,0.2); }
    
    .ultra-priority { border: 3px solid #ef4444 !important; background: rgba(239,68,68,0.12) !important; box-shadow: 0 0 15px rgba(239,68,68,0.4); animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.5); } 70% { box-shadow: 0 0 0 10px rgba(239,68,68,0); } 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); } }
    
    .news-title { color: #1e40af; font-size: 0.92rem; font-weight: 600; line-height: 1.35; text-decoration: none; display: block; margin-bottom: 6px; }
    .news-title:hover { color: #1d4ed8; text-decoration: underline; }
    
    .news-meta { font-size: 0.76rem; color: #64748b; display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
    .time-hot {color: #dc2626; font-weight: 600; font-style: italic;}
    .time-warm {color: #ea580c; font-weight: 600;}
    .time-normal {color: #64748b;}
    
    .col-body::-webkit-scrollbar {width: 6px;}
    .col-body::-webkit-scrollbar-track {background: #f1f5f9; border-radius: 10px;}
    .col-body::-webkit-scrollbar-thumb {background: #94a3b8; border-radius: 10px;}
    
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    [data-testid="column"] {padding: 0 8px !important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# RSS FEEDS - Optimized for NBA-Evergent coverage
# ══════════════════════════════════════════════════════════════════════════════
RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("StreamTV Insider", "https://www.streamtvinsider.com/feed", "sports"),
    ("Sports Business Journal", "https://www.sportsbusinessjournal.com/rss", "sports"),
    ("Sportcal", "https://www.sportcal.com/feed", "sports"),
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/", "ott"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
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

# ══════════════════════════════════════════════════════════════════════════════
# PRIORITY KEYWORDS - Strong focus on Evergent, Amdocs, Netcracker
# ══════════════════════════════════════════════════════════════════════════════
KEY_EVERGENT = ["evergent", "evergent technologies", "nba league pass", "nba evergent"]
KEY_AMDOCS = ["amdocs", "matrixx"]
KEY_NETCRACKER = ["netcracker", "csg", "nec csg"]
PRIORITY_KEYWORDS = KEY_EVERGENT + KEY_AMDOCS + KEY_NETCRACKER + ["oss", "bss", "charging", "billing", "merger", "acquisition", "investment", "partnership", "agentic ai"]

def clean(raw):
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw or ""))).strip()

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code != 200: return items
        
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=10)
        
        for entry in feed.entries[:15]:
            title = clean(entry.get("title", ""))
            if len(title) < 20: continue
            
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
            
            text = (title + " " + summary).lower()
            is_priority = any(kw in text for kw in PRIORITY_KEYWORDS)
            is_ultra = any(kw in text for kw in KEY_EVERGENT)
            is_high_vendor = any(kw in text for kw in KEY_AMDOCS + KEY_NETCRACKER)
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary[:120] + "..." if len(summary) > 120 else summary,
                "category": category,
                "priority": is_priority,
                "ultra": is_ultra,
                "vendor_priority": is_high_vendor
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
            for item in future.result():
                categorized[item["category"]].append(item)
    
    for cat in categorized:
        categorized[cat].sort(key=lambda x: (-x["ultra"], -x["vendor_priority"], -x["priority"], x["pub"]), reverse=True)
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1: return "Now", "time-hot"
    if hrs < 6: return f"{hrs}h", "time-hot"
    if hrs < 24: return f"{hrs}h", "time-warm"
    return f"{hrs//24}d", "time-normal"

def render_body(items):
    if not items:
        return """<div class="col-body"><div style="text-align:center;color:#94a3b8;padding:40px;">No recent news</div></div>"""
    
    cards = []
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        title = html.escape(item["title"])
        link = html.escape(item["link"])
        source = html.escape(item["source"])
        
        card_class = "ultra-priority" if item["ultra"] else "news-card-priority" if item["priority"] else "news-card"
        
        card_parts = [
            f'<div class="{card_class}">',
            f'<a href="{link}" target="_blank" class="news-title">{title}</a>',
            '<div class="news-meta">',
            f'<span class="{time_class}">{time_str}</span>',
            '<span>•</span>',
            f'<span>{source}</span>',
            '</div>',
            '</div>'
        ]
        cards.append(''.join(card_parts))
    
    return '<div class="col-body">' + ''.join(cards) + '</div>'

# ──────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ──────────────────────────────────────────────────────────────────────────────

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

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI Powered Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Dynamic Highlights - Executive style with priority on Evergent, Amdocs, Netcracker
with st.spinner("Loading real-time intelligence..."):
    data = load_feeds()

all_priority = []
for cat in data:
    all_priority.extend([i for i in data[cat] if i["priority"]])

all_priority.sort(key=lambda x: (-x["ultra"], -x["vendor_priority"], x["pub"]), reverse=True)

strategic = [i for i in all_priority if i["ultra"] or i["vendor_priority"] or "merger" in i["title"].lower() or "acquisition" in i["title"].lower() or "investment" in i["title"].lower()][:3]
pulse_list = [i for i in all_priority if i not in strategic][:3]

# Render Highlights
st.markdown(f"""
<div class="hero-container">
    <div class="hero-title">🚀 HIGHLIGHTS</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div class="hero-box">
            <div class="hero-box-title" style="color: #10b981;">🟢 STRATEGIC HITS</div>
            <div class="hero-content">
                {''.join([f'<b>{i["title"]}:</b> {i["summary"]}<br><br>' for i in strategic]) or "Scanning for major strategic moves..."}
            </div>
        </div>
        <div class="hero-box">
            <div class="hero-box-title" style="color: #f97316;">🟠 PULSE</div>
            <div class="hero-content">
                {''.join([f'<b>{i["title"]}:</b> {i["summary"]}<br><br>' for i in pulse_list]) or "Live industry trends loading..."}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# News Columns
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])[:12]
    
    with cols[idx]:
        header_parts = ['<div class="', sec["style"], '">', sec["icon"], ' ', sec["name"], '</div>']
        st.markdown(''.join(header_parts), unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center;color:rgba(255,255,255,0.95);font-size:0.8rem;margin-top:20px;padding:16px;background:linear-gradient(135deg,rgba(10,25,47,0.95),rgba(30,41,59,0.95));border-radius:10px;">
    <strong>🔄 Auto-refresh:</strong> Every 5 minutes | <strong>Dynamic & Prioritized:</strong> Evergent • Amdocs • Netcracker first
</div>
""", unsafe_allow_html=True)

st.markdown('<script>setTimeout(function() {window.location.reload();}, 300000);</script>', unsafe_allow_html=True)

keep_alive()
