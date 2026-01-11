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
import json
from openai import OpenAI

# ══════════════════════════════════════════════════════════════════════════════
# READ ALL SECRETS SAFELY (this is the ONLY place keys should ever live)
# ══════════════════════════════════════════════════════════════════════════════
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except KeyError as e:
    st.error(f"Missing secret key: {str(e)}\n\nPlease go to Streamlit Cloud → Settings → Secrets and add:\nCEO_ACCESS_TOKEN and OPENAI_API_KEY")
    st.stop()

if not OPENAI_API_KEY:
    st.warning("OPENAI_API_KEY is empty in secrets → AI Insights will be disabled. Add a valid key to enable.")

# Security gate
provided_token = st.query_params.get("token", [""])[0]
if provided_token != EXPECTED_TOKEN:
    st.error("⛔ Unauthorized access – Invalid or missing token")
    st.info(f"Append `?token={EXPECTED_TOKEN}` to the URL or contact admin.")
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

# ══════════════════════════════════════════════════════════════════════════════
# FULL STYLING (your original – unchanged)
# ══════════════════════════════════════════════════════════════════════════════
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
   
    .ai-insights-panel {
        background: linear-gradient(135deg, #eef2ff 0%, #faf5ff 100%);
        border: 2px solid #c7d2fe;
        border-radius: 16px;
        padding: 24px;
        margin: 0 1.5rem 1.5rem 1.5rem;
    }
    .ai-insights-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
    }
    .ai-insights-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #4338ca;
        margin: 0;
    }
    .ceo-badge {
        background: #4f46e5;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .insights-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
    }
    .insight-card {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .insight-card-title {
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 1rem;
    }
    .announcement-item {
        margin-bottom: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f3f4f6;
    }
    .announcement-item:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }
    .announcement-title {
        font-weight: 600;
        color: #4338ca;
        font-size: 0.9rem;
        line-height: 1.3;
    }
    .announcement-desc {
        color: #6b7280;
        font-size: 0.8rem;
        margin-top: 4px;
        line-height: 1.4;
    }
    .trend-item {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 10px;
        font-size: 0.88rem;
        color: #374151;
        line-height: 1.4;
    }
    .trend-dot {
        color: #10b981;
        font-size: 0.8rem;
        margin-top: 2px;
        flex-shrink: 0;
    }
    .highlight-item {
        display: flex;
        align-items: flex-start;
        gap: 8px;
        margin-bottom: 10px;
        font-size: 0.88rem;
        color: #374151;
        line-height: 1.4;
    }
    .highlight-star {
        color: #f59e0b;
        flex-shrink: 0;
    }
   
    .col-header {
        padding: 12px 16px;
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
        max-height: 650px;
        overflow-y: auto;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    .google-section {
        background: linear-gradient(to right, #eff6ff, #ffffff);
        border: 2px solid #3b82f6;
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 15px;
    }
    .google-header {
        font-weight: 700;
        color: #1e40af;
        font-size: 0.9rem;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .ai-badge {
        background: #3b82f6;
        color: white;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
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
        font-size: 0.9rem;
        font-weight: 600;
        line-height: 1.35;
        text-decoration: none;
        display: block;
        margin-bottom: 8px;
    }
    .news-title:hover {
        color: #1d4ed8;
    }
    .news-meta {
        font-size: 0.75rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 6px;
        flex-wrap: wrap;
    }
    .time-hot { color: #dc2626; font-weight: 600; font-style: italic; }
    .time-warm { color: #ea580c; font-weight: 600; }
    .time-normal { color: #64748b; }
    .empty-message {
        text-align: center;
        color: #94a3b8;
        padding: 30px;
        font-size: 0.9rem;
    }
    .separator {
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 15px 0;
    }
    .read-more-btn {
        color: #2563eb;
        font-weight: 600;
        text-decoration: none;
        margin-left: auto;
    }
    .read-more-btn:hover {
        color: #1d4ed8;
    }
   
    @media (max-width: 768px) {
        .insights-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Powered Competitive Intelligence for CEO</p>
</div>
""", unsafe_allow_html=True)

# ── RSS FEEDS & CONFIG (unchanged)
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
    ("ESPN", "https://www.espn.com/espn/rss/news"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
    ("Front Office Sports", "https://frontofficesports.com/feed/"),
    ("Sportico", "https://www.sportico.com/feed/"),
    ("SportsPro", "https://www.sportspromedia.com/feed/"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("Ars Technica", "https://arstechnica.com/rss/"),
    ("VentureBeat", "https://venturebeat.com/feed/"),
    ("ZDNet", "https://www.zdnet.com/news/rss.xml"),
    ("Engadget", "https://www.engadget.com/rss.xml"),
]

GOOGLE_OSS_BSS_URL = "https://news.google.com/rss/search?q=(OSS+BSS+OR+%22operations+support+systems%22+OR+%22business+support+systems%22)+telecom+after:2025-12-01&hl=en-US&gl=US&ceid=US:en"

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header col-header-purple"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header col-header-green"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header col-header-orange"},
}

SOURCE_CATEGORY_MAP = {
    "Telecoms.com":"telco", "Light Reading":"telco", "RCR Wireless":"telco",
    "Mobile World Live":"telco", "ET Telecom":"telco", "The Fast Mode":"telco", "TelecomTV":"telco",
    "Variety":"ott", "Hollywood Reporter":"ott", "Deadline":"ott",
    "Digital TV Europe":"ott", "Advanced Television":"ott",
    "ESPN":"sports", "BBC Sport":"sports", "Front Office Sports":"sports",
    "Sportico":"sports", "SportsPro":"sports",
    "TechCrunch":"technology", "The Verge":"technology", "Wired":"technology",
    "Ars Technica":"technology", "VentureBeat":"technology", "ZDNet":"technology", "Engadget":"technology",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ── UTILITY FUNCTIONS (unchanged)
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

def get_priority_score(title, summary):
    text = (title + " " + (summary or "")).lower()
    score = 0
    keywords = ["deal", "contract", "partnership", "acquisition", "billion", "million",
                "oss", "bss", "billing", "revenue", "award", "win", "launch", "expansion"]
    for word in keywords:
        if word in text:
            score += 100
    return score

def simple_title_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# ── FEED FETCHING (unchanged)
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
        for entry in feed.entries[:10]:
            title = clean(entry.get("title", ""))
            if len(title) < 20:
                continue
            link = entry.get("link", "")
            if not link:
                continue
            summary = extract_summary(entry)
            pub = NOW
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                except:
                    pass
            if pub < cutoff:
                continue
            items.append({
                "title": title, "link": link, "pub": pub,
                "source": "Google OSS/BSS", "summary": summary,
                "hash": get_article_hash(title, link),
                "score": get_priority_score(title, summary) + 3000
            })
        items.sort(key=lambda x: (-x["score"], -x["pub"].timestamp()))
        return items
    except Exception as e:
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
            if len(title) < 20:
                continue
            link = entry.get("link", "")
            if not link:
                continue
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
            if pub < cutoff:
                continue
            items.append({
                "title": title, "link": link, "pub": pub,
                "source": source, "summary": summary,
                "hash": get_article_hash(title, link),
                "score": get_priority_score(title, summary)
            })
        return items
    except:
        return []

# ══════════════════════════════════════════════════════════════════════════════
# AI INSIGHTS GENERATION (with improved error handling)
# ══════════════════════════════════════════════════════════════════════════════
def generate_ai_insights(news_items):
    if not OPENAI_API_KEY:
        return None
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        news_text = "\n".join([f"- {item['title']} ({item['source']})" for item in news_items[:35]])
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are a telecom industry analyst providing executive insights for a CEO dashboard.
Focus on OSS/BSS, telecom deals, streaming/OTT news, and major partnerships.
Provide concise, business-focused insights."""
                },
                {
                    "role": "user",
                    "content": f"""Analyze these telecom and OTT news headlines and provide:
1. KEY ANNOUNCEMENTS (max 5): Most important business announcements with 1-line descriptions
2. MARKET TRENDS (max 3): Emerging industry trends
3. CLIENT HIGHLIGHTS (max 3): Notable client/partner news
News:
{news_text}
Return JSON format only:
{{"key_announcements": [{{"title": "...", "description": "..."}}], "market_trends": ["..."], "client_highlights": ["..."]}}"""
                }
            ],
            max_tokens=800,
            temperature=0.3
        )
        content = response.choices[0].message.content
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            return json.loads(json_match.group())
        return None
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "incorrect api key" in error_msg.lower():
            st.error("401 Error: Invalid or revoked OpenAI API key. Please create a new one at https://platform.openai.com/api-keys and update your secrets.")
        elif "429" in error_msg:
            st.warning("Rate limit reached. AI insights temporarily unavailable – try again in a few minutes.")
        else:
            st.error(f"AI Error: {error_msg[:100]}... Check your OPENAI_API_KEY in secrets.")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# LOAD ALL FEEDS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    seen_hashes = set()
    seen_titles = {}
    google_items = fetch_google_oss_bss()
    for item in google_items:
        if item["hash"] not in seen_hashes:
            categorized["telco"].append(item)
            seen_hashes.add(item["hash"])
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_feed, s, u) for s, u in RSS_FEEDS]
        for future in as_completed(futures):
            try:
                items = future.result()
                for item in items:
                    if item["hash"] in seen_hashes:
                        continue
                    skip = False
                    for prev_title in seen_titles:
                        if simple_title_similarity(item["title"], prev_title) > 0.82:
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
    for cat in categorized:
        categorized[cat].sort(key=lambda x: (-x.get("score", 0), -x["pub"].timestamp()))
    return {"google_oss_bss": google_items, "regular": categorized}

# ══════════════════════════════════════════════════════════════════════════════
# RENDERING FUNCTIONS (unchanged)
# ══════════════════════════════════════════════════════════════════════════════
def get_time_str(dt):
    now_et = datetime.now(ZoneInfo("America/New_York"))
    diff = (now_et - dt).total_seconds()
    hrs = int(diff / 3600)
    if hrs < 1: return "Just now", "time-hot"
    if hrs < 6: return f"{hrs}h ago", "time-hot"
    if hrs < 24: return f"{hrs}h ago", "time-warm"
    return f"{hrs // 24}d ago", "time-normal"

def render_ai_insights(insights):
    if not insights:
        return ""
    announcements_html = ""
    for item in insights.get("key_announcements", [])[:5]:
        if isinstance(item, dict):
            title = html.escape(str(item.get("title", "")))
            desc = html.escape(str(item.get("description", "")))
            announcements_html += f'''<div class="announcement-item">
                <div class="announcement-title">{title}</div>
                <div class="announcement-desc">{desc}</div>
            </div>'''
    trends_html = ""
    for trend in insights.get("market_trends", [])[:3]:
        trends_html += f'''<div class="trend-item">
            <span class="trend-dot">●</span>
            <span>{html.escape(str(trend))}</span>
        </div>'''
    highlights_html = ""
    for highlight in insights.get("client_highlights", [])[:3]:
        highlights_html += f'''<div class="highlight-item">
            <span class="highlight-star">★</span>
            <span>{html.escape(str(highlight))}</span>
        </div>'''
    return f'''
    <div class="ai-insights-panel">
        <div class="ai-insights-header">
            <span style="font-size: 1.6rem;">🤖</span>
            <h2 class="ai-insights-title">AI-Powered Industry Insights</h2>
            <span class="ceo-badge">CEO Brief</span>
        </div>
        <div class="insights-grid">
            <div class="insight-card">
                <div class="insight-card-title">📢 Key Announcements</div>
                {announcements_html if announcements_html else '<div class="empty-message">No announcements</div>'}
            </div>
            <div class="insight-card">
                <div class="insight-card-title">📈 Market Trends</div>
                {trends_html if trends_html else '<div class="empty-message">No trends</div>'}
            </div>
            <div class="insight-card">
                <div class="insight-card-title">⭐ Client Highlights</div>
                {highlights_html if highlights_html else '<div class="empty-message">No highlights</div>'}
            </div>
        </div>
    </div>
    '''

def render_google_section(google_items):
    if not google_items:
        return ""
    html_content = '''<div class="google-section">
    <div class="google-header">
        🔍 Google OSS/BSS Intelligence
        <span class="ai-badge">AI Search Results</span>
    </div>'''
    for item in google_items[:5]:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        html_content += f'''<div class="news-card">
            <a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="news-title">{safe_title}</a>
            <div class="news-meta">
                <span class="{time_class}">{time_str}</span>
                <span>•</span>
                <span>Google OSS/BSS</span>
                <a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="read-more-btn">👉 Read More</a>
            </div>
        </div>'''
    return html_content + '</div><div class="separator"></div>'

def render_news_cards(items):
    if not items:
        return '<div class="empty-message">📭 No recent news available</div>'
    cards = ""
    for item in items[:15]:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_source = html.escape(item["source"])
        cards += f'''<div class="news-card">
            <a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="news-title">{safe_title}</a>
            <div class="news-meta">
                <span class="{time_class}">{time_str}</span>
                <span>•</span>
                <span>{safe_source}</span>
                <a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="read-more-btn">👉 Read More</a>
            </div>
        </div>'''
    return cards

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION FLOW
# ══════════════════════════════════════════════════════════════════════════════
placeholder = st.empty()
placeholder.markdown(
    "<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>"
    "⚡ Preparing CEO Intelligence View...<br><small>Aggregating news from 20+ sources</small>"
    "</h2>",
    unsafe_allow_html=True
)

with st.spinner("Loading latest feeds..."):
    data = load_feeds()
    all_news = (
        data["google_oss_bss"] +
        data["regular"]["telco"][:15] +
        data["regular"]["ott"][:10] +
        data["regular"]["technology"][:5]
    )
    ai_insights = generate_ai_insights(all_news)

placeholder.empty()

# Render AI Insights
if ai_insights:
    st.markdown(render_ai_insights(ai_insights), unsafe_allow_html=True)
else:
    st.info("AI Insights powered by OpenAI • Add valid OPENAI_API_KEY in Streamlit secrets to enable")

# Render 4-column layout
cols = st.columns(4)
for idx, cat in enumerate(["telco", "ott", "sports", "technology"]):
    sec = SECTIONS[cat]
    google_section = render_google_section(data["google_oss_bss"]) if cat == "telco" else ""
    news_cards = render_news_cards(data["regular"].get(cat, []))
   
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="col-body">{google_section}{news_cards}</div>', unsafe_allow_html=True)

# Footer & auto-refresh
st.markdown(f"""
<div style="text-align: center; color: #64748b; font-size: 0.8rem; margin-top: 20px;">
    🌐 Global Telecom & OTT Stellar Nexus • AI-Powered Intelligence<br>
    Last Updated: {datetime.now().strftime("%I:%M:%S %p %Z")}
</div>
""", unsafe_allow_html=True)

st.markdown("""
<script>
setInterval(function(){
    window.location.reload();
}, 300000);
</script>
""", unsafe_allow_html=True)
