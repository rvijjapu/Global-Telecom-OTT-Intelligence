import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# KEYWORDS (STRICT)
# ─────────────────────────────────────────────
TELCO_REQUIRED = [
    "oss","bss","billing","charging","revenue management",
    "telecom deal","telco partnership","5g monetization",
    "network slicing","cloud-native oss","api-based bss"
]

OTT_REQUIRED = [
    "ott","streaming","svod","avod","fast channel",
    "subscriber","content deal","platform expansion",
    "distribution partnership","sports streaming"
]

SPORTS_REQUIRED = [
    "media rights","broadcasting rights","sports streaming",
    "league partnership","sports ott","fan engagement",
    "pay-per-view","digital ticketing"
]

TECH_REQUIRED = [
    "artificial intelligence","ai platform","enterprise ai",
    "cloud platform","saas","data platform",
    "technology acquisition","strategic partnership"
]

GLOBAL_EXCLUDE = [
    "oil","gas","petroleum","insurance","banking core",
    "semiconductor","chip","mining","celebrity",
    "movie review","box office","match score","injury"
]

# ─────────────────────────────────────────────
# RSS SOURCES (STABLE & TRUSTED)
# ─────────────────────────────────────────────
RSS_FEEDS = [
    ("Telecoms.com","https://www.telecoms.com/feed","telco"),
    ("Light Reading","https://www.lightreading.com/rss/simple","telco"),
    ("Fierce Telecom","https://www.fierce-network.com/rss.xml","telco"),
    ("Mobile World Live","https://www.mobileworldlive.com/feed/","telco"),

    ("Variety","https://variety.com/feed/","ott"),
    ("Deadline","https://deadline.com/feed/","ott"),
    ("Hollywood Reporter","https://www.hollywoodreporter.com/feed/","ott"),

    ("SportsPro","https://www.sportspromedia.com/feed/","sports"),

    ("TechCrunch","https://techcrunch.com/feed/","technology"),
    ("The Verge","https://www.theverge.com/rss/index.xml","technology"),
    ("Wired","https://www.wired.com/feed/rss","technology")
]

SECTIONS = {
    "telco": "📡 TELCO OSS/BSS",
    "ott": "📺 OTT & STREAMING",
    "sports": "🏆 SPORTS MEDIA",
    "technology": "⚡ AI & TECHNOLOGY"
}

HEADERS = {"User-Agent":"Mozilla/5.0"}

# ─────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────
def clean(txt):
    return html.unescape(re.sub(r"<[^>]+>","",str(txt))).strip()

def is_relevant(title, summary, section):
    text = (title + " " + summary).lower()
    if any(x in text for x in GLOBAL_EXCLUDE):
        return False

    required = {
        "telco": TELCO_REQUIRED,
        "ott": OTT_REQUIRED,
        "sports": SPORTS_REQUIRED,
        "technology": TECH_REQUIRED
    }.get(section, [])

    return any(k in text for k in required)

# ─────────────────────────────────────────────
# FETCHER
# ─────────────────────────────────────────────
def fetch_feed(source, url, section):
    items = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return items

        feed = feedparser.parse(resp.content)
        cutoff = datetime.now() - timedelta(days=30)

        for e in feed.entries[:15]:
            title = clean(e.get("title",""))
            if len(title) < 35:
                continue

            summary = clean(e.get("summary", title))
            if not is_relevant(title, summary, section):
                continue

            pub = None
            for k in ("published_parsed","updated_parsed"):
                val = getattr(e,k,None)
                if val:
                    pub = datetime(*val[:6])
                    break

            if not pub or pub < cutoff:
                continue

            items.append({
                "title": title,
                "link": e.get("link","#"),
                "source": source,
                "pub": pub
            })
    except:
        pass

    return items

@st.cache_data(ttl=600)
def load_all():
    data = {k:[] for k in SECTIONS}

    with ThreadPoolExecutor(max_workers=10) as exe:
        futures = [exe.submit(fetch_feed,s,u,c) for s,u,c in RSS_FEEDS]
        for f in as_completed(futures):
            try:
                for a in f.result():
                    data[a.get("section","")].append(a)
            except:
                pass

    return data

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
st.markdown("""
<h1 style="text-align:center;">🌐 Global Telecom & OTT Stellar Nexus</h1>
<p style="text-align:center;color:gray;">Strict RSS-based Executive Intelligence • 2026</p>
""", unsafe_allow_html=True)

with st.spinner("Loading high-signal intelligence…"):
    data = load_all()

cols = st.columns(4)

for idx, key in enumerate(SECTIONS):
    with cols[idx]:
        st.markdown(f"### {SECTIONS[key]}")
        articles = data.get(key, [])

        if not articles:
            st.info("No high-relevance news in last 30 days")
        else:
            for a in articles[:8]:
                hrs = int((datetime.now()-a["pub"]).total_seconds()/3600)
                time_str = "Now" if hrs<3 else f"{hrs}h ago" if hrs<24 else f"{hrs//24}d ago"

                st.markdown(
                    f"""
                    <div style="border:1px solid #e5e7eb;padding:12px;border-radius:8px;margin-bottom:10px;">
                        <a href="{a['link']}" target="_blank" style="font-weight:600;">
                            {a['title']}
                        </a>
                        <div style="font-size:0.8rem;color:#64748b;">
                            {a['source']} • {time_str}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

st.markdown(f"""
<p style="text-align:center;color:#94a3b8;">
Last updated {datetime.now().strftime('%d %b %Y %H:%M')} • Auto refresh 5 min
</p>
""", unsafe_allow_html=True)

st.markdown("<script>setTimeout(()=>location.reload(),300000);</script>", unsafe_allow_html=True)
