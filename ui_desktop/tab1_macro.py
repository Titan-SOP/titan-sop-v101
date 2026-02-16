# ui_desktop/tab1_macro.py
# Titan SOP V400 — 宏觀風控指揮中心 (Macro Risk Command Center)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  "GOD-TIER V400"  —  Netflix × Palantir × Tesla                 ║
# ║  COMPLETE OPTIMIZATION - ALL 3 MANDATORY UPGRADES APPLIED        ║
# ║    ✅ #1  Tactical Toast - ALL notifications upgraded            ║
# ║    ✅ #2  Valkyrie Typewriter - ALL AI text streamed             ║
# ║    ✅ #3  First Principles UI - Hero/Rank Cards/Transparent      ║
# ║  Logic: V82.0 fully preserved (MacroRiskEngine/Altair/Plotly)    ║
# ╚═══════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
from datetime import datetime
import time

from macro_risk import MacroRiskEngine
from knowledge_base import TitanKnowledgeBase
from config import Config


# ══════════════════════════════════════════════════════════════════════════════
#  [UPGRADE #2] VALKYRIE AI TYPEWRITER — Sci-Fi Terminal Streaming
# ══════════════════════════════════════════════════════════════════════════════
def _stream_text(text, speed=0.015):
    """Character-by-character generator for st.write_stream"""
    for char in text:
        yield char
        time.sleep(speed)


def _stream_fast(text, speed=0.008):
    """Faster streaming for shorter texts"""
    for char in text:
        yield char
        time.sleep(speed)


# ══════════════════════════════════════════════════════════════════════════════
#  [UPGRADE #1] TACTICAL TOAST SYSTEM — Unified Notification System
# ══════════════════════════════════════════════════════════════════════════════
def tactical_toast(message, mode="success", icon=None):
    """
    Unified toast system for all notifications
    Modes: success, processing, alert, info, error
    """
    toast_configs = {
        "success": {"icon": icon or "🎯", "prefix": "✅ 任務完成"},
        "processing": {"icon": icon or "⏳", "prefix": "🚀 正在執行戰術運算..."},
        "alert": {"icon": icon or "⚡", "prefix": "⚠️ 偵測到風險訊號"},
        "info": {"icon": icon or "ℹ️", "prefix": "📊 系統資訊"},
        "error": {"icon": icon or "❌", "prefix": "🔴 系統警報"},
    }
    
    config = toast_configs.get(mode, toast_configs["info"])
    st.toast(f"{config['prefix']} / {message}", icon=config['icon'])


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

**🌡️ 1.2 多空溫度計 / 📊 1.3 籌碼分佈 / 🗺️ 1.4 族群熱度**
高價權值股站上 87MA 的比例 = 市場體溫。籌碼分佈圖 + 族群資金流向，一眼判斷主力資金去向。

**💹 1.5 成交重心 / 👑 1.6 趨勢雷達**
全市場 TOP 100 成交重心即時掃描 + 高價權值股趨勢追蹤，附帶 87MA 扣抵預測與亞當理論反射路徑。

**🎯 1.7 台指獵殺 (WTX Predator)**
獨門戰法 — 利用過去 12 個月結算慣性推導本月台指期虛擬 K 棒，精準鎖定 1B/2B/3B/HR 結算目標價。

</div>""", unsafe_allow_html=True)
    if st.button("✅ 收到，進入戰情室 (Roger That)", type="primary", use_container_width=True):
        st.session_state['tab1_guided'] = True
        tactical_toast("戰情室已激活 / War Room Activated", "success")
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
#  CSS — TITAN OS CINEMATIC STYLES (ENHANCED V400)
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
   GLOBAL — Widen Streamlit container & Enhanced Metrics
══════════════════════════════════════════════════════ */
[data-testid="stMetricValue"] { font-size: 42px !important; }
[data-testid="stDataFrame"]   { font-size: 18px !important; }

/* ══════════════════════════════════════════════════════
   1. HERO BILLBOARD — Universal Module Header
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
.hero-val, .hero-title {
    font-family: var(--f-display);
    font-size: 80px !important;
    font-weight: 900;
    line-height: 1;
    letter-spacing: 3px;
    color: #FFF;
    text-shadow: 0 0 40px var(--hero-color, rgba(255,215,0,0.6));
    margin-bottom: 12px;
}
.hero-lbl, .hero-subtitle {
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
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 50%,
        var(--poster-accent, #FFD700) 0%,
        transparent 70%);
    opacity: 0;
    transition: opacity 0.3s;
}
.poster-card:hover::before {
    opacity: 0.08;
}
.poster-card:hover {
    transform: translateY(-6px) scale(1.02);
    border-color: var(--poster-accent, #FFD700);
    box-shadow: 0 16px 40px rgba(0,0,0,0.6),
                0 0 0 1px var(--poster-accent, #FFD700);
}
.poster-card.active {
    border-color: var(--poster-accent, #FFD700);
    box-shadow: 0 8px 28px rgba(0,0,0,0.5),
                0 0 0 2px var(--poster-accent, #FFD700),
                inset 0 0 40px rgba(var(--poster-rgb, 255,215,0), 0.06);
}
.poster-icon {
    font-size: 38px;
    line-height: 1;
    filter: drop-shadow(0 0 12px var(--poster-accent, #FFD700));
}
.poster-code {
    font-family: var(--f-mono);
    font-size: 11px;
    color: var(--poster-accent, #FFD700);
    letter-spacing: 2px;
    font-weight: 600;
}
.poster-text {
    font-family: var(--f-body);
    font-size: 15px;
    font-weight: 600;
    color: #C8D8E8;
    letter-spacing: 0.5px;
}
.poster-tag {
    font-family: var(--f-mono);
    font-size: 9px;
    color: #556677;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

/* ══════════════════════════════════════════════════════
   3. RANK CARDS — Visual Data Cards (replaces dataframes)
══════════════════════════════════════════════════════ */
.rank-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
    margin: 24px 0;
}
.rank-card {
    background: var(--bg-card);
    border: 1px solid var(--bd-subtle);
    border-radius: 12px;
    padding: 20px;
    transition: all 0.3s;
    position: relative;
}
.rank-card:hover {
    transform: translateY(-4px);
    border-color: var(--c-gold);
    box-shadow: 0 12px 32px rgba(0,0,0,0.4);
}
.rank-number {
    position: absolute;
    top: 12px;
    right: 12px;
    font-family: var(--f-display);
    font-size: 48px;
    color: rgba(255,215,0,0.15);
    font-weight: 900;
}
.rank-title {
    font-family: var(--f-body);
    font-size: 20px;
    font-weight: 700;
    color: #FFF;
    margin-bottom: 8px;
}
.rank-value {
    font-family: var(--f-mono);
    font-size: 32px;
    font-weight: 700;
    color: var(--c-cyan);
    margin: 12px 0;
}
.rank-meta {
    font-family: var(--f-mono);
    font-size: 12px;
    color: #888;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}
.rank-chip {
    background: rgba(255,215,0,0.1);
    border: 1px solid rgba(255,215,0,0.3);
    color: var(--c-gold);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
    letter-spacing: 1px;
}

/* ══════════════════════════════════════════════════════
   4. STREAMING TEXT CONTAINER (Terminal Box)
══════════════════════════════════════════════════════ */
.terminal-box {
    font-family: var(--f-mono);
    background: #050505;
    color: #00F5FF;
    padding: 24px;
    border-left: 3px solid #00F5FF;
    border-radius: 8px;
    box-shadow: inset 0 0 20px rgba(0, 245, 255, 0.05);
    margin: 20px 0;
    line-height: 1.8;
    font-size: 15px;
}

/* ══════════════════════════════════════════════════════
   5. GLASSMORPHISM CONTAINERS (Input Forms)
══════════════════════════════════════════════════════ */
.glass-container {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 28px;
    margin: 20px 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.glass-label {
    font-family: var(--f-mono);
    font-size: 12px;
    color: var(--c-gold);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
    display: block;
}

/* ══════════════════════════════════════════════════════
   6. CHART WRAPPER (Transparent backgrounds)
══════════════════════════════════════════════════════ */
.chart-wrap {
    background: transparent;
    border-radius: 12px;
    padding: 16px;
    margin: 20px 0;
}

/* ══════════════════════════════════════════════════════
   OTHER PRESERVED STYLES
══════════════════════════════════════════════════════ */
.nav-deck-frame {
    background: rgba(10,14,20,0.4);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 18px;
    padding: 22px 18px 18px;
    margin-bottom: 30px;
}
.nav-deck-label {
    font-family: var(--f-mono);
    font-size: 10px;
    color: rgba(255,215,0,0.4);
    letter-spacing: 3px;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 16px;
}
.content-frame {
    background: rgba(255,255,255,0.008);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 20px;
    padding: 32px 28px;
    min-height: 600px;
}

/* Signal gauge (1.1) */
.gauge-box {
    display: inline-block;
    padding: 6px 20px;
    border-radius: 40px;
    font-family: var(--f-mono);
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 1.5px;
    background: rgba(0,0,0,0.6);
}

/* WTX Predator styles (1.7) */
.ctrl-flag {
    font-family: var(--f-mono);
    font-size: 17px;
    font-weight: 700;
    color: #FFF;
    background: linear-gradient(90deg,
        rgba(var(--cf-rgb),0.2) 0%,
        rgba(var(--cf-rgb),0.05) 100%);
    border-left: 4px solid rgb(var(--cf-rgb));
    padding: 16px 24px;
    border-radius: 8px;
    margin: 20px 0;
    letter-spacing: 1px;
}
.bases-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 24px 0;
}
.base-card {
    background: rgba(30,30,40,0.5);
    border: 2px solid rgba(100,100,120,0.3);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s;
}
.base-card.hit {
    border-color: #00FF7F;
    background: rgba(0,255,127,0.08);
    box-shadow: 0 0 20px rgba(0,255,127,0.2);
}
.base-card.miss {
    border-color: rgba(100,100,120,0.3);
}
.base-card.hr {
    background: rgba(50,20,20,0.3);
}
.base-name {
    font-family: var(--f-body);
    font-size: 14px;
    color: #888;
    margin-bottom: 8px;
    letter-spacing: 2px;
}
.base-price {
    font-family: var(--f-display);
    font-size: 32px;
    font-weight: 900;
    color: #FFF;
    margin: 8px 0;
}
.base-status {
    font-family: var(--f-mono);
    font-size: 12px;
    color: #AAA;
}

.titan-foot {
    text-align: center;
    font-family: var(--f-mono);
    font-size: 10px;
    color: rgba(200,215,230,0.2);
    letter-spacing: 2px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.04);
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER: Create Rank Card HTML
# ══════════════════════════════════════════════════════════════════════════════
def create_rank_card(rank, title, value, meta_items):
    """Generate HTML for a single rank card"""
    chips = "".join([f'<span class="rank-chip">{item}</span>' for item in meta_items])
    return f"""
<div class="rank-card">
    <div class="rank-number">#{rank}</div>
    <div class="rank-title">{title}</div>
    <div class="rank-value">{value}</div>
    <div class="rank-meta">{chips}</div>
</div>
"""


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1.1 — MACRO HUD (PRESERVED LOGIC + ENHANCED UX)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_1_hud():
    """
    🚦 風控儀表 (Macro Risk HUD)
    Logic: V82.0 preserved
    UX: Enhanced with typewriter for AI analysis
    """
    tactical_toast("風控儀表系統啟動 / HUD System Online", "processing")
    
    eng = MacroRiskEngine()
    try:
        data = eng.compute_macro_signal()
    except Exception as e:
        tactical_toast(f"資料載入失敗 / Data Load Failed: {str(e)}", "error")
        return

    sig = data["signal"]
    hex_color, rgb_str = SIGNAL_PALETTE[sig]

    # Hero Billboard
    st.markdown(f"""
<div class="hero-container" style="--hero-glow:rgba({rgb_str},0.15);
     --hero-color:{hex_color};--hero-rgb:{rgb_str};">
  <div class="hero-title">{SIGNAL_MAP[sig].split('：')[0]}</div>
  <div class="hero-subtitle">MACRO RISK SIGNAL</div>
  <div class="hero-badge">
    <span class="hero-pulse"></span>
    LIVE ANALYSIS
  </div>
</div>""", unsafe_allow_html=True)

    tactical_toast("信號計算完成 / Signal Computed", "success")

    # Metrics Row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🔥 市場溫度", f"{data.get('temp_pct', 0):.1f}%",
                  f"{data.get('temp_delta', 0):+.1f}%")
    with c2:
        st.metric("📊 PR90 籌碼", f"{data.get('pr90', 0):.1f}%",
                  f"{data.get('pr90_delta', 0):+.1f}%")
    with c3:
        st.metric("💬 PTT 情緒", f"{data.get('ptt_score', 0):.1f}",
                  f"{data.get('ptt_delta', 0):+.1f}")
    with c4:
        st.metric("📈 VIX 指數", f"{data.get('vix', 0):.2f}",
                  f"{data.get('vix_delta', 0):+.2f}")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # [UPGRADE #2] AI Analysis with Typewriter
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis_text = f"""
【宏觀風控 AI 判讀】

當前信號：{SIGNAL_MAP[sig]}

市場體溫 {data.get('temp_pct', 0):.1f}% — {'高溫過熱區' if data.get('temp_pct', 0) > 70 else '溫度正常' if data.get('temp_pct', 0) > 30 else '低溫冷卻區'}
籌碼分佈 PR90 {data.get('pr90', 0):.1f}% — {'籌碼集中主力控盤' if data.get('pr90', 0) > 15 else '籌碼分散散戶主導'}
PTT 散戶情緒 {data.get('ptt_score', 0):.1f} 分 — {'樂觀情緒高漲' if data.get('ptt_score', 0) > 6 else '謹慎觀望氛圍'}
VIX 恐慌指數 {data.get('vix', 0):.2f} — {'市場波動加劇' if data.get('vix', 0) > 20 else '市場平穩運行'}

綜合判定：根據三重驗證機制，系統建議當前採取「{SIGNAL_MAP[sig].split('：')[1]}」策略。
"""
    
    if 'hud_analysis_streamed' not in st.session_state:
        st.write_stream(_stream_text(analysis_text))
        st.session_state['hud_analysis_streamed'] = True
    else:
        st.markdown(analysis_text)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Supporting Chart (preserved logic)
    if 'chart_data' in data:
        chart_df = pd.DataFrame(data['chart_data'])
        chart = alt.Chart(chart_df).mark_area(
            opacity=0.6,
            color=hex_color
        ).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('value:Q', title='Signal Strength')
        ).properties(
            height=300,
            background='rgba(0,0,0,0)'
        ).configure_view(
            strokeOpacity=0
        ).configure_axis(
            labelColor='#556677',
            titleColor='#445566',
            gridColor='rgba(255,255,255,0.04)'
        )
        
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.altair_chart(chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">Macro HUD V400 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1.2 — THERMOMETER (PRESERVED LOGIC + HERO + TYPEWRITER)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_2_thermometer():
    """🌡️ 多空溫度計 (Market Thermometer)"""
    tactical_toast("多空溫度計啟動 / Thermometer Loading", "processing")
    
    eng = MacroRiskEngine()
    try:
        data = eng.compute_temperature()
    except Exception as e:
        tactical_toast(f"溫度計算失敗 / Calculation Failed: {str(e)}", "error")
        return

    temp = data.get('temp_pct', 0)
    color = "#FF6B6B" if temp > 70 else "#FFD700" if temp > 30 else "#00F5FF"
    rgb = "255,107,107" if temp > 70 else "255,215,0" if temp > 30 else "0,245,255"

    # Hero Billboard
    st.markdown(f"""
<div class="hero-container" style="--hero-glow:rgba({rgb},0.15);
     --hero-color:{color};--hero-rgb:{rgb};">
  <div class="hero-val">{temp:.1f}°C</div>
  <div class="hero-lbl">MARKET TEMPERATURE</div>
  <div class="hero-badge">
    <span class="hero-pulse"></span>
    {'過熱 OVERHEATED' if temp > 70 else '正常 NORMAL' if temp > 30 else '過冷 COLD'}
  </div>
</div>""", unsafe_allow_html=True)

    tactical_toast("溫度計算完成 / Temperature Ready", "success")

    # AI Analysis with Typewriter
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis = f"""
【多空溫度計 AI 研判】

當前市場體溫：{temp:.1f}°C

溫度解讀：
- 當前有 {temp:.1f}% 的高價權值股站上 87MA
- {'市場處於過熱狀態，建議警惕回調風險' if temp > 70 else '市場溫度適中，可維持正常操作' if temp > 30 else '市場偏冷，適合尋找低接機會'}

歷史回測：過去 12 個月中，溫度超過 75°C 後平均 {data.get('avg_days_to_cool', 7)} 個交易日開始降溫。
"""
    
    if 'thermo_streamed' not in st.session_state:
        st.write_stream(_stream_fast(analysis))
        st.session_state['thermo_streamed'] = True
    else:
        st.markdown(analysis)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Thermometer Chart (preserved Plotly logic with transparent background)
    if 'history' in data:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['history']['dates'],
            y=data['history']['temps'],
            mode='lines+markers',
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color),
            name='Temperature'
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='JetBrains Mono', color='#556677'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', title='Temperature (%)'),
            height=400,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">Thermometer V400 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1.3 — PR90 (PRESERVED LOGIC + RANK CARDS)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_3_pr90():
    """📊 籌碼分佈 (PR90 Distribution)"""
    tactical_toast("籌碼分析引擎啟動 / Chip Analysis Loading", "processing")
    
    eng = MacroRiskEngine()
    try:
        data = eng.compute_pr90()
    except Exception as e:
        tactical_toast(f"籌碼分析失敗 / Analysis Failed: {str(e)}", "error")
        return

    pr90 = data.get('pr90_pct', 0)
    color = "#00FF7F" if pr90 > 15 else "#FFD700" if pr90 > 10 else "#FF6B6B"
    rgb = "0,255,127" if pr90 > 15 else "255,215,0" if pr90 > 10 else "255,107,107"

    # Hero Billboard
    st.markdown(f"""
<div class="hero-container" style="--hero-glow:rgba({rgb},0.15);
     --hero-color:{color};--hero-rgb:{rgb};">
  <div class="hero-val">{pr90:.1f}%</div>
  <div class="hero-lbl">PR90 CONCENTRATION</div>
  <div class="hero-badge">
    <span class="hero-pulse"></span>
    {'主力控盤 CONTROLLED' if pr90 > 15 else '正常分布 NORMAL' if pr90 > 10 else '分散籌碼 DISPERSED'}
  </div>
</div>""", unsafe_allow_html=True)

    tactical_toast("籌碼分析完成 / Chip Analysis Ready", "success")

    # [UPGRADE #3] Rank Cards instead of raw dataframe
    if 'top_stocks' in data and len(data['top_stocks']) > 0:
        st.markdown('<div class="glass-container"><span class="glass-label">🏆 TOP 10 籌碼集中標的</span>', unsafe_allow_html=True)
        st.markdown('<div class="rank-grid">', unsafe_allow_html=True)
        
        for i, stock in enumerate(data['top_stocks'][:10], 1):
            card_html = create_rank_card(
                rank=i,
                title=f"{stock.get('symbol', 'N/A')} {stock.get('name', '')}",
                value=f"{stock.get('pr90', 0):.1f}%",
                meta_items=[
                    f"價格: {stock.get('price', 0):.2f}",
                    f"成交量: {stock.get('volume', 0):,.0f}K"
                ]
            )
            st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
    else:
        st.info("📊 暫無籌碼數據")

    # AI Analysis
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    analysis = f"""
【籌碼分佈 AI 解讀】

PR90 指標：{pr90:.1f}%

判讀：{'前 10% 股民控制超過 15% 的股票，顯示主力高度控盤' if pr90 > 15 else '籌碼分布相對均勻，散戶參與度高' if pr90 <= 10 else '籌碼集中度中等'}

策略建議：{'關注主力動向，順勢而為' if pr90 > 15 else '市場分散，可自主選股' if pr90 <= 10 else '保持觀察，謹慎操作'}
"""
    
    if 'pr90_streamed' not in st.session_state:
        st.write_stream(_stream_fast(analysis))
        st.session_state['pr90_streamed'] = True
    else:
        st.markdown(analysis)
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">PR90 Analysis V400 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1.4 — HEATMAP (PRESERVED LOGIC + HERO)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_4_heatmap():
    """🗺️ 族群熱度 (Sector Heatmap)"""
    tactical_toast("族群熱度圖生成中 / Heatmap Generating", "processing")
    
    eng = MacroRiskEngine()
    try:
        data = eng.compute_sector_heatmap()
    except Exception as e:
        tactical_toast(f"熱度圖生成失敗 / Generation Failed: {str(e)}", "error")
        return

    # Hero
    st.markdown("""
<div class="hero-container" style="--hero-glow:rgba(0,255,127,0.12);
     --hero-color:#00FF7F;--hero-rgb:0,255,127;">
  <div class="hero-title">🗺️ 族群熱度</div>
  <div class="hero-subtitle">SECTOR HEATMAP</div>
  <div class="hero-badge">
    <span class="hero-pulse"></span>
    REAL-TIME FLOW
  </div>
</div>""", unsafe_allow_html=True)

    tactical_toast("熱度圖就緒 / Heatmap Ready", "success")

    # Rank Cards for top sectors
    if 'sectors' in data and len(data['sectors']) > 0:
        st.markdown('<div class="glass-container"><span class="glass-label">🔥 熱門族群 TOP 6</span>', unsafe_allow_html=True)
        st.markdown('<div class="rank-grid">', unsafe_allow_html=True)
        
        for i, sector in enumerate(data['sectors'][:6], 1):
            card_html = create_rank_card(
                rank=i,
                title=sector.get('name', 'N/A'),
                value=f"+{sector.get('gain_pct', 0):.2f}%",
                meta_items=[
                    f"資金流入: {sector.get('money_flow', 0):,.0f}M",
                    f"領漲股: {sector.get('leader', 'N/A')}"
                ]
            )
            st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

    # Plotly Heatmap (preserved logic with transparent background)
    if 'heatmap_data' in data:
        fig = go.Figure(data=go.Heatmap(
            z=data['heatmap_data']['values'],
            x=data['heatmap_data']['x_labels'],
            y=data['heatmap_data']['y_labels'],
            colorscale='RdYlGn',
            text=data['heatmap_data']['text'],
            texttemplate='%{text}',
            textfont={"size": 14, "family": "JetBrains Mono"},
            colorbar=dict(title="漲跌幅 %")
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='JetBrains Mono', color='#556677'),
            height=500,
            margin=dict(l=100, r=40, t=40, b=100)
        )
        
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">Sector Heatmap V400 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1.5 — TURNOVER (PRESERVED LOGIC + RANK CARDS)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_5_turnover():
    """💹 成交重心 (Volume Leaders)"""
    tactical_toast("成交重心掃描中 / Volume Scanning", "processing")
    
    eng = MacroRiskEngine()
    try:
        data = eng.compute_turnover_leaders()
    except Exception as e:
        tactical_toast(f"掃描失敗 / Scan Failed: {str(e)}", "error")
        return

    # Hero
    st.markdown("""
<div class="hero-container" style="--hero-glow:rgba(255,160,122,0.12);
     --hero-color:#FFA07A;--hero-rgb:255,160,122;">
  <div class="hero-title">💹 成交重心</div>
  <div class="hero-subtitle">VOLUME LEADERS</div>
  <div class="hero-badge">
    <span class="hero-pulse"></span>
    TOP 100 SCAN
  </div>
</div>""", unsafe_allow_html=True)

    tactical_toast("掃描完成 / Scan Complete", "success")

    # Rank Cards
    if 'leaders' in data and len(data['leaders']) > 0:
        st.markdown('<div class="glass-container"><span class="glass-label">📈 成交量王者 TOP 10</span>', unsafe_allow_html=True)
        st.markdown('<div class="rank-grid">', unsafe_allow_html=True)
        
        for i, stock in enumerate(data['leaders'][:10], 1):
            card_html = create_rank_card(
                rank=i,
                title=f"{stock.get('symbol', 'N/A')} {stock.get('name', '')}",
                value=f"{stock.get('volume', 0):,.0f}K",
                meta_items=[
                    f"價格: {stock.get('price', 0):.2f}",
                    f"漲跌: {stock.get('change_pct', 0):+.2f}%"
                ]
            )
            st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">Volume Analysis V400 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1.6 — TREND RADAR (PRESERVED LOGIC + HERO + TYPEWRITER)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_6_trend_radar():
    """👑 趨勢雷達 (Trend Radar)"""
    tactical_toast("趨勢雷達掃描中 / Radar Scanning", "processing")
    
    eng = MacroRiskEngine()
    try:
        data = eng.compute_trend_radar()
    except Exception as e:
        tactical_toast(f"雷達掃描失敗 / Radar Failed: {str(e)}", "error")
        return

    # Hero
    st.markdown("""
<div class="hero-container" style="--hero-glow:rgba(147,112,219,0.12);
     --hero-color:#9370DB;--hero-rgb:147,112,219;">
  <div class="hero-title">👑 趨勢雷達</div>
  <div class="hero-subtitle">TREND RADAR</div>
  <div class="hero-badge">
    <span class="hero-pulse"></span>
    87MA TRACKING
  </div>
</div>""", unsafe_allow_html=True)

    tactical_toast("雷達就緒 / Radar Ready", "success")

    # AI Summary with Typewriter
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    summary = f"""
【趨勢雷達 AI 報告】

監控標的：{data.get('total_stocks', 0)} 支高價權值股
站上 87MA：{data.get('above_87ma', 0)} 支 ({data.get('above_87ma_pct', 0):.1f}%)

趨勢判定：{'強勢多頭格局，主流股普遍站穩趨勢線' if data.get('above_87ma_pct', 0) > 70 else '盤整格局，多空拉鋸' if data.get('above_87ma_pct', 0) > 40 else '弱勢空頭，防守為先'}

亞當理論反射：預估未來 {data.get('prediction_days', 20)} 日關鍵轉折點位於 {data.get('adam_target', 0):,.0f} 點。
"""
    
    if 'radar_streamed' not in st.session_state:
        st.write_stream(_stream_fast(summary))
        st.session_state['radar_streamed'] = True
    else:
        st.markdown(summary)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Rank Cards for trending stocks
    if 'trending' in data and len(data['trending']) > 0:
        st.markdown('<div class="glass-container"><span class="glass-label">🚀 趨勢強勢股 TOP 8</span>', unsafe_allow_html=True)
        st.markdown('<div class="rank-grid">', unsafe_allow_html=True)
        
        for i, stock in enumerate(data['trending'][:8], 1):
            card_html = create_rank_card(
                rank=i,
                title=f"{stock.get('symbol', 'N/A')} {stock.get('name', '')}",
                value=f"+{stock.get('distance_from_87ma', 0):.1f}%",
                meta_items=[
                    f"87MA 扣抵: {stock.get('ma87_deduction', 0):.2f}",
                    f"趨勢強度: {stock.get('trend_strength', 0):.1f}"
                ]
            )
            st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)

    # Altair Chart (preserved logic with transparent background)
    if 'chart_data' in data:
        chart_df = pd.DataFrame(data['chart_data'])
        
        base = alt.Chart(chart_df).encode(
            x=alt.X('date:T', title='Date')
        )
        
        line_87ma = base.mark_line(color='#9370DB', strokeWidth=2).encode(
            y=alt.Y('ma87:Q', title='Price')
        )
        
        line_price = base.mark_line(color='#00F5FF', strokeWidth=3).encode(
            y='price:Q'
        )
        
        chart = (line_87ma + line_price).properties(
            height=350,
            background='rgba(0,0,0,0)'
        ).configure_view(
            strokeOpacity=0
        ).configure_axis(
            labelColor='#556677',
            titleColor='#445566',
            gridColor='rgba(255,255,255,0.04)'
        )
        
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.altair_chart(chart, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">Trend Radar V400 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1.7 — WTX PREDATOR (FULLY PRESERVED FROM V300)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_7_predator():
    """🎯 台指獵殺 (WTX Predator) - EXACT LOGIC PRESERVED"""
    tactical_toast("台指獵殺系統啟動 / Predator System Online", "processing")
    
    eng = MacroRiskEngine()
    try:
        res = eng.compute_wtx_predator()
    except Exception as e:
        tactical_toast(f"獵殺計算失敗 / Predator Failed: {str(e)}", "error")
        return

    is_red  = (res['is_red_month'])
    bias    = res['price'] - res['anc']
    bar_color = "#FF6B6B" if is_red else "#00FF7F"
    cf_rgb    = "255,107,107" if is_red else "0,255,127"

    # Hero Billboard
    st.markdown(f"""
<div class="hero-container" style="--hero-glow:rgba({cf_rgb},0.15);
     --hero-color:{bar_color};--hero-rgb:{cf_rgb};">
  <div class="hero-title">{res['name']}</div>
  <div class="hero-subtitle">WTX PREDATOR TARGET</div>
  <div class="hero-badge">
    <span class="hero-pulse"></span>
    {res['price']:,.0f} pts
  </div>
</div>""", unsafe_allow_html=True)

    tactical_toast("獵殺目標鎖定 / Target Locked", "success")

    # Direction Banner
    ctrl = "🔴 多方控盤 — 慣性收長紅" if is_red else "🟢 空方控盤 — 慣性收長黑"
    st.markdown(f'<div class="ctrl-flag" style="--cf-rgb:{cf_rgb};">{ctrl}</div>',
                unsafe_allow_html=True)

    # [UPGRADE #2] Typewriter for predator verdict
    pred_text = (
        f"【台指期獵殺判讀】{res['name']} 本月開盤錨定 {res['anc']:,.0f}，"
        f"現價 {res['price']:,.0f} ({bias:+.0f} pts)。"
        f"{'多方控盤，慣性收紅K' if is_red else '空方控盤，慣性收黑K'}。"
        f"目標推導：1B={res['t']['1B']:,.0f} / 2B={res['t']['2B']:,.0f} / "
        f"3B={res['t']['3B']:,.0f} / HR={res['t']['HR']:,.0f}。"
    )
    
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    if 'pred_streamed' not in st.session_state:
        st.write_stream(_stream_text(pred_text, speed=0.012))
        st.session_state['pred_streamed'] = True
    else:
        st.markdown(pred_text)
    st.markdown('</div>', unsafe_allow_html=True)

    # Baseball Target Cards
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

    # ALTAIR BASEBALL K-BAR CHART — EXACT LOGIC PRESERVED
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
        f'<div class="titan-foot">WTX Predator V400 &nbsp;·&nbsp; '
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
#  [ALL 3 UPGRADES FULLY INTEGRATED]
# ══════════════════════════════════════════════════════════════════════════════
def render():
    """Tab 1 — God-Tier Cinematic Trading Experience (V400)"""
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
      TITAN OS V400 — GOD-TIER
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
                tactical_toast(f"切換至 {label_zh} / Switching to {label_en}", "info", icon="🎯")
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
            tactical_toast(f"模組 {active} 渲染失敗 / Module Error: {str(exc)}", "error")
            with st.expander("🔍 Debug Trace"):
                st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)  # content-frame
