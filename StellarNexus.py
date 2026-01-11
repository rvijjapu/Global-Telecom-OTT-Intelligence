import streamlit as st
import requests
from datetime import datetime
import html
import re
import hashlib
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

if "keep_alive" not in st.session_state:
    st.session_state.keep_alive = datetime.now()

# ══════════════════════════════════════════════════════════════════════════════
# API KEY
# ══════════════════════════════════════════════════════════════════════════════
GROQ_API_KEY = "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"

# ══════════════════════════════════════════════════════════════════════════════
# SECTION URLS — ONLY SOURCE
# ══════════════════════════════════════════════════════════════════════════════
SECTION_URLS = {
    "telco": "https://www.google.com/search?q=recent+telecom+OSS+BSS+key+announcements+providers+organizers+news+key+announcements+2026+exclude+2025&udm=50",
    "ott": "https://www.google.com/search?q=recent+OTT+providers+key+announcements+mergers+acquisitions+deals+profit+losses+2026+exclude+2025&udm=50",
    "sports": "https://www.google.com/search?q=recent+Sports+Events+key+announcements+mergers+acquisitions+2026+exclude+2025&udm=50",
    "technology": "https://www.google.com/search?q=recent+Technology+key+announcements+mergers+acquisitions+2026+exclude+2025&udm=50"
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
    text = html.unescape(re.sub(r"<[^>]+>", "", raw))
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def get_hash(text):
    return hashlib.md5(text.lower().encode()).hexdigest()[:12]

def is_2026_only(text):
    t = text.lower()
    for y in YEAR_EXCLUSIONS:
        if y in t:
            return False
    return "2026" in t or any(x in t for x in [
        "today", "hours ago", "days ago", "this week", "this month"
    ])

# ══════════════════════════════════════════════════════════════════════════════
# STRICT GOOGLE SEARCH PARSER (NO RSS, NO BS4)
# ══════════════════════════════════════════════════════════════════════════════
def fetch_from_section_url(section, max_results=20):
    url = SECTION_URLS.get(section)
    if not url:
        return []

    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        html_text = r.text

        matches = re.findall(
            r'<a href="/url\\?q=(https?://[^&"]+)[^"]*".*?>(.*?)</a>',
            html_text,
            re.DOTALL
        )

        items, seen = [], set()

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
                "link": urllib.parse.unquote(link)
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
# AI SUMMARIES (UNCHANGED)
# ══════════════════════════════════════════════════════════════════════════════
def generate_ai_descriptions(news_items, section_name):
    if not news_items:
        return []

    news_text = "\n\n".join(
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
                    {"role": "user", "content": news_text}
                ],
                "temperature": 0.15,
                "max_tokens": 3000
            },
            timeout=40
        )

        return [{
            "title": n["title"][:90],
            "description": n["summary"][:260],
            "link": n["link"]
        } for n in news_items[:14]]

    except:
        return [{
            "title": n["title"],
            "description": n["summary"],
            "link": n["link"]
        } for n in news_items[:14]]

# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("## 🌐 Global Telecom & OTT Stellar Nexus — LIVE 2026")

with st.spinner("⚡ Fetching 2026 executive intelligence…"):
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
        for h in highlights:
            st.markdown(
                f"""
                <div style="background:#fff;padding:12px;margin-bottom:10px;
                border-left:4px solid #3b82f6;border-radius:8px">
                    <div style="font-weight:700">{html.escape(h['title'])}</div>
                    <div style="font-size:0.85rem;color:#475569;margin:6px 0">
                        {html.escape(h['description'])}
                    </div>
                    <a href="{h['link']}" target="_blank">Read →</a>
                </div>
                """,
                unsafe_allow_html=True
            )

st.markdown(
    f"Updated: {datetime.now().strftime('%d %b %Y %I:%M %p')} • Auto refresh 5 min"
)

st.markdown("""
<script>
setTimeout(function(){location.reload();},300000);
</script>
""", unsafe_allow_html=True)
