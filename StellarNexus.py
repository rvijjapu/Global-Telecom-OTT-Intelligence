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
# SECTION URLS (EXACTLY YOUR URLS)
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
    f"Updated: {datetime.now().strftime('%d %b %Y %I:%M %p')} • Auto-refresh every 5 minutes"
)

# ─────────────────────────────────────────────
# DISPLAY EACH SECTION IMMEDIATELY
# ─────────────────────────────────────────────
cols = st.columns(4)

for col, (section_name, url) in zip(cols, SECTION_URLS.items()):
    with col:
        st.markdown(f"### {section_name}")
        st.components.v1.iframe(
            src=url,
            height=750,     # fits neatly inside each section
            scrolling=True
        )

# ─────────────────────────────────────────────
# AUTO REFRESH
# ─────────────────────────────────────────────
st.markdown("""
<script>
setTimeout(function () {
    window.location.reload();
}, 300000);
</script>
""", unsafe_allow_html=True)
