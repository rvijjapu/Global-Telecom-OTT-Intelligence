import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re
from zoneinfo import ZoneInfo

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

# YOUR ORIGINAL STYLING - KEPT EXACTLY
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.4);
    }
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .main-subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
    }
    .col-header {
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 700;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .col-header-pink {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .col-header-purple {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .col-header-green {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    .col-header-orange {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    .news-body {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
        padding: 0.5rem;
        max-height: 75vh;
        overflow-y: auto;
    }
    .news-body::-webkit-scrollbar {
        width: 6px;
    }
    .news-body::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
    }
    .news-body::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.6);
        border-radius: 10px;
    }
    .news-card {
        background: rgba(26, 32, 44, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    .news-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        border-color: rgba(102, 126, 234, 0.5);
    }
    .news-title {
        font-size: 1rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.6rem;
        line-height: 1.4;
    }
    .news-summary {
        font-size: 0.85rem;
        color: #a0aec0;
        margin-bottom: 0.6rem;
        line-height: 1.5;
        border-left: 2px solid rgba(102, 126, 234, 0.4);
        padding-left: 0.6rem;
    }
    .news-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.8rem;
        color: #718096;
        margin-top: 0.5rem;
    }
    .news-source {
        font-weight: 600;
        color: #667eea;
    }
    .time-badge {
        padding: 0.2rem 0.5rem;
        border-radius: 5px;
        font-weight: 600;
    }
    .time-hot {
        background: rgba(255, 71, 87, 0.2);
        color: #ff4757;
    }
    .time-warm {
        background: rgba(255, 165, 2, 0.2);
        color: #ffa502;
    }
    .time-normal {
        background: rgba(160, 174, 192, 0.2);
        color: #a0aec0;
    }
    .empty-msg {
        text-align: center;
        padding: 2rem;
        color: #718096;
        font-size: 0.9rem;
    }
    .loading-box {
        background: rgba(26, 32, 44, 0.8);
        padding: 3rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
    .loading-text {
        color: #a0aec0;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# RSS FEEDS
RSS_FEEDS = [
    # Telco
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("The Fast Mode", "https://www.thefastmode.com/rss-feeds"),
    # OTT
    ("Variety", "https://variety.com/feed/"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
    ("Deadline", "https://deadline.com/feed/"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ("Advanced Television", "https://advanced-television.com/feed/"),
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

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header col-header-purple"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header col-header-green"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header col-header-orange"},
}

SOURCE_CATEGORY_MAP = {
    "Telecoms.com": "telco",
    "Light Reading": "telco",
    "Fierce Telecom": "telco",
    "RCR Wireless": "telco",
    "Mobile World Live": "telco",
    "ET Telecom": "telco",
    "The Fast Mode": "telco",
    "Variety": "ott",
    "Hollywood Reporter": "ott",
    "Deadline": "ott",
    "Digital TV Europe": "ott",
    "Advanced Television": "ott",
    "ESPN": "sports",
    "BBC Sport": "sports",
    "Front Office Sports": "sports",
    "Sportico": "sports",
    "SportsPro": "sports",
    "Sports Business": "sports",
    "TechCrunch": "technology",
    "The Verge": "technology",
    "Wired": "technology",
    "Ars Technica": "technology",
    "VentureBeat": "technology",
    "ZDNet": "technology",
    "Engadget": "technology",
    "Techmeme": "technology",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

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
    return summary if summary else "Click to read the full article"

def fetch_feed(source, url):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return items
        feed = feedparser.parse(resp.content)
        if not feed.entries:
            return items
        
        NOW = datetime.now(ZoneInfo("America/New_York"))
        today_et = NOW.date()
        yesterday_et = today_et - timedelta(days=1)
        min_date = datetime(2026, 1, 1, tzinfo=ZoneInfo("America/New_York"))
        
        for entry in feed.entries[:5]:
            title = clean(entry.get("title", ""))
            if len(title) < 15:
                continue
            link = entry.get("link", "")
            if not link:
                continue
            
            summary = extract_summary(entry)
            
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                        break
                    except:
                        pass
            if not pub:
                pub = NOW
            pub_date = pub.date()
            if pub < min_date or (pub_date != today_et and pub_date != yesterday_et):
                continue
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary
            })
        items.sort(key=lambda x: x["pub"], reverse=True)
        return items
    except:
        return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_feed, source, url) for source, url in RSS_FEEDS]
        for future in as_completed(futures):
            try:
                items = future.result()
                for item in items:
                    category = SOURCE_CATEGORY_MAP.get(item["source"], "technology")
                    categorized[category].append(item)
            except:
                pass
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
    return categorized

def get_time_str(dt):
    now_et = datetime.now(ZoneInfo("America/New_York"))
    hrs = int((now_et - dt).total_seconds() / 3600)
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
        safe_summary = html.escape(item["summary"])
        
        cards += f'''
<a href="{safe_link}" target="_blank" style="text-decoration: none;">
    <div class="news-card">
        <div class="news-title">{safe_title}</div>
        <div class="news-summary">{safe_summary}</div>
        <div class="news-footer">
            <span class="news-source">{safe_source}</span>
            <span class="time-badge {time_class}">{time_str}</span>
        </div>
    </div>
</a>
'''
    if not items:
        cards = '<div class="empty-msg">No fresh news today or yesterday (US Eastern Time)</div>'
    return f'<div class="news-body">{cards}</div>'

# HEADER
st.markdown('''
<div class="main-header">
    <div class="main-title">🌐 Global Telecom & OTT Stellar Nexus</div>
    <div class="main-subtitle">Real-time Competitive Intelligence Dashboard</div>
</div>
''', unsafe_allow_html=True)

# LOADING
placeholder = st.empty()
placeholder.markdown('<div class="loading-box"><div class="loading-text">⚡ Powering up the latest insights... Please wait a moment</div></div>', unsafe_allow_html=True)

with st.spinner(""):
    data = load_feeds()

placeholder.empty()

# RENDER COLUMNS
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
