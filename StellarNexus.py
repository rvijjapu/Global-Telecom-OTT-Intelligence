import streamlit as st
import time
from datetime import datetime

# 1. PAGE CONFIGURATION
st.set_page_config(page_title="Global Intelligence Stellar Nexus", layout="wide")

# 2. CUSTOM CSS FOR BACKGROUND & LOADING
st.markdown("""
<style>
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        color: #1e293b;
    }
    
    /* Center the loading text */
    .loading-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 80vh;
        color: #ffffff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .loading-text {
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }

    /* Professional Card Styling for Sections */
    .vertical-section {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 12px;
        min-height: 480px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
    }

    .vertical-header {
        font-size: 1.2rem;
        font-weight: 800;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 3px solid;
        text-transform: uppercase;
    }

    .news-item {
        margin-bottom: 15px;
        padding-bottom: 8px;
        border-bottom: 1px solid #f1f5f9;
    }

    .news-text {
        font-size: 0.95rem;
        color: #334155;
        line-height: 1.4;
    }

    .read-more {
        font-size: 0.85rem;
        color: #1e40af;
        font-weight: 700;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

# 3. LOADING SCREEN (st.empty used to replace content)
placeholder = st.empty()
with placeholder.container():
    st.markdown("""
        <div class="loading-container">
            <div class="loading-text">🔥 Igniting AI-powered intelligence...</div>
            <div style="color: #cbd5e1;">Please wait while we synchronize global nodes.</div>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(1.5)  # Simulate fast loading

placeholder.empty()

# 4. DASHBOARD CONTENT
# Header
st.markdown("<h1 style='text-align: center; color: white; text-shadow: 2px 2px 5px #000;'>Global Telecom & OTT Stellar Nexus</h1>", unsafe_allow_html=True)

# TOP SECTION: STRATEGIC BASELINE
st.markdown("""
<div style="background: rgba(255,255,255,0.9); padding: 25px; border-radius: 15px; margin-bottom: 30px; border-left: 8px solid #1e40af;">
    <h2 style="color: #0f172a; margin: 0 0 15px 0;">🚀 STRATEGIC BASELINE</h2>
    <div style="display: flex; gap: 20px;">
        <div style="flex: 1; background: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0;">
            <div style="font-weight:800; color:#10b981; margin-bottom:8px;">🟢 STRATEGIC HITS (JAN 2026)</div>
            <div style="font-size:0.95rem; color:#334155;"><b>Netflix-WBD Merger:</b> Netflix confirms definitive agreement to acquire Warner Bros. for $82.7B to unify HBO Max with its global platform.</div>
            <div style="font-size:0.95rem; color:#334155; margin-top:8px;"><b>Amdocs-Matrixx Deal:</b> Amdocs completes $200M acquisition of Matrixx Software to dominate 5G cloud-native charging.</div>
        </div>
        <div style="flex: 1; background: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #e2e8f0;">
            <div style="font-weight:800; color:#f97316; margin-bottom:8px;">🟠 TECH PULSE: AGENTIC REALITY</div>
            <div style="font-size:0.95rem; color:#334155;"><b>Agentic AI Core:</b> 40% of upcoming agentic projects predicted to fail unless organizations redesign operations for silicon-based workforces.</div>
            <div style="font-size:0.95rem; color:#334155; margin-top:8px;"><b>Autonomous Networks:</b> Ericsson and Nokia advance self-healing "sensing" networks capable of real-time anomaly detection.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# INDUSTRY SECTIONS
col1, col2, col3, col4 = st.columns(4)

sections = [
    ("📡 TELCO OSS/BSS", "#db2777", [
        {"t": "Amdocs snaps up Matrixx for $200M to consolidate charging product market share.", "l": "https://www.lightreading.com"},
        {"t": "BSS/OSS modernization deemed essential for monetizing 5G Standalone and network slicing.", "l": "https://www.rcrwireless.com"},
        {"t": "NEC completes acquisition of CSG to scale Netcracker's global BSS footprint.", "l": "https://www.netcracker.com"}
    ]),
    ("📺 OTT & STREAMING", "#7c3aed", [
        {"t": "Netflix board rejects Paramount's $77.9B offer, favoring WBD $72B proposal for studios.", "l": "https://www.variety.com"},
        {"t": "Warner Bros. Discovery separation into Discovery Global expected in Q3 2026.", "l": "https://about.netflix.com"},
        {"t": "Consolidation unease grows in Indian market over content concentration risk.", "l": "https://www.outlookindia.com"}
    ]),
    ("🏆 SPORTS MEDIA", "#059669", [
        {"t": "WNBA secures landmark 11-year rights deal with Disney, Amazon, and NBCUniversal.", "l": "https://www.wnba.com"},
        {"t": "NBA Sunday Night Basketball series to debut on NBC and Peacock for 2025-26 season.", "l": "https://www.nbcuniversal.com"},
        {"t": "Prime Video expands global distribution rights for WNBA League Pass through 2036.", "l": "https://www.amazon.com"}
    ]),
    ("⚡ CORE TECHNOLOGY", "#ea580c", [
        {"t": "Amazon deploys 1 millionth robot; DeepFleet AI improves travel efficiency by 10%.", "l": "https://www.deloitte.com"},
        {"t": "Enterprises shift from cloud-first to strategic hybrid for AI inference economics.", "l": "https://www.gartner.com"},
        {"t": "Multi-agent systems (MAS) evolve to automate complex cross-platform workflows.", "l": "https://digitalmara.com"}
    ])
]

# Render industry section cards
for idx, (label, color, news_list) in enumerate(sections):
    with [col1, col2, col3, col4][idx]:
        news_html = ""
        for item in news_list:
            news_html += f"""
            <div class="news-item">
                <div class="news-text">{item['t']}</div>
                <a href="{item['l']}" target="_blank" class="read-more">Read Full Story →</a>
            </div>"""
        
        st.markdown(f"""
        <div class="vertical-section">
            <div class="vertical-header" style="color: {color}; border-color: {color};">{label}</div>
            {news_html}
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown(f"<div style='text-align: center; color: white; padding: 20px;'>Live Intelligence Sync: {datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
