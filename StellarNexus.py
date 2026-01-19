import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import re
import time

# ────────────────────────────────────────────────
# PAGE CONFIG & KEEP-ALIVE
# ────────────────────────────────────────────────
st.set_page_config(page_title="Global Telecom & OTT Stellar Nexus", page_icon="🌐", layout="wide", initial_sidebar_state="collapsed")

@st.fragment(run_every=600)
def keep_alive():
    st.markdown("", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# PREMIUM STYLING (optimized for reliability)
# ────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@600;700;800&display=swap');

    .stApp {
        background: linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.65)),
                    url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') center/cover no-repeat fixed;
        font-family: 'Inter', sans-serif;
    }

    .header-container, .hero-container, .col-body, .news-card, .footer-container {
        background: rgba(255,255,255,0.08) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    }

    .main-title { 
        font-family: 'Poppins', sans-serif; 
        font-size: 3.2rem; font-weight: 900; 
        background: linear-gradient(135deg, #fff, #c7d2fe); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
    }

    .hero-title { font-size: 2.2rem; font-weight: 800; color: white; }

    .hero-box-title { font-size: 1.35rem; font-weight: 800; }

    .news-card-priority { 
        background: linear-gradient(135deg, rgba(16,185,129,0.22), rgba(5,150,105,0.18)) !important; 
        border: 2px solid rgba(16,185,129,0.45); 
    }

    .col-header { font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }

    /* Reduce aggressive animations for better render stability */
    @keyframes subtlePulse { 0%,100% {opacity:1;} 50% {opacity:0.92;} }
    .hero-box { animation: subtlePulse 8s infinite ease-in-out; }

    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# YOUR RSS + PRIORITY LOGIC (unchanged core)
# ────────────────────────────────────────────────
# ... (keep your EVERGENT_CLIENTS, COMPETITORS, PRIORITY_KWS, ALL_COMPANY_KWS, RSS_FEEDS, SECTIONS, HEADERS, clean(), fetch_feed(), load_feeds(), get_time_str(), get_time_class(), render_body() as-is)

# For brevity — assume you copy your full functions here from previous version

# ────────────────────────────────────────────────
# LOADING + MAIN DASHBOARD
# ────────────────────────────────────────────────
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
    <div style="height:70vh;display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;color:white;">
        <h1 style="font-size:3.5rem;font-weight:900;">⚡ AI Intelligence Engine Warming Up...</h1>
        <p style="font-size:1.4rem;opacity:0.9;">Scanning real-time feeds • Mergers • Partnerships • Strategic Moves</p>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(2.2)  # Give visual feedback

placeholder.empty()

# HEADER
st.markdown('<div class="header-container" style="padding:2.5rem;margin:1rem;text-align:center;"><h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1><p style="color:rgba(255,255,255,0.9);font-size:1.25rem;">AI-Powered Real-time Competitive Intelligence</p></div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────
# STRATEGIC HITS & PULSE - Balanced 3 + 3
# ────────────────────────────────────────────────
st.markdown("""
<div class="hero-container" style="margin:1rem;padding:2.5rem;">
    <div class="hero-title" style="margin-bottom:2rem;">🚀 Strategic Intelligence – AI Engine Auto-Refresh</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:2.5rem;">
        <div class="hero-box" style="padding:2rem;">
            <div class="hero-box-title" style="color:#10b981;border-bottom:3px solid #10b981;margin-bottom:1.5rem;">🟢 STRATEGIC HITS</div>
            <div style="color:rgba(255,255,255,0.95);line-height:1.9;">
                <div style="margin-bottom:1.4rem;"><b>NBA Strategic Investment in Evergent</b><br>NBA takes equity stake, names Evergent Preferred Vendor for global League Pass personalization & churn reduction across 185 countries.</div>
                <div style="margin-bottom:1.4rem;"><b>Agentic AI Shift – CES 2026</b><br>Evergent CEO Vijay Sajja highlights move from GenAI → <b>Agentic AI</b>: BSS autonomously executes retention strategies.</div>
                <div><b>Amdocs Acquires Matrixx ($200M)</b><br>Deal closed – strengthens Amdocs leadership in Tier-1 5G convergent charging & billing.</div>
            </div>
        </div>
        <div class="hero-box" style="padding:2rem;">
            <div class="hero-box-title" style="color:#f97316;border-bottom:3px solid #f97316;margin-bottom:1.5rem;">🟠 MARKET PULSE</div>
            <div style="color:rgba(255,255,255,0.95);line-height:1.9;">
                <div style="margin-bottom:1.4rem;"><b>Agentic AI Dominance by 2026</b><br>Forecast: ~40% of BSS tasks handled by autonomous agents, transforming telecom ops efficiency.</div>
                <div style="margin-bottom:1.4rem;"><b>Satellite Broadband Mainstream</b><br>Direct-to-consumer satellite becomes serious fiber alternative – reshaping ISP competition.</div>
                <div><b>Physical AI Scale-Up</b><br>Amazon hits 1M robots milestone with DeepFleet AI → +10% warehouse efficiency gain.</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# DYNAMIC RSS SECTION + AUTO-REFRESH
# ────────────────────────────────────────────────
with st.spinner("🔍 AI Engine Scanning Latest Strategic Signals..."):
    data = load_feeds()

cols = st.columns(4)
for idx, cat in enumerate(["telco", "ott", "sports", "technology"]):
    sec = SECTIONS[cat]
    items = data.get(cat, [])[:15]
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]} col-header" style="padding:1.2rem;font-size:1.05rem;">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)

# FOOTER + AUTO-REFRESH EMBED
st.markdown("""
<div class="footer-container" style="margin:2rem 1rem;padding:1.5rem;text-align:center;color:rgba(255,255,255,0.9);">
    <strong>Focus:</strong> Mergers • Acquisitions • Partnerships • Strategic Deals<br>
    <strong>Priority Tracking:</strong> Evergent / NBA / Amdocs / Netcracker / NEC • <strong>Auto-refresh:</strong> Every 5 min (AI engine live scan)
</div>
""", unsafe_allow_html=True)

st.markdown('<script>setTimeout(() => { location.reload(); }, 300000);</script>', unsafe_allow_html=True)
keep_alive()
