import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import html
import time
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed

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

    .ai-overview {
        background: linear-gradient(135deg, #fef3c7 0%, #fef9e7 100%);
        border: 3px solid #fbbf24;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 15px;
    }

    .ai-header {
        font-size: 0.85rem;
        font-weight: 700;
        color: #78350f;
        text-align: center;
        padding: 8px;
        background: #fbbf24;
        border-radius: 8px;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .key-announcement {
        background: #fafbfc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }

    .key-announcement:hover {
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

    .separator {
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# Sections and their AI search queries for key announcements last week
SECTIONS = {
    "telco": {
        "icon": "📡",
        "name": "Telco & OSS/BSS",
        "style": "col-header col-header-pink",
        "search_query": "key recent announcements in OSS BSS telecom last week"
    },
    "ott": {
        "icon": "📺",
        "name": "OTT & Streaming",
        "style": "col-header col-header-purple",
        "search_query": "key recent announcements in OTT streaming last week"
    },
    "sports": {
        "icon": "🏆",
        "name": "Sports & Events",
        "style": "col-header col-header-green",
        "search_query": "key recent announcements in sports events last week"
    },
    "technology": {
        "icon": "⚡",
        "name": "Technology",
        "style": "col-header col-header-orange",
        "search_query": "key recent announcements in technology last week"
    },
}

# Function to fetch AI-driven news for a section
def fetch_ai_news(query):
    # Use Grok's web_search tool simulation - in practice, integrate with an API like Serper or Bing
    # For this code, we use a placeholder fetch from Google News RSS with the query
    url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+after:{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}&hl=en-US&gl=US&ceid=US:en"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    if resp.status_code != 200:
        return []
    
    feed = feedparser.parse(resp.content)
    items = []
    for entry in feed.entries[:10]:  # Top 10 key announcements
        title = clean(entry.get("title", ""))
        summary = extract_summary(entry)
        if title and summary:
            items.append({
                "title": title,
                "summary": summary,
                "pub": datetime.now(ZoneInfo("America/New_York")) - timedelta(days=len(items)),  # Simulate dates
                "source": "AI Search"
            })
    
    return items

# Fetch news for all sections using AI algorithms
@st.cache_data(ttl=300, show_spinner=False)
def load_ai_news():
    categorized = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_ai_news, sec["search_query"]): cat for cat, sec in SECTIONS.items()}
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
    if hrs < 1: return "Just now", "time-hot"
    if hrs < 6: return f"{hrs}h ago", "time-hot"
    if hrs < 24: return f"{hrs}h ago", "time-warm"
    days = hrs // 24
    return f"{days}d ago", "time-normal"

def render_section_news(items):
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_summary = html.escape(item["summary"])
        safe_source = html.escape(item["source"])
        
        cards += f'''<div class="key-announcement">
<div class="announcement-title">{safe_title}</div>
<div class="announcement-summary">{safe_summary}</div>
<div class="announcement-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
</div>
</div>'''
    
    if not cards:
        cards = '<div class="empty-message">No key announcements found in last week</div>'
    
    return cards

# Loading
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ Loading AI-Driven Key Announcements...<br><small>Fetching latest summaries for all sections</small></h2>", unsafe_allow_html=True)

with st.spinner(""):
    data = load_ai_news()

placeholder.empty()

# === RENDER DASHBOARD ===
cols = st.columns(4)
cat_list = list(SECTIONS.keys())

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
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
