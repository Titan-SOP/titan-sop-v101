# ui_desktop/tab1_macro.py
# Titan SOP V300 — 宏觀風控指揮中心 (Macro Risk Command Center)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  "DIRECTOR'S CUT V300"  —  Netflix × Palantir × Tesla            ║
# ║  4 MANDATORY UPGRADES:                                            ║
# ║    ✅ #1  Tactical Guide Dialog (Onboarding Modal)                ║
# ║    ✅ #2  Toast Notifications (replace st.success/info/warning)   ║
# ║    ✅ #3  Valkyrie AI Typewriter (_stream_text)                   ║
# ║    ✅ #4  Director's Cut Visuals (Hero/Poster/Glass — preserved)  ║
# ║  Logic: V82.0 fully preserved (MacroRiskEngine/Altair/Plotly)     ║
# ╚═══════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import datetime
import time

from macro_risk import MacroRiskEngine
from knowledge_base import TitanKnowledgeBase
from config import Config
from streamlit_option_menu import option_menu

# ══════════════════════════════════════════════════════════════════════════════
#  [UPGRADE #3] VALKYRIE AI TYPEWRITER — Sci-Fi Terminal Streaming
# ══════════════════════════════════════════════════════════════════════════════
def _stream_text(text, speed=0.018):
    """Character-by-character generator for st.write_stream"""
    for char in text:
        yield char
        time.sleep(speed)


# ══════════════════════════════════════════════════════════════════════════════
#  [UPGRADE #1] TACTICAL GUIDE DIALOG — Onboarding Modal
# ══════════════════════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導 — Macro Risk Command Center")
def _show_tactical_guide():
    st.markdown("""
    ### 指揮官，歡迎進入宏觀風控指揮中心

    **核心功能**：
    - **🚦 1.1 風控儀表 (MACRO HUD)**：三燈號系統 (🟢綠/🟡黃/🔴紅) 自動判定進攻/防守態勢，搭配 VIX、PR90 籌碼分佈、PTT 散戶情緒三重驗證。
    - **🌡️ 1.2 多空溫度計 / 📊 1.3 籌碼分佈**：高價權值股站上 87MA 的比例 = 市場體溫。籌碼分佈圖即時呈現全市場 CB 籌碼壓力，PR90 過熱線精準辨識危險區。
    - **🔥 1.4 族群熱度 (SECTOR MAP)**：台股 6 大板塊類別 × 動態熱力矩陣，一眼辨識哪個板塊在吸金、哪個板塊在失血。結合近 3 個月相對強度與資金輪動信號，精準鎖定主力進駐族群（共 30 大板塊全覆蓋）。
    - **💹 1.5 成交重心 / 👑 1.6 趨勢雷達**：全市場 TOP 100 成交重心即時掃描 + 高價權值股趨勢追蹤，附帶 87MA 扣抵預測與亞當理論反射路徑。
    - **🎯 1.7 台指獵殺 (WTX Predator)**：獨門戰法，利用過去 12 個月結算慣性推導本月台指期虛擬 K 棒，精準鎖定 1B/2B/3B/HR 結算目標價。

    **操作方式**：點擊上方海報欄切換模組 (1.1 風控儀表 → 1.2 多空溫度 → ... → 1.7 台指獵殺)。

    **狀態監控**：隨時留意三燈號系統訊號，紅燈期間所有慣性策略自動暫停。

    ---
    *建議：先查看 1.1 宏觀燈號確認市場狀態 → 再進入各子模組分析*
    """)

    if st.button("✅ 收到，進入戰情室 (Roger That)", type="primary", use_container_width=True):
        st.session_state['tab1_guided'] = True
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
SIGNAL_MAP = {
    "GREEN_LIGHT":  "🟢 綠燈：積極進攻",
    "YELLOW_LIGHT": "🟡 黃燈：區間操作",
    "RED_LIGHT":    "🔴 紅燈：現金為王",
}

SIGNAL_PALETTE = {
    "GREEN_LIGHT":  ("#00FF7F", "0,255,127"),
    "YELLOW_LIGHT": ("#FFD700", "255,215,0"),
    "RED_LIGHT":    ("#FF3131", "255,49,49"),
}

# (code, emoji, label-zh, label-en)
SUB_MODULES = [
    ("1.1", "🚦", "風控儀表",  "MACRO HUD"),
    ("1.2", "🌡️", "多空溫度",  "THERMO"),
    ("1.3", "📊", "籌碼分佈",  "PR90"),
    ("1.4", "🔥", "族群熱度",  "SECTOR MAP"),
    ("1.5", "💹", "成交重心",  "VOLUME"),
    ("1.6", "👑", "趨勢雷達",  "RADAR"),
    ("1.7", "🎯", "台指獵殺",  "PREDATOR"),
]


# ══════════════════════════════════════════════════════════════════════════════
#  CSS — TITAN OS CINEMATIC STYLES (PRESERVED + ENHANCED)
# ══════════════════════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;600;700&family=Orbitron:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">

<style>
/* ══════════════════════════════════════════════════════
   CSS VARIABLES — TITAN OS COLOR SYSTEM
══════════════════════════════════════════════════════ */
:root {
    --c-gold:    #FFD700;
    --c-cyan:    #00F5FF;
    --c-red:     #FF3131;
    --c-green:   #00FF7F;
    --c-dim:     #667788;
    --bg-card:   rgba(14, 20, 32, 0.88);
    --bg-glass:  rgba(255, 255, 255, 0.028);
    --bd-subtle: rgba(255, 255, 255, 0.07);
    --f-display: 'Bebas Neue', sans-serif;
    --f-body:    'Rajdhani', sans-serif;
    --f-mono:    'JetBrains Mono', monospace;
    --f-o:       'Orbitron', sans-serif;
}

/* ══════════════════════════════════════════════════════
   GLOBAL — Widen Streamlit container
══════════════════════════════════════════════════════ */
[data-testid="stMetricValue"] { font-size: 42px !important; }
[data-testid="stDataFrame"]   { font-size: 18px !important; }

/* ══════════════════════════════════════════════════════
   1. HERO BILLBOARD — Section 1.1 signal card
══════════════════════════════════════════════════════ */
.hero-container {
    position: relative;
    padding: 44px 40px 36px;
    border-radius: 22px;
    text-align: center;
    margin-bottom: 28px;
    background: linear-gradient(180deg, rgba(10,10,16,0) 0%, rgba(0,0,0,0.82) 100%);
    border: 1px solid rgba(255,255,255,0.09);
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 120%,
        var(--hero-glow, rgba(255,215,0,0.08)) 0%,
        transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: var(--f-display);
    font-size: 80px !important;
    font-weight: 900;
    line-height: 1;
    letter-spacing: 3px;
    color: #FFF;
    text-shadow: 0 0 40px var(--hero-color, rgba(255,215,0,0.6));
    margin-bottom: 12px;
}
.hero-subtitle {
    font-family: var(--f-mono);
    font-size: 22px !important;
    color: #777;
    letter-spacing: 6px;
    text-transform: uppercase;
}
.hero-badge {
    display: inline-block;
    margin-top: 18px;
    font-family: var(--f-mono);
    font-size: 13px;
    color: var(--hero-color, #FFD700);
    border: 1px solid var(--hero-color, #FFD700);
    border-radius: 30px;
    padding: 6px 22px;
    letter-spacing: 3px;
    background: rgba(0,0,0,0.4);
}
.hero-pulse {
    display: inline-block;
    width: 14px; height: 14px;
    border-radius: 50%;
    background: var(--hero-color, #FFD700);
    margin-right: 10px;
    box-shadow: 0 0 0 4px rgba(var(--hero-rgb, 255,215,0), 0.2),
                0 0 20px var(--hero-color, #FFD700);
    animation: pulse-anim 2s ease-in-out infinite;
}
@keyframes pulse-anim {
    0%,100% { opacity: 1; box-shadow: 0 0 0 4px rgba(var(--hero-rgb, 255,215,0),0.2), 0 0 20px var(--hero-color,#FFD700); }
    50%     { opacity: 0.7; box-shadow: 0 0 0 8px rgba(var(--hero-rgb, 255,215,0),0.1), 0 0 36px var(--hero-color,#FFD700); }
}

/* ══════════════════════════════════════════════════════
   2. NETFLIX POSTER RAIL
══════════════════════════════════════════════════════ */
.poster-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 10px;
    margin-bottom: 32px;
}
.poster-card {
    height: 160px;
    background: #0d1117;
    border: 1px solid #22282f;
    border-radius: 14px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: all 0.28s cubic-bezier(0.25, 0.8, 0.25, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.poster-card::after {
    content:'';
    position:absolute; bottom:0; left:15%; right:15%; height:2px;
    background: var(--poster-accent, #00F5FF);
    opacity: 0;
    transition: opacity 0.28s ease;
    border-radius: 2px;
}
.poster-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 16px 40px rgba(0,0,0,0.6);
    border-color: var(--c-cyan);
}
.poster-card:hover::after { opacity: 1; }
.poster-card.active {
    border: 2px solid var(--c-gold);
    background: linear-gradient(180deg,
        rgba(255,215,0,0.10) 0%,
        rgba(255,215,0,0.03) 60%,
        transparent 100%);
    box-shadow: 0 0 24px rgba(255,215,0,0.18),
                0 12px 40px rgba(0,0,0,0.5);
    transform: translateY(-6px) scale(1.03);
}
.poster-card.active::after { opacity: 1; background: var(--c-gold); }
.poster-icon { font-size: 38px; line-height: 1; filter: drop-shadow(0 0 8px rgba(255,255,255,0.2)); }
.poster-code {
    font-family: var(--f-mono);
    font-size: 9px;
    color: #444;
    letter-spacing: 2px;
}
.poster-text {
    font-family: var(--f-body);
    font-size: 28px;
    font-weight: 700;
    color: #DDE;
    letter-spacing: 0.5px;
}
.poster-tag {
    font-family: var(--f-mono);
    font-size: 26px;
    color: #333;
    letter-spacing: 2px;
    text-transform: uppercase;
}
.poster-card.active .poster-text { color: var(--c-gold); }
.poster-card.active .poster-code { color: rgba(255,215,0,0.45); }

/* nav button overlay (invisible) */
.poster-card.stButton > button {
    position: absolute; inset: 0;
    opacity: 0; cursor: pointer;
    width: 100%; height: 100%;
}

/* ══════════════════════════════════════════════════════
   3. RANK NUMBERS — Sections 1.5 & 1.6
══════════════════════════════════════════════════════ */
.rank-card {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 18px 22px;
    border-radius: 16px;
    margin-bottom: 12px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.065);
    position: relative;
    overflow: hidden;
    transition: transform 0.18s ease;
}
.rank-card:hover { transform: translateX(4px); }
.rank-card::before {
    content: '';
    position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
    background: var(--rc-accent, #FFD700);
    border-radius: 0 2px 2px 0;
}
.rank-num {
    font-family: var(--f-display);
    font-size: 54px;
    font-weight: 900;
    color: #333;
    min-width: 62px;
    text-align: right;
    line-height: 1;
}
.rank-1 .rank-num { color: #FFD700; text-shadow: 0 0 14px rgba(255,215,0,0.5); }
.rank-2 .rank-num { color: #C0C0C0; }
.rank-3 .rank-num { color: #CD7F32; }
.rank-info { flex: 1; min-width: 0; }
.rank-name {
    font-family: var(--f-body);
    font-size: 20px;
    font-weight: 700;
    color: #E0E8F0;
    margin-bottom: 3px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.rank-meta {
    font-family: var(--f-mono);
    font-size: 11px;
    color: #556677;
    letter-spacing: 1px;
}
.rank-value {
    font-family: var(--f-display);
    font-size: 32px;
    color: var(--rc-accent, #FFD700);
    text-align: right;
    flex-shrink: 0;
}
.rank-trend {
    font-family: var(--f-mono);
    font-size: 10px;
    text-align: right;
    margin-top: 2px;
}

/* ══════════════════════════════════════════════════════
   4. KPI METRIC CARDS  (64px values)
══════════════════════════════════════════════════════ */
.kpi-grid {
    display: grid;
    gap: 12px;
    margin-bottom: 22px;
}
.kpi-g4 { grid-template-columns: repeat(4,1fr); }
.kpi-g3 { grid-template-columns: repeat(3,1fr); }
.kpi-g2 { grid-template-columns: repeat(2,1fr); }

.kpi-card {
    position: relative;
    background: var(--bg-glass);
    border: 1px solid var(--bd-subtle);
    border-top: 2px solid var(--kc, #FFD700);
    border-radius: 16px;
    padding: 20px 18px 16px;
    overflow: hidden;
    transition: transform .18s ease;
}
.kpi-card:hover { transform: translateY(-2px); }
.kpi-card::after {
    content:'';
    position:absolute; top:0; right:0;
    width:80px; height:80px;
    background: radial-gradient(circle at top right, var(--kc, #FFD700), transparent 65%);
    opacity:0.04; pointer-events:none;
}
.kpi-label {
    font-family: var(--f-mono);
    font-size: 9px;
    font-weight: 700;
    color: var(--c-dim);
    text-transform: uppercase;
    letter-spacing: 2.5px;
    margin-bottom: 10px;
}
.kpi-value {
    font-family: var(--f-display);
    font-size: 64px;
    line-height: 0.92;
    color: #FFFFFF;
    margin-bottom: 10px;
    letter-spacing: 1px;
}
.kpi-sub {
    font-family: var(--f-body);
    font-size: 13px;
    color: var(--kc, #FFD700);
    opacity: 0.85;
    font-weight: 600;
}

/* ══════════════════════════════════════════════════════
   5. SECTION HEADER
══════════════════════════════════════════════════════ */
.sec-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 22px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.055);
}
.sec-icon { font-size: 28px; }
.sec-title {
    font-family: var(--f-display);
    font-size: 28px;
    letter-spacing: 2px;
    color: var(--c-gold);
    text-shadow: 0 0 18px rgba(255,215,0,0.3);
}
.sec-pill {
    margin-left: auto;
    font-family: var(--f-mono);
    font-size: 8px;
    color: rgba(255,215,0,0.38);
    border: 1px solid rgba(255,215,0,0.15);
    border-radius: 20px;
    padding: 4px 12px;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ══════════════════════════════════════════════════════
   6. CHART CONTAINER
══════════════════════════════════════════════════════ */
.chart-wrap {
    background: rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    padding: 16px 10px 6px;
    margin: 16px 0;
    overflow: hidden;
}

/* ══════════════════════════════════════════════════════
   7. TSE PANEL (1.1)
══════════════════════════════════════════════════════ */
.tse-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:12px; }
.tse-chip {
    background:rgba(0,0,0,0.32); border:1px solid rgba(255,255,255,0.058);
    border-radius:12px; padding:11px 13px;
}
.tsc-lbl {
    font-family:var(--f-mono); font-size:8px; color:rgba(150,162,178,0.5);
    text-transform:uppercase; letter-spacing:1.5px; margin-bottom:6px;
}
.tsc-val { font-family:var(--f-body); font-size:14px; font-weight:600; color:rgba(220,228,242,0.9); }
.tse-deduct {
    font-family:var(--f-mono); font-size:10px; color:#445566;
    background:rgba(0,0,0,0.25); border-radius:9px; padding:8px 14px;
    border-left:2px solid rgba(0,245,255,0.2); letter-spacing:0.4px;
}

/* ══════════════════════════════════════════════════════
   8. THERMOMETER VERDICT
══════════════════════════════════════════════════════ */
.thermo-verdict {
    font-family:var(--f-body); font-size:17px; font-weight:700;
    text-align:center; padding:16px 24px; border-radius:14px; margin-top:14px;
    border:1px solid rgba(var(--vr),0.3);
    background:rgba(var(--vr),0.055);
    color:rgb(var(--vr)); letter-spacing:0.5px;
}

/* ══════════════════════════════════════════════════════
   9. SCAN BUTTON / ACTION BUTTONS
══════════════════════════════════════════════════════ */
.action-wrap div.stButton > button {
    background: rgba(0,245,255,0.05) !important;
    border: 1px solid rgba(0,245,255,0.28) !important;
    color: rgba(0,245,255,0.85) !important;
    font-family: var(--f-mono) !important;
    font-size: 11px !important;
    letter-spacing: 2px !important;
    min-height: 46px !important;
    border-radius: 12px !important;
    text-transform: uppercase !important;
}
.action-wrap div.stButton > button:hover {
    background: rgba(0,245,255,0.10) !important;
    box-shadow: 0 0 20px rgba(0,245,255,0.2) !important;
    transform: none !important;
}

/* ══════════════════════════════════════════════════════
   10. LEADER TABLE
══════════════════════════════════════════════════════ */
.ldr-tbl { width:100%; border-collapse:collapse; font-family:var(--f-body); }
.ldr-tbl th {
    font-family:var(--f-mono); font-size:9px; font-weight:700;
    letter-spacing:2px; text-transform:uppercase;
    color:rgba(0,245,255,0.65); background:rgba(0,245,255,0.04);
    padding:10px 13px; border-bottom:1px solid rgba(0,245,255,0.10);
}
.ldr-tbl td { padding:9px 13px; border-bottom:1px solid rgba(255,255,255,0.03); color:rgba(210,220,235,0.82); font-size:14px; }
.ldr-tbl tr:hover td { background:rgba(0,245,255,0.025); }

/* ══════════════════════════════════════════════════════
   11. BASEBALL TARGETS (1.7)
══════════════════════════════════════════════════════ */
.bases-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:11px; margin:16px 0; }
.base-card {
    border-radius:16px; padding:18px 10px; text-align:center;
    border:1px solid rgba(255,255,255,0.068); background:rgba(255,255,255,0.022);
    transition:transform .18s ease;
}
.base-card:hover { transform:translateY(-2px); }
.base-card.hit  { border-color:rgba(0,255,127,0.35); background:rgba(0,255,127,0.04); }
.base-card.hr   { border-color:rgba(255,49,49,0.38);  background:rgba(255,49,49,0.04); }
.base-card.hr.hit { border-color:rgba(255,49,49,0.6); box-shadow:0 0 20px rgba(255,49,49,0.14); }
.base-name { font-family:var(--f-mono); font-size:10px; color:#445566; letter-spacing:2px; margin-bottom:9px; text-transform:uppercase; }
.base-price { font-family:var(--f-display); font-size:36px; color:#FFF; margin-bottom:8px; letter-spacing:1px; }
.base-status { font-family:var(--f-body); font-size:12px; font-weight:600; display:inline-block; padding:3px 12px; border-radius:20px; }
.hit  .base-status { background:rgba(0,255,127,0.14); color:#00FF7F; }
.miss .base-status { background:rgba(255,255,255,0.05); color:#445566; }
.hr   .base-status { background:rgba(255,49,49,0.12);  color:#FF6B6B; }

/* ══════════════════════════════════════════════════════
   12. CONTENT FRAME
══════════════════════════════════════════════════════ */
.content-frame {
    background: linear-gradient(175deg, #06090e 0%, #090c14 100%);
    border: 1px solid rgba(255,255,255,0.052);
    border-radius: 22px;
    padding: 28px 24px 32px;
    min-height: 420px;
    position: relative;
}
.content-frame::after {
    content:''; position:absolute; bottom:0; left:8%; right:8%; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,245,255,0.12) 50%,transparent);
}

/* ══════════════════════════════════════════════════════
   13. EMPTY STATE
══════════════════════════════════════════════════════ */
.empty-state {
    border:1px dashed rgba(255,255,255,0.08); border-radius:16px;
    padding:60px 30px; text-align:center;
}
.empty-icon { font-size:44px; opacity:0.25; margin-bottom:14px; }
.empty-text { font-family:var(--f-mono); font-size:13px; color:#334455; letter-spacing:2px; text-transform:uppercase; }

/* ══════════════════════════════════════════════════════
   14. CTRL BANNER (1.7 direction flag)
══════════════════════════════════════════════════════ */
.ctrl-flag {
    border-radius:14px; padding:16px 22px; text-align:center;
    font-family:var(--f-body); font-size:16px; font-weight:700;
    letter-spacing:0.5px; margin:14px 0 18px;
    border:1px solid rgba(var(--cf-rgb),0.25);
    background:rgba(var(--cf-rgb),0.06);
    color:rgb(var(--cf-rgb));
}

/* ══════════════════════════════════════════════════════
   15. TIMESTAMP FOOTER
══════════════════════════════════════════════════════ */
.titan-foot {
    font-family:var(--f-mono); font-size:9px;
    color:rgba(100,120,140,0.3); letter-spacing:2px;
    text-align:right; margin-top:18px; text-transform:uppercase;
}

/* ══════════════════════════════════════════════════════
   16. NAV DECK FRAME
══════════════════════════════════════════════════════ */
.nav-deck-frame {
    background:linear-gradient(165deg,#07080f 0%,#0a0b14 100%);
    border:1px solid rgba(255,255,255,0.06);
    border-radius:20px; padding:18px 14px 14px; margin-bottom:18px;
    position:relative; overflow:hidden;
}
.nav-deck-frame::after {
    content:''; position:absolute; top:0; left:10%; right:10%; height:1px;
    background:linear-gradient(90deg,transparent,rgba(255,215,0,0.4) 50%,transparent);
}
.nav-deck-label {
    font-family:var(--f-mono); font-size:8px; letter-spacing:4px;
    color:rgba(255,215,0,0.2); text-transform:uppercase; margin-bottom:14px; padding-left:2px;
}

/* ── POSTER RAIL NAV BUTTON — fully transparent clickable overlay ──────────
   Strategy: poster card renders FIRST (visual layer),
             button renders SECOND with negative margin-top to sit on top (hit layer).
   The button is 100% invisible; the poster card IS the visual.
─────────────────────────────────────────────────────────────────────────── */
.nav-deck-frame div[data-testid="stVerticalBlock"] div.stButton {
    margin-top: -170px !important;
    position: relative !important;
    z-index: 10 !important;
}
.nav-deck-frame div[data-testid="stVerticalBlock"] div.stButton > button {
    opacity: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    min-height: 170px !important;
    width: 100% !important;
    cursor: pointer !important;
}
.nav-deck-frame div[data-testid="stVerticalBlock"] div.stButton > button:hover,
.nav-deck-frame div[data-testid="stVerticalBlock"] div.stButton > button:focus,
.nav-deck-frame div[data-testid="stVerticalBlock"] div.stButton > button:active {
    opacity: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
.nav-deck-frame div[data-testid="stVerticalBlock"] div.stButton > button p {
    opacity: 0 !important;
    pointer-events: none !important;
}
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ENGINE CACHE  (V82 soul — unchanged)
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
#  REUSABLE UI PRIMITIVES (PRESERVED)
# ══════════════════════════════════════════════════════════════════════════════
def _sec_header(icon: str, title: str, pill: str = ""):
    pill_html = f'<span class="sec-pill">{pill}</span>' if pill else ""
    st.markdown(
        f'<div class="sec-header">'
        f'<span class="sec-icon">{icon}</span>'
        f'<span class="sec-title">{title}</span>'
        f'{pill_html}</div>',
        unsafe_allow_html=True
    )


def _kpi_card_html(label: str, value: str, sub: str, color: str = "#FFD700") -> str:
    return (
        f'<div class="kpi-card" style="--kc:{color};">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-sub">{sub}</div>'
        f'</div>'
    )


def _kpi_row(*cards):
    """cards = (label, value, sub, color) tuples"""
    n   = len(cards)
    cls = {2:"kpi-g2", 3:"kpi-g3", 4:"kpi-g4"}.get(n, "kpi-g4")
    inner = "".join(_kpi_card_html(l, v, s, c) for l, v, s, c in cards)
    st.markdown(f'<div class="kpi-grid {cls}">{inner}</div>', unsafe_allow_html=True)


def _rank_card_html(rank: int, name: str, ticker: str, industry: str,
                    value: str, sub: str, trend_status: str, accent: str) -> str:
    rank_cls = {1: "rank-1", 2: "rank-2", 3: "rank-3"}.get(rank, "")
    trend_color = "#FF4B4B" if "多頭" in str(trend_status) else "#26A69A" if "空頭" in str(trend_status) else "#667788"
    return f"""
<div class="rank-card {rank_cls}" style="--rc-accent:{accent};">
  <div class="rank-num">{rank}</div>
  <div class="rank-info">
    <div class="rank-name">{name} <span style="font-size:13px;color:#445566;font-family:var(--f-mono)">({ticker})</span></div>
    <div class="rank-meta">{industry}</div>
  </div>
  <div>
    <div class="rank-value" style="color:{accent}">{value}</div>
    <div class="rank-trend" style="color:{trend_color}">{sub}</div>
  </div>
</div>"""


# ══════════════════════════════════════════════════════════════════════════════
#  LEADER DASHBOARD  (V78.2 complete — logic unchanged)
#  [UPGRADE #2] Toast notifications  [UPGRADE #3] Typewriter for analysis
# ══════════════════════════════════════════════════════════════════════════════
def _render_leader_dashboard(session_state_key: str, fetch_function,
                              top_n: int, sort_key_name: str):
    macro, kb, strat = _load_engines()

    st.markdown(
        f'<div style="font-family:var(--f-mono);font-size:11px;color:#445566;'
        f'letter-spacing:1.5px;border-left:2px solid rgba(0,245,255,0.2);'
        f'padding:8px 14px;margin-bottom:18px;text-transform:uppercase;">'
        f'Scanning by {sort_key_name} · TOP {top_n} · V78.2 RADAR</div>',
        unsafe_allow_html=True
    )

    if session_state_key not in st.session_state:
        st.session_state[session_state_key] = pd.DataFrame()

    st.markdown('<div class="action-wrap">', unsafe_allow_html=True)
    if st.button(f"▶  SCAN  {sort_key_name}  TOP {top_n}", key=f"btn_{session_state_key}"):
        st.toast(f"🚀 掃描 {sort_key_name} TOP {top_n} 中…", icon="⏳")
        with st.spinner(f"SCANNING {sort_key_name} TOP {top_n} — PLEASE WAIT…"):
            st.session_state[session_state_key] = fetch_function(top_n=top_n)
        st.toast(f"✅ {sort_key_name} TOP {top_n} 掃描完成！", icon="🎯")
    st.markdown('</div>', unsafe_allow_html=True)

    leaders_df = st.session_state[session_state_key]
    if leaders_df.empty:
        st.markdown('<div class="empty-state"><div class="empty-icon">📡</div>'
                    '<div class="empty-text">AWAITING SCAN COMMAND</div></div>',
                    unsafe_allow_html=True)
        return
    if "error" in leaders_df.columns:
        st.toast(f"⚠️ {leaders_df.iloc[0]['error']}", icon="⚡")
        return

    # ── TOP 3 RANK CARDS ──────────────────────────────────────────────────────
    top3 = leaders_df.head(3)
    accents = ["#FFD700", "#C0C0C0", "#CD7F32"]
    cards_html = ""
    for i, (_, row) in enumerate(top3.iterrows()):
        cards_html += _rank_card_html(
            rank=int(row['rank']),
            name=row['name'],
            ticker=row['ticker'],
            industry=row['industry'],
            value=f"{row['current_price']:.2f}",
            sub=row['trend_status'],
            trend_status=row['trend_status'],
            accent=accents[i]
        )
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── REST AS TABLE ─────────────────────────────────────────────────────────
    rest = leaders_df.iloc[3:].copy()
    if not rest.empty:
        def style_status(s):
            if "多頭" in str(s): return f"<span style='color:#FF4B4B;font-weight:700'>{s}</span>"
            if "空頭" in str(s): return f"<span style='color:#26A69A;font-weight:700'>{s}</span>"
            return s
        def style_ded(s):
            if "助漲" in str(s): return f"<span style='color:#00FF7F'>{s}</span>"
            if "壓力" in str(s): return f"<span style='color:#FF3131'>{s}</span>"
            return s

        disp = rest.copy()
        disp['#']       = disp['rank']
        disp['代號']     = disp['ticker']
        disp['名稱']     = disp['name']
        disp['產業']     = disp['industry']
        disp['現價']     = disp['current_price'].apply(lambda x: f"{x:.2f}")
        disp['趨勢']     = disp['trend_status'].apply(style_status)
        disp['天數']     = disp['trend_days']
        disp['87MA扣抵'] = disp['deduction_signal'].apply(style_ded)

        cols_show = ['#','代號','名稱','產業','現價','趨勢','天數','87MA扣抵']
        tbl_html  = disp[cols_show].to_html(escape=False, index=False)
        tbl_html  = tbl_html.replace('<table', '<table class="ldr-tbl"')
        st.markdown(tbl_html, unsafe_allow_html=True)

    st.divider()

    # ── DEEP PREDICTION ───────────────────────────────────────────────────────
    st.markdown('<div style="font-family:var(--f-display);font-size:22px;color:#00F5FF;'
                'letter-spacing:3px;margin:16px 0 12px;">DEEP DIVE ANALYSIS</div>',
                unsafe_allow_html=True)

    options      = [f"{r['rank']}. {r['name']} ({r['ticker']})" for _, r in leaders_df.iterrows()]
    selected_str = st.selectbox("選擇分析標的", options=options,
                                 key=f"select_{session_state_key}")
    if not selected_str:
        return

    sel           = leaders_df[leaders_df['rank'] == int(selected_str.split('.')[0])].iloc[0]
    stock_df      = sel['stock_df']
    deduction_df  = sel['deduction_df']
    adam_df        = sel['adam_df']
    current_price = sel['current_price']
    ma87          = sel['ma87']

    bias_pct     = ((current_price - ma87) / ma87) * 100 if ma87 > 0 else 0
    is_recent_bo = (current_price > ma87) and (stock_df['Close'].iloc[-5] < ma87)
    granville    = strat._get_granville_status(current_price, ma87, is_recent_bo, bias_pct)
    bias_col     = "#00FF7F" if bias_pct >= 0 else "#FF3131"

    _kpi_row(
        ("現價",       f"{current_price:.2f}", f"87MA 乖離 {bias_pct:+.1f}%",    bias_col),
        ("格蘭碧法則", granville,               f"生命線 {ma87:.2f}",             "#FFD700"),
        ("趨勢波段",   sel['trend_status'],     f"持續 {sel['trend_days']} 天",   "#00F5FF"),
        ("扣抵預判",   sel['deduction_signal'], f"斜率 {sel['ma87_slope']:.2f}°", "#FF9A3C"),
    )

    # [UPGRADE #3] Typewriter summary for deep analysis
    analysis_text = (
        f"【{sel['name']} ({sel['ticker']}) 深度分析摘要】\n"
        f"現價 {current_price:.2f}，87MA 生命線 {ma87:.2f}，乖離率 {bias_pct:+.1f}%。\n"
        f"格蘭碧法則判定：{granville}。"
        f"趨勢狀態：{sel['trend_status']}（持續 {sel['trend_days']} 天）。\n"
        f"87MA 扣抵預判：{sel['deduction_signal']}（斜率 {sel['ma87_slope']:.2f}°）。\n"
    )
    if f"streamed_{session_state_key}_{sel['ticker']}" not in st.session_state:
        st.write_stream(_stream_text(analysis_text, speed=0.012))
        st.session_state[f"streamed_{session_state_key}_{sel['ticker']}"] = True
    else:
        st.markdown(f'<div style="font-family:var(--f-mono);font-size:12px;color:rgba(200,215,230,0.6);line-height:1.7;padding:8px 0;">{analysis_text}</div>', unsafe_allow_html=True)

    tab_d, tab_a = st.tabs(["📉 87MA 扣抵值預測", "🔄 亞當理論二次反射"])

    with tab_d:
        if not deduction_df.empty:
            cdata = deduction_df.reset_index()
            cdata['Current_Price'] = current_price
            base   = alt.Chart(cdata).encode(x='Date:T')
            line_d = (base.mark_line(color='#FFD700', strokeDash=[6, 3])
                      .encode(y=alt.Y('Deduction_Value', title='Price'),
                              tooltip=['Date', 'Deduction_Value'])
                      .properties(title=alt.TitleParams("未來 60 日 87MA 扣抵值預測", color='#FFD700')))
            line_c = base.mark_line(color='#00F5FF', strokeWidth=1.5).encode(y='Current_Price')
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.altair_chart(
                (line_d + line_c).interactive()
                .configure_view(strokeOpacity=0, fill='rgba(0,0,0,0)')
                .configure_axis(gridColor='rgba(0,245,255,0.07)', labelColor='#445566', titleColor='#445566'),
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.toast("⚠️ 歷史資料不足，無法預測均線扣抵值", icon="⚡")

    with tab_a:
        if not adam_df.empty:
            hist_d = stock_df.iloc[-60:].reset_index(); hist_d['Type'] = '歷史路徑'
            proj_d = adam_df.reset_index();             proj_d['Type'] = '亞當投影'
            proj_d.rename(columns={'Projected_Price': 'Close'}, inplace=True)
            combined     = pd.concat([hist_d[['Date', 'Close', 'Type']], proj_d[['Date', 'Close', 'Type']]])
            adam_colors  = alt.Scale(domain=['歷史路徑', '亞當投影'], range=['#00F5FF', '#FFD700'])
            chart = (alt.Chart(combined).mark_line(strokeWidth=2)
                     .encode(x='Date:T',
                             y=alt.Y('Close', title='Price', scale=alt.Scale(zero=False)),
                             color=alt.Color('Type:N', scale=adam_colors),
                             strokeDash='Type:N')
                     .properties(title=alt.TitleParams("亞當理論二次反射路徑圖", color='#FFD700'))
                     .interactive())
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.altair_chart(
                chart.configure_view(strokeOpacity=0, fill='rgba(0,0,0,0)')
                     .configure_axis(gridColor='rgba(0,245,255,0.07)', labelColor='#445566', titleColor='#445566')
                     .configure_legend(labelColor='#C8D8E8', titleColor='#C8D8E8'),
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.toast("⚠️ 歷史資料不足，無法進行亞當理論投影", icon="⚡")


# ══════════════════════════════════════════════════════════════════════════════
#  FUTURES TARGETS  (V82.0 math — unchanged)
# ══════════════════════════════════════════════════════════════════════════════
def _calculate_futures_targets():
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
            h  = m_data['High'].max();  l  = m_data['Low'].min()
            hv = float(h.item() if hasattr(h, 'item') else h)
            lv = float(l.item() if hasattr(l, 'item') else l)
            stats.append(hv - lv)

    if len(stats) < 12:
        return {"error": "資料不足"}

    l12   = stats[-12:]
    min_a = min(l12);  avg_a = sum(l12) / 12;  max_a = max(l12)

    curr = df[df['Date'] > s_dates[-1]]
    if curr.empty:
        return {"error": "新合約未開始"}

    op_v   = float(curr.iloc[0]['Open'])
    cl_v   = float(curr.iloc[-1]['Close'])
    is_red = cl_v >= op_v
    sign   = 1 if is_red else -1
    return {
        "name": ticker_name, "anc": op_v, "price": cl_v, "is_red": is_red,
        "t": {
            "1B": op_v + sign * min_a * 0.5,
            "2B": op_v + sign * min_a,
            "3B": op_v + sign * avg_a,
            "HR": op_v + sign * max_a,
        }
    }


# ══════════════════════════════════════════════════════════════════════════════
#  SUB-MODULE RENDERERS
# ══════════════════════════════════════════════════════════════════════════════

def render_1_1_hud():
    # ══════════════════════════════════════════════════════════════════════
    # 1.1 宏觀風控儀表 — 第一性原則重建
    # 核心邏輯：三燈號系統 = VIX × PR90 × PTT 三重交叉驗證
    #   GREEN：VIX<20 且 PR90<115 且 PTT<50%  → 系統性風險低，積極進攻
    #   YELLOW：任一指標進入警戒區            → 區間操作，控制倉位
    #   RED：VIX>30 或 PR90>130 或 PTT>65%   → 極端恐慌/過熱，現金為王
    # ══════════════════════════════════════════════════════════════════════
    _sec_header("🚦", "宏觀風控儀表 · 三重驗證戰情系統", "MACRO HUD v3.0")
    macro, _, _ = _load_engines()
    df      = st.session_state.get('df', pd.DataFrame())
    df_hash = f"{len(df)}_{list(df.columns)}" if not df.empty else "empty"

    if df.empty:
        st.markdown("""
<div class="hero-container">
  <div class="hero-title" style="font-size:60px!important;color:#222;">AWAITING DATA</div>
  <div class="hero-subtitle">請上傳 CB 清單以啟動戰情室</div>
</div>""", unsafe_allow_html=True)
        return

    md  = _get_macro_data(macro, df_hash)
    sig = md['signal']
    col, rgb = SIGNAL_PALETTE.get(sig, ("#FFD700", "255,215,0"))
    sig_text = SIGNAL_MAP.get(sig, "⚪ UNKNOWN")
    parts    = sig_text.split("：")
    sig_main = parts[0] if parts else sig_text
    sig_desc = parts[1] if len(parts) > 1 else ""

    vix     = md['vix']
    pr90    = md['price_distribution']['pr90']
    ptt     = md['ptt_ratio']
    ptt_txt = f"{ptt:.1f}%" if ptt != -1.0 else "N/A"
    tse     = md['tse_analysis']

    # ── 指標評級 ───────────────────────────────────────────────────────────
    # VIX 評級
    if vix > 35:   vix_lv, vix_col = "💀 極端恐慌", "#FF3131"
    elif vix > 25: vix_lv, vix_col = "🔴 高度警戒", "#FF3131"
    elif vix > 20: vix_lv, vix_col = "🟡 溫和警戒", "#FFD700"
    else:          vix_lv, vix_col = "🟢 市場平靜", "#00FF7F"

    # PR90 評級（CB籌碼壓力）
    if pr90 > 135:   pr90_lv, pr90_col = "🔴 嚴重過熱 — 獲利了結", "#FF3131"
    elif pr90 > 120: pr90_lv, pr90_col = "🟡 籌碼偏高 — 謹慎追高", "#FFD700"
    elif pr90 > 100: pr90_lv, pr90_col = "🟢 健康區間 — 正常操作", "#00FF7F"
    else:            pr90_lv, pr90_col = "🔵 籌碼偏低 — 可積極佈局", "#00F5FF"

    # PTT 評級（散戶情緒反向指標）
    if ptt != -1.0:
        if ptt > 65:   ptt_lv, ptt_col = "🔴 散戶過度悲觀 → 反向看多訊號", "#FF3131"
        elif ptt > 50: ptt_lv, ptt_col = "🟡 散戶偏空 → 市場謹慎", "#FFD700"
        elif ptt > 35: ptt_lv, ptt_col = "🟢 散戶情緒平衡", "#00FF7F"
        else:          ptt_lv, ptt_col = "⚠️ 散戶過度樂觀 → 反向注意", "#FF9A3C"
    else:
        ptt_lv, ptt_col = "⚪ 數據無法取得", "#667788"

    # TSE 技術面
    tse_price = tse.get('price', 0)
    tse_mom   = tse.get('momentum', 'N/A')
    tse_gran  = tse.get('granville', 'N/A')
    tse_ma    = tse.get('magic_ma', 'N/A')
    deducts   = " | ".join(tse.get('deduct_slope', ["計算中…"]))

    # 三重驗證總評分（0~3，判定燈號合理性）
    score = 0
    if vix <= 20:             score += 1
    if pr90 <= 115:           score += 1
    if ptt != -1.0 and ptt <= 50: score += 1
    score_txt   = "三重確認 ✅" if score == 3 else f"{score}/3 訊號確認"
    score_color = "#00FF7F" if score == 3 else "#FFD700" if score == 2 else "#FF3131"

    # VIX 歷史情境對照
    vix_context = (
        "歷史對照：VIX>40 對應金融危機（2008/2020）極端底部，通常為千載難逢買點。"
        if vix > 40 else
        "歷史對照：VIX 25~35 對應修正行情，波動劇烈，需降低倉位等待企穩。"
        if vix > 25 else
        "歷史對照：VIX 20~25 為市場轉折敏感區，宜縮減高風險部位。"
        if vix > 20 else
        "歷史對照：VIX<20 為牛市常態，市場波動可控，可正常佈局。"
    )

    # ── 英雄告示牌 ──────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="hero-container" style="--hero-color:{col};--hero-glow:rgba({rgb},0.10);--hero-rgb:{rgb};">
  <div style="display:inline-flex;align-items:center;margin-bottom:6px;">
    <span class="hero-pulse" style="--hero-color:{col};--hero-rgb:{rgb};"></span>
    <span style="font-family:var(--f-mono);font-size:11px;color:rgba({rgb},0.6);letter-spacing:3px;">TITAN SOP V300 · 三重驗證</span>
  </div>
  <div class="hero-title" style="--hero-color:{col};">{sig_main}</div>
  <div class="hero-subtitle" style="margin-top:8px;">{sig_desc}</div>
  <div style="display:flex;justify-content:center;gap:16px;margin-top:16px;flex-wrap:wrap;">
    <div style="font-family:var(--f-mono);font-size:12px;color:{vix_col};border:1px solid {vix_col};border-radius:20px;padding:5px 16px;">VIX {vix:.1f} — {vix_lv}</div>
    <div style="font-family:var(--f-mono);font-size:12px;color:{pr90_col};border:1px solid {pr90_col};border-radius:20px;padding:5px 16px;">PR90 {pr90:.1f} — {pr90_lv[:4]}</div>
    <div style="font-family:var(--f-mono);font-size:12px;color:{score_color};border:1px solid {score_color};border-radius:20px;padding:5px 16px;">{score_txt}</div>
  </div>
  <div class="hero-badge" style="margin-top:14px;">TITAN SOP V300 &nbsp;·&nbsp; {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</div>""", unsafe_allow_html=True)

    st.toast(f"{sig_main} — {sig_desc}  |  三重驗證 {score}/3", icon="🚦")

    # ── KPI 儀表板（8格）──────────────────────────────────────────────────
    _kpi_row(
        ("VIX 恐慌指數",    f"{vix:.2f}",  vix_lv,   vix_col),
        ("PR90 籌碼壓力",   f"{pr90:.1f}", pr90_lv[:8], pr90_col),
        ("PTT 散戶看空比",  ptt_txt,       ptt_lv[:10], ptt_col),
        ("訊號驗證強度",    f"{score}/3",  score_txt, score_color),
    )
    _kpi_row(
        ("加權指數",     f"{tse_price:,.0f}", "TSE 即時點位",  "#00F5FF"),
        ("動能方向",     tse_mom,             "MA 斜率判定",   "#FFD700"),
        ("格蘭碧法則",   tse_gran,            "生命線關係",    "#FF9A3C"),
        ("神奇均線",     tse_ma,              "87MA 狀態",     "#FF6BFF"),
    )

    # ── AI 戰術分析（Typewriter）────────────────────────────────────────────
    st.markdown("### 🧠 三重驗證 · 第一性原則戰術推演")
    st.markdown('<div style="background:rgba(0,0,0,0.4);border:1px solid rgba(0,245,255,0.1);border-radius:16px;padding:20px 24px;margin:12px 0;font-family:var(--f-mono);font-size:13px;color:rgba(200,215,230,0.85);line-height:1.9;">', unsafe_allow_html=True)

    analysis = f"""
═══════════════════════════════════════════════════════════
🚦 MACRO HUD v3.0 — 三重驗證戰情推演
   信號燈：{sig_text}  |  驗證強度：{score}/3
═══════════════════════════════════════════════════════════

【一、三燈號系統原理（為什麼是這個燈？）】
  三燈號系統由三個獨立指標交叉驗證決定：
  ① VIX（恐慌指數）：衡量選擇權市場對未來波動的預期
  ② PR90（籌碼分佈）：CB籌碼分佈的第90百分位，反映市場超漲程度
  ③ PTT 散戶情緒：散戶看空比例，作為反向指標使用
  
  當前燈號：{sig_text}
  觸發依據：VIX {vix:.1f} ({vix_lv}) | PR90 {pr90:.1f} ({pr90_lv[:8]}) | PTT {ptt_txt} ({ptt_lv[:10]})

【二、VIX 深度解讀（現值：{vix:.2f}）】
  VIX 的本質：S&P 500選擇權隱含波動率指數，代表市場對未來30天波動的「恐懼定價」。
  
  當前評級：{vix_lv}
  {vix_context}
  
  操作含義：{'VIX 高位通常是買點，但需等待VIX從峰值回落後才進場（峰值買 = 接飛刀）。' if vix > 25 else 'VIX 低位市場自滿，代表系統性風險被忽視，適合持股但需設好停損。' if vix < 15 else 'VIX 中性區間，跟著技術面操作即可，無特殊系統性風險。'}

【三、PR90 籌碼壓力解讀（現值：{pr90:.1f}）】
  PR90 的本質：CB 可轉換公司債的第90百分位價格，反映市場「過熱籌碼」的集中程度。
  
  當前評級：{pr90_lv}
  解讀：PR90 > 130 代表高價籌碼已嚴重堆積，若遭主力出貨，市場將面臨籌碼崩塌式下跌。
  {'⚠️ 目前籌碼壓力嚴重偏高，持股風險升高，建議降低高PR值個股的倉位。' if pr90 > 130 else '✅ 籌碼分佈尚在合理範圍，無立即性崩盤風險。' if pr90 <= 115 else '🟡 籌碼分佈偏高，注意高位個股的獲利了結壓力。'}

【四、PTT 散戶情緒（反向指標）解讀（現值：{ptt_txt}）】
  PTT 的本質：散戶情緒是最佳反向指標——散戶最悲觀時，往往是市場底部。
  
  當前評級：{ptt_lv}
  {'逆向邏輯：散戶>65%看空 = 空方能量基本耗盡，主力有機會在此區間吸籌，歷史上是強買點。' if ptt != -1.0 and ptt > 65 else '逆向邏輯：散戶<35%看空 = 全員樂觀，歷史上反而是市場頂部前兆，需謹慎。' if ptt != -1.0 and ptt < 35 else '逆向邏輯：散戶情緒中性，無強烈反向訊號，跟隨技術面操作。' if ptt != -1.0 else 'PTT 數據暫無法取得，僅憑 VIX + PR90 兩重驗證。'}

【五、加權指數技術面（TSE 精讀）】
  現值：{tse_price:,.0f}  │  動能：{tse_mom}
  格蘭碧法則：{tse_gran}
  神奇均線(87MA)：{tse_ma}
  扣抵斜率：{deducts}
  解讀：格蘭碧法則判定生命線關係，當現值{'高於' if '多頭' in str(tse_gran) else '低於'}87MA，{'趨勢偏多，回測均線為買點。' if '多頭' in str(tse_gran) else '趨勢偏空，反彈均線為賣點。'}

【六、綜合戰術推演】
  {'🟢 積極進攻：三重驗證全數通過（VIX低+PR90健康+PTT中性），系統性風險極低。策略：正常倉位佈局，以格蘭碧法則選股，優先布局動能強的族群。' if score == 3 else '🟡 區間操作：三重驗證部分警示，市場存在局部風險。策略：精選強勢股，倉位控制在60%以下，避開高PR90個股，設好停損。' if score == 2 else '🔴 防守模式：三重驗證多數警示，系統性風險上升。策略：降低整體倉位至30%以下，持有現金等待訊號轉為中性後再積極操作。'}

═══════════════════════════════════════════════════════════
"""
    key_hud = 'hud_streamed_v3'
    if key_hud not in st.session_state:
        st.write_stream(_stream_text(analysis, speed=0.008))
        st.session_state[key_hud] = True
    else:
        st.markdown(f'<pre style="white-space:pre-wrap;font-size:13px;color:rgba(200,215,230,0.8);line-height:1.85;">{analysis}</pre>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── TSE 深度面板 ────────────────────────────────────────────────────────
    st.markdown('<div style="margin-top:16px;">', unsafe_allow_html=True)
    deducts_full = " &nbsp;|&nbsp; ".join(tse.get('deduct_slope', ["計算中…"]))
    st.markdown(f"""
<div style="background:rgba(0,0,0,0.28);border:1px solid rgba(255,255,255,0.06);border-radius:18px;padding:20px 22px 18px;margin-top:8px;">
  <div style="font-family:var(--f-mono);font-size:9px;letter-spacing:3.5px;color:#334455;text-transform:uppercase;margin-bottom:16px;">
    🇹🇼 Taiwan Weighted Index — 技術面深度解讀
  </div>
  <div class="tse-grid">
    <div class="tse-chip">
      <div class="tsc-lbl">目前點位</div>
      <div class="tsc-val" style="font-family:var(--f-display);font-size:24px;color:#FFF;margin-top:4px;">
        {tse.get('price', 0):,.0f}
      </div>
    </div>
    <div class="tse-chip">
      <div class="tsc-lbl">動能方向</div>
      <div class="tsc-val" style="margin-top:4px;">{tse.get('momentum', 'N/A')}</div>
    </div>
    <div class="tse-chip">
      <div class="tsc-lbl">神奇均線(87MA)</div>
      <div class="tsc-val" style="margin-top:4px;">{tse.get('magic_ma', 'N/A')}</div>
    </div>
    <div class="tse-chip">
      <div class="tsc-lbl">格蘭碧法則</div>
      <div class="tsc-val" style="margin-top:4px;">{tse.get('granville', 'N/A')}</div>
    </div>
  </div>
  <div class="tse-deduct" style="margin-top:12px;font-size:12px;line-height:1.7;">
    扣抵斜率預判 — {deducts_full}
  </div>
</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── VIX × PR90 對照圖（近期趨勢）──────────────────────────────────────
    try:
        vix_df = macro.get_single_stock_data("^VIX", period="3mo")
        if not vix_df.empty:
            vix_plot = vix_df[['Close']].tail(60).reset_index()
            vix_plot.columns = ['Date', 'VIX']
            vix_plot['Date'] = pd.to_datetime(vix_plot['Date'])
            ax_v = alt.Axis(labelFontSize=26, titleFontSize=24, labelColor='#aaa')
            vix_line = alt.Chart(vix_plot).mark_area(
                line={'color': '#FF3131', 'strokeWidth': 2},
                color=alt.Gradient(gradient='linear', stops=[
                    alt.GradientStop(color='rgba(255,49,49,0.3)', offset=0),
                    alt.GradientStop(color='rgba(255,49,49,0.02)', offset=1)
                ], x1=1, x2=1, y1=1, y2=0)
            ).encode(
                x=alt.X('Date:T', axis=ax_v, title='日期'),
                y=alt.Y('VIX:Q', axis=ax_v, title='VIX', scale=alt.Scale(zero=False)),
                tooltip=[alt.Tooltip('Date:T'), alt.Tooltip('VIX:Q', format='.2f')]
            )
            r20 = alt.Chart(pd.DataFrame({'y': [20]})).mark_rule(color='#FFD700', strokeDash=[5,3], strokeWidth=2).encode(y='y:Q')
            r30 = alt.Chart(pd.DataFrame({'y': [30]})).mark_rule(color='#FF3131', strokeDash=[5,3], strokeWidth=2).encode(y='y:Q')
            vix_chart = alt.layer(vix_line, r20, r30).properties(
                height=200,
                title=alt.TitleParams('VIX 近60日走勢  金虛=警戒(20)  紅虛=危險(30)',
                                      color='#aaa', fontSize=18, font='JetBrains Mono')
            ).configure_view(strokeOpacity=0, fill='rgba(0,0,0,0)'
            ).configure_axis(gridColor='rgba(0,245,255,0.07)', labelColor='#aaa', titleColor='#aaa')
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.altair_chart(vix_chart, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception:
        pass  # VIX chart is bonus — don't crash if unavailable


def render_1_2_thermometer():
    # ══════════════════════════════════════════════════════════════════════
    # 1.2 多空溫度計 — 第一性原則重建
    # 核心邏輯：高價權值股站上87MA的比例 = 市場廣度（Market Breadth）
    #   市場廣度 > 65%：強勢多頭，主力資金全面進場，趨勢性行情
    #   市場廣度 50~65%：多方略優，選股行情，非系統性上漲
    #   市場廣度 35~50%：多空拉鋸，盤整格局，等待方向確認
    #   市場廣度 < 35%：空頭主控，現金為王，等待底部訊號
    # ══════════════════════════════════════════════════════════════════════
    _sec_header("🌡️", "高價權值股多空溫度計 · 市場廣度分析", "BREADTH THERMOMETER v3.0")
    macro, _, _ = _load_engines()

    if 'high_50_sentiment' not in st.session_state:
        st.session_state.high_50_sentiment = None

    st.markdown('<div class="action-wrap">', unsafe_allow_html=True)
    if st.button("🔄  REFRESH MARKET BREADTH SCAN", key="btn_sentiment"):
        st.toast("🚀 市場廣度掃描中…", icon="⏳")
        with st.spinner("Scanning high-price weighted stocks breadth…"):
            st.session_state.high_50_sentiment = macro.analyze_high_50_sentiment()
        st.toast("✅ 多空溫度計更新完成！", icon="🌡️")
    st.markdown('</div>', unsafe_allow_html=True)

    sent = st.session_state.high_50_sentiment
    if not sent:
        st.markdown('<div class="empty-state"><div class="empty-icon">🌡️</div>' +
                    '<div class="empty-text">CLICK SCAN TO LOAD MARKET BREADTH</div></div>', unsafe_allow_html=True)
        return
    if "error" in sent:
        st.toast(f"⚠️ {sent['error']}", icon="⚡")
        return

    ratio   = sent['bull_ratio']
    bear_r  = sent['bear_ratio']
    total   = sent['total']
    neutral = max(0, 100 - ratio - bear_r)

    # ── 溫度分級 ──────────────────────────────────────────────────────────
    if ratio >= 70:
        vd, vc, vr = "🔥 強勢多頭市場 — 主力全面進場，趨勢性行情", "#FF3131", "255,49,49"
        market_phase = "BULL MARKET"
        strategy = "積極進攻：均線多頭排列確認，持倉比例可提升至70~80%，以動能強股為主。"
        breadth_interp = "超過70%的高價權值股站上87MA，代表大資金已全面回歸，市場廣度極強，趨勢性牛市特徵顯著。"
    elif ratio >= 55:
        vd, vc, vr = "🟢 多方略佔優勢 — 選股行情，挑強勢族群", "#00FF7F", "0,255,127"
        market_phase = "SELECTIVE BULL"
        strategy = "精選進攻：非系統性上漲，需選對族群和個股。避開站上87MA比例低的弱勢族群。"
        breadth_interp = "55~70%高價股站上87MA，市場呈現選股行情。強者恆強，弱勢個股可能持續落後，需精選標的。"
    elif ratio >= 40:
        vd, vc, vr = "🟡 多空膠著 — 盤整格局，等待方向", "#FFD700", "255,215,0"
        market_phase = "NEUTRAL ZONE"
        strategy = "中性觀望：倉位控制在40~50%，等待市場廣度突破55%確認多頭，或跌破35%確認空頭再行動。"
        breadth_interp = "40~55%高價股站上87MA，多空力量接近均衡，市場缺乏方向性，易現上下震盪。"
    else:
        vd, vc, vr = "🔴 空頭市場 — 現金為王，等待底部訊號", "#26A69A", "38,166,154"
        market_phase = "BEAR MARKET"
        strategy = "防守撤退：倉位降至20%以下，等待市場廣度回升至40%以上才考慮佈局，切勿抄底搶反彈。"
        breadth_interp = "不足40%高價股站上87MA，主力資金撤離明顯，空頭結構確立，系統性風險高。"

    # ── 廣度趨勢判斷（動態方向）──────────────────────────────────────────
    prev_ratio = st.session_state.get('prev_breadth', ratio)
    breadth_dir = "📈 擴張" if ratio > prev_ratio + 2 else "📉 收縮" if ratio < prev_ratio - 2 else "➡️ 持平"
    breadth_dir_color = "#00FF7F" if "擴張" in breadth_dir else "#FF3131" if "收縮" in breadth_dir else "#FFD700"
    st.session_state['prev_breadth'] = ratio

    # ── 英雄面板 ──────────────────────────────────────────────────────────
    bar_fill = ratio
    st.markdown(f"""
<div style="background:linear-gradient(175deg,rgba(8,10,18,0.95),rgba(10,12,20,0.98));
     border:1px solid rgba({vr},0.2);border-radius:22px;padding:28px 28px 22px;margin-bottom:20px;">
  <div style="font-family:var(--f-mono);font-size:9px;letter-spacing:4px;color:rgba({vr},0.5);
       text-transform:uppercase;margin-bottom:16px;">🌡️ MARKET BREADTH THERMOMETER · HIGH-PRICE WEIGHTED STOCKS</div>

  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:22px;">
    <div style="text-align:center;">
      <div style="font-family:var(--f-mono);font-size:10px;color:#445566;letter-spacing:2px;margin-bottom:8px;">🐂 多頭（站上87MA）</div>
      <div style="font-family:var(--f-display);font-size:64px;color:#FF3131;line-height:1;">{ratio:.1f}%</div>
      <div style="font-family:var(--f-mono);font-size:11px;color:#FF3131;margin-top:4px;">{ratio/100*total:.0f} 檔</div>
    </div>
    <div style="text-align:center;">
      <div style="font-family:var(--f-mono);font-size:10px;color:#445566;letter-spacing:2px;margin-bottom:8px;">📊 掃描樣本</div>
      <div style="font-family:var(--f-display);font-size:64px;color:#FFF;line-height:1;">{total}</div>
      <div style="font-family:var(--f-mono);font-size:11px;color:#667788;margin-top:4px;">高價權值股</div>
    </div>
    <div style="text-align:center;">
      <div style="font-family:var(--f-mono);font-size:10px;color:#445566;letter-spacing:2px;margin-bottom:8px;">🐻 空頭（低於87MA）</div>
      <div style="font-family:var(--f-display);font-size:64px;color:#26A69A;line-height:1;">{bear_r:.1f}%</div>
      <div style="font-family:var(--f-mono);font-size:11px;color:#26A69A;margin-top:4px;">{bear_r/100*total:.0f} 檔</div>
    </div>
  </div>

  <!-- 廣度溫度條 -->
  <div style="margin-bottom:16px;">
    <div style="font-family:var(--f-mono);font-size:10px;color:#334455;letter-spacing:2px;margin-bottom:8px;">MARKET BREADTH GAUGE</div>
    <div style="position:relative;height:20px;background:rgba(0,0,0,0.4);border-radius:10px;overflow:hidden;">
      <div style="position:absolute;left:0;top:0;height:100%;width:{bar_fill:.0f}%;
           background:linear-gradient(90deg,#26A69A,#FFD700 50%,#FF3131);border-radius:10px;
           transition:width 0.5s;"></div>
      <div style="position:absolute;left:35%;top:-4px;width:2px;height:28px;background:#FFD700;opacity:0.5;"></div>
      <div style="position:absolute;left:65%;top:-4px;width:2px;height:28px;background:#FF3131;opacity:0.5;"></div>
    </div>
    <div style="display:flex;justify-content:space-between;margin-top:6px;font-family:var(--f-mono);font-size:10px;color:#334455;">
      <span>0% 極度空頭</span><span>35% 警戒</span><span>65% 多頭確認</span><span>100%</span>
    </div>
  </div>

  <div style="background:rgba({vr},0.06);border:1px solid rgba({vr},0.2);border-radius:12px;
       padding:14px 18px;font-family:var(--f-body);font-size:16px;color:rgb({vr});
       font-weight:700;letter-spacing:0.3px;">
    {vd}
  </div>
</div>""", unsafe_allow_html=True)

    # ── KPI 儀表板 ────────────────────────────────────────────────────────
    _kpi_row(
        ("多頭佔比",   f"{ratio:.1f}%",   f"站上87MA · {ratio/100*total:.0f}檔", vc),
        ("空頭佔比",   f"{bear_r:.1f}%",  f"低於87MA · {bear_r/100*total:.0f}檔", "#26A69A"),
        ("廣度趨勢",   breadth_dir,       "vs 上次掃描",                          breadth_dir_color),
        ("市場階段",   market_phase[:6],  vd[:8],                                 vc),
    )

    # ── AI 戰術分析（Typewriter）────────────────────────────────────────────
    st.markdown("### 🧠 市場廣度 · 第一性原則戰術推演")
    st.markdown('<div style="background:rgba(0,0,0,0.4);border:1px solid rgba(0,245,255,0.1);border-radius:16px;padding:20px 24px;margin:12px 0;font-family:var(--f-mono);font-size:13px;color:rgba(200,215,230,0.85);line-height:1.9;">', unsafe_allow_html=True)

    analysis = f"""
═══════════════════════════════════════════════════════════
🌡️ BREADTH THERMOMETER v3.0 — 市場廣度精密推演
   多頭佔比：{ratio:.1f}%  |  空頭佔比：{bear_r:.1f}%  |  樣本：{total} 檔
═══════════════════════════════════════════════════════════

【一、市場廣度第一性原則】
  市場廣度的本質：「高價權值股有多少比例站在87MA生命線之上」。
  87MA（87日均線）= 近87個交易日的平均成本，是多空力量的關鍵分水嶺：
    站上87MA = 主力資金成本有支撐，多方佔優
    跌破87MA = 主力資金套牢，空方主控
  
  廣度 vs 價格的關係：
    廣度擴張 + 指數上漲 → 最強多頭訊號（主力全面進場）
    廣度收縮 + 指數上漲 → 高度警戒（指數創高但廣度不確認 = 頭部分佈訊號）
    廣度擴張 + 指數下跌 → 超賣反彈（廣度領先見底）
    廣度收縮 + 指數下跌 → 空頭加速（趨勢確認向下）

【二、當前廣度數據解讀】
  多頭佔比（站上87MA）：{ratio:.1f}%  ({ratio/100*total:.0f}/{total} 檔)
  空頭佔比（低於87MA）：{bear_r:.1f}%  ({bear_r/100*total:.0f}/{total} 檔)
  廣度趨勢：{breadth_dir}  (vs 上次掃描)
  
  {breadth_interp}

【三、市場階段判定：{market_phase}】
  當前分類：{vd}
  
  歷史對照（台股經驗值）：
  · 廣度 > 70%：牛市高峰，但也是過熱警訊前兆（2021年台股最高時達80%+）
  · 廣度 50~70%：健康牛市區間，適合積極操作
  · 廣度 35~50%：震盪整理，耐心等待方向
  · 廣度 < 35%：熊市，等待廣度「黃金交叉」（從底部回升穿越35%）再考慮進場

【四、廣度背離預警機制】
  廣度背離是最重要的警示訊號：
  正向背離（廣度擴張 > 指數）→ 市場底部能量積累，即將反彈
  負向背離（廣度收縮 < 指數）→ 市場頂部分配，即將見頂
  
  當前廣度趨勢：{breadth_dir}（{breadth_dir_color}方向）
  {'⚠️ 若當前指數持續創高但廣度收縮，須高度警戒，可能為頭部訊號。' if ratio > 60 and "收縮" in breadth_dir else '✅ 廣度與趨勢方向一致，無明顯背離警訊。' if "擴張" in breadth_dir else '🟡 廣度持平，市場方向待確認。'}

【五、操作戰術推演】
  {strategy}
  
  關鍵觀察指標：
  · 若廣度從當前水準{'上升突破65%' if ratio < 65 else '維持在65%以上'}，代表多方力量{'進一步增強' if ratio < 65 else '穩定'}，可加碼。
  · 若廣度{'跌破50%' if ratio > 50 else '跌破35%'}，代表{'多空均勢打破，需降低倉位' if ratio > 50 else '空頭確認，需全面撤退'}。

═══════════════════════════════════════════════════════════
"""
    key_thermo = 'thermo_streamed_v3'
    if key_thermo not in st.session_state:
        st.write_stream(_stream_text(analysis, speed=0.008))
        st.session_state[key_thermo] = True
    else:
        st.markdown(f'<pre style="white-space:pre-wrap;font-size:13px;color:rgba(200,215,230,0.8);line-height:1.85;">{analysis}</pre>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Plotly 儀表盤（保留但升級）──────────────────────────────────────
    st.markdown("#### 📊 廣度儀表盤（多頭佔比 vs 警戒線）")
    col1, col2 = st.columns(2)
    with col1:
        fig_bull = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ratio,
            title={'text': "多頭佔比 %", 'font': {'color': '#445566', 'size': 14, 'family': 'JetBrains Mono'}},
            number={'font': {'color': '#FFF', 'size': 64, 'family': 'Bebas Neue'}, 'suffix': '%'},
            delta={'reference': prev_ratio, 'relative': False,
                   'font': {'size': 18}, 'increasing': {'color': '#00FF7F'}, 'decreasing': {'color': '#FF3131'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#222', 'tickfont': {'size': 14}},
                'bar': {'color': vc},
                'bgcolor': 'rgba(0,0,0,0)',
                'bordercolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [0,  35], 'color': '#060e14'},
                    {'range': [35, 65], 'color': '#090f0a'},
                    {'range': [65,100], 'color': '#13060a'},
                ],
                'threshold': {'line': {'color': '#FFD700', 'width': 4}, 'thickness': 0.78, 'value': 50}
            }
        ))
        fig_bull.update_layout(
            height=280, template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=18, b=4, l=18, r=18),
            font=dict(family='JetBrains Mono')
        )
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_bull, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # 多空比例圓餅
        fig_pie = go.Figure(go.Pie(
            labels=['多頭(站上87MA)', '空頭(低於87MA)', '中性'],
            values=[ratio, bear_r, max(0, neutral)],
            marker_colors=['#FF3131', '#26A69A', '#334455'],
            hole=0.55,
            textfont_size=16,
            textfont_family='JetBrains Mono',
        ))
        fig_pie.update_layout(
            height=280, template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(font=dict(size=14, family='JetBrains Mono', color='#aaa')),
            margin=dict(t=18, b=4, l=8, r=8),
            annotations=[dict(text=f'{ratio:.0f}%', x=0.5, y=0.5, font_size=28,
                               font_family='Bebas Neue', font_color='#FFF', showarrow=False)]
        )
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


def render_1_3_pr90():
    # ══════════════════════════════════════════════════════════════════════
    # 1.3 PR90 籌碼分佈 — 第一性原則重建
    #
    # 核心問題：市場現在「過熱」還是「低估」？
    #
    # 第一性原則出發點：
    #   可轉換公司債（CB）是股票的「影子鏡像」—— 當市場過熱時，
    #   CB 市價跟著推高；當恐慌拋售時，CB 市價跟著崩落。
    #   PR90（第90百分位）= 市場中最貴的那 10% CB 的價位門檻，
    #   它是「籌碼過熱壓力計」的核心刻度。
    #
    # 為什麼是 PR90 而不是均價？
    #   均價受少數極端值扭曲，中位數對尾部風險不敏感。
    #   PR90 的優勢：代表「高度套牢區」的下緣——超過此線的籌碼
    #   持有者即將面臨轉換壓力或獲利了結衝動，是供給端的壓力錶。
    #
    # 操作翻譯：
    #   PR90 > 130 → 頂端籌碼嚴重壓頂，新資金進場即面對大量供給
    #   PR90 110~130 → 警示區，追高需謹慎
    #   PR90 90~110 → 健康中性，正常操作
    #   PR90 < 90  → 籌碼低谷，可積極佈局（下方承接力強）
    # ══════════════════════════════════════════════════════════════════════
    _sec_header("📊", "CB 全市場籌碼分佈 · PR90 過熱壓力系統", "CHIP DISTRIBUTION v3.0")
    macro, _, _ = _load_engines()
    df      = st.session_state.get('df', pd.DataFrame())
    df_hash = f"{len(df)}_{list(df.columns)}" if not df.empty else "empty"

    # ── 第一性原則導言 ─────────────────────────────────────────────────────
    st.markdown("""
<div style="background:rgba(0,0,0,0.32);border:1px solid rgba(255,215,0,0.12);
     border-left:3px solid rgba(255,215,0,0.5);border-radius:14px;
     padding:16px 20px;margin-bottom:20px;font-family:var(--f-mono);
     font-size:11px;color:rgba(200,215,230,0.7);line-height:1.9;letter-spacing:0.3px;">

<span style="color:#FFD700;font-weight:700;letter-spacing:2px;">█ 第一性原則 — 為什麼籌碼分佈是最誠實的市場溫度計？</span><br><br>

股票市場存在「資訊不對稱」—— 主力可以控制消息面、技術面甚至短期籌碼，
但他們無法偽造 CB（可轉換公司債）的市場定價。CB 由市場公開競價，
其分佈形態直接反映全市場的「真實風險偏好」：<br><br>

&nbsp;&nbsp;→ <span style="color:#FF3131;">右側厚尾（高價籌碼堆積）</span>：市場過度樂觀，頂部籌碼承壓，是多頭末段警訊<br>
&nbsp;&nbsp;→ <span style="color:#00F5FF;">左側厚尾（低價籌碼堆積）</span>：市場恐慌性拋售，底部蓄能，是逆向買點積累訊號<br>
&nbsp;&nbsp;→ <span style="color:#00FF7F;">鐘形正態分佈</span>：市場健康，籌碼均勻分散，可正常操作<br><br>

<span style="color:#FFD700;">PR90 = 全市場 CB 價格的第 90 百分位</span> — 這條「過熱線」以上是最後 10% 最貴的籌碼，
它們持有者的獲利了結衝動最強，是最直接的賣壓來源。

</div>""", unsafe_allow_html=True)

    if df.empty:
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">📂</div>'
            '<div class="empty-text">UPLOAD CB LIST TO ACTIVATE CHIP ANALYSIS</div></div>',
            unsafe_allow_html=True
        )
        return

    md    = _get_macro_data(macro, df_hash)
    pd_   = md.get('price_distribution', {})
    cdata = pd_.get('chart_data')

    if cdata is None or cdata.empty:
        st.toast("⚠️ 無法生成籌碼分佈圖，請檢查 CB 清單價格欄位", icon="⚡")
        return

    pr90 = pd_.get('pr90', 0)
    pr75 = pd_.get('pr75', 0)
    avg  = pd_.get('avg', 0)
    total_count = int(cdata['數量'].sum()) if '數量' in cdata.columns else 0

    # ── PR90 深度評級 ──────────────────────────────────────────────────────
    if pr90 > 135:
        pr90_lv, pr90_col, pr90_rgb = "💀 極度過熱 — 獲利了結壓力山大", "#FF3131", "255,49,49"
        pr90_advice = "立即降低倉位至 30% 以下。PR90 超過 135 代表市場貪婪指數到頂，歷史上此位置持倉超過 3 週的勝率不足 30%。"
        pr90_phase = "EXTREME HEAT"
    elif pr90 > 120:
        pr90_lv, pr90_col, pr90_rgb = "🔴 嚴重過熱 — 謹慎追高，控制新倉", "#FF6B35", "255,107,53"
        pr90_advice = "新倉布局需極度謹慎。此區間上方籌碼供給充足，每一波拉高都可能引發集中獲利了結。優先執行既有持倉的停利計劃。"
        pr90_phase = "OVERHEATED"
    elif pr90 > 110:
        pr90_lv, pr90_col, pr90_rgb = "🟡 警示區間 — 局部過熱，選股更嚴格", "#FFD700", "255,215,0"
        pr90_advice = "個股篩選需更嚴格，優先選 PR90 以下、籌碼集中度低的標的。整體市場仍可操作，但需為回調做好準備。"
        pr90_phase = "CAUTION ZONE"
    elif pr90 > 95:
        pr90_lv, pr90_col, pr90_rgb = "🟢 健康區間 — 正常操作，籌碼結構良好", "#00FF7F", "0,255,127"
        pr90_advice = "籌碼結構健康，市場壓力適中。可正常執行選股策略，此區間歷史上是勝率最高的操作環境（> 60% 勝率）。"
        pr90_phase = "HEALTHY ZONE"
    else:
        pr90_lv, pr90_col, pr90_rgb = "🔵 低位積累 — 籌碼充分低位，逆向佈局機會", "#00F5FF", "0,245,255"
        pr90_advice = "籌碼跌至極低，市場已過度恐慌性拋售。此為逆向積累訊號 —— 但需搭配 VIX 和多空溫度計確認底部。盲目搶底風險高。"
        pr90_phase = "ACCUMULATION"

    # PR75 評級（機會線）
    if pr75 > 115:   pr75_lv, pr75_col = "偏高 — 中位籌碼也有壓力", "#FF6B35"
    elif pr75 > 100: pr75_lv, pr75_col = "正常 — 中位籌碼健康",     "#FFD700"
    else:            pr75_lv, pr75_col = "低位 — 中位籌碼尚有空間",  "#00F5FF"

    # 頂部佔比（PR90 以上的籌碼佔比）
    cd = cdata.copy()
    def _zone(lbl):
        try:    mid = float(str(lbl).split('~')[0])
        except: return "正常區"
        if mid >= pr90: return "PR90 過熱區"
        if mid >= pr75: return "PR75 警示區"
        return "正常區"
    cd['區域'] = cd['區間'].apply(_zone)

    hot_count = int(cd[cd['區域'] == 'PR90 過熱區']['數量'].sum()) if '數量' in cd.columns else 0
    hot_ratio = (hot_count / total_count * 100) if total_count > 0 else 0

    # ── KPI 儀表板 ───────────────────────────────────────────────────────
    _kpi_row(
        ("PR90  過熱壓力線", f"{pr90:.0f}",
         f"{'🔴 過熱' if pr90 > 120 else '🟡 警示' if pr90 > 110 else '🟢 健康'}",
         pr90_col),
        ("PR75  機會線",    f"{pr75:.0f}", pr75_lv, pr75_col),
        ("全市場均價",      f"{avg:.0f}",  "CB 中心重力位",   "#00F5FF"),
        ("頂部籌碼佔比",   f"{hot_ratio:.1f}%", f"PR90 以上 {hot_count} 檔", pr90_col),
    )

    # ── 籌碼分佈圖 ─────────────────────────────────────────────────────────
    bar = (
        alt.Chart(cd)
        .mark_bar(opacity=0.92, cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X('區間:N', sort=None, title='CB 市價區間',
                     axis=alt.Axis(labelColor='#445566', titleColor='#334455',
                                   labelAngle=-32, labelFontSize=11)),
            y=alt.Y('數量:Q', title='檔數',
                     axis=alt.Axis(labelColor='#445566', titleColor='#334455')),
            color=alt.Color('區域:N',
                scale=alt.Scale(
                    domain=["正常區", "PR75 警示區", "PR90 過熱區"],
                    range=["#00F5FF", "#FFD700", "#FF3131"]
                ),
                legend=alt.Legend(orient='top', labelColor='#C8D8E8',
                                  titleColor='#C8D8E8', padding=10, symbolSize=90)
            ),
            tooltip=['區間', '數量', '區域']
        )
        .properties(
            title=alt.TitleParams(
                text="CB 全市場籌碼分佈圖 — 顏色代表壓力分區",
                color='#FFD700', fontSize=13, font='JetBrains Mono'
            ),
            height=340, background='rgba(0,0,0,0)'
        )
        .configure_axis(gridColor='rgba(255,255,255,0.04)')
        .configure_view(strokeOpacity=0)
    )

    st.markdown("""
<div style="font-family:var(--f-mono);font-size:9px;color:#334455;letter-spacing:2px;
     text-transform:uppercase;margin-bottom:6px;">
  █ 柱狀圖解讀：藍色=健康低壓區 · 金色=PR75警示區 · 紅色=PR90過熱區（賣壓最重）
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.altair_chart(bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 第一性原則 AI 深度分析 ───────────────────────────────────────────────
    st.markdown("""
<div style="background:rgba(0,0,0,0.4);border:1px solid rgba(0,245,255,0.1);border-radius:16px;
     padding:20px 24px;margin:20px 0;font-family:var(--f-mono);font-size:13px;
     color:rgba(200,215,230,0.85);line-height:1.9;">""", unsafe_allow_html=True)

    analysis = f"""
═══════════════════════════════════════════════════════════
📊 PR90 籌碼分佈 v3.0 — 第一性原則深度解讀
   PR90: {pr90:.1f}  |  PR75: {pr75:.1f}  |  均價: {avg:.1f}  |  頂部籌碼: {hot_ratio:.1f}%
   市場狀態：{pr90_phase}
═══════════════════════════════════════════════════════════

【一、PR90 的本質與計算邏輯（為什麼這個數字有意義？）】
  PR90 是可轉換公司債（CB）全市場價格分佈的「第 90 百分位」。
  具體含義：市場上 90% 的 CB 市價低於 {pr90:.0f}，僅最頂端 10% 超過此線。

  為什麼 CB 比股票更誠實？
  ① CB 有固定到期還本保證 → 市場定價時不會被情緒推到完全脫離基本面
  ② CB 轉換溢價機制 → 當 CB 高度偏離轉換價值時，套利機制自然產生壓制
  ③ CB 市場受公法人和外資高度參與 → 難以被單一主力人為操控
  因此 CB 的 PR90 = 「市場最誠實的過熱溫度計」。

【二、當前籌碼狀態深度解讀（PR90 = {pr90:.1f}）】
  評級：{pr90_lv}
  
  {pr90_advice}

  頂部籌碼分析：
  · 目前 PR90 以上有 {hot_count} 檔 CB，佔全市場 {hot_ratio:.1f}%
  · {'這是高度警示訊號：超過 15% 的市場籌碼處於過熱壓力區，歷史上超過此水準後 3 個月內回調概率 > 70%。' if hot_ratio > 15 else '尚在可控範圍：頂部籌碼佔比 < 15%，市場壓力尚未到達危險臨界點。' if hot_ratio > 8 else '市場籌碼健康：高壓區佔比低，說明絕大多數籌碼仍在健康區間操作。'}

【三、PR75 機會線解讀（PR75 = {pr75:.1f}）】
  PR75 是「上方 25% 籌碼」的起始線，也是尋找短線機會的重要參考。
  當個股 CB 市價在 PR75 以下：代表該股籌碼集中在市場中低區，主力尚有空間拉抬。
  當個股 CB 市價在 PR75~PR90 之間：需要更謹慎，繼續上漲面臨中位籌碼壓力。
  當前 PR75 評級：{pr75_lv}

【四、全市場均價 {avg:.1f} 的意義】
  全市場 CB 均價代表市場「重心位置」：
  · 若個股 CB 市價 >> 均價：代表市場給予的溢價高，但也意味更高風險
  · 若個股 CB 市價 ≈ 均價：市場評價中性，相對安全
  · 若個股 CB 市價 << 均價：市場低估或遭拋售，需分析是否為機會

【五、籌碼分佈形態學（讀懂這張圖）】
  理想健康分佈 → 鐘形曲線，均價居中，左右對稱
  {'⚠️ 當前形態偏向右側厚尾 → 高價籌碼堆積，過熱訊號，市場貪婪。' if pr90 > 115 else '✅ 當前形態相對正常，無明顯極端偏斜。' if pr90 > 95 else '⚠️ 當前形態偏向左側厚尾 → 低價籌碼堆積，市場恐慌，但也是逆向機會積累時機。'}
  
  PR90 與 VIX 的交叉驗證：
  · PR90 高 + VIX 低 → 最危險組合（市場過熱但無恐懼，自滿期，頂部特徵）
  · PR90 低 + VIX 高 → 最佳逆向機會（市場恐慌拋售，籌碼低位，底部特徵）
  · PR90 中性 + VIX 中性 → 正常操作環境，跟著趨勢和選股系統走即可

【六、操作指令（基於當前 PR90 = {pr90:.1f}）】
  {pr90_advice}
  
  具體行動：
  {'⛔ 停止追高新倉  ⛔ 執行既有持倉停利  ⛔ 若 VIX 同步上升，立即降倉至 30%' if pr90 > 120 else '⚠️ 精選標的（僅選 PR90 以下低壓籌碼）  ⚠️ 倉位控制 60% 以下  ⚠️ 嚴設停損' if pr90 > 110 else '✅ 正常佈局  ✅ 依選股系統操作  ✅ 維持紀律性停損' if pr90 > 95 else '🔵 逆向積累時機  🔵 分批佈局優質個股  🔵 等待 PR90 止跌回升確認'}

═══════════════════════════════════════════════════════════
"""

    key_pr90 = 'pr90_streamed_v3'
    if key_pr90 not in st.session_state:
        st.write_stream(_stream_text(analysis, speed=0.008))
        st.session_state[key_pr90] = True
    else:
        st.markdown(
            f'<pre style="white-space:pre-wrap;font-size:13px;'
            f'color:rgba(200,215,230,0.8);line-height:1.85;">{analysis}</pre>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 壓力帶可視化 (Plotly Gauge) ────────────────────────────────────────
    st.markdown("#### 🌡️ PR90 壓力儀表盤")
    col1, col2 = st.columns(2)

    with col1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pr90,
            title={'text': "PR90 籌碼壓力指數", 'font': {'color': '#445566', 'size': 14, 'family': 'JetBrains Mono'}},
            number={'font': {'color': '#FFF', 'size': 56, 'family': 'Bebas Neue'}},
            delta={'reference': 100, 'relative': False,
                   'font': {'size': 16}, 'increasing': {'color': '#FF3131'}, 'decreasing': {'color': '#00FF7F'}},
            gauge={
                'axis': {'range': [70, 160], 'tickcolor': '#222', 'tickfont': {'size': 12}},
                'bar': {'color': pr90_col},
                'bgcolor': 'rgba(0,0,0,0)',
                'bordercolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [70,  95],  'color': '#030e0a'},
                    {'range': [95,  110], 'color': '#090c02'},
                    {'range': [110, 120], 'color': '#0c0a02'},
                    {'range': [120, 160], 'color': '#130204'},
                ],
                'threshold': {'line': {'color': '#FF3131', 'width': 4}, 'thickness': 0.82, 'value': 130}
            }
        ))
        fig_gauge.update_layout(
            height=280, template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=18, b=4, l=18, r=18),
            font=dict(family='JetBrains Mono')
        )
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # 壓力分區圓餅圖
        fig_pie = go.Figure(go.Pie(
            labels=['健康區 (< PR75)', 'PR75 警示區', 'PR90 過熱區'],
            values=[
                max(0, int(cd[cd['區域'] == '正常區']['數量'].sum()) if '數量' in cd.columns else 0),
                max(0, int(cd[cd['區域'] == 'PR75 警示區']['數量'].sum()) if '數量' in cd.columns else 0),
                max(0, hot_count),
            ],
            marker_colors=['#00F5FF', '#FFD700', '#FF3131'],
            hole=0.55,
            textfont_size=14,
            textfont_family='JetBrains Mono',
        ))
        fig_pie.update_layout(
            height=280, template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=True,
            legend=dict(font=dict(size=13, family='JetBrains Mono', color='#aaa')),
            margin=dict(t=18, b=4, l=8, r=8),
            annotations=[dict(text=f'{hot_ratio:.0f}%\n過熱', x=0.5, y=0.5, font_size=22,
                               font_family='Bebas Neue', font_color='#FF3131', showarrow=False)]
        )
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">PR90 Chip Distribution V300 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────────────────

def render_1_4_heatmap():
    """
    🔥 1.4 台股族群熱度矩陣 (SECTOR HEAT MAP)
    30大板塊 × 動態資金輪動偵測 — 第一性原則重建
    Data: yfinance 抓取板塊代理個股，計算 3M 相對強度 × 近期動能
    板塊涵蓋：科技(11) / 金融(4) / 工業(6) / 消費(4) / 醫療(2) / 能源電信(3)
    """
    _sec_header("🔥", "台股族群熱度矩陣 · 30大板塊全覆蓋", "SECTOR HEAT MAP")

    # ── Sector CSS injected once ──────────────────────────────────────────────
    st.markdown("""
<style>
/* SECTOR HEAT MAP — extra styles */
.sector-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin: 18px 0 24px;
}
.sector-card {
    position: relative;
    border-radius: 18px;
    padding: 16px 12px 14px;
    border: 1px solid rgba(255,255,255,0.065);
    background: rgba(255,255,255,0.018);
    overflow: hidden;
    transition: transform .2s cubic-bezier(.25,.8,.25,1), box-shadow .2s ease;
    cursor: default;
}
.sector-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 44px rgba(0,0,0,0.55);
}
.sector-card::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 0%,
        var(--sc-glow) 0%, transparent 65%);
    pointer-events: none;
}
.sc-rank {
    position: absolute; top: 8px; right: 10px;
    font-family: var(--f-display); font-size: 32px; font-weight: 900;
    color: rgba(255,255,255,0.04); line-height: 1;
}
.sc-emoji { font-size: 26px; line-height: 1; margin-bottom: 8px; }
.sc-name {
    font-family: var(--f-body); font-size: 14px; font-weight: 700;
    color: #DDE; margin-bottom: 3px; letter-spacing: 0.3px;
}
.sc-ticker {
    font-family: var(--f-mono); font-size: 8px; color: #445566;
    letter-spacing: 2px; margin-bottom: 10px; text-transform: uppercase;
}
.sc-change {
    font-family: var(--f-display); font-size: 36px; line-height: 1;
    font-weight: 900; margin-bottom: 4px;
}
.sc-bar-bg {
    height: 4px; border-radius: 3px; background: rgba(255,255,255,0.05);
    margin-top: 12px; overflow: hidden;
}
.sc-bar-fill {
    height: 100%; border-radius: 3px;
    background: var(--sc-color);
    transition: width .6s cubic-bezier(.4,0,.2,1);
}
.sc-signal {
    font-family: var(--f-mono); font-size: 9px; font-weight: 700;
    letter-spacing: 2px; margin-top: 8px; text-transform: uppercase;
    color: var(--sc-color);
}
/* Top heat glow strip */
.heat-strip {
    height: 3px; border-radius: 3px;
    background: linear-gradient(90deg, transparent, var(--sc-color) 50%, transparent);
    position: absolute; top: 0; left: 10%; right: 10%;
}
/* Summary banner */
.sector-summary {
    border-radius: 16px; padding: 18px 22px;
    background: rgba(255,255,255,0.018);
    border: 1px solid rgba(255,255,255,0.055);
    margin-bottom: 20px;
    display: flex; align-items: center; gap: 24px;
    flex-wrap: wrap;
}
.ss-item { text-align: center; }
.ss-label {
    font-family: var(--f-mono); font-size: 8px; color: #445566;
    letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 4px;
}
.ss-value {
    font-family: var(--f-display); font-size: 32px; line-height: 1;
}
.rotation-badge {
    margin-left: auto;
    font-family: var(--f-body); font-size: 14px; font-weight: 700;
    padding: 10px 20px; border-radius: 24px;
    border: 1px solid var(--rb-color);
    color: var(--rb-color);
    background: rgba(var(--rb-rgb), 0.06);
    letter-spacing: 0.5px;
}
</style>
""", unsafe_allow_html=True)

    # ── 30大台股板塊代理 — 第一性原則重建 ────────────────────────────────────
    #
    # 設計原則：
    #   板塊 = 「具有相關聯商業模式、相同利潤驅動因子、相近資金輪動週期」的股票集合
    #   代理標的選擇標準：① 板塊市值佔比最高  ② yfinance 流動性充足  ③ 不重複使用同一供應鏈節點
    #
    # 板塊分類架構：
    #   🔵 科技     11個 — 半導體供應鏈拆解至最小可監控單元
    #   🟡 金融      4個 — 壽險/銀行/證券/消費金融，資金屬性各異
    #   🟢 工業      6個 — 景氣循環型，與全球貿易/原物料強相關
    #   🌿 消費      4個 — 內需防禦型，受利率/消費信心驅動
    #   🔴 醫療      2個 — 生技新藥 vs 醫療器材，兩種不同商業邏輯
    #   🟣 能源/電信 3個 — 台灣能源轉型 + 電信基礎建設
    # ──────────────────────────────────────────────────────────────────────────
    SECTORS = [
        # ── 🔵 科技板塊 (11) — 半導體供應鏈全覆蓋 ───────────────────────────
        ("半導體/晶圓代工", "2330.TW", "💎", "科技"),   # 台積電   — 全球晶圓霸主，板塊定海神針
        ("IC設計/SoC",      "2454.TW", "🔬", "科技"),   # 聯發科   — 無線晶片領袖，手機/IoT指標
        ("先進封裝/測試",   "3711.TW", "🏭", "科技"),   # 日月光投控— 封測全球第一，CoWoS受惠股
        ("AI伺服器/ODM",    "2382.TW", "🖥️","科技"),  # 廣達電腦 — AI雲端機架龍頭，GB200主力
        ("網通/乙太交換器", "2345.TW", "🌐", "科技"),   # 智邦科技 — 400G/800G乙太網路龍頭
        ("PCB/高頻載板",    "3037.TW", "📋", "科技"),   # 欣興電子 — ABF載板主力，AI封裝必需
        ("被動元件/MLCC",   "2327.TW", "⚡", "科技"),   # 國巨     — MLCC/電阻霸主，車電/AI雙驅
        ("光學/鏡頭模組",   "3008.TW", "💡", "科技"),   # 大立光   — 光學鏡頭龍頭，毛利率之王
        ("電動車/電源管理", "2308.TW", "🔋", "科技"),   # 台達電   — 電源/EV/工廠自動化三引擎
        ("散熱/液冷模組",   "3017.TW", "🌡️","科技"),  # 奇鋐科技 — AI伺服器散熱龍頭，液冷受惠
        ("電子代工/EMS",    "2317.TW", "🏗️","科技"),  # 鴻海精密 — EMS全球第一，AI/電動車佈局
        # ── 🟡 金融板塊 (4) — 資金屬性細分 ──────────────────────────────────
        ("壽險/金控",       "2882.TW", "🏦", "金融"),   # 國泰金   — 最大壽險金控，利率敏感度最高
        ("銀行/外匯金控",   "2886.TW", "🏛️","金融"),  # 兆豐金   — 外匯/貿易融資龍頭，出口景氣連動
        ("證券/ETF投信",    "2885.TW", "📊", "金融"),   # 元大金   — 最大券商+ETF發行商，市場溫度計
        ("消費金融/信貸",   "2891.TW", "💳", "金融"),   # 中信金   — 信用卡/消費貸款龍頭，內需指標
        # ── 🟢 工業/傳產板塊 (6) — 全球景氣循環 ─────────────────────────────
        ("航運/貨櫃海運",   "2603.TW", "🚢", "工業"),   # 長榮海運 — 貨櫃三雄之首，運價即時溫度計
        ("航空/客貨運",     "2610.TW", "✈️","工業"),   # 中華航空 — 台灣最大航空，觀光/貿易雙引擎
        ("鋼鐵/金屬",       "2002.TW", "🔩", "工業"),   # 中鋼     — 台灣鋼鐵指標，基礎建設需求鏡像
        ("石化/塑膠原料",   "1301.TW", "🛢️","工業"),  # 台塑     — 石化龍頭，油價/乙烯價差直連
        ("水泥/骨材",       "1101.TW", "🪨", "工業"),   # 台泥     — 台灣水泥第一，營建活動先行指標
        ("汽車/運輸代理",   "2207.TW", "🚗", "工業"),   # 和泰車   — 豐田代理商，消費景氣/電動化指標
        # ── 🌿 消費/民生板塊 (4) — 內需防禦型 ───────────────────────────────
        ("食品/飲料",       "1216.TW", "🍜", "消費"),   # 統一企業 — 食品龍頭，消費通膨傳導指標
        ("零售/超商",       "2912.TW", "🛒", "消費"),   # 統一超商 — 7-ELEVEN，消費頻率最高板塊
        ("紡織/機能纖維",   "1402.TW", "👕", "消費"),   # 遠東新世紀— 紡織+機能布料，出口/越南廠連動
        ("觀光/飯店餐旅",   "2707.TW", "🏨", "消費"),   # 晶華酒店 — 觀光龍頭，入境旅遊景氣最直接
        # ── 🔴 醫療/生技板塊 (2) — 研發週期驅動 ─────────────────────────────
        ("生技/新藥研發",   "6446.TW", "🧬", "醫療"),   # 藥華藥   — 明星新藥股，FDA核准進度驅動
        ("醫療器材/檢測",   "4736.TW", "🏥", "醫療"),   # 泰博科技 — 血糖/血氧醫材，老齡化需求
        # ── 🟣 能源/電信板塊 (3) — 台灣能源轉型 ─────────────────────────────
        ("電信/5G基礎建設", "2412.TW", "📡", "電信"),   # 中華電信 — 台灣電信第一，防禦性高殖利率
        ("太陽能/綠電",     "6443.TW", "☀️","能源"),   # 元晶太陽能— 太陽電池龍頭，綠電政策受惠
        ("離岸風電/海工",   "9958.TW", "🌊", "能源"),   # 世紀鋼鐵 — 風電塔架製造商，能源轉型核心
    ]

    # ── Trigger button ────────────────────────────────────────────────────────
    if not st.session_state.get('sector_map_active', False):
        col_btn, _ = st.columns([1, 2])
        with col_btn:
            st.markdown('<div class="action-wrap">', unsafe_allow_html=True)
            if st.button("🔥  SCAN SECTOR HEAT MAP", key="btn_sector_scan",
                         use_container_width=True):
                st.toast("🔥 掃描族群熱度中…", icon="⏳")
                st.session_state.sector_map_active = True
                st.session_state.pop('sector_data', None)  # force refresh
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="empty-state"><div class="empty-icon">🔥</div>'
            '<div class="empty-text">AWAITING SECTOR SCAN COMMAND</div></div>',
            unsafe_allow_html=True
        )
        return

    # ── Fetch & compute ───────────────────────────────────────────────────────
    if 'sector_data' not in st.session_state:
        with st.spinner("🛰️  INTERCEPTING SECTOR CAPITAL FLOWS…"):
            tickers_list = [s[1] for s in SECTORS]
            try:
                raw = yf.download(tickers_list, period="3mo",
                                   auto_adjust=True, progress=False)
                close_df = raw['Close'] if 'Close' in raw.columns else raw

                results = []
                for name_zh, ticker, emoji, category in SECTORS:
                    if ticker not in close_df.columns:
                        continue
                    series = close_df[ticker].dropna()
                    if len(series) < 5:
                        continue

                    # ── Core metrics (first-principles) ──
                    price_now   = float(series.iloc[-1])
                    price_1w    = float(series.iloc[-5])   if len(series) > 5  else price_now
                    price_1m    = float(series.iloc[-22])  if len(series) > 22 else float(series.iloc[0])
                    price_3m    = float(series.iloc[0])

                    chg_1w  = (price_now - price_1w)  / price_1w  * 100
                    chg_1m  = (price_now - price_1m)  / price_1m  * 100
                    chg_3m  = (price_now - price_3m)  / price_3m  * 100

                    # ── Momentum score (normalized composite) ──
                    # Weight: 3M=40%, 1M=40%, 1W=20%
                    momentum = chg_3m * 0.40 + chg_1m * 0.40 + chg_1w * 0.20

                    # ── Signal classification ──
                    if momentum > 8:    signal = "🔥 強力流入"
                    elif momentum > 3:  signal = "📈 緩步流入"
                    elif momentum > -3: signal = "⚖️ 資金持平"
                    elif momentum > -8: signal = "📉 緩步流出"
                    else:               signal = "❄️ 大幅流出"

                    results.append({
                        "name":     name_zh,
                        "ticker":   ticker,
                        "emoji":    emoji,
                        "category": category,
                        "price":    price_now,
                        "chg_1w":   chg_1w,
                        "chg_1m":   chg_1m,
                        "chg_3m":   chg_3m,
                        "momentum": momentum,
                        "signal":   signal,
                    })

                # Sort by momentum desc
                results.sort(key=lambda x: x['momentum'], reverse=True)
                for i, r in enumerate(results):
                    r['rank'] = i + 1

                st.session_state.sector_data = results
                st.toast(f"✅ 族群熱度掃描完成！共 {len(results)} 個板塊", icon="🔥")
            except Exception as e:
                st.error(f"❌ 族群資料擷取失敗: {e}")
                st.session_state.sector_map_active = False
                return

    results = st.session_state.get('sector_data', [])
    if not results:
        st.toast("⚠️ 無有效族群數據", icon="⚡")
        return

    # ── Refresh button ────────────────────────────────────────────────────────
    col_ref, _ = st.columns([1, 4])
    with col_ref:
        st.markdown('<div class="action-wrap">', unsafe_allow_html=True)
        if st.button("🔄  重新掃描", key="btn_sector_refresh"):
            st.session_state.pop('sector_data', None)
            st.toast("🔄 重新掃描中…", icon="⏳")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Summary KPI Row ───────────────────────────────────────────────────────
    hot_sectors  = [r for r in results if r['momentum'] > 3]
    cold_sectors = [r for r in results if r['momentum'] < -3]
    best         = results[0]
    worst        = results[-1]
    avg_mom      = sum(r['momentum'] for r in results) / len(results)

    # Rotation signal
    if avg_mom > 5:      rb_label, rb_col, rb_rgb = "🚀 全面進攻期", "#00FF7F", "0,255,127"
    elif avg_mom > 0:    rb_label, rb_col, rb_rgb = "📈 資金緩步入市", "#FFD700", "255,215,0"
    elif avg_mom > -5:   rb_label, rb_col, rb_rgb = "⚖️ 資金觀望輪動", "#00F5FF", "0,245,255"
    else:                rb_label, rb_col, rb_rgb = "❄️ 全面撤退期", "#FF3131", "255,49,49"

    _kpi_row(
        ("HOT SECTORS",  str(len(hot_sectors)),  f"動能 > +3% 族群",            "#FF3131"),
        ("COLD SECTORS", str(len(cold_sectors)), f"動能 < −3% 族群",            "#26A69A"),
        ("TOP SECTOR",   best['emoji'],          f"{best['name']} {best['chg_3m']:+.1f}%", "#FFD700"),
        ("AVG MOMENTUM", f"{avg_mom:+.1f}",      rb_label,                      rb_col),
    )

    # ── HEAT GRID — 11 Sector Cards ───────────────────────────────────────────
    st.markdown('<div class="sector-grid">', unsafe_allow_html=True)
    cards_html = ""
    for r in results:
        mom = r['momentum']
        chg_display = r['chg_3m']  # 3-month as headline change

        # Color mapping: heat → red, cold → teal, neutral → gold
        if mom > 8:    sc_color, sc_rgb, sc_glow_a = "#FF3131", "255,49,49",   "0.15"
        elif mom > 3:  sc_color, sc_rgb, sc_glow_a = "#FF8C42", "255,140,66",  "0.10"
        elif mom > 0:  sc_color, sc_rgb, sc_glow_a = "#FFD700", "255,215,0",   "0.08"
        elif mom > -3: sc_color, sc_rgb, sc_glow_a = "#00F5FF", "0,245,255",   "0.06"
        elif mom > -8: sc_color, sc_rgb, sc_glow_a = "#26A69A", "38,166,154",  "0.08"
        else:          sc_color, sc_rgb, sc_glow_a = "#6C757D", "108,117,125", "0.04"

        # Bar width: normalize momentum to 0–100%
        bar_w = min(100, max(3, (mom + 20) / 40 * 100))

        # Arrow for display
        arrow = "▲" if chg_display >= 0 else "▼"
        chg_color = sc_color

        cards_html += f"""
<div class="sector-card" style="--sc-color:{sc_color};--sc-glow:rgba({sc_rgb},{sc_glow_a});">
  <div class="heat-strip"></div>
  <div class="sc-rank">{r['rank']}</div>
  <div class="sc-emoji">{r['emoji']}</div>
  <div class="sc-name">{r['name']}</div>
  <div class="sc-ticker">{r['ticker']} · {r['category']}</div>
  <div class="sc-change" style="color:{chg_color};">{arrow}{abs(chg_display):.1f}%</div>
  <div style="font-family:var(--f-mono);font-size:9px;color:#445566;letter-spacing:1px;margin-top:2px;">
    1W: <span style="color:{sc_color};">{r['chg_1w']:+.1f}%</span>
    &nbsp;·&nbsp;
    1M: <span style="color:{sc_color};">{r['chg_1m']:+.1f}%</span>
  </div>
  <div class="sc-bar-bg">
    <div class="sc-bar-fill" style="width:{bar_w:.0f}%;"></div>
  </div>
  <div class="sc-signal">{r['signal']}</div>
</div>"""

    st.markdown(cards_html + '</div>', unsafe_allow_html=True)

    # ── Plotly Horizontal Bar — Momentum Ranking ──────────────────────────────
    st.markdown(
        '<div style="font-family:var(--f-display);font-size:20px;color:#00F5FF;'
        'letter-spacing:3px;margin:20px 0 8px;">MOMENTUM RANKING  ·  3-MONTH</div>',
        unsafe_allow_html=True
    )

    sorted_results = sorted(results, key=lambda x: x['momentum'])
    names  = [f"{r['emoji']} {r['name']}" for r in sorted_results]
    moms   = [r['momentum'] for r in sorted_results]
    colors = []
    for m in moms:
        if m > 8:    colors.append("#FF3131")
        elif m > 3:  colors.append("#FF8C42")
        elif m > 0:  colors.append("#FFD700")
        elif m > -3: colors.append("#00F5FF")
        elif m > -8: colors.append("#26A69A")
        else:        colors.append("#556677")

    fig = go.Figure(go.Bar(
        x=moms, y=names,
        orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{m:+.1f}%" for m in moms],
        textposition='outside',
        textfont=dict(family='JetBrains Mono', size=11, color='rgba(180,200,220,0.7)'),
        hovertemplate='%{y}<br>動能分數: %{x:+.2f}%<extra></extra>'
    ))
    fig.add_vline(x=0, line_color='rgba(255,215,0,0.35)', line_width=2)
    fig.update_layout(
        height=max(380, len(sorted_results) * 34),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(8,12,18,0.5)',
        font=dict(family='JetBrains Mono', color='#667788'),
        margin=dict(l=10, r=80, t=12, b=12),
        xaxis=dict(
            showgrid=True, gridcolor='rgba(255,255,255,0.04)',
            zeroline=False, title_text='',
            tickfont=dict(color='#334455')
        ),
        yaxis=dict(showgrid=False, tickfont=dict(color='#8899AA', size=13)),
        bargap=0.28,
    )
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Rotation Intel (Typewriter) ───────────────────────────────────────────
    rotation_text = (
        f"【族群資金輪動偵測】市場整體動能指數 {avg_mom:+.1f}%，判定：{rb_label}。\n"
        f"最強族群：{best['emoji']} {best['name']} (3M {best['chg_3m']:+.1f}%，{best['signal']})。\n"
        f"最弱族群：{worst['emoji']} {worst['name']} (3M {worst['chg_3m']:+.1f}%，{worst['signal']})。\n"
        f"共 {len(hot_sectors)} 個族群資金流入 / {len(cold_sectors)} 個族群資金流出。操作建議：聚焦 TOP 3 族群，迴避末 3 族群。"
    )
    cache_key = f"sector_streamed_{len(results)}_{best['ticker']}"
    if cache_key not in st.session_state:
        st.write_stream(_stream_text(rotation_text, speed=0.012))
        st.session_state[cache_key] = True
    else:
        st.markdown(
            f'<div style="font-family:var(--f-mono);font-size:11px;color:rgba(180,200,220,0.55);'
            f'line-height:1.8;padding:10px 0;">{rotation_text}</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        f'<div class="titan-foot">Sector Heat Map V300 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────────────────────────────────────

def render_1_5_turnover():
    # ══════════════════════════════════════════════════════════════════════
    # 1.5 成交重心 — 第一性原則重建
    #
    # 核心問題：「錢在哪裡流動？」
    #
    # 第一性原則：
    #   成交額是市場最民主的投票機制。主力藏得住倉位、藏得住意圖，
    #   但藏不住「資金流向」—— 當大資金進場，必然製造巨額成交。
    #   成交重心 = 當日全市場前 100 大成交額個股的集中地帶，
    #   是偵測「主力正在佈局哪裡」的最直接雷達。
    #
    # 為什麼是 TOP 100 而不是 TOP 10？
    #   TOP 10 容易被特定事件（如業績發布）扭曲。
    #   TOP 100 能呈現市場整體的「資金輪動結構」，
    #   讓我們看清哪個族群在吸金、哪個族群在失血。
    # ══════════════════════════════════════════════════════════════════════
    _sec_header("💹", "全市場成交重心偵測系統 · TOP 100", "TURNOVER GRAVITY SCANNER v3.0")
    macro, _, _ = _load_engines()

    # ── 第一性原則導言 ─────────────────────────────────────────────────────
    st.markdown("""
<div style="background:rgba(0,0,0,0.32);border:1px solid rgba(255,163,10,0.15);
     border-left:3px solid rgba(255,163,10,0.55);border-radius:14px;
     padding:16px 20px;margin-bottom:20px;font-family:var(--f-mono);
     font-size:11px;color:rgba(200,215,230,0.7);line-height:1.9;">

<span style="color:#FFA07A;font-weight:700;letter-spacing:2px;">█ 第一性原則 — 為什麼成交額是「資金意圖」最誠實的泄露者？</span><br><br>

市場裡存在一個悖論：主力機構可以透過市場操作製造假象，
但他們無法假造「成交量」——每一筆成交都意味著有人真實付出了資金。<br><br>

<span style="color:#FFA07A;">成交重心的三大戰術意義：</span><br>
→ <span style="color:#FFD700;">資金聚焦點</span>：TOP 100 成交額代表當日 80%+ 的市場有效資金集中地<br>
→ <span style="color:#00FF7F;">族群輪動信號</span>：連續 3 日成交重心偏移 = 主力正在切換戰場的強力訊號<br>
→ <span style="color:#00F5FF;">量能確認工具</span>：股價創高但成交掉出 TOP 100 = 無量上漲，假突破警訊<br><br>

<span style="color:#FFA07A;">讀取方法：</span>掃描結果後，觀察 TOP 3 的族群是否集中 → 集中代表主力聚焦（趨勢性行情）；
分散代表資金無方向感（盤整格局），需等待成交重心形成共識再進場。

</div>""", unsafe_allow_html=True)

    # ── 掃描引擎 ─────────────────────────────────────────────────────────
    _render_leader_dashboard(
        session_state_key="w15_data",
        fetch_function=macro.get_dynamic_turnover_leaders,
        top_n=100,
        sort_key_name="成交值"
    )

    # ── 掃描後戰術指引 ────────────────────────────────────────────────────
    df_result = st.session_state.get('w15_data', pd.DataFrame())
    if not df_result.empty:
        st.markdown("""
<div style="background:rgba(0,0,0,0.35);border:1px solid rgba(255,163,10,0.12);
     border-radius:14px;padding:16px 20px;margin-top:16px;font-family:var(--f-mono);
     font-size:11px;color:rgba(180,200,220,0.65);line-height:1.9;">

<span style="color:#FFA07A;letter-spacing:2px;font-weight:700;">█ 成交重心 · 使用指南（掃描完成後的操作流程）</span><br><br>

<span style="color:#FFD700;">STEP 1 — 識別族群共識：</span>
觀察 TOP 10 中哪個板塊出現次數最多 → 這就是當日「主力共識族群」，優先跟進。<br><br>

<span style="color:#FFD700;">STEP 2 — 量能質量判斷：</span>
排名越前且趨勢為「多頭」= 主力積極吸籌。排名前但趨勢「空頭」= 可能是出貨成交，避免追高。<br><br>

<span style="color:#FFD700;">STEP 3 — 連日追蹤機制：</span>
同一標的連續 3 日位於 TOP 20 且呈多頭趨勢 → 是主力進場的最強確認訊號，可納入候選名單。<br><br>

<span style="color:#FFD700;">STEP 4 — 量縮出場訊號：</span>
持倉個股從 TOP 50 滑落至 TOP 100 以外，且股價同步停滯 → 主力可能退出，考慮降倉或出場。

</div>""", unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">Turnover Gravity Scanner V300 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────────────────

def render_1_6_trend_radar():
    # ══════════════════════════════════════════════════════════════════════
    # 1.6 趨勢雷達 — 第一性原則重建
    #
    # 核心問題：「市場的領頭羊（龍頭股）現在多強？」
    #
    # 第一性原則：
    #   市場牛熊的最本質特徵不是指數點位，而是「高價權值股的健康程度」。
    #   高價股（500元以上）通常是法人、外資重倉的核心持股，
    #   它們的走勢代表「大戶資金的集體共識」。
    #
    #   87MA（神奇均線）的由來：
    #   87 個交易日 ≈ 4 個月 ≈ 一季財報周期。
    #   站上 87MA = 四季度平均成本線以上 = 法人季度成本已獲利
    #   = 法人無需急於賣出 = 多頭趨勢確立。
    #   跌破 87MA = 法人季度持倉套牢 = 法人倒貨壓力出現 = 趨勢反轉警訊。
    #
    # 趨勢雷達 = 高價股的「生命體徵監測器」
    # ══════════════════════════════════════════════════════════════════════
    _sec_header("👑", "高價權值股趨勢雷達 · 87MA 生命線偵測系統", "TREND RADAR v3.0 — TOP 50")
    macro, _, _ = _load_engines()

    # ── 第一性原則導言 ─────────────────────────────────────────────────────
    st.markdown("""
<div style="background:rgba(0,0,0,0.32);border:1px solid rgba(147,112,219,0.18);
     border-left:3px solid rgba(147,112,219,0.6);border-radius:14px;
     padding:16px 20px;margin-bottom:20px;font-family:var(--f-mono);
     font-size:11px;color:rgba(200,215,230,0.7);line-height:1.9;">

<span style="color:#9370DB;font-weight:700;letter-spacing:2px;">█ 第一性原則 — 為什麼高價股是市場最敏感的「礦坑金絲雀」？</span><br><br>

在所有技術分析工具中，最能揭露市場「真實走勢」的不是 K 線，而是高價股的健康狀態。<br><br>

<span style="color:#9370DB;">核心邏輯鏈：</span><br>
法人選股首選高股價 × 高流動性個股 → 500元以上權值股是法人「必持倉」→
法人資金進出高度反映在這些股的均線位置 → 87MA 以上 = 法人持倉有利可圖 = 不急於出貨<br><br>

<span style="color:#9370DB;">87MA 神奇均線的第一性原理：</span><br>
→ 87 個交易日 ≈ <span style="color:#FFD700;">4.3 個月 ≈ 一個財報週期</span><br>
→ 站上 87MA = 買進成本在過去一季均線以下 = 法人季度倉位浮盈狀態 = <span style="color:#00FF7F;">趨勢安全</span><br>
→ 跌破 87MA = 法人季度平均成本套牢 = 賣壓從法人端開始積累 = <span style="color:#FF3131;">趨勢危險</span><br><br>

<span style="color:#9370DB;">趨勢雷達使用方式：</span>掃描後找出「股價最高 × 趨勢多頭 × 87MA 上升」的標的，
這類個股代表法人願意在高位繼續持有，是最強勢龍頭，是選股系統的優先篩選池。

</div>""", unsafe_allow_html=True)

    # ── 掃描引擎 ─────────────────────────────────────────────────────────
    _render_leader_dashboard(
        session_state_key="w16_data",
        fetch_function=macro.get_high_price_leaders,
        top_n=50,
        sort_key_name="股價"
    )

    # ── 掃描後戰術指引 ────────────────────────────────────────────────────
    df_result = st.session_state.get('w16_data', pd.DataFrame())
    if not df_result.empty:
        st.markdown("""
<div style="background:rgba(0,0,0,0.35);border:1px solid rgba(147,112,219,0.12);
     border-radius:14px;padding:16px 20px;margin-top:16px;font-family:var(--f-mono);
     font-size:11px;color:rgba(180,200,220,0.65);line-height:1.9;">

<span style="color:#9370DB;letter-spacing:2px;font-weight:700;">█ 趨勢雷達 · 解讀框架 — 四種戰術情境</span><br><br>

<span style="color:#00FF7F;">【A 類 — 頂級多頭結構】</span>
股價 > 500，趨勢多頭，87MA 上揚，格蘭碧法則 Rule 1/2 ：
→ 法人控盤中，可作為「核心倉位」的持有標的，跌破 87MA 才考慮出場。<br><br>

<span style="color:#FFD700;">【B 類 — 回測買點】</span>
趨勢多頭但股價剛剛從 87MA 上方回測，格蘭碧 Rule 3（均線扣抵支撐）：
→ 是主動佈局的黃金位置，但需確認回測時成交量縮（代表無主力出貨）。<br><br>

<span style="color:#FF6B35;">【C 類 — 警示觀察】</span>
趨勢中性或剛剛從多頭轉中性，87MA 由上揚轉平：
→ 列入觀察名單，不新增倉位。等待趨勢明確再行動。<br><br>

<span style="color:#FF3131;">【D 類 — 空頭結構，絕對迴避】</span>
趨勢空頭，股價位於 87MA 下方，均線向下：
→ 即便股價便宜也不進場。空頭結構中「便宜」意味更大跌幅的開始。
法人仍在出貨，沒有任何理由讓散戶先於法人吃到底部。

</div>""", unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">Trend Radar V300 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────────────────

def render_1_7_predator():
    # ══════════════════════════════════════════════════════════════════════
    # 1.7 台指獵殺 (WTX Predator) — 第一性原則重建
    #
    # 核心問題：「本月台指期會在哪裡結算？」
    #
    # 第一性原則：
    #   市場並非隨機遊走（Random Walk）——期貨結算存在「慣性引力」。
    #   台指期每月第三個週三結算，過去 12 個月的結算區間
    #   形成了一個「歷史慣性分佈」，這個分佈的統計特性可預測
    #   本月結算的最可能目標帶。
    #
    #   棒球比喻的第一性原理：
    #   開盤價 = 打者站上打擊區的「起始位置」（錨定點）
    #   過去 12 月的結算移動幅度 = 打者的「揮棒能力統計」
    #   · 1B（一壘安打）= 過去 12 月的最小結算移動幅度 × 50%
    #   · 2B（二壘安打）= 過去 12 月的最小結算移動幅度（保守目標）
    #   · 3B（三壘安打）= 過去 12 月的平均結算移動幅度（基準目標）
    #   · HR（全壘打）  = 過去 12 月的最大結算移動幅度（極端目標）
    #   方向（收紅/收黑）由「當月開盤錨定 vs 當前走勢」決定。
    # ══════════════════════════════════════════════════════════════════════
    _sec_header("🎯", "台指期月K結算目標價推導 · 歷史慣性獵殺系統", "WTX PREDATOR v3.0")

    # ── 第一性原則導言 ─────────────────────────────────────────────────────
    st.markdown("""
<div style="background:rgba(0,0,0,0.32);border:1px solid rgba(255,49,49,0.18);
     border-left:3px solid rgba(255,49,49,0.55);border-radius:14px;
     padding:16px 20px;margin-bottom:20px;font-family:var(--f-mono);
     font-size:11px;color:rgba(200,215,230,0.7);line-height:1.9;">

<span style="color:#FF3131;font-weight:700;letter-spacing:2px;">█ 第一性原則 — 台指期結算不是隨機的，而是「歷史慣性」的再現</span><br><br>

主流金融理論（效率市場假說）認為市場完全隨機、無法預測。
但台指期的結算有一個獨特的「制度性引力」——<span style="color:#FFD700;">每月固定結算機制</span>製造出
大量選擇權賣方的對沖行為，使得期指結算點傾向收斂在特定的統計帶內。<br><br>

<span style="color:#FF3131;">WTX Predator 的核心假設：</span><br>
① 市場主力（期貨商、外資）在結算前會主動<span style="color:#FFD700;">「引導」價格靠近有利的結算點</span><br>
② 這種引導行為受到<span style="color:#FFD700;">過去 12 個月結算慣性</span>的約束，不會無限延伸<br>
③ 因此，用歷史結算幅度的統計分佈（min/avg/max）可以
   <span style="color:#00FF7F;">框定本月最可能的結算目標帶</span>，提供精確的攻守參考位<br><br>

<span style="color:#FF3131;">風險聲明：</span>這是統計推導，不是精確預言。目標帶是概率範圍，非保證。
應搭配宏觀燈號（1.1）和族群動能（1.4）綜合研判，切勿單獨孤注一擲。

</div>""", unsafe_allow_html=True)

    st.markdown('<div class="action-wrap">', unsafe_allow_html=True)
    if st.button("🔮  DERIVE WTX TARGETS — 推導本月台指期目標價", key="btn_futures"):
        st.toast("🚀 推導台指期目標價中…", icon="⏳")
        with st.spinner("Analyzing 12-month settlement inertia patterns…"):
            st.session_state['futures_result'] = _calculate_futures_targets()
        st.toast("✅ 台指期目標價推導完成！", icon="🎯")
    st.markdown('</div>', unsafe_allow_html=True)

    res = st.session_state.get('futures_result', None)
    if res is None:
        st.markdown('<div class="empty-state"><div class="empty-icon">🎯</div>'
                    '<div class="empty-text">CLICK TO DERIVE TARGETS</div></div>', unsafe_allow_html=True)
        return
    if "error" in res:
        st.toast(f"⚠️ {res['error']}", icon="⚡")
        return

    is_red    = res['is_red']
    bar_color = "#d62728" if is_red else "#2ca02c"
    cf_rgb    = "214,39,40" if is_red else "44,160,44"
    bias      = res['price'] - res['anc']
    bias_col  = "#FF3131" if bias > 0 else "#26A69A"
    bias_pct  = (bias / res['anc'] * 100) if res['anc'] != 0 else 0

    # ── KPI Row ──────────────────────────────────────────────────────────────
    _kpi_row(
        ("ANCHOR OPEN",   f"{res['anc']:,.0f}",   res['name'],           "#00F5FF"),
        ("CURRENT PRICE", f"{res['price']:,.0f}",  f"{bias:+.0f} pts",   bias_col),
        ("BIAS FROM ANCHOR", f"{bias_pct:+.2f}%", "偏離開盤錨定點",      bias_col),
    )

    # ── Direction Banner ─────────────────────────────────────────────────────
    ctrl_text = "🔴 多方控盤 — 月K 慣性收長紅 K 棒" if is_red else "🟢 空方控盤 — 月K 慣性收長黑 K 棒"
    st.markdown(f'<div class="ctrl-flag" style="--cf-rgb:{cf_rgb};">{ctrl_text}</div>',
                unsafe_allow_html=True)

    # ── 深度第一性原則分析 Typewriter ─────────────────────────────────────────
    st.markdown("""
<div style="background:rgba(0,0,0,0.4);border:1px solid rgba(255,49,49,0.1);
     border-radius:16px;padding:20px 24px;margin:16px 0;font-family:var(--f-mono);
     font-size:13px;color:rgba(200,215,230,0.85);line-height:1.9;">""", unsafe_allow_html=True)

    # 目標達成判斷
    t1_hit = (is_red and res['price'] >= res['t']['1B']) or (not is_red and res['price'] <= res['t']['1B'])
    t2_hit = (is_red and res['price'] >= res['t']['2B']) or (not is_red and res['price'] <= res['t']['2B'])
    t3_hit = (is_red and res['price'] >= res['t']['3B']) or (not is_red and res['price'] <= res['t']['3B'])
    hr_hit = (is_red and res['price'] >= res['t']['HR']) or (not is_red and res['price'] <= res['t']['HR'])

    t1_status = "✅ 已達標" if t1_hit else "⏳ 未達標"
    t2_status = "✅ 已達標" if t2_hit else "⏳ 未達標"
    t3_status = "✅ 已達標" if t3_hit else "⏳ 未達標"
    hr_status = "🏆 全壘打達標！" if hr_hit else "⏳ 未達標"

    # 當前進度研判
    if hr_hit:
        progress_txt = "已達全壘打！若指數繼續延伸，謹防過熱逆轉風險。考慮分批減倉。"
    elif t3_hit:
        progress_txt = f"已達 3 壘，距全壘打還差 {abs(res['t']['HR'] - res['price']):,.0f} 點。可持倉等待，但上方空間有限，需警覺。"
    elif t2_hit:
        progress_txt = f"已達 2 壘，下一目標 3 壘 {res['t']['3B']:,.0f}（距 {abs(res['t']['3B'] - res['price']):,.0f} 點）。趨勢確立，可持倉。"
    elif t1_hit:
        progress_txt = f"已突破 1 壘，動能確認。關注是否能一鼓作氣挑戰 2 壘 {res['t']['2B']:,.0f}（距 {abs(res['t']['2B'] - res['price']):,.0f} 點）。"
    else:
        progress_txt = f"尚未突破 1 壘（{res['t']['1B']:,.0f}），{'多' if is_red else '空'}方動能需觀察。若月末前無法突破，慣性動能減弱。"

    pred_analysis = f"""
═══════════════════════════════════════════════════════════
🎯 WTX PREDATOR v3.0 — 台指期月K慣性獵殺分析
   合約：{res['name']}  |  方向：{'多方控盤（紅K）' if is_red else '空方控盤（黑K）'}
═══════════════════════════════════════════════════════════

【一、核心邏輯 — 為什麼開盤是「錨定點」？】
  開盤價（{res['anc']:,.0f}）是本月的「行情起點錨定坐標」。
  月K棒的收盤方向由「當前股價是否高於/低於開盤」決定：
  · 現價 {res['price']:,.0f} vs 開盤 {res['anc']:,.0f} → 偏離 {bias:+.0f} 點 ({bias_pct:+.2f}%)
  · 方向確認：{'✅ 多方占優，月K收紅機率較高' if is_red else '✅ 空方占優，月K收黑機率較高'}

  重要：方向判定越接近月末越準確（收盤前 5 個交易日是最後決戰時機）。
  在月初階段，方向仍可能逆轉，需配合 1.1 宏觀燈號綜合研判。

【二、目標帶推導邏輯（過去 12 個月結算慣性統計）】
  利用過去 12 個月每月結算日的「實際移動幅度」建立統計分佈：
  · 最小幅度（保守場景）→ 1B 一壘安打目標
  · 1/2 最小幅度（初始突破）→ 入場確認點
  · 平均幅度（歷史最可能場景）→ 3B 三壘安打主要目標  
  · 最大幅度（極端場景）→ HR 全壘打黑天鵝目標

  當前目標帶（{'多方向上' if is_red else '空方向下'}）：
  ├─ 1 壘 {res['t']['1B']:,.0f}  →  {t1_status}
  ├─ 2 壘 {res['t']['2B']:,.0f}  →  {t2_status}
  ├─ 3 壘 {res['t']['3B']:,.0f}  →  {t3_status}
  └─ 全壘打 {res['t']['HR']:,.0f} →  {hr_status}

【三、當前進度判讀】
  {progress_txt}

【四、為什麼要看「月K」而不是「日K」？】
  台指期月結算的特殊性在於：
  ① 選擇權賣方在結算前需主動對沖 → 製造「結算磁吸效應」
  ② 外資每月的法人部位調整高度集中在月末 3 天 → 最大量能出現在月末
  ③ 月K的方向性遠比日K穩定（月K紅轉黑的機率遠低於日K）
  因此：若本月月K確立多頭方向，可在日K拉回時佈局，以月K結算作為停利目標。

【五、操作策略推演（基於當前數據）】
  {'多方策略：' if is_red else '空方策略：'}
  {'① 確認現價站穩於開盤錨定 ' + f'{res["anc"]:,.0f}' + ' 以上（每日收盤確認）\n  ② 日K 拉回不破錨定 ±0.5% 均為合理回測，可加碼多方\n  ③ 主要目標：3 壘 ' + f'{res["t"]["3B"]:,.0f}' + '（歷史慣性平均值）\n  ④ 若 VIX 突然飆升 > 25，暫停多方策略，等 VIX 回穩再執行' if is_red else '① 確認現價跌穿開盤錨定 ' + f'{res["anc"]:,.0f}' + ' 以下（每日收盤確認）\n  ② 日K 反彈不過錨定 ±0.5% 均為合理反彈，可加碼空方（或減少多方倉位）\n  ③ 主要目標：3 壘 ' + f'{res["t"]["3B"]:,.0f}' + '（向下歷史慣性平均值）\n  ④ 若宏觀燈號轉為紅燈，優先保護資本而非追空'}

  停損設定：月K方向逆轉（收盤站回/跌破錨定 {res['anc']:,.0f} 且偏離超過 1.5%）→ 停損出場。

【六、歷史驗證局限性說明】
  WTX Predator 基於統計慣性，有以下場景會失效：
  ① 重大黑天鵝（戰爭/金融危機）→ 慣性失效，HR 被突破但方向急轉
  ② 月初假突破 → 月前半段不可靠，越接近結算日越準確
  ③ 流動性危機 → 外資強制平倉打亂慣性節奏
  → 因此，永遠搭配 1.1 宏觀燈號使用。紅燈期間慣性策略暫停。

═══════════════════════════════════════════════════════════
"""

    key_pred = 'pred_streamed_v3'
    if key_pred not in st.session_state:
        st.write_stream(_stream_text(pred_analysis, speed=0.006))
        st.session_state[key_pred] = True
    else:
        st.markdown(
            f'<pre style="white-space:pre-wrap;font-size:13px;'
            f'color:rgba(200,215,230,0.8);line-height:1.85;">{pred_analysis}</pre>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Baseball Target Cards ─────────────────────────────────────────────────
    def hit_cls(tg):
        return "hit" if (is_red and res['price'] >= tg) or (not is_red and res['price'] <= tg) else "miss"
    def hit_lbl(tg): return "✅ 達標" if "hit" == hit_cls(tg) else "⏳ 未達"

    st.markdown(f"""
<div class="bases-grid">
  <div class="base-card {hit_cls(res['t']['1B'])}">
    <div class="base-name">1 壘 — 保守目標</div>
    <div class="base-price">{res['t']['1B']:,.0f}</div>
    <div class="base-status">{hit_lbl(res['t']['1B'])}</div>
  </div>
  <div class="base-card {hit_cls(res['t']['2B'])}">
    <div class="base-name">2 壘 — 最小幅度</div>
    <div class="base-price">{res['t']['2B']:,.0f}</div>
    <div class="base-status">{hit_lbl(res['t']['2B'])}</div>
  </div>
  <div class="base-card {hit_cls(res['t']['3B'])}">
    <div class="base-name">3 壘 — 歷史均值</div>
    <div class="base-price">{res['t']['3B']:,.0f}</div>
    <div class="base-status">{hit_lbl(res['t']['3B'])}</div>
  </div>
  <div class="base-card hr {hit_cls(res['t']['HR'])}">
    <div class="base-name" style="color:#FF6B6B">🏠 全壘打 — 極端場景</div>
    <div class="base-price" style="color:#FF8888">{res['t']['HR']:,.0f}</div>
    <div class="base-status">{hit_lbl(res['t']['HR'])}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── ALTAIR BASEBALL K-BAR CHART ────────────────────────────────────────────
    chart_df = pd.DataFrame({
        "Label":     ["本月"],
        "Anchor":    [res['anc']],
        "Current":   [res['price']],
        "Target_HR": [res['t']['HR']],
        "Target_1B": [res['t']['1B']],
        "Target_2B": [res['t']['2B']],
        "Target_3B": [res['t']['3B']],
    })

    base  = alt.Chart(chart_df).encode(x=alt.X('Label', axis=None))
    ghost = (base.mark_bar(size=72, color="#ffdddd" if is_red else "#ddffdd", opacity=0.25)
             .encode(y=alt.Y('Anchor', scale=alt.Scale(zero=False), title='Points'),
                     y2='Target_HR'))
    real  = (base.mark_bar(size=36, color=bar_color, opacity=0.96)
             .encode(y='Anchor', y2='Current'))

    chart = ghost + real
    for k in ['1B', '2B', '3B']:
        chart += (
            base.mark_tick(color='#FFD700', thickness=2, size=86)
            .encode(y=f'Target_{k}')
            + base.mark_text(dx=52, align='left', color='#FFD700',
                             fontSize=14, fontWeight='bold', font='JetBrains Mono')
            .encode(y=f'Target_{k}', text=alt.value(f"{k}  {res['t'][k]:,.0f}"))
        )
    chart += (
        base.mark_tick(color='#FF3131', thickness=4, size=100)
        .encode(y='Target_HR')
        + base.mark_text(dx=56, align='left', color='#FF3131',
                         fontSize=15, fontWeight='bold', font='JetBrains Mono')
        .encode(y='Target_HR', text=alt.value(f"HR  {res['t']['HR']:,.0f}"))
    )

    _, cc, _ = st.columns([1, 2, 1])
    with cc:
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.altair_chart(
            chart.properties(height=460, background='rgba(0,0,0,0)')
                 .configure_view(strokeOpacity=0)
                 .configure_axis(labelColor='#334455', titleColor='#223344',
                                 gridColor='rgba(255,255,255,0.04)'),
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">WTX Predator V300 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
#  RENDER MAP
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

# Icon accent per poster card
_POSTER_ACCENT = {
    "1.1": "#00F5FF",
    "1.2": "#FF6B6B",
    "1.3": "#FFD700",
    "1.4": "#FF5722",
    "1.5": "#FFA07A",
    "1.6": "#9370DB",
    "1.7": "#FF3131",
}


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY — Netflix Poster Rail + Cinematic Content Frame
#  [UPGRADE #1] Tactical Guide Dialog on first visit
# ══════════════════════════════════════════════════════════════════════════════
def render():
    """Tab 1 — Cinematic Trading Experience (Director's Cut V300)"""
    _inject_css()

    # [UPGRADE #1] Onboarding dialog — show once per session
    if not st.session_state.get('tab1_guided', False):
        _show_tactical_guide()
        return  # dialog blocks rendering; will rerun after close

    if 'tab1_active' not in st.session_state:
        st.session_state.tab1_active = "1.1"
    active = st.session_state.tab1_active

    # ── SYSTEM BAR ────────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="display:flex;align-items:baseline;justify-content:space-between;
            padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.06);
            margin-bottom:22px;">
  <div>
    <span style="font-family:'Bebas Neue',sans-serif;font-size:26px;
                 color:#FFD700;letter-spacing:3px;
                 text-shadow:0 0 22px rgba(255,215,0,0.4);">
      🛡️ 宏觀風控指揮中心
    </span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:9px;
                 color:rgba(255,215,0,0.3);letter-spacing:3px;
                 border:1px solid rgba(255,215,0,0.12);border-radius:20px;
                 padding:3px 13px;margin-left:14px;background:rgba(255,215,0,0.025);">
      TITAN OS V300
    </span>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
              color:rgba(200,215,230,0.25);letter-spacing:2px;text-align:right;line-height:1.7;">
    {datetime.now().strftime('%H:%M:%S')}<br>{datetime.now().strftime('%Y · %m · %d')}
  </div>
</div>""", unsafe_allow_html=True)

    # ── NETFLIX POSTER RAIL ───────────────────────────────────────────────────
    st.markdown('<div class="nav-deck-frame"><div class="nav-deck-label">⬡ module select — poster rail</div>', unsafe_allow_html=True)

    cols = st.columns(7)
    for col, (code, emoji, label_zh, label_en) in zip(cols, SUB_MODULES):
        accent  = _POSTER_ACCENT.get(code, "#FFD700")
        is_active = (active == code)
        act_cls   = "active" if is_active else ""

        with col:
            # ── Poster card drawn FIRST (visual layer) ───────────────────────
            st.markdown(f"""
<div class="poster-card {act_cls}" style="--poster-accent:{accent};">
  <div class="heat-strip" style="background:linear-gradient(90deg,transparent,{accent} 50%,transparent);opacity:{'1' if is_active else '0'};"></div>
  <div class="poster-icon">{emoji}</div>
  <div class="poster-code">{code}</div>
  <div class="poster-text">{label_zh}</div>
  <div class="poster-tag">{label_en}</div>
</div>""", unsafe_allow_html=True)

            # ── Invisible button on top (hit layer) — no visible chrome ──────
            if st.button(f"{emoji} {label_zh}", key=f"nav_{code}",
                         use_container_width=True):
                st.session_state.tab1_active = code
                st.rerun()

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # nav-deck-frame

    # ── CONTENT FRAME ─────────────────────────────────────────────────────────
    st.markdown('<div class="content-frame">', unsafe_allow_html=True)
    fn = RENDER_MAP.get(active)
    if fn:
        try:
            fn()
        except Exception as exc:
            import traceback
            st.error(f"❌ 子模組 {active} 渲染失敗: {exc}")
            with st.expander("🔍 Debug Trace"):
                st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)  # content-frame
