import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time

# ==========================
# 🔐 CEO TOKEN SECURITY GATE
# ==========================
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except:
    st.error("🔧 Missing or invalid CEO_ACCESS_TOKEN in secrets")
    st.stop()

provided_token = st.query_params.get("token")
if provided_token is not None:
    provided_token = provided_token[0] if isinstance(provided_token, list) else provided_token
else:
    provided_token = ""

if provided_token != EXPECTED_TOKEN:
    st.error("⛔ Unauthorized access – Invalid or missing token")
    st.info("Append `?token=your_token` to the URL")
    st.stop()

# Rate limiting
if "last_access" not in st.session_state:
    st.session_state.last_access = 0
if time.time() - st.session_state.last_access < 2:
    st.warning("⏱ Too many requests – Please wait.")
    st.stop()
st.session_state.last_access = time.time()

st.set_page_config(page_title="🌐 Global Telecom & OTT Stellar Nexus", page_icon="🌐", layout="wide", initial_sidebar_state="collapsed")

# ==========================
# 🎀 MAXIMUM CUTE & STUNNING PASTEL DESIGN
# ==========================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&family=Fredoka+One&display=swap" rel="stylesheet">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&family=Fredoka+One&display=swap');

    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Poppins', sans-serif;
        color: #2d3748;
        padding-top: 0.5rem;
    }

    .header-container {
        background: rgba(255, 255, 255, 0.94);
        padding: 2.5rem 1.5rem;
        text-align: center;
        border-radius: 45px;
        box-shadow: 0 18px 45px rgba(0,0,0,0.15);
        margin: 0 1.5rem 3rem 1.5rem;
        border-bottom: 12px solid #d8b4fe;
        backdrop-filter: blur(18px);
    }

    .main-title {
        font-family: 'Fredoka One', cursive;
        font-size: 3.8rem;
        color: #7c3aed;
        margin: 0;
        letter-spacing: -2px;
        text-shadow: 0 5px 10px rgba(124,58,237,0.25);
    }

    .subtitle {
        font-size: 1.6rem;
        color: #64748b;
        margin-top: 1.4rem;
        font-weight: 500;
    }

    .col-header {
        padding: 28px;
        border-radius: 40px 40px 0 0;
        color: white;
        font-family: 'Fredoka One', cursive;
        font-size: 2.2rem;
        text-align: center;
        box-shadow: 0 12px 30px rgba(0,0,0,0.22);
        text-shadow: 0 4px 10px rgba(0,0,0,0.35);
    }

    .col-header-pink { background: linear-gradient(135deg, #fecdd3, #f472b6); }
    .col-header-purple { background: linear-gradient(135deg, #e9d5ff, #a78bfa); }
    .col-header-green { background: linear-gradient(135deg, #bbf7d0, #4ade80); }
    .col-header-orange { background: linear-gradient(135deg, #fed7aa, #fb923c); }

    .col-body {
        background: white;
        border-radius: 0 0 40px 40px;
        padding: 28px;
        min-height: 620px;
        max-height: 720px;
        overflow-y: auto;
        box-shadow: 0 18px 45px rgba(0,0,0,0.15);
        margin-bottom: 3rem;
    }

    .news-card {
        background: #fdfdfb;
        border-radius: 32px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.12);
        transition: all 0.6s ease;
    }

    .news-card:hover {
        transform: translateY(-12px);
        box-shadow: 0 30px 60px rgba(167,139,250,0.4);
    }

    .news-card-priority {
        background: linear-gradient(135deg, #fffbeb, #fde68a);
        border: 6px solid #f59e0b;
        border-radius: 32px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 15px 40px rgba(251,146,60,0.35);
    }

    .news-card-priority:hover {
        transform: translateY(-15px);
        box-shadow: 0 35px 70px rgba(251,146,60,0.45);
    }

    .news-title {
        color: #5b21b6;
        font-size: 1.2rem;
        font-weight: 600;
        line-height: 1.55;
        text-decoration: none;
        display: block;
        margin-bottom: 14px;
    }

    .news-title:hover {
        color: #7c3aed;
    }

    .news-meta {
        font-size: 0.95rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 16px;
        flex-wrap: wrap;
    }

    .time-hot { color: #dc2626; font-weight: 700; font-style: italic; }
    .time-warm { color: #ea580c; font-weight: 700; }
    .time-normal { color: #64748b; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time Competitive Intelligence Dashboard ✨</p>
</div>
""", unsafe_allow_html=True)

# === RSS FEEDS (RICH & DIVERSE COVERAGE) ===
RSS_FEEDS = [
    # Telco
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("Netcracker Press", "https://rss.app/feeds/oyAS1q31oAma1iDX.xml"),
    ("Netcracker News", "https://rss.app/feeds/GxJESz3Wl0PRbyFG.xml"),
    ("Amdocs LinkedIn", "https://rss.app/feeds/rszN8UooJxRHd9RT.xml"),

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

    # Technology
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("Ars Technica", "https://arstechnica.com/rss/"),
    ("VentureBeat", "https://venturebeat.com/feed/"),
    ("ZDNet", "https://www.zdnet.com/news/rss.xml"),
    ("Engadget", "https://www.engadget.com/rss.xml"),
    ("Techmeme", "https://www.techmeme.com/feed.xml"),

    # Key Evergent OTT Clients (official)
    ("Netflix Press", "https://ir.netflix.net/resources/rss-feeds/default.aspx"),
    ("Disney Company News", "https://thewaltdisneycompany.com/feed/"),
    ("Warner Bros Discovery", "https://press.wbd.com/us/rss-feed"),
    ("Paramount Global", "https://ir.paramount.com/rss/news-releases.xml"),
    ("Peacock Press", "https://www.nbcuniversal.com/rss/peacock"),

    # Top Telcos (official)
    ("Verizon Newsroom", "https://www.verizon.com/about/news/rss"),
    ("T-Mobile News", "https://www.t-mobile.com/news/rss"),
    ("Vodafone Group", "https://www.vodafone.com/news/rss"),
    ("Deutsche Telekom", "https://www.telekom.com/en/media/rss-feed"),
    ("Bharti Airtel", "https://www.airtel.in/press-release/rss"),
    ("Reliance Jio", "https://www.jio.com/rss/news"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header-orange"},
}

SOURCE_CATEGORY_MAP = {
    "Telecoms.com": "telco", "Light Reading": "telco", "Fierce Telecom": "telco",
    "RCR Wireless": "telco", "Mobile World Live": "telco", "ET Telecom": "telco",
    "Netcracker Press": "telco", "Netcracker News": "telco", "Amdocs LinkedIn": "telco",
    "Variety": "ott", "Hollywood Reporter": "ott", "Deadline": "ott",
    "Digital TV Europe": "ott", "Advanced Television": "ott",
    "ESPN": "sports", "BBC Sport": "sports", "Front Office Sports": "sports",
    "Sportico": "sports", "SportsPro": "sports",
    "TechCrunch": "technology", "The Verge": "technology", "Wired": "technology",
    "Ars Technica": "technology", "VentureBeat": "technology", "ZDNet": "technology",
    "Engadget": "technology", "Techmeme": "technology",
    "Netflix Press": "ott", "Disney Company News": "ott", "Warner Bros Discovery": "ott",
    "Paramount Global": "ott", "Peacock Press": "ott",
    "Verizon Newsroom": "telco", "T-Mobile News": "telco", "Vodafone Group": "telco",
    "Deutsche Telekom": "telco", "Bharti Airtel": "telco", "Reliance Jio": "telco",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean(raw):
    if not raw: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def fetch_feed(source, url):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200: return items
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=7)  # Ensures content even during quiet periods
        for entry in feed.entries[:10]:
            title = clean(entry.get("title", ""))
            if len(title) < 20: continue
            summary = clean(entry.get("summary", ""))
            link = entry.get("link", "")
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try: pub = datetime(*val[:6])
                    except: pass
                    break
            if not pub or pub < CUTOFF: continue
            items.append({"title": title, "link": link, "pub": pub, "source": source, "summary": summary})
    except: pass
    items.sort(key=lambda x: x["pub"], reverse=True)
    return items[:1]  # Only the newest, most impactful from each source

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(fetch_feed, source, url) for source, url in RSS_FEEDS]
        for future in as_completed(futures):
            items = future.result()
            if items:
                item = items[0]
                category = SOURCE_CATEGORY_MAP.get(item["source"], "technology")
                categorized[category].append(item)
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1: return "Now", "time-hot"
    if hrs < 6: return f"{hrs}h", "time-hot"
    if hrs < 24: return f"{hrs}h", "time-warm"
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
        cards = '<div style="text-align:center;color:#94a3b8;padding:80px;font-size:1.4rem;">No recent news in this category yet 🌙<br><small style="font-size:1rem;">Check back soon! ♡</small></div>'
    return f'<div class="col-body">{cards}</div>'

# Loading message
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#7c3aed;margin-top:180px;font-family:\"Fredoka One\";font-size:3.2rem;'>✨ Powering up the latest insights...<br><small style='font-size:1.4rem;color:#94a3b8;'>Please wait a moment ♡</small></h2>", unsafe_allow_html=True)

with st.spinner(""):
    data = load_feeds()

placeholder.empty()

# Render dashboard
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]
for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)
