import streamlit as st
import feedparser
import requests
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
import time
import re

# ==========================
# 🔐 CEO TOKEN SECURITY GATE
# ==========================
try:
    EXPECTED_TOKEN = st.secrets["CEO_ACCESS_TOKEN"]
except FileNotFoundError:
    st.error("🔧 Missing secrets.toml – Add CEO_ACCESS_TOKEN in .streamlit/secrets.toml or Streamlit Cloud Secrets")
    st.stop()
except KeyError:
    st.error("🔧 CEO_ACCESS_TOKEN not found in secrets")
    st.stop()

provided_token = st.query_params.get("token")
if provided_token is not None:
    provided_token = provided_token[0] if isinstance(provided_token, list) else provided_token
else:
    provided_token = ""

if provided_token != EXPECTED_TOKEN:
    st.error("⛔ Unauthorized access – Invalid or missing token")
    st.info("Append `?token=your_token` to the URL or contact admin.")
    st.stop()

# Rate limiting
if "last_access" not in st.session_state:
    st.session_state.last_access = 0

now = time.time()
if now - st.session_state.last_access < 2:
    st.warning("⏱ Too many requests – Please wait a moment.")
    st.stop()

st.session_state.last_access = now

st.set_page_config(
    page_title="🌐 Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === FANTASTIC MODERN 2026 UI STYLING – GLASSMORPHISM + VIBRANT GRADIENTS ===
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap" rel="stylesheet">
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    html, body, [class*="css"]  {  
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: url('https://raw.githubusercontent.com/rvijjapu/stellar-Nexus/main/4.png') no-repeat center center fixed;
        background-size: cover;
        padding-top: 0.5rem;
    }

    .header-container {
        background: rgba(255, 255, 255, 0.15);
        padding: 2rem 2.5rem;
        text-align: center;
        border-radius: 28px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        margin: 0 2.5rem 3rem 2.5rem;
        border: 1px solid rgba(255,255,255,0.2);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    .main-title {
        font-family: 'Manrope', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1.5px;
        background: linear-gradient(135deg, #a855f7, #3b82f6, #10b981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        font-family: 'Manrope', sans-serif;
        font-size: 1.35rem;
        color: rgba(255,255,255,0.9);
        margin-top: 0.8rem;
        font-weight: 600;
    }

    .col-header {
        padding: 16px 24px;
        border-radius: 20px 20px 0 0;
        color: white;
        font-family: 'Manrope', sans-serif;
        font-weight: 700;
        font-size: 1.15rem;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        letter-spacing: 0.8px;
        backdrop-filter: blur(10px);
    }

    /* Vibrant 2026 Gradient Headers */
    .col-header-telco { background: linear-gradient(135deg, #ff6b6b, #ee5a24); }      /* Fiery Coral-Orange */
    .col-header-ott { background: linear-gradient(135deg, #9f7aea, #da70d6); }        /* Orchid-Pink */
    .col-header-sports { background: linear-gradient(135deg, #51cf66, #40c057); }     /* Emerald Green */
    .col-header-tech { background: linear-gradient(135deg, #339af0, #22b8cf); }       /* Cyan Blue */

    .col-body {
        background: rgba(255, 255, 255, 0.12);
        border-radius: 0 0 20px 20px;
        padding: 18px;
        min-height: 560px;
        max-height: 660px;
        overflow-y: auto;
        box-shadow: 0 12px 40px rgba(0,0,0,0.18);
        margin-bottom: 1.8rem;
        border: 1px solid rgba(255,255,255,0.18);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
    }

    .news-card {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 14px;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 6px 16px rgba(0,0,0,0.1);
    }

    .news-card:hover {
        transform: translateY(-8px) scale(1.02);
        background: rgba(255, 255, 255, 0.18);
        box-shadow: 0 20px 40px rgba(0,0,0,0.25);
    }

    .news-card-priority {
        background: linear-gradient(145deg, rgba(255,251,235,0.25), rgba(254,252,232,0.15));
        border: 2px solid rgba(251,191,36,0.6);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(251,191,36,0.25);
        transition: all 0.5s ease;
    }

    .news-card-priority:hover {
        transform: translateY(-10px) scale(1.03);
        box-shadow: 0 24px 48px rgba(251,191,36,0.35);
        background: linear-gradient(145deg, rgba(255,251,235,0.35), rgba(254,252,232,0.25));
    }

    /* STYLISH MODERN NEWS TITLE */
    .news-title {
        font-family: 'Manrope', sans-serif;   /* Ultra-modern geometric font – 2026 favorite */
        font-size: 1.05rem;                   /* Perfect clarity & elegance */
        font-weight: 700;
        line-height: 1.5;
        color: #ffffff;
        text-decoration: none;
        display: block;
        margin-bottom: 10px;
        transition: all 0.4s ease;
    }

    .news-title:hover {
        color: #e0f2fe;
        transform: translateX(6px);
    }

    .news-meta {
        font-size: 0.82rem;
        color: rgba(255,255,255,0.85);
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
        font-weight: 500;
    }

    .time-hot { color: #ff6b6b; font-weight: 800; }
    .time-warm { color: #ffa726; font-weight: 700; }
    .time-normal { color: rgba(255,255,255,0.7); }
</style>
""", unsafe_allow_html=True)

# === TITLE ===
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# === RSS FEEDS & REST OF CODE (UNCHANGED FROM PREVIOUS VERSION) ===
# ... [Keep all the RSS_FEEDS, PRIORITY_SOURCES, filters, fetch_feed, load_feeds, render_body, etc. exactly as in the last version]

# (To save space, the rest of the code remains identical – only styling changed above)

# === LOADING MESSAGE ===
placeholder = st.empty()
placeholder.markdown("<h2 style='text-align:center;color:#e0f2fe;margin-top:160px;font-family:\"Manrope\";font-weight:700;'>✨ Igniting the future of intelligence...<br><small style='color:rgba(255,255,255,0.8);'>Preparing your nexus</small></h2>", unsafe_allow_html=True)

with st.spinner(""):
    data = load_feeds()

placeholder.empty()

# === RENDER DASHBOARD ===
cols = st.columns(4)
cat_list = ["telco", "ott", "sports", "technology"]

for idx, cat in enumerate(cat_list):
    sec = SECTIONS[cat]
    items = data.get(cat, [])
    
    with cols[idx]:
        st.markdown(f'<div class="{sec["style"]}">{sec["icon"]} {sec["name"]}</div>', unsafe_allow_html=True)
        st.markdown(render_body(items), unsafe_allow_html=True)
