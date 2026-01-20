import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# PAGE CONFIG
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# KEEP-ALIVE + AUTO-REFRESH EVERY 5 MINUTES
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

st.markdown(
    '<script>setTimeout(function(){window.location.reload();}, 300000);</script>',
    unsafe_allow_html=True
)

# ENHANCED STYLING (unchanged)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', sans-serif;
        padding-top: 0.5rem;
    }
    .header-container {
        background: rgba(255, 255, 255, 0.96);
        padding: 1.5rem 2rem;
        text-align: center;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        margin: 0 0 2rem 0;
        border-bottom: 4px solid #1e40af;
    }
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #0a192f;
        margin: 0;
        letter-spacing: -0.8px;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #475569;
        margin-top: 0.6rem;
        font-weight: 500;
    }
    .hero-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 35px rgba(0,0,0,0.12);
        border: 1px solid #e2e8f0;
    }
    .hero-title {
        color: #0a192f;
        font-size: 1.85rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        border-left: 6px solid #1e40af;
        padding-left: 15px;
    }
    .hero-box {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        min-height: 240px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    .hero-box-title {
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 12px;
    }
    .hero-content {
        color: #1e293b;
        font-size: 0.95rem;
        line-height: 1.7;
    }
    .hero-content b {
        color: #0a192f;
        font-weight: 700;
    }
    .col-header {
        padding: 12px 16px;
        border-radius: 14px 14px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #8b5cf6);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #10b981);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #f97316);}
    .col-body {
        background: white;
        border-radius: 0 0 14px 14px;
        padding: 12px;
        min-height: 480px;
        max-height: 580px;
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
        position: relative;
    }
    .news-card-priority {
        background: linear-gradient(135deg, #fff5f5, #fef2f2);
        border: 2px solid #fca5a5;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
        position: relative;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
    }
    .news-card-priority::before {
        content: "⚡ PRIORITY";
        position: absolute;
        top: -8px;
        right: 10px;
        background: #dc2626;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
    }
    .news-card:hover, .news-card-priority:hover {
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    .news-title {
        color: #1e40af;
        font-size: 0.92rem;
        font-weight: 600;
        line-height: 1.35;
        text-decoration: none;
        display: block;
        margin-bottom: 6px;
    }
    .news-title:hover {
        color: #1d4ed8;
        text-decoration: underline;
    }
    .news-meta {
        font-size: 0.76rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 7px;
        flex-wrap: wrap;
    }
    .impact-badge {
        background: #dc2626;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
    }
    .time-hot {color: #dc2626; font-weight: 600; font-style: italic;}
    .time-warm {color: #ea580c; font-weight: 600;}
    .time-normal {color: #64748b;}
    .col-body::-webkit-scrollbar {width: 6px;}
    .col-body::-webkit-scrollbar-track {background: #f1f5f9; border-radius: 10px;}
    .col-body::-webkit-scrollbar-thumb {background: #94a3b8; border-radius: 10px;}
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="column"] {padding: 0 8px !important;}
</style>
""", unsafe_allow_html=True)

# STRATEGIC KEYWORDS BY CATEGORY (minor expansions for better matching)
TELCO_KEYWORDS = {
    "must_have": ["bss", "oss", "billing", "charging", "5g", "fiber", "network", "telecom", "telco", "operator", "carrier", "6g"],
    "strategic": ["acquisition", "merger", "partnership", "deal", "launches", "deploys", "contract", "appoints ceo", "expansion"],
    "companies": ["verizon", "at&t", "t-mobile", "vodafone", "deutsche telekom", "orange", "telefonica", "bt group",
                  "singtel", "telstra", "ntt docomo", "china mobile", "reliance jio", "airtel", "netcracker", "amdocs",
                  "csg", "oracle communications", "ericsson", "matrixx", "evergent"]
}
OTT_KEYWORDS = {
    "must_have": ["streaming", "ott", "content", "subscription", "svod", "avod", "vod", "video platform", "live streaming"],
    "strategic": ["launches platform", "content deal", "licensing", "original series", "streaming rights", "subscriber growth", "merger"],
    "companies": ["netflix", "disney", "hulu", "max", "paramount", "peacock", "prime video", "apple tv",
                  "shahid", "viki", "sonyliv", "bbc iplayer", "astro", "sky", "directv", "abs-cbn", "trt", "evergent"]
}
SPORTS_KEYWORDS = {
    "must_have": ["sports", "league", "broadcasting", "media rights", "sports streaming", "nfl", "nba", "soccer"],
    "strategic": ["broadcasting deal", "media rights", "streaming rights", "broadcast contract", "sports platform", "partnership"],
    "companies": ["nba", "nfl", "premier league", "espn", "fox sports", "dazn", "bally sports", "peacock sports",
                  "amazon sports", "apple sports", "sportspro", "bbc sport", "evergent"]
}
TECH_KEYWORDS = {
    "must_have": ["ai", "technology", "startup", "funding", "acquisition", "tech", "cloud", "cybersecurity"],
    "strategic": ["raises $", "funding round", "acquires", "merger", "ipo", "valuation", "investment", "breakthrough"],
    "companies": ["anthropic", "openai", "google", "microsoft", "amazon", "meta", "nvidia", "apple", "tesla", "evergent"]
}

# NOISE BLOCKLIST (expanded)
NOISE_BLOCKLIST = [
    "opinion:", "op-ed:", "commentary:", "analysis:", "perspective:", "editorial:",
    "review:", "recap:", "roundup:", "preview:", "predictions:", "forecast:",
    "how to", "guide to", "tips for", "best practices", "what to watch", "what to expect",
    "webinar:", "podcast:", "interview:", "q&a:", "transcript:",
    "awards", "wins award", "nominated", "hall of fame", "celebrates", "anniversary",
    "prediction market", "betting", "gambling", "fantasy sports", "quiz:", "poll:", "survey:"
]

# PRIORITY COMPANIES (added "evergent" and minor expansions)
EVERGENT_CLIENTS = ["nba", "astro", "shahid", "fox sports", "directv", "tv asahi", "abs-cbn",
                    "viki", "trt", "sonyliv", "bbc iplayer", "sky", "telekom malaysia", "evergent"]
COMPETITORS = ["netcracker", "amdocs", "csg", "oracle communications", "ericsson", "matrixx", "optiva"]
TOP_TELCOS = ["verizon", "at&t", "t-mobile", "vodafone", "deutsche telekom", "orange",
              "telefonica", "bt group", "singtel", "telstra", "ntt", "china mobile", "jio", "airtel"]
ALL_PRIORITY = EVERGENT_CLIENTS + COMPETITORS + TOP_TELCOS

# RSS FEEDS - EXPANDED WITH MORE SOURCES FOR COMPREHENSIVE COVERAGE
RSS_FEEDS = [
    # TELCO (added more for depth)
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Total Telecom", "https://totaltele.com/feed/", "telco"),
    ("TelecomTalk", "https://telecomtalk.info/feed", "telco"),
    ("Telecompaper", "https://www.telecompaper.com/rss", "telco"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss", "telco"),

    # OTT (added more for streaming focus)
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/", "ott"),
    ("Fierce Video", "https://www.fiercevideo.com/rss.xml", "ott"),
    ("StreamTV Insider", "https://www.streamtvinsider.com/feed", "ott"),
    ("Streaming Media", "https://feeds.feedburner.com/StreamingMediaMagazine-AllArticles", "ott"),

    # SPORTS (added more for media rights and deals)
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("Sports Business Journal", "https://www.sportsbusinessjournal.com/rss", "sports"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    ("FOX Sports", "https://api.foxsports.com/v2/content/optimized-rss?partnerKey=MB0Wehpmuj2lUhuRhQaafhBjAJqaPU244mlTDK1i&size=30", "sports"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml", "sports"),
    ("SportsLogos", "https://news.sportslogos.net/feed/", "sports"),

    # TECH (added more for M&A/funding focus)
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("WIRED", "https://www.wired.com/feed/rss", "technology"),
    ("Gizmodo", "https://gizmodo.com/rss", "technology"),
    ("Mashable", "https://mashable.com/feeds/rss/all", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("Ars Technica", "https://arstechnica.com/feed/", "technology"),
    ("ComputerWeekly", "https://www.computerweekly.com/rss/Latest-IT-news.xml", "technology"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO BSS/OSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT STREAMING", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "TECH M&A", "style": "col-header-orange"},
}

HEADERS = {"User-Agent": "Mozilla/5.0"}

def clean(raw):
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw or ""))).strip()

def is_noise(text):
    text_lower = text.lower()
    return any(noise in text_lower for noise in NOISE_BLOCKLIST)

def calculate_category_relevance(title, summary, category):
    text = (title + " " + summary).lower()
    score = 0

    if category == "telco":
        keywords = TELCO_KEYWORDS
    elif category == "ott":
        keywords = OTT_KEYWORDS
    elif category == "sports":
        keywords = SPORTS_KEYWORDS
    else:  # technology
        keywords = TECH_KEYWORDS

    # Must-have is now optional but boosts score
    if any(kw in text for kw in keywords["must_have"]):
        score += 20

    # Strategic keywords
    if any(kw in text for kw in keywords["strategic"]):
        score += 30

    # Priority companies
    if any(company in text for company in keywords["companies"]):
        score += 25

    # Global priority companies
    if any(company in text for company in ALL_PRIORITY):
        score += 15

    return score

def deduplicate_stories(items):
    seen_titles = set()
    unique_items = []

    for item in items:
        title_sig = re.sub(r'[^\w\s]', '', item['title'].lower())
        title_sig = ' '.join(sorted(title_sig.split()[:10]))  # Increased to 10 words
        if title_sig not in seen_titles:
            seen_titles.add(title_sig)
            unique_items.append(item)

    return unique_items

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            st.warning(f"Failed to fetch {source} ({url}): Status {resp.status_code}")
            return items

        feed = feedparser.parse(resp.content)
        NOW = datetime.now(timezone.utc)
        CUTOFF = NOW - timedelta(days=3)  # Tighter for latest news

        for entry in feed.entries[:100]:  # Increased to 100
            title = clean(entry.get("title", ""))
            summary = clean(entry.get("summary", entry.get("description", title)))  # Fallback to title if summary missing

            if len(title) < 20:
                continue

            if is_noise(title + " " + summary):
                continue

            link = entry.get("link", "")

            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6], tzinfo=timezone.utc)
                    except Exception as e:
                        st.warning(f"Date parse error for {title}: {e}")
                    break

            if not pub or pub < CUTOFF:
                continue

            relevance = calculate_category_relevance(title, summary, category)
            if relevance < 15:  # Lowered threshold
                continue

            full_text = (title + " " + summary).lower()
            is_priority = any(company in full_text for company in ALL_PRIORITY)

            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary[:100] + "..." if len(summary) > 100 else summary,
                "category": category,
                "priority": is_priority,
                "score": relevance
            })
    except Exception as e:
        st.warning(f"Error fetching {source} ({url}): {e}")

    return items

@st.cache_data(ttl=180, show_spinner=False)  # Shorter TTL for fresher data
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}

    with ThreadPoolExecutor(max_workers=20) as executor:  # Increased workers
        futures = [executor.submit(fetch_feed, s, u, c) for s, u, c in RSS_FEEDS]
        for future in as_completed(futures):
            items = future.result()
            for item in items:
                categorized[item["category"]].append(item)

    # Deduplicate and sort (priorities recency)
    for cat in categorized:
        categorized[cat] = deduplicate_stories(categorized[cat])
        categorized[cat].sort(key=lambda x: (-x["pub"].timestamp(), -x["score"]))  # Recency first, then score

    return categorized

def get_time_str(dt):
    hrs = int((datetime.now(timezone.utc) - dt).total_seconds() / 3600)
    if hrs < 1: return "Now"
    if hrs < 6: return f"{hrs}h"
    if hrs < 24: return f"{hrs}h"
    return f"{hrs//24}d"

def get_time_class(dt):
    hrs = int((datetime.now(timezone.utc) - dt).total_seconds() / 3600)
    if hrs < 6: return "time-hot"
    if hrs < 24: return "time-warm"
    return "time-normal"

def render_body(items):
    if not items:
        return """<div class="col-body"><div style="text-align:center;color:#94a3b8;padding:40px;">🎯 Monitoring for strategic signals...</div></div>"""

    cards = []
    for item in items[:12]:
        time_str = get_time_str(item["pub"])
        time_class = get_time_class(item["pub"])
        title = html.escape(item["title"])
        link = html.escape(item["link"])
        source = html.escape(item["source"])

        card_class = "news-card-priority" if item["priority"] else "news-card"

        impact_badge = ""
        if item["score"] >= 60:
            impact_badge = '<span class="impact-badge">CRITICAL</span>'

        card_html = f'''
        <div class="{card_class}">
            <a href="{link}" target="_blank" class="news-title">{title}</a>
            <div class="news-meta">
                <span class="{time_class}">{time_str}</span>
                <span>•</span>
                <span>{source}</span>
                {impact_badge}
            </div>
        </div>
        '''
        cards.append(card_html)

    return '<div class="col-body">' + ''.join(cards) + '</div>'

# STRATEGIC INTELLIGENCE (unchanged)
@st.cache_data(ttl=600)
def get_strategic_hits(data):
    all_items = []
    for cat_items in data.values():
        all_items.extend(cat_items)

    all_items.sort(key=lambda x: x["score"], reverse=True)

    hits = []
    for item in all_items[:3]:
        hits.append({"title": item["title"], "source": item["source"]})

    return hits

@st.cache_data(ttl=600)
def get_market_pulse(data):
    all_items = []
    for cat_items in data.values():
        all_items.extend(cat_items)

    pulse = []

    # Count priority company mentions
    priority_mentions = {}
    for item in all_items:
        text = (item["title"] + " " + item["summary"]).lower()
        for company in ALL_PRIORITY:
            if company in text:
                priority_mentions[company] = priority_mentions.get(company, 0) + 1

    # Top 3 trending companies
    top_companies = sorted(priority_mentions.items(), key=lambda x: x[1], reverse=True)[:3]

    for company, count in top_companies:
        pulse.append(f"<b>{company.upper()}:</b> {count} strategic mentions")

    return pulse

# LOADING SCREEN (unchanged)
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:70vh;text-align:center;">
            <h1 style="color:#0a192f;font-size:2.8rem;font-weight:800;">⚡ Strategic Intelligence Engine</h1>
            <p style="color:#64748b;font-size:1.2rem;">Scanning Global Telecom & OTT Markets</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)
placeholder.empty()

# HEADER (unchanged)
st.markdown("""
<div class="header-container">
    <h1 class="main-title">Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Executive Intelligence • Strategic Signals Only</p>
</div>
""", unsafe_allow_html=True)

# LOAD DATA
with st.spinner("🔍 Analyzing strategic signals..."):
    data = load_feeds()
    strategic_hits = get_strategic_hits(data)
    market_pulse = get_market_pulse(data)

# STRATEGIC SECTION (unchanged)
hits_html = ""
if strategic_hits:
    for idx, hit in enumerate(strategic_hits, 1):
        hits_html += f"<b>#{idx}:</b> {hit['title']}<br><span style='color:#64748b;font-size:0.85rem;'>({hit['source']})</span><br><br>"
else:
    hits_html = "<i style='color:#64748b;'>Monitoring for M&A and strategic moves...</i>"

pulse_html = ""
if market_pulse:
    for p in market_pulse:
        pulse_html += f"{p}<br><br>"
else:
    pulse_html = "<i style='color:#64748b;'>Analyzing market trends...</i>"

total_signals = sum(len(items) for items in data.values())
priority_signals = len([i for cat in data.values() for i in cat if i['priority']])
critical_signals = len([i for cat in data.values() for i in cat if i['score'] >= 60])

st.markdown(f"""
<div class="hero-container">
    <div class="hero-title">🎯 Strategic Intelligence Dashboard</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div class="hero-box">
            <div class="hero-box-title" style="color: #dc2626;">🔥 BREAKING STRATEGIC SIGNALS</div>
            <div class="hero-content">
                {hits_html}
            </div>
        </div>
        <div class="hero-box">
            <div class="hero-box-title" style="color: #10b981;">📊 MARKET PULSE</div>
            <div class="hero-content">
                {pulse_html}
                <div style="margin-top:15px;padding-top:15px;border-top:1px solid #e2e8f0;">
                    <b>Total Signals:</b> {total_signals} | <b>Priority:</b> {priority_signals} | <b>Critical:</b> {critical_signals}
                </div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# NEWS COLUMNS (unchanged)
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]
for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])

    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)

# FOOTER (unchanged)
st.markdown(f"""
<div style="text-align:center;color:rgba(255,255,255,0.95);font-size:0.8rem;margin-top:20px;padding:16px;background:linear-gradient(135deg,rgba(10,25,47,0.95),rgba(30,41,59,0.95));border-radius:10px;">
    <strong>Focus:</strong> M&A • Partnerships • Strategic Launches • Market Entry/Exit | <strong>Last Scan:</strong> {datetime.now().strftime('%I:%M %p')} | <strong>Auto-refresh:</strong> 5 min
</div>
""", unsafe_allow_html=True)
keep_alive()
