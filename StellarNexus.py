import streamlit as st
import feedparser
import requests
from datetime import datetime
import html
import re
import hashlib
from difflib import SequenceMatcher
import urllib.parse

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus — LIVE 2026",
    page_icon="🌐",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# KEYWORD DEFINITIONS (STRICT & RELEVANT)
# ─────────────────────────────────────────────────────────────

TELCO_KEYWORDS = [
    "telecom", "telco", "oss", "bss", "5g", "network", "billing",
    "charging", "mediation", "subscriber", "operator", "mvno",
    "roaming", "core network", "cloud native telecom"
]

OTT_KEYWORDS = [
    "ott", "streaming", "vod", "svod", "avod",
    "content platform", "media streaming", "video platform",
    "subscription video", "digital media"
]

SPORTS_KEYWORDS = [
    "sports broadcast", "media rights", "league", "tournament",
    "live sports", "sports streaming", "sports network"
]

TECH_KEYWORDS = [
    "cloud", "ai", "artificial intelligence", "saas",
    "platform", "enterprise software", "data platform"
]

EXCLUDED_KEYWORDS = [
    "oil", "gas", "energy", "insurance", "bank", "finance",
    "stock", "share price", "semiconductor", "chip", "mining"
]

SECTION_KEYWORDS = {
    "telco": TELCO_KEYWORDS,
    "ott": OTT_KEYWORDS,
    "sports": SPORTS_KEYWORDS,
    "technology": TECH_KEYWORDS
}

# ─────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────

def clean_text(text):
    if not text:
        return ""
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def contains_any(text, keywords):
    t = text.lower()
    return any(k in t for k in keywords)

def excluded(text):
    t = text.lower()
    return any(k in t for k in EXCLUDED_KEYWORDS)

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def unique(items):
    seen = []
    out = []
    for i in items:
        if not any(similarity(i["title"], s) > 0.65 for s in seen):
            seen.append(i["title"])
            out.append(i)
    return out

# ─────────────────────────────────────────────────────────────
# GOOGLE NEWS RSS FETCH
# ─────────────────────────────────────────────────────────────

def fetch_news(section, limit=12):
    keywords = SECTION_KEYWORDS[section]
    query = " ".join(keywords) + " 2026"

    url = (
        "https://news.google.com/rss/search?"
        f"q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
    )

    feed = feedparser.parse(url)
    items = []

    for e in feed.entries:
        title = clean_text(e.title)
        link = e.link
        summary = clean_text(e.get("summary", ""))

        text_blob = f"{title} {summary}"

        if excluded(text_blob):
            continue
        if not contains_any(text_blob, keywords):
            continue
        if len(title) < 30:
            continue

        items.append({
            "title": title,
            "summary": summary[:280],
            "link": link
        })

        if len(items) >= limit * 2:
            break

    return unique(items)[:limit]

# ─────────────────────────────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────────────────────────────

def render_card(item, color):
    return f"""
    <div style="
        background:white;
        padding:14px;
        margin-bottom:12px;
        border-left:4px solid {color};
        border-radius:10px;
        box-shadow:0 4px 12px rgba(0,0,0,0.08)
    ">
        <div style="font-weight:700;font-size:0.95rem">
            {html.escape(item['title'])}
        </div>
        <div style="font-size:0.85rem;color:#475569;margin:6px 0">
            {html.escape(item['summary'])}
        </div>
        <a href="{item['link']}" target="_blank"
           style="font-size:0.8rem;font-weight:600;color:#2563eb">
           Read Full Story →
        </a>
    </div>
    """

def render_section(title, icon, items, color):
    cards = "".join(render_card(i, color) for i in items) or \
            "<p style='color:#64748b'>No relevant news found</p>"

    return f"""
    <div style="
        background:linear-gradient(135deg,{color},#00000020);
        color:white;
        padding:14px;
        border-radius:14px 14px 0 0;
        font-weight:800;
        text-align:center
    ">
        {icon} {title}
    </div>
    <div style="
        background:white;
        padding:12px;
        min-height:650px;
        max-height:750px;
        overflow-y:auto;
        border-radius:0 0 14px 14px
    ">
        {cards}
    </div>
    """

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────

st.markdown("""
<h2 style="text-align:center">
🌐 Global Telecom & OTT Stellar Nexus — LIVE 2026
</h2>
<p style="text-align:center;color:#64748b">
Executive-grade competitive intelligence
</p>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FETCH & DISPLAY (IMMEDIATE PER SECTION)
# ─────────────────────────────────────────────────────────────

cols = st.columns(4)

sections = [
    ("telco", "TELCO OSS/BSS", "📡", "#ec4899"),
    ("ott", "OTT & STREAMING", "📺", "#8b5cf6"),
    ("sports", "SPORTS & EVENTS", "🏆", "#10b981"),
    ("technology", "TECHNOLOGY", "⚡", "#f97316"),
]

for col, (key, label, icon, color) in zip(cols, sections):
    with col:
        with st.spinner(f"Loading {label}…"):
            data = fetch_news(key)
        st.markdown(render_section(label, icon, data, color),
                    unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────

st.markdown(f"""
<p style="text-align:center;color:#64748b;font-size:0.8rem;margin-top:20px">
Last updated: {datetime.now().strftime('%d %b %Y %I:%M %p')} · Auto-refresh 5 min
</p>
""", unsafe_allow_html=True)

st.markdown("""
<script>
setTimeout(() => location.reload(), 300000);
</script>
""", unsafe_allow_html=True)
