import streamlit as st
import requests
from datetime import datetime
import html
import re
import hashlib
from difflib import SequenceMatcher
import json
import urllib.parse

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
# API KEY
# ══════════════════════════════════════════════════════════════════════════════
GROQ_API_KEY = "PUT_YOUR_KEY_HERE"

# ══════════════════════════════════════════════════════════════════════════════
# SECTION URLS — SINGLE SOURCE OF TRUTH
# ══════════════════════════════════════════════════════════════════════════════
SECTION_URLS = {
    "telco": "https://www.google.com/search?q=telecom+OSS+BSS+key+announcements+2026&udm=50",
    "ott": "https://www.google.com/search?q=OTT+streaming+key+announcements+2026&udm=50",
    "sports": "https://www.google.com/search?q=sports+media+rights+events+2026&udm=50",
    "technology": "https://www.google.com/search?q=technology+AI+cloud+platform+deals+2026&udm=50"
}

YEAR_EXCLUSIONS = ["2025", "2024", "2023", "2022"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
def clean_text(text):
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def get_hash(text):
    return hashlib.md5(text.lower().encode()).hexdigest()[:12]

def is_2026_only(text):
    t = text.lower()
    for y in YEAR_EXCLUSIONS:
        if y in t:
            return False
    return "2026" in t or any(k in t for k in ["today", "hours ago", "days ago", "this week"])

# ══════════════════════════════════════════════════════════════════════════════
# STRICT GOOGLE SEARCH HTML PARSER (NO BS4)
# ══════════════════════════════════════════════════════════════════════════════
def fetch_from_section_url(section_key, max_results=20):
    url = SECTION_URLS.get(section_key)
    if not url:
        return []

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        html_text = r.text

        # Extract Google redirect links
        matches = re.findall(
            r'<a href="/url\?q=(https?://[^&"]+)[^"]*".*?>(.*?)</a>',
            html_text,
            re.DOTALL
        )

        items = []
        seen = set()

        for link, raw_title in matches:
            title = clean_text(raw_title)

            if len(title) < 30:
                continue
            if not is_2026_only(title):
                continue

            h = get_hash(title)
            if h in seen:
                continue

            items.append({
                "title": title,
                "summary": title,
                "link": urllib.parse.unquote(link),
                "hash": h
            })

            seen.add(h)

            if len(items) >= max_results:
                break

        return items

    except:
        return []

@st.cache_data(ttl=180)
def fetch_all_sections():
    return {k: fetch_from_section_url(k) for k in SECTION_URLS}

# ══════════════════════════════════════════════════════════════════════════════
# AI SUMMARIES
# ══════════════════════════════════════════════════════════════════════════════
def generate_ai_descriptions(news_items, section_name):
    if not news_items:
        return []

    text = "\n\n".join(
        f"{i+1}. {n['title']} ({n['link']})"
        for i, n in enumerate(news_items[:14])
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
                    {"role": "system", "content": f"You are a 2026 {section_name} industry analyst."},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.2,
                "max_tokens": 3000
            },
            timeout=40
        )

        return [{
            "title": n["title"][:90],
            "description": n["summary"][:280],
            "link": n["link"]
        } for n in news_items[:14]]

    except:
        return [{
            "title": n["title"],
            "description": n["summary"],
            "link": n["link"]
        } for n in news_items[:14]]

# ══════════════════════════════════════════════════════════════════════════════
# UI RENDER
# ══════════════════════════════════════════════════════════════════════════════
def render_card(h):
    return f"""
    <div style="padding:12px;border-left:4px solid #3b82f6;margin-bottom:10px;background:#fff;">
        <div style="font-weight:700">{html.escape(h['title'])}</div>
        <div style="font-size:0.85rem;color:#475569;margin:6px 0">
            {html.escape(h['description'])}
        </div>
        <a href="{h['link']}" target="_blank">Read →</a>
    </div>
    """

def render_section(name, highlights):
    return "".join(render_card(h) for h in highlights)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 🌐 Global Telecom & OTT Stellar Nexus — LIVE 2026")

with st.spinner("Fetching 2026 intelligence…"):
    all_news = fetch_all_sections()

cols = st.columns(4)

sections = [
    ("telco", "TELCO OSS/BSS"),
    ("ott", "OTT & STREAMING"),
    ("sports", "SPORTS & EVENTS"),
    ("technology", "TECHNOLOGY")
]

for col, (key, title) in zip(cols, sections):
    with col:
        highlights = generate_ai_descriptions(all_news.get(key, []), title)
        st.markdown(f"### {title}")
        st.markdown(render_section(title, highlights), unsafe_allow_html=True)

st.markdown(f"""
Updated: {datetime.now().strftime("%d %b %Y %I:%M %p")} • Auto refresh 5 min
""")

st.markdown("""
<script>
setTimeout(()=>location.reload(),300000);
</script>
""", unsafe_allow_html=True)
