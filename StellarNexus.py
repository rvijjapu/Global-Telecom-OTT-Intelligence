import streamlit as st
import feedparser
import requests
import html
import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# ══════════════════════════════════════════════════════════════════════════════
# AI INTELLIGENCE & ANALYSIS LOGIC
# ══════════════════════════════════════════════════════════════════════════════

# Target Intelligence Profile (Evergent Focused)
INTEL_PROFILE = {
    "COMPETITORS": ["amdocs", "netcracker", "csg", "matrixx", "optiva", "cerillion", "tecnomen", "tecnotree"],
    "CLIENTS": ["astro", "sony", "sonyliv", "sky nz", "sky uk", "nba", "at&t", "directv", "mbc", "shahid", "britbox"],
    "KEYWORDS": ["bss", "oss", "monetization", "billing", "churn", "revenue management", "agentic ai", "saas"]
}

def analyze_impact(title, summary):
    """Simulates AI Analysis for the CEO"""
    text = (title + " " + (summary or "")).lower()
    impact_statement = ""
    score = 0
    
    # Check Competitor Threat
    for comp in INTEL_PROFILE["COMPETITORS"]:
        if comp in text:
            score += 50
            impact_statement = f"⚠️ HIGH THREAT: Direct competitor {comp.capitalize()} activity detected in the BSS/OSS stack."
    
    # Check Client Opportunity
    for client in INTEL_PROFILE["CLIENTS"]:
        if client in text:
            score += 60
            impact_statement = f"💎 CLIENT SIGNAL: Potential upsell or churn risk detected for {client.upper()}."

    # General Industry Shift
    if not impact_statement:
        for kw in INTEL_PROFILE["KEYWORDS"]:
            if kw in text:
                score += 20
                impact_statement = f"⚡ MARKET SHIFT: Dynamics in {kw} suggest a strategic pivot point."
                break
    
    return score, impact_statement or "Market monitoring update."

# ══════════════════════════════════════════════════════════════════════════════
# DYNAMIC DATA & UI ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def render_news_column(items):
    """Renders cards with AI Summarization"""
    cards_html = ""
    # Filter for quality and sort by AI Score
    scored_items = []
    for item in items:
        score, impact = analyze_impact(item['title'], item.get('summary', ''))
        item['score'] = score
        item['impact'] = impact
        scored_items.append(item)
    
    # Sort: Highest AI Impact first
    scored_items.sort(key=lambda x: x['score'], reverse=True)

    for item in scored_items[:8]: # Top 8 signals per column
        is_high_signal = item['score'] >= 50
        card_style = "border-left: 5px solid #f59e0b; background: #fffbeb;" if is_high_signal else "background: #ffffff;"
        badge = '<span style="color:#d97706; font-weight:bold; font-size:10px;">🔥 CRITICAL SIGNAL</span>' if is_high_signal else ""
        
        cards_html += f"""
        <div style="padding: 15px; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); {card_style}">
            {badge}
            <a href="{item['link']}" target="_blank" style="text-decoration:none; color:#1e3a8a; font-weight:700; font-size:0.95rem;">{item['title']}</a>
            <div style="font-size: 0.8rem; color: #64748b; margin: 8px 0;">{item['source']} • {item['pub'].strftime('%H:%M')}</div>
            <div style="background: rgba(0,0,0,0.03); padding: 8px; border-radius: 6px; font-size: 0.85rem; color: #334155; border-top: 1px solid rgba(0,0,0,0.05);">
                <strong>AI ANALYSIS:</strong> {item['impact']}
            </div>
        </div>
        """
    return cards_html

# ... (Standard feed fetching logic from your previous imports) ...
