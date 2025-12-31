import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import re
import html

st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(180deg, #f0f4f8 0%, #e2e8f0 100%);
    }
    #MainMenu, footer, header {visibility: hidden;}
    
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #1a365d, #2b6cb0, #4c51bf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .col-header-pink {
        background: linear-gradient(90deg, #ec4899, #db2777);
        padding: 12px 16px;
        border-radius: 12px 12px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
    }
    
    .col-header-purple {
        background: linear-gradient(90deg, #8b5cf6, #7c3aed);
        padding: 12px 16px;
        border-radius: 12px 12px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
    }
    
    .col-header-green {
        background: linear-gradient(90deg, #10b981, #059669);
        padding: 12px 16px;
        border-radius: 12px 12px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
    }
    
    .col-header-orange {
        background: linear-gradient(90deg, #f97316, #ea580c);
        padding: 12px 16px;
        border-radius: 12px 12px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
    }
    
    .col-body {
        background: white;
        border-radius: 0 0 12px 12px;
        padding: 12px;
        min-height: 550px;
        max-height: 650px;
        overflow-y: auto;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .news-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
    
    .news-card:hover {
        background: #f1f5f9;
        border-color: #cbd5e0;
    }
    
    .news-title {
        color: #1e40af;
        font-size: 0.9rem;
        font-weight: 600;
        line-height: 1.4;
        text-decoration: none;
        display: block;
        margin-bottom: 8px;
    }
    
    .news-title:hover {
        color: #1d4ed8;
        text-decoration: underline;
    }
    
    .news-meta {
        font-size: 0.75rem;
        color: #64748b;
        display: flex;
        align-items: center;
        gap: 6px;
        flex-wrap: wrap;
    }
    
    .time-hot {
        color: #dc2626;
        font-weight: 600;
        font-style: italic;
    }
    
    .time-warm {
        color: #ea580c;
        font-weight: 600;
    }
    
    .time-normal {
        color: #64748b;
        font-weight: 600;
    }
    
    .tag-client {
        background: #fef3c7;
        color: #b45309;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    .tag-competitor {
        background: #fee2e2;
        color: #dc2626;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    .tag-telco {
        background: #dbeafe;
        color: #1d4ed8;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
    }
    
    .col-body::-webkit-scrollbar {
        width: 6px;
    }
    .col-body::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    .col-body::-webkit-scrollbar-thumb {
        background: #cbd5e0;
        border-radius: 3px;
    }
    
    .footer-text {
        text-align: center;
        padding: 1rem;
        color: #64748b;
        font-size: 0.8rem;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

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
        # Existing
        ("Light Reading", "https://www.lightreading.com/rss.xml"),
        ("Fierce Telecom", "https://www.fiercetelecom.com/rss/xml"),
        ("Telecoms.com", "https://telecoms.com/feed/"),
        ("RCR Wireless", "https://www.rcrwireless.com/feed"),
        ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
        ("Capacity Media", "https://www.capacitymedia.com/feed"),
        ("Total Telecom", "https://www.totaltele.com/rss.xml"),
        ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
        ("TelecomTech News", "https://telecomstechnews.com/feed"),
        ("Developing Telecoms", "https://developingtelecoms.com/feed"),

        # Added – CEO / Strategy Grade
        ("GSMA", "https://www.gsma.com/feed/"),
        ("TM Forum", "https://www.tmforum.org/feed/"),
        ("PolicyTracker", "https://www.policytracker.com/feed/"),
        ("ITU News", "https://www.itu.int/en/mediacentre/rss/Pages/default.aspx"),
        ("McKinsey Telecom", "https://www.mckinsey.com/industries/technology-media-and-telecommunications/rss"),
        ("Deloitte TMT", "https://www2.deloitte.com/global/en/pages/technology-media-and-telecommunications/articles/rss-feed.html"),
        ("Bain TMT", "https://www.bain.com/insights/rss/?industry=technology"),
    ],

    "ott": [
        # Existing
        ("Variety", "https://variety.com/feed/"),
        ("Hollywood Reporter", "https://www.hollywoodreporter.com/feed/"),
        ("Deadline", "https://deadline.com/feed/"),
        ("Fierce Video", "https://www.fiercevideo.com/rss/xml"),
        ("Streaming Media", "https://www.streamingmedia.com/rss"),
        ("Multichannel News", "https://www.multichannel.com/rss"),
        ("Broadcast Pro ME", "https://www.broadcastprome.com/feed/"),
        ("TV Technology", "https://www.tvtechnology.com/rss"),
        ("Rapid TV News", "https://www.rapidtvnews.com/rss.xml"),
        ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),

        # Added – Boardroom Media Feeds
        ("Reuters Media & Telecom", "https://www.reutersagency.com/feed/?best-topics=media-telecom"),
        ("Bloomberg Media", "https://www.bloomberg.com/feed/podcast/etf-report.xml"),
        ("Financial Times Media", "https://www.ft.com/media?format=rss"),
        ("PwC Media Outlook", "https://www.pwc.com/gx/en/industries/tmt/rss.xml"),
        ("Ampere Analysis", "https://www.ampereanalysis.com/rss"),
    ],

    "sports": [
        # Existing
        ("ESPN News", "https://www.espn.com/espn/rss/news"),
        ("Sports Business Journal", "https://www.sportsbusinessjournal.com/RSS.aspx"),
        ("SportTechie", "https://www.sporttechie.com/feed/"),
        ("Sports Video Group", "https://www.sportsvideo.org/feed/"),
        ("Sky Sports News", "https://www.skysports.com/rss/12040"),
        ("BBC Sport", "https://feeds.bbci.co.uk/sport/rss.xml"),
        ("CBS Sports", "https://www.cbssports.com/rss/headlines"),
        ("Bleacher Report", "https://bleacherreport.com/articles/feed"),
        ("Fox Sports", "https://api.foxsports.com/v1/rss"),
        ("NBC Sports", "https://www.nbcsports.com/rss"),

        # Added – Rights, Money, Strategy
        ("Sportico", "https://www.sportico.com/feed/"),
        ("Front Office Sports", "https://frontofficesports.com/feed/"),
        ("SportsPro Media", "https://www.sportspromedia.com/feed/"),
        ("The Athletic Business", "https://theathletic.com/feed/business/"),
        ("Forbes SportsMoney", "https://www.forbes.com/sportsmoney/feed/"),
    ],

    "technology": [
        # Existing
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("Wired", "https://www.wired.com/feed/rss"),
        ("Ars Technica", "https://arstechnica.com/feed/"),
        ("VentureBeat", "https://venturebeat.com/feed/"),
        ("ZDNet", "https://www.zdnet.com/news/rss.xml"),
        ("Engadget", "https://www.engadget.com/rss.xml"),
        ("Hacker News", "https://news.ycombinator.com/rss"),
        ("Techmeme", "https://www.techmeme.com/feed.xml"),
        ("GigaOM", "https://gigaom.com/feed/"),

        # Added – CEO / Boardroom Tech
        ("Reuters Technology", "https://www.reuters.com/rssFeed/technologyNews"),
        ("Bloomberg Technology", "https://www.bloomberg.com/feed/podcast/technology.xml"),
        ("Financial Times Technology", "https://www.ft.com/technology?format=rss"),
        ("MIT Sloan Management", "https://sloanreview.mit.edu/feed/"),
        ("Harvard Business Review", "https://hbr.org/feed"),
        ("McKinsey Digital", "https://www.mckinsey.com/capabilities/mckinsey-digital/rss"),
    ],
}
SECTIONS = {
    "telco": {"icon": "📡", "name": "Telco & OSS/BSS", "style": "col-header-pink"},
    "ott": {"icon": "📺", "name": "OTT & Streaming", "style": "col-header-purple"},
    "sports": {"icon": "🏆", "name": "Sports & Events", "style": "col-header-green"},
    "technology": {"icon": "⚡", "name": "Technology", "style": "col-header-orange"},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

def classify(title, summary=""):
    text = (title + " " + summary).lower()
    for name, kws in EVERGENT_CLIENTS.items():
        for kw in kws:
            if kw in text:
                return "CLIENT", name
    for name, kws in COMPETITORS.items():
        for kw in kws:
            if kw in text:
                return "COMPETITOR", name
    for name, kws in TOP_TELCOS.items():
        for kw in kws:
            if kw in text:
                return "TELCO", name
    return "GENERAL", ""

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
        cutoff = datetime.now() - timedelta(hours=96)
        for entry in feed.entries[:30]:
            title = clean(entry.get("title", ""))
            if len(title) < 20 or any(x in title.lower() for x in ["click here", "subscribe", "download now", "sign up", "sponsored", "advertisement"]):
                continue
            summary = clean(entry.get("summary", ""))
            link = entry.get("link", "")
            pub = datetime.now()
            for k in ["published_parsed", "updated_parsed"]:
                val = getattr(entry, k, None)
                if val:
                    try:
                        pub = datetime(*val[:6])
                    except:
                        pass
                    break
            if pub < cutoff:
                continue
            ptype, entity = classify(title, summary)
            items.append({
                "title": title,
                "link": link,
                "pub": pub,
                "source": source,
                "ptype": ptype,
                "entity": entity,
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
            h = hashlib.md5(item["title"].lower()[:50].encode()).hexdigest()
            if h not in seen:
                seen.add(h)
                unique.append(item)
        unique.sort(key=lambda x: -x["pub"].timestamp())
        data[cat] = unique[:50]
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
        
        tag_html = ""
        if item["entity"]:
            safe_entity = escape_html(item["entity"])
            if item["ptype"] == "CLIENT":
                tag_html = f'<span class="tag-client">{safe_entity}</span>'
            elif item["ptype"] == "COMPETITOR":
                tag_html = f'<span class="tag-competitor">{safe_entity}</span>'
            elif item["ptype"] == "TELCO":
                tag_html = f'<span class="tag-telco">{safe_entity}</span>'
        
        cards += f'''<div class="news-card">
<a href="{safe_link}" target="_blank" class="news-title">{safe_title}</a>
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
{tag_html}
</div>
</div>'''
    
    if not items:
        cards = '<div style="text-align:center;color:#94a3b8;padding:30px;">Loading...</div>'
    
    body = f'<div class="col-body">{cards}</div>'
    
    return header + body

def main():
    st.markdown('<div class="main-title">🌐 Global Telecom & OTT Stellar Nexus</div>', unsafe_allow_html=True)
    
    with st.spinner("Loading executive feeds..."):
        data = load_feeds()
    
    cols = st.columns(4)
    cat_list = ["telco", "ott", "sports", "technology"]
    
    for idx, cat in enumerate(cat_list):
        sec = SECTIONS[cat]
        items = data.get(cat, [])
        
        with cols[idx]:
            column_html = render_column(cat, items, sec)
            st.markdown(column_html, unsafe_allow_html=True)
    
    st.markdown(f'<div class="footer-text">CEO Dashboard • Auto-refresh: 10 min • {datetime.now().strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
