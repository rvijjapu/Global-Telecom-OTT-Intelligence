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

# === MODERN & CLEAN STYLING WITH IMPROVED NEWS TITLE FONT ===
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@500;600;700&display=swap" rel="stylesheet">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@500;600;700&display=swap');

    html, body, [class*="css"]  {  
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        padding-top: 0.5rem;
    }

    .header-container {
        background: rgba(255, 255, 255, 0.92);
        padding: 1.8rem 2rem;
        text-align: center;
        border-radius: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        margin: 0 2rem 2.5rem 2rem;
        border-bottom: 5px solid #6366f1;
        backdrop-filter: blur(12px);
    }

    .main-title {
        font-family: 'Poppins', sans-serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0;
        letter-spacing: -1px;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        font-family: 'Poppins', sans-serif;
        font-size: 1.25rem;
        color: #475569;
        margin-top: 0.8rem;
        font-weight: 500;
    }

    .col-header {
        padding: 14px 20px;
        border-radius: 18px 18px 0 0;
        color: white;
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 1.05rem;
        text-align: center;
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
        letter-spacing: 0.5px;
    }

    /* Modern Gradient Headers */
    .col-header-telco { background: linear-gradient(135deg, #ec4899, #f43f5e); }
    .col-header-ott { background: linear-gradient(135deg, #a855f7, #d946ef); }
    .col-header-sports { background: linear-gradient(135deg, #10b981, #34d399); }
    .col-header-tech { background: linear-gradient(135deg, #3b82f6, #06b6d4); }

    .col-body {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 0 0 18px 18px;
        padding: 16px;
        min-height: 540px;
        max-height: 640px;
        overflow-y: auto;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        margin-bottom: 1.5rem;
        backdrop-filter: blur(8px);
    }

    .news-card {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border: none;
        border-radius: 14px;
        padding: 15px;
        margin-bottom: 12px;
        transition: all 0.4s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }

    .news-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 25px rgba(0,0,0,0.15);
        background: #ffffff;
    }

    .news-card-priority {
        background: linear-gradient(145deg, #fffbeb, #fefce8);
        border: 2px solid #f59e0b;
        border-radius: 14px;
        padding: 17px;
        margin-bottom: 14px;
        box-shadow: 0 6px 18px rgba(251, 191, 36, 0.2);
        transition: all 0.4s ease;
    }

    .news-card-priority:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 32px rgba(251, 191, 36, 0.3);
        background: #fffbeb;
    }

    /* IMPROVED MODERN NEWS TITLE */
    .news-title {
        font-family: 'Inter', sans-serif;   /* Clean, highly readable modern font */
        font-size: 1.02rem;                 /* Slightly larger for better clarity */
        font-weight: 600;                   /* Strong but not bold-overkill */
        line-height: 1.45;                  /* Improved spacing for readability */
        color: #1e293b;                     /* Deep slate for professional look */
        text-decoration: none;
        display: block;
        margin-bottom: 9px;
        transition: color 0.3s ease;
    }

    .news-title:hover {
        color: #4f46e5;                     /* Indigo accent on hover */
        text-decoration: none;              /* Clean underline removed for modern feel */
    }

    .news-meta {
        font-size: 0.80rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
        font-weight: 500;
    }

    .time-hot { color: #ef4444; font-weight: 700; }
    .time-warm { color: #f97316; font-weight: 600; }
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

# === RSS FEEDS (BUSINESS-FOCUSED OTT) ===
RSS_FEEDS = [
    # Telco (regular)
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("Subex News", "https://rss.app/feeds/nBo6830ABe1HTZ5u.xml"),
    ("OSS/BSS News", "https://rss.app/feeds/OXf4iibABnDj7t1l.xml"),
    
    # Priority Telco sources
    ("Netcracker", "https://rss.app/feeds/GxJESz3Wl0PRbyFG.xml"),
    ("Ericsson", "https://rss.app/feeds/Z6HUnDFle57Uu0hU.xml"),
    ("Telecom TV", "https://rss.app/feeds/4OeTYFrRAw7YjI6B.xml"),

    # OTT - Business & Industry Focused
    ("Variety Business", "https://variety.com/varietyvip/business/feed/"),
    ("Hollywood Reporter Business", "https://www.hollywoodreporter.com/c/business/feed/"),
    ("Deadline Business", "https://deadline.com/vip/business/feed/"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ("Advanced Television", "https://advanced-television.com/feed/"),
    ("Streaming Media", "https://www.streamingmedia.com/rss"),
    ("Netflix Press Releases", "https://ir.netflix.net/resources/rss-feeds/press-releases/rss.xml"),

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

PRIORITY_SOURCES = ["Netcracker", "Ericsson", "Telecom TV"]

# === CONTENT FILTERS ===
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
    "Subex News": "telco", "OSS/BSS News": "telco",
    "Netcracker": "telco", "Ericsson": "telco", "Telecom TV": "telco",
    "Variety Business": "ott", "Hollywood Reporter Business": "ott", "Deadline Business": "ott",
    "Digital TV Europe": "ott", "Advanced Television": "ott", "Streaming Media": "ott",
    "Netflix Press Releases": "ott",
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
            
            summary = clean(entry.get("summary", ""))
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
                "source": source,
                "summary": summary,
                "is_priority": source in PRIORITY_SOURCES
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
    
    for cat in ["ott", "sports", "technology"]:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
    
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
        
        card_class = "news-card-priority" if item.get("is_priority", False) else "news-card"
        
        cards += f'''<div class="{card_class}">
<a href="{safe_link}" target="_blank" class="news-title">{safe_title}</a>
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
</div>
</div>'''
    
    if not items or not cards:
        cards = '<div style="text-align:center;color:#94a3b8;padding:40px;font-size:1rem;">No recent news</div>'
    
    return f'<div class="col-body">{cards}</div>'

# === LOADING MESSAGE ===
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#4f46e5;margin-top:140px;font-family:\"Poppins\";font-weight:600;'>✨ Loading the latest intelligence...<br><small style='color:#64748b;'>One moment please</small></h2>", unsafe_allow_html=True)

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
