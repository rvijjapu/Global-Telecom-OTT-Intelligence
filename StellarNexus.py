import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import html
import time
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import hashlib

# ────────────────────────────────────────────────
# SECURITY & CONFIG
# ────────────────────────────────────────────────
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except (FileNotFoundError, KeyError):
    st.error("Missing or invalid CEO_ACCESS_TOKEN in secrets")
    st.stop()

token_param = st.query_params.get("token")
provided_token = token_param[0] if isinstance(token_param, list) and token_param else (token_param if token_param else "")

if provided_token != EXPECTED_TOKEN:
    st.error("⛔ Unauthorized – Invalid or missing token")
    st.stop()

if "last_access" not in st.session_state:
    st.session_state.last_access = 0

now = time.time()
if now - st.session_state.last_access < 2:
    st.warning("⏱ Too many requests – wait a moment")
    st.stop()

st.session_state.last_access = now

st.set_page_config(page_title="🌐 Global Telecom & OTT Stellar Nexus", page_icon="🌐", layout="wide")

# ────────────────────────────────────────────────
# CLEAN PROFESSIONAL STYLING
# ────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; color: #1e293b; padding-top: 0.5rem; }
    .header-container { background: rgba(255,255,255,0.95); padding: 1.2rem 1.5rem; text-align: center; border-radius: 20px; box-shadow: 0 6px 25px rgba(0,0,0,0.08); margin: 0 1.5rem 1.8rem 1.5rem; border-bottom: 4px solid #3b82f6; backdrop-filter: blur(8px); }
    .main-title { font-size: 2.4rem; font-weight: 800; color: #1e40af; margin: 0; letter-spacing: -0.6px; }
    .subtitle { font-size: 1.1rem; color: #475569; margin-top: 0.6rem; font-weight: 500; }
    .col-header { padding: 10px 16px; border-radius: 14px 14px 0 0; color: white; font-weight: 700; font-size: 0.95rem; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .col-header-pink { background: linear-gradient(135deg, #ec4899, #db2777); }
    .col-header-purple { background: linear-gradient(135deg, #a78bfa, #8b5cf6); }
    .col-header-green { background: linear-gradient(135deg, #34d399, #10b981); }
    .col-header-orange { background: linear-gradient(135deg, #fb923c, #f97316); }
    .col-body { background: white; border-radius: 0 0 14px 14px; padding: 12px; min-height: 520px; max-height: 620px; overflow-y: auto; box-shadow: 0 6px 20px rgba(0,0,0,0.08); margin-bottom: 1rem; }
    .news-card { background: #fafbfc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 10px; transition: all 0.3s ease; }
    .news-card:hover { background: #f1f5f9; box-shadow: 0 6px 16px rgba(0,0,0,0.08); transform: translateY(-2px); }
    .news-card-priority { background: linear-gradient(135deg, #fef3c7 0%, #fef9e7 100%); border: 2px solid #f59e0b; border-left: 5px solid #f59e0b; }
    .news-title a { color: #1e40af; font-size: 0.92rem; font-weight: 600; text-decoration: none; display: block; line-height: 1.4; }
    .news-title a:hover { color: #1d4ed8; text-decoration: underline; }
    .news-meta { font-size: 0.76rem; color: #64748b; margin-top: 8px; }
    .time-hot { color: #dc2626; font-weight: 600; }
    .time-warm { color: #ea580c; font-weight: 600; }
    .time-normal { color: #64748b; }
    .entity-tag { background: #3b82f6; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; }
    .empty-message { text-align: center; color: #94a3b8; padding: 30px; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Powered Intelligence • Evergent-Focused • Real-Time Industry News</p>
</div>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# EVERGENT ECOSYSTEM DATABASE
# ────────────────────────────────────────────────
PRIORITY_ENTITIES = [
    # Evergent Clients
    "astro", "sooka", "mongoltv", "fox sports", "fox corporation", "directv", "nba",
    "shahid", "mbc", "tv asahi", "tv3", "media prima", "abs-cbn", "viki", "rakuten viki",
    "trt", "sinclair", "fanduel", "bally sports", "gotham", "marquee sports", "sony pictures",
    "sonyliv", "aha video", "bbc", "lightbox", "sky nz", "sky uk", "cignal", "etv",
    "simpletv", "telekom malaysia", "unifi", "britbox", "quickplay",
    
    # Major Competitors
    "netcracker", "amdocs", "csg systems", "oracle communications", "ericsson", "nokia",
    "huawei", "comarch", "tecnotree", "matrixx", "optiva", "cerillion", "hansen",
    
    # Top Global Telcos
    "verizon", "at&t", "t-mobile", "comcast", "charter", "bt group", "vodafone", "orange",
    "deutsche telekom", "telefonica", "singtel", "maxis", "telstra", "china mobile",
    "ntt docomo", "softbank", "reliance jio", "airtel", "etisalat", "telus"
]

# ────────────────────────────────────────────────
# AI-OPTIMIZED SEARCH QUERIES - FOCUSED ON DEALS
# ────────────────────────────────────────────────
SECTION_QUERIES = {
    "telco": {
        "icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header col-header-pink",
        "phrases": [
            # Evergent Client Deals
            "Astro Malaysia deal announcement", "Shahid VIP partnership", "MBC Group acquisition",
            "Bally Sports streaming deal", "Sinclair Broadcast merger", "Sky streaming partnership",
            "Telekom Malaysia Unifi deal", "Britbox content partnership",
            # Competitor Deals
            "Netcracker contract win", "Amdocs acquisition deal", "CSG Systems partnership",
            "Oracle Communications BSS contract", "Ericsson OSS deal", "Nokia BSS announcement",
            # Telco Deals
            "Verizon 5G deployment deal", "AT&T network partnership", "T-Mobile merger announcement",
            "Vodafone digital transformation", "Deutsche Telekom deal", "Singtel partnership",
            "Reliance Jio acquisition", "Airtel partnership deal",
            # Technology & Products
            "5G BSS platform launch", "cloud native OSS release", "AI BSS product launch",
            "telecom billing system update", "OSS automation platform launch",
            # Financial News
            "telecom quarterly earnings", "OSS BSS revenue growth", "telecom profit announcement",
            "BSS vendor financial results", "telecom loss report"
        ]
    },
    "ott": {
        "icon": "📺", "name": "OTT & Streaming", "style": "col-header col-header-purple",
        "phrases": [
            # Platform Deals
            "Netflix content deal", "Disney+ partnership announcement", "HBO Max merger",
            "Paramount+ acquisition", "Amazon Prime Video deal", "Apple TV+ content partnership",
            # Evergent Client OTT
            "Astro Sooka content deal", "Shahid VIP exclusive content", "Viki streaming partnership",
            "Sony LIV original series", "BBC streaming deal",
            # Business Moves
            "streaming merger acquisition", "OTT platform partnership", "streaming bundle deal",
            "subscription service launch", "ad-tier streaming launch",
            # Sports & Content
            "streaming sports rights deal", "exclusive content licensing", "original series announcement",
            # Financial
            "streaming subscriber growth", "OTT revenue announcement", "streaming profit report"
        ]
    },
    "sports": {
        "icon": "🏆", "name": "Sports & Events", "style": "col-header col-header-green",
        "phrases": [
            # Major Rights
            "NFL broadcasting deal", "NBA streaming rights", "MLB broadcast contract",
            "Premier League rights deal", "FIFA broadcasting partnership", "Formula 1 media rights",
            # Streaming Sports
            "FanDuel sports betting deal", "Bally Sports partnership", "FOX Sports streaming deal",
            "ESPN+ rights acquisition", "Amazon Prime sports deal", "Apple TV+ sports partnership",
            # Franchises & Events
            "sports franchise acquisition", "stadium partnership deal", "sports league expansion",
            "Olympic broadcasting rights", "sports betting partnership",
            # Financial
            "sports rights revenue", "franchise valuation announcement", "sports deal financial terms"
        ]
    },
    "technology": {
        "icon": "⚡", "name": "Technology", "style": "col-header col-header-orange",
        "phrases": [
            # AI & Innovation
            "AI partnership deal", "machine learning acquisition", "ChatGPT enterprise deal",
            "generative AI partnership", "AI chip announcement",
            # Cloud & Enterprise
            "AWS partnership announcement", "Microsoft Azure deal", "Google Cloud contract",
            "SaaS platform acquisition", "enterprise software merger",
            # Major Tech Deals
            "Apple partnership announcement", "Microsoft acquisition deal", "Meta partnership",
            "Amazon strategic deal", "Google acquisition announcement",
            # Financial & IPO
            "tech IPO announcement", "startup funding deal", "tech acquisition price",
            "venture capital investment", "tech earnings announcement"
        ]
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def clean(raw):
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip() if raw else ""

def get_content_hash(title, link):
    """Generate unique hash for deduplication"""
    content = f"{title.lower()}{link}"
    return hashlib.md5(content.encode()).hexdigest()

def extract_priority_entity(title, link):
    """Extract priority entity (Evergent client, competitor, or telco)"""
    text = (title + " " + link).lower()
    for entity in PRIORITY_ENTITIES:
        if entity.lower() in text:
            return entity.title()
    return None

def is_valid_2026_article(title, pub_date):
    """Strict 2026 filter - no 2025 content"""
    if "2025" in title or pub_date.year < 2026:
        return False
    return True

def fetch_news_for_section(phrases):
    items = []
    seen_hashes = set()
    
    for phrase in phrases:
        try:
            url = f"https://news.google.com/rss/search?q={phrase.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                continue
            
            feed = feedparser.parse(resp.content)
            NOW = datetime.now(ZoneInfo("America/New_York"))
            seven_days_ago = NOW - timedelta(days=7)
            
            for entry in feed.entries[:3]:
                title = clean(entry.get("title", ""))
                if not title or len(title) < 15:
                    continue
                
                link = entry.get("link", "")
                if not link:
                    continue
                
                # Deduplication
                content_hash = get_content_hash(title, link)
                if content_hash in seen_hashes:
                    continue
                
                pub = NOW
                if 'published_parsed' in entry:
                    try:
                        pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                    except:
                        pass
                
                # Strict filters
                if pub < seven_days_ago or not is_valid_2026_article(title, pub):
                    continue
                
                # Extract priority entity
                priority_entity = extract_priority_entity(title, link)
                
                items.append({
                    "title": title,
                    "link": link,
                    "pub": pub,
                    "entity": priority_entity,
                    "is_priority": priority_entity is not None,
                    "hash": content_hash
                })
                seen_hashes.add(content_hash)
        except:
            continue
    
    # Sort: Priority entities first, then by date
    items.sort(key=lambda x: (not x["is_priority"], -x["pub"].timestamp()))
    return items[:20]

@st.cache_data(ttl=300)
def load_news():
    categorized = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_news_for_section, SECTION_QUERIES[cat]["phrases"]): cat for cat in SECTION_QUERIES}
        for future in as_completed(futures):
            cat = futures[future]
            try:
                categorized[cat] = future.result()
            except:
                categorized[cat] = []
    return categorized

def get_time_str(dt):
    now_et = datetime.now(ZoneInfo("America/New_York"))
    hrs = int((now_et - dt).total_seconds() / 3600)
    if hrs < 1:
        return "Just now", "time-hot"
    if hrs < 6:
        return f"{hrs}h ago", "time-hot"
    if hrs < 24:
        return f"{hrs}h ago", "time-warm"
    return f"{hrs//24}d ago", "time-normal"

def render_news(items):
    if not items:
        return '<div class="empty-message">No news in last 7 days</div>'
    
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        
        card_class = "news-card-priority" if item["is_priority"] else "news-card"
        entity_tag = f'<span class="entity-tag">{html.escape(item["entity"])}</span>' if item["entity"] else ''
        
        cards += f'''<div class="{card_class}">
<div class="news-title"><a href="{safe_link}" target="_blank">{safe_title}</a></div>
<div class="news-meta">
{entity_tag}
<span class="{time_class}">{time_str}</span>
</div>
</div>'''
    
    return cards

# ─── LOADING ─────────────────────────────────────
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ Igniting AI-Powered Intelligence...<br><small>Scanning Evergent Clients • Competitors • Global Telcos</small></h2>", unsafe_allow_html=True)

with st.spinner(""):
    data = load_news()

placeholder.empty()

# ─── RENDER ──────────────────────────────────────
cols = st.columns(4)
for idx, cat in enumerate(SECTION_QUERIES):
    sec = SECTION_QUERIES[cat]
    items = data.get(cat, [])
    news_html = render_news(items)
    
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="col-body">{news_html}</div>', unsafe_allow_html=True)

st.markdown("""
<script>
setTimeout(function(){ window.location.reload(); }, 300000);
</script>
""", unsafe_allow_html=True)
