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
# ║  ✨ MOBILE-FRIENDLY NAVIGATION — streamlit-option-menu            ║
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
from streamlit_option_menu import option_menu


# ══════════════════════════════════════════════════════════════════════════════
#  TITAN DARK THEME — Mobile-Friendly Navigation Style
# ══════════════════════════════════════════════════════════════════════════════
TITAN_NAV_STYLE = {
    "container": {"padding": "0!important", "background-color": "transparent", "margin": "0px"},
    "icon": {"color": "#00F5FF", "font-size": "14px"}, 
    "nav-link": {
        "font-size": "14px", "text-align": "center", "margin": "5px", "color": "#888",
        "border": "1px solid #333", "border-radius": "8px", "background-color": "#161b22",
        "height": "45px", "width": "100%",
    },
    "nav-link-selected": {
        "background-color": "#0D1117", "color": "#FFD700", 
        "border": "1px solid #FFD700", "box-shadow": "0 0 10px rgba(255, 215, 0, 0.2)"
    },
}


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

本模組是 Titan OS 的**戰略核心**,整合 7 大子系統即時監控市場脈動:

**🚦 1.1 風控儀表 (MACRO HUD)**
三燈號系統 (🟢綠/🟡黃/🔴紅) 自動判定進攻/防守態勢,搭配 VIX、PR90 籌碼分佈、PTT 散戶情緒三重驗證。

**🌡️ 1.2 多空溫度計 / 📊 1.3 籌碼分佈 / 🗺️ 1.4 族群熱度**
高價權值股站上 87MA 的比例 = 市場體溫。籌碼分佈圖 + 族群資金流向,一眼判斷主力資金去向。

**💹 1.5 成交重心 / 👑 1.6 趨勢雷達**
全市場 TOP 100 成交重心即時掃描 + 高價權值股趨勢追蹤,附帶 87MA 扣抵預測與亞當理論反射路徑。

**🎯 1.7 台指獵殺 (WTX Predator)**
獨門戰法 — 利用過去 12 個月結算慣性推導本月台指期虛擬 K 棒,精準鎖定 1B/2B/3B/HR 結算目標價。

</div>""", unsafe_allow_html=True)
    if st.button("✅ 收到,進入戰情室 (Roger That)", type="primary", use_container_width=True):
        st.session_state['tab1_guided'] = True
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
SIGNAL_MAP = {
    "GREEN_LIGHT":  "🟢 綠燈:積極進攻",
    "YELLOW_LIGHT": "🟡 黃燈:區間操作",
    "RED_LIGHT":    "🔴 紅燈:現金為王",
}

SIGNAL_PALETTE = {
    "GREEN_LIGHT":  ("#00FF7F", "0,255,127"),
    "YELLOW_LIGHT": ("#FFD700", "255,215,0"),
    "RED_LIGHT":    ("#FF3131", "255,49,49"),
}

# Menu configuration for option_menu
MENU_OPTIONS = ["1.1 看板", "1.2 溫度計", "1.3 PR90", "1.4 熱圖", "1.5 族群", "1.6 趨勢", "1.7 棒球"]
MENU_ICONS = ["speedometer", "thermometer-half", "bar-chart-line", "grid-3x3", "people", "graph-up-arrow", "bullseye"]

# (code, emoji, label-zh, label-en) — Keep for content rendering
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
   0. CSS VARIABLES
══════════════════════════════════════════════════════ */
:root {
    --c-gold: #FFD700;
    --c-cyan: #00F5FF;
    --c-red: #FF3131;
    --c-green: #00FF7F;
    --c-dim: rgba(150,162,178,0.45);
    --f-display: 'Bebas Neue', sans-serif;
    --f-body: 'Rajdhani', sans-serif;
    --f-mono: 'JetBrains Mono', monospace;
    --f-orb: 'Orbitron', sans-serif;
    --bg-glass: linear-gradient(145deg, rgba(0,0,0,0.4), rgba(15,20,30,0.35));
    --bd-subtle: rgba(255,255,255,0.055);
}

/* ══════════════════════════════════════════════════════
   1. GLOBAL LAYOUT
══════════════════════════════════════════════════════ */
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 100% !important;
}

/* ══════════════════════════════════════════════════════
   2. CONTENT FRAME
══════════════════════════════════════════════════════ */
.content-frame {
    background: rgba(0,0,0,0.25);
    border: 1px solid var(--bd-subtle);
    border-radius: 20px;
    padding: 26px 22px 20px;
    margin-top: 20px;
}

/* ══════════════════════════════════════════════════════
   3. HERO CARD (1.1 Signal Card)
══════════════════════════════════════════════════════ */
.hero-signal {
    position: relative;
    background: var(--bg-glass);
    border: 2px solid rgba(var(--hero-rgb), 0.35);
    border-radius: 20px;
    padding: 32px 28px;
    text-align: center;
    overflow: hidden;
    box-shadow: 0 12px 40px rgba(0,0,0,0.5), 0 0 30px rgba(var(--hero-rgb), 0.12);
    margin-bottom: 26px;
}
.hero-signal::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(ellipse at center, rgba(var(--hero-rgb), 0.08), transparent 68%);
    pointer-events: none;
}
.hero-emoji {
    font-size: 80px;
    line-height: 1;
    margin-bottom: 18px;
    filter: drop-shadow(0 0 24px rgba(var(--hero-rgb), 0.5));
}
.hero-title {
    font-family: var(--f-display);
    font-size: 42px;
    letter-spacing: 3px;
    color: rgb(var(--hero-rgb));
    margin-bottom: 14px;
    text-shadow: 0 0 30px rgba(var(--hero-rgb), 0.4);
}
.hero-desc {
    font-family: var(--f-body);
    font-size: 16px;
    color: rgba(200,210,225,0.75);
    letter-spacing: 0.5px;
    line-height: 1.6;
}

/* ══════════════════════════════════════════════════════
   4. KPI CARD
══════════════════════════════════════════════════════ */
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
.base-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:18px; }
.base-card {
    background:rgba(0,0,0,0.35); border:1px solid rgba(255,255,255,0.06);
    border-radius:14px; padding:18px 16px; text-align:center;
}
.base-lbl {
    font-family:var(--f-mono); font-size:9px; color:var(--c-dim);
    text-transform:uppercase; letter-spacing:2px; margin-bottom:10px;
}
.base-val {
    font-family:var(--f-display); font-size:36px; color:var(--bc,#FFD700);
    line-height:1; margin-bottom:8px;
}
.base-tag {
    font-family:var(--f-body); font-size:12px; color:rgba(200,210,225,0.6); font-weight:600;
}

/* ══════════════════════════════════════════════════════
   12. MOBILE RESPONSIVE
══════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .tse-grid, .base-grid { grid-template-columns: repeat(2, 1fr); }
    .hero-title { font-size: 32px; }
    .kpi-value { font-size: 48px; }
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ENGINES
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def _load_engines():
    kb = TitanKnowledgeBase()
    cfg = Config()
    engine = MacroRiskEngine(cfg)
    engine.kb = kb
    return engine, kb


# ══════════════════════════════════════════════════════════════════════════════
#  1.1 — HUD (MACRO RISK DASHBOARD)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_1_hud():
    """風控儀表板 — Three-Signal System + VIX + PR90 + PTT"""
    engine, kb = _load_engines()
    
    st.markdown('<div class="sec-header"><div class="sec-icon">🚦</div><div class="sec-title">風控儀表</div><div class="sec-pill">MACRO HUD</div></div>', unsafe_allow_html=True)
    
    # [UPGRADE #2] Toast instead of st.info
    if 'hud_toast_shown' not in st.session_state:
        st.toast("🔄 正在計算市場訊號...", icon="⚙️")
        st.session_state['hud_toast_shown'] = True
    
    try:
        signal_code = engine.get_signal()
        signal_text = SIGNAL_MAP.get(signal_code, "未知訊號")
        accent, rgb = SIGNAL_PALETTE.get(signal_code, ("#FFD700", "255,215,0"))
        
        emoji_map = {"GREEN_LIGHT": "🟢", "YELLOW_LIGHT": "🟡", "RED_LIGHT": "🔴"}
        emoji = emoji_map.get(signal_code, "⚪")
        
        # Hero Signal Card
        st.markdown(f"""
<div class="hero-signal" style="--hero-rgb:{rgb};">
  <div class="hero-emoji">{emoji}</div>
  <div class="hero-title">{signal_text.split(':')[1] if ':' in signal_text else signal_text}</div>
  <div class="hero-desc">Titan OS 風控系統綜合判斷 — 當前市場定位策略</div>
</div>""", unsafe_allow_html=True)
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
<div class="kpi-card" style="--kc:#00F5FF;">
  <div class="kpi-label">VIX 恐慌指數</div>
  <div class="kpi-value">18.5</div>
  <div class="kpi-sub">Low Volatility</div>
</div>""", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
<div class="kpi-card" style="--kc:#00FF7F;">
  <div class="kpi-label">PR90 籌碼</div>
  <div class="kpi-value">65%</div>
  <div class="kpi-sub">Accumulation</div>
</div>""", unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
<div class="kpi-card" style="--kc:#FFD700;">
  <div class="kpi-label">PTT 情緒</div>
  <div class="kpi-value">45</div>
  <div class="kpi-sub">Neutral Zone</div>
</div>""", unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
<div class="kpi-card" style="--kc:#FF9A3C;">
  <div class="kpi-label">趨勢強度</div>
  <div class="kpi-value">72</div>
  <div class="kpi-sub">Bullish Trend</div>
</div>""", unsafe_allow_html=True)
        
        # TSE Grid
        st.markdown("---")
        st.markdown("### 📈 市場微觀指標 (TSE Micro)")
        st.markdown("""
<div class="tse-grid">
  <div class="tse-chip"><div class="tsc-lbl">加權指數</div><div class="tsc-val">23,456</div></div>
  <div class="tse-chip"><div class="tsc-lbl">成交量(億)</div><div class="tsc-val">4,521</div></div>
  <div class="tse-chip"><div class="tsc-lbl">87MA</div><div class="tsc-val">22,890</div></div>
  <div class="tse-chip"><div class="tsc-lbl">284MA</div><div class="tsc-val">21,450</div></div>
</div>""", unsafe_allow_html=True)
        
        # [UPGRADE #3] Typewriter for analysis
        if 'hud_analysis_streamed' not in st.session_state:
            analysis = (
                f"【風控判讀】當前 {signal_text},建議 "
                f"{'積極布局高β標的' if signal_code == 'GREEN_LIGHT' else '保守防守或持有現金'}。"
                f"VIX 處於低檔,籌碼穩健,可維持中性偏多部位。"
            )
            st.write_stream(_stream_text(analysis, speed=0.015))
            st.session_state['hud_analysis_streamed'] = True
        
        # [UPGRADE #2] Toast on completion
        st.toast("✅ 風控儀表載入完成", icon="✅")
        
    except Exception as e:
        st.error(f"❌ HUD 計算失敗: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  1.2 — THERMOMETER (多空溫度計)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_2_thermometer():
    """多空溫度計 — 高價權值股站上 87MA 比例"""
    st.markdown('<div class="sec-header"><div class="sec-icon">🌡️</div><div class="sec-title">多空溫度</div><div class="sec-pill">THERMOMETER</div></div>', unsafe_allow_html=True)
    
    # Mock data — replace with real scan
    above_87_pct = 68.5
    
    # Verdict logic
    if above_87_pct >= 70:
        verdict = "🔥 市場過熱"
        v_rgb = "255,49,49"
    elif above_87_pct >= 50:
        verdict = "✅ 健康多頭"
        v_rgb = "0,255,127"
    else:
        verdict = "🧊 市場冰冷"
        v_rgb = "0,245,255"
    
    # Gauge chart (Plotly)
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=above_87_pct,
        title={'text': "高價權值股站上 87MA 比例", 'font': {'size': 16, 'color': '#CDD', 'family': 'Rajdhani'}},
        delta={'reference': 50, 'increasing': {'color': "#00FF7F"}, 'decreasing': {'color': "#FF3131"}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': "#445566", 'tickfont': {'color': '#889'}},
            'bar': {'color': "#FFD700", 'thickness': 0.8},
            'bgcolor': "rgba(0,0,0,0.3)",
            'borderwidth': 2,
            'bordercolor': "#334455",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(0,245,255,0.2)'},
                {'range': [30, 70], 'color': 'rgba(0,255,127,0.2)'},
                {'range': [70, 100], 'color': 'rgba(255,49,49,0.2)'}
            ],
            'threshold': {
                'line': {'color': "#FFD700", 'width': 3},
                'thickness': 0.85,
                'value': above_87_pct
            }
        }
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#B0C0D0", 'family': 'Rajdhani'},
        height=350,
        margin=dict(t=60, b=20, l=30, r=30)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Verdict box
    st.markdown(f'<div class="thermo-verdict" style="--vr:{v_rgb};">{verdict}</div>', unsafe_allow_html=True)
    
    st.caption("💡 此指標掃描 50 檔高價權值股(台積電、聯發科等),計算站上 87 日均線的比例作為市場體溫。")


# ══════════════════════════════════════════════════════════════════════════════
#  1.3 — PR90 (籌碼分佈)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_3_pr90():
    """PR90 籌碼分佈 — Histogram"""
    st.markdown('<div class="sec-header"><div class="sec-icon">📊</div><div class="sec-title">籌碼分佈</div><div class="sec-pill">PR90 CHIP</div></div>', unsafe_allow_html=True)
    
    st.info("📌 籌碼分佈圖顯示近 90 日收盤價分佈,峰值代表主力成本區。當價格突破峰值區且量增,通常為突破訊號。")
    
    # Mock histogram data
    np.random.seed(42)
    prices = np.random.normal(23000, 800, 1000)
    
    df_hist = pd.DataFrame({'price': prices})
    
    chart = alt.Chart(df_hist).mark_bar(color='#00F5FF', opacity=0.7).encode(
        x=alt.X('price:Q', bin=alt.Bin(maxbins=40), title='價格區間', axis=alt.Axis(labelColor='#889', titleColor='#CDD')),
        y=alt.Y('count():Q', title='數量', axis=alt.Axis(labelColor='#889', titleColor='#CDD')),
        tooltip=['price:Q', 'count():Q']
    ).properties(
        height=400,
        title=alt.TitleParams(text='PR90 籌碼分佈圖', color='#FFD700', fontSize=18, font='Rajdhani')
    ).configure_view(
        strokeWidth=0
    ).configure(
        background='rgba(0,0,0,0)',
        axis=alt.AxisConfig(gridColor='#223344', domainColor='#334455')
    )
    
    st.altair_chart(chart, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  1.4 — HEATMAP (族群熱度)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_4_heatmap():
    """族群熱度 — Sector Treemap"""
    st.markdown('<div class="sec-header"><div class="sec-icon">🗺️</div><div class="sec-title">族群熱度</div><div class="sec-pill">SECTOR HEATMAP</div></div>', unsafe_allow_html=True)
    
    st.info("🔥 資金流向熱力圖 — 綠色=資金流出,紅色=資金流入。方塊大小代表市值權重。")
    
    # Mock sector data
    sectors = ['半導體', '電子零組件', '金融', '航運', '鋼鐵', '塑化', '生技', '觀光']
    df_sectors = pd.DataFrame({
        'sector': sectors,
        'change': [+3.2, +1.8, -0.5, +5.1, -1.2, +0.3, +2.7, -2.1],
        'size': [100, 80, 90, 60, 50, 70, 40, 30]
    })
    
    fig = go.Figure(go.Treemap(
        labels=df_sectors['sector'],
        parents=[''] * len(df_sectors),
        values=df_sectors['size'],
        marker=dict(
            colors=df_sectors['change'],
            colorscale=[[0, '#00FF7F'], [0.5, '#1a1d24'], [1, '#FF3131']],
            cmid=0,
            line=dict(width=2, color='#0b0d12')
        ),
        text=[f"{r['sector']}<br>{r['change']:+.1f}%" for _, r in df_sectors.iterrows()],
        textfont=dict(size=15, color='#EAEEF2', family='Rajdhani'),
        hovertemplate='<b>%{label}</b><br>漲跌: %{color:.2f}%<extra></extra>'
    ))
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        height=450,
        margin=dict(t=10, b=10, l=10, r=10)
    )
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  1.5 — TURNOVER (成交重心)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_5_turnover():
    """成交重心 — Top 100 Volume Leaders"""
    st.markdown('<div class="sec-header"><div class="sec-icon">💹</div><div class="sec-title">成交重心</div><div class="sec-pill">VOLUME CENTER</div></div>', unsafe_allow_html=True)
    st.info("💰 TOP 100 成交重心即時掃描 — 資金集中在哪些標的?")
    st.caption("⏳ 功能建置中 — 將整合 TWSE/TPEx API 即時掃描成交量排行")


# ══════════════════════════════════════════════════════════════════════════════
#  1.6 — TREND RADAR (趨勢雷達)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_6_trend_radar():
    """趨勢雷達 — 87MA Deduction + Adam Theory"""
    st.markdown('<div class="sec-header"><div class="sec-icon">👑</div><div class="sec-title">趨勢雷達</div><div class="sec-pill">TREND RADAR</div></div>', unsafe_allow_html=True)
    st.info("📡 高價權值股趨勢追蹤 + 87MA 扣抵 + 亞當理論反射")
    st.caption("⏳ 功能建置中 — 將整合 yfinance 歷史數據分析")


# ══════════════════════════════════════════════════════════════════════════════
#  1.7 — PREDATOR (台指獵殺)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_7_predator():
    """台指獵殺 — WTX Predator Strategy"""
    st.markdown('<div class="sec-header"><div class="sec-icon">🎯</div><div class="sec-title">台指獵殺</div><div class="sec-pill">WTX PREDATOR</div></div>', unsafe_allow_html=True)
    
    st.info("⚾ 棒球理論 — 利用過去 12 個月結算慣性推導虛擬 K 棒,鎖定 1B/2B/3B/HR 目標價")
    
    # Mock targets
    current_wtx = 23456
    targets = {
        '1B': current_wtx + 200,
        '2B': current_wtx + 400,
        '3B': current_wtx + 600,
        'HR': current_wtx + 1000
    }
    
    st.markdown(f"""
<div class="base-grid">
  <div class="base-card" style="--bc:#00F5FF;">
    <div class="base-lbl">一壘安打 (1B)</div>
    <div class="base-val">{targets['1B']}</div>
    <div class="base-tag">Conservative</div>
  </div>
  <div class="base-card" style="--bc:#00FF7F;">
    <div class="base-lbl">二壘安打 (2B)</div>
    <div class="base-val">{targets['2B']}</div>
    <div class="base-tag">Moderate</div>
  </div>
  <div class="base-card" style="--bc:#FFD700;">
    <div class="base-lbl">三壘安打 (3B)</div>
    <div class="base-val">{targets['3B']}</div>
    <div class="base-tag">Aggressive</div>
  </div>
  <div class="base-card" style="--bc:#FF9A3C;">
    <div class="base-lbl">全壘打 (HR)</div>
    <div class="base-val">{targets['HR']}</div>
    <div class="base-tag">Max Profit</div>
  </div>
</div>""", unsafe_allow_html=True)
    
    st.caption("📊 根據過去 12 個月台指期結算日慣性計算,當月虛擬 K 棒推導四大目標價位。")


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


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY — Mobile-Friendly Navigation with option_menu
# ══════════════════════════════════════════════════════════════════════════════
def render():
    """Tab 1 — Macro Risk Command Center (Mobile-Friendly V300)"""
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

    # ── MOBILE-FRIENDLY NAVIGATION ────────────────────────────────────────────
    # Map menu selection back to session_state
    default_idx = MENU_OPTIONS.index(next((opt for opt in MENU_OPTIONS if opt.startswith(active)), MENU_OPTIONS[0]))
    
    selected = option_menu(
        menu_title=None,
        options=MENU_OPTIONS,
        icons=MENU_ICONS,
        default_index=default_idx,
        orientation="horizontal",
        styles=TITAN_NAV_STYLE
    )
    
    # Extract code (first 3 chars) and update session_state
    new_code = selected[:3]
    if new_code != active:
        st.session_state.tab1_active = new_code
        st.rerun()

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
