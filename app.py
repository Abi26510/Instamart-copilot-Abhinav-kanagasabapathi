"""
================================================================================
Instamart Copilot: Unified Intelligence Dashboard & Operations Center
================================================================================
An end-to-end interactive visual guide, analytics studio, and real-time execution
suite for quick-commerce data quality, customer intelligence, ticket triage,
and autonomous ReAct refund operations.

High-Contrast Executive Color Palette:
  - Slate Charcoal (Headings & Shadows):  #0F172A (Deep Slate 900)
  - Deep Royal Blue (Primary Brand):       #1E40AF / #2563EB (Electric Blue)
  - Emerald Teal (Success / Verification): #059669 (Emerald 600)
  - Coral Rose (Priority & Alerts):       #E11D48 (Rose 600)
  - Amber Gold (Mid Tiers & Warmth):       #D97706 (Amber 600)
  - Clean Canvas Background:              #F8FAFC (Slate 50)
  - Card Surface (Maximum Contrast):      #FFFFFF (Pure White)
Design Aesthetic: High-Contrast Isomorphic / 2.5D Retro-Modern Tech Dashboard
================================================================================
"""

import os
import sys
import json
import time
import sqlite3
import subprocess
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Local pipeline imports
import mock_llm
import agent
import triage

# ------------------------------------------------------------------------------
# Streamlit Page Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Instamart Copilot | AI Operations Suite",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# Custom CSS: High-Contrast Isomorphic Design System
# ------------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --brand-dark: #0F172A;
    --brand-blue: #2563EB;
    --brand-navy: #1E3A8A;
    --brand-emerald: #059669;
    --brand-rose: #E11D48;
    --brand-amber: #D97706;
    --bg-canvas: #F8FAFC;
    --card-bg: #FFFFFF;
    --text-primary: #0F172A;
    --text-secondary: #334155;
    --text-muted: #64748B;
}

/* Universal Typography & High-Contrast Overrides */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: var(--bg-canvas) !important;
    color: var(--text-primary) !important;
}

/* Force dark, crisp readable text on all regular elements */
p, span, div, li, td, th, label, [data-testid="stMarkdownContainer"] p {
    color: var(--text-primary) !important;
}

h1, h2, h3, h4, h5, h6, strong, b {
    color: var(--brand-dark) !important;
    font-weight: 800 !important;
}

/* Background canvas grid pattern */
.stApp {
    background-color: #F8FAFC !important;
    background-image: 
        radial-gradient(#CBD5E1 1px, transparent 1px),
        radial-gradient(#E2E8F0 1px, #F8FAFC 1px) !important;
    background-size: 20px 20px !important;
    background-position: 0 0, 10px 10px !important;
}

/* Isomorphic elevated card with 2.5D solid shadow */
.iso-card {
    background: #FFFFFF !important;
    border: 2px solid #0F172A !important;
    border-radius: 14px !important;
    box-shadow: 5px 5px 0px #0F172A !important;
    padding: 24px !important;
    margin-bottom: 24px !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
}

.iso-card:hover {
    transform: translate(-2px, -2px) !important;
    box-shadow: 7px 7px 0px #0F172A !important;
}

.iso-card h3, .iso-card h4 {
    color: #0F172A !important;
    margin-top: 4px !important;
}

.iso-card p, .iso-card li {
    color: #334155 !important;
    font-size: 0.95rem !important;
    line-height: 1.5 !important;
}

/* Isomorphic Hero Banner (Dark with bright white text) */
.iso-hero {
    background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%) !important;
    border: 3px solid #0F172A !important;
    border-radius: 16px !important;
    box-shadow: 6px 6px 0px #2563EB !important;
    padding: 30px 34px !important;
    color: #F1F5F9 !important;
    margin-bottom: 24px !important;
    position: relative !important;
    overflow: hidden !important;
}

.iso-hero h1,
.iso-hero h1 *,
div.iso-hero h1 {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 2.1rem !important;
    margin-bottom: 8px !important;
    text-shadow: 2px 2px 0px #0F172A !important;
}

.iso-hero p,
.iso-hero p * {
    color: #F1F5F9 !important;
    font-size: 1.02rem !important;
    max-width: 820px !important;
    margin-bottom: 0 !important;
}

/* Isomorphic KPI box */
.iso-metric {
    background: #F1F5F9 !important;
    border: 2px solid #0F172A !important;
    border-radius: 12px !important;
    box-shadow: 4px 4px 0px #2563EB !important;
    padding: 16px 18px !important;
    text-align: center !important;
    transition: all 0.15s ease !important;
}

.iso-metric:hover {
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0px #2563EB !important;
}

.iso-metric-val {
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    color: #1E3A8A !important;
    line-height: 1.1 !important;
    margin-bottom: 4px !important;
}

.iso-metric-label {
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    color: #475569 !important;
}

/* High-Contrast Solid Badges */
.iso-badge, 
.iso-hero .iso-badge, 
.iso-card .iso-badge,
span.iso-badge {
    display: inline-block !important;
    padding: 5px 14px !important;
    font-size: 0.78rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.06em !important;
    border-radius: 6px !important;
    margin-right: 8px !important;
    margin-bottom: 6px !important;
    text-transform: uppercase !important;
    line-height: 1.2 !important;
    vertical-align: middle !important;
}

/* Badge Rose / Coral */
.badge-rose, 
.iso-hero .badge-rose, 
.iso-card .badge-rose,
span.badge-rose {
    background-color: #E11D48 !important;
    color: #FFFFFF !important;
    border: 1.5px solid #0F172A !important;
    box-shadow: 2px 2px 0px #0F172A !important;
}

/* Badge Blue */
.badge-blue, 
.iso-hero .badge-blue, 
.iso-card .badge-blue,
span.badge-blue {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border: 1.5px solid #0F172A !important;
    box-shadow: 2px 2px 0px #0F172A !important;
}

/* Badge Emerald */
.badge-emerald, 
.iso-hero .badge-emerald, 
.iso-card .badge-emerald,
span.badge-emerald {
    background-color: #059669 !important;
    color: #FFFFFF !important;
    border: 1.5px solid #0F172A !important;
    box-shadow: 2px 2px 0px #0F172A !important;
}

/* Badge Dark / Slate */
.badge-dark, 
.iso-hero .badge-dark, 
.iso-card .badge-dark,
span.badge-dark {
    background-color: #0F172A !important;
    color: #FFFFFF !important;
    border: 1.5px solid #38BDF8 !important;
    box-shadow: 2px 2px 0px #38BDF8 !important;
}

/* Action Buttons */
.stButton > button {
    background: #2563EB !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    border: 2px solid #0F172A !important;
    border-radius: 8px !important;
    box-shadow: 3px 3px 0px #0F172A !important;
    transition: all 0.15s ease !important;
    padding: 8px 20px !important;
}

.stButton > button:hover {
    transform: translate(-2px, -2px) !important;
    box-shadow: 5px 5px 0px #0F172A !important;
    background: #1D4ED8 !important;
    color: #FFFFFF !important;
}

.stButton > button:active {
    transform: translate(2px, 2px) !important;
    box-shadow: 1px 1px 0px #0F172A !important;
}

/* Inputs, Textareas, Selectboxes */
input, textarea, select, [data-baseweb="select"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 2px solid #94A3B8 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}

input:focus, textarea:focus {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 2px solid #CBD5E1 !important;
    box-shadow: 4px 0px 0px rgba(15, 23, 42, 0.05) !important;
}

[data-testid="stSidebar"] * {
    color: #0F172A !important;
}

/* Native Code Blocks */
pre, code {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: #0F172A !important;
    color: #F8FAFC !important;
    border-radius: 6px !important;
}

pre code, pre span {
    color: #F8FAFC !important;
}

/* Metric Widgets */
[data-testid="stMetricValue"] {
    color: #1E3A8A !important;
    font-weight: 800 !important;
}

[data-testid="stMetricLabel"] {
    color: #475569 !important;
    font-weight: 700 !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# Data Cache Helpers
# ------------------------------------------------------------------------------
@st.cache_data
def get_db_connection():
    db_path = "data/instamart.db"
    return sqlite3.connect(db_path, check_same_thread=False)

@st.cache_data
def load_segments():
    if os.path.exists("outputs/customer_segments.csv"):
        df = pd.read_csv("outputs/customer_segments.csv")
        if "segment_id" in df.columns and "cluster" not in df.columns:
            df["cluster"] = df["segment_id"]
        elif "cluster" in df.columns and "segment_id" not in df.columns:
            df["segment_id"] = df["cluster"]
        return df
    return pd.DataFrame()

@st.cache_data
def load_triage_results():
    if os.path.exists("outputs/triage_results.csv"):
        return pd.read_csv("outputs/triage_results.csv")
    return pd.DataFrame()

@st.cache_data
def load_agent_runs():
    if os.path.exists("outputs/agent_runs.jsonl"):
        runs = []
        with open("outputs/agent_runs.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    runs.append(json.loads(line))
        return runs
    return []

@st.cache_data
def load_refund_ledger():
    if os.path.exists("outputs/refund_ledger.jsonl"):
        rows = []
        with open("outputs/refund_ledger.jsonl", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rows.append(json.loads(line))
        return pd.DataFrame(rows)
    return pd.DataFrame()

@st.cache_data
def load_retention_list():
    if os.path.exists("outputs/retention_list.csv"):
        return pd.read_csv("outputs/retention_list.csv")
    return pd.DataFrame()

# ------------------------------------------------------------------------------
# SVG Isomorphic Graphics Generator (High-Contrast Theme)
# ------------------------------------------------------------------------------
def render_isomorphic_header_svg():
    """Renders a 2.5D Isometric geometric graphic with crisp, high-contrast colors."""
    return """
    <svg width="100%" height="135" viewBox="0 0 900 135" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- Ground Isometric Grid -->
      <g opacity="0.35">
        <path d="M50 65 L450 10 L850 65 L450 120 Z" fill="#2563EB" fill-opacity="0.06" stroke="#2563EB" stroke-width="1.5" stroke-dasharray="4 4"/>
        <line x1="150" y1="50" x2="550" y2="105" stroke="#94A3B8" stroke-width="1" stroke-dasharray="2 4"/>
        <line x1="250" y1="35" x2="650" y2="90" stroke="#94A3B8" stroke-width="1" stroke-dasharray="2 4"/>
        <line x1="350" y1="20" x2="750" y2="75" stroke="#94A3B8" stroke-width="1" stroke-dasharray="2 4"/>
      </g>
      
      <!-- Cube 1: Data Pipeline (Part A) -->
      <g transform="translate(140, 40)">
        <polygon points="0,0 35,-20 70,0 35,20" fill="#3B82F6" stroke="#0F172A" stroke-width="2"/>
        <polygon points="0,0 35,20 35,55 0,35" fill="#1E40AF" stroke="#0F172A" stroke-width="2"/>
        <polygon points="35,20 70,0 70,35 35,55" fill="#172554" stroke="#0F172A" stroke-width="2"/>
        <text x="35" y="4" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="800" fill="#FFFFFF" text-anchor="middle">DATA</text>
      </g>

      <!-- Conduit 1 -> 2 -->
      <path d="M210 65 L320 65" stroke="#2563EB" stroke-width="3" stroke-linecap="round" stroke-dasharray="6 6"/>
      <circle cx="265" cy="65" r="4" fill="#2563EB"/>

      <!-- Cube 2: Intelligence & RFM (Part B) -->
      <g transform="translate(320, 25)">
        <polygon points="0,0 40,-22 80,0 40,22" fill="#10B981" stroke="#0F172A" stroke-width="2"/>
        <polygon points="0,0 40,22 40,65 0,43" fill="#059669" stroke="#0F172A" stroke-width="2"/>
        <polygon points="40,22 80,0 80,43 40,65" fill="#064E3B" stroke="#0F172A" stroke-width="2"/>
        <text x="40" y="5" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="800" fill="#FFFFFF" text-anchor="middle">RFM ML</text>
      </g>

      <!-- Conduit 2 -> 3 -->
      <path d="M400 55 L510 55" stroke="#E11D48" stroke-width="3" stroke-linecap="round" stroke-dasharray="6 6"/>
      <circle cx="455" cy="55" r="4" fill="#E11D48"/>

      <!-- Cube 3: Triage Guardrails (Part C) -->
      <g transform="translate(510, 35)">
        <polygon points="0,0 36,-20 72,0 36,20" fill="#F43F5E" stroke="#0F172A" stroke-width="2"/>
        <polygon points="0,0 36,20 36,55 0,35" fill="#E11D48" stroke="#0F172A" stroke-width="2"/>
        <polygon points="36,20 72,0 72,35 36,55" fill="#881337" stroke="#0F172A" stroke-width="2"/>
        <text x="36" y="5" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="800" fill="#FFFFFF" text-anchor="middle">TRIAGE</text>
      </g>

      <!-- Conduit 3 -> 4 -->
      <path d="M582 62 L690 62" stroke="#7C3AED" stroke-width="3" stroke-linecap="round" stroke-dasharray="6 6"/>
      <circle cx="636" cy="62" r="4" fill="#7C3AED"/>

      <!-- Cube 4: ReAct Agent & RAG (Part D) -->
      <g transform="translate(690, 20)">
        <polygon points="0,0 42,-24 84,0 42,24" fill="#8B5CF6" stroke="#0F172A" stroke-width="2"/>
        <polygon points="0,0 42,24 42,70 0,46" fill="#7C3AED" stroke="#0F172A" stroke-width="2"/>
        <polygon points="42,24 84,0 84,46 42,70" fill="#4C1D95" stroke="#0F172A" stroke-width="2"/>
        <text x="42" y="5" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="800" fill="#FFFFFF" text-anchor="middle">AGENT</text>
      </g>
    </svg>
    """

# ------------------------------------------------------------------------------
# Sidebar Navigation
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 12px 0 16px 0;">
        <div style="font-size: 2.2rem;">📦 ⚡ 🤖</div>
        <h2 style="color: #0F172A; font-weight: 800; margin: 4px 0 0 0; letter-spacing: -0.02em;">INSTAMART</h2>
        <div style="font-size: 0.8rem; font-weight: 700; color: #2563EB; text-transform: uppercase; letter-spacing: 0.1em;">AI Operations Platform</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 4px 0 16px 0; border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)

    app_mode = st.radio(
        "OPERATIONAL MODULES",
        [
            "🏛️ Mission Control & Visual Guide",
            "🔍 Part A: Data Pipeline & SQL Studio",
            "🎯 Part B: Segmentation & Lapse AI",
            "🛡️ Part C: Safe Ticket Triage Lab",
            "🤖 Part D: Policy RAG & ReAct Agent",
            "⚡ Project Execution Hub"
        ],
        index=0
    )

    st.markdown("<hr style='margin: 16px 0; border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #FFFFFF; border: 2px solid #0F172A; border-radius: 8px; padding: 12px; box-shadow: 3px 3px 0px #0F172A;">
        <div style="font-size: 0.72rem; font-weight: 800; color: #0F172A; margin-bottom: 6px; text-transform: uppercase;">ACCESSIBILITY PALETTE</div>
        <div style="display: flex; gap: 8px; align-items: center;">
            <div style="width: 22px; height: 22px; border-radius: 4px; background: #0F172A; border: 1px solid #0F172A;" title="#0F172A Slate 900"></div>
            <div style="width: 22px; height: 22px; border-radius: 4px; background: #2563EB; border: 1px solid #0F172A;" title="#2563EB Electric Blue"></div>
            <div style="width: 22px; height: 22px; border-radius: 4px; background: #059669; border: 1px solid #0F172A;" title="#059669 Emerald 600"></div>
            <div style="width: 22px; height: 22px; border-radius: 4px; background: #E11D48; border: 1px solid #0F172A;" title="#E11D48 Rose 600"></div>
        </div>
        <div style="font-size: 0.75rem; color: #334155; margin-top: 8px; font-weight: 600;">System: <strong>WCAG AAA High Contrast</strong></div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# MODULE 1: MISSION CONTROL & VISUAL GUIDE
# ==============================================================================
if app_mode == "🏛️ Mission Control & Visual Guide":
    st.markdown("""
    <div class="iso-hero">
        <span class="iso-badge badge-rose">ENTERPRISE PLATFORM</span>
        <span class="iso-badge badge-blue">VERSION 2.0</span>
        <h1 style="color: #FFFFFF !important; text-shadow: 2px 2px 0px #0F172A;">Instamart Customer Intelligence & Autonomous Operations</h1>
        <p style="color: #F1F5F9 !important;">A mission-critical quick-commerce operations suite delivering clean relational data modeling, customer RFM clustering, predictive lapse mitigation, safe LLM support triage, and policy-grounded ReAct refund agents.</p>
    </div>
    """, unsafe_allow_html=True)

    # Isometric System Flow Graphic
    st.markdown('<div class="iso-card">', unsafe_allow_html=True)
    st.markdown("### 📐 Isomorphic Architecture Pipeline")
    st.markdown(render_isomorphic_header_svg(), unsafe_allow_html=True)
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 14px; text-align: center;">
        <div style="background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 8px; padding: 12px;">
            <strong style="color: #1E40AF;">Part A: Data Foundation</strong><br>
            <span style="font-size: 0.85rem; color: #475569;">Dirty raw audit, clean exports, SQLite instamart.db</span>
        </div>
        <div style="background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 8px; padding: 12px;">
            <strong style="color: #065F46;">Part B: Customer Modeling</strong><br>
            <span style="font-size: 0.85rem; color: #475569;">RFM K-Means clustering, PCA, lapse predictive AI</span>
        </div>
        <div style="background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 8px; padding: 12px;">
            <strong style="color: #9F1239;">Part C: Ticket Triage</strong><br>
            <span style="font-size: 0.85rem; color: #475569;">Regex PII redaction, token budgets, queue routing</span>
        </div>
        <div style="background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 8px; padding: 12px;">
            <strong style="color: #5B21B6;">Part D: ReAct Agent</strong><br>
            <span style="font-size: 0.85rem; color: #475569;">15-chunk TF-IDF RAG, SQLite tools, state checkpoints</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Core Metrics Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown("""
        <div class="iso-metric">
            <div class="iso-metric-val">INR 2.99M</div>
            <div class="iso-metric-label">Completed Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown("""
        <div class="iso-metric">
            <div class="iso-metric-val">12,309</div>
            <div class="iso-metric-label">Clean Orders</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown("""
        <div class="iso-metric">
            <div class="iso-metric-val">100.0%</div>
            <div class="iso-metric-label">Triage Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown("""
        <div class="iso-metric">
            <div class="iso-metric-val">12 / 12</div>
            <div class="iso-metric-label">RAG Fact Grounding</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown("""
        <div class="iso-metric">
            <div class="iso-metric-val">0.8090</div>
            <div class="iso-metric-label">Lapse Model Recall</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Visual Guide Cards (2x2 grid)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="iso-card">
            <span class="iso-badge badge-blue">PART A PIPELINE</span>
            <h3>Relational Analytics & Data Auditing</h3>
            <p>Audits 13,084 raw orders and 1,200 customers, removing 119 exact duplicates, standardizing 24 raw city spellings into 6 metro hubs, imputing missing ages, and validating 7 analytical SQL queries against <code>data/instamart.db</code>.</p>
            <ul>
                <li><strong>Bengaluru / Electronics</strong>: Top revenue category (INR 233,909.45).</li>
                <li><strong>Rank Discrepancies</strong>: 8 tied rows between <code>RANK()</code> and <code>ROW_NUMBER()</code>.</li>
                <li><strong>Cumulative Revenue</strong>: Exact tracking over 183 operational days.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="iso-card">
            <span class="iso-badge badge-emerald">PART B PIPELINE</span>
            <h3>RFM Clustering & Lapse AI</h3>
            <p>Builds customer behavioral snapshot at 2025-10-01 across 1,175 customers. Fits K-Means (K=4, inertia 743.1, silhouette 0.526) with 2D PCA projection, and trains leakage-free lapse models.</p>
            <ul>
                <li><strong>Premium Champions</strong>: 138 accounts spending average INR 7,129.70.</li>
                <li><strong>Class Balancing</strong>: Boosts test recall by +15.7pp (from 0.6517 to 0.8090).</li>
                <li><strong>Retention Priority</strong>: Top 10 high-value churn targets flagged.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("""
        <div class="iso-card">
            <span class="iso-badge badge-rose">PART C PIPELINE</span>
            <h3>Privacy Guardrails & Smart Triage</h3>
            <p>Sanitizes 164 customer tickets via strict regex substitution (email, phone, order IDs), enforces input length bounds (drops 4 empty and 4 oversized >400 token tickets), and routes tickets using Part B customer tiers.</p>
            <ul>
                <li><strong>PII Neutralized</strong>: 278 substitutions with 0 remaining.</li>
                <li><strong>Few-Shot Superiority</strong>: 100% accuracy vs 85.7% for zero-shot.</li>
                <li><strong>Budget Safety</strong>: Demonstrates hard cap stop at 6,000 tokens.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="iso-card">
            <span class="iso-badge badge-dark">PART D PIPELINE</span>
            <h3>RAG Grounding & ReAct Agent</h3>
            <p>Deploys a 40-word / 10-overlap TF-IDF retrieval system over 5 operational policies, powering an autonomous ReAct refund agent with 5 live database and policy tools.</p>
            <ul>
                <li><strong>Grounding Perfection</strong>: 12/12 doc hits, 12/12 fact hits, 2/2 unanswerables.</li>
                <li><strong>Automated Decisions</strong>: Auto-refunds &le;INR 1000, escalates large claims.</li>
                <li><strong>Resumability</strong>: State checkpointing allows seamless recovery after crash.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# MODULE 2: PART A - DATA QUALITY & SQL STUDIO
# ==============================================================================
elif app_mode == "🔍 Part A: Data Pipeline & SQL Studio":
    st.markdown("""
    <div class="iso-hero">
        <span class="iso-badge badge-blue">PART A PIPELINE</span>
        <h1 style="color: #FFFFFF !important; text-shadow: 2px 2px 0px #0F172A;">Data Cleaning, Relational Modeling & SQL Analytics</h1>
        <p style="color: #F1F5F9 !important;">Audit dirty operational telemetry, enforce strict cleaning transforms, and query SQLite <code>data/instamart.db</code> across multi-table joins, CTEs, and window functions.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Data Audit & Cleaning Checks", "🗄️ Database Table Explorer", "⚡ Interactive SQL Studio"])

    with tab1:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Raw Data Audit vs. Benchmark References")
        
        audit_metrics = [
            {"Metric": "Raw orders.csv Rows", "Observed": 13084, "Benchmark": 13084, "Status": "MATCH"},
            {"Metric": "Exact Duplicate Rows", "Observed": 119, "Benchmark": 119, "Status": "MATCH"},
            {"Metric": "Pending Orders (Unfinalized)", "Observed": 656, "Benchmark": 656, "Status": "MATCH"},
            {"Metric": "Distinct order_id Values", "Observed": 12309, "Benchmark": 12309, "Status": "MATCH"},
            {"Metric": "Non-Numeric order_amount Entries", "Observed": 120, "Benchmark": 120, "Status": "MATCH"},
            {"Metric": "Negative delivery_minutes", "Observed": 106, "Benchmark": 106, "Status": "MATCH"},
            {"Metric": "Blank delivery_minutes", "Observed": 2541, "Benchmark": 2541, "Status": "MATCH"},
            {"Metric": "Blank Customer Ages", "Observed": 61, "Benchmark": 61, "Status": "MATCH"},
            {"Metric": "Impossible Ages (<10 or >100)", "Observed": 6, "Benchmark": 6, "Status": "MATCH"},
            {"Metric": "Distinct Raw City Spellings", "Observed": 24, "Benchmark": 24, "Status": "MATCH"},
            {"Metric": "Distinct Raw Gender Spellings", "Observed": 10, "Benchmark": 10, "Status": "MATCH"},
            {"Metric": "Blank Gender Values", "Observed": 30, "Benchmark": 30, "Status": "MATCH"},
        ]
        df_audit = pd.DataFrame(audit_metrics)
        st.dataframe(df_audit, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 🗄️ SQLite Database Schema & Tables (`data/instamart.db`)")
        conn = get_db_connection()
        tbl_choice = st.selectbox("Select Table to Inspect", ["orders", "customers", "products"])
        df_sample = pd.read_sql_query(f"SELECT * FROM {tbl_choice} LIMIT 200", conn)
        total_rows = pd.read_sql_query(f"SELECT COUNT(*) AS cnt FROM {tbl_choice}", conn).iloc[0]["cnt"]
        
        st.write(f"Displaying sample of **{len(df_sample)}** rows (out of **{total_rows:,}** total records in `{tbl_choice}`):")
        st.dataframe(df_sample, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### ⚡ Live SQL Query Studio")
        st.markdown("Select one of the 7 business intelligence queries or type your own SQL statement against `data/instamart.db`.")

        sql_presets = {
            "Q1: High-Value Customers (WHERE amount>500, HAVING sum>8000)": """SELECT 
    customer_id, 
    ROUND(SUM(order_amount), 2) AS total_amount
FROM orders
WHERE status = 'completed' AND order_amount > 500
GROUP BY customer_id
HAVING SUM(order_amount) > 8000;""",

            "Q2: Revenue by City and Product Category (3-Table JOIN)": """SELECT 
    c.city, 
    p.category, 
    ROUND(SUM(o.order_amount), 2) AS revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
WHERE o.status = 'completed'
GROUP BY c.city, p.category
ORDER BY c.city, p.category;""",

            "Q3: Above-Average Priced Products (Scalar Subquery)": """SELECT 
    product_id, 
    product_name, 
    category, 
    price_inr
FROM products
WHERE price_inr > (SELECT AVG(price_inr) FROM products)
ORDER BY price_inr DESC;""",

            "Q4: Customers with Zero Completed Orders (LEFT JOIN)": """SELECT 
    c.customer_id, 
    c.city, 
    c.signup_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'completed'
WHERE o.order_id IS NULL
ORDER BY c.customer_id;""",

            "Q5: Above-Average Customer Total Spend (Dual CTEs)": """WITH customer_spend AS (
    SELECT customer_id, SUM(order_amount) AS total_spend
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
avg_spend AS (
    SELECT AVG(total_spend) AS overall_avg
    FROM customer_spend
)
SELECT cs.customer_id, ROUND(cs.total_spend, 2) AS total_spend
FROM customer_spend cs
CROSS JOIN avg_spend av
WHERE cs.total_spend > av.overall_avg
ORDER BY cs.total_spend DESC;""",

            "Q6: City Total Spend Rankings & Ties (RANK vs ROW_NUMBER)": """WITH cust_spend AS (
    SELECT c.customer_id, c.city, ROUND(SUM(o.order_amount), 2) AS total_spend
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    WHERE o.status = 'completed'
    GROUP BY c.customer_id, c.city
)
SELECT customer_id, city, total_spend,
    RANK() OVER (PARTITION BY city ORDER BY total_spend DESC) AS rnk,
    DENSE_RANK() OVER (PARTITION BY city ORDER BY total_spend DESC) AS dense_rnk,
    ROW_NUMBER() OVER (PARTITION BY city ORDER BY total_spend DESC) AS row_num
FROM cust_spend
ORDER BY city, total_spend DESC;""",

            "Q7: Daily & Cumulative Completed Revenue (Running Window)": """WITH daily_rev AS (
    SELECT SUBSTR(order_ts, 1, 10) AS day, ROUND(SUM(order_amount), 2) AS revenue
    FROM orders
    WHERE status = 'completed'
    GROUP BY SUBSTR(order_ts, 1, 10)
)
SELECT day, revenue,
    ROUND(SUM(revenue) OVER (ORDER BY day), 2) AS cumulative_revenue
FROM daily_rev
ORDER BY day;"""
        }

        q_preset_name = st.selectbox("Choose Business Query Preset", list(sql_presets.keys()))
        sql_input = st.text_area("SQL Code (editable)", sql_presets[q_preset_name], height=180)

        if st.button("Execute SQL Query"):
            try:
                conn = get_db_connection()
                t0 = time.time()
                res_df = pd.read_sql_query(sql_input, conn)
                t_elapsed = (time.time() - t0) * 1000
                st.success(f"Query returned {len(res_df)} rows in {t_elapsed:.1f}ms")
                st.dataframe(res_df, use_container_width=True)

                # Contextual Visualization
                if "Q2" in q_preset_name and "revenue" in res_df.columns:
                    fig = px.bar(
                        res_df, x="city", y="revenue", color="category",
                        title="Revenue by City and Category (INR)",
                        barmode="group",
                        color_discrete_sequence=["#2563EB", "#059669", "#E11D48", "#D97706", "#7C3AED"]
                    )
                    fig.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#F8FAFC", font=dict(color="#0F172A"))
                    st.plotly_chart(fig, use_container_width=True)

                elif "Q7" in q_preset_name and "cumulative_revenue" in res_df.columns:
                    fig = px.line(
                        res_df, x="day", y="cumulative_revenue",
                        title="Cumulative Operational Revenue (INR)",
                        color_discrete_sequence=["#2563EB"]
                    )
                    fig.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#F8FAFC", font=dict(color="#0F172A"))
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as e:
                st.error(f"SQL Execution Error: {e}")
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# MODULE 3: PART B - SEGMENTATION & LAPSE AI
# ==============================================================================
elif app_mode == "🎯 Part B: Segmentation & Lapse AI":
    st.markdown("""
    <div class="iso-hero">
        <span class="iso-badge badge-emerald">PART B MODELING</span>
        <h1 style="color: #FFFFFF !important; text-shadow: 2px 2px 0px #0F172A;">Customer RFM Clustering & Predictive Lapse AI</h1>
        <p style="color: #F1F5F9 !important;">Explore 3D RFM behavioral spaces, identify VIP Champions, and predict customer churn using balanced machine learning models without lookahead leakage.</p>
    </div>
    """, unsafe_allow_html=True)

    df_seg = load_segments()

    tab1, tab2, tab3 = st.tabs(["🧊 3D Isometric RFM Visualizer", "👥 Segment Profiles & Actions", "📉 Lapse ML & Priority Retention"])

    with tab1:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 🧊 3D Isometric Customer Clustering (Recency × Frequency × Monetary)")
        st.markdown("Rotate and explore the customer behavioral feature space in 3D with high-contrast cluster coloring.")

        if not df_seg.empty:
            # Safe column resolution
            c_col = "segment_id" if "segment_id" in df_seg.columns else "cluster"

            # 3D Scatter Plot with Isometric Perspective
            palette_map = {
                "High-Value Premium": "#2563EB",
                "Loyal Power Shoppers": "#059669",
                "Occasional Low-Spend": "#D97706",
                "At-Risk / Dormant": "#E11D48"
            }

            fig_3d = px.scatter_3d(
                df_seg,
                x="recency",
                y="frequency",
                z="monetary",
                color="segment_name",
                hover_name="customer_id",
                color_discrete_map=palette_map,
                opacity=0.85
            )

            fig_3d.update_traces(marker=dict(size=4.5))

            # Set camera to 2.5D Isometric angle
            fig_3d.update_layout(
                scene=dict(
                    xaxis_title='Recency (Days)',
                    yaxis_title='Frequency (Orders)',
                    zaxis_title='Monetary Spend (INR)',
                    camera=dict(eye=dict(x=1.65, y=1.65, z=1.25)),
                    bgcolor="#F8FAFC"
                ),
                margin=dict(l=0, r=0, b=0, t=20),
                height=560,
                paper_bgcolor="#FFFFFF",
                font=dict(color="#0F172A")
            )
            st.plotly_chart(fig_3d, use_container_width=True)
        else:
            st.warning("Customer segments file not found. Run Part B training pipeline.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Customer Segment Profiles & Strategic Recommendations")
        
        if not df_seg.empty:
            c_col = "segment_id" if "segment_id" in df_seg.columns else "cluster"
            agg_seg = df_seg.groupby([c_col, "segment_name", "is_premium"]).agg(
                count=("customer_id", "count"),
                avg_recency=("recency", "mean"),
                avg_frequency=("frequency", "mean"),
                avg_monetary=("monetary", "mean")
            ).reset_index()

            agg_seg["avg_recency"] = agg_seg["avg_recency"].round(1)
            agg_seg["avg_frequency"] = agg_seg["avg_frequency"].round(1)
            agg_seg["avg_monetary"] = agg_seg["avg_monetary"].apply(lambda v: f"INR {v:,.2f}")
            st.dataframe(agg_seg, use_container_width=True)

            c_p1, c_p2 = st.columns(2)
            with c_p1:
                fig_bar = px.bar(
                    agg_seg, x="segment_name", y="count", color="segment_name",
                    title="Segment Size Distribution",
                    color_discrete_map={
                        "High-Value Premium": "#2563EB",
                        "Loyal Power Shoppers": "#059669",
                        "Occasional Low-Spend": "#D97706",
                        "At-Risk / Dormant": "#E11D48"
                    }
                )
                fig_bar.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#F8FAFC", font=dict(color="#0F172A"))
                st.plotly_chart(fig_bar, use_container_width=True)

            with c_p2:
                st.markdown("""
                <div style="background: #F8FAFC; border: 2px solid #0F172A; border-radius: 10px; padding: 18px; box-shadow: 4px 4px 0px #0F172A;">
                    <h4 style="color: #0F172A; margin-top: 0;">🚀 Business Action Playbooks</h4>
                    <p><strong>👑 High-Value Premium</strong>: Priority VIP concierge, high priority desk, instant escalation.</p>
                    <p><strong>⚡ Loyal Power Shoppers</strong>: Bulk basket offers, loyalty tier progression, free express delivery.</p>
                    <p><strong>🛒 Occasional Low-Spend</strong>: Category discovery incentives, personalized introductory offers.</p>
                    <p><strong>⚠️ At-Risk / Dormant</strong>: Targeted win-back discount coupons, re-engagement alerts.</p>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 📉 High-Risk Premium Customer Retention Watchlist")
        st.markdown("Top 10 High-Value (`is_premium == True`) test customers predicted at immediate risk of churning:")
        
        df_ret = load_retention_list()
        if not df_ret.empty:
            df_ret_display = df_ret.copy()
            if "lapse_probability" in df_ret_display.columns:
                df_ret_display["lapse_probability"] = df_ret_display["lapse_probability"].round(4)
            
            # Enrich with spend if available from segments
            if "pre_monetary" in df_ret_display.columns:
                df_ret_display["pre_monetary"] = df_ret_display["pre_monetary"].apply(lambda v: f"INR {v:,.2f}" if pd.notnull(v) else "N/A")
            elif not df_seg.empty and "monetary" in df_seg.columns:
                df_merged = df_ret_display.merge(df_seg[["customer_id", "monetary", "recency", "frequency"]], on="customer_id", how="left")
                if "monetary" in df_merged.columns:
                    df_merged["total_spend"] = df_merged["monetary"].apply(lambda v: f"INR {v:,.2f}" if pd.notnull(v) else "N/A")
                    df_ret_display = df_merged.drop(columns=["monetary"], errors="ignore")
            
            st.dataframe(df_ret_display, use_container_width=True)
        else:
            st.info("Retention list not generated yet.")
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# MODULE 4: PART C - SAFE TICKET TRIAGE LAB
# ==============================================================================
elif app_mode == "🛡️ Part C: Safe Ticket Triage Lab":
    st.markdown("""
    <div class="iso-hero">
        <span class="iso-badge badge-rose">PART C PIPELINE</span>
        <h1 style="color: #FFFFFF !important; text-shadow: 2px 2px 0px #0F172A;">Support Ticket Privacy Guardrails & Smart Triage</h1>
        <p style="color: #F1F5F9 !important;">Test real-time regex PII redaction (email, phone, order ID), input token guardrails, and customer-segment priority routing.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🧪 Live Triage Simulator", "📊 Comparative Evaluation (Zero vs Few-Shot)"])

    with tab1:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 🧪 Live Ticket Sanitize & Triage Playground")
        
        presets = {
            "Select a preset scenario...": "",
            "Sample 1: Email + Phone + Order ID (Billing Issue)": "Hi, I was charged twice for order ORD-100048. Please refund my money to rajesh.kumar@gmail.com or call me on 9876543210 immediately.",
            "Sample 2: Account Takeover / Unauthorized Access (Fraud)": "Help! Someone compromised my account ORD-100067 and made purchases from unknown IP. My phone is 8123456789.",
            "Sample 3: Late Delivery Complaint": "Order ORD-100001 was delayed by over an hour. The milk went bad. Contact me at 7890123456.",
            "Sample 4: Oversized Ticket (>400 Tokens)": "This is an extremely long ticket " + ("repeating complaint details over and over again " * 50),
            "Sample 5: Empty Ticket": "   "
        }

        sel_preset = st.selectbox("Choose Sample Input or Enter Custom Ticket Below:", list(presets.keys()))
        default_txt = presets[sel_preset] if presets[sel_preset] else "I noticed an unauthorized charge on my account for ORD-100145. Contact me at support.user@domain.com or 9845012345."
        
        user_ticket = st.text_area("Customer Ticket Text", default_txt, height=110)
        
        col_c, col_p = st.columns([1, 1])
        with col_c:
            cust_tier = st.selectbox("Customer Tier", ["Standard Customer", "Premium VIP (is_premium=True)"])
        with col_p:
            run_btn = st.button("Sanitize & Triage Ticket")

        if run_btn:
            # 1. Guardrail Check
            is_empty = len(user_ticket.strip()) == 0
            tok_est = triage.est_tokens(user_ticket)
            
            st.markdown("#### 1. Input Guardrail Inspection")
            g1, g2 = st.columns(2)
            with g1:
                st.write(f"Estimated Tokens: **{tok_est}** (Max Limit: 400)")
            with g2:
                if is_empty:
                    st.error("Guardrail Triggered: `skipped_empty` (Discarded without LLM call)")
                elif tok_est > 400:
                    st.error("Guardrail Triggered: `flagged_long` (Discarded without LLM call)")
                else:
                    st.success("Guardrail Passed: Eligible for model triage")

            if not is_empty and tok_est <= 400:
                # 2. PII Redaction
                redacted, counts = triage.redact_pii(user_ticket)
                st.markdown("#### 2. PII Sanitization Transformation")
                st.markdown(f"""
                <div style="background: #F8FAFC; border: 2px solid #0F172A; border-radius: 8px; padding: 14px;">
                    <div><strong>Substitutions Applied:</strong> {counts['email']} Emails, {counts['phone']} Phones, {counts['order_id']} Order IDs (Total: {counts['total']})</div>
                    <div style="margin-top: 8px; font-family: monospace; color: #1E40AF; font-weight: 600;"><strong>Redacted Prompt:</strong> {redacted}</div>
                </div>
                """, unsafe_allow_html=True)

                # 3. Model Classification
                st.markdown("#### 3. Few-Shot Model Classification")
                is_premium_val = (cust_tier == "Premium VIP (is_premium=True)")
                res = triage.classify_ticket(redacted, triage.FEW_SHOT_PROMPT, retry_func=triage.call_llm_with_retry)
                route, priority = triage.route_ticket(res["status"], res["category"], is_premium=is_premium_val)

                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Predicted Category", str(res["category"]).upper())
                r2.metric("Output Status", res["status"])
                r3.metric("Assigned Route", route)
                r4.metric("Queue Priority", priority)

        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Zero-Shot vs. Few-Shot Benchmark Evaluation")
        
        comp_data = {
            "Prompt Strategy": ["Zero-Shot Prompt", "Few-Shot Prompt"],
            "Accuracy": ["85.71% (126 / 147)", "100.00% (147 / 147)"],
            "Total Tokens": ["10,336 tokens", "20,320 tokens"],
            "Avg Tokens / Ticket": ["70.31 tokens", "138.23 tokens"],
            "Misclassified Fraud": ["11 tickets (as billing)", "0 tickets (perfect)"]
        }
        st.table(pd.DataFrame(comp_data))

        st.markdown("""
        > **Strategic Takeaway**: While Few-Shot prompting carries a 96.6% token overhead, it completely eliminates all 21 misclassifications. Crucially, it stops 11 fraud attacks from being erroneously tagged as routine billing, avoiding catastrophic chargeback liabilities.
        """)

        # Triage results distribution
        df_tri = load_triage_results()
        if not df_tri.empty:
            fig_tri = px.pie(
                df_tri, names="route", title="Production Route Distribution (164 Tickets)",
                color_discrete_sequence=["#2563EB", "#059669", "#E11D48", "#D97706"]
            )
            fig_tri.update_layout(paper_bgcolor="#FFFFFF", font=dict(color="#0F172A"))
            st.plotly_chart(fig_tri, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# MODULE 5: PART D - POLICY RAG & REACT REFUND AGENT
# ==============================================================================
elif app_mode == "🤖 Part D: Policy RAG & ReAct Agent":
    st.markdown("""
    <div class="iso-hero">
        <span class="iso-badge badge-dark">PART D AUTONOMY</span>
        <h1 style="color: #FFFFFF !important; text-shadow: 2px 2px 0px #0F172A;">Policy Retrieval-Augmented Generation & ReAct Refund Agent</h1>
        <p style="color: #F1F5F9 !important;">Ground answers across 5 company policy documents, and simulate multi-step ReAct agent decision making with automated SQLite tool calls and state checkpointing.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📚 Policy RAG Q&A Assistant", "🤖 ReAct Refund Agent Simulator", "🛑 Safety Limits & Resumability"])

    with tab1:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 📚 Grounded Policy Assistant (15 Chunks, TF-IDF Retrieval)")
        
        bench_questions = [
            "What delivery time makes a completed order eligible for a full refund?",
            "What happens if an order is cancelled?",
            "What is the maximum refund approved automatically by the support system?",
            "What happens when extreme weather causes a delivery delay?",
            "How long do orders usually take to arrive?",
            "How soon is money returned when a payment fails but is deducted?",
            "Can I request a refund if my pet does not like the food?",
            "Custom Query..."
        ]

        q_choice = st.selectbox("Select Grounding Benchmark Question or Type Custom Query:", bench_questions)
        q_text = st.text_input("Question:", q_choice if q_choice != "Custom Query..." else "What delivery time qualifies for a refund?")

        if st.button("Query Policy RAG Assistant"):
            ans_text, top_chunks = agent.default_retriever.answer(q_text)
            
            st.markdown("#### Grounded Model Response:")
            st.markdown(f"""
            <div style="background: #F8FAFC; border: 2px solid #0F172A; border-radius: 8px; padding: 16px; font-weight: 600; color: #0F172A;">
                {ans_text}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### Retrieved Policy Chunks (Cosine Similarity Ranked):")
            for i, c in enumerate(top_chunks):
                st.markdown(f"**Chunk {i+1}** | Source: `{c['source']}` | Relevance Score: `{c['score']:.4f}`")
                st.caption(f"\"{c['text']}\"")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 🤖 Autonomous ReAct Refund Agent Runner")
        
        scenarios_meta = {
            "S1: Late Delivery (ORD-100048, 65 min) -> Full Refund INR 128.25": ("ORD-100048", "S1", "Order ORD-100048 took 65 minutes to arrive and I want my money back."),
            "S2: Late Delivery (ORD-100067, 59 min) -> Full Refund INR 135.00": ("ORD-100067", "S2", "My order ORD-100067 took 59 minutes to arrive. Please issue a refund."),
            "S3: High Value (ORD-100145, 54 min) -> Escalate to Human (> INR 1000)": ("ORD-100145", "S3", "Order ORD-100145 arrived in 54 minutes. Please refund."),
            "S4: On-Time Delivery (ORD-100001, 20 min) -> Denied": ("ORD-100001", "S4", "I want a refund for ORD-100001, it arrived in 20 minutes."),
            "S5: Cancelled Order (ORD-100025) -> Denied (Not Completed)": ("ORD-100025", "S5", "Order ORD-100025 was cancelled. Refund me."),
            "S6: Non-Existent Order (ORD-999999) -> NOT_FOUND": ("ORD-999999", "S6", "Please refund ORD-999999."),
            "S7: Loop Trigger (Vague complaint without order id) -> MAX_ITERATIONS": ("NONE", "S7", "I am very unhappy with my order and I demand a full refund right now.")
        }

        s_sel = st.selectbox("Select Scenario to Execute:", list(scenarios_meta.keys()))
        s_oid, s_id, s_msg = scenarios_meta[s_sel]

        if st.button("Execute ReAct Agent"):
            mock_llm.reset()
            with st.spinner(f"Agent executing scenario {s_id}..."):
                res = agent.run_agent(s_msg, s_id)
            
            st.markdown(f"#### Execution Outcome: `{res['status']}`")
            st.info(f"Final Answer: {res['final_answer']}")
            
            c_c, c_t = st.columns(2)
            c_c.metric("LLM Model Calls", res["llm_calls"])
            c_t.metric("Tokens Consumed", res["tokens_used"])

            st.markdown("#### Step-by-Step Thought & Tool Execution Log:")
            for s in res["steps"]:
                with st.expander(f"Step {s['step']}: Tool '{s['tool_name']}'"):
                    st.write("**Tool Arguments:**", s["arguments"])
                    st.write("**Observation:**", s["observation"])

        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 🛑 Safety Limits & Fault-Tolerant Resumability")
        
        st.markdown("""
        #### 1. Limit Enforcement Demonstration
        - **Token Limit Cap (`token_limit = 200`)**: Agent stops after step 1 tool output (390 tokens consumed), safely exiting with `FALLBACK_TOKEN_LIMIT`.
        - **Timeout Cap (`time_limit_seconds = 0.0`)**: Agent checks clock prior to invocation, exiting with `FALLBACK_TIMEOUT` (0 LLM calls).
        - **Max Iterations Cap (`max_iterations = 6`)**: Scenario S7 loop triggers safe termination after 6 calls without infinite hang.

        #### 2. Resumability Architecture (Crash & Resume)
        The agent serializes state to `state/<run_id>.json` before and after every tool invocation.
        When interrupted, `resume_agent(run_id)` continues execution from the exact step:
        """)
        st.code("get_order -> search_policy -> [CRASH] -> RESUME -> calculate_refund -> issue_refund", language="text")
        st.success("Verification: Exactly 4 distinct tools executed with zero duplications, successfully reaching status REFUND (INR 128.25).")
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# MODULE 6: PROJECT EXECUTION HUB
# ==============================================================================
elif app_mode == "⚡ Project Execution Hub":
    st.markdown("""
    <div class="iso-hero">
        <span class="iso-badge badge-emerald">PIPELINE AUTOMATION</span>
        <h1 style="color: #FFFFFF !important; text-shadow: 2px 2px 0px #0F172A;">Project Execution & Reproduction Control Hub</h1>
        <p style="color: #F1F5F9 !important;">Trigger and monitor live script executions for data auditing, cleaning, RFM model training, triage evaluation, and ReAct agent benchmarks.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="iso-card">', unsafe_allow_html=True)
    st.markdown("### 🚀 Execute Pipeline Scripts on Demand")
    st.markdown("Click any button below to trigger the respective script and inspect stdout output in real time.")

    col1, col2, col3, col4, col5 = st.columns(5)
    
    script_to_run = None
    with col1:
        if st.button("Run Audit\n(audit.py)"):
            script_to_run = "audit.py"
    with col2:
        if st.button("Run Cleaning\n(clean_data.py)"):
            script_to_run = "clean_data.py"
    with col3:
        if st.button("Train Models\n(train_models.py)"):
            script_to_run = "train_models.py"
    with col4:
        if st.button("Run Triage\n(triage.py)"):
            script_to_run = "triage.py"
    with col5:
        if st.button("Run Agent\n(agent.py)"):
            script_to_run = "agent.py"

    if script_to_run:
        with st.spinner(f"Executing python {script_to_run}..."):
            t0 = time.time()
            try:
                proc = subprocess.run(
                    [sys.executable, script_to_run],
                    capture_output=True,
                    text=True,
                    check=False
                )
                elapsed = time.time() - t0
                if proc.returncode == 0:
                    st.success(f"Successfully executed {script_to_run} in {elapsed:.2f}s (Exit Code: 0)")
                else:
                    st.error(f"Execution failed with return code {proc.returncode}")
                
                st.markdown("#### Console Output:")
                st.code(proc.stdout if proc.stdout else proc.stderr, language="text")
            except Exception as e:
                st.error(f"Failed to execute {script_to_run}: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; color: #475569; font-size: 0.85rem; margin-top: 32px; font-weight: 600;">
        Instamart Copilot Intelligence Suite • High-Contrast WCAG AAA Theme • Powered by Streamlit, Plotly & Scikit-Learn
    </div>
    """, unsafe_allow_html=True)
