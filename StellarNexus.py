import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import hashlib

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus – AI Powered Real-time Competitive Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Health check
if st.query_params.get("ping") == "1":
    st.write("alive")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# CONTENT FILTER
# ─────────────────────────────────────────────────────────────────────────────
BLACKLIST_WORDS = [
    "sexual", "porn", "xxx", "adult", "explicit", "nude", "nsfw",
    "murder", "killing", "shooter", "terrorist", "massacre", "rape", "assault",
    "scandal", "affair", "divorce", "lawsuit", "fraud", "corruption",
    "celebrity breakup", "dating rumors", "feud", "controversy",
    "casino", "gambling", "tobacco", "drug", "overdose",
    "ponzi", "scam", "pyramid scheme", "crypto crash", "gossip", "rumor",
    "score", "injury", "fantasy", "betting"
]

def is_content_appropriate(title, summary=""):
    content = f"{title} {summary}".lower()
    return not any(word in content for word in BLACKLIST_WORDS)

# ─────────────────────────────────────────────────────────────────────────────
# EVERGENT DATA – PASTE YOUR FULL DICTS HERE
# ─────────────────────────────────────────────────────────────────────────────
EVERGENT_CLIENTS = {
    "Astro": ["astro malaysia", "astro sooka", "astro njoi", "astro", "sooka", "njoi"],
    "MongolTV": ["mongoltv", "mongol tv", "mongolia tv"],
    "FOX": ["fox sports", "fox corporation", "fox networks", "fox"],
    "AT&T": ["at&t", "att inc", "att wireless", "directv"],
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
    # Add remaining if needed
}

COMPETITORS = {
    "Netcracker": ["netcracker", "netcracker technology", "nec netcracker"],
    "Amdocs": ["amdocs", "amdocs ltd", "amdocs inc"],
    "CSG": ["csg systems", "csg international", "csg"],
    "Oracle": ["oracle communications", "oracle corporation", "oracle telecom"],
    "Ericsson": ["ericsson", "telefonaktiebolaget lm ericsson"],
    "Nokia": ["nokia", "nokia networks", "nokia corporation"],
    "Huawei": ["huawei", "huawei technologies"],
    # Add remaining
}

TOP_TELCOS = {
    "Verizon": ["verizon", "verizon wireless", "verizon fios"],
    "AT&T": ["at&t", "att mobility"],
    "T-Mobile": ["t-mobile", "tmobile usa", "sprint"],
    "Reliance Jio": ["reliance jio", "jio", "jio platforms"],
    # Add remaining
}

# Scoring signals (unchanged)
TELCO_SIGNALS = { ... }  # ← keep your original dicts here
OTT_SIGNALS   = { ... }
SPORTS_SIGNALS = { ... }
AI_SIGNALS    = { ... }

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

    score += sum(50 for kw in signals.get("tier1", []) if kw in content)
    score += sum(25 for kw in signals.get("tier2", []) if kw in content)
    score += sum(10 for kw in signals.get("tier3", []) if kw in content)

    # Boosts
    if any(any(v in content for v in vs) for vs in EVERGENT_CLIENTS.values()):
        score += 80

    if any(any(v in content for v in vs) for vs in COMPETITORS.values()):
        score += 60

    if any(any(v in content for v in vs) for vs in TOP_TELCOS.values()):
        score += 30

    action_keywords = [
        "acquisition", "merger", "partnership", "deal", "extension", "investment", "strategic",
        "wins", "award", "deploy", "scale", "growth", "churn reduction", "monetization",
        "subscriber growth", "arpu", "billing transformation", "oss transformation", "5g monetization",
        "real-time charging", "revenue management", "content deal", "media rights"
    ]
    score += sum(20 for kw in action_keywords if kw in content)

    return min(score, 100)

def classify_article_ai(title, summary, category):
    content = f"{title} {summary}".lower()
    score = calculate_relevance_score(title, summary, category)

    if score < 50:
        return "IRRELEVANT", "", "", 999

    if any(any(v in content for v in vs) for vs in EVERGENT_CLIENTS.values()):
        return "CLIENT", "🌟", "Strategic", 0

    if any(any(v in content for v in vs) for vs in COMPETITORS.values()):
        return "COMPETITOR", "⚠️", "Competitive", 1

    badges = {
        "telco":      ("TELCO",  "📡", 5),
        "ott":        ("OTT",    "📺", 6),
        "sports":     ("SPORTS", "🏆", 7),
        "technology": ("TECH",   "⚡", 8)
    }

    tag, icon, prio = badges.get(category, ("", "", 999))
    return tag, icon, prio

# ─────────────────────────────────────────────────────────────────────────────
# RSS FEEDS
# ─────────────────────────────────────────────────────────────────────────────
RSS_FEEDS = [
    ("Telecoms.com", "https://www.telecoms.com/feed", "telco"),
    ("Light Reading", "https://www.lightreading.com/rss/simple", "telco"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml", "telco"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed", "telco"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/", "telco"),
    ("Variety", "https://variety.com/feed/", "ott"),
    ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/", "ott"),
    ("Deadline", "https://deadline.com/feed/", "ott"),
    ("Streaming Media", "https://www.streamingmedia.com/rss", "ott"),
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    ("SportsPro", "https://www.sportspromedia.com/feed/", "sports"),
    ("SportBusiness", "https://www.sportbusiness.com/feed/", "sports"),
    ("TV News Check", "https://tvnewscheck.com/business/feed", "sports"),
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, */*"
}

def clean(raw):
    if not raw: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def fetch_feed(source, url, cat):
    items = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if r.status_code != 200: return items

        feed = feedparser.parse(r.content)
        now = datetime.now()

        for e in feed.entries[:25]:
            title = clean(e.get("title", ""))
            if len(title) < 30: continue

            summary = clean(e.get("summary") or e.get("description", ""))
            if not is_content_appropriate(title, summary): continue

            link = e.get("link", "")
            pub = now
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(e, k, None)
                if val:
                    try: pub = datetime(*val[:6])
                    except: pass
                    break

            tag, badge, prio = classify_article_ai(title, summary, cat)
            if tag == "IRRELEVANT": continue

            score = calculate_relevance_score(title, summary, cat)

            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary,
                "category": cat,
                "tag": tag,
                "badge": badge,
                "prio": prio,
                "score": score,
                "is_evergent": tag == "CLIENT"
            })
    except:
        pass
    return items

@st.cache_data(ttl=240, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}

    with ThreadPoolExecutor(max_workers=16) as ex:
        futures = [ex.submit(fetch_feed, s, u, c) for s,u,c in RSS_FEEDS]
        for f in as_completed(futures):
            for item in f.result():
                categorized[item["category"]].append(item)

    # Deduplicate
    for cat in categorized:
        seen = set()
        unique = []
        for item in categorized[cat]:
            key = hashlib.md5(
                re.sub(r'\W+', '', (item["title"] + item["summary"]).lower()).encode()
            ).hexdigest()
            if key not in seen:
                seen.add(key)
                unique.append(item)
        categorized[cat] = unique

    # Sort: Evergent news ALWAYS first, then highest score → newest
    for cat in categorized:
        cutoff = datetime.now() - timedelta(days=10)
        items = [x for x in categorized[cat] if x["pub"] >= cutoff]

        # Split: Evergent first
        evergent_items = [x for x in items if x["is_evergent"]]
        other_items    = [x for x in items if not x["is_evergent"]]

        # Sort each group
        evergent_items.sort(key=lambda x: (-x["score"], -x["pub"].timestamp()))
        other_items.sort(key=lambda x: (-x["score"], -x["pub"].timestamp()))

        # Combine: Evergent on top
        categorized[cat] = evergent_items + other_items[:6 - len(evergent_items)]
        categorized[cat] = categorized[cat][:6]  # max 6 per section

    return categorized

def time_ago(dt):
    secs = (datetime.now() - dt).total_seconds()
    if secs < 3600:    return "Now", "hot"
    if secs < 21600:   return f"{int(secs//3600)}h", "hot"
    if secs < 86400:   return f"{int(secs//3600)}h", "warm"
    return f"{int(secs//86400)}d", "normal"

# ─────────────────────────────────────────────────────────────────────────────
# STYLING – CLEAN LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', sans-serif;
    }

    .header {
        background: rgba(15, 23, 42, 0.92);
        backdrop-filter: blur(12px);
        padding: 2.2rem 3rem;
        border-radius: 16px;
        text-align: center;
        margin: 1.5rem 0 2.5rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    .title {
        font-size: 3.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a5b4fc, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    .subtitle {
        font-size: 1.15rem;
        color: #cbd5e1;
        margin-top: 0.6rem;
        font-weight: 500;
    }

    .section-header {
        font-size: 1.35rem;
        font-weight: 700;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px 12px 0 0;
        margin-bottom: 0;
    }

    .section-body {
        background: rgba(30, 41, 59, 0.88);
        border-radius: 0 0 12px 12px;
        padding: 1.2rem;
        min-height: 420px;
        overflow-y: auto;
    }

    .news-card {
        background: rgba(59, 69, 94, 0.45);
        border: 1px solid rgba(148, 163, 184, 0.3);
        border-radius: 10px;
        padding: 1.1rem;
        margin-bottom: 0.9rem;
        transition: all 0.22s ease;
    }

    .news-card:hover {
        background: rgba(79, 89, 114, 0.6);
        border-color: #818cf8;
        transform: translateY(-2px);
    }

    .news-title {
        color: #e0f2fe;
        font-size: 1.05rem;
        font-weight: 600;
        line-height: 1.4;
        text-decoration: none;
        display: block;
        margin-bottom: 0.5rem;
    }

    .news-title:hover { color: #c7d2fe; }

    .news-meta {
        font-size: 0.82rem;
        color: #94a3b8;
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }

    .time-hot   { color: #f87171; font-weight: 600; }
    .time-warm  { color: #fb923c; font-weight: 600; }
    .time-normal{ color: #94a3b8; }

    #MainMenu, footer, header { visibility: hidden !important; }
    .stDeployButton { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header">
    <div class="title">Global Telecom & OTT Stellar Nexus</div>
    <div class="subtitle">AI Powered Real-time Competitive Intelligence Dashboard</div>
</div>
""", unsafe_allow_html=True)

with st.spinner("Loading latest intelligence…"):
    data = load_feeds()

# ── MAIN SECTIONS ──
cols = st.columns(4)

section_cfg = {
    "telco":      {"name":"TELCO OSS/BSS",      "color":"#ec4899", "icon":"📡"},
    "ott":        {"name":"OTT & STREAMING",    "color":"#a78bfa", "icon":"📺"},
    "sports":     {"name":"SPORTS MEDIA",       "color":"#34d399", "icon":"🏆"},
    "technology": {"name":"AI & TECHNOLOGY",    "color":"#fb923c", "icon":"⚡"},
}

for idx, (cat, cfg) in enumerate(section_cfg.items()):
    with cols[idx]:
        st.markdown(f"""
        <div class="section-header" style="background: {cfg['color']};">
            {cfg['icon']} {cfg['name']}
        </div>
        <div class="section-body">
        """, unsafe_allow_html=True)

        items = data.get(cat, [])
        if not items:
            st.markdown("<div style='text-align:center; color:#94a3b8; padding:80px 0;'>Monitoring...</div>", unsafe_allow_html=True)
        else:
            for item in items:
                tago, cls = time_ago(item["pub"])
                st.markdown(f"""
                <div class="news-card">
                    <a href="{html.escape(item['link'])}" target="_blank" class="news-title">
                        {item['badge']} {html.escape(item['title'])}
                    </a>
                    <div class="news-meta">
                        <span class="{cls}">{tago}</span>
                        <span>•</span>
                        <span>{html.escape(item['source'])}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="text-align:center; color:#cbd5e1; margin:3rem 0; padding:1.5rem; background:rgba(15,23,42,0.8); border-radius:12px;">
    <strong>AI Intelligence Active</strong>  • 
    Articles: {sum(len(data[c]) for c in section_cfg)}  • 
    Last update: {datetime.now().strftime('%H:%M:%S')}
</div>
""", unsafe_allow_html=True)

# Auto-refresh every 5 minutes
st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

@st.fragment(run_every=300)
def keep_alive():
    st.empty()

keep_alive()
