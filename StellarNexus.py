import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import re
import html
import time  # For rate limiting


# ==========================
# 🔐 CEO TOKEN SECURITY GATE (Using Streamlit Secrets)
# ==========================
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except FileNotFoundError:
    st.error("🔧 Missing secrets.toml – Add CEO_ACCESS_TOKEN in .streamlit/secrets.toml or Streamlit Cloud Secrets")
    st.stop()
except KeyError:
    st.error("🔧 CEO_ACCESS_TOKEN not found in secrets")
    st.stop()

# Get token from URL query parameter: ?token=Vijay
provided_token = st.query_params.get("token")
if provided_token is not None:
    provided_token = provided_token[0] if isinstance(provided_token, list) else provided_token
else:
    provided_token = ""

if provided_token != EXPECTED_TOKEN:
    st.error("⛔ Unauthorized access – Invalid or missing token")
    st.info("Append `?token=your_token` to the URL or contact admin.")
    st.stop()

# Simple rate limiting (anti-bot protection)
if "last_access" not in st.session_state:
    st.session_state.last_access = 0

now = time.time()
if now - st.session_state.last_access < 2:  # Less than 2 seconds
    st.warning("⏱ Too many requests – Please wait a moment.")
    st.stop()

st.session_state.last_access = now


st.set_page_config(
    page_title="🌐 Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === BEAUTIFUL HEADER WITH EVERGENT LOGO BESIDE TITLE ===
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #334155 100%);
        color: #e2e8f0;
    }
    #MainMenu, footer, header {visibility: hidden;}

    .header-container {
        background: linear-gradient(180deg, rgba(15,23,42,0.98), rgba(30,41,59,0.9));
        padding: 3rem 2rem 4rem;
        text-align: center;
        border-radius: 0 0 28px 28px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.5);
        margin-bottom: 3rem;
        border-bottom: 4px solid #3b82f6;
    }

    .logo-title-row {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
        flex-wrap: wrap;
    }

    .evergent-logo {
        height: 100px;
        filter: brightness(1.1) drop-shadow(0 6px 15px rgba(0,0,0,0.6));
    }

    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #60a5fa, #a78bfa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -1px;
    }

    .col-header-pink {
        background: linear-gradient(135deg, #ec4899, #db2777);
        padding: 18px 22px;
        border-radius: 18px 18px 0 0;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        box-shadow: 0 8px 20px rgba(236,72,153,0.4);
    }

    .col-header-purple {
        background: linear-gradient(135deg, #a78bfa, #7c3aed);
        padding: 18px 22px;
        border-radius: 18px 18px 0 0;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        box-shadow: 0 8px 20px rgba(167,139,250,0.4);
    }

    .col-header-green {
        background: linear-gradient(135deg, #34d399, #10b981);
        padding: 18px 22px;
        border-radius: 18px 18px 0 0;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        box-shadow: 0 8px 20px rgba(52,211,153,0.4);
    }

    .col-header-orange {
        background: linear-gradient(135deg, #fb923c, #f97316);
        padding: 18px 22px;
        border-radius: 18px 18px 0 0;
        color: white;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        box-shadow: 0 8px 20px rgba(251,146,60,0.4);
    }

    .col-body {
        background: rgba(255,255,255,0.97);
        border-radius: 0 0 18px 18px;
        padding: 22px;
        min-height: 640px;
        max-height: 740px;
        overflow-y: auto;
        box-shadow: 0 15px 35px rgba(0,0,0,0.25);
        backdrop-filter: blur(15px);
    }

    .news-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.4s ease;
        border-left: 6px solid #e2e8f0;
    }

    .news-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 16px 35px rgba(0,0,0,0.15);
        border-left-color: #3b82f6;
    }

    .news-card-priority {
        background: linear-gradient(135deg, #fffbeb, #fef3c7);
        border: 3px solid #fbbf24;
        border-left: 8px solid #f59e0b;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.4s ease;
    }

    .news-card-priority:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 45px rgba(251,191,36,0.4);
    }

    .news-title {
        color: #1e40af;
        font-size: 1.05rem;
        font-weight: 600;
        line-height: 1.5;
        text-decoration: none;
        display: block;
        margin-bottom: 12px;
    }

    .news-title:hover {
        color: #1d4ed8;
        text-decoration: underline;
    }

    .news-meta {
        font-size: 0.82rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
    }

    .time-hot { color: #dc2626; font-weight: 700; font-style: italic; }
    .time-warm { color: #ea580c; font-weight: 600; }
    .time-normal { color: #64748b; }

    .tag-netcracker {
        background: #dc2626;
        color: white;
        padding: 8px 16px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 800;
        animation: glow 2s infinite alternate;
    }

    @keyframes glow {
        from { box-shadow: 0 0 12px #dc2626; }
        to { box-shadow: 0 0 28px #dc2626, 0 0 40px #dc2626; }
    }

    .tag-client, .tag-competitor, .tag-telco {
        padding: 6px 14px;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    .tag-client { background: #fef3c7; color: #92400e; }
    .tag-competitor { background: #fee2e2; color: #dc2626; }
    .tag-telco { background: #dbeafe; color: #1d4ed8; }

    .footer-text {
        text-align: center;
        padding: 2.5rem 1rem;
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 4rem;
        border-top: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# === EVERGENT LOGO + ORIGINAL TITLE (SIDE BY SIDE) ===
st.markdown("""
<div class="header-container">
    <div class="logo-title-row">
        <img src="https://www.evergent.com/wp-content/uploads/2023/06/Evergent-Logo-Horizontal-White.png" class="evergent-logo" alt="Evergent Logo">
        <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    </div>
</div>
""", unsafe_allow_html=True)


# CLIENTS, COMPETITORS, TELCOS
EVERGENT_CLIENTS = {
    "Astro": ["astro malaysia", "astro sooka", "astro"],
    "FOX": ["fox sports", "fox corporation", "fox news"],
    "AT&T": ["at&t", "directv", "warner media"],
    "NBA": ["nba league", "national basketball"],
    "Shahid": ["shahid vip", "mbc shahid", "shahid"],
    "MBC": ["mbc group"],
    "Sony": ["sony liv", "sony pictures", "sony entertainment"],
    "BBC": ["bbc iplayer", "bbc studios"],
    "Sky": ["sky tv", "sky sports", "sky news", "comcast sky"],
    "Telekom Malaysia": ["telekom malaysia", "unifi tv", "tm unifi"],
    "Discovery": ["discovery+", "warner bros discovery", "discovery inc"],
    "ESPN": ["espn+", "espn networks"],
    "DAZN": ["dazn"],
    "Peacock": ["peacock", "nbcuniversal"],
    "Paramount+": ["paramount+", "paramount global", "cbs"],
    "HBO Max": ["hbo max", "max streaming"],
    "Netflix": ["netflix"],
    "Disney+": ["disney+", "disney plus", "hotstar"],
    "Amazon Prime": ["prime video", "amazon prime"],
    "TV3": ["tv3 malaysia", "media prima"],
    "ABS-CBN": ["abs-cbn"],
    "TRT": ["trt world"],
    "Viki": ["rakuten viki"],
    "beIN": ["bein sports", "bein media"],
    "Apple TV+": ["apple tv+", "apple tv plus"],
    "Hulu": ["hulu"],
    "Roku": ["roku"],
    "Tubi": ["tubi"],
    "Pluto TV": ["pluto tv"],
}

COMPETITORS = {
    "Netcracker": ["netcracker", "nec netcracker"],
    "Amdocs": ["amdocs"],
    "CSG": ["csg systems", "csg international"],
    "Oracle": ["oracle communications", "oracle bss", "oracle telecom"],
    "Ericsson": ["ericsson"],
    "Nokia": ["nokia"],
    "Huawei": ["huawei"],
    "Comarch": ["comarch"],
    "Tecnotree": ["tecnotree"],
    "MATRIXX": ["matrixx software"],
    "Optiva": ["optiva"],
    "Cerillion": ["cerillion"],
    "ZTE": ["zte corporation", "zte"],
    "Infosys": ["infosys"],
    "TCS": ["tata consultancy", "tcs"],
    "Wipro": ["wipro"],
    "Tech Mahindra": ["tech mahindra", "comviva"],
    "Accenture": ["accenture"],
    "Capgemini": ["capgemini"],
    "IBM": ["ibm"],
    "SAP": ["sap"],
    "Salesforce": ["salesforce"],
    "Microsoft": ["microsoft azure", "microsoft cloud"],
    "AWS": ["amazon web services", "aws"],
    "Google Cloud": ["google cloud"],
}

TOP_TELCOS = {
    "Verizon": ["verizon"],
    "T-Mobile": ["t-mobile"],
    "AT&T Telecom": ["at&t mobility", "at&t wireless"],
    "Vodafone": ["vodafone"],
    "Orange": ["orange telecom", "orange sa"],
    "Deutsche Telekom": ["deutsche telekom", "t-systems"],
    "Telefonica": ["telefonica", "movistar"],
    "Singtel": ["singtel"],
    "Airtel": ["bharti airtel", "airtel"],
    "Jio": ["reliance jio", "jio platforms"],
    "China Mobile": ["china mobile"],
    "China Telecom": ["china telecom"],
    "NTT": ["ntt docomo", "ntt communications"],
    "SoftBank": ["softbank"],
    "SK Telecom": ["sk telecom"],
    "Etisalat": ["etisalat", "e&"],
    "STC": ["saudi telecom", "stc group"],
    "MTN": ["mtn group"],
    "Telstra": ["telstra"],
    "Rogers": ["rogers communications"],
    "Bell Canada": ["bell canada", "bce"],
    "Du": ["du telecom"],
    "Ooredoo": ["ooredoo"],
    "Zain": ["zain"],
    "Maxis": ["maxis"],
    "Celcom": ["celcom"],
    "Globe Telecom": ["globe telecom"],
    "PLDT": ["pldt"],
    "Comcast": ["comcast"],
    "Charter": ["charter communications", "spectrum"],
    "BT Group": ["bt group", "british telecom"],
    "Telenor": ["telenor"],
    "Telia": ["telia company"],
    "Swisscom": ["swisscom"],
    "KPN": ["kpn"],
    "Proximus": ["proximus"],
    "América Móvil": ["america movil", "claro"],
    "Liberty Global": ["liberty global"],
    "Altice": ["altice"],
    "Lumen": ["lumen technologies"],
}

RSS_FEEDS = {
    "telco": [
        ("Netcracker Press", "https://rss.app/feeds/oyAS1q31oAma1iDX.xml"),
        ("Netcracker News", "https://rss.app/feeds/yjUOdJDmq92SORmi.xml"),
        ("Amdocs","https://rss.app/feeds/rszN8UooJxRHd9RT.xml"),
        ("CSG","https://rss.app/feeds/G5rBYt8g3kDv1FgU.xml"),
        ("Oracle","https://rss.app/feeds/MkInd3OSqWptsP2p.xml"),
        ("TELUS Communications","https://rss.app/feeds/xP8RlSJ5pdZh800p.xml"),
        ("Amdocs", "https://investors.amdocs.com/rss/news-releases.xml"),
        ("Ericsson", "https://www.ericsson.com/en/newsroom/rss"),
        ("TM Forum", "https://www.tmforum.org/feed/"),
        ("GSMA", "https://www.gsma.com/newsroom/feed/"),
        ("Telecoms.com", "https://telecoms.com/feed/"),
        ("Light Reading", "https://www.lightreading.com/rss.xml"),
        ("Fierce Telecom", "https://www.fiercetelecom.com/rss/xml"),
        ("RCR Wireless", "https://www.rcrwireless.com/feed"),
        ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
        ("Total Telecom", "https://www.totaltele.com/rss.xml"),
        ("Capacity Media", "https://www.capacitymedia.com/feed"),
        ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ],
    "ott": [
        ("Variety", "https://variety.com/feed/"),
        ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
        ("Deadline", "https://deadline.com/feed/"),
        ("Fierce Video", "https://www.fiercevideo.com/rss/xml"),
        ("Streaming Media", "https://www.streamingmedia.com/rss"),
        ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
        ("Rapid TV News", "https://www.rapidtvnews.com/rss.xml"),
        ("Advanced Television", "https://advanced-television.com/feed/"),
        ("Ampere Analysis", "https://www.ampereanalysis.com/rss"),
    ],
    "sports": [
        ("NBA News", "https://rss.app/feeds/ecdAVYD0y8xcaJ8K.xml"),
        ("ESPN", "https://www.espn.com/espn/rss/news"),
        ("Sports Business Journal", "https://www.sportsbusinessdaily.com/RSS/SBJ-RSS.xml"),
        ("SportTechie", "https://www.sporttechie.com/feed/"),
        ("Sky Sports", "https://www.skysports.com/rss/12040"),
        ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
        ("Sportico", "https://www.sportico.com/feed/"),
        ("Front Office Sports", "https://frontofficesports.com/feed/"),
        ("SportsPro", "https://www.sportspromedia.com/feed/"),
    ],
    "technology": [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("Wired", "https://www.wired.com/feed/rss"),
        ("Ars Technica", "https://arstechnica.com/feed/"),
        ("VentureBeat", "https://venturebeat.com/feed/"),
        ("ZDNet", "https://www.zdnet.com/news/rss.xml"),
        ("Engadget", "https://www.engadget.com/rss.xml"),
        ("Techmeme", "https://www.techmeme.com/feed.xml"),
    ],
}

SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header-orange"},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def classify(title, summary="", source=""):
    text = (title + " " + summary).lower()
    if "netcracker" in source.lower() or "netcracker" in text:
        return "NETCRACKER", "Netcracker", -1
    if "amdocs" in source.lower() or "amdocs" in text:
        return "COMPETITOR", "Amdocs", -1
    for name, kws in EVERGENT_CLIENTS.items():
        for kw in kws:
            if kw in text:
                return "CLIENT", name, 0
    for name, kws in COMPETITORS.items():
        for kw in kws:
            if kw in text:
                return "COMPETITOR", name, 1
    for name, kws in TOP_TELCOS.items():
        for kw in kws:
            if kw in text:
                return "TELCO", name, 2
    return "GENERAL", "", 999

def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def fetch_feed(source, url):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return items
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=30)
        EXCLUDE_KEYWORDS = ["thank you", "thanks", "gratitude", "appreciate", "grateful",
                            "goodbye", "farewell", "retiring", "retirement", "final message"]
        for entry in feed.entries[:30]:
            title = clean(entry.get("title", ""))
            if len(title) < 20:
                continue
            if any(x in title.lower() for x in ["click here", "subscribe", "download now", "sponsored"]):
                continue
            if any(kw in title.lower() for kw in EXCLUDE_KEYWORDS):
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
            if not pub or pub < CUTOFF:
                continue
            ptype, entity, priority = classify(title, summary, source)
            items.append({
                "title": title, "link": link, "pub": pub, "source": source,
                "ptype": ptype, "entity": entity, "priority": priority,
            })
    except:
        pass
    return items

@st.cache_data(ttl=600, show_spinner=False)
def load_feeds():
    data = {k: [] for k in RSS_FEEDS}
    jobs = []
    for cat, feeds in RSS_FEEDS.items():
        for name, url in feeds:
            jobs.append((cat, name, url))
    with ThreadPoolExecutor(max_workers=40) as pool:
        futures = {pool.submit(fetch_feed, name, url): cat for cat, name, url in jobs}
        for fut in as_completed(futures, timeout=60):
            cat = futures[fut]
            try:
                items = fut.result()
                data[cat].extend(items)
            except:
                pass
    for cat in data:
        seen = set()
        unique = []
        for item in data[cat]:
            h = hashlib.md5(item["title"].lower()[:60].encode()).hexdigest()
            if h not in seen:
                seen.add(h)
                unique.append(item)
        pinned = [item for item in unique if item["ptype"] in ("NETCRACKER", "COMPETITOR") and item["entity"] in ("Netcracker", "Amdocs")]
        others = [item for item in unique if item not in pinned]
        pinned.sort(key=lambda x: x["pub"].timestamp(), reverse=True)
        others.sort(key=lambda x: x["pub"].timestamp(), reverse=True)
        data[cat] = (pinned + others)[:50]
    return data

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1:
        return "Now", "time-hot"
    if hrs < 6:
        return f"{hrs}h", "time-hot"
    if hrs < 24:
        return f"{hrs}h", "time-warm"
    return f"{hrs//24}d", "time-normal"

def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")

def render_column(cat, items, sec):
    header = f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>'
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = escape_html(item["title"])
        safe_link = escape_html(item["link"])
        safe_source = escape_html(item["source"])
        card_class = "news-card-priority" if item.get("ptype") == "NETCRACKER" else "news-card"
        tag_html = ""
        if item.get("ptype") == "NETCRACKER":
            tag_html = '<span class="tag-netcracker">⚠️ NETCRACKER</span>'
        elif item["entity"] == "Amdocs":
            tag_html = '<span class="tag-competitor">Amdocs</span>'
        elif item["entity"]:
            safe_entity = escape_html(item["entity"])
            if item["ptype"] == "CLIENT":
                tag_html = f'<span class="tag-client">{safe_entity}</span>'
            elif item["ptype"] == "COMPETITOR":
                tag_html = f'<span class="tag-competitor">{safe_entity}</span>'
            elif item["ptype"] == "TELCO":
                tag_html = f'<span class="tag-telco">{safe_entity}</span>'
        cards += f'''<div class="{card_class}">
<a href="{safe_link}" target="_blank" class="news-title">{safe_title}</a>
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
{tag_html}
</div>
</div>'''
    if not items:
        cards = '<div style="text-align:center;color:#94a3b8;padding:30px;">No recent news</div>'
    body = f'<div class="col-body">{cards}</div>'
    return header + body

def main():
    with st.spinner("Loading latest feeds (Netcracker & Amdocs pinned on top)..."):
        data = load_feeds()
    cols = st.columns(4)
    cat_list = ["telco", "ott", "sports", "technology"]
    for idx, cat in enumerate(cat_list):
        sec = SECTIONS[cat]
        items = data.get(cat, [])
        with cols[idx]:
            st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
            column_html = render_column(cat, items, sec)
            st.markdown(column_html, unsafe_allow_html=True)
    netcracker_count = sum(1 for c in data.values() for i in c if i.get("ptype") == "NETCRACKER")
    st.markdown(f'<div class="footer-text">CEO Dashboard • ⚠️ {netcracker_count} Netcracker Updates • Last 48 hours • Auto-refresh: 10 min • {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
