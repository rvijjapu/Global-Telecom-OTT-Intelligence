import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
import html
import time
from zoneinfo import ZoneInfo
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import hashlib

# Security gate
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except FileNotFoundError:
    st.error("🔧 Missing secrets.toml – Add CEO_ACCESS_TOKEN in .streamlit/secrets.toml or Streamlit Cloud Secrets")
    st.stop()
except KeyError:
    st.error("🔧 CEO_ACCESS_TOKEN not found in secrets")
    st.stop()

provided_token = st.query_params.get("token")
if provided_token is not None:
    provided_token = provided_token[0] if isinstance(provided_token, list) else provided_token
else:
    provided_token = ""

if provided_token != EXPECTED_TOKEN:
    st.error("⛔ Unauthorized access – Invalid or missing token")
    st.info("Append `?token=your_token` to the URL or contact admin.")
    st.stop()

if "last_access" not in st.session_state:
    st.session_state.last_access = 0

now = time.time()
if now - st.session_state.last_access < 2:
    st.warning("⏱ Too many requests – Please wait a moment.")
    st.stop()

st.session_state.last_access = now

st.set_page_config(
    page_title="🌐 Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
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

    .announcement-title a { color: #1e40af; font-size: 0.92rem; font-weight: 600; text-decoration: none; display: block; margin-bottom: 8px; }
    .announcement-title a:hover { color: #1d4ed8; text-decoration: underline; }
    .announcement-summary { color: #475569; font-size: 0.85rem; line-height: 1.5; margin-bottom: 10px; padding: 10px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 8px; border-left: 4px solid #3b82f6; font-weight: 500; }
    .announcement-meta { font-size: 0.76rem; color: #64748b; display: flex; align-items: center; gap: 7px; flex-wrap: wrap; }
    .time-hot { color: #dc2626; font-weight: 600; font-style: italic; }
    .time-warm { color: #ea580c; font-weight: 600; }
    .time-normal { color: #64748b; }
    .empty-message { text-align: center; color: #94a3b8; padding: 30px; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# User-provided lists for CEO-focused monitoring
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
    # USA
    "Verizon": ["verizon", "verizon wireless", "verizon fios"],
    "AT&T": ["at&t", "att inc", "att mobility"],
    "T-Mobile": ["t-mobile", "tmobile usa", "sprint"],
    "Comcast": ["comcast", "xfinity", "comcast cable"],
    "Charter": ["charter communications", "spectrum", "charter spectrum"],
    "Cox": ["cox communications", "cox cable", "cox business"],
    "Lumen": ["lumen technologies", "centurylink", "lumen"],
    "Frontier": ["frontier communications", "frontier"],
    "Windstream": ["windstream", "windstream enterprise"],
    "Mediacom": ["mediacom communications", "mediacom"],
    "Altice USA": ["altice usa", "optimum", "suddenlink"],
   
    # UK & Europe
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
   
    # APAC - Singapore/Malaysia/NZ
    "Singtel": ["singtel", "singapore telecom", "singapore telecommunications"],
    "StarHub": ["starhub", "starhub singapore"],
    "M1": ["m1 limited", "m1 singapore"],
    "Maxis": ["maxis", "maxis communications", "maxis malaysia"],
    "Celcom": ["celcom", "celcom axiata"],
    "Digi": ["digi telecommunications", "digi malaysia", "digi.com"],
    "Telekom Malaysia": ["telekom malaysia", "tm unifi", "unifi tv", "tm"],
    "U Mobile": ["u mobile", "umobile malaysia"],
    "Sky NZ": ["sky new zealand", "sky nz", "sky network television"],
    "Spark": ["spark new zealand", "spark nz"],
    "2degrees": ["2degrees", "2degrees mobile"],
    "Vodafone NZ": ["vodafone new zealand", "vodafone nz"],
   
    # Australia
    "Telstra": ["telstra", "telstra corporation"],
    "Optus": ["optus", "singtel optus"],
    "TPG": ["tpg telecom", "vodafone australia"],
   
    # Asia
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
   
    # Middle East
    "Etisalat": ["etisalat", "emirates telecom", "e&"],
    "Du": ["du", "emirates integrated"],
    "STC": ["stc", "saudi telecom", "saudi telecom company"],
    "Ooredoo": ["ooredoo", "ooredoo group"],
    "Zain": ["zain", "zain group"],
    "Mobily": ["mobily", "etihad etisalat"],
   
    # Americas
    "América Móvil": ["america movil", "claro", "telmex"],
    "Telus": ["telus", "telus communications"],
    "Rogers": ["rogers communications", "rogers"],
    "Bell": ["bell canada", "bce inc"],
    "Shaw": ["shaw communications", "shaw"],
   
    # Africa
    "MTN": ["mtn group", "mtn"],
    "Vodacom": ["vodacom", "vodacom group"],
    "Safaricom": ["safaricom", "safaricom plc"],
}

# Flatten lists for permutations
def flatten_dict(d):
    flat = []
    for key, vals in d.items():
        flat.extend(vals)
        flat.append(key.lower())
    return list(set(flat))  # Unique

clients_flat = flatten_dict(EVERGENT_CLIENTS)
competitors_flat = flatten_dict(COMPETITORS)
telcos_flat = flatten_dict(TOP_TELCOS)

# Brainstormed and optimized CEO phrases with permutations (using clients, competitors, telcos)
def generate_ceo_phrases(base_terms, entities):
    phrases = []
    terms = ["key announcements", "major deals", "contracts", "mergers acquisitions", "strategic updates", "business developments"]
    for term in terms:
        # Permutations with entities
        entity_perm = f"({ ' OR '.join(entities[:5]) })" if entities else ""  # Limit to avoid query length issues
        phrases.append(f"{term} {base_terms} last week {entity_perm}")
    return phrases

SECTION_QUERIES = {
    "telco": generate_ceo_phrases("telecom OSS BSS", telcos_flat + competitors_flat + clients_flat),
    "ott": generate_ceo_phrases("OTT streaming content", clients_flat + competitors_flat),
    "sports": generate_ceo_phrases("sports events rights", clients_flat + telcos_flat),
    "technology": generate_ceo_phrases("technology AI cloud", competitors_flat + clients_flat)
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def clean(raw):
    if not raw:
        return ""
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()

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

def ai_summarize_news(title, summary):
    # AI algorithm mimicking human brain: Focus on critical elements (impact, numbers, strategy)
    full_text = f"{title}. {summary}"
    sentences = re.split(r'[.!?]+', full_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Permutation-based scoring for best summary
    scored_sentences = []
    for sentence in sentences:
        score = 0
        lower = sentence.lower()
        # Permutations of key terms
        if any(term in lower for term in all_critical_terms):  # From brainstormed lists
            score += 5
        scored_sentences.append((sentence, score))
    
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    
    exec_summary = [s for s, score in scored_sentences if score > 0][:3]  # Top 3
    if not exec_summary:
        return summary[:220] + "..." if len(summary) > 220 else summary
    
    result = '. '.join(exec_summary)
    return result + '.' if not result.endswith('.') else result

all_critical_terms = set()
for d in [EVERGENT_CLIENTS, COMPETITORS, TOP_TELCOS]:
    for vals in d.values():
        all_critical_terms.update([v.lower() for v in vals])

def fetch_news_for_section(phrases):
    items = []
    seen_titles = set()
    for phrase in phrases:
        try:
            url = f"https://news.google.com/rss/search?q={phrase.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                continue
            
            feed = feedparser.parse(resp.content)
            NOW = datetime.now(ZoneInfo("America/New_York"))
            seven_days_ago = NOW - timedelta(days=7)
            
            for entry in feed.entries:
                title = clean(entry.get("title", ""))
                if title in seen_titles or len(title) < 15:
                    continue
                
                link = entry.get("link", "")
                if not link:
                    continue
                
                raw_summary = extract_summary(entry)
                if not raw_summary:
                    continue
                
                exec_summary = ai_summarize_news(title, raw_summary)
                
                pub = NOW
                if 'published_parsed' in entry:
                    try:
                        pub = datetime(*entry.published_parsed[:6], tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo("America/New_York"))
                    except:
                        pass
                
                if pub < seven_days_ago:
                    continue
                
                items.append({
                    "title": title,
                    "link": link,
                    "summary": exec_summary,
                    "pub": pub,
                    "source": "AI Search"
                })
                seen_titles.add(title)
        
        except:
            pass
    
    # AI-optimized: Sort by recency and relevance (length of summary as proxy for info density)
    items.sort(key=lambda x: (x["pub"], len(x["summary"])), reverse=True)
    return items[:10]  # Best 10

# Load AI-driven news
@st.cache_data(ttl=300)
def load_ai_news():
    categorized = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_news_for_section, SECTION_QUERIES[cat]): cat for cat in SECTION_QUERIES}
        for future in as_completed(futures):
            cat = futures[future]
            try:
                categorized[cat] = future.result()
            except:
                categorized[cat] = []
    
    return categorized

def get_time_str(dt):
    now_et = datetime.now(ZoneInfo("America/New_York"))
    hrs = int((now_et - dt).total_seconds() / 3600)
    if hrs < 1: return "Just now"
    if hrs < 6: return f"{hrs}h ago"
    if hrs < 24: return f"{hrs}h ago"
    return f"{hrs//24}d ago"

def render_section_news(items):
    cards = ""
    for item in items:
        time_str = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_summary = html.escape(item["summary"])
        safe_source = html.escape(item["source"])
        
        title_html = f'<a href="{safe_link}" target="_blank">{safe_title}</a>'
        
        cards += f'''<div class="news-card">
<div class="announcement-title">{title_html}</div>
<div class="announcement-summary">{safe_summary}</div>
<div class="announcement-meta">
<span>{time_str}</span> • <span>{safe_source}</span>
</div>
</div>'''
    
    if not cards:
        cards = '<div class="empty-message">No key announcements in last week</div>'
    
    return cards

# === LOADING ===
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#1e40af;margin-top:120px;'>⚡ Loading AI-Driven CEO Dashboard...<br><small>Fetching critical news summaries</small></h2>", unsafe_allow_html=True)

with st.spinner(""):
    data = load_ai_news()

placeholder.empty()

# === RENDER DASHBOARD ===
cols = st.columns(4)
cat_list = list(SECTION_QUERIES.keys())

for idx, cat in enumerate(cat_list):
    sec = SECTION_QUERIES[cat]
    items = data.get(cat, [])
    news_html = render_section_news(items)
    
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="col-body">{news_html}</div>', unsafe_allow_html=True)

# Auto-refresh every 5 minutes
st.markdown("""
<script>
setTimeout(function(){
    window.location.reload();
}, 300000);
</script>
""", unsafe_allow_html=True)
