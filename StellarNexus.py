import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Evergent Strategic Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Health check endpoint
query_params = st.query_params
if query_params.get("ping") == "1":
    st.write("alive")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# AI CONTENT FILTER - BLOCKS INAPPROPRIATE CONTENT
# ══════════════════════════════════════════════════════════════════════════════

BLACKLIST_WORDS = [
    # Explicit content
    "sexual", "porn", "xxx", "adult", "explicit", "nude", "nsfw",
    # Violence/Crime
    "murder", "killing", "shooter", "terrorist", "massacre", "rape", "assault",
    # Inappropriate topics
    "scandal", "affair", "divorce", "lawsuit", "fraud", "corruption",
    # Entertainment gossip
    "celebrity breakup", "dating rumors", "feud", "controversy",
    # Off-topic industries
    "oil spill", "gas leak", "mining accident", "casino", "gambling addiction",
    "tobacco", "cigarette", "alcohol abuse", "drug", "overdose",
    # Political drama
    "election fraud", "protest violence", "riot", "impeachment",
    # Health/Medical drama
    "pandemic outbreak", "epidemic", "disease outbreak",
    # Crypto/Scam
    "ponzi", "scam", "fraud", "pyramid scheme", "crypto crash"
]

def is_content_appropriate(title, summary=""):
    """AI Filter: Blocks inappropriate content"""
    content = f"{title} {summary}".lower()
    
    # Check blacklist
    for word in BLACKLIST_WORDS:
        if word in content:
            return False
    
    # Additional pattern checks
    inappropriate_patterns = [
        r'\b(sex|porn|xxx)\b',
        r'\b(kill|murder|death)\b.*\b(trial|arrest)\b',
        r'\b(scandal|affair|divorce)\b',
    ]
    
    for pattern in inappropriate_patterns:
        if re.search(pattern, content):
            return False
    
    return True

# ══════════════════════════════════════════════════════════════════════════════
# AI RELEVANCE SCORING ENGINE
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

# AI Relevance Scoring Keywords
TELCO_SIGNALS = {
    "tier1": ["5g monetization", "convergent billing", "digital bss", "oss transformation", 
              "real-time charging", "network slicing", "telco cloud", "api-based billing"],
    "tier2": ["bss", "oss", "billing platform", "charging system", "revenue management",
              "order management", "product catalog", "service orchestration"],
    "tier3": ["telecom", "telco", "operator", "service provider", "network"],
    "negative": ["oil", "gas", "petroleum", "insurance core", "banking", "semiconductor fab",
                 "chip manufacturing", "mining", "power plant", "automotive"]
}

OTT_SIGNALS = {
    "tier1": ["subscriber growth", "arpu increase", "streaming platform", "content deal",
              "ott expansion", "svod launch", "sports streaming rights", "platform acquisition"],
    "tier2": ["streaming", "ott", "video platform", "content monetization", "subscription",
              "avod", "svod", "live streaming", "content aggregation"],
    "tier3": ["media", "entertainment", "video", "content"],
    "negative": ["cinema release", "box office", "movie review", "celebrity gossip",
                 "film awards", "red carpet", "paparazzi", "dating rumors"]
}

SPORTS_SIGNALS = {
    "tier1": ["media rights deal", "broadcasting rights", "sports streaming platform",
              "league partnership", "fan engagement platform", "sports ott launch"],
    "tier2": ["sports media", "broadcasting", "sports streaming", "league", "tournament",
              "fan platform", "sports technology", "digital ticketing"],
    "tier3": ["sports", "football", "basketball", "cricket", "racing"],
    "negative": ["player injury", "match score", "game result", "fantasy tips",
                 "betting odds", "transfer gossip", "player scandal"]
}

AI_SIGNALS = {
    "tier1": ["ai platform launch", "generative ai", "enterprise ai", "ai monetization",
              "ai acquisition", "saas platform", "cloud platform deal", "api platform"],
    "tier2": ["artificial intelligence", "machine learning", "ai platform", "cloud computing",
              "enterprise software", "saas", "platform", "api"],
    "tier3": ["technology", "software", "digital", "innovation"],
    "negative": ["semiconductor", "chip fabrication", "gpu manufacturing", "crypto mining",
                 "nft", "blockchain gaming", "metaverse hype"]
}

def calculate_relevance_score(title, summary, category):
    """AI Agent: Scores article relevance (0-100)"""
    content = f"{title} {summary}".lower()
    score = 0
    
    # Get category signals
    signals = {
        "telco": TELCO_SIGNALS,
        "ott": OTT_SIGNALS,
        "sports": SPORTS_SIGNALS,
        "technology": AI_SIGNALS
    }.get(category, {})
    
    if not signals:
        return 0
    
    # Check negative signals (immediate disqualification)
    if any(neg in content for neg in signals.get("negative", [])):
        return 0
    
    # Tier 1 keywords: +40 points each
    tier1_matches = sum(1 for kw in signals.get("tier1", []) if kw in content)
    score += tier1_matches * 40
    
    # Tier 2 keywords: +20 points each
    tier2_matches = sum(1 for kw in signals.get("tier2", []) if kw in content)
    score += tier2_matches * 20
    
    # Tier 3 keywords: +10 points each
    tier3_matches = sum(1 for kw in signals.get("tier3", []) if kw in content)
    score += tier3_matches * 10
    
    # Evergent client bonus: +50 points
    for client_name, variations in EVERGENT_CLIENTS.items():
        if any(var in content for var in variations):
            score += 50
            break
    
    # Business action keywords: +15 points each
    action_keywords = ["acquisition", "merger", "partnership", "deal", "expansion", 
                      "launches", "announces", "signs", "investment"]
    action_matches = sum(1 for kw in action_keywords if kw in content)
    score += action_matches * 15
    
    # Recency bonus
    # (handled separately by publication date)
    
    return min(score, 100)  # Cap at 100

def classify_article_ai(title, summary, category):
    """AI Agent: Intelligent classification"""
    content = f"{title} {summary}".lower()
    
    # Priority 1: Evergent Clients
    for client_name, variations in EVERGENT_CLIENTS.items():
        if any(var in content for var in variations):
            score = calculate_relevance_score(title, summary, category)
            return "CLIENT", "🌟", client_name, 0, score
    
    # Calculate relevance score
    score = calculate_relevance_score(title, summary, category)
    
    # Must score at least 30 to be included
    if score < 30:
        return "IRRELEVANT", "", "", 999, 0
    
    # Categorize based on category
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
    ("Capacity Media", "https://www.capacitymedia.com/rss", "telco"),
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/", "ott"),
    ("Streaming Media", "https://www.streamingmedia.com/rss", "ott"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("SportBusiness", "https://www.sportbusiness.com/feed/", "sports"),
    ("SportTechie", "https://www.sporttechie.com/feed/", "sports"),
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("Ars Technica", "https://arstechnica.com/feed/", "technology"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ══════════════════════════════════════════════════════════════════════════════
# FEED FETCHING ENGINE
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
            link = entry.get("link", "")
            
            # AI Content Filter
            if not is_content_appropriate(title, summary):
                continue
            
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6])
                    except:
                        pass
                    break
            
            if not pub:
                pub = NOW
            
            # AI Classification & Scoring
            priority_type, badge, entity, sort_priority, relevance_score = classify_article_ai(
                title, summary, category
            )
            
            # Skip irrelevant articles
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
    """AI Agent: Load and rank articles by relevance"""
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
                
                # Strategic hits (last 30 days, high relevance)
                if item["is_strategic"] and (datetime.now() - item["pub"]).days <= 30:
                    categorized["strategic_hits"].append(item)
    
    # AI Ranking: Sort by relevance score + recency
    for cat in ["telco", "ott", "sports", "technology"]:
        # Filter to last 3 days
        cutoff = datetime.now() - timedelta(days=3)
        categorized[cat] = [a for a in categorized[cat] if a["pub"] >= cutoff]
        
        # Sort by relevance score (descending) then recency
        categorized[cat].sort(
            key=lambda x: (
                -x["relevance_score"],  # Higher score first
                -x["pub"].timestamp()   # More recent first
            )
        )
        
        # Keep top 10 most relevant
        categorized[cat] = categorized[cat][:10]
    
    # Strategic hits: Keep top 6
    categorized["strategic_hits"].sort(
        key=lambda x: (-x["relevance_score"], -x["pub"].timestamp())
    )
    categorized["strategic_hits"] = categorized["strategic_hits"][:6]
    
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
    if days < 30:
        return f"{days}d", "time-normal"
    return f"{days}d", "time-old"

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
        position: relative;
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
    .time-old {color: #94a3b8;}
    
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

# Fetch Data
with st.spinner(""):
    data = load_feeds()

# Strategic Highlights
strategic_hits = data.get("strategic_hits", [])

if strategic_hits:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🚀 AI-DETECTED STRATEGIC HIGHLIGHTS (Last 30 Days)</div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    mid = len(strategic_hits) // 2
    
    with col1:
        for item in strategic_hits[:mid]:
            entity = item.get("entity", "Industry")
            title = html.escape(item["title"])
            days_ago = (datetime.now() - item["pub"]).days
            score = item["relevance_score"]
            
            st.markdown(f"""
            <div class="strategic-item">
                <span class="relevance-badge">AI: {score}%</span>
                <strong>{entity}:</strong> {title}<br>
                <small>{days_ago}d ago • {item['source']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        for item in strategic_hits[mid:]:
            entity = item.get("entity", "Industry")
            title = html.escape(item["title"])
            days_ago = (datetime.now() - item["pub"]).days
            score = item["relevance_score"]
            
            st.markdown(f"""
            <div class="strategic-item">
                <span class="relevance-badge">AI: {score}%</span>
                <strong>{entity}:</strong> {title}<br>
                <small>{days_ago}d ago • {item['source']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# News Sections
SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & STREAMING", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "AI & TECHNOLOGY", "style": "col-header-orange"},
}

cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])
    
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]} col-header">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        
        if not items:
            st.markdown('<div class="col-body"><div style="text-align:center;color:#94a3b8;padding:40px;">🤖 AI monitoring...</div></div>', unsafe_allow_html=True)
        else:
            html_parts = ['<div class="col-body">']
            
            for item in items:
                time_str, time_class = get_time_str(item["pub"])
                title = html.escape(item["title"])
                link = html.escape(item["link"])
                source = html.escape(item["source"])
                badge = item.get("badge", "")
                score = item["relevance_score"]
                
                card_class = "news-card-client" if item["priority_type"] == "CLIENT" else "news-card"
                
                html_parts.append(f'''
                <div class="{card_class}">
                    <a href="{link}" target="_blank" class="news-title">{badge} {title}</a>
                    <div class="news-meta">
                        <span class="{time_class}">{time_str}</span>
                        <span>•</span>
                        <span>{source}</span>
                        <span>•</span>
                        <span class="score-badge">{score}%</span>
                    </div>
                </div>
                ''')
            
            html_parts.append('</div>')
            st.markdown(''.join(html_parts), unsafe_allow_html=True)

# Footer
total_articles = sum(len(data[cat]) for cat in cat_list)
avg_score = sum(
    item["relevance_score"] 
    for cat in cat_list 
    for item in data[cat]
) / max(total_articles, 1)

st.markdown(f"""
<div style="text-align:center;color:rgba(255,255,255,0.95);font-size:0.8rem;margin-top:20px;padding:16px;background:linear-gradient(135deg,rgba(10,25,47,0.95),rgba(30,41,59,0.95));border-radius:10px;">
    <p><strong>🤖 AI Agent Active</strong> | <strong>📊 Articles:</strong> {total_articles} | <strong>⭐ Avg Quality:</strong> {avg_score:.0f}% | <strong>🔄 Refresh:</strong> 5min</p>
    <p style="margin-top:6px;font-size:0.7rem;opacity:0.85;">AI-Filtered • Content-Safe • Relevance-Ranked • Last update: {datetime.now().strftime('%H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

@st.fragment(run_every=300)
def auto_refresh():
    load_feeds()
    st.empty()

auto_refresh()
