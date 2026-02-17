# ui_desktop/tab1_macro.py
# Titan SOP V300 — 宏觀風控指揮中心 (Macro Risk Command Center)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  "OPERATION UNCHAIN V301"  —  Netflix × Palantir × Tesla         ║
# ║  🔓 CRITICAL UPGRADES:                                            ║
# ║    ✅ Operation Unchain — Removed df.empty gatekeeper             ║
# ║    ✅ Manual Trigger System — User-initiated scan                 ║
# ║    ✅ Global Overwatch — S&P 500, USD/TWD, DXY tracking           ║
# ║    ✅ All V300 upgrades preserved (Toast/Typewriter/Hero/Modal)   ║
# ╚═══════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time
import yfinance as yf

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
<div style="font-family:'Rajdhani',sans-serif;font-size:15px;color:#C8D8E8;line-height:1.8;">

### 🛡️ 歡迎進入宏觀風控指揮中心

本模組是 Titan OS 的**戰略核心**，整合 7 大子系統即時監控市場脈動：

**🚦 1.1 風控儀表 (MACRO HUD)**
三燈號系統 (🟢綠/🟡黃/🔴紅) 自動判定進攻/防守態勢，搭配 VIX、PR90 籌碼分佈、PTT 散戶情緒三重驗證。

**🌍 GLOBAL OVERWATCH (NEW!)**
全球市場監控：S&P 500、美元/新台幣、美元指數三大指標即時追蹤，3個月趨勢分析。

**🌡️ 1.2 多空溫度計 / 📊 1.3 籌碼分佈 / 🗺️ 1.4 族群熱度**
高價權值股站上 87MA 的比例 = 市場體溫。籌碼分佈圖 + 族群資金流向，一眼判斷主力資金去向。

**💹 1.5 成交重心 / 👑 1.6 趨勢雷達**
全市場 TOP 100 成交重心即時掃描 + 高價權值股趨勢追蹤，附帶 87MA 扣抵預測與亞當理論反射路徑。

**🎯 1.7 台指獵殺 (WTX Predator)**
獨門戰法 — 利用過去 12 個月結算慣性推導本月台指期虛擬 K 棒，精準鎖定 1B/2B/3B/HR 結算目標價。

</div>""", unsafe_allow_html=True)
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
    ("1.4", "🗺️", "族群熱度",  "HEATMAP"),
    ("1.5", "💹", "成交重心",  "VOLUME"),
    ("1.6", "👑", "趨勢雷達",  "RADAR"),
    ("1.7", "🎯", "台指獵殺",  "PREDATOR"),
]


# ══════════════════════════════════════════════════════════════════════════════
#  [NEW] GLOBAL MARKET DATA FETCHER — Operation Overwatch
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def fetch_global_data():
    """Fetch S&P 500, USD/TWD, DXY for Global Overwatch"""
    tickers = {
        "S&P 500": "^GSPC",
        "USD/TWD": "TWD=X",
        "Dollar Index": "DX-Y.NYB"
    }
    
    try:
        # Fetch 3-month historical data
        df = yf.download(
            list(tickers.values()), 
            period="3mo", 
            progress=False
        )['Close']
        
        # Rename columns to friendly names
        if isinstance(df, pd.Series):
            df = df.to_frame()
        
        # Handle column naming
        if len(tickers) == 1:
            df.columns = [list(tickers.keys())[0]]
        else:
            col_map = {v: k for k, v in tickers.items()}
            df.columns = [col_map.get(c, c) for c in df.columns]
        
        return df
    except Exception as e:
        st.error(f"⚠️ Global data fetch failed: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_vix_data():
    """Fetch VIX data separately"""
    try:
        vix_df = yf.download("^VIX", period="3mo", progress=False)
        return vix_df
    except Exception as e:
        return pd.DataFrame()


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
.poster-card::before {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(circle at 50% 50%,
        var(--poster-accent, #FFD700) 0%, transparent 70%);
    opacity: 0; transition: opacity 0.28s;
}
.poster-card:hover::before { opacity: 0.08; }
.poster-card:hover {
    transform: translateY(-6px);
    border-color: var(--poster-accent, #FFD700);
    box-shadow: 0 12px 40px rgba(0,0,0,0.6), 0 0 0 1px var(--poster-accent, #FFD700);
}
.poster-card.active {
    background: linear-gradient(165deg, #0a0c14 0%, #141822 100%);
    border-color: var(--poster-accent, #FFD700);
    box-shadow: 0 8px 28px rgba(0,0,0,0.7), inset 0 0 0 1px var(--poster-accent, #FFD700);
}
.poster-card.active::before { opacity: 0.12; }
.poster-icon {
    font-size: 44px; margin-bottom: 4px; position: relative; z-index: 1;
}
.poster-code {
    font-family: var(--f-mono); font-size: 12px; font-weight: 700;
    color: var(--poster-accent, #FFD700); letter-spacing: 2px;
    position: relative; z-index: 1;
}
.poster-text {
    font-family: var(--f-body); font-size: 16px; font-weight: 600;
    color: #C8D8E8; margin: 2px 0; position: relative; z-index: 1;
}
.poster-tag {
    font-family: var(--f-mono); font-size: 9px; color: #445566;
    letter-spacing: 2px; text-transform: uppercase; position: relative; z-index: 1;
}

/* ══════════════════════════════════════════════════════
   3. CONTENT FRAME
══════════════════════════════════════════════════════ */
.content-frame {
    background: linear-gradient(165deg, rgba(7,8,15,0.3) 0%, rgba(10,11,20,0.5) 100%);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 20px;
    padding: 28px 32px;
    position: relative;
    min-height: 600px;
}
.content-frame::before {
    content: ''; position: absolute; top: -1px; left: 20%; right: 20%; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,245,255,0.3) 50%, transparent);
}

/* ══════════════════════════════════════════════════════
   4. SECTION HEADER
══════════════════════════════════════════════════════ */
.sec-header {
    display: flex; align-items: baseline; gap: 14px;
    padding-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 24px;
}
.sec-icon {
    font-size: 28px;
}
.sec-title {
    font-family: var(--f-display); font-size: 28px; letter-spacing: 2px;
    color: #FFF; text-shadow: 0 0 16px rgba(255,255,255,0.2);
}
.sec-pill {
    font-family: var(--f-mono); font-size: 9px; color: rgba(0,245,255,0.4);
    border: 1px solid rgba(0,245,255,0.15); border-radius: 20px;
    padding: 3px 12px; letter-spacing: 2px; text-transform: uppercase;
    background: rgba(0,245,255,0.03); margin-left: auto;
}

/* ══════════════════════════════════════════════════════
   5. KPI CARD GRID
══════════════════════════════════════════════════════ */
.kpi-grid {
    display: grid; gap: 14px; margin-bottom: 24px;
}
.kpi-g2 { grid-template-columns: repeat(2, 1fr); }
.kpi-g3 { grid-template-columns: repeat(3, 1fr); }
.kpi-g4 { grid-template-columns: repeat(4, 1fr); }

.kpi-card {
    background: rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.052);
    border-radius: 16px;
    padding: 18px 20px 16px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute; inset: 0;
    background: radial-gradient(circle at 50% 100%,
        var(--kc, #FFD700) 0%, transparent 60%);
    opacity: 0.03;
}
.kpi-label {
    font-family: var(--f-mono); font-size: 10px; color: #667788;
    letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;
}
.kpi-value {
    font-family: var(--f-display); font-size: 38px; color: var(--kc, #FFD700);
    font-weight: 900; line-height: 1; letter-spacing: 1px;
}
.kpi-sub {
    font-family: var(--f-mono); font-size: 11px; color: #445566;
    margin-top: 6px; letter-spacing: 1px;
}

/* ══════════════════════════════════════════════════════
   6. RANK CARD (For Leader Dashboard)
══════════════════════════════════════════════════════ */
.rank-card {
    background: rgba(0,0,0,0.15);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 18px;
    margin-bottom: 10px;
    transition: all 0.2s;
}
.rank-card:hover {
    background: rgba(0,0,0,0.25);
    border-color: var(--rc-accent, #FFD700);
    box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}
.rank-card.rank-1 { border-left: 3px solid #FFD700; }
.rank-card.rank-2 { border-left: 3px solid #C0C0C0; }
.rank-card.rank-3 { border-left: 3px solid #CD7F32; }

.rank-num {
    font-family: var(--f-display); font-size: 36px; color: var(--rc-accent, #FFD700);
    font-weight: 900; width: 50px; text-align: center;
}
.rank-info { flex: 1; }
.rank-name {
    font-family: var(--f-body); font-size: 18px; font-weight: 600; color: #FFF;
}
.rank-meta {
    font-family: var(--f-mono); font-size: 11px; color: #667788;
    letter-spacing: 1px; margin-top: 4px;
}
.rank-value {
    font-family: var(--f-display); font-size: 28px; font-weight: 900;
    text-align: right; line-height: 1;
}
.rank-trend {
    font-family: var(--f-mono); font-size: 12px; text-align: right; margin-top: 4px;
}

/* ══════════════════════════════════════════════════════
   7. ACTION BUTTON WRAP
══════════════════════════════════════════════════════ */
.action-wrap {
    display: flex; justify-content: center; margin: 24px 0;
}

/* ══════════════════════════════════════════════════════
   8. EMPTY STATE
══════════════════════════════════════════════════════ */
.empty-state {
    text-align: center;
    padding: 80px 20px;
    background: rgba(0,0,0,0.1);
    border: 1px dashed rgba(255,255,255,0.08);
    border-radius: 16px;
    margin: 40px 0;
}
.empty-icon {
    font-size: 72px;
    opacity: 0.2;
    margin-bottom: 16px;
}
.empty-text {
    font-family: var(--f-mono);
    font-size: 14px;
    color: #667788;
    letter-spacing: 3px;
}

/* ══════════════════════════════════════════════════════
   9. LEADER TABLE
══════════════════════════════════════════════════════ */
.ldr-tbl {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--f-mono);
    font-size: 13px;
    margin-top: 16px;
}
.ldr-tbl th {
    background: rgba(0,245,255,0.08);
    color: #00F5FF;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    font-size: 11px;
}
.ldr-tbl td {
    padding: 12px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    color: #C8D8E8;
}
.ldr-tbl tr:hover td {
    background: rgba(255,255,255,0.02);
}

/* ══════════════════════════════════════════════════════
   10. CHART WRAP
══════════════════════════════════════════════════════ */
.chart-wrap {
    background: rgba(0,0,0,0.15);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 14px;
    padding: 20px;
    margin: 16px 0;
}

/* ══════════════════════════════════════════════════════
   11. TSE GRID (Taiwan Index Analysis)
══════════════════════════════════════════════════════ */
.tse-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 14px;
}
.tse-chip {
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(0,245,255,0.1);
    border-radius: 12px;
    padding: 14px 16px;
    text-align: center;
}
.tsc-lbl {
    font-family: var(--f-mono);
    font-size: 9px;
    color: #667788;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.tsc-val {
    font-family: var(--f-body);
    font-size: 18px;
    font-weight: 700;
    color: #00F5FF;
}
.tse-deduct {
    font-family: var(--f-mono);
    font-size: 11px;
    color: #667788;
    letter-spacing: 1px;
    padding: 12px 16px;
    background: rgba(0,0,0,0.2);
    border-radius: 8px;
}

/* ══════════════════════════════════════════════════════
   12. PREDATOR BASEBALL BASES
══════════════════════════════════════════════════════ */
.bases-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 24px 0;
}
.base-card {
    background: rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s;
}
.base-card.hit {
    background: rgba(0,255,127,0.1);
    border-color: #00FF7F;
    box-shadow: 0 0 20px rgba(0,255,127,0.2);
}
.base-card.miss {
    opacity: 0.5;
}
.base-card.hr {
    border: 2px solid rgba(255,49,49,0.3);
}
.base-card.hr.hit {
    background: rgba(255,49,49,0.15);
    border-color: #FF3131;
    box-shadow: 0 0 30px rgba(255,49,49,0.4);
}
.base-name {
    font-family: var(--f-mono);
    font-size: 11px;
    color: #667788;
    letter-spacing: 2px;
    margin-bottom: 10px;
}
.base-price {
    font-family: var(--f-display);
    font-size: 32px;
    font-weight: 900;
    color: #FFD700;
    line-height: 1;
    margin-bottom: 8px;
}
.base-status {
    font-family: var(--f-mono);
    font-size: 12px;
    color: #00FF7F;
}

/* ══════════════════════════════════════════════════════
   13. CONTROL FLAG (Predator Red/Green)
══════════════════════════════════════════════════════ */
.ctrl-flag {
    display: inline-block;
    font-family: var(--f-mono);
    font-size: 13px;
    font-weight: 700;
    color: rgba(var(--cf-rgb), 1);
    border: 2px solid rgba(var(--cf-rgb), 0.4);
    border-radius: 8px;
    padding: 8px 20px;
    margin: 16px 0;
    background: rgba(var(--cf-rgb), 0.08);
    letter-spacing: 2px;
}

/* ══════════════════════════════════════════════════════
   14. HEATMAP CELL
══════════════════════════════════════════════════════ */
.heatmap-cell {
    background: var(--cell-bg, rgba(0,0,0,0.3));
    border: 1px solid var(--cell-bd, rgba(255,255,255,0.05));
    border-radius: 10px;
    padding: 16px;
    text-align: center;
    transition: all 0.2s;
}
.heatmap-cell:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 16px var(--cell-shadow, rgba(0,0,0,0.4));
}
.hm-name {
    font-family: var(--f-body);
    font-size: 15px;
    font-weight: 600;
    color: #FFF;
    margin-bottom: 8px;
}
.hm-val {
    font-family: var(--f-display);
    font-size: 28px;
    font-weight: 900;
    color: var(--cell-color, #FFD700);
    line-height: 1;
    margin-bottom: 6px;
}
.hm-sub {
    font-family: var(--f-mono);
    font-size: 10px;
    color: #667788;
    letter-spacing: 1px;
}

/* ══════════════════════════════════════════════════════
   15. TITAN FOOTER
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

/* ══════════════════════════════════════════════════════
   17. GLOBAL OVERWATCH SECTION (NEW)
══════════════════════════════════════════════════════ */
.overwatch-header {
    font-family: var(--f-display);
    font-size: 24px;
    color: #00F5FF;
    letter-spacing: 3px;
    margin: 32px 0 16px;
    text-shadow: 0 0 20px rgba(0,245,255,0.4);
}
.overwatch-subheader {
    font-family: var(--f-mono);
    font-size: 10px;
    color: #667788;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 20px;
}
.global-metric {
    background: linear-gradient(135deg, rgba(0,10,20,0.6) 0%, rgba(0,5,15,0.8) 100%);
    border: 1px solid rgba(0,245,255,0.15);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.global-metric::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 100%, rgba(0,245,255,0.08) 0%, transparent 70%);
}
.gm-label {
    font-family: var(--f-mono);
    font-size: 11px;
    color: #667788;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
    position: relative;
}
.gm-value {
    font-family: var(--f-display);
    font-size: 36px;
    font-weight: 900;
    color: #00F5FF;
    line-height: 1;
    margin-bottom: 8px;
    position: relative;
}
.gm-change {
    font-family: var(--f-mono);
    font-size: 14px;
    font-weight: 700;
    position: relative;
}
.gm-change.positive { color: #00FF7F; }
.gm-change.negative { color: #FF3131; }

/* ══════════════════════════════════════════════════════
   18. VIX GAUGE SECTION
══════════════════════════════════════════════════════ */
.vix-section {
    background: rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.052);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 32px;
}
.vix-header {
    font-family: var(--f-display);
    font-size: 22px;
    color: #FFD700;
    letter-spacing: 2px;
    margin-bottom: 16px;
    text-align: center;
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
#  [NEW] GLOBAL OVERWATCH RENDERER
# ══════════════════════════════════════════════════════════════════════════════
def _render_global_overwatch():
    """Display Global Market Data: S&P 500, USD/TWD, Dollar Index"""
    st.markdown('<div class="overwatch-header">🌍 GLOBAL OVERWATCH</div>', unsafe_allow_html=True)
    st.markdown('<div class="overwatch-subheader">Real-time tracking of key global indices</div>', unsafe_allow_html=True)
    
    # Fetch global data
    global_df = fetch_global_data()
    
    if global_df.empty:
        st.warning("⚠️ Unable to fetch global market data")
        return
    
    # Calculate current values and changes
    cols = st.columns(3)
    
    for idx, col_name in enumerate(global_df.columns):
        with cols[idx]:
            # Get current and previous day values
            current = global_df[col_name].iloc[-1]
            if len(global_df) > 1:
                previous = global_df[col_name].iloc[-2]
                change_pct = ((current - previous) / previous) * 100
            else:
                change_pct = 0.0
            
            change_class = "positive" if change_pct >= 0 else "negative"
            change_sign = "+" if change_pct >= 0 else ""
            
            # Display metric card
            st.markdown(f"""
<div class="global-metric">
    <div class="gm-label">{col_name}</div>
    <div class="gm-value">{current:,.2f}</div>
    <div class="gm-change {change_class}">{change_sign}{change_pct:.2f}%</div>
</div>
""", unsafe_allow_html=True)
    
    # Normalized Trend Chart (Last 3 months)
    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    st.markdown("""
<div style="font-family:var(--f-mono);font-size:11px;color:#667788;
letter-spacing:1.5px;text-transform:uppercase;margin-bottom:12px;">
📈 3-Month Normalized Trend Comparison
</div>""", unsafe_allow_html=True)
    
    # Normalize data (% change from first day)
    norm_df = pd.DataFrame()
    for col in global_df.columns:
        first_val = global_df[col].iloc[0]
        norm_df[col] = ((global_df[col] - first_val) / first_val) * 100
    
    # Reset index for plotting
    norm_df = norm_df.reset_index()
    norm_df.columns = ['Date'] + list(norm_df.columns[1:])
    
    # Create Plotly line chart
    fig = px.line(
        norm_df, 
        x='Date', 
        y=list(norm_df.columns[1:]),
        title="",
        labels={'value': '% Change', 'Date': ''},
        color_discrete_map={
            'S&P 500': '#FFD700',
            'USD/TWD': '#00FF7F',
            'Dollar Index': '#00F5FF'
        }
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', size=11, color='#667788'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.04)',
            gridwidth=1,
            showline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.04)',
            gridwidth=1,
            title='% Change from Start',
            showline=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color='#C8D8E8')
        ),
        hovermode='x unified',
        height=400,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    fig.update_traces(
        line=dict(width=2.5),
        hovertemplate='%{y:.2f}%<extra></extra>'
    )
    
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  [NEW] VIX GAUGE RENDERER
# ══════════════════════════════════════════════════════════════════════════════
def _render_vix_gauge():
    """Render VIX Fear Gauge"""
    st.markdown('<div class="vix-section">', unsafe_allow_html=True)
    st.markdown('<div class="vix-header">💎 VIX FEAR INDEX</div>', unsafe_allow_html=True)
    
    vix_df = fetch_vix_data()
    
    if not vix_df.empty and 'Close' in vix_df.columns:
        vix_current = float(vix_df['Close'].iloc[-1])
        
        # Determine VIX status
        if vix_current > 30:
            vix_status = "🔴 EXTREME FEAR"
            vix_color = "#FF3131"
        elif vix_current > 20:
            vix_status = "🟡 ELEVATED FEAR"
            vix_color = "#FFD700"
        else:
            vix_status = "🟢 LOW FEAR"
            vix_color = "#00FF7F"
        
        # Create gauge
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=vix_current,
            title={'text': "VIX Level", 'font': {'color': '#667788', 'size': 14, 'family': 'JetBrains Mono'}},
            number={'font': {'color': vix_color, 'size': 56, 'family': 'Bebas Neue'}},
            gauge={
                'axis': {'range': [0, 80], 'tickcolor': '#334455', 'tickwidth': 1},
                'bar': {'color': vix_color, 'thickness': 0.7},
                'bgcolor': 'rgba(0,0,0,0)',
                'bordercolor': 'rgba(0,0,0,0)',
                'steps': [
                    {'range': [0, 20], 'color': 'rgba(0,255,127,0.1)'},
                    {'range': [20, 30], 'color': 'rgba(255,215,0,0.1)'},
                    {'range': [30, 80], 'color': 'rgba(255,49,49,0.1)'}
                ],
                'threshold': {
                    'line': {'color': vix_color, 'width': 3},
                    'thickness': 0.85,
                    'value': vix_current
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=60, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='JetBrains Mono', color='#667788')
        )
        
        _, cc, _ = st.columns([1, 2, 1])
        with cc:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                f'<div style="text-align:center;font-family:var(--f-mono);'
                f'font-size:16px;font-weight:700;color:{vix_color};'
                f'letter-spacing:2px;margin-top:-20px;">{vix_status}</div>',
                unsafe_allow_html=True
            )
    else:
        st.warning("⚠️ Unable to fetch VIX data")
    
    st.markdown('</div>', unsafe_allow_html=True)


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
            st.info("無法計算 87MA 扣抵值預測")

    with tab_a:
        if not adam_df.empty:
            base  = alt.Chart(adam_df).encode(x='Date:T')
            real  = base.mark_line(color='#C0C0C0', strokeWidth=1).encode(y='Price')
            pred  = base.mark_line(color='#FF3131', strokeWidth=2, strokeDash=[5, 5]).encode(y='Adam_Predict')
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.altair_chart(
                (real + pred).interactive()
                .properties(title=alt.TitleParams("亞當理論二次反射", color='#FF3131'))
                .configure_view(strokeOpacity=0, fill='rgba(0,0,0,0)')
                .configure_axis(gridColor='rgba(0,245,255,0.07)', labelColor='#445566', titleColor='#445566'),
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("無法計算亞當理論路徑")

    st.markdown(
        f'<div class="titan-foot">TREND RADAR V300 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


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
    """
    🔓 OPERATION UNCHAIN — V301
    This function NO LONGER requires df to be uploaded.
    It works independently by fetching VIX and Global Market Data.
    """
    _sec_header("🚦", "宏觀風控儀表", "MACRO HUD")
    
    macro, _, _ = _load_engines()
    df = st.session_state.get('df', pd.DataFrame())
    df_hash = f"{len(df)}_{list(df.columns)}" if not df.empty else "empty"

    # ═══════════════════════════════════════════════════════════════════════
    #  🔓 REMOVED GATEKEEPER: The old check "if df.empty: return" is GONE
    #  Now we proceed to render VIX + Global Data regardless of df status
    # ═══════════════════════════════════════════════════════════════════════
    
    # ── IF DATA AVAILABLE: Show full dashboard ────────────────────────────
    if not df.empty:
        md  = _get_macro_data(macro, df_hash)
        sig = md['signal']
        col, rgb = SIGNAL_PALETTE.get(sig, ("#FFD700", "255,215,0"))
        sig_text = SIGNAL_MAP.get(sig, "⚪ UNKNOWN")
        parts    = sig_text.split("：")
        sig_main = parts[0] if parts else sig_text
        sig_desc = parts[1] if len(parts) > 1 else ""

        # ── HERO BILLBOARD ──
        st.markdown(f"""
<div class="hero-container" style="--hero-color:{col};--hero-glow:rgba({rgb},0.10);--hero-rgb:{rgb};">
  <div style="display:inline-flex;align-items:center;margin-bottom:6px;">
    <span class="hero-pulse" style="--hero-color:{col};--hero-rgb:{rgb};"></span>
  </div>
  <div class="hero-title" style="--hero-color:{col};">{sig_main}</div>
  <div class="hero-subtitle">{sig_desc}</div>
  <div class="hero-badge">TITAN SOP V301 &nbsp;·&nbsp; {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</div>""", unsafe_allow_html=True)

        # [UPGRADE #2] Toast for signal
        st.toast(f"{sig_main} — {sig_desc}", icon="🚦")

        # ── 4-KPI ROW ──────────────────────────────────────────────────────
        vix      = md['vix']
        pr90     = md['price_distribution']['pr90']
        ptt      = md['ptt_ratio']
        ptt_txt  = f"{ptt:.1f}%" if ptt != -1.0 else "N/A"
        vix_col  = "#FF3131" if vix > 30 else "#FFD700" if vix > 20 else "#00FF7F"
        pr90_col = "#FF3131" if pr90 > 130 else "#FFD700" if pr90 > 115 else "#00F5FF"
        ptt_col  = "#FF3131" if (ptt != -1.0 and ptt > 50) else "#00FF7F"

        _kpi_row(
            ("SIGNAL",   sig_main,      sig_desc,               col),
            ("VIX",      f"{vix:.2f}",  ">30 DANGER · >20 WARN", vix_col),
            ("PR90",     f"{pr90:.1f}", ">130 OVERHEATED",        pr90_col),
            ("PTT BEAR", ptt_txt,       ">50% RED SIGNAL",        ptt_col),
        )

        # [UPGRADE #3] Typewriter for HUD summary
        hud_summary = (
            f"【戰情總覽】信號燈：{sig_text}。"
            f"VIX 恐慌指數 {vix:.2f}{'⚠️ 警戒' if vix > 20 else ' 正常'}。"
            f"PR90 籌碼壓力 {pr90:.1f}{'🔴 過熱' if pr90 > 130 else ' 正常'}。"
            f"PTT 散戶看空比 {ptt_txt}。"
        )
        if 'hud_streamed' not in st.session_state:
            st.write_stream(_stream_text(hud_summary, speed=0.015))
            st.session_state['hud_streamed'] = True
        else:
            st.caption(hud_summary)

        # ── TSE DEEP-DIVE ──────────────────────────────────────────────────
        tse     = md['tse_analysis']
        deducts = " &nbsp;|&nbsp; ".join(tse.get('deduct_slope', ["計算中…"]))
        st.markdown(f"""
<div style="background:rgba(0,0,0,0.2);border:1px solid rgba(255,255,255,0.052);border-radius:16px;padding:18px 20px 16px;margin-top:4px;">
  <div style="font-family:var(--f-mono);font-size:8px;letter-spacing:3.5px;color:#334455;text-transform:uppercase;margin-bottom:13px;">
    🇹🇼 Taiwan Weighted Index — Deep Analysis
  </div>
  <div class="tse-grid">
    <div class="tse-chip">
      <div class="tsc-lbl">目前點位</div>
      <div class="tsc-val" style="font-family:var(--f-display);font-size:22px;color:#FFF;">
        {tse.get('price', 0):,.0f}
      </div>
    </div>
    <div class="tse-chip">
      <div class="tsc-lbl">動能方向</div>
      <div class="tsc-val">{tse.get('momentum', 'N/A')}</div>
    </div>
    <div class="tse-chip">
      <div class="tsc-lbl">神奇均線</div>
      <div class="tsc-val">{tse.get('magic_ma', 'N/A')}</div>
    </div>
    <div class="tse-chip">
      <div class="tsc-lbl">格蘭碧法則</div>
      <div class="tsc-val">{tse.get('granville', 'N/A')}</div>
    </div>
  </div>
  <div class="tse-deduct">扣抵與斜率 — {deducts}</div>
</div>""", unsafe_allow_html=True)
    
    else:
        # ── NO CB DATA: Show minimal hero + notice ─────────────────────────
        st.markdown("""
<div class="hero-container">
  <div class="hero-title" style="font-size:60px!important;color:#888;">STANDBY MODE</div>
  <div class="hero-subtitle">CB 數據未載入 — 僅顯示全球市場監控</div>
  <div class="hero-badge">TITAN SOP V301 &nbsp;·&nbsp; GLOBAL OVERWATCH ACTIVE</div>
</div>""", unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════════════
    #  ✅ OPERATION OVERWATCH: ALWAYS RENDER (independent of df)
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown('<div style="height:32px"></div>', unsafe_allow_html=True)
    
    # VIX Gauge (Always visible)
    _render_vix_gauge()
    
    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)
    
    # Global Overwatch (Always visible)
    _render_global_overwatch()
    
    st.markdown(
        f'<div class="titan-foot">MACRO HUD V301 — OPERATION UNCHAIN ACTIVE &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────────────────
# The following render functions remain unchanged from original
# ─────────────────────────────────────────────────────────────────────────────

def render_1_2_thermometer():
    _sec_header("🌡️", "高價權值股多空溫度計", "BULL / BEAR THERMO")
    macro, _, _ = _load_engines()

    if 'high_50_sentiment' not in st.session_state:
        st.session_state.high_50_sentiment = None

    st.markdown('<div class="action-wrap">', unsafe_allow_html=True)
    if st.button("🔄  REFRESH MARKET SENTIMENT", key="btn_sentiment"):
        st.toast("🚀 掃描高價權值股多空…", icon="⏳")
        with st.spinner("Analyzing high-price weighted stocks…"):
            st.session_state.high_50_sentiment = macro.analyze_high_50_sentiment()
        st.toast("✅ 多空溫度計更新完成！", icon="🌡️")
    st.markdown('</div>', unsafe_allow_html=True)

    sent = st.session_state.high_50_sentiment
    if not sent:
        st.markdown('<div class="empty-state"><div class="empty-icon">🌡️</div>'
                    '<div class="empty-text">CLICK TO FETCH SENTIMENT</div></div>', unsafe_allow_html=True)
        return
    if "error" in sent:
        st.toast(f"⚠️ {sent['error']}", icon="⚡")
        return

    ratio  = sent['bull_ratio']
    bear_r = sent['bear_ratio']
    total  = sent['total']

    if ratio >= 65:   vd, vc, vr = "🔥 強勢多頭市場 — 全力進攻",  "#FF3131", "255,49,49"
    elif ratio >= 50: vd, vc, vr = "🟢 多方略佔優勢 — 持股向好",  "#00FF7F", "0,255,127"
    elif ratio >= 35: vd, vc, vr = "🟡 多空膠著 — 審慎選股",      "#FFD700", "255,215,0"
    else:             vd, vc, vr = "🔴 空頭市場 — 輕倉防守",      "#26A69A", "38,166,154"

    # ── 64px KPI Cards ──
    _kpi_row(
        ("MARKET MOOD",  sent['sentiment'],   f"Based on {total} stocks", vc),
        ("🐂 BULL RATIO", f"{ratio:.1f}%",    "Above 87MA lifeline",      "#FF3131"),
        ("🐻 BEAR RATIO", f"{bear_r:.1f}%",   "Below 87MA lifeline",      "#26A69A"),
    )

    # ── Plotly Gauge ──
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ratio,
        title={'text': "多頭佔比 (%)", 'font': {'color': '#445566', 'size': 13, 'family': 'JetBrains Mono'}},
        number={'font': {'color': '#FFF', 'size': 64, 'family': 'Bebas Neue'}, 'suffix': '%'},
        gauge={
            'axis':    {'range': [0, 100], 'tickcolor': '#222'},
            'bar':     {'color': "#FF3131"},
            'bgcolor': 'rgba(0,0,0,0)',
            'bordercolor': 'rgba(0,0,0,0)',
            'steps': [
                {'range': [0, 35],  'color': 'rgba(38,166,154,0.15)'},
                {'range': [35, 50], 'color': 'rgba(255,215,0,0.15)'},
                {'range': [50, 65], 'color': 'rgba(0,255,127,0.15)'},
                {'range': [65, 100],'color': 'rgba(255,49,49,0.15)'}
            ],
            'threshold': {'line': {'color': "#FFF", 'width': 4}, 'thickness': 0.75, 'value': ratio}
        }
    ))
    fig.update_layout(
        height=360,
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color='#445566')
    )
    _, cc, _ = st.columns([1, 2, 1])
    with cc:
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center;font-family:var(--f-mono);font-size:16px;'
                    f'font-weight:700;color:{vc};letter-spacing:2px;margin-top:12px;">{vd}</div>',
                    unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">THERMO V300 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


def render_1_3_pr90():
    _sec_header("📊", "籌碼分佈分析 — PR90", "PRICE DISTRIBUTION")
    df = st.session_state.get('df', pd.DataFrame())
    if df.empty:
        st.markdown('<div class="empty-state"><div class="empty-icon">📊</div>'
                    '<div class="empty-text">請上傳 CB 清單</div></div>', unsafe_allow_html=True)
        return

    macro, _, _ = _load_engines()
    df_hash = f"{len(df)}_{list(df.columns)}"
    md = _get_macro_data(macro, df_hash)
    pr_data = md['price_distribution']

    _kpi_row(
        ("PR25", f"{pr_data['pr25']:.1f}", "低價區 (25%)",  "#26A69A"),
        ("PR50", f"{pr_data['pr50']:.1f}", "中價區 (50%)",  "#FFD700"),
        ("PR75", f"{pr_data['pr75']:.1f}", "高價區 (75%)",  "#FFA07A"),
        ("PR90", f"{pr_data['pr90']:.1f}", "極高價 (90%)", "#FF3131"),
    )

    st.markdown(f"""
<div style="font-family:var(--f-mono);font-size:12px;color:#667788;
line-height:1.8;padding:12px 16px;background:rgba(0,0,0,0.15);
border-radius:12px;border:1px solid rgba(255,255,255,0.04);margin:16px 0;">
<strong style="color:#FFD700">【解讀】</strong> PR90 = {pr_data['pr90']:.1f}<br>
{'🔴 籌碼過熱警戒區 (>130)' if pr_data['pr90'] > 130 else '🟡 正常區間 (115~130)' if pr_data['pr90'] > 115 else '🟢 健康區間 (<115)'}
</div>""", unsafe_allow_html=True)

    # Histogram
    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=df['成交價'],
        nbinsx=30,
        marker=dict(
            color=df['成交價'],
            colorscale='RdYlGn_r',
            line=dict(color='rgba(255,255,255,0.1)', width=1)
        ),
        opacity=0.85,
        name='Price Distribution'
    ))
    for pr_val in [pr_data['pr25'], pr_data['pr50'], pr_data['pr75'], pr_data['pr90']]:
        fig.add_vline(x=pr_val, line_dash="dash", line_color="#00F5FF", line_width=2,
                      annotation_text=f"PR{int((pr_data.get(f'pr{int(pr_val)}') or pr_val))}",
                      annotation_position="top")

    fig.update_layout(
        title=dict(text="可轉債價格分佈直方圖", font=dict(color='#FFD700', size=16, family='Rajdhani')),
        xaxis=dict(title="成交價", gridcolor='rgba(255,255,255,0.05)', color='#667788'),
        yaxis=dict(title="Count", gridcolor='rgba(255,255,255,0.05)', color='#667788'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='JetBrains Mono', color='#667788'),
        height=400,
        margin=dict(l=10, r=10, t=60, b=10)
    )
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">PR90 DISTRIBUTION V300 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


def render_1_4_heatmap():
    _sec_header("🗺️", "族群熱度地圖", "SECTOR HEATMAP")
    df = st.session_state.get('df', pd.DataFrame())
    if df.empty or '產業類別' not in df.columns:
        st.markdown('<div class="empty-state"><div class="empty-icon">🗺️</div>'
                    '<div class="empty-text">請上傳包含產業類別的 CB 清單</div></div>', unsafe_allow_html=True)
        return

    grp = df.groupby('產業類別').agg({'成交價': 'mean', '成交金額': 'sum'}).reset_index()
    grp.columns = ['Industry', 'Avg_Price', 'Total_Volume']
    grp['Avg_Price'] = grp['Avg_Price'].round(2)
    grp['Total_Volume'] = (grp['Total_Volume'] / 1_000_000).round(2)
    grp = grp.sort_values('Total_Volume', ascending=False).head(12)

    cols = st.columns(3)
    for i, row in grp.iterrows():
        col_idx = i % 3
        with cols[col_idx]:
            intensity = min(row['Total_Volume'] / grp['Total_Volume'].max(), 1.0)
            bg_c = f"rgba(255, 215, 0, {intensity * 0.15})"
            bd_c = f"rgba(255, 215, 0, {intensity * 0.4})"
            shadow = f"rgba(255, 215, 0, {intensity * 0.3})"
            st.markdown(f"""
<div class="heatmap-cell" style="--cell-bg:{bg_c};--cell-bd:{bd_c};--cell-shadow:{shadow};--cell-color:#FFD700;">
  <div class="hm-name">{row['Industry']}</div>
  <div class="hm-val">{row['Total_Volume']:.1f}M</div>
  <div class="hm-sub">平均價 {row['Avg_Price']:.2f}</div>
</div>""", unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">SECTOR HEATMAP V300 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


def render_1_5_turnover():
    _sec_header("💹", "全市場成交重心 TOP 100", "TURNOVER LEADERS")
    macro, _, _ = _load_engines()
    _render_leader_dashboard(
        session_state_key='turnover_leaders',
        fetch_function=macro.get_top_n_turnover_leaders,
        top_n=100,
        sort_key_name='Turnover'
    )


def render_1_6_trend_radar():
    _sec_header("👑", "高價權值股趨勢雷達", "TREND RADAR — HIGH-CAP")
    macro, _, _ = _load_engines()
    _render_leader_dashboard(
        session_state_key='trend_leaders',
        fetch_function=macro.get_top_n_high_price_leaders,
        top_n=100,
        sort_key_name='Trend Days'
    )


def render_1_7_predator():
    _sec_header("🎯", "台指獵殺 — WTX Predator", "FUTURES SETTLEMENT HUNTER")
    res = _calculate_futures_targets()
    if "error" in res:
        st.toast(f"⚠️ {res['error']}", icon="❌")
        st.markdown('<div class="empty-state"><div class="empty-icon">🎯</div>'
                    '<div class="empty-text">資料不足或尚未開始</div></div>', unsafe_allow_html=True)
        return

    is_red   = res['is_red']
    bar_color = "#FF6B6B" if is_red else "#26A69A"
    cf_rgb    = "255,107,107" if is_red else "38,166,154"
    bias      = res['price'] - res['anc']

    _kpi_row(
        ("合約名稱",  res['name'],         f"台指期近月 / ^TWII",       "#FFD700"),
        ("開盤錨點",  f"{res['anc']:,.0f}", f"本月結算基準",            "#00F5FF"),
        ("現價",      f"{res['price']:,.0f}", f"乖離 {bias:+.0f} pts", "#FFF"),
    )

    ctrl = "🔴 多方控盤 — 慣性收長紅" if is_red else "🟢 空方控盤 — 慣性收長黑"
    st.markdown(f'<div class="ctrl-flag" style="--cf-rgb:{cf_rgb};">{ctrl}</div>',
                unsafe_allow_html=True)

    # [UPGRADE #3] Typewriter for predator verdict
    pred_text = (
        f"【台指期獵殺判讀】{res['name']} 本月開盤錨定 {res['anc']:,.0f}，"
        f"現價 {res['price']:,.0f} ({bias:+.0f} pts)。"
        f"{'多方控盤，慣性收紅K' if is_red else '空方控盤，慣性收黑K'}。"
        f"目標推導：1B={res['t']['1B']:,.0f} / 2B={res['t']['2B']:,.0f} / "
        f"3B={res['t']['3B']:,.0f} / HR={res['t']['HR']:,.0f}。"
    )
    if 'pred_streamed' not in st.session_state:
        st.write_stream(_stream_text(pred_text, speed=0.012))
        st.session_state['pred_streamed'] = True
    else:
        st.caption(pred_text)

    # ── Baseball Target Cards ─────────────────────────────────────────────────
    def hit_cls(tg):
        return "hit" if (is_red and res['price'] >= tg) or (not is_red and res['price'] <= tg) else "miss"
    def hit_lbl(tg): return "✅ 達標" if "hit" == hit_cls(tg) else "⏳ 未達"

    st.markdown(f"""
<div class="bases-grid">
  <div class="base-card {hit_cls(res['t']['1B'])}">
    <div class="base-name">1 壘</div>
    <div class="base-price">{res['t']['1B']:,.0f}</div>
    <div class="base-status">{hit_lbl(res['t']['1B'])}</div>
  </div>
  <div class="base-card {hit_cls(res['t']['2B'])}">
    <div class="base-name">2 壘</div>
    <div class="base-price">{res['t']['2B']:,.0f}</div>
    <div class="base-status">{hit_lbl(res['t']['2B'])}</div>
  </div>
  <div class="base-card {hit_cls(res['t']['3B'])}">
    <div class="base-name">3 壘</div>
    <div class="base-price">{res['t']['3B']:,.0f}</div>
    <div class="base-status">{hit_lbl(res['t']['3B'])}</div>
  </div>
  <div class="base-card hr {hit_cls(res['t']['HR'])}">
    <div class="base-name" style="color:#FF6B6B">🏠 全壘打</div>
    <div class="base-price" style="color:#FF8888">{res['t']['HR']:,.0f}</div>
    <div class="base-status">{hit_lbl(res['t']['HR'])}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── ALTAIR BASEBALL K-BAR CHART — EXACT LOGIC PRESERVED ──────────────────
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
                             fontSize=14, fontWeight='bold',
                             font='JetBrains Mono')
            .encode(y=f'Target_{k}', text=alt.value(f"{k}  {res['t'][k]:,.0f}"))
        )
    chart += (
        base.mark_tick(color='#FF3131', thickness=4, size=100)
        .encode(y='Target_HR')
        + base.mark_text(dx=56, align='left', color='#FF3131',
                         fontSize=15, fontWeight='bold',
                         font='JetBrains Mono')
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
        f'<div class="titan-foot">WTX PREDATOR V300 &nbsp;·&nbsp; '
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
    "1.4": "#00FF7F",
    "1.5": "#FFA07A",
    "1.6": "#9370DB",
    "1.7": "#FF3131",
}


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY — Netflix Poster Rail + Cinematic Content Frame
#  [UPGRADE #1] Tactical Guide Dialog on first visit
#  [NEW V301] Manual Trigger System for Macro HUD
# ══════════════════════════════════════════════════════════════════════════════
def render():
    """Tab 1 — Cinematic Trading Experience (Director's Cut V301 — Operation Unchain)"""
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
      TITAN OS V301
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
            # Invisible button on top of the poster (no visible button chrome)
            if st.button(f"{emoji} {label_zh}", key=f"nav_{code}",
                         use_container_width=True):
                st.session_state.tab1_active = code
                st.rerun()

            # Poster card HTML drawn below (the button is transparent; poster is display)
            st.markdown(f"""
<div class="poster-card {act_cls}" style="--poster-accent:{accent};margin-top:-54px;
     pointer-events:none;z-index:0;position:relative;">
  <div class="poster-icon">{emoji}</div>
  <div class="poster-code">{code}</div>
  <div class="poster-text">{label_zh}</div>
  <div class="poster-tag">{label_en}</div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # nav-deck-frame

    # ═══════════════════════════════════════════════════════════════════════
    #  🚀 MANUAL TRIGGER SYSTEM (NEW V301)
    #  Only applies to module 1.1 (MACRO HUD)
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown('<div class="content-frame">', unsafe_allow_html=True)
    
    if active == "1.1":
        # Check if macro has been initialized
        if not st.session_state.get('macro_initialized', False):
            # State 1: Idle — Show trigger button
            st.markdown('<div style="height:60px"></div>', unsafe_allow_html=True)
            st.markdown("""
<div class="hero-container">
  <div class="hero-title" style="font-size:64px!important;color:#00F5FF;">GLOBAL SCAN</div>
  <div class="hero-subtitle">INITIALIZE MACRO OVERWATCH SYSTEM</div>
  <div class="hero-badge">CLICK BELOW TO ACTIVATE</div>
</div>""", unsafe_allow_html=True)
            
            st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "🚀 啟動全域戰情掃描 (Initialize Global Scan)",
                    use_container_width=True,
                    key="init_macro",
                    type="primary"
                ):
                    st.session_state.macro_initialized = True
                    st.rerun()
        else:
            # State 2: Active — Render the dashboard
            with st.spinner("🌐 正在建立全球連線 / Establishing Global Uplink..."):
                render_1_1_hud()
    else:
        # All other modules render normally
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
