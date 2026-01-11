import streamlit as st
import feedparser
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re
from zoneinfo import ZoneInfo
import hashlib
import json
import urllib.parse

# ══════════════════════════════════════════════════════════════════════════════
# SECURE ACCESS & CONFIG
# ══════════════════════════════════════════════════════════════════════════════
GROQ_API_KEY = "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"
CEO_ACCESS_TOKEN = "Vijay"

st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus | 2026",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════════════════════
# STRATEGIC FILTERS (2026 CEO FOCUS)
# ══════════════════════════════════════════════════════════════════════════════
# These queries ensure we only get high-impact "business" news, not consumer fluff.
STRATEGIC_QUERIES = {
    "telco": '(OSS OR BSS OR "digital transformation" OR "5G core") AND (merger OR acquisition OR "major deal" OR contract) after:2025-12-31',
    "ott": '(OTT OR streaming OR "content rights") AND (merger OR acquisition OR "subscriber growth" OR "profitability") after:2025-12-31',
    "sports": '("broadcast rights" OR "streaming rights" OR "media deal") AND (NBA OR NFL OR FIFA OR EPL OR "Bally Sports") after:2025-12-31',
    "technology": '("Generative AI" OR "Cloud Infrastructure" OR "SaaS") AND (telecom OR media) AND (investment OR partnership) after:2025-12-31'
}

EVERGENT_CLIENTS = ["Astro", "NBA", "Shahid", "MBC", "Sky NZ", "Singtel", "Sony", "Aha", "AT&T", "FOX", "Bally Sports"]
COMPETITORS = ["Netcracker", "Amdocs", "CSG", "Oracle", "Ericsson", "Nokia"]

# ══════════════════════════════════════════════════════════════════════════════
# PREMIUM CSS STYLING
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    .stApp { background-color: #0f172a; font-family: 'Inter', sans-serif; }
    
    .header-container {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem; text-align: center; border-radius: 15px; margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .main-title { color: white; font-size: 2.5rem; font-weight: 800; margin: 0; }
    
    .col-header {
        padding: 15px; border-radius: 12px 12px 0 0; color: white;
        font-weight: 800; text-align: center; text-transform: uppercase; letter-spacing: 1px;
    }
    .pink-h { background: #db2777; } .purple-h { background: #7c3aed; }
    .green-h { background: #059669; } .orange-h { background: #ea580c; }

    .col-body {
        background: #f8fafc; border-radius: 0 0 12px 12px; padding: 10px;
        min-height: 700px; max-height: 800px; overflow-y: auto;
    }

    .news-card {
        background: white; border-radius: 8px; padding: 15px; margin-bottom: 12px;
        border-left: 5px solid #cbd5e1; transition: transform 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .news-card:hover { transform: scale(1.02); border-left-color: #3b82f6; }
    
    .client-hit { border-left: 6px solid #10b981 !important; background: #f0fdf4; }
    .comp-hit { border-left: 6px solid #ef4444 !important; background: #fef2f2; }

    .badge {
        font-size: 0.65rem; font-weight: 800; padding: 2px 8px; border-radius: 10px;
        text-transform: uppercase; margin-bottom: 5px; display: inline-block;
    }
    .badge-client { background: #10b981; color: white; }
    .badge-comp { background: #ef4444; color: white; }
    .badge-strat { background: #3b82f6; color: white; }

    .news-title { 
        color: #1e293b; font-weight: 700; font-size: 0.95rem; 
        text-decoration: none; line-height: 1.4; display: block;
    }
    .news-desc { color: #64748b; font-size: 0.8rem; margin-top: 8px; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA CORE
# ══════════════════════════════════════════════════════════════════════════════

def fetch_2026_news(category, query):
    encoded = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=en-US&gl=US&ceid=US:en"
    try:
        feed = feedparser.parse(url)
        results = []
        for entry in feed.entries[:15]:
            title = html.unescape(entry.title)
            desc = html.unescape(re.sub(r'<[^>]+>', '', entry.summary))[:180] + "..."
            
            # Entity Detection
            tag = "Strategic"
            if any(c.lower() in title.lower() for c in EVERGENT_CLIENTS): tag = "Client"
            if any(cp.lower() in title.lower() for cp in COMPETITORS): tag = "Competitor"
            
            results.append({
                "title": title,
                "link": entry.link,
                "desc": desc,
                "tag": tag,
                "date": entry.published
            })
        return results
    except:
        return []

# ══════════════════════════════════════════════════════════════════════════════
# RENDER ENGINE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown('<div class="header-container"><h1 class="main-title">2026 Global Intelligence Nexus</h1><p style="color: #bfdbfe; margin-top: 10px;">Executive Competitive Dashboard for CEO</p></div>', unsafe_allow_html=True)



cols = st.columns(4)
sections = [
    ("telco", "📡 Telco OSS/BSS", "pink-h"),
    ("ott", "📺 OTT & Streaming", "purple-h"),
    ("sports", "🏆 Sports Rights", "green-h"),
    ("technology", "⚡ AI & Tech Ops", "orange-h")
]

with st.spinner("Analyzing 2026 Strategic Signals..."):
    for i, (key, label, color_class) in enumerate(sections):
        with cols[i]:
            st.markdown(f'<div class="col-header {color_class}">{label}</div>', unsafe_allow_html=True)
            news_items = fetch_2026_news(key, STRATEGIC_QUERIES[key])
            
            # Sort: Clients first, then Competitors, then others
            news_items.sort(key=lambda x: (x['tag'] != 'Client', x['tag'] != 'Competitor'))
            
            body_html = '<div class="col-body">'
            if not news_items:
                body_html += '<p style="text-align:center; padding:20px; color:#94a3b8;">Scanning for 2026 deals...</p>'
            
            for item in news_items:
                card_class = "news-card"
                badge_class = "badge-strat"
                if item['tag'] == "Client":
                    card_class += " client-hit"
                    badge_class = "badge-client"
                elif item['tag'] == "Competitor":
                    card_class += " comp-hit"
                    badge_class = "badge-comp"
                
                body_html += f'''
                <div class="{card_class}">
                    <span class="badge {badge_class}">{item['tag']}</span>
                    <a href="{item['link']}" target="_blank" class="news-title">{item['title']}</a>
                    <div class="news-desc">{item['desc']}</div>
                    <div style="font-size:0.65rem; color:#94a3b8; margin-top:10px;">{item['date']}</div>
                </div>
                '''
            body_html += '</div>'
            st.markdown(body_html, unsafe_allow_html=True)

# Auto-refresh and Footer
st.markdown(f"""
<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 30px; padding: 20px;">
    System Status: Live | Last Update: {datetime.now().strftime("%H:%M:%S")} | Strategy Engine: Active
</div>
<script>setTimeout(function(){{ window.location.reload(); }}, 300000);</script>
""", unsafe_allow_html=True)
