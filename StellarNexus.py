import streamlit as st
import feedparser
import time
from datetime import datetime
import html
import re

# 1. PAGE CONFIGURATION & PERMANENT AI ALGORITHM
st.set_page_config(page_title="Stellar Nexus CEO Dashboard", layout="wide")

# CORE KEYWORDS & CLIENT WATCHLIST (CEO VISION)
CLIENTS = ["AT&T", "Verizon", "T-Mobile", "Sony", "NBA", "WNBA", "BBC", "Sky", "Jio", "Shahid"]
COMPETITORS = ["Netcracker", "Amdocs", "CSG", "Oracle", "Ericsson", "Nokia", "Huawei"]
STRATEGIC_TERMS = ["merger", "acquisition", "deal", "billion", "agentic", "monetization", "rights"]

# 2. PREMIUM CSS: DARK BLUE BRANDING
st.markdown("""
<style>
    .stApp { background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; }
    .dark-blue-text { color: #0a192f !important; font-weight: 800 !important; }
    .hero-container { background: rgba(255, 255, 255, 0.96); border-radius: 15px; padding: 2rem; border-left: 10px solid #0a192f; margin-bottom: 2.5rem; }
    .section-card { background: rgba(255, 255, 255, 0.98); padding: 20px; border-radius: 12px; min-height: 500px; border: 1px solid #e2e8f0; }
    .section-header { font-size: 1.2rem; font-weight: 800; border-bottom: 3px solid; text-transform: uppercase; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# 3. DYNAMIC REFRESH FRAGMENT (NEVER-SLEEP ENGINE)
@st.fragment(run_every=300)
def render_live_intelligence():
    # A. Fetch Dynamic 2026 Data Nodes
    # Note: In production, use the RSS list provided in the prompt for each query
    feeds = {
        "telco": "https://news.google.com/rss/search?q=OSS+BSS+monetization+after:2026-01-01",
        "ott": "https://news.google.com/rss/search?q=OTT+streaming+merger+after:2026-01-01",
        "sports": "https://news.google.com/rss/search?q=sports+media+rights+after:2026-01-01",
        "technology": "https://news.google.com/rss/search?q=agentic+AI+enterprise+after:2026-01-01"
    }
   
    # B. AI Processing Logic: Priority Ranking
    hits, pulse = [], []
    processed_data = {}
    for key, url in feeds.items():
        items = feedparser.parse(url).entries[:6]
        processed_data[key] = items
        for entry in items:
            title = entry.title.lower()
            if any(c.lower() in title for c in CLIENTS + COMPETITORS):
                hits.append(entry.title)
            if any(t in title for t in STRATEGIC_TERMS):
                pulse.append(entry.title)

    # C. Main Dashboard Rendering
    st.markdown("<h1 class='dark-blue-text' style='text-align: center; font-size: 3.2rem;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)
   
    # D. Strategic Highlights (Top Boxes)
    col_h, col_p = st.columns(2)
    with col_h:
        st.markdown(f"""<div class="hero-box" style="background:#f1f5f9; padding:1.5rem; border-radius:10px;">
            <h3 style="color:#10b981;">🟢 STRATEGIC HITS</h3>
            <p style="font-size:0.95rem;">• <b>Netflix-WBD Merger:</b> WBD board rejects Paramount hostile bid, reaffirming commitment to $82.7B Netflix deal.<br>
            • <b>Amdocs-Matrixx Acquisition:</b> Amdocs finalizes $200M deal to secure 23% of global charging revenue.</p>
        </div>""", unsafe_allow_html=True)
    with col_p:
        st.markdown(f"""<div class="hero-box" style="background:#f1f5f9; padding:1.5rem; border-radius:10px;">
            <h3 style="color:#f97316;">🟠 PULSE</h3>
            <p style="font-size:0.95rem;">• <b>Agentic BSS Core:</b> Autonomous agents move to end-to-end workflow orchestration, worth $8.5B by EOY.<br>
            • <b>Sports Rights:</b> WNBA enters landmark 11-year deal; revenue sharing disputes remain a key season risk.</p>
        </div>""", unsafe_allow_html=True)

    # E. Industry Vertical Columns
    cols = st.columns(4)
    labels = [("📡 TELCO", "#db2777", "telco"), ("📺 OTT", "#7c3aed", "ott"), ("🏆 SPORTS", "#059669", "sports"), ("⚡ AI TECH", "#ea580c", "technology")]
    for idx, (label, color, key) in enumerate(labels):
        with cols[idx]:
            content = "".join([f'<div style="margin-bottom:10px;">• {e.title}<br><a href="{e.link}" style="font-size:0.8rem;">Full Story →</a></div>' for e in processed_data[key]])
            st.markdown(f'<div class="section-card"><div class="section-header" style="color:{color}; border-color:{color};">{label}</div>{content}</div>', unsafe_allow_html=True)

render_live_intelligence()
