import streamlit as st
import feedparser
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import html, re, hashlib, json, urllib.parse
from difflib import SequenceMatcher

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "keep_alive" not in st.session_state:
    st.session_state.keep_alive = datetime.now()

GROQ_API_KEY = "YOUR_GROQ_KEY"

# ─────────────────────────────────────────────
# SECTION QUERIES (SEARCH SEEDS ONLY)
# ─────────────────────────────────────────────
SECTION_QUERIES = {
    "telco": "telecom OSS BSS 5G billing revenue management 2026",
    "ott": "OTT streaming platform content subscription 2026",
    "sports": "sports media rights broadcasting streaming 2026",
    "technology": "enterprise AI cloud SaaS platform 2026"
}

SECTION_BACKUP_QUERIES = {
    "telco": ["telecom billing system", "OSS BSS transformation", "5G monetization"],
    "ott": ["OTT platform deal", "streaming content partnership"],
    "sports": ["sports broadcast rights", "league media deal"],
    "technology": ["enterprise AI platform", "cloud SaaS acquisition"]
}

# ─────────────────────────────────────────────
# RELEVANCE CONTROL (CORE FIX)
# ─────────────────────────────────────────────

TELCO_KEYWORDS = [
    "oss", "bss", "billing", "charging", "revenue management",
    "5g", "network slicing", "cloud native telecom",
    "csp", "telecom transformation"
]

OTT_KEYWORDS = [
    "ott", "streaming", "video platform", "svod", "avod",
    "fast channel", "content licensing", "subscriber"
]

SPORTS_KEYWORDS = [
    "sports rights", "media rights", "broadcasting",
    "sports streaming", "league", "tournament", "esports"
]

TECH_KEYWORDS = [
    "enterprise ai", "cloud platform", "saas",
    "data platform", "enterprise software", "b2b tech"
]

GLOBAL_EXCLUSIONS = [
    "oil", "gas", "petroleum", "energy",
    "insurance", "bank", "loan",
    "semiconductor", "chip", "fab",
    "mining", "steel", "cement",
    "pharma", "biotech", "drug",
    "automobile", "ev battery"
]

SECTION_KEYWORDS = {
    "telco": TELCO_KEYWORDS,
    "ott": OTT_KEYWORDS,
    "sports": SPORTS_KEYWORDS,
    "technology": TECH_KEYWORDS
}

# ─────────────────────────────────────────────
# EVERGENT SIGNAL BOOST
# ─────────────────────────────────────────────
EVERGENT_TERMS = set()
for group in [EVERGENT_CLIENTS, COMPETITITORS, TOP_TELCOS]:
    for names in group.values():
        for n in names:
            EVERGENT_TERMS.add(n.lower())

# ─────────────────────────────────────────────
# UTILS
# ─────────────────────────────────────────────
def clean_text(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", str(t)))).strip()

def get_hash(t):
    return hashlib.md5(t.lower().encode()).hexdigest()[:12]

def is_relevant(item, section):
    text = f"{item['title']} {item['summary']}".lower()

    if any(x in text for x in GLOBAL_EXCLUSIONS):
        return False

    if not any(k in text for k in SECTION_KEYWORDS.get(section, [])):
        return False

    return True

# ─────────────────────────────────────────────
# GOOGLE NEWS FETCH
# ─────────────────────────────────────────────
def fetch_google_news(query):
    try:
        q = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(requests.get(url, timeout=12).content)

        items = []
        for e in feed.entries:
            title = clean_text(e.title)
            link = e.link
            summary = clean_text(getattr(e, "summary", title))

            if len(title) < 30:
                continue

            items.append({
                "title": title,
                "summary": summary,
                "link": link,
                "hash": get_hash(title)
            })

        return items
    except:
        return []

@st.cache_data(ttl=300)
def fetch_section_news(section):
    seen, results = set(), []

    queries = [SECTION_QUERIES[section]] + SECTION_BACKUP_QUERIES[section]

    for q in queries:
        for item in fetch_google_news(q):
            if item["hash"] in seen:
                continue
            if not is_relevant(item, section):
                continue
            results.append(item)
            seen.add(item["hash"])

    return results[:18]

# ─────────────────────────────────────────────
# AI SUMMARIES (UNCHANGED)
# ─────────────────────────────────────────────
def generate_ai_descriptions(news, section):
    if not news:
        return []

    text = "\n".join(
        f"{i+1}. {n['title']} – {n['summary'][:200]}"
        for i, n in enumerate(news)
    )

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": f"You are a {section} industry analyst."},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.15,
                "max_tokens": 3000
            },
            timeout=45
        )

        data = json.loads(re.search(r"\{.*\}", r.json()["choices"][0]["message"]["content"], re.S).group())
        return data.get("highlights", [])[:14]
    except:
        return [{"title": n["title"], "description": n["summary"], "link": n["link"]} for n in news[:14]]

# ─────────────────────────────────────────────
# UI RENDER (UNCHANGED)
# ─────────────────────────────────────────────
st.markdown("## 🌐 Global Telecom & OTT Stellar Nexus — LIVE 2026")

sections = [
    ("telco", "TELCO OSS/BSS", "📡"),
    ("ott", "OTT & STREAMING", "📺"),
    ("sports", "SPORTS & EVENTS", "🏆"),
    ("technology", "TECHNOLOGY", "⚡")
]

cols = st.columns(4)

for col, (key, name, icon) in zip(cols, sections):
    with col:
        news = fetch_section_news(key)
        highlights = generate_ai_descriptions(news, name)
        st.subheader(f"{icon} {name}")
        for h in highlights:
            st.markdown(f"**{h['title']}**")
            st.caption(h["description"])
            st.markdown(f"[Read →]({h['link']})")

st.caption(f"Updated: {datetime.now().strftime('%d %b %Y %I:%M %p')}")
