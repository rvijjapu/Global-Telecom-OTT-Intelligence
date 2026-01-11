import streamlit as st
import time
from datetime import datetime

# --- 1. NEVER-SLEEP / KEEP-ALIVE FRAGMENT ---
@st.fragment(run_every=600)
def keep_alive_engine():
    st.markdown("", unsafe_allow_html=True)

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# --- 3. PREMIUM CSS: DARK BLUE VISIBILITY & LIGHT THEME CARDS ---
st.markdown("""
<style>
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
    }
    
    .loading-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 80vh;
        text-align: center;
    }
    
    .dark-blue-text {
        color: #0a192f !important;
        font-weight: 800 !important;
    }

    .main-title {
        font-size: 3.5rem !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.4);
        margin-bottom: 25px;
    }

    /* Strategic Baseline (Top Focus) */
    .hero-container {
        background: rgba(255, 255, 255, 0.98);
        border-radius: 15px;
        padding: 2rem;
        border-left: 10px solid #0a192f;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 3rem;
    }

    .hero-title {
        color: #0a192f !important;
        font-size: 1.85rem;
        font-weight: 800;
        margin-bottom: 1.5rem;
        border-left: 6px solid #1e40af;
        padding-left: 15px;
    }

    .hero-box {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 1.5rem;
        min-height: 220px;
        border: 1px solid #e2e8f0;
    }

    /* Industry Vertical Cards */
    .section-card {
        background: rgba(255, 255, 255, 1.0);
        padding: 24px;
        border-radius: 12px;
        min-height: 520px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    .section-header {
        font-size: 1.25rem;
        font-weight: 800;
        padding-bottom: 12px;
        border-bottom: 3px solid;
        text-transform: uppercase;
        margin-bottom: 20px;
    }

    .news-item {
        margin-bottom: 18px;
        padding-bottom: 10px;
        border-bottom: 1px solid #f1f5f9;
    }

    .news-text {
        font-size: 0.95rem;
        color: #1e293b;
        line-height: 1.6;
        margin-bottom: 8px;
    }

    .link-btn {
        color: #1e40af;
        font-weight: 700;
        text-decoration: none;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. IMPACTFUL LOADING SEQUENCE ---
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div class="loading-container">
            <h1 class="dark-blue-text" style="font-size: 3.5rem;">Igniting AI-powered intelligence...</h1>
            <p class="dark-blue-text" style="font-size: 1.2rem; opacity: 0.8;">Bypassing legacy filters. Synchronizing 2026 strategic nodes.</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.8) 

placeholder.empty()
keep_alive_engine()

# --- 5. MAIN DASHBOARD CONTENT ---
st.markdown("<h1 class='dark-blue-text main-title' style='text-align: center;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

# --- 🚀 STRATEGIC BASELINE ---
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🚀 STRATEGIC HIGHLIGHTS</div>
    <div style="display: flex; gap: 20px;">
        <div class="hero-box" style="flex: 1;">
            <div style="font-weight:800; color:#10b981; font-size:1.1rem; margin-bottom:12px;">🟢 STRATEGIC HITS (JAN 2026)</div>
            <div style="color:#1e293b; font-size:0.95rem; line-height:1.7;">
                • <b>Netflix-WBD Merger Reaffirmed:</b> Warner Bros. Discovery board unanimously backs Netflix's $82.7B proposal, rejecting Paramount's $108.4B hostile bid due to excessive debt risks.<br>
                • <b>NEC-CSG Finalization:</b> NEC (Netcracker) has closed its $2.9B acquisition of CSG, creating a dominant SaaS-first monetization powerhouse for Tier-1 telcos.<br>
                • <b>Amdocs Secures Charging Lead:</b> Completion of $200M Matrixx acquisition gives Amdocs a 23% revenue share in the global charging platform market.
            </div>
        </div>
        <div class="hero-box" style="flex: 1;">
            <div style="font-weight:800; color:#f97316; font-size:1.1rem; margin-bottom:12px;">🟠 PULSE: AGENTIC REALITY</div>
            <div style="color:#1e293b; font-size:0.95rem; line-height:1.7;">
                • <b>Agentic BSS Core:</b> Gartner predicts 40% of enterprise applications will embed autonomous AI agents by end-of-year 2026, up from <5% in 2025.<br>
                • <b>Zero-Touch Orchestration:</b> Telcos like Telefónica and AT&T move beyond copilots to agentic systems that take autonomous troubleshooting and fulfillment actions.<br>
                • <b>Legacy Replacement Wave:</b> 2026 marks the tipping point where "wrapping" legacy stacks is no longer viable, making full cloud-native replacement inevitable.
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 📊 VERTICAL INDUSTRY GRID ---
col1, col2, col3, col4 = st.columns(4)

sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        {"t": "NEC (Netcracker) completes $2.9B acquisition of CSG to dominate SaaS BSS globally.", "l": "https://tecknexus.com/nec-buys-csg-for-2-9b-to-scale-saas-bss-monetization/"},
        {"t": "Amdocs acquires Matrixx for $200M to bolster its leadership in 5G charging platform sales.", "l": "https://www.lightreading.com/oss-bss-cx/amdocs-snaps-up-matrixx-for-200m-in-rescue-of-bss-player"},
        {"t": "Wavelo named 'Digital BSS Trailblazer' as event-driven software gains market traction.", "l": "https://www.thefastmode.com/oss-bss-news"}
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        {"t": "Netflix $82.7B WBD merger on track for Q3 2026 close after board rejects rival suitor.", "l": "https://ir.netflix.net/investor-news-and-events/financial-releases/press-release-details/2026/Netflix-Supports-Warner-Bros--Discovery-Boards-Commitment-to-Merger-Agreement/default.aspx"},
        {"t": "Warner Bros. Discovery board unanimously recommends stockholders reject Paramount hostile bid.", "l": "https://ir.wbd.com/news-and-events/financial-news/financial-news-details/2026/WARNER-BROS--DISCOVERY-BOARD-OF-DIRECTORS-UNANIMOUSLY-RECOMMENDS-SHAREHOLDERS-REJECT-AMENDED-PARAMOUNT-TENDER-OFFER/default.aspx"},
        {"t": "Media M&A surge continues as players move from growth phase to profitability focus.", "l": "https://www.thecurrent.com/streaming-2025-media-mergers-acquisitions-streaming-2026"}
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        {"t": "WNBA secures landmark 11-year, $2.2B rights agreement with Disney, NBC, and Amazon.", "l": "https://frontofficesports.com/wnba-signs-2-2-billion-rights-deal-with-disney-nbc-amazon/"},
        {"t": "DAZN acquires Foxtel in strategic move to secure high-value sports rights in Australia.", "l": "https://www.thecurrent.com/streaming-2025-media-mergers-acquisitions-streaming-2026"},
        {"t": "Streaming players transition to unified ad-inventory models for live sports events.", "l": "https://www.thecurrent.com/streaming-2025-media-mergers-acquisitions-streaming-2026"}
    ]),
    ("⚡ AI TECHWATCH", "#ea580c", [
        {"t": "2026 defined by 'Industrialisation of AI' as enterprises embed agents into core workflows.", "l": "https://www.financialexpress.com/business/news/2026-will-be-defined-by-the-industrialisation-of-ai-venu-lambu-ceo-amp-md-ltimindtree/4097152/"},
        {"t": "Gartner: 40% of enterprise apps will embed AI agents by the end of 2026.", "l": "https://machinelearningmastery.com/7-agentic-ai-trends-to-watch-in-2026/"},
        {"t": "Coforge launches EvolveOps.AI for autonomous IT operations management.", "l": "https://www.thefastmode.com/oss-bss-news"}
    ])
]

# RENDER COLUMNS
for idx, (label, color, news_list) in enumerate(sections):
    with [col1, col2, col3, col4][idx]:
        news_html = ""
        for item in news_list:
            news_html += f"""
            <div class="news-item">
                <div class="news-text">{item['t']}</div>
                <a href="{item['l']}" target="_blank" class="link-btn">Read Full Story →</a>
            </div>"""
        
        st.html(f"""
        <div class="section-card">
            <div class="section-header" style="color: {color}; border-color: {color};">{label}</div>
            {news_html}
        </div>
        """)

# --- 7. FOOTER ---
st.markdown(f"<p style='text-align: center; color: white; padding-top: 20px;'>Live Intelligence Sync: {datetime.now().strftime('%H:%M:%S')} | 🚀 Never-Sleep Active</p>", unsafe_allow_html=True)
