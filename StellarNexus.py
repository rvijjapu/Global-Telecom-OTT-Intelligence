import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import streamlit.components.v1 as components

# ──────────────────────────────────────────────────────────────────────────────
# KEEP-ALIVE (defined first - no NameError)
# ──────────────────────────────────────────────────────────────────────────────
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

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
# CLEAN & BEAUTIFUL STYLING (all sections match Highlights look)
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', sans-serif;
    }

    .header-box, .section-box, .footer-box {
        background: rgba(255,255,255,0.97);
        border-radius: 18px;
        padding: 2rem;
        box-shadow: 0 12px 50px rgba(0,0,0,0.14);
        margin-bottom: 2.5rem;
        border: 1px solid #e2e8f0;
    }

    .main-title {
        font-size: 3.4rem;
        font-weight: 900;
        color: #0a192f;
        text-align: center;
        margin: 0;
    }

    .subtitle {
        font-size: 1.4rem;
        color: #475569;
        text-align: center;
        margin-top: 0.8rem;
    }

    .section-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #0a192f;
        margin-bottom: 1.5rem;
        border-left: 7px solid #1e40af;
        padding-left: 16px;
    }

    .col-header {
        padding: 16px;
        color: white;
        font-weight: 800;
        font-size: 1.3rem;
        text-align: center;
        border-radius: 16px 16px 0 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.18);
    }

    .pink-header { background: linear-gradient(135deg, #ec4899, #db2777); }
    .purple-header { background: linear-gradient(135deg, #a78bfa, #7c3aed); }
    .green-header { background: linear-gradient(135deg, #10b981, #059669); }
    .orange-header { background: linear-gradient(135deg, #fb923c, #ea580c); }

    .news-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
        transition: all 0.35s ease;
    }

    .news-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.12);
    }

    .priority-card {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border: 2px solid #fbbf24;
    }

    .news-title {
        color: #1e40af;
        font-size: 1.08rem;
        font-weight: 600;
        text-decoration: none;
        display: block;
        margin-bottom: 0.8rem;
    }

    .news-title:hover { color: #1d4ed8; text-decoration: underline; }

    .news-meta {
        font-size: 0.9rem;
        color: #64748b;
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }

    .time-hot { color: #dc2626; font-weight: 700; }
    .time-warm { color: #ea580c; font-weight: 700; }
    .time-normal { color: #64748b; }

    .footer-box {
        color: rgba(255,255,255,0.92);
        font-size: 0.95rem;
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, rgba(10,25,47,0.96), rgba(30,41,59,0.96));
        border-radius: 20px;
        box-shadow: 0 10px 45px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# STRICT KEYWORDS & EXCLUDES (exactly as you provided)
# ──────────────────────────────────────────────────────────────────────────────
TELCO_KEYWORDS = [
    "oss", "bss", "telecom oss", "telecom bss", "digital bss", "cloud-native oss",
    "telecom it stack", "telco transformation", "billing system", "charging system",
    "convergent billing", "mediation", "revenue management", "policy control",
    "order management", "product catalog", "service fulfillment", "network orchestration",
    "telecom deal", "telco partnership", "oss bss contract", "telecom modernization",
    "digital transformation", "system migration", "platform consolidation",
    "vendor replacement", "5g monetization", "network slicing", "open ran oss",
    "api-based bss", "ai-driven assurance", "real-time charging", "saas telecom platform"
]

OTT_KEYWORDS = [
    "ott platform", "streaming service", "video streaming", "subscription video",
    "svod", "avod", "fast channels", "hybrid ott", "subscriber growth", "arpu",
    "churn reduction", "content monetization", "pricing strategy", "bundling",
    "super app", "content licensing", "sports streaming", "live streaming",
    "original content", "regional content", "multi-language ott", "content aggregation",
    "ott acquisition", "streaming merger", "content deal", "distribution partnership",
    "platform expansion", "market entry"
]

SPORTS_KEYWORDS = [
    "sports media rights", "broadcasting rights", "sports streaming", "live sports",
    "sports ott", "league partnership", "media rights deal", "sponsorship deal",
    "betting partnership", "fan engagement", "digital ticketing", "pay-per-view",
    "football league", "cricket board", "basketball league", "formula racing",
    "olympics preparation", "world cup media", "sports analytics", "fan data platform",
    "ai sports insights", "smart stadium", "ar/vr sports"
]

TECH_KEYWORDS = [
    "artificial intelligence", "generative ai", "enterprise ai", "ai platform",
    "ai monetization", "ai deployment", "cloud platform", "saas platform",
    "digital platform", "enterprise software", "api platform", "data platform",
    "technology acquisition", "ai startup acquisition", "strategic partnership",
    "platform expansion", "product launch", "enterprise contract", "cloud migration",
    "data warehouse", "mlops", "ai governance", "responsible ai", "edge computing"
]

JUNK_EXCLUDES = [
    "oil", "gas", "petroleum", "insurance", "banking core", "semiconductor",
    "chip manufacturing", "mining", "power plant", "cinema release", "box office",
    "movie review", "celebrity gossip", "film awards", "music album launch",
    "player injury", "match score", "fantasy tips", "sports betting odds",
    "player transfers gossip", "chip fabrication", "gpu manufacturing",
    "mining hardware", "crypto mining", "nft art"
]

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
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS", "style": "pink-header"},
    "ott": {"icon": "📺", "name": "OTT & STREAMING", "style": "purple-header"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA", "style": "green-header"},
    "technology": {"icon": "⚡", "name": "AI TECHWATCH", "style": "orange-header"},
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ──────────────────────────────────────────────────────────────────────────────
# FILTERING
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
            if len(title) < 45: continue
            
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
            
            is_priority = any(kw in (title + summary).lower() for kw in ["netcracker", "amdocs", "matrixx", "merger", "acquisition"])
            
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
# MAIN DASHBOARD - ALL SAFE via components.html
# ──────────────────────────────────────────────────────────────────────────────
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

# Header
components.html("""
<div class="header-box">
    <div class="main-title">🌐 Global Telecom & OTT Stellar Nexus</div>
    <div class="subtitle">AI-Powered Real-time Critical Intelligence • January 2026</div>
</div>
""", height=140, scrolling=False)

# Highlights
components.html("""
<div class="section-box">
    <div class="section-title">🚀 HIGHLIGHTS</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div class="strategic-box">
            <div class="strategic-title"><span style="font-size:2rem;">🌟</span> STRATEGIC HITS</div>
            <div class="highlight-item"><b>Amdocs-Matrixx Deal:</b> Amdocs completes $200M acquisition of charging leader Matrixx Software to dominate Tier-1 5G billing market.</div>
            <div class="highlight-item"><b>Disney-Hulu Merger:</b> Disney begins phasing out standalone Hulu app for unified Disney+ hub.</div>
            <div class="highlight-item"><b>NEC Expansion:</b> NEC finalizes CSG acquisition, scaling Netcracker North American SaaS footprint.</div>
        </div>
        <div class="pulse-box">
            <div class="pulse-title"><span style="font-size:2rem;">🔥</span> PULSE</div>
            <div class="highlight-item"><b>Agentic AI Core:</b> By EOY 2026, autonomous AI agents expected to handle ~40% of BSS operations.</div>
            <div class="highlight-item"><b>Satellite Breakout:</b> Direct-to-consumer satellite broadband becomes mainstream fiber competitor.</div>
            <div class="highlight-item"><b>Physical AI Milestone:</b> Amazon deploys 1-millionth robot with DeepFleet AI integration.</div>
        </div>
    </div>
</div>
""", height=420, scrolling=False)

# Load news
with st.spinner("Loading only critical, relevant intelligence..."):
    data = load_feeds()

cols = st.columns(4)

for idx, cat in enumerate(["telco", "ott", "sports", "technology"]):
    with cols[idx]:
        sec = SECTIONS[cat]
        items = data.get(cat, [])[:10]
        
        header = f'<div class="col-header {sec["style"]}">{sec["icon"]} {sec["name"]}</div>'
        
        content = ""
        if not items:
            content = '<div style="padding:140px 20px; text-align:center; color:#94a3b8; font-size:1.2rem;">No critical news in last 7 days</div>'
        else:
            for item in items:
                time_str, time_class = get_time_str(item["pub"])
                title = html.escape(item["title"])
                link = html.escape(item["link"])
                source = html.escape(item["source"])
                
                card_class = "priority-card" if item["priority"] else "news-card"
                
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
        
        full_section = f'''
        <div class="section-box">
            {header}
            <div class="news-container">{content}</div>
        </div>
        '''
        
        components.html(full_section, height=860, scrolling=True)

# Footer
components.html(f"""
<div class="footer-box">
    <p><strong>🕐 Live:</strong> {datetime.now().strftime('%H:%M:%S')} IST | <strong>🔄 Auto-refresh:</strong> Every 5 minutes</p>
    <p style="margin-top:1.2rem; opacity:0.92;">
        Strictly filtered using your exact keywords • OSS/BSS • OTT • Sports Rights • Enterprise AI • No junk • CEO Dashboard
    </p>
</div>
""", height=140, scrolling=False)

# Auto-refresh
st.markdown('<script>setTimeout(() => location.reload(), 300000);</script>', unsafe_allow_html=True)

keep_alive()
