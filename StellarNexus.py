import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta, date
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re
from zoneinfo import ZoneInfo
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

    .google-section {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 15px;
    }

    .google-header {
        font-size: 0.85rem;
        font-weight: 700;
        color: #374151;
        text-align: center;
        padding: 8px;
        background: #f3f4f6;
        border-radius: 8px;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
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

    .news-card-google {
        background: #fafbfc;
        border: 1px solid #e2e8f0;
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

    .news-summary {
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

    .read-more-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #3b82f6;
        text-decoration: none;
        font-size: 0.8rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .read-more-btn:hover {
        color: #1d4ed8;
    }

    .hand-icon {
        font-size: 0.9rem;
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

# === RSS FEEDS ===
RSS_FEEDS = [
    # Telco & OSS/BSS
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
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

# Google OSS/BSS specific search
GOOGLE_OSS_BSS_URL = "https://news.google.com/rss/search?q=(OSS+BSS+OR+%22operations+support+systems%22+OR+%22business+support+systems%22)+telecom+after:2026-01-01&hl=en-US&gl=US&ceid=US:en"

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header col-header-purple"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header col-header-green"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header col-header-orange"},
}

SOURCE_CATEGORY_MAP = {
    "Telecoms.com": "telco", "Light Reading": "telco",
    "RCR Wireless": "telco", "Mobile World Live": "telco", "ET Telecom": "telco",
    "The Fast Mode": "telco", "TelecomTV": "telco",
    "Variety": "ott", "Hollywood Reporter": "ott", "Deadline": "ott",
    "Digital TV Europe": "ott", "Advanced Television": "ott", "StreamingMedia": "ott",
    "ESPN": "sports", "BBC Sport": "sports", "Front Office Sports": "sports",
    "Sportico": "sports", "SportsPro": "sports", "Sports Business": "sports",
    "TechCrunch": "technology", "The Verge": "technology", "Wired": "technology",
    "Ars Technica": "technology", "VentureBeat": "technology", "ZDNet": "technology",
    "Engadget": "technology", "Techmeme": "technology",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# AI importance scoring keywords
CRITICAL_KEYWORDS = {
    "telco": ["5g", "oss", "bss", "network", "spectrum", "carrier", "wireless", "fiber", "broadband", 
              "telecom", "mvno", "mobile operator", "infrastructure", "tower", "antenna", "satellite"],
    "ott": ["streaming", "netflix", "disney", "hbo", "paramount", "peacock", "hulu", "prime video",
            "subscription", "svod", "avod", "content", "original series", "licensing", "bundle"],
    "sports": ["nfl", "nba", "mlb", "soccer", "premier league", "espn", "rights deal", "broadcast",
               "sports betting", "fantasy", "athlete", "championship", "tournament"],
    "technology": ["ai", "artificial intelligence", "machine learning", "cloud", "saas", "cybersecurity",
                   "blockchain", "quantum", "semiconductor", "chip", "startup", "venture capital"]
}

def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def calculate_importance_score(title, summary, category):
    score = 0
    text = (title + " " + summary).lower()
    
    keywords = CRITICAL_KEYWORDS.get(category, [])
    for keyword in keywords:
        if keyword in text:
            score += 2
    
    if len(title) > 60:
        score += 1
    
    if len(summary) > 50:
        score += 2
    
    critical_terms = ["acquisition", "merger", "partnership", "launch", "announce", "billion", 
                     "million", "breakthrough", "first", "new", "major", "strategic"]
    for term in critical_terms:
        if term in text:
            score += 3
    
    return score

def extract_summary(entry, max_len=300):
    """Extract comprehensive summary for AI processing"""
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

def fetch_full_article_content(url):
    """Attempt to fetch full article text from URL"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code != 200:
            return ""
        
        from html.parser import HTMLParser
        
        class ArticleParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.in_script = False
                self.in_style = False
            
            def handle_starttag(self, tag, attrs):
                if tag in ['script', 'style', 'nav', 'header', 'footer']:
                    self.in_script = True
            
            def handle_endtag(self, tag):
                if tag in ['script', 'style', 'nav', 'header', 'footer']:
                    self.in_script = False
            
            def handle_data(self, data):
                if not self.in_script and data.strip():
                    self.text.append(data.strip())
        
        parser = ArticleParser()
        parser.feed(resp.text)
        full_text = ' '.join(parser.text)
        
        full_text = re.sub(r'\s+', ' ', full_text)
        return full_text[:3000]
    except:
        return ""

def ai_summarize_news(title, summary, url=None):
    """Advanced AI algorithm to create unique 2-3 line executive summary"""
    
    article_content = ""
    if url:
        article_content = fetch_full_article_content(url)
    
    source_text = article_content if article_content else summary
    full_text = f"{title}. {source_text}"
    
    sentences = re.split(r'[.!?]+', full_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
    
    if not sentences:
        return summary[:200] + "..." if len(summary) > 200 else summary
    
    unique_sentences = []
    seen_content = set()
    
    for sentence in sentences:
        fingerprint = sentence.lower().replace(' ', '')[:50]
        if fingerprint not in seen_content:
            unique_sentences.append(sentence)
            seen_content.add(fingerprint)
    
    sentences = unique_sentences[:8]
    
    scored_sentences = []
    
    for idx, sentence in enumerate(sentences):
        score = 0
        sentence_lower = sentence.lower()
        
        critical_words = {
            'announce': 5, 'launch': 5, 'partnership': 5, 'agreement': 5,
            'merger': 6, 'acquisition': 6, 'deal': 5, 'contract': 5,
            'revenue': 4, 'profit': 4, 'billion': 5, 'million': 4,
            'percent': 3, '%': 3, 'growth': 4, 'expand': 4,
            'ceo': 4, 'president': 4, 'executive': 3, 'invest': 5,
            'strategic': 4, 'plan': 3, 'customers': 3, 'users': 3,
            'new': 3, 'first': 4, 'major': 3, 'significant': 3
        }
        
        for word, weight in critical_words.items():
            if word in sentence_lower:
                score += weight
        
        numbers = re.findall(r'\d+', sentence)
        if numbers:
            score += len(numbers) * 2
        
        caps = [w for w in sentence.split() if len(w) > 3 and w[0].isupper()]
        score += min(len(caps), 3)
        
        if idx > 0 and idx < 4:
            score += (4 - idx) * 2
        
        if len(sentence) < 40 or len(sentence) > 200:
            score -= 2
        
        if sentence.strip().lower() == title.strip().lower():
            score = 0
        
        scored_sentences.append((sentence, score, idx))
    
    scored_sentences.sort(key=lambda x: (-x[1], x[2]))
    
    exec_summary = []
    total_length = 0
    max_length = 280
    used_words = set()
    
    for sentence, score, idx in scored_sentences:
        if score <= 0:
            continue
        
        sentence_words = set(sentence.lower().split())
        overlap = len(sentence_words & used_words) / max(len(sentence_words), 1)
        
        if overlap > 0.6 and exec_summary:
            continue
        
        if total_length + len(sentence) <= max_length and len(exec_summary) < 3:
            exec_summary.append(sentence)
            total_length += len(sentence)
            used_words.update(sentence_words)
        
        if len(exec_summary) >= 2 and total_length > 150:
            break
    
    if not exec_summary:
        if summary and len(summary) > 50:
            return summary[:220] + "..."
        return "Details available in full article."
    
    result = '. '.join(exec_summary)
    if not result.endswith(('.', '!', '?')):
        result += '.'
    
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result

def get_article_hash(title, link):
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()

def extract_redirect_url(google_url):
    """Extract actual article URL from Google News redirect"""
    try:
        if 'google.com' in google_url and '/articles/' in google_url:
            resp = requests.get(google_url, headers=HEADERS, timeout=10, allow_redirects=True)
            return resp.url
        return google_url
    except:
        return google_url

def fetch_google_oss_bss():
    """Fetch ALL Google OSS/BSS news with direct links"""
    items = []
    try:
        resp = requests.get(GOOGLE_OSS_BSS_URL, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return items
        
        feed = feedparser.parse(resp.content)
        if not feed.entries:
            return items
        
        NOW = datetime.now(ZoneInfo("America/New_York"))
        cutoff_date = datetime(2026, 1, 1, tzinfo=ZoneInfo("America/New_York"))
        
        for entry in feed.entries:
            try:
                title = clean(entry.get("title", ""))
                if len(title) < 15:
                    continue
                
                link = entry.get("link", "")
                if not link:
                    continue
                
                direct_link = extract_redirect_url(link)
                
                summary = extract_summary(entry, max_len=300)
                
                exec_summary = ai_summarize_news(title, summary, direct_link)
                
                pub = NOW
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                    except:
                        pass
                
                if pub < cutoff_date:
                    continue
                
                items.append({
                    "title": title,
                    "link": direct_link,
                    "pub": pub,
                    "source": "Google OSS/BSS",
                    "summary": exec_summary,
                    "is_google": True,
                    "hash": get_article_hash(title, direct_link)
                })
            except:
                continue
        
        items.sort(key=lambda x: x["pub"], reverse=True)
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
        cutoff_date = datetime(2026, 1, 1, tzinfo=ZoneInfo("America/New_York"))
        
        for entry in feed.entries[:10]:
            try:
                title = clean(entry.get("title", ""))
                if len(title) < 15:
                    continue
               
                link = entry.get("link", "")
                if not link:
                    continue
                
                summary = extract_summary(entry, max_len=300)
                
                exec_summary = ai_summarize_news(title, summary, link)
               
                pub = NOW
                for k in ("published_parsed", "updated_parsed"):
                    val = getattr(entry, k, None)
                    if val:
                        try:
                            pub = datetime(*val[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                            break
                        except:
                            pass
               
                if pub < cutoff_date:
                    continue
               
                items.append({
                    "title": title,
                    "link": link,
                    "pub": pub,
                    "source": source,
                    "summary": exec_summary,
                    "is_google": False,
                    "hash": get_article_hash(title, link)
                })
            except:
                continue
       
        return items
    except:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    seen_hashes = set()
    
    google_items = fetch_google_oss_bss()
    
    regular_items = {"telco": [], "ott": [], "sports": [], "technology": []}
    
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(fetch_feed, source, url) for source, url in RSS_FEEDS]
       
        for future in as_completed(futures):
            try:
                items = future.result()
                for item in items:
                    if item["hash"] not in seen_hashes:
                        category = SOURCE_CATEGORY_MAP.get(item["source"], "technology")
                        score = calculate_importance_score(item["title"], item["summary"], category)
                        item["importance"] = score
                        regular_items[category].append(item)
                        seen_hashes.add(item["hash"])
            except:
                pass
    
    for cat in regular_items:
        regular_items[cat].sort(key=lambda x: (-x.get("importance", 0), -x["pub"].timestamp()))
    
    return {
        "google_oss_bss": google_items,
        "regular": regular_items
    }

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

def render_google_section(google_items):
    if not google_items:
        return ""
    
    cards = ""
    for item in google_items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        
        cards += f'''<div class="news-card news-card-google">
<div class="news-title">{safe_title}</div>
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>Google OSS/BSS</span>
<a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="read-more-btn">
<span class="hand-icon">👉</span> Read Full Article
</a>
</div>
</div>'''
    
    return f'''<div class="google-section">
{cards}
</div>
<div class="separator"></div>'''

def render_regular_body(items):
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_source = html.escape(item["source"])
       
        cards += f'''<div class="news-card">
<div class="news-title">{safe_title}</div>
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
        cards = '<div class="empty-message">No news available</div>'
   
    return cards

placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ Igniting AI-Powered Intelligence...<br><small>Please wait for a moment</small></h2>", unsafe_allow_html=True)

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
}, 240000);
</script>
""", unsafe_allow_html=True)
