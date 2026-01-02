import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re

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

st.set_page_config(
    page_title="🌐 Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================
# 🎀 MAXIMUM CUTE & STUNNING PASTEL DESIGN
# ==========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #ffeef8 0%, #e8f4ff 50%, #fff5e6 100%);
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 50%, #ffecd2 100%);
        border-radius: 25px;
        box-shadow: 0 15px 40px rgba(255, 154, 158, 0.3);
        margin-bottom: 2rem;
        animation: fadeIn 0.8s ease-in;
    }
    
    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #ff6b9d, #c06c84, #f67280);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        text-shadow: 2px 2px 10px rgba(255, 107, 157, 0.2);
    }
    
    .main-header p {
        color: #6a4c93;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 300;
    }
    
    .col-header {
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        color: white;
    }
    
    .col-header-pink {
        background: linear-gradient(135deg, #ff9a9e, #fecfef);
    }
    
    .col-header-purple {
        background: linear-gradient(135deg, #a18cd1, #fbc2eb);
    }
    
    .col-header-green {
        background: linear-gradient(135deg, #84fab0, #8fd3f4);
    }
    
    .col-header-orange {
        background: linear-gradient(135deg, #ffd89b, #19547b);
    }
    
    .news-card, .news-card-priority {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border-left: 4px solid #ffc3a0;
    }
    
    .news-card-priority {
        border-left: 5px solid #ff6b9d;
        background: linear-gradient(135deg, #fff5f7 0%, #ffe5ec 100%);
        box-shadow: 0 8px 25px rgba(255, 107, 157, 0.2);
    }
    
    .news-card:hover, .news-card-priority:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(255, 107, 157, 0.3);
    }
    
    .card-title {
        font-size: 1.05rem;
        font-weight: 600;
        color: #2d3436;
        line-height: 1.5;
        margin-bottom: 0.8rem;
        display: block;
        text-decoration: none;
    }
    
    .card-title:hover {
        color: #ff6b9d;
    }
    
    .card-meta {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: #636e72;
    }
    
    .time-hot {
        background: linear-gradient(135deg, #ff6b9d, #f67280);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 8px;
        font-weight: 600;
    }
    
    .time-warm {
        background: linear-gradient(135deg, #ffa502, #ff6348);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 8px;
        font-weight: 600;
    }
    
    .time-normal {
        background: #dfe6e9;
        color: #2d3436;
        padding: 0.2rem 0.6rem;
        border-radius: 8px;
        font-weight: 500;
    }
    
    .empty-state {
        text-align: center;
        padding: 3rem 1rem;
        color: #b2bec3;
        font-size: 1.1rem;
    }
    
    .loading-msg {
        text-align: center;
        padding: 3rem;
        font-size: 1.3rem;
        color: #ff6b9d;
        font-weight: 600;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p>Real-time Competitive Intelligence Dashboard ✨</p>
</div>
""", unsafe_allow_html=True)

# === VALID & ACTIVE RSS FEEDS ONLY (Verified Jan 2, 2026) ===
RSS_FEEDS = [
    # Telco - All active
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("Verizon Newsroom", "https://www.verizon.com/about/news/rss"),
    ("T-Mobile News", "https://www.t-mobile.com/news/rss"),
    ("Vodafone Group", "https://www.vodafone.com/news/rss"),
    
    # OTT - All active
    ("Variety", "https://variety.com/feed/"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
    ("Deadline", "https://deadline.com/feed/"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ("Advanced Television", "https://advanced-television.com/feed/"),
    ("Netflix Press", "https://ir.netflix.net/resources/rss-feeds/default.aspx"),
    ("Disney Company News", "https://thewaltdisneycompany.com/feed/"),
    ("Warner Bros Discovery", "https://press.wbd.com/us/rss-feed"),
    
    # Sports - All active
    ("ESPN", "https://www.espn.com/espn/rss/news"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
    ("Front Office Sports", "https://frontofficesports.com/feed/"),
    ("Sportico", "https://www.sportico.com/feed/"),
    ("SportsPro", "https://www.sportspromedia.com/feed/"),
    
    # Technology - All active
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
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header-orange"},
}

SOURCE_CATEGORY_MAP = {
    "Telecoms.com": "telco",
    "Light Reading": "telco",
    "Fierce Telecom": "telco",
    "RCR Wireless": "telco",
    "Mobile World Live": "telco",
    "ET Telecom": "telco",
    "Verizon Newsroom": "telco",
    "T-Mobile News": "telco",
    "Vodafone Group": "telco",
    
    "Variety": "ott",
    "Hollywood Reporter": "ott",
    "Deadline": "ott",
    "Digital TV Europe": "ott",
    "Advanced Television": "ott",
    "Netflix Press": "ott",
    "Disney Company News": "ott",
    "Warner Bros Discovery": "ott",
    
    "ESPN": "sports",
    "BBC Sport": "sports",
    "Front Office Sports": "sports",
    "Sportico": "sports",
    "SportsPro": "sports",
    
    "TechCrunch": "technology",
    "The Verge": "technology",
    "Wired": "technology",
    "Ars Technica": "technology",
    "VentureBeat": "technology",
    "ZDNet": "technology",
    "Engadget": "technology",
    "Techmeme": "technology",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean(raw):
    """Clean HTML and escape special characters"""
    if not raw:
        return ""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', str(raw))
    # Unescape HTML entities
    text = html.unescape(text)
    # Clean whitespace
    text = ' '.join(text.split())
    return text.strip()

def fetch_feed(source, url):
    """Fetch and parse a single RSS feed"""
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            print(f"Failed to fetch {source}: HTTP {resp.status_code}")
            return items
        
        feed = feedparser.parse(resp.content)
        
        if not feed.entries:
            print(f"No entries found for {source}")
            return items
        
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=14)
        
        for entry in feed.entries[:15]:
            title = clean(entry.get("title", ""))
            
            # Skip very short titles
            if len(title) < 15:
                continue
            
            summary = clean(entry.get("summary", ""))
            link = entry.get("link", "")
            
            # Parse publication date
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6])
                        break
                    except:
                        pass
            
            # If no valid date, use current time
            if not pub:
                pub = NOW
            
            # Skip old articles
            if pub < CUTOFF:
                continue
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary
            })
        
        # Sort by date and keep top 3
        items.sort(key=lambda x: x["pub"], reverse=True)
        items = items[:3]
        
        print(f"✓ {source}: {len(items)} articles")
        
    except Exception as e:
        print(f"Error fetching {source}: {str(e)}")
    
    return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    """Load all RSS feeds in parallel"""
    categorized = {
        "telco": [],
        "ott": [],
        "sports": [],
        "technology": []
    }
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_feed, source, url) for source, url in RSS_FEEDS]
        
        for future in as_completed(futures):
            try:
                items = future.result()
                for item in items:
                    category = SOURCE_CATEGORY_MAP.get(item["source"], "technology")
                    categorized[category].append(item)
            except Exception as e:
                print(f"Error processing future: {str(e)}")
    
    # Sort each category by date
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
    
    return categorized

def get_time_str(dt):
    """Get human-readable time string with styling class"""
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    
    if hrs < 1:
        return "Now", "time-hot"
    if hrs < 6:
        return f"{hrs}h", "time-hot"
    if hrs < 24:
        return f"{hrs}h", "time-warm"
    
    return f"{hrs//24}d", "time-normal"

def render_body(items):
    """Render news cards for a category"""
    if not items:
        return '<div class="empty-state">No recent news in this category yet 🌙<br>Check back soon! ♡</div>'
    
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_source = html.escape(item["source"])
        
        # Check if this is a priority item (mentions netcracker)
        content_lower = (item["title"] + item.get("summary", "")).lower()
        card_class = "news-card-priority" if "netcracker" in content_lower else "news-card"
        
        cards += f'''
        <div class="{card_class}">
            <a href="{safe_link}" target="_blank" class="card-title">
                {safe_title}
            </a>
            <div class="card-meta">
                <span class="{time_class}">{time_str}</span>
                <span>•</span>
                <span>{safe_source}</span>
            </div>
        </div>
        '''
    
    return f'<div>{cards}</div>'

# Loading message
placeholder = st.empty()
placeholder.markdown(
    '<div class="loading-msg">✨ Powering up the latest insights... Please wait a moment ♡</div>',
    unsafe_allow_html=True
)

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
        st.markdown(
            f'<div class="col-header {sec["style"]}">{sec["icon"]} {sec["name"]}</div>',
            unsafe_allow_html=True
        )
        st.markdown(render_body(items), unsafe_allow_html=True)

# Debug info (optional - remove in production)
with st.expander("📊 Debug Information"):
    st.write("Items per category:")
    for cat in cat_list:
        st.write(f"- {cat}: {len(data.get(cat, []))} articles")
