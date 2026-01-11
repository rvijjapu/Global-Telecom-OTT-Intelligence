pip install beautifulsoup4
import streamlit as st
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import hashlib
from difflib import SequenceMatcher
import json
import urllib.parse
from bs4 import BeautifulSoup

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'keep_alive' not in st.session_state:
    st.session_state.keep_alive = datetime.now()

GROQ_API_KEY = "PUT_YOUR_KEY_HERE"

# ══════════════════════════════════════════════════════════════════════════════
# SECTION URLS (ONLY SOURCE OF TRUTH)
# ══════════════════════════════════════════════════════════════════════════════
SECTION_URLS = {
    "telco": "https://www.google.com/search?q=recent+telecom+OSS+BSS+key+announcements+2026&udm=50",
    "ott": "https://www.google.com/search?q=recent+OTT+streaming+key+announcements+2026&udm=50",
    "sports": "https://www.google.com/search?q=recent+sports+media+rights+events+2026&udm=50",
    "technology": "https://www.google.com/search?q=recent+technology+AI+cloud+platform+deals+2026&udm=50"
}

YEAR_EXCLUSIONS = ["2025", "2024", "2023", "2022"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════════════════════
def clean_text(raw):
    if not raw:
        return ""
    text = html.unescape(re.sub(r'<[^>]+>', '', str(raw)))
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_hash(text):
    return hashlib.md5(text.lower().encode()).hexdigest()[:12]

def title_similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def is_2026_only(text):
    t = text.lower()
    for y in YEAR_EXCLUSIONS:
        if y in t:
            return False
    return "2026" in t or any(x in t for x in ["today", "hours ago", "days ago", "this week"])

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE SEARCH URL PARSER (STRICT)
# ══════════════════════════════════════════════════════════════════════════════
def fetch_from_section_url(section_key, max_results=20):
    url = SECTION_URLS.get(section_key)
    if not url:
        return []

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        items, seen = [], set()

        for a in soup.select("a"):
            title = clean_text(a.get_text())
            link = a.get("href", "")

            if not title or len(title) < 30:
                continue

            if link.startswith("/url?q="):
                link = link.split("/url?q=")[1].split("&")[0]

            if not link.startswith("http"):
                continue

            if not is_2026_only(title):
                continue

            h = get_hash(title)
            if h in seen:
                continue

            items.append({
                "title": title,
                "summary": title,
                "link": link,
                "hash": h
            })
            seen.add(h)

            if len(items) >= max_results:
                break

        return items
    except:
        return []

@st.cache_data(ttl=180, show_spinner=False)
def fetch_all_sections():
    return {k: fetch_from_section_url(k) for k in SECTION_URLS.keys()}

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

        data = r.json()["choices"][0]["message"]["content"]
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
def render_card(h, color):
    return f"""
    <div class="highlight-card {color}">
        <div class="highlight-title">{html.escape(h['title'])}</div>
        <div class="highlight-description">{html.escape(h['description'])}</div>
        <a href="{h['link']}" target="_blank" class="read-more">Read Full Story →</a>
    </div>
    """

def render_section(icon, name, highlights, header, color):
    cards = "".join(render_card(h, color) for h in highlights)
    return f"""
    <div class="col-header {header}">{icon} {name}</div>
    <div class="col-body">{cards}</div>
    """

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 🌐 Global Telecom & OTT Stellar Nexus — LIVE 2026")

with st.spinner("Fetching 2026 intelligence..."):
    all_news = fetch_all_sections()

sections = [
    ("telco", "TELCO OSS/BSS", "📡", "col-header-pink", "pink"),
    ("ott", "OTT & STREAMING", "📺", "col-header-purple", "purple"),
    ("sports", "SPORTS & EVENTS", "🏆", "col-header-green", "green"),
    ("technology", "TECHNOLOGY", "⚡", "col-header-orange", "orange")
]

cols = st.columns(4)

for col, (k, name, icon, header, color) in zip(cols, sections):
    with col:
        highlights = generate_ai_descriptions(all_news.get(k, []), name)
        st.markdown(render_section(icon, name, highlights, header, color), unsafe_allow_html=True)

st.markdown(f"""
<div class="footer">
Updated: {datetime.now().strftime("%d %b %Y %I:%M %p")} | Auto refresh 5 min
</div>
""", unsafe_allow_html=True)

st.markdown("""
<script>
setTimeout(()=>location.reload(),300000);
</script>
""", unsafe_allow_html=True)
