import streamlit as st
import time
from datetime import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# 2. PREMIUM CSS: Background, Dark Blue visibility, and Modular Sections
st.markdown("""
<style>
    /* Custom Background */
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
    }
    
    /* Center the Loading State */
    .loading-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 80vh;
        text-align: center;
    }
    
    /* Dark Blue Professional Fonts for Loading and Titles */
    .dark-blue-text {
        color: #0a192f !important;
        font-weight: 800 !important;
    }

    .main-title {
        font-size: 3.2rem !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.5);
        margin-bottom: 20px;
    }

    /* Hero Section: Strategic Baseline (Dark Font on Light Background) */
    .hero-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-bottom: 3rem;
    }

    .hero-title {
        color: #0f172a !important;
        font-size: 1.8rem;
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

    /* Vertical Section Cards (Light Background for Data Visibility) */
    .section-card {
        background: rgba(255, 255, 255, 0.98);
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
    .link-btn:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# 3. IMPACTFUL LOADING SEQUENCE
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div class="loading-container">
            <h1 class="dark-blue-text main-title">Igniting AI-powered intelligence...</h1>
            <p style="color: #0a192f; font-weight: 700; font-size: 1.2rem;">Synchronizing Global Strategic Nodes</p>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.8) # Milliseconds simulation

placeholder.empty()

# 4. MAIN DASHBOARD CONTENT
st.markdown("<h1 class='dark-blue-text main-title' style='text-align: center;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

# 🚀 STRATEGIC BASELINE SECTION
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🚀 STRATEGIC BASELINE</div>
    <div style="display: flex; gap: 20px;">
        <div class="hero-box" style="flex: 1;">
            <div style="font-weight:800; color:#10b981; font-size:1.1rem; margin-bottom:12px;">🟢 STRATEGIC HITS (JAN 2026)</div>
            <p style="color:#1e293b; font-size:0.95rem; line-height:1.7;">
                <b>Netflix-WBD Merger:</b> Board unanimously recommends stockholders approve the $82.7B merger with Netflix, rejecting Paramount’s amended offer as "insufficient value." <br>
                <b>NEC-CSG Finalization:</b> NEC Corporation (Netcracker) has closed its $2.9B acquisition of CSG, creating a dominant SaaS and AI powerhouse. <br>
                <b>Jio Platforms IPO:</b> Reliance Jio preparing for a landmark 2.5% stake sale, potentially India's largest-ever IPO at a $180B+ valuation.
            </p>
        </div>
        <div class="hero-box" style="flex: 1;">
            <div style="font-weight:800; color:#f97316; font-size:1.1rem; margin-bottom:12px;">🟠 TECH PULSE: AGENTIC REALITY</div>
            <p style="color:#1e293b; font-size:0.95rem; line-height:1.7;">
                <b>Agentic Infrastructure:</b> By EOY 2026, 40% of enterprise software will embed task-specific AI agents, up from <5% in 2024. <br>
                <b>BSS Consolidation:</b> Amdocs completes its $200M rescue of Matrixx Software, securing a 23% revenue share in the charging product market. <br>
                <b>CES 2026 Roundup:</b> First eSIM-enabled AR glasses and mass-market humanoid robot production confirmed as 2026 key tech trends.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 📊 VERTICAL INTELLIGENCE GRID
col1, col2, col3, col4 = st.columns(4)

sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        {"t": "NEC (Netcracker) completes $2.9B CSG acquisition to dominate global BSS/OSS market share.", "l": "https://techafricanews.com/2025/10/29/nec-expands-global-saas-and-ai-capabilities-with-us2-9-billion-csg-acquisition/"},
        {"t": "Amdocs acquires Matrixx Software for $200M to counter rising competitor M&A scaling.", "l": "https://www.lightreading.com/oss-bss-cx/amdocs-snaps-up-matrixx-for-200m-in-rescue-of-bss-player"},
        {"t": "Reliance Jio eyes $4.5B from public offering as IPO documentation enters advanced phase.", "l": "https://www.business-standard.com/markets/ipo/reliance-jio-platforms-considers-2-5-public-offering-in-2026-india-ipo-126010900777_1.html"}
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        {"t": "Netflix merger agreement with WBD on track for Q3 2026 completion of Discovery Global spin-off.", "l": "https://ir.netflix.net/investor-news-and-events/financial-releases/press-release-details/2026/Netflix-Supports-Warner-Bros--Discovery-Boards-Commitment-to-Merger-Agreement/default.aspx"},
        {"t": "WBD Board unanimously recommends rejection of Paramount tender offer in favor of Netflix combination.", "l": "https://ir.wbd.com/news-and-events/financial-news/financial-news-details/2026/WARNER-BROS--DISCOVERY-BOARD-OF-DIRECTORS-UNANIMOUSLY-RECOMMENDS-SHAREHOLDERS-REJECT-AMENDED-PARAMOUNT-TENDER-OFFER/default.aspx"},
        {"t": "Regional OTT consolidation: Discovery Global planned separation set for late 2026.", "l": "https://ir.netflix.net/investor-news-and-events/financial-releases/press-release-details/2026/Netflix-Supports-Warner-Bros--Discovery-Boards-Commitment-to-Merger-Agreement/default.aspx"}
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        {"t": "WNBA secures landmark 11-year, $2.2B rights deal with Disney, NBC, and Amazon Prime Video.", "l": "https://www.wnba.com/news/media-rights-deal-disney-prime-nbc"},
        {"t": "Amazon Prime Video becomes first streamer to secure exclusive WNBA Finals rights for 3 years.", "l": "https://frontofficesports.com/wnba-signs-2-2-billion-rights-deal-with-disney-nbc-amazon/"},
        {"t": "NBA All-Star 2026 set for Chase Center as media rights officially transition to new partners.", "l": "https://frontofficesports.com/wnba-signs-2-2-billion-rights-deal-with-disney-nbc-amazon/"}
    ]),
    ("⚡ CORE TECHNOLOGY", "#ea580c", [
        {"t": "Agentic AI shift: Gartner predicts 40% of early enterprise agentic projects will face abandonment due to poor governance.", "l": "https://www.analyticsvidhya.com/blog/2026/01/agentic-ai-expert-learning-path/"},
        {"t": "2026 predicted to be the 'Year of the Agentic AI Intern' as task-specific AI adoption surges.", "l": "https://www.artificialintelligence-news.com/news/agent-ai-as-the-intern-in-2026-prediction-by-nexos-ai/"},
        {"t": "Humanoid robot production goes exponential in early 2026, led by significant advancements in China.", "l": "https://www.telecoms.com/oss-bss-cx/matrixx-takes-the-blue-pill-and-joins-amdocs"}
    ])
]

# RENDER SECTIONS
for idx, (label, color, news_list) in enumerate(sections):
    with [col1, col2, col3, col4][idx]:
        news_html = ""
        for item in news_list:
            news_html += f"""
            <div class="news-item">
                <div class="news-text">{item['t']}</div>
                <a href="{item['l']}" target="_blank" class="link-btn">Read Full Story →</a>
            </div>"""
        
        st.markdown(f"""
        <div class="section-card">
            <div class="section-header" style="color: {color}; border-color: {color};">{label}</div>
            {news_html}
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown(f"<p style='text-align: center; color: white; padding-top: 20px;'>Live Sync: {datetime.now().strftime('%H:%M:%S')}</p>", unsafe_allow_html=True)
