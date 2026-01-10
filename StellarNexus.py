import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta, date
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re
from zoneinfo import ZoneInfo
import hashlib

# Security gate
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

st.markdown("""
<style>
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        color: #1e293b;
        padding-top: 0.5rem;
    }
    
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.2rem 1.5rem;
        text-align: center;
        border-radius: 20px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.08);
        margin: 0 1.5rem 1.8rem 1.5rem;
        border-bottom: 4px solid #3b82f6;
        backdrop-filter: blur(8px);
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1e40af;
        margin: 0;
        letter-spacing: -0.6px;
    }

    .subtitle {
        font-size: 1.1rem;
        color: #475569;
        margin-top: 0.6rem;
        margin-bottom: 0;
        font-weight: 500;
    }

    .col-header {
        padding: 10px 16px;
        border-radius: 14px 14px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    .col-header-pink { background: linear-gradient(135deg, #ec4899, #db2777); }
    .col-header-purple { background: linear-gradient(135deg, #a78bfa, #8b5cf6); }
    .col-header-green { background: linear-gradient(135deg, #34d399, #10b981); }
    .col-header-orange { background: linear-gradient(135deg, #fb923c, #f97316); }

    .col-body {
        background: white;
        border-radius: 0 0 14px 14px;
        padding: 12px;
        min-height: 520px;
        max-height: 620px;
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
        transform: translateY(-2px);
    }

    .news-card-google {
        background: linear-gradient(135deg, #fef3c7 0%, #fef9e7 100%);
        border: 2px solid #fbbf24;
        border-left: 5px solid #f59e0b;
    }

    .news-title {
        color: #1e40af;
        font-size: 0.92rem;
        font-weight: 600;
        line-height: 1.35;
        text-decoration: none;
        display: block;
        margin-bottom: 8px;
    }

    .news-title:hover {
        color: #1d4ed8;
        text-decoration: underline;
    }

    .news-summary {
        color: #64748b;
        font-size: 0.82rem;
        line-height: 1.45;
        margin-bottom: 8px;
        padding-left: 8px;
        border-left: 3px solid #e2e8f0;
    }

    .news-meta {
        font-size: 0.76rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 7px;
        flex-wrap: wrap;
    }

    .time-hot { color: #dc2626; font-weight: 600; font-style: italic; }
    .time-warm { color: #ea580c; font-weight: 600; }
    .time-normal { color: #64748b; }
    
    .empty-message {
        text-align: center;
        color: #94a3b8;
        padding: 30px;
    }

    .google-badge {
        background: #fbbf24;
        color: #78350f;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Powered Competitive Intelligence • All Critical News in One Place</p>
</div>
""", unsafe_allow_html=True)

# === COMPREHENSIVE RSS FEEDS ===
RSS_FEEDS = [
    # Telco & OSS/BSS (Enhanced Coverage)
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("The Fast Mode", "https://www.thefastmode.com/rss-feeds"),
    ("TelecomTV", "https://www.telecomtv.com/feed/"),
    
    # OTT & Streaming (Enhanced Coverage)
    ("Variety", "https://variety.com/feed/"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
    ("Deadline", "https://deadline.com/feed/"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ("Advanced Television", "https://advanced-television.com/feed/"),
    ("StreamingMedia", "https://www.streamingmedia.com/RSS/"),
    
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

# Google News RSS for OSS/BSS
GOOGLE_NEWS_QUERIES = [
    ("OSS BSS Telecom", "https://news.google.com/rss/search?q=(OSS+BSS+OR+%22operations+support+systems%22+OR+%22business+support+systems%22)+telecom+after:2026-01-01&hl=en-US&gl=US&ceid=US:en"),
    ("5G Network", "https://news.google.com/rss/search?q=5G+telecom+network+after:2026-01-01&hl=en-US&gl=US&ceid=US:en"),
    ("OTT Streaming", "https://news.google.com/rss/search?q=(OTT+OR+streaming+OR+%22video+platform%22)+after:2026-01-01&hl=en-US&gl=US&ceid=US:en"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header col-header-purple"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header col-header-green"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header col-header-orange"},
}

SOURCE_CATEGORY_MAP = {
    "Telecoms.com": "telco", "Light Reading": "telco", "Fierce Telecom": "telco",
    "RCR Wireless": "telco", "Mobile World Live": "telco", "ET Telecom": "telco",
    "The Fast Mode": "telco", "TelecomTV": "telco",
    "Variety": "ott", "Hollywood Reporter": "ott", "Deadline": "ott",
    "Digital TV Europe": "ott", "Advanced Television": "ott", "StreamingMedia": "ott",
    "ESPN": "sports", "BBC Sport": "sports", "Front Office Sports": "sports",
    "Sportico": "sports", "SportsPro": "sports", "Sports Business": "sports",
    "TechCrunch": "technology", "The Verge": "technology", "Wired": "technology",
    "Ars Technica": "technology", "VentureBeat": "technology", "ZDNet": "technology",
    "Engadget": "technology", "Techmeme": "technology",
    "Google News": "telco",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# AI-powered importance scoring keywords
CRITICAL_KEYWORDS = {
    "telco": ["5g", "oss", "bss", "network", "spectrum", "carrier", "wireless", "fiber", "broadband", 
              "telecom", "mvno", "mobile operator", "infrastructure", "tower", "antenna", "satellite"],
    "ott": ["streaming", "netflix", "disney", "hbo", "paramount", "peacock", "hulu", "prime video",
            "subscription", "svod", "avod", "content", "original series", "licensing", "bundle"],
    "sports": ["nfl", "nba", "mlb", "soccer", "premier league", "espn", "rights deal", "broadcast",
               "sports betting", "fantasy", "athlete", "championship", "tournament"],
    "technology": ["ai", "artificial intelligence", "machine learning", "cloud", "saas", "cybersecurity",
                   "blockchain", "quantum", "semiconductor", "chip", "startup", "venture capital"]
}

def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def calculate_importance_score(title, summary, category):
    """AI algorithm to score news importance"""
    score = 0
    text = (title + " " + summary).lower()
    
    # Keywords matching
    keywords = CRITICAL_KEYWORDS.get(category, [])
    for keyword in keywords:
        if keyword in text:
            score += 2
    
    # Title length (more detailed = more important)
    if len(title) > 60:
        score += 1
    
    # Summary availability
    if len(summary) > 50:
        score += 2
    
    # Critical terms boost
    critical_terms = ["acquisition", "merger", "partnership", "launch", "announce", "billion", 
                     "million", "breakthrough", "first", "new", "major", "strategic"]
    for term in critical_terms:
        if term in text:
            score += 3
    
    return score

def extract_summary(entry, max_len=180):
    summary = ""
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and len(content) > 0:
                content = content[0].get('value', '')
            summary = clean(content)
            if summary:
                break
    if len(summary) > max_len:
        summary = summary[:max_len].rsplit(' ', 1)[0] + '...'
    return summary if summary else ""

def get_article_hash(title, link):
    """Generate unique hash to avoid duplicates"""
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()

def fetch_google_news(query_name, url):
    """Fetch ALL Google News results (no limit)"""
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return items
        
        feed = feedparser.parse(resp.content)
        if not feed.entries:
            return items
        
        NOW = datetime.now(ZoneInfo("America/New_York"))
        cutoff_date = datetime(2026, 1, 1, tzinfo=ZoneInfo("America/New_York"))
        
        for entry in feed.entries:  # ALL entries, no limit
            try:
                title = clean(entry.get("title", ""))
                if len(title) < 15:
                    continue
                
                link = entry.get("link", "")
                if not link:
                    continue
                
                summary = extract_summary(entry, max_len=200)
                
                pub = NOW
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                    except:
                        pass
                
                if pub < cutoff_date:
                    continue
                
                items.append({
                    "title": title,
                    "link": link,
                    "pub": pub,
                    "source": "Google News",
                    "summary": summary,
                    "is_google": True,
                    "hash": get_article_hash(title, link)
                })
            except:
                continue
        
        return items
    except:
        return []

def fetch_feed(source, url):
    """Fetch RSS feed with error handling"""
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return items
       
        feed = feedparser.parse(resp.content)
        if not feed.entries:
            return items
       
        NOW = datetime.now(ZoneInfo("America/New_York"))
        cutoff_date = datetime(2026, 1, 1, tzinfo=ZoneInfo("America/New_York"))
        
        for entry in feed.entries[:10]:  # Top 10 per source
            try:
                title = clean(entry.get("title", ""))
                if len(title) < 15:
                    continue
               
                link = entry.get("link", "")
                if not link:
                    continue
                
                summary = extract_summary(entry)
               
                pub = NOW
                for k in ("published_parsed", "updated_parsed"):
                    val = getattr(entry, k, None)
                    if val:
                        try:
                            pub = datetime(*val[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                            break
                        except:
                            pass
               
                if pub < cutoff_date:
                    continue
               
                items.append({
                    "title": title,
                    "link": link,
                    "pub": pub,
                    "source": source,
                    "summary": summary,
                    "is_google": False,
                    "hash": get_article_hash(title, link)
                })
            except:
                continue
       
        return items
    except:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    seen_hashes = set()
    
    # STEP 1: Fetch ALL Google News first (highest priority)
    google_items = []
    for query_name, url in GOOGLE_NEWS_QUERIES:
        items = fetch_google_news(query_name, url)
        google_items.extend(items)
    
    # Add Google News to telco/ott
    for item in google_items:
        if item["hash"] not in seen_hashes:
            # Categorize based on title/summary
            text = (item["title"] + " " + item["summary"]).lower()
            if any(k in text for k in ["ott", "streaming", "netflix", "disney", "hbo", "video"]):
                categorized["ott"].append(item)
            else:
                categorized["telco"].append(item)
            seen_hashes.add(item["hash"])
    
    # STEP 2: Fetch regular RSS feeds
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(fetch_feed, source, url) for source, url in RSS_FEEDS]
       
        for future in as_completed(futures):
            try:
                items = future.result()
                for item in items:
                    if item["hash"] not in seen_hashes:
                        category = SOURCE_CATEGORY_MAP.get(item["source"], "technology")
                        
                        # Calculate importance score
                        score = calculate_importance_score(item["title"], item["summary"], category)
                        item["importance"] = score
                        
                        categorized[category].append(item)
                        seen_hashes.add(item["hash"])
            except:
                pass
    
    # STEP 3: Sort each category by importance + recency
    for cat in categorized:
        # Google News always first, then by importance score + recency
        categorized[cat].sort(key=lambda x: (
            not x.get("is_google", False),  # Google first
            -x.get("importance", 0),        # Then by importance
            -x["pub"].timestamp()            # Then by recency
        ))
   
    return categorized

def get_time_str(dt):
    now_et = datetime.now(ZoneInfo("America/New_York"))
    diff = (now_et - dt).total_seconds()
    hrs = int(diff / 3600)
    
    if hrs < 1:
        return "Just now", "time-hot"
    if hrs < 6:
        return f"{hrs}h ago", "time-hot"
    if hrs < 24:
        return f"{hrs}h ago", "time-warm"
    days = hrs // 24
    return f"{days}d ago", "time-normal"

def render_body(items):
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_source = html.escape(item["source"])
        safe_summary = html.escape(item.get("summary", ""))
        
        is_google = item.get("is_google", False)
        card_class = "news-card news-card-google" if is_google else "news-card"
        google_badge = '<span class="google-badge">🔍 GOOGLE</span>' if is_google else ''
        
        summary_html = f'<div class="news-summary">{safe_summary}</div>' if safe_summary else ''
       
        cards += f'''<div class="{card_class}">
<a href="{safe_link}" target="_blank" class="news-title">{safe_title}</a>
{summary_html}
<div class="news-meta">
{google_badge}
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
</div>
</div>'''
   
    if not items:
        cards = '<div class="empty-message">No news available</div>'
   
    return f'<div class="col-body">{cards}</div>'

# === LOADING ===
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ AI-Powered News Aggregation<br><small>Analyzing all sources...</small></h2>", unsafe_allow_html=True)

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

# Auto-refresh every 5 minutes
st.markdown("""
<script>
setTimeout(function(){
    window.location.reload();
}, 300000);
</script>
""", unsafe_allow_html=True)
