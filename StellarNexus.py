import streamlit as st
import feedparser
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re
from zoneinfo import ZoneInfo
import hashlib
from difflib import SequenceMatcher
import json

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG - FIRST LINE
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
# YOUR COMPLETE ENTITY DATABASES (unchanged)
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

OTT_PLATFORMS = {
    "Netflix": ["netflix"], "Disney+": ["disney+", "disney plus", "hotstar"],
    "Prime Video": ["prime video", "amazon prime"], "HBO Max": ["hbo max", "max"],
    "Peacock": ["peacock"], "Paramount+": ["paramount+", "paramount plus"],
    "Apple TV+": ["apple tv+", "apple tv plus"], "Hulu": ["hulu"],
    "Roku": ["roku"], "Tubi": ["tubi"], "DAZN": ["dazn"],
    "ESPN+": ["espn+", "espn plus"], "YouTube TV": ["youtube tv"],
}

SPORTS_ENTITIES = {
    "NBA": ["nba", "national basketball association"],
    "NFL": ["nfl", "national football league"],
    "MLB": ["mlb", "major league baseball"],
    "ESPN": ["espn"], "FanDuel": ["fanduel"], "DraftKings": ["draftkings"],
    "Bally Sports": ["bally sports", "bally"], "Premier League": ["premier league", "epl"],
    "UEFA": ["uefa", "champions league"], "UFC": ["ufc"], "Sky Sports": ["sky sports"],
}

# ══════════════════════════════════════════════════════════════════════════════
# RSS FEEDS (your original)
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
# UTILITY FUNCTIONS (optimized)
# ══════════════════════════════════════════════════════════════════════════════
def clean(raw):
    if not raw: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def extract_summary(entry):
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and content:
                content = content[0].get('value', '')
            summary = clean(content)
            if summary: return summary[:400] + ('...' if len(summary) > 400 else '')
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

def fetch_feed(source, url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code != 200: return []
        feed = feedparser.parse(resp.content)
        items = []
        for entry in feed.entries[:15]:  # Reduced for speed
            title = clean(entry.get("title", ""))
            if len(title) < 20: continue
            link = entry.get("link", "")
            if not link: continue
            summary = extract_summary(entry)
            items.append({"title": title, "link": link, "source": source, "summary": summary})
        return items
    except:
        return []

@st.cache_data(ttl=180)  # Faster cache refresh
def load_all_news():
    all_news = {}
    for section, feeds in RSS_FEEDS.items():
        items = []
        with ThreadPoolExecutor(max_workers=6) as executor:  # Reduced workers for speed
            for result in executor.map(lambda f: fetch_feed(*f), feeds):
                items.extend(result)
        # Light duplicate removal
        seen = set()
        unique = []
        for item in items:
            h = hashlib.md5(item["title"].encode()).hexdigest()
            if h not in seen:
                seen.add(h)
                unique.append(item)
        all_news[section] = unique[:25]  # Limit per section
    return all_news

# AI Highlights - Fast, 12+ with Read More
def generate_highlights(news_items):
    if not news_items: return []
    news_text = "\n".join([f"- {n['title']} ({n['source']})" for n in news_items[:30]])
    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",  # Fast model
                "messages": [
                    {"role": "system", "content": "Extract 12+ unique client/partner/operator highlights from news. Use real names only. Format as JSON."},
                    {"role": "user", "content": f"""From these headlines, create 12+ client highlights (no duplicates, latest only).
Each: client name + 1-2 sentence benefit/impact + source link.

News:
{news_text}

Return JSON only:
{{"highlights": [{{"client": "Company", "description": "Impact", "source_link": "url"}}]}}
"""}
                ],
                "max_tokens": 1800,
                "temperature": 0.35
            },
            timeout=30
        )
        if r.status_code == 200:
            content = r.json()["choices"][0]["message"]["content"]
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                return json.loads(match.group()).get("highlights", [])[:15]
    except:
        pass
    # Fallback
    return [{"client": n["source"], "description": n["title"][:120] + "...", "source_link": n.get("link", "#")} for n in news_items[:12]]

# Render functions
def render_highlight(h):
    client = html.escape(h.get("client", "Client"))
    desc = html.escape(h.get("description", ""))
    link = html.escape(h.get("source_link", "#"))
    return f'''
    <div class="highlight-card">
        <div class="highlight-title">{client}</div>
        <div class="highlight-desc">{desc}</div>
        <a href="{link}" target="_blank" class="read-more">Read More →</a>
    </div>
    '''

def render_section(icon, name, highlights, color_class):
    cards = "".join([render_highlight(h) for h in highlights])
    return f'''
    <div class="col-header {color_class}">{icon} {name}</div>
    <div class="col-body">{cards or '<div style="text-align:center;padding:80px;color:#999;">Loading highlights...</div>'}</div>
    '''

# MAIN DASHBOARD
st.markdown('<div class="header-container"><h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1><p class="subtitle">AI-Powered Competitive Intelligence for CEO</p></div>', unsafe_allow_html=True)

placeholder = st.empty()
placeholder.markdown("""
<div style="text-align:center; padding:140px 20px; background:rgba(255,255,255,0.92); border-radius:24px; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
    <h2 style="color:#1e40af; font-size:1.9rem;">Igniting AI-Powered Intelligence...</h2>
    <p style="color:#64748b;">Fetching real-time telecom, OTT, sports & tech highlights</p>
</div>
""", unsafe_allow_html=True)

with st.spinner(""):
    all_news = load_all_news()
    highlights = {}
    for sec in ["telco", "ott", "sports", "technology"]:
        highlights[sec] = generate_highlights(all_news.get(sec, []))

placeholder.empty()

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(render_section("📡", "Telco OSS/BSS", highlights["telco"], "col-header-pink"), unsafe_allow_html=True)
with c2: st.markdown(render_section("📺", "OTT & Streaming", highlights["ott"], "col-header-purple"), unsafe_allow_html=True)
with c3: st.markdown(render_section("🏆", "Sports & Events", highlights["sports"], "col-header-green"), unsafe_allow_html=True)
with c4: st.markdown(render_section("⚡", "Technology", highlights["technology"], "col-header-orange"), unsafe_allow_html=True)

st.markdown('<div class="footer">Last Updated: ' + datetime.now().strftime("%I:%M:%S %p") + ' • Auto-refreshes every 5 min</div>', unsafe_allow_html=True)

# Auto-refresh + anti-sleep
st.markdown("""
<script>
setInterval(() => { window.location.reload(); }, 300000);
setInterval(() => { fetch('/'); }, 60000); // Keep-alive ping
</script>
""", unsafe_allow_html=True)
