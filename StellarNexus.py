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

# PREMIUM STYLING (unchanged - kept your beautiful design)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', sans-serif;
        padding-top: 0.5rem;
    }
    
    .header-container {
        background: rgba(255, 255, 255, 0.96);
        padding: 1.5rem 2rem;
        text-align: center;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        margin: 0 0 2rem 0;
        border-bottom: 4px solid #1e40af;
    }
    
    .main-title { font-size: 2.6rem; font-weight: 800; color: #0a192f; margin: 0; letter-spacing: -0.8px; }
    .subtitle { font-size: 1.1rem; color: #475569; margin-top: 0.6rem; font-weight: 500; }
    
    .hero-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 35px rgba(0,0,0,0.12);
        border: 1px solid #e2e8f0;
    }
    
    .hero-title {
        color: #0a192f;
        font-size: 1.85rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        border-left: 6px solid #1e40af;
        padding-left: 15px;
    }
    
    .hero-box {
        background: #f1f5f9;
        border-radius: 12px;
        padding: 1.5rem;
        min-height: 220px;
        border: 1px solid #e2e8f0;
    }
    
    .hero-box-title { font-weight: 800; font-size: 1.1rem; margin-bottom: 12px; }
    .hero-content { color: #1e293b; font-size: 0.95rem; line-height: 1.7; }
    .hero-content b { color: #0a192f; font-weight: 700; }
    
    /* News Sections - unchanged */
    .col-header { padding: 12px 16px; border-radius: 14px 14px 0 0; color: white; font-weight: 700; font-size: 0.95rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.12); }
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #8b5cf6);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #10b981);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #f97316);}
    
    .col-body { background: white; border-radius: 0 0 14px 14px; padding: 12px; min-height: 480px; max-height: 580px; overflow-y: auto; box-shadow: 0 6px 20px rgba(0,0,0,0.08); margin-bottom: 1rem; }
    
    .news-card { background: #fafbfc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 10px; transition: all 0.3s ease; }
    .news-card:hover { background: #f1f5f9; box-shadow: 0 6px 16px rgba(0,0,0,0.08); transform: translateY(-1px); }
    
    .news-card-priority { background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%); border: 2px solid #fbbf24; border-radius: 10px; padding: 12px; margin-bottom: 10px; }
    .news-card-priority:hover { background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); box-shadow: 0 8px 20px rgba(251,191,36,0.2); }
    
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
    
    .ultra-priority { border: 3px solid #ef4444; background: rgba(239,68,68,0.1); box-shadow: 0 0 15px rgba(239,68,68,0.4); animation: pulse 2s infinite; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(239,68,68,0.5); } 70% { box-shadow: 0 0 0 10px rgba(239,68,68,0); } 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); } }
</style>
""", unsafe_allow_html=True)

# EXPANDED RSS FEEDS (dynamic, Jan 2026-relevant sources)
RSS_FEEDS = [
    # Telco OSS/BSS + Agentic AI focus
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Light Reading OSS/BSS", "https://www.lightreading.com/rss/oss-bss-cx", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("The Fast Mode OSS/BSS", "https://www.thefastmode.com/oss-bss-news/feed", "telco"),

    # OTT & Streaming
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/", "ott"),

    # Sports Media & Rights
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml", "sports"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("Sports Business Journal", "https://www.sportsbusinessjournal.com/rss", "sports"),

    # AI/Tech (including telecom AI)
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("Wired", "https://www.wired.com/feed/rss", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS & AGENTIC AI", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & STREAMING", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA & RIGHTS", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "AI & TECHWATCH", "style": "col-header-orange"},
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# CATEGORY-SPECIFIC PRIORITY KEYWORDS (Jan 2026 trends)
PRIORITY_KEYWORDS = {
    "telco": ["amdocs", "matrixx", "netcracker", "csg", "evergent", "oss", "bss", "charging", "billing", "agentic ai", "multi-agent", "mycom", "groundhog", "t-mobile", "cerillion", "merger", "acquisition"],
    "ott": ["netflix", "disney+", "streaming", "ott", "release", "content deal", "subscriber", "churn"],
    "sports": ["nba", "league pass", "rights", "streaming sports", "golf", "evergent"],
    "technology": ["ai", "agentic ai", "generative ai", "quantum ai", "nvidia", "telecom ai", "autonomous"]
}

EVERGENT_KEYWORDS = ["evergent", "evergent technologies"]

def clean(raw):
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw or ""))).strip()

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code != 200: return items
        
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=10)  # Wider window for better coverage
        
        for entry in feed.entries[:12]:
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
            
            text_lower = (title + " " + summary).lower()
            is_evergent = any(kw in text_lower for kw in EVERGENT_KEYWORDS)
            is_priority = is_evergent or any(kw in text_lower for kw in PRIORITY_KEYWORDS.get(category, []))
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary,
                "category": category,
                "priority": is_priority,
                "ultra": is_evergent
            })
    except:
        pass
    return items

@st.cache_data(ttl=600, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(fetch_feed, s, u, c) for s, u, c in RSS_FEEDS]
        for future in as_completed(futures):
            for item in future.result():
                categorized[item["category"]].append(item)
    
    # AI-like sorting: ultra first, then priority, then newest
    for cat in categorized:
        categorized[cat].sort(key=lambda x: (-x["ultra"], -x["priority"], x["pub"]), reverse=True)
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1: return "Now", "time-hot"
    if hrs < 6: return f"{hrs}h", "time-hot"
    if hrs < 24: return f"{hrs}h", "time-warm"
    return f"{hrs//24}d", "time-normal"

def render_body(items):
    if not items:
        return """<div class="col-body"><div style="text-align:center;color:#94a3b8;padding:40px;">No recent signals — scanning...</div></div>"""
    
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
            <p style="color:#64748b;font-size:1.2rem;">Fetching real-time global signals...</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.8)

placeholder.empty()

# Header
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time AI-Powered Competitive Intelligence Dashboard • Jan 16, 2026</p>
</div>
""", unsafe_allow_html=True)

# Dynamic Highlights (pulled from real feeds)
with st.spinner("Building dynamic highlights..."):
    data = load_feeds()

highlight_grid = '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">'

for cat, color, title in [("telco", "#10b981", "🟢 OSS/BSS & AGENTIC AI HITS"), ("sports", "#f97316", "🟠 SPORTS & EVERGENT PULSE")]:
    recent_priorities = [i for i in data.get(cat, []) if i["priority"] and (datetime.now() - i["pub"]).days <= 10][:3]
    box_md = f'<div class="hero-box"><div class="hero-box-title" style="color: {color};">{title}</div><div class="hero-content">'
    if recent_priorities:
        for h in recent_priorities:
            days = (datetime.now() - h["pub"]).days
            tag = "🚨 ULTRA EVERGENT" if h["ultra"] else "High Priority"
            box_md += f'<b>{tag}:</b> {h["title"]} ({days}d ago via {h["source"]})<br><a href="{h["link"]}" target="_blank">Read →</a><br><br>'
    else:
        box_md += "Scanning for fresh signals..."
    box_md += '</div></div>'
    highlight_grid += box_md

highlight_grid += '</div>'

st.markdown(f"""
<div class="hero-container">
    <div class="hero-title">🚀 REAL-TIME HIGHLIGHTS (Dynamic)</div>
    {highlight_grid}
</div>
""", unsafe_allow_html=True)

# News Columns
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])[:12]  # More items for richer view
    
    with cols[idx]:
        prio_count = sum(1 for i in items if i["priority"] or i["ultra"])
        extra = f' <span style="background:#fef3c7;color:#92400e;padding:4px 10px;border-radius:8px;font-size:0.85rem;">{prio_count} Priorities</span>' if prio_count else ""
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}{extra}</div>', unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center;color:rgba(255,255,255,0.95);font-size:0.8rem;margin-top:25px;padding:16px;background:linear-gradient(135deg,rgba(10,25,47,0.95),rgba(30,41,59,0.95));border-radius:10px;">
    <strong>🔄 Auto-refresh:</strong> Every 10 min | <strong>🤖 Powered by:</strong> Real-time RSS + AI Priority Engine
    <p style="margin-top:8px;font-size:0.75rem;opacity:0.9;">@saptechsrini • Live as of Jan 16, 2026</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
st.markdown('<script>setTimeout(() => location.reload(), 600000);</script>', unsafe_allow_html=True)

keep_alive()
