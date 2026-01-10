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
    st.info("Use: ?token=your_token")
    st.stop()

# Rate limit
if "last_access" not in st.session_state:
    st.session_state.last_access = 0

now = time.time()
if now - st.session_state.last_access < 2:
    st.warning("⏱ Too many requests – wait a moment")
    st.stop()

st.session_state.last_access = now

st.set_page_config(page_title="Global Telecom & OTT Stellar Nexus", page_icon="🌐", layout="wide")

# ────────────────────────────────────────────────
# CLEAN CEO-FRIENDLY STYLING
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
    .news-title a { color: #1e40af; font-size: 0.95rem; font-weight: 600; text-decoration: none; display: block; }
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
    <p class="subtitle">AI-Driven CEO Dashboard – Critical News (Last 7 Days)</p>
</div>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# COMPREHENSIVE 20+ SEARCH PHRASES PER SECTION
# ────────────────────────────────────────────────
SECTION_QUERIES = {
    "telco": {
        "icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header col-header-pink",
        "phrases": [
            "OSS BSS announcement telecom",
            "operations support systems news",
            "business support systems telecom",
            "OSS BSS contract award",
            "telecom OSS BSS merger acquisition",
            "OSS BSS platform launch",
            "BSS billing system announcement",
            "OSS network management announcement",
            "telecom BSS charging system",
            "OSS orchestration announcement",
            "BSS revenue management news",
            "OSS service assurance telecom",
            "BSS customer management announcement",
            "telecom OSS automation",
            "BSS order management news",
            "OSS inventory management telecom",
            "BSS policy management announcement",
            "telecom OSS BSS vendor",
            "OSS BSS deal partnership",
            "BSS monetization platform announcement",
            "OSS BSS cloud migration",
            "telecom BSS digital transformation",
            "OSS network orchestration announcement",
            "BSS subscription management news"
        ]
    },
    "ott": {
        "icon": "📺", "name": "OTT & Streaming", "style": "col-header col-header-purple",
        "phrases": [
            "OTT streaming announcement",
            "streaming platform launch",
            "OTT content deal",
            "streaming service merger acquisition",
            "OTT video platform announcement",
            "streaming rights agreement",
            "OTT subscription announcement",
            "streaming original content deal",
            "OTT partnership announcement",
            "streaming technology announcement",
            "OTT monetization announcement",
            "streaming advertising deal",
            "OTT bundle announcement",
            "streaming expansion announcement",
            "OTT content licensing deal",
            "streaming platform upgrade",
            "OTT revenue announcement",
            "streaming user growth announcement",
            "OTT international expansion",
            "streaming content library announcement",
            "OTT pricing announcement",
            "streaming device partnership",
            "OTT distribution deal",
            "streaming quality enhancement announcement"
        ]
    },
    "sports": {
        "icon": "🏆", "name": "Sports & Events", "style": "col-header col-header-green",
        "phrases": [
            "sports rights deal announcement",
            "sports broadcasting agreement",
            "sports event announcement",
            "sports league partnership",
            "sports streaming rights deal",
            "sports sponsorship announcement",
            "sports media rights agreement",
            "sports franchise announcement",
            "sports venue deal",
            "sports technology partnership",
            "sports betting announcement",
            "sports league expansion",
            "sports broadcast contract",
            "sports digital rights deal",
            "sports team announcement",
            "sports event hosting announcement",
            "sports merchandise deal",
            "sports content distribution agreement",
            "sports international rights deal",
            "sports platform announcement",
            "sports analytics partnership",
            "sports streaming platform announcement",
            "sports event rights acquisition",
            "sports league broadcasting deal"
        ]
    },
    "technology": {
        "icon": "⚡", "name": "Technology", "style": "col-header col-header-orange",
        "phrases": [
            "technology company announcement",
            "tech merger acquisition",
            "AI artificial intelligence announcement",
            "cloud computing deal announcement",
            "software platform launch",
            "technology partnership announcement",
            "tech startup funding announcement",
            "cybersecurity deal announcement",
            "technology investment announcement",
            "tech product launch",
            "enterprise software announcement",
            "technology infrastructure deal",
            "SaaS platform announcement",
            "tech acquisition deal",
            "semiconductor technology announcement",
            "data center announcement",
            "technology expansion announcement",
            "tech collaboration partnership",
            "innovation technology announcement",
            "digital transformation deal",
            "technology solution announcement",
            "tech IPO announcement",
            "technology contract award",
            "tech platform integration announcement"
        ]
    }
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

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
            
            for entry in feed.entries[:5]:  # Top 5 per phrase
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
                
                items.append({
                    "title": title,
                    "link": link,
                    "pub": pub,
                    "source": "Google News"
                })
                seen_titles.add(title)
        except:
            continue
    
    # Sort by newest first
    items.sort(key=lambda x: x["pub"], reverse=True)
    return items[:15]  # Top 15 most recent

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
    
    if not cards:
        cards = '<div class="empty-message">No key news in last 7 days</div>'
    
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

# Auto-refresh every 5 minutes
st.markdown("""
<script>
setTimeout(function(){ window.location.reload(); }, 300000);
</script>
""", unsafe_allow_html=True)
