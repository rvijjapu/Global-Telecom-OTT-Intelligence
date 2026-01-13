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
# PAGE CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ──────────────────────────────────────────────────────────────────────────────
# GLOBAL PROFESSIONAL STYLING - Fixed containment & beautiful look
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    
    .header-container {
        background: rgba(10, 25, 47, 0.94);
        color: white;
        padding: 2rem 2.5rem;
        text-align: center;
        border-radius: 0 0 24px 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.35);
        margin-bottom: 2.5rem;
    }
    
    .main-title {
        font-size: 3.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .subtitle {
        font-size: 1.3rem;
        opacity: 0.9;
        margin-top: 0.7rem;
    }
    
    .hero-container {
        background: rgba(255,255,255,0.97);
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
    
    .col-header {
        padding: 14px 16px;
        border-radius: 14px 14px 0 0;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        box-shadow: 0 5px 16px rgba(0,0,0,0.18);
    }
    
    .col-header-pink    { background: linear-gradient(135deg, #ec4899, #db2777); }
    .col-header-purple  { background: linear-gradient(135deg, #a78bfa, #7c3aed); }
    .col-header-green   { background: linear-gradient(135deg, #10b981, #059669); }
    .col-header-orange  { background: linear-gradient(135deg, #fb923c, #ea580c); }
    
    .section-box {
        background: white;
        border-radius: 0 0 14px 14px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        overflow: hidden;
        margin-bottom: 2rem;
        border: 1px solid #e5e7eb;
    }
    
    .news-container {
        padding: 16px;
        min-height: 420px;
        max-height: 680px;
        overflow-y: auto;
    }
    
    .news-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 14px;
        transition: all 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        background: #f1f5f9;
    }
    
    .news-card-priority {
        background: linear-gradient(135deg, #fefce8, #fef3c7);
        border: 2px solid #fbbf24;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 14px;
    }
    
    .news-title {
        color: #1e40af;
        font-size: 1.02rem;
        font-weight: 600;
        line-height: 1.38;
        text-decoration: none;
        display: block;
        margin-bottom: 0.6rem;
    }
    
    .news-title:hover {
        color: #1d4ed8;
        text-decoration: underline;
    }
    
    .news-meta {
        font-size: 0.84rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    
    .time-hot    { color: #dc2626; font-weight: 700; }
    .time-warm   { color: #ea580c; font-weight: 700; }
    .time-normal { color: #64748b; }
    
    .news-container::-webkit-scrollbar { width: 7px; }
    .news-container::-webkit-scrollbar-track { background: #f3f4f6; border-radius: 12px; }
    .news-container::-webkit-scrollbar-thumb { background: #9ca3af; border-radius: 12px; }
    
    #MainMenu, footer, header { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# RSS SOURCES & CONFIG
# ──────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("Wired", "https://www.wired.com/feed/rss", "technology"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & STREAMING", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "AI & TECH", "style": "col-header-orange"},
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Aggressive junk filter
JUNK_PATTERNS = [
    r'coupon', r'code', r'discount.*code', r'sale', r'offer', r'promo', r'voucher',
    r'black\s*friday', r'cyber\s*monday', r'flash\s*sale', r'limited\s*time',
    r'giveaway', r'contest', r'win\s*(free|now)', r'free\s*trial', r'sign\s*up',
    r'shop\s*now', r'buy\s*now', r'best\s*price', r'%.*off'
]

# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────
def clean(raw):
    if not raw: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def is_junk(title, summary=""):
    text = (title + " " + summary).lower()
    return any(re.search(pat, text) for pat in JUNK_PATTERNS)

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200: return items
        
        feed = feedparser.parse(resp.content)
        cutoff = datetime.now() - timedelta(days=7)
        
        for entry in feed.entries[:12]:
            title = clean(entry.get("title", ""))
            if len(title) < 30: continue
            
            summary = clean(entry.get("summary", title))
            
            if is_junk(title, summary): continue
            
            link = entry.get("link", "#")
            
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6])
                        break
                    except: pass
            
            if not pub or pub < cutoff: continue
            
            # Priority flag for visual highlight
            priority_keywords = ["amdocs", "netcracker", "matrixx", "evergent", "oss", "bss",
                               "merger", "acquisition", "charging", "billing", "monetization"]
            is_priority = any(kw in (title + summary).lower() for kw in priority_keywords)
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "category": category,
                "priority": is_priority
            })
    except: pass
    
    return items

@st.cache_data(ttl=600, show_spinner=False)
def load_feeds():
    categorized = {k: [] for k in SECTIONS}
    
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(fetch_feed, src, url, cat) 
                   for src, url, cat in RSS_FEEDS]
        
        for future in as_completed(futures):
            try:
                categorized[future.result()[0]["category"]].extend(future.result())
            except: pass
    
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
        categorized[cat] = categorized[cat][:12]
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 2: return "🟢 Now", "time-hot"
    if hrs < 12: return f"🟠 {hrs}h", "time-warm"
    return f"🔵 {hrs//24}d", "time-normal"

# ──────────────────────────────────────────────────────────────────────────────
# RENDER SECTION - Perfect containment
# ──────────────────────────────────────────────────────────────────────────────
def render_section(icon, name, style_class, items):
    header = f'<div class="{style_class}">{icon} {name}</div>'
    
    content = ""
    if not items:
        content = '<div style="padding:140px 20px; text-align:center; color:#94a3b8; font-size:1.15rem;">No critical news in last 7 days</div>'
    else:
        for item in items:
            time_str, time_class = get_time_str(item["pub"])
            title = html.escape(item["title"])
            link = html.escape(item["link"])
            source = html.escape(item["source"])
            
            card_class = "news-card-priority" if item["priority"] else "news-card"
            
            content += f'''
            <div class="{card_class}">
                <a href="{link}" target="_blank" class="news-title">{title}</a>
                <div class="news-meta">
                    <span class="{time_class}">{time_str}</span>
                    <span>•</span>
                    <span>{source}</span>
                </div>
            </div>
            '''
    
    full_html = f'''
    <div class="section-box">
        {header}
        <div class="news-container">{content}</div>
    </div>
    '''
    
    components.html(full_html, height=700, scrolling=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION FLOW
# ──────────────────────────────────────────────────────────────────────────────
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:70vh; text-align:center;">
            <h1 style="color:#0a192f; font-size:3rem; font-weight:800;">⚡ Stellar Nexus Intelligence</h1>
            <p style="color:#64748b; font-size:1.3rem; margin-top:1.2rem;">Loading critical global telecom & OTT signals...</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.6)

placeholder.empty()

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Powered Real-time Critical Intelligence • No Promos • January 2026</p>
</div>
""", unsafe_allow_html=True)

# Strategic Highlights (your original content)
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🚀 KEY HIGHLIGHTS</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
        <div class="hero-box">
            <div class="hero-box-title" style="color: #10b981;">🟢 STRATEGIC HITS</div>
            <div class="hero-content">
                <b>Amdocs-Matrixx Deal:</b> $200M acquisition completed — strengthens Tier-1 5G charging leadership<br><br>
                <b>Disney-Hulu Integration:</b> Standalone Hulu app phase-out begins for unified Disney+ hub<br><br>
                <b>NEC-CSG Acquisition:</b> NEC finalizes CSG deal, expanding Netcracker North America footprint
            </div>
        </div>
        <div class="hero-box">
            <div class="hero-box-title" style="color: #f97316;">🟠 MARKET PULSE</div>
            <div class="hero-content">
                <b>Agentic BSS Core:</b> Autonomous AI agents projected to manage ~40% of BSS operations by EOY<br><br>
                <b>Satellite Broadband Rise:</b> Direct-to-consumer services emerging as fiber alternative<br><br>
                <b>Physical AI Milestone:</b> Amazon reaches 1-millionth robot with DeepFleet integration
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Load & Display
with st.spinner("Scanning high-impact sources (zero promotions)..."):
    data = load_feeds()

cols = st.columns(4)

for idx, cat in enumerate(["telco", "ott", "sports", "technology"]):
    sec = SECTIONS[cat]
    items = data.get(cat, [])[:12]
    
    with cols[idx]:
        render_section(
            sec["icon"],
            sec["name"],
            sec["style"],
            items
        )

# Footer
st.markdown(f'''
<div style="text-align:center; color:rgba(255,255,255,0.9); font-size:0.9rem; margin:3rem 0 2rem; 
            padding:20px; background:linear-gradient(135deg,rgba(10,25,47,0.96),rgba(30,41,59,0.96)); 
            border-radius:16px;">
    <p><strong>🕐 Live:</strong> {datetime.now().strftime('%H:%M:%S')} IST • <strong>🔄 Auto-refresh:</strong> every 5 min</p>
    <p style="margin-top:10px; opacity:0.85;">
        Focused on critical telecom/OTT news • No coupons, sales or promos • Powered by Real-time Intelligence
    </p>
</div>
''', unsafe_allow_html=True)

# Auto-refresh
st.markdown('<script>setTimeout(() => location.reload(), 300000);</script>', unsafe_allow_html=True)

# Keep-alive
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

keep_alive()
