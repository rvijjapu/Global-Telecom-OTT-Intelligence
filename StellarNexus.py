import streamlit as st
import feedparser
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import hashlib
from difflib import SequenceMatcher
import json
import urllib.parse
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
   
if 'keep_alive' not in st.session_state:
    st.session_state.keep_alive = datetime.now()
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

GROQ_API_KEY = "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"

# ══════════════════════════════════════════════════════════════════════════════
# OPTIMIZED SEARCH QUERIES - EXACT AS SPECIFIED + ENHANCED FOR 2024-2025 NEWS
# ══════════════════════════════════════════════════════════════════════════════
SECTION_QUERIES = {
    "telco": "recent telecom OSS BSS key announcements providers organizers news mergers acquisitions deals profit losses 2026",
    "ott": "recent OTT providers key announcements providers organizers news mergers acquisitions deals profit losses 2026",
    "sports": "recent Sports Events organizers key announcements provider organizers news mergers acquisitions deals profit losses 2026",
    "technology": "recent Technology key announcements provider organizers news mergers acquisitions deals profit losses 2026"
}

# Enhanced multi-query strategy for comprehensive coverage
SECTION_MULTI_QUERIES = {
    "telco": [
        "telecom OSS BSS merger acquisition 2026",
        "5G network operator partnership deal announcement",
        "telecom billing revenue management news",
        "BSS digital transformation monetization",
        "telecom operator earnings profit loss 2026",
        "Ericsson Nokia Huawei telecom deal",
        "telecom infrastructure investment announcement",
        "wireless carrier merger acquisition news"
    ],
    "ott": [
        "OTT streaming merger acquisition 2026",
        "Netflix Disney HBO Max streaming news",
        "streaming platform subscriber revenue",
        "OTT content deal partnership announcement",
        "video streaming profit loss market",
        "Amazon Prime Apple TV streaming deal",
        "streaming wars media acquisition",
        "SVOD AVOD platform announcement"
    ],
    "sports": [
        "sports media rights deal 2026",
        "sports broadcasting streaming partnership",
        "NFL NBA MLB broadcasting deal",
        "sports league broadcast rights announcement",
        "esports gaming media deal",
        "Olympic FIFA World Cup broadcasting",
        "sports betting merger acquisition",
        "sports streaming rights contract"
    ],
    "technology": [
        "technology merger acquisition 2026",
        "AI artificial intelligence deal partnership",
        "tech company earnings profit loss",
        "cloud computing AWS Azure Google deal",
        "semiconductor chip deal partnership",
        "Apple Google Microsoft announcement",
        "enterprise software acquisition",
        "tech IPO funding announcement 2026"
    ]
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM STYLING - CEO READY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .header-container {
        background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(248,250,252,0.98) 100%);
        padding: 1.5rem 2.5rem;
        text-align: center;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12), 0 0 0 1px rgba(255,255,255,0.1);
        margin: 0 0 1.5rem 0;
        border-bottom: 4px solid transparent;
        background-clip: padding-box;
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
        border-radius: 0 0 20px 20px;
    }
    
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 12px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .col-header {
        padding: 14px 16px;
        border-radius: 16px 16px 0 0;
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #7c3aed);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #059669);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #ea580c);}
    
    .highlight-count {
        background: rgba(255,255,255,0.25);
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    
    .col-body {
        background: rgba(255,255,255,0.98);
        border-radius: 0 0 16px 16px;
        padding: 12px;
        min-height: 650px;
        max-height: 750px;
        overflow-y: auto;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }
    
    .highlight-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        border-left: 4px solid #3b82f6;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
        position: relative;
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
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 8px;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .highlight-description {
        color: #475569;
        font-size: 0.84rem;
        line-height: 1.6;
        margin-bottom: 10px;
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .read-more {
        color: #2563eb;
        font-weight: 600;
        font-size: 0.8rem;
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
        color: rgba(255,255,255,0.9);
        font-size: 0.8rem;
        margin-top: 20px;
        padding: 16px 24px;
        background: linear-gradient(135deg, rgba(15,23,42,0.9), rgba(30,41,59,0.9));
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .col-body::-webkit-scrollbar {width: 6px;}
    .col-body::-webkit-scrollbar-track {background: #f1f5f9; border-radius: 10px;}
    .col-body::-webkit-scrollbar-thumb {background: linear-gradient(180deg, #94a3b8, #64748b); border-radius: 10px;}
    .col-body::-webkit-scrollbar-thumb:hover {background: linear-gradient(180deg, #64748b, #475569);}
    
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .loading-spinner {
        text-align: center;
        padding: 60px 20px;
        color: #64748b;
    }
    
    .news-tag {
        display: inline-block;
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        color: #1e40af;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def clean_text(raw):
    """Clean HTML and normalize text"""
    if not raw:
        return ""
    text = html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()
    # Remove source attribution at end
    text = re.sub(r'\s*[-–|]\s*[A-Za-z][A-Za-z0-9\s\.,&\']+$', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_summary(entry, max_len=500):
    """Extract the best available summary from feed entry"""
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and content:
                content = content[0].get('value', '')
            summary = clean_text(content)
            if summary and len(summary) > 50:
                if len(summary) > max_len:
                    return summary[:max_len].rsplit(' ', 1)[0] + '...'
                return summary
    return ""

def get_hash(text):
    """Generate hash for deduplication"""
    return hashlib.md5(text.lower().strip().encode()).hexdigest()[:12]

def title_similarity(a, b):
    """Calculate similarity ratio between two titles"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE NEWS RSS FETCHER - OPTIMIZED
# ══════════════════════════════════════════════════════════════════════════════
def fetch_google_news_rss(query, max_results=25):
    """Fetch news from Google News RSS feed"""
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return []
        
        feed = feedparser.parse(resp.content)
        results = []
        
        for entry in feed.entries[:max_results]:
            title = clean_text(entry.get("title", ""))
            link = entry.get("link", "")
            
            # Validate entry
            if len(title) < 30 or not link.startswith("http"):
                continue
            
            summary = extract_summary(entry) or title
            pub_date = entry.get("published", "")
            
            results.append({
                "title": title,
                "link": link,
                "summary": summary,
                "published": pub_date,
                "hash": get_hash(title)
            })
        
        return results
    except Exception as e:
        return []

@st.cache_data(ttl=180, show_spinner=False)
def fetch_section_news(section):
    """Fetch and deduplicate news for a section using multiple queries"""
    all_items = []
    seen_hashes = set()
    seen_titles = []
    
    # Get all queries for this section
    queries = [SECTION_QUERIES.get(section, "")]
    queries.extend(SECTION_MULTI_QUERIES.get(section, []))
    
    # Fetch in parallel
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_google_news_rss, q): q for q in queries}
        
        for future in as_completed(futures, timeout=30):
            try:
                items = future.result()
                for item in items:
                    # Skip duplicates
                    if item["hash"] in seen_hashes:
                        continue
                    
                    # Skip similar titles
                    is_similar = any(title_similarity(item["title"], t) > 0.65 for t in seen_titles)
                    if is_similar:
                        continue
                    
                    all_items.append(item)
                    seen_hashes.add(item["hash"])
                    seen_titles.append(item["title"])
            except:
                continue
    
    return all_items[:25]

@st.cache_data(ttl=180, show_spinner=False)
def fetch_all_sections():
    """Fetch news for all sections in parallel"""
    all_news = {}
    sections = ["telco", "ott", "sports", "technology"]
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_section_news, sec): sec for sec in sections}
        
        for future in as_completed(futures, timeout=45):
            section = futures[future]
            try:
                all_news[section] = future.result()
            except:
                all_news[section] = []
    
    return all_news

# ══════════════════════════════════════════════════════════════════════════════
# AI DESCRIPTION GENERATOR - GROQ OPTIMIZED
# ══════════════════════════════════════════════════════════════════════════════
def generate_ai_descriptions(news_items, section_name):
    """Generate AI-powered executive summaries using Groq"""
    if not news_items:
        return []
    
    # Prepare news context
    news_text = "\n\n".join([
        f"[{i+1}] TITLE: {item['title']}\nSUMMARY: {item['summary'][:300]}\nLINK: {item['link']}"
        for i, item in enumerate(news_items[:20])
    ])
    
    section_context = {
        "Telco OSS/BSS": "telecom industry focusing on OSS/BSS systems, network operators, 5G, billing, revenue management",
        "OTT & Streaming": "OTT streaming platforms, content providers, media companies, subscriber metrics",
        "Sports & Events": "sports broadcasting, media rights, leagues, events, esports",
        "Technology": "technology companies, AI, cloud computing, semiconductors, enterprise software"
    }
    
    context = section_context.get(section_name, section_name)
    
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
                        "content": f"""You are a senior {section_name} industry analyst creating executive briefings for a CEO.
Focus on: {context}

CRITICAL RULES:
1. Create EXACTLY 14 highlights from the provided news
2. Each highlight needs: compelling title (max 15 words), executive summary (2-3 sentences, 50-80 words)
3. Focus on: mergers, acquisitions, deals, partnerships, earnings, market moves, strategic announcements
4. Use EXACT original links from the news provided - do not modify URLs
5. Make descriptions CEO-ready: business impact, strategic significance, numbers/metrics when available
6. Return valid JSON only"""
                    },
                    {
                        "role": "user",
                        "content": f"""Create 14 executive highlights from this {section_name} news.

Return ONLY this JSON format:
{{"highlights": [
  {{"title": "Compelling headline", "description": "2-3 sentence executive summary with business impact", "link": "exact url from news"}}
]}}

NEWS TO ANALYZE:
{news_text}"""
                    }
                ],
                "max_tokens": 4500,
                "temperature": 0.15,
                "top_p": 0.9
            },
            timeout=60
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                data = json.loads(json_match.group())
                highlights = data.get("highlights", [])[:14]
                
                # Validate and fix links
                valid_links = {item['link'] for item in news_items}
                for i, h in enumerate(highlights):
                    link = h.get("link", "")
                    if not link.startswith("http") or link not in valid_links:
                        # Use corresponding news item link
                        if i < len(news_items):
                            h['link'] = news_items[i]['link']
                        elif news_items:
                            h['link'] = news_items[0]['link']
                
                return highlights
    except Exception as e:
        pass
    
    # Fallback: return raw news items formatted
    return [
        {
            "title": item['title'][:100],
            "description": item['summary'][:300],
            "link": item['link']
        }
        for item in news_items[:14]
    ]

# ══════════════════════════════════════════════════════════════════════════════
# RENDER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def render_card(highlight, color):
    """Render a single news card"""
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
            Read Full Story →
        </a>
    </div>
    '''

def render_section(icon, name, highlights, header_class, color):
    """Render a complete section column"""
    count = len(highlights) if highlights else 0
    
    if highlights:
        cards = "".join([render_card(h, color) for h in highlights])
    else:
        cards = '''
        <div class="loading-spinner">
            <p>⏳ Fetching latest news...</p>
        </div>
        '''
    
    return f'''
    <div class="col-header {header_class}">
        <span style="font-size: 1.2rem;">{icon}</span>
        <span>{name}</span>
        <span class="highlight-count">{count}</span>
    </div>
    <div class="col-body">
        {cards}
    </div>
    '''

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

# Header
st.markdown(f'''
<div class="header-container">
    <h1 class="main-title">
        🌐 Global Telecom & OTT Stellar Nexus
        <span class="live-badge">● LIVE</span>
    </h1>
    <p class="subtitle">AI-Powered Competitive Intelligence Dashboard for Executive Leadership</p>
</div>
''', unsafe_allow_html=True)

# Fetch all news
with st.spinner("⚡ Fetching latest global news from Google..."):
    all_news = fetch_all_sections()

# Generate AI descriptions for each section
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

# Render columns
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

# Footer
total_items = sum(len(highlights.get(s, [])) for s in ["telco", "ott", "sports", "technology"])
st.markdown(f'''
<div class="footer">
    <p>
        <strong>📊 Total Insights:</strong> {total_items} | 
        <strong>🕐 Last Updated:</strong> {datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")} | 
        <strong>🔄 Auto-refresh:</strong> Every 5 minutes
    </p>
    <p style="margin-top: 8px; font-size: 0.75rem; opacity: 0.8;">
        Powered by Google News RSS + Groq AI • Executive Intelligence Platform
    </p>
</div>
''', unsafe_allow_html=True)

# Auto-refresh script (5 minutes = 300000ms)
st.markdown("""
<script>
    setTimeout(function() {
        window.location.reload();
    }, 300000);
</script>
""", unsafe_allow_html=True)

# Session-based auto-refresh fallback
if (datetime.now() - st.session_state.keep_alive).seconds > 280:
    st.session_state.keep_alive = datetime.now()
    st.cache_data.clear()
    st.rerun()
