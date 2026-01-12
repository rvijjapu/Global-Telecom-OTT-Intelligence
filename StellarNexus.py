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
import time

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Evergent Intelligence Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'keep_alive' not in st.session_state:
    st.session_state.keep_alive = datetime.now()

GROQ_API_KEY = "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"

# ══════════════════════════════════════════════════════════════════════════════
# EVERGENT INTELLIGENCE DATABASE
# ══════════════════════════════════════════════════════════════════════════════
EVERGENT_CLIENTS = {
    "Astro": ["astro malaysia", "astro sooka", "astro njoi", "sooka", "njoi"],
    "FOX": ["fox sports", "fox corporation", "fox networks"],
    "AT&T": ["at&t", "att", "directv"],
    "NBA": ["nba", "national basketball association"],
    "Shahid": ["shahid", "shahid vip", "mbc shahid"],
    "MBC": ["mbc group", "mbc", "middle east broadcasting"],
    "Sony": ["sony pictures", "sony entertainment", "sonyliv"],
    "BBC": ["bbc", "british broadcasting", "bbc iplayer"],
    "Sky": ["sky nz", "sky uk", "sky italia", "sky deutschland"],
    "FanDuel": ["fanduel", "fanduel group"],
    "Bally Sports": ["bally sports", "diamond sports"],
    "Telekom Malaysia": ["telekom malaysia", "tm unifi", "unifi tv"]
}

COMPETITORS = {
    "Netcracker": ["netcracker", "nec netcracker"],
    "Amdocs": ["amdocs", "amdocs ltd"],
    "CSG": ["csg systems", "csg international"],
    "Oracle": ["oracle communications", "oracle telecom"],
    "Ericsson": ["ericsson"],
    "Nokia": ["nokia"],
    "Matrixx": ["matrixx", "matrixx software"],
    "Optiva": ["optiva"],
    "Cerillion": ["cerillion"]
}

TOP_TELCOS = {
    "Verizon": ["verizon", "verizon wireless"],
    "T-Mobile": ["t-mobile", "tmobile"],
    "Vodafone": ["vodafone"],
    "BT": ["bt group", "british telecom"],
    "Singtel": ["singtel", "singapore telecom"],
    "Jio": ["reliance jio", "jio platforms"],
    "Airtel": ["bharti airtel", "airtel"]
}

# Flatten for efficient searching
ALL_CLIENTS = [term.lower() for terms in EVERGENT_CLIENTS.values() for term in terms]
ALL_COMPETITORS = [term.lower() for terms in COMPETITORS.values() for term in terms]
ALL_TELCOS = [term.lower() for terms in TOP_TELCOS.values() for term in terms]
STRATEGIC_KEYWORDS = ["merger", "acquisition", "deal", "partnership", "contract", "billion", "million", "revenue", "subscriber", "oss", "bss", "billing", "monetization", "5g"]

# ══════════════════════════════════════════════════════════════════════════════
# KEEP-ALIVE
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
    }
    
    .header-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.98) 100%);
        padding: 1.5rem 2rem;
        text-align: center;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        margin: 0 0 1.5rem 0;
        border-bottom: 4px solid #0a192f;
    }
    
    .main-title {
        font-size: 2rem;
        font-weight: 800;
        color: #0a192f;
        margin: 0;
    }
    
    .subtitle {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.4rem;
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
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .ceo-summary {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 6px solid #f59e0b;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(245,158,11,0.2);
    }
    
    .ceo-summary-title {
        color: #92400e;
        font-size: 1.3rem;
        font-weight: 800;
        margin-bottom: 1rem;
    }
    
    .ceo-summary-content {
        color: #451a03;
        font-size: 0.9rem;
        line-height: 1.7;
    }
    
    .hero-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .hero-title {
        color: #0a192f;
        font-size: 1.3rem;
        font-weight: 800;
        margin-bottom: 1rem;
        border-left: 6px solid #3b82f6;
        padding-left: 12px;
    }
    
    .hero-box {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 10px;
        padding: 1.2rem;
        height: 100%;
        border: 1px solid #e2e8f0;
    }
    
    .hero-box-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.8rem;
    }
    
    .hero-content {
        color: #334155;
        font-size: 0.8rem;
        line-height: 1.6;
    }
    
    .priority-badge {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 4px;
    }
    
    .col-header {
        padding: 12px 14px;
        border-radius: 12px 12px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.85rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #7c3aed);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #059669);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #ea580c);}
    
    .col-body {
        background: rgba(255,255,255,0.98);
        border-radius: 0 0 12px 12px;
        padding: 10px;
        height: 480px;
        overflow-y: auto;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }
    
    .highlight-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #3b82f6;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }
    
    .highlight-card:hover {
        background: #f8fafc;
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    .highlight-card.client {
        border-left: 4px solid #10b981;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    }
    
    .highlight-card.competitor {
        border-left: 4px solid #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    }
    
    .highlight-title {
        color: #0f172a;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 6px;
        line-height: 1.3;
    }
    
    .highlight-description {
        color: #475569;
        font-size: 0.75rem;
        line-height: 1.5;
        margin-bottom: 8px;
    }
    
    .read-more {
        color: #2563eb;
        font-weight: 600;
        font-size: 0.7rem;
        text-decoration: none;
    }
    
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.95);
        font-size: 0.75rem;
        margin-top: 15px;
        padding: 12px 20px;
        background: linear-gradient(135deg, rgba(10,25,47,0.95), rgba(30,41,59,0.95));
        border-radius: 10px;
    }
    
    .col-body::-webkit-scrollbar {width: 5px;}
    .col-body::-webkit-scrollbar-track {background: #f1f5f9;}
    .col-body::-webkit-scrollbar-thumb {background: #64748b; border-radius: 10px;}
    
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    [data-testid="column"] {padding: 0 8px !important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def clean_text(raw):
    if not raw:
        return ""
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', str(raw)))).strip()

def get_hash(text):
    return hashlib.md5(text.lower().encode()).hexdigest()[:10]

def is_2026_only(text):
    text_lower = text.lower()
    if any(year in text_lower for year in ["2024", "2025", "2023", "2022"]):
        return False
    if "2026" in text_lower:
        return True
    return any(ind in text_lower for ind in ["hours ago", "today", "yesterday"])

def calculate_relevance_score(title, summary):
    """AI-powered relevance scoring for Evergent"""
    text = (title + " " + summary).lower()
    score = 0
    
    # High priority: Evergent clients
    for client in ALL_CLIENTS:
        if client in text:
            score += 15
            break
    
    # Medium priority: Competitors
    for competitor in ALL_COMPETITORS:
        if competitor in text:
            score += 10
            break
    
    # Important telcos
    for telco in ALL_TELCOS:
        if telco in text:
            score += 8
            break
    
    # Strategic keywords
    for keyword in STRATEGIC_KEYWORDS:
        if keyword in text:
            score += 3
    
    return score

def extract_entities(title, summary):
    """Extract Evergent-relevant entities"""
    text = (title + " " + summary).lower()
    found = {"clients": [], "competitors": [], "telcos": []}
    
    for name, terms in EVERGENT_CLIENTS.items():
        if any(term in text for term in terms):
            found["clients"].append(name)
    
    for name, terms in COMPETITORS.items():
        if any(term in text for term in terms):
            found["competitors"].append(name)
    
    for name, terms in TOP_TELCOS.items():
        if any(term in text for term in terms):
            found["telcos"].append(name)
    
    return found

# ══════════════════════════════════════════════════════════════════════════════
# NEWS FETCHER WITH AI SCORING
# ══════════════════════════════════════════════════════════════════════════════
def fetch_intelligent_news(query, max_results=25):
    """Fetch and score news using AI algorithm"""
    try:
        query_2026 = f"{query} 2026"
        encoded = urllib.parse.quote(query_2026)
        url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
        
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if resp.status_code != 200:
            return []
        
        feed = feedparser.parse(resp.content)
        results = []
        
        for entry in feed.entries[:max_results]:
            title = clean_text(entry.get("title", ""))
            link = entry.get("link", "")
            summary = clean_text(entry.get("summary", "")) or title
            
            if not is_2026_only(title + summary) or len(title) < 25:
                continue
            
            # AI Scoring
            score = calculate_relevance_score(title, summary)
            entities = extract_entities(title, summary)
            
            # Determine news type
            news_type = "standard"
            if entities["clients"]:
                news_type = "client"
            elif entities["competitors"]:
                news_type = "competitor"
            
            results.append({
                "title": title,
                "link": link,
                "summary": summary,
                "score": score,
                "type": news_type,
                "entities": entities,
                "hash": get_hash(title)
            })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
        
    except:
        return []

@st.cache_data(ttl=180, show_spinner=False)
def fetch_all_intelligence():
    """Fetch news across all sectors with AI prioritization"""
    queries = {
        "telco": [
            "telecom OSS BSS deal partnership 2026",
            "5G network operator contract 2026",
            f"{' OR '.join(list(EVERGENT_CLIENTS.keys())[:5])} telecom deal 2026"
        ],
        "ott": [
            "streaming platform merger acquisition 2026",
            "OTT video service deal 2026",
            f"{' OR '.join(list(EVERGENT_CLIENTS.keys())[:5])} streaming 2026"
        ],
        "sports": [
            "sports media rights broadcasting 2026",
            "sports betting platform deal 2026",
            "NBA NFL broadcasting partnership 2026"
        ],
        "technology": [
            "cloud computing AI platform deal 2026",
            "enterprise SaaS acquisition 2026",
            "fintech platform merger 2026"
        ]
    }
    
    all_news = {}
    for section, query_list in queries.items():
        section_news = []
        seen_hashes = set()
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(fetch_intelligent_news, q): q for q in query_list}
            
            for future in as_completed(futures, timeout=25):
                try:
                    items = future.result()
                    for item in items:
                        if item["hash"] not in seen_hashes and item["score"] > 5:
                            section_news.append(item)
                            seen_hashes.add(item["hash"])
                except:
                    continue
        
        # Sort by score and take top 12
        section_news.sort(key=lambda x: x["score"], reverse=True)
        all_news[section] = section_news[:12]
    
    return all_news

# ══════════════════════════════════════════════════════════════════════════════
# CEO INSIGHTS GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
def generate_ceo_insights(all_news):
    """Generate executive summary using AI"""
    # Extract high-priority news
    priority_news = []
    for section_news in all_news.values():
        priority_news.extend([n for n in section_news if n["score"] >= 15][:3])
    
    if not priority_news:
        return "No high-priority Evergent-related news in the last 24 hours. Monitoring continues."
    
    # Prepare context for AI
    news_context = "\n".join([
        f"• {item['title'][:100]} (Relevance: {item['score']}, Entities: {item['entities']})"
        for item in priority_news[:8]
    ])
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an executive intelligence analyst for Evergent. Create a 3-4 sentence CEO summary highlighting key industry moves, client news, and competitive threats. Focus on business impact and strategic implications."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze these top industry developments and create a CEO executive summary:\n\n{news_context}"
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.3
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
    except:
        pass
    
    return f"🎯 {len(priority_news)} high-priority developments detected involving Evergent clients and competitors. Key focus areas: {', '.join(set([e for n in priority_news for e in n['entities']['clients'][:2]]))}."

# ══════════════════════════════════════════════════════════════════════════════
# RENDER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def render_news_card(item):
    """Render individual news card with priority indicators"""
    title = html.escape(item["title"])
    summary = html.escape(item["summary"][:150])
    link = html.escape(item["link"])
    
    card_class = f"highlight-card {item['type']}"
    
    badge_html = ""
    if item["type"] == "client":
        badge_html = '<span class="priority-badge">🟢 CLIENT</span>'
    elif item["type"] == "competitor":
        badge_html = '<span class="priority-badge" style="background: linear-gradient(135deg, #f59e0b, #d97706);">🟡 COMPETITOR</span>'
    
    return f'''
    <div class="{card_class}">
        {badge_html}
        <div class="highlight-title">{title}</div>
        <div class="highlight-description">{summary}...</div>
        <a href="{link}" target="_blank" class="read-more">Full Story →</a>
    </div>
    '''

def render_section(icon, name, news_items, header_class):
    header = f'<div class="col-header {header_class}"><span style="font-size: 1.1rem;">{icon}</span> <span>{name}</span></div>'
    
    if news_items:
        cards = "".join([render_news_card(item) for item in news_items])
    else:
        cards = '<div style="text-align:center;color:#94a3b8;padding:40px;">No priority news</div>'
    
    body = f'<div class="col-body">{cards}</div>'
    return header + body

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

# Loading
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div style="display:flex;flex-direction:column;justify-content:center;align-items:center;height:70vh;text-align:center;">
            <h1 style="color:#0a192f;font-size:2.5rem;font-weight:800;">⚡ Activating Intelligence Layer...</h1>
            <p style="color:#64748b;font-size:1.1rem;">Scanning global news for Evergent priorities</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.3)

placeholder.empty()

# Header
st.markdown(f'''
<div class="header-container">
    <h1 class="main-title">
        🌐 Evergent Intelligence Dashboard
        <span class="live-badge">● LIVE 2026</span>
    </h1>
    <p class="subtitle">AI-Powered Client & Competitor Intelligence for Executive Leadership</p>
</div>
''', unsafe_allow_html=True)

# Fetch Intelligence
with st.spinner(""):
    all_news = fetch_all_intelligence()
    ceo_summary = generate_ceo_insights(all_news)

# CEO Executive Summary
st.markdown(f'''
<div class="ceo-summary">
    <div class="ceo-summary-title">🎯 CEO EXECUTIVE SUMMARY</div>
    <div class="ceo-summary-content">{ceo_summary}</div>
</div>
''', unsafe_allow_html=True)

# Strategic Highlights
client_news = [n for section in all_news.values() for n in section if n["type"] == "client"][:4]
competitor_news = [n for section in all_news.values() for n in section if n["type"] == "competitor"][:4]

col_h1, col_h2 = st.columns(2)

with col_h1:
    client_html = "<br>".join([f"• <b>{n['entities']['clients'][0]}</b>: {n['title'][:80]}..." for n in client_news]) if client_news else "• Monitoring client ecosystem..."
    st.markdown(f'''
    <div class="hero-container">
        <div class="hero-title">🟢 CLIENT INTELLIGENCE</div>
        <div class="hero-box">
            <div class="hero-box-title" style="color: #10b981;">Evergent Client Activity</div>
            <div class="hero-content">{client_html}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with col_h2:
    comp_html = "<br>".join([f"• <b>{n['entities']['competitors'][0]}</b>: {n['title'][:80]}..." for n in competitor_news]) if competitor_news else "• Monitoring competitive landscape..."
    st.markdown(f'''
    <div class="hero-container">
        <div class="hero-title">🟡 COMPETITIVE INTELLIGENCE</div>
        <div class="hero-box">
            <div class="hero-box-title" style="color: #f59e0b;">Competitor Moves</div>
            <div class="hero-content">{comp_html}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

# Industry Sections
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(render_section("📡", "TELCO OSS/BSS", all_news.get("telco", []), "col-header-pink"), unsafe_allow_html=True)

with col2:
    st.markdown(render_section("📺", "OTT & STREAMING", all_news.get("ott", []), "col-header-purple"), unsafe_allow_html=True)

with col3:
    st.markdown(render_section("🏆", "SPORTS & EVENTS", all_news.get("sports", []), "col-header-green"), unsafe_allow_html=True)

with col4:
    st.markdown(render_section("⚡", "TECHNOLOGY", all_news.get("technology", []), "col-header-orange"), unsafe_allow_html=True)

# Footer
total = sum(len(all_news.get(s, [])) for s in ["telco", "ott", "sports", "technology"])
priority = len([n for section in all_news.values() for n in section if n["score"] >= 15])

st.markdown(f'''
<div class="footer">
    <p><strong>📊 Intelligence:</strong> {total} articles analyzed | <strong>🎯 High Priority:</strong> {priority} | <strong>🕐 Live:</strong> {datetime.now().strftime("%H:%M:%S")} | <strong>🔄 Auto-refresh:</strong> 5 min</p>
    <p style="margin-top: 6px; font-size: 0.7rem; opacity: 0.85;">Powered by Evergent AI Intelligence Engine</p>
</div>
''', unsafe_allow_html=True)

st.markdown('<script>setTimeout(function() {window.location.reload();}, 300000);</script>', unsafe_allow_html=True)

if (datetime.now() - st.session_state.keep_alive).seconds > 280:
    st.session_state.keep_alive = datetime.now()
    st.cache_data.clear()
    st.rerun()

keep_alive()
