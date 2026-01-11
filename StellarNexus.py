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
# KEEP ALIVE - PREVENTS STREAMLIT SLEEP
# ══════════════════════════════════════════════════════════════════════════════
if 'keep_alive' not in st.session_state:
    st.session_state.keep_alive = datetime.now()

# ══════════════════════════════════════════════════════════════════════════════
# API KEY
# ══════════════════════════════════════════════════════════════════════════════
GROQ_API_KEY = "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"

# ══════════════════════════════════════════════════════════════════════════════
# ENTITY DATABASES
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
    "Sinclair": ["sinclair broadcast", "sinclair"],
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
    "Telekom Malaysia": ["telekom malaysia", "tm unifi", "unifi tv"],
    "Britbox": ["britbox", "britbox international"],
    "Quickplay": ["quickplay", "quickplay media"],
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
    "BT": ["bt group", "british telecom", "bt enterprise", "ee"],
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
    "Rakuten": ["rakuten", "rakuten mobile"],
    "Omantel": ["omantel", "oman telecommunications"],
    "Zain": ["zain", "zain group"],
    "Axiata": ["axiata", "axiata group"],
}

OTT_PLATFORMS = {
    "Netflix": ["netflix"], "Disney+": ["disney+", "disney plus", "hotstar"],
    "Prime Video": ["prime video", "amazon prime"], "HBO Max": ["hbo max", "max"],
    "Peacock": ["peacock"], "Paramount+": ["paramount+", "paramount plus"],
    "Apple TV+": ["apple tv+", "apple tv plus"], "Hulu": ["hulu"],
    "Roku": ["roku"], "Tubi": ["tubi"], "DAZN": ["dazn"],
    "ESPN+": ["espn+", "espn plus"], "YouTube TV": ["youtube tv"],
    "Pluto TV": ["pluto tv"], "Crunchyroll": ["crunchyroll"],
}

SPORTS_ENTITIES = {
    "NBA": ["nba", "national basketball association"],
    "NFL": ["nfl", "national football league"],
    "MLB": ["mlb", "major league baseball"],
    "NHL": ["nhl", "national hockey league"],
    "ESPN": ["espn"], "FanDuel": ["fanduel"], "DraftKings": ["draftkings"],
    "Bally Sports": ["bally sports", "bally"], "Premier League": ["premier league", "epl"],
    "UEFA": ["uefa", "champions league"], "UFC": ["ufc"], "Sky Sports": ["sky sports"],
    "F1": ["formula 1", "f1"], "WWE": ["wwe", "world wrestling"],
    "PGA": ["pga", "pga tour"], "FIFA": ["fifa"],
}

# ══════════════════════════════════════════════════════════════════════════════
# RSS FEEDS
# ══════════════════════════════════════════════════════════════════════════════
RSS_FEEDS = {
    "telco": [
        ("Google OSS/BSS", "https://news.google.com/rss/search?q=(OSS+BSS+OR+telecom+billing+OR+BSS+transformation)+when:7d&hl=en-US&gl=US&ceid=US:en"),
        ("Google 5G", "https://news.google.com/rss/search?q=(5G+network+OR+telecom+operator)+when:7d&hl=en-US&gl=US&ceid=US:en"),
        ("Light Reading", "https://www.lightreading.com/rss/simple"),
        ("RCR Wireless", "https://www.rcrwireless.com/feed"),
        ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
        ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
        ("The Fast Mode", "https://www.thefastmode.com/rss-feeds"),
    ],
    "ott": [
        ("Google Streaming", "https://news.google.com/rss/search?q=(streaming+OR+OTT+OR+netflix+OR+disney)+when:7d&hl=en-US&gl=US&ceid=US:en"),
        ("Variety", "https://variety.com/feed/"),
        ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
        ("Deadline", "https://deadline.com/feed/"),
        ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ],
    "sports": [
        ("Google Sports", "https://news.google.com/rss/search?q=(sports+media+OR+sports+streaming+OR+sports+betting)+when:7d&hl=en-US&gl=US&ceid=US:en"),
        ("ESPN", "https://www.espn.com/espn/rss/news"),
        ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
        ("Sportico", "https://www.sportico.com/feed/"),
    ],
    "technology": [
        ("Google Tech", "https://news.google.com/rss/search?q=(5G+AI+cloud+telecom)+when:7d&hl=en-US&gl=US&ceid=US:en"),
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("VentureBeat", "https://venturebeat.com/feed/"),
    ],
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# ══════════════════════════════════════════════════════════════════════════════
# STYLING
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp {background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; color: #1e293b;}
    .header-container {background: rgba(255,255,255,0.97); padding: 1.2rem 2rem; text-align: center; border-radius: 18px; box-shadow: 0 6px 28px rgba(0,0,0,0.1); margin: 0 0 1.2rem 0; border-bottom: 4px solid #3b82f6;}
    .main-title {font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #1e40af, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;}
    .subtitle {font-size: 0.95rem; color: #64748b; margin-top: 0.3rem;}
    .col-header {padding: 12px 14px; border-radius: 12px 12px 0 0; color: white; font-weight: 700; font-size: 0.9rem; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.12); display: flex; align-items: center; justify-content: center; gap: 6px;}
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #8b5cf6);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #10b981);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #f97316);}
    .highlight-count {background: rgba(255,255,255,0.25); padding: 2px 8px; border-radius: 10px; font-size: 0.7rem;}
    .col-body {background: rgba(255,255,255,0.98); border-radius: 0 0 12px 12px; padding: 10px; min-height: 620px; max-height: 720px; overflow-y: auto; box-shadow: 0 6px 20px rgba(0,0,0,0.08);}
    .highlight-card {background: linear-gradient(135deg, #fafbfc, #ffffff); border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; border-radius: 8px; padding: 12px; margin-bottom: 10px; transition: all 0.15s ease;}
    .highlight-card:hover {background: #f8fafc; box-shadow: 0 4px 16px rgba(0,0,0,0.08); transform: translateY(-1px);}
    .highlight-card.pink {border-left-color: #ec4899;}
    .highlight-card.purple {border-left-color: #8b5cf6;}
    .highlight-card.green {border-left-color: #10b981;}
    .highlight-card.orange {border-left-color: #f97316;}
    .highlight-title {color: #1e293b; font-size: 0.88rem; font-weight: 700; margin-bottom: 6px; line-height: 1.25;}
    .highlight-description {color: #475569; font-size: 0.82rem; line-height: 1.45; margin-bottom: 8px;}
    .read-more {color: #2563eb; font-weight: 600; font-size: 0.78rem; text-decoration: none;}
    .read-more:hover {color: #1d4ed8; text-decoration: underline;}
    .footer {text-align: center; color: rgba(255,255,255,0.8); font-size: 0.75rem; margin-top: 15px; padding: 12px; background: rgba(0,0,0,0.2); border-radius: 10px;}
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def clean(raw):
    if not raw: return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def extract_summary(entry, max_len=350):
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and content: content = content[0].get('value', '')
            summary = clean(content)
            if summary: return summary[:max_len] + ('...' if len(summary) > max_len else '')
    return ""

def get_hash(text): return hashlib.md5(text.encode()).hexdigest()[:12]

def title_similarity(a, b): return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def detect_company(text, section):
    text_lower = text.lower()
    sources = {"telco": [EVERGENT_CLIENTS, TOP_TELCOS, COMPETITORS], "ott": [EVERGENT_CLIENTS, OTT_PLATFORMS], "sports": [EVERGENT_CLIENTS, SPORTS_ENTITIES], "technology": [TOP_TELCOS, COMPETITORS]}
    for db in sources.get(section, []):
        for name, keywords in db.items():
            if any(k in text_lower for k in keywords): return name
    return None

# ══════════════════════════════════════════════════════════════════════════════
# FEED FETCHING - FAST & DEDUPLICATED
# ══════════════════════════════════════════════════════════════════════════════
def fetch_feed(source, url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200: return []
        feed = feedparser.parse(resp.content)
        return [{"title": clean(e.get("title","")), "link": e.get("link",""), "source": source, "summary": extract_summary(e), "hash": get_hash(clean(e.get("title","")))} for e in feed.entries[:25] if len(clean(e.get("title",""))) > 25 and e.get("link","").startswith("http")]
    except: return []

@st.cache_data(ttl=180, show_spinner=False)
def fetch_all_news():
    all_news = {}
    for section, feeds in RSS_FEEDS.items():
        items, seen_hashes, seen_titles = [], set(), []
        with ThreadPoolExecutor(max_workers=12) as executor:
            for result in executor.map(lambda f: fetch_feed(*f), feeds):
                for item in result:
                    if item["hash"] in seen_hashes or any(title_similarity(item["title"], t) > 0.75 for t in seen_titles): continue
                    items.append(item); seen_hashes.add(item["hash"]); seen_titles.append(item["title"])
        all_news[section] = items[:40]
    return all_news

# ══════════════════════════════════════════════════════════════════════════════
# AI HIGHLIGHTS - 14 PER SECTION
# ══════════════════════════════════════════════════════════════════════════════
def generate_highlights_ai(news_items, section, section_name):
    if not news_items: return []
    news_entries = [{"title": n['title'], "summary": n.get('summary','')[:200], "link": n['link'], "company": detect_company(n['title']+' '+n.get('summary',''), section)} for n in news_items[:28]]
    news_text = "\n".join([f"[{i+1}] {e['title']} | Company: {e['company'] or 'Unknown'} | Link: {e['link']}" for i, e in enumerate(news_entries)])
    
    clients = {"telco": list(TOP_TELCOS.keys())[:20]+list(COMPETITORS.keys())[:15], "ott": list(OTT_PLATFORMS.keys())+list(EVERGENT_CLIENTS.keys())[:15], "sports": list(SPORTS_ENTITIES.keys())+["FanDuel","Bally Sports","ESPN","NBA"], "technology": list(COMPETITORS.keys())[:20]+list(TOP_TELCOS.keys())[:15]}
    
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.1-8b-instant", "messages": [
                {"role": "system", "content": f"You are a {section_name} analyst. RULES: 1. Use ONLY real company names as titles (Vodafone, Netflix, Ericsson) 2. NEVER generic titles 3. Focus on: {', '.join(clients.get(section,[])[:25])}"},
                {"role": "user", "content": f"Create 14 unique client highlights. Title=Company Name. Return JSON only:\n{{\"highlights\": [{{\"title\": \"Company\", \"description\": \"2-3 sentences\", \"link\": \"url\"}}]}}\n\nNEWS:\n{news_text}"}
            ], "max_tokens": 3000, "temperature": 0.3}, timeout=50)
        
        if resp.status_code == 200:
            match = re.search(r'\{[\s\S]*\}', resp.json()["choices"][0]["message"]["content"])
            if match:
                highlights = json.loads(match.group()).get("highlights", [])[:14]
                for h in highlights:
                    if not h.get("link","").startswith("http"): h["link"] = news_entries[0]['link'] if news_entries else "#"
                return highlights
    except: pass
    
    # Fallback
    highlights, used = [], set()
    for n in news_items[:20]:
        company = detect_company(n['title']+' '+n.get('summary',''), section)
        if company and company not in used:
            highlights.append({"title": company, "description": n['title'][:150], "link": n['link']}); used.add(company)
            if len(highlights) >= 14: break
    return highlights

# ══════════════════════════════════════════════════════════════════════════════
# RENDER
# ══════════════════════════════════════════════════════════════════════════════
def render_card(h, color):
    link = h.get("link", "#")
    if not link.startswith("http"): link = "#"
    return f'<div class="highlight-card {color}"><div class="highlight-title">{html.escape(str(h.get("title","")))}</div><div class="highlight-description">{html.escape(str(h.get("description","")))}</div><a href="{html.escape(link)}" target="_blank" class="read-more">Read More →</a></div>'

def render_section(icon, name, highlights, hdr_class, color):
    cards = "".join([render_card(h, color) for h in (highlights or [])])
    return f'<div class="col-header {hdr_class}"><span>{icon}</span><span>{name}</span><span class="highlight-count">{len(highlights or [])}</span></div><div class="col-body">{cards or "<p style=\"text-align:center;color:#999;padding:40px;\">Loading...</p>"}</div>'

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="header-container"><h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1><p class="subtitle">AI-Powered Competitive Intelligence for CEO</p></div>', unsafe_allow_html=True)

all_news = fetch_all_news()
highlights = {sec: generate_highlights_ai(all_news.get(sec,[]), sec, name) for sec, name in [("telco","Telco OSS/BSS"),("ott","OTT & Streaming"),("sports","Sports & Events"),("technology","Technology")]}

c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown(render_section("📡","Telco OSS/BSS",highlights.get("telco",[]),"col-header-pink","pink"), unsafe_allow_html=True)
with c2: st.markdown(render_section("📺","OTT & Streaming",highlights.get("ott",[]),"col-header-purple","purple"), unsafe_allow_html=True)
with c3: st.markdown(render_section("🏆","Sports & Events",highlights.get("sports",[]),"col-header-green","green"), unsafe_allow_html=True)
with c4: st.markdown(render_section("⚡","Technology",highlights.get("technology",[]),"col-header-orange","orange"), unsafe_allow_html=True)

st.markdown(f'<div class="footer"><p>Last Updated: {datetime.now().strftime("%I:%M:%S %p")} • Auto-refreshes every 5 minutes</p></div>', unsafe_allow_html=True)
st.markdown("<script>setTimeout(function(){window.location.reload();},300000);</script>", unsafe_allow_html=True)

# Keep-alive
if (datetime.now() - st.session_state.keep_alive).seconds > 240: st.session_state.keep_alive = datetime.now(); st.rerun()
