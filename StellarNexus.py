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

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Global Telecom & OTT Stellar Nexus", page_icon="🌐", layout="wide", initial_sidebar_state="collapsed")

if 'keep_alive' not in st.session_state:
    st.session_state.keep_alive = datetime.now()

GROQ_API_KEY = "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"

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE SEARCH PHRASES - ONE PER SECTION (EXACTLY AS YOU SPECIFIED)
# ══════════════════════════════════════════════════════════════════════════════
SECTION_SEARCH_QUERIES = {
    "telco": "recent telecom OSS BSS providers news key announcements mergers acquisitions deals profit losses",
    "ott": "recent OTT providers news key announcements mergers acquisitions deals profit losses streaming",
    "sports": "recent sports events announcements providers organizers news key announcements mergers acquisitions",
    "technology": "recent Technology key announcements providers news mergers acquisitions deals profit losses"
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"}

# ══════════════════════════════════════════════════════════════════════════════
# STYLING
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    .stApp {background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; color: #1e293b;}
    .header-container {background: rgba(255,255,255,0.97); padding: 1.2rem 2rem; text-align: center; border-radius: 18px; box-shadow: 0 6px 28px rgba(0,0,0,0.1); margin: 0 0 1.2rem 0; border-bottom: 4px solid #3b82f6;}
    .main-title {font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #1e40af, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;}
    .subtitle {font-size: 0.95rem; color: #64748b; margin-top: 0.3rem;}
    .col-header {padding: 12px 14px; border-radius: 12px 12px 0 0; color: white; font-weight: 700; font-size: 0.9rem; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.12); display: flex; align-items: center; justify-content: center; gap: 6px;}
    .col-header-pink {background: linear-gradient(135deg, #ec4899, #db2777);}
    .col-header-purple {background: linear-gradient(135deg, #a78bfa, #8b5cf6);}
    .col-header-green {background: linear-gradient(135deg, #34d399, #10b981);}
    .col-header-orange {background: linear-gradient(135deg, #fb923c, #f97316);}
    .highlight-count {background: rgba(255,255,255,0.25); padding: 2px 8px; border-radius: 10px; font-size: 0.7rem;}
    .col-body {background: rgba(255,255,255,0.98); border-radius: 0 0 12px 12px; padding: 10px; min-height: 620px; max-height: 720px; overflow-y: auto; box-shadow: 0 6px 20px rgba(0,0,0,0.08);}
    .highlight-card {background: linear-gradient(135deg, #fafbfc, #ffffff); border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; border-radius: 8px; padding: 12px; margin-bottom: 10px; transition: all 0.15s ease;}
    .highlight-card:hover {background: #f8fafc; box-shadow: 0 4px 16px rgba(0,0,0,0.08); transform: translateY(-1px);}
    .highlight-card.pink {border-left-color: #ec4899;}
    .highlight-card.purple {border-left-color: #8b5cf6;}
    .highlight-card.green {border-left-color: #10b981;}
    .highlight-card.orange {border-left-color: #f97316;}
    .highlight-title {color: #1e293b; font-size: 0.88rem; font-weight: 700; margin-bottom: 6px; line-height: 1.3;}
    .highlight-description {color: #475569; font-size: 0.82rem; line-height: 1.5; margin-bottom: 8px;}
    .read-more {color: #2563eb; font-weight: 600; font-size: 0.78rem; text-decoration: none;}
    .read-more:hover {color: #1d4ed8; text-decoration: underline;}
    .footer {text-align: center; color: rgba(255,255,255,0.85); font-size: 0.75rem; margin-top: 15px; padding: 12px; background: rgba(0,0,0,0.25); border-radius: 10px;}
    .col-body::-webkit-scrollbar {width: 5px;}
    .col-body::-webkit-scrollbar-thumb {background: #cbd5e1; border-radius: 10px;}
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════
def clean_text(raw):
    if not raw: return ""
    text = html.unescape(re.sub(r'<[^>]+>', '', str(raw))).strip()
    return re.sub(r'\s*[-–|]\s*[A-Za-z][A-Za-z\s\.]+$', '', text)

def extract_summary(entry, max_len=350):
    for field in ['summary', 'description', 'content']:
        if hasattr(entry, field):
            content = getattr(entry, field)
            if isinstance(content, list) and content: content = content[0].get('value', '')
            summary = clean_text(content)
            if summary and len(summary) > 50:
                return summary[:max_len].rsplit(' ', 1)[0] + '...' if len(summary) > max_len else summary
    return ""

def get_hash(text): return hashlib.md5(text.lower().strip().encode()).hexdigest()[:12]
def title_similarity(a, b): return SequenceMatcher(None, a.lower(), b.lower()).ratio()

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE NEWS FETCHER - USES EXACT SEARCH PHRASE FOR EACH SECTION
# ══════════════════════════════════════════════════════════════════════════════
def fetch_google_news(section, query):
    """Fetch news from Google News RSS using the exact search phrase"""
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200: return []
        
        feed = feedparser.parse(resp.content)
        items, seen_hashes, seen_titles = [], set(), []
        
        for entry in feed.entries[:30]:
            title = clean_text(entry.get("title", ""))
            if len(title) < 25: continue
            link = entry.get("link", "")
            if not link.startswith("http"): continue
            
            title_hash = get_hash(title)
            if title_hash in seen_hashes or any(title_similarity(title, t) > 0.75 for t in seen_titles): continue
            
            summary = extract_summary(entry) or title
            items.append({"title": title, "link": link, "summary": summary, "hash": title_hash})
            seen_hashes.add(title_hash)
            seen_titles.append(title)
            if len(items) >= 18: break
        
        return items
    except: return []

@st.cache_data(ttl=180, show_spinner=False)
def fetch_all_sections():
    """Fetch news for all 4 sections using their search phrases"""
    all_news = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fetch_google_news, sec, qry): sec for sec, qry in SECTION_SEARCH_QUERIES.items()}
        for future in as_completed(futures, timeout=20):
            section = futures[future]
            try: all_news[section] = future.result()
            except: all_news[section] = []
    return all_news

# ══════════════════════════════════════════════════════════════════════════════
# AI ENHANCEMENT - CREATE DESCRIPTIONS
# ══════════════════════════════════════════════════════════════════════════════
def enhance_with_ai(news_items, section_name):
    """AI creates brief descriptions for the fetched news"""
    if not news_items: return []
    
    news_text = "\n".join([f"[{i+1}] {item['title']}\nSummary: {item['summary'][:200]}\nLink: {item['link']}" for i, item in enumerate(news_items[:16])])
    
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.1-8b-instant", "messages": [
                {"role": "system", "content": f"You are a {section_name} analyst. Create 2-3 sentence descriptions for each news. Keep original titles. Use EXACT original links."},
                {"role": "user", "content": f"Create 14 highlights. Return JSON:\n{{\"highlights\": [{{\"title\": \"original title\", \"description\": \"2-3 sentences\", \"link\": \"exact url\"}}]}}\n\n{news_text}"}
            ], "max_tokens": 3500, "temperature": 0.2}, timeout=50)
        
        if resp.status_code == 200:
            match = re.search(r'\{[\s\S]*\}', resp.json()["choices"][0]["message"]["content"])
            if match:
                highlights = json.loads(match.group()).get("highlights", [])[:14]
                valid_links = {item['link'] for item in news_items}
                for i, h in enumerate(highlights):
                    if not h.get("link","").startswith("http") or h.get("link") not in valid_links:
                        h['link'] = news_items[i]['link'] if i < len(news_items) else news_items[0]['link']
                return highlights
    except: pass
    
    return [{"title": item['title'], "description": item['summary'][:250], "link": item['link']} for item in news_items[:14]]

# ══════════════════════════════════════════════════════════════════════════════
# RENDER
# ══════════════════════════════════════════════════════════════════════════════
def render_card(h, color):
    link = h.get("link", "#")
    if not link.startswith("http"): link = "#"
    return f'<div class="highlight-card {color}"><div class="highlight-title">{html.escape(str(h.get("title","")))}</div><div class="highlight-description">{html.escape(str(h.get("description","")))}</div><a href="{html.escape(link)}" target="_blank" class="read-more">Read More →</a></div>'

def render_section(icon, name, highlights, hdr_class, color):
    cards = "".join([render_card(h, color) for h in (highlights or [])])
    return f'<div class="col-header {hdr_class}"><span>{icon}</span><span>{name}</span><span class="highlight-count">{len(highlights or [])}</span></div><div class="col-body">{cards or "<p style=\"text-align:center;color:#999;padding:40px;\">Loading...</p>"}</div>'

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="header-container"><h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1><p class="subtitle">AI-Powered Competitive Intelligence for CEO</p></div>', unsafe_allow_html=True)

with st.spinner("⚡ Fetching latest news..."):
    all_news = fetch_all_sections()

highlights = {sec: enhance_with_ai(all_news.get(sec,[]), name) for sec, name in [("telco","Telco OSS/BSS"),("ott","OTT & Streaming"),("sports","Sports & Events"),("technology","Technology")]}

c1,c2,c3,c4 = st.columns(4)
with c1: st.markdown(render_section("📡","Telco OSS/BSS",highlights.get("telco",[]),"col-header-pink","pink"), unsafe_allow_html=True)
with c2: st.markdown(render_section("📺","OTT & Streaming",highlights.get("ott",[]),"col-header-purple","purple"), unsafe_allow_html=True)
with c3: st.markdown(render_section("🏆","Sports & Events",highlights.get("sports",[]),"col-header-green","green"), unsafe_allow_html=True)
with c4: st.markdown(render_section("⚡","Technology",highlights.get("technology",[]),"col-header-orange","orange"), unsafe_allow_html=True)

st.markdown(f'<div class="footer"><p>Last Updated: {datetime.now().strftime("%I:%M:%S %p")} • Auto-refreshes every 5 minutes</p></div>', unsafe_allow_html=True)
st.markdown("<script>setTimeout(function(){window.location.reload();},300000);</script>", unsafe_allow_html=True)

if (datetime.now() - st.session_state.keep_alive).seconds > 240: st.session_state.keep_alive = datetime.now(); st.rerun()
