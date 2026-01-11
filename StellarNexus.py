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

# ══════════════════════════════════════════════════════════════════════════════
# API KEY & TOKEN
# ══════════════════════════════════════════════════════════════════════════════
GROQ_API_KEY = "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"
CEO_ACCESS_TOKEN = "Vijay"

# Security gate
provided_token = st.query_params.get("token", "")
if isinstance(provided_token, list):
    provided_token = provided_token[0] if provided_token else ""
if provided_token != CEO_ACCESS_TOKEN:
    st.error("⛔ Unauthorized access – Invalid or missing token")
    st.info(f"Append ?token={CEO_ACCESS_TOKEN} to the URL")
    st.stop()

# Rate limiting
if "last_access" not in st.session_state:
    st.session_state.last_access = 0
now = time.time()
if now - st.session_state.last_access < 2:
    st.warning("⏱ Too many requests – Please wait.")
    st.stop()
st.session_state.last_access = now

st.set_page_config(page_title="Global Telecom & OTT Stellar Nexus", page_icon="🌐", layout="wide")

# ══════════════════════════════════════════════════════════════════════════════
# STYLING (your original + badges)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp {background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; color: #1e293b;}
    .header-container {background: rgba(255,255,255,0.95); padding: 1.2rem; text-align: center; border-radius: 20px; box-shadow: 0 6px 25px rgba(0,0,0,0.08); margin: 0 1.5rem 1.8rem; border-bottom: 4px solid #3b82f6;}
    .main-title {font-size: 2.4rem; font-weight: 800; color: #1e40af; margin: 0;}
    .subtitle {font-size: 1.1rem; color: #475569; margin-top: 0.6rem;}
    .ai-insights-panel {background: linear-gradient(135deg, #eef2ff, #faf5ff); border: 2px solid #c7d2fe; border-radius: 16px; padding: 24px; margin: 0 1.5rem 1.5rem;}
    .ai-insights-header {display: flex; align-items: center; gap: 12px; margin-bottom: 20px;}
    .ai-insights-title {font-size: 1.4rem; font-weight: 700; color: #4338ca;}
    .ceo-badge {background: #4f46e5; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600;}
    .insights-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;}
    .insight-card {background: white; border-radius: 12px; padding: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);}
    .insight-card-title {font-weight: 700; color: #1f2937; margin-bottom: 12px; font-size: 1rem;}
    .col-header {padding: 12px 16px; border-radius: 14px 14px 0 0; color: white; font-weight: 700; font-size: 0.95rem; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);}
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #8b5cf6);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #10b981);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #f97316);}
    .col-body {background: white; border-radius: 0 0 14px 14px; padding: 12px; min-height: 520px; max-height: 650px; overflow-y: auto; box-shadow: 0 6px 20px rgba(0,0,0,0.08);}
    .google-section {background: linear-gradient(to right, #eff6ff, #ffffff); border: 2px solid #3b82f6; border-left: 4px solid #3b82f6; border-radius: 12px; padding: 12px; margin-bottom: 15px;}
    .google-header {font-weight: 700; color: #1e40af; font-size: 0.9rem; margin-bottom: 10px; display: flex; gap: 8px;}
    .ai-badge {background: #3b82f6; color: white; padding: 2px 8px; border-radius: 6px; font-size: 0.7rem;}
    .client-badge {background: #10b981; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; margin-left: 8px;}
    .news-card {background: #fafbfc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px; margin-bottom: 10px;}
    .news-card:hover {background: #f1f5f9; box-shadow: 0 6px 16px rgba(0,0,0,0.08); transform: translateY(-2px);}
    .news-title {color: #1e40af; font-size: 0.9rem; font-weight: 600;}
    .news-meta {font-size: 0.75rem; color: #64748b; display: flex; gap: 6px; flex-wrap: wrap;}
    .time-hot {color: #dc2626; font-weight: 600; font-style: italic;}
    .time-warm {color: #ea580c; font-weight: 600;}
    .time-normal {color: #64748b;}
    .empty-message {text-align: center; color: #94a3b8; padding: 30px; font-size: 0.9rem;}
    .separator {height: 2px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); margin: 15px 0;}
    .read-more-btn {color: #2563eb; font-weight: 600; text-decoration: none; margin-left: auto;}
    .read-more-btn:hover {color: #1d4ed8;}
    @media (max-width: 768px) {.insights-grid {grid-template-columns: 1fr;}}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-container'><h1 class='main-title'>🌐 Global Telecom & OTT Stellar Nexus</h1><p class='subtitle'>AI-Powered Competitive Intelligence for CEO</p></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ENTITY DATABASES FOR EACH SECTION
# ══════════════════════════════════════════════════════════════════════════════
TELCO_CLIENTS = {
    "Matrixx Software": ["matrixx", "matrixx software"],
    "Omantel": ["omantel"],
    "Rakuten": ["rakuten"],
    "Telefónica Germany": ["telefonica germany"],
    "Swisscom": ["swisscom"],
    "Deutsche Telekom": ["deutsche telekom"],
    "Cerillion": ["cerillion"],
    "Netcracker": ["netcracker"],
    "Qvantel": ["qvantel"],
    "Airspan": ["airspan"],
}

OTT_CLIENTS = {
    "Netflix": ["netflix"],
    "Disney+": ["disney+"],
    "Prime Video": ["prime video"],
    "Shahid": ["shahid"],
    "Viki": ["viki"],
    "Aha": ["aha"],
    "SonyLIV": ["sonyliv"],
}

SPORTS_CLIENTS = {
    "NBA": ["nba"],
    "ESPN": ["espn"],
    "FanDuel": ["fanduel"],
    "Bally Sports": ["bally sports"],
}

TECH_CLIENTS = {
    "Nokia": ["nokia"],
    "Ericsson": ["ericsson"],
    "Huawei": ["huawei"],
    "Samsung": ["samsung"],
    "Qualcomm": ["qualcomm"],
}

def detect_entity(text, section):
    text = text.lower()
    db = TELCO_CLIENTS if section == "telco" else OTT_CLIENTS if section == "ott" else SPORTS_CLIENTS if section == "sports" else TECH_CLIENTS
    for name, keywords in db.items():
        if any(k in text for k in keywords):
            return name
    return None

# ══════════════════════════════════════════════════════════════════════════════
# RSS & GOOGLE FEEDS (your original)
# ══════════════════════════════════════════════════════════════════════════════
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
    ("VentureBeat", "https://venturebeat.com/feed/"),
]

GOOGLE_OSS_BSS_URL = "https://news.google.com/rss/search?q=(OSS+BSS+OR+%22operations+support+systems%22+OR+%22business+support+systems%22)+telecom+after:2026-01-01&hl=en-US&gl=US&ceid=US:en"

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
    "ESPN":"sports", "BBC Sport":"sports", "Front Office Sports":"sports", "SportsPro":"sports",
    "TechCrunch":"technology", "The Verge":"technology", "Wired":"technology", "VentureBeat":"technology",
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ── UTILITY FUNCTIONS ──────────────────────────────────────────────────────
def clean(raw):
    if not raw: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def extract_summary(entry, max_len=280):
    summary = ""
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and len(content) > 0:
                content = content[0].get('value', '')
            summary = clean(content)
            if summary: break
    if len(summary) > max_len:
        summary = summary[:max_len].rsplit(' ', 1)[0] + '...'
    return summary

def get_article_hash(title, link):
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()

def simple_title_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# ── FEED FETCHING ──────────────────────────────────────────────────────────
def fetch_google_oss_bss():
    items = []
    try:
        resp = requests.get(GOOGLE_OSS_BSS_URL, headers=HEADERS, timeout=15)
        if resp.status_code != 200: return items
        feed = feedparser.parse(resp.content)
        NOW = datetime.now(ZoneInfo("America/New_York"))
        cutoff = datetime(2026, 1, 1, tzinfo=ZoneInfo("America/New_York"))
        for entry in feed.entries[:15]:
            title = clean(entry.get("title", ""))
            if len(title) < 20: continue
            link = entry.get("link", "")
            if not link: continue
            summary = extract_summary(entry)
            pub = NOW
            if hasattr(entry, 'published_parsed'):
                try:
                    pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                except:
                    pass
            if pub < cutoff: continue
            items.append({"title": title, "link": link, "pub": pub, "source": "Google OSS/BSS", "summary": summary, "hash": get_article_hash(title, link)})
        items.sort(key=lambda x: -x["pub"].timestamp())
        return items
    except:
        return []

def fetch_feed(source, url):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200: return items
        feed = feedparser.parse(resp.content)
        NOW = datetime.now(ZoneInfo("America/New_York"))
        cutoff = datetime(2026, 1, 1, tzinfo=ZoneInfo("America/New_York"))
        for entry in feed.entries[:12]:
            title = clean(entry.get("title", ""))
            if len(title) < 20: continue
            link = entry.get("link", "")
            if not link: continue
            summary = extract_summary(entry)
            pub = NOW
            if 'published_parsed' in entry:
                try:
                    pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                except:
                    pass
            if pub < cutoff: continue
            items.append({"title": title, "link": link, "pub": pub, "source": source, "summary": summary, "hash": get_article_hash(title, link)})
        return items
    except:
        return []

# Load feeds + remove duplicates
@st.cache_data(ttl=300)
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
            items = future.result()
            for item in items:
                if item["hash"] in seen_hashes: continue
                skip = any(simple_title_similarity(item["title"], t) > 0.85 for t in seen_titles)
                if skip: continue
                cat = SOURCE_CATEGORY_MAP.get(item["source"], "technology")
                categorized[cat].append(item)
                seen_hashes.add(item["hash"])
                seen_titles[item["title"]] = item

    for cat in categorized:
        categorized[cat].sort(key=lambda x: -x["pub"].timestamp())

    return {"google_oss_bss": google_items, "regular": categorized}

# Groq AI Insights
def generate_ai_insights(news_items):
    try:
        news_text = "\n".join([f"- {item['title']} ({item['source']})" for item in news_items[:30]])
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are a telecom & OTT analyst. Provide concise executive insights."},
                    {"role": "user", "content": f"""Analyze these headlines and return JSON only:
{{"key_announcements": [{{"title": "short title", "description": "1-sentence impact"}}], "market_trends": ["short trend"], "client_highlights": ["highlight"]}}
News:
{news_text}"""}
                ],
                "max_tokens": 800,
                "temperature": 0.3
            },
            timeout=20
        )
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                return json.loads(match.group())
    except:
        pass
    return None

# Rendering
def get_time_str(dt):
    diff = (datetime.now(ZoneInfo("America/New_York")) - dt).total_seconds() / 3600
    hrs = int(diff)
    if hrs < 1: return "Just now", "time-hot"
    if hrs < 6: return f"{hrs}h ago", "time-hot"
    if hrs < 24: return f"{hrs}h ago", "time-warm"
    return f"{hrs//24}d ago", "time-normal"

def render_ai_insights(insights):
    if not insights: return ""
    ann = "".join([f'<div class="announcement-item"><div class="announcement-title">{html.escape(i["title"])}</div><div class="announcement-desc">{html.escape(i["description"])}</div></div>' for i in insights.get("key_announcements", [])[:5]])
    tr = "".join([f'<div class="trend-item"><span class="trend-dot">●</span><span>{html.escape(t)}</span></div>' for t in insights.get("market_trends", [])[:3]])
    hl = "".join([f'<div class="highlight-item"><span class="highlight-star">★</span><span>{html.escape(h)}</span></div>' for h in insights.get("client_highlights", [])[:3]])
    return f'''
    <div class="ai-insights-panel">
        <div class="ai-insights-header">
            <span style="font-size:1.6rem;">🤖</span>
            <h2 class="ai-insights-title">AI-Powered Industry Insights</h2>
            <span class="ceo-badge">CEO Brief</span>
        </div>
        <div class="insights-grid">
            <div class="insight-card"><div class="insight-card-title">📢 Key Announcements</div>{ann or '<div class="empty-message">No announcements</div>'}</div>
            <div class="insight-card"><div class="insight-card-title">📈 Market Trends</div>{tr or '<div class="empty-message">No trends</div>'}</div>
            <div class="insight-card"><div class="insight-card-title">⭐ Client Highlights</div>{hl or '<div class="empty-message">No highlights</div>'}</div>
        </div>
    </div>
    '''

def render_news_cards(items, section):
    if not items: return '<div class="empty-message">No recent news</div>'
    cards = ""
    for item in items[:15]:
        time_str, tclass = get_time_str(item["pub"])
        title = html.escape(item["title"])
        link = html.escape(item["link"])
        source = html.escape(item["source"])
        entity = detect_entity(item["title"] + " " + (item.get("summary", "")), section)
        badge = f'<span class="client-badge">{entity}</span>' if entity else ""
        cards += f'''<div class="news-card">
            <a href="{link}" target="_blank" class="news-title">{title}{badge}</a>
            <div class="news-meta">
                <span class="{tclass}">{time_str}</span> • <span>{source}</span>
                <a href="{link}" target="_blank" class="read-more-btn">👉 Read More</a>
            </div>
        </div>'''
    return cards

# MAIN DASHBOARD
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ Preparing CEO Intelligence View...</h2>", unsafe_allow_html=True)

with st.spinner(""):
    data = load_feeds()
    all_news = data["google_oss_bss"] + data["regular"]["telco"][:10] + data["regular"]["ott"][:5]
    ai_insights = generate_ai_insights(all_news)

placeholder.empty()

if ai_insights:
    st.markdown(render_ai_insights(ai_insights), unsafe_allow_html=True)

cols = st.columns(4)
for i, cat in enumerate(["telco", "ott", "sports", "technology"]):
    sec = SECTIONS[cat]
    google = render_news_cards(data["google_oss_bss"][:5], "telco") if cat == "telco" else ""
    cards = render_news_cards(data["regular"].get(cat, []), cat)
    with cols[i]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="col-body">{google}{cards}</div>', unsafe_allow_html=True)

st.markdown(f"<div style='text-align:center; color:#64748b; font-size:0.8rem; margin-top:20px;'>Last Updated: {datetime.now().strftime('%I:%M:%S %p')}</div>", unsafe_allow_html=True)
st.markdown("<script>setInterval(()=>location.reload(),300000);</script>", unsafe_allow_html=True)
