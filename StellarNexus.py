import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time
import streamlit.components.v1 as components

# ══════════════════════════════════════════════════════════════════════════════
# KEEP-ALIVE - MOVED TO TOP so it's defined before call
# ══════════════════════════════════════════════════════════════════════════════
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM LIGHT THEME STYLING (beautiful & stable)
# ══════════════════════════════════════════════════════════════════════════════
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
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        margin: 0 0 2.5rem 0;
        border-bottom: 6px solid #1e40af;
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        color: #0a192f;
        margin: 0;
        letter-spacing: -0.8px;
    }
    
    .subtitle {
        font-size: 1.35rem;
        color: #475569;
        margin-top: 0.8rem;
        font-weight: 500;
    }
    
    .hero-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 18px;
        padding: 2.2rem;
        margin-bottom: 2.5rem;
        box-shadow: 0 14px 48px rgba(0,0,0,0.12);
        border: 1px solid #e2e8f0;
    }
    
    .hero-title {
        color: #0a192f;
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 1.6rem;
        border-left: 8px solid #1e40af;
        padding-left: 18px;
    }
    
    .hero-box {
        background: #f8fafc;
        border-radius: 14px;
        padding: 1.8rem;
        border: 1px solid #e2e8f0;
        min-height: 240px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    }
    
    .hero-box-title {
        font-weight: 800;
        font-size: 1.25rem;
        margin-bottom: 1rem;
        color: #0a192f;
    }
    
    .hero-content {
        color: #1e293b;
        font-size: 1rem;
        line-height: 1.75;
    }
    
    .col-header {
        padding: 16px;
        border-radius: 16px 16px 0 0;
        color: white;
        font-weight: 700;
        font-size: 1.2rem;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.18);
    }
    
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #7c3aed);}
    .col-header-green {background: linear-gradient(135deg, #10b981, #059669);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #ea580c);}
    
    .section-box {
        background: white;
        border-radius: 0 0 16px 16px;
        box-shadow: 0 12px 48px rgba(0,0,0,0.12);
        overflow: hidden;
        margin-bottom: 2.8rem;
        border: 1px solid #e5e7eb;
    }
    
    .news-container {
        padding: 1.6rem;
        min-height: 520px;
        max-height: 820px;
        overflow-y: auto;
    }
    
    .news-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1.4rem;
        transition: all 0.35s ease;
    }
    
    .news-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 40px rgba(0,0,0,0.12);
        background: #f1f5f9;
    }
    
    .news-card-priority {
        background: linear-gradient(135deg, #fefce8, #fef3c7);
        border: 2px solid #fbbf24;
    }
    
    .news-title {
        color: #1e40af;
        font-size: 1.12rem;
        font-weight: 600;
        line-height: 1.45;
        text-decoration: none;
        display: block;
        margin-bottom: 0.8rem;
    }
    
    .news-title:hover { color: #1d4ed8; text-decoration: underline; }
    
    .news-meta {
        font-size: 0.9rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
    }
    
    .time-hot {color: #dc2626; font-weight: 700;}
    .time-warm {color: #ea580c; font-weight: 700;}
    .time-normal {color: #64748b;}
    
    .news-container::-webkit-scrollbar {width: 8px;}
    .news-container::-webkit-scrollbar-track {background: #f3f4f6; border-radius: 14px;}
    .news-container::-webkit-scrollbar-thumb {background: #9ca3af; border-radius: 14px;}
    
    .footer-bar {
        text-align: center;
        color: rgba(255,255,255,0.9);
        font-size: 0.95rem;
        margin: 3rem 0 2rem;
        padding: 1.8rem;
        background: linear-gradient(135deg, rgba(10,25,47,0.94), rgba(30,41,59,0.94));
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    #MainMenu, footer, header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# RSS FEEDS & CONFIG
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
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("Wired", "https://www.wired.com/feed/rss", "technology"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & STREAMING", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "AI TECHWATCH", "style": "col-header-orange"},
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def clean(raw):
    if not raw: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200: return items
        
        feed = feedparser.parse(resp.content)
        cutoff = datetime.now() - timedelta(days=7)
        
        for entry in feed.entries[:12]:
            title = clean(entry.get("title", ""))
            if len(title) < 40: continue
            
            summary = clean(entry.get("summary", title))
            
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
            
            is_priority = any(kw in (title + summary).lower() for kw in ["amdocs", "netcracker", "matrixx", "merger", "acquisition"])
            
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

@st.cache_data(ttl=600)
def load_feeds():
    categorized = {k: [] for k in SECTIONS}
    
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(fetch_feed, src, url, cat) for src, url, cat in RSS_FEEDS]
        
        for future in as_completed(futures):
            try:
                articles = future.result()
                if articles:
                    cat = articles[0]["category"]
                    categorized[cat].extend(articles)
            except: pass
    
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
        categorized[cat] = categorized[cat][:12]
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 3: return "🟢 Now", "time-hot"
    if hrs < 12: return f"🟠 {hrs}h", "time-warm"
    return f"🔵 {hrs//24}d", "time-normal"

# ══════════════════════════════════════════════════════════════════════════════
# RENDER SECTION - Stable HTML rendering
# ══════════════════════════════════════════════════════════════════════════════
def render_section(icon, name, style_class, items):
    header = f'<div class="{style_class}">{icon} {name}</div>'
    
    content = ""
    if not items:
        content = '<div style="padding:140px 20px; text-align:center; color:#94a3b8; font-size:1.2rem;">No critical news in last 7 days</div>'
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
        <div class="news-container">
            {content}
        </div>
    </div>
    '''
    
    # Use components.html for reliable rendering
    components.html(full_html, height=760, scrolling=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION - CEO-READY LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:70vh; text-align:center;">
            <h1 style="color:#0a192f; font-size:3.2rem; font-weight:800;">⚡ Stellar Nexus Intelligence</h1>
            <p style="color:#64748b; font-size:1.4rem; margin-top:1.2rem;">Loading critical telecom & OTT signals...</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)

placeholder.empty()

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Powered Real-time Critical Intelligence • January 2026</p>
</div>
""", unsafe_allow_html=True)

# Strategic Highlights (your original content)
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🚀 HIGHLIGHTS</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
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

# Load & Render News
with st.spinner("Scanning high-impact sources..."):
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
st.markdown(f"""
<div class="footer-bar">
    <p><strong>🕐 Live:</strong> {datetime.now().strftime('%H:%M:%S')} IST 
       | <strong>🔄 Auto-refresh:</strong> Every 5 minutes</p>
    <p style="margin-top:0.8rem; opacity:0.9;">
        Strictly filtered for business-critical news • Powered by Real-time Intelligence
    </p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
st.markdown('<script>setTimeout(() => location.reload(), 300000);</script>', unsafe_allow_html=True)

# Call keep_alive at the end (now safe)
keep_alive()
