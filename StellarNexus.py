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
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ──────────────────────────────────────────────────────────────────────────────
# KEEP-ALIVE (defined at top)
# ──────────────────────────────────────────────────────────────────────────────
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# BEAUTIFUL CEO-LEVEL LIGHT THEME STYLING
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', sans-serif;
    }
    
    .header-container {
        background: rgba(255, 255, 255, 0.97);
        padding: 2.2rem 3rem;
        text-align: center;
        border-radius: 22px;
        box-shadow: 0 12px 50px rgba(0,0,0,0.15);
        margin: 0 0 2.8rem 0;
        border-bottom: 6px solid #1e40af;
    }
    
    .main-title {
        font-size: 3.4rem;
        font-weight: 900;
        color: #0a192f;
        margin: 0;
        letter-spacing: -1px;
    }
    
    .subtitle {
        font-size: 1.4rem;
        color: #475569;
        margin-top: 0.8rem;
        font-weight: 500;
    }
    
    .hero-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        padding: 2.4rem;
        margin-bottom: 3rem;
        box-shadow: 0 16px 60px rgba(0,0,0,0.12);
        border: 1px solid #e2e8f0;
    }
    
    .hero-title {
        color: #0a192f;
        font-size: 2.1rem;
        font-weight: 800;
        margin-bottom: 1.8rem;
        border-left: 8px solid #1e40af;
        padding-left: 20px;
    }
    
    .hit-pulse-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2.5rem;
    }
    
    .strategic-box, .pulse-box {
        background: #f8fafc;
        border-radius: 16px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.06);
    }
    
    .strategic-title {
        color: #10b981;
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 1.3rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .pulse-title {
        color: #f97316;
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 1.3rem;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .highlight-item {
        margin-bottom: 1.6rem;
        font-size: 1.05rem;
        line-height: 1.7;
        color: #1e293b;
    }
    
    .highlight-item b {
        color: #0a192f;
        font-weight: 700;
    }
    
    .col-header {
        padding: 16px;
        border-radius: 16px 16px 0 0;
        color: white;
        font-weight: 700;
        font-size: 1.25rem;
        text-align: center;
        box-shadow: 0 6px 22px rgba(0,0,0,0.2);
    }
    
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #7c3aed);}
    .col-header-green {background: linear-gradient(135deg, #10b981, #059669);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #ea580c);}
    
    .section-box {
        background: white;
        border-radius: 0 0 16px 16px;
        box-shadow: 0 14px 50px rgba(0,0,0,0.12);
        overflow: hidden;
        margin-bottom: 3rem;
        border: 1px solid #e5e7eb;
    }
    
    .news-container {
        padding: 1.8rem;
        min-height: 560px;
        max-height: 860px;
        overflow-y: auto;
    }
    
    .news-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.35s ease;
    }
    
    .news-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 44px rgba(0,0,0,0.12);
        background: #f1f5f9;
    }
    
    .news-card-priority {
        background: linear-gradient(135deg, #fefce8, #fef3c7);
        border: 2px solid #fbbf24;
    }
    
    .news-title {
        color: #1e40af;
        font-size: 1.15rem;
        font-weight: 600;
        line-height: 1.48;
        text-decoration: none;
        display: block;
        margin-bottom: 0.9rem;
    }
    
    .news-title:hover { color: #1d4ed8; text-decoration: underline; }
    
    .news-meta {
        font-size: 0.92rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
    }
    
    .time-hot {color: #dc2626; font-weight: 700;}
    .time-warm {color: #ea580c; font-weight: 700;}
    .time-normal {color: #64748b;}
    
    .footer-bar {
        text-align: center;
        color: rgba(255,255,255,0.92);
        font-size: 0.98rem;
        margin: 4rem 0 2.5rem;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(10,25,47,0.95), rgba(30,41,59,0.95));
        border-radius: 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.35);
    }
    
    #MainMenu, footer, header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# STRICT SECTION-SPECIFIC KEYWORDS (no cross-mixing)
# ──────────────────────────────────────────────────────────────────────────────
TELCO_KEYWORDS = [
    "oss", "bss", "billing", "charging", "convergent billing", "mediation",
    "revenue management", "policy control", "order management", "product catalog",
    "service fulfillment", "network orchestration", "5g monetization", "real-time charging",
    "saas telecom platform", "telecom deal", "telco partnership", "oss bss contract",
    "telecom modernization", "digital transformation", "system migration", "platform consolidation",
    "vendor replacement"
]

OTT_KEYWORDS = [
    "ott platform", "streaming service", "svod", "avod", "fast channels", "hybrid ott",
    "subscriber growth", "arpu", "churn reduction", "content monetization", "bundling",
    "content licensing", "sports streaming", "original content", "ott acquisition",
    "streaming merger", "content deal", "distribution partnership", "platform expansion"
]

SPORTS_KEYWORDS = [
    "sports media rights", "broadcasting rights", "sports streaming", "league partnership",
    "media rights deal", "sponsorship deal", "betting partnership", "fan engagement",
    "digital ticketing", "pay-per-view"
]

TECH_KEYWORDS = [
    "artificial intelligence", "generative ai", "enterprise ai", "ai platform",
    "cloud platform", "saas platform", "technology acquisition", "strategic partnership",
    "platform expansion", "enterprise contract", "cloud migration", "mlops", "ai governance"
]

JUNK_EXCLUDES = [
    "coupon", "discount", "sale", "promo", "voucher", "giveaway", "contest", "black friday",
    "cyber monday", "flash sale", "baby", "birth", "newborn", "pregnant", "wedding", "divorce",
    "gossip", "celebrity", "player injury", "match score", "fantasy", "betting odds",
    "oil", "gas", "petroleum", "insurance", "semiconductor", "chip", "mining", "power plant",
    "crypto", "nft", "legislation", "spam", "phishing", "packaging", "satellite", "geopolitics"
]

# ──────────────────────────────────────────────────────────────────────────────
# RSS FEEDS
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
    "technology": {"icon": "⚡", "name": "AI TECHWATCH", "style": "col-header-orange"},
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ──────────────────────────────────────────────────────────────────────────────
# STRICT FILTERING
# ──────────────────────────────────────────────────────────────────────────────
def clean(raw):
    if not raw: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def is_junk(title, summary=""):
    text = (title + " " + summary).lower()
    return any(ex in text for ex in JUNK_EXCLUDES)

def is_relevant(title, summary, section):
    text = (title + " " + summary).lower()
    keywords = {
        "telco": TELCO_KEYWORDS,
        "ott": OTT_KEYWORDS,
        "sports": SPORTS_KEYWORDS,
        "technology": TECH_KEYWORDS
    }[section]
    
    return any(kw in text for kw in keywords)

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
            
            if is_junk(title, summary): continue
            if not is_relevant(title, summary, category): continue
            
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6])
                        break
                    except: pass
            
            if not pub or pub < cutoff: continue
            
            is_priority = any(kw in (title + summary).lower() for kw in ["netcracker", "amdocs", "matrixx", "merger", "acquisition", "billing", "charging"])
            
            items.append({
                "title": title,
                "link": entry.get("link", "#"),
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
        categorized[cat] = categorized[cat][:10]
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 3: return "🟢 Now", "time-hot"
    if hrs < 12: return f"🟠 {hrs}h", "time-warm"
    return f"🔵 {hrs//24}d", "time-normal"

# ──────────────────────────────────────────────────────────────────────────────
# RENDER SECTION - Stable & Beautiful
# ──────────────────────────────────────────────────────────────────────────────
def render_section(icon, name, style_class, items):
    header = f'<div class="{style_class}">{icon} {name}</div>'
    
    content = ""
    if not items:
        content = '<div style="padding:160px 20px; text-align:center; color:#94a3b8; font-size:1.25rem;">No high-impact section news in last 7 days</div>'
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
    
    components.html(full_html, height=820, scrolling=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION - CEO-READY LAYOUT
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Powered Real-time Critical Intelligence • January 2026</p>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# HIGHLIGHTS - Rocket style (CEO favorite)
# ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🚀 HIGHLIGHTS</div>
    <div class="hit-pulse-grid">
        <div class="strategic-box">
            <div class="strategic-title">
                <span style="font-size:1.8rem;">🌟</span> STRATEGIC HITS
            </div>
            <div class="highlight-item">
                <b>Amdocs-Matrixx Deal:</b> Amdocs completes $200M acquisition of charging leader Matrixx Software to dominate Tier-1 5G billing market.
            </div>
            <div class="highlight-item">
                <b>Disney-Hulu Merger:</b> Disney begins phasing out standalone Hulu app for unified Disney+ hub.
            </div>
            <div class="highlight-item">
                <b>NEC Expansion:</b> NEC finalizes CSG acquisition, scaling Netcracker North American SaaS footprint.
            </div>
        </div>
        
        <div class="pulse-box">
            <div class="pulse-title">
                <span style="font-size:1.8rem;">🔥</span> PULSE
            </div>
            <div class="highlight-item">
                <b>Agentic AI Core:</b> By EOY 2026, autonomous AI agents expected to handle ~40% of BSS operations.
            </div>
            <div class="highlight-item">
                <b>Satellite Breakout:</b> Direct-to-consumer satellite broadband becomes mainstream fiber competitor.
            </div>
            <div class="highlight-item">
                <b>Physical AI Milestone:</b> Amazon deploys 1-millionth robot with DeepFleet AI integration.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# REAL NEWS SECTIONS
# ──────────────────────────────────────────────────────
with st.spinner("Loading strictly section-relevant intelligence..."):
    data = load_feeds()

cols = st.columns(4)

for idx, cat in enumerate(["telco", "ott", "sports", "technology"]):
    with cols[idx]:
        render_section(
            SECTIONS[cat]["icon"],
            SECTIONS[cat]["name"],
            SECTIONS[cat]["style"],
            data.get(cat, [])
        )

# Footer
st.markdown(f"""
<div class="footer-bar">
    <p><strong>🕐 Live Update:</strong> {datetime.now().strftime('%H:%M:%S')} IST 
       | <strong>🔄 Auto-refresh:</strong> Every 5 minutes</p>
    <p style="margin-top:1rem; opacity:0.92;">
        Strictly filtered: TELCO OSS/BSS only • OTT deals only • Sports rights only • AI enterprise only • No junk
    </p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
st.markdown('<script>setTimeout(() => location.reload(), 300000);</script>', unsafe_allow_html=True)

# Safe call at end
keep_alive()
