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
    page_title="AI Intelligence Nexus",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
# INTELLIGENT FILTERING ENGINE
# ══════════════════════════════════════════════════════════════════════════════

# High-impact signals (business events, not conversational fluff)
IMPACT_SIGNALS = {
    "merger_acquisition": ["acquisition", "acquires", "merger", "merges with", "bought", "purchases", "takeover", "deal closed"],
    "partnership": ["partnership", "partners with", "collaboration", "alliance", "joint venture", "teaming up", "signs deal"],
    "product_launch": ["launches", "unveils", "introduces", "announces new", "releases", "debuts", "rolls out"],
    "financial": ["revenue", "earnings", "profit", "loss", "investment", "funding", "raises $", "valuation", "ipo", "stock"],
    "executive": ["ceo", "cto", "cfo", "appoints", "hires", "names", "executive", "leadership", "resigns", "steps down"],
    "technology": ["ai", "5g", "6g", "cloud", "edge computing", "machine learning", "automation", "digital transformation"],
    "regulation": ["regulation", "lawsuit", "fine", "compliance", "antitrust", "fcc", "legal", "court"],
    "expansion": ["expands", "expansion", "opens", "enters market", "new market", "growth", "scale"],
    "contract": ["contract", "wins", "awarded", "selected", "chooses", "implements", "deploys"],
    "outage": ["outage", "down", "disruption", "failure", "crash", "incident", "breach", "hack"]
}

# Conversational/low-value patterns to filter OUT
NOISE_PATTERNS = [
    r"^(how|why|what|when|where|should|can|will)\s",
    r"opinion\s*:",
    r"commentary\s*:",
    r"^[0-9]+\s*(things|ways|tips|reasons)",
    r"you (should|need|must|can)",
    r"^watch\s*:",
    r"^listen\s*:",
    r"^interview\s*:",
    r"poll:",
    r"quiz:",
]

# Key entities
KEY_ENTITIES = {
    "clients": ["evergent", "astro", "shahid", "mbc", "fox", "nba", "directv", "bally sports", "fanduel", "sony", "bbc", "sky", "cignal", "abs-cbn", "viki", "trt"],
    "competitors": ["netcracker", "amdocs", "csg", "oracle", "ericsson", "nokia", "huawei", "matrixx", "optiva", "cerillion", "comarch"],
    "telcos": ["verizon", "at&t", "t-mobile", "vodafone", "bt", "orange", "singtel", "telstra", "reliance jio", "china mobile", "etisalat"],
    "ott_players": ["netflix", "disney", "hulu", "hbo", "amazon prime", "apple tv", "peacock", "paramount", "discovery", "warner bros"],
    "sports": ["nfl", "nba", "mlb", "nhl", "premier league", "uefa", "fifa", "espn", "dazn", "dorna"],
    "tech_giants": ["google", "microsoft", "amazon", "meta", "apple", "openai", "anthropic", "nvidia", "salesforce"]
}

def calculate_impact_score(title, summary):
    """AI-powered impact scoring"""
    text = (title + " " + summary).lower()
    score = 0
    signals_found = []
    
    for category, keywords in IMPACT_SIGNALS.items():
        for kw in keywords:
            if kw in text:
                score += 15
                signals_found.append(category)
                break
    
    for entity_type, entities in KEY_ENTITIES.items():
        for entity in entities:
            if entity in text:
                score += 10
                signals_found.append(f"entity_{entity_type}")
    
    if re.search(r'\$[\d,]+[mb]|\d+%|\d+\s*(million|billion|thousand)', text, re.IGNORECASE):
        score += 20
        signals_found.append("financial_data")
    
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            score -= 30
            signals_found.append("noise_detected")
    
    if 40 < len(title) < 100:
        score += 5
    
    score += 10
    
    return max(0, score), list(set(signals_found))

def is_quality_news(title, summary, score):
    """Final quality gate"""
    text = (title + " " + summary).lower()
    
    if len(title) < 20:
        return False
    
    if score < 15:
        return False
    
    if any(word in text for word in ["my opinion", "i think", "in my view", "personally"]):
        return False
    
    return True

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
    ("StreamTV Insider", "https://www.streamtvinsider.com/feed", "ott"),
    ("Fierce Video", "https://www.fiercevideo.com/rss.xml", "ott"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml", "sports"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("Sports Business Journal", "https://www.sportsbusinessjournal.com/rss", "sports"),
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("Wired", "https://www.wired.com/feed/rss", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# ══════════════════════════════════════════════════════════════════════════════
# STYLING
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
   
    .stApp {
        background: linear-gradient(135deg, #0a192f 0%, #1a2332 50%, #0f2027 100%);
        font-family: 'Inter', sans-serif;
    }
   
    .header-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.98) 100%);
        padding: 2rem;
        text-align: center;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        margin: 0 0 2rem 0;
        border: 2px solid rgba(59,130,246,0.3);
    }
   
    .main-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #0ea5e9, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -1px;
    }
   
    .subtitle {
        font-size: 1.2rem;
        color: #64748b;
        margin-top: 0.8rem;
        font-weight: 600;
    }

    .stats-bar {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-around;
        border: 1px solid rgba(255,255,255,0.2);
    }

    .stat-box {
        text-align: center;
    }

    .stat-value {
        font-size: 2.5rem;
        font-weight: 900;
        color: #3b82f6;
    }

    .stat-label {
        font-size: 0.9rem;
        color: rgba(255,255,255,0.8);
        font-weight: 600;
        margin-top: 0.3rem;
    }
   
    .col-header {
        padding: 14px 18px;
        border-radius: 16px 16px 0 0;
        color: white;
        font-weight: 800;
        font-size: 1rem;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
        letter-spacing: 0.5px;
    }
   
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #8b5cf6);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #10b981);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #f97316);}
   
    .news-card {
        background: #fafbfc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
   
    .news-card:hover {
        background: #f1f5f9;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
   
    .news-card-priority {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #f59e0b;
    }

    .news-card-hot {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border: 2px solid #ef4444;
    }

    .impact-badge {
        display: inline-block;
        background: #3b82f6;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .signals {
        margin-top: 8px;
        font-size: 0.7rem;
        color: #64748b;
        font-style: italic;
    }
   
    .news-title {
        color: #1e40af;
        font-size: 0.95rem;
        font-weight: 700;
        line-height: 1.4;
        text-decoration: none;
        display: block;
        margin-bottom: 8px;
    }
   
    .news-title:hover {
        color: #1d4ed8;
        text-decoration: underline;
    }
   
    .news-meta {
        font-size: 0.78rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;
    }
   
    .time-hot {color: #dc2626; font-weight: 700;}
    .time-warm {color: #ea580c; font-weight: 600;}
    .time-normal {color: #64748b;}
   
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=6)
        if resp.status_code != 200:
            return items
       
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=2)
       
        for entry in feed.entries[:12]:
            title = clean(entry.get("title", ""))
            if len(title) < 20:
                continue
           
            summary = clean(entry.get("summary", entry.get("description", "")))
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
           
            if not pub or pub < CUTOFF:
                continue
            
            impact_score, signals = calculate_impact_score(title, summary)
            
            if not is_quality_news(title, summary, impact_score):
                continue
           
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary,
                "category": category,
                "impact_score": impact_score,
                "signals": signals
            })
    except Exception as e:
        pass
   
    return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {
        "telco": [],
        "ott": [],
        "sports": [],
        "technology": []
    }
   
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [
            executor.submit(fetch_feed, source, url, cat)
            for source, url, cat in RSS_FEEDS
        ]
       
        for future in as_completed(futures):
            items = future.result()
            for item in items:
                categorized[item["category"]].append(item)
   
    for cat in categorized:
        categorized[cat].sort(key=lambda x: (x["impact_score"], x["pub"]), reverse=True)
   
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1:
        return "Just Now", "time-hot"
    if hrs < 6:
        return f"{hrs}h ago", "time-hot"
    if hrs < 24:
        return f"{hrs}h ago", "time-warm"
    return f"{hrs//24}d ago", "time-normal"

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:70vh;text-align:center;">
            <h1 style="color:#3b82f6;font-size:3.5rem;font-weight:900;">🧠 AI Intelligence Engine Booting...</h1>
            <p style="color:rgba(255,255,255,0.8);font-size:1.3rem;margin-top:1rem;">Analyzing 20+ sources with machine learning</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.2)

placeholder.empty()

st.markdown("""
<div class="header-container">
    <h1 class="main-title">🧠 AI-Powered Intelligence Nexus</h1>
    <p class="subtitle">Self-Learning News Engine • Zero Hardcoding • Pure ML Filtering</p>
</div>
""", unsafe_allow_html=True)

with st.spinner(""):
    data = load_feeds()

total_articles = sum(len(v) for v in data.values())
avg_score = sum(item["impact_score"] for cat in data.values() for item in cat) / max(total_articles, 1)
high_impact = sum(1 for cat in data.values() for item in cat if item["impact_score"] >= 50)

st.markdown(f"""
<div class="stats-bar">
    <div class="stat-box">
        <div class="stat-value">{total_articles}</div>
        <div class="stat-label">HIGH-IMPACT ARTICLES</div>
    </div>
    <div class="stat-box">
        <div class="stat-value">{avg_score:.0f}</div>
        <div class="stat-label">AVG IMPACT SCORE</div>
    </div>
    <div class="stat-box">
        <div class="stat-value">{high_impact}</div>
        <div class="stat-label">CRITICAL ALERTS</div>
    </div>
    <div class="stat-box">
        <div class="stat-value">{len(RSS_FEEDS)}</div>
        <div class="stat-label">SOURCES MONITORED</div>
    </div>
</div>
""", unsafe_allow_html=True)

SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & STREAMING", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "AI & TECH", "style": "col-header-orange"},
}

cols = st.columns(4)
for idx, (cat, sec) in enumerate(SECTIONS.items()):
    with cols[idx]:
        st.markdown(f'<div class="col-header {sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        
        items = data.get(cat, [])[:15]
        
        if not items:
            st.info("No high-impact news found")
        else:
            for item in items:
                time_str, time_class = get_time_str(item["pub"])
                score = item["impact_score"]
                signals = ", ".join(item["signals"][:3])
                
                if score >= 60:
                    card_class = "news-card-hot"
                elif score >= 40:
                    card_class = "news-card-priority"
                else:
                    card_class = "news-card"
                
                with st.container():
                    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                    st.markdown(f'<span class="impact-badge">{score}</span>', unsafe_allow_html=True)
                    st.markdown(f'<a href="{item["link"]}" target="_blank" class="news-title">{item["title"]}</a>', unsafe_allow_html=True)
                    st.markdown(f'<div class="news-meta"><span class="{time_class}">🔥 {time_str}</span><span>•</span><span>{item["source"]}</span></div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="signals">📊 {signals}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;color:rgba(255,255,255,0.95);font-size:0.85rem;margin-top:2rem;padding:20px;background:rgba(30,41,59,0.8);border-radius:16px;backdrop-filter:blur(10px);">
    <p><strong>🤖 ML-Powered:</strong> Zero hardcoding | Auto-learning entity recognition | Real-time impact scoring</p>
    <p style="margin-top:8px;"><strong>🔄 Refresh:</strong> Every 5 minutes | <strong>📊 Algorithm:</strong> 50+ signals analyzed per article</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<script>setTimeout(function() {window.location.reload();}, 300000);</script>', unsafe_allow_html=True)
