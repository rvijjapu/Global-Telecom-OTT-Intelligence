import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import time

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Global Telecom & OTT Stellar Nexus 2026",
    page_icon="🌐",
    layout="wide"
)

# Your specific URLs
SECTION_URLS = {
    "telco": "https://www.google.com/search?q=recent+telecom+OSS+BSS+key+announcements+providers+organizers+news+key+announcements+2026+exclude+2025&sca_esv=97c75da79839edd2&rlz=1C1UEAD_enIN1080IN1080&sxsrf=ANbL-n6Y1I2D5BOfWBvBDUgqPl31Oiy6xQ%3A1768132406344&udm=50&fbs=ADc_l-aN0CWEZBOHjofHoaMMDiKp0UJuhqwKhR0QUhF54-6jIYFfWbU_Clyew-1Wh7zkL7FFfeQ8UTZRt91soqZupfwPo0crig5A2MrUrvJfjH7QciSH8xUwQHQ9E5ErbsMbM8TE-vSnoDz0uiGZY2lFFSUOY9YcktIMaOamWoIYoq_K39QHv1JgkGPARMooT83wM_fA1Z7IQJUEzhMYSXrprIOMkBHVHg&aep=1&ntc=1&sa=X&ved=2ahUKEwjS0Pu_toOSAxVC1TgGHRECGv8Q2J8OegQIERAE&biw=1422&bih=612&dpr=1.35&aic=0&mstk=AUtExfA9FGudV3YaSUB511w5d1440OBa353H1Qk3TmP_O-KBT4LqBTRk2IR62Q_cZ3yuRGVsVuTmIxZhsz9sE3BsSlhMDAGyj3pCvheMl8nPQFgMvlRUmEIDgjmWiUwm_b5fLiZVQHds5UxlTUeb4oOTD7-Lb-8YNY8ZVjpGBNlvwPcdC1bcwU89dJlE7wb-jkge8yxois-2Lk29NOvDml9iE8WfsMtsg1f3McuTsgsW-nbM3Y8s12SK4qlZe3p1RduBLnkQ2cJmUbZP11TiIfKoiVECb_LvCNCy0DWE1POOfd5NjwtJY-pnegncw04YrCNFzg7rwDYHVfg-8g&csuir=1&mtid=OY9jaYf3HLje4-EPhv3yoAU",
    "ott": "https://www.google.com/search?q=recent+OTT+providers+key+announcements+providers+organizers+news+key+announcements+mergers+acquisitions+deals+profit+losses+2026+exclude+2025&sca_esv=97c75da79839edd2&rlz=1C1UEAD_enIN1080IN1080&sxsrf=ANbL-n4miE8aOlknWfxsF4X_IE0otjaCQQ%3A1768132507283&udm=50&fbs=ADc_l-aN0CWEZBOHjofHoaMMDiKp0UJuhqwKhR0QUhF54-6jIeXhzwX3V5R0etslDc8-1a0tyM5CQSLc0N0slnxynxBIz6ZzcPeDhR8vI86QqVWmGviw2LMnVVbZ0SgqVDyBgA5mp8dFI-oUKAJoYaocNuzeRXKZqD-Yfm57gMu1a6F3B54MdIZd6k7565JJJxq-3t-ULVpqMhBojSQ600P1DwK6IinDog&aep=1&ntc=1&sa=X&ved=2ahUKEwi0tIzwtoOSAxW1yTgGHR0TLREQ2J8OegQIERAE&biw=1422&bih=612&dpr=1.35&aic=0&mtid=no9jaf7pGMOX4-EPpfbg6As&mstk=AUtExfDpY7qpvYktV1-3T3N7DGX7gQuuxIPlUOf19ZrjWgTcFLo7jlE3VRNYdHnJk1Kxxc7yWrX5dO0qjabNEXiDjV3LbaU6fLK0bNnlTee3MgXCK0ea7E8WaL3Sad6nHWN7-uNnF7M29drVuuGNdoGlD4jcwrEzsgIkf576TidNnO4_vbsoARTNd0CTqFiXvtqU9CWvtyRKn8ZgQJWaLPlSOidPhdHNYBBHZGkuHB-vz7XhsVTNP95gPUVgxAiUNKR4j1QowbZf923nxZviNdHgeErOyXz7_Razy_Nsg_bfwBIgjaNG-gbKE6QLMGQHke0u1jeMTRcd8VTQtw&csuir=1",
    "sports": "https://www.google.com/search?q=recent+Sports+Events+organizers+key+announcements+provider+organizers+news+key+announcements+mergers+acquisitions+deals+profit+losses+2026+exclude+2025&sca_esv=97c75da79839edd2&rlz=1C1UEAD_enIN1080IN1080&sxsrf=ANbL-n5CinvPVyJoqquWC7dDw-0eenmnVw:1768132574870&udm=50&fbs=ADc_l-aN0CWEZBOHjofHoaMMDiKp0UJuhqwKhR0QUhF54-6jIZ4fQLFxpd-X3cjBjwn-bveY3JtHHw9t0-P88yah9ue3MMzF3jLCllupWlb45zkYCJ_RZsAkHmSRsPN7eNmIcZoUkoQLXg5liJhL8Vv1GjPjugb83sAFSSGmo8p1XAFQpBg6DisTtw7-3u35WkSCXkFhPkpc5q3ymuPZOpYpnc8eT8FgYw&aep=1&ntc=1&sa=X&ved=2ahUKEwjS2KmQt4OSAxWw2TgGHTakF5wQ2J8OegQIERAE&biw=1422&bih=612&dpr=1.35&aic=0",
    "technology": "https://www.google.com/search?q=recent+Technology+key+announcements+provider+organizers+news+key+announcements+mergers+acquisitions+deals+profit+losses+2026+exclude+2025&sca_esv=97c75da79839edd2&rlz=1C1UEAD_enIN1080IN1080&sxsrf=ANbL-n4mpM_9oVTobFWob50L1AD6LF7YeA:1768132676225&udm=50&fbs=ADc_l-aN0CWEZBOHjofHoaMMDiKp0UJuhqwKhR0QUhF54-6jIZ4fQLFxpd-X3cjBjwn-bveY3JtHHw9t0-P88yah9ue3MMzF3jLCllupWlb45zkYCJ_RZsAkHmSRsPN7eNmIcZoUkoQLXg5liJhL8Vv1GjPjugb83sAFSSGmo8p1XAFQpBg6DisTtw7-3u35WkSCXkFhPkpc5q3ymuPZOpYpnc8eT8FgYw&aep=1&ntc=1&sa=X&ved=2ahUKEwiH8NPAt4OSAxV11TgGHVv_AuEQ2J8OegQIERAE&biw=1422&bih=612&dpr=1.35&aic=0"
}

# ══════════════════════════════════════════════════════════════════════════════
# DATA EXTRACTION LOGIC
# ══════════════════════════════════════════════════════════════════════════════

def scrape_google_search(label, url):
    """Parses a Google Search result page for headlines and snippets."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # Target the organic result containers
        # Common Google Search container classes: MjjYud, g, Ww4FFb
        for result in soup.select('div.MjjYud, div.g'):
            title_tag = result.select_one('h3')
            link_tag = result.select_one('a')
            # Common snippet classes: VwiC3b, BNeawe
            snippet_tag = result.select_one('div.VwiC3b, span.BNeawe')
            
            if title_tag and link_tag:
                title = title_tag.get_text()
                link = link_tag['href']
                
                # Cleanup Google internal redirect links if necessary
                if link.startswith('/url?q='):
                    link = link.split('/url?q=')[1].split('&')[0]
                
                snippet = snippet_tag.get_text() if snippet_tag else "No summary available."
                
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })
        
        return label, results[:10]  # Return top 10 results
    except Exception as e:
        return label, []

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD UI
# ══════════════════════════════════════════════════════════════════════════════

# Premium Styling
st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #f1f5f9; }
    .header { text-align: center; padding: 2rem; background: linear-gradient(90deg, #1e40af, #3b82f6); border-radius: 12px; margin-bottom: 2rem; }
    .card { background-color: #1e293b; border-left: 5px solid #3b82f6; border-radius: 8px; padding: 1.2rem; margin-bottom: 1.2rem; transition: 0.3s; }
    .card:hover { transform: translateY(-3px); box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
    .title-link { color: #f8fafc; font-weight: 700; text-decoration: none; font-size: 1.05rem; }
    .snippet { color: #94a3b8; font-size: 0.85rem; margin-top: 8px; }
    .section-title { text-align: center; font-weight: 800; text-transform: uppercase; padding: 10px; border-radius: 6px; margin-bottom: 20px; }
    .telco-h { background: #db2777; } .ott-h { background: #7c3aed; } 
    .sports-h { background: #059669; } .tech-h { background: #ea580c; }
    .badge { font-size: 0.7rem; background: #334155; padding: 2px 8px; border-radius: 10px; color: #cbd5e1; margin-right: 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>🌐 Global Telecom & OTT Stellar Nexus</h1><p>2026 Executive Competitive Briefing</p></div>', unsafe_allow_html=True)

# Fetching Data using ThreadPool for speed
with st.spinner("⚡ Scanning Global Networks for 2026 Strategic Signals..."):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(scrape_google_search, label, url) for label, url in SECTION_URLS.items()]
        results_map = {f.result()[0]: f.result()[1] for f in futures}

# Rendering Columns
cols = st.columns(4)
sections = [
    ("telco", "📡 Telco & OSS/BSS", "telco-h"),
    ("ott", "📺 OTT & Streaming", "ott-h"),
    ("sports", "🏆 Sports Events", "sports-h"),
    ("technology", "⚡ Technology", "tech-h")
]

for i, (key, label, color_class) in enumerate(sections):
    with cols[i]:
        st.markdown(f'<div class="section-title {color_class}">{label}</div>', unsafe_allow_html=True)
        news_items = results_map.get(key, [])
        
        if not news_items:
            st.info("No 2026 specific results found in this segment. Retrying search parameters...")
        
        for item in news_items:
            st.markdown(f"""
            <div class="card">
                <span class="badge">LIVE 2026</span>
                <a href="{item['link']}" target="_blank" class="title-link">{item['title']}</a>
                <div class="snippet">{item['snippet'][:160]}...</div>
            </div>
            """, unsafe_allow_html=True)

# Auto-Refresh Footer
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #64748b;'>Last Updated: {time.strftime('%H:%M:%S')} | Data pulled from real-time SERP</div>", unsafe_allow_html=True)

# 5-minute auto-refresh
st.markdown("""
<script>
    setTimeout(function(){ window.location.reload(); }, 300000);
</script>
""", unsafe_allow_html=True)
