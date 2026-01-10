import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import html
import time
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed
import re

# Security gate
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except FileNotFoundError:
    st.error("🔧 Missing secrets.toml – Add CEO_ACCESS_TOKEN")
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
    st.info("Append ?token=your_token to the URL")
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
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Styling (clean, CEO-friendly)
st.markdown("""
<style>
    .stApp { background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; color: #1e293b; padding-top: 0.5rem; }
    .header-container { background: rgba(255, 255, 255, 0.95); padding: 1.2rem 1.5rem; text-align: center; border-radius: 20px; box-shadow: 0 6px 25px rgba(0,0,0,0.08); margin: 0 1.5rem 1.8rem 1.5rem; border-bottom: 4px solid #3b82f6; backdrop-filter: blur(8px); }
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
    .news-title a { color: #1e40af; font-size: 0.95rem; font-weight: 600; text-decoration: none; display: block; margin-bottom: 8px; }
    .news-title a:hover { color: #1d4ed8; text-decoration: underline; }
    .news-summary { color: #475569; font-size: 0.85rem; line-height: 1.5; margin-bottom: 10px; padding: 10px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 8px; border-left: 4px solid #3b82f6; font-weight: 500; }
    .news-meta { font-size: 0.76rem; color: #64748b; display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
    .time-hot { color: #dc2626; font-weight: 600; font-style: italic; }
    .time-warm { color: #ea580c; font-weight: 600; }
    .time-normal { color: #64748b; }
    .empty-message { text-align: center; color: #94a3b8; padding: 30px; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Driven CEO Dashboard – Key Announcements (Last 7 Days)</p>
</div>
""", unsafe_allow_html=True)

# CEO-focused search phrases (permutations that pull real data)
SECTION_QUERIES = {
    "telco": {
        "icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header col-header-pink",
        "query": "OSS BSS key announcements telecom last week OR major deals OR contracts OR mergers after:2026-01-03"
    },
    "ott": {
        "icon": "📺", "name": "OTT & Streaming", "style": "col-header col-header-purple",
        "query": "OTT streaming key announcements last week OR major deals OR content launches OR mergers after:2026-01-03"
    },
    "sports": {
        "icon": "🏆", "name": "Sports & Events", "style": "col-header col-header-green",
        "query": "sports events key announcements last week OR rights deals OR contracts OR major events after:2026-01-03"
    },
    "technology": {
        "icon": "⚡", "name": "Technology", "style": "col-header col-header-orange",
        "query": "technology key announcements last week OR major deals OR acquisitions OR AI cloud after:2026-01-03"
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

def extract_summary(entry, max_len=280):
    summary = ""
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and content:
                content = content[0].get('value', '')
            summary = clean(content)
            if summary:
                break
    if len(summary) > max_len:
        summary = summary[:max_len].rsplit(' ', 1)[0] + '...'
    return summary if summary else ""

def fetch_ai_announcements(query):
    items = []
    try:
        # Dynamic Google News RSS with CEO-focused query
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return items
        
        feed = feedparser.parse(resp.content)
        NOW = datetime.now(ZoneInfo("America/New_York"))
        seven_days_ago = NOW - timedelta(days=7)
        
        for entry in feed.entries:
            title = clean(entry.get("title", ""))
            if len(title) < 15:
                continue
            
            link = entry.get("link", "")
            if not link:
                continue
            
            summary = extract_summary(entry)
            if not summary:
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
                "summary": summary,
                "pub": pub,
                "source": "AI Search"
            })
        
        items.sort(key=lambda x: x["pub"], reverse=True)
        return items
    except Exception as e:
        st.warning(f"Search failed for '{query}': {str(e)}")
        return []

# Load AI-driven announcements for all sections
@st.cache_data(ttl=300)
def load_ai_announcements():
    categorized = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_ai_announcements, sec["query"]): cat for cat, sec in SECTION_QUERIES.items()}
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
    if hrs < 1: return "Just now"
    if hrs < 6: return f"{hrs}h ago"
    if hrs < 24: return f"{hrs}h ago"
    return f"{hrs//24}d ago"

def render_section_news(items):
    cards = ""
    for item in items:
        time_str = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_summary = html.escape(item["summary"])
        safe_source = html.escape(item["source"])
        
        title_html = f'<div class="announcement-title"><a href="{safe_link}" target="_blank">{safe_title}</a></div>'
        
        cards += f'''<div class="news-card">
{title_html}
<div class="announcement-summary">{safe_summary}</div>
<div class="announcement-meta">
<span>{time_str}</span> • <span>{safe_source}</span>
</div>
</div>'''
    
    if not cards:
        cards = '<div class="empty-message">No key announcements found in last week</div>'
    
    return cards

# === LOADING ===
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ AI-Driven CEO Dashboard Loading...<br><small>Fetching key announcements from last week</small></h2>", unsafe_allow_html=True)

with st.spinner(""):
    data = load_ai_announcements()

placeholder.empty()

# === RENDER DASHBOARD ===
cols = st.columns(4)
cat_list = list(SECTION_QUERIES.keys())

for idx, cat in enumerate(cat_list):
    sec = SECTION_QUERIES[cat]
    items = data.get(cat, [])
    news_html = render_section_news(items)
    
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="col-body">{news_html}</div>', unsafe_allow_html=True)

# Auto-refresh every 5 minutes
st.markdown("""
<script>
setTimeout(function(){
    window.location.reload();
}, 300000);
</script>
""", unsafe_allow_html=True)
