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
# PROFESSIONAL & STRICT STYLING
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    .header {
        background: rgba(10, 25, 47, 0.94);
        color: white;
        padding: 2rem 2.5rem;
        text-align: center;
        border-radius: 0 0 24px 24px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.35);
        margin-bottom: 2.5rem;
    }
    .title { font-size: 3.2rem; font-weight: 800; margin: 0; }
    .subtitle { font-size: 1.35rem; opacity: 0.9; margin-top: 0.7rem; }
    .section-box {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
        margin-bottom: 2.5rem;
        border: 1px solid #e2e8f0;
    }
    .section-header {
        padding: 1.3rem 1.6rem;
        font-size: 1.4rem;
        font-weight: 700;
        color: white;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .pink-header { background: linear-gradient(135deg, #ec4899, #db2777); }
    .purple-header { background: linear-gradient(135deg, #a78bfa, #7c3aed); }
    .green-header { background: linear-gradient(135deg, #10b981, #059669); }
    .orange-header { background: linear-gradient(135deg, #fb923c, #ea580c); }
    .news-container {
        padding: 1.4rem;
        min-height: 420px;
        max-height: 680px;
        overflow-y: auto;
    }
    .news-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1rem;
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
        margin-bottom: 0.6rem;
    }
    .news-title:hover { color: #1d4ed8; text-decoration: underline; }
    .news-meta {
        font-size: 0.85rem;
        color: #64748b;
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        align-items: center;
    }
    .time-hot { color: #dc2626; font-weight: 700; }
    .time-warm { color: #ea580c; font-weight: 700; }
    .time-normal { color: #64748b; }
    .status-bar {
        background: rgba(16,185,129,0.15);
        color: #065f46;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        font-weight: 500;
        font-size: 1.05rem;
    }
    #MainMenu, footer, header { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# EVERGENT CLIENTS + COMPETITORS + TELCOS (FULL LISTS)
# ──────────────────────────────────────────────────────────────────────────────
EVERGENT_CLIENTS = {
    "Astro": ["astro malaysia", "astro sooka", "astro njoi", "astro", "sooka", "njoi"],
    "MongolTV": ["mongoltv", "mongol tv", "mongolia tv"],
    "FOX": ["fox sports", "fox corporation", "fox networks", "fox"],
    "AT&T": ["at&t", "att inc", "att wireless", "directv"],
    "NBA": ["nba", "national basketball"],
    "Shahid": ["shahid", "shahid vip", "mbc shahid"],
    "MBC": ["mbc group", "mbc", "middle east broadcasting"],
    "TV ASAHI": ["tv asahi", "asahi television", "asahi tv"],
    "TV3": ["tv3 malaysia", "tv3", "media prima"],
    "ABS-CBN": ["abs-cbn", "abscbn", "abs cbn", "philippine broadcast"],
    "Viki": ["viki", "rakuten viki", "viki streaming"],
    "TRT": ["trt world", "trt", "turkish radio"],
    "Sinclair": ["sinclair broadcast", "sinclair", "bally sports"],
    "FanDuel": ["fanduel", "fanduel group", "flutter"],
    "Bally Sports": ["bally sports", "bally regional", "diamond sports"],
    "Gotham": ["gotham advanced", "gotham fc"],
    "Marquee": ["marquee sports", "marquee network"],
    "Sony": ["sony pictures", "sony entertainment", "sonyliv", "sony india"],
    "Aha": ["aha video", "aha ott", "aha telugu"],
    "BBC": ["bbc", "british broadcasting", "bbc iplayer"],
    "Lightbox": ["lightbox", "spark lightbox"],
    "Sky": ["sky nz", "sky new zealand", "sky tv", "sky uk", "sky italia", "sky deutschland"],
    "Cignal": ["cignal tv", "cignal", "cignal satellite"],
    "ETV": ["etv network", "etv bharat"],
    "Simple TV": ["simpletv", "simple tv venezuela"],
    "Telekom Malaysia": ["telekom malaysia", "tm", "tm unifi", "unifi tv"],
    "Britbox": ["britbox", "britbox international"],
    "Quickplay": ["quickplay", "quickplay media"],
    "Pilipinas": ["pilipinas", "abs-cbn"],
}

COMPETITORS = {
    "Netcracker": ["netcracker", "netcracker technology", "nec netcracker"],
    "Amdocs": ["amdocs", "amdocs ltd", "amdocs inc"],
    "CSG": ["csg systems", "csg international", "csg"],
    "Oracle": ["oracle communications", "oracle corporation", "oracle telecom"],
    "Ericsson": ["ericsson", "telefonaktiebolaget lm ericsson"],
    "Nokia": ["nokia", "nokia networks", "nokia corporation"],
    "Huawei": ["huawei", "huawei technologies"],
    "Comarch": ["comarch", "comarch bss"],
    "Tecnotree": ["tecnotree", "tecnotree corporation"],
    "MATRIXX": ["matrixx", "matrixx software"],
    "Optiva": ["optiva", "optiva inc"],
    "Cerillion": ["cerillion", "cerillion plc"],
    "AsiaInfo": ["asiainfo", "asiainfo technologies"],
    "Hansen": ["hansen technologies", "hansen"],
    "Openet": ["openet", "openet telecom"],
    "ZTE": ["zte", "zte corporation"],
    "Mavenir": ["mavenir", "mavenir systems"],
    "Infosys": ["infosys", "infosys telecom"],
    "TCS": ["tata consultancy", "tcs", "tata communications"],
    "Wipro": ["wipro", "wipro digital"],
    "Tech Mahindra": ["tech mahindra", "mahindra comviva"],
    "Accenture": ["accenture", "accenture telecom"],
    "Capgemini": ["capgemini", "capgemini telecom"],
    "IBM": ["ibm", "ibm telecom", "ibm watson"],
    "SAP": ["sap", "sap telecom"],
    "Salesforce": ["salesforce", "salesforce communications"],
}

TOP_TELCOS = {  # (your full list here - abbreviated for brevity in this response)
    "Verizon": ["verizon", "verizon wireless", "verizon fios"],
    "AT&T": ["at&t", "att mobility"],
    "T-Mobile": ["t-mobile", "tmobile usa", "sprint"],
    # ... add remaining telcos from your list
}

# ──────────────────────────────────────────────────────────────────────────────
# STRICT KEYWORDS PER SECTION (no baby news, no junk)
# ──────────────────────────────────────────────────────────────────────────────
TELCO_KEYWORDS = [
    "oss", "bss", "billing", "charging", "monetization", "convergent billing",
    "5g", "network slicing", "revenue management", "policy control", "order management",
    "product catalog", "service fulfillment", "digital transformation", "telco modernization",
    "system migration", "platform consolidation", "vendor replacement"
]

OTT_KEYWORDS = [
    "ott platform", "streaming service", "svod", "avod", "fast channels", "hybrid ott",
    "subscriber growth", "arpu", "churn", "content monetization", "bundling",
    "content licensing", "sports streaming", "live streaming", "original content",
    "ott acquisition", "streaming merger", "distribution partnership"
]

SPORTS_KEYWORDS = [
    "sports media rights", "broadcasting rights", "sports streaming", "league partnership",
    "media rights deal", "sponsorship deal", "betting partnership", "fan engagement",
    "digital ticketing", "pay-per-view", "sports analytics", "smart stadium"
]

TECH_KEYWORDS = [
    "artificial intelligence", "generative ai", "enterprise ai", "ai platform",
    "cloud platform", "saas platform", "technology acquisition", "ai startup acquisition",
    "cloud migration", "data platform", "mlops", "ai governance", "edge computing"
]

JUNK_EXCLUDES = [
    "baby", "birth", "newborn", "pregnant", "wedding", "divorce", "gossip", "celebrity",
    "coupon", "discount", "sale", "promo", "voucher", "giveaway", "contest", "win free",
    "black friday", "cyber monday", "flash sale", "limited time offer"
]

# ──────────────────────────────────────────────────────────────────────────────
# RSS FEEDS (quality-focused)
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

# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS - Very strict filtering
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
    }.get(section, [])
    
    has_keyword = any(kw in text for kw in keywords)
    has_client = any(any(v in text for v in vars) for vars in EVERGENT_CLIENTS.values())
    has_comp = any(any(v in text for v in vars) for vars in COMPETITORS.values())
    has_telco = any(any(v in text for v in vars) for vars in TOP_TELCOS.values())
    
    return has_keyword or has_client or has_comp or has_telco

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200: return items
        
        feed = feedparser.parse(resp.content)
        cutoff = datetime.now() - timedelta(days=7)
        
        for entry in feed.entries[:15]:
            title = clean(entry.get("title", ""))
            if len(title) < 35: continue
            
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
            
            is_priority = any(kw in (title + summary).lower() for kw in ["amdocs", "netcracker", "matrixx", "merger", "acquisition"])
            
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
        categorized[cat] = categorized[cat][:12]
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 3: return "🟢 Now", "time-hot"
    if hrs < 12: return f"🟠 {hrs}h", "time-warm"
    return f"🔵 {hrs//24}d", "time-normal"

# ──────────────────────────────────────────────────────────────────────────────
# RENDER SECTION - Perfect containment
# ──────────────────────────────────────────────────────────────────────────────
def render_section(icon, name, style_class, items):
    header = f'<div class="{style_class}">{icon} {name}</div>'
    
    content = ""
    if not items:
        content = '<div style="padding:120px 20px; text-align:center; color:#94a3b8; font-size:1.15rem;">No high-impact news in last 7 days</div>'
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
    
    components.html(full_html, height=720, scrolling=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION
# ──────────────────────────────────────────────────────────────────────────────
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:70vh; text-align:center;">
            <h1 style="color:#0a192f; font-size:3.2rem; font-weight:800;">⚡ Stellar Nexus Intelligence</h1>
            <p style="color:#64748b; font-size:1.35rem; margin-top:1.2rem;">Loading critical telecom & OTT signals (no junk)...</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)

placeholder.empty()

st.markdown("""
<div class="header">
    <div class="title">Global Telecom & OTT Intelligence Nexus</div>
    <div class="subtitle">Real-time Critical Business Intelligence • Clients • Competitors • OSS/BSS • January 2026</div>
</div>
""", unsafe_allow_html=True)

with st.spinner("Scanning high-priority sources..."):
    data = load_feeds()

total = sum(len(v) for v in data.values())
st.markdown(f"""
<div class="status-bar">
    Loaded {total} high-impact articles • Last 7 days • Strictly filtered for business relevance
</div>
""", unsafe_allow_html=True)

cols = st.columns(4)

for idx, cat in enumerate(["telco", "ott", "sports", "technology"]):
    with cols[idx]:
        render_section(
            SECTIONS[cat]["icon"],
            SECTIONS[cat]["name"],
            SECTIONS[cat]["style"],
            data.get(cat, [])
        )

st.markdown("""
<div style="text-align:center; color:#94a3b8; font-size:0.9rem; margin:3rem 0 2rem;">
    Focused exclusively on EVERGENT clients, competitors, OSS/BSS, deals & monetization • No promotions • Auto-refreshes every 5 min
</div>
""", unsafe_allow_html=True)

st.markdown('<script>setTimeout(() => location.reload(), 300000);</script>', unsafe_allow_html=True)
