# ui_desktop/tab1_macro.py
# Titan SOP V300 — 宏觀風控指揮中心 (Macro Risk Command Center)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  "DIRECTOR'S CUT V300" + GLOBAL OVERWATCH UPGRADE                ║
# ║  5 MANDATORY UPGRADES:                                            ║
# ║    ✅ #1  Tactical Guide Dialog (Onboarding Modal)                ║
# ║    ✅ #2  Toast Notifications (replace st.success/info/warning)   ║
# ║    ✅ #3  Valkyrie AI Typewriter (_stream_text)                   ║
# ║    ✅ #4  Director's Cut Visuals (Hero/Poster/Glass — preserved)  ║
# ║    🆕 #5  Manual Trigger + Global Market Monitoring               ║
# ║         → S&P 500, USD/TWD, DXY, TWII correlation                 ║
# ║  Logic: V82.0 fully preserved (MacroRiskEngine/Altair/Plotly)     ║
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
#  [UPGRADE #5] GLOBAL MARKET DATA FETCHER
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def fetch_global_data():
    """Fetch SPX, USD/TWD, DXY, and TWII for comparison"""
    tickers = {
        "S&P 500": "^GSPC",
        "USD/TWD": "TWD=X",
        "DXY (美元指數)": "^DXY",  # Primary DXY ticker
        "TWII (加權)": "^TWII"
    }
    
    try:
        # Fetch last 3 months for trend analysis
        ticker_list = list(tickers.values())
        df = yf.download(ticker_list, period="3mo", progress=False)['Close']
        
        # Handle single vs multiple ticker response structure
        if isinstance(df, pd.Series):
            # Single ticker case
            df = pd.DataFrame({ticker_list[0]: df})
        
        # Try to download DX-Y.NYB as fallback for DXY
        if "^DXY" in ticker_list and "^DXY" not in df.columns:
            try:
                dxy_alt = yf.download("DX-Y.NYB", period="3mo", progress=False)['Close']
                if not dxy_alt.empty:
                    df["^DXY"] = dxy_alt
            except:
                pass
        
        # Rename columns to friendly names
        df_renamed = pd.DataFrame()
        for friendly, ticker in tickers.items():
            if ticker in df.columns:
                df_renamed[friendly] = df[ticker]
        
        # If we still don't have DXY data, mark it as unavailable
        if "DXY (美元指數)" not in df_renamed.columns:
            st.toast("⚠️ DXY 數據暫時無法取得", icon="📊")
        
        return df_renamed if not df_renamed.empty else pd.DataFrame()
        
    except Exception as e:
        st.error(f"全球市場數據獲取失敗: {e}")
        return pd.DataFrame()


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
🆕 **全球戰情監控** — 整合 S&P 500、美元指數、台幣匯率即時連動分析。

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

/* 🆕 HERO LAUNCH BUTTON */
.hero-launch-btn div.stButton > button {
    background: linear-gradient(135deg, rgba(0,245,255,0.1) 0%, rgba(255,215,0,0.1) 100%) !important;
    border: 2px solid rgba(0,245,255,0.4) !important;
    color: #00F5FF !important;
    font-family: var(--f-o) !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    letter-spacing: 4px !important;
    min-height: 68px !important;
    border-radius: 16px !important;
    text-transform: uppercase !important;
    box-shadow: 0 0 30px rgba(0,245,255,0.2) !important;
    transition: all 0.3s ease !important;
}
.hero-launch-btn div.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,245,255,0.2) 0%, rgba(255,215,0,0.2) 100%) !important;
    border-color: rgba(255,215,0,0.6) !important;
    color: #FFD700 !important;
    box-shadow: 0 0 50px rgba(255,215,0,0.4), 0 0 80px rgba(0,245,255,0.2) !important;
    transform: translateY(-2px) !important;
}

/* 🆕 GLOBAL MARKET CARDS */
.global-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin: 20px 0;
}
.global-card {
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.06);
    border-top: 2px solid var(--gcard-accent, #00F5FF);
    border-radius: 14px;
    padding: 16px 18px;
    position: relative;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.global-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4), 0 0 20px rgba(var(--gcard-rgb, 0,245,255),0.15);
}
.global-card::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 80px;
    height: 80px;
    background: radial-gradient(circle at top right, var(--gcard-accent, #00F5FF), transparent 65%);
    opacity: 0.06;
    pointer-events: none;
}
.gcard-label {
    font-family: var(--f-mono);
    font-size: 9px;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 10px;
}
.gcard-value {
    font-family: var(--f-display);
    font-size: 38px;
    color: #FFF;
    line-height: 1;
    margin-bottom: 6px;
    letter-spacing: 1px;
}
.gcard-change {
    font-family: var(--f-body);
    font-size: 14px;
    font-weight: 700;
    color: var(--gcard-accent, #00F5FF);
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
    position: relative; overflow: hidden;
}
.poster-card::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(circle at 50% 0%,
        var(--poster-accent, #FFD700), transparent 70%);
    opacity: 0; transition: opacity 0.3s;
}
.poster-card.active::before { opacity: 0.08; }
.poster-card:hover::before  { opacity: 0.12; }
.poster-card.active {
    border-color: var(--poster-accent, #FFD700);
    background: rgba(0,0,0,0.72);
    transform: scale(1.04);
    box-shadow: 0 8px 28px rgba(0,0,0,0.4),
                0 0 20px rgba(var(--poster-accent-rgb, 255,215,0), 0.2);
}
.poster-icon {
    font-size: 36px;
    line-height: 1;
    filter: grayscale(60%);
    transition: filter 0.3s;
}
.poster-card:hover .poster-icon,
.poster-card.active .poster-icon { filter: grayscale(0%); }
.poster-code {
    font-family: var(--f-mono);
    font-size: 10px; letter-spacing: 2px;
    color: #334455;
    font-weight: 700;
    margin-top: 6px;
}
.poster-text {
    font-family: var(--f-body);
    font-size: 15px; font-weight: 700;
    color: #99AABB;
    transition: color 0.3s;
}
.poster-card:hover .poster-text { color: #CDD; }
.poster-card.active .poster-text {
    color: var(--poster-accent, #FFD700);
    text-shadow: 0 0 14px rgba(var(--poster-accent-rgb, 255,215,0), 0.4);
}
.poster-tag {
    font-family: var(--f-mono);
    font-size: 7.5px; letter-spacing: 2px;
    color: #223344;
    text-transform: uppercase;
}

/* ══════════════════════════════════════════════════════
   3. SECTION HEADER
══════════════════════════════════════════════════════ */
.sec-header {
    display: flex; align-items: center; gap: 12px;
    padding-bottom: 14px; border-bottom: 1px solid rgba(255,255,255,0.052);
    margin-bottom: 20px;
}
.sec-icon {
    font-size: 28px;
    filter: drop-shadow(0 0 12px rgba(0,245,255,0.4));
}
.sec-title {
    font-family: var(--f-display); font-size: 24px;
    color: #00F5FF; letter-spacing: 3px;
    text-shadow: 0 0 18px rgba(0,245,255,0.3);
}
.sec-pill {
    font-family: var(--f-mono); font-size: 9px;
    color: rgba(0,245,255,0.4); letter-spacing: 2px;
    border: 1px solid rgba(0,245,255,0.15);
    border-radius: 20px; padding: 3px 12px;
    text-transform: uppercase;
    margin-left: 8px;
    background: rgba(0,245,255,0.02);
}

/* ══════════════════════════════════════════════════════
   4. KPI CARD GRID — 4 metric cards
══════════════════════════════════════════════════════ */
.kpi-grid { display: grid; gap: 11px; margin-bottom: 20px; }
.kpi-g2 { grid-template-columns: repeat(2, 1fr); }
.kpi-g3 { grid-template-columns: repeat(3, 1fr); }
.kpi-g4 { grid-template-columns: repeat(4, 1fr); }

.kpi-card {
    background: rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.05);
    border-top: 2px solid var(--kc, #FFD700);
    border-radius: 14px;
    padding: 16px 18px;
    position: relative; overflow: hidden;
    transition: transform 0.2s ease;
}
.kpi-card:hover { transform: translateY(-3px); }
.kpi-card::after {
    content: '';
    position: absolute; top: 0; right: 0;
    width: 90px; height: 90px;
    background: radial-gradient(circle at top right,
        var(--kc, #FFD700), transparent 65%);
    opacity: 0.04;
    pointer-events: none;
}
.kpi-label {
    font-family: var(--f-mono);
    font-size: 9px;
    color: rgba(255,255,255,0.35);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 10px;
}
.kpi-value {
    font-family: var(--f-display);
    font-size: 42px;
    color: #FFF;
    line-height: 1;
    margin-bottom: 6px;
    letter-spacing: 1px;
}
.kpi-sub {
    font-family: var(--f-body);
    font-size: 12px;
    color: var(--kc, #FFD700);
    font-weight: 600;
    opacity: 0.85;
}

/* ══════════════════════════════════════════════════════
   5. RANK CARD — Top 3 leaders
══════════════════════════════════════════════════════ */
.rank-card {
    display: flex; align-items: center; gap: 18px;
    background: rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.05);
    border-left: 3px solid var(--rc-accent, #FFD700);
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: all 0.22s ease;
}
.rank-card:hover {
    transform: translateX(6px);
    background: rgba(0,0,0,0.35);
    box-shadow: 0 0 18px rgba(var(--rc-accent-rgb, 255,215,0), 0.12);
}
.rank-num {
    font-family: var(--f-display); font-size: 56px;
    color: var(--rc-accent, #FFD700);
    line-height: 1; opacity: 0.12;
}
.rank-info { flex: 1; }
.rank-name {
    font-family: var(--f-body); font-size: 17px; font-weight: 700;
    color: #DDD; margin-bottom: 4px;
}
.rank-meta {
    font-family: var(--f-mono); font-size: 10px;
    color: #445566; letter-spacing: 1px;
}
.rank-value {
    font-family: var(--f-display); font-size: 32px;
    color: var(--rc-accent, #FFD700);
    text-align: right; line-height: 1;
}
.rank-trend {
    font-family: var(--f-body); font-size: 12px; font-weight: 600;
    text-align: right; margin-top: 4px;
}

/* ══════════════════════════════════════════════════════
   6. TSE DEEP ANALYSIS — TWII chips
══════════════════════════════════════════════════════ */
.tse-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-bottom: 12px;
}
.tse-chip {
    background: rgba(0,0,0,0.22);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 11px 13px;
    text-align: center;
}
.tsc-lbl {
    font-family: var(--f-mono);
    font-size: 8px;
    color: rgba(0,245,255,0.35);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 7px;
}
.tsc-val {
    font-family: var(--f-body);
    font-size: 16px;
    font-weight: 700;
    color: #FFF;
}
.tse-deduct {
    font-family: var(--f-mono);
    font-size: 11px;
    color: rgba(0,245,255,0.5);
    background: rgba(0,0,0,0.25);
    border-radius: 9px;
    padding: 8px 14px;
    border-left: 2px solid rgba(0,245,255,0.2);
    letter-spacing: 0.4px;
}

/* ══════════════════════════════════════════════════════
   7. CHART WRAP — Glass frame
══════════════════════════════════════════════════════ */
.chart-wrap {
    background: rgba(0,0,0,0.32);
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 16px;
    padding: 14px 8px 5px;
    margin: 14px 0;
    overflow: hidden;
}

/* ══════════════════════════════════════════════════════
   8. THERMOMETER VERDICT
══════════════════════════════════════════════════════ */
.thermo-verdict {
    font-family: var(--f-body);
    font-size: 17px;
    font-weight: 700;
    text-align: center;
    padding: 16px 24px;
    border-radius: 14px;
    margin-top: 14px;
    border: 1px solid rgba(var(--vr),0.3);
    background: rgba(var(--vr),0.055);
    color: rgb(var(--vr));
    letter-spacing: 0.5px;
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
.ldr-tbl { width: 100%; border-collapse: collapse; font-family: var(--f-body); }
.ldr-tbl th {
    font-family: var(--f-mono);
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(0,245,255,0.65);
    background: rgba(0,245,255,0.04);
    padding: 10px 13px;
    border-bottom: 1px solid rgba(0,245,255,0.10);
}
.ldr-tbl td {
    padding: 9px 13px;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    color: rgba(210,220,235,0.82);
    font-size: 14px;
}
.ldr-tbl tr:hover td { background: rgba(0,245,255,0.025); }

/* ══════════════════════════════════════════════════════
   11. BASEBALL TARGETS (1.7)
══════════════════════════════════════════════════════ */
.bases-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 11px;
    margin: 16px 0;
}
.base-card {
    border-radius: 16px;
    padding: 18px 10px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.068);
    background: rgba(255,255,255,0.022);
    transition: transform 0.18s ease;
}
.base-card:hover { transform: translateY(-2px); }
.base-card.hit {
    border-color: rgba(0,255,127,0.35);
    background: rgba(0,255,127,0.04);
}
.base-card.hr {
    border-color: rgba(255,49,49,0.38);
    background: rgba(255,49,49,0.04);
}
.base-card.hr.hit {
    border-color: rgba(255,49,49,0.6);
    box-shadow: 0 0 20px rgba(255,49,49,0.14);
}
.base-name {
    font-family: var(--f-mono);
    font-size: 10px;
    color: #445566;
    letter-spacing: 2px;
    margin-bottom: 9px;
    text-transform: uppercase;
}
.base-price {
    font-family: var(--f-display);
    font-size: 36px;
    color: #FFF;
    margin-bottom: 8px;
    letter-spacing: 1px;
}
.base-status {
    font-family: var(--f-body);
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
}
.hit .base-status {
    background: rgba(0,255,127,0.14);
    color: #00FF7F;
}
.miss .base-status {
    background: rgba(255,255,255,0.05);
    color: #445566;
}
.hr .base-status {
    background: rgba(255,49,49,0.12);
    color: #FF6B6B;
}

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
    content: '';
    position: absolute;
    bottom: 0;
    left: 8%;
    right: 8%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,245,255,0.12) 50%, transparent);
}

/* ══════════════════════════════════════════════════════
   13. EMPTY STATE
══════════════════════════════════════════════════════ */
.empty-state {
    border: 1px dashed rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 60px 30px;
    text-align: center;
}
.empty-icon {
    font-size: 44px;
    opacity: 0.25;
    margin-bottom: 14px;
}
.empty-text {
    font-family: var(--f-mono);
    font-size: 13px;
    color: #334455;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ══════════════════════════════════════════════════════
   14. CTRL BANNER (1.7 direction flag)
══════════════════════════════════════════════════════ */
.ctrl-flag {
    border-radius: 14px;
    padding: 16px 22px;
    text-align: center;
    font-family: var(--f-body);
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.5px;
    margin: 14px 0 18px;
    border: 1px solid rgba(var(--cf-rgb),0.25);
    background: rgba(var(--cf-rgb),0.06);
    color: rgb(var(--cf-rgb));
}

/* ══════════════════════════════════════════════════════
   15. TIMESTAMP FOOTER
══════════════════════════════════════════════════════ */
.titan-foot {
    font-family: var(--f-mono);
    font-size: 9px;
    color: rgba(100,120,140,0.3);
    letter-spacing: 2px;
    text-align: right;
    margin-top: 18px;
    text-transform: uppercase;
}

/* ══════════════════════════════════════════════════════
   16. NAV DECK FRAME
══════════════════════════════════════════════════════ */
.nav-deck-frame {
    background: linear-gradient(165deg, #07080f 0%, #0a0b14 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 18px 14px 14px;
    margin-bottom: 18px;
    position: relative;
    overflow: hidden;
}
.nav-deck-frame::after {
    content: '';
    position: absolute;
    top: 0;
    left: 10%;
    right: 10%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,215,0,0.4) 50%, transparent);
}
.nav-deck-label {
    font-family: var(--f-mono);
    font-size: 8px;
    letter-spacing: 4px;
    color: rgba(255,215,0,0.2);
    text-transform: uppercase;
    margin-bottom: 14px;
    padding-left: 2px;
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
#  [UPGRADE #5] SECTION 1.1 — HUD WITH MANUAL TRIGGER + GLOBAL OVERWATCH
# ══════════════════════════════════════════════════════════════════════════════
def render_1_1_hud():
    """
    🆕 MANUAL TRIGGER FLOW:
    1. Check if macro_initialized = False → Show hero + launch button
    2. When clicked → Set macro_initialized = True, fetch global data
    3. Display full dashboard with VIX + Global Market Monitoring
    """
    _sec_header("🚦", "宏觀風控儀表", "MACRO HUD + GLOBAL OVERWATCH")
    
    # ─── 1. CHECK INITIALIZATION STATE ────────────────────────────────────────
    if not st.session_state.get('macro_initialized', False):
        # ─── HERO SECTION: NOT INITIALIZED ───
        st.markdown("""
<div class="hero-container" style="--hero-color:#00F5FF;--hero-glow:rgba(0,245,255,0.08);--hero-rgb:0,245,255;">
  <div style="display:inline-flex;align-items:center;margin-bottom:6px;">
    <span class="hero-pulse" style="--hero-color:#00F5FF;--hero-rgb:0,245,255;"></span>
  </div>
  <div class="hero-title" style="--hero-color:#00F5FF;">🌐 GLOBAL MISSION CONTROL</div>
  <div class="hero-subtitle">全球市場即時連動監控系統</div>
  <div class="hero-badge">TITAN OS V300 GLOBAL OVERWATCH &nbsp;·&nbsp; STANDBY MODE</div>
</div>""", unsafe_allow_html=True)
        
        st.markdown("""
<div style="text-align:center; padding:40px 20px; 
            background:rgba(0,0,0,0.2); border:1px dashed rgba(0,245,255,0.15); 
            border-radius:16px; margin:20px 0;">
  <div style="font-family:var(--f-body); font-size:18px; color:rgba(200,220,240,0.7); 
              line-height:1.8; max-width:700px; margin:0 auto 30px;">
    準備啟動全域戰情掃描，整合以下市場數據：
    <br><br>
    <span style="color:#00F5FF">🇺🇸 S&P 500 指數</span> &nbsp;·&nbsp; 
    <span style="color:#FFD700">💵 美元指數 (DXY)</span> &nbsp;·&nbsp; 
    <span style="color:#00FF7F">💱 台幣匯率 (USD/TWD)</span> &nbsp;·&nbsp; 
    <span style="color:#FF6B6B">🇹🇼 加權指數 (TWII)</span>
    <br><br>
    <span style="font-size:14px; color:#445566;">系統將分析全球市場連動關係與風險態勢</span>
  </div>
</div>""", unsafe_allow_html=True)
        
        # ─── LAUNCH BUTTON ───
        st.markdown('<div class="hero-launch-btn" style="margin:0 auto;max-width:500px;">', unsafe_allow_html=True)
        if st.button("🚀 啟動全域戰情掃描 (INITIALIZE GLOBAL SCAN)", key="init_macro", use_container_width=True):
            st.session_state['macro_initialized'] = True
            st.toast("🚀 正在建立全球市場連線...", icon="🌐")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        return  # Exit here if not initialized
    
    # ─── 2. INITIALIZED: FULL DASHBOARD ──────────────────────────────────────
    with st.spinner("🌐 正在建立全球連線... (Establishing Global Connections)"):
        time.sleep(0.8)  # Dramatic pause
    
    macro, _, _ = _load_engines()
    df      = st.session_state.get('df', pd.DataFrame())
    df_hash = f"{len(df)}_{list(df.columns)}" if not df.empty else "empty"

    # ─── 2.1 FETCH GLOBAL DATA (NEW) ──────────────────────────────────────────
    global_df = fetch_global_data()
    
    # ─── 2.2 DISPLAY GLOBAL MARKET CARDS (NEW) ────────────────────────────────
    if not global_df.empty:
        st.markdown("""
<div style="font-family:var(--f-display); font-size:20px; color:#FFD700; 
            letter-spacing:3px; margin:18px 0 14px; text-align:center;
            text-shadow:0 0 20px rgba(255,215,0,0.3);">
  🌍 GLOBAL MARKET SNAPSHOT
</div>""", unsafe_allow_html=True)
        
        # Calculate current values and daily changes
        metric_data = []
        colors = {
            "S&P 500": ("#00F5FF", "0,245,255"),
            "USD/TWD": ("#00FF7F", "0,255,127"),
            "DXY (美元指數)": ("#FFD700", "255,215,0")
        }
        
        for col in global_df.columns:
            if col == "TWII (加權)":  # Skip TWII for metrics (show in chart only)
                continue
            if col in global_df.columns and not global_df[col].isna().all():
                current = global_df[col].iloc[-1]
                prev = global_df[col].iloc[-2] if len(global_df) > 1 else current
                change_pct = ((current - prev) / prev * 100) if prev != 0 else 0
                change_sign = "+" if change_pct >= 0 else ""
                color, rgb = colors.get(col, ("#00F5FF", "0,245,255"))
                
                metric_data.append({
                    'label': col,
                    'value': f"{current:,.2f}",
                    'change': f"{change_sign}{change_pct:.2f}%",
                    'color': color,
                    'rgb': rgb
                })
        
        # Display 3 metric cards
        if len(metric_data) >= 3:
            cards_html = '<div class="global-grid">'
            for m in metric_data:
                cards_html += f"""
<div class="global-card" style="--gcard-accent:{m['color']};--gcard-rgb:{m['rgb']};">
  <div class="gcard-label">{m['label']}</div>
  <div class="gcard-value">{m['value']}</div>
  <div class="gcard-change">{m['change']}</div>
</div>"""
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)
        
        # ─── 2.3 NORMALIZED TREND CHART (NEW) ─────────────────────────────────
        st.markdown("""
<div style="font-family:var(--f-mono); font-size:10px; color:#445566; 
            letter-spacing:2px; text-transform:uppercase; margin:24px 0 12px;">
  📈 COMPARATIVE TREND ANALYSIS (3-MONTH NORMALIZED RETURN %)
</div>""", unsafe_allow_html=True)
        
        # Normalize all series to % return from start
        normalized_df = pd.DataFrame()
        for col in global_df.columns:
            if not global_df[col].isna().all():
                start_val = global_df[col].dropna().iloc[0]
                if start_val != 0:
                    normalized_df[col] = (global_df[col] / start_val - 1) * 100
        
        if not normalized_df.empty:
            # Use Plotly for better interactivity
            fig = px.line(
                normalized_df.reset_index(),
                x='Date',
                y=normalized_df.columns.tolist(),
                title="全球市場連動趨勢 — 標準化漲跌幅 (%)",
                labels={'value': 'Return (%)', 'variable': 'Market'}
            )
            
            # Color mapping
            color_map = {
                "S&P 500": "#00F5FF",
                "USD/TWD": "#00FF7F",
                "DXY (美元指數)": "#FFD700",
                "TWII (加權)": "#FF6B6B"
            }
            
            fig.update_traces(
                line=dict(width=2.5),
                hovertemplate='%{y:.2f}%<br>%{x}<extra></extra>'
            )
            
            # Update each trace color
            for i, col in enumerate(normalized_df.columns):
                if col in color_map:
                    fig.data[i].line.color = color_map[col]
            
            fig.update_layout(
                template="plotly_dark",
                height=400,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Rajdhani, sans-serif", color="#C8D8E8"),
                xaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.05)",
                    title="Date"
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.05)",
                    zeroline=True,
                    zerolinecolor="rgba(0,245,255,0.3)",
                    zerolinewidth=2,
                    title="Return (%)"
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor="rgba(0,0,0,0.5)",
                    font=dict(size=11)
                ),
                margin=dict(t=60, b=40, l=50, r=40)
            )
            
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # ─── CORRELATION INSIGHT ───
            if len(normalized_df.columns) >= 2:
                # Calculate correlation between TWII and other markets
                twii_col = "TWII (加權)"
                if twii_col in normalized_df.columns:
                    correlations = []
                    for col in normalized_df.columns:
                        if col != twii_col and not normalized_df[col].isna().all():
                            corr = normalized_df[twii_col].corr(normalized_df[col])
                            if not pd.isna(corr):
                                correlations.append((col, corr))
                    
                    if correlations:
                        corr_text = " · ".join([f"{name}: {corr:.2f}" for name, corr in correlations])
                        st.markdown(f"""
<div style="background:rgba(0,0,0,0.3); border:1px solid rgba(0,245,255,0.1); 
            border-radius:10px; padding:12px 18px; margin-top:10px;">
  <span style="font-family:var(--f-mono); font-size:9px; color:#445566; 
                letter-spacing:2px; text-transform:uppercase;">
    相關係數分析 (CORRELATION) —
  </span>
  <span style="font-family:var(--f-body); font-size:13px; color:#00F5FF; 
                margin-left:10px;">
    {corr_text}
  </span>
</div>""", unsafe_allow_html=True)

    st.divider()
    
    # ─── 2.4 ORIGINAL VIX + MACRO DASHBOARD (PRESERVED) ──────────────────────
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
  <div class="hero-badge">TITAN SOP V300 &nbsp;·&nbsp; {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
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
        st.markdown("""
<div class="hero-container">
  <div class="hero-title" style="font-size:60px!important;color:#222;">AWAITING DATA</div>
  <div class="hero-subtitle">請上傳 CB 清單以啟動戰情室</div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  REMAINING SECTIONS (1.2 - 1.7) — PRESERVED EXACTLY AS ORIGINAL
#  (truncated for brevity — insert full original code here)
# ══════════════════════════════════════════════════════════════════════════════
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
    # ─── 1.1 HERO BILLBOARD ──────────────────────────────────────────────────
    _sec_header("🚦", "宏觀風控儀表", "MACRO HUD")
    macro, _, _ = _load_engines()
    df      = st.session_state.get('df', pd.DataFrame())
    df_hash = f"{len(df)}_{list(df.columns)}" if not df.empty else "empty"

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
  <div class="hero-badge">TITAN SOP V300 &nbsp;·&nbsp; {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
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
        st.markdown("""
<div class="hero-container">
  <div class="hero-title" style="font-size:60px!important;color:#222;">AWAITING DATA</div>
  <div class="hero-subtitle">請上傳 CB 清單以啟動戰情室</div>
</div>""", unsafe_allow_html=True)


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
                {'range': [0,   35], 'color': '#060e14'},
                {'range': [35,  65], 'color': '#090f0a'},
                {'range': [65, 100], 'color': '#13060a'},
            ],
            'threshold': {
                'line': {'color': "#FFD700", 'width': 4},
                'thickness': 0.78, 'value': 50
            }
        }
    ))
    fig.update_layout(
        height=300, template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=18, b=4, l=18, r=18),
        font=dict(family='JetBrains Mono')
    )
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="thermo-verdict" style="--vr:{vr};">{vd}</div>',
                unsafe_allow_html=True)

    # [UPGRADE #3] Typewriter verdict
    thermo_text = (
        f"【多空溫度計判讀】市場情緒: {sent['sentiment']}。"
        f"多頭佔比 {ratio:.1f}% / 空頭佔比 {bear_r:.1f}% (共 {total} 檔高價股)。"
        f"結論: {vd.split('—')[1].strip() if '—' in vd else vd}。"
    )
    if 'thermo_streamed' not in st.session_state:
        st.write_stream(_stream_text(thermo_text, speed=0.015))
        st.session_state['thermo_streamed'] = True
    else:
        st.caption(thermo_text)


# ─────────────────────────────────────────────────────────────────────────────

def render_1_3_pr90():
    _sec_header("📊", "PR90 籌碼分佈圖", "CHIP DISTRIBUTION")
    macro, _, _ = _load_engines()
    df      = st.session_state.get('df', pd.DataFrame())
    df_hash = f"{len(df)}_{list(df.columns)}" if not df.empty else "empty"

    if not df.empty:
        md    = _get_macro_data(macro, df_hash)
        pd_   = md.get('price_distribution', {})
        cdata = pd_.get('chart_data')

        if cdata is not None and not cdata.empty:
            pr90 = pd_.get('pr90', 0);  pr75 = pd_.get('pr75', 0);  avg = pd_.get('avg', 0)
            pr90c = "#FF3131" if pr90 > 130 else "#FFD700"

            _kpi_row(
                ("PR90  過熱線", f"{pr90:.0f}", "🔴 過熱" if pr90 > 130 else "◆ 正常", pr90c),
                ("PR75  機會線", f"{pr75:.0f}", "尋寶機會區",   "#FFD700"),
                ("市場均價",    f"{avg:.0f}",  "全市場中心",   "#00F5FF"),
            )

            cd = cdata.copy()
            def _zone(lbl):
                try:    mid = float(str(lbl).split('~')[0])
                except: return "正常區"
                if mid >= pr90: return "PR90 過熱區"
                if mid >= pr75: return "PR75 警示區"
                return "正常區"
            cd['區域'] = cd['區間'].apply(_zone)

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
                        text="CB 市場籌碼分佈 (Price Distribution)",
                        color='#FFD700', fontSize=13, font='JetBrains Mono'
                    ),
                    height=320, background='rgba(0,0,0,0)'
                )
                .configure_axis(gridColor='rgba(255,255,255,0.04)')
                .configure_view(strokeOpacity=0)
            )
            st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
            st.altair_chart(bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.toast("⚠️ 無法生成籌碼分佈圖，請檢查 CB 清單價格欄位", icon="⚡")
    else:
        st.markdown('<div class="empty-state"><div class="empty-icon">📂</div>'
                    '<div class="empty-text">UPLOAD CB LIST TO ACTIVATE</div></div>',
                    unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────

def render_1_4_heatmap():
    _sec_header("🗺️", "族群熱度雷達", "SECTOR HEATMAP")
    macro, kb, _ = _load_engines()
    df = st.session_state.get('df', pd.DataFrame())

    if not df.empty:
        if 'sector_heatmap' not in st.session_state:
            st.session_state.sector_heatmap = pd.DataFrame()

        st.markdown('<div class="action-wrap">', unsafe_allow_html=True)
        if st.button("🛰️  SCAN SECTOR HEATMAP", key="btn_heatmap"):
            st.toast("🚀 掃描族群資金流向中…", icon="⏳")
            with st.spinner("Analyzing sector capital flows…"):
                st.session_state.sector_heatmap = macro.analyze_sector_heatmap(df, kb)
            st.toast("✅ 族群熱度雷達掃描完成！", icon="🗺️")
        st.markdown('</div>', unsafe_allow_html=True)

        if not st.session_state.sector_heatmap.empty:
            st.caption("「多頭比例」= 族群中股價站上 87MA 生命線的比例")
            hm = st.session_state.sector_heatmap.copy()

            def colorize_ratio(val):
                try:
                    v = float(val)
                    if v >= 70:   return 'background-color:rgba(255,49,49,0.30)'
                    elif v >= 50: return 'background-color:rgba(255,215,0,0.22)'
                    else:         return 'background-color:rgba(38,166,154,0.20)'
                except: return ''

            styled = hm.style.applymap(colorize_ratio, subset=['多頭比例 (%)'])
            st.dataframe(styled, use_container_width=True)

            if '產業' in hm.columns and 'CB 數量' in hm.columns:
                try:
                    fig_pie = go.Figure(go.Pie(
                        labels=hm['產業'], values=hm['CB 數量'], hole=0.48,
                        marker=dict(
                            colors=['#FF3131','#FFD700','#00F5FF','#00FF7F',
                                    '#FF69B4','#FFA07A','#9370DB','#26A69A'],
                            line=dict(color='rgba(0,0,0,0.5)', width=1)
                        ),
                        textfont=dict(color='#EEE', size=13, family='Rajdhani'),
                    ))
                    fig_pie.update_layout(
                        title=dict(text="各族群 CB 數量佔比",
                                   font=dict(color='#FFD700', size=14, family='JetBrains Mono')),
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        height=320, margin=dict(t=40, b=0, l=0, r=0),
                        legend=dict(font=dict(color='#B0C0D0', size=12, family='Rajdhani'))
                    )
                    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
                    st.plotly_chart(fig_pie, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception: pass
        else:
            st.markdown('<div class="empty-state"><div class="empty-icon">🛰️</div>'
                        '<div class="empty-text">CLICK TO SCAN</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-state"><div class="empty-icon">📂</div>'
                    '<div class="empty-text">UPLOAD CB LIST TO ACTIVATE</div></div>',
                    unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────

def render_1_5_turnover():
    _sec_header("💹", "成交重心即時預測", "VOLUME LEADERS  TOP 100")
    macro, _, _ = _load_engines()
    _render_leader_dashboard(
        session_state_key="w15_data",
        fetch_function=macro.get_dynamic_turnover_leaders,
        top_n=100,
        sort_key_name="成交值"
    )


# ─────────────────────────────────────────────────────────────────────────────

def render_1_6_trend_radar():
    _sec_header("👑", "高價權值股趨勢雷達", "TREND RADAR  TOP 50")
    macro, _, _ = _load_engines()
    _render_leader_dashboard(
        session_state_key="w16_data",
        fetch_function=macro.get_high_price_leaders,
        top_n=50,
        sort_key_name="股價"
    )


# ─────────────────────────────────────────────────────────────────────────────

def render_1_7_predator():
    _sec_header("🎯", "台指期月K結算目標價推導", "WTX PREDATOR SYSTEM")
    st.markdown(
        '<div style="font-family:var(--f-mono);font-size:11px;color:#445566;'
        'letter-spacing:1.5px;border-left:2px solid rgba(255,215,0,0.2);'
        'padding:8px 14px;margin-bottom:18px;">'
        '獨門戰法 — 利用過去 12 個月結算慣性，推導本月台指期 (TX) 虛擬 K 棒與目標價</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="action-wrap">', unsafe_allow_html=True)
    if st.button("🔮  DERIVE WTX TARGETS", key="btn_futures"):
        st.toast("🚀 推導台指期目標價中…", icon="⏳")
        with st.spinner("Deriving settlement targets…"):
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

    # ── KPI Row ──────────────────────────────────────────────────────────────
    _kpi_row(
        ("ANCHOR OPEN", f"{res['anc']:,.0f}", res['name'],          "#00F5FF"),
        ("CURRENT",     f"{res['price']:,.0f}", f"{bias:+.0f} pts", bias_col),
    )

    # ── Direction Banner ─────────────────────────────────────────────────────
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
    "1.4": "#00FF7F",
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
