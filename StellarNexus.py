import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import html
import time
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# ────────────────────────────────────────────────
# SECURITY & CONFIG
# ────────────────────────────────────────────────
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except (FileNotFoundError, KeyError):
    st.error("Missing or invalid CEO_ACCESS_TOKEN in secrets")
    st.stop()

token_param = st.query_params.get("token")
if isinstance(token_param, list):
    provided_token = token_param[0] if token_param else ""
else:
    provided_token = token_param if token_param else ""

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

st.set_page_config(page_title="🌐 World's #1 Telecom Intelligence Hub", page_icon="🌐", layout="wide")

# ────────────────────────────────────────────────
# PREMIUM CEO STYLING
# ────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; color: #1e293b; padding-top: 0.5rem; }
    .header-container { background: rgba(255,255,255,0.98); padding: 1.5rem 2rem; text-align: center; border-radius: 20px; box-shadow: 0 8px 35px rgba(0,0,0,0.12); margin: 0 1.5rem 2rem 1.5rem; border-bottom: 5px solid #3b82f6; backdrop-filter: blur(12px); }
    .main-title { font-size: 2.6rem; font-weight: 900; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; letter-spacing: -0.8px; }
    .subtitle { font-size: 1.15rem; color: #475569; margin-top: 0.7rem; font-weight: 600; }
    .col-header { padding: 12px 18px; border-radius: 14px 14px 0 0; color: white; font-weight: 800; font-size: 1rem; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15); text-transform: uppercase; letter-spacing: 0.5px; }
    .col-header-pink { background: linear-gradient(135deg, #ec4899, #db2777); }
    .col-header-purple { background: linear-gradient(135deg, #a78bfa, #8b5cf6); }
    .col-header-green { background: linear-gradient(135deg, #34d399, #10b981); }
    .col-header-orange { background: linear-gradient(135deg, #fb923c, #f97316); }
    .col-body { background: white; border-radius: 0 0 14px 14px; padding: 14px; min-height: 540px; max-height: 640px; overflow-y: auto; box-shadow: 0 6px 25px rgba(0,0,0,0.1); margin-bottom: 1rem; }
    .news-card { background: #fafbfc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; margin-bottom: 12px; transition: all 0.3s ease; position: relative; }
    .news-card:hover { background: #f1f5f9; box-shadow: 0 6px 20px rgba(59,130,246,0.15); transform: translateY(-3px); border-color: #3b82f6; }
    .news-card-evergent { background: linear-gradient(135deg, #fef3c7 0%, #fef9e7 100%); border: 2px solid #f59e0b; border-left: 6px solid #f59e0b; }
    .news-card-competitor { background: linear-gradient(135deg, #fee2e2 0%, #fef2f2 100%); border: 2px solid #ef4444; border-left: 6px solid #dc2626; }
    .news-card-telco { background: linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%); border: 2px solid #3b82f6; border-left: 6px solid #2563eb; }
    .news-title a { color: #1e40af; font-size: 0.97rem; font-weight: 700; text-decoration: none; display: block; line-height: 1.4; }
    .news-title a:hover { color: #1d4ed8; text-decoration: underline; }
    .news-meta { font-size: 0.78rem; color: #64748b; margin-top: 10px; display: flex; align-items: center; gap: 8px; }
    .badge { padding: 3px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
    .badge-evergent { background: #f59e0b; color: white; }
    .badge-competitor { background: #dc2626; color: white; }
    .badge-telco { background: #2563eb; color: white; }
    .time-hot { color: #dc2626; font-weight: 700; }
    .time-warm { color: #ea580c; font-weight: 700; }
    .time-normal { color: #64748b; }
    .empty-message { text-align: center; color: #94a3b8; padding: 40px; font-size: 0.95rem; }
    .stats-badge { display: inline-block; padding: 4px 10px; background: #3b82f6; color: white; border-radius: 8px; font-size: 0.75rem; font-weight: 700; margin-left: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 World's #1 Telecom Intelligence Hub</h1>
    <p class="subtitle">Evergent-Focused • Competitor Tracking • Global Telco News • Real-Time Intelligence</p>
</div>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# EVERGENT, COMPETITORS & TELCOS DATABASE
# ────────────────────────────────────────────────
EVERGENT_CLIENTS = ["astro", "mongoltv", "fox sports", "at&t", "nba", "shahid", "mbc", "tv asahi", "tv3", "abs-cbn", 
                    "viki", "trt", "sinclair", "fanduel", "bally sports", "gotham", "marquee", "sony", "aha", "bbc",
                    "lightbox", "sky", "cignal", "etv", "simpletv", "telekom malaysia", "britbox", "quickplay", "sooka", "directv"]

COMPETITORS = ["netcracker", "amdocs", "csg", "oracle communications", "ericsson", "nokia", "huawei", "comarch", 
               "tecnotree", "matrixx", "optiva", "cerillion", "asiainfo", "hansen", "openet", "zte", "mavenir"]

TOP_TELCOS = ["verizon", "at&t", "t-mobile", "comcast", "charter", "bt group", "vodafone", "o2", "orange", "deutsche telekom",
              "telefonica", "singtel", "maxis", "telstra", "optus", "china mobile", "ntt docomo", "softbank", "reliance jio",
              "airtel", "etisalat", "stc", "telus", "rogers", "bell canada", "mtn", "telekom malaysia", "spark"]

# ────────────────────────────────────────────────
# WORLD-CLASS SEARCH INTELLIGENCE
# ────────────────────────────────────────────────
SECTION_QUERIES = {
    "telco": {
        "icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header col-header-pink",
        "phrases": [
            # Evergent Clients
            "Astro Malaysia announcement", "MongolTV deal", "FOX Sports streaming", "Shahid VIP update", "MBC Group news",
            "TV Asahi announcement", "ABS-CBN streaming", "Viki Rakuten deal", "Sinclair Broadcast news", "FanDuel sports",
            "Bally Sports announcement", "Sony Pictures OTT", "BBC streaming", "Sky NZ announcement", "Cignal TV news",
            "Telekom Malaysia Unifi", "Britbox announcement", "DirectTV streaming",
            # Competitors
            "Netcracker contract win", "Amdocs BSS deal", "CSG Systems announcement", "Oracle Communications BSS",
            "Ericsson OSS deployment", "Nokia BSS contract", "Huawei BSS news", "Comarch BSS deal", "Tecnotree announcement",
            "MATRIXX Software contract", "Optiva BSS deal", "Cerillion contract win", "Hansen Technologies news",
            # Telcos
            "Verizon network announcement", "AT&T 5G deployment", "T-Mobile network", "Comcast Xfinity", "BT Group announcement",
            "Vodafone digital transformation", "Deutsche Telekom news", "Singtel announcement", "Telstra network",
            "China Mobile 5G", "NTT Docomo announcement", "Reliance Jio news", "Airtel India", "Etisalat announcement",
            # Core Topics
            "5G BSS monetization", "cloud native BSS", "AI OSS automation", "digital BSS transformation", "telecom BSS SaaS"
        ]
    },
    "ott": {
        "icon": "📺", "name": "OTT & Streaming", "style": "col-header col-header-purple",
        "phrases": [
            # Major Platforms
            "Netflix subscriber announcement", "Disney+ streaming news", "HBO Max Warner Bros", "Paramount+ announcement",
            "Peacock NBCUniversal", "Amazon Prime Video", "Apple TV+ content", "Hulu streaming", "YouTube TV announcement",
            # Evergent Client OTT
            "Astro Sooka streaming", "Shahid VIP content", "MBC streaming", "Viki streaming", "Sony LIV announcement",
            "BBC iPlayer", "Sky streaming", "Britbox content",
            # Business & Tech
            "streaming ad tier launch", "password sharing crackdown", "streaming bundle", "SVOD AVOD", "streaming price increase",
            "OTT sports rights", "streaming original content", "4K HDR streaming", "streaming technology", "OTT monetization"
        ]
    },
    "sports": {
        "icon": "🏆", "name": "Sports & Events", "style": "col-header col-header-green",
        "phrases": [
            # Major Leagues
            "NFL broadcasting rights", "NBA streaming deal", "MLB broadcast", "Premier League rights", "FIFA World Cup",
            "Formula 1 broadcast", "UEFA Champions League", "Super Bowl broadcast",
            # Streaming Sports
            "Amazon Prime sports", "Apple TV+ sports", "Peacock sports", "ESPN+ streaming", "DAZN sports rights",
            "FanDuel sports betting", "Bally Sports regional", "FOX Sports streaming",
            # Events
            "Olympic Games broadcasting", "tennis streaming rights", "golf tournament broadcast", "esports streaming"
        ]
    },
    "technology": {
        "icon": "⚡", "name": "Technology", "style": "col-header col-header-orange",
        "phrases": [
            # AI & Cloud
            "OpenAI ChatGPT announcement", "Google AI Gemini", "Microsoft Copilot", "NVIDIA AI chip", "AWS cloud announcement",
            "Microsoft Azure deal", "Google Cloud contract",
            # Major Tech
            "Apple product launch", "Google announcement", "Microsoft acquisition", "Meta announcement", "Amazon AWS",
            # Enterprise
            "cybersecurity announcement", "SaaS platform funding", "tech IPO", "semiconductor announcement", "5G infrastructure",
            "quantum computing", "edge computing", "data center expansion"
        ]
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def clean(raw):
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip() if raw else ""

def categorize_news(title, link):
    """Intelligent categorization: Evergent client, competitor, or major telco"""
    text = (title + " " + link).lower()
    
    for client in EVERGENT_CLIENTS:
        if client.lower() in text:
            return "evergent", client.title()
    
    for comp in COMPETITORS:
        if comp.lower() in text:
            return "competitor", comp.title()
    
    for telco in TOP_TELCOS:
        if telco.lower() in text:
            return "telco", telco.title()
    
    return "general", "Industry"

def fetch_news_for_section(phrases):
    items = []
    seen_titles = set()
    
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
                if not title or title in seen_titles or len(title) < 15:
                    continue
                
                link = entry.get("link", "")
                if not link:
                    continue
                
                pub = NOW
                if 'published_parsed' in entry:
                    try:
                        pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                    except:
                        pass
                
                if pub < seven_days_ago:
                    continue
                
                category, entity = categorize_news(title, link)
                
                items.append({
                    "title": title,
                    "link": link,
                    "pub": pub,
                    "category": category,
                    "entity": entity
                })
                seen_titles.add(title)
        except:
            continue
    
    # Sort: Evergent first, then competitors, then telcos, then by date
    priority = {"evergent": 0, "competitor": 1, "telco": 2, "general": 3}
    items.sort(key=lambda x: (priority.get(x["category"], 3), -x["pub"].timestamp()))
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
        return f"{hrs}h", "time-hot"
    if hrs < 24:
        return f"{hrs}h", "time-warm"
    return f"{hrs//24}d", "time-normal"

def render_news(items):
    if not items:
        return '<div class="empty-message">No news in last 7 days</div>'
    
    evergent_count = sum(1 for x in items if x["category"] == "evergent")
    competitor_count = sum(1 for x in items if x["category"] == "competitor")
    telco_count = sum(1 for x in items if x["category"] == "telco")
    
    stats = ""
    if evergent_count:
        stats += f'<span class="stats-badge">🎯 Evergent: {evergent_count}</span>'
    if competitor_count:
        stats += f'<span class="stats-badge" style="background:#dc2626">⚠️ Competitors: {competitor_count}</span>'
    if telco_count:
        stats += f'<span class="stats-badge" style="background:#2563eb">📞 Telcos: {telco_count}</span>'
    
    cards = stats
    
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_entity = html.escape(item["entity"])
        
        card_class = "news-card"
        badge_html = ""
        
        if item["category"] == "evergent":
            card_class = "news-card news-card-evergent"
            badge_html = f'<span class="badge badge-evergent">🎯 EVERGENT CLIENT</span>'
        elif item["category"] == "competitor":
            card_class = "news-card news-card-competitor"
            badge_html = f'<span class="badge badge-competitor">⚠️ COMPETITOR</span>'
        elif item["category"] == "telco":
            card_class = "news-card news-card-telco"
            badge_html = f'<span class="badge badge-telco">📞 TELCO</span>'
        
        cards += f'''<div class="{card_class}">
<div class="news-title"><a href="{safe_link}" target="_blank">{safe_title}</a></div>
<div class="news-meta">
{badge_html}
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_entity}</span>
</div>
</div>'''
    
    return cards

# ─── LOADING ─────────────────────────────────────
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ Igniting World-Class Intelligence...<br><small>Scanning Evergent Clients • Competitors • Global Telcos</small></h2>", unsafe_allow_html=True)

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
