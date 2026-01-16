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
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
# KEEP-ALIVE FRAGMENT
# ══════════════════════════════════════════════════════════════════════════════
@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM STYLING
# ══════════════════════════════════════════════════════════════════════════════
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
    
    /* Highlights Section */
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
        background: #f1f5f9;
        border-radius: 12px;
        padding: 1.5rem;
        min-height: 200px;
        border: 1px solid #e2e8f0;
    }
    
    .hero-box-title {
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 12px;
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
    
    /* News Sections */
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
    }
    
    .news-card:hover {
        background: #f1f5f9;
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }
    
    .news-card-priority {
        background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
        border: 2px solid #fbbf24;
        border-radius: 10px;
        padding: 12px;
        margin-bottom: 10px;
    }
    
    .news-card-priority:hover {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        box-shadow: 0 8px 20px rgba(251,191,36,0.2);
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

# ══════════════════════════════════════════════════════════════════════════════
# COMPREHENSIVE INTELLIGENCE LISTS
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
    # Additional clients
    "Akash DTH": ["akash dth"],
    "DirecTV": ["directv"],
    "Britbox": ["britbox"],
    "NBA": ["nba"],
    "Gotham": ["gotham"],
    "FanDuel Sports": ["fanduel sports", "bally sports"],
    "WONDER Project": ["wonder project"],
    "Marquee Sports": ["marquee sports"],
    "Astro": ["astro"],
    "Akash": ["akash"],
    "Etisalat": ["etisalat"],
    "Sony": ["sony"],
    "DAZN": ["dazn"],
    "Simple TV": ["simple tv"],
    "Antel": ["antel"],
    "Aha": ["aha"],
    "Sky NZ": ["sky nz"],
    "BBC": ["bbc"],
    "ABS CBN": ["abs cbn"],
    "BC - Mongol TV": ["bc mongol tv"],
    "Shahid": ["shahid"],
    "Viki": ["viki"],
    "TRT": ["trt"],
    "TV3": ["tv3"],
    "ETV": ["etv"],
    "Cignal- Philippinas": ["cignal philippinas", "first light"],
    "TV Asahi": ["tv asahi"],
    "Ooredo - MK": ["ooredoo mk"],
    "BC - One 31": ["bc one 31"],
    "Antenna Greece": ["antenna greece"],
    "Telekom Malaysia": ["telekom malaysia"],
    "Exxen": ["exxen"],
    "Cignal Super": ["cignal super"],
    "Dorna Sports": ["dorna sports"],
    "Premier League": ["premier league"],
    "StarHub": ["starhub"],
    "Subhub e&": ["subhub e&"],
    "TV NZ": ["tv nz"],
    "TV9 - Firstlight Media": ["tv9 firstlight media"],
    "Korea Content Platform": ["korea content platform"],
    "Firstlight Ltd - PLDT Home": ["firstlight ltd pldt home"],
    "Minno": ["minno"],
    "EKKL (Pinnacle Peak)": ["ekkl pinnacle peak"],
    "Liberty Global": ["liberty global"],
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
    "Telekom Malaysia": ["telekom malaysia", "tm", "tm unifi"],
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

# Combined keyword list for filtering
ALL_COMPANY_KWS = []
for d in [EVERGENT_CLIENTS, COMPETITORS, TOP_TELCOS]:
    for names in d.values():
        ALL_COMPANY_KWS.extend(names)
ALL_COMPANY_KWS = list(set([kw.lower() for kw in ALL_COMPANY_KWS]))  # unique, lowercased for matching

# RSS FEEDS (expanded for coverage)
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
    ("ESPN", "https://www.espn.com/espn/rss/news", "sports"),
    "BBC Sport": ["bbc sport", "bbc sports"],
    "SportsPro": ["sportspromedia.com", "sports pro"],
    ("TechCrunch", "https://techcrunch.com/feed/", "technology"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "technology"),
    ("Wired", "https://www.wired.com/feed/rss", "technology"),
    ("VentureBeat", "https://venturebeat.com/feed/", "technology"),
    # Additional for clients & competitors
    ("Sports Business Journal", "https://www.sportsbusinessjournal.com/rss", "sports"),
    ("Sportcal", "https://www.sportcal.com/feed", "sports"),
    ("StreamTV Insider", "https://www.streamtvinsider.com/feed", "ott"),
    ("Fierce Video", "https://www.fiercevideo.com/rss.xml", "ott"),
    ("TM Forum", "https://inform.tmforum.org/feed/", "telco"),
    ("Appledore Research", "https://appledoreresearch.com/feed/", "telco"),
    ("Omdia", "https://omdia.tech.informa.com/feed", "technology"),
]

SECTIONS = {
    "telco": {"icon": "📡", "name": "TELCO OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & STREAMING", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "SPORTS MEDIA", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "AI TECHWATCH", "style": "col-header-orange"},
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def clean(raw):
    return html.unescape(re.sub(r'<[^>]+>', '', str(raw or ""))).strip()

def fetch_feed(source, url, category):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code != 200: return items
        
        feed = feedparser.parse(resp.content)
        NOW = datetime.now()
        CUTOFF = NOW - timedelta(days=10)
        
        for entry in feed.entries[:15]:
            title = clean(entry.get("title", ""))
            if len(title) < 30: continue
            
            summary = clean(entry.get("summary", entry.get("description", "")))
            link = entry.get("link", "")
            
            pub = None
            for k in ("published_parsed", "updated_parsed"):
                val = getattr(entry, k, None)
                if val:
                    try: pub = datetime(*val[:6])
                    except: pass
                    break
            
            if not pub or pub < CUTOFF: continue
            
            full_text = (title + " " + summary).lower()
            
            # Strict filter: must match at least one company keyword
            if not any(kw in full_text for kw in ALL_COMPANY_KWS):
                continue
            
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "summary": summary[:140] + "..." if len(summary) > 140 else summary,
                "category": category
            })
    except:
        pass
    return items

@st.cache_data(ttl=300, show_spinner=False)
def load_feeds():
    categorized = {"telco": [], "ott": [], "sports": [], "technology": []}
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch_feed, s, u, c) for s, u, c in RSS_FEEDS]
        for future in as_completed(futures):
            for item in future.result():
                categorized[item["category"]].append(item)
    
    # Sort newest first
    for cat in categorized:
        categorized[cat].sort(key=lambda x: x["pub"], reverse=True)
    
    return categorized

def get_time_str(dt):
    hrs = int((datetime.now() - dt).total_seconds() / 3600)
    if hrs < 1: return "Now"
    if hrs < 6: return f"{hrs}h"
    if hrs < 24: return f"{hrs}h"
    return f"{hrs//24}d"

def render_body(items):
    if not items:
        return """<div class="col-body"><div style="text-align:center;color:#94a3b8;padding:40px;">No critical signals at this time</div></div>"""
    
    cards = []
    for item in items:
        time_str = get_time_str(item["pub"])
        title = html.escape(item["title"])
        link = html.escape(item["link"])
        source = html.escape(item["source"])
        
        card_parts = [
            f'<div class="news-card">',
            f'<a href="{link}" target="_blank" class="news-title">{title}</a>',
            '<div class="news-meta">',
            f'<span class="time-hot">{time_str}</span>',
            '<span>•</span>',
            f'<span>{source}</span>',
            '</div>',
            '</div>'
        ]
        cards.append(''.join(card_parts))
    
    return '<div class="col-body">' + ''.join(cards) + '</div>'

# MAIN APPLICATION
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:70vh;text-align:center;">
            <h1 style="color:#0a192f;font-size:2.8rem;font-weight:800;">⚡ Critical Intelligence Engine</h1>
            <p style="color:#64748b;font-size:1.2rem;">Real-time signals for Evergent – Clients & Competitors only</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)

placeholder.empty()

st.markdown("""
<div class="header-container">
    <h1 class="main-title">Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time Critical Intelligence – Evergent Clients, Competitors & Strategic Deals</p>
</div>
""", unsafe_allow_html=True)

# Load & Render Columns Only
with st.spinner("Scanning latest critical news..."):
    data = load_feeds()

cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])[:15]
    
    with cols[idx]:
        header_parts = ['<div class="', sec["style"], '">', sec["icon"], ' ', sec["name"], '</div>']
        st.markdown(''.join(header_parts), unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center;color:rgba(255,255,255,0.95);font-size:0.8rem;margin-top:20px;padding:16px;background:linear-gradient(135deg,rgba(10,25,47,0.95),rgba(30,41,59,0.95));border-radius:10px;">
    <strong>Strict Filter:</strong> Only Evergent Clients, Competitors & Strategic Deals | <strong>🔄 Auto-refresh:</strong> Every 5 minutes
</div>
""", unsafe_allow_html=True)

st.markdown('<script>setTimeout(function() {window.location.reload();}, 300000);</script>', unsafe_allow_html=True)

keep_alive()
