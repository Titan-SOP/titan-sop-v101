# ui_desktop/tab1_macro.py
# Titan SOP V100 — 宏觀風控指揮中心
# UI: God-Tier Glass-HUD (PLTR × Tesla × iOS)
# Logic: Fully preserved from V81.1 + V100 refactor

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
from datetime import datetime

from macro_risk import MacroRiskEngine
from knowledge_base import TitanKnowledgeBase
from config import Config

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
SIGNAL_MAP = {
    "GREEN_LIGHT":  "🟢 綠燈：積極進攻",
    "YELLOW_LIGHT": "🟡 黃燈：區間操作",
    "RED_LIGHT":    "🔴 紅燈：現金為王",
}

SIGNAL_PALETTE = {
    "GREEN_LIGHT":  "#00FF7F",
    "YELLOW_LIGHT": "#FFD700",
    "RED_LIGHT":    "#FF3131",
}

SUB_MODULES = [
    ("1.1", "HUD",  "風控儀表"),
    ("1.2", "TEMP", "多空溫度"),
    ("1.3", "PR90", "籌碼分佈"),
    ("1.4", "HEAT", "族群熱度"),
    ("1.5", "VOL",  "成交重心"),
    ("1.6", "RADAR","趨勢雷達"),
    ("1.7", "WTX",  "台指獵殺"),
]

# ══════════════════════════════════════════════════════════════════════════════
#  MASTER CSS — Glass-HUD Terminal (High Visibility Edition)
# ══════════════════════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@400;600;700&family=JetBrains+Mono:wght@400;600;800&display=swap" rel="stylesheet">

<style>
/* ────────────────────────────────────────────────────────────
   0. ROOT VARIABLES & GLOBAL RESET
──────────────────────────────────────────────────────────── */
:root {
  --c-bg:       #06090E;
  --c-surface:  #0D1117;
  --c-glass:    rgba(13, 17, 23, 0.85);
  --c-border:   rgba(0, 245, 255, 0.25);
  --c-cyan:     #00F5FF;
  --c-gold:     #FFD700;
  --c-red:      #FF3131;
  --c-green:    #00FF7F;
  --c-dim:      #3A4A5A;
  --c-text:     #E0E6ED;
  --c-muted:    #8899AA;
  --f-display:  'Orbitron', monospace;
  --f-sub:      'Rajdhani', sans-serif;
  --f-mono:     'JetBrains Mono', monospace;
  --glow-cyan:  0 0 10px rgba(0,245,255,0.6), 0 0 30px rgba(0,245,255,0.3);
  --glow-gold:  0 0 10px rgba(255,215,0,0.6), 0 0 30px rgba(255,215,0,0.3);
}

/* Streamlit baseline */
[data-testid="stAppViewContainer"] { background: var(--c-bg) !important; }
[data-testid="stHeader"]           { background: transparent !important; }
[data-testid="stSidebar"]          { background: #080C12 !important; border-right: 1px solid var(--c-border) !important; }
.main .block-container             { padding: 2rem 3rem 5rem !important; max-width: 1600px !important; }

/* ────────────────────────────────────────────────────────────
   1. HEADER — TITAN GLOWING TITLE (BIGGER)
──────────────────────────────────────────────────────────── */
.titan-masthead {
  font-family: var(--f-display);
  font-size: 42px; /* 原本 28px */
  font-weight: 900;
  letter-spacing: 6px;
  text-transform: uppercase;
  color: var(--c-gold);
  text-shadow: var(--glow-gold);
  margin: 0 0 8px;
}
.titan-masthead-sub {
  font-family: var(--f-sub);
  font-size: 16px; /* 原本 12px */
  letter-spacing: 6px;
  color: var(--c-muted);
  text-transform: uppercase;
  margin-bottom: 32px;
}

/* ────────────────────────────────────────────────────────────
   2. COMMAND DECK — NAVIGATION (BIGGER BUTTONS)
──────────────────────────────────────────────────────────── */
.cmd-deck {
  background: linear-gradient(160deg, #0A0E15 0%, #0D1420 100%);
  border: 1px solid var(--c-border);
  border-radius: 18px;
  padding: 24px;
  margin-bottom: 30px;
}
.cmd-deck-label {
  font-family: var(--f-display);
  font-size: 12px; /* 原本 8px */
  letter-spacing: 4px;
  color: var(--c-muted);
  text-transform: uppercase;
  margin-bottom: 16px;
}

/* Nav buttons - Increasing size */
div.stButton > button[kind="secondary"] {
  font-family: var(--f-display) !important;
  font-size: 14px !important; /* 原本 10px */
  font-weight: 700 !important;
  letter-spacing: 2px !important;
  min-height: 80px !important; /* 加高 */
  border-radius: 12px !important;
}

/* Active nav card */
.nav-active {
  background: linear-gradient(135deg, rgba(0,245,255,0.15), rgba(255,215,0,0.1)) !important;
  border: 2px solid var(--c-gold) !important;
  border-radius: 12px !important;
  min-height: 80px !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  box-shadow: var(--glow-gold) !important;
  padding: 10px !important;
}
.nav-active div:first-child { font-size: 24px !important; margin-bottom: 6px !important; } /* Icon */
.nav-active div:nth-child(2) { font-size: 10px !important; } /* Code */
.nav-active div:nth-child(3) { font-size: 14px !important; font-weight: 900 !important; } /* Label */


/* ────────────────────────────────────────────────────────────
   3. HUD CARDS (MASSIVE DATA)
──────────────────────────────────────────────────────────── */
.hud-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; margin: 24px 0; }

.hud-card {
  background: rgba(13,17,23,0.9);
  backdrop-filter: blur(16px);
  border-radius: 16px;
  padding: 24px 20px 20px; /* 加大內距 */
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.05);
}
.hud-card::before { height: 4px; } /* 更粗的頂部線條 */

.hud-label {
  font-family: var(--f-display);
  font-size: 14px; /* 原本 9px，大幅提升 */
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--c-muted);
  margin-bottom: 12px;
  font-weight: 700;
}
.hud-value {
  font-family: var(--f-mono);
  font-size: 42px; /* 原本 28px，霸氣數據 */
  font-weight: 800;
  color: #FFFFFF;
  line-height: 1.1;
  margin-bottom: 10px;
  letter-spacing: -1px;
}
.hud-delta {
  font-family: var(--f-sub);
  font-size: 18px; /* 原本 13px */
  font-weight: 700;
  letter-spacing: 1px;
}
.hud-corner-tag {
  font-size: 10px; /* 原本 7px */
  top: 14px; right: 16px;
  font-weight: 700;
  background: rgba(255,255,255,0.1);
  padding: 2px 6px;
  border-radius: 4px;
}

/* ────────────────────────────────────────────────────────────
   4. SECTION HEADERS & SIGNALS
──────────────────────────────────────────────────────────── */
.sec-header {
  font-size: 20px; /* 原本 14px */
  letter-spacing: 4px;
  padding: 0 0 16px 16px;
  border-left: 4px solid var(--c-cyan);
  margin-bottom: 24px;
}
.sec-header .sec-num {
  font-size: 14px;
  padding: 4px 8px;
}

.signal-panel {
  padding: 28px 32px;
}
.signal-dot { width: 24px; height: 24px; }
.signal-text {
  font-size: 28px; /* 原本 18px */
  letter-spacing: 3px;
}
.signal-sub {
  font-size: 16px; /* 原本 13px */
  margin-top: 6px;
}

/* ────────────────────────────────────────────────────────────
   5. DATA TABLE (READABLE)
──────────────────────────────────────────────────────────── */
.content-shell {
  padding: 32px;
}

[data-testid="stDataFrame"] thead tr th {
  font-size: 14px !important; /* 原本 10px */
  padding: 12px !important;
}
[data-testid="stDataFrame"] tbody tr td {
  font-size: 16px !important; /* 原本 12px，看得清楚了 */
  padding: 12px !important;
}

/* ────────────────────────────────────────────────────────────
   6. METRIC OVERRIDE & BUTTONS
──────────────────────────────────────────────────────────── */
[data-testid="stMetricLabel"] p {
  font-size: 12px !important; /* 原本 9px */
}
[data-testid="stMetricValue"] {
  font-size: 32px !important; /* 原本 24px */
}

.content-shell div.stButton > button {
  font-size: 14px !important; /* 原本 11px */
  padding: 12px 24px !important;
}

/* ────────────────────────────────────────────────────────────
   7. BASEBALL & HEATMAP
──────────────────────────────────────────────────────────── */
.base-card-label { font-size: 12px; }
.base-card-value { font-size: 28px; font-weight: 800; } /* 棒球跑壘數字加大 */
.base-card-status { font-size: 14px; }

.tse-cell-label { font-size: 11px; }
.tse-cell-value { font-size: 20px; }

/* ────────────────────────────────────────────────────────────
   8. INPUTS
──────────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
  font-size: 16px !important;
}
div[data-baseweb="select"] span {
  font-size: 16px !important;
}
</style>
""", unsafe_allow_html=True)
/* ────────────────────────────────────────────────────────────
   0. ROOT VARIABLES & GLOBAL RESET
──────────────────────────────────────────────────────────── */
:root {
  --c-bg:       #06090E;
  --c-surface:  #0D1117;
  --c-glass:    rgba(13, 17, 23, 0.75);
  --c-border:   rgba(0, 245, 255, 0.15);
  --c-cyan:     #00F5FF;
  --c-gold:     #FFD700;
  --c-red:      #FF3131;
  --c-green:    #00FF7F;
  --c-dim:      #3A4A5A;
  --c-text:     #C8D8E8;
  --c-muted:    #556070;
  --f-display:  'Orbitron', monospace;
  --f-sub:      'Rajdhani', sans-serif;
  --f-mono:     'JetBrains Mono', monospace;
  --glow-cyan:  0 0 8px rgba(0,245,255,0.6), 0 0 24px rgba(0,245,255,0.25);
  --glow-gold:  0 0 8px rgba(255,215,0,0.6), 0 0 24px rgba(255,215,0,0.25);
  --glow-red:   0 0 8px rgba(255,49,49,0.6),  0 0 24px rgba(255,49,49,0.25);
}

/* Streamlit baseline */
[data-testid="stAppViewContainer"] { background: var(--c-bg) !important; }
[data-testid="stHeader"]           { background: transparent !important; }
[data-testid="stSidebar"]          { background: #080C12 !important; border-right: 1px solid var(--c-border) !important; }
.main .block-container             { padding: 1.2rem 2rem 4rem !important; max-width: 1400px !important; }

/* ────────────────────────────────────────────────────────────
   1. AMBIENT SCANLINE OVERLAY
──────────────────────────────────────────────────────────── */
[data-testid="stAppViewContainer"]::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 245, 255, 0.012) 2px,
    rgba(0, 245, 255, 0.012) 4px
  );
  z-index: 9999;
}

/* ────────────────────────────────────────────────────────────
   2. HEADER — TITAN GLOWING TITLE
──────────────────────────────────────────────────────────── */
.titan-masthead {
  font-family: var(--f-display);
  font-size: clamp(18px, 2.5vw, 28px);
  font-weight: 900;
  letter-spacing: 4px;
  text-transform: uppercase;
  color: var(--c-gold);
  text-shadow: var(--glow-gold);
  margin: 0 0 6px;
}
.titan-masthead-sub {
  font-family: var(--f-sub);
  font-size: 12px;
  letter-spacing: 5px;
  color: var(--c-muted);
  text-transform: uppercase;
  margin-bottom: 24px;
}

/* ────────────────────────────────────────────────────────────
   3. COMMAND DECK — NAVIGATION
──────────────────────────────────────────────────────────── */
.cmd-deck {
  background: linear-gradient(160deg, #0A0E15 0%, #0D1420 100%);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  padding: 20px 22px 16px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
}
.cmd-deck::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, var(--c-cyan), transparent);
  opacity: 0.6;
}
.cmd-deck-label {
  font-family: var(--f-display);
  font-size: 8px;
  letter-spacing: 4px;
  color: var(--c-muted);
  text-transform: uppercase;
  margin-bottom: 14px;
}

/* Nav buttons */
div.stButton > button[kind="secondary"] {
  background: rgba(13,20,32,0.9) !important;
  border: 1px solid rgba(0,245,255,0.18) !important;
  border-radius: 10px !important;
  color: var(--c-muted) !important;
  font-family: var(--f-display) !important;
  font-size: 10px !important;
  font-weight: 600 !important;
  letter-spacing: 1.5px !important;
  padding: 10px 4px !important;
  min-height: 68px !important;
  width: 100% !important;
  transition: all 0.2s ease !important;
  line-height: 1.5 !important;
  text-transform: uppercase !important;
  cursor: pointer !important;
}
div.stButton > button[kind="secondary"]:hover {
  border-color: var(--c-cyan) !important;
  color: var(--c-cyan) !important;
  background: rgba(0,245,255,0.06) !important;
  box-shadow: var(--glow-cyan) !important;
  transform: translateY(-2px) !important;
}

/* Active nav card */
.nav-active {
  background: linear-gradient(135deg, rgba(0,245,255,0.10), rgba(255,215,0,0.06)) !important;
  border: 1.5px solid var(--c-gold) !important;
  border-radius: 10px !important;
  min-height: 68px !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  font-family: var(--f-display) !important;
  font-size: 10px !important;
  font-weight: 700 !important;
  letter-spacing: 1.5px !important;
  text-transform: uppercase !important;
  color: var(--c-gold) !important;
  box-shadow: var(--glow-gold) !important;
  animation: active-breathe 2.8s ease-in-out infinite !important;
  cursor: default !important;
  padding: 8px 4px !important;
}
@keyframes active-breathe {
  0%, 100% { box-shadow: 0 0 6px rgba(255,215,0,0.5), 0 0 18px rgba(255,215,0,0.2); }
  50%       { box-shadow: 0 0 12px rgba(255,215,0,0.8), 0 0 32px rgba(255,215,0,0.35); }
}

/* ────────────────────────────────────────────────────────────
   4. HUD CARDS
──────────────────────────────────────────────────────────── */
.hud-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin: 18px 0;
}
.hud-card {
  background: rgba(13,17,23,0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  padding: 18px 16px 14px;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.hud-card::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
  background: var(--accent-color, var(--c-cyan));
  box-shadow: 0 0 8px var(--accent-color, var(--c-cyan));
}
.hud-card::after {
  content: "";
  position: absolute;
  bottom: 0; left: 0; width: 30%; height: 1px;
  background: linear-gradient(90deg, var(--accent-color, var(--c-cyan)), transparent);
}
.hud-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(0,245,255,0.12);
}
.hud-label {
  font-family: var(--f-display);
  font-size: 9px;
  letter-spacing: 2.5px;
  text-transform: uppercase;
  color: var(--c-muted);
  margin-bottom: 10px;
}
.hud-value {
  font-family: var(--f-mono);
  font-size: 28px;
  font-weight: 600;
  color: #FFFFFF;
  line-height: 1;
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}
.hud-delta {
  font-family: var(--f-sub);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.hud-corner-tag {
  position: absolute;
  top: 10px; right: 12px;
  font-family: var(--f-display);
  font-size: 7px;
  letter-spacing: 1px;
  color: var(--c-muted);
  opacity: 0.6;
}

/* ────────────────────────────────────────────────────────────
   5. SECTION HEADERS
──────────────────────────────────────────────────────────── */
.sec-header {
  font-family: var(--f-display);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 3px;
  text-transform: uppercase;
  color: var(--c-cyan);
  text-shadow: var(--glow-cyan);
  padding: 0 0 14px 14px;
  border-left: 2px solid var(--c-cyan);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.sec-header .sec-num {
  font-size: 10px;
  color: var(--c-muted);
  background: rgba(0,245,255,0.08);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid var(--c-border);
}

/* ────────────────────────────────────────────────────────────
   6. SIGNAL LIGHT PANEL
──────────────────────────────────────────────────────────── */
.signal-panel {
  background: rgba(8, 12, 18, 0.9);
  border: 1px solid var(--c-border);
  border-radius: 14px;
  padding: 22px 28px;
  display: flex;
  align-items: center;
  gap: 20px;
  margin: 18px 0;
}
.signal-dot {
  width: 18px; height: 18px;
  border-radius: 50%;
  flex-shrink: 0;
  animation: dot-pulse 2s ease-in-out infinite;
}
@keyframes dot-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.7; transform: scale(1.15); }
}
.signal-text {
  font-family: var(--f-display);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 2px;
}
.signal-sub {
  font-family: var(--f-sub);
  font-size: 13px;
  color: var(--c-muted);
  letter-spacing: 1px;
  margin-top: 3px;
}

/* ────────────────────────────────────────────────────────────
   7. DATA TABLE — CUSTOM DARK OVERRIDE
──────────────────────────────────────────────────────────── */
.content-shell {
  background: rgba(8,12,18,0.96);
  border: 1px solid var(--c-border);
  border-radius: 14px;
  padding: 28px 26px 32px;
  position: relative;
  overflow: hidden;
}
.content-shell::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent 5%, var(--c-cyan) 40%, var(--c-gold) 60%, transparent 95%);
  opacity: 0.4;
}

[data-testid="stDataFrame"] { background: transparent !important; }
[data-testid="stDataFrame"] thead tr th {
  background: rgba(0,245,255,0.06) !important;
  color: var(--c-cyan) !important;
  font-family: var(--f-display) !important;
  font-size: 10px !important;
  letter-spacing: 2px !important;
  border-bottom: 1px solid var(--c-border) !important;
}
[data-testid="stDataFrame"] tbody tr td {
  font-family: var(--f-mono) !important;
  font-size: 12px !important;
  color: var(--c-text) !important;
  border-bottom: 1px solid rgba(0,245,255,0.04) !important;
}

/* ────────────────────────────────────────────────────────────
   8. BUTTONS INSIDE CONTENT AREA — OVERRIDE STREAMLIT GREEN
──────────────────────────────────────────────────────────── */
.content-shell div.stButton > button,
.content-shell div.stButton > button:focus {
  background: linear-gradient(135deg, #0D1420, #0A1028) !important;
  border: 1px solid var(--c-gold) !important;
  color: var(--c-gold) !important;
  font-family: var(--f-display) !important;
  font-size: 11px !important;
  letter-spacing: 2px !important;
  border-radius: 8px !important;
  padding: 10px 20px !important;
  box-shadow: none !important;
  text-transform: uppercase !important;
  transition: all 0.2s !important;
}
.content-shell div.stButton > button:hover {
  background: rgba(255,215,0,0.08) !important;
  box-shadow: var(--glow-gold) !important;
  transform: translateY(-1px) !important;
}

/* ────────────────────────────────────────────────────────────
   9. METRIC OVERRIDE — hide default st.metric in content
──────────────────────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: rgba(13,17,23,0.7) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: 10px !important;
  padding: 14px !important;
}
[data-testid="stMetricLabel"] p {
  font-family: var(--f-display) !important;
  font-size: 9px !important;
  letter-spacing: 2px !important;
  color: var(--c-muted) !important;
  text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
  font-family: var(--f-mono) !important;
  font-size: 24px !important;
  color: #FFF !important;
}
[data-testid="stMetricDelta"] {
  font-family: var(--f-sub) !important;
  font-size: 12px !important;
}

/* ────────────────────────────────────────────────────────────
   10. INFO / WARNING CHIPS
──────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  background: rgba(0,245,255,0.05) !important;
  border: 1px solid rgba(0,245,255,0.2) !important;
  border-radius: 10px !important;
  font-family: var(--f-sub) !important;
}

/* ────────────────────────────────────────────────────────────
   11. DIVIDERS
──────────────────────────────────────────────────────────── */
hr {
  border: none !important;
  height: 1px !important;
  background: linear-gradient(90deg, transparent, var(--c-border), transparent) !important;
  margin: 20px 0 !important;
}

/* ────────────────────────────────────────────────────────────
   12. TSE ANALYSIS MINI-GRID
──────────────────────────────────────────────────────────── */
.tse-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin: 14px 0;
}
.tse-cell {
  background: rgba(0,245,255,0.04);
  border: 1px solid var(--c-border);
  border-radius: 10px;
  padding: 14px 16px;
}
.tse-cell-label {
  font-family: var(--f-display);
  font-size: 9px;
  letter-spacing: 2px;
  color: var(--c-muted);
  text-transform: uppercase;
  margin-bottom: 6px;
}
.tse-cell-value {
  font-family: var(--f-sub);
  font-size: 16px;
  font-weight: 700;
  color: var(--c-text);
}
.deduct-bar {
  font-family: var(--f-mono);
  font-size: 11px;
  color: var(--c-muted);
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 8px;
  padding: 10px 14px;
  margin-top: 12px;
  letter-spacing: 1px;
  word-break: break-all;
}

/* ────────────────────────────────────────────────────────────
   13. BASEBALL CHART WRAPPER
──────────────────────────────────────────────────────────── */
.chart-dark-wrap {
  background: rgba(6,9,14,0.95);
  border: 1px solid var(--c-border);
  border-radius: 14px;
  padding: 20px;
  margin-top: 16px;
}

/* ────────────────────────────────────────────────────────────
   14. BASE HIT TARGETS GRID
──────────────────────────────────────────────────────────── */
.base-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin: 16px 0;
}
.base-card {
  border-radius: 12px;
  padding: 16px 14px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.base-card::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0; height: 2px;
}
.base-card-label {
  font-family: var(--f-display);
  font-size: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.base-card-value {
  font-family: var(--f-mono);
  font-size: 22px;
  font-weight: 600;
  color: #FFF;
}
.base-card-status {
  font-family: var(--f-sub);
  font-size: 12px;
  margin-top: 4px;
}

/* ────────────────────────────────────────────────────────────
   15. SECTOR HEATMAP TABLE STYLES
──────────────────────────────────────────────────────────── */
.hm-hot   { background: rgba(255,49,49,0.25)   !important; color: #FF9090 !important; }
.hm-warm  { background: rgba(255,215,0,0.20)   !important; color: #FFD700 !important; }
.hm-cool  { background: rgba(0,245,255,0.12)   !important; color: #7AF5FF !important; }

/* ────────────────────────────────────────────────────────────
   16. EMPTY STATE
──────────────────────────────────────────────────────────── */
.empty-state {
  text-align: center;
  padding: 56px 24px;
  color: var(--c-dim);
}
.empty-state-icon { font-size: 52px; margin-bottom: 14px; }
.empty-state-text {
  font-family: var(--f-sub);
  font-size: 16px;
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* ────────────────────────────────────────────────────────────
   17. SELECTBOX / INPUT CLEANUP
──────────────────────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div {
  background: rgba(13,20,32,0.9) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: 8px !important;
  font-family: var(--f-sub) !important;
  color: var(--c-text) !important;
}

/* ────────────────────────────────────────────────────────────
   18. SPINNER
──────────────────────────────────────────────────────────── */
[data-testid="stSpinner"] p {
  font-family: var(--f-display) !important;
  font-size: 11px !important;
  letter-spacing: 2px !important;
  color: var(--c-cyan) !important;
  text-transform: uppercase !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HUD CARD COMPONENT
# ══════════════════════════════════════════════════════════════════════════════
def _render_hud_card(label: str, value: str, delta: str = "",
                     color: str = "#00F5FF", tag: str = ""):
    """Glassmorphism HUD card — replaces st.metric everywhere in 1.1"""
    delta_html = f'<div class="hud-delta" style="color:{color};">{delta}</div>' if delta else ""
    tag_html   = f'<div class="hud-corner-tag">{tag}</div>' if tag else ""
    st.markdown(f"""
    <div class="hud-card" style="--accent-color:{color};">
        {tag_html}
        <div class="hud-label">{label}</div>
        <div class="hud-value">{value}</div>
        {delta_html}
    </div>""", unsafe_allow_html=True)


def _render_hud_row(cards: list):
    """Render a row of HUD cards via st.columns"""
    cols = st.columns(len(cards))
    for col, (label, value, delta, color, tag) in zip(cols, cards):
        with col:
            _render_hud_card(label, value, delta, color, tag)


def _render_section_header(code: str, icon: str, title: str):
    st.markdown(f"""
    <div class="sec-header">
        <span class="sec-num">{code}</span>
        <span>{icon} {title}</span>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ENGINES (singleton + cache)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def _load_engines():
    from strategy import TitanStrategyEngine
    kb    = TitanKnowledgeBase()
    macro = MacroRiskEngine()
    strat = TitanStrategyEngine()
    strat.kb = kb
    return macro, kb, strat


@st.cache_data(ttl=600)
def _get_macro_data(_macro, _df_hash):
    df = st.session_state.get('df', pd.DataFrame())
    return _macro.check_market_status(cb_df=df)


# ══════════════════════════════════════════════════════════════════════════════
#  SHARED HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def _render_leader_dashboard(session_state_key: str, fetch_function, top_n: int, sort_key_name: str):
    """雙雷達趨勢掃描 V78.2 完整版 (Glass-HUD 外殼)"""
    macro, kb, strat = _load_engines()

    st.markdown(f"""
    <div style="font-family:var(--f-sub);font-size:14px;color:#667788;letter-spacing:1px;
                border-left:2px solid var(--c-border);padding:8px 14px;margin-bottom:16px;">
        掃描指定股票池，依「{sort_key_name}」找出 Top {top_n}，進行高階趨勢預測
    </div>""", unsafe_allow_html=True)

    if session_state_key not in st.session_state:
        st.session_state[session_state_key] = pd.DataFrame()

    if st.button(f"▶  掃描 {sort_key_name} TOP {top_n}", key=f"btn_{session_state_key}"):
        with st.spinner(f"SCANNING {sort_key_name} TOP {top_n} — PLEASE WAIT…"):
            st.session_state[session_state_key] = fetch_function(top_n=top_n)

    leaders_df = st.session_state[session_state_key]
    if leaders_df.empty:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-icon">📡</div>
            <div class="empty-state-text">AWAITING SCAN COMMAND</div>
        </div>""", unsafe_allow_html=True)
        return
    if "error" in leaders_df.columns:
        st.error(leaders_df.iloc[0]["error"])
        return

    def style_status(status):
        if "多頭" in str(status):
            return f"<span style='color:#FF4B4B;font-weight:700;font-family:var(--f-sub)'>{status}</span>"
        if "空頭" in str(status):
            return f"<span style='color:#26A69A;font-weight:700;font-family:var(--f-sub)'>{status}</span>"
        return status

    def style_deduction(sig):
        if "助漲" in str(sig): return f"<span style='color:#00FF7F'>{sig}</span>"
        if "壓力" in str(sig): return f"<span style='color:#FF3131'>{sig}</span>"
        return sig

    display_df = leaders_df.copy()
    display_df['#']          = display_df['rank']
    display_df['代號']        = display_df['ticker']
    display_df['名稱']        = display_df['name']
    display_df['產業']        = display_df['industry']
    display_df['現價']        = display_df['current_price'].apply(lambda x: f"{x:.2f}")
    display_df['趨勢']        = display_df['trend_status'].apply(style_status)
    display_df['天數']        = display_df['trend_days']
    display_df['87MA扣抵']    = display_df['deduction_signal'].apply(style_deduction)

    cols_show = ['#', '代號', '名稱', '產業', '現價', '趨勢', '天數', '87MA扣抵']
    table_html = display_df[cols_show].to_html(escape=False, index=False)
    styled_table = f"""
    <style>
    .leader-tbl {{ width:100%; border-collapse:collapse; font-family:'Rajdhani',sans-serif; }}
    .leader-tbl th {{
        background:rgba(0,245,255,0.07); color:#00C8D8;
        font-size:10px; letter-spacing:2px; text-transform:uppercase;
        padding:10px 10px; border-bottom:1px solid rgba(0,245,255,0.15);
    }}
    .leader-tbl td {{
        font-size:13px; color:#B0C0D0; padding:8px 10px;
        border-bottom:1px solid rgba(255,255,255,0.04);
    }}
    .leader-tbl tr:hover td {{ background:rgba(0,245,255,0.04); }}
    </style>
    {table_html.replace('<table', '<table class="leader-tbl"')}
    """
    st.markdown(styled_table, unsafe_allow_html=True)
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── 深度預測 ──
    st.markdown('<div class="sec-header" style="margin-top:12px"><span class="sec-num">DEEP</span> 🔍 深度預測</div>',
                unsafe_allow_html=True)
    options = [f"{row['rank']}. {row['name']} ({row['ticker']})" for _, row in leaders_df.iterrows()]
    selected_str = st.selectbox("選擇分析標的", options=options, key=f"select_{session_state_key}")

    if selected_str:
        selected_rank = int(selected_str.split('.')[0])
        sel = leaders_df[leaders_df['rank'] == selected_rank].iloc[0]

        stock_df      = sel['stock_df']
        deduction_df  = sel['deduction_df']
        adam_df       = sel['adam_df']
        current_price = sel['current_price']
        ma87          = sel['ma87']

        bias_pct      = ((current_price - ma87) / ma87) * 100 if ma87 > 0 else 0
        is_recent_bo  = (current_price > ma87) and (stock_df['Close'].iloc[-5] < ma87)
        granville     = strat._get_granville_status(current_price, ma87, is_recent_bo, bias_pct)

        _render_hud_row([
            ("現價", f"{current_price:.2f}", "", "#00F5FF", "PRICE"),
            ("格蘭碧狀態", granville, "", "#FFD700", "GRANVILLE"),
            ("趨勢波段", sel['trend_status'], f"{sel['trend_days']} 天", "#00FF7F", "TREND"),
            ("87MA扣抵預判", sel['deduction_signal'], f"斜率 {sel['ma87_slope']:.2f}°", "#FF9A3C", "DEDUCT"),
        ])

        tab_deduct, tab_adam = st.tabs(["📉 87MA 扣抵值預測", "🔄 亞當理論二次反射"])

        with tab_deduct:
            if not deduction_df.empty:
                chart_data = deduction_df.reset_index()
                chart_data['Current_Price'] = current_price
                base   = alt.Chart(chart_data).encode(x='Date:T')
                line_d = (base.mark_line(color='#FFD700', strokeDash=[6, 3])
                          .encode(y=alt.Y('Deduction_Value', title='Price'),
                                  tooltip=['Date', 'Deduction_Value'])
                          .properties(title=alt.TitleParams("未來 60 日 87MA 扣抵值預測", color='#FFD700')))
                line_c = base.mark_line(color='#00F5FF', strokeWidth=1.5).encode(y='Current_Price')
                st.altair_chart(
                    (line_d + line_c).interactive()
                    .configure_view(strokeOpacity=0, fill='#06090E')
                    .configure_axis(gridColor='rgba(0,245,255,0.07)', labelColor='#667788', titleColor='#667788')
                    .configure_title(color='#FFD700'),
                    use_container_width=True
                )
            else:
                st.warning("歷史資料不足，無法預測均線扣抵值。")

        with tab_adam:
            if not adam_df.empty:
                hist_d = stock_df.iloc[-60:].reset_index()
                hist_d['Type'] = '歷史路徑'
                proj_d = adam_df.reset_index()
                proj_d['Type'] = '亞當投影'
                proj_d.rename(columns={'Projected_Price': 'Close'}, inplace=True)
                combined = pd.concat([hist_d[['Date', 'Close', 'Type']], proj_d[['Date', 'Close', 'Type']]])
                adam_colors = alt.Scale(domain=['歷史路徑', '亞當投影'], range=['#00F5FF', '#FFD700'])
                chart = (alt.Chart(combined)
                         .mark_line(strokeWidth=2)
                         .encode(
                             x='Date:T',
                             y=alt.Y('Close', title='Price', scale=alt.Scale(zero=False)),
                             color=alt.Color('Type:N', scale=adam_colors),
                             strokeDash='Type:N'
                         )
                         .properties(title=alt.TitleParams("亞當理論二次反射路徑圖", color='#FFD700'))
                         .interactive())
                st.altair_chart(
                    chart.configure_view(strokeOpacity=0, fill='#06090E')
                         .configure_axis(gridColor='rgba(0,245,255,0.07)', labelColor='#667788', titleColor='#667788')
                         .configure_legend(labelColor='#C8D8E8', titleColor='#C8D8E8'),
                    use_container_width=True
                )
            else:
                st.warning("歷史資料不足，無法進行亞當理論投影。")


def _calculate_futures_targets():
    """V82.0 台指期月K結算目標價推導 — fully preserved"""
    macro, _, _ = _load_engines()
    df = macro.get_single_stock_data("WTX=F", period="max")
    if df.empty or len(df) < 300:
        df = macro.get_single_stock_data("^TWII", period="max")
        ticker_name = "加權指數(模擬期指)"
    else:
        ticker_name = "台指期近月"
    if df.empty:
        return {"error": "無法下載數據"}

    df = df.reset_index().loc[:, ~df.reset_index().columns.duplicated()]
    if 'Date' not in df.columns:
        df.rename(columns={'index': 'Date'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df['YM'] = df['Date'].dt.to_period('M')

    s_dates = []
    for ym in df['YM'].unique():
        wed = df[(df['YM'] == ym) & (df['Date'].dt.weekday == 2)]
        if len(wed) >= 3:
            d   = wed.iloc[2]['Date']
            val = d.item() if hasattr(d, 'item') else d
            if not df[df['Date'] >= val].empty:
                s_dates.append(val)

    stats = []
    for i in range(len(s_dates) - 1):
        mask   = (df['Date'] > s_dates[i]) & (df['Date'] <= s_dates[i + 1])
        m_data = df.loc[mask]
        if not m_data.empty:
            h  = m_data['High'].max()
            l  = m_data['Low'].min()
            hv = float(h.item() if hasattr(h, 'item') else h)
            lv = float(l.item() if hasattr(l, 'item') else l)
            stats.append(hv - lv)

    if len(stats) < 12:
        return {"error": "資料不足"}

    l12   = stats[-12:]
    min_a = min(l12)
    avg_a = sum(l12) / 12
    max_a = max(l12)

    curr = df[df['Date'] > s_dates[-1]]
    if curr.empty:
        return {"error": "新合約未開始"}

    op_v   = float(curr.iloc[0]['Open'])
    cl_v   = float(curr.iloc[-1]['Close'])
    is_red = cl_v >= op_v
    sign   = 1 if is_red else -1
    targets = {
        "1B": op_v + sign * min_a * 0.5,
        "2B": op_v + sign * min_a,
        "3B": op_v + sign * avg_a,
        "HR": op_v + sign * max_a,
    }
    return {"name": ticker_name, "anc": op_v, "price": cl_v, "is_red": is_red, "t": targets}


# ══════════════════════════════════════════════════════════════════════════════
#  SUB-MODULE RENDERERS
# ══════════════════════════════════════════════════════════════════════════════

def render_1_1_hud():
    _render_section_header("1.1", "🚦", "MACRO RISK HUD")
    macro, _, _ = _load_engines()
    df      = st.session_state.get('df', pd.DataFrame())
    df_hash = f"{len(df)}_{list(df.columns)}" if not df.empty else "empty"

    if df.empty:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-icon">📂</div>
            <div class="empty-state-text">UPLOAD CB LIST TO ACTIVATE HUD</div>
        </div>""", unsafe_allow_html=True)
        return

    macro_data  = _get_macro_data(macro, df_hash)
    sig         = macro_data['signal']
    sig_color   = SIGNAL_PALETTE.get(sig, "#888888")
    sig_text    = SIGNAL_MAP.get(sig, "⚪ 未知")
    sig_emoji   = sig_text.split('：')[0] if '：' in sig_text else sig_text
    sig_desc    = sig_text.split('：')[1] if '：' in sig_text else ""
    ptt_ratio   = macro_data['ptt_ratio']
    ptt_str     = f"{ptt_ratio:.1f}%" if ptt_ratio != -1.0 else "N/A"
    pr90        = macro_data['price_distribution']['pr90']

    # ── 4-Column Glass HUD Row ──
    cols = st.columns(4)
    cards = [
        ("SIGNAL LIGHT",    sig_emoji, sig_desc,             sig_color,  "MARKET"),
        ("VIX FEAR INDEX",  f"{macro_data['vix']:.2f}", "高於25為警示", "#FF9A3C", "VIX"),
        ("PR90 HEAT",       f"{pr90:.2f}",        "高於130為過熱",   "#FF3131",  "PR90"),
        ("PTT SHORT RATIO", ptt_str,              "高於50%為危險",   "#00F5FF",  "PTT"),
    ]
    for col, (label, value, delta, color, tag) in zip(cols, cards):
        with col:
            _render_hud_card(label, value, delta, color, tag)

    # ── Signal Light Panel ──
    st.markdown(f"""
    <div class="signal-panel" style="border-color:{sig_color}33; margin-top:20px;">
        <div class="signal-dot" style="background:{sig_color}; box-shadow:0 0 12px {sig_color}, 0 0 28px {sig_color}66;"></div>
        <div>
            <div class="signal-text" style="color:{sig_color}; text-shadow:0 0 10px {sig_color}88;">{sig_text}</div>
            <div class="signal-sub">MARKET CONDITION · {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── TSE Deep Analysis ──
    tse = macro_data['tse_analysis']
    st.markdown("""<div style="font-family:'Orbitron',monospace;font-size:9px;letter-spacing:3px;
                             color:#334455;text-transform:uppercase;margin:14px 0 10px;">
        ▸ TAIWAN WEIGHTED INDEX — DEEP ANALYSIS</div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="tse-grid">
        <div class="tse-cell">
            <div class="tse-cell-label">CURRENT LEVEL</div>
            <div class="tse-cell-value" style="color:#00F5FF;font-family:'JetBrains Mono',monospace;">
                {tse['price']:.2f} <span style="font-size:12px;color:#667788;">{tse['momentum']}</span>
            </div>
        </div>
        <div class="tse-cell">
            <div class="tse-cell-label">MAGIC MA TREND</div>
            <div class="tse-cell-value">{tse['magic_ma']}</div>
        </div>
        <div class="tse-cell">
            <div class="tse-cell-label">GRANVILLE RULE</div>
            <div class="tse-cell-value">{tse['granville']}</div>
        </div>
    </div>
    <div class="deduct-bar">
        DEDUCT &amp; SLOPE — {' &nbsp;|&nbsp; '.join(tse['deduct_slope'])}
    </div>""", unsafe_allow_html=True)


def render_1_2_thermometer():
    _render_section_header("1.2", "🌡️", "BULL/BEAR THERMOMETER")
    macro, _, _ = _load_engines()

    if 'high_50_sentiment' not in st.session_state:
        st.session_state.high_50_sentiment = None

    if st.button("▶  REFRESH MARKET TEMPERATURE", key="btn_sentiment"):
        with st.spinner("ANALYZING HIGH-PRICE LEADERS…"):
            st.session_state.high_50_sentiment = macro.analyze_high_50_sentiment()

    if not st.session_state.high_50_sentiment:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-icon">🌡️</div>
            <div class="empty-state-text">CLICK BUTTON TO ANALYZE</div>
        </div>""", unsafe_allow_html=True)
        return

    sentiment = st.session_state.high_50_sentiment
    if "error" in sentiment:
        st.error(sentiment["error"])
        return

    bull = sentiment['bull_ratio']
    bear = sentiment['bear_ratio']
    mood = sentiment['sentiment']
    total = sentiment['total']

    # Determine colors
    if bull >= 65:
        mood_color, mood_label = "#FF3131", "🔥 強勢多頭 · BULL DOMINANT"
    elif bull >= 50:
        mood_color, mood_label = "#00FF7F", "✅ 多方略優 · BULLISH"
    elif bull >= 35:
        mood_color, mood_label = "#FFD700", "⚡ 多空交戰 · NEUTRAL"
    else:
        mood_color, mood_label = "#00F5FF", "🧊 空頭市場 · BEARISH"

    # HUD row
    _render_hud_row([
        ("MARKET MOOD", mood, f"Based on {total} stocks", mood_color, "SENTIMENT"),
        ("BULL RATIO", f"{bull:.1f}%", "Above 87MA",  "#FF3131", "BULL"),
        ("BEAR RATIO", f"{bear:.1f}%", "Below 87MA",  "#00F5FF", "BEAR"),
        ("SIGNAL",     mood_label.split('·')[0].strip(), "", mood_color, "SIGNAL"),
    ])

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Plotly gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=bull,
        delta={'reference': 50, 'valueformat': '.1f', 'suffix': '%'},
        title={'text': "BULL RATIO (87MA)", 'font': {'family': 'Orbitron', 'color': '#FFD700', 'size': 13}},
        number={'font': {'family': 'JetBrains Mono', 'color': '#FFFFFF', 'size': 40}, 'suffix': '%'},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#334455',
                     'tickfont': {'family': 'Orbitron', 'color': '#334455', 'size': 9}},
            'bar': {'color': mood_color, 'thickness': 0.22},
            'bgcolor': 'rgba(0,0,0,0)',
            'bordercolor': 'rgba(0,245,255,0.15)',
            'steps': [
                {'range': [0,  35], 'color': 'rgba(0,245,255,0.10)'},
                {'range': [35, 65], 'color': 'rgba(255,215,0,0.08)'},
                {'range': [65,100], 'color': 'rgba(255,49,49,0.12)'},
            ],
            'threshold': {
                'line': {'color': '#FFD700', 'width': 3},
                'thickness': 0.78, 'value': 50
            }
        }
    ))
    fig.update_layout(
        height=280,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=40, b=10, l=20, r=20),
        font=dict(family='Rajdhani')
    )
    st.plotly_chart(fig, use_container_width=True)

    # Status bar
    st.markdown(f"""
    <div style="background:rgba(0,0,0,0.4);border:1px solid {mood_color}44;border-radius:10px;
                padding:14px 20px;text-align:center;font-family:'Rajdhani',sans-serif;
                font-size:18px;font-weight:700;letter-spacing:2px;color:{mood_color};
                box-shadow:0 0 16px {mood_color}22;margin-top:4px;">
        {mood_label}
    </div>""", unsafe_allow_html=True)


def render_1_3_pr90():
    _render_section_header("1.3", "📊", "PR90 CHIP DISTRIBUTION")
    macro, _, _ = _load_engines()
    df      = st.session_state.get('df', pd.DataFrame())
    df_hash = f"{len(df)}_{list(df.columns)}" if not df.empty else "empty"

    if df.empty:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <div class="empty-state-text">UPLOAD CB LIST TO GENERATE CHART</div>
        </div>""", unsafe_allow_html=True)
        return

    macro_data = _get_macro_data(macro, df_hash)
    price_dist = macro_data.get('price_distribution', {})
    chart_data = price_dist.get('chart_data')

    if chart_data is None or chart_data.empty:
        st.warning("無法生成籌碼分佈圖，請檢查 CB 清單中的價格欄位。")
        return

    pr90 = price_dist.get('pr90', 0)
    pr75 = price_dist.get('pr75', 0)
    avg  = price_dist.get('avg',  0)

    _render_hud_row([
        ("PR90 OVERHEATING LINE", f"{pr90:.2f}", "90% CB below this", "#FF3131",  "PR90"),
        ("PR75 OPPORTUNITY LINE", f"{pr75:.2f}", "75% CB below this", "#FFD700",  "PR75"),
        ("MARKET AVG PRICE",      f"{avg:.2f}",  "All CB average",    "#00F5FF",  "AVG"),
    ])

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Zone coloring via DataFrame column
    chart_data = chart_data.copy()
    def _zone(label):
        try:
            mid = float(str(label).split('~')[0])
        except Exception:
            return "正常區"
        if mid >= pr90: return "PR90 過熱區"
        if mid >= pr75: return "PR75 警示區"
        return "正常區"
    chart_data['區域'] = chart_data['區間'].apply(_zone)

    bar = (
        alt.Chart(chart_data)
        .mark_bar(opacity=0.90, cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
        .encode(
            x=alt.X('區間:N', sort=None, title=None,
                    axis=alt.Axis(labelColor='#556070', labelFontSize=10,
                                  labelFont='JetBrains Mono', grid=False, ticks=False,
                                  domainColor='rgba(0,245,255,0.1)')),
            y=alt.Y('數量:Q', title='VOLUME',
                    axis=alt.Axis(labelColor='#556070', titleColor='#556070',
                                  gridColor='rgba(0,245,255,0.05)', tickColor='transparent',
                                  labelFont='JetBrains Mono', labelFontSize=10)),
            color=alt.Color('區域:N',
                scale=alt.Scale(
                    domain=["正常區", "PR75 警示區", "PR90 過熱區"],
                    range=["#1A6CA8", "#C8A000", "#C82828"]
                ),
                legend=alt.Legend(orient='top', labelColor='#8899AA', titleColor='#556070',
                                  labelFont='Rajdhani', titleFont='Orbitron',
                                  titleFontSize=8, labelFontSize=12, symbolSize=80)),
            tooltip=[
                alt.Tooltip('區間:N', title='RANGE'),
                alt.Tooltip('數量:Q', title='COUNT'),
                alt.Tooltip('區域:N', title='ZONE'),
            ]
        )
        .properties(height=320)
        .configure_view(fill='#06090E', strokeOpacity=0)
        .configure_title(color='#FFD700')
    )
    st.altair_chart(bar, use_container_width=True)

    # Legend note
    st.markdown("""
    <div style="display:flex;gap:20px;font-family:'Rajdhani';font-size:12px;
                letter-spacing:1px;opacity:0.7;margin-top:-4px;padding:0 4px;">
        <span style="color:#4490C8">■ NORMAL ZONE</span>
        <span style="color:#C8A000">■ PR75 WARNING</span>
        <span style="color:#C82828">■ PR90 OVERHEATING</span>
    </div>""", unsafe_allow_html=True)


def render_1_4_heatmap():
    _render_section_header("1.4", "🗺️", "SECTOR HEAT RADAR")
    macro, kb, _ = _load_engines()
    df = st.session_state.get('df', pd.DataFrame())

    if df.empty:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-icon">🗺️</div>
            <div class="empty-state-text">UPLOAD CB LIST TO SCAN SECTORS</div>
        </div>""", unsafe_allow_html=True)
        return

    if 'sector_heatmap' not in st.session_state:
        st.session_state.sector_heatmap = pd.DataFrame()

    if st.button("▶  SCAN SECTOR HEAT", key="btn_heatmap"):
        with st.spinner("ANALYZING SECTOR CAPITAL FLOWS…"):
            st.session_state.sector_heatmap = macro.analyze_sector_heatmap(df, kb)

    if st.session_state.sector_heatmap.empty:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-icon">📡</div>
            <div class="empty-state-text">AWAITING SCAN — CLICK BUTTON ABOVE</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown("""
    <div style="font-family:'Rajdhani';font-size:13px;color:#556070;letter-spacing:1px;
                border-left:2px solid rgba(0,245,255,0.2);padding:6px 12px;margin-bottom:14px;">
        「多頭比例」= 各族群中股價站上 87MA 生命線之比例
    </div>""", unsafe_allow_html=True)

    heatmap_df = st.session_state.sector_heatmap.copy()

    def colorize_ratio(val):
        try:
            v = float(val)
            if v >= 70: return 'background-color:rgba(255,49,49,0.22);color:#FF9090;font-weight:700'
            if v >= 50: return 'background-color:rgba(255,215,0,0.18);color:#FFD700;font-weight:700'
            return 'background-color:rgba(0,245,255,0.10);color:#7AF5FF'
        except Exception:
            return ''

    styled = heatmap_df.style.applymap(colorize_ratio, subset=['多頭比例 (%)'])
    st.dataframe(styled, use_container_width=True)


def render_1_5_turnover():
    _render_section_header("1.5", "💹", "VOLUME GRAVITY CENTER — TOP 100")
    macro, _, _ = _load_engines()
    _render_leader_dashboard(
        session_state_key="w15_data",
        fetch_function=macro.get_dynamic_turnover_leaders,
        top_n=100,
        sort_key_name="成交值"
    )


def render_1_6_trend_radar():
    _render_section_header("1.6", "👑", "HIGH-PRICE TREND RADAR — TOP 50")
    macro, _, _ = _load_engines()
    _render_leader_dashboard(
        session_state_key="w16_data",
        fetch_function=macro.get_high_price_leaders,
        top_n=50,
        sort_key_name="股價"
    )


def render_1_7_predator():
    _render_section_header("1.7", "🎯", "WTX PREDATOR — SETTLEMENT TARGETS")

    st.markdown("""
    <div style="background:rgba(255,215,0,0.05);border:1px solid rgba(255,215,0,0.2);
                border-radius:10px;padding:12px 18px;font-family:'Rajdhani';font-size:14px;
                color:#AABBCC;letter-spacing:1px;margin-bottom:20px;">
        💡 <strong style="color:#FFD700;">獨門戰法</strong>：利用過去 12 個月結算慣性，推導本月台指期 (TX) 的「虛擬 K 棒」與目標價
    </div>""", unsafe_allow_html=True)

    if st.button("▶  DERIVE WTX SETTLEMENT TARGETS", key="btn_futures"):
        with st.spinner("CALCULATING FUTURES TARGETS…"):
            st.session_state['futures_result'] = _calculate_futures_targets()

    res = st.session_state.get('futures_result', None)

    if res is None:
        st.markdown("""<div class="empty-state">
            <div class="empty-state-icon">🎯</div>
            <div class="empty-state-text">AWAITING DERIVATION COMMAND</div>
        </div>""", unsafe_allow_html=True)
        return

    if "error" in res:
        st.markdown(f"""
        <div style="background:rgba(255,49,49,0.08);border:1px solid rgba(255,49,49,0.3);
                    border-radius:10px;padding:14px 18px;color:#FF6666;font-family:'Rajdhani';">
            ⚠️ {res['error']}
        </div>""", unsafe_allow_html=True)
        return

    is_red  = res['is_red']
    c_bull  = "#FF3131"
    c_bear  = "#00F5FF"
    c_main  = c_bull if is_red else c_bear
    polarity = "🔴 多方控盤" if is_red else "🟢 空方控盤"
    bias_str = f"+{res['price']-res['anc']:.0f}" if res['price'] >= res['anc'] else f"{res['price']-res['anc']:.0f}"

    # Header banner
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{c_main}14,{c_main}06);
                border:1px solid {c_main}44;border-radius:12px;
                padding:16px 22px;display:flex;align-items:center;gap:14px;margin-bottom:18px;">
        <div style="font-family:'Orbitron';font-size:20px;font-weight:900;color:{c_main};
                    text-shadow:0 0 12px {c_main}88;">{polarity}</div>
        <div style="font-family:'Rajdhani';font-size:14px;color:#778899;letter-spacing:2px;">{res['name']}</div>
        <div style="margin-left:auto;font-family:'JetBrains Mono';font-size:13px;color:#889AAA;">
            {"🔥 易收長紅" if is_red else "💀 易收長黑"}
        </div>
    </div>""", unsafe_allow_html=True)

    # Top 2 HUD
    _render_hud_row([
        ("ANCHOR OPEN",  f"{res['anc']:.0f}",   "定錨開盤價",  "#FFD700",  "ANCHOR"),
        ("CURRENT PRICE",f"{res['price']:.0f}", bias_str,     c_main,     "NOW"),
    ])

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Baseball targets
    def hit_check(tg):
        return ("✅ REACHED", "#00FF7F") if (is_red and res['price'] >= tg) or \
               (not is_red and res['price'] <= tg) else ("⏳ PENDING", "#556070")

    base_config = [
        ("1B", "1壘 — SINGLE",   c_main + "22", c_main),
        ("2B", "2壘 — DOUBLE",   c_main + "33", c_main),
        ("3B", "3壘 — TRIPLE",   c_main + "44", c_main),
        ("HR", "HR — HOME RUN",  "#FF3131"+"33", "#FF3131"),
    ]
    base_html_parts = []
    for k, label, bg, bc in base_config:
        val = res['t'][k]
        status, st_color = hit_check(val)
        base_html_parts.append(f"""
        <div class="base-card" style="background:{bg};border:1px solid {bc}55;">
            <div class="base-card::before" style="background:{bc};"></div>
            <div class="base-card-label" style="color:{bc};">{label}</div>
            <div class="base-card-value">{val:.0f}</div>
            <div class="base-card-status" style="color:{st_color};">{status}</div>
        </div>""")

    st.markdown(f'<div class="base-grid">{"".join(base_html_parts)}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Altair Baseball K-Bar Chart — fully preserved ──
    chart_df = pd.DataFrame({
        "Label":     ["本月"],
        "Anchor":    [res['anc']],
        "Current":   [res['price']],
        "Target_HR": [res['t']['HR']],
        "Target_1B": [res['t']['1B']],
        "Target_2B": [res['t']['2B']],
        "Target_3B": [res['t']['3B']],
    })

    bar_color  = "#CC2222" if is_red else "#117755"
    ghost_c    = "#331111" if is_red else "#113322"
    base       = alt.Chart(chart_df).encode(x=alt.X('Label', axis=None))
    ghost      = (base.mark_bar(size=72, color=ghost_c, opacity=0.9)
                  .encode(y=alt.Y('Anchor', scale=alt.Scale(zero=False), title='INDEX'),
                          y2='Target_HR'))
    real       = (base.mark_bar(size=32, color=bar_color)
                  .encode(y='Anchor', y2='Current'))
    chart = ghost + real

    for k in ['1B', '2B', '3B']:
        chart += (
            base.mark_tick(color='#FFD700', thickness=2, size=80)
            .encode(y=f'Target_{k}')
            + base.mark_text(dx=50, align='left', color='#FFD700',
                             fontSize=13, fontWeight='bold', font='Rajdhani')
            .encode(y=f'Target_{k}', text=alt.value(f"{k}   {res['t'][k]:.0f}"))
        )
    chart += (
        base.mark_tick(color='#FF3131', thickness=4, size=90)
        .encode(y='Target_HR')
        + base.mark_text(dx=54, align='left', color='#FF3131',
                         fontSize=15, fontWeight='bold', font='Rajdhani')
        .encode(y='Target_HR', text=alt.value(f"HR   {res['t']['HR']:.0f}"))
    )

    st.markdown('<div class="chart-dark-wrap">', unsafe_allow_html=True)
    _, chart_col, _ = st.columns([1, 2, 1])
    with chart_col:
        st.altair_chart(
            chart.properties(height=460)
                 .configure_view(fill='#06090E', strokeOpacity=0)
                 .configure_axis(labelColor='#556070', titleColor='#556070',
                                 gridColor='rgba(0,245,255,0.06)'),
            use_container_width=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:right;font-family:'JetBrains Mono';font-size:10px;
                color:#334455;letter-spacing:2px;margin-top:10px;">
        LAST UPDATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════
RENDER_MAP = {
    "1.1": render_1_1_hud,
    "1.2": render_1_2_thermometer,
    "1.3": render_1_3_pr90,
    "1.4": render_1_4_heatmap,
    "1.5": render_1_5_turnover,
    "1.6": render_1_6_trend_radar,
    "1.7": render_1_7_predator,
}


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def render():
    """Tab 1 — Titan OS God-Tier Glass-HUD Terminal"""

    _inject_css()

    if 'tab1_active' not in st.session_state:
        st.session_state.tab1_active = "1.1"

    active = st.session_state.tab1_active

    # ── MASTHEAD ──────────────────────────────────────────────
    st.markdown("""
    <div class="titan-masthead">🛡️ MACRO RISK COMMAND CENTER</div>
    <div class="titan-masthead-sub">TITAN SOP · REAL-TIME MARKET INTELLIGENCE PLATFORM</div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    #  COMMAND DECK — 7 NAV BUTTONS
    # ══════════════════════════════════════════════════════════
    st.markdown('<div class="cmd-deck">', unsafe_allow_html=True)
    st.markdown('<div class="cmd-deck-label">▸ COMMAND SELECT · MODULE NAVIGATION</div>', unsafe_allow_html=True)

    row1 = SUB_MODULES[:4]
    row2 = SUB_MODULES[4:]

    # Row 1
    r1_cols = st.columns(4)
    for col, (code, short, label) in zip(r1_cols, row1):
        with col:
            if active == code:
                st.markdown(f"""
                <div class="nav-active">
                    <div style="font-size:18px;margin-bottom:3px">{short}</div>
                    <div style="font-size:7px;letter-spacing:2px;color:#FFD70088">{code}</div>
                    <div style="font-size:11px;margin-top:2px">{label}</div>
                </div>""", unsafe_allow_html=True)
            else:
                if st.button(f"{short}\n{code}  {label}", key=f"nav_{code}",
                             use_container_width=True):
                    st.session_state.tab1_active = code
                    st.rerun()

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Row 2
    r2_cols = st.columns(4)
    for i, (code, short, label) in enumerate(row2):
        with r2_cols[i]:
            if active == code:
                st.markdown(f"""
                <div class="nav-active">
                    <div style="font-size:18px;margin-bottom:3px">{short}</div>
                    <div style="font-size:7px;letter-spacing:2px;color:#FFD70088">{code}</div>
                    <div style="font-size:11px;margin-top:2px">{label}</div>
                </div>""", unsafe_allow_html=True)
            else:
                if st.button(f"{short}\n{code}  {label}", key=f"nav_{code}",
                             use_container_width=True):
                    st.session_state.tab1_active = code
                    st.rerun()
    # 4th col spacer
    with r2_cols[3]:
        st.markdown("<div style='min-height:68px'></div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # cmd-deck

    # ══════════════════════════════════════════════════════════
    #  CONTENT SHELL
    # ══════════════════════════════════════════════════════════
    st.markdown('<div class="content-shell">', unsafe_allow_html=True)

    render_fn = RENDER_MAP.get(active)
    if render_fn:
        try:
            render_fn()
        except Exception as e:
            import traceback
            st.markdown(f"""
            <div style="background:rgba(255,49,49,0.08);border:1px solid rgba(255,49,49,0.35);
                        border-radius:10px;padding:16px 20px;font-family:'Rajdhani';">
                <div style="color:#FF6666;font-size:14px;font-weight:700;margin-bottom:6px;">
                    ❌ MODULE {active} RENDER ERROR
                </div>
                <div style="color:#888;font-size:13px;">{e}</div>
            </div>""", unsafe_allow_html=True)
            with st.expander("🔍 STACK TRACE"):
                st.code(traceback.format_exc())

    st.markdown('</div>', unsafe_allow_html=True)  # content-shell