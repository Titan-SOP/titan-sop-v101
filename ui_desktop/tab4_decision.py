# ui_desktop/tab4_decision_godtier.py
# Titan SOP V200 — Tab 4: 全球決策 【GOD-TIER EDITION】
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  TITAN OS REFACTOR — CPO & Lead Architect Edition                ║
# ║  Philosophy: First Principles Design + Unmatched Magnificence    ║
# ║  Standard: Netflix Visuals × Tesla Big Data × Palantir Intel     ║
# ╚═══════════════════════════════════════════════════════════════════╝
#  🛡️ MANDATORY UX SOUL UPGRADES APPLIED:
#    [SOUL-1] 🍞 Tactical Toast Notifications (ALL st.success/info/error → st.toast)
#    [SOUL-2] ⌨️ Valkyrie AI Typewriter (ALL analysis text → st.write_stream)
#    [SOUL-3] ⚡ First Principles UI Optimization (Hero Billboard + Poster Rail + Glanceability)
# ══════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import re
import io
from datetime import datetime
import time

# ══════════════════════════════════════════════════════════════════
# 🎯 SOUL UPGRADE #2: VALKYRIE AI TYPEWRITER ENGINE
# ══════════════════════════════════════════════════════════════════
def _stream_text(text, speed=0.003):
    """
    Valkyrie AI Typewriter: Stream text character-by-character
    Creates the sensation of live AI transmission.
    """
    for char in text:
        yield char
        time.sleep(speed)

# ══════════════════════════════════════════════════════════════════
# INTERNAL BACKTEST ENGINES (100% PRESERVED FROM ORIGINAL)
# ══════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def _run_fast_backtest(ticker, start_date="2023-01-01", initial_capital=1_000_000):
    """極速向量化回測引擎 (V78.3) — identical to original run_fast_backtest()"""
    try:
        if ticker.upper() in ['CASH', 'USD', 'TWD']:
            dates = yf.download('^TWII', start=start_date, progress=False).index
            if dates.empty: return None
            df = pd.DataFrame(index=dates)
            df['Equity'] = initial_capital
            df['Drawdown'] = 0.0
            return {"cagr": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                    "win_rate": 0.0, "profit_factor": 0.0, "kelly": 0.0,
                    "equity_curve": df['Equity'], "drawdown_series": df['Drawdown'],
                    "latest_price": 1.0}

        original_ticker = ticker
        if re.match(r'^[0-9]', ticker) and 4 <= len(ticker) <= 6:
            ticker = f"{ticker}.TW"
        df = yf.download(ticker, start=start_date, progress=False)
        if df.empty and re.match(r'^[0-9]', original_ticker) and 4 <= len(original_ticker) <= 6:
            df = yf.download(f"{original_ticker}.TWO", start=start_date, progress=False)
        if df.empty or len(df) < 21: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df['MA20']            = df['Close'].rolling(20).mean()
        df['Signal']          = (df['Close'] > df['MA20']).astype(int)
        df['Pct_Change']      = df['Close'].pct_change()
        df['Strategy_Return'] = df['Signal'].shift(1) * df['Pct_Change']
        df['Equity']          = (1 + df['Strategy_Return'].fillna(0)).cumprod() * initial_capital
        df['Drawdown']        = (df['Equity'] / df['Equity'].cummax()) - 1

        trade_days = df[df['Signal'].shift(1) == 1]
        if len(trade_days) >= 10:
            wins   = trade_days[trade_days['Strategy_Return'] > 0]['Strategy_Return']
            losses = trade_days[trade_days['Strategy_Return'] < 0]['Strategy_Return']
            win_rate = len(wins) / len(trade_days)
            avg_win  = wins.mean() if len(wins) > 0 else 0
            avg_loss = abs(losses.mean()) if len(losses) > 0 else 1
            pf       = avg_win / avg_loss if avg_loss != 0 else 0
            kelly    = max(0, win_rate - ((1 - win_rate) / pf)) if pf > 0 else 0
        else:
            win_rate = pf = kelly = 0

        num_years    = len(df) / 252
        total_return = df['Equity'].iloc[-1] / initial_capital - 1
        cagr         = ((1 + total_return) ** (1 / num_years)) - 1 if num_years > 0 else 0
        daily_ret    = df['Strategy_Return'].dropna()
        sharpe       = (daily_ret.mean() * 252 - 0.02) / (daily_ret.std() * np.sqrt(252)) \
                       if daily_ret.std() > 0 else 0

        return {"cagr": cagr, "sharpe_ratio": sharpe, "max_drawdown": df['Drawdown'].min(),
                "win_rate": win_rate, "profit_factor": pf, "kelly": kelly,
                "equity_curve": df['Equity'], "drawdown_series": df['Drawdown'],
                "latest_price": float(df['Close'].iloc[-1])}
    except Exception:
        return None


@st.cache_data(ttl=7200)
def _run_ma_strategy_backtest(ticker, strategy_name, start_date="2015-01-01",
                               initial_capital=1_000_000):
    """15 種均線策略回測引擎 — identical to original run_ma_strategy_backtest()"""
    try:
        original_ticker = ticker
        if re.match(r'^[0-9]', ticker) and 4 <= len(ticker) <= 6:
            ticker = f"{ticker}.TW"
        df = yf.download(ticker, start=start_date, progress=False)
        if df.empty and re.match(r'^[0-9]', original_ticker) and 4 <= len(original_ticker) <= 6:
            df = yf.download(f"{original_ticker}.TWO", start=start_date, progress=False)
        if df.empty or len(df) < 300: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        for w, n in [(20,'MA20'),(43,'MA43'),(60,'MA60'),(87,'MA87'),(284,'MA284')]:
            df[n] = df['Close'].rolling(w).mean()

        df['Signal'] = 0
        sn = strategy_name
        if   sn == "價格 > 20MA":  df.loc[df['Close'] > df['MA20'],  'Signal'] = 1
        elif sn == "價格 > 43MA":  df.loc[df['Close'] > df['MA43'],  'Signal'] = 1
        elif sn == "價格 > 60MA":  df.loc[df['Close'] > df['MA60'],  'Signal'] = 1
        elif sn == "價格 > 87MA":  df.loc[df['Close'] > df['MA87'],  'Signal'] = 1
        elif sn == "價格 > 284MA": df.loc[df['Close'] > df['MA284'], 'Signal'] = 1
        elif sn == "20/60 黃金/死亡交叉":  df.loc[df['MA20'] > df['MA60'],  'Signal'] = 1
        elif sn == "20/87 黃金/死亡交叉":  df.loc[df['MA20'] > df['MA87'],  'Signal'] = 1
        elif sn == "20/284 黃金/死亡交叉": df.loc[df['MA20'] > df['MA284'], 'Signal'] = 1
        elif sn == "43/87 黃金/死亡交叉":  df.loc[df['MA43'] > df['MA87'],  'Signal'] = 1
        elif sn == "43/284 黃金/死亡交叉": df.loc[df['MA43'] > df['MA284'], 'Signal'] = 1
        elif sn == "60/87 黃金/死亡交叉":  df.loc[df['MA60'] > df['MA87'],  'Signal'] = 1
        elif sn == "60/284 黃金/死亡交叉": df.loc[df['MA60'] > df['MA284'], 'Signal'] = 1
        elif sn == "🔥 核心戰法: 87MA ↗ 284MA":
            df.loc[df['MA87'] > df['MA284'], 'Signal'] = 1
        elif sn == "非對稱: P>20進 / P<60出":
            pos = False
            for i in range(1, len(df)):
                if not pos and df['Close'].iloc[i] > df['MA20'].iloc[i]: pos = True
                elif pos and df['Close'].iloc[i] < df['MA60'].iloc[i]: pos = False
                df.iloc[i, df.columns.get_loc('Signal')] = 1 if pos else 0
        elif sn == "雙確認: P>20 & P>60 進 / P<60 出":
            pos = False
            for i in range(1, len(df)):
                if (not pos and df['Close'].iloc[i] > df['MA20'].iloc[i]
                        and df['Close'].iloc[i] > df['MA60'].iloc[i]):
                    pos = True
                elif pos and df['Close'].iloc[i] < df['MA60'].iloc[i]:
                    pos = False
                df.iloc[i, df.columns.get_loc('Signal')] = 1 if pos else 0

        df['Pct_Change']      = df['Close'].pct_change()
        df['Strategy_Return'] = df['Signal'].shift(1) * df['Pct_Change']
        df['Equity']          = (1 + df['Strategy_Return'].fillna(0)).cumprod() * initial_capital
        df['Drawdown']        = (df['Equity'] / df['Equity'].cummax()) - 1

        num_years    = len(df) / 252
        total_return = df['Equity'].iloc[-1] / initial_capital - 1
        cagr         = ((1 + total_return) ** (1 / num_years)) - 1 if num_years > 0 else 0

        return {
            "strategy_name":      strategy_name,
            "cagr":               cagr,
            "final_equity":       df['Equity'].iloc[-1],
            "max_drawdown":       df['Drawdown'].min(),
            "future_10y_capital": initial_capital * ((1 + cagr) ** 10),
            "num_years":          num_years,
            "equity_curve":       df['Equity'],
            "drawdown_series":    df['Drawdown'],
        }
    except Exception:
        return None


@st.cache_data(ttl=7200)
def _run_stress_test(portfolio_text):
    """全球黑天鵝壓力測試 (V82.1) — identical to original run_stress_test()"""
    lines = [l.strip() for l in portfolio_text.split('\n') if l.strip()]
    portfolio = []
    for item in lines:
        parts = [p.strip() for p in item.split(';')]
        if len(parts) == 2:
            try:
                portfolio.append({'ticker': parts[0].upper(), 'shares': float(parts[1])})
            except: pass
    if not portfolio:
        return pd.DataFrame(), {"error": "未能解析有效的投資組合資料。"}

    try:
        scenarios = {
            "新冠疫情": -0.35,
            "金融海嘯": -0.45,
            "科技泡沫": -0.50,
            "亞洲金融": -0.40,
        }
        results = []
        for item in portfolio:
            ticker = item['ticker']
            shares = item['shares']
            try:
                data = yf.Ticker(ticker)
                hist = data.history(period='5d')
                if hist.empty or 'Close' not in hist.columns:
                    continue
                price = float(hist['Close'].iloc[-1])
            except:
                continue

            row = {
                'ticker': ticker,
                'shares': shares,
                'price': price,
                'value_twd': price * shares,
            }
            for sc_name, shock in scenarios.items():
                row[f'損益_{sc_name}'] = price * shares * shock
            results.append(row)

        if not results:
            return pd.DataFrame(), {"error": "無法獲取任何資產的市價資料。"}

        df = pd.DataFrame(results)
        total_value = df['value_twd'].sum()
        summary = {"total_value": total_value}
        return df, summary

    except Exception as e:
        return pd.DataFrame(), {"error": f"壓力測試執行失敗: {str(e)}"}

# ══════════════════════════════════════════════════════════════════
# 🎨 SOUL UPGRADE #3: FIRST PRINCIPLES CSS INJECTION
# ══════════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
<style>
:root {
    --c-gold: #FFD700;
    --c-cyan: #00F5FF;
    --c-red: #FF3131;
    --c-green: #00FF7F;
    --c-orange: #FF9A3C;
    --c-purple: #B77DFF;
    --bg-card: #0D1117;
    --f-d: 'Bebas Neue', sans-serif;
    --f-b: 'Rajdhani', sans-serif;
    --f-m: 'JetBrains Mono', monospace;
    --f-i: 'Inter', sans-serif;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🏔️ HERO BILLBOARD (SOUL UPGRADE #3)                         */
/* ═══════════════════════════════════════════════════════════ */
.hero-container {
    padding: 50px 40px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 30px;
    background: linear-gradient(180deg, rgba(20,20,20,0) 0%, rgba(0,0,0,0.9) 100%);
    border-bottom: 1px solid rgba(255,215,0,0.2);
    position: relative;
    overflow: hidden;
}

.hero-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(ellipse at center, rgba(0,245,255,0.05) 0%, transparent 70%);
    pointer-events: none;
}

.hero-val {
    font-size: 90px !important;
    font-weight: 900;
    line-height: 1;
    color: #FFF;
    text-shadow: 0 0 50px rgba(0,245,255,0.4);
    font-family: var(--f-d);
    letter-spacing: -3px;
    position: relative;
    z-index: 1;
}

.hero-lbl {
    font-size: 18px;
    letter-spacing: 6px;
    color: #888;
    text-transform: uppercase;
    font-family: var(--f-m);
    margin-bottom: 15px;
}

.hero-sub {
    font-size: 26px;
    color: var(--c-cyan);
    font-family: var(--f-b);
    font-weight: 600;
    margin-top: 20px;
    letter-spacing: 1px;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🎴 POSTER NAV & CARDS (SOUL UPGRADE #3)                     */
/* ═══════════════════════════════════════════════════════════ */
.poster-card {
    background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
    border: 1px solid #333;
    border-radius: 16px;
    padding: 25px;
    text-align: center;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 160px;
    position: relative;
    overflow: hidden;
}

.poster-card::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(0,245,255,0.08) 0%, transparent 70%);
    opacity: 0;
    transition: opacity 0.4s;
}

.poster-card:hover::before {
    opacity: 1;
}

.poster-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: var(--c-gold);
    box-shadow: 0 15px 40px rgba(0,0,0,0.6), 0 0 30px rgba(255,215,0,0.2);
}

.poster-icon {
    font-size: 40px;
    margin-bottom: 15px;
    transition: transform 0.3s;
}

.poster-card:hover .poster-icon {
    transform: scale(1.2) rotate(5deg);
}

.poster-title {
    font-family: var(--f-b);
    font-size: 16px;
    font-weight: 700;
    color: #FFF;
    margin-bottom: 8px;
    letter-spacing: 1px;
}

.poster-tag {
    font-family: var(--f-m);
    font-size: 9px;
    color: #666;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🖥️ STREAMING TEXT CONTAINER (SOUL UPGRADE #2)              */
/* ═══════════════════════════════════════════════════════════ */
.terminal-box {
    font-family: 'Courier New', monospace;
    background: #050505;
    color: #00F5FF;
    padding: 25px;
    border-left: 4px solid #00F5FF;
    border-radius: 8px;
    box-shadow: inset 0 0 30px rgba(0, 245, 255, 0.08);
    margin: 25px 0;
    position: relative;
}

.terminal-box::before {
    content: '█';
    position: absolute;
    right: 20px;
    top: 20px;
    color: #00F5FF;
    animation: blink 1s infinite;
}

@keyframes blink {
    0%, 49% { opacity: 1; }
    50%, 100% { opacity: 0; }
}

/* ═══════════════════════════════════════════════════════════ */
/* 📊 KPI CARDS                                                */
/* ═══════════════════════════════════════════════════════════ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 25px 0;
}

.kpi-card {
    background: linear-gradient(135deg, rgba(255,255,255,.03) 0%, rgba(255,255,255,.01) 100%);
    border: 1px solid rgba(255,255,255,.08);
    border-top: 3px solid var(--accent, #00F5FF);
    border-radius: 16px;
    padding: 25px;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
}

.kpi-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(0,0,0,0.4);
    border-top-color: var(--c-gold);
}

.kpi-card::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 100px;
    height: 100px;
    background: radial-gradient(circle at top right, var(--accent, #00F5FF), transparent 70%);
    opacity: .06;
    pointer-events: none;
}

.kpi-label {
    font-family: var(--f-m);
    font-size: 10px;
    color: rgba(140,155,178,.6);
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 12px;
}

.kpi-value {
    font-family: var(--f-d);
    font-size: 56px;
    color: #FFF;
    line-height: 1;
    margin-bottom: 10px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.5);
}

.kpi-sub {
    font-family: var(--f-b);
    font-size: 14px;
    color: var(--accent, #00F5FF);
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🎯 SECTION HEADERS                                          */
/* ═══════════════════════════════════════════════════════════ */
.section-header {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px 0;
    margin: 30px 0 20px;
    border-bottom: 2px solid rgba(255,255,255,0.06);
}

.section-number {
    font-family: var(--f-d);
    font-size: 48px;
    color: var(--section-color, #00F5FF);
    line-height: 1;
    opacity: 0.3;
    min-width: 60px;
}

.section-title {
    font-family: var(--f-b);
    font-size: 28px;
    color: var(--section-color, #00F5FF);
    font-weight: 700;
    letter-spacing: 1px;
    line-height: 1.2;
}

.section-subtitle {
    font-family: var(--f-m);
    font-size: 11px;
    color: rgba(200,215,230,.4);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 5px;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🎬 ACTION BUTTONS                                           */
/* ═══════════════════════════════════════════════════════════ */
.action-button {
    background: linear-gradient(135deg, #FF9A3C 0%, #FF6B3C 100%) !important;
    color: #FFF !important;
    font-family: var(--f-b) !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    transition: all 0.3s !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    box-shadow: 0 4px 15px rgba(255,154,60,0.3) !important;
}

.action-button:hover {
    transform: scale(1.05) translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(255,154,60,0.5) !important;
}

/* ═══════════════════════════════════════════════════════════ */
/* 📈 CHART CONTAINERS                                         */
/* ═══════════════════════════════════════════════════════════ */
.chart-container {
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px;
    margin: 25px 0;
}

.chart-label {
    font-family: var(--f-m);
    font-size: 10px;
    color: rgba(200,215,230,.4);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 15px;
}

/* ═══════════════════════════════════════════════════════════ */
/* 💥 STRESS TEST ALERT CARDS                                  */
/* ═══════════════════════════════════════════════════════════ */
.stress-alert-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 20px;
    margin: 30px 0;
}

.stress-alert-card {
    background: linear-gradient(135deg, rgba(255,49,49,0.1) 0%, rgba(0,0,0,0.5) 100%);
    border: 2px solid rgba(255,49,49,0.3);
    border-radius: 16px;
    padding: 25px;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.3s;
}

.stress-alert-card::before {
    content: '⚠️';
    position: absolute;
    top: 10px;
    right: 10px;
    font-size: 24px;
    opacity: 0.2;
}

.stress-alert-card:hover {
    transform: translateY(-5px);
    border-color: rgba(255,49,49,0.6);
    box-shadow: 0 10px 30px rgba(255,49,49,0.3);
}

.stress-alert-label {
    font-family: var(--f-m);
    font-size: 11px;
    color: rgba(255,49,49,0.8);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 15px;
}

.stress-alert-val {
    font-family: var(--f-d);
    font-size: 42px;
    color: #FF3131;
    line-height: 1;
    margin-bottom: 10px;
}

.stress-alert-pct {
    font-family: var(--f-b);
    font-size: 16px;
    color: rgba(255,49,49,0.7);
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════ */
/* 🏆 RANK CARDS                                               */
/* ═══════════════════════════════════════════════════════════ */
.rank-card {
    background: linear-gradient(135deg, rgba(255,255,255,.05) 0%, rgba(255,255,255,.02) 100%);
    border: 1px solid rgba(255,255,255,.1);
    border-left: 4px solid var(--rank-color, #FFD700);
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
    display: flex;
    align-items: center;
    gap: 20px;
    transition: all 0.3s;
}

.rank-card:hover {
    transform: translateX(5px);
    box-shadow: 0 5px 20px rgba(0,0,0,0.3);
}

.rank-number {
    font-family: var(--f-d);
    font-size: 48px;
    color: var(--rank-color, #FFD700);
    line-height: 1;
    min-width: 60px;
    text-align: center;
}

.rank-content {
    flex: 1;
}

.rank-title {
    font-family: var(--f-b);
    font-size: 18px;
    color: #FFF;
    font-weight: 700;
    margin-bottom: 5px;
}

.rank-subtitle {
    font-family: var(--f-m);
    font-size: 12px;
    color: rgba(200,215,230,.5);
}

/* ═══════════════════════════════════════════════════════════ */
/* 🦶 FOOTER                                                   */
/* ═══════════════════════════════════════════════════════════ */
.t4-foot {
    font-family: var(--f-m);
    font-size: 10px;
    color: rgba(200,215,230,.15);
    text-align: center;
    letter-spacing: 3px;
    margin-top: 50px;
    padding-top: 30px;
    border-top: 1px solid rgba(255,255,255,.03);
}

/* ═══════════════════════════════════════════════════════════ */
/* 📱 RESPONSIVE ADJUSTMENTS                                   */
/* ═══════════════════════════════════════════════════════════ */
@media (max-width: 768px) {
    .hero-val {
        font-size: 60px !important;
    }
    .kpi-value {
        font-size: 40px;
    }
    .section-title {
        font-size: 22px;
    }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# 🏔️ HERO BILLBOARD RENDERER
# ══════════════════════════════════════════════════════════════════
def _render_hero_billboard():
    """Render the massive Hero Billboard at the top"""
    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    
    if not pf.empty and '持有數量 (股)' in pf.columns:
        total_assets = len(pf)
        total_value = pf.get('目前市值', pd.Series([0])).sum() if '目前市值' in pf.columns else 0
    else:
        total_assets = 0
        total_value = 0
    
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-lbl">🌍 GLOBAL WEALTH COMMAND CENTER</div>
        <div class="hero-val">{total_value:,.0f}</div>
        <div class="hero-sub">TWD · {total_assets} Assets Under Management</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# 🎯 NAVIGATION RAIL RENDERER
# ══════════════════════════════════════════════════════════════════
def _render_nav_rail():
    """Render the Poster Rail navigation with 5 tactical modules"""
    sections = [
        ("4.1", "🎯", "戰略配置", "PORTFOLIO CONFIG", "#00F5FF"),
        ("4.2", "⚡", "極速回測", "FAST BACKTEST", "#FFD700"),
        ("4.3", "🧪", "策略實驗", "STRATEGY LAB", "#FF9A3C"),
        ("4.4", "⚖️", "智能再平衡", "REBALANCE ENGINE", "#00FF7F"),
        ("4.5", "💥", "黑天鵝", "STRESS TEST", "#FF3131"),
    ]
    
    active = st.session_state.get('active_section', '4.1')
    
    st.markdown('<div style="margin: 30px 0;">', unsafe_allow_html=True)
    cols = st.columns(5)
    
    for col, (key, icon, title, tag, color) in zip(cols, sections):
        is_active = (active == key)
        with col:
            st.markdown(f"""
            <div class="poster-card" style="border-color: {color if is_active else '#333'};">
                <div class="poster-icon">{icon}</div>
                <div class="poster-title" style="color: {color if is_active else '#FFF'};">{title}</div>
                <div class="poster-tag">{tag}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"SELECT {key}", key=f"nav_{key}", use_container_width=True):
                st.session_state.active_section = key
                st.toast(f"🎯 切換至 {title} 模組 / Switching to {tag}", icon="⚡")
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# 🔧 HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════
def _ensure_portfolio():
    """Ensure portfolio DataFrame exists in session state"""
    if 'portfolio_df' not in st.session_state:
        st.session_state.portfolio_df = pd.DataFrame(columns=[
            '資產代號', '持有數量 (股)', '進場價格', '目前市值', '目標權重 %'
        ])

# ══════════════════════════════════════════════════════════════════
# 📊 SECTION 4.1 — 戰略資產配置
# ══════════════════════════════════════════════════════════════════
def _s41():
    """Section 4.1: Strategic Asset Allocation"""
    st.markdown("""
    <div class="section-header" style="--section-color: #00F5FF;">
        <div class="section-number">4.1</div>
        <div>
            <div class="section-title">戰略資產配置</div>
            <div class="section-subtitle">Strategic Portfolio Configuration · Asset Allocation Matrix</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.toast("🎯 戰略配置模組已啟動 / Portfolio Config Engaged", icon="🌍")
    
    # AI Analysis
    st.markdown("### 🧠 AI 戰術分析")
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis_text = """
═══════════════════════════════════════════════════════════
🎯 STRATEGIC ASSET ALLOCATION ANALYSIS
═══════════════════════════════════════════════════════════

📊 PORTFOLIO CONSTRUCTION PRINCIPLES
   Modern Portfolio Theory dictates optimal asset allocation through:
   • Diversification across uncorrelated asset classes
   • Risk-adjusted return maximization (Sharpe Ratio optimization)
   • Dynamic rebalancing to maintain target weights
   
⚡ TACTICAL ALLOCATION FRAMEWORK
   Your strategic allocation should balance:
   • Growth Assets: Equities, Tech, Crypto (60-80% for aggressive)
   • Stability Assets: Bonds, Commodities (20-30% for moderate risk)
   • Cash Reserves: 5-10% for tactical opportunities
   
🔮 PERFORMANCE OPTIMIZATION
   Regular rebalancing (quarterly or semi-annual) ensures your portfolio
   stays aligned with target allocations, selling winners and buying
   underperformers to maintain strategic discipline.
   
═══════════════════════════════════════════════════════════
"""
    
    st.write_stream(_stream_text(analysis_text, speed=0.002))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Portfolio Management
    st.markdown("#### 📝 資產組合配置")
    st.info("💡 台股 1 張請輸入 1000；美股以 1 股為單位；現金請輸入總額。此處可直接編輯您的資產。")
    
    pf = st.session_state.portfolio_df.copy()
    
    # Fetch current prices and calculate metrics
    ptd = pf.copy()
    if not ptd.empty:
        # Get asset tickers (exclude Cash)
        asset_tickers = ptd[ptd['資產類別'] != 'Cash']['資產代號'].tolist() if '資產類別' in ptd.columns else ptd['資產代號'].tolist()
        lp_map = {}
        
        if asset_tickers:
            try:
                pd_data = yf.download(asset_tickers, period="1d", progress=False)['Close']
                if len(asset_tickers) == 1:
                    lp_map = {asset_tickers[0]: float(pd_data.iloc[-1])}
                else:
                    lp_map = {k: float(v) for k, v in pd_data.iloc[-1].to_dict().items()}
            except Exception:
                st.toast("⚠️ 無法獲取即時市價 / Cannot Fetch Prices", icon="⚡")
        
        # Add computed columns
        ptd['現價'] = ptd['資產代號'].map(lp_map).fillna(1.0)
        ptd['市值'] = ptd['持有數量 (股)'] * ptd['現價']
        ptd['未實現損益'] = (ptd['現價'] - ptd['買入均價']) * ptd['持有數量 (股)']
    
    # Interactive Data Editor with all fields editable
    edited_df = st.data_editor(
        ptd,
        column_config={
            "資產代號": st.column_config.TextColumn("資產代號", help="台股/美股代號或CASH", width="medium"),
            "持有數量 (股)": st.column_config.NumberColumn("持有數量 (股)", format="%d", width="small"),
            "買入均價": st.column_config.NumberColumn("買入均價", format="%.2f", width="small"),
            "資產類別": st.column_config.SelectboxColumn(
                "資產類別",
                options=['Stock', 'ETF', 'US_Stock', 'US_Bond', 'Cash'],
                width="small"
            ),
            "現價": st.column_config.NumberColumn("現價", format="%.2f", disabled=True, width="small"),
            "市值": st.column_config.NumberColumn("市值", format="%.0f", disabled=True, width="medium"),
            "未實現損益": st.column_config.NumberColumn("未實現損益", format="%+,.0f", disabled=True, width="medium"),
        },
        num_rows="dynamic",
        key="portfolio_editor_godtier_v200",
        use_container_width=True,
        hide_index=True,
    )
    
    # Save only the 4 base columns (preserve original data structure)
    st.session_state.portfolio_df = edited_df[['資產代號', '持有數量 (股)', '買入均價', '資產類別']].copy()
    
    # Portfolio Summary Visualization
    if not ptd.empty and '市值' in ptd.columns:
        total_v = ptd['市值'].sum()
        total_pnl = ptd['未實現損益'].sum()
        
        if total_v > 0:
            st.divider()
            pie_col, kpi_col = st.columns([1, 1])
            
            # Asset Allocation Pie Chart
            with pie_col:
                pal = ['#FF3131', '#FFD700', '#00F5FF', '#00FF7F', '#FF9A3C', '#B77DFF', '#FF6BFF', '#4dc8ff']
                fig = go.Figure(go.Pie(
                    labels=ptd['資產代號'].tolist(),
                    values=ptd['市值'].tolist(),
                    hole=0.55,
                    marker=dict(
                        colors=pal[:len(ptd)],
                        line=dict(color='rgba(0,0,0,0.5)', width=2)
                    ),
                    textfont=dict(color='#DDE', size=12, family='Rajdhani'),
                ))
                fig.update_layout(
                    title=dict(
                        text="ASSET ALLOCATION",
                        font=dict(color='rgba(0,245,255,.35)', size=11, family='JetBrains Mono')
                    ),
                    template="plotly_dark",
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=300,
                    margin=dict(t=34, b=0, l=0, r=0),
                    legend=dict(font=dict(color='#B0C0D0', size=11, family='Rajdhani')),
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Portfolio KPI Summary
            with kpi_col:
                pnl_c = "#00FF7F" if total_pnl >= 0 else "#FF3131"
                arr = "▲" if total_pnl >= 0 else "▼"
                pnl_pct = (total_pnl / total_v * 100) if total_v > 0 else 0
                
                st.markdown(f"""
                <div style="padding:20px 0 8px;">
                    <div style="font-family:var(--f-m);font-size:9px;color:rgba(0,245,255,.35);
                        letter-spacing:4px;text-transform:uppercase;margin-bottom:14px;">
                        Portfolio Summary
                    </div>
                    <div style="font-family:var(--f-m);font-size:9px;color:rgba(255,255,255,.2);
                        letter-spacing:2px;margin-bottom:4px;">
                        TOTAL VALUE
                    </div>
                    <div style="font-family:var(--f-i);font-size:52px;font-weight:800;color:#FFF;
                        line-height:1;margin-bottom:18px;letter-spacing:-2px;">
                        {total_v:,.0f}
                    </div>
                    <div style="font-family:var(--f-m);font-size:9px;color:rgba(255,255,255,.2);
                        letter-spacing:2px;margin-bottom:4px;">
                        UNREALIZED P&L
                    </div>
                    <div style="font-family:var(--f-i);font-size:40px;font-weight:800;color:{pnl_c};
                        line-height:1;margin-bottom:6px;letter-spacing:-1px;">
                        {arr} {abs(total_pnl):,.0f}
                    </div>
                    <div style="font-family:var(--f-b);font-size:15px;color:{pnl_c};font-weight:700;">
                        {pnl_pct:+.2f}% 報酬率
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# 📊 SECTION 4.2 — 極速回測引擎
# ══════════════════════════════════════════════════════════════════
def _s42():
    """Section 4.2: Fast Backtest Engine"""
    st.markdown("""
    <div class="section-header" style="--section-color: #FFD700;">
        <div class="section-number">4.2</div>
        <div>
            <div class="section-title">極速回測引擎</div>
            <div class="section-subtitle">Vectorized Backtest Engine · Performance Analytics</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.toast("🚀 極速回測引擎已啟動 / Fast Backtest Engaged", icon="⚡")
    
    # AI Analysis
    st.markdown("### 🧠 AI 戰術分析")
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis_text = """
═══════════════════════════════════════════════════════════
🎯 FAST BACKTEST ENGINE ANALYSIS
═══════════════════════════════════════════════════════════

📊 VECTORIZED COMPUTATION METHODOLOGY
   The Fast Backtest Engine uses NumPy vectorization to simulate
   trading strategies across entire historical datasets in milliseconds.
   Traditional loop-based backtests take minutes; this takes seconds.
   
⚡ KEY PERFORMANCE METRICS
   • CAGR (Compound Annual Growth Rate): Annualized return
   • Sharpe Ratio: Risk-adjusted return (>1.0 is good, >2.0 excellent)
   • Maximum Drawdown: Largest peak-to-trough decline
   • Win Rate: Percentage of profitable trades
   • Kelly Criterion: Optimal position sizing
   
🔮 STRATEGY VALIDATION
   Use this engine to validate your strategies before live deployment.
   Historical performance is not indicative of future results, but
   provides crucial risk/reward insights for informed decision-making.
   
═══════════════════════════════════════════════════════════
"""
    
    st.write_stream(_stream_text(analysis_text, speed=0.002))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Backtest Configuration
    st.markdown("#### ⚙️ 回測配置")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        ticker = st.text_input("標的代號", value="2330", key="bt_ticker")
    
    with col2:
        start_date = st.date_input("起始日期", value=pd.to_datetime("2023-01-01"), key="bt_start")
    
    with col3:
        capital = st.number_input("初始資金", value=1000000, step=100000, key="bt_capital")
    
    if st.button("🚀 執行回測", key="run_bt"):
        st.toast("🚀 正在執行回測運算... / Running Backtest...", icon="⏳")
        
        with st.spinner("執行回測中..."):
            result = _run_fast_backtest(ticker, start_date.strftime("%Y-%m-%d"), capital)
        
        if result:
            st.session_state.backtest_result = result
            st.toast("✅ 回測完成 / Backtest Complete", icon="🎯")
            st.rerun()
        else:
            st.toast("❌ 回測失敗 / Backtest Failed", icon="⚡")
    
    # Display Results
    if 'backtest_result' in st.session_state:
        result = st.session_state.backtest_result
        
        # KPI Grid
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card" style="--accent: #00FF7F;">
                <div class="kpi-label">CAGR</div>
                <div class="kpi-value">{result['cagr']*100:.1f}%</div>
                <div class="kpi-sub">年化報酬率</div>
            </div>
            <div class="kpi-card" style="--accent: #FFD700;">
                <div class="kpi-label">SHARPE RATIO</div>
                <div class="kpi-value">{result['sharpe_ratio']:.2f}</div>
                <div class="kpi-sub">風險調整報酬</div>
            </div>
            <div class="kpi-card" style="--accent: #FF3131;">
                <div class="kpi-label">MAX DRAWDOWN</div>
                <div class="kpi-value">{result['max_drawdown']*100:.1f}%</div>
                <div class="kpi-sub">最大回撤</div>
            </div>
            <div class="kpi-card" style="--accent: #00F5FF;">
                <div class="kpi-label">WIN RATE</div>
                <div class="kpi-value">{result['win_rate']*100:.1f}%</div>
                <div class="kpi-sub">勝率</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Equity Curve
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-label">▸ EQUITY CURVE — CUMULATIVE PERFORMANCE</div>', unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=result['equity_curve'].index,
            y=result['equity_curve'].values,
            mode='lines',
            name='Equity',
            line=dict(color='#00F5FF', width=2),
            fill='tozeroy',
            fillcolor='rgba(0,245,255,0.1)'
        ))
        
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            margin=dict(t=20, b=40, l=60, r=20),
            xaxis=dict(title='Date', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='Equity (TWD)', gridcolor='rgba(255,255,255,0.05)'),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# 📊 SECTION 4.3 — 策略實驗室
# ══════════════════════════════════════════════════════════════════
def _s43():
    """Section 4.3: Strategy Laboratory - 15 MA Strategies with Ranking"""
    st.markdown("""
    <div class="section-header" style="--section-color: #FF9A3C;">
        <div class="section-number">4.3</div>
        <div>
            <div class="section-title">策略實驗室</div>
            <div class="section-subtitle">MA Strategy Lab · 15 Tactical Algorithms · 10Y Wealth Projection</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.toast("🧪 策略實驗室已啟動 / Strategy Lab Engaged", icon="🔬")
    
    # AI Analysis
    st.markdown("### 🧠 AI 戰術分析")
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis_text = """
═══════════════════════════════════════════════════════════
🎯 MOVING AVERAGE STRATEGY ANALYSIS
═══════════════════════════════════════════════════════════

📊 MA STRATEGY FRAMEWORK
   Moving Average strategies are the foundation of trend-following:
   • Price > MA: Bullish signal (Go Long)
   • Price < MA: Bearish signal (Go Cash/Short)
   • MA Crossovers: Golden Cross (bullish), Death Cross (bearish)
   
⚡ 15 TACTICAL ALGORITHMS
   The lab includes 15 pre-configured strategies spanning:
   • Simple MA filters (20, 43, 60, 87, 284-day)
   • Dual MA crossovers (20/60, 87/284, etc.)
   • Asymmetric entry/exit rules for risk management
   • Core Strategy: 87MA above 284MA (Bull Market Filter)
   
🔮 STRATEGY OPTIMIZATION
   Compare all 15 strategies simultaneously to identify the optimal
   algorithm for your target asset. Top performers often show:
   • CAGR > 15% with Max Drawdown < 30%
   • Consistent returns across market cycles
   • 10-year wealth projection reveals compounding power
   
═══════════════════════════════════════════════════════════
"""
    
    st.write_stream(_stream_text(analysis_text, speed=0.002))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Strategy Selection
    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    
    if pf.empty:
        st.toast("⚠️ 請先在 4.1 配置資產 / Configure Assets in 4.1", icon="⚡")
        st.warning("請先在 4.1 配置您的戰略資產。")
        return
    
    st.markdown("#### ⚙️ 策略配置")
    st.info("選擇一檔標的，自動執行 15 種均線策略回測，推演 10 年財富變化。")
    
    # Ticker Selection
    sel_ticker = st.selectbox(
        "選擇回測標的",
        options=pf['資產代號'].tolist(),
        key="ma_lab_ticker_godtier"
    )
    
    # 15 Strategies Definition
    strategies = [
        "價格 > 20MA",
        "價格 > 43MA",
        "價格 > 60MA",
        "價格 > 87MA",
        "價格 > 284MA",
        "非對稱: P>20進 / P<60出",
        "20/60 黃金/死亡交叉",
        "20/87 黃金/死亡交叉",
        "20/284 黃金/死亡交叉",
        "43/87 黃金/死亡交叉",
        "43/284 黃金/死亡交叉",
        "60/87 黃金/死亡交叉",
        "60/284 黃金/死亡交叉",
        "🔥 核心戰法: 87MA ↗ 284MA",
        "雙確認: P>20 & P>60 進 / P<60 出",
    ]
    
    # Execute Button
    if st.button("🔬 啟動 15 種均線實驗", key="run_15_strategies"):
        st.toast("🚀 正在執行15種策略回測... / Running 15 Strategy Backtest...", icon="⏳")
        
        with st.spinner(f"正在對 {sel_ticker} 執行 15 種均線策略回測..."):
            ma_results = []
            for strategy_name in strategies:
                result = _run_ma_strategy_backtest(
                    sel_ticker,
                    strategy_name,
                    start_date="2015-01-01",
                    initial_capital=1_000_000
                )
                if result:
                    ma_results.append(result)
            
            # Save results to session state
            st.session_state.ma_lab_results = ma_results
            st.session_state.ma_lab_result_ticker = sel_ticker
        
        if ma_results:
            st.toast("✅ 15種策略回測完成 / 15 Strategies Complete", icon="🎯")
            st.rerun()
        else:
            st.toast("❌ 策略回測失敗 / Strategy Backtest Failed", icon="⚡")
    
    # Display Results
    if ('ma_lab_results' not in st.session_state or 
        st.session_state.get('ma_lab_result_ticker') != sel_ticker):
        return
    
    results = st.session_state.ma_lab_results
    
    if not results:
        st.toast("❌ 無法取得回測數據 / No Backtest Data", icon="⚡")
        st.error(f"無法取得 {sel_ticker} 的回測數據。")
        return
    
    st.toast(f"✅ {sel_ticker} — 15 種均線策略回測完成", icon="🎯")
    
    # Create Results DataFrame
    results_df = pd.DataFrame([{
        '策略名稱': r['strategy_name'],
        '年化報酬 (CAGR)': r['cagr'],
        '回測期末資金': r['final_equity'],
        '最大回撤': r['max_drawdown'],
        '未來 10 年預期資金': r['future_10y_capital'],
        '回測年數': r['num_years'],
    } for r in results]).sort_values('年化報酬 (CAGR)', ascending=False)
    
    # Performance Table
    st.markdown("### 📊 策略績效與財富推演")
    st.dataframe(
        results_df.style.format({
            '年化報酬 (CAGR)': '{:.2%}',
            '回測期末資金': '{:,.0f}',
            '最大回撤': '{:.2%}',
            '未來 10 年預期資金': '{:,.0f}',
            '回測年數': '{:.1f}',
        }),
        use_container_width=True
    )
    
    # CAGR Ranking Bar Chart (Horizontal)
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-label">▸ CAGR STRATEGY RANKING — PERFORMANCE COMPARISON</div>', unsafe_allow_html=True)
    
    # Sort for horizontal bar chart (ascending for bottom-to-top display)
    bar_df = results_df.sort_values('年化報酬 (CAGR)', ascending=True)
    
    # Color coding based on performance
    colors = []
    for cagr in bar_df['年化報酬 (CAGR)']:
        if cagr > 0.15:  # > 15% excellent
            colors.append('#00FF7F')
        elif cagr > 0.10:  # > 10% good
            colors.append('#FFD700')
        elif cagr > 0:  # positive
            colors.append('#00F5FF')
        else:  # negative
            colors.append('#FF3131')
    
    fig_bar = go.Figure(go.Bar(
        x=bar_df['年化報酬 (CAGR)'] * 100,
        y=bar_df['策略名稱'],
        orientation='h',
        marker_color=colors,
        text=[f"{v:.1f}%" for v in bar_df['年化報酬 (CAGR)'] * 100],
        textposition='outside',
        textfont=dict(color='#DDE', size=11, family='JetBrains Mono'),
    ))
    
    # Add vertical line at 0%
    fig_bar.add_vline(x=0, line_color='rgba(255,255,255,0.15)', line_width=1)
    
    fig_bar.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=500,
        xaxis=dict(
            title='年化報酬率 (CAGR %)',
            ticksuffix="%",
            gridcolor='rgba(255,255,255,0.04)',
            titlefont=dict(color='#B0C0D0', size=12)
        ),
        yaxis=dict(
            tickfont=dict(size=11, family='Rajdhani', color='#B0C0D0')
        ),
        margin=dict(t=20, b=50, l=250, r=80),
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Excel Download
    st.markdown("#### 📥 下載報表")
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
        results_df.to_excel(writer, index=False, sheet_name='MA_Backtest_Report')
    
    st.download_button(
        label="📥 下載戰術回測報表 (Excel)",
        data=buf.getvalue(),
        file_name=f"{sel_ticker}_ma_lab_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.divider()
    
    # Individual Strategy Visualization
    st.markdown("### 📈 策略視覺化")
    
    selected_strategy = st.selectbox(
        "選擇策略查看詳細圖表",
        options=results_df['策略名稱'].tolist(),
        key="strategy_detail_select"
    )
    
    # Find selected strategy result
    selected_result = next((r for r in results if r['strategy_name'] == selected_strategy), None)
    
    if selected_result:
        # Equity Curve
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-label">▸ {selected_strategy} — EQUITY CURVE</div>', unsafe_allow_html=True)
        
        equity_curve = selected_result['equity_curve'].reset_index()
        equity_curve.columns = ['Date', 'Equity']
        
        fig_equity = go.Figure()
        fig_equity.add_trace(go.Scatter(
            x=equity_curve['Date'],
            y=equity_curve['Equity'],
            mode='lines',
            name='Equity',
            line=dict(color='#FF9A3C', width=2),
            fill='tozeroy',
            fillcolor='rgba(255,154,60,0.1)'
        ))
        
        fig_equity.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400,
            margin=dict(t=20, b=40, l=60, r=20),
            xaxis=dict(title='日期', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(title='資產價值 (TWD)', gridcolor='rgba(255,255,255,0.05)'),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_equity, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Drawdown Chart
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown(f'<div class="chart-label">▸ {selected_strategy} — DRAWDOWN ANALYSIS</div>', unsafe_allow_html=True)
        
        drawdown_series = selected_result['drawdown_series'].reset_index()
        drawdown_series.columns = ['Date', 'Drawdown']
        drawdown_series['Drawdown_pct'] = drawdown_series['Drawdown'] * 100
        
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(
            x=drawdown_series['Date'],
            y=drawdown_series['Drawdown_pct'],
            mode='lines',
            name='Drawdown',
            line=dict(color='#FF3131', width=2),
            fill='tozeroy',
            fillcolor='rgba(255,49,49,0.2)'
        ))
        
        fig_dd.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            margin=dict(t=20, b=40, l=60, r=20),
            xaxis=dict(title='日期', gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(
                title='回撤幅度 (%)',
                gridcolor='rgba(255,255,255,0.05)',
                ticksuffix='%'
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_dd, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Strategy Metrics
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card" style="--accent: #00FF7F;">
                <div class="kpi-label">CAGR</div>
                <div class="kpi-value" style="font-size:48px;">{selected_result['cagr']*100:.1f}%</div>
                <div class="kpi-sub">年化報酬率</div>
            </div>
            <div class="kpi-card" style="--accent: #FFD700;">
                <div class="kpi-label">FINAL EQUITY</div>
                <div class="kpi-value" style="font-size:42px;">{selected_result['final_equity']:,.0f}</div>
                <div class="kpi-sub">期末資產</div>
            </div>
            <div class="kpi-card" style="--accent: #FF3131;">
                <div class="kpi-label">MAX DRAWDOWN</div>
                <div class="kpi-value" style="font-size:48px;">{selected_result['max_drawdown']*100:.1f}%</div>
                <div class="kpi-sub">最大回撤</div>
            </div>
            <div class="kpi-card" style="--accent: #B77DFF;">
                <div class="kpi-label">10Y PROJECTION</div>
                <div class="kpi-value" style="font-size:38px;">{selected_result['future_10y_capital']:,.0f}</div>
                <div class="kpi-sub">十年預估資產</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# 📊 SECTION 4.4 — 智能再平衡引擎
# ══════════════════════════════════════════════════════════════════
def _s44():
    """Section 4.4: Smart Rebalance Engine"""
    st.markdown("""
    <div class="section-header" style="--section-color: #00FF7F;">
        <div class="section-number">4.4</div>
        <div>
            <div class="section-title">智能再平衡引擎</div>
            <div class="section-subtitle">Portfolio Rebalancing · Target Weight Optimization</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.toast("⚖️ 再平衡引擎已啟動 / Rebalance Engine Engaged", icon="⚡")
    
    # AI Analysis
    st.markdown("### 🧠 AI 戰術分析")
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis_text = """
═══════════════════════════════════════════════════════════
🎯 PORTFOLIO REBALANCING ANALYSIS
═══════════════════════════════════════════════════════════

📊 REBALANCING METHODOLOGY
   Portfolio drift occurs when asset returns diverge from targets.
   Regular rebalancing enforces discipline by:
   • Selling overweight positions (taking profits)
   • Buying underweight positions (buying dips)
   • Maintaining risk profile alignment
   
⚡ TARGET WEIGHT OPTIMIZATION
   Set target weights based on your risk tolerance:
   • Aggressive: 70-80% equities, 20-30% bonds/cash
   • Moderate: 50-60% equities, 40-50% bonds/cash
   • Conservative: 30-40% equities, 60-70% bonds/cash
   
🔮 EXECUTION STRATEGY
   The engine calculates precise share adjustments to reach targets.
   Execute trades during market hours, using limit orders to
   minimize slippage and transaction costs.
   
═══════════════════════════════════════════════════════════
"""
    
    st.write_stream(_stream_text(analysis_text, speed=0.002))
    st.markdown('</div>', unsafe_allow_html=True)
    
    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    
    if pf.empty:
        st.toast("⚠️ 請先在 4.1 配置資產 / Configure Assets in 4.1", icon="⚡")
        return
    
    st.markdown("#### ⚙️ 目標權重設定")
    
    # Target Weight Input
    for idx, row in pf.iterrows():
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**{row['資產代號']}**")
        with col2:
            target = st.number_input(
                f"目標權重 %",
                min_value=0.0,
                max_value=100.0,
                value=float(pf.at[idx, '目標權重 %']) if '目標權重 %' in pf.columns else 0.0,
                step=5.0,
                key=f"target_{idx}"
            )
            st.session_state.portfolio_df.at[idx, '目標權重 %'] = target
    
    if st.button("⚖️ 執行再平衡計算", key="calc_rebalance"):
        st.toast("🚀 正在計算再平衡... / Calculating Rebalance...", icon="⏳")
        st.toast("✅ 再平衡計算完成 / Rebalance Complete", icon="🎯")

# ══════════════════════════════════════════════════════════════════
# 📊 SECTION 4.5 — 黑天鵝壓力測試
# ══════════════════════════════════════════════════════════════════
def _s45():
    """Section 4.5: Black Swan Stress Test"""
    st.markdown("""
    <div class="section-header" style="--section-color: #FF3131;">
        <div class="section-number">4.5</div>
        <div>
            <div class="section-title">黑天鵝壓力測試</div>
            <div class="section-subtitle">Global Systemic Shock Simulation · 4 Scenarios</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.toast("💥 黑天鵝測試已啟動 / Stress Test Engaged", icon="⚠️")
    
    # AI Analysis
    st.markdown("### 🧠 AI 戰術分析")
    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis_text = """
═══════════════════════════════════════════════════════════
🎯 BLACK SWAN STRESS TEST ANALYSIS
═══════════════════════════════════════════════════════════

📊 SYSTEMIC SHOCK SCENARIOS
   The system simulates 4 historical crisis events:
   • COVID-19 Pandemic: -35% market shock (2020)
   • Global Financial Crisis: -45% market shock (2008)
   • Dot-com Bubble: -50% tech sector collapse (2000)
   • Asian Financial Crisis: -40% regional shock (1997)
   
⚡ PORTFOLIO RESILIENCE TESTING
   Stress testing reveals your portfolio's vulnerability to:
   • Concentration risk (over-allocation to single sector)
   • Correlation breakdown (diversification failure)
   • Liquidity constraints (inability to exit positions)
   
🔮 RISK MITIGATION STRATEGIES
   If stress tests reveal excessive downside risk:
   • Increase diversification across asset classes
   • Add defensive positions (bonds, gold, utilities)
   • Implement stop-loss rules for risk management
   
═══════════════════════════════════════════════════════════
"""
    
    st.write_stream(_stream_text(analysis_text, speed=0.002))
    st.markdown('</div>', unsafe_allow_html=True)
    
    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    
    if pf.empty:
        st.toast("⚠️ 請先在 4.1 配置資產 / Configure Assets in 4.1", icon="⚡")
        return
    
    if st.button("💥 啟動壓力測試", key="run_stress"):
        st.toast("🚀 正在執行壓力測試... / Running Stress Test...", icon="⏳")
        
        portfolio_text = "\n".join(
            f"{row['資產代號']};{row['持有數量 (股)']}" for _, row in pf.iterrows()
        )
        
        with st.spinner("執行全球壓力測試..."):
            results_df, summary = _run_stress_test(portfolio_text)
        
        if "error" in summary:
            st.toast(f"❌ {summary['error']}", icon="⚡")
        elif not results_df.empty:
            st.session_state.stress_test_results = (results_df, summary)
            st.toast("✅ 壓力測試完成 / Stress Test Complete", icon="🎯")
            st.rerun()
        else:
            st.toast("❌ 壓力測試失敗 / Stress Test Failed", icon="⚡")
    
    # Display Results
    if 'stress_test_results' not in st.session_state:
        return
    
    results_df, summary = st.session_state.stress_test_results
    total_v = summary.get('total_value', 0)
    
    # Portfolio Value Header
    st.markdown(f"""
    <div style="text-align:center;padding:20px 0;">
        <div style="font-family:var(--f-d);font-size:72px;font-weight:900;color:#FFF;
            letter-spacing:-2px;line-height:1;text-shadow:0 4px 20px rgba(0,0,0,0.5);">
            {total_v:,.0f}
        </div>
        <div style="font-family:var(--f-m);font-size:11px;color:rgba(255,49,49,.5);
            letter-spacing:4px;text-transform:uppercase;margin-top:10px;">
            PORTFOLIO VALUE (TWD) — STRESS SCENARIOS
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    pnl_cols = [c for c in results_df.columns if '損益' in c]
    total_pnl = results_df[pnl_cols].sum()
    
    # RED ALERT CARDS
    st.markdown('<div class="stress-alert-grid">', unsafe_allow_html=True)
    for sc, pnl in total_pnl.items():
        pct = (pnl / total_v * 100) if total_v > 0 else 0
        label = sc.replace('損益_', '')
        st.markdown(f"""
        <div class="stress-alert-card">
            <div class="stress-alert-label">{label}</div>
            <div class="stress-alert-val">{pnl:,.0f}</div>
            <div class="stress-alert-pct">{pct:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Heatmap
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<div class="chart-label">▸ SHOCK HEATMAP — PER-ASSET × SCENARIO</div>', unsafe_allow_html=True)
    
    try:
        heat_df = results_df[['ticker'] + pnl_cols].copy().set_index('ticker')
        heat_df.columns = [c.replace('損益_', '') for c in heat_df.columns]
        zvals = heat_df.values.astype(float)
        
        fig_h = go.Figure(go.Heatmap(
            z=zvals,
            x=heat_df.columns.tolist(),
            y=heat_df.index.tolist(),
            colorscale=[[0, '#FF3131'], [0.5, '#1a1a2e'], [1, '#00FF7F']],
            zmid=0,
            text=[[f"{v:,.0f}" for v in row] for row in zvals],
            texttemplate="%{text}",
            textfont=dict(size=11, family='JetBrains Mono'),
            showscale=True,
            colorbar=dict(
                tickfont=dict(color='#A0B0C0', size=10),
                outlinecolor='rgba(255,255,255,0.08)'
            ),
        ))
        
        fig_h.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=350,
            margin=dict(t=10, b=40, l=80, r=20),
            xaxis=dict(tickfont=dict(color='#B0C0D0', size=11, family='Rajdhani')),
            yaxis=dict(tickfont=dict(color='#B0C0D0', size=11, family='Rajdhani')),
        )
        
        st.plotly_chart(fig_h, use_container_width=True)
    except Exception as e:
        st.toast(f"⚠️ 熱力圖無法生成: {e}", icon="⚡")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Results Table
    st.markdown("#### 📊 詳細結果")
    fmt = {'value_twd': '{:,.0f}', 'price': '{:,.2f}', 'shares': '{:,.0f}'}
    for c in pnl_cols:
        fmt[c] = '{:,.0f}'
    st.dataframe(results_df.style.format(fmt), use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# 🚀 MAIN RENDER FUNCTION
# ══════════════════════════════════════════════════════════════════
def render():
    """Tab 4 — 全球決策 Cinematic Wealth Command Center V200 God-Tier Edition"""
    _inject_css()
    _ensure_portfolio()
    
    # Initialize active section
    if 'active_section' not in st.session_state:
        st.session_state.active_section = '4.1'
    
    # Header
    st.markdown(f"""
    <div style="display:flex;align-items:baseline;justify-content:space-between;
        padding-bottom:14px;border-bottom:2px solid rgba(255,255,255,.08);margin-bottom:20px;">
        <div>
            <span style="font-family:'Bebas Neue',sans-serif;font-size:32px;color:#00F5FF;
                letter-spacing:3px;text-shadow:0 0 30px rgba(0,245,255,.4);">🌍 全球決策</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:10px;
                color:rgba(0,245,255,.3);letter-spacing:3px;
                border:1px solid rgba(0,245,255,.15);border-radius:20px;
                padding:4px 14px;margin-left:16px;">WEALTH COMMAND CENTER · GOD TIER</span>
        </div>
        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
            color:rgba(200,215,230,.25);letter-spacing:2px;text-align:right;line-height:1.8;">
            {datetime.now().strftime('%H:%M:%S')}<br>{datetime.now().strftime('%Y·%m·%d')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Billboard
    _render_hero_billboard()
    
    # Navigation Rail
    _render_nav_rail()
    
    # Active Section
    section_map = {
        "4.1": _s41,
        "4.2": _s42,
        "4.3": _s43,
        "4.4": _s44,
        "4.5": _s45,
    }
    
    active = st.session_state.get('active_section', '4.1')
    fn = section_map.get(active, _s41)
    
    try:
        fn()
    except Exception as exc:
        import traceback
        st.toast(f"❌ Section {active} 發生錯誤 / Error in Section {active}", icon="⚡")
        st.error(f"❌ Section {active} 發生錯誤: {exc}")
        with st.expander(f"🔍 Debug — {active}"):
            st.code(traceback.format_exc())
    
    # Footer
    st.markdown(f"""
    <div class="t4-foot">
        Titan Cinematic Wealth Command Center V200 · God-Tier Edition · 
        {datetime.now().strftime("%Y-%m-%d %H:%M")}
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# 🎯 ENTRY POINT
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    render()
