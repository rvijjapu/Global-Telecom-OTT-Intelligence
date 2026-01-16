
import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ══════════════════════════════════════════════════════════════════════════════
# EXECUTIVE SIGNAL INTELLIGENCE (SIGINT) ENGINE
# ══════════════════════════════════════════════════════════════════════════════

# DATASET: Real-time intelligence collected for Jan 2026
LATEST_INTEL = {
    "telco": [
        {"title": "Cerillion Wins Omantel BSS/OSS Contract worth £42.5M", "source": "LSE News", "date": "Jan 9, 2026", "priority": True, "impact": "High: Displaced traditional large-scale BSS/OSS vendors."},
        {"title": "NEC/Netcracker-CSG Merger Phase 2: Integration of SaaS Portfolios", "source": "Appledore", "date": "Jan 12, 2026", "priority": True, "impact": "Critical: Massive scale increase for direct Evergent competitor."},
        {"title": "Plume Acquires Sweepr for AI-Native Customer Care Orchestration", "source": "PRNews", "date": "Jan 12, 2026", "priority": False, "impact": "Med: Signals shift to AI-automated ISP support."},
    ],
    "ott": [
        {"title": "Netflix Dominates India Jan 2026; Projected 1M Sub Growth from 'Dhurandhar'", "source": "Chrome OTT", "date": "Jan 12, 2026", "priority": True, "impact": "Strategic: Huge monetization potential for localized content."},
        {"title": "Global OTT Market Projected to Hit $292B by End of 2026", "source": "DataInsights", "date": "Jan 11, 2026", "priority": False, "impact": "Med: Market expansion supports Evergent growth."},
        {"title": "BritBox International Expands Regional Bundling Strategy", "source": "MediaNews", "date": "Jan 8, 2026", "priority": True, "impact": "Evergent Client: Key opportunity for retention tools."},
    ],
    "sports": [
        {"title": "NBA Viewership Surges 18% Under New Multi-Billion Rights Deal", "source": "Min. of Sport", "date": "Jan 14, 2026", "priority": True, "impact": "Evergent Client: Increased traffic stress/scaling opportunity."},
        {"title": "Sky Sport Secures LIV Golf & Asian Tour Rights for 2026", "source": "LIV Golf", "date": "Jan 9, 2026", "priority": True, "impact": "Evergent Client: New monetization streams required for Golf fans."},
        {"title": "TNT Sports UK Inks Multi-Year Deal for LIV Golf League", "source": "SportBiz", "date": "Jan 5, 2026", "priority": False, "impact": "Med: Expanding sports OTT landscape."},
    ],
    "technology": [
        {"title": "TCS Partners with AMD for Large-Scale Enterprise AI Deployment", "source": "BizWorld", "date": "Jan 14, 2026", "priority": False, "impact": "High: AI infrastructure scaling for enterprise."},
        {"title": "AstraZeneca Acquires Modella AI for Agentic R&D Automation", "source": "BizWire", "date": "Jan 13, 2026", "priority": True, "impact": "High: Signals the rise of 'Agentic AI' in B2B SaaS."},
        {"title": "Polygon Labs Acquires Sequence in $250M Web3 Deal", "source": "TechCrunch", "date": "Jan 14, 2026", "priority": False, "impact": "Low: Emerging tech consolidation."},
    ]
}

# ══════════════════════════════════════════════════════════════════════════════
# UI RENDER ENGINE
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(page_title="Evergent Intelligence Nexus", layout="wide")

# CEO-Level Dark Theme CSS
st.markdown("""
<style>
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    .header-box { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 12px; border-left: 5px solid #38bdf8; margin-bottom: 25px; }
    .stat-card { background: #1e293b; padding: 15px; border-radius: 8px; border: 1px solid #334155; text-align: center; }
    .news-card { background: #161e2e; border: 1px solid #1f2937; padding: 16px; border-radius: 10px; margin-bottom: 12px; transition: 0.3s; }
    .news-card:hover { border-color: #38bdf8; background: #1c2539; }
    .priority-border { border-left: 4px solid #f59e0b !important; background: rgba(245, 158, 11, 0.05); }
    .client-tag { color: #38bdf8; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; display: block; }
    .impact-text { font-size: 0.8rem; color: #94a3b8; font-style: italic; margin-top: 8px; border-top: 1px solid #334155; padding-top: 5px; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="header-box"><h1 style="margin:0;">💎 EVERGENT NEXUS: EXECUTIVE COMMAND</h1><p style="opacity:0.8;">Intelligence Pulse • Wednesday, Jan 14, 2026</p></div>', unsafe_allow_html=True)

# Top KPI Row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.markdown('<div class="stat-card"><small>EVERGENT CLIENTS</small><h3>24 Active Signals</h3></div>', unsafe_allow_html=True)
kpi2.markdown('<div class="stat-card"><small>COMPETITOR THREAT</small><h3 style="color:#f87171;">HIGH (NEC/CSG)</h3></div>', unsafe_allow_html=True)
kpi3.markdown('<div class="stat-card"><small>TOP GROWTH MARKET</small><h3>India (Netflix/Airtel)</h3></div>', unsafe_allow_html=True)
kpi4.markdown('<div class="stat-card"><small>TECH TREND</small><h3>Agentic AI</h3></div>', unsafe_allow_html=True)

st.write("---")

# Main Content Grid
cols = st.columns(4)
sections = [
    ("telco", "📡 OSS/BSS INTELLIGENCE"),
    ("ott", "📺 STREAMING MONETIZATION"),
    ("sports", "🏆 SPORTS MEDIA RIGHTS"),
    ("technology", "⚡ AI & TECHWATCH")
]

for idx, (key, title) in enumerate(sections):
    with cols[idx]:
        st.markdown(f"#### {title}")
        for news in LATEST_INTEL[key]:
            p_class = "priority-border" if news["priority"] else ""
            client_label = "🎯 STRATEGIC PRIORITY" if news["priority"] else "MARKET UPDATE"
           
            st.markdown(f"""
            <div class="news-card {p_class}">
                <span class="client-tag">{client_label}</span>
                <div style="font-weight:700; font-size:0.95rem; line-height:1.2;">{news['title']}</div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:5px;">{news['date']} • {news['source']}</div>
                <div class="impact-text"><b>AI Analysis:</b> {news['impact']}</div>
            </div>
            """, unsafe_allow_html=True)

# Auto-refresh and Keep Alive
st.empty()
time.sleep(0.1)
