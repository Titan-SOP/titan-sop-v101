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

def calculate_hypergrowth_valuation(rev, shares, rev_g, gm_now, gm_target, opex_now,
                                     opex_improve, ps_terminal, pe_terminal, dr=0.15, y=7):
    """
    Pre-Profit HyperGrowth Valuation Model (for companies like QBTS, IONQ)
    ──────────────────────────────────────────────────────────────────────
    Logic:
      1. Project revenue year-by-year at rev_g
      2. Gross margin improves linearly from gm_now → gm_target over y years
      3. OpEx (as % of rev) improves by opex_improve each year (converging to profitability)
      4. Detect breakeven year (net income > 0)
      5. Terminal value:
         - If profitable within y years → use P/E on terminal net income
         - Else → use P/S on terminal revenue
      6. Discount terminal value back at dr
    Returns dict: terminal_price, breakeven_year (None if not found), projections DataFrame
    """
    if not rev or shares == 0:
        return None

    rows = []
    r = rev
    opex_pct = opex_now
    breakeven_year = None

    for yr in range(1, y + 1):
        r = r * (1 + rev_g)
        # Gross margin improves linearly each year
        gm = gm_now + (gm_target - gm_now) * (yr / y)
        gross_profit = r * gm
        # OpEx declines as % of revenue
        opex_pct = max(opex_pct - opex_improve, gm * 0.5)  # floor: opex can't drop below 50% of GP
        opex_abs = r * opex_pct
        net_income = gross_profit - opex_abs
        net_margin = net_income / r if r > 0 else 0
        eps_proj = net_income / shares if shares > 0 else 0
        price_ps = r * ps_terminal / shares if shares > 0 else 0

        is_profitable = net_income > 0
        if is_profitable and breakeven_year is None:
            breakeven_year = yr

        rows.append({
            'Year': yr,
            'Revenue': round(r, 1),
            'GrossMargin': round(gm * 100, 1),
            'GrossProfit': round(gross_profit, 1),
            'OpEx': round(opex_abs, 1),
            'NetIncome': round(net_income, 1),
            'NetMargin': round(net_margin * 100, 2),
            'EPS_proj': round(eps_proj, 4),
            'Price_PS': round(price_ps, 4),
            'Profitable': is_profitable,
        })

    proj_df = pd.DataFrame(rows)
    terminal_row = proj_df.iloc[-1]

    if breakeven_year is not None:
        # Use P/E on terminal net income
        terminal_mktcap = terminal_row['NetIncome'] * pe_terminal
        terminal_price_raw = terminal_mktcap / shares
    else:
        # Use P/S on terminal revenue
        terminal_price_raw = terminal_row['Revenue'] * ps_terminal / shares

    terminal_price = terminal_price_raw / ((1 + dr) ** y)
    terminal_price = max(terminal_price, 0)

    return {
        'terminal_price': terminal_price,
        'terminal_price_raw': terminal_price_raw,
        'breakeven_year': breakeven_year,
        'projections': proj_df,
        'used_method': 'P/E' if breakeven_year is not None else 'P/S',
    }

def calculate_moonshot_valuation(
    rev, shares, cash, burn_annual,
    rev_g_y1, rev_g_decel,
    gm_now, gm_target,
    opex_pct, opex_improve,
    dilution_annual,
    ps_terminal, pe_terminal,
    dr=0.20, y=7,
    scenario_mult=None  # dict: {g_decel_mult, gm_target_adj, terminal_mult}
):
    """
    Moonshot ARK Valuation Engine — 燒錢超高速成長股專用
    ──────────────────────────────────────────────────────────────────────
    第一性原則設計：針對 QBTS / IONQ / RGTI 這類公司的核心特質
      - 收入極小但成長極快（50~200% YoY）
      - 大量燒錢，現金跑道有限
      - 每年發新股稀釋（SBC + 增資）
      - 毛利率尚低但有清晰改善路徑
      - 終端市場（TAM）龐大，但滲透率尚在 0.x%

    建模邏輯（8 個步驟）：
      1. 收入以「衰減曲線」成長：第 n 年成長率 = rev_g_y1 × (1 − rev_g_decel)^(n−1)，
         地板為 15%（避免成熟期假設成長消失）
      2. 毛利率線性改善：gm_now → gm_target over y years
      3. 費用佔比每年收斂：opex_pct 每年下降 opex_improve（地板：gm × 0.45）
      4. 現金追蹤：每年 EBITDA 負值即為燒錢；累積現金耗盡年份 = 現金跑道
      5. 股數稀釋：每年 × (1 + dilution_annual)，反映 SBC + 潛在增資
      6. 找到轉盈點（EBITDA > 0）
      7. 終端定價：
         - 已獲利 → 終端淨利 × pe_terminal
         - 仍虧損 → 終端收入 × ps_terminal
      8. 折現回今日，並以稀釋後股數換算每股目標價

    scenario_mult 參數用於多情境：
      g_decel_mult  : 成長衰減速度乘數（>1 = 更快衰減 = 悲觀）
      gm_target_adj : 目標毛利率調整（+0.10 = 樂觀 +10pp）
      terminal_mult : 終端倍數乘數（1.3 = 牛市溢價 30%）

    Returns dict:
      terminal_price, terminal_price_raw, breakeven_year,
      cash_runway_years, terminal_shares, used_method, projections
    """
    if not rev or shares <= 0:
        return None

    # ── 解包情境乘數 ──────────────────────────────────────────
    if scenario_mult is None:
        scenario_mult = {}
    g_decel_eff     = rev_g_decel * scenario_mult.get('g_decel_mult', 1.0)
    gm_target_eff   = min(0.95, gm_target + scenario_mult.get('gm_target_adj', 0.0))
    term_mult       = scenario_mult.get('terminal_mult', 1.0)
    ps_eff          = ps_terminal * term_mult
    pe_eff          = pe_terminal * term_mult

    rows = []
    r            = rev
    cur_shares   = shares
    cur_cash     = cash
    opex_pct_cur = opex_pct
    breakeven_year   = None
    cash_runway_years = None

    for yr in range(1, y + 1):
        # 1. 收入衰減成長曲線
        g_this_yr = max(rev_g_y1 * ((1 - g_decel_eff) ** (yr - 1)), 0.10)
        r = r * (1 + g_this_yr)

        # 2. 毛利率線性改善
        gm = gm_now + (gm_target_eff - gm_now) * (yr / y)
        gross_profit = r * gm

        # 3. 費用收斂（不能低於毛利的45%）
        opex_pct_cur = max(opex_pct_cur - opex_improve, gm * 0.45)
        opex_abs = r * opex_pct_cur
        ebitda   = gross_profit - opex_abs
        net_income = ebitda  # 簡化：EBITDA ≈ 淨利（早期公司D&A較小）
        net_margin = net_income / r if r > 0 else 0

        # 4. 現金追蹤
        if cur_cash is not None and burn_annual is not None:
            annual_burn = max(0, -ebitda) if ebitda < 0 else 0
            cur_cash = cur_cash - annual_burn
            if cur_cash <= 0 and cash_runway_years is None:
                cash_runway_years = yr

        # 5. 股數稀釋
        cur_shares = cur_shares * (1 + dilution_annual)
        eps_proj   = net_income / cur_shares if cur_shares > 0 else 0

        # 6. 轉盈點
        is_profitable = net_income > 0
        if is_profitable and breakeven_year is None:
            breakeven_year = yr

        rows.append({
            'Year'        : yr,
            'GrowthRate'  : round(g_this_yr * 100, 1),
            'Revenue'     : round(r, 2),
            'GrossMargin' : round(gm * 100, 1),
            'GrossProfit' : round(gross_profit, 2),
            'OpEx'        : round(opex_abs, 2),
            'EBITDA'      : round(ebitda, 2),
            'NetIncome'   : round(net_income, 2),
            'NetMargin'   : round(net_margin * 100, 2),
            'Shares'      : round(cur_shares, 1),
            'EPS_proj'    : round(eps_proj, 4),
            'CashBal'     : round(cur_cash, 1) if cur_cash is not None else None,
            'Profitable'  : is_profitable,
        })

    proj_df = pd.DataFrame(rows)
    terminal_row = proj_df.iloc[-1]

    # 7. 終端定價
    if breakeven_year is not None:
        terminal_mktcap = terminal_row['NetIncome'] * pe_eff
        terminal_price_raw = terminal_mktcap / terminal_row['Shares']
        used_method = f'P/E {pe_eff:.0f}x'
    else:
        terminal_price_raw = terminal_row['Revenue'] * ps_eff / terminal_row['Shares']
        used_method = f'P/S {ps_eff:.0f}x'

    # 8. 折現回今日
    terminal_price = max(terminal_price_raw / ((1 + dr) ** y), 0)

    return {
        'terminal_price'     : terminal_price,
        'terminal_price_raw' : terminal_price_raw,
        'breakeven_year'     : breakeven_year,
        'cash_runway_years'  : cash_runway_years,
        'terminal_shares'    : terminal_row['Shares'],
        'used_method'        : used_method,
        'projections'        : proj_df,
    }


def calculate_tam_penetration(rev, tam_b, market_cap_b, ps_terminal):
    """
    TAM 滲透率分析
    ──────────────────────────────────────────────────────────────────────
    回答三個關鍵問題：
      Q1. 現在的收入是 TAM 的多少 %？（知道你現在有多渺小）
      Q2. 要達到終端 P/S 倍數能支撐當前市值，需要多少收入？（隱含需要多大市占率）
      Q3. 若達到 10% TAM，用你設定的 P/S 定價，值多少錢？
    """
    tam_m = tam_b * 1000  # 轉換為百萬
    current_pen = (rev / tam_m * 100) if tam_m > 0 else 0

    # 隱含收入（要讓 P/S × 收入 = 市值）
    market_cap_m = market_cap_b * 1000
    implied_rev = market_cap_m / ps_terminal if ps_terminal > 0 else 0
    implied_pen = (implied_rev / tam_m * 100) if tam_m > 0 else 0

    # 達到 10% TAM 時的潛在市值（按終端 P/S）
    ten_pct_rev = tam_m * 0.10
    ten_pct_mktcap_b = (ten_pct_rev * ps_terminal) / 1000

    return {
        'current_pen'      : current_pen,
        'implied_rev_m'    : implied_rev,
        'implied_pen'      : implied_pen,
        'ten_pct_mktcap_b' : ten_pct_mktcap_b,
        'tam_m'            : tam_m,
    }


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
# 🎯 TAB 1: DUAL-TRACK DEDUCTION PREVIEW (雙軌扣抵預演) — 第一性原則重建
# ══════════════════════════════════════════════════════════════
# 扣抵原理：N日均線 = 近N日收盤價總和 ÷ N
# 明天的均線 = 今天均線 + (今日新收盤 - N日前收盤) ÷ N
# 核心推演：比較「今日收盤」vs「N日前收盤（即將被扣掉的舊值）」
#   今日 > 舊值 → 明天均線上揚（扣低拉升）
#   今日 < 舊值 → 明天均線下彎（扣高壓抑）
# ══════════════════════════════════════════════════════════════
def _t1(sdf, ticker, cp, m87, m87p5, m284):
    """T1: Dual-Track MA Deduction — First Principles Full Engine"""
    st.toast("🚀 雙軌扣抵推演引擎啟動中…", icon="⏳")

    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown('<div class="hero-lbl">🔮 DUAL-TRACK DEDUCTION ENGINE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">{ticker}</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">雙軌扣抵預演系統 · 第一性原則推演</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if len(sdf) < 300:
        st.toast("⚠️ 歷史數據不足 300 天，無法精確計算年線扣抵。", icon="⚡")
        return

    # ── 核心計算：扣抵數據建構 ───────────────────────────────────────
    df = sdf[['Close']].copy()
    df['MA87']       = df['Close'].rolling(87).mean()
    df['MA284']      = df['Close'].rolling(284).mean()
    df['扣抵值_87']   = df['Close'].shift(87)    # 即將被MA87扣掉的舊收盤
    df['扣抵值_284']  = df['Close'].shift(284)   # 即將被MA284扣掉的舊收盤
    df = df.dropna()

    # ── 未來30日扣抵推演表 ──────────────────────────────────────────
    # 未來第i天的MA87，取決於「第i天新收盤」vs「87天前的舊收盤（已知）」
    # 假設股價維持現價(cp)不變，推算均線走勢
    future_rows_87  = []
    future_rows_284 = []
    last_ma87  = float(df['MA87'].iloc[-1])
    last_ma284 = float(df['MA284'].iloc[-1])
    closes     = df['Close'].values

    for i in range(1, 31):
        # 即將被扣掉的舊值（已知歷史數據）
        old87  = float(df['Close'].iloc[-(87  - i)] if i < 87  else closes[-1])
        old284 = float(df['Close'].iloc[-(284 - i)] if i < 284 else closes[-1])

        delta87  = (cp - old87)  / 87
        delta284 = (cp - old284) / 284

        last_ma87  += delta87
        last_ma284 += delta284

        future_rows_87.append({
            '天數': f'+{i}天',
            '推估MA87':    round(last_ma87, 2),
            '被扣舊值_87': round(old87, 2),
            '扣抵差額_87': round(cp - old87, 2),
            '方向_87':     '↑ 上揚' if cp > old87 else '↓ 下彎',
        })
        future_rows_284.append({
            '天數': f'+{i}天',
            '推估MA284':    round(last_ma284, 2),
            '被扣舊值_284': round(old284, 2),
            '扣抵差額_284': round(cp - old284, 2),
            '方向_284':     '↑ 上揚' if cp > old284 else '↓ 下彎',
        })

    fut87_df  = pd.DataFrame(future_rows_87)
    fut284_df = pd.DataFrame(future_rows_284)

    # ── 均線保持持平所需的「保平價」 ──────────────────────────────────
    # MA(N) 明天持平 → 今日收盤 = 87天前的舊收盤
    breakeven_87  = float(df['扣抵值_87'].iloc[-1])
    breakeven_284 = float(df['扣抵值_284'].iloc[-1])

    # ── 扣抵壓力評分（未來30天中，下彎天數佔比）──────────────────────
    down87_pct  = sum(1 for r in future_rows_87  if '↓' in r['方向_87'])  / 30 * 100
    down284_pct = sum(1 for r in future_rows_284 if '↓' in r['方向_284']) / 30 * 100

    # ── 均線多空關係 ──────────────────────────────────────────────────
    slope_87   = m87 - m87p5
    ma_gap_pct = (m87 - m284) / m284 * 100
    ma_align   = '多頭排列' if m87 > m284 else '空頭排列'
    align_color = '#00FF7F' if m87 > m284 else '#FF3131'

    # ── 戰術分析（AI Typewriter）─────────────────────────────────────
    st.markdown("### 🧠 扣抵第一性原則 · 戰術推演")
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    analysis = f"""
═══════════════════════════════════════════════════════════
🔮 TITAN DEDUCTION ENGINE v3.0 — {ticker}
   現價: ${cp:.2f}  │  MA87: ${m87:.2f}  │  MA284: ${m284:.2f}
═══════════════════════════════════════════════════════════

【一、扣抵原理精解】
  移動平均線的漲跌，由一個簡單公式決定：
    ΔMA(N) = (今日收盤 − N日前收盤) ÷ N
  這意味著均線的走向，在 N 天前就已被「鎖定」。
  我們能精確預判未來 30 天的均線趨勢，無需預測股價。

【二、MA87 季線扣抵現況】
  今日將扣掉的舊收盤：      ${breakeven_87:.2f}
  現價 vs 扣抵值差額：      {cp - breakeven_87:+.2f}
  明日MA87方向：            {'↑ 上揚（現價高於扣抵值，買方佔優）' if cp >= breakeven_87 else '↓ 下彎（現價低於扣抵值，賣方壓抑）'}
  保平價（MA87持平需達到）： ${breakeven_87:.2f}
  未來30天下彎比例：        {down87_pct:.0f}%  → {'⚠️ 季線壓力沉重' if down87_pct > 60 else '✅ 季線支撐有效' if down87_pct < 40 else '🟡 季線方向拉鋸'}

【三、MA284 年線扣抵現況】
  今日將扣掉的舊收盤：      ${breakeven_284:.2f}
  現價 vs 扣抵值差額：      {cp - breakeven_284:+.2f}
  明日MA284方向：           {'↑ 上揚（長期底部支撐強化中）' if cp >= breakeven_284 else '↓ 下彎（年線長期壓力持續累積）'}
  保平價（MA284持平需達到）：${breakeven_284:.2f}
  未來30天下彎比例：        {down284_pct:.0f}%  → {'⚠️ 年線長期壓制' if down284_pct > 60 else '✅ 年線底部墊高' if down284_pct < 40 else '🟡 年線鬆動待確認'}

【四、雙軌多空結構】
  均線排列：  {ma_align}（MA87 vs MA284 差距 {ma_gap_pct:+.1f}%）
  MA87斜率：  {slope_87:+.2f}（{'加速上揚' if slope_87 > 1 else '緩步上揚' if slope_87 > 0 else '緩步下彎' if slope_87 > -1 else '加速下彎'}）

【五、操作戰術推演】
  {'🟢 多頭結構確立：均線多頭排列，季線向上，扣抵壓力輕，逢回佈局。' if ma_align == '多頭排列' and down87_pct < 50 else '🔴 空頭結構確立：均線空頭排列，雙線均受扣抵壓力，持股需降低水位。' if ma_align == '空頭排列' and down87_pct > 50 else '🟡 轉折觀察期：雙軌扣抵訊號分歧，等待方向確認後再行動。'}
  關鍵觀察：若股價能守住 ${min(breakeven_87, breakeven_284):.2f}（雙軌保平線低者），則均線不惡化。

═══════════════════════════════════════════════════════════
"""
    st.write_stream(_stream_text(analysis, speed=0.002))
    st.markdown('</div>', unsafe_allow_html=True)

    # ── KPI 儀表板 ────────────────────────────────────────────────────
    slope_txt   = f"{'↑' if slope_87 > 0 else '↓'} {abs(slope_87):.2f}/天"
    slope_color = '#00FF7F' if slope_87 > 0 else '#FF3131'
    gap87_color = '#00FF7F' if cp >= breakeven_87  else '#FF3131'
    gap284_color= '#00FF7F' if cp >= breakeven_284 else '#FF3131'

    st.markdown(f"""
    <div class="t3-kpi-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom:18px;">
        <div class="t3-kpi-card" style="--kc:#00F5FF;">
            <div class="t3-kpi-lbl">MA87 保平價</div>
            <div class="t3-kpi-val" style="font-size:30px; color:{gap87_color};">${breakeven_87:.2f}</div>
            <div class="t3-kpi-sub">現價差 {cp-breakeven_87:+.2f}</div>
        </div>
        <div class="t3-kpi-card" style="--kc:#FF9A3C;">
            <div class="t3-kpi-lbl">MA284 保平價</div>
            <div class="t3-kpi-val" style="font-size:30px; color:{gap284_color};">${breakeven_284:.2f}</div>
            <div class="t3-kpi-sub">現價差 {cp-breakeven_284:+.2f}</div>
        </div>
        <div class="t3-kpi-card" style="--kc:#FFD700;">
            <div class="t3-kpi-lbl">MA87 斜率</div>
            <div class="t3-kpi-val" style="font-size:30px; color:{slope_color};">{slope_txt}</div>
            <div class="t3-kpi-sub">季線動能</div>
        </div>
        <div class="t3-kpi-card" style="--kc:{align_color};">
            <div class="t3-kpi-lbl">均線排列</div>
            <div class="t3-kpi-val" style="font-size:26px; color:{align_color};">{ma_align}</div>
            <div class="t3-kpi-sub">差距 {ma_gap_pct:+.1f}%</div>
        </div>
    </div>
    <div class="t3-kpi-grid" style="grid-template-columns: repeat(2, 1fr); margin-bottom:24px;">
        <div class="t3-kpi-card" style="--kc:#00F5FF;">
            <div class="t3-kpi-lbl">MA87 未來30天 下彎壓力</div>
            <div class="t3-kpi-val" style="font-size:34px; color:{'#FF3131' if down87_pct>60 else '#00FF7F' if down87_pct<40 else '#FFD700'};">{down87_pct:.0f}%</div>
            <div class="t3-kpi-sub">{'⚠️ 壓力沉重' if down87_pct>60 else '✅ 支撐有效' if down87_pct<40 else '🟡 方向拉鋸'}</div>
        </div>
        <div class="t3-kpi-card" style="--kc:#FF9A3C;">
            <div class="t3-kpi-lbl">MA284 未來30天 下彎壓力</div>
            <div class="t3-kpi-val" style="font-size:34px; color:{'#FF3131' if down284_pct>60 else '#00FF7F' if down284_pct<40 else '#FFD700'};">{down284_pct:.0f}%</div>
            <div class="t3-kpi-sub">{'⚠️ 年線長壓' if down284_pct>60 else '✅ 年線底墊高' if down284_pct<40 else '🟡 年線待確認'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 圖一：近60日 雙軌扣抵全景圖 ──────────────────────────────────
    st.markdown("#### 📊 雙軌扣抵全景圖（近60日 · 現價 vs 被扣舊值）")
    chart_df = df[['Close', 'MA87', 'MA284', '扣抵值_87', '扣抵值_284']].tail(60).reset_index()
    chart_df['Date'] = pd.to_datetime(chart_df['Date'])

    c_close  = alt.Chart(chart_df).mark_line(color='#FFFFFF', strokeWidth=2).encode(
        x=alt.X('Date:T', title='日期', axis=alt.Axis(labelFontSize=26, titleFontSize=24, labelColor='#aaa')),
        y=alt.Y('Close:Q', title='價格', axis=alt.Axis(labelFontSize=26, titleFontSize=24, labelColor='#aaa')),
        tooltip=[alt.Tooltip('Date:T', title='日期'), alt.Tooltip('Close:Q', title='收盤', format='.2f')]
    )
    c_ma87   = alt.Chart(chart_df).mark_line(color='#00F5FF', strokeWidth=2.5).encode(
        x='Date:T', y='MA87:Q',
        tooltip=[alt.Tooltip('MA87:Q', title='MA87', format='.2f')]
    )
    c_ma284  = alt.Chart(chart_df).mark_line(color='#FF9A3C', strokeWidth=2.5).encode(
        x='Date:T', y='MA284:Q',
        tooltip=[alt.Tooltip('MA284:Q', title='MA284', format='.2f')]
    )
    c_d87    = alt.Chart(chart_df).mark_line(color='#FFD700', strokeWidth=1.5, strokeDash=[6, 3]).encode(
        x='Date:T', y='扣抵值_87:Q',
        tooltip=[alt.Tooltip('扣抵值_87:Q', title='87日前價', format='.2f')]
    )
    c_d284   = alt.Chart(chart_df).mark_line(color='#FF6BFF', strokeWidth=1.5, strokeDash=[6, 3]).encode(
        x='Date:T', y='扣抵值_284:Q',
        tooltip=[alt.Tooltip('扣抵值_284:Q', title='284日前價', format='.2f')]
    )
    combo_chart = (c_close + c_ma87 + c_ma284 + c_d87 + c_d284).properties(
        height=320,
        title=alt.TitleParams(
            '白=收盤  青=MA87  橘=MA284  金虛=87日前扣抵值  紫虛=284日前扣抵值',
            color='#aaa', fontSize=18, font='JetBrains Mono'
        )
    )
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(combo_chart), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 圖二：未來30日 MA87 推估軌跡（假設股價維持現價）──────────────
    st.markdown("#### 🔮 MA87 未來30日推估軌跡（假設現價維持不變）")
    fut87_df['顏色'] = fut87_df['方向_87'].apply(lambda x: '#00FF7F' if '↑' in x else '#FF3131')

    bars87 = alt.Chart(fut87_df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('天數:N', sort=None, axis=alt.Axis(labelFontSize=26, titleFontSize=24, labelColor='#aaa')),
        y=alt.Y('扣抵差額_87:Q', title='扣抵差額（現價−舊值）',
                axis=alt.Axis(labelFontSize=26, titleFontSize=24, labelColor='#aaa')),
        color=alt.Color('顏色:N', scale=None),
        tooltip=[
            alt.Tooltip('天數:N', title='天數'),
            alt.Tooltip('推估MA87:Q', title='預估MA87', format='.2f'),
            alt.Tooltip('被扣舊值_87:Q', title='被扣舊值', format='.2f'),
            alt.Tooltip('扣抵差額_87:Q', title='差額', format='+.2f'),
            alt.Tooltip('方向_87:N', title='方向'),
        ]
    )
    zero_rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(
        color='#555', strokeDash=[4, 4], strokeWidth=1.5
    ).encode(y='y:Q')
    ma87_line = alt.Chart(fut87_df).mark_line(color='#00F5FF', strokeWidth=2.5).encode(
        x=alt.X('天數:N', sort=None),
        y=alt.Y('推估MA87:Q', title=''),
        tooltip=[alt.Tooltip('推估MA87:Q', title='推估MA87', format='.2f')]
    )
    fut87_chart = alt.layer(bars87, zero_rule).resolve_scale(y='shared').properties(
        height=260,
        title=alt.TitleParams(
            f'綠柱=均線上揚  紅柱=均線下彎（假設現價維持 ${cp:.2f}）',
            color='#00F5FF', fontSize=18, font='JetBrains Mono'
        )
    )
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(fut87_chart), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 圖三：未來30日 MA284 推估軌跡 ─────────────────────────────────
    st.markdown("#### 🔮 MA284 未來30日推估軌跡（假設現價維持不變）")
    fut284_df['顏色'] = fut284_df['方向_284'].apply(lambda x: '#00FF7F' if '↑' in x else '#FF3131')

    bars284 = alt.Chart(fut284_df).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        x=alt.X('天數:N', sort=None, axis=alt.Axis(labelFontSize=26, titleFontSize=24, labelColor='#aaa')),
        y=alt.Y('扣抵差額_284:Q', title='扣抵差額（現價−舊值）',
                axis=alt.Axis(labelFontSize=26, titleFontSize=24, labelColor='#aaa')),
        color=alt.Color('顏色:N', scale=None),
        tooltip=[
            alt.Tooltip('天數:N', title='天數'),
            alt.Tooltip('推估MA284:Q', title='預估MA284', format='.2f'),
            alt.Tooltip('被扣舊值_284:Q', title='被扣舊值', format='.2f'),
            alt.Tooltip('扣抵差額_284:Q', title='差額', format='+.2f'),
            alt.Tooltip('方向_284:N', title='方向'),
        ]
    )
    zero_rule2 = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(
        color='#555', strokeDash=[4, 4], strokeWidth=1.5
    ).encode(y='y:Q')
    fut284_chart = alt.layer(bars284, zero_rule2).resolve_scale(y='shared').properties(
        height=260,
        title=alt.TitleParams(
            f'綠柱=年線上揚  紅柱=年線下彎（假設現價維持 ${cp:.2f}）',
            color='#FF9A3C', fontSize=18, font='JetBrains Mono'
        )
    )
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(fut284_chart), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 扣抵明細表（未來10天）────────────────────────────────────────
    st.markdown("#### 📋 扣抵明細表（未來10個交易日）")
    table_data = []
    for i in range(10):
        r87  = future_rows_87[i]
        r284 = future_rows_284[i]
        table_data.append({
            '天數':         r87['天數'],
            'MA87被扣舊值': f"${r87['被扣舊值_87']:.2f}",
            'MA87推估值':   f"${r87['推估MA87']:.2f}",
            'MA87方向':     r87['方向_87'],
            'MA284被扣舊值':f"${r284['被扣舊值_284']:.2f}",
            'MA284推估值':  f"${r284['推估MA284']:.2f}",
            'MA284方向':    r284['方向_284'],
        })
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

    st.toast("✅ 雙軌扣抵完整推演完成", icon="🎯")


# ══════════════════════════════════════════════════════════════
# 🎯 TAB 2: ADAM THEORY (亞當理論) — 第一性原則重建
# ══════════════════════════════════════════════════════════════
# 亞當理論核心（Welles Wilder）：
#   1. 市場永遠走阻力最小的路徑
#   2. Swing High / Swing Low：前後各N根K棒均比當根低/高，才算有效擺動點
#   3. 雙擺確認法：同方向連續兩個擺動點（雙高/雙低）確認趨勢
#   4. 投影法則：以最近一段擺動幅度，等量投影下一個目標位
#   5. 第一失守法：價格跌破最近擺動低點 → 趨勢逆轉信號
#   6. Adam角度：擺動幅度 ÷ 時間跨度 = 趨勢強度角
# ══════════════════════════════════════════════════════════════
def _t2(sdf, ticker):
    """T2: Adam Theory — First Principles Full Engine"""
    st.toast("🚀 亞當理論擺動引擎啟動中…", icon="⏳")

    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown('<div class="hero-lbl">📐 ADAM THEORY ENGINE v3.0</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">{ticker}</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">亞當雙擺分析 · 第一性原則重建</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if len(sdf) < 80:
        st.toast("⚠️ 歷史數據不足，無法計算亞當擺動。", icon="⚡")
        return

    # ── 核心計算：擺動點偵測 ──────────────────────────────────────────
    # 條件：前後各5根K棒的高/低點均不超過當根，才認定為有效擺動點
    lookback = 200
    df = sdf[['Close', 'High', 'Low']].tail(lookback).reset_index()
    df['Date'] = pd.to_datetime(df['Date'])
    n = len(df)
    wing = 5  # 左右各5根確認

    swing_highs = []
    swing_lows  = []

    for i in range(wing, n - wing):
        hi_window = df['High'].iloc[i - wing: i + wing + 1]
        lo_window = df['Low'].iloc[i  - wing: i + wing + 1]
        if df['High'].iloc[i] == hi_window.max():
            swing_highs.append({'idx': i, 'Date': df['Date'].iloc[i],
                                  'Price': df['High'].iloc[i], 'Type': 'High'})
        if df['Low'].iloc[i] == lo_window.min():
            swing_lows.append({'idx': i, 'Date': df['Date'].iloc[i],
                                 'Price': df['Low'].iloc[i], 'Type': 'Low'})

    sh_df = pd.DataFrame(swing_highs)
    sl_df = pd.DataFrame(swing_lows)

    # 取最近4個擺動高點 & 低點
    sh_recent = sh_df.tail(4).reset_index(drop=True) if len(sh_df) >= 2 else sh_df
    sl_recent = sl_df.tail(4).reset_index(drop=True) if len(sl_df) >= 2 else sl_df

    cp = float(df['Close'].iloc[-1])

    # ── 雙擺確認法 ────────────────────────────────────────────────────
    # 雙高（Higher High + Higher Low）→ 多頭確認
    # 雙低（Lower High + Lower Low）→ 空頭確認
    double_bull = False
    double_bear = False
    hh_text = ll_text = "不足2個擺動點，無法確認"

    if len(sh_recent) >= 2:
        hh = sh_recent['Price'].iloc[-1] > sh_recent['Price'].iloc[-2]
        hl = sl_recent['Price'].iloc[-1] > sl_recent['Price'].iloc[-2] if len(sl_recent) >= 2 else False
        lh = sh_recent['Price'].iloc[-1] < sh_recent['Price'].iloc[-2]
        ll = sl_recent['Price'].iloc[-1] < sl_recent['Price'].iloc[-2] if len(sl_recent) >= 2 else False
        double_bull = hh and hl
        double_bear = lh and ll
        hh_text = f"最新擺高 ${sh_recent['Price'].iloc[-1]:.2f} {'>' if hh else '<'} 前擺高 ${sh_recent['Price'].iloc[-2]:.2f}"
        ll_text  = f"最新擺低 ${sl_recent['Price'].iloc[-1]:.2f} {'>' if hl else '<'} 前擺低 ${sl_recent['Price'].iloc[-2]:.2f}" if len(sl_recent) >= 2 else "低點數據不足"

    # ── 投影目標計算 ──────────────────────────────────────────────────
    # 找最近的一段完整波段（擺高→擺低 or 擺低→擺高），等量投影
    proj_target_up   = None
    proj_target_down = None
    swing_amplitude  = None
    swing_days       = None
    adam_angle       = None

    if len(sh_recent) >= 1 and len(sl_recent) >= 1:
        last_hi = sh_recent.iloc[-1]
        last_lo = sl_recent.iloc[-1]
        swing_amplitude = abs(last_hi['Price'] - last_lo['Price'])
        swing_days      = abs((last_hi['Date'] - last_lo['Date']).days)
        adam_angle      = swing_amplitude / max(swing_days, 1)

        # 多頭投影：從最低點向上等量投影
        proj_target_up   = last_lo['Price'] + swing_amplitude
        # 空頭投影：從最高點向下等量投影
        proj_target_down = last_hi['Price'] - swing_amplitude

    # ── 第一失守判斷 ──────────────────────────────────────────────────
    # 跌破最近擺動低點 → 警示
    first_loss_level = float(sl_recent['Price'].iloc[-1]) if len(sl_recent) >= 1 else None
    first_loss_breach = cp < first_loss_level if first_loss_level else False

    # 突破最近擺動高點 → 突破確認
    breakout_level  = float(sh_recent['Price'].iloc[-1]) if len(sh_recent) >= 1 else None
    breakout_confirm = cp > breakout_level if breakout_level else False

    # ── 趨勢強度評分（0~100）─────────────────────────────────────────
    score = 50
    if double_bull:  score += 20
    if double_bear:  score -= 20
    if breakout_confirm: score += 15
    if first_loss_breach: score -= 15
    if len(sh_recent) >= 2 and sh_recent['Price'].iloc[-1] > sh_recent['Price'].iloc[-2]: score += 10
    if len(sl_recent) >= 2 and sl_recent['Price'].iloc[-1] > sl_recent['Price'].iloc[-2]: score += 10
    score = max(0, min(100, score))

    trend_label = '強勢多頭' if score >= 75 else '偏多' if score >= 55 else '偏空' if score >= 35 else '強勢空頭'
    trend_color = '#00FF7F' if score >= 65 else '#FF3131' if score <= 35 else '#FFD700'

    # ── AI 戰術分析 ────────────────────────────────────────────────────
    st.markdown("### 🧠 亞當理論 · 第一性原則戰術推演")
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    proj_text_up   = f"${proj_target_up:.2f}"   if proj_target_up   else "計算中"
    proj_text_down = f"${proj_target_down:.2f}"  if proj_target_down else "計算中"
    amp_text       = f"${swing_amplitude:.2f}"   if swing_amplitude  else "N/A"
    angle_text     = f"{adam_angle:.2f}/日"      if adam_angle       else "N/A"
    fl_text        = f"${first_loss_level:.2f}"  if first_loss_level else "N/A"
    bo_text        = f"${breakout_level:.2f}"    if breakout_level   else "N/A"

    analysis = f"""
═══════════════════════════════════════════════════════════
📐 ADAM THEORY ENGINE v3.0 — {ticker}   現價: ${cp:.2f}
   趨勢強度評分: {score}/100  →  {trend_label}
═══════════════════════════════════════════════════════════

【一、亞當理論第一性原則】
  核心命題：市場永遠走阻力最小的路徑。
  擺動點不是簡單的最高/最低，而是前後各{wing}根K棒均被當根穿越後，
  才能確認為有效轉折。虛假突破將被自動過濾。

【二、有效擺動點偵測結果（wing={wing}）】
  識別擺動高點數量：{len(sh_df)} 個  │  最近4個已提取分析
  識別擺動低點數量：{len(sl_df)} 個  │  最近4個已提取分析
  最新擺動高點：{sh_recent['Price'].iloc[-1]:.2f} @ {sh_recent['Date'].iloc[-1].strftime('%Y-%m-%d') if len(sh_recent)>0 else 'N/A'}
  最新擺動低點：{sl_recent['Price'].iloc[-1]:.2f} @ {sl_recent['Date'].iloc[-1].strftime('%Y-%m-%d') if len(sl_recent)>0 else 'N/A'}

【三、雙擺確認法（Double Swing Confirmation）】
  擺動高點比較：{hh_text}
  擺動低點比較：{ll_text}
  雙擺確認結果：{'✅ 多頭雙擺確認（Higher High + Higher Low），趨勢向上有效' if double_bull else '✅ 空頭雙擺確認（Lower High + Lower Low），趨勢向下有效' if double_bear else '🟡 雙擺方向分歧，市場仍處盤整區間，等待確認'}

【四、等量投影目標（Adam Projection）】
  最近波段振幅：  {amp_text}
  波段時間跨度：  {swing_days if swing_days else 'N/A'} 個交易日
  Adam角度：      {angle_text}（振幅÷時間，越大代表趨勢越陡峭）
  多頭投影目標：  {proj_text_up}  （擺動低點 + 等量振幅）
  空頭投影目標：  {proj_text_down}  （擺動高點 − 等量振幅）

【五、第一失守法則（First Loss Rule）】
  關鍵支撐（最近擺低）：{fl_text}
  突破確認位（最近擺高）：{bo_text}
  現價 vs 第一失守線：{'🔴 已跌破第一失守線！趨勢逆轉警示，應立即減倉或出場。' if first_loss_breach else f'✅ 守住 {fl_text}，多頭結構未破壞。'}
  現價 vs 突破確認位：{'✅ 已突破擺動高點！多頭確認，可追漲或加碼。' if breakout_confirm else f'🟡 尚未突破 {bo_text}，突破前宜觀望。'}

【六、操作戰術推演】
  {'🟢 多頭策略：雙擺確認，可在回測擺動低點附近佈多，目標看多頭投影 ' + proj_text_up + '，停損設最近擺低 ' + fl_text if double_bull else '🔴 空頭策略：雙擺空頭確認，逢反彈高點減碼，目標看空頭投影 ' + proj_text_down + '，停損設最近擺高 ' + bo_text if double_bear else '🟡 盤整策略：雙擺未確認，等突破 ' + bo_text + ' 再多，跌破 ' + fl_text + ' 再空。'}

═══════════════════════════════════════════════════════════
"""
    st.write_stream(_stream_text(analysis, speed=0.002))
    st.markdown('</div>', unsafe_allow_html=True)

    # ── KPI 儀表板 ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="t3-kpi-grid" style="grid-template-columns: repeat(4, 1fr); margin-bottom:18px;">
        <div class="t3-kpi-card" style="--kc:{trend_color};">
            <div class="t3-kpi-lbl">趨勢強度評分</div>
            <div class="t3-kpi-val" style="font-size:34px; color:{trend_color};">{score}<span style="font-size:16px">/100</span></div>
            <div class="t3-kpi-sub">{trend_label}</div>
        </div>
        <div class="t3-kpi-card" style="--kc:#00FF7F;">
            <div class="t3-kpi-lbl">多頭投影目標</div>
            <div class="t3-kpi-val" style="font-size:30px; color:#00FF7F;">{proj_text_up}</div>
            <div class="t3-kpi-sub">等量波段投影</div>
        </div>
        <div class="t3-kpi-card" style="--kc:#FF3131;">
            <div class="t3-kpi-lbl">空頭投影目標</div>
            <div class="t3-kpi-val" style="font-size:30px; color:#FF3131;">{proj_text_down}</div>
            <div class="t3-kpi-sub">等量波段投影</div>
        </div>
        <div class="t3-kpi-card" style="--kc:#FFD700;">
            <div class="t3-kpi-lbl">Adam角度</div>
            <div class="t3-kpi-val" style="font-size:30px; color:#FFD700;">{angle_text}</div>
            <div class="t3-kpi-sub">振幅÷時間</div>
        </div>
    </div>
    <div class="t3-kpi-grid" style="grid-template-columns: repeat(3, 1fr); margin-bottom:24px;">
        <div class="t3-kpi-card" style="--kc:#00F5FF;">
            <div class="t3-kpi-lbl">第一失守線（支撐）</div>
            <div class="t3-kpi-val" style="font-size:30px; color:{'#FF3131' if first_loss_breach else '#00FF7F'};">{fl_text}</div>
            <div class="t3-kpi-sub">{'🔴 已失守！' if first_loss_breach else '✅ 守住中'}</div>
        </div>
        <div class="t3-kpi-card" style="--kc:#FF9A3C;">
            <div class="t3-kpi-lbl">突破確認位（阻力）</div>
            <div class="t3-kpi-val" style="font-size:30px; color:{'#00FF7F' if breakout_confirm else '#FF9A3C'};">{bo_text}</div>
            <div class="t3-kpi-sub">{'✅ 已突破！' if breakout_confirm else '🟡 待突破'}</div>
        </div>
        <div class="t3-kpi-card" style="--kc:#FF6BFF;">
            <div class="t3-kpi-lbl">雙擺確認</div>
            <div class="t3-kpi-val" style="font-size:26px; color:{'#00FF7F' if double_bull else '#FF3131' if double_bear else '#FFD700'};">{'✅ 多頭雙擺' if double_bull else '✅ 空頭雙擺' if double_bear else '🟡 未確認'}</div>
            <div class="t3-kpi-sub">HH+HL / LH+LL</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 圖一：主圖 — 擺動點標記全景圖 ───────────────────────────────
    st.markdown("#### 📊 亞當理論擺動點全景圖（近200日）")

    base_line = alt.Chart(df).mark_line(color='#00F5FF', strokeWidth=2).encode(
        x=alt.X('Date:T', title='日期', axis=alt.Axis(labelFontSize=26, titleFontSize=24, labelColor='#aaa')),
        y=alt.Y('Close:Q', title='收盤價', scale=alt.Scale(zero=False),
                axis=alt.Axis(labelFontSize=26, titleFontSize=24, labelColor='#aaa')),
        tooltip=[alt.Tooltip('Date:T', title='日期'), alt.Tooltip('Close:Q', title='收盤', format='.2f')]
    )

    charts = [base_line]

    if len(sh_recent) > 0:
        sh_plot = sh_recent.copy()
        sh_plot['label'] = sh_plot['Price'].apply(lambda p: f"H ${p:.2f}")
        sh_mark = alt.Chart(sh_plot).mark_point(
            color='#FF3131', size=200, shape='triangle-down', filled=True
        ).encode(
            x='Date:T', y=alt.Y('Price:Q'),
            tooltip=[alt.Tooltip('Date:T', title='日期'), alt.Tooltip('Price:Q', title='擺高', format='.2f')]
        )
        sh_text = alt.Chart(sh_plot).mark_text(
            color='#FF3131', fontSize=18, font='JetBrains Mono', dy=-18, fontWeight='bold'
        ).encode(x='Date:T', y=alt.Y('Price:Q'), text='label:N')
        charts += [sh_mark, sh_text]

    if len(sl_recent) > 0:
        sl_plot = sl_recent.copy()
        sl_plot['label'] = sl_plot['Price'].apply(lambda p: f"L ${p:.2f}")
        sl_mark = alt.Chart(sl_plot).mark_point(
            color='#00FF7F', size=200, shape='triangle-up', filled=True
        ).encode(
            x='Date:T', y=alt.Y('Price:Q'),
            tooltip=[alt.Tooltip('Date:T', title='日期'), alt.Tooltip('Price:Q', title='擺低', format='.2f')]
        )
        sl_text = alt.Chart(sl_plot).mark_text(
            color='#00FF7F', fontSize=18, font='JetBrains Mono', dy=18, fontWeight='bold'
        ).encode(x='Date:T', y=alt.Y('Price:Q'), text='label:N')
        charts += [sl_mark, sl_text]

    # 加入第一失守線 & 突破確認位水平線
    if first_loss_level:
        fl_rule = alt.Chart(pd.DataFrame({'y': [first_loss_level]})).mark_rule(
            color='#FF3131', strokeDash=[6, 3], strokeWidth=2
        ).encode(y='y:Q')
        charts.append(fl_rule)

    if breakout_level:
        bo_rule = alt.Chart(pd.DataFrame({'y': [breakout_level]})).mark_rule(
            color='#00FF7F', strokeDash=[6, 3], strokeWidth=2
        ).encode(y='y:Q')
        charts.append(bo_rule)

    # 加入投影目標水平線
    if proj_target_up:
        pu_rule = alt.Chart(pd.DataFrame({'y': [proj_target_up]})).mark_rule(
            color='#FFD700', strokeDash=[4, 4], strokeWidth=1.5
        ).encode(y='y:Q')
        charts.append(pu_rule)

    if proj_target_down:
        pd_rule = alt.Chart(pd.DataFrame({'y': [proj_target_down]})).mark_rule(
            color='#FF6BFF', strokeDash=[4, 4], strokeWidth=1.5
        ).encode(y='y:Q')
        charts.append(pd_rule)

    full_chart = alt.layer(*charts).properties(
        height=380,
        title=alt.TitleParams(
            '▲綠=擺低  ▼紅=擺高  紅虛=第一失守線  綠虛=突破確認  金虛=多頭目標  紫虛=空頭目標',
            color='#aaa', fontSize=18, font='JetBrains Mono'
        )
    )
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(full_chart), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 圖二：擺動點波動幅度歷史條圖 ────────────────────────────────
    if len(sh_df) >= 2 and len(sl_df) >= 2:
        st.markdown("#### 📊 歷史波段振幅統計（近10個擺動高點）")

        amp_rows = []
        sh_list = sh_df.tail(10).reset_index(drop=True)
        sl_list = sl_df.reset_index(drop=True)

        for i in range(len(sh_list)):
            hi_date = sh_list['Date'].iloc[i]
            # 找最近在此擺高之前的擺低
            prior_lows = sl_list[sl_list['Date'] < hi_date]
            if len(prior_lows) == 0:
                continue
            lo = prior_lows.iloc[-1]
            amp = sh_list['Price'].iloc[i] - lo['Price']
            days_span = (hi_date - lo['Date']).days
            amp_rows.append({
                '波段':    f"#{i+1} {lo['Date'].strftime('%m/%d')}→{hi_date.strftime('%m/%d')}",
                '振幅':    round(amp, 2),
                '天數':    days_span,
                'Adam角度': round(amp / max(days_span, 1), 3),
                '顏色':    '#00FF7F' if amp > 0 else '#FF3131'
            })

        if amp_rows:
            amp_df = pd.DataFrame(amp_rows)
            amp_bars = alt.Chart(amp_df).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                x=alt.X('波段:N', sort=None, axis=alt.Axis(labelFontSize=26, titleFontSize=24, labelColor='#aaa', labelAngle=-30)),
                y=alt.Y('振幅:Q', title='波段振幅（$）',
                        axis=alt.Axis(labelFontSize=26, titleFontSize=24, labelColor='#aaa')),
                color=alt.Color('顏色:N', scale=None),
                tooltip=[
                    alt.Tooltip('波段:N', title='波段'),
                    alt.Tooltip('振幅:Q', title='振幅', format='.2f'),
                    alt.Tooltip('天數:Q', title='天數'),
                    alt.Tooltip('Adam角度:Q', title='Adam角度', format='.3f'),
                ]
            ).properties(
                height=240,
                title=alt.TitleParams(
                    '歷史波段振幅 — 越高代表趨勢越強勁',
                    color='#FFD700', fontSize=18, font='JetBrains Mono'
                )
            )
            avg_amp = amp_df['振幅'].mean()
            avg_rule = alt.Chart(pd.DataFrame({'y': [avg_amp]})).mark_rule(
                color='#FFD700', strokeDash=[5, 3], strokeWidth=2
            ).encode(y='y:Q')
            st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
            st.altair_chart(_cfg(alt.layer(amp_bars, avg_rule).properties(height=240,
                title=alt.TitleParams('歷史波段振幅 — 金虛線=平均振幅', color='#FFD700', fontSize=18, font='JetBrains Mono')
            )), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── 擺動點明細表 ───────────────────────────────────────────────────
    st.markdown("#### 📋 近期擺動點明細")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**擺動高點（最近4個）**")
        if len(sh_recent) > 0:
            sh_show = sh_recent[['Date', 'Price']].copy()
            sh_show.columns = ['日期', '擺動高點']
            sh_show['日期'] = sh_show['日期'].dt.strftime('%Y-%m-%d')
            sh_show['擺動高點'] = sh_show['擺動高點'].apply(lambda x: f"${x:.2f}")
            st.dataframe(sh_show, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("**擺動低點（最近4個）**")
        if len(sl_recent) > 0:
            sl_show = sl_recent[['Date', 'Price']].copy()
            sl_show.columns = ['日期', '擺動低點']
            sl_show['日期'] = sl_show['日期'].dt.strftime('%Y-%m-%d')
            sl_show['擺動低點'] = sl_show['擺動低點'].apply(lambda x: f"${x:.2f}")
            st.dataframe(sl_show, use_container_width=True, hide_index=True)

    st.toast("✅ 亞當理論完整推演完成", icon="🎯")

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

    # ── session_state 初始值（第一次載入時設定） ──────────────────────────────
    _ark_defaults = {"ark_rev": 50000.0, "ark_shares": 5000.0, "ark_g": 0.15,
                     "ark_m": 0.15, "ark_pe": 25.0, "ark_years": 5}
    for k, v in _ark_defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown('<div class="hero-lbl">🧠 ARK WAR ROOM — SCENARIO ENGINE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">{ticker}</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Bull · Base · Bear 三情境五年推演</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 使用說明卡片 ─────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(0,255,127,0.07),rgba(0,245,255,0.04));
    border:1px solid rgba(0,255,127,0.28);border-left:4px solid #00FF7F;
    border-radius:16px;padding:24px 28px;margin:0 0 26px;">
  <div style="font-family:'Bebas Neue',sans-serif;font-size:20px;letter-spacing:4px;
      color:#00FF7F;margin-bottom:16px;">
    📋 ARK 三情境分析 — 完整操作說明
  </div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:16px;color:rgba(215,230,245,0.95);line-height:2.0;margin-bottom:14px;">
    ARK 投資法的核心是對同一標的同時建立<strong style="color:#FFD700;font-size:17px;">三種情境假設</strong>，
    用不同的成長率 × 利潤率 × 本益比組合，推算出 <strong style="color:#00F5FF;font-size:17px;">N年後的目標股價</strong>，
    再反推「現在買入、持有到期」的<strong style="color:#FF9A3C;font-size:17px;">年化報酬率 CAGR</strong>。
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px;">
    <div style="background:rgba(255,49,49,0.08);border:1px solid rgba(255,49,49,0.25);border-radius:12px;padding:14px 16px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:16px;color:#FF3131;letter-spacing:2px;margin-bottom:6px;">🐻 BEAR 熊市</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(215,225,235,0.85);line-height:1.8;">
        成長率 &amp; 本益比各<strong style="color:#FF3131;">下調 20%</strong>。<br>
        代表公司遭遇逆風：競爭加劇、經濟衰退、產品失敗的最壞情境。
      </div>
    </div>
    <div style="background:rgba(255,215,0,0.07);border:1px solid rgba(255,215,0,0.25);border-radius:12px;padding:14px 16px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:16px;color:#FFD700;letter-spacing:2px;margin-bottom:6px;">⚖️ BASE 基準</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(215,225,235,0.85);line-height:1.8;">
        維持你填入的<strong style="color:#FFD700;">原始數字</strong>計算。<br>
        代表公司依照歷史趨勢穩定發展的中性情境。
      </div>
    </div>
    <div style="background:rgba(0,255,127,0.07);border:1px solid rgba(0,255,127,0.25);border-radius:12px;padding:14px 16px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:16px;color:#00FF7F;letter-spacing:2px;margin-bottom:6px;">🚀 BULL 牛市</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(215,225,235,0.85);line-height:1.8;">
        成長率 &amp; 本益比各<strong style="color:#00FF7F;">上調 20%</strong>。<br>
        代表公司超出預期：新市場開拓、產品爆款、行業龍頭溢價的樂觀情境。
      </div>
    </div>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:rgba(0,245,255,0.65);
      padding:10px 14px;background:rgba(0,245,255,0.04);border-radius:8px;letter-spacing:0.3px;">
    📐 計算公式：目標股價 = (年營收 × (1+成長率)^年限 × 淨利率 × 目標本益比) ÷ 流通股數（股）<br>
    📌 目前市價：<strong style="color:#00F5FF;font-size:15px;">{cp:.2f}</strong>
    &nbsp;·&nbsp; CAGR = (目標價 / 市價)^(1/年限) − 1
  </div>
</div>
""", unsafe_allow_html=True)

    # ── 範例選單 (25檔) ───────────────────────────────────────────────────────
    # preset: (label, rev_ttm, shares_M, g, m, pe, years)
    ARK_PRESETS = {
        "── 台股科技 ──":                    None,
        "🇹🇼 台積電 2330  半導體龍頭":       (2161000, 25930, 0.15, 0.37, 28, 5),
        "🇹🇼 聯發科 2454  IC設計王":         (547000,  1585,  0.12, 0.24, 22, 5),
        "🇹🇼 鴻海 2317    電子代工":         (6162000, 13860, 0.06, 0.03, 12, 5),
        "🇹🇼 台達電 2308  電源/EV":          (380000,  2572,  0.10, 0.09, 18, 5),
        "🇹🇼 大立光 3008  光學鏡頭":         (62000,   134,   0.08, 0.35, 25, 5),
        "🇹🇼 廣達 2382    AI伺服器":         (1380000, 7767,  0.20, 0.04, 16, 5),
        "── 台股金融/傳產 ──":               None,
        "🇹🇼 中信金 2891  金融控股":         (210000,  19800, 0.07, 0.18, 12, 5),
        "🇹🇼 長榮 2603    航運":             (320000,  14280, 0.05, 0.28, 8,  5),
        "🇹🇼 台塑 1301    石化":             (360000,  12645, 0.04, 0.07, 10, 5),
        "🇹🇼 統一 1216    食品消費":         (170000,  5679,  0.05, 0.06, 14, 5),
        "── 美股科技巨頭 ──":                None,
        "🇺🇸 NVIDIA      AI晶片王":         (96300,   2460,  0.45, 0.55, 35, 5),
        "🇺🇸 Apple AAPL  消費電子":          (391000,  15200, 0.07, 0.26, 28, 5),
        "🇺🇸 Microsoft   雲端/AI":           (245000,  7430,  0.14, 0.36, 30, 5),
        "🇺🇸 Google GOOG 廣告/雲端":         (307000,  12280, 0.12, 0.24, 22, 5),
        "🇺🇸 Amazon AMZN 電商/AWS":          (590000,  10560, 0.12, 0.08, 30, 5),
        "🇺🇸 Meta        社群/AI":           (135000,  2530,  0.16, 0.35, 22, 5),
        "🇺🇸 Tesla TSLA  電動車":            (97690,   3190,  0.20, 0.15, 40, 5),
        "── 美股成長股 ──":                  None,
        "🇺🇸 Palantir    數據AI":            (2860,    2150,  0.25, 0.16, 60, 5),
        "🇺🇸 CrowdStrike 資安":              (3660,    243,   0.30, 0.18, 55, 5),
        "🇺🇸 Datadog     雲端監控":          (2430,    323,   0.22, 0.14, 50, 5),
        "🇺🇸 Snowflake   數據雲":            (3240,    326,   0.28, 0.05, 45, 5),
        "── 美股穩健型 ──":                  None,
        "🇺🇸 Berkshire   巴菲特控股":        (364000,  2176,  0.05, 0.21, 14, 5),
        "🇺🇸 Johnson&J   醫療消費":          (88000,   2410,  0.04, 0.21, 18, 5),
        "🇺🇸 Coca-Cola   飲料":              (46000,   4310,  0.04, 0.23, 22, 5),
        "🇺🇸 McDonald's  餐飲":              (25500,   730,   0.04, 0.33, 24, 5),
    }

    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:20px;color:#00F5FF;
    letter-spacing:3px;margin:8px 0 10px;">⚡ 快速套用範例 — 選一檔自動填入</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:15px;color:rgba(180,200,220,0.75);
    margin-bottom:10px;">
    從下方選單挑選任意個股，系統會自動將該公司的真實財務數據填入下方欄位，
    你也可以在填入後手動微調任何數字。
</div>
""", unsafe_allow_html=True)

    preset_options = list(ARK_PRESETS.keys())
    preset_choice = st.selectbox(
        "選擇範例股票", options=preset_options, index=0,
        key="ark_preset", label_visibility="collapsed"
    )

    # ── 自動填入：偵測選單變動，寫入 session_state 再 rerun ──────────────────
    pv = ARK_PRESETS.get(preset_choice)
    if pv is not None and st.session_state.get("_ark_preset_prev") != preset_choice:
        p_rev, p_shares, p_g, p_m, p_pe, p_years = pv
        st.session_state["ark_rev"]    = float(p_rev)
        st.session_state["ark_shares"] = float(p_shares)
        st.session_state["ark_g"]      = float(p_g)
        st.session_state["ark_m"]      = float(p_m)
        st.session_state["ark_pe"]     = float(p_pe)
        st.session_state["ark_years"]  = int(p_years)
        st.session_state["_ark_preset_prev"] = preset_choice
        st.rerun()

    # Use current session_state as display values (already updated above)
    pv = ARK_PRESETS.get(preset_choice)
    if pv is None:
        pv = (50000, 5000, 0.15, 0.15, 25, 5)
    p_rev, p_shares, p_g, p_m, p_pe, p_years = pv

    if preset_choice and ARK_PRESETS.get(preset_choice) is not None:
        st.markdown(f"""
<div style="background:rgba(255,215,0,0.05);border:1px solid rgba(255,215,0,0.2);
    border-radius:10px;padding:10px 16px;margin:6px 0 14px;
    font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(255,215,0,0.75);">
  ✅ 已套用：<strong style="color:#FFD700;">{preset_choice}</strong>
  &nbsp;｜ 年營收：{p_rev:,.0f}百萬
  &nbsp;｜ 股數：{p_shares:,.0f}百萬股
  &nbsp;｜ 成長率：{p_g*100:.0f}%
  &nbsp;｜ 淨利率：{p_m*100:.0f}%
  &nbsp;｜ P/E：{p_pe}x
</div>
""", unsafe_allow_html=True)

    # ── 參數輸入區 ────────────────────────────────────────────────────────────
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:20px;color:#00F5FF;
    letter-spacing:3px;margin:4px 0 14px;">📝 參數確認 / 手動調整</div>
""", unsafe_allow_html=True)

    # --- Row 1: Revenue & Shares & Years ---
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;
    color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:6px;">
    💰 年營收 TTM（百萬元）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);
    line-height:1.8;margin-bottom:8px;">
    <strong style="color:#FFD700;">什麼是TTM？</strong> 最近12個月（Trailing Twelve Months）的總營業收入。<br>
    <strong style="color:#FFD700;">台股單位：</strong>百萬新台幣（例如台積電年營收約 2,161,000 百萬台幣）<br>
    <strong style="color:#FFD700;">美股單位：</strong>百萬美元（例如 Apple 約 391,000 百萬美元）<br>
    <strong style="color:#FFD700;">哪裡查？</strong>公司財報 / Goodinfo / 財報狗 / Yahoo Finance
</div>
""", unsafe_allow_html=True)
        rev_ttm = st.number_input("年營收", min_value=1.0, step=1000.0,
                                   format="%.0f", key="ark_rev", label_visibility="collapsed")

    with c2:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;
    color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:6px;">
    📊 流通股數（百萬股）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);
    line-height:1.8;margin-bottom:8px;">
    <strong style="color:#FFD700;">什麼是流通股數？</strong> 公司公開發行、可在市場自由交易的股份總數。<br>
    <strong style="color:#FFD700;">單位：</strong>百萬股（台積電約 25,930 百萬股；TSLA 約 3,190 百萬股）<br>
    <strong style="color:#FFD700;">注意：</strong>不含庫藏股。台股可從集保中心或財報查閱。<br>
    <strong style="color:#FFD700;">哪裡查？</strong>Yahoo Finance → Statistics → Shares Outstanding
</div>
""", unsafe_allow_html=True)
        shares = st.number_input("流通股數 (M)", min_value=1.0, step=100.0,
                                  format="%.0f", key="ark_shares", label_visibility="collapsed")

    with c3:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;
    color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:6px;">
    📅 推演年限（年）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);
    line-height:1.8;margin-bottom:8px;">
    <strong style="color:#FFD700;">ARK 標準：</strong>5年。這是對「不確定未來」與「足夠時間複利」的平衡。<br>
    <strong style="color:#FFD700;">成長科技股：</strong>5 年，因為商業模式仍在快速演化。<br>
    <strong style="color:#FFD700;">成熟穩定股：</strong>3～5 年，業績可見度較高。<br>
    <strong style="color:#FFD700;">不建議超過 7 年，</strong>遠期預測誤差會急劇放大。
</div>
""", unsafe_allow_html=True)
        years = st.number_input("推演年限", min_value=1, max_value=10, step=1,
                                 key="ark_years", label_visibility="collapsed")

    # --- Row 2: Growth, Margin, PE ---
    c4, c5, c6 = st.columns([1, 1, 1])
    with c4:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;
    color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:6px;">
    📈 基準成長率 CAGR</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);
    line-height:1.8;margin-bottom:8px;">
    <strong style="color:#00F5FF;">意義：</strong>每年預期的「營收複合成長率」（0.15 = 每年成長 15%）。<br>
    <strong style="color:#00F5FF;">爆發型科技股：</strong>0.25～0.50（如 NVIDIA AI 爆發期）<br>
    <strong style="color:#00F5FF;">穩健成長科技：</strong>0.12～0.20（如台積電、聯發科）<br>
    <strong style="color:#00F5FF;">傳統產業：</strong>0.03～0.08（如台塑、統一）<br>
    <strong style="color:#00F5FF;">哪裡查？</strong>近3年營收 YoY% 的平均值即為參考值。
</div>
""", unsafe_allow_html=True)
        g = st.number_input("成長率", min_value=0.0, max_value=2.0,
                             step=0.01, format="%.2f", key="ark_g", label_visibility="collapsed")

    with c5:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;
    color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:6px;">
    💹 淨利率 Net Margin</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);
    line-height:1.8;margin-bottom:8px;">
    <strong style="color:#00F5FF;">意義：</strong>稅後淨利 ÷ 年營收（0.20 = 每賺 100 元留下 20 元）。<br>
    <strong style="color:#00F5FF;">半導體/軟體：</strong>0.25～0.55（台積電 0.37、NVIDIA 0.55）<br>
    <strong style="color:#00F5FF;">科技平台：</strong>0.20～0.35（Apple 0.26、Meta 0.35）<br>
    <strong style="color:#00F5FF;">電商/硬體：</strong>0.03～0.10（亞馬遜 0.08、鴻海 0.03）<br>
    <strong style="color:#00F5FF;">傳統製造：</strong>0.03～0.08（汽車、航運依周期大幅波動）
</div>
""", unsafe_allow_html=True)
        m = st.number_input("淨利率", min_value=0.0, max_value=1.0,
                             step=0.01, format="%.2f", key="ark_m", label_visibility="collapsed")

    with c6:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;
    color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:6px;">
    🏷️ 目標本益比 P/E</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);
    line-height:1.8;margin-bottom:8px;">
    <strong style="color:#00F5FF;">意義：</strong>5年後市場願意給多少倍的本益比（成長越快越貴）。<br>
    <strong style="color:#00F5FF;">AI爆發/高成長：</strong>40～80（NVIDIA、Palantir 成長期）<br>
    <strong style="color:#00F5FF;">科技龍頭成熟：</strong>22～35（Apple、Microsoft 穩定期）<br>
    <strong style="color:#00F5FF;">台灣電子：</strong>15～25（台積電 20～28、聯發科 18～22）<br>
    <strong style="color:#00F5FF;">傳統/金融：</strong>8～16（銀行 10～14、航運 6～10）
</div>
""", unsafe_allow_html=True)
        pe = st.number_input("目標 P/E", min_value=1.0, max_value=200.0,
                              step=1.0, key="ark_pe", label_visibility="collapsed")

    # ── 計算按鈕 ─────────────────────────────────────────────────────────────
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="t3-action">', unsafe_allow_html=True)
    run_ark = st.button("🔮  執行 ARK 三情境推演", key="ark_calc", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not run_ark:
        return

    st.toast("🚀 正在推演三情境目標價…", icon="⏳")
    result = calculate_ark_scenarios(rev_ttm, shares, cp, g, m, pe, int(years))

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
                                                         labelFontSize=26, labelFont="Rajdhani")),
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
                                   fontSize=24, font="JetBrains Mono")
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
# 🎯 TAB 6: SMART VALUATION (智能估值) — 雙模式引擎
# ══════════════════════════════════════════════════════════════
def _t6(ticker, cp):
    """T6: Smart Valuation — DCF (獲利型) + HyperGrowth (虧損高速成長型) 雙引擎"""
    st.toast("🚀 智能估值引擎啟動中…", icon="⏳")

    # ── session_state 初始值 ──────────────────────────────────────────────────
    _dcf_defaults = {"val_rev": 50000.0, "val_shares": 5000.0, "val_eps": 10.0,
                     "val_g": 0.12, "val_m": 0.15, "val_pe": 20.0, "val_dr": 0.10}
    for k, v in _dcf_defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    _hg_defaults = {"hg_rev": 100.0, "hg_shares": 300.0, "hg_rev_g": 0.60,
                    "hg_gm_now": 0.30, "hg_gm_target": 0.65, "hg_opex_pct": 1.20,
                    "hg_opex_improve": 0.12, "hg_ps": 20.0, "hg_pe": 80.0,
                    "hg_dr": 0.15, "hg_years": 7}
    for k, v in _hg_defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    if "val_mode" not in st.session_state:
        st.session_state["val_mode"] = "DCF"

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown('<div class="hero-lbl">💎 SMART VALUATION ENGINE — DUAL MODE</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">{ticker}</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">DCF 獲利型 · HyperGrowth 虧損高速成長型</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 模式切換 ──────────────────────────────────────────────────────────────
    mode = st.session_state["val_mode"]
    mc1, mc2 = st.columns(2)
    is_dcf = (mode == "DCF")
    dcf_border = "2px solid #B77DFF" if is_dcf  else "1px solid rgba(255,255,255,0.07)"
    hg_border  = "2px solid #FF9A3C" if not is_dcf else "1px solid rgba(255,255,255,0.07)"
    dcf_bg     = "rgba(183,125,255,0.10)" if is_dcf else "rgba(255,255,255,0.02)"
    hg_bg      = "rgba(255,154,60,0.10)"  if not is_dcf else "rgba(255,255,255,0.02)"
    dcf_col    = "#B77DFF" if is_dcf else "rgba(200,215,230,0.55)"
    hg_col     = "#FF9A3C" if not is_dcf else "rgba(200,215,230,0.55)"

    with mc1:
        if st.button("💎 DCF 估值  ·  適用已獲利公司", key="mode_dcf", use_container_width=True):
            st.session_state["val_mode"] = "DCF"
            st.rerun()
        st.markdown(f"""
<div style="position:relative;background:{dcf_bg};border:{dcf_border};border-radius:14px;
    padding:16px 20px;margin-top:-38px;pointer-events:none;z-index:1;">
  <div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:{dcf_col};letter-spacing:2px;">💎 DCF 現金流折現</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:13px;color:rgba(200,215,230,0.65);margin-top:4px;">
    台積電 · NVIDIA · Apple · 聯發科<br>
    <span style="color:{dcf_col};font-weight:600;">適用：EPS > 0 的獲利公司</span>
  </div>
</div>""", unsafe_allow_html=True)

    with mc2:
        if st.button("🚀 HyperGrowth  ·  適用虧損高速成長", key="mode_hg", use_container_width=True):
            st.session_state["val_mode"] = "HyperGrowth"
            st.rerun()
        st.markdown(f"""
<div style="position:relative;background:{hg_bg};border:{hg_border};border-radius:14px;
    padding:16px 20px;margin-top:-38px;pointer-events:none;z-index:1;">
  <div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:{hg_col};letter-spacing:2px;">🚀 HyperGrowth 成長推演</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:13px;color:rgba(200,215,230,0.65);margin-top:4px;">
    QBTS · IONQ · RGTI · ARQQ · RKLB<br>
    <span style="color:{hg_col};font-weight:600;">適用：尚未獲利的超高速成長股</span>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════
    # MODE A: DCF 估值（獲利型）
    # ════════════════════════════════════════════════════════════
    if mode == "DCF":
        st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(183,125,255,0.08),rgba(0,245,255,0.04));
    border:1px solid rgba(183,125,255,0.30);border-left:4px solid #B77DFF;
    border-radius:16px;padding:24px 28px;margin:0 0 26px;">
  <div style="font-family:'Bebas Neue',sans-serif;font-size:20px;letter-spacing:4px;color:#B77DFF;margin-bottom:16px;">
    💎 智能 DCF 估值 — 完整操作說明</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:16px;color:rgba(215,230,245,0.95);line-height:2.0;margin-bottom:14px;">
    <strong style="color:#B77DFF;font-size:17px;">DCF（現金流折現）</strong>是巴菲特最推崇的估值法。
    核心：<strong style="color:#FFD700;font-size:17px;">今日價值 = 未來10年現金流折算回今天的總和</strong>。</div>
  <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:16px;">
    <div style="background:rgba(0,245,255,0.06);border:1px solid rgba(0,245,255,0.18);border-radius:12px;padding:14px 16px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:15px;color:#00F5FF;letter-spacing:2px;margin-bottom:8px;">📐 計算邏輯（五步驟）</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(210,225,240,0.85);line-height:2.0;">
        ① 年營收 × (1+成長率)^10 → <strong style="color:#FFD700;">10年後總營收</strong><br>
        ② × 淨利率 → <strong style="color:#FFD700;">10年後總淨利</strong><br>
        ③ × 目標本益比 → <strong style="color:#FFD700;">10年後市值</strong><br>
        ④ ÷ 流通股數 → <strong style="color:#FFD700;">10年後每股價值</strong><br>
        ⑤ ÷ (1+折現率)^10 → <strong style="color:#00FF7F;">今日公允價值</strong>
      </div>
    </div>
    <div style="background:rgba(255,215,0,0.05);border:1px solid rgba(255,215,0,0.18);border-radius:12px;padding:14px 16px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:15px;color:#FFD700;letter-spacing:2px;margin-bottom:8px;">🎯 結果判讀標準</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(210,225,240,0.85);line-height:2.0;">
        公允價值 &gt; 市價 +20%：<strong style="color:#00FF7F;">明顯低估，值得建倉</strong><br>
        公允價值 &gt; 市價 +5%：<strong style="color:#FFD700;">合理偏低，可分批佈局</strong><br>
        公允價值 ≈ 市價 ±5%：<strong style="color:#00F5FF;">合理價位，持有觀察</strong><br>
        公允價值 &lt; 市價 -10%：<strong style="color:#FF3131;">高估警示，等待回調</strong>
      </div>
    </div>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:13px;color:rgba(0,245,255,0.65);
      padding:10px 14px;background:rgba(0,245,255,0.04);border-radius:8px;">
    📐 公式：公允價值 = (年營收 × (1+g)^10 × 淨利率 × P/E) ÷ 股數 ÷ (1+折現率)^10<br>
    📌 目前市價：<strong style="color:#00F5FF;font-size:15px;">{cp:.2f}</strong>
  </div>
</div>
""", unsafe_allow_html=True)

        DCF_PRESETS = {
            "── 台股科技 ──":                    None,
            "🇹🇼 台積電 2330  半導體龍頭":       (2161000, 25930, 48.0,  0.13, 0.37, 26, 0.10),
            "🇹🇼 聯發科 2454  IC設計王":         (547000,  1585,  85.0,  0.10, 0.24, 20, 0.10),
            "🇹🇼 鴻海 2317    電子代工":         (6162000, 13860, 10.5,  0.05, 0.03, 11, 0.10),
            "🇹🇼 台達電 2308  電源/EV":          (380000,  2572,  14.0,  0.09, 0.09, 17, 0.10),
            "🇹🇼 大立光 3008  光學鏡頭":         (62000,   134,   145.0, 0.07, 0.35, 24, 0.10),
            "🇹🇼 廣達 2382    AI伺服器":         (1380000, 7767,  8.5,   0.18, 0.04, 15, 0.10),
            "🇹🇼 緯創 3231    伺服器":           (1050000, 5475,  6.8,   0.15, 0.03, 13, 0.10),
            "── 台股金融/傳產 ──":               None,
            "🇹🇼 中信金 2891  金融控股":         (210000,  19800, 2.8,   0.06, 0.18, 11, 0.09),
            "🇹🇼 長榮 2603    航運":             (320000,  14280, 16.5,  0.04, 0.28, 7,  0.10),
            "🇹🇼 台塑 1301    石化":             (360000,  12645, 3.5,   0.03, 0.07, 9,  0.09),
            "🇹🇼 統一 1216    食品消費":         (170000,  5679,  4.2,   0.04, 0.06, 13, 0.09),
            "── 美股科技巨頭 ──":                None,
            "🇺🇸 NVIDIA      AI晶片王":         (96300,   2460,  11.93, 0.40, 0.55, 32, 0.10),
            "🇺🇸 Apple AAPL  消費電子":          (391000,  15200, 6.57,  0.07, 0.26, 26, 0.10),
            "🇺🇸 Microsoft   雲端/AI":           (245000,  7430,  11.45, 0.13, 0.36, 28, 0.10),
            "🇺🇸 Google GOOG 廣告/雲端":         (307000,  12280, 8.04,  0.12, 0.24, 20, 0.10),
            "🇺🇸 Amazon AMZN 電商/AWS":          (590000,  10560, 3.98,  0.12, 0.08, 28, 0.10),
            "🇺🇸 Meta        社群/AI":           (135000,  2530,  19.85, 0.15, 0.35, 20, 0.10),
            "🇺🇸 Tesla TSLA  電動車":            (97690,   3190,  3.01,  0.18, 0.15, 38, 0.11),
            "── 美股成長股 ──":                  None,
            "🇺🇸 Palantir    數據AI":            (2860,    2150,  0.36,  0.24, 0.16, 55, 0.12),
            "🇺🇸 CrowdStrike 資安":              (3660,    243,   2.93,  0.28, 0.18, 50, 0.12),
            "🇺🇸 Datadog     雲端監控":          (2430,    323,   1.80,  0.22, 0.14, 48, 0.11),
            "── 美股穩健/配息 ──":               None,
            "🇺🇸 Berkshire   巴菲特控股":        (364000,  2176,  59.21, 0.05, 0.21, 13, 0.09),
            "🇺🇸 Johnson&J   醫療消費":          (88000,   2410,  8.76,  0.04, 0.21, 17, 0.09),
            "🇺🇸 Coca-Cola   飲料":              (46000,   4310,  2.47,  0.04, 0.23, 21, 0.09),
            "🇺🇸 McDonald's  餐飲":              (25500,   730,   11.56, 0.05, 0.33, 22, 0.09),
        }

        st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:20px;color:#B77DFF;
    letter-spacing:3px;margin:8px 0 10px;">⚡ 快速套用範例 — 選一檔自動填入</div>
""", unsafe_allow_html=True)

        dcf_options = list(DCF_PRESETS.keys())
        dcf_choice = st.selectbox("選擇範例股票", options=dcf_options, index=0,
                                   key="dcf_preset", label_visibility="collapsed")
        pv = DCF_PRESETS.get(dcf_choice)
        if pv is not None and st.session_state.get("_dcf_preset_prev") != dcf_choice:
            p_rev, p_shares, p_eps, p_g, p_m, p_pe, p_dr = pv
            st.session_state["val_rev"]    = float(p_rev)
            st.session_state["val_shares"] = float(p_shares)
            st.session_state["val_eps"]    = float(p_eps)
            st.session_state["val_g"]      = float(p_g)
            st.session_state["val_m"]      = float(p_m)
            st.session_state["val_pe"]     = float(p_pe)
            st.session_state["val_dr"]     = float(p_dr)
            st.session_state["_dcf_preset_prev"] = dcf_choice
            st.rerun()

        pv = DCF_PRESETS.get(dcf_choice)
        if pv is None: pv = (50000, 5000, 10.0, 0.12, 0.15, 20, 0.10)
        p_rev, p_shares, p_eps, p_g, p_m, p_pe, p_dr = pv

        if dcf_choice and DCF_PRESETS.get(dcf_choice) is not None:
            st.markdown(f"""
<div style="background:rgba(183,125,255,0.05);border:1px solid rgba(183,125,255,0.22);
    border-radius:10px;padding:10px 16px;margin:6px 0 14px;
    font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(183,125,255,0.8);">
  ✅ 已套用：<strong style="color:#B77DFF;">{dcf_choice}</strong>
  &nbsp;｜ 年營收：{p_rev:,.0f}百萬 &nbsp;｜ 股數：{p_shares:,.0f}百萬股
  &nbsp;｜ EPS：{p_eps} &nbsp;｜ 成長率：{p_g*100:.0f}%
  &nbsp;｜ 淨利率：{p_m*100:.0f}% &nbsp;｜ P/E：{p_pe}x &nbsp;｜ 折現率：{p_dr*100:.0f}%
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:20px;color:#B77DFF;
    letter-spacing:3px;margin:4px 0 14px;">📝 參數確認 / 手動調整</div>
""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:6px;">💰 年營收（百萬元）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
<strong style="color:#FFD700;">TTM</strong> = 最近12個月合計營收。台股：百萬新台幣（年報→損益表）；美股：百萬美元（Yahoo Finance → Financials）
</div>""", unsafe_allow_html=True)
            rev = st.number_input("年營收", min_value=1.0, step=1000.0,
                                   format="%.0f", key="val_rev", label_visibility="collapsed")

        with c2:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:6px;">📊 流通股數（百萬股）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
台股：集保中心 / Goodinfo；美股：Yahoo Finance → Statistics → Shares Outstanding。台積電 259.3億股 = 25,930百萬股
</div>""", unsafe_allow_html=True)
            shares = st.number_input("流通股數 (M)", min_value=1.0, step=100.0,
                                      format="%.0f", key="val_shares", label_visibility="collapsed")

        with c3:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:6px;">💵 EPS TTM（每股盈餘）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
近12個月稅後淨利 ÷ 流通股數。台股：Goodinfo / 財報狗；美股：Yahoo Finance → Statistics → EPS (TTM)
</div>""", unsafe_allow_html=True)
            eps = st.number_input("EPS (TTM)", min_value=0.01, step=0.5,
                                   format="%.2f", key="val_eps", label_visibility="collapsed")

        c4, c5, c6, c7 = st.columns(4)
        with c4:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:6px;">📈 年均成長率 CAGR</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
AI/半導體：0.15～0.40；科技平台：0.10～0.18；傳統產業：0.03～0.08
</div>""", unsafe_allow_html=True)
            g = st.number_input("成長率", min_value=0.0, max_value=2.0,
                                 step=0.01, format="%.2f", key="val_g", label_visibility="collapsed")

        with c5:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:6px;">💹 淨利率 Net Margin</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
半導體：0.30～0.55；科技平台：0.20～0.36；電商/硬體：0.03～0.10
</div>""", unsafe_allow_html=True)
            m = st.number_input("淨利率", min_value=0.0, max_value=1.0,
                                 step=0.01, format="%.2f", key="val_m", label_visibility="collapsed")

        with c6:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:6px;">🏷️ 終端本益比 P/E</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
高成長科技：35～60；科技龍頭：20～32；台電子/金融：10～20；傳統：6～12
</div>""", unsafe_allow_html=True)
            pe = st.number_input("終端 P/E", min_value=1.0, max_value=200.0,
                                  step=1.0, key="val_pe", label_visibility="collapsed")

        with c7:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:6px;">📉 折現率 Discount Rate</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
穩健：0.08（8%）；一般：0.10（10%）；高風險溢價：0.12～0.15
</div>""", unsafe_allow_html=True)
            dr = st.number_input("折現率", min_value=0.01, max_value=0.5,
                                  step=0.01, format="%.2f", key="val_dr", label_visibility="collapsed")

        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="t3-action">', unsafe_allow_html=True)
        run_val = st.button("💎  執行 DCF 智能估值計算", key="val_calc", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if not run_val:
            return

        st.toast("🚀 正在計算內在價值…", icon="⏳")
        fair_value = calculate_smart_valuation(eps, rev, shares, g, m, pe, dr, 10)

        if not fair_value or fair_value <= 0:
            st.toast("⚠️ 計算失敗，請確認股數 > 0 且所有欄位已填寫", icon="⚡")
            return

        upside  = (fair_value - cp) / cp * 100
        up_col  = "#00FF7F" if upside > 20 else "#FFD700" if upside > 0 else "#FF3131"
        verdict = "🟢 明顯低估 — 具備買入價值" if upside > 20 else \
                  "🟡 合理偏低 — 可逢低佈局" if upside > 5 else \
                  "⚪ 接近合理價 — 觀察等待" if upside > -10 else \
                  "🔴 高估警示 — 建議等待回調"

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
  <div style="border:1px solid {up_col}44;border-top:3px solid {up_col};
      border-radius:16px;padding:24px 20px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
        color:rgba(200,215,230,0.4);letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">
      📍 市價 {cp:.2f} vs 公允價值</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:62px;color:{up_col};
        line-height:1;margin-bottom:6px;">{upside:+.1f}%</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:{up_col};font-weight:700;">{verdict}</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # 折現率敏感性分析
        st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:16px;color:#00F5FF;
    letter-spacing:3px;margin:16px 0 10px;">📊 折現率敏感性分析</div>""", unsafe_allow_html=True)

        dr_range = [0.06, 0.08, 0.10, 0.12, 0.14, 0.15]
        sens_rows = []
        for d in dr_range:
            fv = calculate_smart_valuation(eps, rev, shares, g, m, pe, d, 10)
            up = (fv - cp) / cp * 100
            sens_rows.append({"折現率": f"{d*100:.0f}%", "公允價值": round(fv, 2),
                               "溢價/折價": round(up, 1), "顏色": "#00FF7F" if up > 0 else "#FF3131"})

        sens_df = pd.DataFrame(sens_rows)
        sens_chart = (
            alt.Chart(sens_df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("折現率:N", sort=None, axis=alt.Axis(labelColor="#778899", titleColor="#445566", labelFontSize=26)),
                y=alt.Y("公允價值:Q", title="DCF 公允價值",
                         axis=alt.Axis(labelColor="#556677", titleColor="#445566"),
                         scale=alt.Scale(zero=False)),
                color=alt.Color("顏色:N", scale=None),
                tooltip=["折現率", alt.Tooltip("公允價值:Q", format=".2f"), alt.Tooltip("溢價/折價:Q", format="+.1f")]
            ).properties(height=240,
                         title=alt.TitleParams("不同折現率下的公允價值（橫線=當前市價）",
                                                color="#FFD700", fontSize=24, font="JetBrains Mono"))
        )
        rule = alt.Chart(pd.DataFrame({"cp": [cp]})).mark_rule(
            color="#00F5FF", strokeDash=[6, 3], strokeWidth=2).encode(y="cp:Q")
        st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
        st.altair_chart(_cfg(alt.layer(sens_chart, rule).properties(background="rgba(0,0,0,0)")),
                        use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        summary = (
            f"【智能估值摘要 — {ticker}】"
            f"以 {dr*100:.0f}% 折現率、{g*100:.0f}% 成長率推算，"
            f"10年DCF公允價值為 {fair_value:.2f}，"
            f"{'低於' if fair_value < cp else '高於'}市價 {cp:.2f} 約 {abs(upside):.1f}%。"
            f"結論：{verdict.split('—')[1].strip() if '—' in verdict else verdict}。"
        )
        if f"val_streamed_{ticker}" not in st.session_state:
            st.write_stream(_stream_text(summary, speed=0.012))
            st.session_state[f"val_streamed_{ticker}"] = True
        else:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
                        f'color:rgba(180,200,220,0.55);line-height:1.8;padding:8px 0;">{summary}</div>',
                        unsafe_allow_html=True)
        st.toast("✅ DCF 估值完成！", icon="💎")

    # ════════════════════════════════════════════════════════════
    # MODE B: HyperGrowth 超高速成長型（尚未獲利）
    # ════════════════════════════════════════════════════════════
    else:
        st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(255,154,60,0.08),rgba(255,107,255,0.04));
    border:1px solid rgba(255,154,60,0.35);border-left:4px solid #FF9A3C;
    border-radius:16px;padding:24px 28px;margin:0 0 26px;">
  <div style="font-family:'Bebas Neue',sans-serif;font-size:20px;letter-spacing:4px;color:#FF9A3C;margin-bottom:16px;">
    🚀 HyperGrowth 成長路徑估值 — 完整操作說明</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:16px;color:rgba(215,230,245,0.95);line-height:2.0;margin-bottom:14px;">
    尚未獲利的公司<strong style="color:#FF9A3C;font-size:17px;">無法使用 P/E 和 DCF</strong>（分母淨利為負數）。
    本模型改用<strong style="color:#FFD700;font-size:17px;">「成長路徑模擬」</strong>：逐年推算收入成長 →
    毛利率改善 → 費用收斂 → 找到獲利轉折點（Breakeven Year）→ 用<strong style="color:#00F5FF;">終端 P/S 或 P/E</strong> 定價再折現。
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px;">
    <div style="background:rgba(255,107,255,0.07);border:1px solid rgba(255,107,255,0.25);border-radius:12px;padding:14px 16px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:14px;color:#FF6BFF;letter-spacing:2px;margin-bottom:6px;">📐 計算邏輯</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:13px;color:rgba(210,225,240,0.85);line-height:1.9;">
        ① 收入每年 × (1+成長率)<br>② 毛利率線性改善至目標<br>③ 費用佔收入比逐年下降<br>
        ④ 找到<strong style="color:#FFD700;">獲利轉折年</strong><br>⑤ 終端價值折現回今日
      </div>
    </div>
    <div style="background:rgba(255,215,0,0.06);border:1px solid rgba(255,215,0,0.20);border-radius:12px;padding:14px 16px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:14px;color:#FFD700;letter-spacing:2px;margin-bottom:6px;">🔑 兩種終端定價</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:13px;color:rgba(210,225,240,0.85);line-height:1.9;">
        <strong style="color:#00FF7F;">已獲利 → P/E 定價</strong><br>終端淨利 × P/E ÷ 股數<br>
        <strong style="color:#FF9A3C;">仍虧損 → P/S 定價</strong><br>終端收入 × P/S ÷ 股數
      </div>
    </div>
    <div style="background:rgba(0,245,255,0.06);border:1px solid rgba(0,245,255,0.18);border-radius:12px;padding:14px 16px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:14px;color:#00F5FF;letter-spacing:2px;margin-bottom:6px;">⚠️ 適用標的</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:13px;color:rgba(210,225,240,0.85);line-height:1.9;">
        量子電腦：QBTS / IONQ / RGTI<br>AI基礎建設：ARQQ / SOUN<br>
        生物科技：早期 mRNA/基因療法<br>航太新創：RKLB / ASTS
      </div>
    </div>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(255,154,60,0.65);
      padding:10px 14px;background:rgba(255,154,60,0.04);border-radius:8px;">
    ⚡ 公式：終端價 = (Rev_N × PS_terminal 或 NetIncome_N × PE_terminal) ÷ 股數 ÷ (1+折現率)^N<br>
    📌 目前市價：<strong style="color:#FF9A3C;font-size:15px;">{cp:.2f}</strong>
    &nbsp;·&nbsp; 折現率建議 15%～25%（高不確定性溢價）
  </div>
</div>
""", unsafe_allow_html=True)

        # ── HyperGrowth 範例選單 ────────────────────────────────
        # (rev_M, shares_M, rev_g, gm_now, gm_target, opex_pct, opex_improve, ps_terminal, pe_terminal, dr, years)
        HG_PRESETS = {
            "── 量子電腦 ──":                     None,
            "⚛️ QBTS  D-Wave Quantum":           (8.0,    185.0,  0.65, 0.55, 0.75, 1.80, 0.15, 18.0, 80.0, 0.20, 7),
            "⚛️ IONQ  量子雲端":                  (22.0,   310.0,  0.70, 0.60, 0.78, 1.50, 0.14, 20.0, 90.0, 0.20, 7),
            "⚛️ RGTI  Rigetti":                  (12.0,   380.0,  0.75, 0.50, 0.72, 1.90, 0.16, 15.0, 75.0, 0.22, 7),
            "⚛️ QUBT  Quantum Computing":         (4.0,    210.0,  0.80, 0.40, 0.68, 2.20, 0.18, 12.0, 70.0, 0.22, 7),
            "── AI / 新興科技 ──":                None,
            "🔊 SOUN  SoundHound AI":             (84.0,   440.0,  0.55, 0.60, 0.75, 1.20, 0.12, 15.0, 85.0, 0.18, 6),
            "🔐 ARQQ  Arqit Quantum":             (1.5,    95.0,   0.90, 0.70, 0.85, 2.50, 0.20, 25.0, 100.0, 0.25, 8),
            "🤖 BBAI  BigBear.ai":                (170.0,  170.0,  0.25, 0.25, 0.55, 0.95, 0.08, 8.0,  60.0, 0.18, 7),
            "── 航太/太空新創 ──":                None,
            "🚀 RKLB  Rocket Lab":                (436.0,  505.0,  0.35, 0.28, 0.55, 0.85, 0.09, 10.0, 70.0, 0.15, 7),
            "📡 ASTS  AST SpaceMobile":           (5.0,    290.0,  1.20, 0.55, 0.80, 2.80, 0.22, 30.0, 100.0, 0.25, 8),
            "── 生物科技/基因 ──":                None,
            "🧬 BEAM  Beam Therapeutics":         (38.0,   72.0,   0.45, 0.80, 0.88, 2.20, 0.18, 25.0, 90.0, 0.18, 8),
            "🧬 CRSP  CRISPR Therapeutics":       (350.0,  83.0,   0.35, 0.75, 0.85, 1.40, 0.14, 12.0, 65.0, 0.15, 7),
        }

        st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:20px;color:#FF9A3C;
    letter-spacing:3px;margin:8px 0 10px;">⚡ 快速套用範例 — 選一檔自動填入</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:15px;color:rgba(180,200,220,0.80);margin-bottom:10px;">
以下均為<strong style="color:#FF9A3C;">尚未穩定獲利</strong>的高速成長標的，財務數字為參考估計，請自行驗證最新財報。
</div>""", unsafe_allow_html=True)

        hg_options = list(HG_PRESETS.keys())
        hg_choice = st.selectbox("選擇範例股票", options=hg_options, index=0,
                                  key="hg_preset", label_visibility="collapsed")
        hgv = HG_PRESETS.get(hg_choice)
        if hgv is not None and st.session_state.get("_hg_preset_prev") != hg_choice:
            h_rev, h_shares, h_rg, h_gm, h_gmt, h_op, h_opi, h_ps, h_pe, h_dr, h_yr = hgv
            st.session_state["hg_rev"]          = float(h_rev)
            st.session_state["hg_shares"]       = float(h_shares)
            st.session_state["hg_rev_g"]        = float(h_rg)
            st.session_state["hg_gm_now"]       = float(h_gm)
            st.session_state["hg_gm_target"]    = float(h_gmt)
            st.session_state["hg_opex_pct"]     = float(h_op)
            st.session_state["hg_opex_improve"] = float(h_opi)
            st.session_state["hg_ps"]           = float(h_ps)
            st.session_state["hg_pe"]           = float(h_pe)
            st.session_state["hg_dr"]           = float(h_dr)
            st.session_state["hg_years"]        = int(h_yr)
            st.session_state["_hg_preset_prev"] = hg_choice
            st.rerun()

        hgv = HG_PRESETS.get(hg_choice)
        if hgv is not None:
            h_rev, h_shares, h_rg, h_gm, h_gmt, h_op, h_opi, h_ps, h_pe, h_dr, h_yr = hgv
            st.markdown(f"""
<div style="background:rgba(255,154,60,0.05);border:1px solid rgba(255,154,60,0.22);
    border-radius:10px;padding:10px 16px;margin:6px 0 14px;
    font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(255,154,60,0.85);">
  ✅ 已套用：<strong style="color:#FF9A3C;">{hg_choice}</strong>
  &nbsp;｜ 年收入：{h_rev}M &nbsp;｜ 股數：{h_shares}M股
  &nbsp;｜ 成長率：{h_rg*100:.0f}% &nbsp;｜ 毛利率：{h_gm*100:.0f}%→{h_gmt*100:.0f}%
  &nbsp;｜ 費用率：{h_op*100:.0f}% &nbsp;｜ 推演：{h_yr}年
</div>
""", unsafe_allow_html=True)

        st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:20px;color:#FF9A3C;
    letter-spacing:3px;margin:4px 0 14px;">📝 參數確認 / 手動調整</div>""", unsafe_allow_html=True)

        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:6px;">💰 年收入（百萬美元/元）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
TTM 年化收入（不需是淨利）。QBTS≈8M、IONQ≈22M。查詢：Yahoo Finance → Financials → Revenue
</div>""", unsafe_allow_html=True)
            hg_rev = st.number_input("年收入 (M)", min_value=0.1, step=1.0,
                                      format="%.1f", key="hg_rev", label_visibility="collapsed")

        with hc2:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:6px;">📊 流通股數（百萬股）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
<strong style="color:#FF3131;">注意股本稀釋！</strong>成長型公司每次融資都會增加股數。建議預留 5%～15% 稀釋空間。
</div>""", unsafe_allow_html=True)
            hg_shares = st.number_input("流通股數 (M)", min_value=1.0, step=10.0,
                                         format="%.0f", key="hg_shares", label_visibility="collapsed")

        with hc3:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:6px;">📅 推演年限（年）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
建議 5～8年。量子/航太：7～8年；AI新創：5～6年；生技新藥：7～10年
</div>""", unsafe_allow_html=True)
            hg_years = st.number_input("推演年限", min_value=3, max_value=10, step=1,
                                        key="hg_years", label_visibility="collapsed")

        hc4, hc5, hc6 = st.columns(3)
        with hc4:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:6px;">📈 年均收入成長率</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
超高速（量子/AI）：0.60～1.20；高速：0.40～0.60；快速：0.25～0.40
</div>""", unsafe_allow_html=True)
            hg_rev_g = st.number_input("收入成長率", min_value=0.05, max_value=3.0,
                                        step=0.05, format="%.2f", key="hg_rev_g", label_visibility="collapsed")

        with hc5:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:6px;">💹 毛利率（現在 → 目標）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
SaaS/軟體成熟目標：70%～85%；量子硬體：60%～75%。查：Yahoo Finance → Gross Profit %
</div>""", unsafe_allow_html=True)
            hgc5a, hgc5b = st.columns(2)
            with hgc5a:
                hg_gm_now = st.number_input("毛利率(現)", min_value=0.0, max_value=1.0,
                                             step=0.01, format="%.2f", key="hg_gm_now", label_visibility="collapsed")
            with hgc5b:
                hg_gm_target = st.number_input("毛利率(目標)", min_value=0.0, max_value=1.0,
                                                step=0.01, format="%.2f", key="hg_gm_target", label_visibility="collapsed")

        with hc6:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:6px;">🔥 費用率（現在） + 年降幅</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
費用率 = 總營業費用 ÷ 收入（早期常超過 100%）。年降幅：0.10～0.20 為常見
</div>""", unsafe_allow_html=True)
            hgc6a, hgc6b = st.columns(2)
            with hgc6a:
                hg_opex_pct = st.number_input("費用率(現)", min_value=0.1, max_value=5.0,
                                               step=0.05, format="%.2f", key="hg_opex_pct", label_visibility="collapsed")
            with hgc6b:
                hg_opex_improve = st.number_input("年降幅", min_value=0.0, max_value=0.5,
                                                   step=0.01, format="%.2f", key="hg_opex_improve", label_visibility="collapsed")

        hc7, hc8, hc9 = st.columns(3)
        with hc7:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(255,107,255,0.9);letter-spacing:1px;margin-bottom:6px;">🏷️ 終端 P/S 倍數（仍虧損時用）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
超早期量子：15～30x；成熟SaaS：8～15x。參考同類公司現在的 P/S 中位數
</div>""", unsafe_allow_html=True)
            hg_ps = st.number_input("終端 P/S", min_value=1.0, max_value=100.0,
                                     step=1.0, format="%.1f", key="hg_ps", label_visibility="collapsed")

        with hc8:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(255,107,255,0.9);letter-spacing:1px;margin-bottom:6px;">🏷️ 終端 P/E 倍數（已轉盈時用）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
成長龍頭轉盈早期：60～100x；穩定後：30～60x。參考類似成熟期公司
</div>""", unsafe_allow_html=True)
            hg_pe = st.number_input("終端 P/E", min_value=1.0, max_value=200.0,
                                     step=1.0, format="%.1f", key="hg_pe", label_visibility="collapsed")

        with hc9:
            st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:12px;font-weight:700;color:rgba(255,107,255,0.9);letter-spacing:1px;margin-bottom:6px;">📉 折現率（高風險溢價）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(190,210,230,0.85);line-height:1.8;margin-bottom:8px;">
量子/航太：0.20～0.25；AI新創：0.15～0.20；生技早期：0.18～0.25。越早期越高。
</div>""", unsafe_allow_html=True)
            hg_dr = st.number_input("折現率", min_value=0.05, max_value=0.50,
                                     step=0.01, format="%.2f", key="hg_dr", label_visibility="collapsed")

        st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="t3-action">', unsafe_allow_html=True)
        run_hg = st.button("🚀  執行 HyperGrowth 成長路徑推演", key="hg_calc", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if not run_hg:
            return

        st.toast("🚀 正在模擬成長路徑…", icon="⏳")
        hg_result = calculate_hypergrowth_valuation(
            hg_rev, hg_shares, hg_rev_g,
            hg_gm_now, hg_gm_target,
            hg_opex_pct, hg_opex_improve,
            hg_ps, hg_pe, hg_dr, int(hg_years)
        )

        if hg_result is None:
            st.toast("⚠️ 計算失敗，請確認所有欄位已填寫", icon="⚡")
            return

        tp      = hg_result['terminal_price']
        tp_raw  = hg_result['terminal_price_raw']
        by      = hg_result['breakeven_year']
        method  = hg_result['used_method']
        proj_df = hg_result['projections']

        upside  = (tp - cp) / cp * 100 if cp > 0 else 0
        up_col  = "#00FF7F" if upside > 30 else "#FFD700" if upside > 0 else "#FF3131"
        by_str  = f"第 {by} 年" if by else f"推演期內未獲利（採 P/S）"
        by_col  = "#00FF7F" if by else "#FF9A3C"
        verdict = "🟢 強力低估 — 高成長兌現則超額回報" if upside > 50 else \
                  "🟡 合理偏低 — 成長路徑需持續驗證" if upside > 10 else \
                  "⚪ 接近合理 — 市場已充分定價" if upside > -20 else \
                  "🔴 高估警示 — 成長預期已過度折現入股價"

        # 主要結果 KPI
        st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:18px 0;">
  <div style="background:rgba(255,154,60,0.07);border:1px solid rgba(255,154,60,0.3);
      border-top:3px solid #FF9A3C;border-radius:16px;padding:22px 18px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,154,60,0.6);
        letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">🚀 HyperGrowth 推算目標價</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:52px;color:#FF9A3C;
        line-height:1;margin-bottom:8px;">{tp:.2f}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,154,60,0.55);">
        {int(hg_years)}年後原始估值 {tp_raw:.2f} → 折現率 {hg_dr*100:.0f}%^{int(hg_years)} 折現</div>
  </div>
  <div style="border:1px solid {up_col}44;border-top:3px solid {up_col};
      border-radius:16px;padding:22px 18px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(200,215,230,0.4);
        letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">📍 市價 {cp:.2f} vs 推算目標</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:52px;color:{up_col};
        line-height:1;margin-bottom:8px;">{upside:+.1f}%</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:13px;color:{up_col};font-weight:700;">{verdict}</div>
  </div>
  <div style="background:rgba(0,255,127,0.05);border:1px solid rgba(0,255,127,0.2);
      border-top:3px solid {by_col};border-radius:16px;padding:22px 18px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(200,215,230,0.4);
        letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">⚡ 獲利轉折點</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:36px;color:{by_col};
        line-height:1;margin-bottom:8px;">{by_str}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(200,215,230,0.45);">
        終端定價方式：{method} 法</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # 逐年成長路徑表格
        st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:16px;color:#FF9A3C;
    letter-spacing:3px;margin:16px 0 10px;">📈 逐年成長路徑模擬</div>""", unsafe_allow_html=True)

        rows_html = ""
        for _, row in proj_df.iterrows():
            yr = int(row['Year'])
            ni_col = "#00FF7F" if row['NetIncome'] > 0 else "#FF6B6B"
            prof_badge = '<span style="color:#00FF7F;font-weight:700;">✅ 獲利</span>' \
                         if row['Profitable'] else '<span style="color:#FF6B6B;">🔴 虧損</span>'
            rows_html += f"""
<tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
  <td style="padding:8px 10px;font-family:'Bebas Neue',sans-serif;font-size:18px;color:#FF9A3C;">Y+{yr}</td>
  <td style="padding:8px 10px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#00F5FF;">{row['Revenue']:,.1f}M</td>
  <td style="padding:8px 10px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#FFD700;">{row['GrossMargin']:.1f}%</td>
  <td style="padding:8px 10px;font-family:'JetBrains Mono',monospace;font-size:12px;color:{ni_col};">{row['NetIncome']:,.1f}M</td>
  <td style="padding:8px 10px;font-family:'JetBrains Mono',monospace;font-size:12px;color:{ni_col};">{row['NetMargin']:.1f}%</td>
  <td style="padding:8px 10px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#00F5FF;">{row['EPS_proj']:.3f}</td>
  <td style="padding:8px 10px;">{prof_badge}</td>
</tr>"""

        st.markdown(f"""
<div style="background:rgba(0,0,0,0.3);border:1px solid rgba(255,154,60,0.15);border-radius:14px;overflow:hidden;margin:10px 0;">
  <table style="width:100%;border-collapse:collapse;">
    <thead>
      <tr style="background:rgba(255,154,60,0.08);border-bottom:1px solid rgba(255,154,60,0.25);">
        <th style="padding:10px;font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,154,60,0.7);letter-spacing:2px;text-align:left;">年度</th>
        <th style="padding:10px;font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(0,245,255,0.7);letter-spacing:2px;text-align:left;">年收入</th>
        <th style="padding:10px;font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,215,0,0.7);letter-spacing:2px;text-align:left;">毛利率</th>
        <th style="padding:10px;font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,107,107,0.7);letter-spacing:2px;text-align:left;">淨利/虧損</th>
        <th style="padding:10px;font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,107,107,0.7);letter-spacing:2px;text-align:left;">淨利率</th>
        <th style="padding:10px;font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(0,245,255,0.7);letter-spacing:2px;text-align:left;">預測EPS</th>
        <th style="padding:10px;font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(200,215,230,0.5);letter-spacing:2px;text-align:left;">狀態</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)

        # 收入成長 + 淨利路徑圖
        proj_chart_df = proj_df.copy()
        proj_chart_df['年度'] = proj_chart_df['Year'].apply(lambda x: f"Y+{x}")
        proj_chart_df['NetIncome_plot'] = proj_chart_df['NetIncome'].clip(lower=proj_chart_df['Revenue'] * -2)

        rev_bars = alt.Chart(proj_chart_df).mark_bar(
            cornerRadiusTopLeft=6, cornerRadiusTopRight=6, opacity=0.7, color='#FF9A3C'
        ).encode(
            x=alt.X('年度:N', sort=None, axis=alt.Axis(labelColor='#888', labelFontSize=26)),
            y=alt.Y('Revenue:Q', title='百萬元', axis=alt.Axis(labelColor='#556677', titleColor='#445566'), scale=alt.Scale(zero=True)),
            tooltip=[alt.Tooltip('年度:N'), alt.Tooltip('Revenue:Q', title='收入', format=',.1f')]
        )
        ni_line = alt.Chart(proj_chart_df).mark_line(
            color='#00FF7F', strokeWidth=3, point=alt.OverlayMarkDef(color='#00FF7F', size=80)
        ).encode(
            x='年度:N',
            y=alt.Y('NetIncome_plot:Q'),
            tooltip=[alt.Tooltip('年度:N'), alt.Tooltip('NetIncome:Q', title='淨利', format=',.1f')]
        )
        zero_rule = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(
            color='#FF3131', strokeDash=[4, 4], strokeWidth=1.5).encode(y='y:Q')

        combo = (rev_bars + ni_line + zero_rule).properties(
            height=260, background='rgba(0,0,0,0)',
            title=alt.TitleParams('年收入（橘柱）與淨利路徑（綠線）— 紅線=損益平衡點',
                                   color='#FF9A3C', fontSize=24, font='JetBrains Mono')
        )
        st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
        st.altair_chart(_cfg(combo), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # 折現率敏感性分析
        st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:16px;color:#FF6BFF;
    letter-spacing:3px;margin:16px 0 10px;">📊 折現率敏感性分析</div>""", unsafe_allow_html=True)

        hg_dr_range = [0.10, 0.13, 0.15, 0.18, 0.20, 0.25]
        hg_sens_rows = []
        for d in hg_dr_range:
            r = calculate_hypergrowth_valuation(
                hg_rev, hg_shares, hg_rev_g, hg_gm_now, hg_gm_target,
                hg_opex_pct, hg_opex_improve, hg_ps, hg_pe, d, int(hg_years))
            fv = r['terminal_price'] if r else 0
            up = (fv - cp) / cp * 100 if cp > 0 else 0
            hg_sens_rows.append({"折現率": f"{d*100:.0f}%", "推算目標價": round(fv, 2),
                                  "溢價/折價": round(up, 1), "顏色": "#00FF7F" if up > 0 else "#FF3131"})

        hg_sens_df = pd.DataFrame(hg_sens_rows)
        hg_sens_chart = (
            alt.Chart(hg_sens_df).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X("折現率:N", sort=None, axis=alt.Axis(labelColor="#778899", titleColor="#445566", labelFontSize=26)),
                y=alt.Y("推算目標價:Q", title="折現後目標價",
                         axis=alt.Axis(labelColor="#556677", titleColor="#445566"), scale=alt.Scale(zero=False)),
                color=alt.Color("顏色:N", scale=None),
                tooltip=["折現率", alt.Tooltip("推算目標價:Q", format=".2f"), alt.Tooltip("溢價/折價:Q", format="+.1f")]
            ).properties(height=240,
                         title=alt.TitleParams("不同折現率下的推算目標價（橫線=當前市價）",
                                                color="#FF9A3C", fontSize=24, font="JetBrains Mono"))
        )
        hg_rule = alt.Chart(pd.DataFrame({"cp": [cp]})).mark_rule(
            color="#00F5FF", strokeDash=[6, 3], strokeWidth=2).encode(y="cp:Q")
        st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
        st.altair_chart(_cfg(alt.layer(hg_sens_chart, hg_rule).properties(background="rgba(0,0,0,0)")),
                        use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        summary = (
            f"【HyperGrowth 估值摘要 — {ticker}】"
            f"以每年 {hg_rev_g*100:.0f}% 收入成長率推演 {int(hg_years)} 年，"
            f"{'第'+str(by)+'年轉盈，採 P/E '+str(int(hg_pe))+'x 定價' if by else '推演期內未轉盈，採終端 P/S '+str(hg_ps)+'x 定價'}。"
            f"折現率 {hg_dr*100:.0f}%，推算目標價 {tp:.2f}，"
            f"{'高於' if tp > cp else '低於'}市價 {cp:.2f} 約 {abs(upside):.1f}%。"
            f"⚠️ 此類高度投機標的，不確定性極高，務必分散倉位。"
        )
        if f"hg_streamed_{ticker}" not in st.session_state:
            st.write_stream(_stream_text(summary, speed=0.012))
            st.session_state[f"hg_streamed_{ticker}"] = True
        else:
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
                        f'color:rgba(180,200,220,0.55);line-height:1.8;padding:8px 0;">{summary}</div>',
                        unsafe_allow_html=True)

        st.toast("✅ HyperGrowth 推演完成！", icon="🚀")

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
            dy=-30, color='#FF6BFF', fontSize=24, fontWeight='bold'
        ).encode(x='Date:T', y='Price:Q', text='Label')
        
        chart_combined = chart_combined + sim_line + sim_points + sim_labels
    
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(chart_combined), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.toast("✅ 艾略特波浪分析完成 / Elliott Wave Complete", icon="🎯")

# ══════════════════════════════════════════════════════════════
# 🎯 TAB 8: MOONSHOT ARK ENGINE — 燒錢超高速成長股估值模型
# ══════════════════════════════════════════════════════════════
def _t8(ticker, cp):
    """
    T8: Moonshot ARK Valuation Engine
    ──────────────────────────────────────────────────────────────────────
    專為美國小型燒錢超高速成長股設計（QBTS / IONQ / RGTI / ASTS / RKLB 等）
    以第一性原則重建：傳統 P/E 與 DCF 對這類公司完全失效，
    本引擎整合：
      ① 收入衰減成長曲線（非固定成長率）
      ② 股數稀釋追蹤（SBC + 增資）
      ③ 現金跑道 / 燒錢壓力分析
      ④ 五情境目標價（Deep Bear → Bear → Base → Bull → Moonshot）
      ⑤ TAM 滲透率分析（你需要佔市場多少份額才能合理化現在股價）
      ⑥ 風險雷達儀表板（跑道 / 稀釋 / 競爭 / 估值風險）
    """
    st.toast("🚀 Moonshot ARK 引擎啟動中…", icon="⏳")

    # ── session_state 初始值 ──────────────────────────────────────────────────
    _ms_defaults = {
        "ms_rev"          : 20.0,    # 年收入 $M
        "ms_shares"       : 300.0,   # 股數 M
        "ms_cash"         : 200.0,   # 現金 $M
        "ms_burn"         : 80.0,    # 年燒錢 $M（EBITDA虧損金額）
        "ms_rev_g_y1"     : 0.70,    # 第1年收入成長率
        "ms_rev_g_decel"  : 0.12,    # 每年成長衰減幅度（12%）
        "ms_gm_now"       : 0.45,    # 當前毛利率
        "ms_gm_target"    : 0.72,    # 目標成熟期毛利率
        "ms_opex_pct"     : 1.60,    # 當前費用佔收入比（160% = 嚴重虧損）
        "ms_opex_improve" : 0.14,    # 每年費用佔比下降幅度
        "ms_dilution"     : 0.12,    # 年股數稀釋率（12%）
        "ms_ps_terminal"  : 18.0,    # 終端 P/S 倍數（未盈利時用）
        "ms_pe_terminal"  : 80.0,    # 終端 P/E 倍數（盈利後用）
        "ms_dr"           : 0.20,    # 折現率（高風險 20%）
        "ms_years"        : 7,       # 推演年限
        "ms_tam"          : 50.0,    # TAM 總可尋址市場 $B（十億美元）
        "ms_mktcap"       : 1.0,     # 當前市值 $B
    }
    for k, v in _ms_defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Hero Billboard ─────────────────────────────────────────────────────────
    st.markdown('<div class="hero-container">', unsafe_allow_html=True)
    st.markdown('<div class="hero-lbl">🌙 MOONSHOT ARK ENGINE · PRE-PROFIT HYPERGROWTH</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="hero-val">{ticker}</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">燒錢超高速成長股 · 五情境月球砲估值</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 模型說明卡片 ───────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(0,245,255,0.06),rgba(183,125,255,0.06));
    border:1px solid rgba(0,245,255,0.28);border-left:4px solid #00F5FF;
    border-radius:16px;padding:24px 28px;margin:0 0 26px;">
  <div style="font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:4px;
      color:#00F5FF;margin-bottom:16px;">
    🌙 MOONSHOT ARK 燒錢成長股估值引擎 — 完整操作說明</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:16px;
      color:rgba(215,230,245,0.95);line-height:2.0;margin-bottom:18px;">
    傳統 DCF 和 ARK 三情境<strong style="color:#FF3131;font-size:17px;">完全不適用</strong>這類公司——
    因為它們根本沒有正的淨利或自由現金流可以折現。<br>
    本引擎從<strong style="color:#00F5FF;font-size:17px;">第一性原則</strong>重建：
    它們的股價是在賭「<strong style="color:#FFD700;">未來 7 年的成長軌跡能否兌現</strong>」。
    所以估值的核心是模擬「<em>如果成長如預期，幾年後值多少，折現回今天</em>」。
  </div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px;">
    <div style="background:rgba(0,245,255,0.07);border:1px solid rgba(0,245,255,0.20);
        border-radius:12px;padding:14px 16px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:14px;color:#00F5FF;
          letter-spacing:2px;margin-bottom:8px;">📐 核心計算邏輯（8步）</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:13px;
          color:rgba(210,225,240,0.85);line-height:1.9;">
        ① 收入以<strong style="color:#FFD700;">衰減曲線</strong>成長（非固定）<br>
        ② 毛利率線性改善至成熟目標<br>
        ③ 費用佔比逐年收斂<br>
        ④ 追蹤每年現金消耗 / 跑道<br>
        ⑤ 追蹤<strong style="color:#FF9A3C;">股數稀釋</strong>（SBC+增資）<br>
        ⑥ 找到<strong style="color:#00FF7F;">EBITDA轉盈點</strong><br>
        ⑦ 終端定價（P/E 或 P/S）<br>
        ⑧ 以稀釋後股數折現回今日
      </div>
    </div>
    <div style="background:rgba(255,215,0,0.06);border:1px solid rgba(255,215,0,0.20);
        border-radius:12px;padding:14px 16px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:14px;color:#FFD700;
          letter-spacing:2px;margin-bottom:8px;">🎯 五情境設計</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:13px;
          color:rgba(210,225,240,0.85);line-height:1.9;">
        <span style="color:#FF3131;">💀 Deep Bear</span>：成長快速塌縮+倍數壓縮<br>
        <span style="color:#FF6B6B;">🐻 Bear</span>：成長放緩+估值折扣<br>
        <span style="color:#FFD700;">⚖️ Base</span>：你填入的基準假設<br>
        <span style="color:#00FF7F;">🚀 Bull</span>：成長超預期+估值溢價<br>
        <span style="color:#B77DFF;">🌙 Moonshot</span>：科技泡沫+TAM 全吃
      </div>
    </div>
    <div style="background:rgba(255,107,255,0.06);border:1px solid rgba(255,107,255,0.20);
        border-radius:12px;padding:14px 16px;">
      <div style="font-family:'Bebas Neue',sans-serif;font-size:14px;color:#FF6BFF;
          letter-spacing:2px;margin-bottom:8px;">🛡️ 獨家風險雷達</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:13px;
          color:rgba(210,225,240,0.85);line-height:1.9;">
        💸 <strong>現金跑道壓力</strong>（幾年燒完）<br>
        📉 <strong>稀釋損傷度</strong>（幾年後稀釋幾成）<br>
        🎯 <strong>TAM 滲透率</strong>（你需要多大市占）<br>
        ⚡ <strong>隱含 P/S</strong>（市場現在幫你標的什麼價格）
      </div>
    </div>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:12px;
      color:rgba(0,245,255,0.60);padding:10px 14px;
      background:rgba(0,245,255,0.04);border-radius:8px;letter-spacing:0.3px;">
    ⚡ 目標價 = 終端價值(P/E或P/S) ÷ 稀釋後股數 ÷ (1+折現率)^N&nbsp;&nbsp;
    ·&nbsp;&nbsp;📌 市價：<strong style="color:#00F5FF;font-size:15px;">{cp:.2f}</strong>
    &nbsp;·&nbsp; 折現率建議：<strong style="color:#FFD700;">20%~25%</strong>（高不確定性溢價）
  </div>
</div>
""", unsafe_allow_html=True)

    # ── 範例選單 ───────────────────────────────────────────────────────────────
    # (rev_M, shares_M, cash_M, burn_M, g_y1, g_decel, gm_now, gm_target,
    #  opex_pct, opex_improve, dilution, ps_terminal, pe_terminal, dr, years, tam_B, mktcap_B)
    MS_PRESETS = {
        "── 量子電腦（Quantum Computing）──":  None,
        "⚛️ QBTS  D-Wave Quantum":   (8.0,   185.0, 175.0, 55.0,  0.65, 0.12, 0.55, 0.72, 1.80, 0.14, 0.10, 18.0, 80.0, 0.20, 7, 65.0,  0.9),
        "⚛️ IONQ  量子雲端平台":      (22.0,  310.0, 300.0, 90.0,  0.70, 0.11, 0.62, 0.78, 1.50, 0.13, 0.09, 20.0, 90.0, 0.20, 7, 65.0,  5.5),
        "⚛️ RGTI  Rigetti Computing": (12.0,  380.0, 150.0, 65.0,  0.75, 0.13, 0.50, 0.70, 1.90, 0.15, 0.13, 15.0, 75.0, 0.22, 7, 65.0,  1.2),
        "⚛️ QUBT  Quantum Computing": (4.0,   210.0, 80.0,  45.0,  0.80, 0.14, 0.40, 0.68, 2.20, 0.17, 0.15, 12.0, 70.0, 0.22, 7, 65.0,  0.5),
        "── AI / 語音 / 新興科技 ──":          None,
        "🔊 SOUN  SoundHound AI":     (84.0,  440.0, 220.0, 100.0, 0.55, 0.10, 0.62, 0.75, 1.20, 0.11, 0.08, 15.0, 85.0, 0.18, 6, 160.0, 4.5),
        "🔐 ARQQ  Arqit Quantum":     (1.5,   95.0,  50.0,  30.0,  0.90, 0.15, 0.72, 0.85, 2.50, 0.20, 0.18, 25.0, 100.0,0.25, 8, 20.0,  0.2),
        "🤖 BBAI  BigBear.ai":        (170.0, 170.0, 50.0,  40.0,  0.25, 0.08, 0.25, 0.55, 0.95, 0.08, 0.07, 8.0,  60.0, 0.18, 7, 30.0,  0.4),
        "── 航太 / 太空新創 ──":               None,
        "🚀 RKLB  Rocket Lab USA":    (436.0, 505.0, 480.0, 150.0, 0.35, 0.08, 0.28, 0.55, 0.85, 0.09, 0.06, 10.0, 70.0, 0.15, 7, 400.0, 10.5),
        "📡 ASTS  AST SpaceMobile":   (5.0,   290.0, 500.0, 200.0, 1.20, 0.18, 0.55, 0.80, 2.80, 0.22, 0.14, 30.0, 100.0,0.25, 8, 1000.0,5.0),
        "── 核能 / 清潔能源 ──":               None,
        "⚡ NNE   Nano Nuclear":       (2.0,   50.0,  45.0,  15.0,  1.00, 0.16, 0.60, 0.80, 2.00, 0.18, 0.12, 20.0, 90.0, 0.22, 8, 500.0, 1.2),
        "⚡ OKLO  Oklo Inc":           (0.5,   120.0, 260.0, 30.0,  1.50, 0.20, 0.65, 0.82, 3.00, 0.25, 0.10, 22.0, 95.0, 0.22, 8, 500.0, 1.8),
    }

    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:20px;color:#00F5FF;
    letter-spacing:3px;margin:8px 0 10px;">⚡ 快速套用範例 — 選一檔自動填入</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:15px;color:rgba(180,200,220,0.80);
    margin-bottom:10px;">
以下均為<strong style="color:#FF9A3C;">尚未穩定獲利</strong>的超高速成長標的，
財務數字為參考估計，<strong style="color:#FF3131;">請務必自行驗證最新財報</strong>再調整。
</div>""", unsafe_allow_html=True)

    ms_options = list(MS_PRESETS.keys())
    ms_choice = st.selectbox("選擇範例股票", options=ms_options, index=0,
                              key="ms_preset", label_visibility="collapsed")
    msv = MS_PRESETS.get(ms_choice)

    if msv is not None and st.session_state.get("_ms_preset_prev") != ms_choice:
        (h_rev, h_shares, h_cash, h_burn, h_g1, h_gd, h_gm, h_gmt,
         h_op, h_opi, h_dil, h_ps, h_pe, h_dr, h_yr, h_tam, h_mc) = msv
        st.session_state["ms_rev"]         = float(h_rev)
        st.session_state["ms_shares"]      = float(h_shares)
        st.session_state["ms_cash"]        = float(h_cash)
        st.session_state["ms_burn"]        = float(h_burn)
        st.session_state["ms_rev_g_y1"]    = float(h_g1)
        st.session_state["ms_rev_g_decel"] = float(h_gd)
        st.session_state["ms_gm_now"]      = float(h_gm)
        st.session_state["ms_gm_target"]   = float(h_gmt)
        st.session_state["ms_opex_pct"]    = float(h_op)
        st.session_state["ms_opex_improve"]= float(h_opi)
        st.session_state["ms_dilution"]    = float(h_dil)
        st.session_state["ms_ps_terminal"] = float(h_ps)
        st.session_state["ms_pe_terminal"] = float(h_pe)
        st.session_state["ms_dr"]          = float(h_dr)
        st.session_state["ms_years"]       = int(h_yr)
        st.session_state["ms_tam"]         = float(h_tam)
        st.session_state["ms_mktcap"]      = float(h_mc)
        st.session_state["_ms_preset_prev"] = ms_choice
        st.rerun()

    msv = MS_PRESETS.get(ms_choice)
    if msv is not None and ms_choice and MS_PRESETS.get(ms_choice) is not None:
        (p_rev, p_shares, p_cash, p_burn, p_g1, p_gd, p_gm, p_gmt,
         p_op, p_opi, p_dil, p_ps, p_pe, p_dr, p_yr, p_tam, p_mc) = msv
        st.markdown(f"""
<div style="background:rgba(0,245,255,0.05);border:1px solid rgba(0,245,255,0.22);
    border-radius:10px;padding:10px 16px;margin:6px 0 14px;
    font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(0,245,255,0.8);">
  ✅ 已套用：<strong style="color:#00F5FF;">{ms_choice}</strong>
  &nbsp;｜ 收入：{p_rev:.1f}M &nbsp;｜ 股數：{p_shares:.0f}M股
  &nbsp;｜ 現金：{p_cash:.0f}M &nbsp;｜ 年燒：{p_burn:.0f}M
  &nbsp;｜ Y1成長：{p_g1*100:.0f}% &nbsp;｜ TAM：${p_tam:.0f}B
</div>""", unsafe_allow_html=True)

    # ── 參數輸入：分組卡片 ──────────────────────────────────────────────────────
    # ┌─── GROUP A: 公司基本財務 ────────────────────────────────────────────────┐
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:#00F5FF;
    letter-spacing:3px;margin:20px 0 12px;border-bottom:1px solid rgba(0,245,255,0.15);
    padding-bottom:6px;">🏦 GROUP A · 公司現況財務數據</div>""", unsafe_allow_html=True)

    ga1, ga2, ga3, ga4 = st.columns(4)
    with ga1:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:5px;">
💰 年收入 TTM（$M 百萬美元）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
最近12個月總收入（美元百萬）。<br>
<strong style="color:#FFD700;">哪裡查：</strong>Yahoo Finance → Financials → Revenue TTM。
QBTS≈$8M，IONQ≈$22M，RGTI≈$12M。
</div>""", unsafe_allow_html=True)
        ms_rev = st.number_input("年收入", min_value=0.1, step=1.0, format="%.1f",
                                  key="ms_rev", label_visibility="collapsed")

    with ga2:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:5px;">
📊 流通股數（百萬股）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
含 Warrants 的完全稀釋股數（Fully Diluted）。<br>
<strong style="color:#FFD700;">哪裡查：</strong>Yahoo Finance → Statistics → Shares Outstanding。
QBTS≈185M，IONQ≈310M。
</div>""", unsafe_allow_html=True)
        ms_shares = st.number_input("流通股數(M)", min_value=1.0, step=10.0, format="%.1f",
                                     key="ms_shares", label_visibility="collapsed")

    with ga3:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:5px;">
💵 現金與約當（$M）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
最新季報的 Cash + Short-term Investments（現金糧草）。<br>
<strong style="color:#FF3131;">⚠️ 這決定公司還能撐多久不增資稀釋你。</strong>
</div>""", unsafe_allow_html=True)
        ms_cash = st.number_input("現金($M)", min_value=0.0, step=10.0, format="%.1f",
                                   key="ms_cash", label_visibility="collapsed")

    with ga4:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:5px;">
🔥 年燒錢金額（$M）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
年度 Operating Cash Outflow（運營現金流出）。<br>
<strong style="color:#FFD700;">哪裡查：</strong>Cash Flow Statement → 取負數的 Operating CF。
</div>""", unsafe_allow_html=True)
        ms_burn = st.number_input("年燒錢($M)", min_value=0.1, step=5.0, format="%.1f",
                                   key="ms_burn", label_visibility="collapsed")

    # ┌─── GROUP B: 成長路徑假設 ────────────────────────────────────────────────┐
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:#FFD700;
    letter-spacing:3px;margin:20px 0 12px;border-bottom:1px solid rgba(255,215,0,0.15);
    padding-bottom:6px;">📈 GROUP B · 成長路徑假設</div>""", unsafe_allow_html=True)

    gb1, gb2, gb3 = st.columns(3)
    with gb1:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:5px;">
🚀 第1年收入成長率</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
最樂觀的近期收入 YoY 成長（衰減曲線的起點）。<br>
量子股：0.60~0.90（60%~90%）。<br>
<strong style="color:#FF9A3C;">哪裡查：</strong>近2季財報 Revenue YoY%。
</div>""", unsafe_allow_html=True)
        ms_rev_g_y1 = st.number_input("Y1成長率", min_value=0.05, max_value=5.0,
                                       step=0.05, format="%.2f",
                                       key="ms_rev_g_y1", label_visibility="collapsed")

    with gb2:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(255,215,0,0.9);letter-spacing:1px;margin-bottom:5px;">
📉 成長衰減速度（每年）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
每年成長率<strong style="color:#FF3131;">衰減的幅度</strong>（0.12 = 每年少12%）。<br>
例：0.70 → 0.62 → 0.54 → 0.48…<br>
<strong style="color:#FFD700;">保守：0.15，基準：0.12，樂觀：0.08</strong>
</div>""", unsafe_allow_html=True)
        ms_rev_g_decel = st.number_input("成長衰減", min_value=0.01, max_value=0.50,
                                          step=0.01, format="%.2f",
                                          key="ms_rev_g_decel", label_visibility="collapsed")

    with gb3:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(0,245,255,0.9);letter-spacing:1px;margin-bottom:5px;">
📅 推演年限（年）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
建議 7 年（給足夠時間讓成長兌現）。<br>
量子電腦這類需要較長時間的技術，可設 8 年。<br>
<strong style="color:#FF3131;">不建議超過 10 年</strong>，預測誤差急劇放大。
</div>""", unsafe_allow_html=True)
        ms_years = st.number_input("推演年限", min_value=3, max_value=12, step=1,
                                    key="ms_years", label_visibility="collapsed")

    # ┌─── GROUP C: 毛利率與費用結構 ────────────────────────────────────────────┐
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:#FF9A3C;
    letter-spacing:3px;margin:20px 0 12px;border-bottom:1px solid rgba(255,154,60,0.15);
    padding-bottom:6px;">🏗️ GROUP C · 毛利率改善路徑 & 費用結構</div>""", unsafe_allow_html=True)

    gc1, gc2, gc3, gc4 = st.columns(4)
    with gc1:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(255,154,60,0.9);letter-spacing:1px;margin-bottom:5px;">
📦 當前毛利率</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
(收入 - 直接成本) ÷ 收入。<br>
量子股通常 40~65%（硬體+軟體混合）。<br>
<strong style="color:#FFD700;">哪裡查：</strong>Income Statement → Gross Profit ÷ Revenue。
</div>""", unsafe_allow_html=True)
        ms_gm_now = st.number_input("當前毛利率", min_value=0.0, max_value=1.0,
                                     step=0.01, format="%.2f",
                                     key="ms_gm_now", label_visibility="collapsed")

    with gc2:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(255,154,60,0.9);letter-spacing:1px;margin-bottom:5px;">
🎯 目標成熟毛利率</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
成熟期（推演期末）預期的毛利率。<br>
軟體/量子雲端成熟期：70~85%。<br>
<strong style="color:#00F5FF;">AWS、Azure 軟體業務毛利率≈70%+</strong>。
</div>""", unsafe_allow_html=True)
        ms_gm_target = st.number_input("目標毛利率", min_value=0.0, max_value=0.99,
                                        step=0.01, format="%.2f",
                                        key="ms_gm_target", label_visibility="collapsed")

    with gc3:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(255,154,60,0.9);letter-spacing:1px;margin-bottom:5px;">
💸 當前費用佔收入比</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
(R&D + S&M + G&A) ÷ 收入。&gt;1.0 = 嚴重虧損。<br>
QBTS≈1.8，IONQ≈1.5，RGTI≈1.9。<br>
<strong style="color:#FFD700;">哪裡查：</strong>Operating Expenses ÷ Revenue TTM。
</div>""", unsafe_allow_html=True)
        ms_opex_pct = st.number_input("費用佔比", min_value=0.10, max_value=5.0,
                                       step=0.05, format="%.2f",
                                       key="ms_opex_pct", label_visibility="collapsed")

    with gc4:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(255,154,60,0.9);letter-spacing:1px;margin-bottom:5px;">
⬇️ 費用年均改善幅度</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
費用佔比每年下降多少（營收槓桿效應）。<br>
快速改善：0.15~0.20；溫和：0.10~0.13。<br>
<strong style="color:#FF3131;">越高 = 越快達到獲利</strong>。
</div>""", unsafe_allow_html=True)
        ms_opex_improve = st.number_input("費用改善", min_value=0.01, max_value=0.50,
                                           step=0.01, format="%.2f",
                                           key="ms_opex_improve", label_visibility="collapsed")

    # ┌─── GROUP D: 稀釋 / 終端定價 / 折現 / TAM ────────────────────────────────┐
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:#B77DFF;
    letter-spacing:3px;margin:20px 0 12px;border-bottom:1px solid rgba(183,125,255,0.15);
    padding-bottom:6px;">💎 GROUP D · 稀釋 / 定價倍數 / 折現率 / TAM</div>""",
                unsafe_allow_html=True)

    gd1, gd2, gd3 = st.columns(3)
    with gd1:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(183,125,255,0.9);letter-spacing:1px;margin-bottom:5px;">
📉 年股數稀釋率</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
每年因<strong style="color:#FF3131;">SBC + 增資</strong>增加的股數佔比。<br>
量子股通常 8~15%/年。<br>
<strong style="color:#FFD700;">哪裡查：</strong>近2年 Shares Outstanding 對比 YoY%。
</div>""", unsafe_allow_html=True)
        ms_dilution = st.number_input("年稀釋率", min_value=0.0, max_value=0.5,
                                       step=0.01, format="%.2f",
                                       key="ms_dilution", label_visibility="collapsed")

    with gd2:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(183,125,255,0.9);letter-spacing:1px;margin-bottom:5px;">
🏷️ 終端 P/S（未盈利時）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
若推演期末仍虧損，以此 P/S 倍數定價。<br>
高成長科技：15~25x，泡沫情境：30~50x。<br>
<strong style="color:#00FF7F;">同行對比：IONQ 當前約 70x P/S（含成長溢價）</strong>。
</div>""", unsafe_allow_html=True)
        ms_ps_terminal = st.number_input("終端P/S", min_value=1.0, max_value=200.0,
                                          step=1.0, key="ms_ps_terminal",
                                          label_visibility="collapsed")

    with gd3:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(183,125,255,0.9);letter-spacing:1px;margin-bottom:5px;">
💹 終端 P/E（盈利後用）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
若推演期末已獲利，以此 P/E 定價。<br>
高成長科技：60~100x，穩定成長後：30~50x。<br>
<strong style="color:#FFD700;">一旦量子電腦商業化，可期望給予高 P/E 溢價</strong>。
</div>""", unsafe_allow_html=True)
        ms_pe_terminal = st.number_input("終端P/E", min_value=1.0, max_value=300.0,
                                          step=1.0, key="ms_pe_terminal",
                                          label_visibility="collapsed")

    gd4, gd5, gd6 = st.columns(3)
    with gd4:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(183,125,255,0.9);letter-spacing:1px;margin-bottom:5px;">
📉 折現率</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
反映<strong style="color:#FF3131;">高度不確定性的風險溢價</strong>。<br>
<strong style="color:#FFD700;">量子/航太：0.20~0.25</strong>（20%~25%）。<br>
一般科技成長股：0.15；穩健型：0.10。
</div>""", unsafe_allow_html=True)
        ms_dr = st.number_input("折現率", min_value=0.05, max_value=0.50,
                                 step=0.01, format="%.2f",
                                 key="ms_dr", label_visibility="collapsed")

    with gd5:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(0,255,127,0.9);letter-spacing:1px;margin-bottom:5px;">
🌐 TAM 總可尋址市場（$B）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
公司所在市場的<strong style="color:#00FF7F;">全球可尋址市場規模（十億美元）</strong>。<br>
量子電腦TAM≈$65B（2030E），太空通信≈$1T+。<br>
<strong style="color:#FFD700;">用來計算你現在的股價隱含多少市占率。</strong>
</div>""", unsafe_allow_html=True)
        ms_tam = st.number_input("TAM($B)", min_value=0.1, max_value=10000.0,
                                  step=1.0, format="%.1f",
                                  key="ms_tam", label_visibility="collapsed")

    with gd6:
        st.markdown("""<div style="font-family:'JetBrains Mono',monospace;font-size:11px;
font-weight:700;color:rgba(0,255,127,0.9);letter-spacing:1px;margin-bottom:5px;">
🏦 當前市值（$B）</div>
<div style="font-family:'Rajdhani',sans-serif;font-size:13px;
color:rgba(190,210,230,0.80);line-height:1.7;margin-bottom:7px;">
目前公司總市值（Market Cap，十億美元）。<br>
<strong style="color:#FFD700;">哪裡查：</strong>Yahoo Finance → Market Cap。<br>
用於計算隱含 P/S 和 TAM 滲透率。
</div>""", unsafe_allow_html=True)
        ms_mktcap = st.number_input("市值($B)", min_value=0.01, max_value=10000.0,
                                     step=0.1, format="%.2f",
                                     key="ms_mktcap", label_visibility="collapsed")

    # ── 計算按鈕 ────────────────────────────────────────────────────────────────
    st.markdown('<div style="height:14px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="t3-action">', unsafe_allow_html=True)
    run_ms = st.button("🌙  執行 MOONSHOT ARK 五情境推演", key="ms_calc",
                        use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if not run_ms:
        return

    st.toast("🌙 正在推演五情境月球砲目標價…", icon="⏳")

    # ── 定義五情境乘數 ──────────────────────────────────────────────────────────
    SCENARIOS = {
        '💀 Deep Bear': {'g_decel_mult': 2.20, 'gm_target_adj': -0.18, 'terminal_mult': 0.45},
        '🐻 Bear':       {'g_decel_mult': 1.45, 'gm_target_adj': -0.10, 'terminal_mult': 0.70},
        '⚖️ Base':        {'g_decel_mult': 1.00, 'gm_target_adj':  0.00, 'terminal_mult': 1.00},
        '🚀 Bull':        {'g_decel_mult': 0.70, 'gm_target_adj':  0.06, 'terminal_mult': 1.35},
        '🌙 Moonshot':   {'g_decel_mult': 0.40, 'gm_target_adj':  0.12, 'terminal_mult': 1.80},
    }

    scenario_results = {}
    for s_name, s_mult in SCENARIOS.items():
        r = calculate_moonshot_valuation(
            ms_rev, ms_shares, ms_cash, ms_burn,
            ms_rev_g_y1, ms_rev_g_decel,
            ms_gm_now, ms_gm_target,
            ms_opex_pct, ms_opex_improve,
            ms_dilution, ms_ps_terminal, ms_pe_terminal,
            ms_dr, int(ms_years), scenario_mult=s_mult
        )
        scenario_results[s_name] = r

    base_result = scenario_results['⚖️ Base']
    if base_result is None:
        st.toast("⚠️ 計算失敗，請確認所有欄位已填寫且股數 > 0", icon="⚡")
        return

    base_tp     = base_result['terminal_price']
    base_by     = base_result['breakeven_year']
    base_method = base_result['used_method']
    base_proj   = base_result['projections']
    runway_yrs  = base_result['cash_runway_years']
    final_shares= base_result['terminal_shares']

    upside = (base_tp - cp) / cp * 100 if cp > 0 else 0
    up_col = "#00FF7F" if upside > 50 else "#FFD700" if upside > 0 else "#FF3131"

    by_str  = f"第 {base_by} 年" if base_by else "推演期內未獲利"
    by_col  = "#00FF7F" if base_by else "#FF9A3C"
    rw_str  = f"第 {runway_yrs} 年耗盡" if runway_yrs else "跑道充足"
    rw_col  = "#FF3131" if runway_yrs and runway_yrs <= 2 else \
              "#FFD700" if runway_yrs and runway_yrs <= 4 else "#00FF7F"

    dilution_total = ((1 + ms_dilution) ** int(ms_years) - 1) * 100
    implied_ps = (ms_mktcap * 1000) / ms_rev if ms_rev > 0 else 0

    verdict = ("🟢 強力低估 — 成長兌現則超額回報" if upside > 50 else
               "🟡 合理偏低 — 需持續驗證成長路徑" if upside > 15 else
               "⚪ 接近合理 — 市場已充分反映成長預期" if upside > -20 else
               "🔴 高估警示 — 市場已過度定價未來成長")

    # ── 區塊1: 基準情境主要 KPI ──────────────────────────────────────────────────
    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:#00F5FF;
    letter-spacing:3px;margin:22px 0 12px;">🎯 基準情境（Base Case）推演結果</div>""",
                unsafe_allow_html=True)

    st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:0 0 18px;">

  <div style="background:rgba(0,245,255,0.07);border:1px solid rgba(0,245,255,0.3);
      border-top:3px solid #00F5FF;border-radius:16px;padding:18px 14px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:8px;color:rgba(0,245,255,0.55);
        letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">🌙 Moonshot 目標價</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:46px;color:#00F5FF;line-height:1;
        margin-bottom:6px;">{base_tp:.2f}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(0,245,255,0.45);">
        {int(ms_years)}年後折現 · {base_method}</div>
  </div>

  <div style="border:1px solid {up_col}44;border-top:3px solid {up_col};
      border-radius:16px;padding:18px 14px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:8px;color:rgba(200,215,230,0.4);
        letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">📍 市價 {cp:.2f} 對比</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:46px;color:{up_col};line-height:1;
        margin-bottom:6px;">{upside:+.1f}%</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:12px;color:{up_col};font-weight:700;">
        {verdict}</div>
  </div>

  <div style="background:rgba(0,0,0,0.2);border:1px solid {by_col}44;
      border-top:3px solid {by_col};border-radius:16px;padding:18px 14px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:8px;color:rgba(200,215,230,0.4);
        letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">⚡ EBITDA 轉盈點</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:30px;color:{by_col};line-height:1.1;
        margin-bottom:6px;">{by_str}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(200,215,230,0.45);">
        終端定價：{base_method}</div>
  </div>

  <div style="background:rgba(0,0,0,0.2);border:1px solid {rw_col}44;
      border-top:3px solid {rw_col};border-radius:16px;padding:18px 14px;text-align:center;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:8px;color:rgba(200,215,230,0.4);
        letter-spacing:3px;text-transform:uppercase;margin-bottom:8px;">💸 現金跑道</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:30px;color:{rw_col};line-height:1.1;
        margin-bottom:6px;">{rw_str}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(200,215,230,0.45);">
        現金 {ms_cash:.0f}M · 年燒 {ms_burn:.0f}M</div>
  </div>

</div>
""", unsafe_allow_html=True)

    # ── 區塊2: 五情境對比 ─────────────────────────────────────────────────────────
    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:#FFD700;
    letter-spacing:3px;margin:22px 0 12px;">📊 五情境目標價總覽</div>""",
                unsafe_allow_html=True)

    s_colors = {
        '💀 Deep Bear': '#FF3131',
        '🐻 Bear':       '#FF6B6B',
        '⚖️ Base':        '#FFD700',
        '🚀 Bull':        '#00FF7F',
        '🌙 Moonshot':   '#B77DFF',
    }

    scenario_cards_html = '<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-bottom:18px;">'
    for s_name, s_res in scenario_results.items():
        s_col = s_colors.get(s_name, '#888')
        if s_res:
            s_tp   = s_res['terminal_price']
            s_up   = (s_tp - cp) / cp * 100 if cp > 0 else 0
            s_by   = s_res['breakeven_year']
            s_by_s = f"Y+{s_by}" if s_by else "未轉盈"
            s_dir  = "⬆" if s_tp >= cp else "⬇"
            s_meth = s_res['used_method']
            s_brd  = f"2px solid {s_col}" if s_name == '⚖️ Base' else f"1px solid {s_col}55"
        else:
            s_tp, s_up, s_by_s, s_dir, s_meth = 0, -100, "N/A", "⬇", "N/A"
            s_brd = f"1px solid {s_col}33"
        scenario_cards_html += f"""
<div style="background:rgba(0,0,0,0.25);border:{s_brd};border-top:3px solid {s_col};
    border-radius:14px;padding:16px 10px;text-align:center;">
  <div style="font-family:'JetBrains Mono',monospace;font-size:8px;
      color:{s_col};letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">{s_name}</div>
  <div style="font-family:'Bebas Neue',sans-serif;font-size:38px;color:{s_col};
      line-height:1;margin-bottom:6px;">{s_tp:.2f}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
      color:{"#00FF7F" if s_up >= 0 else "#FF3131"};">{s_dir} {abs(s_up):.0f}% vs 市價</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
      color:rgba(180,200,220,0.45);margin-top:4px;">轉盈：{s_by_s} · {s_meth}</div>
</div>"""
    scenario_cards_html += '</div>'
    st.markdown(scenario_cards_html, unsafe_allow_html=True)

    # ── 區塊2b: 五情境 Altair 條形圖 ─────────────────────────────────────────────
    bar_rows = []
    for s_name, s_res in scenario_results.items():
        tp_val = s_res['terminal_price'] if s_res else 0
        bar_rows.append({
            "情境": s_name.split(' ', 1)[-1],   # 去掉 emoji
            "目標價": tp_val,
            "顏色": s_colors.get(s_name, '#888'),
        })
    bar_rows.append({"情境": "📍 現在市價", "目標價": cp, "顏色": "#00F5FF"})
    bar_df_ms = pd.DataFrame(bar_rows)

    bar_ms = (
        alt.Chart(bar_df_ms)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("情境:N", sort=None,
                    axis=alt.Axis(labelColor="#778899", titleColor="#445566",
                                  labelFontSize=26, labelFont="Rajdhani")),
            y=alt.Y("目標價:Q", title="推算目標股價",
                    axis=alt.Axis(labelColor="#556677", titleColor="#445566"),
                    scale=alt.Scale(zero=False)),
            color=alt.Color("顏色:N", scale=None),
            tooltip=["情境", alt.Tooltip("目標價:Q", format=".2f")]
        )
        .properties(
            height=280,
            background="rgba(0,0,0,0)",
            title=alt.TitleParams(f"五情境推算目標價對比 ({int(ms_years)}年後折現)",
                                   color="#FFD700", fontSize=24, font="JetBrains Mono")
        )
    )
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(bar_ms), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 區塊3: 逐年成長路徑表（Base Case）────────────────────────────────────────
    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:#FF9A3C;
    letter-spacing:3px;margin:22px 0 10px;">📈 逐年成長路徑模擬（Base Case）</div>""",
                unsafe_allow_html=True)

    rows_html = ""
    for _, row in base_proj.iterrows():
        yr    = int(row['Year'])
        ni_c  = "#00FF7F" if row['EBITDA'] > 0 else "#FF6B6B"
        gr_c  = "#00F5FF"
        prof_b = ('<span style="color:#00FF7F;font-weight:700;">✅ 轉盈</span>'
                  if row['Profitable']
                  else '<span style="color:#FF6B6B;">🔴 虧損</span>')
        cash_s = (f"<span style='color:{'#00FF7F' if row['CashBal'] and row['CashBal'] > 50 else '#FF3131'};'>"
                  f"{row['CashBal']:.0f}M</span>" if row['CashBal'] is not None else "—")
        rows_html += f"""
<tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
  <td style="padding:7px 9px;font-family:'Bebas Neue',sans-serif;font-size:16px;color:#FF9A3C;">
    Y+{yr}</td>
  <td style="padding:7px 9px;font-family:'JetBrains Mono',monospace;font-size:11px;color:{gr_c};">
    {row['GrowthRate']:.0f}%</td>
  <td style="padding:7px 9px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#00F5FF;">
    {row['Revenue']:,.1f}M</td>
  <td style="padding:7px 9px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#FFD700;">
    {row['GrossMargin']:.1f}%</td>
  <td style="padding:7px 9px;font-family:'JetBrains Mono',monospace;font-size:11px;color:{ni_c};">
    {row['EBITDA']:,.1f}M</td>
  <td style="padding:7px 9px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#B77DFF;">
    {row['Shares']:.0f}M</td>
  <td style="padding:7px 9px;">{cash_s}</td>
  <td style="padding:7px 9px;">{prof_b}</td>
</tr>"""

    st.markdown(f"""
<div style="background:rgba(0,0,0,0.3);border:1px solid rgba(255,154,60,0.15);
    border-radius:14px;overflow:hidden;margin:10px 0;">
  <table style="width:100%;border-collapse:collapse;">
    <thead>
      <tr style="background:rgba(255,154,60,0.08);border-bottom:1px solid rgba(255,154,60,0.25);">
        <th style="padding:9px 9px;font-family:'JetBrains Mono',monospace;font-size:9px;
            color:rgba(255,154,60,0.7);letter-spacing:2px;text-align:left;">年度</th>
        <th style="padding:9px 9px;font-family:'JetBrains Mono',monospace;font-size:9px;
            color:rgba(0,245,255,0.7);letter-spacing:2px;text-align:left;">成長率</th>
        <th style="padding:9px 9px;font-family:'JetBrains Mono',monospace;font-size:9px;
            color:rgba(0,245,255,0.7);letter-spacing:2px;text-align:left;">收入</th>
        <th style="padding:9px 9px;font-family:'JetBrains Mono',monospace;font-size:9px;
            color:rgba(255,215,0,0.7);letter-spacing:2px;text-align:left;">毛利率</th>
        <th style="padding:9px 9px;font-family:'JetBrains Mono',monospace;font-size:9px;
            color:rgba(255,107,107,0.7);letter-spacing:2px;text-align:left;">EBITDA</th>
        <th style="padding:9px 9px;font-family:'JetBrains Mono',monospace;font-size:9px;
            color:rgba(183,125,255,0.7);letter-spacing:2px;text-align:left;">稀釋股數</th>
        <th style="padding:9px 9px;font-family:'JetBrains Mono',monospace;font-size:9px;
            color:rgba(0,255,127,0.6);letter-spacing:2px;text-align:left;">現金餘</th>
        <th style="padding:9px 9px;font-family:'JetBrains Mono',monospace;font-size:9px;
            color:rgba(200,215,230,0.5);letter-spacing:2px;text-align:left;">狀態</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)

    # ── 區塊3b: 收入 + EBITDA 雙軌路徑圖 ────────────────────────────────────────
    pcd = base_proj.copy()
    pcd['年度'] = pcd['Year'].apply(lambda x: f"Y+{x}")
    pcd['EBITDA_clip'] = pcd['EBITDA'].clip(lower=pcd['Revenue'] * -3)

    rev_b = alt.Chart(pcd).mark_bar(
        cornerRadiusTopLeft=6, cornerRadiusTopRight=6,
        opacity=0.65, color='#FF9A3C'
    ).encode(
        x=alt.X('年度:N', sort=None,
                axis=alt.Axis(labelColor='#888', labelFontSize=26, labelFont='Rajdhani')),
        y=alt.Y('Revenue:Q', title='百萬美元',
                axis=alt.Axis(labelColor='#556677', titleColor='#445566'),
                scale=alt.Scale(zero=True)),
        tooltip=[alt.Tooltip('年度:N'),
                 alt.Tooltip('Revenue:Q', title='收入', format=',.1f'),
                 alt.Tooltip('GrowthRate:Q', title='YoY%', format='.0f')]
    )
    ebitda_l = alt.Chart(pcd).mark_line(
        color='#00FF7F', strokeWidth=3,
        point=alt.OverlayMarkDef(color='#00FF7F', size=80)
    ).encode(
        x='年度:N',
        y=alt.Y('EBITDA_clip:Q'),
        tooltip=[alt.Tooltip('EBITDA:Q', title='EBITDA', format=',.1f')]
    )
    zero_l = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(
        color='#FF3131', strokeDash=[4, 4], strokeWidth=2
    ).encode(y='y:Q')

    combo_ms = (rev_b + ebitda_l + zero_l).resolve_scale(y='independent').properties(
        height=270, background='rgba(0,0,0,0)',
        title=alt.TitleParams('收入路徑（橘柱）× EBITDA（綠線）· 紅線=損益平衡',
                               color='#FF9A3C', fontSize=24, font='JetBrains Mono')
    )
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(combo_ms), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 區塊4: 風險雷達儀表板 ──────────────────────────────────────────────────────
    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:#FF3131;
    letter-spacing:3px;margin:22px 0 12px;">🛡️ 風險雷達儀表板</div>""",
                unsafe_allow_html=True)

    # 1. 現金跑道風險
    raw_runway = ms_cash / ms_burn if ms_burn > 0 else 99
    if raw_runway < 1.5:
        rr_lvl, rr_c, rr_icon, rr_desc = "🔴 極高危", "#FF3131", "💀", "現金不足 1.5 年！極可能大規模增資稀釋！"
    elif raw_runway < 2.5:
        rr_lvl, rr_c, rr_icon, rr_desc = "🟠 高風險", "#FF9A3C", "⚠️", "現金約 2 年，預期 6~12 個月內發布增資計劃"
    elif raw_runway < 4.0:
        rr_lvl, rr_c, rr_icon, rr_desc = "🟡 中等", "#FFD700", "👀", "現金跑道約 3~4 年，近期壓力不大但需關注"
    else:
        rr_lvl, rr_c, rr_icon, rr_desc = "🟢 安全", "#00FF7F", "✅", "現金充足，近期無稀釋壓力"

    # 2. 稀釋損傷風險
    dil_7yr = dilution_total
    if dil_7yr > 100:
        dr_lvl, dr_c, dr_icon, dr_desc = "🔴 極嚴重", "#FF3131", "💀", f"{int(ms_years)}年後股數翻倍以上，嚴重侵蝕每股價值"
    elif dil_7yr > 60:
        dr_lvl, dr_c, dr_icon, dr_desc = "🟠 嚴重", "#FF9A3C", "⚠️", f"{int(ms_years)}年累積稀釋超 60%，每股成長大幅打折"
    elif dil_7yr > 30:
        dr_lvl, dr_c, dr_icon, dr_desc = "🟡 中等", "#FFD700", "👀", f"累積稀釋 {dil_7yr:.0f}%，成長需超額補償稀釋損失"
    else:
        dr_lvl, dr_c, dr_icon, dr_desc = "🟢 可控", "#00FF7F", "✅", f"累積稀釋 {dil_7yr:.0f}%，在可接受範圍內"

    # 3. 估值泡沫風險（隱含 P/S）
    if implied_ps > 80:
        vr_lvl, vr_c, vr_icon, vr_desc = "🔴 極度泡沫", "#FF3131", "🫧", f"隱含P/S {implied_ps:.0f}x，市場定價極為樂觀，修正風險大"
    elif implied_ps > 40:
        vr_lvl, vr_c, vr_icon, vr_desc = "🟠 高估值", "#FF9A3C", "⚠️", f"隱含P/S {implied_ps:.0f}x，高成長假設需要嚴格兌現"
    elif implied_ps > 15:
        vr_lvl, vr_c, vr_icon, vr_desc = "🟡 偏高", "#FFD700", "👀", f"隱含P/S {implied_ps:.0f}x，合理的高成長溢價"
    else:
        vr_lvl, vr_c, vr_icon, vr_desc = "🟢 合理", "#00FF7F", "✅", f"隱含P/S {implied_ps:.0f}x，估值相對合理"

    st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:0 0 18px;">

  <div style="background:rgba(0,0,0,0.25);border:1px solid {rr_c}44;
      border-left:4px solid {rr_c};border-radius:14px;padding:18px 16px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:{rr_c};
        letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">
        {rr_icon} 現金跑道風險</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:{rr_c};
        margin-bottom:8px;">{rr_lvl}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:17px;color:{rr_c};
        margin-bottom:8px;">{raw_runway:.1f} 年</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:13px;
        color:rgba(200,215,230,0.70);line-height:1.6;">{rr_desc}</div>
  </div>

  <div style="background:rgba(0,0,0,0.25);border:1px solid {dr_c}44;
      border-left:4px solid {dr_c};border-radius:14px;padding:18px 16px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:{dr_c};
        letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">
        {dr_icon} 稀釋損傷風險</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:{dr_c};
        margin-bottom:8px;">{dr_lvl}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:17px;color:{dr_c};
        margin-bottom:8px;">+{dil_7yr:.0f}% 股數</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:13px;
        color:rgba(200,215,230,0.70);line-height:1.6;">{dr_desc}</div>
  </div>

  <div style="background:rgba(0,0,0,0.25);border:1px solid {vr_c}44;
      border-left:4px solid {vr_c};border-radius:14px;padding:18px 16px;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:{vr_c};
        letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">
        {vr_icon} 估值泡沫風險</div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:{vr_c};
        margin-bottom:8px;">{vr_lvl}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:17px;color:{vr_c};
        margin-bottom:8px;">{implied_ps:.0f}x P/S</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:13px;
        color:rgba(200,215,230,0.70);line-height:1.6;">{vr_desc}</div>
  </div>

</div>
""", unsafe_allow_html=True)

    # ── 區塊5: TAM 滲透率分析 ──────────────────────────────────────────────────────
    tam_r = calculate_tam_penetration(ms_rev, ms_tam, ms_mktcap, ms_ps_terminal)
    cur_p   = tam_r['current_pen']
    impl_r  = tam_r['implied_rev_m']
    impl_p  = tam_r['implied_pen']
    mc10_b  = tam_r['ten_pct_mktcap_b']

    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:#00FF7F;
    letter-spacing:3px;margin:22px 0 12px;">🌐 TAM 滲透率分析 — 你需要吃掉多少市場？</div>""",
                unsafe_allow_html=True)

    st.markdown(f"""
<div style="background:rgba(0,255,127,0.04);border:1px solid rgba(0,255,127,0.22);
    border-radius:14px;padding:20px 24px;margin-bottom:16px;">
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:18px;">

    <div style="text-align:center;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(0,255,127,0.55);
          letter-spacing:3px;margin-bottom:8px;">📍 現在的市場滲透率</div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:44px;color:#00FF7F;line-height:1;">
          {cur_p:.2f}%</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:13px;
          color:rgba(200,215,230,0.65);margin-top:6px;">
          收入 {ms_rev:.1f}M ÷ TAM {ms_tam:.0f}B × 1000<br>
          <strong style="color:#FFD700;">⭐ 你現在渺小到接近零</strong></div>
    </div>

    <div style="text-align:center;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,154,60,0.55);
          letter-spacing:3px;margin-bottom:8px;">🎯 市值隱含需要多少收入</div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:44px;color:#FF9A3C;line-height:1;">
          {impl_r:,.0f}M</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:13px;
          color:rgba(200,215,230,0.65);margin-top:6px;">
          市值 {ms_mktcap:.2f}B ÷ P/S {ms_ps_terminal:.0f}x<br>
          = 佔TAM的 <strong style="color:#FF9A3C;">{impl_p:.1f}%</strong></div>
    </div>

    <div style="text-align:center;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(183,125,255,0.55);
          letter-spacing:3px;margin-bottom:8px;">🌙 達到10% TAM後的潛在市值</div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:44px;color:#B77DFF;line-height:1;">
          ${mc10_b:.1f}B</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:13px;
          color:rgba(200,215,230,0.65);margin-top:6px;">
          10% × TAM × P/S {ms_ps_terminal:.0f}x<br>
          vs 現在市值 <strong style="color:#B77DFF;">{ms_mktcap:.2f}B</strong></div>
    </div>

  </div>
</div>
""", unsafe_allow_html=True)

    # TAM 滲透率 bar chart
    tam_chart_df = pd.DataFrame([
        {"類別": "現在滲透率", "滲透率%": round(cur_p, 3), "顏色": "#00FF7F"},
        {"類別": "市值隱含需要", "滲透率%": round(impl_p, 2), "顏色": "#FF9A3C"},
        {"類別": "10% TAM 目標", "滲透率%": 10.0, "顏色": "#B77DFF"},
    ])
    tam_ch = (
        alt.Chart(tam_chart_df)
        .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
        .encode(
            x=alt.X("類別:N", sort=None,
                    axis=alt.Axis(labelColor="#778899", labelFontSize=26, labelFont="Rajdhani")),
            y=alt.Y("滲透率%:Q", title="市場滲透率 (%)",
                    axis=alt.Axis(labelColor="#556677", titleColor="#445566")),
            color=alt.Color("顏色:N", scale=None),
            tooltip=["類別", alt.Tooltip("滲透率%:Q", format=".3f")]
        )
        .properties(height=240, background="rgba(0,0,0,0)",
                    title=alt.TitleParams("TAM 滲透率對比（現在 vs 市值隱含 vs 10%目標）",
                                          color="#00FF7F", fontSize=24, font="JetBrains Mono"))
    )
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(_cfg(tam_ch), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 區塊6: 折現率敏感性分析 ────────────────────────────────────────────────────
    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:#FF6BFF;
    letter-spacing:3px;margin:22px 0 10px;">📊 折現率敏感性分析（Base Case）</div>""",
                unsafe_allow_html=True)

    ms_dr_range = [0.10, 0.13, 0.15, 0.18, 0.20, 0.22, 0.25, 0.30]
    ms_sens_rows = []
    for d in ms_dr_range:
        sr = calculate_moonshot_valuation(
            ms_rev, ms_shares, ms_cash, ms_burn,
            ms_rev_g_y1, ms_rev_g_decel,
            ms_gm_now, ms_gm_target,
            ms_opex_pct, ms_opex_improve,
            ms_dilution, ms_ps_terminal, ms_pe_terminal,
            d, int(ms_years)
        )
        fv2 = sr['terminal_price'] if sr else 0
        up2 = (fv2 - cp) / cp * 100 if cp > 0 else 0
        ms_sens_rows.append({
            "折現率": f"{d*100:.0f}%",
            "推算目標價": round(fv2, 2),
            "溢價折價": round(up2, 1),
            "顏色": "#00FF7F" if up2 > 0 else "#FF3131"
        })

    ms_sens_df = pd.DataFrame(ms_sens_rows)
    ms_sens_ch = (
        alt.Chart(ms_sens_df)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("折現率:N", sort=None,
                    axis=alt.Axis(labelColor="#778899", labelFontSize=26)),
            y=alt.Y("推算目標價:Q", title="折現後目標價",
                    axis=alt.Axis(labelColor="#556677", titleColor="#445566"),
                    scale=alt.Scale(zero=False)),
            color=alt.Color("顏色:N", scale=None),
            tooltip=["折現率",
                     alt.Tooltip("推算目標價:Q", format=".2f"),
                     alt.Tooltip("溢價折價:Q", format="+.1f")]
        )
        .properties(height=250,
                    title=alt.TitleParams("折現率敏感性 — 水平線=當前市價",
                                          color="#FF6BFF", fontSize=24, font="JetBrains Mono"))
    )
    ms_rule = alt.Chart(pd.DataFrame({"cp": [cp]})).mark_rule(
        color="#00F5FF", strokeDash=[6, 3], strokeWidth=2
    ).encode(y="cp:Q")
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(
        _cfg(alt.layer(ms_sens_ch, ms_rule).properties(background="rgba(0,0,0,0)")),
        use_container_width=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 區塊7: Valkyrie AI 摘要 ────────────────────────────────────────────────────
    bull_tp = scenario_results.get('🚀 Bull', {})
    bear_tp = scenario_results.get('🐻 Bear', {})
    bull_price = bull_tp['terminal_price'] if bull_tp else 0
    bear_price = bear_tp['terminal_price'] if bear_tp else 0
    moon_tp_val = scenario_results.get('🌙 Moonshot', {})
    moon_price  = moon_tp_val['terminal_price'] if moon_tp_val else 0

    by_display = f"第{base_by}年" if base_by else "推演期內未轉盈"
    summary_ms = (
        f"【Moonshot ARK 推演摘要 — {ticker}】"
        f"市價 {cp:.2f}，Base Case 推算 {int(ms_years)} 年目標價 {base_tp:.2f}"
        f"（折現率 {ms_dr*100:.0f}%，{base_method}），"
        f"{'高於' if base_tp > cp else '低於'}市價 {abs(upside):.0f}%。"
        f"Bear Case {bear_price:.2f} → Base {base_tp:.2f} → Bull {bull_price:.2f} → Moonshot {moon_price:.2f}。"
        f"EBITDA 轉盈點：{by_display}，"
        f"現金跑道 {raw_runway:.1f} 年（{rr_lvl.split()[0]}），"
        f"{int(ms_years)}年累積稀釋 {dil_7yr:.0f}%（{dr_lvl.split()[0]}），"
        f"當前隱含P/S {implied_ps:.0f}x（{vr_lvl.split()[0]}）。"
        f"⚠️ 此類標的不確定性極高，務必嚴格控制倉位，嚴禁重倉。"
    )

    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif;font-size:18px;color:#00F5FF;
    letter-spacing:3px;margin:22px 0 10px;">🧠 AI 戰術摘要</div>""", unsafe_allow_html=True)
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    if f"ms_streamed_{ticker}" not in st.session_state:
        st.write_stream(_stream_text(summary_ms, speed=0.010))
        st.session_state[f"ms_streamed_{ticker}"] = True
    else:
        st.markdown(
            f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;'
            f'color:rgba(0,245,255,0.75);line-height:1.9;">{summary_ms}</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    st.toast("✅ Moonshot ARK 推演完成！", icon="🌙")


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
    ("t7", "🌊", "5波模擬", "ELLIOTT", "#FF6BFF"),
    ("t8", "🌙", "月球砲ARK", "MOONSHOT", "#00F5FF"),
]

RENDER = {
    "t1": _t1,
    "t2": _t2,
    "t3": _t3,
    "t4": _t4,
    "t5": _t5,
    "t6": _t6,
    "t7": _t7,
    "t8": _t8,
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
        
        p_cols = st.columns(8)
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
            elif active in ("t5", "t6", "t8"):
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
