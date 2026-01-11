import streamlit as st
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# SECTION URLS (EXACT)
# ─────────────────────────────────────────────
SECTION_URLS = {
    "TELCO OSS/BSS":
        "https://www.google.com/search?q=recent+telecom+OSS+BSS+key+announcements+providers+organizers+news+key+announcements+2026+exclude+2025&udm=50",

    "OTT & STREAMING":
        "https://www.google.com/search?q=recent+OTT+providers+key+announcements+providers+organizers+news+key+announcements+mergers+acquisitions+deals+profit+losses+2026+exclude+2025&udm=50",

    "SPORTS & EVENTS":
        "https://www.google.com/search?q=recent+Sports+Events+organizers+key+announcements+provider+organizers+news+key+announcements+mergers+acquisitions+deals+profit+losses+2026+exclude+2025&udm=50",

    "TECHNOLOGY":
        "https://www.google.com/search?q=recent+Technology+key+announcements+provider+organizers+news+key+announcements+mergers+acquisitions+deals+profit+losses+2026+exclude+2025&udm=50"
}

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("## 🌐 Global Telecom & OTT Stellar Nexus — LIVE 2026")

st.caption(
    f"Updated: {datetime.now().strftime('%d %b %Y %I:%M %p')}"
)

# ─────────────────────────────────────────────
# IMMEDIATE DISPLAY PER SECTION (NO IFRAME)
# ─────────────────────────────────────────────
cols = st.columns(4)

for col, (section, url) in zip(cols, SECTION_URLS.items()):
    with col:
        st.subheader(section)

        st.markdown(
            f"""
            <div style="
                background:#ffffff;
                padding:18px;
                border-radius:12px;
                border-left:6px solid #2563eb;
                box-shadow:0 4px 12px rgba(0,0,0,0.08);
                text-align:center;
            ">
                <p style="font-size:0.9rem;color:#475569;margin-bottom:12px;">
                    Live Google Search results for <b>{section}</b>
                </p>
                <a href="{url}" target="_blank"
                   style="
                     display:inline-block;
                     padding:10px 18px;
                     background:#2563eb;
                     color:white;
                     text-decoration:none;
                     border-radius:8px;
                     font-weight:600;
                   ">
                   🔎 Open Live Results
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<br>
<p style="text-align:center;color:#64748b;font-size:0.8rem;">
Each section opens live Google Search intelligence in a new tab.
</p>
""", unsafe_allow_html=True)
