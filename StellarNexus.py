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
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Global Telecom & OTT Intelligence Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
# PROFESSIONAL LIGHT THEME STYLING (beautiful wow UI)
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
        margin-bottom: 2.2rem;
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
# STRICT CLIENT / COMPETITOR / TELCO LISTS (FULL)
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
# STRICT KEYWORDS + EXCLUDES (very tight filtering)
# ──────────────────────────────────────────────────────────────────────────────
TELCO_KEYWORDS = [
    "oss", "bss", "billing system", "charging system", "convergent billing", "mediation",
    "revenue management", "policy control", "order management", "product catalog",
    "service fulfillment", "network orchestration", "5g monetization", "network slicing",
    "open ran oss", "api-based bss", "ai-driven assurance", "real-time charging",
    "saas telecom platform", "telecom deal", "telco partnership", "oss bss contract",
    "telecom modernization", "digital transformation", "system migration", "platform consolidation",
    "vendor replacement"
]

OTT_KEYWORDS = [
    "ott platform", "streaming service", "video streaming", "subscription video", "svod",
    "avod", "fast channels", "hybrid ott", "subscriber growth", "arpu", "churn reduction",
    "content monetization", "pricing strategy", "bundling", "super app", "content licensing",
    "sports streaming", "live streaming", "original content", "regional content",
    "multi-language ott", "content aggregation", "ott acquisition", "streaming merger",
    "content deal", "distribution partnership", "platform expansion", "market entry"
]

SPORTS_KEYWORDS = [
    "sports media rights", "broadcasting rights", "sports streaming", "live sports",
    "sports ott", "league partnership", "media rights deal", "sponsorship deal",
    "betting partnership", "fan engagement", "digital ticketing", "pay-per-view",
    "sports analytics", "fan data platform", "ai sports insights", "smart stadium",
    "ar/vr sports"
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
    "baby", "birth", "newborn", "pregnant", "wedding", "divorce", "gossip", "celebrity",
    "coupon", "discount", "sale", "promo", "voucher", "giveaway", "contest", "win free",
    "black friday", "cyber monday", "flash sale", "limited time offer", "player injury",
    "match score", "fantasy tips", "sports betting odds", "player transfers", "box office",
    "movie review", "film awards", "music album", "oil", "gas", "petroleum", "insurance",
    "banking core", "semiconductor", "chip", "mining", "power plant", "crypto", "nft"
]

# ──────────────────────────────────────────────────────────────────────────────
# RSS FEEDS (quality sources only)
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
# UTILITY FUNCTIONS - Ultra-strict filtering
# ──────────────────────────────────────────────────────────────────────────────
def clean(raw):
    if not raw: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def is_junk(title, summary=""):
    text = (title + " " + summary).lower()
    return any(ex in text for ex in JUNK_EXCLUDES)

def has_client_or_comp_or_telco(title, summary):
    text = (title + " " + summary).lower()
    
    # EVERGENT CLIENTS
    for variations in EVERGENT_CLIENTS.values():
        if any(v in text for v in variations):
            return True
    
    # COMPETITORS (extra strict for Netcracker)
    for variations in COMPETITORS.values():
        if any(v in text for v in variations):
            return True
    
    # TOP TELCOS
    for variations in TOP_TELCOS.values():
        if any(v in text for v in variations):
            return True
    
    return False

def is_section_relevant(title, summary, section):
    text = (title + " " + summary).lower()
    keywords = {
        "telco": TELCO_KEYWORDS,
        "ott": OTT_KEYWORDS,
        "sports": SPORTS_KEYWORDS,
        "technology": TECH_KEYWORDS
    }.get(section, [])
    
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
            if len(title) < 40: continue
            
            summary = clean(entry.get("summary", title))
            
            # Ultra-strict: MUST have client/competitor/telco OR section keyword
            if not (has_client_or_comp_or_telco(title, summary) or is_section_relevant(title, summary, category)):
                continue
            
            # Double-check junk
            if is_junk(title, summary): continue
            
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
# RENDER SECTION - Perfect containment & beautiful cards
# ──────────────────────────────────────────────────────────────────────────────
def render_section(icon, name, style_class, items):
    header = f'<div class="{style_class}">{icon} {name}</div>'
    
    content = ""
    if not items:
        content = '<div style="padding:140px 20px; text-align:center; color:#94a3b8; font-size:1.2rem;">No client/competitor critical news in last 7 days</div>'
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
    
    components.html(full_html, height=740, scrolling=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN APPLICATION FLOW
# ──────────────────────────────────────────────────────────────────────────────
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex; flex-direction:column; justify-content:center; align-items:center; height:70vh; text-align:center;">
            <h1 style="color:#0a192f; font-size:3.2rem; font-weight:800;">⚡ Stellar Nexus Intelligence</h1>
            <p style="color:#64748b; font-size:1.4rem; margin-top:1.2rem;">Loading ONLY client, competitor & critical business news...</p>
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

with st.spinner("Scanning high-priority sources (strict client focus)..."):
    data = load_feeds()

total = sum(len(v) for v in data.values())
st.markdown(f"""
<div class="status-bar">
    Loaded {total} high-impact articles • Last 7 days • ONLY EVERGENT clients, competitors & critical keywords
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
<div style="text-align:center; color:#94a3b8; font-size:0.95rem; margin:3.5rem 0 2rem;">
    Strictly filtered: ONLY EVERGENT clients, competitors, OSS/BSS, deals & monetization news • No promotions, no gossip • Auto-refreshes every 5 min
</div>
""", unsafe_allow_html=True)

st.markdown('<script>setTimeout(() => location.reload(), 300000);</script>', unsafe_allow_html=True)
