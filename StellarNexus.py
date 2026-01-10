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
    .news-title a { color: #1e40af; font-size: 0.92rem; font-weight: 600; text-decoration: none; display: block; line-height: 1.4; }
    .news-title a:hover { color: #1d4ed8; text-decoration: underline; }
    .news-meta { font-size: 0.76rem; color: #64748b; margin-top: 8px; }
    .time-hot { color: #dc2626; font-weight: 600; }
    .time-warm { color: #ea580c; font-weight: 600; }
    .time-normal { color: #64748b; }
    .empty-message { text-align: center; color: #94a3b8; padding: 30px; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Powered Intelligence • Real-Time Industry News</p>
</div>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# OPTIMIZED SEARCH PHRASES - KEY ANNOUNCEMENTS
# ────────────────────────────────────────────────
SECTION_QUERIES = {
    "telco": {
        "icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header col-header-pink",
        "phrases": [
            # Mergers & Acquisitions
            "telecom merger acquisition 2026", "OSS BSS acquisition deal", "telecom company acquisition announcement",
            "BSS vendor merger 2026", "OSS platform acquisition", "telecom M&A deal announced",
            # Major Deals & Contracts
            "OSS BSS contract win announcement", "telecom operator contract deal", "5G network contract awarded",
            "BSS platform deployment deal", "OSS implementation contract", "telecom infrastructure deal 2026",
            # Technology Launches
            "5G BSS platform launch", "cloud native OSS announcement", "AI powered BSS launch",
            "digital BSS transformation deal", "OSS automation platform", "next-gen BSS launch 2026",
            # Partnerships
            "telecom strategic partnership 2026", "OSS BSS partnership deal", "5G monetization partnership",
            "digital transformation partnership telecom", "cloud BSS partnership announced",
            # Company News
            "Amdocs announcement 2026", "Oracle Communications deal", "Ericsson OSS news",
            "Nokia BSS announcement", "Netcracker contract", "CSG Systems deal 2026"
        ]
    },
    "ott": {
        "icon": "📺", "name": "OTT & Streaming", "style": "col-header col-header-purple",
        "phrases": [
            # Platform Announcements
            "Netflix announcement 2026", "Disney+ streaming deal", "HBO Max Warner Bros announcement",
            "Paramount+ news 2026", "Amazon Prime Video deal", "Apple TV+ content announcement",
            # Business Moves
            "streaming merger acquisition 2026", "OTT platform acquisition deal", "streaming service partnership",
            "OTT bundle launch announced", "streaming price change 2026", "subscriber growth announcement",
            # Content Deals
            "streaming content deal 2026", "OTT sports rights acquisition", "exclusive content licensing deal",
            "streaming original series announcement", "movie streaming rights deal",
            # Technology
            "streaming technology launch", "OTT monetization platform", "ad-supported streaming launch 2026",
            "streaming AI personalization", "4K streaming announcement"
        ]
    },
    "sports": {
        "icon": "🏆", "name": "Sports & Events", "style": "col-header col-header-green",
        "phrases": [
            # Major Rights Deals
            "NFL broadcasting rights deal 2026", "NBA streaming contract announcement", "MLB broadcast deal",
            "Premier League rights deal 2026", "FIFA broadcasting contract", "Formula 1 media rights 2026",
            # Streaming Sports
            "sports streaming rights deal", "Amazon Prime sports announcement", "Apple TV+ sports deal 2026",
            "ESPN+ streaming rights", "sports betting partnership 2026",
            # Events & Franchises
            "Olympic broadcasting deal", "sports franchise acquisition 2026", "stadium naming rights deal",
            "sports league expansion announcement", "regional sports network deal 2026"
        ]
    },
    "technology": {
        "icon": "⚡", "name": "Technology", "style": "col-header col-header-orange",
        "phrases": [
            # AI & Innovation
            "AI announcement 2026", "ChatGPT update announcement", "Google AI deal",
            "generative AI partnership 2026", "AI chip announcement", "machine learning platform launch",
            # Cloud & Enterprise
            "AWS cloud announcement 2026", "Microsoft Azure deal", "Google Cloud contract win",
            "enterprise software acquisition", "SaaS platform funding 2026",
            # Major Tech
            "Apple product launch 2026", "Microsoft acquisition announcement", "Meta announcement",
            "Amazon announcement 2026", "Google product launch",
            # Infrastructure
            "data center expansion 2026", "semiconductor deal announcement", "5G infrastructure deployment",
            "cybersecurity acquisition 2026", "tech IPO announcement", "quantum computing breakthrough"
        ]
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def clean(raw):
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip() if raw else ""

def is_valid_article(title, pub_date):
    """Filter out 2025 articles and ensure recent news only"""
    # Exclude if title contains "2025"
    if "2025" in title:
        return False
    
    # Must be from 2026
    if pub_date.year < 2026:
        return False
    
    return True

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
                
                # Skip old articles and 2025 content
                if pub < seven_days_ago or not is_valid_article(title, pub):
                    continue
                
                items.append({
                    "title": title,
                    "link": link,
                    "pub": pub,
                    "source": "Industry News"
                })
                seen_titles.add(title)
        except:
            continue
    
    # Sort by newest first
    items.sort(key=lambda x: x["pub"], reverse=True)
    return items[:15]

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
        safe_source = html.escape(item["source"])
        
        cards += f'''<div class="news-card">
<div class="news-title"><a href="{safe_link}" target="_blank">{safe_title}</a></div>
<div class="news-meta">
<span class="{time_class}">{time_str}</span> • <span>{safe_source}</span>
</div>
</div>'''
    
    return cards

# ─── LOADING ─────────────────────────────────────
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ Igniting AI-Powered Intelligence...<br><small>Please wait a moment</small></h2>", unsafe_allow_html=True)

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
