import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
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

# ENHANCED STYLING WITH PRIORITY INDICATORS
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
        color: #1e40af;
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

# CRITICAL STRATEGIC KEYWORDS - ULTRA FOCUSED
CRITICAL_IMPACT_KWS = [
    # M&A and Deals
    "acquisition", "acquires", "acquired", "merger", "merges", "merged",
    "partnership", "partners with", "joint venture", "collaboration with",
    "strategic investment", "invests in", "funding round", "raises $",
    "deal worth", "contract award", "wins contract", "tender award",
    
    # Market Moving Events  
    "launches new", "expands into", "enters market", "exits",
    "shuts down", "bankruptcy", "restructuring", "layoffs",
    "appoints ceo", "appoints cto", "new ceo", "leadership change",
    "ipo", "goes public", "unicorn valuation",
    
    # Technology & Product
    "5g rollout", "fiber deployment", "network upgrade",
    "streaming platform", "ott launch", "content deal",
    "media rights", "broadcasting rights", "exclusive rights",
    
    # Financial
    "revenue decline", "revenue growth", "earnings beat", "earnings miss",
    "subscriber loss", "subscriber gain", "churn rate",
    "market share", "valuation reaches"
]

# ABSOLUTE NOISE - AUTO-REJECT
NOISE_BLOCKLIST = [
    "opinion:", "op-ed:", "commentary:", "analysis:", "perspective:",
    "review:", "recap:", "roundup:", "preview:", "predictions:",
    "how to", "guide to", "tips for", "best practices", "what to watch",
    "webinar:", "podcast:", "interview:", "q&a:", "transcript:",
    "awards", "wins award", "nominated for", "hall of fame",
    "celebrates", "anniversary", "birthday", "tribute to",
    "ai bubble", "flux.2", "black forest labs"  # Today's junk examples
]

# EVERGENT CLIENTS - ULTRA PRECISE
EVERGENT_CLIENTS = {
    "NBA": ["nba", "national basketball association", "nba league pass"],
    "Astro Malaysia": ["astro malaysia", "astro sooka"],
    "Shahid": ["shahid vip", "shahid mbc"],
    "FOX Sports": ["fox sports", "fox corporation"],
    "AT&T": ["directv", "at&t tv"],
    "TV Asahi": ["tv asahi"],
    "ABS-CBN": ["abs-cbn"],
    "Viki": ["rakuten viki"],
    "TRT": ["trt world"],
    "Sony": ["sonyliv", "sony pictures networks"],
    "BBC": ["bbc iplayer"],
    "Sky": ["sky nz", "sky uk"],
    "Telekom Malaysia": ["telekom malaysia", "tm unifi"],
}

# DIRECT COMPETITORS
COMPETITORS = {
    "Netcracker": ["netcracker"],
    "Amdocs": ["amdocs"],
    "CSG": ["csg systems", "csg ascendon"],
    "Oracle": ["oracle communications"],
    "Ericsson": ["ericsson charging", "ericsson bss"],
    "Matrixx": ["matrixx software"],
    "Optiva": ["optiva"],
}

# TOP TIER TELCOS ONLY
TOP_TELCOS = {
    "Verizon": ["verizon"],
    "AT&T": ["at&t mobility"],
    "T-Mobile": ["t-mobile"],
    "Vodafone": ["vodafone"],
    "Deutsche Telekom": ["deutsche telekom"],
    "Orange": ["orange sa"],
    "Telefónica": ["telefonica"],
    "BT Group": ["bt group"],
    "Singtel": ["singtel"],
    "Telstra": ["telstra"],
    "NTT Docomo": ["ntt docomo"],
    "China Mobile": ["china mobile"],
    "Jio": ["reliance jio"],
    "Airtel": ["bharti airtel"],
}

# COMBINED PRIORITY
PRIORITY_COMPANIES = {}
for d in [EVERGENT_CLIENTS, COMPETITORS, TOP_TELCOS]:
    PRIORITY_COMPANIES.update(d)

ALL_PRIORITY_KWS = []
for names in PRIORITY_COMPANIES.values():
    ALL_PRIORITY_KWS.extend([kw.lower() for kw in names])
ALL_PRIORITY_KWS = list(set(ALL_PRIORITY_KWS))

# RSS FEEDS - BUSINESS FOCUSED ONLY
RSS_FEEDS = [
    # Telecom Business
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    
    # OTT Business
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/", "ott"),
    
    # Sports Business
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("Sports Business Journal", "https://www.sportsbusinessjournal.com/rss", "sports"),
    
    # Tech Business (very selective)
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
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

def is_strategic_signal(title, summary):
    """STRICT filter - must have critical impact keyword"""
    text = (title + " " + summary).lower()
    
    # IMMEDIATE REJECT if noise
    for noise in NOISE_BLOCKLIST:
        if noise in text:
            return False
    
    # MUST have critical keyword
    has_critical_kw = any(kw in text for kw in CRITICAL_IMPACT_KWS)
    
    # OR must mention priority company with business context
    if not has_critical_kw:
        has_company = any(kw in text for kw in ALL_PRIORITY_KWS)
        has_business = any(word in text for word in ["revenue", "subscriber", "customer", "market", "deal", "contract", "platform", "service"])
        if not (has_company and has_business):
            return False
    
    return True

def calculate_relevance_score(text):
    """Score based on strategic relevance"""
    text_lower = text.lower()
    score = 0
    
    # Critical business events
    critical_events = ["acquisition", "merger", "partnership", "deal", "investment", "funding", "contract"]
    for event in critical_events:
        if event in text_lower:
            score += 20
    
    # Priority companies
    for kw in ALL_PRIORITY_KWS:
        if kw in text_lower:
            score += 25
            break
    
    # Business metrics
    metrics = ["revenue", "subscriber", "customer", "market share", "churn", "arpu"]
    for metric in metrics:
        if metric in text_lower:
            score += 10
    
    # Strategic keywords
    strategic = ["launches", "expands", "enters", "appoints", "ceo", "platform"]
    for word in strategic:
        if word in text_lower:
            score += 5
    
    return score

def deduplicate_stories(items):
    """Remove duplicate stories"""
    seen_titles = set()
    unique_items = []
    
    for item in items:
        title_sig = re.sub(r'[^\w\s]', '', item['title'].lower())
        title_sig = ' '.join(sorted(title_sig.split()[:6]))
        
        if title_sig not in seen_titles:
            seen_titles.add(title_sig)
            unique_items.append(item)
    
    return unique_items

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200: 
            return items
        
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=7)  # Last 7 days only
        
        for entry in feed.entries[:50]:
            title = clean(entry.get("title", ""))
            summary = clean(entry.get("summary", entry.get("description", "")))
            
            # STRICT strategic filter
            if not is_strategic_signal(title, summary):
                continue
            
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
            
            full_text = title + " " + summary
            relevance_score = calculate_relevance_score(full_text)
            
            # Only keep highly relevant stories
            if relevance_score < 15:
                continue
            
            is_priority = any(kw in full_text.lower() for kw in ALL_PRIORITY_KWS)
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary[:100] + "..." if len(summary) > 100 else summary,
                "category": category,
                "priority": is_priority,
                "score": relevance_score
            })
    except:
        pass
    
    return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(fetch_feed, s, u, c) for s, u, c in RSS_FEEDS]
        for future in as_completed(futures):
            items = future.result()
            for item in items:
                categorized[item["category"]].append(item)
    
    # Deduplicate and sort by relevance + recency
    for cat in categorized:
        categorized[cat] = deduplicate_stories(categorized[cat])
        categorized[cat].sort(key=lambda x: (x["score"], x["pub"]), reverse=True)
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1: return "Now"
    if hrs < 6: return f"{hrs}h"
    if hrs < 24: return f"{hrs}h"
    return f"{hrs//24}d"

def get_time_class(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 6: return "time-hot"
    if hrs < 24: return "time-warm"
    return "time-normal"

def render_body(items):
    if not items:
        return """<div class="col-body"><div style="text-align:center;color:#94a3b8;padding:40px;">🎯 Monitoring for strategic signals...</div></div>"""
    
    cards = []
    for item in items[:10]:  # Top 10 only
        time_str = get_time_str(item["pub"])
        time_class = get_time_class(item["pub"])
        title = html.escape(item["title"])
        link = html.escape(item["link"])
        source = html.escape(item["source"])
        
        card_class = "news-card-priority" if item["priority"] else "news-card"
        
        impact_badge = ""
        if item["score"] >= 40:
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

# DYNAMIC STRATEGIC INTELLIGENCE - ONLY BUSINESS CRITICAL
@st.cache_data(ttl=600)
def get_strategic_hits(data):
    """Extract top strategic hits - BUSINESS FOCUSED"""
    all_items = []
    for cat_items in data.values():
        all_items.extend(cat_items)
    
    # Sort by score
    all_items.sort(key=lambda x: x["score"], reverse=True)
    
    hits = []
    for item in all_items[:3]:
        # Extract key info
        title = item["title"]
        source = item["source"]
        
        # Create concise summary
        hits.append({
            "title": title,
            "source": source,
        })
    
    return hits

# LOADING SCREEN
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:70vh;text-align:center;">
            <h1 style="color:#0a192f;font-size:2.8rem;font-weight:800;">⚡ Strategic Intelligence Engine</h1>
            <p style="color:#64748b;font-size:1.2rem;">M&A • Partnerships • Market-Moving Events Only</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)
placeholder.empty()

# HEADER
st.markdown("""
<div class="header-container">
    <h1 class="main-title">Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Executive Intelligence • Zero Noise • Strategic Signals Only</p>
</div>
""", unsafe_allow_html=True)

# LOAD DATA
with st.spinner("🔍 Analyzing strategic signals..."):
    data = load_feeds()
    strategic_hits = get_strategic_hits(data)

# DYNAMIC STRATEGIC SECTION
hits_html = ""
if strategic_hits:
    for idx, hit in enumerate(strategic_hits, 1):
        hits_html += f"<b>#{idx}:</b> {hit['title']}<br><span style='color:#64748b;font-size:0.85rem;'>({hit['source']})</span><br><br>"
else:
    hits_html = "<i style='color:#64748b;'>Monitoring for M&A, partnerships, and strategic announcements...</i>"

total_signals = sum(len(items) for items in data.values())
priority_signals = len([i for cat in data.values() for i in cat if i['priority']])
critical_signals = len([i for cat in data.values() for i in cat if i['score'] >= 40])

st.markdown(f"""
<div class="hero-container">
    <div class="hero-title">🎯 Top Strategic Intelligence (Live Feed)</div>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div class="hero-box">
            <div class="hero-box-title" style="color: #dc2626;">🔥 BREAKING STRATEGIC SIGNALS</div>
            <div class="hero-content">
                {hits_html}
            </div>
        </div>
        <div class="hero-box">
            <div class="hero-box-title" style="color: #1e40af;">📊 INTELLIGENCE METRICS</div>
            <div class="hero-content">
                <b>High-Impact Signals Detected:</b> {total_signals}<br><br>
                <b>Priority Company Mentions:</b> {priority_signals}<br><br>
                <b>Critical Events (M&A/Deals):</b> {critical_signals}<br><br>
                <b>Last Scan:</b> {datetime.now().strftime('%I:%M %p')}<br><br>
                <b>Focus:</b> Evergent Clients • Competitors • Top Telcos
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# NEWS COLUMNS
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])
    
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)

# FOOTER
st.markdown(f"""
<div style="text-align:center;color:rgba(255,255,255,0.95);font-size:0.8rem;margin-top:20px;padding:16px;background:linear-gradient(135deg,rgba(10,25,47,0.95),rgba(30,41,59,0.95));border-radius:10px;">
    <strong>Strategic Focus:</strong> M&A • Partnerships • Revenue Events • Leadership Changes • Market Entry/Exit | <strong>Auto-refresh:</strong> Every 5 minutes
</div>
""", unsafe_allow_html=True)

keep_alive()
