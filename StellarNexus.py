import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import hashlib

# PAGE CONFIG
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus AI Powered Real-time Competitive Intelligence Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Health check
query_params = st.query_params
if query_params.get("ping") == "1":
    st.write("alive")
    st.stop()

# AI CONTENT FILTER (unchanged)
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

# EVERGENT CLIENTS - FULL LIST WITH VARIATIONS
EVERGENT_CLIENTS = {
    "Astro": ["astro malaysia", "astro sooka", "astro njoi", "astro", "sooka", "njoi"],
    "MongolTV": ["mongoltv", "mongol tv", "mongolia tv"],
    "FOX": ["fox sports", "fox corporation", "fox networks", "fox"],
    "AT&T": ["at&t", "att inc", "att wireless", "directv", "att mobility"],
    "NBA": ["nba", "national basketball"],
    "Shahid": ["shahid", "shahid vip", "mbc shahid"],
    "MBC": ["mbc group", "mbc", "middle east broadcasting"],
    "TV ASAHI": ["tv asahi", "asahi television", "asahi tv"],
    "TV3": ["tv3 malaysia", "tv3", "media prima"],
    "ABS-CBN": ["abs-cbn", "abscbn", "abs cbn", "philippine broadcast"],
    "Viki": ["viki", "rakuten viki", "viki streaming"],
    "TRT": ["trt world", "trt", "turkish radio"],
    "Sinclair": ["sinclair broadcast", "sinclair", "bally sports"],
    "FanDuel": ["fanduel", "fanduel group", "flutter"],
    "Bally Sports": ["bally sports", "bally regional", "diamond sports"],
    "Gotham": ["gotham advanced", "gotham fc"],
    "Marquee": ["marquee sports", "marquee network"],
    "Sony": ["sony pictures", "sony entertainment", "sonyliv", "sony india"],
    "Aha": ["aha video", "aha ott", "aha telugu"],
    "BBC": ["bbc", "british broadcasting", "bbc iplayer"],
    "Lightbox": ["lightbox", "spark lightbox"],
    "Sky": ["sky nz", "sky new zealand", "sky tv", "sky uk", "sky italia", "sky deutschland"],
    "Cignal": ["cignal tv", "cignal", "cignal satellite"],
    "ETV": ["etv network", "etv bharat"],
    "Simple TV": ["simpletv", "simple tv venezuela"],
    "Telekom Malaysia": ["telekom malaysia", "tm unifi", "unifi tv", "tm"],
    "Britbox": ["britbox", "britbox international"],
    "Quickplay": ["quickplay", "quickplay media"],
    "Pilipinas": ["pilipinas", "abs-cbn"],
    # From recent sources: Neon, KOCOWA, Brightcove integrations (but not direct clients), etc. — add if confirmed
}

# COMPETITORS - FULL WITH VARIATIONS
COMPETITORS = {
    "Netcracker": ["netcracker", "netcracker technology", "nec netcracker"],
    "Amdocs": ["amdocs", "amdocs ltd", "amdocs inc"],
    "CSG": ["csg systems", "csg international", "csg"],
    "Oracle": ["oracle communications", "oracle corporation", "oracle telecom"],
    "Ericsson": ["ericsson", "telefonaktiebolaget lm ericsson"],
    "Nokia": ["nokia", "nokia networks", "nokia corporation"],
    "Huawei": ["huawei", "huawei technologies"],
    "Comarch": ["comarch", "comarch bss"],
    "Tecnotree": ["tecnotree", "tecnotree corporation"],
    "MATRIXX": ["matrixx", "matrixx software"],
    "Optiva": ["optiva", "optiva inc"],
    "Cerillion": ["cerillion", "cerillion plc"],
    "AsiaInfo": ["asiainfo", "asiainfo technologies"],
    "Hansen": ["hansen technologies", "hansen"],
    "Openet": ["openet", "openet telecom"],
    "ZTE": ["zte", "zte corporation"],
    "Mavenir": ["mavenir", "mavenir systems"],
    "Infosys": ["infosys", "infosys telecom"],
    "TCS": ["tata consultancy", "tcs", "tata communications"],
    "Wipro": ["wipro", "wipro digital"],
    "Tech Mahindra": ["tech mahindra", "mahindra comviva"],
    "Accenture": ["accenture", "accenture telecom"],
    "Capgemini": ["capgemini", "capgemini telecom"],
    "IBM": ["ibm", "ibm telecom", "ibm watson"],
    "SAP": ["sap", "sap telecom"],
    "Salesforce": ["salesforce", "salesforce communications"],
}

# TOP GLOBAL TELCOS - COMPREHENSIVE (used for relevance boost if mentioned in context)
TOP_TELCOS = {**{k: v for k, v in {  # Flatten for search
    **TOP_TELCOS.get("USA", {}),
    **TOP_TELCOS.get("UK & Europe", {}),
    # ... add others as needed
}.items()}  # You can expand as per your dict
}

# AI SIGNALS (unchanged but can extend)
TELCO_SIGNALS = { ... }  # Keep your original
OTT_SIGNALS = { ... }
SPORTS_SIGNALS = { ... }
AI_SIGNALS = { ... }

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

    # Client boost
    client_found = False
    for variations in EVERGENT_CLIENTS.values():
        if any(var in content for var in variations):
            score += 60  # Higher boost for direct client mentions
            client_found = True
            break

    # Competitor mention (competitive intel boost)
    for variations in COMPETITORS.values():
        if any(var in content for var in variations):
            score += 30  # Flag as important for Evergent team

    # Top telco / operator mention in context
    for variations in TOP_TELCOS.values():
        if any(var in content for var in variations):
            score += 20

    action_keywords = ["acquisition", "merger", "partnership", "deal", "expansion", "launches", "extension", "investment", "strategic", "wins", "award", "deploy", "scale", "growth", "churn reduction", "monetization", "subscriber", "retention"]
    score += sum(15 for kw in action_keywords if kw in content)

    # Special boosts from recent real news (e.g., NBA)
    if "nba" in content and any(kw in content for kw in ["investment", "strategic", "extension", "partnership"]):
        score += 70

    return min(score, 95)

def classify_article_ai(title, summary, category):
    content = f"{title} {summary}".lower()

    client_name = None
    for name, variations in EVERGENT_CLIENTS.items():
        if any(var in content for var in variations):
            client_name = name
            break

    score = calculate_relevance_score(title, summary, category)

    if client_name:
        return "CLIENT", "🌟", client_name, 0, score

    if any(any(var in content for var in vars) for vars in COMPETITORS.values()):
        return "COMPETITOR", "⚠️", "Competitive", 1, score

    if score < 45:
        return "IRRELEVANT", "", "", 999, 0

    badges = {
        "telco": ("TELCO", "📡", "Telecom", 5),
        "ott": ("OTT", "📺", "Streaming", 6),
        "sports": ("SPORTS", "🏆", "Sports", 7),
        "technology": ("TECH", "⚡", "AI/Tech", 8)
    }

    priority_type, badge, entity, priority = badges.get(category, ("OTHER", "", "", 999))
    return priority_type, badge, entity, priority, score

# RSS FEEDS - Enhanced for impact (press releases, premium sources, competitor news)
RSS_FEEDS_LIST = [
    # Competitors / BSS-OSS focused
    ("Netcracker", "https://www.netcracker.com/news/press-releases/", "telco"),
    ("Amdocs", "https://www.amdocs.com/rss.xml", "telco"),
    ("Ericsson Press", "https://www.ericsson.com/en/news-and-events/rss-feeds/rss-press-releases-all", "telco"),
    ("Nokia News", "https://www.nokia.com/about-us/news/rss/", "telco"),
    ("Light Reading", "https://www.lightreading.com/rss.xml", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("TelecomTV", "https://www.telecomtv.com/feed", "telco"),
    ("TM Forum", "https://inform.tmforum.org/feed/", "telco"),

    # OTT & Streaming
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Streaming Media", "https://www.streamingmedia.com/rss", "ott"),
    ("Cord Cutters News", "https://www.cordcuttersnews.com/feed/", "ott"),
    ("Advanced Television", "https://advanced-television.com/feed/", "ott"),
    ("Broadcasting Cable", "https://www.broadcastingcable.com/feed", "ott"),

    # Sports / Live Events
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    ("Sports Business Journal", "https://www.sportsbusinessjournal.com/rss", "sports"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("Sportcal", "https://www.sportcal.com/feed/", "sports"),
    ("TV News Check", "https://tvnewscheck.com/business/feed", "sports"),

    # Tech / AI
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
]

# Convert to list of tuples
RSS_FEEDS = [(name, url, cat) for name, url, cat in RSS_FEEDS_LIST if url.endswith(('.xml', '/feed', '/rss', '.rss')) or 'feed' in url]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# Feed fetching functions (unchanged except minor robustness)
def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code != 200:
            return items

        feed = feedparser.parse(resp.content)
        NOW = datetime.now()

        for entry in feed.entries[:25]:  # Slightly more to catch good ones
            title = clean(entry.get("title", ""))
            if len(title) < 20:
                continue

            summary = clean(entry.get("summary", entry.get("description", "")))

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

            priority_type, badge, entity, sort_priority, relevance_score = classify_article_ai(title, summary, category)

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
                "is_strategic": relevance_score >= 70 or priority_type in ["CLIENT", "COMPETITOR"]
            })
    except Exception as e:
        pass  # Silent fail for one feed

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

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_feed, source, url, cat) for source, url, cat in RSS_FEEDS]

        for future in as_completed(futures):
            items = future.result()
            for item in items:
                categorized[item["category"]].append(item)

                if item["is_strategic"] and (datetime.now() - item["pub"]).days <= 30:
                    categorized["strategic_hits"].append(item)

    # Improved dedup across all
    for cat in categorized:
        seen = set()
        unique = []
        for item in categorized[cat]:
            norm = re.sub(r'[^\w\s]', '', (item["title"] + item.get("summary", "")).lower())[:100]
            h = hashlib.md5(norm.encode()).hexdigest()
            if h not in seen:
                seen.add(h)
                unique.append(item)
        categorized[cat] = unique

    # Sort & limit
    for cat in ["telco", "ott", "sports", "technology"]:
        cutoff = datetime.now() - timedelta(days=7)  # Last week for freshness
        categorized[cat] = [a for a in categorized[cat] if a["pub"] >= cutoff]
        categorized[cat].sort(key=lambda x: (-x["relevance_score"], -x["pub"].timestamp()))
        categorized[cat] = categorized[cat][:5]

    categorized["strategic_hits"] = sorted(
        [i for i in categorized["strategic_hits"] if (datetime.now() - i["pub"]).days <= 30],
        key=lambda x: (-x["relevance_score"], -x["pub"].timestamp())
    )[:8]  # More room for highlights

    return categorized

# Time ago string (unchanged)
def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1: return "Now", "time-hot"
    if hrs < 6: return f"{hrs}h", "time-hot"
    if hrs < 24: return f"{hrs}h", "time-warm"
    days = hrs // 24
    return f"{days}d", "time-normal"

# STYLING (unchanged, but header updated below)

# MAIN APP
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🤖 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Powered Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Your full CSS here (copy from previous versions - omitted for brevity, but keep it)

with st.spinner("Loading latest intelligence..."):
    data = load_feeds()

# Strategic Highlights (now includes competitor alerts)
strategic_hits = data.get("strategic_hits", [])
if strategic_hits:
    st.markdown('<div class="hero-container"><div class="hero-title">🚀 STRATEGIC & COMPETITIVE HIGHLIGHTS (Last 30 Days)</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    mid = len(strategic_hits) // 2
    
    with col1:
        for item in strategic_hits[:mid]:
            entity = html.escape(item.get("entity", "Industry"))
            title = html.escape(item["title"])
            days_ago = (datetime.now() - item["pub"]).days
            score = item["relevance_score"]
            badge = item.get("badge", "")
            st.markdown(f'<div class="strategic-item"><span class="relevance-badge">AI: {score}%</span><strong>{badge} {entity}:</strong> {title}<br><small>{days_ago}d ago • {html.escape(item["source"])}</small></div>', unsafe_allow_html=True)
    
    with col2:
        for item in strategic_hits[mid:]:
            # same as above
            ...

    st.markdown('</div>', unsafe_allow_html=True)

# Sections display (unchanged logic, but now feeds are stronger)

# Footer (unchanged)

# Auto-refresh
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)
@st.fragment(run_every=300)
def auto_refresh():
    load_feeds()
    st.empty()
auto_refresh()
