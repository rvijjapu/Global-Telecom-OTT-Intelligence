import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import hashlib
# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Evergent Strategic Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# Health check
query_params = st.query_params
if query_params.get("ping") == "1":
    st.write("alive")
    st.stop()
# ══════════════════════════════════════════════════════════════════════════════
# AI CONTENT FILTER
# ══════════════════════════════════════════════════════════════════════════════
BLACKLIST_WORDS = [
    "sexual", "porn", "xxx", "adult", "explicit", "nude", "nsfw",
    "murder", "killing", "shooter", "terrorist", "massacre", "rape", "assault",
    "scandal", "affair", "divorce", "lawsuit", "fraud", "corruption",
    "celebrity breakup", "dating rumors", "feud", "controversy",
    "casino", "gambling", "tobacco", "drug", "overdose",
    "ponzi", "scam", "pyramid scheme", "crypto crash"
]
def is_content_appropriate(title, summary=""):
    content = f"{title} {summary}".lower()
    return not any(word in content for word in BLACKLIST_WORDS)
# ══════════════════════════════════════════════════════════════════════════════
# EVERGENT INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
EVERGENT_CLIENTS = {
    "Astro": ["astro", "sooka", "njoi"],
    "Shahid": ["shahid", "mbc shahid"],
    "AT&T": ["at&t", "att", "directv"],
    "NBA": ["nba", "national basketball"],
    "Sony": ["sony", "sonyliv"],
    "Sky": ["sky nz", "sky new zealand", "sky tv"],
    "BBC": ["bbc", "bbc iplayer"],
    "ABS-CBN": ["abs-cbn", "abscbn"],
    "FOX": ["fox sports", "fox networks"],
}
# AI Scoring Keywords
TELCO_SIGNALS = {
    "tier1": ["5g monetization", "convergent billing", "digital bss", "oss transformation",
              "real-time charging", "network slicing", "api-based billing"],
    "tier2": ["bss", "oss", "billing platform", "charging system", "revenue management"],
    "tier3": ["telecom", "telco", "operator"],
    "negative": ["oil", "gas", "petroleum", "insurance", "banking", "semiconductor", "mining"]
}
OTT_SIGNALS = {
    "tier1": ["subscriber growth", "arpu", "streaming platform", "content deal", "ott expansion"],
    "tier2": ["streaming", "ott", "video platform", "subscription", "svod", "avod"],
    "tier3": ["media", "entertainment", "video"],
    "negative": ["cinema release", "box office", "movie review", "celebrity gossip", "red carpet"]
}
SPORTS_SIGNALS = {
    "tier1": ["media rights deal", "broadcasting rights", "sports streaming platform", "league partnership"],
    "tier2": ["sports media", "broadcasting", "sports streaming", "fan engagement"],
    "tier3": ["sports", "football", "basketball"],
    "negative": ["player injury", "match score", "fantasy tips", "betting odds", "transfer gossip"]
}
AI_SIGNALS = {
    "tier1": ["ai platform launch", "generative ai", "enterprise ai", "saas platform"],
    "tier2": ["artificial intelligence", "cloud computing", "enterprise software", "api"],
    "tier3": ["technology", "software", "digital"],
    "negative": ["semiconductor", "chip fabrication", "crypto mining", "nft"]
}
def calculate_relevance_score(title, summary, category):
    content = f"{title} {summary}".lower()
    score = 0
   
    signals = {
        "telco": TELCO_SIGNALS,
        "ott": OTT_SIGNALS,
        "sports": SPORTS_SIGNALS,
        "technology": AI_SIGNALS
    }.get(category, {})
   
    if not signals:
        return 0
   
    if any(neg in content for neg in signals.get("negative", [])):
        return 0
   
    score += sum(40 for kw in signals.get("tier1", []) if kw in content)
    score += sum(20 for kw in signals.get("tier2", []) if kw in content)
    score += sum(10 for kw in signals.get("tier3", []) if kw in content)
   
    for variations in EVERGENT_CLIENTS.values():
        if any(var in content for var in variations):
            score += 50
            break
   
    action_keywords = ["acquisition", "merger", "partnership", "deal", "expansion", "launches", "extension", "investment", "strategic", "wins", "award", "deploy", "scale", "growth", "churn reduction"]
    score += sum(15 for kw in action_keywords if kw in content)
   
    # Special boost for NBA strategic investment
    if "nba" in content and any(kw in content for kw in ["investment", "strategic", "extension", "partnership"]):
        score += 80
   
    return min(score, 100)
def classify_article_ai(title, summary, category):
    content = f"{title} {summary}".lower()
   
    for client_name, variations in EVERGENT_CLIENTS.items():
        if any(var in content for var in variations):
            score = calculate_relevance_score(title, summary, category)
            return "CLIENT", "🌟", client_name, 0, score
   
    score = calculate_relevance_score(title, summary, category)
   
    if score < 45:  # Raised from 30 for higher quality
        return "IRRELEVANT", "", "", 999, 0
   
    badges = {
        "telco": ("TELCO", "📡", "Telecom", 5),
        "ott": ("OTT", "📺", "Streaming", 6),
        "sports": ("SPORTS", "🏆", "Sports", 7),
        "technology": ("TECH", "⚡", "AI/Tech", 8)
    }
   
    priority_type, badge, entity, priority = badges.get(category, ("OTHER", "", "", 999))
    return priority_type, badge, entity, priority, score
# ══════════════════════════════════════════════════════════════════════════════
# RSS FEEDS
# ══════════════════════════════════════════════════════════════════════════════
RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/", "ott"),
    ("Streaming Media", "https://www.streamingmedia.com/rss", "ott"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("SportBusiness", "https://www.sportbusiness.com/feed/", "sports"),
    ("TV News Check", "https://tvnewscheck.com/business/feed", "sports"),  # Added for NBA/Evergent news
    ("TelecomTV", "https://www.telecomtv.com/feed", "telco"),  # Added premium feed
    ("TM Forum", "https://inform.tmforum.org/feed/", "telco"),  # OSS/BSS heavy
    ("StreamTV Insider", "https://www.streamtvinsider.com/rss.xml", "ott"),
    ("Cord Cutters News", "https://www.cordcuttersnews.com/feed/", "ott"),
    ("Sports Business Journal", "https://www.sportsbusinessjournal.com/rss", "sports"),
    ("Sportcal", "https://www.sportcal.com/feed/", "sports"),
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}
# ══════════════════════════════════════════════════════════════════════════════
# FEED FETCHING
# ══════════════════════════════════════════════════════════════════════════════
def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()
def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=5)
        if resp.status_code != 200:
            return items
       
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
       
        for entry in feed.entries[:20]:
            title = clean(entry.get("title", ""))
            if len(title) < 20:
                continue
           
            summary = clean(entry.get("summary", ""))
           
            if not is_content_appropriate(title, summary):
                continue
           
            link = entry.get("link", "")
           
            pub = NOW
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6])
                    except:
                        pass
                    break
           
            priority_type, badge, entity, sort_priority, relevance_score = classify_article_ai(
                title, summary, category
            )
           
            if priority_type == "IRRELEVANT":
                continue
           
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary,
                "category": category,
                "priority_type": priority_type,
                "badge": badge,
                "entity": entity,
                "sort_priority": sort_priority,
                "relevance_score": relevance_score,
                "is_strategic": relevance_score >= 60 and priority_type == "CLIENT"
            })
    except:
        pass
   
    return items
@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {
        "telco": [],
        "ott": [],
        "sports": [],
        "technology": [],
        "strategic_hits": []
    }
   
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = [
            executor.submit(fetch_feed, source, url, cat)
            for source, url, cat in RSS_FEEDS
        ]
       
        for future in as_completed(futures):
            items = future.result()
            for item in items:
                categorized[item["category"]].append(item)
               
                if item["is_strategic"] and (datetime.now() - item["pub"]).days <= 30:
                    categorized["strategic_hits"].append(item)
   
    # Deduplication using hash
    for cat in ["telco", "ott", "sports", "technology"]:
        seen_hashes = set()
        unique = []
       
        for item in categorized[cat]:
            # Create hash from normalized title
            norm_title = re.sub(r'[^\w\s]', '', item["title"].lower())[:50]
            content_hash = hashlib.md5(norm_title.encode()).hexdigest()
           
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique.append(item)
       
        categorized[cat] = unique
   
    # Sort and filter
    for cat in ["telco", "ott", "sports", "technology"]:
        cutoff = datetime.now() - timedelta(days=3)
        categorized[cat] = [a for a in categorized[cat] if a["pub"] >= cutoff]
       
        categorized[cat].sort(
            key=lambda x: (-x["relevance_score"], -x["pub"].timestamp())
        )
        categorized[cat] = categorized[cat][:5]  # Reduced to 5 for quality focus
   
    # Deduplicate strategic hits
    seen_hashes = set()
    unique_strategic = []
    for item in categorized["strategic_hits"]:
        norm_title = re.sub(r'[^\w\s]', '', item["title"].lower())[:50]
        content_hash = hashlib.md5(norm_title.encode()).hexdigest()
       
        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_strategic.append(item)
   
    categorized["strategic_hits"] = sorted(
        unique_strategic,
        key=lambda x: (-x["relevance_score"], -x["pub"].timestamp())
    )[:6]
   
    return categorized
def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1:
        return "Now", "time-hot"
    if hrs < 6:
        return f"{hrs}h", "time-hot"
    if hrs < 24:
        return f"{hrs}h", "time-warm"
    days = hrs // 24
    return f"{days}d", "time-normal"
# ══════════════════════════════════════════════════════════════════════════════
# STYLING
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
   
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
        padding-top: 0.5rem;
    }
   
    .header-container {
        background: rgba(255, 255, 255, 0.97);
        padding: 1.5rem 2rem;
        text-align: center;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.2);
        margin: 0 0 2rem 0;
        border-bottom: 4px solid #1e40af;
    }
   
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
   
    .subtitle {
        font-size: 1rem;
        color: #475569;
        margin-top: 0.5rem;
        font-weight: 500;
    }
   
    .hero-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 35px rgba(0,0,0,0.15);
    }
   
    .hero-title {
        color: #0a192f;
        font-size: 1.6rem;
        font-weight: 800;
        margin-bottom: 1.2rem;
        border-left: 6px solid #667eea;
        padding-left: 15px;
    }
   
    .strategic-item {
        background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
        border-left: 4px solid #f59e0b;
        padding: 12px 16px;
        margin-bottom: 12px;
        border-radius: 8px;
        position: relative;
    }
   
    .strategic-item strong {
        color: #0a192f;
        font-size: 0.95rem;
    }
   
    .strategic-item small {
        color: #64748b;
        font-size: 0.8rem;
    }
   
    .relevance-badge {
        position: absolute;
        top: 8px;
        right: 12px;
        background: #10b981;
        color: white;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.7rem;
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
    }
   
    .news-card:hover {
        background: #f1f5f9;
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }
   
    .news-card-client {
        background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
        border: 2px solid #fbbf24;
    }
   
    .news-title {
        color: #1e40af;
        font-size: 0.9rem;
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
        font-size: 0.75rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 7px;
        flex-wrap: wrap;
    }
   
    .score-badge {
        background: #10b981;
        color: white;
        padding: 2px 6px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 700;
    }
   
    .time-hot {color: #dc2626; font-weight: 600;}
    .time-warm {color: #ea580c; font-weight: 600;}
    .time-normal {color: #64748b;}
   
    .col-body::-webkit-scrollbar {width: 6px;}
    .col-body::-webkit-scrollbar-track {background: #f1f5f9;}
    .col-body::-webkit-scrollbar-thumb {background: #94a3b8; border-radius: 10px;}
   
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="column"] {padding: 0 8px !important;}
</style>
""", unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🤖 Evergent AI Strategic Intelligence</h1>
    <p class="subtitle">AI-Powered News Ranking • Content Filtered • Real-time Updates</p>
</div>
""", unsafe_allow_html=True)
with st.spinner(""):
    data = load_feeds()
    # Temporary high-priority injection for NBA news - remove after feeds reliably catch it
    nba_news = {
        "title": "NBA Makes Strategic Investment in Evergent Technologies + Multi-Year Partnership Extension",
        "link": "https://tvnewscheck.com/business/article/nba-makes-strategic-investment-in-evergent-technologies",
        "pub": datetime(2026, 1, 14),
        "source": "TV News Check",
        "summary": "NBA invests strategically in Evergent while extending partnership to enhance personalization, global subscriber growth, and churn management for League Pass.",
        "category": "sports",
        "priority_type": "CLIENT",
        "badge": "🏆",
        "entity": "NBA",
        "sort_priority": 7,
        "relevance_score": 100,
        "is_strategic": True
    }
    # Check if already in data to avoid dupes
    if not any(item["title"] == nba_news["title"] for item in data["strategic_hits"]):
        data["strategic_hits"].insert(0, nba_news)
    if not any(item["title"] == nba_news["title"] for item in data["sports"]):
        data["sports"].insert(0, nba_news)
# Strategic Highlights
strategic_hits = data.get("strategic_hits", [])
if strategic_hits:
    st.markdown('<div class="hero-container"><div class="hero-title">🚀 AI-DETECTED STRATEGIC HIGHLIGHTS (Last 30 Days)</div>', unsafe_allow_html=True)
   
    col1, col2 = st.columns(2)
    mid = len(strategic_hits) // 2
   
    with col1:
        for item in strategic_hits[:mid]:
            entity = html.escape(item.get("entity", "Industry"))
            title = html.escape(item["title"])
            days_ago = (datetime.now() - item["pub"]).days
            score = item["relevance_score"]
           
            st.markdown(f'<div class="strategic-item"><span class="relevance-badge">AI: {score}%</span><strong>{entity}:</strong> {title}<br><small>{days_ago}d ago • {html.escape(item["source"])}</small></div>', unsafe_allow_html=True)
   
    with col2:
        for item in strategic_hits[mid:]:
            entity = html.escape(item.get("entity", "Industry"))
            title = html.escape(item["title"])
            days_ago = (datetime.now() - item["pub"]).days
            score = item["relevance_score"]
           
            st.markdown(f'<div class="strategic-item"><span class="relevance-badge">AI: {score}%</span><strong>{entity}:</strong> {title}<br><small>{days_ago}d ago • {html.escape(item["source"])}</small></div>', unsafe_allow_html=True)
   
    st.markdown('</div>', unsafe_allow_html=True)
# News Sections
SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & STREAMING", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "AI & TECHNOLOGY", "style": "col-header-orange"},
}
cols = st.columns(4)
for idx, (cat, sec) in enumerate(SECTIONS.items()):
    items = data.get(cat, [])
   
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]} col-header">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
       
        if not items:
            st.markdown('<div class="col-body"><div style="text-align:center;color:#94a3b8;padding:40px;">🤖 AI monitoring...</div></div>', unsafe_allow_html=True)
        else:
            body_html = ['<div class="col-body">']
           
            for item in items:
                time_str, time_class = get_time_str(item["pub"])
                title = html.escape(item["title"])
                link = html.escape(item["link"])
                source = html.escape(item["source"])
                badge = item.get("badge", "")
                score = item["relevance_score"]
               
                card_class = "news-card-client" if item["priority_type"] == "CLIENT" else "news-card"
               
                body_html.append(f'<div class="{card_class}"><a href="{link}" target="_blank" class="news-title">{badge} {title}</a><div class="news-meta"><span class="{time_class}">{time_str}</span><span>•</span><span>{source}</span><span>•</span><span class="score-badge">{score}%</span></div></div>')
           
            body_html.append('</div>')
            st.markdown(''.join(body_html), unsafe_allow_html=True)
# Footer
total = sum(len(data[cat]) for cat in ["telco", "ott", "sports", "technology"])
avg_score = sum(item["relevance_score"] for cat in ["telco", "ott", "sports", "technology"] for item in data[cat]) / max(total, 1)
st.markdown(f'<div style="text-align:center;color:rgba(255,255,255,0.95);font-size:0.8rem;margin-top:20px;padding:16px;background:linear-gradient(135deg,rgba(10,25,47,0.95),rgba(30,41,59,0.95));border-radius:10px;"><p><strong>🤖 AI Agent Active</strong> | <strong>📊 Articles:</strong> {total} | <strong>⭐ Avg Quality:</strong> {avg_score:.0f}% | <strong>🔄 Refresh:</strong> 5min</p><p style="margin-top:6px;font-size:0.7rem;opacity:0.85;">AI-Filtered • Deduplicated • Relevance-Ranked • Last: {datetime.now().strftime("%H:%M:%S")}</p></div>', unsafe_allow_html=True)
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)
@st.fragment(run_every=300)
def auto_refresh():
    load_feeds()
    st.empty()
auto_refresh()
