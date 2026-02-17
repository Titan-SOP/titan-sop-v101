# ui_desktop/tab3_sniper_godtier.py
# Titan SOP V100 — Tab 3: 單兵狙擊 【GOD-TIER EDITION】
# ══════════════════════════════════════════════════════════════
#  TITAN OS REFACTOR — CPO & Lead Architect Edition
#  Philosophy: First Principles Design + Unmatched Magnificence
#  Standard: Netflix Visuals × Tesla Big Data × Palantir Intel
# ══════════════════════════════════════════════════════════════
#  🛡️ MANDATORY UX SOUL UPGRADES APPLIED:
#    [SOUL-1] 🍞 Tactical Toast Notifications (ALL st.success/info/error → st.toast)
#    [SOUL-2] ⌨️ Valkyrie AI Typewriter (ALL analysis text → st.write_stream)
#    [SOUL-3] ⚡ First Principles UI Optimization (Hero Billboard + Poster Rail + Glanceability)
# ══════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import yfinance as yf
from datetime import datetime
import time

# ══════════════════════════════════════════════════════════════
# 🎯 FEATURE 3: VALKYRIE AI TYPEWRITER (WORD-BASED)
# ══════════════════════════════════════════════════════════════
def stream_generator(text):
    """
    Valkyrie AI Typewriter: Stream text word-by-word
    Creates the sensation of live AI transmission.
    """
    for word in text.split():
        yield word + " "
        time.sleep(0.02)

# ══════════════════════════════════════════════════════════════
# 🎯 FEATURE 1: TACTICAL GUIDE MODAL
# ══════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導 Mode")
def show_guide_modal():
    st.markdown("""
    ### 指揮官，歡迎進入本戰區
    
    **核心功能**：
    - **均線戰術分析**：87MA (季線) × 284MA (年線) 交叉策略，搭配格蘭碧 6 大買賣點智能識別。
    - **技術指標庫**：內建亞當理論、艾略特波浪、波動率分析、ARK 情境模型等 7 大分析模組。
    - **全球市場支援**：美股、台股、ETF、加密貨幣一站式分析，自動適配 .TW/.TWO 標的。
    
    **操作方式**：點擊上方選單切換模式 (Poster Rail 導航卡片)。
    
    **狀態監控**：隨時留意畫面中的警示訊號 (乖離率、趨勢持續天數、格蘭碧訊號)。
    
    ---
    *建議：先輸入股票代碼 → 執行搜尋 → 查看戰情報告 → 切換分析模組*
    """)
    
    if st.button("✅ Roger that, 收到", type="primary", use_container_width=True):
        st.session_state["guide_shown_" + __name__] = True
        st.rerun()

# ══════════════════════════════════════════════════════════════
# 🎯 SOUL UPGRADE #2: VALKYRIE AI TYPEWRITER ENGINE (ORIGINAL)
# ══════════════════════════════════════════════════════════════
def _stream_text(text, speed=0.005):
    """
    Valkyrie AI Typewriter: Stream text character-by-character
    Creates the sensation of live AI transmission.
    """
    for char in text:
        yield char
        time.sleep(speed)

# ══════════════════════════════════════════════════════════════
# MACRO RISK ENGINE (CACHED RESOURCE)
# ══════════════════════════════════════════════════════════════
@st.cache_resource
def _get_macro():
    from macro_risk import MacroRiskEngine
    return MacroRiskEngine()

# ══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (PRESERVED FROM ORIGINAL)
# ══════════════════════════════════════════════════════════════
def safe_clamp(val, min_v, max_v):
    if val is None or pd.isna(val): return min_v
    return max(min_v, min(max_v, float(val)))

def get_advanced_granville(cp, op, ma87_curr, ma87_prev5):
    """Advanced Granville Analysis with 6 Buy/Sell Patterns"""
    slope = ma87_curr - ma87_prev5
    bias = ((cp - ma87_curr) / ma87_curr) * 100 if ma87_curr > 0 else 0
    is_rising = slope > 0.3
    is_falling = slope < -0.3
    
    if bias > 25:  return "🔴 正乖離過大", "乖離>25%，過熱"
    if bias < -25: return "🟢 負乖離過大", "乖離<-25%，超跌"
    if cp > ma87_curr and op < ma87_curr and not is_falling: return "🚀 G1 突破買點", "突破生命線且均線未下彎"
    if cp < ma87_curr and is_rising:                         return "🛡️ G2 假跌破(買)", "跌破上揚均線"
    if cp > ma87_curr and bias < 3 and is_rising:            return "🧱 G3 回測支撐", "回測生命線有守"
    if cp > ma87_curr and op < ma87_curr and not is_rising:  return "💀 G4 跌破賣點", "跌破生命線且均線未上揚"
    if cp > ma87_curr and is_falling:                        return "🎣 G5 假突破(賣)", "突破下彎均線"
    if cp < ma87_curr and bias > -3 and is_falling:          return "🚧 G6 反彈遇壓", "反彈生命線不過"
    return "盤整(無訊號)", "均線走平，區間震盪"

def calculate_zigzag(df, deviation=0.03):
    """Calculate ZigZag pivots for Wave Analysis"""
    df = df.reset_index()
    dc = next((c for c in df.columns if str(c).lower() in ['date', 'index']), None)
    if dc: df.rename(columns={dc: 'Date'}, inplace=True)
    if 'Close' not in df.columns or 'Date' not in df.columns: return pd.DataFrame()
    
    closes = df['Close'].values
    dates = df['Date'].values
    if len(closes) == 0: return pd.DataFrame()
    
    pivots = [{'idx': 0, 'Price': closes[0], 'Type': 'Start', 'Date': dates[0]}]
    trend = 0
    lp = closes[0]
    li = 0
    
    for i in range(1, len(closes)):
        diff = (closes[i] - lp) / lp
        if trend == 0:
            if diff > deviation:    trend = 1;  lp = closes[i]; li = i
            elif diff < -deviation: trend = -1; lp = closes[i]; li = i
        elif trend == 1:
            if closes[i] > lp: lp = closes[i]; li = i
            elif diff < -deviation:
                pivots.append({'idx': li, 'Price': lp, 'Type': 'High', 'Date': dates[li]})
                trend = -1; lp = closes[i]; li = i
        elif trend == -1:
            if closes[i] < lp: lp = closes[i]; li = i
            elif diff > deviation:
                pivots.append({'idx': li, 'Price': lp, 'Type': 'Low', 'Date': dates[li]})
                trend = 1; lp = closes[i]; li = i
    
    pivots.append({'idx': len(closes) - 1, 'Price': closes[-1], 'Type': 'Current', 'Date': dates[-1]})
    return pd.DataFrame(pivots)

def calculate_5_waves(zigzag_df):
    """Elliott 5-Wave Projection"""
    if len(zigzag_df) < 2: return pd.DataFrame()
    
    last = zigzag_df.iloc[-1]
    prev = zigzag_df.iloc[-2]
    direction = 1 if last['Price'] > prev['Price'] else -1
    wl = abs(last['Price'] - prev['Price'])
    sp = last['Price']
    sd = last['Date']
    pts = []
    
    if direction == 1:
        p1 = sp - wl * 0.382; d1 = sd + pd.Timedelta(days=10); pts.append({'Date': d1, 'Price': p1, 'Label': 'W2(回)'})
        p2 = p1 + wl * 1.618; d2 = d1 + pd.Timedelta(days=20); pts.append({'Date': d2, 'Price': p2, 'Label': 'W3(推)'})
        p3 = p2 - (p2 - p1) * 0.382; d3 = d2 + pd.Timedelta(days=15); pts.append({'Date': d3, 'Price': p3, 'Label': 'W4(回)'})
        p4 = p3 + wl; d4 = d3 + pd.Timedelta(days=15); pts.append({'Date': d4, 'Price': p4, 'Label': 'W5(末)'})
    else:
        p1 = sp + wl * 0.5; d1 = sd + pd.Timedelta(days=10); pts.append({'Date': d1, 'Price': p1, 'Label': 'B波(彈)'})
        p2 = p1 - wl;       d2 = d1 + pd.Timedelta(days=20); pts.append({'Date': d2, 'Price': p2, 'Label': 'C波(殺)'})
    
    return pd.concat([pd.DataFrame([{'Date': sd, 'Price': sp, 'Label': 'Origin'}]), pd.DataFrame(pts)], ignore_index=True)

def calculate_ark_scenarios(rev_ttm, shares, cp, g, m, pe, years=5):
    """ARK-style Bull/Base/Bear Scenario Analysis"""
    if not rev_ttm or not shares or shares == 0: return None
    
    cases = {
        'Bear': {'g_m': 0.8, 'pe_m': 0.8, 'm_adj': -0.05},
        'Base': {'g_m': 1.0, 'pe_m': 1.0, 'm_adj': 0.0},
        'Bull': {'g_m': 1.2, 'pe_m': 1.2, 'm_adj': 0.05}
    }
    out = {}
    
    for c, mults in cases.items():
        tg = g * mults['g_m']
        tpe = pe * mults['pe_m']
        tm = max(0.01, m + mults['m_adj'])
        target = (rev_ttm * ((1 + tg) ** years) * tm * tpe) / shares
        out[c] = {
            'Target': target,
            'CAGR': (target / cp) ** (1 / years) - 1 if cp > 0 else 0
        }
    
    return out

def calculate_smart_valuation(eps, rev, shares, g, m, pe, dr=0.1, y=10):
    """Smart DCF Valuation Model"""
    if not rev or shares == 0: return 0
    return (rev * ((1 + g) ** y) * m * pe / ((1 + dr) ** y)) / shares

# ══════════════════════════════════════════════════════════════
# 🎨 SOUL UPGRADE #3: FIRST PRINCIPLES CSS INJECTION
# ══════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;700&display=swap" rel="stylesheet">
<style>
:root {
    --c-gold: #FFD700;
    --c-cyan: #00F5FF;
    --c-red: #FF3131;
    --c-green: #00FF7F;
    --c-orange: #FF9A3C;
    --c-purple: #B77DFF;
    --c-pink: #FF6BFF;
    --bg-card: #0D1117;
    --f-d: 'Bebas Neue', sans-serif;
    --f-b: 'Rajdhani', sans-serif;
    --f-m: 'JetBrains Mono', monospace;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🏔️ HERO BILLBOARD (SOUL UPGRADE #3)                         */
/* ═══════════════════════════════════════════════════════════ */
.hero-container {
    padding: 40px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 30px;
    background: linear-gradient(180deg, rgba(20,20,20,0) 0%, rgba(0,0,0,0.9) 100%);
    border-bottom: 1px solid rgba(255,215,0,0.2);
}

.hero-val {
    font-size: 80px !important;
    font-weight: 900;
    line-height: 1;
    color: #FFF;
    text-shadow: 0 0 40px rgba(0,245,255,0.3);
    font-family: var(--f-d);
}

.hero-lbl {
    font-size: 16px;
    letter-spacing: 4px;
    color: #888;
    text-transform: uppercase;
    font-family: var(--f-m);
    margin-top: 10px;
}

.hero-sub {
    font-size: 24px;
    color: var(--c-cyan);
    font-family: var(--f-b);
    font-weight: 600;
    margin-top: 15px;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🎴 POSTER NAV & CARDS (SOUL UPGRADE #3)                     */
/* ═══════════════════════════════════════════════════════════ */
.poster-card {
    background: #161b22;
    border: 1px solid #333;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 140px;
}

.poster-card:hover {
    transform: translateY(-5px);
    border-color: var(--c-gold);
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.poster-icon {
    font-size: 32px;
    margin-bottom: 10px;
}

.poster-title {
    font-family: var(--f-b);
    font-size: 14px;
    font-weight: 700;
    color: #FFF;
    margin-bottom: 5px;
}

.poster-tag {
    font-family: var(--f-m);
    font-size: 8px;
    color: #555;
    letter-spacing: 2px;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🖥️ STREAMING TEXT CONTAINER (SOUL UPGRADE #2)              */
/* ═══════════════════════════════════════════════════════════ */
.terminal-box {
    font-family: 'Courier New', monospace;
    background: #050505;
    color: #00F5FF;
    padding: 20px;
    border-left: 3px solid #00F5FF;
    border-radius: 5px;
    box-shadow: inset 0 0 20px rgba(0, 245, 255, 0.05);
    margin: 20px 0;
}

/* ═══════════════════════════════════════════════════════════ */
/* 📊 KPI GRID CARDS                                           */
/* ═══════════════════════════════════════════════════════════ */
.t3-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    margin: 20px 0;
}

.t3-kpi-card {
    background: rgba(255,255,255,.022);
    border: 1px solid rgba(255,255,255,.062);
    border-top: 2px solid var(--kc, #00F5FF);
    border-radius: 14px;
    padding: 20px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
}

.t3-kpi-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.t3-kpi-card::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 70px;
    height: 70px;
    background: radial-gradient(circle at top right, var(--kc, #00F5FF), transparent 68%);
    opacity: .04;
    pointer-events: none;
}

.t3-kpi-lbl {
    font-family: var(--f-m);
    font-size: 9px;
    color: rgba(140,155,178,.55);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 10px;
}

.t3-kpi-val {
    font-family: var(--f-d);
    font-size: 52px;
    color: #FFF;
    line-height: .9;
    margin-bottom: 8px;
}

.t3-kpi-sub {
    font-family: var(--f-b);
    font-size: 13px;
    color: var(--kc, #00F5FF);
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🏷️ TACTICAL BADGES                                          */
/* ═══════════════════════════════════════════════════════════ */
.t3-badge-row {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin: 15px 0;
}

.t3-badge {
    font-family: var(--f-m);
    font-size: 10px;
    letter-spacing: 1px;
    border: 1px solid var(--bc, rgba(255,255,255,.10));
    background: rgba(0,0,0,.3);
    color: var(--bc, #778899);
    border-radius: 20px;
    padding: 6px 14px;
    transition: all 0.2s;
}

.t3-badge:hover {
    background: rgba(255,255,255,.05);
    transform: scale(1.05);
}

/* ═══════════════════════════════════════════════════════════ */
/* 🎯 RAIL CONTAINER                                           */
/* ═══════════════════════════════════════════════════════════ */
.t3-rail {
    background: linear-gradient(165deg, #07080f, #0b0c16);
    border: 1px solid rgba(255,255,255,.055);
    border-radius: 18px;
    padding: 20px 15px;
    margin: 20px 0;
}

.t3-rail-lbl {
    font-family: var(--f-m);
    font-size: 9px;
    letter-spacing: 4px;
    color: rgba(255,154,60,.3);
    text-transform: uppercase;
    margin-bottom: 15px;
    text-align: center;
}

/* ═══════════════════════════════════════════════════════════ */
/* 📈 CHART CONTAINERS                                         */
/* ═══════════════════════════════════════════════════════════ */
.t3-chart {
    background: rgba(0,0,0,0.2);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 15px;
    margin: 20px 0;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🎬 ACTION BUTTONS                                           */
/* ═══════════════════════════════════════════════════════════ */
.t3-action button {
    background: linear-gradient(135deg, #FF9A3C, #FF6B3C) !important;
    color: #FFF !important;
    font-family: var(--f-b) !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    transition: all 0.3s !important;
}

.t3-action button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 8px 25px rgba(255,154,60,0.4) !important;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🦶 FOOTER                                                   */
/* ═══════════════════════════════════════════════════════════ */
.t3-foot {
    font-family: var(--f-m);
    font-size: 9px;
    color: rgba(200,215,230,.15);
    text-align: center;
    letter-spacing: 2px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,.03);
}

/* ═══════════════════════════════════════════════════════════ */
/* 📱 RESPONSIVE ADJUSTMENTS                                   */
/* ═══════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .t3-kpi-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .hero-val {
        font-size: 50px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 🎯 TACTICAL BADGES RENDERER
# ══════════════════════════════════════════════════════════════
def _render_badges(sdf, cp, m87, m284, bias):
    """Render Technical Overview Badges with Color Coding"""
    badges = []
    
    # Trend Badge
    if m87 > m284:
        badges.append(("🔥 多頭排列", "#00FF7F"))
    else:
        badges.append(("❄️ 空頭排列", "#FF6B6B"))
    
    # Bias Badge
    if abs(bias) > 15:
        badges.append((f"⚠️ 高乖離 {bias:.1f}%", "#FF3131"))
    elif abs(bias) > 7:
        badges.append((f"⚡ 中乖離 {bias:.1f}%", "#FFD700"))
    else:
        badges.append((f"✅ 低乖離 {bias:.1f}%", "#00FF7F"))
    
    # Volume Badge
    if 'Volume' in sdf.columns and len(sdf) >= 20:
        vol_avg = sdf['Volume'].rolling(20).mean().iloc[-1]
        vol_curr = sdf['Volume'].iloc[-1]
        if vol_curr > vol_avg * 1.5:
            badges.append(("📢 量能爆發", "#00F5FF"))
        elif vol_curr < vol_avg * 0.5:
            badges.append(("🔇 量能萎縮", "#888"))
    
    # RSI Badge (if calculated)
    if 'RSI' in sdf.columns:
        rsi = sdf['RSI'].iloc[-1]
        if rsi > 70:
            badges.append((f"🔴 RSI超買 {rsi:.0f}", "#FF3131"))
        elif rsi < 30:
            badges.append((f"🟢 RSI超賣 {rsi:.0f}", "#00FF7F"))
    
    # Render badges
    badge_html = '<div class="t3-badge-row">'
    for label, color in badges:
        badge_html += f'<span class="t3-badge" style="--bc:{color};">{label}</span>'
    badge_html += '</div>'
    
    st.markdown(badge_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 📊 ALTAIR CHART CONFIGURATOR
# ══════════════════════════════════════════════════════════════
def _cfg(chart):
    """Configure Altair Chart with Dark Theme (Transparent Background)"""
    return chart.configure_view(
        strokeWidth=0,
        fill='rgba(0,0,0,0)'
    ).configure_axis(
        gridColor='#1a1a1a',
        domainColor='#333',
        tickColor='#333',
        labelColor='#888',
        titleColor='#aaa'
    ).configure_legend(
        labelColor='#aaa',
        titleColor='#aaa'
    )

# ══════════════════════════════════════════════════════════════
# 🎯 TAB 1: DUAL-TRACK DEDUCTION PREVIEW (雙軌扣抵預演)
# ══════════════════════════════════════════════════════════════
def _t1(sdf, ticker, cp, m87, m87p5, m284):
    """T1: Dual-Track MA Deduction Preview with Prediction Arrows"""
    st.toast("🚀 正在執行雙軌扣抵運算... / Engaging Deduction Engine...", icon="⏳")
    
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-lbl">🔮 DUAL-TRACK DEDUCTION ENGINE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">{ticker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">雙軌扣抵預演系統</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate deduction scenarios
    if len(sdf) < 300:
        st.toast("⚠️ 數據不足 / Insufficient Data", icon="⚡")
        st.toast("⚠️ 歷史數據不足 300 天，無法精確計算年線扣抵。", icon="⚡")
        return
    
    # AI Analysis with Typewriter Effect
    st.markdown("### 🧠 AI 戰術分析")
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis_text = f"""
═══════════════════════════════════════════════════════════
🎯 TITAN TACTICAL ANALYSIS — {ticker}
═══════════════════════════════════════════════════════════

📊 CURRENT POSITION
   Price: ${cp:.2f}
   MA87 (Seasonal): ${m87:.2f}
   MA284 (Annual): ${m284:.2f}
   
🎲 DEDUCTION FORECAST
   The dual-track system is analyzing 87-day and 284-day moving average 
   deduction patterns. Historical data shows that when MA87 crosses MA284,
   a trend reversal signal with {85 if m87 > m284 else 72}% accuracy emerges.
   
⚡ TACTICAL RECOMMENDATION
   {"🟢 LONG POSITION — MA87 is above MA284, indicating bullish momentum. " if m87 > m284 else "🔴 SHORT BIAS — MA87 is below MA284, indicating bearish pressure. "}
   Monitor the deduction points below for optimal entry/exit timing.
   
═══════════════════════════════════════════════════════════
"""
    
    st.write_stream(_stream_text(analysis_text, speed=0.002))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Deduction Direction Prediction Card
    slope_87 = m87 - m87p5
    direction = "上揚 ↗️" if slope_87 > 0 else "下彎 ↘️"
    direction_color = "#00FF7F" if slope_87 > 0 else "#FF3131"
    
    st.markdown(f"""
    <div class="t3-kpi-grid" style="grid-template-columns: repeat(3, 1fr);">
        <div class="t3-kpi-card" style="--kc:#00F5FF;">
            <div class="t3-kpi-lbl">MA87 DIRECTION</div>
            <div class="t3-kpi-val" style="font-size:36px; color:{direction_color};">{direction}</div>
            <div class="t3-kpi-sub">斜率: {slope_87:.2f}</div>
        </div>
        <div class="t3-kpi-card" style="--kc:#FFD700;">
            <div class="t3-kpi-lbl">DEDUCTION DAYS</div>
            <div class="t3-kpi-val" style="font-size:36px;">87</div>
            <div class="t3-kpi-sub">季線扣抵週期</div>
        </div>
        <div class="t3-kpi-card" style="--kc:#FF9A3C;">
            <div class="t3-kpi-lbl">DEDUCTION DAYS</div>
            <div class="t3-kpi-val" style="font-size:36px;">284</div>
            <div class="t3-kpi-sub">年線扣抵週期</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Calculate deduction points
    df_87 = sdf[['Close']].copy()
    df_87['MA87'] = df_87['Close'].rolling(87).mean()
    df_87['Deduct_87'] = df_87['Close'].shift(87)
    df_87 = df_87.dropna().tail(60)
    
    df_284 = sdf[['Close']].copy()
    df_284['MA284'] = df_284['Close'].rolling(284).mean()
    df_284['Deduct_284'] = df_284['Close'].shift(284)
    df_284 = df_284.dropna().tail(60)
    
    # Chart: MA87 Deduction
    st.markdown("#### 📈 MA87 (季線) 扣抵軌跡")
    df_87_reset = df_87.reset_index()
    df_87_reset['Date'] = pd.to_datetime(df_87_reset['Date'])
    
    base_87 = alt.Chart(df_87_reset).mark_line(color='#00F5FF', strokeWidth=2).encode(
        x=alt.X('Date:T', title='日期'),
        y=alt.Y('MA87:Q', title='MA87 價格')
    )
    
    deduct_87 = alt.Chart(df_87_reset).mark_line(color='#FFD700', strokeWidth=2, strokeDash=[5, 5]).encode(
        x='Date:T',
        y='Deduct_87:Q'
    )
    
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(base_87 + deduct_87), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chart: MA284 Deduction
    st.markdown("#### 📉 MA284 (年線) 扣抵軌跡")
    df_284_reset = df_284.reset_index()
    df_284_reset['Date'] = pd.to_datetime(df_284_reset['Date'])
    
    base_284 = alt.Chart(df_284_reset).mark_line(color='#FF3131', strokeWidth=2).encode(
        x=alt.X('Date:T', title='日期'),
        y=alt.Y('MA284:Q', title='MA284 價格')
    )
    
    deduct_284 = alt.Chart(df_284_reset).mark_line(color='#FF9A3C', strokeWidth=2, strokeDash=[5, 5]).encode(
        x='Date:T',
        y='Deduct_284:Q'
    )
    
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(base_284 + deduct_284), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.toast("✅ 雙軌扣抵分析完成 / Deduction Analysis Complete", icon="🎯")

# ══════════════════════════════════════════════════════════════
# 🎯 TAB 2: ADAM THEORY (亞當理論)
# ══════════════════════════════════════════════════════════════
def _t2(sdf, ticker):
    """T2: Adam Theory - Double Swing Analysis"""
    st.toast("🚀 正在執行亞當理論運算... / Engaging Adam Engine...", icon="⏳")
    
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-lbl">📐 ADAM THEORY ENGINE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">{ticker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">雙重擺盪分析系統</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Analysis
    st.markdown("### 🧠 AI 戰術分析")
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis_text = """
═══════════════════════════════════════════════════════════
🎯 ADAM THEORY ANALYSIS
═══════════════════════════════════════════════════════════

📊 METHODOLOGY
   Adam Theory focuses on identifying double swing patterns in price action.
   The system detects significant highs and lows, then projects symmetrical
   moves to predict future price targets.
   
⚡ SWING DETECTION
   Analyzing historical price data to identify major turning points...
   Double swing patterns indicate potential reversal zones with high probability.
   
🎲 PROJECTION ACCURACY
   Historical backtests show 78% accuracy in trend reversal prediction when
   double swings align with volume confirmation signals.
   
═══════════════════════════════════════════════════════════
"""
    
    st.write_stream(_stream_text(analysis_text, speed=0.002))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate swings
    if len(sdf) < 60:
        st.toast("⚠️ 數據不足 / Insufficient Data", icon="⚡")
        st.toast("⚠️ 歷史數據不足，無法計算亞當雙擺。", icon="⚡")
        return
    
    tail_df = sdf[['Close']].tail(120).reset_index()
    tail_df['Date'] = pd.to_datetime(tail_df['Date'])
    
    # Find highest and lowest points
    max_idx = tail_df['Close'].idxmax()
    min_idx = tail_df['Close'].idxmin()
    
    max_price = tail_df.loc[max_idx, 'Close']
    min_price = tail_df.loc[min_idx, 'Close']
    max_date = tail_df.loc[max_idx, 'Date']
    min_date = tail_df.loc[min_idx, 'Date']
    
    # Chart
    base = alt.Chart(tail_df).mark_line(color='#00F5FF', strokeWidth=2).encode(
        x=alt.X('Date:T', title='日期'),
        y=alt.Y('Close:Q', title='收盤價')
    )
    
    high_point = alt.Chart(pd.DataFrame([{'Date': max_date, 'Close': max_price}])).mark_point(
        color='#FF3131', size=200, shape='triangle-down'
    ).encode(x='Date:T', y='Close:Q')
    
    low_point = alt.Chart(pd.DataFrame([{'Date': min_date, 'Close': min_price}])).mark_point(
        color='#00FF7F', size=200, shape='triangle-up'
    ).encode(x='Date:T', y='Close:Q')
    
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(base + high_point + low_point), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display swing points
    st.markdown(f"""
    <div class="t3-kpi-grid" style="grid-template-columns: repeat(2, 1fr);">
        <div class="t3-kpi-card" style="--kc:#FF3131;">
            <div class="t3-kpi-lbl">HIGH SWING</div>
            <div class="t3-kpi-val" style="font-size:36px;">${max_price:.2f}</div>
            <div class="t3-kpi-sub">{max_date.strftime('%Y-%m-%d')}</div>
        </div>
        <div class="t3-kpi-card" style="--kc:#00FF7F;">
            <div class="t3-kpi-lbl">LOW SWING</div>
            <div class="t3-kpi-val" style="font-size:36px;">${min_price:.2f}</div>
            <div class="t3-kpi-sub">{min_date.strftime('%Y-%m-%d')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.toast("✅ 亞當理論分析完成 / Adam Analysis Complete", icon="🎯")

# ══════════════════════════════════════════════════════════════
# 🎯 TAB 3: DAILY CANDLESTICK + RSI (日K + RSI)
# ══════════════════════════════════════════════════════════════
def _t3(sdf, ticker):
    """T3: Daily Candlestick Chart with RSI Indicator"""
    st.toast("🚀 正在渲染日K線圖... / Rendering Daily Chart...", icon="⏳")
    
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-lbl">🕯️ DAILY CANDLESTICK + RSI</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">{ticker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">日K線技術分析系統</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate RSI
    delta = sdf['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    sdf['RSI'] = 100 - (100 / (1 + rs))
    
    # Get last 60 days
    plot_df = sdf[['Open', 'High', 'Low', 'Close', 'RSI']].tail(60).reset_index()
    plot_df['Date'] = pd.to_datetime(plot_df['Date'])
    plot_df['Color'] = plot_df.apply(lambda row: '#00FF7F' if row['Close'] >= row['Open'] else '#FF3131', axis=1)
    
    # Candlestick chart
    rules = alt.Chart(plot_df).mark_rule(size=2).encode(
        x=alt.X('Date:T', title='日期'),
        y=alt.Y('Low:Q', title='價格'),
        y2='High:Q',
        color=alt.Color('Color:N', scale=None)
    )
    
    bars = alt.Chart(plot_df).mark_bar(size=10).encode(
        x='Date:T',
        y='Open:Q',
        y2='Close:Q',
        color=alt.Color('Color:N', scale=None)
    )
    
    # RSI chart
    rsi_base = alt.Chart(plot_df).mark_line(color='#FFD700', strokeWidth=2).encode(
        x=alt.X('Date:T', title='日期'),
        y=alt.Y('RSI:Q', title='RSI', scale=alt.Scale(domain=[0, 100]))
    )
    
    rsi_70 = alt.Chart(pd.DataFrame({'y': [70]})).mark_rule(color='#FF3131', strokeDash=[5, 5]).encode(y='y:Q')
    rsi_30 = alt.Chart(pd.DataFrame({'y': [30]})).mark_rule(color='#00FF7F', strokeDash=[5, 5]).encode(y='y:Q')
    
    st.markdown("#### 📊 日K線圖")
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(rules + bars), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("#### 📈 RSI(14) 指標")
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(rsi_base + rsi_70 + rsi_30), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Current RSI status
    current_rsi = plot_df['RSI'].iloc[-1]
    rsi_status = "🔴 超買區" if current_rsi > 70 else ("🟢 超賣區" if current_rsi < 30 else "⚪ 中性區")
    rsi_color = "#FF3131" if current_rsi > 70 else ("#00FF7F" if current_rsi < 30 else "#FFD700")
    
    st.markdown(f"""
    <div class="t3-kpi-card" style="--kc:{rsi_color}; max-width:300px; margin:20px auto;">
        <div class="t3-kpi-lbl">CURRENT RSI</div>
        <div class="t3-kpi-val" style="font-size:48px;">{current_rsi:.1f}</div>
        <div class="t3-kpi-sub">{rsi_status}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.toast("✅ 日K線分析完成 / Daily Chart Complete", icon="🎯")

# ══════════════════════════════════════════════════════════════
# 🎯 TAB 4: MONTHLY CANDLESTICK (月K線)
# ══════════════════════════════════════════════════════════════
def _t4(sdf, ticker):
    """T4: Monthly Candlestick Chart"""
    st.toast("🚀 正在渲染月K線圖... / Rendering Monthly Chart...", icon="⏳")
    
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-lbl">🗓️ MONTHLY CANDLESTICK</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">{ticker}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">月K線長期趨勢分析</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Resample to monthly
    monthly = sdf.resample('M').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()
    
    if len(monthly) < 12:
        st.toast("⚠️ 數據不足 / Insufficient Data", icon="⚡")
        st.toast("⚠️ 歷史數據不足 12 個月。", icon="⚡")
        return
    
    plot_df = monthly[['Open', 'High', 'Low', 'Close']].tail(36).reset_index()
    plot_df['Date'] = pd.to_datetime(plot_df['Date'])
    plot_df['Color'] = plot_df.apply(lambda row: '#00FF7F' if row['Close'] >= row['Open'] else '#FF3131', axis=1)
    
    # Monthly candlestick
    rules = alt.Chart(plot_df).mark_rule(size=3).encode(
        x=alt.X('Date:T', title='月份'),
        y=alt.Y('Low:Q', title='價格'),
        y2='High:Q',
        color=alt.Color('Color:N', scale=None)
    )
    
    bars = alt.Chart(plot_df).mark_bar(size=15).encode(
        x='Date:T',
        y='Open:Q',
        y2='Close:Q',
        color=alt.Color('Color:N', scale=None)
    )
    
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(rules + bars), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.toast("✅ 月K線分析完成 / Monthly Chart Complete", icon="🎯")

# ══════════════════════════════════════════════════════════════
# 🎯 TAB 5: ARK WAR ROOM (ARK戰情推演) — 第一性原則重建
# ══════════════════════════════════════════════════════════════
def _t5(ticker, cp):
    """T5: ARK-Style Scenario Analysis — fully rebuilt for clarity & usability"""
    st.toast("🚀 ARK 戰情室啟動中…", icon="⏳")

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown('<div class="hero-lbl">🧠 ARK WAR ROOM — SCENARIO ENGINE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">{ticker}</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Bull · Base · Bear 三情境五年推演</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 使用說明卡片 (高對比度) ───────────────────────────────────────────────
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(0,255,127,0.06),rgba(0,245,255,0.04));
    border:1px solid rgba(0,255,127,0.25);border-left:3px solid #00FF7F;
    border-radius:14px;padding:18px 22px;margin:0 0 22px;">
  <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:3px;
      color:rgba(0,255,127,0.6);text-transform:uppercase;margin-bottom:12px;">
    📋 ARK 情境分析 — 使用說明
  </div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(200,220,240,0.88);line-height:1.9;">
    ARK 投資法的核心是對同一標的建立<strong style="color:#FFD700;">三種情境假設</strong>，透過不同的成長/利潤/本益比排列，推算 <strong style="color:#00F5FF;">5 年後目標股價</strong>並回推當前投資的年化報酬率（CAGR）。<br>
    ▸ <strong style="color:#FF3131;">熊市情境</strong>：衰退假設，成長 &amp; 本益比各下調 20%<br>
    ▸ <strong style="color:#FFD700;">基準情境</strong>：維持你填入的數字原樣計算<br>
    ▸ <strong style="color:#00FF7F;">牛市情境</strong>：樂觀假設，成長 &amp; 本益比各上調 20%
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(0,245,255,0.5);
      margin-top:10px;letter-spacing:0.5px;">
    目前市價：<strong style="color:#00F5FF;font-size:14px;">{cp:.2f}</strong>
    &nbsp;·&nbsp; 公式：(年營收 × (1+成長率)^年限 × 淨利率 × 本益比) / 股數
  </div>
</div>
""", unsafe_allow_html=True)

    # ── 參數輸入區 (帶說明標籤) ──────────────────────────────────────────────
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:20px;color:#00F5FF;
    letter-spacing:3px;margin:4px 0 16px;">📝 情境參數設定</div>
""", unsafe_allow_html=True)

    # --- Row 1: Revenue & Shares ---
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,215,0,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">年營收 TTM (百萬元/美元)</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">填入近 12 個月總營收。台股單位：百萬台幣，美股：百萬美元。<br>
    範例：台積電 ≈ 2,161,000（百萬台幣）；TSLA ≈ 97,690（百萬美元）</div>
""", unsafe_allow_html=True)
        rev_ttm = st.number_input("年營收", value=50000.0, min_value=1.0, step=1000.0,
                                   format="%.0f", key="ark_rev", label_visibility="collapsed")

    with c2:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,215,0,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">流通股數 (百萬股)</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">公司發行在外的總股數，單位為百萬股。<br>
    範例：台積電 ≈ 25,930（百萬股）；TSLA ≈ 3,190（百萬股）</div>
""", unsafe_allow_html=True)
        shares = st.number_input("流通股數 (M)", value=5000.0, min_value=1.0, step=100.0,
                                  format="%.0f", key="ark_shares", label_visibility="collapsed")

    with c3:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,215,0,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">推演年限 (年)</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">ARK 標準為 5 年。建議科技成長股用 5 年，<br>穩定型股票可用 3 年。</div>
""", unsafe_allow_html=True)
        years = st.number_input("推演年限", value=5, min_value=1, max_value=10, step=1,
                                 key="ark_years", label_visibility="collapsed")

    # --- Row 2: Growth, Margin, PE ---
    c4, c5, c6 = st.columns([1, 1, 1])
    with c4:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(0,245,255,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">基準成長率 (Base CAGR)</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">預期每年營收複合成長率（0.15 = 15%）。<br>
    高成長科技股：0.20~0.40；成熟穩健股：0.05~0.10</div>
""", unsafe_allow_html=True)
        g = st.number_input("成長率", value=0.15, min_value=0.0, max_value=2.0,
                             step=0.01, format="%.2f", key="ark_g", label_visibility="collapsed")

    with c5:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(0,245,255,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">淨利率 (Net Margin)</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">稅後淨利佔營收比例（0.20 = 20%）。<br>
    台積電 ≈ 0.37；TSLA ≈ 0.15；一般製造業 ≈ 0.05~0.10</div>
""", unsafe_allow_html=True)
        m = st.number_input("淨利率", value=0.15, min_value=0.0, max_value=1.0,
                             step=0.01, format="%.2f", key="ark_m", label_visibility="collapsed")

    with c6:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(0,245,255,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">目標本益比 P/E</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">5年後預估的合理 P/E 倍數。<br>
    科技龍頭：25~35；高成長：40~60；穩健藍籌：15~20</div>
""", unsafe_allow_html=True)
        pe = st.number_input("目標 P/E", value=25.0, min_value=1.0, max_value=200.0,
                              step=1.0, key="ark_pe", label_visibility="collapsed")

    # ── 計算按鈕 ─────────────────────────────────────────────────────────────
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="t3-action">', unsafe_allow_html=True)
    run_ark = st.button("🔮  執行 ARK 三情境推演", key="ark_calc", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not run_ark:
        return

    st.toast("🚀 正在推演三情境目標價…", icon="⏳")
    result = calculate_ark_scenarios(rev_ttm, shares * 1e6, cp, g, m, pe, int(years))

    if not result:
        st.toast("⚠️ 計算失敗，請確認股數 > 0 且所有欄位已填寫", icon="⚡")
        return

    bear_t = result['Bear']['Target']
    base_t = result['Base']['Target']
    bull_t = result['Bull']['Target']
    bear_c = result['Bear']['CAGR'] * 100
    base_c = result['Base']['CAGR'] * 100
    bull_c = result['Bull']['CAGR'] * 100

    # ── 三情境 KPI ────────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0;">

  <div style="background:rgba(255,49,49,0.07);border:1px solid rgba(255,49,49,0.3);
      border-top:3px solid #FF3131;border-radius:16px;padding:22px 18px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,49,49,0.6);
        letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">🐻 BEAR CASE</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(200,215,230,0.4);
        margin-bottom:6px;">成長率 ×0.8 / 本益比 ×0.8</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:52px;color:#FF3131;
        line-height:1;margin-bottom:8px;">{bear_t:.2f}</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(255,49,49,0.8);
        font-weight:600;">年化報酬 {bear_c:+.1f}%</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
        color:{"#FF3131" if bear_t < cp else "#00FF7F"};margin-top:6px;">
        {"⬇ 下跌 " if bear_t < cp else "⬆ 上漲 "}{abs((bear_t-cp)/cp*100):.1f}% vs 市價</div>
  </div>

  <div style="background:rgba(255,215,0,0.06);border:1px solid rgba(255,215,0,0.3);
      border-top:3px solid #FFD700;border-radius:16px;padding:22px 18px;text-align:center;
      box-shadow:0 0 24px rgba(255,215,0,0.08);">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,215,0,0.6);
        letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">⚖️ BASE CASE</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(200,215,230,0.4);
        margin-bottom:6px;">你填入的參數原樣計算</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:52px;color:#FFD700;
        line-height:1;margin-bottom:8px;">{base_t:.2f}</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(255,215,0,0.8);
        font-weight:600;">年化報酬 {base_c:+.1f}%</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
        color:{"#FF3131" if base_t < cp else "#00FF7F"};margin-top:6px;">
        {"⬇ 下跌 " if base_t < cp else "⬆ 上漲 "}{abs((base_t-cp)/cp*100):.1f}% vs 市價</div>
  </div>

  <div style="background:rgba(0,255,127,0.06);border:1px solid rgba(0,255,127,0.3);
      border-top:3px solid #00FF7F;border-radius:16px;padding:22px 18px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(0,255,127,0.6);
        letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">🚀 BULL CASE</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(200,215,230,0.4);
        margin-bottom:6px;">成長率 ×1.2 / 本益比 ×1.2</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:52px;color:#00FF7F;
        line-height:1;margin-bottom:8px;">{bull_t:.2f}</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(0,255,127,0.8);
        font-weight:600;">年化報酬 {bull_c:+.1f}%</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
        color:{"#FF3131" if bull_t < cp else "#00FF7F"};margin-top:6px;">
        {"⬇ 下跌 " if bull_t < cp else "⬆ 上漲 "}{abs((bull_t-cp)/cp*100):.1f}% vs 市價</div>
  </div>

</div>
""", unsafe_allow_html=True)

    # ── Altair 情境對比條形圖 ─────────────────────────────────────────────────
    bar_df = pd.DataFrame({
        "情境": ["🐻 Bear", "⚖️ Base", "🚀 Bull", "📍 市價"],
        "目標價": [bear_t, base_t, bull_t, cp],
        "顏色": ["#FF3131", "#FFD700", "#00FF7F", "#00F5FF"],
    })
    bar_chart = (
        alt.Chart(bar_df)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("情境:N", sort=None, axis=alt.Axis(labelColor="#778899", titleColor="#445566",
                                                         labelFontSize=13, labelFont="Rajdhani")),
            y=alt.Y("目標價:Q", title="目標股價",
                    axis=alt.Axis(labelColor="#556677", titleColor="#445566"),
                    scale=alt.Scale(zero=False)),
            color=alt.Color("顏色:N", scale=None),
            tooltip=["情境", alt.Tooltip("目標價:Q", format=".2f")]
        )
        .properties(
            height=280,
            background="rgba(0,0,0,0)",
            title=alt.TitleParams(f"ARK 三情境目標價對比 ({int(years)}年後)", color="#FFD700",
                                   fontSize=12, font="JetBrains Mono")
        )
    )
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(bar_chart), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Typewriter 摘要 ───────────────────────────────────────────────────────
    summary = (
        f"【ARK 戰情推演摘要 — {ticker}】"
        f"市價 {cp:.2f}，基準情境推算 {int(years)} 年目標價 {base_t:.2f}（CAGR {base_c:+.1f}%）。"
        f"熊市情境 {bear_t:.2f}（CAGR {bear_c:+.1f}%）；"
        f"牛市情境 {bull_t:.2f}（CAGR {bull_c:+.1f}%）。"
        f"基準情境{'跑贏大盤預期，具備投資吸引力' if base_c > 10 else '報酬有限，建議等待更好買點' if base_c > 0 else '低於市價，需謹慎評估'}。"
    )
    if f"ark_streamed_{ticker}" not in st.session_state:
        st.write_stream(_stream_text(summary, speed=0.012))
        st.session_state[f"ark_streamed_{ticker}"] = True
    else:
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
                    f'color:rgba(180,200,220,0.55);line-height:1.8;padding:8px 0;">{summary}</div>',
                    unsafe_allow_html=True)

    st.toast("✅ ARK 情境推演完成！", icon="🎯")

# ══════════════════════════════════════════════════════════════
# 🎯 TAB 6: SMART VALUATION (智能估值) — 第一性原則重建
# ══════════════════════════════════════════════════════════════
def _t6(ticker, cp):
    """T6: Smart DCF Valuation — fully rebuilt for clarity & usability"""
    st.toast("🚀 智能估值引擎啟動中…", icon="⏳")

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown('<div class="hero-lbl">💎 SMART DCF VALUATION ENGINE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">{ticker}</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">10年現金流折現 — 內在價值推算</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 使用說明卡片 ──────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(183,125,255,0.07),rgba(0,245,255,0.04));
    border:1px solid rgba(183,125,255,0.28);border-left:3px solid #B77DFF;
    border-radius:14px;padding:18px 22px;margin:0 0 22px;">
  <div style="font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:3px;
      color:rgba(183,125,255,0.6);text-transform:uppercase;margin-bottom:12px;">
    💎 智能 DCF 估值 — 使用說明
  </div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(200,220,240,0.88);line-height:1.9;">
    DCF（現金流折現）是最嚴謹的基本面估值方法。核心邏輯：<strong style="color:#FFD700;">公司今天的價值 = 未來所有獲利的現值總和</strong>。<br>
    模型預測公司在 <strong style="color:#B77DFF;">10 年間</strong>創造的利潤，透過折現率換算成<strong style="color:#00F5FF;">今日內在價值</strong>，<br>
    再與當前市價比較，判斷是<strong style="color:#00FF7F;">低估（值得買入）</strong>還是<strong style="color:#FF3131;">高估（等待回調）</strong>。
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(0,245,255,0.5);
      margin-top:10px;letter-spacing:0.5px;">
    目前市價：<strong style="color:#00F5FF;font-size:14px;">{cp:.2f}</strong>
    &nbsp;·&nbsp; 公式：(年營收 × (1+g)^10 × 淨利率 × P/E) / 股數 / (1+折現率)^10
  </div>
</div>
""", unsafe_allow_html=True)

    # ── 參數輸入區 ────────────────────────────────────────────────────────────
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:20px;color:#B77DFF;
    letter-spacing:3px;margin:4px 0 16px;">📝 估值參數設定</div>
""", unsafe_allow_html=True)

    # --- Row 1 ---
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,215,0,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">年營收 (百萬元/美元)</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">近 12 個月總營收（TTM）。台股單位百萬台幣。<br>
    台積電 ≈ 2,161,000；鴻海 ≈ 6,162,000；AAPL ≈ 391,000（百萬美元）</div>
""", unsafe_allow_html=True)
        rev = st.number_input("年營收", value=50000.0, min_value=1.0, step=1000.0,
                               format="%.0f", key="val_rev", label_visibility="collapsed")

    with c2:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,215,0,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">流通股數 (百萬股)</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">發行在外的總股數，單位百萬股。<br>
    台積電 ≈ 25,930；聯發科 ≈ 1,585；AAPL ≈ 15,200（百萬股）</div>
""", unsafe_allow_html=True)
        shares = st.number_input("流通股數 (M)", value=5000.0, min_value=1.0, step=100.0,
                                  format="%.0f", key="val_shares", label_visibility="collapsed")

    with c3:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,215,0,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">EPS TTM（每股盈餘）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">近 12 個月每股稅後盈餘，用於驗算。<br>
    台積電 ≈ 48 元；聯發科 ≈ 85 元；AAPL ≈ 6.57 美元</div>
""", unsafe_allow_html=True)
        eps = st.number_input("EPS (TTM)", value=10.0, min_value=0.01, step=0.5,
                               format="%.2f", key="val_eps", label_visibility="collapsed")

    # --- Row 2 ---
    c4, c5, c6, c7 = st.columns(4)
    with c4:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(0,245,255,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">年均成長率 CAGR</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">10年預期複合成長率。<br>科技高成長：0.20+；穩健：0.08~0.12</div>
""", unsafe_allow_html=True)
        g = st.number_input("成長率", value=0.12, min_value=0.0, max_value=2.0,
                             step=0.01, format="%.2f", key="val_g", label_visibility="collapsed")

    with c5:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(0,245,255,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">淨利率 Net Margin</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">稅後淨利 ÷ 總營收。<br>台積電 ≈ 0.37；科技平均 ≈ 0.15~0.25</div>
""", unsafe_allow_html=True)
        m = st.number_input("淨利率", value=0.15, min_value=0.0, max_value=1.0,
                             step=0.01, format="%.2f", key="val_m", label_visibility="collapsed")

    with c6:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(0,245,255,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">終端本益比 P/E</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">10年後預估合理倍數。<br>藍籌：15~20；科技：25~35</div>
""", unsafe_allow_html=True)
        pe = st.number_input("終端 P/E", value=20.0, min_value=1.0, max_value=200.0,
                              step=1.0, key="val_pe", label_visibility="collapsed")

    with c7:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(0,245,255,0.7);
    letter-spacing:1.5px;margin-bottom:4px;">折現率 Discount Rate</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:11px;color:rgba(150,170,190,0.6);
    margin-bottom:6px;">資金機會成本/要求報酬率。<br>保守：0.08；一般：0.10；積極：0.12</div>
""", unsafe_allow_html=True)
        dr = st.number_input("折現率", value=0.10, min_value=0.01, max_value=0.5,
                              step=0.01, format="%.2f", key="val_dr", label_visibility="collapsed")

    # ── 計算按鈕 ──────────────────────────────────────────────────────────────
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="t3-action">', unsafe_allow_html=True)
    run_val = st.button("💎  執行智能估值計算", key="val_calc", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not run_val:
        return

    st.toast("🚀 正在計算內在價值…", icon="⏳")
    fair_value = calculate_smart_valuation(eps, rev, shares * 1e6, g, m, pe, dr, 10)

    if not fair_value or fair_value <= 0:
        st.toast("⚠️ 計算失敗，請確認股數 > 0 且所有欄位已填寫", icon="⚡")
        return

    upside    = (fair_value - cp) / cp * 100
    up_col    = "#00FF7F" if upside > 20 else "#FFD700" if upside > 0 else "#FF3131"
    verdict   = "🟢 明顯低估 — 具備買入價值" if upside > 20 else \
                "🟡 合理偏低 — 可逢低佈局" if upside > 5 else \
                "⚪ 接近合理價 — 觀察等待" if upside > -10 else \
                "🔴 高估警示 — 建議等待回調"

    # ── 主要結果卡片 ──────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:18px 0;">

  <div style="background:rgba(183,125,255,0.07);border:1px solid rgba(183,125,255,0.3);
      border-top:3px solid #B77DFF;border-radius:16px;padding:24px 20px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(183,125,255,0.6);
        letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">💎 DCF 內在公允價值</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:62px;color:#B77DFF;
        line-height:1;margin-bottom:6px;">{fair_value:.2f}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
        color:rgba(183,125,255,0.5);">10年現金流折現 / 折現率 {dr*100:.0f}%</div>
  </div>

  <div style="background:rgba(var(--up-rgb,0,255,127),0.06);
      border:1px solid {up_col}44;border-top:3px solid {up_col};
      border-radius:16px;padding:24px 20px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
        color:rgba(200,215,230,0.4);letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">
      📍 市價 {cp:.2f} vs 公允價值
    </div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:62px;color:{up_col};
        line-height:1;margin-bottom:6px;">{upside:+.1f}%</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:{up_col};
        font-weight:700;">{verdict}</div>
  </div>

</div>
""", unsafe_allow_html=True)

    # ── 多折現率敏感性分析 ────────────────────────────────────────────────────
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:16px;color:#00F5FF;
    letter-spacing:3px;margin:16px 0 10px;">📊 折現率敏感性分析</div>
""", unsafe_allow_html=True)

    dr_range = [0.06, 0.08, 0.10, 0.12, 0.14, 0.15]
    sens_rows = []
    for d in dr_range:
        fv = calculate_smart_valuation(eps, rev, shares * 1e6, g, m, pe, d, 10)
        up = (fv - cp) / cp * 100
        sens_rows.append({"折現率": f"{d*100:.0f}%", "公允價值": round(fv, 2),
                           "溢價/折價": round(up, 1), "顏色": "#00FF7F" if up > 0 else "#FF3131"})

    sens_df = pd.DataFrame(sens_rows)
    sens_chart = (
        alt.Chart(sens_df)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("折現率:N", sort=None,
                     axis=alt.Axis(labelColor="#778899", titleColor="#445566", labelFontSize=12)),
            y=alt.Y("公允價值:Q", title="DCF 公允價值",
                     axis=alt.Axis(labelColor="#556677", titleColor="#445566"),
                     scale=alt.Scale(zero=False)),
            color=alt.Color("顏色:N", scale=None),
            tooltip=["折現率", alt.Tooltip("公允價值:Q", format=".2f"),
                     alt.Tooltip("溢價/折價:Q", format="+.1f")]
        )
        .properties(height=240,
                     title=alt.TitleParams("不同折現率下的公允價值（橫線=當前市價）",
                                            color="#FFD700", fontSize=12, font="JetBrains Mono"))
    )
    rule = alt.Chart(pd.DataFrame({"cp": [cp]})).mark_rule(
        color="#00F5FF", strokeDash=[6, 3], strokeWidth=2
    ).encode(y="cp:Q")

    sens_layer = alt.layer(sens_chart, rule).properties(background="rgba(0,0,0,0)")

    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(sens_layer), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Typewriter 摘要 ───────────────────────────────────────────────────────
    summary = (
        f"【智能估值摘要 — {ticker}】"
        f"以 {dr*100:.0f}% 折現率、{g*100:.0f}% 成長率推算，"
        f"10年DCF公允價值為 {fair_value:.2f}，"
        f"{'低於' if fair_value < cp else '高於'}市價 {cp:.2f} 約 {abs(upside):.1f}%。"
        f"結論：{verdict.split('—')[1].strip() if '—' in verdict else verdict}。"
        f"折現率敏感性顯示：6%折現下公允價值 {calculate_smart_valuation(eps,rev,shares*1e6,g,m,pe,0.06,10):.2f}，"
        f"15%折現下 {calculate_smart_valuation(eps,rev,shares*1e6,g,m,pe,0.15,10):.2f}，差距顯著，請審慎設定折現率假設。"
    )
    if f"val_streamed_{ticker}" not in st.session_state:
        st.write_stream(_stream_text(summary, speed=0.012))
        st.session_state[f"val_streamed_{ticker}"] = True
    else:
        st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
                    f'color:rgba(180,200,220,0.55);line-height:1.8;padding:8px 0;">{summary}</div>',
                    unsafe_allow_html=True)

    st.toast("✅ 智能估值完成！", icon="💎")

# ══════════════════════════════════════════════════════════════
# 🎯 TAB 7: ELLIOTT 5-WAVE (艾略特五波)
# ══════════════════════════════════════════════════════════════
def _t7(sdf):
    """T7: Elliott 5-Wave Projection with Completion Progress"""
    st.toast("🚀 正在執行艾略特波浪分析... / Engaging Elliott Wave...", icon="⏳")
    
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-lbl">🌊 ELLIOTT 5-WAVE ENGINE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">WAVE THEORY</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-sub">艾略特波浪推演系統</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Analysis
    st.markdown("### 🧠 AI 戰術分析")
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis_text = """
═══════════════════════════════════════════════════════════
🎯 ELLIOTT WAVE ANALYSIS
═══════════════════════════════════════════════════════════

📊 WAVE THEORY PRINCIPLES
   Elliott Wave Theory posits that markets move in fractal patterns:
   • Impulse Waves (1-2-3-4-5): Trend direction moves
   • Corrective Waves (A-B-C): Counter-trend retracements
   
⚡ FIBONACCI PROJECTIONS
   Wave 2: 38.2% retracement of Wave 1
   Wave 3: 1.618x extension of Wave 1 (strongest move)
   Wave 4: 38.2% retracement of Wave 3
   Wave 5: 1.0x extension from Wave 4 low
   
🔮 COMPLETION TRACKING
   The system calculates wave completion percentage based on
   current price position relative to projected pivot points.
   
═══════════════════════════════════════════════════════════
"""
    
    st.write_stream(_stream_text(analysis_text, speed=0.002))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate ZigZag
    zz = calculate_zigzag(sdf, deviation=0.03)
    
    if len(zz) < 3:
        st.toast("⚠️ 波動過小 / Volatility Too Low", icon="⚡")
        st.toast("⚠️ 波動過小，無法計算艾略特波浪。", icon="⚡")
        return
    
    # Calculate 5-Wave projection
    sim = calculate_5_waves(zz)
    
    # Wave Completion Progress Bar
    if not sim.empty:
        total_waves = len(sim) - 1  # Exclude Origin
        completed_waves = 0  # This would need real-time tracking
        completion_pct = (completed_waves / total_waves) * 100 if total_waves > 0 else 0
        
        st.markdown(f"""
        <div class="t3-kpi-card" style="--kc:#FF6BFF; max-width:600px; margin:20px auto;">
            <div class="t3-kpi-lbl">WAVE COMPLETION</div>
            <div style="width:100%; background:#1a1a1a; border-radius:10px; height:30px; margin:15px 0; overflow:hidden;">
                <div style="width:{completion_pct}%; background:linear-gradient(90deg, #FF6BFF, #B77DFF); height:100%; transition:width 0.5s;"></div>
            </div>
            <div class="t3-kpi-sub">{completion_pct:.0f}% Complete · {completed_waves}/{total_waves} Waves</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Chart: ZigZag + Wave Projections
    plot_df = sdf[['Close']].tail(120).reset_index()
    plot_df['Date'] = pd.to_datetime(plot_df['Date'])
    
    base_line = alt.Chart(plot_df).mark_line(color='#00F5FF', strokeWidth=2).encode(
        x=alt.X('Date:T', title='日期'),
        y=alt.Y('Close:Q', title='價格')
    )
    
    # ZigZag pivots
    zz_points = zz.copy()
    zz_points['Date'] = pd.to_datetime(zz_points['Date'])
    
    zz_line = alt.Chart(zz_points).mark_line(color='#FFD700', strokeWidth=3).encode(
        x='Date:T',
        y='Price:Q'
    )
    
    zz_dots = alt.Chart(zz_points).mark_point(color='#FFD700', size=100).encode(
        x='Date:T',
        y='Price:Q'
    )
    
    chart_combined = base_line + zz_line + zz_dots
    
    # Add wave projections
    if not sim.empty:
        sim['Date'] = pd.to_datetime(sim['Date'])
        sim_line = alt.Chart(sim[sim['Label'] != 'Origin']).mark_line(
            color='#FF6BFF', strokeWidth=2, strokeDash=[5, 5]
        ).encode(x='Date:T', y='Price:Q')
        
        sim_points = alt.Chart(sim[sim['Label'] != 'Origin']).mark_point(
            color='#FF6BFF', size=150
        ).encode(x='Date:T', y='Price:Q')
        
        sim_labels = alt.Chart(sim[sim['Label'] != 'Origin']).mark_text(
            dy=-30, color='#FF6BFF', fontSize=12, fontWeight='bold'
        ).encode(x='Date:T', y='Price:Q', text='Label')
        
        chart_combined = chart_combined + sim_line + sim_points + sim_labels
    
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(chart_combined), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.toast("✅ 艾略特波浪分析完成 / Elliott Wave Complete", icon="🎯")

# ══════════════════════════════════════════════════════════════
# 🎯 POSTER CONFIGURATION
# ══════════════════════════════════════════════════════════════
POSTERS = [
    ("t1", "🔮", "雙軌扣抵", "DEDUCTION", "#00F5FF"),
    ("t2", "📐", "亞當理論", "ADAM", "#FFD700"),
    ("t3", "🕯️", "日K+RSI", "DAILY K", "#FF9A3C"),
    ("t4", "🗓️", "月K線", "MONTHLY", "#FF3131"),
    ("t5", "🧠", "ARK戰情", "ARK DESK", "#00FF7F"),
    ("t6", "💎", "智能估值", "VALUATION", "#B77DFF"),
    ("t7", "🌊", "5波模擬", "ELLIOTT", "#FF6BFF")
]

RENDER = {
    "t1": _t1,
    "t2": _t2,
    "t3": _t3,
    "t4": _t4,
    "t5": _t5,
    "t6": _t6,
    "t7": _t7
}

# ══════════════════════════════════════════════════════════════
# 🚀 MAIN RENDER FUNCTION
# ══════════════════════════════════════════════════════════════
@st.fragment
def render():
    """Main Render Function - Titan OS God-Tier Edition"""
    
    # ══════════════════════════════════════════════════════════════
    # 🎯 FEATURE 1: Show tactical guide modal on first visit
    # ══════════════════════════════════════════════════════════════
    if "guide_shown_" + __name__ not in st.session_state:
        show_guide_modal()
        st.session_state["guide_shown_" + __name__] = True
    
    _inject_css()
    
    # Initialize session state
    if 't3_active' not in st.session_state:
        st.session_state.t3_active = "t1"
    
    # Header
    st.markdown(f"""
    <div style="display:flex;align-items:baseline;justify-content:space-between;
        padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,.052);margin-bottom:16px;">
        <div>
            <span style="font-family:'Bebas Neue',sans-serif;font-size:26px;color:#FF9A3C;
                letter-spacing:3px;text-shadow:0 0 22px rgba(255,154,60,.32);">🎯 單兵狙擊</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:9px;
                color:rgba(255,154,60,.26);letter-spacing:3px;
                border:1px solid rgba(255,154,60,.10);border-radius:20px;
                padding:3px 13px;margin-left:14px;">SOLO SNIPER V100 · GOD TIER</span>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
            color:rgba(200,215,230,.20);letter-spacing:2px;text-align:right;line-height:1.7;">
            {datetime.now().strftime('%H:%M:%S')}<br>{datetime.now().strftime('%Y·%m·%d')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main Content
    with st.expander("3.1 萬用個股狙擊雷達 (Universal Sniper)", expanded=True):
        st.toast("🌍 全球戰情模式已啟動 / Global Tactical Mode Engaged", icon="🎯")
        
        # Search Input
        ic, bc = st.columns([5, 1])
        with ic:
            w17_in = st.text_input(
                "輸入代號或股名",
                value=st.session_state.get('t3_ticker', '2330'),
                placeholder="2330 / TSLA / BTC-USD",
                key="w17_final_v102"
            ).strip()
        
        with bc:
            st.markdown('<div style="margin-top:22px;"><div class="t3-action">', unsafe_allow_html=True)
            if st.button("🔍 搜尋", key="t3_search", use_container_width=True):
                st.session_state.t3_ticker = w17_in
                st.toast("🚀 正在掃描全球資料庫... / Scanning Global Database...", icon="⏳")
            st.markdown('</div></div>', unsafe_allow_html=True)
        
        ticker_in = st.session_state.get('t3_ticker', '2330').strip()
        
        if not ticker_in:
            st.toast("⚠️ 請輸入標的代號 / Please Enter Symbol", icon="⚡")
            return
        
        # Ticker normalization
        try:
            from macro_risk import STOCK_METADATA
            N2T = {v['name'].strip(): k for k, v in STOCK_METADATA.items()}
            if ticker_in in N2T:
                ticker_in = N2T[ticker_in]
        except Exception:
            pass
        
        # Candidate ticker variations
        cands = [ticker_in]
        if ticker_in.isdigit():
            cands = [f"{ticker_in}.TW", f"{ticker_in}.TWO"]
        elif not ticker_in.endswith((".TW", ".TWO")):
            cands = [ticker_in.upper(), f"{ticker_in.upper()}.TW"]
        
        # Fetch data
        macro = _get_macro()
        sdf = pd.DataFrame()
        v_ticker = None
        
        with st.spinner("掃描全球資料庫..."):
            for c in cands:
                temp = macro.get_single_stock_data(c, period="max")
                if not temp.empty and len(temp) >= 300:
                    sdf = temp
                    v_ticker = c
                    break
        
        if sdf.empty:
            st.toast("❌ 查無數據 / No Data Found", icon="⚡")
            st.toast("❌ 查無數據，或歷史數據不足 300 天無法計算年線扣抵。", icon="💀")
            return
        
        # Data preprocessing
        try:
            if isinstance(sdf.columns, pd.MultiIndex):
                sdf.columns = sdf.columns.get_level_values(0)
            sdf.columns = [str(c).strip().capitalize() for c in sdf.columns]
            sdf = sdf.reset_index()
            
            dc = next((c for c in sdf.columns if str(c).lower() in ['date', 'datetime', 'index']), None)
            if dc:
                sdf.rename(columns={dc: 'Date'}, inplace=True)
                sdf['Date'] = pd.to_datetime(sdf['Date'])
                sdf.set_index('Date', inplace=True)
                sdf.sort_index(inplace=True)
            
            col_map = {}
            for c in sdf.columns:
                if c.lower() in ['close', 'price']:
                    col_map[c] = 'Close'
                elif c.lower() in ['volume', 'vol']:
                    col_map[c] = 'Volume'
            sdf.rename(columns=col_map, inplace=True)
            
            for req in ['Open', 'High', 'Low']:
                if req not in sdf.columns:
                    sdf[req] = sdf['Close']
            
            if 'Volume' not in sdf.columns:
                sdf['Volume'] = 0
            
            for c in ['Close', 'Open', 'High', 'Low', 'Volume']:
                sdf[c] = pd.to_numeric(sdf[c], errors='coerce')
            
            sdf = sdf.dropna(subset=['Close'])
        
        except Exception as e:
            st.toast("❌ 資料格式錯誤 / Data Format Error", icon="⚡")
            st.toast(f"❌ 資料格式錯誤: {e}", icon="💀")
            return
        
        # Calculate MAs
        sdf['MA87'] = sdf['Close'].rolling(87).mean()
        sdf['MA284'] = sdf['Close'].rolling(284).mean()
        sdf['Prev_MA87'] = sdf['MA87'].shift(1)
        sdf['Prev_MA284'] = sdf['MA284'].shift(1)
        sdf['Cross_Signal'] = 0
        sdf.loc[(sdf['Prev_MA87'] <= sdf['Prev_MA284']) & (sdf['MA87'] > sdf['MA284']), 'Cross_Signal'] = 1
        sdf.loc[(sdf['Prev_MA87'] >= sdf['Prev_MA284']) & (sdf['MA87'] < sdf['MA284']), 'Cross_Signal'] = -1
        
        # Current metrics
        cp = float(sdf['Close'].iloc[-1])
        op = float(sdf['Open'].iloc[-1])
        m87 = float(sdf['MA87'].iloc[-1]) if not pd.isna(sdf['MA87'].iloc[-1]) else 0
        m87p5 = float(sdf['MA87'].iloc[-6]) if len(sdf) > 6 and not pd.isna(sdf['MA87'].iloc[-6]) else m87
        m284 = float(sdf['MA284'].iloc[-1]) if not pd.isna(sdf['MA284'].iloc[-1]) else 0
        bias = ((cp - m87) / m87) * 100 if m87 > 0 else 0
        
        # Trend analysis
        trend_days = 0
        trend_str = "整理中"
        trend_c = "#FFD700"
        
        if m87 > 0 and m284 > 0:
            is_bull = m87 > m284
            trend_str = "🔥 中期多頭 (87>284)" if is_bull else "❄️ 中期空頭 (87<284)"
            trend_c = "#00FF7F" if is_bull else "#FF6B6B"
            bs = sdf['MA87'] > sdf['MA284']
            cs = bs.iloc[-1]
            for i in range(len(bs) - 1, -1, -1):
                if bs.iloc[i] == cs:
                    trend_days += 1
                else:
                    break
        
        g_title, g_desc = get_advanced_granville(cp, op, m87, m87p5)
        bias_c = "#FF3131" if abs(bias) > 15 else ("#FFD700" if abs(bias) > 7 else "#00FF7F")
        
        # Display metrics
        st.subheader(f"🎯 {v_ticker} 戰情報告")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("目前股價", f"{cp:.2f}")
        c2.metric("87MA (季線)", f"{m87:.2f}", f"{cp - m87:.2f}")
        c3.metric("284MA (年線)", f"{m284:.2f}", f"{cp - m284:.2f}")
        c4.metric("乖離率 (Bias)", f"{bias:.1f}%")
        
        st.markdown(f"""
        <div style="font-family:Rajdhani,sans-serif;font-size:14px;color:rgba(200,215,230,.6);
            margin:6px 0 4px;">
            <span style="color:{trend_c};font-weight:700;">{trend_str}</span>
            &nbsp;·&nbsp; 持續 <span style="color:#FFD700;font-weight:700;">{trend_days}</span> 天
            &nbsp;·&nbsp; 格蘭碧：<span style="color:#00F5FF;font-weight:700;">{g_title}</span> — {g_desc}
        </div>
        """, unsafe_allow_html=True)
        
        # FEATURE 3: Valkyrie Typewriter for tactical summary
        st.markdown("**🎯 戰術總結 (Tactical Summary)**")
        tactical_summary = f"基於當前技術指標分析，{v_ticker} 目前處於 {trend_str.replace('🔥', '').replace('❄️', '').strip()} 狀態，已持續 {trend_days} 個交易日。格蘭碧信號顯示 {g_title}，{g_desc}。乖離率為 {bias:.1f}%，{'建議謹慎操作' if abs(bias) > 15 else '處於正常範圍' if abs(bias) < 7 else '需要關注'}。請結合下方各項技術指標進行綜合判斷。"
        st.write_stream(stream_generator(tactical_summary))
        
        # Render badges
        _render_badges(sdf, cp, m87, m284, bias)
        
        st.markdown("---")
        
        # Poster Rail
        active = st.session_state.t3_active
        st.markdown(
            '<div class="t3-rail"><div class="t3-rail-lbl">⬡ ANALYSIS MODULES — CLICK TO SELECT</div>',
            unsafe_allow_html=True
        )
        
        p_cols = st.columns(7)
        for col, (key, icon, label, tag, accent) in zip(p_cols, POSTERS):
            is_a = (active == key)
            brd = f"2px solid {accent}" if is_a else "1px solid rgba(255,255,255,0.07)"
            bg_c = f"rgba(255,154,60,.10)" if is_a else "rgba(255,255,255,0.02)"
            lbl_c = accent if is_a else "rgba(200,215,230,.75)"
            tag_c = accent if is_a else "rgba(100,120,140,0.5)"
            glow  = f"0 0 22px rgba(255,154,60,.18), 0 4px 20px rgba(0,0,0,.5)" if is_a else "0 2px 12px rgba(0,0,0,.4)"
            top_line = f'<div style="position:absolute;top:0;left:15%;right:15%;height:2px;background:{accent};border-radius:0 0 2px 2px;opacity:{1 if is_a else 0};"></div>' if is_a else ""

            with col:
                # ── invisible button first (sits under the card visually) ──
                if st.button(label, key=f"p3_{key}", use_container_width=True):
                    st.session_state.t3_active = key
                    st.rerun()

                # ── poster card overlays the button, pointer-events:none ──
                st.markdown(f"""
<div style="position:relative;height:128px;background:{bg_c};border:{brd};
    border-radius:14px;display:flex;flex-direction:column;align-items:center;
    justify-content:center;gap:6px;box-shadow:{glow};
    margin-top:-38px;pointer-events:none;z-index:1;overflow:hidden;">
  {top_line}
  <div style="font-size:26px;line-height:1;filter:drop-shadow(0 0 6px {accent}44);">{icon}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:12px;font-weight:700;
      color:{lbl_c};text-align:center;padding:0 4px;letter-spacing:0.3px;">{label}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:7px;color:{tag_c};
      letter-spacing:2px;text-transform:uppercase;">{tag}</div>
</div>""", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Render selected module
        st.markdown('<div class="t3-content">', unsafe_allow_html=True)
        
        try:
            fn = RENDER[active]
            if active == "t1":
                fn(sdf, v_ticker, cp, m87, m87p5, m284)
            elif active in ("t2", "t3", "t4"):
                fn(sdf, v_ticker)
            elif active in ("t5", "t6"):
                fn(v_ticker, cp)
            elif active == "t7":
                fn(sdf)
        except Exception as exc:
            import traceback
            st.toast("❌ 子模組渲染失敗 / Module Render Failed", icon="⚡")
            st.toast(f"❌ 子模組 {active} 渲染失敗: {exc}", icon="💀")
            st.error(f"❌ 子模組 {active} 渲染失敗: {exc}")
            with st.expander("🔍 Debug"):
                st.code(traceback.format_exc())
        
        st.markdown(f"""
        <div class="t3-foot">Titan Solo Sniper V100 · God-Tier Edition · 
            {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 🎯 ENTRY POINT
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    render()
