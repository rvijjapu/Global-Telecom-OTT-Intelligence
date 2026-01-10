import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import html
import time
from zoneinfo import ZoneInfo

# Security gate (unchanged)
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except FileNotFoundError:
    st.error("Missing secrets.toml – Add CEO_ACCESS_TOKEN")
    st.stop()
except KeyError:
    st.error("CEO_ACCESS_TOKEN not found in secrets")
    st.stop()

provided_token = st.query_params.get("token", [""])[0]
if provided_token != EXPECTED_TOKEN:
    st.error("Unauthorized – Append ?token=your_token")
    st.stop()

# Rate limiting
if "last_access" not in st.session_state:
    st.session_state.last_access = 0

now = time.time()
if now - st.session_state.last_access < 2:
    st.warning("Too many requests – Wait a moment.")
    st.stop()

st.session_state.last_access = now

st.set_page_config(page_title="Global Telecom & OTT Stellar Nexus", page_icon="🌐", layout="wide")

# Original styling (unchanged)
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
    .news-title { color: #1e40af; font-size: 0.92rem; font-weight: 600; line-height: 1.35; text-decoration: none; display: block; margin-bottom: 8px; }
    .news-title:hover { color: #1d4ed8; text-decoration: underline; }
    .news-summary { color: #64748b; font-size: 0.82rem; line-height: 1.45; margin-bottom: 8px; padding-left: 8px; border-left: 3px solid #e2e8f0; }
    .news-meta { font-size: 0.76rem; color: #64748b; display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
    .time-hot { color: #dc2626; font-weight: 600; font-style: italic; }
    .time-warm { color: #ea580c; font-weight: 600; }
    .time-normal { color: #64748b; }
    .empty-message { text-align: center; color: #94a3b8; padding: 30px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("The Fast Mode", "https://www.thefastmode.com/rss-feeds"),
    ("Variety", "https://variety.com/feed/"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
    ("Deadline", "https://deadline.com/feed/"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ("Advanced Television", "https://advanced-television.com/feed/"),
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

GOOGLE_OSS_BSS_RSS = "https://news.google.com/rss/search?q=(OSS+BSS+OR+%22operations+support+systems%22+OR+%22business+support+systems%22)+telecom+after:2025-12-01&hl=en-US&gl=US&ceid=US:en"

def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def extract_summary(entry):
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and content:
                content = content[0].get('value', '')
            summary = clean(content)
            if summary:
                return summary[:160] + '...' if len(summary) > 160 else summary
    return ""

def fetch_google_news_oss_bss():
    items = []
    try:
        resp = requests.get(GOOGLE_OSS_BSS_RSS, timeout=10)
        if resp.status_code == 200:
            feed = feedparser.parse(resp.content)
            NOW = datetime.now(ZoneInfo("America/New_York"))
            seven_days_ago = NOW - timedelta(days=7)
            for entry in feed.entries:
                title = clean(entry.title or "")
                if len(title) < 15:
                    continue
                link = entry.link or ""
                if not link:
                    continue
                summary = extract_summary(entry)
                pub = None
                if 'published_parsed' in entry:
                    try:
                        pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                    except:
                        pub = NOW
                if not pub:
                    pub = NOW
                if pub >= seven_days_ago:
                    items.append({
                        "title": title,
                        "link": link,
                        "pub": pub,
                        "source": "Google News OSS/BSS",
                        "summary": summary
                    })
            items.sort(key=lambda x: x["pub"], reverse=True)
    except:
        pass
    return items

@st.cache_data(ttl=60)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    
    # Google first - ALL items
    google_items = fetch_google_news_oss_bss()
    categorized["telco"].extend(google_items)
    
    # Then regular RSS
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(lambda s, u: fetch_feed(s, u), s, u) for s, u in RSS_FEEDS]
        for future in as_completed(futures):
            try:
                source, items = future.result()
                for item in items:
                    cat = SOURCE_CATEGORY_MAP.get(source, "technology")
                    categorized[cat].append(item)
            except:
                pass
    
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
    
    return categorized

def get_time_str(dt):
    now_et = datetime.now(ZoneInfo("America/New_York"))
    hrs = int((now_et - dt).total_seconds() / 3600)
    if hrs < 1: return "Now", "time-hot"
    if hrs < 6: return f"{hrs}h ago", "time-hot"
    if hrs < 24: return f"{hrs}h ago", "time-warm"
    return f"{hrs//24}d ago", "time-normal"

def render_body(items):
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_source = html.escape(item["source"])
        safe_summary = html.escape(item.get("summary", ""))
        summary_html = f'<div class="news-summary">{safe_summary}</div>' if safe_summary else ''
        cards += f'''<div class="news-card">
<a href="{safe_link}" target="_blank" class="news-title">{safe_title}</a>
{summary_html}
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
</div>
</div>'''
    if not items:
        cards = '<div class="empty-message">No fresh news in last 7 days</div>'
    return f'<div class="col-body">{cards}</div>'

placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ Loading latest OSS/BSS intelligence...<br><small>All Google OSS/BSS first</small></h2>", unsafe_allow_html=True)

with st.spinner(""):
    data = load_feeds()

placeholder.empty()

cols = st.columns(4)
for idx, cat in enumerate(["telco", "ott", "sports", "technology"]):
    sec = SECTIONS[cat]
    items = data.get(cat, [])
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)

st.markdown("""
<script>
setTimeout(function(){ window.location.reload(); }, 300000);
</script>
""", unsafe_allow_html=True)
