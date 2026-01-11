import streamlit as st
import feedparser
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re
from zoneinfo import ZoneInfo
import hashlib
from difflib import SequenceMatcher

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

# ── STYLING (UNCHANGED) ────────────────────────────────────────────────────
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
    .google-section {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 15px;
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
        text-decoration: none;
    }
    .client-badge {
        background: #10b981;
        color: white;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 700;
        margin-left: 8px;
        vertical-align: middle;
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
    .separator {
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Powered Competitive Intelligence</p>
</div>
""", unsafe_allow_html=True)

# ── EVERGENT CLIENT DETECTION (minimal but effective) ───────────────────────
EVERGENT_CLIENT_KEYWORDS = {
    "astro", "sooka", "njoi",
    "shahid",
    "sonyliv", "sony liv",
    "aha video", "aha ott",
    "sky nz", "sky uk", "sky tv", "sky deutschland",
    "bbc iplayer",
    "abs-cbn",
    "rakuten viki", "viki",
    "lightbox",
    "britbox",
    "cignal", "unifi tv", "telekom malaysia",
}

def is_evergent_client_related(text):
    if not text:
        return False
    text = text.lower()
    return any(kw in text for kw in EVERGENT_CLIENT_KEYWORDS)

def get_priority_score(title, summary):
    text = (title + " " + (summary or "")).lower()
    score = 0
    if is_evergent_client_related(text):
        score += 1000
    for word in ["deal", "contract", "partnership", "expansion", "renew", "launch",
                 "migration", "acquisition", "monetization", "billion", "million"]:
        if word in text:
            score += 80
    if "evergent" in text:
        score += 250
    return score

def simple_title_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# ── RSS FEEDS & CONFIG (unchanged list) ─────────────────────────────────────
RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("The Fast Mode", "https://www.thefastmode.com/rss-feeds"),
    ("TelecomTV", "https://www.telecomtv.com/feed/"),
    ("Variety", "https://variety.com/feed/"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
    ("Deadline", "https://deadline.com/feed/"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ("Advanced Television", "https://advanced-television.com/feed/"),
    ("StreamingMedia", "https://www.streamingmedia.com/RSS/"),
    ("ESPN", "https://www.espn.com/espn/rss/news"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
    ("Front Office Sports", "https://frontofficesports.com/feed/"),
    ("Sportico", "https://www.sportico.com/feed/"),
    ("SportsPro", "https://www.sportspromedia.com/feed/"),
    ("Sports Business", "https://rss.app/feeds/qDuU3qpiuafUec6u.xml"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("Ars Technica", "https://arstechnica.com/rss/"),
    ("VentureBeat", "https://venturebeat.com/feed/"),
    ("ZDNet", "https://www.zdnet.com/news/rss.xml"),
    ("Engadget", "https://www.engadget.com/rss.xml"),
    ("Techmeme", "https://www.techmeme.com/feed.xml"),
]

GOOGLE_OSS_BSS_URL = "https://news.google.com/rss/search?q=(OSS+BSS+OR+%22operations+support+systems%22+OR+%22business+support+systems%22)+telecom+after:2025-12-01&hl=en-US&gl=US&ceid=US:en"

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header col-header-purple"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header col-header-green"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header col-header-orange"},
}

SOURCE_CATEGORY_MAP = {
    "Telecoms.com":"telco", "Light Reading":"telco", "RCR Wireless":"telco", "Mobile World Live":"telco",
    "ET Telecom":"telco", "The Fast Mode":"telco", "TelecomTV":"telco",
    "Variety":"ott", "Hollywood Reporter":"ott", "Deadline":"ott",
    "Digital TV Europe":"ott", "Advanced Television":"ott", "StreamingMedia":"ott",
    "ESPN":"sports", "BBC Sport":"sports", "Front Office Sports":"sports",
    "Sportico":"sports", "SportsPro":"sports", "Sports Business":"sports",
    "TechCrunch":"technology", "The Verge":"technology", "Wired":"technology",
    "Ars Technica":"technology", "VentureBeat":"technology", "ZDNet":"technology",
    "Engadget":"technology", "Techmeme":"technology",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ── UTILITY FUNCTIONS ──────────────────────────────────────────────────────
def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def extract_summary(entry, max_len=280):
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
    return summary

def get_article_hash(title, link):
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()

def extract_redirect_url(google_url):
    try:
        if 'google.com' in google_url and '/articles/' in google_url:
            resp = requests.get(google_url, headers=HEADERS, timeout=10, allow_redirects=True)
            return resp.url
        return google_url
    except:
        return google_url

def fetch_google_oss_bss():
    items = []
    try:
        resp = requests.get(GOOGLE_OSS_BSS_URL, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return items
        
        feed = feedparser.parse(resp.content)
        if not feed.entries:
            return items
        
        NOW = datetime.now(ZoneInfo("America/New_York"))
        cutoff = datetime(2026, 1, 1, tzinfo=ZoneInfo("America/New_York"))
        
        for entry in feed.entries:
            title = clean(entry.get("title", ""))
            if len(title) < 20: continue
            
            link = entry.get("link", "")
            if not link: continue
            
            direct_link = extract_redirect_url(link)
            summary = extract_summary(entry)
            
            pub = NOW
            if hasattr(entry, 'published_parsed'):
                try:
                    pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                except:
                    pass
            
            if pub < cutoff: continue
            
            items.append({
                "title": title,
                "link": direct_link,
                "pub": pub,
                "source": "Google OSS/BSS",
                "summary": summary,
                "hash": get_article_hash(title, direct_link),
                "score": get_priority_score(title, summary)
            })
        
        items.sort(key=lambda x: (-x["score"], -x["pub"].timestamp()))
        return items
    except:
        return []

def fetch_feed(source, url):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return items
        
        feed = feedparser.parse(resp.content)
        if not feed.entries:
            return items
        
        NOW = datetime.now(ZoneInfo("America/New_York"))
        cutoff = datetime(2026, 1, 1, tzinfo=ZoneInfo("America/New_York"))
        
        for entry in feed.entries[:12]:
            title = clean(entry.get("title", ""))
            if len(title) < 20: continue
            
            link = entry.get("link", "")
            if not link: continue
            
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
            
            if pub < cutoff: continue
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary,
                "hash": get_article_hash(title, link),
                "score": get_priority_score(title, summary)
            })
        
        return items
    except:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    seen_hashes = set()
    seen_titles = {}  # for basic semantic dedup
    
    google_items = fetch_google_oss_bss()
    
    # Process Google items
    for item in google_items:
        if item["hash"] in seen_hashes:
            continue
        cat = "telco"
        categorized[cat].append(item)
        seen_hashes.add(item["hash"])
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_feed, s, u) for s, u in RSS_FEEDS]
        
        for future in as_completed(futures):
            try:
                items = future.result()
                for item in items:
                    if item["hash"] in seen_hashes:
                        continue
                        
                    # Basic title similarity dedup
                    skip = False
                    for prev_title in seen_titles:
                        if simple_title_similarity(item["title"], prev_title) > 0.82:
                            # Keep better scored / newer
                            if item["score"] > seen_titles[prev_title]["score"] or item["pub"] > seen_titles[prev_title]["pub"]:
                                seen_titles[prev_title] = item
                            skip = True
                            break
                    
                    if skip:
                        continue
                        
                    cat = SOURCE_CATEGORY_MAP.get(item["source"], "technology")
                    categorized[cat].append(item)
                    seen_hashes.add(item["hash"])
                    seen_titles[item["title"]] = item
            except:
                pass
    
    # Final sorting: client-related first, then score, then newest
    for cat in categorized:
        categorized[cat].sort(key=lambda x: (-(10000 if is_evergent_client_related(x["title"] + " " + x.get("summary","")) else 0),
                                            -x.get("score",0),
                                            -x["pub"].timestamp()))
    
    return {
        "google_oss_bss": google_items,
        "regular": categorized
    }

def get_time_str(dt):
    now_et = datetime.now(ZoneInfo("America/New_York"))
    diff = (now_et - dt).total_seconds()
    hrs = int(diff / 3600)
    
    if hrs < 1:    return "Just now", "time-hot"
    if hrs < 6:    return f"{hrs}h ago", "time-hot"
    if hrs < 24:   return f"{hrs}h ago", "time-warm"
    days = hrs // 24
    return f"{days}d ago", "time-normal"

def render_google_section(google_items):
    if not google_items:
        return ""
    
    cards = ""
    for item in google_items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        
        is_client = is_evergent_client_related(item["title"] + " " + item.get("summary", ""))
        badge = ' <span class="client-badge">CLIENT</span>' if is_client else ""
        
        cards += f'''<div class="news-card news-card-google">
<div class="news-title">{safe_title}{badge}</div>
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>Google OSS/BSS</span>
<a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="read-more-btn">
<span class="hand-icon">👉</span> Read Full Article
</a>
</div>
</div>'''
    
    return f'''<div class="google-section">{cards}</div><div class="separator"></div>'''

def render_regular_body(items):
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_source = html.escape(item["source"])
        
        is_client = is_evergent_client_related(item["title"] + " " + item.get("summary", ""))
        badge = ' <span class="client-badge">CLIENT</span>' if is_client else ""
        
        cards += f'''<div class="news-card">
<div class="news-title">{safe_title}{badge}</div>
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
<a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="read-more-btn">
<span class="hand-icon">👉</span> Read Full Article
</a>
</div>
</div>'''
    
    if not cards:
        return '<div class="empty-message">No recent news available</div>'
    return cards

# ── MAIN LAYOUT ────────────────────────────────────────────────────────────
placeholder = st.empty()
placeholder.markdown(
    "<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>"
    "⚡ Preparing CEO Intelligence View...<br><small>Please wait</small>"
    "</h2>",
    unsafe_allow_html=True
)

with st.spinner(""):
    data = load_feeds()

placeholder.empty()

cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    
    google_section = ""
    if cat == "telco":
        google_section = render_google_section(data["google_oss_bss"])
    
    regular_items = data["regular"].get(cat, [])
    regular_cards = render_regular_body(regular_items)
    
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="col-body">{google_section}{regular_cards}</div>', unsafe_allow_html=True)

st.markdown("""
<script>
setInterval(function(){
    window.location.reload();
}, 300000);  // 5 minutes
</script>
""", unsafe_allow_html=True)
