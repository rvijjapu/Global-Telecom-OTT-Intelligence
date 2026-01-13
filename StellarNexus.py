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
# KEEP-ALIVE - Defined at top to avoid NameError
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
# PREMIUM STYLING - Light theme, beautiful, stable rendering
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
    
    [data-testid="column"] {padding: 0 8px !important;}
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
# EVERGENT CLIENTS, COMPETITORS, TOP TELCOS (FULL LISTS)
# ══════════════════════════════════════════════════════════════════════════════
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
    "Telekom Malaysia": ["telekom malaysia", "tm unifi", "unifi tv", "tm"],
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

TOP_TELCOS = {
    "Verizon": ["verizon", "verizon wireless", "verizon fios"],
    "AT&T": ["at&t", "att mobility"],
    "T-Mobile": ["t-mobile", "tmobile usa", "sprint"],
    "Comcast": ["comcast", "xfinity", "comcast cable"],
    "Charter": ["charter communications", "spectrum", "charter spectrum"],
    "Cox": ["cox communications", "cox cable", "cox business"],
    "Lumen": ["lumen technologies", "centurylink", "lumen"],
    "Frontier": ["frontier communications", "frontier"],
    "Windstream": ["windstream", "windstream enterprise"],
    "Mediacom": ["mediacom communications", "mediacom"],
    "Altice USA": ["altice usa", "optimum", "suddenlink"],
    "BT": ["bt group", "british telecom", "bt", "bt enterprise", "ee"],
    "Vodafone": ["vodafone", "vodafone group"],
    "O2": ["o2", "telefonica uk"],
    "Virgin Media": ["virgin media", "virgin media o2"],
    "Three": ["three uk", "three mobile"],
    "Orange": ["orange", "orange sa"],
    "Deutsche Telekom": ["deutsche telekom", "t-mobile europe", "telekom"],
    "Telefónica": ["telefonica", "telefonica spain", "movistar"],
    "Telecom Italia": ["telecom italia", "tim", "tim brasil"],
    "Swisscom": ["swisscom", "swisscom ag"],
    "KPN": ["kpn", "koninklijke pn"],
    "Proximus": ["proximus", "belgacom"],
    "Telenor": ["telenor", "telenor group"],
    "Telia": ["telia", "telia company"],
    "Bouygues": ["bouygues telecom", "bouygues"],
    "Singtel": ["singtel", "singapore telecom", "singapore telecommunications"],
    "StarHub": ["starhub", "starhub singapore"],
    "M1": ["m1 limited", "m1 singapore"],
    "Maxis": ["maxis", "maxis communications", "maxis malaysia"],
    "Celcom": ["celcom", "celcom axiata"],
    "Digi": ["digi telecommunications", "digi malaysia", "digi.com"],
    "Telekom Malaysia": ["telekom malaysia", "tm", "tm unifi"],
    "U Mobile": ["u mobile", "umobile malaysia"],
    "Sky NZ": ["sky new zealand", "sky nz", "sky network television"],
    "Spark": ["spark new zealand", "spark nz"],
    "2degrees": ["2degrees", "2degrees mobile"],
    "Vodafone NZ": ["vodafone new zealand", "vodafone nz"],
    "Telstra": ["telstra", "telstra corporation"],
    "Optus": ["optus", "singtel optus"],
    "TPG": ["tpg telecom", "vodafone australia"],
    "China Mobile": ["china mobile", "cmcc"],
    "China Telecom": ["china telecom", "chinanet"],
    "China Unicom": ["china unicom", "unicom"],
    "NTT": ["ntt", "nippon telegraph", "ntt docomo"],
    "SoftBank": ["softbank", "softbank corp"],
    "KDDI": ["kddi", "kddi corporation", "au"],
    "Reliance Jio": ["reliance jio", "jio", "jio platforms"],
    "Airtel": ["bharti airtel", "airtel", "airtel india"],
    "Vi": ["vodafone idea", "vi", "idea cellular"],
    "BSNL": ["bsnl", "bharat sanchar"],
    "SK Telecom": ["sk telecom", "skt"],
    "KT": ["kt corporation", "kt"],
    "LG Uplus": ["lg uplus", "lg u+"],
    "Globe": ["globe telecom", "globe philippines"],
    "PLDT": ["pldt", "philippine long distance"],
    "Smart": ["smart communications", "smart philippines"],
    "Etisalat": ["etisalat", "emirates telecom", "e&"],
    "Du": ["du", "emirates integrated"],
    "STC": ["stc", "saudi telecom", "saudi telecom company"],
    "Ooredoo": ["ooredoo", "ooredoo group"],
    "Zain": ["zain", "zain group"],
    "Mobily": ["mobily", "etihad etisalat"],
    "América Móvil": ["america movil", "claro", "telmex"],
    "Telus": ["telus", "telus communications"],
    "Rogers": ["rogers communications", "rogers"],
    "Bell": ["bell canada", "bce inc"],
    "Shaw": ["shaw communications", "shaw"],
    "MTN": ["mtn group", "mtn"],
    "Vodacom": ["vodacom", "vodacom group"],
    "Safaricom": ["safaricom", "safaricom plc"],
}

# ──────────────────────────────────────────────────────────────────────────────
# STRICT SECTION KEYWORDS
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
    "player transfers gossip", "semiconductor", "chip fabrication", "gpu manufacturing",
    "mining hardware", "crypto mining", "nft art"
]

# ──────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS - Strict per-section
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

@st.cache_data(ttl=600, show_spinner=False)
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
    if hrs < 1: return "Now", "time-hot"
    if hrs < 6: return f"{hrs}h", "time-hot"
    if hrs < 24: return f"{hrs}h", "time-warm"
    return f"{hrs//24}d", "time-normal"

# ──────────────────────────────────────────────────────────────────────────────
# RENDER SECTION - Stable rendering
# ──────────────────────────────────────────────────────────────────────────────
def render_section(icon, name, style_class, items):
    header = f'<div class="{style_class}">{icon} {name}</div>'
    
    content = ""
    if not items:
        content = '<div style="text-align:center;color:#94a3b8;padding:40px;">No recent news</div>'
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
    
    components.html(full_html, height=900, scrolling=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION - Complete dashboard
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

# Header
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI Powered Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Strategic Highlights Section - Stable rendering with components.html
highlights_html = """
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
"""
components.html(highlights_html, height=320, scrolling=False)

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
        render_section(sec["icon"], sec["name"], sec["style"], items)

# Footer
footer_html = f"""
<div style="text-align:center;color:rgba(255,255,255,0.95);font-size:0.8rem;margin-top:20px;padding:16px;background:linear-gradient(135deg,rgba(10,25,47,0.95),rgba(30,41,59,0.95));border-radius:10px;">
    <p><strong>🕐 Live:</strong> {datetime.now().strftime('%H:%M:%S')}
       | <strong>🔄 Auto-refresh:</strong> Every 5 minutes</p>
    <p style="margin-top:6px;font-size:0.7rem;opacity:0.85;">Powered by Real-time RSS Intelligence</p>
</div>
"""
components.html(footer_html, height=120, scrolling=False)

# Auto-refresh
st.markdown('<script>setTimeout(function() {window.location.reload();}, 300000);</script>', unsafe_allow_html=True)

keep_alive()
