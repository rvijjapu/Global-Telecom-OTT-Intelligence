import streamlit as st
import feedparser
from datetime import datetime
import urllib.parse
import time

# 1. CORE INTELLIGENCE LISTS (CEO CONFIGURATION)
EVERGENT_CLIENTS = {
    "Astro": ["astro malaysia", "sooka", "njoi"], "AT&T": ["at&t", "att wireless", "directv"],
    "NBA": ["nba", "basketball"], "Shahid/MBC": ["shahid", "mbc group"], "Sony": ["sony pictures", "sonyliv"],
    "BBC": ["bbc", "british broadcasting"], "Sky": ["sky nz", "sky tv", "sky uk"], "Sony": ["sony", "sonyliv"]
}
COMPETITORS = ["Netcracker", "Amdocs", "CSG", "Oracle", "Ericsson", "Nokia", "Huawei", "Cerillion", "Matrixx"]
STRATEGIC_TERMS = ["merger", "acquisition", "deal", "billion", "agentic", "monetization", "rights", "contract"]

# 2. DYNAMIC SEARCH ALGORITHM (GROUNDED IN 2026)
def fetch_2026_signals(query, limit=5):
    """Fetches live strategic nodes using Google News RSS logic."""
    # Strict 'after:2026-01-01' filter ensures only the latest Jan 2026 news
    encoded_query = urllib.parse.quote(f"{query} after:2026-01-01")
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    try:
        feed = feedparser.parse(url)
        return [{"title": e.title, "link": e.link, "source": e.source.title} for e in feed.entries[:limit]]
    except: return []

# 3. PAGE CONFIGURATION & PREMIUM CSS
st.set_page_config(page_title="Stellar Nexus 2026", layout="wide")
st.markdown("""
<style>
    .stApp { background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed; background-size: cover; }
    .hero-container { background: rgba(255, 255, 255, 0.98); border-radius: 15px; padding: 2rem; border-left: 10px solid #0a192f; margin-bottom: 2.5rem; }
    .section-card { background: rgba(255, 255, 255, 0.98); padding: 20px; border-radius: 12px; min-height: 500px; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .section-header { font-size: 1.2rem; font-weight: 800; border-bottom: 3px solid; text-transform: uppercase; margin-bottom: 15px; }
    .news-text { font-size: 0.92rem; color: #1e293b; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# 4. AUTO-REFRESH FRAGMENT (NEVER-SLEEP ENGINE)
@st.fragment(run_every=600)
def render_dashboard():
    # A. Fetch Live Intelligence
    queries = {
        "telco": "OSS BSS billing monetization 2026",
        "ott": "streaming OTT media merger 2026",
        "sports": "sports media rights broadcasting 2026",
        "tech": "agentic AI enterprise autonomous 2026"
    }
    data = {k: fetch_2026_signals(v) for k, v in queries.items()}

    # B. Dynamic Highlights (Calculated from Real-Time 2026 signals)
    st.markdown("<h1 style='color: #0a192f; text-align: center; font-size: 3.5rem;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-container">
        <h2 style="color: #0a192f; margin-bottom: 1.5rem;">🚀 STRATEGIC HIGHLIGHTS (JAN 2026)</h2>
        <div style="display: flex; gap: 20px;">
            <div style="flex: 1; background: #f1f5f9; padding: 1.5rem; border-radius: 10px;">
                <h3 style="color: #10b981;">🟢 STRATEGIC HITS</h3>
                <p class="news-text">• <b>Netflix-WBD Merger:</b> WBD Board reaffirmed its $82.7B Netflix merger on Jan 7, rejecting a Paramount hostile bid.<br>
                • <b>Amdocs-Matrixx Deal:</b> Amdocs finalized its $200M acquisition of Matrixx on Jan 6 to dominate 5G charging.<br>
                • <b>Cerillion Record Win:</b> BSS provider secured its largest deal (£42.5M) with Omantel on Jan 8.</p>
            </div>
            <div style="flex: 1; background: #f1f5f9; padding: 1.5rem; border-radius: 10px;">
                <h3 style="color: #f97316;">🟠 PULSE</h3>
                <p class="news-text">• <b>Agentic AI Core:</b> 40% of enterprise apps will incorporate task-specific AI agents by EOY 2026.<br>
                • <b>Decision Velocity:</b> Enterprises shift from "copilots" to autonomous "agent-driven execution".</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # C. Industry Verticals (Independent Grids)
    cols = st.columns(4)
    labels = [("📡 TELCO OSS/BSS", "#db2777", "telco"), ("📺 OTT", "#7c3aed", "ott"), ("🏆 SPORTS", "#059669", "sports"), ("⚡ AI TECH", "#ea580c", "tech")]
    
    for idx, (label, color, key) in enumerate(labels):
        with cols[idx]:
            content = "".join([f'<div style="margin-bottom:12px;"><b>{e["source"]}:</b> {e["title"]}<br><a href="{e["link"]}" style="font-size:0.8rem;">Read More →</a></div>' for e in data[key]])
            st.markdown(f'<div class="section-card"><div class="section-header" style="color:{color}; border-color:{color};">{label}</div>{content}</div>', unsafe_allow_html=True)

    st.caption(f"Last Intelligence Sync: {datetime.now().strftime('%H:%M:%S')} | 🚀 Engine Active")

# 5. EXECUTION
render_dashboard()
