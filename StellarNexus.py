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
# EVERGENT-FOCUSED INTELLIGENCE ENGINE
# ══════════════════════════════════════════════════════════════════════════════

# EVERGENT CLIENTS - All variations
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

# Strategic Keywords for Dynamic Highlights (Last 30 days)
STRATEGIC_KEYWORDS = {
    "acquisition": 10,
    "merger": 10,
    "partnership": 8,
    "deal": 7,
    "expansion": 6,
    "launches": 5,
    "signs": 5,
}

# TELCO OSS/BSS Keywords
TELCO_KEYWORDS = {
    "must_have": ["oss", "bss", "billing", "charging", "monetization", "5g", "digital transformation",
                  "revenue management", "order management", "catalog", "convergent", "mediation"],
    "exclude": ["oil", "gas", "petroleum", "insurance", "banking", "semiconductor", "chip", "mining"]
}

# OTT & STREAMING Keywords
OTT_KEYWORDS = {
    "must_have": ["ott", "streaming", "svod", "avod", "subscriber", "content", "platform",
                  "video", "sports streaming", "live streaming", "arpu", "churn"],
    "exclude": ["cinema", "box office", "movie review", "celebrity", "awards", "album"]
}

# SPORTS Keywords
SPORTS_KEYWORDS = {
    "must_have": ["media rights", "broadcasting", "sports streaming", "league", "fan engagement",
                  "sponsorship", "betting", "pay-per-view", "sports platform"],
    "exclude": ["player injury", "match score", "fantasy", "betting odds", "transfer gossip"]
}

# AI & TECHNOLOGY Keywords
AI_KEYWORDS = {
    "must_have": ["artificial intelligence", "ai platform", "generative ai", "cloud platform",
                  "saas", "api", "enterprise", "data platform", "mlops", "ai monetization"],
    "exclude": ["semiconductor", "chip fabrication", "gpu manufacturing", "crypto", "nft"]
}

# ══════════════════════════════════════════════════════════════════════════════
# RSS FEEDS - EVERGENT FOCUSED
# ══════════════════════════════════════════════════════════════════════════════
RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/", "ott"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("SportBusiness", "https://www.sportbusiness.com/feed/", "sports"),
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ══════════════════════════════════════════════════════════════════════════════
# INTELLIGENT CLASSIFICATION ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def has_keywords(content, must_have, exclude):
    """Check if content matches keyword criteria"""
    content_lower = content.lower()
    
    # Check exclusions first
    if any(ex in content_lower for ex in exclude):
        return False
    
    # Check must-have keywords
    return any(kw in content_lower for kw in must_have)

def classify_article(title, summary, category):
    """Intelligent article classification based on Evergent focus"""
    content = f"{title} {summary}".lower()
    
    # Priority 1: Evergent Clients
    for client_name, variations in EVERGENT_CLIENTS.items():
        if any(var in content for var in variations):
            return "CLIENT", "🌟", client_name, 0
    
    # Priority 2: Category-specific relevance
    if category == "telco":
        if has_keywords(content, TELCO_KEYWORDS["must_have"], TELCO_KEYWORDS["exclude"]):
            return "TELCO", "📡", "Telecom", 5
    
    elif category == "ott":
        if has_keywords(content, OTT_KEYWORDS["must_have"], OTT_KEYWORDS["exclude"]):
            return "OTT", "📺", "Streaming", 6
    
    elif category == "sports":
        if has_keywords(content, SPORTS_KEYWORDS["must_have"], SPORTS_KEYWORDS["exclude"]):
            return "SPORTS", "🏆", "Sports Media", 7
    
    elif category == "technology":
        if has_keywords(content, AI_KEYWORDS["must_have"], AI_KEYWORDS["exclude"]):
            return "TECH", "⚡", "AI & Tech", 8
    
    return "GENERIC", "", "", 999

def is_strategic_hit(title, summary):
    """Identify strategic news for highlights section"""
    content = f"{title} {summary}".lower()
    
    # Check for Evergent clients + strategic keywords
    client_found = any(
        any(var in content for var in variations)
        for variations in EVERGENT_CLIENTS.values()
    )
    
    strategic_found = any(kw in content for kw in STRATEGIC_KEYWORDS.keys())
    
    return client_found and strategic_found

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
        
        for entry in feed.entries[:15]:
            title = clean(entry.get("title", ""))
            if len(title) < 20:
                continue
            
            summary = clean(entry.get("summary", ""))
            link = entry.get("link", "")
            
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
            
            # Classify article
            priority_type, badge, entity, sort_priority = classify_article(title, summary, category)
            
            # Skip generic articles
            if priority_type == "GENERIC":
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
                "is_strategic": is_strategic_hit(title, summary)
            })
    except:
        pass
    
    return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    """Load and categorize all feeds"""
    categorized = {
        "telco": [],
        "ott": [],
        "sports": [],
        "technology": [],
        "strategic_hits": []
    }
    
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [
            executor.submit(fetch_feed, source, url, cat)
            for source, url, cat in RSS_FEEDS
        ]
        
        for future in as_completed(futures):
            items = future.result()
            for item in items:
                # Add to appropriate category
                categorized[item["category"]].append(item)
                
                # Add to strategic hits if relevant (last 30 days)
                if item["is_strategic"] and (datetime.now() - item["pub"]).days <= 30:
                    categorized["strategic_hits"].append(item)
    
    # Sort by priority and date
    for cat in categorized:
        categorized[cat].sort(key=lambda x: (x["sort_priority"], -x["pub"].timestamp()))
    
    # Filter to last 3 days for main sections
    cutoff = datetime.now() - timedelta(days=3)
    for cat in ["telco", "ott", "sports", "technology"]:
        categorized[cat] = [a for a in categorized[cat] if a["pub"] >= cutoff][:10]
    
    # Keep top 6 strategic hits from last 30 days
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
# PREMIUM STYLING
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
    }
    
    .strategic-item strong {
        color: #0a192f;
        font-size: 0.95rem;
    }
    
    .strategic-item small {
        color: #64748b;
        font-size: 0.8rem;
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
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

# Header
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Evergent Strategic Intelligence</h1>
    <p class="subtitle">AI-Powered Market Intelligence • Real-time Industry Insights</p>
</div>
""", unsafe_allow_html=True)

# Fetch Data
with st.spinner(""):
    data = load_feeds()

# Dynamic Strategic Highlights
strategic_hits = data.get("strategic_hits", [])

if strategic_hits:
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🚀 STRATEGIC HIGHLIGHTS (Last 30 Days)</div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    mid = len(strategic_hits) // 2
    
    with col1:
        for item in strategic_hits[:mid]:
            entity = item.get("entity", "Industry")
            title = item["title"]
            days_ago = (datetime.now() - item["pub"]).days
            
            st.markdown(f"""
            <div class="strategic-item">
                <strong>{entity}:</strong> {title}<br>
                <small>{days_ago}d ago • {item['source']}</small>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        for item in strategic_hits[mid:]:
            entity = item.get("entity", "Industry")
            title = item["title"]
            days_ago = (datetime.now() - item["pub"]).days
            
            st.markdown(f"""
            <div class="strategic-item">
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
            st.markdown('<div class="col-body"><div style="text-align:center;color:#94a3b8;padding:40px;">No recent news</div></div>', unsafe_allow_html=True)
        else:
            html_parts = ['<div class="col-body">']
            
            for item in items:
                time_str, time_class = get_time_str(item["pub"])
                title = html.escape(item["title"])
                link = html.escape(item["link"])
                source = html.escape(item["source"])
                badge = item.get("badge", "")
                
                card_class = "news-card-client" if item["priority_type"] == "CLIENT" else "news-card"
                
                html_parts.append(f'''
                <div class="{card_class}">
                    <a href="{link}" target="_blank" class="news-title">{badge} {title}</a>
                    <div class="news-meta">
                        <span class="{time_class}">{time_str}</span>
                        <span>•</span>
                        <span>{source}</span>
                    </div>
                </div>
                ''')
            
            html_parts.append('</div>')
            st.markdown(''.join(html_parts), unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="text-align:center;color:rgba(255,255,255,0.95);font-size:0.8rem;margin-top:20px;padding:16px;background:linear-gradient(135deg,rgba(10,25,47,0.95),rgba(30,41,59,0.95));border-radius:10px;">
    <p><strong>🟢 Live Status</strong> | <strong>🔄 Refreshes:</strong> Every 5 minutes | <strong>📊 Sources:</strong> {len(RSS_FEEDS)} feeds</p>
    <p style="margin-top:6px;font-size:0.7rem;opacity:0.85;">Evergent Strategic Intelligence • Last update: {datetime.now().strftime('%H:%M:%S')}</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

# Keep-alive fragment
@st.fragment(run_every=300)
def auto_refresh():
    load_feeds()
    st.empty()

auto_refresh()
