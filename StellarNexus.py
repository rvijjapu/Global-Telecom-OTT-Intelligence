import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re

# ==========================
# 🔐 CEO TOKEN SECURITY GATE
# ==========================
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except FileNotFoundError:
    st.error("🔧 Missing secrets.toml – Add CEO_ACCESS_TOKEN in .streamlit/secrets.toml or Streamlit Cloud Secrets")
    st.stop()
except KeyError:
    st.error("🔧 CEO_ACCESS_TOKEN not found in secrets")
    st.stop()

provided_token = st.query_params.get("token")
if provided_token is not None:
    provided_token = provided_token[0] if isinstance(provided_token, list) else provided_token
else:
    provided_token = ""

if provided_token != EXPECTED_TOKEN:
    st.error("⛔ Unauthorized access – Invalid or missing token")
    st.info("Append `?token=your_token` to the URL or contact admin.")
    st.stop()

# Rate limiting
if "last_access" not in st.session_state:
    st.session_state.last_access = 0

now = time.time()
if now - st.session_state.last_access < 2:
    st.warning("⏱ Too many requests – Please wait a moment.")
    st.stop()

st.session_state.last_access = now

st.set_page_config(
    page_title="🌐 Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === ULTRA-MODERN CEO-APPROVED DASHBOARD UI ===
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap" rel="stylesheet">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    html, body, [class*="css"]  {  
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        padding-top: 0.5rem;
    }

    .header-container {
        background: rgba(255, 255, 255, 0.20);
        padding: 2.2rem 2.8rem;
        text-align: center;
        border-radius: 32px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.20);
        margin: 0 3rem 3.5rem 3rem;
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
    }

    .main-title {
        font-family: 'Manrope', sans-serif;
        font-size: 3.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1.8px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        font-family: 'Manrope', sans-serif;
        font-size: 1.4rem;
        color: #1e293b;
        margin-top: 1rem;
        font-weight: 600;
        opacity: 0.92;
    }

    .col-header {
        padding: 18px 28px;
        border-radius: 22px 22px 0 0;
        color: white;
        font-family: 'Manrope', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.28);
        letter-spacing: 1px;
        backdrop-filter: blur(12px);
    }

    .col-header-telco { background: linear-gradient(135deg, #ff6b6b, #ee5a24); }
    .col-header-ott { background: linear-gradient(135deg, #9f7aea, #da70d6); }
    .col-header-sports { background: linear-gradient(135deg, #51cf66, #40c057); }
    .col-header-tech { background: linear-gradient(135deg, #339af0, #22b8cf); }

    .col-body {
        background: rgba(255, 255, 255, 0.28);
        border-radius: 0 0 22px 22px;
        padding: 20px;
        min-height: 580px;
        max-height: 680px;
        overflow-y: auto;
        box-shadow: 0 14px 45px rgba(0,0,0,0.25);
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.35);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    .news-card {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 16px;
        transition: all 0.5s ease;
        border: 1px solid rgba(255,255,255,0.7);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }

    .news-card:hover {
        transform: translateY(-10px) scale(1.02);
        background: rgba(255, 255, 255, 0.95);
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
    }

    .news-title {
        font-family: 'Manrope', sans-serif;
        font-size: 0.98rem;
        font-weight: 700;
        line-height: 1.48;
        color: #1e293b;
        text-decoration: none;
        display: block;
        margin-bottom: 12px;
        transition: color 0.4s ease;
    }

    .news-title:hover {
        color: #6366f1;
    }

    .news-meta {
        font-size: 0.80rem;
        color: #475569;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
        font-weight: 500;
    }

    .time-hot { color: #dc2626; font-weight: 800; }
    .time-warm { color: #ea580c; font-weight: 700; }
    .time-normal { color: #64748b; }
</style>
""", unsafe_allow_html=True)

# === TITLE ===
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# === RSS FEEDS ===
RSS_FEEDS = [
    # Regular Telco sources
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("Subex News", "https://rss.app/feeds/nBo6830ABe1HTZ5u.xml"),
    ("OSS/BSS News", "https://rss.app/feeds/OXf4iibABnDj7t1l.xml"),
    ("The Fast Mode", "https://www.thefastmode.com/rss-feeds"),

    # Priority Telco sources – always pinned at top (4 sources)
    ("Netcracker", "https://rss.app/feeds/GxJESz3Wl0PRbyFG.xml"),
    ("Ericsson", "https://rss.app/feeds/Z6HUnDFle57Uu0hU.xml"),
    ("Telecom TV", "https://rss.app/feeds/4OeTYFrRAw7YjI6B.xml"),
    ("Amdocs", "https://rss.app/feeds/E9xROIQmdwZQP7YN.xml"),

    # OTT Business-focused sources
    ("Variety Business", "https://variety.com/varietyvip/business/feed/"),
    ("Hollywood Reporter Business", "https://www.hollywoodreporter.com/c/business/feed/"),
    ("Deadline Business", "https://deadline.com/vip/business/feed/"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ("Advanced Television", "https://advanced-television.com/feed/"),
    ("Streaming Media", "https://www.streamingmedia.com/rss"),
    ("Netflix Press Releases", "https://ir.netflix.net/resources/rss-feeds/press-releases/rss.xml"),
    ("VideoNuze", "https://www.videonuze.com/atom"),
    ("nScreenMedia", "https://nscreenmedia.com/feed/"),
    ("Fierce Video", "https://www.fierce-network.com/rss.xml"),

    # Sports
    ("ESPN", "https://www.espn.com/espn/rss/news"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
    ("Front Office Sports", "https://frontofficesports.com/feed/"),
    ("Sportico", "https://www.sportico.com/feed/"),
    ("SportsPro", "https://www.sportspromedia.com/feed/"),
    ("Sports Business", "https://rss.app/feeds/qDuU3qpiuafUec6u.xml"),

    # Technology
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("Ars Technica", "https://arstechnica.com/rss/"),
    ("VentureBeat", "https://venturebeat.com/feed/"),
    ("ZDNet", "https://www.zdnet.com/news/rss.xml"),
    ("Engadget", "https://www.engadget.com/rss.xml"),
    ("Techmeme", "https://www.techmeme.com/feed.xml"),
]

# 4 Priority sources – always at the top of Telco column
PRIORITY_SOURCES = ["Netcracker", "Ericsson", "Telecom TV", "Amdocs"]

# Content filters
BAD_WORDS = ["sex", "sexual", "nude", "nudity", "porn", "orgasm", "erotic", "anal", "bdsm",
             "fetish", "xxx", "adult", "explicit", "nc-17", "full frontal", "oral sex",
             "vagina", "penis", "boobs", "tits", "ass", "fuck", "fisting", "facials"]

OTT_IRRELEVANT_WORDS = ["trailer", "teaser", "preview", "episode", "season", "recap", "review", "spoiler",
                        "watch now", "streaming now", "new episode", "binge", "series premiere", "finale"]

BAD_PATTERN = re.compile(r'\b(' + '|'.join(re.escape(word) for word in BAD_WORDS) + r')\b', re.IGNORECASE)
OTT_IRRELEVANT_PATTERN = re.compile(r'\b(' + '|'.join(re.escape(word) for word in OTT_IRRELEVANT_WORDS) + r')\b', re.IGNORECASE)

def is_inappropriate(title):
    return bool(BAD_PATTERN.search(title))

def is_ott_irrelevant(title):
    return bool(OTT_IRRELEVANT_PATTERN.search(title.lower()))

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header col-header-telco"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header col-header-ott"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header col-header-sports"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header col-header-tech"},
}

SOURCE_CATEGORY_MAP = {
    "Telecoms.com": "telco", "Light Reading": "telco", "Fierce Telecom": "telco",
    "RCR Wireless": "telco", "Mobile World Live": "telco", "ET Telecom": "telco",
    "Subex News": "telco", "OSS/BSS News": "telco", "The Fast Mode": "telco",
    "Netcracker": "telco", "Ericsson": "telco", "Telecom TV": "telco", "Amdocs": "telco",
    "Variety Business": "ott", "Hollywood Reporter Business": "ott", "Deadline Business": "ott",
    "Digital TV Europe": "ott", "Advanced Television": "ott", "Streaming Media": "ott",
    "Netflix Press Releases": "ott", "VideoNuze": "ott", "nScreenMedia": "ott", "Fierce Video": "ott",
    "ESPN": "sports", "BBC Sport": "sports", "Front Office Sports": "sports",
    "Sportico": "sports", "SportsPro": "sports", "Sports Business": "sports",
    "TechCrunch": "technology", "The Verge": "technology", "Wired": "technology",
    "Ars Technica": "technology", "VentureBeat": "technology", "ZDNet": "technology",
    "Engadget": "technology", "Techmeme": "technology",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def fetch_feed(source, url):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return items
        
        feed = feedparser.parse(resp.content)
        if not feed.entries:
            return items
        
        NOW = datetime.now()
        cutoff_days = 7 if source in PRIORITY_SOURCES else 15
        CUTOFF = NOW - timedelta(days=cutoff_days)
        
        for entry in feed.entries[:15]:
            title = clean(entry.get("title", ""))
            if len(title) < 15 or is_inappropriate(title):
                continue
            
            source_category = SOURCE_CATEGORY_MAP.get(source, "")
            if source_category == "ott" and is_ott_irrelevant(title):
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
            
            if not pub:
                pub = NOW
            
            if pub < CUTOFF:
                continue
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source
            })
        
        items.sort(key=lambda x: x["pub"], reverse=True)
        return items[:1]
        
    except Exception:
        return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    priority_items = []
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_feed, source, url) for source, url in RSS_FEEDS]
        
        for future in as_completed(futures):
            try:
                items = future.result()
                for item in items:
                    category = SOURCE_CATEGORY_MAP.get(item["source"], "technology")
                    if item["source"] in PRIORITY_SOURCES:
                        priority_items.append(item)
                    else:
                        categorized[category].append(item)
            except:
                pass
    
    # Sort non-telco categories
    for cat in ["ott", "sports", "technology"]:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
    
    # Priority pinning: 4 sources always at top of telco (latest first)
    ordered_priority = []
    for src in PRIORITY_SOURCES:
        src_items = [it for it in priority_items if it["source"] == src]
        if src_items:
            ordered_priority.append(max(src_items, key=lambda x: x["pub"]))
    
    ordered_priority.sort(key=lambda x: x["pub"], reverse=True)
    
    regular_telco = categorized["telco"]
    regular_telco.sort(key=lambda x: x["pub"], reverse=True)
    
    categorized["telco"] = ordered_priority + regular_telco
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1:
        return "Now", "time-hot"
    if hrs < 6:
        return f"{hrs}h", "time-hot"
    if hrs < 24:
        return f"{hrs}h", "time-warm"
    return f"{hrs//24}d", "time-normal"

def render_body(items):
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_source = html.escape(item["source"])
        
        # All cards use the same clean, uniform style – no priority highlight
        cards += f'''<div class="news-card">
<a href="{safe_link}" target="_blank" class="news-title">{safe_title}</a>
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
</div>
</div>'''
    
    if not items:
        cards = '<div style="text-align:center;color:#64748b;padding:70px;font-size:1rem;">No recent news</div>'
    
    return f'<div class="col-body">{cards}</div>'

# === LOADING MESSAGE ===
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#4338ca;margin-top:160px;font-family:\"Manrope\";font-weight:700;'>✨ Igniting the future of intelligence...<br><small style='color:#64748b;'>Preparing your nexus</small></h2>", unsafe_allow_html=True)

with st.spinner(""):
    data = load_feeds()

placeholder.empty()

# === RENDER DASHBOARD ===
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])
    
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)
