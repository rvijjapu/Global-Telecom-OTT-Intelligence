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
# GLOBAL CSS (moved to top for reliability)
# ──────────────────────────────────────────────────────────────────────────────
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
    
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #0a192f;
        margin: 0;
        letter-spacing: -0.8px;
    }
    
    .subtitle {
        font-size: 1.1rem;
        color: #475569;
        margin-top: 0.6rem;
        font-weight: 500;
    }
    
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
        min-height: 200px;
        border: 1px solid #e2e8f0;
    }
    
    .hero-box-title {
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 12px;
    }
    
    .hero-content {
        color: #1e293b;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    
    .hero-content b {
        color: #0a192f;
        font-weight: 700;
    }
    
    .col-header {
        padding: 12px 16px;
        border-radius: 14px 14px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #8b5cf6);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #10b981);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #f97316);}
    
    .col-body {
        background: white;
        border-radius: 0 0 14px 14px;
        padding: 12px;
        min-height: 480px;
        max-height: 580px;
        overflow-y: auto;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    .news-card {
        background: #fafbfc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    
    .news-card:hover {
        background: #f1f5f9;
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }
    
    .news-card-priority {
        background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
        border: 2px solid #fbbf24;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    
    .news-card-priority:hover {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        box-shadow: 0 8px 20px rgba(251,191,36,0.2);
    }
    
    .news-title {
        color: #1e40af;
        font-size: 0.92rem;
        font-weight: 600;
        line-height: 1.35;
        text-decoration: none;
        display: block;
        margin-bottom: 6px;
    }
    
    .news-title:hover {
        color: #1d4ed8;
        text-decoration: underline;
    }
    
    .news-meta {
        font-size: 0.76rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 7px;
        flex-wrap: wrap;
    }
    
    .time-hot {color: #dc2626; font-weight: 600; font-style: italic;}
    .time-warm {color: #ea580c; font-weight: 600;}
    .time-normal {color: #64748b;}
    
    .col-body::-webkit-scrollbar {width: 6px;}
    .col-body::-webkit-scrollbar-track {background: #f1f5f9; border-radius: 10px;}
    .col-body::-webkit-scrollbar-thumb {background: #94a3b8; border-radius: 10px;}
    
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# RSS FEEDS & CONFIG
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

# Content filters & keywords
EXCLUDED_KEYWORDS = [
    "sex", "sexual", "assault", "abuse", "murder", "kill", "death", "rape", "violence",
    "porn", "pornography", "nude", "naked", "explicit", "xxx", "adult content",
    "drug", "cocaine", "heroin", "meth", "overdose", "scandal", "controversy",
    "accused", "arrest", "lawsuit", "fraud", "scam", "crash", "accident", "disaster",
    "promo code", "coupon", "discount", "sale", "giveaway", "contest", "viral", "meme"
]

EVERGENT_CLIENTS = [
    "astro", "sooka", "njoi", "fox sports", "fox corporation", "at&t", "directv",
    "nba", "wnba", "shahid", "mbc", "tv asahi", "tv3", "abs-cbn", "viki",
    "trt", "sinclair", "fanduel", "bally sports", "sony pictures", "sonyliv",
    "aha", "bbc", "sky", "cignal", "telekom malaysia", "tm unifi", "britbox"
]

COMPETITORS = [
    "netcracker", "amdocs", "csg systems", "oracle communications", "ericsson",
    "nokia", "huawei", "matrixx", "optiva", "cerillion", "tecnotree", "comarch"
]

TOP_TELCOS = [
    "verizon", "at&t", "t-mobile", "vodafone", "bt group", "singtel",
    "reliance jio", "airtel", "china mobile", "softbank", "deutsche telekom"
]

CRITICAL_KEYWORDS = [
    "merger", "acquisition", "deal", "partnership", "contract", "agreement",
    "billion", "million", "revenue", "earnings", "profit", "loss",
    "oss", "bss", "billing", "charging", "monetization", "5g", "network",
    "streaming", "platform", "subscriber", "rights", "broadcasting",
    "launch", "expansion", "shutdown", "bankruptcy", "ipo", "investment"
]

# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────
def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def is_content_appropriate(title, summary):
    text = (title + " " + summary).lower()
    return not any(kw in text for kw in EXCLUDED_KEYWORDS)

def calculate_relevance_score(title, summary):
    text = (title + " " + summary).lower()
    score = 0
    
    for kw in CRITICAL_KEYWORDS:
        if kw in text:
            score += 8
    
    for client in EVERGENT_CLIENTS:
        if client in text:
            score += 15
            break
    
    for comp in COMPETITORS:
        if comp in text:
            score += 12
            break
    
    for telco in TOP_TELCOS:
        if telco in text:
            score += 6
            break
            
    return score

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return items
        
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=5)
        
        for entry in feed.entries[:12]:
            title = clean(entry.get("title", ""))
            if len(title) < 25:
                continue
            
            summary = clean(entry.get("summary", "") or title)
            
            if not is_content_appropriate(title, summary):
                continue
            
            link = entry.get("link", "")
            
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6])
                        break
                    except:
                        pass
            
            if not pub or pub < CUTOFF:
                continue
            
            relevance = calculate_relevance_score(title, summary)
            
            priority_keywords = ["amdocs", "netcracker", "matrixx", "evergent", "oss", "bss", 
                               "merger", "acquisition", "charging", "billing", "monetization"]
            is_priority = any(kw in (title + summary).lower() for kw in priority_keywords) \
                          or relevance >= 25
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary,
                "category": category,
                "priority": is_priority,
                "relevance": relevance
            })
    except:
        pass
    
    return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(fetch_feed, src, url, cat) 
                   for src, url, cat in RSS_FEEDS]
        
        for future in as_completed(futures):
            try:
                for item in future.result():
                    categorized[item["category"]].append(item)
            except:
                continue
    
    for cat in categorized:
        categorized[cat].sort(key=lambda x: (-x["relevance"], x["pub"]))
        categorized[cat] = categorized[cat][:10]
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1: return "Now", "time-hot"
    if hrs < 6: return f"{hrs}h ago", "time-hot"
    if hrs < 24: return f"{hrs}h ago", "time-warm"
    return f"{hrs//24}d ago", "time-normal"

# ──────────────────────────────────────────────────────────────────────────────
# RENDERING WITH COMPONENTS.HTML (most reliable method)
# ──────────────────────────────────────────────────────────────────────────────
def render_section(icon, name, style_class, items):
    header = f'''
    <div class="{style_class}">
        {icon} {name}
    </div>
    '''
    
    body_content = ""
    if not items:
        body_content = '<div style="text-align:center;color:#94a3b8;padding:40px;">No recent relevant news</div>'
    else:
        for item in items:
            time_str, time_class = get_time_str(item["pub"])
            title = html.escape(item["title"])
            link = html.escape(item["link"])
            source = html.escape(item["source"])
            
            card_class = "news-card-priority" if item["priority"] else "news-card"
            
            body_content += f'''
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
    {header}
    <div class="col-body">
        {body_content}
    </div>
    '''
    
    # Use components.html - this is the most reliable way in 2025/2026 Streamlit
    components.html(full_html, height=550, scrolling=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ──────────────────────────────────────────────────────────────────────────────

# Loading screen
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:70vh;text-align:center;">
            <h1 style="color:#0a192f;font-size:2.8rem;font-weight:800;">⚡ Igniting intelligence layer...</h1>
            <p style="color:#64748b;font-size:1.2rem;">Collecting latest telecom, OTT & sports signals</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.4)

placeholder.empty()

# Header
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time Competitive Intelligence • January 2026</p>
</div>
""", unsafe_allow_html=True)

# Strategic Highlights
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🚀 KEY HIGHLIGHTS</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div class="hero-box">
            <div class="hero-box-title" style="color: #10b981;">🟢 STRATEGIC HITS</div>
            <div class="hero-content">
                <b>Amdocs-Matrixx:</b> $200M acquisition completed — strengthens charging leadership<br><br>
                <b>Disney-Hulu:</b> Standalone Hulu app phase-out begins for unified Disney+ experience<br><br>
                <b>NEC-CSG:</b> NEC finalizes CSG acquisition, boosting Netcracker's NA footprint
            </div>
        </div>
        <div class="hero-box">
            <div class="hero-box-title" style="color: #f97316;">🟠 MARKET PULSE</div>
            <div class="hero-content">
                <b>Agentic BSS:</b> Autonomous AI agents expected to manage ~40% of BSS tasks by EOY<br><br>
                <b>Satellite Broadband:</b> Direct-to-consumer services gaining ground vs fiber<br><br>
                <b>Physical AI:</b> Amazon hits 1-million-robot milestone with DeepFleet integration
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Load & render news
with st.spinner("Loading industry intelligence..."):
    data = load_feeds()

cols = st.columns(4)
for idx, cat in enumerate(["telco", "ott", "sports", "technology"]):
    sec = SECTIONS[cat]
    items = data.get(cat, [])[:10]
    
    with cols[idx]:
        render_section(
            sec["icon"],
            sec["name"],
            sec["style"],
            items
        )

# Footer
st.markdown(f'''
<div style="text-align:center; color:rgba(255,255,255,0.95); font-size:0.8rem; margin-top:20px; padding:16px; 
            background:linear-gradient(135deg,rgba(10,25,47,0.95),rgba(30,41,59,0.95)); border-radius:10px;">
    <p><strong>🕐 Live:</strong> {datetime.now().strftime('%H:%M:%S')} • <strong>🔄 Refresh:</strong> every 5 min</p>
    <p style="margin-top:6px; font-size:0.7rem; opacity:0.85;">Powered by Real-time RSS Intelligence</p>
</div>
''', unsafe_allow_html=True)

# Auto-refresh
st.markdown('<script>setTimeout(() => {window.location.reload()}, 300000);</script>', unsafe_allow_html=True)

# Keep-alive fragment
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

keep_alive()
