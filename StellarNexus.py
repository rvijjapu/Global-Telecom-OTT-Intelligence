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
# (unchanged)

# ... [security code unchanged]

st.set_page_config(
    page_title="🌐 Global Telecom & OTT Stellar Nexus",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === ULTRA-MODERN, CEO-PRAISED DASHBOARD UI ===
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
        background: rgba(255, 255, 255, 0.20);
        padding: 2.2rem 2.8rem;
        text-align: center;
        border-radius: 32px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.20);
        margin: 0 3rem 3.5rem 3rem;
        border: 1px solid rgba(255,255,255,0.3);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
    }

    .main-title {
        font-family: 'Manrope', sans-serif;
        font-size: 3.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1.8px;
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        font-family: 'Manrope', sans-serif;
        font-size: 1.4rem;
        color: #1e293b;
        margin-top: 1rem;
        font-weight: 600;
        opacity: 0.92;
    }

    .col-header {
        padding: 18px 28px;
        border-radius: 22px 22px 0 0;
        color: white;
        font-family: 'Manrope', sans-serif;
        font-weight: 700;
        font-size: 1.2rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.28);
        letter-spacing: 1px;
        backdrop-filter: blur(12px);
    }

    /* Premium Gradient Headers */
    .col-header-telco { background: linear-gradient(135deg, #ff6b6b, #ee5a24); }
    .col-header-ott { background: linear-gradient(135deg, #9f7aea, #da70d6); }
    .col-header-sports { background: linear-gradient(135deg, #51cf66, #40c057); }
    .col-header-tech { background: linear-gradient(135deg, #339af0, #22b8cf); }

    .col-body {
        background: rgba(255, 255, 255, 0.28);
        border-radius: 0 0 22px 22px;
        padding: 20px;
        min-height: 580px;
        max-height: 680px;
        overflow-y: auto;
        box-shadow: 0 14px 45px rgba(0,0,0,0.25);
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.35);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }

    /* Uniform clean cards – no priority highlighting */
    .news-card {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 16px;
        transition: all 0.5s ease;
        border: 1px solid rgba(255,255,255,0.7);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }

    .news-card:hover {
        transform: translateY(-10px) scale(1.02);
        background: rgba(255, 255, 255, 0.95);
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
    }

    /* Ultra-modern, smaller, stylish title */
    .news-title {
        font-family: 'Manrope', sans-serif;
        font-size: 0.98rem;        /* Smaller & elegant */
        font-weight: 700;
        line-height: 1.48;
        color: #1e293b;
        text-decoration: none;
        display: block;
        margin-bottom: 12px;
        transition: color 0.4s ease;
    }

    .news-title:hover {
        color: #6366f1;
    }

    .news-meta {
        font-size: 0.80rem;
        color: #475569;
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
        font-weight: 500;
    }

    .time-hot { color: #dc2626; font-weight: 800; }
    .time-warm { color: #ea580c; font-weight: 700; }
    .time-normal { color: #64748b; }
</style>
""", unsafe_allow_html=True)

# === TITLE ===
st.markdown("""
<div class="header-container">
    <h1 class="main-title">🌐 Global Telecom & OTT Stellar Nexus</h1>
    <p class="subtitle">Real-time Competitive Intelligence Dashboard</p>
</div>
""", unsafe_allow_html=True)

# === RSS FEEDS – NOW WITH 4 PRIORITY TELCO SOURCES ===
RSS_FEEDS = [
    # Regular Telco
    ("Telecoms.com", "https://www.telecoms.com/feed"),
    ("Light Reading", "https://www.lightreading.com/rss/simple"),
    ("Fierce Telecom", "https://www.fierce-network.com/rss.xml"),
    ("RCR Wireless", "https://www.rcrwireless.com/feed"),
    ("Mobile World Live", "https://www.mobileworldlive.com/feed/"),
    ("ET Telecom", "https://telecom.economictimes.indiatimes.com/rss/topstories"),
    ("Subex News", "https://rss.app/feeds/nBo6830ABe1HTZ5u.xml"),
    ("OSS/BSS News", "https://rss.app/feeds/OXf4iibABnDj7t1l.xml"),
    ("The Fast Mode", "https://www.thefastmode.com/rss-feeds"),  # Added reliable OSS/BSS-rich feed

    # Priority Telco sources – now 4, always pinned at top (latest first)
    ("Netcracker", "https://rss.app/feeds/GxJESz3Wl0PRbyFG.xml"),
    ("Ericsson", "https://rss.app/feeds/Z6HUnDFle57Uu0hU.xml"),
    ("Telecom TV", "https://rss.app/feeds/4OeTYFrRAw7YjI6B.xml"),
    ("Amdocs", "https://rss.app/feeds/E9xROIQmdwZQP7YN.xml"),  # New 4th priority source

    # OTT Business-focused (more feeds for richer content)
    ("Variety Business", "https://variety.com/varietyvip/business/feed/"),
    ("Hollywood Reporter Business", "https://www.hollywoodreporter.com/c/business/feed/"),
    ("Deadline Business", "https://deadline.com/vip/business/feed/"),
    ("Digital TV Europe", "https://www.digitaltveurope.com/feed/"),
    ("Advanced Television", "https://advanced-television.com/feed/"),
    ("Streaming Media", "https://www.streamingmedia.com/rss"),
    ("Netflix Press Releases", "https://ir.netflix.net/resources/rss-feeds/press-releases/rss.xml"),
    ("VideoNuze", "https://www.videonuze.com/atom"),
    ("nScreenMedia", "https://nscreenmedia.com/feed/"),
    ("Fierce Video", "https://www.streamtvinsider.com/fiercevideocom/rss-feeds"),  # Main feed link

    # Sports & Technology unchanged
    # ...
]

# Now 4 priority sources
PRIORITY_SOURCES = ["Netcracker", "Ericsson", "Telecom TV", "Amdocs"]

# === NO PRIORITY HIGHLIGHTING – ALL CARDS UNIFORM ===
# Removed news-card-priority class entirely – all use .news-card

# (Rest of the code – filters, fetch_feed, load_feeds, render_body – unchanged except:
# In render_body: always use card_class = "news-card"

def render_body(items):
    cards = ""
    for item in items:
        time_str, time_class = get_time_str(item["pub"])
        safe_title = html.escape(item["title"])
        safe_link = html.escape(item["link"])
        safe_source = html.escape(item["source"])
        
        # Uniform styling for all
        card_class = "news-card"
        
        cards += f'''<div class="{card_class}">
<a href="{safe_link}" target="_blank" class="news-title">{safe_title}</a>
<div class="news-meta">
<span class="{time_class}">{time_str}</span>
<span>•</span>
<span>{safe_source}</span>
</div>
</div>'''
    
    if not items or not cards:
        cards = '<div style="text-align:center;color:#64748b;padding:70px;font-size:1rem;">No recent news</div>'
    
    return f'<div class="col-body">{cards}</div>'

# In load_feeds: priority pinning logic updated for 4 sources (same as before, just longer list)

# === LOADING & DASHBOARD RENDER (unchanged) ===
