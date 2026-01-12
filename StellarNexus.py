import streamlit as st
import feedparser
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
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

if 'keep_alive' not in st.session_state:
    st.session_state.keep_alive = datetime.now()

GROQ_API_KEY = "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"

# ══════════════════════════════════════════════════════════════════════════════
# INDUSTRY-FOCUSED SEARCH QUERIES
# ══════════════════════════════════════════════════════════════════════════════
SECTION_RSS_QUERIES = {
    "telco": [
        "telecom operator OSS BSS acquisition merger 2026",
        "Amdocs Netcracker CSG Oracle telecom deal 2026",
        "5G network operator partnership Ericsson Nokia 2026",
        "Verizon AT&T T-Mobile Vodafone earnings 2026"
    ],
    "ott": [
        "Netflix Disney streaming merger acquisition 2026",
        "HBO Max Paramount Peacock streaming deal 2026",
        "Amazon Prime Apple TV partnership 2026",
        "streaming subscriber revenue earnings 2026"
    ],
    "sports": [
        "NFL NBA MLB broadcasting rights deal 2026",
        "ESPN Fox Sports broadcasting partnership 2026",
        "FanDuel DraftKings sports betting merger 2026",
        "sports streaming media rights 2026"
    ],
    "technology": [
        "Microsoft Google Amazon cloud partnership 2026",
        "OpenAI AI platform deal merger 2026",
        "enterprise SaaS software acquisition 2026",
        "fintech payment platform deal 2026"
    ]
}

# EXCLUSION FILTERS
GLOBAL_EXCLUSIONS = [
    "solar panel", "credit card processor", "labor law", "minimum wage", "work week",
    "immigration", "public works", "tax rate", "gst", "water billing", "city council",
    "municipality", "local government", "ordinance", "zoning", "permit",
    "semiconductor", "chip manufacturer", "oil", "gas", "petroleum", "mining", "coal",
    "real estate", "construction", "automotive", "vehicle", "insurance", "mortgage"
]

YEAR_EXCLUSIONS = ["2024", "2025", "2023", "2022", "2021", "2020"]

# INDUSTRY VALIDATORS
TELCO_VALIDATORS = ["telecom", "telco", "operator", "network", "5g", "oss", "bss", "billing", 
                    "verizon", "at&t", "vodafone", "bt group", "ericsson", "nokia", "amdocs", "netcracker"]

OTT_VALIDATORS = ["streaming", "ott", "netflix", "disney", "hbo", "paramount", "peacock",
                  "amazon prime", "apple tv", "hulu", "subscriber", "svod", "avod"]

SPORTS_VALIDATORS = ["nfl", "nba", "mlb", "nhl", "espn", "fox sports", "broadcasting rights",
                     "sports betting", "fanduel", "draftkings", "sports media"]

TECH_VALIDATORS = ["microsoft", "google", "amazon", "apple", "meta", "oracle", "salesforce",
                   "openai", "cloud computing", "saas", "enterprise software", "fintech", "ai platform"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM STYLING - FIXED LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Inter', sans-serif;
    }
    
    .header-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.98) 100%);
        padding: 1.5rem 2rem;
        text-align: center;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        margin: 0 0 1.5rem 0;
        position: relative;
    }
    
    .header-container::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #ec4899, #8b5cf6, #10b981, #f97316);
        border-radius: 0 0 16px 16px;
    }
    
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.4rem;
        font-weight: 500;
    }
    
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-left: 10px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* Fixed Column Layout */
    .col-header {
        padding: 12px 14px;
        border-radius: 12px 12px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.85rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #7c3aed);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #059669);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #ea580c);}
    
    .col-body {
        background: rgba(255,255,255,0.98);
        border-radius: 0 0 12px 12px;
        padding: 10px;
        height: 600px;
        overflow-y: auto;
        overflow-x: hidden;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }
    
    .highlight-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-left: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    .highlight-card:hover {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        transform: translateY(-2px);
        border-left-width: 5px;
    }
    
    .highlight-card.pink {border-left-color: #ec4899;}
    .highlight-card.purple {border-left-color: #8b5cf6;}
    .highlight-card.green {border-left-color: #10b981;}
    .highlight-card.orange {border-left-color: #f97316;}
    
    .highlight-title {
        color: #0f172a;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 6px;
        line-height: 1.3;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        word-wrap: break-word;
    }
    
    .highlight-description {
        color: #475569;
        font-size: 0.78rem;
        line-height: 1.5;
        margin-bottom: 8px;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        word-wrap: break-word;
    }
    
    .read-more {
        color: #2563eb;
        font-weight: 600;
        font-size: 0.75rem;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        transition: all 0.15s ease;
    }
    
    .read-more:hover {
        color: #1d4ed8;
        gap: 8px;
    }
    
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.95);
        font-size: 0.75rem;
        margin-top: 15px;
        padding: 12px 20px;
        background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(30,41,59,0.95));
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .col-body::-webkit-scrollbar {width: 5px;}
    .col-body::-webkit-scrollbar-track {background: #f1f5f9; border-radius: 10px;}
    .col-body::-webkit-scrollbar-thumb {background: linear-gradient(180deg, #94a3b8, #64748b); border-radius: 10px;}
    
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .loading-spinner {
        text-align: center;
        padding: 40px 20px;
        color: #64748b;
        font-size: 0.85rem;
    }
    
    /* Fix Streamlit column spacing */
    [data-testid="column"] {
        padding: 0 8px !important;
    }
    
    div[data-testid="stHorizontalBlock"] {
        gap: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def clean_text(raw):
    if not raw:
        return ""
    text = html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_summary(entry, max_len=400):
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and content:
                content = content[0].get('value', '')
            summary = clean_text(content)
            if summary and len(summary) > 50:
                return summary[:max_len].rsplit(' ', 1)[0] + '...' if len(summary) > max_len else summary
    return ""

def get_hash(text):
    return hashlib.md5(text.lower().strip().encode()).hexdigest()[:12]

def content_similarity(a, b):
    def extract_key_phrases(text):
        text_lower = text.lower()
        for word in ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']:
            text_lower = text_lower.replace(f' {word} ', ' ')
        return set(text_lower.split())
    
    phrases_a = extract_key_phrases(a)
    phrases_b = extract_key_phrases(b)
    
    if not phrases_a or not phrases_b:
        return 0
    
    intersection = len(phrases_a & phrases_b)
    union = len(phrases_a | phrases_b)
    
    return intersection / union if union > 0 else 0

def is_2026_only(text):
    text_lower = text.lower()
    
    for year in YEAR_EXCLUSIONS:
        if year in text_lower:
            return False
    
    if "2026" in text_lower:
        return True
    
    recent_indicators = ["hours ago", "hour ago", "minutes ago", "today", "yesterday"]
    return any(indicator in text_lower for indicator in recent_indicators)

def is_relevant_to_section(title, summary, section):
    text = (title + " " + summary).lower()
    
    if any(exclusion in text for exclusion in GLOBAL_EXCLUSIONS):
        return False
    
    validators = {
        "telco": TELCO_VALIDATORS,
        "ott": OTT_VALIDATORS,
        "sports": SPORTS_VALIDATORS,
        "technology": TECH_VALIDATORS
    }
    
    section_validators = validators.get(section, [])
    return any(validator in text for validator in section_validators)

# ══════════════════════════════════════════════════════════════════════════════
# NEWS FETCHER
# ══════════════════════════════════════════════════════════════════════════════
def fetch_google_news_rss(query, max_results=20):
    try:
        query_2026 = f"{query} 2026"
        encoded_query = urllib.parse.quote(query_2026)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return []
        
        feed = feedparser.parse(resp.content)
        results = []
        
        for entry in feed.entries[:max_results]:
            title = clean_text(entry.get("title", ""))
            link = entry.get("link", "")
            pub_date = entry.get("published", "")
            summary = extract_summary(entry) or title
            
            full_text = f"{title} {summary} {pub_date}"
            if not is_2026_only(full_text):
                continue
            
            if len(title) < 30 or not link.startswith("http"):
                continue
            
            results.append({
                "title": title,
                "link": link,
                "summary": summary,
                "published": pub_date,
                "hash": get_hash(title)
            })
        
        return results
    except:
        return []

@st.cache_data(ttl=180, show_spinner=False)
def fetch_section_news(section):
    all_items = []
    seen_hashes = set()
    seen_content = []
    
    queries = SECTION_RSS_QUERIES.get(section, [])
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(fetch_google_news_rss, q): q for q in queries}
        
        for future in as_completed(futures, timeout=20):
            try:
                items = future.result()
                for item in items:
                    full_text = f"{item['title']} {item['summary']}"
                    if not is_2026_only(full_text):
                        continue
                    
                    if not is_relevant_to_section(item['title'], item['summary'], section):
                        continue
                    
                    if item["hash"] in seen_hashes:
                        continue
                    
                    is_duplicate = False
                    for prev_item in seen_content:
                        title_sim = content_similarity(item["title"], prev_item["title"])
                        content_sim = content_similarity(item["summary"], prev_item["summary"])
                        
                        if title_sim > 0.65 or content_sim > 0.70:
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        continue
                    
                    all_items.append(item)
                    seen_hashes.add(item["hash"])
                    seen_content.append({"title": item["title"], "summary": item["summary"]})
                    
            except:
                continue
    
    return all_items[:15]

@st.cache_data(ttl=180, show_spinner=False)
def fetch_all_sections():
    all_news = {}
    sections = ["telco", "ott", "sports", "technology"]
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_section_news, sec): sec for sec in sections}
        
        for future in as_completed(futures, timeout=35):
            section = futures[future]
            try:
                all_news[section] = future.result()
            except:
                all_news[section] = []
    
    return all_news

# ══════════════════════════════════════════════════════════════════════════════
# AI GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
def generate_ai_descriptions(news_items, section_name):
    if not news_items:
        return []
    
    news_text = "\n\n".join([
        f"[{i+1}] {item['title']}\n{item['summary'][:250]}\n{item['link']}"
        for i, item in enumerate(news_items[:15])
    ])
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": f"""Create 12 unique {section_name} highlights from 2026 news. Remove duplicates. Each: title (12 words max), description (40-60 words). Return JSON only."""
                    },
                    {
                        "role": "user",
                        "content": f"""Create 12 highlights:\n\n{news_text}\n\nReturn: {{"highlights": [{{"title": "...", "description": "...", "link": "..."}}]}}"""
                    }
                ],
                "max_tokens": 3500,
                "temperature": 0.15
            },
            timeout=45
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
                highlights = data.get("highlights", [])[:12]
                
                unique_highlights = []
                seen_titles = []
                
                for h in highlights:
                    title = h.get("title", "")
                    is_dup = any(content_similarity(title, prev) > 0.65 for prev in seen_titles)
                    
                    if not is_dup:
                        unique_highlights.append(h)
                        seen_titles.append(title)
                
                valid_links = {item['link'] for item in news_items}
                for i, h in enumerate(unique_highlights):
                    link = h.get("link", "")
                    if not link.startswith("http") or link not in valid_links:
                        if i < len(news_items):
                            h['link'] = news_items[i]['link']
                
                return unique_highlights
    except:
        pass
    
    unique_items = []
    seen = []
    for item in news_items[:12]:
        is_dup = any(content_similarity(item['title'], s['title']) > 0.65 for s in seen)
        if not is_dup:
            unique_items.append({
                "title": item['title'][:80],
                "description": item['summary'][:250],
                "link": item['link']
            })
            seen.append(item)
    
    return unique_items

# ══════════════════════════════════════════════════════════════════════════════
# RENDER
# ══════════════════════════════════════════════════════════════════════════════
def render_card(highlight, color):
    title = html.escape(str(highlight.get("title", "No Title")))
    description = html.escape(str(highlight.get("description", "")))
    link = highlight.get("link", "#")
    
    if not link.startswith("http"):
        link = "#"
    
    return f'''
    <div class="highlight-card {color}">
        <div class="highlight-title">{title}</div>
        <div class="highlight-description">{description}</div>
        <a href="{html.escape(link)}" target="_blank" rel="noopener noreferrer" class="read-more">
            Read More →
        </a>
    </div>
    '''

def render_section(icon, name, highlights, header_class, color):
    if highlights:
        cards = "".join([render_card(h, color) for h in highlights])
    else:
        cards = '<div class="loading-spinner"><p>⏳ Loading 2026 news...</p></div>'
    
    return f'''
    <div class="col-header {header_class}">
        <span style="font-size: 1.1rem;">{icon}</span>
        <span>{name}</span>
    </div>
    <div class="col-body">
        {cards}
    </div>
    '''

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f'''
<div class="header-container">
    <h1 class="main-title">
        🌐 Global Telecom & OTT Stellar Nexus
        <span class="live-badge">● LIVE 2026</span>
    </h1>
    <p class="subtitle">AI-Powered 2026 Industry Intelligence Dashboard</p>
</div>
''', unsafe_allow_html=True)

with st.spinner("⚡ Fetching 2026 industry news..."):
    all_news = fetch_all_sections()

section_configs = [
    ("telco", "Telco OSS/BSS"),
    ("ott", "OTT & Streaming"),
    ("sports", "Sports & Events"),
    ("technology", "Technology")
]

highlights = {}
for section_key, section_name in section_configs:
    news_items = all_news.get(section_key, [])
    highlights[section_key] = generate_ai_descriptions(news_items, section_name)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        render_section("📡", "TELCO OSS/BSS", highlights.get("telco", []), "col-header-pink", "pink"),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        render_section("📺", "OTT & STREAMING", highlights.get("ott", []), "col-header-purple", "purple"),
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        render_section("🏆", "SPORTS & EVENTS", highlights.get("sports", []), "col-header-green", "green"),
        unsafe_allow_html=True
    )

with col4:
    st.markdown(
        render_section("⚡", "TECHNOLOGY", highlights.get("technology", []), "col-header-orange", "orange"),
        unsafe_allow_html=True
    )

total_items = sum(len(highlights.get(s, [])) for s in ["telco", "ott", "sports", "technology"])
st.markdown(f'''
<div class="footer">
    <p>
        <strong>📊 2026 Insights:</strong> {total_items} | 
        <strong>🕐 Updated:</strong> {datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")} | 
        <strong>🔄 Auto-refresh:</strong> Every 5 minutes
    </p>
    <p style="margin-top: 6px; font-size: 0.7rem; opacity: 0.85;">
        Powered by AI • Industry-Filtered Intelligence
    </p>
</div>
''', unsafe_allow_html=True)

st.markdown("""
<script>
    setTimeout(function() {
        window.location.reload();
    }, 300000);
</script>
""", unsafe_allow_html=True)

if (datetime.now() - st.session_state.keep_alive).seconds > 280:
    st.session_state.keep_alive = datetime.now()
    st.cache_data.clear()
    st.rerun()
