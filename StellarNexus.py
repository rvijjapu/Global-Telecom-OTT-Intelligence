import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re
from zoneinfo import ZoneInfo
import hashlib

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
    page_title="🌐 Global Telecom & OTT Intelligence Hub 2026",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Auto-refresh configuration
AUTO_REFRESH_INTERVAL = 300  # 5 minutes in seconds

# Enhanced styling with modern 2026 design trends
st.markdown("""
<style>
    /* Global Variables */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --telco-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --ott-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --sports-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --tech-gradient: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        --dark-bg: #0f1419;
        --card-bg: #1a1f2e;
        --text-primary: #e4e6eb;
        --text-secondary: #8b92a8;
        --border-color: #2d3748;
    }
    
    /* Reset and Base */
    .stApp {
        background: var(--dark-bg);
        color: var(--text-primary);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Dashboard Header */
    .dashboard-header {
        background: var(--primary-gradient);
        padding: 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        text-align: center;
    }
    
    .dashboard-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    .dashboard-subtitle {
        font-size: 1.1rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    /* Section Headers */
    .section-header {
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        font-size: 1.3rem;
        font-weight: 700;
        color: white;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        position: sticky;
        top: 0;
        z-index: 10;
    }
    
    .section-telco { background: var(--telco-gradient); }
    .section-ott { background: var(--ott-gradient); }
    .section-sports { background: var(--sports-gradient); }
    .section-tech { background: var(--tech-gradient); }
    
    /* News Cards Container */
    .news-container {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        padding: 0.5rem;
        max-height: calc(100vh - 280px);
        overflow-y: auto;
    }
    
    .news-container::-webkit-scrollbar {
        width: 6px;
    }
    
    .news-container::-webkit-scrollbar-track {
        background: var(--dark-bg);
    }
    
    .news-container::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 3px;
    }
    
    /* Enhanced News Card with Summary */
    .news-card {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    
    .news-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary-gradient);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .news-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .news-card:hover::before {
        transform: scaleX(1);
    }
    
    /* Breaking/Hot News Indicator */
    .news-card.breaking {
        border-left: 4px solid #ff4757;
        background: linear-gradient(135deg, rgba(255,71,87,0.1) 0%, var(--card-bg) 100%);
    }
    
    .news-card.breaking .news-title::before {
        content: '🔥 ';
    }
    
    /* News Title */
    .news-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    /* News Summary */
    .news-summary {
        font-size: 0.9rem;
        color: var(--text-secondary);
        line-height: 1.6;
        margin-bottom: 0.75rem;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        border-left: 3px solid var(--border-color);
        padding-left: 0.75rem;
    }
    
    /* Metadata Bar */
    .news-meta {
        display: flex;
        align-items: center;
        gap: 1rem;
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-top: 0.75rem;
    }
    
    .news-source {
        font-weight: 600;
        color: #667eea;
    }
    
    .news-time {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .time-badge {
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        font-size: 0.75rem;
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
        background: rgba(139, 146, 168, 0.2);
        color: var(--text-secondary);
    }
    
    /* Read More Button */
    .read-more {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-top: 0.5rem;
        color: #667eea;
        font-size: 0.85rem;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    
    .read-more:hover {
        color: #764ba2;
        gap: 0.75rem;
    }
    
    /* Empty State */
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: var(--text-secondary);
        background: var(--card-bg);
        border-radius: 12px;
        border: 2px dashed var(--border-color);
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    /* Loading State */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 4rem 2rem;
        background: var(--card-bg);
        border-radius: 16px;
        margin: 2rem 0;
    }
    
    .loading-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid var(--border-color);
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        margin-top: 1.5rem;
        font-size: 1.1rem;
        color: var(--text-secondary);
    }
    
    /* Stats Bar */
    .stats-bar {
        display: flex;
        gap: 1rem;
        justify-content: space-around;
        background: var(--card-bg);
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: var(--text-secondary);
        margin-top: 0.25rem;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .dashboard-title {
            font-size: 1.8rem;
        }
        
        .news-card {
            padding: 1rem;
        }
        
        .news-title {
            font-size: 0.95rem;
        }
        
        .stats-bar {
            flex-wrap: wrap;
        }
    }
</style>
""", unsafe_allow_html=True)

# Enhanced RSS feeds with better sources for 2026
RSS_FEEDS = [
    # Telco & OSS/BSS
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("The Fast Mode", "https://www.thefastmode.com/rss-feeds"),
    ("TelecomTV", "https://www.telecomtv.com/feed/"),
    
    # OTT & Streaming
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

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "section-telco"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "section-ott"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "section-sports"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "section-tech"},
}

SOURCE_CATEGORY_MAP = {
    "Telecoms.com": "telco",
    "Light Reading": "telco",
    "Fierce Telecom": "telco",
    "RCR Wireless": "telco",
    "Mobile World Live": "telco",
    "ET Telecom": "telco",
    "The Fast Mode": "telco",
    "TelecomTV": "telco",
    "Variety": "ott",
    "Hollywood Reporter": "ott",
    "Deadline": "ott",
    "Digital TV Europe": "ott",
    "Advanced Television": "ott",
    "StreamingMedia": "ott",
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

def extract_summary(entry, max_length=200):
    """Extract and clean summary from feed entry"""
    summary = ""
    
    # Try different summary fields
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and len(content) > 0:
                content = content[0].get('value', '')
            summary = clean(content)
            if summary:
                break
    
    # Truncate to max length with ellipsis
    if len(summary) > max_length:
        summary = summary[:max_length].rsplit(' ', 1)[0] + '...'
    
    return summary if summary else "Click to read full article"

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
        
        for entry in feed.entries[:8]:  # Get more entries for better coverage
            title = clean(entry.get("title", ""))
            if len(title) < 15:
                continue
            
            link = entry.get("link", "")
            if not link:
                continue
            
            # Extract summary
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
            
            # Only today or yesterday in US ET, no 2025
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

@st.cache_data(ttl=300, show_spinner=False)  # 5 minute cache
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

def get_time_info(dt):
    now_et = datetime.now(ZoneInfo("America/New_York"))
    diff = (now_et - dt).total_seconds()
    hrs = int(diff / 3600)
    mins = int(diff / 60)
    
    if mins < 30:
        return "Just now", "time-hot", True
    elif hrs < 6:
        return f"{hrs}h ago", "time-hot", True
    elif hrs < 24:
        return f"{hrs}h ago", "time-warm", False
    else:
        return f"{hrs//24}d ago", "time-normal", False

def render_news_card(item):
    time_str, time_class, is_breaking = get_time_info(item["pub"])
    safe_title = html.escape(item["title"])
    safe_link = html.escape(item["link"])
    safe_source = html.escape(item["source"])
    safe_summary = html.escape(item["summary"])
    
    breaking_class = "breaking" if is_breaking else ""
    
    return f"""
    <div class="news-card {breaking_class}">
        <div class="news-title">{safe_title}</div>
        <div class="news-summary">{safe_summary}</div>
        <div class="news-meta">
            <span class="news-source">{safe_source}</span>
            <span class="news-time">
                <span class="time-badge {time_class}">{time_str}</span>
            </span>
        </div>
        <a href="{safe_link}" target="_blank" class="read-more">
            Read full article →
        </a>
    </div>
    """

def render_section(items, section_key):
    sec = SECTIONS[section_key]
    
    if not items:
        return f"""
        <div class="section-header {sec['style']}">
            {sec['icon']} {sec['name']}
        </div>
        <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <div>No fresh news in the last 24 hours</div>
        </div>
        """
    
    cards_html = "".join([render_news_card(item) for item in items[:10]])  # Show top 10
    
    return f"""
    <div class="section-header {sec['style']}">
        {sec['icon']} {sec['name']} <span style="opacity: 0.7; font-size: 0.9rem; margin-left: auto;">({len(items)} stories)</span>
    </div>
    <div class="news-container">
        {cards_html}
    </div>
    """

# Header
st.markdown("""
<div class="dashboard-header">
    <div class="dashboard-title">🌐 Global Intelligence Hub 2026</div>
    <div class="dashboard-subtitle">Real-time competitive intelligence across Telecom, OTT, Sports & Technology</div>
</div>
""", unsafe_allow_html=True)

# Loading state
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
    <div class="loading-container">
        <div class="loading-spinner"></div>
        <div class="loading-text">⚡ Aggregating latest insights from 28 premium sources...</div>
    </div>
    """, unsafe_allow_html=True)

# Load data
with st.spinner(""):
    data = load_feeds()

placeholder.empty()

# Calculate stats
total_stories = sum(len(data[cat]) for cat in data)
breaking_count = sum(1 for cat in data for item in data[cat] if get_time_info(item["pub"])[2])
sources_active = len(set(item["source"] for cat in data for item in data[cat]))

# Stats bar
st.markdown(f"""
<div class="stats-bar">
    <div class="stat-item">
        <div class="stat-value">{total_stories}</div>
        <div class="stat-label">Total Stories</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">{breaking_count}</div>
        <div class="stat-label">Breaking News</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">{sources_active}</div>
        <div class="stat-label">Active Sources</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">{datetime.now(ZoneInfo('America/New_York')).strftime('%I:%M %p')}</div>
        <div class="stat-label">Last Updated (ET)</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Render columns
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    with cols[idx]:
        st.markdown(render_section(data[cat], cat), unsafe_allow_html=True)

# Auto-refresh script
st.markdown(f"""
<script>
    setTimeout(function(){{
        window.location.reload();
    }}, {AUTO_REFRESH_INTERVAL * 1000});
</script>
""", unsafe_allow_html=True)

# Footer with refresh info
st.markdown(f"""
<div style="text-align: center; margin-top: 2rem; padding: 1rem; color: var(--text-secondary); font-size: 0.85rem;">
    Auto-refresh every {AUTO_REFRESH_INTERVAL//60} minutes • Last refresh: {datetime.now(ZoneInfo('America/New_York')).strftime('%I:%M:%S %p ET')}
</div>
""", unsafe_allow_html=True)
