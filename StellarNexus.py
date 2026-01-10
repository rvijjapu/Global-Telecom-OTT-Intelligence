import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import html
import time
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
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

    .announcement-title {
        color: #1e40af;
        font-size: 0.92rem;
        font-weight: 600;
        line-height: 1.35;
        margin-bottom: 8px;
    }

    .announcement-summary {
        color: #475569;
        font-size: 0.85rem;
        line-height: 1.5;
        margin-bottom: 10px;
        padding: 10px;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        font-weight: 500;
    }

    .announcement-meta {
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
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Driven CEO Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Define CEO-focused search queries for each section
SECTIONS = {
    "telco": {
        "icon": "📡",
        "name": "Telco & OSS/BSS",
        "style": "col-header col-header-pink",
        "search_query": "key announcements OSS BSS telecom mergers acquisitions deals contracts last week CEO view"
    },
    "ott": {
        "icon": "📺",
        "name": "OTT & Streaming",
        "style": "col-header col-header-purple",
        "search_query": "key announcements OTT streaming mergers acquisitions deals contracts last week CEO view"
    },
    "sports": {
        "icon": "🏆",
        "name": "Sports & Events",
        "style": "col-header col-header-green",
        "search_query": "key announcements sports events mergers acquisitions deals contracts last week CEO view"
    },
    "technology": {
        "icon": "⚡",
        "name": "Technology",
        "style": "col-header col-header-orange",
        "search_query": "key announcements technology mergers acquisitions deals contracts last week CEO view"
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def extract_summary(entry, max_len=300):
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

def ai_summarize_news(title, summary):
    # Simple AI-like summarizer for CEO view - focus on key business impacts
    full_text = f"{title}. {summary}"
    sentences = re.split(r'[.!?]+', full_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    exec_summary = []
    for sentence in sentences[:5]:  # Top 5 sentences for summary
        if any(term in sentence.lower() for term in ["announce", "launch", "partnership", "merger", "acquisition", "deal", "contract", "billion", "million", "growth"]):
            exec_summary.append(sentence)
    
    if not exec_summary:
        return summary[:220] + "..." if len(summary) > 220 else summary
    
    result = '. '.join(exec_summary[:3])  # 3 key sentences
    return result + '.' if not result.endswith('.') else result

def fetch_ai_announcements(search_query):
    items = []
    try:
        # Use Google News RSS for dynamic fetch
        url = f"https://news.google.com/rss/search?q={search_query.replace(' ', '+')}+after:{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}&hl=en-US&gl=US&ceid=US:en"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return items
        
        feed = feedparser.parse(resp.content)
        NOW = datetime.now(ZoneInfo("America/New_York"))
        
        for entry in feed.entries:
            title = clean(entry.get("title", ""))
            if len(title) < 15:
                continue
            
            link = entry.get("link", "")
            if not link:
                continue
            
            raw_summary = extract_summary(entry)
            if not raw_summary:
                continue
            
            # AI summarize for CEO view
            exec_summary = ai_summarize_news(title, raw_summary)
            
            pub = NOW
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                except:
                    pass
            
            items.append({
                "title": title,
                "summary": exec_summary,
                "pub": pub,
                "source": "AI Search",
                "link": link  # Kept for potential use, but not displayed
            })
        
        items.sort(key=lambda x: x["pub"], reverse=True)
        return items
    except:
        return []

# Load AI-driven announcements for all sections
@st.cache_data(ttl=300, show_spinner=False)
def load_ai_announcements():
    categorized = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(fetch_ai_announcements, sec["search_query"]) for sec in SECTIONS.values()]
        for cat, future in zip(SECTIONS.keys(), futures):
            try:
                categorized[cat] = future.result()
            except:
                categorized[cat] = []
    
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

def render_announcements(items):
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_summary = html.escape(item["summary"])
        safe_source = html.escape(item["source"])
       
        cards += f'''<div class="news-card">
<div class="announcement-title">{safe_title}</div>
<div class="announcement-summary">{safe_summary}</div>
<div class="announcement-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
</div>
</div>'''
   
    if not cards:
        cards = '<div class="empty-message">No key announcements in last week</div>'
   
    return cards

# === LOADING ===
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ Loading AI-Driven Key Announcements...<br><small>Fetching CEO-level summaries for last week</small></h2>", unsafe_allow_html=True)

with st.spinner(""):
    data = load_ai_announcements()

placeholder.empty()

# === RENDER DASHBOARD ===
cols = st.columns(4)
cat_list = list(SECTIONS.keys())

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])
    news_html = render_announcements(items)
   
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
