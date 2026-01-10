import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta, date
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re
from zoneinfo import ZoneInfo
import hashlib

# Security gate
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except FileNotFoundError:
    st.error(" Missing secrets.toml – Add CEO_ACCESS_TOKEN in .streamlit/secrets.toml or Streamlit Cloud Secrets")
    st.stop()
except KeyError:
    st.error(" CEO_ACCESS_TOKEN not found in secrets")
    st.stop()

provided_token = st.query_params.get("token")
if provided_token is not None:
    provided_token = provided_token[0] if isinstance(provided_token, list) else provided_token
else:
    provided_token = ""

if provided_token != EXPECTED_TOKEN:
    st.error(" Unauthorized access – Invalid or missing token")
    st.info("Append `?token=your_token` to the URL or contact admin.")
    st.stop()

if "last_access" not in st.session_state:
    st.session_state.last_access = 0

now = time.time()
if now - st.session_state.last_access < 2:
    st.warning(" Too many requests – Please wait a moment.")
    st.stop()

st.session_state.last_access = now

st.set_page_config(
    page_title=" Global Telecom & OTT Stellar Nexus",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        color: #1e293b;
        padding-top: 0.5rem;
    }
   
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.2rem 1.5rem;
        text-align: center;
        border-radius: 20px;
        box-shadow: 0 6px 25px rgba(0,0,0,0.08);
        margin: 0 1.5rem 1.8rem 1.5rem;
        border-bottom: 4px solid #3b82f6;
        backdrop-filter: blur(8px);
    }

    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1e40af;
        margin: 0;
        letter-spacing: -0.6px;
    }

    .subtitle {
        font-size: 1.1rem;
        color: #475569;
        margin-top: 0.6rem;
        margin-bottom: 0;
        font-weight: 500;
    }

    .col-header {
        padding: 10px 16px;
        border-radius: 14px 14px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }

    .col-header-pink { background: linear-gradient(135deg, #ec4899, #db2777); }
    .col-header-purple { background: linear-gradient(135deg, #a78bfa, #8b5cf6); }
    .col-header-green { background: linear-gradient(135deg, #34d399, #10b981); }
    .col-header-orange { background: linear-gradient(135deg, #fb923c, #f97316); }

    .col-body {
        background: white;
        border-radius: 0 0 14px 14px;
        padding: 12px;
        min-height: 520px;
        max-height: 620px;
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
        transform: translateY(-2px);
    }

    .news-title {
        color: #1e40af;
        font-size: 0.92rem;
        font-weight: 600;
        line-height: 1.35;
        text-decoration: none;
        display: block;
        margin-bottom: 8px;
    }

    .news-summary {
        color: #475569;
        font-size: 0.85rem;
        line-height: 1.5;
        margin-bottom: 10px;
        padding: 10px;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        font-weight: 500;
    }

    .news-meta {
        font-size: 0.76rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 7px;
        flex-wrap: wrap;
    }

    .time-hot { color: #dc2626; font-weight: 600; font-style: italic; }
    .time-warm { color: #ea580c; font-weight: 600; }
    .time-normal { color: #64748b; }
   
    .empty-message {
        text-align: center;
        color: #94a3b8;
        padding: 30px;
    }

    .separator {
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-container">
    <h1 class="main-title"> Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">AI-Powered Competitive Intelligence for CEO Vision</p>
</div>
""", unsafe_allow_html=True)

# Expanded Evergent Clients with variations from research
EVERGENT_CLIENTS = {
    "Astro": ["astro malaysia", "astro sooka", "astro njoi", "astro", "sooka", "njoi"],
    "MongolTV": ["mongoltv", "mongol tv", "mongolia tv"],
    "FOX": ["fox sports", "fox corporation", "fox networks", "fox", "fox latin america"],
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
    "Singtel": ["singtel", "singapore telecom", "singapore telecommunications"],
    "T-Mobile": ["t-mobile", "tmobile usa"],
    "HBO": ["hbo", "hbo max"],
    "Neon": ["neon", "neon streaming", "sky neon"],
    "JCOM": ["jcom", "jupiter communications", "j:com"],
    "GoBx": ["gobx"],
    "Toshiba": ["toshiba"],
    "Tornado": ["tornado"],
    "Samsung": ["samsung"],
    "PUBG": ["pubg"],
    "Hisense": ["hisense"],
}

# Competitors
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

# Top Telcos
TOP_TELCOS = {
    "Verizon": ["verizon", "verizon wireless", "verizon fios"],
    "AT&T": ["at&t", "att mobility"],
    "T-Mobile": ["t-mobile", "tmobile usa", "sprint"],
    "Comcast": ["comcast", "xfinity", "comcast cable"],
    "Charter": ["charter communications", "spectrum", "charter spectrum"],
    "Cox": ["cox communications", "cox cable", "cox business"],
    "Lumen": ["lumen technologies", "centurylink", "lumen"],
    "Frontier": ["frontier communications", "frontier"],
    "Windstream": ["windstream", "windstream enterprise"],
    "Mediacom": ["mediacom communications", "mediacom"],
    "Altice USA": ["altice usa", "optimum", "suddenlink"],
    "BT": ["bt group", "british telecom", "bt", "bt enterprise", "ee"],
    "Vodafone": ["vodafone", "vodafone group"],
    "O2": ["o2", "telefonica uk"],
    "Virgin Media": ["virgin media", "virgin media o2"],
    "Three": ["three uk", "three mobile"],
    "Orange": ["orange", "orange sa"],
    "Deutsche Telekom": ["deutsche telekom", "t-mobile europe", "telekom"],
    "Telefónica": ["telefonica", "telefonica spain", "movistar"],
    "Telecom Italia": ["telecom italia", "tim", "tim brasil"],
    "Swisscom": ["swisscom", "swisscom ag"],
    "KPN": ["kpn", "koninklijke pn"],
    "Proximus": ["proximus", "belgacom"],
    "Telenor": ["telenor", "telenor group"],
    "Telia": ["telia", "telia company"],
    "Bouygues": ["bouygues telecom", "bouygues"],
    "Singtel": ["singtel", "singapore telecom", "singapore telecommunications"],
    "StarHub": ["starhub", "starhub singapore"],
    "M1": ["m1 limited", "m1 singapore"],
    "Maxis": ["maxis", "maxis communications", "maxis malaysia"],
    "Celcom": ["celcom", "celcom axiata"],
    "Digi": ["digi telecommunications", "digi malaysia", "digi.com"],
    "Telekom Malaysia": ["telekom malaysia", "tm", "tm unifi"],
    "U Mobile": ["u mobile", "umobile malaysia"],
    "Sky NZ": ["sky new zealand", "sky nz", "sky network television"],
    "Spark": ["spark new zealand", "spark nz"],
    "2degrees": ["2degrees", "2degrees mobile"],
    "Vodafone NZ": ["vodafone new zealand", "vodafone nz"],
    "Telstra": ["telstra", "telstra corporation"],
    "Optus": ["optus", "singtel optus"],
    "TPG": ["tpg telecom", "vodafone australia"],
    "China Mobile": ["china mobile", "cmcc"],
    "China Telecom": ["china telecom", "chinanet"],
    "China Unicom": ["china unicom", "unicom"],
    "NTT": ["ntt", "nippon telegraph", "ntt docomo"],
    "SoftBank": ["softbank", "softbank corp"],
    "KDDI": ["kddi", "kddi corporation", "au"],
    "Reliance Jio": ["reliance jio", "jio", "jio platforms"],
    "Airtel": ["bharti airtel", "airtel", "airtel india"],
    "Vi": ["vodafone idea", "vi", "idea cellular"],
    "BSNL": ["bsnl", "bharat sanchar"],
    "SK Telecom": ["sk telecom", "skt"],
    "KT": ["kt corporation", "kt"],
    "LG Uplus": ["lg uplus", "lg u+"],
    "Globe": ["globe telecom", "globe philippines"],
    "PLDT": ["pldt", "philippine long distance"],
    "Smart": ["smart communications", "smart philippines"],
    "Etisalat": ["etisalat", "emirates telecom", "e&"],
    "Du": ["du", "emirates integrated"],
    "STC": ["stc", "saudi telecom", "saudi telecom company"],
    "Ooredoo": ["ooredoo", "ooredoo group"],
    "Zain": ["zain", "zain group"],
    "Mobily": ["mobily", "etihad etisalat"],
    "América Móvil": ["america movil", "claro", "telmex"],
    "Telus": ["telus", "telus communications"],
    "Rogers": ["rogers communications", "rogers"],
    "Bell": ["bell canada", "bce inc"],
    "Shaw": ["shaw communications", "shaw"],
    "MTN": ["mtn group", "mtn"],
    "Vodacom": ["vodacom", "vodacom group"],
    "Safaricom": ["safaricom", "safaricom plc"],
}

# Categorize for sections
def get_category_entities(category):
    if category == "telco":
        entities = {**{k: v for k, v in EVERGENT_CLIENTS.items() if k in ["AT&T", "Telekom Malaysia", "Singtel", "T-Mobile"]}, **COMPETITORS, **TOP_TELCOS}
    elif category == "ott":
        entities = {k: v for k, v in EVERGENT_CLIENTS.items() if k in ["Astro", "MongolTV", "Shahid", "MBC", "TV ASAHI", "TV3", "ABS-CBN", "Viki", "Sony", "Aha", "BBC", "Lightbox", "Sky", "Cignal", "ETV", "Simple TV", "Britbox", "Quickplay", "Pilipinas", "HBO", "Neon", "JCOM", "GoBx", "Toshiba", "Tornado", "Samsung", "PUBG", "Hisense"]}
    elif category == "sports":
        entities = {k: v for k, v in EVERGENT_CLIENTS.items() if k in ["FOX", "NBA", "TRT", "Sinclair", "FanDuel", "Bally Sports", "Gotham", "Marquee"]}
    elif category == "technology":
        entities = COMPETITORS  # Tech competitors
    return entities

# Focus phrases
FOCUS_PHRASES = "(key achievements OR deals OR mergers OR acquisitions OR profit OR loss OR recent news)"

# Google base URL
GOOGLE_BASE = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

SECTIONS = {
    "telco": {"icon": "", "name": "Telco & OSS/BSS", "style": "col-header col-header-pink"},
    "ott": {"icon": "", "name": "OTT & Streaming", "style": "col-header col-header-purple"},
    "sports": {"icon": "", "name": "Sports & Events", "style": "col-header col-header-green"},
    "technology": {"icon": "", "name": "Technology", "style": "col-header col-header-orange"},
}

CRITICAL_KEYWORDS = {
    "telco": ["5g", "oss", "bss", "network", "spectrum", "carrier", "wireless", "fiber", "broadband",
              "telecom", "mvno", "mobile operator", "infrastructure", "tower", "antenna", "satellite"],
    "ott": ["streaming", "netflix", "disney", "hbo", "paramount", "peacock", "hulu", "prime video",
            "subscription", "svod", "avod", "content", "original series", "licensing", "bundle"],
    "sports": ["nfl", "nba", "mlb", "soccer", "premier league", "espn", "rights deal", "broadcast",
               "sports betting", "fantasy", "athlete", "championship", "tournament"],
    "technology": ["ai", "artificial intelligence", "machine learning", "cloud", "saas", "cybersecurity",
                   "blockchain", "quantum", "semiconductor", "chip", "startup", "venture capital"]
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

def calculate_importance_score(title, summary, category):
    score = 0
    text = (title + " " + summary).lower()
   
    keywords = CRITICAL_KEYWORDS.get(category, [])
    for keyword in keywords:
        if keyword in text:
            score += 2
   
    if len(title) > 60:
        score += 1
   
    if len(summary) > 50:
        score += 2
   
    critical_terms = ["acquisition", "merger", "partnership", "launch", "announce", "billion",
                      "million", "breakthrough", "first", "new", "major", "strategic", "profit", "loss"]
    for term in critical_terms:
        if term in text:
            score += 3
   
    return score

def extract_summary(entry, max_len=300):
    summary = ""
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and len(content) > 0:
                content = content[0].get('value', '')
            summary = clean(content)
            if summary:
                break
    if len(summary) > max_len:
        summary = summary[:max_len].rsplit(' ', 1)[0] + '...'
    return summary if summary else ""

def fetch_full_article_content(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return ""
       
        from html.parser import HTMLParser
       
        class ArticleParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.in_script = False
                self.in_style = False
           
            def handle_starttag(self, tag, attrs):
                if tag in ['script', 'style', 'nav', 'header', 'footer']:
                    self.in_script = True
           
            def handle_endtag(self, tag):
                if tag in ['script', 'style', 'nav', 'header', 'footer']:
                    self.in_script = False
           
            def handle_data(self, data):
                if not self.in_script and data.strip():
                    self.text.append(data.strip())
       
        parser = ArticleParser()
        parser.feed(resp.text)
        full_text = ' '.join(parser.text)
        full_text = re.sub(r'\s+', ' ', full_text)
        return full_text[:3000]
    except:
        return ""

def ai_summarize_news(title, summary, url=None):
    article_content = ""
    if url:
        article_content = fetch_full_article_content(url)
   
    source_text = article_content if article_content else summary
    full_text = f"{title}. {source_text}"
   
    sentences = re.split(r'[.!?]+', full_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 25]
   
    if not sentences:
        return summary[:200] + "..." if len(summary) > 200 else summary
   
    unique_sentences = []
    seen_content = set()
   
    for sentence in sentences:
        fingerprint = sentence.lower().replace(' ', '')[:50]
        if fingerprint not in seen_content:
            unique_sentences.append(sentence)
            seen_content.add(fingerprint)
   
    sentences = unique_sentences[:8]
   
    scored_sentences = []
   
    for idx, sentence in enumerate(sentences):
        score = 0
        sentence_lower = sentence.lower()
       
        critical_words = {
            'announce': 5, 'launch': 5, 'partnership': 5, 'agreement': 5,
            'merger': 6, 'acquisition': 6, 'deal': 5, 'contract': 5,
            'revenue': 4, 'profit': 4, 'billion': 5, 'million': 4,
            'percent': 3, '%': 3, 'growth': 4, 'expand': 4,
            'ceo': 4, 'president': 4, 'executive': 3, 'invest': 5,
            'strategic': 4, 'plan': 3, 'customers': 3, 'users': 3,
            'new': 3, 'first': 4, 'major': 3, 'significant': 3,
            'loss': 4
        }
       
        for word, weight in critical_words.items():
            if word in sentence_lower:
                score += weight
       
        numbers = re.findall(r'\d+', sentence)
        if numbers:
            score += len(numbers) * 2
       
        caps = [w for w in sentence.split() if len(w) > 3 and w[0].isupper()]
        score += min(len(caps), 3)
       
        if idx > 0 and idx < 4:
            score += (4 - idx) * 2
       
        if len(sentence) < 40 or len(sentence) > 200:
            score -= 2
       
        if sentence.strip().lower() == title.strip().lower():
            score = 0
       
        scored_sentences.append((sentence, score, idx))
   
    scored_sentences.sort(key=lambda x: (-x[1], x[2]))
   
    exec_summary = []
    total_length = 0
    max_length = 200
    used_words = set()
   
    for sentence, score, idx in scored_sentences:
        if score <= 0:
            continue
       
        sentence_words = set(sentence.lower().split())
        overlap = len(sentence_words & used_words) / max(len(sentence_words), 1)
       
        if overlap > 0.6 and exec_summary:
            continue
       
        if total_length + len(sentence) <= max_length and len(exec_summary) < 2:
            exec_summary.append(sentence)
            total_length += len(sentence)
            used_words.update(sentence_words)
       
        if len(exec_summary) >= 1 and total_length > 100:
            break
   
    if not exec_summary:
        if summary and len(summary) > 50:
            return summary[:150] + "..."
        return "Details in article."
   
    result = '. '.join(exec_summary)
    if not result.endswith(('.', '!', '?')):
        result += '.'
   
    result = re.sub(r'\s+', ' ', result).strip()
   
    return result

def get_article_hash(title, link):
    return hashlib.md5(f"{title}{link}".encode()).hexdigest()

def extract_redirect_url(google_url):
    try:
        if 'google.com' in google_url and '/articles/' in google_url:
            resp = requests.get(google_url, headers=HEADERS, timeout=10, allow_redirects=True)
            return resp.url
        return google_url
    except:
        return google_url

def fetch_google_news(query):
    items = []
    url = GOOGLE_BASE.format(query=query)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return items
       
        feed = feedparser.parse(resp.content)
        if not feed.entries:
            return items
       
        NOW = datetime.now(ZoneInfo("America/New_York"))
        cutoff_date = datetime(2026, 1, 1, tzinfo=ZoneInfo("America/New_York"))
       
        for entry in feed.entries:
            try:
                title = clean(entry.get("title", ""))
                if len(title) < 15:
                    continue
               
                link = entry.get("link", "")
                if not link:
                    continue
               
                direct_link = extract_redirect_url(link)
               
                summary = extract_summary(entry, max_len=300)
               
                exec_summary = ai_summarize_news(title, summary, direct_link)
               
                pub = NOW
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                    except:
                        pass
               
                if pub < cutoff_date:
                    continue
               
                items.append({
                    "title": title,
                    "link": direct_link,
                    "pub": pub,
                    "source": "Google News",
                    "summary": exec_summary,
                    "hash": get_article_hash(title, direct_link)
                })
            except:
                continue
       
        items.sort(key=lambda x: x["pub"], reverse=True)
        return items[:20]  # Limit to top 20
    except:
        return []

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    seen_hashes = set()
   
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for cat in categorized:
            entities = get_category_entities(cat)
            name_vars = []
            for vars in entities.values():
                name_vars.extend(vars)
            entity_query = " OR ".join(set(name_vars))  # Unique to avoid too long query
            full_query = f"({entity_query}) {FOCUS_PHRASES} after:2026-01-01"
            futures[executor.submit(fetch_google_news, full_query)] = cat
        
        for future in as_completed(futures):
            cat = futures[future]
            try:
                items = future.result()
                for item in items:
                    if item["hash"] not in seen_hashes:
                        score = calculate_importance_score(item["title"], item["summary"], cat)
                        item["importance"] = score
                        categorized[cat].append(item)
                        seen_hashes.add(item["hash"])
            except:
                pass  # Fail-safe, continue even if one fails
   
    for cat in categorized:
        categorized[cat].sort(key=lambda x: (-x.get("importance", 0), -x["pub"].timestamp()))
   
    return categorized

def get_time_str(dt):
    now_et = datetime.now(ZoneInfo("America/New_York"))
    diff = (now_et - dt).total_seconds()
    hrs = int(diff / 3600)
   
    if hrs < 1:
        return "Just now", "time-hot"
    if hrs < 6:
        return f"{hrs}h ago", "time-hot"
    if hrs < 24:
        return f"{hrs}h ago", "time-warm"
    days = hrs // 24
    return f"{days}d ago", "time-normal"

def render_body(items):
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_summary = html.escape(item["summary"])
        safe_source = html.escape(item["source"])
       
        cards += f'''<div class="news-card">
<div class="news-title">{safe_title}</div>
<div class="news-summary">{safe_summary}</div>
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
</div>
</div>'''
   
    if not cards:
        cards = '<div class="empty-message">No recent news available. Retrying soon.</div>'
   
    return cards

# Loading
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'> Igniting AI-Powered Intelligence...<br><small>Please wait for a moment</small></h2>", unsafe_allow_html=True)

with st.spinner("Fetching latest news..."):
    try:
        data = load_feeds()
    except:
        st.error("Temporary fetch issue. Please refresh.")
        st.stop()

placeholder.empty()

# Render Dashboard
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
   
    regular_items = data.get(cat, [])
    regular_cards = render_body(regular_items)
   
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="col-body">{regular_cards}</div>', unsafe_allow_html=True)

# Auto-refresh every 5 minutes
st.markdown("""
<script>
setTimeout(function(){
    window.location.reload();
}, 300000);
</script>
""", unsafe_allow_html=True)
