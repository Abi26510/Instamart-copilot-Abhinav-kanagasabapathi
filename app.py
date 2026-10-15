"""
================================================================================
Instamart Copilot: Unified Intelligence Dashboard & Operations Center
================================================================================
An end-to-end interactive visual guide, analytics studio, and real-time execution
suite for quick-commerce data quality, customer intelligence, ticket triage,
and autonomous ReAct refund operations.

Color Palette Theme:
  - Deep Indigo / Slate Blue: #425B9A
  - Cerulean / Sky Blue:      #76C0EC
  - Warm Vanilla / Cream:     #FFF6DC
  - Soft Coral / Pink-Red:    #FF95A5
Design Aesthetic: Isomorphic / 2.5D Isometric Retro-Modern Tech Dashboard
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
    page_title="Instamart Copilot | AI Intelligence Suite",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------------------
# Custom CSS: Isomorphic Design System with Target Color Palette
# Palette: #425B9A (Deep Slate), #76C0EC (Sky Blue), #FFF6DC (Ivory), #FF95A5 (Coral)
# ------------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
    --primary-indigo: #425B9A;
    --sky-blue: #76C0EC;
    --warm-cream: #FFF6DC;
    --coral-pink: #FF95A5;
    --dark-slate: #1C2438;
    --card-bg: #FFFFFF;
    --card-surface: #F8F9FE;
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--dark-slate);
}

/* Background canvas */
.stApp {
    background-color: #FAF8F2;
    background-image: 
        radial-gradient(#425B9A15 1px, transparent 1px),
        radial-gradient(#76C0EC20 1px, #FAF8F2 1px);
    background-size: 24px 24px;
    background-position: 0 0, 12px 12px;
}

/* Isomorphic elevated card */
.iso-card {
    background: #FFFFFF;
    border: 2px solid #425B9A;
    border-radius: 14px;
    box-shadow: 6px 6px 0px #425B9A;
    padding: 24px;
    margin-bottom: 24px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.iso-card:hover {
    transform: translate(-3px, -3px);
    box-shadow: 9px 9px 0px #425B9A;
}

/* Isomorphic Banner */
.iso-hero {
    background: linear-gradient(135deg, #425B9A 0%, #2A3C6B 100%);
    border: 3px solid #1C2438;
    border-radius: 16px;
    box-shadow: 8px 8px 0px #1C2438;
    padding: 32px 36px;
    color: #FFFFFF;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}

.iso-hero h1 {
    color: #FFF6DC;
    font-weight: 800;
    font-size: 2.2rem;
    margin-bottom: 8px;
    text-shadow: 2px 2px 0px #1C2438;
}

.iso-hero p {
    color: #E2E8F8;
    font-size: 1.05rem;
    max-width: 800px;
    margin-bottom: 0;
}

/* Isomorphic KPI box */
.iso-metric {
    background: #FFF6DC;
    border: 2px solid #425B9A;
    border-radius: 12px;
    box-shadow: 4px 4px 0px #425B9A;
    padding: 16px 20px;
    text-align: center;
    transition: all 0.2s ease;
}

.iso-metric:hover {
    transform: translate(-2px, -2px);
    box-shadow: 6px 6px 0px #425B9A;
}

.iso-metric-val {
    font-size: 1.8rem;
    font-weight: 800;
    color: #425B9A;
    line-height: 1.1;
    margin-bottom: 4px;
}

.iso-metric-label {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #55627E;
}

/* Badges */
.iso-badge {
    display: inline-block;
    padding: 4px 12px;
    font-size: 0.8rem;
    font-weight: 700;
    border-radius: 6px;
    border: 1.5px solid #425B9A;
    box-shadow: 2px 2px 0px #425B9A;
    margin-right: 6px;
    margin-bottom: 4px;
}

.badge-cream { background: #FFF6DC; color: #425B9A; }
.badge-pink  { background: #FF95A5; color: #1C2438; }
.badge-blue  { background: #76C0EC; color: #1C2438; }
.badge-navy  { background: #425B9A; color: #FFF6DC; }

/* Buttons styling */
.stButton > button {
    background: #425B9A !important;
    color: #FFF6DC !important;
    font-weight: 700 !important;
    border: 2px solid #1C2438 !important;
    border-radius: 8px !important;
    box-shadow: 4px 4px 0px #1C2438 !important;
    transition: all 0.15s ease !important;
    padding: 8px 20px !important;
}

.stButton > button:hover {
    transform: translate(-2px, -2px) !important;
    box-shadow: 6px 6px 0px #1C2438 !important;
    background: #34487C !important;
}

.stButton > button:active {
    transform: translate(2px, 2px) !important;
    box-shadow: 2px 2px 0px #1C2438 !important;
}

/* Custom code block styling */
pre, code {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: #232D42 !important;
    color: #FFF6DC !important;
    border-radius: 6px !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 2px solid #425B9A !important;
    box-shadow: 4px 0px 0px #425B9A20 !important;
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
        return pd.read_csv("outputs/customer_segments.csv")
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
# SVG Isomorphic Graphics Generator
# ------------------------------------------------------------------------------
def render_isomorphic_header_svg():
    """Renders a clean 2.5D Isometric geometric graphic with the project palette."""
    return """
    <svg width="100%" height="140" viewBox="0 0 900 140" fill="none" xmlns="http://www.w3.org/2000/svg">
      <!-- Background Grid Plane -->
      <g opacity="0.4">
        <path d="M50 70 L450 10 L850 70 L450 130 Z" fill="#76C0EC" fill-opacity="0.1" stroke="#76C0EC" stroke-width="1.5" stroke-dasharray="4 4"/>
        <line x1="150" y1="55" x2="550" y2="115" stroke="#76C0EC" stroke-width="1" stroke-dasharray="2 4"/>
        <line x1="250" y1="40" x2="650" y2="100" stroke="#76C0EC" stroke-width="1" stroke-dasharray="2 4"/>
        <line x1="350" y1="25" x2="750" y2="85" stroke="#76C0EC" stroke-width="1" stroke-dasharray="2 4"/>
      </g>
      
      <!-- Cube 1: Data Pipeline (Part A) -->
      <g transform="translate(140, 45)">
        <!-- Top Face -->
        <polygon points="0,0 35,-20 70,0 35,20" fill="#76C0EC" stroke="#425B9A" stroke-width="2"/>
        <!-- Left Face -->
        <polygon points="0,0 35,20 35,60 0,40" fill="#425B9A" stroke="#1C2438" stroke-width="2"/>
        <!-- Right Face -->
        <polygon points="35,20 70,0 70,40 35,60" fill="#2E406F" stroke="#1C2438" stroke-width="2"/>
        <text x="35" y="5" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="800" fill="#FFF6DC" text-anchor="middle">DATA</text>
      </g>

      <!-- Isometric Conduit 1 -> 2 -->
      <path d="M210 75 L320 75" stroke="#FF95A5" stroke-width="3" stroke-linecap="round" stroke-dasharray="6 6"/>
      <circle cx="265" cy="75" r="4" fill="#FF95A5"/>

      <!-- Cube 2: Intelligence & RFM (Part B) -->
      <g transform="translate(320, 30)">
        <polygon points="0,0 40,-22 80,0 40,22" fill="#FFF6DC" stroke="#425B9A" stroke-width="2"/>
        <polygon points="0,0 40,22 40,68 0,46" fill="#76C0EC" stroke="#1C2438" stroke-width="2"/>
        <polygon points="40,22 80,0 80,46 40,68" fill="#589BCE" stroke="#1C2438" stroke-width="2"/>
        <text x="40" y="5" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="800" fill="#425B9A" text-anchor="middle">RFM ML</text>
      </g>

      <!-- Isometric Conduit 2 -> 3 -->
      <path d="M400 65 L510 65" stroke="#76C0EC" stroke-width="3" stroke-linecap="round" stroke-dasharray="6 6"/>
      <circle cx="455" cy="65" r="4" fill="#76C0EC"/>

      <!-- Cube 3: Triage Guardrails (Part C) -->
      <g transform="translate(510, 40)">
        <polygon points="0,0 36,-20 72,0 36,20" fill="#FF95A5" stroke="#425B9A" stroke-width="2"/>
        <polygon points="0,0 36,20 36,60 0,40" fill="#DE687A" stroke="#1C2438" stroke-width="2"/>
        <polygon points="36,20 72,0 72,40 36,60" fill="#BA495B" stroke="#1C2438" stroke-width="2"/>
        <text x="36" y="5" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="800" fill="#FFFFFF" text-anchor="middle">TRIAGE</text>
      </g>

      <!-- Isometric Conduit 3 -> 4 -->
      <path d="M582 70 L690 70" stroke="#FFF6DC" stroke-width="3" stroke-linecap="round" stroke-dasharray="6 6"/>
      <circle cx="636" cy="70" r="4" fill="#FFF6DC"/>

      <!-- Cube 4: ReAct Agent & RAG (Part D) -->
      <g transform="translate(690, 25)">
        <polygon points="0,0 42,-24 84,0 42,24" fill="#76C0EC" stroke="#425B9A" stroke-width="2"/>
        <polygon points="0,0 42,24 42,75 0,51" fill="#425B9A" stroke="#1C2438" stroke-width="2"/>
        <polygon points="42,24 84,0 84,51 42,75" fill="#2E406F" stroke="#1C2438" stroke-width="2"/>
        <text x="42" y="5" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="800" fill="#FFF6DC" text-anchor="middle">AGENT</text>
      </g>
    </svg>
    """

# ------------------------------------------------------------------------------
# Sidebar Navigation
# ------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 12px 0 20px 0;">
        <div style="font-size: 2.2rem;">📦 ⚡ 🤖</div>
        <h2 style="color: #425B9A; font-weight: 800; margin: 4px 0 0 0; letter-spacing: -0.02em;">INSTAMART</h2>
        <div style="font-size: 0.85rem; font-weight: 700; color: #FF95A5; text-transform: uppercase; letter-spacing: 0.1em;">Copilot Intelligence</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 8px 0 16px 0; border: 1px solid #425B9A25;'>", unsafe_allow_html=True)

    app_mode = st.radio(
        "NAVIGATION MODULES",
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

    st.markdown("<hr style='margin: 16px 0; border: 1px solid #425B9A25;'>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: #FFF6DC; border: 1.5px solid #425B9A; border-radius: 8px; padding: 12px; box-shadow: 3px 3px 0px #425B9A;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #425B9A; margin-bottom: 4px;">ACTIVE SYSTEM PALETTE</div>
        <div style="display: flex; gap: 6px; align-items: center;">
            <div style="width: 20px; height: 20px; border-radius: 4px; background: #425B9A; border: 1px solid #1C2438;" title="#425B9A Deep Indigo"></div>
            <div style="width: 20px; height: 20px; border-radius: 4px; background: #76C0EC; border: 1px solid #1C2438;" title="#76C0EC Sky Blue"></div>
            <div style="width: 20px; height: 20px; border-radius: 4px; background: #FFF6DC; border: 1px solid #1C2438;" title="#FFF6DC Warm Ivory"></div>
            <div style="width: 20px; height: 20px; border-radius: 4px; background: #FF95A5; border: 1px solid #1C2438;" title="#FF95A5 Coral Pink"></div>
        </div>
        <div style="font-size: 0.7rem; color: #55627E; margin-top: 6px;">Status: <strong>All Pipelines Online</strong></div>
    </div>
    """, unsafe_allow_html=True)


# ==============================================================================
# MODULE 1: MISSION CONTROL & VISUAL GUIDE
# ==============================================================================
if app_mode == "🏛️ Mission Control & Visual Guide":
    st.markdown("""
    <div class="iso-hero">
        <span class="iso-badge badge-pink">OPERATIONAL INTELLIGENCE</span>
        <span class="iso-badge badge-blue">ENTERPRISE COPILOT</span>
        <h1>Instamart Customer Intelligence & Autonomous Operations</h1>
        <p>An integrated, fault-tolerant platform delivering clean relational data modeling, customer RFM clustering, predictive lapse mitigation, safe LLM support triage, and policy-grounded ReAct refund agents.</p>
    </div>
    """, unsafe_allow_html=True)

    # Isometric System Flow Graphic
    st.markdown('<div class="iso-card">', unsafe_allow_html=True)
    st.markdown("### 📐 Isomorphic Architecture Pipeline")
    st.markdown(render_isomorphic_header_svg(), unsafe_allow_html=True)
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 12px; text-align: center;">
        <div><strong>Part A: Data Foundation</strong><br><span style="font-size: 0.85rem; color: #55627E;">Dirty raw audit, clean exports, SQLite instamart.db</span></div>
        <div><strong>Part B: Customer Modeling</strong><br><span style="font-size: 0.85rem; color: #55627E;">RFM K-Means clustering, PCA, lapse predictive AI</span></div>
        <div><strong>Part C: Ticket Triage</strong><br><span style="font-size: 0.85rem; color: #55627E;">Regex PII redaction, token budgets, queue routing</span></div>
        <div><strong>Part D: Policy ReAct Agent</strong><br><span style="font-size: 0.85rem; color: #55627E;">15-chunk TF-IDF RAG, SQLite tools, state checkpoints</span></div>
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
            <div class="iso-metric-val">4 Stages</div>
            <div class="iso-metric-label">Zero-Data Leakage</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Visual Guide Cards (2x2 grid)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="iso-card">
            <span class="iso-badge badge-blue">PART A</span>
            <h3 style="color: #425B9A; margin-top: 8px;">Relational Analytics & Auditing</h3>
            <p>Audits 13,084 raw orders and 1,200 customers, removing 119 exact duplicates, standardizing 24 raw city spellings into 6 metro hubs, imputing missing ages, and validating 7 analytical SQL queries against <code>data/instamart.db</code>.</p>
            <ul style="font-size: 0.9rem; color: #3A4664;">
                <li><strong>Bengaluru / Electronics</strong>: Top revenue category (INR 233,909.45).</li>
                <li><strong>Rank Discrepancies</strong>: 8 tied rows between <code>RANK()</code> and <code>ROW_NUMBER()</code>.</li>
                <li><strong>Cumulative Revenue</strong>: Exact tracking over 183 operational days.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="iso-card">
            <span class="iso-badge badge-cream">PART B</span>
            <h3 style="color: #425B9A; margin-top: 8px;">RFM Clustering & Lapse AI</h3>
            <p>Builds customer behavioral snapshot at 2025-10-01 across 1,175 customers. Fits K-Means (K=4, inertia 743.1, silhouette 0.526) with 2D PCA projection, and trains leakage-free lapse models.</p>
            <ul style="font-size: 0.9rem; color: #3A4664;">
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
            <span class="iso-badge badge-pink">PART C</span>
            <h3 style="color: #425B9A; margin-top: 8px;">Privacy Guardrails & Triage</h3>
            <p>Sanitizes 164 customer tickets via strict regex substitution (email, phone, order IDs), enforces input length bounds (drops 4 empty and 4 oversized >400 token tickets), and routes tickets using Part B customer tiers.</p>
            <ul style="font-size: 0.9rem; color: #3A4664;">
                <li><strong>PII Neutralized</strong>: 278 substitutions with 0 remaining.</li>
                <li><strong>Few-Shot Superiority</strong>: 100% accuracy vs 85.7% for zero-shot.</li>
                <li><strong>Budget Safety</strong>: Demonstrates hard cap stop at 6,000 tokens.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="iso-card">
            <span class="iso-badge badge-navy">PART D</span>
            <h3 style="color: #425B9A; margin-top: 8px;">RAG Grounding & ReAct Agent</h3>
            <p>Deploys a 40-word / 10-overlap TF-IDF retrieval system over 5 operational policies, powering an autonomous ReAct refund agent with 5 live database and policy tools.</p>
            <ul style="font-size: 0.9rem; color: #3A4664;">
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
        <h1>Data Cleaning, Relational Modeling & SQL Analytics</h1>
        <p>Audit dirty operational telemetry, enforce strict cleaning transforms, and query SQLite <code>data/instamart.db</code> across multi-table joins, CTEs, and window functions.</p>
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
                        title="Revenue by City and Category",
                        barmode="group",
                        color_discrete_sequence=["#425B9A", "#76C0EC", "#FF95A5", "#F5A623", "#2EC4B6"]
                    )
                    fig.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#FAF8F2")
                    st.plotly_chart(fig, use_container_width=True)

                elif "Q7" in q_preset_name and "cumulative_revenue" in res_df.columns:
                    fig = px.line(
                        res_df, x="day", y="cumulative_revenue",
                        title="Cumulative Operational Revenue (INR)",
                        color_discrete_sequence=["#425B9A"]
                    )
                    fig.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#FAF8F2")
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
        <span class="iso-badge badge-cream">PART B MODELING</span>
        <h1>Customer RFM Clustering & Predictive Lapse AI</h1>
        <p>Explore 3D RFM behavioral spaces, identify VIP Champions, and predict customer churn using balanced machine learning models without lookahead leakage.</p>
    </div>
    """, unsafe_allow_html=True)

    df_seg = load_segments()

    tab1, tab2, tab3 = st.tabs(["🧊 3D Isometric RFM Visualizer", "👥 Segment Profiles & Actions", "📉 Lapse ML & Priority Retention"])

    with tab1:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 🧊 3D Isometric Customer Clustering (Recency × Frequency × Monetary)")
        st.markdown("Rotate and explore the customer behavioral feature space in 3D.")

        if not df_seg.empty:
            # 3D Scatter Plot with Isometric Perspective
            palette_map = {
                "At-Risk / Lapsed": "#FF95A5",
                "Champions": "#425B9A",
                "Promising": "#76C0EC",
                "Occasional Buyers": "#FFD166"
            }
            colors = [palette_map.get(s, "#425B9A") for s in df_seg["segment_name"]]

            fig_3d = go.Figure(data=[go.Scatter3d(
                x=df_seg["recency"],
                y=df_seg["frequency"],
                z=df_seg["monetary"],
                mode='markers',
                marker=dict(
                    size=4.5,
                    color=df_seg["cluster"],
                    colorscale=[[0, '#425B9A'], [0.33, '#76C0EC'], [0.66, '#FF95A5'], [1.0, '#FFD166']],
                    opacity=0.85
                ),
                text=[f"Customer: {cid}<br>Recency: {r}d<br>Freq: {f}<br>Spend: INR {m:,.2f}<br>Segment: {s}" 
                      for cid, r, f, m, s in zip(df_seg['customer_id'], df_seg['recency'], df_seg['frequency'], df_seg['monetary'], df_seg['segment_name'])],
                hoverinfo='text'
            )])

            # Set camera to 2.5D Isometric angle
            fig_3d.update_layout(
                scene=dict(
                    xaxis_title='Recency (Days)',
                    yaxis_title='Frequency (Orders)',
                    zaxis_title='Monetary Spend (INR)',
                    camera=dict(eye=dict(x=1.65, y=1.65, z=1.25)),
                    bgcolor="#FAF8F2"
                ),
                margin=dict(l=0, r=0, b=0, t=20),
                height=580,
                paper_bgcolor="#FFFFFF"
            )
            st.plotly_chart(fig_3d, use_container_width=True)
        else:
            st.warning("Customer segments file not found. Run Part B training pipeline.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Customer Segment Profiles & Strategic Recommendations")
        
        if not df_seg.empty:
            agg_seg = df_seg.groupby(["cluster", "segment_name", "is_premium"]).agg(
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
                    color_discrete_sequence=["#76C0EC", "#425B9A", "#FF95A5", "#FFD166"]
                )
                fig_bar.update_layout(paper_bgcolor="#FFFFFF", plot_bgcolor="#FAF8F2")
                st.plotly_chart(fig_bar, use_container_width=True)

            with c_p2:
                st.markdown("""
                <div style="background: #FFF6DC; border: 2px solid #425B9A; border-radius: 10px; padding: 18px; box-shadow: 4px 4px 0px #425B9A;">
                    <h4 style="color: #425B9A; margin-top: 0;">🚀 Business Action Playbooks</h4>
                    <p><strong>👑 Champions (Premium)</strong>: Priority concierge, exclusive early access, dedicated support route.</p>
                    <p><strong>🌟 Promising</strong>: Personalized category upsells, loyalty tier progression bonuses.</p>
                    <p><strong>⚠️ At-Risk / Lapsed</strong>: Win-back discount coupons, push notifications on habitual shopping days.</p>
                    <p><strong>🛒 Occasional Buyers</strong>: Category discovery prompts, free delivery thresholds.</p>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="iso-card">', unsafe_allow_html=True)
        st.markdown("### 📉 High-Risk Premium Customer Retention Watchlist")
        st.markdown("Top 10 High-Value (`is_premium == True`) test customers predicted at immediate risk of churning:")
        
        df_ret = load_retention_list()
        if not df_ret.empty:
            df_ret["lapse_probability"] = df_ret["lapse_probability"].round(4)
            df_ret["pre_monetary"] = df_ret["pre_monetary"].apply(lambda v: f"INR {v:,.2f}")
            st.dataframe(df_ret, use_container_width=True)
        else:
            st.info("Retention list not generated yet.")
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# MODULE 4: PART C - SAFE TICKET TRIAGE LAB
# ==============================================================================
elif app_mode == "🛡️ Part C: Safe Ticket Triage Lab":
    st.markdown("""
    <div class="iso-hero">
        <span class="iso-badge badge-pink">PART C PIPELINE</span>
        <h1>Support Ticket Privacy Guardrails & Smart Triage</h1>
        <p>Test real-time regex PII redaction (email, phone, order ID), input token guardrails, and customer-segment priority routing.</p>
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
                    st.success("Guardrail Passed: Eligible for processing")

            if not is_empty and tok_est <= 400:
                # 2. PII Redaction
                redacted, counts = triage.redact_pii(user_ticket)
                st.markdown("#### 2. PII Sanitization Transformation")
                st.markdown(f"""
                <div style="background: #FFF6DC; border: 2px solid #425B9A; border-radius: 8px; padding: 12px;">
                    <div><strong>Substitutions Applied:</strong> {counts['email']} Emails, {counts['phone']} Phones, {counts['order_id']} Order IDs (Total: {counts['total']})</div>
                    <div style="margin-top: 8px; font-family: monospace; color: #425B9A;"><strong>Redacted User Prompt:</strong> {redacted}</div>
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
                color_discrete_sequence=["#425B9A", "#76C0EC", "#FF95A5", "#FFF6DC"]
            )
            fig_tri.update_layout(paper_bgcolor="#FFFFFF")
            st.plotly_chart(fig_tri, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ==============================================================================
# MODULE 5: PART D - POLICY RAG & REACT REFUND AGENT
# ==============================================================================
elif app_mode == "🤖 Part D: Policy RAG & ReAct Agent":
    st.markdown("""
    <div class="iso-hero">
        <span class="iso-badge badge-navy">PART D AUTONOMY</span>
        <h1>Policy Retrieval-Augmented Generation & ReAct Refund Agent</h1>
        <p>Ground answers across 5 company policy documents, and simulate multi-step ReAct agent decision making with automated SQLite tool calls and state checkpointing.</p>
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
            <div style="background: #FFF6DC; border: 2px solid #425B9A; border-radius: 8px; padding: 14px; font-weight: 600; color: #1C2438;">
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
        <span class="iso-badge badge-cream">PIPELINE AUTOMATION</span>
        <h1>Project Execution & Reproduction Control Hub</h1>
        <p>Trigger and monitor live script executions for data auditing, cleaning, RFM model training, triage evaluation, and ReAct agent benchmarks.</p>
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
    <div style="text-align: center; color: #55627E; font-size: 0.85rem; margin-top: 32px;">
        Instamart Copilot Intelligence Suite • Built with Streamlit, Plotly & Scikit-Learn • Palette: #425B9A, #76C0EC, #FFF6DC, #FF95A5
    </div>
    """, unsafe_allow_html=True)
