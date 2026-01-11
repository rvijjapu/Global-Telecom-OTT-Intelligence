import streamlit as st
import feedparser
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re
import hashlib
from difflib import SequenceMatcher
import json

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG - MUST BE FIRST
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
# API KEY
# ══════════════════════════════════════════════════════════════════════════════
GROQ_API_KEY = "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"

# ══════════════════════════════════════════════════════════════════════════════
# EVERGENT CLIENTS - COMPLETE LIST
# ══════════════════════════════════════════════════════════════════════════════
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
}

# COMPETITORS
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

# TOP GLOBAL TELCOS
TOP_TELCOS = {
    "Verizon": ["verizon", "verizon wireless", "verizon fios"],
    "AT&T": ["at&t", "att mobility"],
    "T-Mobile": ["t-mobile", "tmobile usa", "sprint"],
    "Comcast": ["comcast", "xfinity", "comcast cable"],
    "BT": ["bt group", "british telecom", "bt", "bt enterprise", "ee"],
    "Vodafone": ["vodafone", "vodafone group"],
    "Orange": ["orange", "orange sa"],
    "Deutsche Telekom": ["deutsche telekom", "t-mobile europe", "telekom"],
    "Telefónica": ["telefonica", "telefonica spain", "movistar"],
    "Swisscom": ["swisscom", "swisscom ag"],
    "Singtel": ["singtel", "singapore telecom"],
    "Maxis": ["maxis", "maxis communications", "maxis malaysia"],
    "Telstra": ["telstra", "telstra corporation"],
    "NTT": ["ntt", "nippon telegraph", "ntt docomo"],
    "SoftBank": ["softbank", "softbank corp"],
    "Reliance Jio": ["reliance jio", "jio", "jio platforms"],
    "Airtel": ["bharti airtel", "airtel", "airtel india"],
    "Etisalat": ["etisalat", "emirates telecom", "e&"],
    "STC": ["stc", "saudi telecom", "saudi telecom company"],
    "Ooredoo": ["ooredoo", "ooredoo group"],
    "MTN": ["mtn group", "mtn"],
    "Safaricom": ["safaricom", "safaricom plc"],
    "Globe": ["globe telecom", "globe philippines"],
    "PLDT": ["pldt", "philippine long distance"],
    "Telus": ["telus", "telus communications"],
    "Rogers": ["rogers communications", "rogers"],
}

# OTT PLATFORMS
OTT_PLATFORMS = {
    "Netflix": ["netflix"], "Disney+": ["disney+", "disney plus", "hotstar"],
    "Prime Video": ["prime video", "amazon prime"], "HBO Max": ["hbo max", "max"],
    "Peacock": ["peacock"], "Paramount+": ["paramount+", "paramount plus"],
    "Apple TV+": ["apple tv+", "apple tv plus"], "Hulu": ["hulu"],
    "Roku": ["roku"], "Tubi": ["tubi"], "DAZN": ["dazn"],
    "ESPN+": ["espn+", "espn plus"], "YouTube TV": ["youtube tv"],
}

# SPORTS ENTITIES
SPORTS_ENTITIES = {
    "NBA": ["nba", "national basketball association"],
    "NFL": ["nfl", "national football league"],
    "MLB": ["mlb", "major league baseball"],
    "ESPN": ["espn"], "FanDuel": ["fanduel"], "DraftKings": ["draftkings"],
    "Bally Sports": ["bally sports", "bally"], "Premier League": ["premier league", "epl"],
    "UEFA": ["uefa", "champions league"], "UFC": ["ufc"], "Sky Sports": ["sky sports"],
}

# ══════════════════════════════════════════════════════════════════════════════
# RSS FEEDS
# ══════════════════════════════════════════════════════════════════════════════
RSS_FEEDS = {
    "telco": [
        ("Google OSS/BSS", "https://news.google.com/rss/search?q=(OSS+BSS+OR+%22operations+support+systems%22+OR+%22business+support+systems%22)+telecom&hl=en-US&gl=US&ceid=US:en"),
        ("Google Telecom", "https://news.google.com/rss/search?q=telecom+5G+network+operator&hl=en-US&gl=US&ceid=US:en"),
        ("Light Reading", "https://www.lightreading.com/rss/simple"),
        ("RCR Wireless", "https://www.rcrwireless.com/feed"),
        ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
        ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
        ("The Fast Mode", "https://www.thefastmode.com/rss-feeds"),
    ],
    "ott": [
        ("Google OTT", "https://news.google.com/rss/search?q=streaming+OTT+netflix+disney+hbo&hl=en-US&gl=US&ceid=US:en"),
        ("Variety", "https://variety.com/feed/"),
        ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
        ("Deadline", "https://deadline.com/feed/"),
        ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ],
    "sports": [
        ("Google Sports", "https://news.google.com/rss/search?q=sports+streaming+media+rights+betting&hl=en-US&gl=US&ceid=US:en"),
        ("ESPN", "https://www.espn.com/espn/rss/news"),
        ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
        ("Sportico", "https://www.sportico.com/feed/"),
    ],
    "technology": [
        ("Google Tech", "https://news.google.com/rss/search?q=5G+AI+cloud+telecom+technology&hl=en-US&gl=US&ceid=US:en"),
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("VentureBeat", "https://venturebeat.com/feed/"),
    ],
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ══════════════════════════════════════════════════════════════════════════════
# STYLING + YOUR BACKGROUND IMAGE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        color: #1e293b;
        padding-top: 0.5rem;
    }
    .header-container {
        background: rgba(255,255,255,0.98);
        padding: 1.5rem 2rem;
        text-align: center;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        margin: 0 0 1.5rem 0;
        border-bottom: 4px solid #3b82f6;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-top: 0.4rem;
    }
    .col-header {
        padding: 14px 16px;
        border-radius: 14px 14px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #8b5cf6);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #10b981);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #f97316);}
    .col-body {
        background: white;
        border-radius: 0 0 14px 14px;
        padding: 12px;
        min-height: 600px;
        max-height: 750px;
        overflow-y: auto;
        box-shadow: 0 6px 24px rgba(0,0,0,0.08);
    }
    .highlight-card {
        background: linear-gradient(135deg, #fafbfc 0%, #ffffff 100%);
        border: 1px solid #e2e8f0;
        border-left: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    .highlight-card:hover {
        background: linear-gradient(135deg, #f1f5f9 0%, #ffffff 100%);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    .highlight-card.pink {border-left-color: #ec4899;}
    .highlight-card.purple {border-left-color: #8b5cf6;}
    .highlight-card.green {border-left-color: #10b981;}
    .highlight-card.orange {border-left-color: #f97316;}
    .highlight-title {
        color: #1e293b;
        font-size: 0.92rem;
        font-weight: 700;
        margin-bottom: 8px;
        line-height: 1.3;
    }
    .highlight-description {
        color: #475569;
        font-size: 0.85rem;
        line-height: 1.5;
        margin-bottom: 8px;
    }
    .read-more {
        color: #2563eb;
        font-weight: 600;
        font-size: 0.85rem;
        text-decoration: none;
        display: block;
        margin-top: 8px;
    }
    .read-more:hover {
        color: #1d4ed8;
    }
    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 20px;
        padding: 15px;
    }
    .loading-container {
        text-align: center;
        padding: 100px 20px;
        background: rgba(255,255,255,0.9);
        border-radius: 20px;
    }
    .loading-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #f97316;
        margin-bottom: 10px;
    }
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def clean(raw):
    if not raw: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def extract_summary(entry, max_len=400):
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and content:
                content = content[0].get('value', '')
            summary = clean(content)
            if summary: return summary[:max_len] + ('...' if len(summary) > max_len else '')
    return ""

def detect_client(text, section):
    text_lower = text.lower()
    sources = {
        "telco": {**EVERGENT_CLIENTS, **COMPETITORS, **TOP_TELCOS},
        "ott": {**EVERGENT_CLIENTS, **OTT_PLATFORMS},
        "sports": {**EVERGENT_CLIENTS, **SPORTS_ENTITIES},
        "technology": {**COMPETITORS, **TOP_TELCOS}
    }
    for name, keywords in sources.get(section, {}).items():
        if any(k in text_lower for k in keywords):
            return name
    return None

# ══════════════════════════════════════════════════════════════════════════════
# FEED FETCHING
# ══════════════════════════════════════════════════════════════════════════════
def fetch_feed(source, url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200: return []
        feed = feedparser.parse(resp.content)
        items = []
        for entry in feed.entries[:20]:
            title = clean(entry.get("title", ""))
            if len(title) < 20: continue
            items.append({"title": title, "source": source, "summary": extract_summary(entry)})
        return items
    except: return []

@st.cache_data(ttl=300)
def fetch_all_news():
    all_news = {}
    for section, feeds in RSS_FEEDS.items():
        items = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            for result in executor.map(lambda f: fetch_feed(*f), feeds):
                items.extend(result)
        all_news[section] = items[:30]
    return all_news

# ══════════════════════════════════════════════════════════════════════════════
# AI HIGHLIGHTS - 12+ with Read More
# ══════════════════════════════════════════════════════════════════════════════
def generate_highlights_ai(news_items, section, section_name):
    if not news_items: return []
    news_text = "\n".join([f"- {n['title']}: {n.get('summary','')[:150]}" for n in news_items[:20]])
    
    clients = {
        "telco": list(EVERGENT_CLIENTS.keys()) + list(COMPETITORS.keys())[:10] + list(TOP_TELCOS.keys())[:15],
        "ott": list(EVERGENT_CLIENTS.keys()) + list(OTT_PLATFORMS.keys()),
        "sports": ["NBA", "FanDuel", "Bally Sports", "ESPN", "FOX"] + list(SPORTS_ENTITIES.keys()),
        "technology": list(COMPETITORS.keys())[:15] + list(TOP_TELCOS.keys())[:10]
    }
    
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": f"You are a {section_name} analyst. Focus on: {', '.join(clients.get(section,[])[:30])}. Only use real company/operator names."},
                    {"role": "user", "content": f"Create 12 client highlights from this news. No duplicates, latest only, no generic tags like Industry/Amdocs. Return JSON: {{\"highlights\": [{{\"title\": \"Client/Partner\", \"description\": \"2-3 sentences benefit/impact\", \"source_link\": \"original news url\"}}]}}\n\nNews:\n{news_text}"}
                ],
                "max_tokens": 2000,
                "temperature": 0.4
            }, timeout=45)
        
        if resp.status_code == 200:
            match = re.search(r'\{[\s\S]*\}', resp.json()["choices"][0]["message"]["content"])
            if match: return json.loads(match.group()).get("highlights", [])[:15]
    except: pass
    
    # Fallback - clean, no tags
    return [{"title": detect_client(n["title"], section) or n["source"], "description": n["title"][:120] + "...", "source_link": n.get("link", "#")} for n in news_items[:12]]

@st.cache_data(ttl=300)
def get_highlights(section, name, news_hash):
    return generate_highlights_ai(st.session_state.get(f"news_{section}", []), section, name)

# ══════════════════════════════════════════════════════════════════════════════
# RENDER
# ══════════════════════════════════════════════════════════════════════════════
def render_card(h, color):
    title = html.escape(h.get("title", "Client"))
    desc = html.escape(h.get("description", ""))
    link = html.escape(h.get("source_link", "#"))
    return f'''
    <div class="highlight-card {color}">
        <div class="highlight-title">{title}</div>
        <div class="highlight-description">{desc}</div>
        <a href="{link}" target="_blank" class="read-more">Read More →</a>
    </div>
    '''

def render_section(icon, name, highlights, hdr_class, color):
    cards = "".join([render_card(h, color) for h in (highlights or [])])
    return f'''
    <div class="col-header {hdr_class}"><span>{icon}</span><span>{name}</span></div>
    <div class="col-body">{cards or "<p style=\"text-align:center;color:#999;padding:40px;\">Loading...</p>"}</div>
    '''

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="header-container"><h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1><p class="subtitle">AI-Powered Competitive Intelligence for CEO</p></div>', unsafe_allow_html=True)

# Fetch & Generate
all_news = fetch_all_news()
for sec in all_news:
    st.session_state[f"news_{sec}"] = all_news[sec]

highlights = {}
for sec, name in [("telco","Telco OSS/BSS"), ("ott","OTT & Streaming"), ("sports","Sports & Events"), ("technology","Technology")]:
    highlights[sec] = generate_highlights_ai(all_news.get(sec,[]), sec, name)

# Display
c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown(render_section("📡", "Telco OSS/BSS", highlights.get("telco",[]), "col-header-pink", "pink"), unsafe_allow_html=True)
with c2: st.markdown(render_section("📺", "OTT & Streaming", highlights.get("ott",[]), "col-header-purple", "purple"), unsafe_allow_html=True)
with c3: st.markdown(render_section("🏆", "Sports & Events", highlights.get("sports",[]), "col-header-green", "green"), unsafe_allow_html=True)
with c4: st.markdown(render_section("⚡", "Technology", highlights.get("technology",[]), "col-header-orange", "orange"), unsafe_allow_html=True)

st.markdown(f'<div class="footer"><p>Last Updated: {datetime.now().strftime("%I:%M:%S %p")} • Auto-refreshes every 5 minutes</p></div>', unsafe_allow_html=True)

st.markdown("<script>setTimeout(function(){window.location.reload();},300000);</script>", unsafe_allow_html=True)
