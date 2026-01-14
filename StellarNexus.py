import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# ══════════════════════════════════════════════════════════════════════════════
# ADVANCED AI FILTERING LOGIC (Evergent-Centric)
# ══════════════════════════════════════════════════════════════════════════════

# Flatten lists for fast lookup
EVERGENT_CLIENTS_LIST = [val for sublist in {
    "Astro": ["astro malaysia", "sooka", "njoi"],
    "FOX": ["fox sports", "fox corporation", "fox networks"],
    "AT&T": ["at&t", "att inc", "directv"],
    "NBA": ["nba", "national basketball"],
    "Shahid": ["shahid", "shahid vip", "mbc shahid"],
    "Sony": ["sony pictures", "sonyliv", "sony india"],
    "Sky": ["sky nz", "sky uk", "sky italia", "sky deutschland"],
    "TM": ["telekom malaysia", "tm unifi", "unifi tv"],
    "Britbox": ["britbox"],
    "NBA": ["nba"],
    "FanDuel": ["fanduel"]
}.values() for val in sublist]

COMPETITORS_LIST = ["netcracker", "amdocs", "csg", "oracle communications", "ericsson", "tecnotree", "matrixx", "optiva", "cerillion"]

OSS_BSS_KEYWORDS = [
    "oss", "bss", "billing system", "charging system", "convergent billing", 
    "revenue management", "order management", "5g monetization", "network slicing",
    "telco transformation", "digital bss", "cloud-native oss", "mediation"
]

EXCLUDE_KEYWORDS = ["oil", "gas", "petroleum", "insurance", "banking", "mining", "crypto", "nft"]

def ai_signal_processor(title, summary):
    text = (title + " " + summary).lower()
    
    # 1. Hard Exclusions (Noise Reduction)
    if any(ex in text for ex in EXCLUDE_KEYWORDS):
        return None, False

    # 2. Priority Scoring (The Evergent Signal)
    is_evergent_priority = False
    
    # If it mentions a competitor or Evergent client, it's a High Priority Signal
    if any(comp in text for comp in COMPETITORS_LIST) or any(cli in text for cli in EVERGENT_CLIENTS_LIST):
        is_evergent_priority = True
        
    # 3. Categorization based on specific technical signal
    if any(kw in text for kw in OSS_BSS_KEYWORDS):
        return "telco", is_evergent_priority
    if any(kw in text for kw in ["ott", "streaming", "svod", "avod", "fast channels", "subscriber growth"]):
        return "ott", is_evergent_priority
    if any(kw in text for kw in ["media rights", "broadcasting rights", "live sports", "sports streaming"]):
        return "sports", is_evergent_priority
    if any(kw in text for kw in ["generative ai", "agentic ai", "enterprise ai", "cloud platform"]):
        return "technology", is_evergent_priority
        
    return None, False

# ══════════════════════════════════════════════════════════════════════════════
# STREAMING & UI ENGINE
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="Evergent Intelligence Nexus", page_icon="💎", layout="wide")

# Custom CSS for a "CEO Suite" feel
st.markdown("""
<style>
    .stApp { background: #0f172a; color: #f8fafc; }
    .header-container {
        background: linear-gradient(90deg, #1e293b 0%, #334155 100%);
        padding: 2rem; border-radius: 15px; border-left: 10px solid #38bdf8;
        margin-bottom: 2rem; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.3);
    }
    .main-title { font-size: 2.2rem; font-weight: 800; color: #f8fafc; margin: 0; }
    .news-card {
        background: #1e293b; border: 1px solid #334155;
        border-radius: 12px; padding: 15px; margin-bottom: 12px;
    }
    .news-card-priority {
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid #38bdf8; border-radius: 12px;
        padding: 15px; margin-bottom: 12px;
    }
    .news-title { color: #38bdf8; font-weight: 700; text-decoration: none; font-size: 0.95rem; }
    .news-meta { font-size: 0.75rem; color: #94a3b8; margin-top: 8px; }
    .priority-badge { 
        background: #0369a1; color: white; padding: 2px 8px; 
        border-radius: 4px; font-size: 0.65rem; font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# ... (Include fetch_feed logic from your previous snippet, but update the loop) ...

def fetch_feed(source, url):
    items = []
    try:
        resp = requests.get(url, timeout=5)
        feed = feedparser.parse(resp.content)
        for entry in feed.entries[:10]:
            title = html.unescape(entry.get("title", ""))
            summary = html.unescape(entry.get("summary", ""))
            link = entry.get("link", "")
            
            category, is_priority = ai_signal_processor(title, summary)
            
            if category:
                items.append({
                    "title": title, "link": link, "source": source,
                    "category": category, "priority": is_priority,
                    "pub": datetime.now() # Simplified for brevity
                })
    except: pass
    return items

@st.cache_data(ttl=300)
def load_all_intelligence():
    feeds = [
        ("Telecoms.com", "https://www.telecoms.com/feed"),
        ("Light Reading", "https://www.lightreading.com/rss/simple"),
        ("Variety", "https://variety.com/feed/"),
        ("TechCrunch", "https://techcrunch.com/feed/")
    ]
    all_data = {"telco": [], "ott": [], "sports": [], "technology": []}
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_feed, s, u) for s, u in feeds]
        for f in as_completed(futures):
            for item in f.result():
                all_data[item["category"]].append(item)
    return all_data

# ══════════════════════════════════════════════════════════════════════════════
# MAIN RENDER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="header-container"><h1 class="main-title">💎 Evergent Strategic Nexus</h1><p style="color:#94a3b8">Executive Intelligence Dashboard • AI-Filtered for OSS/BSS Competitive Advantage</p></div>', unsafe_allow_html=True)

data = load_all_intelligence()

# Render 4 Columns
cols = st.columns(4)
titles = {"telco": "📡 OSS/BSS CORE", "ott": "📺 OTT & STREAMING", "sports": "🏆 SPORTS MEDIA", "technology": "⚡ AI & TECH"}

for i, (key, label) in enumerate(titles.items()):
    with cols[i]:
        st.subheader(label)
        for item in data[key][:8]:
            card_style = "news-card-priority" if item["priority"] else "news-card"
            badge = '<span class="priority-badge">STRATEGIC SIGNAL</span>' if item["priority"] else ""
            
            st.markdown(f"""
            <div class="{card_style}">
                <a href="{item['link']}" target="_blank" class="news-title">{item['title']}</a>
                <div class="news-meta">
                    {badge} <span>{item['source']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.info("AI Logic: Filtering for Evergent Clients (Astro, Fox, Sony, etc.) and Competitors (Amdocs, Netcracker, etc.)")
