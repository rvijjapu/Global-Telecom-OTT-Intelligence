import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import html
import time

# ==========================
# 🔐 CEO TOKEN SECURITY GATE (Using Streamlit Secrets)
# ==========================
# In your GitHub repo, create a file: .streamlit/secrets.toml
# Content:
# CEO_ACCESS_TOKEN = "Vijay"   # Change to a strong random string in production!

try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except FileNotFoundError:
    st.error("🔧 Missing secrets.toml – Add CEO_ACCESS_TOKEN in .streamlit/secrets.toml or Streamlit Cloud Secrets")
    st.stop()
except KeyError:
    st.error("🔧 CEO_ACCESS_TOKEN not found in secrets")
    st.stop()

# Get token from URL query parameter: ?token=Vijay
# Handle both old and new Streamlit versions
try:
    provided_token = st.query_params.get("token", "")
    if isinstance(provided_token, list):
        provided_token = provided_token[0] if provided_token else ""
except AttributeError:
    # Fallback for older Streamlit versions
    try:
        provided_token = st.experimental_get_query_params().get("token", [""])[0]
    except:
        provided_token = ""

if provided_token != EXPECTED_TOKEN:
    st.error("⛔ Unauthorized access – Invalid or missing token")
    st.info("Append `?token=your_token` to the URL or contact admin.")
    st.stop()

# Simple rate limiting (anti-bot protection)
if "last_access" not in st.session_state:
    st.session_state.last_access = 0

now = time.time()
if now - st.session_state.last_access < 2:  # Less than 2 seconds
    st.warning("⏱ Too many requests – Please wait a moment.")
    st.stop()

st.session_state.last_access = now


st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# INSTANT LOADING MESSAGE
placeholder = st.empty()
placeholder.markdown("""
<div style="text-align:center; padding:100px 20px; background:rgba(255,255,255,0.94); border-radius:28px; margin:40px; box-shadow:0 12px 40px rgba(0,0,0,0.15);">
    <h2 style="color:#1e40af; font-size:2.8rem;">⚡⚡⚡ Powering up the latest Telecom Intelligence Insights...</h2>
    <p style="color:#475569; font-size:1.4rem; margin-top:20px;">Fetching real-time data instantly...</p>
</div>
""", unsafe_allow_html=True)

# BEAUTIFUL PURE CSS BACKGROUND - NO IMAGE, INSTANT LOAD
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 15% 85%, rgba(147, 197, 253, 0.45), transparent 45%),
        radial-gradient(circle at 85% 15%, rgba(191, 219, 254, 0.4), transparent 50%),
        radial-gradient(circle at 50% 50%, rgba(125, 211, 252, 0.3), transparent 60%),
        radial-gradient(circle at 70% 30%, rgba(99, 102, 241, 0.25), transparent 70%),
        linear-gradient(135deg, #f8fcff 0%, #eef6ff 30%, #e1efff 60%, #d4e8ff 100%);
    background-attachment: fixed;
    background-blend-mode: screen;
    color: #1e293b;
    padding-top: 0.5rem;
    position: relative;
    overflow: hidden;
}

.stApp::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    pointer-events: none;
    z-index: 0;
    background:
        radial-gradient(circle at 10% 90%, #ffffff 10px, transparent 11px),
        radial-gradient(circle at 25% 70%, #e8f0ff 14px, transparent 15px),
        radial-gradient(circle at 80% 15%, #d0e0ff 12px, transparent 13px),
        radial-gradient(circle at 60% 85%, #ffffff 16px, transparent 17px),
        radial-gradient(circle at 40% 30%, #e0eaff 13px, transparent 14px),
        radial-gradient(circle at 90% 60%, #c8d8ff 11px, transparent 12px);
    background-size: 280px 280px, 240px 240px, 300px 300px, 320px 320px, 260px 260px, 250px 250px;
    background-position: 10% 90%, 25% 70%, 80% 15%, 60% 85%, 40% 30%, 90% 60%;
    opacity: 0.35;
    animation: float-glow 60s ease-in-out infinite alternate;
}

@keyframes float-glow {
    0% { transform: translateY(0) translateX(0); opacity: 0.35; }
    100% { transform: translateY(-60px) translateX(50px); opacity: 0.45; }
}

#MainMenu, footer, header {visibility: hidden;}

.block-container { padding-top: 1rem !important; }

.header-container {
    background: rgba(255, 255, 255, 0.96);
    padding: 1.6rem;
    text-align: center;
    border-radius: 30px;
    box-shadow: 0 14px 50px rgba(0,0,0,0.15);
    margin: 1rem 2rem 2.5rem;
    border-bottom: 7px solid #3b82f6;
    backdrop-filter: blur(16px);
}

.main-title {
    font-size: 3rem;
    font-weight: 900;
    color: #1e40af;
    text-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.subtitle {
    font-size: 1.4rem;
    color: #475569;
    margin-top: 1.2rem;
}

.col-header {
    padding: 16px 20px;
    border-radius: 20px 20px 0 0;
    color: white;
    font-weight: 700;
    font-size: 1.1rem;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}

.col-header-pink { background: linear-gradient(135deg, #ec4899, #db2777); }
.col-header-purple { background: linear-gradient(135deg, #a78bfa, #8b5cf6); }
.col-header-green { background: linear-gradient(135deg, #34d399, #10b981); }
.col-header-orange { background: linear-gradient(135deg, #fb923c, #f97316); }

.col-body {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 0 0 20px 20px;
    padding: 18px;
    min-height: 560px;
    max-height: 680px;
    overflow-y: auto;
    box-shadow: 0 14px 40px rgba(0,0,0,0.18);
    margin-bottom: 2rem;
}

.news-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 16px;
    transition: all 0.3s ease;
}

.news-card:hover {
    background: #f8fafc;
    box-shadow: 0 12px 32px rgba(0,0,0,0.15);
    transform: translateY(-5px);
}

.news-card-priority {
    background: #fefce8;
    border: 2.5px solid #fbbf24;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 16px;
}

.news-card-priority:hover {
    background: #fef3c7;
    box-shadow: 0 14px 36px rgba(251,191,36,0.25);
}

.news-title {
    color: #1e40af;
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.45;
    text-decoration: none;
    display: block;
    margin-bottom: 12px;
}

.news-title:hover {
    color: #1d4ed8;
    text-decoration: underline;
}

.news-meta {
    font-size: 0.82rem;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.time-hot { color: #dc2626; font-weight: 600; font-style: italic; }
.time-warm { color: #ea580c; font-weight: 600; }
.time-normal { color: #64748b; }
</style>
""", unsafe_allow_html=True)

# TITLE
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# SEGREGATED RSS FEEDS - NO MIXING
RSS_FEEDS_TELCO = [
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("Netcracker Press", "https://rss.app/feeds/oyAS1q31oAma1iDX.xml"),
    ("Netcracker News", "https://rss.app/feeds/GxJESz3Wl0PRbyFG.xml"),
    ("Amdocs LinkedIn", "https://rss.app/feeds/rszN8UooJxRHd9RT.xml"),
]

RSS_FEEDS_OTT = [
    ("Variety", "https://variety.com/feed/"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
    ("Deadline", "https://deadline.com/feed/"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ("Advanced Television", "https://advanced-television.com/feed/"),
]

RSS_FEEDS_SPORTS = [
    ("ESPN", "https://www.espn.com/espn/rss/news"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
    ("Front Office Sports", "https://frontofficesports.com/feed/"),
    ("Sportico", "https://www.sportico.com/feed/"),
    ("SportsPro", "https://www.sportspromedia.com/feed/"),
]

RSS_FEEDS_TECHNOLOGY = [
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("Ars Technica", "https://arstechnica.com/rss/"),
    ("VentureBeat", "https://venturebeat.com/feed/"),
    ("ZDNet", "https://www.zdnet.com/news/rss.xml"),
    ("Engadget", "https://www.engadget.com/rss.xml"),
    ("Techmeme", "https://www.techmeme.com/feed.xml"),
]

# MAP TO CATEGORIES
CATEGORY_MAP = {
    "telco": RSS_FEEDS_TELCO,
    "ott": RSS_FEEDS_OTT,
    "sports": RSS_FEEDS_SPORTS,
    "technology": RSS_FEEDS_TECHNOLOGY,
}

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header-orange"},
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
        resp = requests.get(url, headers=HEADERS, timeout=5)
        if resp.status_code != 200:
            return items
        feed = feedparser.parse(resp.content)
        CUTOFF = datetime.now() - timedelta(days=3)
        for entry in feed.entries[:10]:
            title = clean(entry.get("title", ""))
            if len(title) < 20:
                continue
            summary = clean(entry.get("summary", ""))
            link = entry.get("link", "")
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6])
                    except:
                        pass
                    break
            if not pub or pub < CUTOFF:
                continue
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary
            })
    except Exception:
        pass
    return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    data = {"telco": [], "ott": [], "sports": [], "technology": []}

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for cat, feeds in CATEGORY_MAP.items():
            for source, url in feeds:
                futures.append((cat, source, executor.submit(fetch_feed, source, url)))

        for cat, source, future in futures:
            try:
                items = future.result()
                for item in items:
                    data[cat].append(item)
            except Exception:
                pass

    for cat in data:
        data[cat].sort(key=lambda x: x["pub"], reverse=True)

    return data

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
        card_class = "news-card-priority" if "netcracker" in (item["title"] + item.get("summary", "")).lower() else "news-card"
        cards += f'''<div class="{card_class}">
<a href="{safe_link}" target="_blank" class="news-title">{safe_title}</a>
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
</div>
</div>'''
    if not items:
        cards = '<div style="text-align:center;color:#94a3b8;padding:40px;">No recent news</div>'
    return f'<div class="col-body">{cards}</div>'

# FETCH & REMOVE PLACEHOLDER
with st.spinner(""):
    data = load_feeds()

placeholder.empty()

# RENDER DASHBOARD
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]
for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)
