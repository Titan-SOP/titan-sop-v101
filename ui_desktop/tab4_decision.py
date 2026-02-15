# ui_desktop/tab4_decision.py — DIRECTOR'S CUT
# Titan SOP V200 — Tab 4: 全球決策 (CINEMATIC WEALTH COMMAND CENTER)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  🎬 DIRECTOR'S CUT FEATURES:                                      ║
# ║  [DC1] 🔰 Tactical Guide Modal (Onboarding)                      ║
# ║  [DC2] 🍞 Toast Notifications (No More Green Boxes)              ║
# ║  [DC3] ⌨️ Valkyrie AI Typewriter (Streaming Text)                ║
# ║  [DC4] 🎬 Cinematic Visuals (Hero Billboard + Glassmorphism)     ║
# ║  ALL backtest engines preserved 100% verbatim from original      ║
# ╚═══════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import re
import io
import time
from datetime import datetime


# ══════════════════════════════════════════════════════════════════
#  [DC3] VALKYRIE AI TYPEWRITER
# ══════════════════════════════════════════════════════════════════
def _stream_text(text, speed=0.02):
    """Character-by-character text streaming for cinematic effect"""
    for char in text:
        yield char
        time.sleep(speed)


# ══════════════════════════════════════════════════════════════════
#  INTERNAL BACKTEST ENGINES
#  (verified verbatim from original V82 → V100 — zero logic changes)
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
        twd_fx = 31.5
        scenarios = {
            'COVID-19 崩盤': -0.35,
            '2008 金融海嘯': -0.42,
            '中美貿易戰': -0.22,
            '全球通膨衝擊': -0.18,
        }

        results = []
        for asset in portfolio:
            ticker = asset['ticker']
            shares = asset['shares']
            orig = ticker
            is_tw = re.match(r'^[0-9]', ticker) and 4 <= len(ticker) <= 6

            if ticker.upper() in ['CASH', 'USD', 'TWD']:
                row = {'ticker': ticker, 'type': 'Cash', 'shares': shares, 'price': 1.0, 'value_twd': shares}
                for k in scenarios.keys():
                    row[f'損益_{k}'] = 0
                results.append(row)
                continue

            if is_tw:
                ticker = f"{ticker}.TW"
            try:
                data = yf.download(ticker, period="1mo", progress=False)
                if data.empty and is_tw:
                    data = yf.download(f"{orig}.TWO", period="1mo", progress=False)
                if data.empty: continue
                if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
                price = float(data['Close'].iloc[-1])
                value = price * shares * (1 if is_tw else twd_fx)
                row = {'ticker': orig, 'type': 'TW' if is_tw else 'US',
                       'shares': shares, 'price': price, 'value_twd': value}
                for k, shock in scenarios.items():
                    row[f'損益_{k}'] = value * shock
                results.append(row)
            except: continue

        if not results:
            return pd.DataFrame(), {"error": "無法獲取任何資產的市價。"}
        return pd.DataFrame(results), {'total_value': pd.DataFrame(results)['value_twd'].sum()}
    except Exception:
        return pd.DataFrame(), {"error": "壓力測試執行時發生錯誤。"}


# ══════════════════════════════════════════════════════════════════
#  DEFAULT PORTFOLIO
# ══════════════════════════════════════════════════════════════════
_DEFAULT_PORTFOLIO = pd.DataFrame([
    {'資產代號': '2330', '持有數量 (股)': 1000, '買入均價': 550.0,    '資產類別': 'Stock'},
    {'資產代號': 'NVDA', '持有數量 (股)': 10,   '買入均價': 400.0,    '資產類別': 'US_Stock'},
    {'資產代號': 'CASH', '持有數量 (股)': 1,    '買入均價': 500000.0, '資產類別': 'Cash'},
])

def _ensure_portfolio():
    if 'portfolio_df' not in st.session_state:
        st.session_state.portfolio_df = _DEFAULT_PORTFOLIO.copy()


# ══════════════════════════════════════════════════════════════════
#  [DC4] DIRECTOR'S CUT MASTER CSS
# ══════════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
/* ═══════════════════════════════════════════════════════ */
/* TITAN OS MASTER CSS — DIRECTOR'S CUT */
/* ═══════════════════════════════════════════════════════ */
:root {
  --c-gold: #FFD700;
  --c-cyan: #00F5FF;
  --c-red: #FF3131;
  --c-green: #00FF7F;
  --c-orange: #FF9A3C;
  --bg-card: #0D1117;
  --f-d: 'Bebas Neue', sans-serif;
  --f-b: 'Rajdhani', sans-serif;
  --f-m: 'JetBrains Mono', monospace;
  --f-i: 'Inter', sans-serif;
}

/* 1. HERO BILLBOARD (CINEMATIC) */
.hero-container {
  padding: 50px 40px 44px;
  background: linear-gradient(180deg, rgba(20,20,20,0) 0%, rgba(10,10,14,0.6) 40%, rgba(0,0,0,0.85) 100%);
  border-bottom: 1px solid rgba(255,215,0,0.2);
  text-align: center;
  margin-bottom: 30px;
  position: relative;
  overflow: hidden;
}
.hero-container::before {
  content: '';
  position: absolute;
  bottom: 60px;
  left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent 0%, rgba(255,215,0,0.15) 20%, rgba(255,215,0,0.35) 50%, rgba(255,215,0,0.15) 80%, transparent 100%);
  pointer-events: none;
}
.hero-container::after {
  content: '';
  position: absolute;
  top: 0; left: 50%;
  transform: translateX(-50%);
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(255,215,0,0.04) 0%, transparent 70%);
  pointer-events: none;
}
.hero-surtitle {
  font-family: var(--f-m);
  font-size: 10px;
  color: rgba(255,215,0,0.4);
  letter-spacing: 6px;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.hero-val {
  font-size: 84px !important;
  font-weight: 900;
  font-family: var(--f-i);
  letter-spacing: -3px;
  line-height: 1;
  color: #FFF;
  text-shadow: 0 0 60px rgba(255,215,0,0.15), 0 0 120px rgba(255,215,0,0.05);
  margin-bottom: 8px;
}
.hero-currency {
  font-family: var(--f-m);
  font-size: 14px;
  color: rgba(255,255,255,0.25);
  letter-spacing: 4px;
  margin-bottom: 18px;
}
.hero-pnl {
  font-size: 32px;
  font-weight: 800;
  font-family: var(--f-i);
  letter-spacing: -1px;
  line-height: 1.2;
}
.hero-pnl-label {
  font-family: var(--f-m);
  font-size: 10px;
  letter-spacing: 3px;
  text-transform: uppercase;
  opacity: 0.4;
  margin-top: 4px;
}
.hero-time {
  font-family: var(--f-m);
  font-size: 9px;
  color: rgba(255,255,255,0.12);
  letter-spacing: 3px;
  margin-top: 20px;
}

/* 2. POSTER NAV RAIL (NETFLIX STYLE) */
.nav-rail {
  display: flex;
  gap: 12px;
  margin-bottom: 32px;
  padding: 0 4px;
  overflow-x: auto;
}
.nav-poster {
  flex: 1;
  min-width: 130px;
  min-height: 160px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 14px;
  padding: 22px 16px 18px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}
.nav-poster::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--poster-accent, rgba(255,255,255,0.05));
  border-radius: 14px 14px 0 0;
  opacity: 0.5;
  transition: opacity 0.3s;
}
.nav-poster.active {
  border-color: var(--c-cyan);
  background: rgba(0,245,255,0.04);
  box-shadow: 0 0 30px rgba(0,245,255,0.08), inset 0 0 30px rgba(0,245,255,0.02);
}
.nav-poster.active::before { opacity: 1; background: var(--c-cyan); }
.nav-poster:hover {
  border-color: var(--c-gold);
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.nav-poster-icon {
  font-size: 32px;
  margin-bottom: 10px;
  filter: drop-shadow(0 0 8px rgba(255,255,255,0.1));
}
.nav-poster-title {
  font-family: var(--f-d);
  font-size: 16px;
  color: #FFF;
  letter-spacing: 2px;
  line-height: 1.3;
  margin-bottom: 4px;
}
.nav-poster-sub {
  font-family: var(--f-m);
  font-size: 8px;
  color: rgba(160,176,192,0.45);
  letter-spacing: 1.5px;
  text-transform: uppercase;
}

/* 3. STREAMING TEXT & DATA (GLASSMORPHISM) */
.stMarkdown p {
  font-size: 18px !important;
  line-height: 1.6;
}
[data-testid="stDataFrame"] {
  font-size: 16px !important;
  background: rgba(13, 17, 23, 0.6) !important;
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 10px;
}

/* KELLY TACTICAL CHIPS (4.2) */
.kelly-chip {
  background: #161b22;
  border-left: 4px solid #FFD700;
  padding: 20px 24px;
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 0 12px 12px 0;
  transition: all 0.25s ease;
}
.kelly-chip:hover {
  background: #1c2230;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.kelly-chip-left { display: flex; flex-direction: column; gap: 4px; }
.kelly-chip-ticker {
  font-family: var(--f-d);
  font-size: 24px;
  color: #FFF;
  letter-spacing: 2px;
}
.kelly-chip-meta {
  font-family: var(--f-m);
  font-size: 10px;
  color: rgba(160,176,192,0.5);
  letter-spacing: 1px;
}
.kelly-chip-advice-tag {
  font-family: var(--f-m);
  font-size: 9px;
  letter-spacing: 1.5px;
  padding: 3px 10px;
  border-radius: 20px;
  margin-top: 6px;
  display: inline-block;
}
.kelly-chip-right { text-align: right; display: flex; flex-direction: column; align-items: flex-end; }
.kelly-chip-kelly {
  font-family: var(--f-i);
  font-size: 38px;
  font-weight: 900;
  color: #FFD700;
  letter-spacing: -1px;
  line-height: 1;
  text-shadow: 0 0 20px rgba(255,215,0,0.2);
}
.kelly-chip-kelly-label {
  font-family: var(--f-m);
  font-size: 9px;
  color: rgba(255,215,0,0.4);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-top: 4px;
}
.kelly-chip.fire  { border-left-color: #FF3131; }
.kelly-chip.fire .kelly-chip-kelly { color: #FF6B6B; text-shadow: 0 0 20px rgba(255,49,49,0.3); }
.kelly-chip.ice   { border-left-color: #556677; }
.kelly-chip.ice .kelly-chip-kelly { color: #778899; text-shadow: none; }

/* RED ALERT CARDS (4.5 Stress) */
.stress-alert-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin: 20px 0;
}
.stress-alert-card {
  background: rgba(255, 0, 0, 0.07);
  border: 1px solid rgba(255, 49, 49, 0.35);
  border-radius: 14px;
  padding: 22px 16px 18px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.stress-alert-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, #FF3131, transparent);
}
.stress-alert-card::after {
  content: '⚠';
  position: absolute;
  top: 8px; right: 10px;
  font-size: 10px;
  opacity: 0.2;
}
.stress-alert-label {
  font-family: var(--f-m);
  font-size: 9px;
  color: rgba(255,100,100,0.6);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.stress-alert-val {
  font-family: var(--f-i);
  font-size: 32px;
  font-weight: 800;
  color: #FF6B6B;
  line-height: 1;
  letter-spacing: -1px;
}
.stress-alert-pct {
  font-family: var(--f-b);
  font-size: 14px;
  color: #FF3131;
  font-weight: 700;
  margin-top: 6px;
}

/* SECTION HEADERS (cinematic) */
.t4-sec-head {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(255,255,255,.052);
  margin-bottom: 20px;
}
.t4-sec-num {
  font-family: var(--f-d);
  font-size: 56px;
  color: rgba(0,245,255,.06);
  letter-spacing: 2px;
  line-height: 1;
}
.t4-sec-title {
  font-family: var(--f-d);
  font-size: 22px;
  color: var(--sa,#00F5FF);
  letter-spacing: 2px;
}
.t4-sec-sub {
  font-family: var(--f-m);
  font-size: 9px;
  color: rgba(0,245,255,.28);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-top: 2px;
}

/* CHART PANELS (GLASSMORPHISM) */
.t4-chart-panel {
  background: rgba(0,0,0,.4);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,.055);
  border-radius: 16px;
  padding: 18px 12px 10px;
  margin: 14px 0;
  overflow: hidden;
}
.t4-chart-lbl {
  font-family: var(--f-m);
  font-size: 9px;
  color: rgba(0,245,255,.28);
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 10px;
  padding-left: 6px;
}

/* ACTION BUTTONS (styled) */
.t4-action div.stButton>button {
  background: linear-gradient(45deg, #FFD700, #DAA520) !important;
  border: none !important;
  color: #000 !important;
  font-family: var(--f-m) !important;
  font-size: 11px !important;
  letter-spacing: 2px !important;
  min-height: 48px !important;
  border-radius: 12px !important;
  text-transform: uppercase !important;
  transition: all 0.3s ease !important;
  box-shadow: 0 0 20px rgba(255,215,0,0.4) !important;
}
.t4-action div.stButton>button:hover {
  box-shadow: 0 0 30px rgba(255,215,0,0.6) !important;
  transform: translateY(-2px);
}
.t4-action-r div.stButton>button {
  border-color: rgba(255,49,49,.3) !important;
  color: rgba(255,100,100,.85) !important;
  background: linear-gradient(135deg, #FF3131, #CC2828) !important;
}
.t4-action-r div.stButton>button:hover {
  background: rgba(255,49,49,.1) !important;
  box-shadow: 0 0 20px rgba(255,49,49,.15) !important;
}
.t4-action-g div.stButton>button {
  border-color: rgba(0,255,127,.22) !important;
  color: rgba(0,255,127,.85) !important;
}
.t4-action-g div.stButton>button:hover {
  background: rgba(0,255,127,.07) !important;
}

/* FOOTER */
.t4-foot {
  font-family: var(--f-m);
  font-size: 9px;
  color: rgba(70,90,110,.28);
  letter-spacing: 2px;
  text-align: right;
  margin-top: 28px;
  text-transform: uppercase;
}
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  [DC1] TACTICAL GUIDE MODAL
# ══════════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導 / Tactical Guide")
def show_tactical_guide():
    st.markdown("""
    ### 全球決策系統操作指南
    
    **核心功能 / Core Functions:**
    
    • **📊 戰略資產配置** — 統一管理台股、美股、現金部位，實時計算市值與損益  
    • **🚀 回測決策 + ⚖️ 再平衡** — MA20策略回測與凱利公式資金管理，精準調倉建議  
    • **🌪️ 黑天鵝壓力測試** — 模擬4種系統性風險，評估投資組合韌性與抗震能力  
    
    **操作流程 / Workflow:**
    1. 在 4.1 配置您的全球資產組合
    2. 使用 4.2/4.3 進行回測與策略實驗
    3. 透過 4.4 獲得再平衡調倉建議
    4. 在 4.5 執行壓力測試評估風險
    
    ---
    *此系統整合即時市價、歷史回測、風險模擬，為財富指揮中心的決策核心。*
    """)
    
    if st.button("✅ Roger that (收到)", type="primary", use_container_width=True):
        st.session_state.t4_guide_shown = True
        st.rerun()


# ══════════════════════════════════════════════════════════════════
#  HERO BILLBOARD (The first thing the user sees)
# ══════════════════════════════════════════════════════════════════
def _render_hero_billboard():
    """Massive cinematic banner showing Total Net Worth + PnL."""
    pf = st.session_state.portfolio_df.copy()
    asset_tickers = pf[pf['資產類別'] != 'Cash']['資產代號'].tolist()

    # Fetch latest prices
    lp_map = {}
    if asset_tickers:
        try:
            tickers_query = [
                f"{t}.TW" if re.match(r'^[0-9]', t) and 4 <= len(t) <= 6 else t
                for t in asset_tickers
            ]
            pd_ = yf.download(tickers_query, period="1d", progress=False)['Close']
            if len(tickers_query) == 1:
                lp_map = {asset_tickers[0]: float(pd_.iloc[-1])}
            else:
                raw = pd_.iloc[-1].to_dict() if isinstance(pd_, pd.DataFrame) else {}
                for orig_t, query_t in zip(asset_tickers, tickers_query):
                    if query_t in raw:
                        lp_map[orig_t] = raw[query_t]
                    elif orig_t in raw:
                        lp_map[orig_t] = raw[orig_t]
        except Exception:
            pass

    pf['現價']       = pf['資產代號'].map(lp_map).fillna(1.0)
    pf['市值']       = pf['持有數量 (股)'] * pf['現價']
    pf['未實現損益'] = (pf['現價'] - pf['買入均價']) * pf['持有數量 (股)']

    total_v   = pf['市值'].sum()
    total_pnl = pf['未實現損益'].sum()
    pnl_color = "#00FF7F" if total_pnl >= 0 else "#FF3131"
    pnl_arrow = "▲" if total_pnl >= 0 else "▼"
    pnl_pct   = (total_pnl / total_v * 100) if total_v > 0 else 0

    st.markdown(f"""
<div class="hero-container">
  <div class="hero-surtitle">TOTAL NET WORTH</div>
  <div class="hero-val">{total_v:,.0f}</div>
  <div class="hero-currency">TWD</div>
  <div class="hero-pnl" style="color:{pnl_color};">{pnl_arrow} {abs(total_pnl):,.0f}</div>
  <div class="hero-pnl-label" style="color:{pnl_color};">Unrealized P&L &nbsp;({pnl_pct:+.2f}%)</div>
  <div class="hero-time">TITAN GLOBAL DECISION V200 — DIRECTOR'S CUT &nbsp;&middot;&nbsp; {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}</div>
</div>""", unsafe_allow_html=True)

    # Store computed data for Section 4.1 reuse
    st.session_state._hero_pf    = pf
    st.session_state._hero_total = total_v
    st.session_state._hero_pnl   = total_pnl


# ══════════════════════════════════════════════════════════════════
#  NAVIGATION RAIL — 5 POSTER CARDS
# ══════════════════════════════════════════════════════════════════
def _render_nav_rail():
    """Horizontal rail of 5 Movie-Poster-shaped navigation cards."""
    if 'active_section' not in st.session_state:
        st.session_state.active_section = "4.1"

    cards = [
        ("4.1", "📊", "資產配置", "Allocation"),
        ("4.2", "🚀", "回測決策", "Backtest"),
        ("4.3", "🧪", "均線實驗", "MA Lab"),
        ("4.4", "⚖️",  "再平衡",   "Rebalance"),
        ("4.5", "🌪️", "壓力測試", "Stress Test"),
    ]
    cols = st.columns(5)
    for i, (sec_id, icon, title, sub) in enumerate(cards):
        with cols[i]:
            is_active = st.session_state.active_section == sec_id
            active_cls = "active" if is_active else ""
            st.markdown(f"""
<div class="nav-poster {active_cls}" style="--poster-accent:{'var(--c-cyan)' if is_active else 'rgba(255,255,255,0.05)'};">
  <div class="nav-poster-icon">{icon}</div>
  <div class="nav-poster-title">{sec_id} {title}</div>
  <div class="nav-poster-sub">{sub}</div>
</div>""", unsafe_allow_html=True)
            if st.button(f"Open {sec_id}", key=f"nav_{sec_id}", use_container_width=True):
                st.session_state.active_section = sec_id
                st.rerun()


# ══════════════════════════════════════════════════════════════════
#  SECTION 4.1 — 戰略資產配置
# ══════════════════════════════════════════════════════════════════
def _s41():
    st.markdown('<div class="t4-sec-head" style="--sa:#00F5FF"><div class="t4-sec-num">4.1</div><div><div class="t4-sec-title">戰略資產配置</div><div class="t4-sec-sub">Strategic Asset Allocation</div></div></div>', unsafe_allow_html=True)
    
    # [DC2] Replace st.info with toast
    st.toast("💡 台股 1 張 = 1000 股 | 美股以 1 股為單位 | 現金輸入總額 / TW shares in 1000s", icon="🎯")

    ptd = st.session_state.get('_hero_pf', st.session_state.portfolio_df.copy())

    # Recompute if hero data not available
    if '市值' not in ptd.columns:
        asset_tickers = ptd[ptd['資產類別'] != 'Cash']['資產代號'].tolist()
        lp_map = {}
        if asset_tickers:
            try:
                pd_ = yf.download(asset_tickers, period="1d", progress=False)['Close']
                if len(asset_tickers) == 1:
                    lp_map = {asset_tickers[0]: float(pd_.iloc[-1])}
                else:
                    lp_map = {k: float(v) for k, v in pd_.iloc[-1].to_dict().items()}
            except Exception:
                st.toast("⚠️ 無法獲取即時市價 / Unable to fetch real-time prices", icon="⚡")
        ptd['現價']       = ptd['資產代號'].map(lp_map).fillna(1.0)
        ptd['市值']       = ptd['持有數量 (股)'] * ptd['現價']
        ptd['未實現損益'] = (ptd['現價'] - ptd['買入均價']) * ptd['持有數量 (股)']

    edited_df = st.data_editor(
        ptd,
        column_config={
            "資產代號":      st.column_config.TextColumn("資產代號", help="台股/美股代號或CASH"),
            "持有數量 (股)": st.column_config.NumberColumn("持有數量 (股)", format="%d"),
            "買入均價":      st.column_config.NumberColumn("買入均價",       format="%.2f"),
            "資產類別":      st.column_config.SelectboxColumn("資產類別",
                                 options=['Stock','ETF','US_Stock','US_Bond','Cash']),
            "現價":          st.column_config.NumberColumn("現價",           format="%.2f",  disabled=True),
            "市值":          st.column_config.NumberColumn("市值",           format="%.0f",  disabled=True),
            "未實現損益":    st.column_config.NumberColumn("未實現損益",     format="%+,.0f",disabled=True),
        },
        num_rows="dynamic",
        key="portfolio_editor_v200_t4",
        use_container_width=True,
    )
    # [CRITICAL] Save only the 4 base columns (identical to original)
    st.session_state.portfolio_df = edited_df[['資產代號','持有數量 (股)','買入均價','資產類別']]

    # Portfolio summary + donut
    total_v   = ptd['市值'].sum()
    total_pnl = ptd['未實現損益'].sum()
    if total_v > 0:
        st.divider()
        pie_col, kpi_col = st.columns([1, 1])
        with pie_col:
            pal = ['#FF3131','#FFD700','#00F5FF','#00FF7F','#FF9A3C','#B77DFF','#FF6BFF','#4dc8ff']
            fig = go.Figure(go.Pie(
                labels=ptd['資產代號'].tolist(), values=ptd['市值'].tolist(), hole=0.55,
                marker=dict(colors=pal[:len(ptd)], line=dict(color='rgba(0,0,0,0.5)', width=2)),
                textfont=dict(color='#DDE', size=12, family='Rajdhani'),
            ))
            fig.update_layout(
                title=dict(text="ASSET ALLOCATION", font=dict(color='rgba(0,245,255,.35)', size=11, family='JetBrains Mono')),
                template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
                height=300, margin=dict(t=34,b=0,l=0,r=0),
                legend=dict(font=dict(color='#B0C0D0', size=11, family='Rajdhani')),
            )
            st.plotly_chart(fig, use_container_width=True)
        with kpi_col:
            pnl_c = "#00FF7F" if total_pnl >= 0 else "#FF3131"
            arr   = "▲" if total_pnl >= 0 else "▼"
            st.markdown(f"""
<div style="padding:20px 0 8px;">
  <div style="font-family:var(--f-m);font-size:9px;color:rgba(0,245,255,.35);letter-spacing:4px;text-transform:uppercase;margin-bottom:14px;">Portfolio Summary</div>
  <div style="font-family:var(--f-m);font-size:9px;color:rgba(255,255,255,.2);letter-spacing:2px;margin-bottom:4px;">TOTAL VALUE</div>
  <div style="font-family:var(--f-i);font-size:52px;font-weight:800;color:#FFF;line-height:1;margin-bottom:18px;letter-spacing:-2px;">{total_v:,.0f}</div>
  <div style="font-family:var(--f-m);font-size:9px;color:rgba(255,255,255,.2);letter-spacing:2px;margin-bottom:4px;">UNREALIZED P&L</div>
  <div style="font-family:var(--f-i);font-size:40px;font-weight:800;color:{pnl_c};line-height:1;margin-bottom:6px;letter-spacing:-1px;">{arr} {abs(total_pnl):,.0f}</div>
  <div style="font-family:var(--f-b);font-size:15px;color:{pnl_c};font-weight:700;">{(total_pnl/total_v)*100:+.2f}% 報酬率</div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  SECTION 4.2 — 績效回測與凱利決策 (TACTICAL CHIPS)
# ══════════════════════════════════════════════════════════════════
def _s42():
    st.markdown('<div class="t4-sec-head" style="--sa:#FFD700"><div class="t4-sec-num">4.2</div><div><div class="t4-sec-title" style="color:#FFD700;">績效回測 · 凱利決策</div><div class="t4-sec-sub">MA20 Strategy · Half-Kelly Position Sizing</div></div></div>', unsafe_allow_html=True)

    # [DC3] Streaming analysis text
    analysis_text = """
    **凱利決策系統分析:**
    
    本系統採用MA20突破策略進行全球資產回測，並使用半凱利公式 (Half-Kelly) 計算最佳資金配置比例。
    凱利值 >10% 表示強勢進攻機會，2.5%-10% 為穩健配置，<2.5% 建議觀望或試單。
    """
    st.write_stream(_stream_text(analysis_text, speed=0.01))

    st.markdown('<div class="t4-action">', unsafe_allow_html=True)
    run_bt = st.button("🚀 啟動全球回測", key="btn_backtest_v200")
    st.markdown('</div>', unsafe_allow_html=True)

    if run_bt:
        pf = st.session_state.get('portfolio_df', pd.DataFrame())
        if pf.empty:
            st.toast("⚠️ 請先在 4.1 配置資產 / Please configure assets in 4.1", icon="⚡")
        else:
            st.toast("🚀 系統運算中 / Processing backtest...", icon="⏳")
            with st.spinner("正在對全球資產執行回測…"):
                bt_list = []
                for _, row in pf.iterrows():
                    r = _run_fast_backtest(str(row['資產代號']).strip(), initial_capital=1_000_000)
                    if r:
                        r['Ticker'] = str(row['資產代號']).strip()
                        bt_list.append(r)
                st.session_state.backtest_results = bt_list
            st.toast("✅ 回測完成 / Backtest Complete", icon="🎯")

    if 'backtest_results' not in st.session_state: return
    results = st.session_state.backtest_results
    if not results:
        st.toast("❌ 所有資產回測失敗 / All backtests failed", icon="⚡")
        return

    # ── TACTICAL CHIPS (not a table!) ──
    summary_data = []
    for res in results:
        ck      = res.get('kelly', 0) * 0.5   # half-Kelly (original)
        cagr    = res.get('cagr', 0)
        sharpe  = res.get('sharpe_ratio', 0)
        mdd     = res.get('max_drawdown', 0)
        advice  = "🧊 觀望或試單"; css = "ice"
        if ck > 0.1:      advice = "🔥🔥 重注進攻"; css = "fire"
        elif ck >= 0.025: advice = "✅ 穩健配置";   css = "ok"
        clr = "#00FF7F" if cagr > 0 else "#FF6B6B"
        kclr = "#FF3131" if ck > 0.1 else ("#00F5FF" if ck >= 0.025 else "#778899")

        # Advice tag styling
        if css == "fire":
            tag_bg = "rgba(255,49,49,0.12)"; tag_border = "rgba(255,49,49,0.3)"; tag_color = "#FF6B6B"
        elif css == "ok":
            tag_bg = "rgba(0,245,255,0.08)"; tag_border = "rgba(0,245,255,0.2)"; tag_color = "#00F5FF"
        else:
            tag_bg = "rgba(100,115,135,0.08)"; tag_border = "rgba(100,115,135,0.2)"; tag_color = "#778899"

        st.markdown(f"""
<div class="kelly-chip {css}">
  <div class="kelly-chip-left">
    <div class="kelly-chip-ticker">{res['Ticker']}</div>
    <div class="kelly-chip-meta">CAGR <span style="color:{clr};font-weight:700;">{cagr:.1%}</span> &nbsp;&middot;&nbsp; Sharpe {sharpe:.2f} &nbsp;&middot;&nbsp; MDD {mdd:.1%}</div>
    <div class="kelly-chip-advice-tag" style="background:{tag_bg};border:1px solid {tag_border};color:{tag_color};">{advice}</div>
  </div>
  <div class="kelly-chip-right">
    <div class="kelly-chip-kelly">{ck:.1%}</div>
    <div class="kelly-chip-kelly-label">Half-Kelly</div>
  </div>
</div>""", unsafe_allow_html=True)
        summary_data.append({'代號':res['Ticker'],'最新價':res.get('latest_price',0),
            '年化報酬 (CAGR)':cagr,'投資性價比 (Sharpe)':sharpe,
            '最大回撤':mdd,'凱利建議 %':ck,'建議動作':advice})

    if summary_data:
        st.divider()
        st.dataframe(
            pd.DataFrame(summary_data),
            column_config={
                '代號': st.column_config.TextColumn('代號', width='small'),
                '最新價': st.column_config.NumberColumn('最新價', format='%.2f'),
                '年化報酬 (CAGR)': st.column_config.NumberColumn('年化報酬', format='%.2%'),
                '投資性價比 (Sharpe)': st.column_config.NumberColumn('夏普', format='%.2f'),
                '最大回撤': st.column_config.NumberColumn('最大回撤', format='%.2%'),
                '凱利建議 %': st.column_config.NumberColumn('Half-Kelly %', format='%.2%'),
            },
            use_container_width=True,
            hide_index=True,
        )

    # Equity curves in glassmorphism panel
    st.markdown('<div class="t4-chart-panel"><div class="t4-chart-lbl">▸ equity curves — portfolio performance</div>', unsafe_allow_html=True)
    fig_eq = go.Figure()
    for res in results:
        fig_eq.add_trace(go.Scatter(
            x=res['equity_curve'].index,
            y=res['equity_curve'].values,
            mode='lines',
            name=res['Ticker'],
            line=dict(width=2),
        ))
    fig_eq.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(t=20, b=40, l=60, r=20),
        legend=dict(font=dict(color='#B0C0D0', size=11, family='Rajdhani')),
        xaxis=dict(tickfont=dict(color='#A0B0C0', size=10)),
        yaxis=dict(tickfont=dict(color='#A0B0C0', size=10), title='Equity (TWD)'),
    )
    st.plotly_chart(fig_eq, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  SECTION 4.3 — 均線策略實驗室 (15 STRATEGIES)
# ══════════════════════════════════════════════════════════════════
def _s43():
    st.markdown('<div class="t4-sec-head" style="--sa:#FF9A3C"><div class="t4-sec-num">4.3</div><div><div class="t4-sec-title" style="color:#FF9A3C;">均線策略實驗室</div><div class="t4-sec-sub">15 MA Strategies · 10-Year Future Value Projection</div></div></div>', unsafe_allow_html=True)
    
    # [DC3] Streaming intro
    intro_text = """
    **均線實驗室系統:**
    
    測試15種均線策略組合，包含突破、交叉、非對稱進出等戰法。
    系統將推算10年後財富變化，協助您找出最適合標的特性的策略。
    """
    st.write_stream(_stream_text(intro_text, speed=0.01))

    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    if pf.empty:
        st.toast("⚠️ 請先在 4.1 配置資產 / Please configure assets in 4.1", icon="⚡")
        return

    sel_t = st.selectbox("選擇標的 (Select Asset)", pf['資產代號'].tolist(), key="ma_lab_ticker")
    
    st.markdown('<div class="t4-action">', unsafe_allow_html=True)
    run_ma = st.button("🧪 執行實驗", key="btn_ma_lab_v200")
    st.markdown('</div>', unsafe_allow_html=True)

    if run_ma:
        st.toast("🚀 運算中 / Running MA strategies...", icon="⏳")
        strategies = [
            "價格 > 20MA", "價格 > 43MA", "價格 > 60MA", "價格 > 87MA", "價格 > 284MA",
            "20/60 黃金/死亡交叉", "20/87 黃金/死亡交叉", "20/284 黃金/死亡交叉",
            "43/87 黃金/死亡交叉", "43/284 黃金/死亡交叉", "60/87 黃金/死亡交叉",
            "60/284 黃金/死亡交叉", "🔥 核心戰法: 87MA ↗ 284MA",
            "非對稱: P>20進 / P<60出", "雙確認: P>20 & P>60 進 / P<60 出"
        ]
        
        with st.spinner(f"正在測試 {sel_t} 的 15 種策略…"):
            results = []
            for strat in strategies:
                r = _run_ma_strategy_backtest(sel_t, strat, initial_capital=1_000_000)
                if r:
                    results.append(r)
            st.session_state.ma_lab_results = results
        
        if results:
            st.toast("✅ 實驗完成 / Lab Complete", icon="🎯")
        else:
            st.toast("❌ 無法取得回測數據 / Failed to fetch backtest data", icon="⚡")
            return

    if 'ma_lab_results' not in st.session_state:
        return

    results = st.session_state.ma_lab_results
    if not results:
        return

    # Results table
    df_res = pd.DataFrame(results)
    df_res = df_res.sort_values('future_10y_capital', ascending=False).reset_index(drop=True)
    
    st.markdown('<div class="t4-chart-panel"><div class="t4-chart-lbl">▸ strategy leaderboard — 10 year projection</div>', unsafe_allow_html=True)
    st.dataframe(
        df_res[['strategy_name', 'cagr', 'final_equity', 'max_drawdown', 'future_10y_capital']],
        column_config={
            'strategy_name': st.column_config.TextColumn('策略', width='large'),
            'cagr': st.column_config.NumberColumn('年化報酬', format='%.2%'),
            'final_equity': st.column_config.NumberColumn('最終市值', format='%,.0f'),
            'max_drawdown': st.column_config.NumberColumn('最大回撤', format='%.2%'),
            'future_10y_capital': st.column_config.NumberColumn('10年後資本', format='%,.0f'),
        },
        use_container_width=True,
        hide_index=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Top 3 bar chart
    st.divider()
    top3 = df_res.head(3)
    fig_bar = go.Figure(go.Bar(
        x=top3['strategy_name'],
        y=top3['future_10y_capital'],
        text=[f"${v:,.0f}" for v in top3['future_10y_capital']],
        textposition='outside',
        marker=dict(
            color=['#FFD700', '#00F5FF', '#FF9A3C'],
            line=dict(color='rgba(255,255,255,0.1)', width=1.5)
        ),
    ))
    fig_bar.update_layout(
        title=dict(text="TOP 3 STRATEGIES — 10Y FUTURE VALUE", 
                   font=dict(color='rgba(255,154,60,.5)', size=12, family='JetBrains Mono')),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(t=50, b=80, l=60, r=20),
        xaxis=dict(tickfont=dict(color='#B0C0D0', size=10, family='Rajdhani')),
        yaxis=dict(tickfont=dict(color='#A0B0C0', size=10), title='10Y Capital (TWD)'),
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
#  SECTION 4.4 — 智能再平衡 (REBALANCE)
# ══════════════════════════════════════════════════════════════════
def _s44():
    st.markdown('<div class="t4-sec-head" style="--sa:#00FF7F"><div class="t4-sec-num">4.4</div><div><div class="t4-sec-title" style="color:#00FF7F;">智能再平衡</div><div class="t4-sec-sub">Portfolio Rebalancing · Target Weight Optimization</div></div></div>', unsafe_allow_html=True)
    
    # [DC3] Streaming explanation
    rebal_text = """
    **再平衡系統說明:**
    
    輸入各資產的目標權重比例，系統將基於當前市值計算需要買入或賣出的股數。
    建議定期（如每季）執行再平衡，以維持資產配置符合投資策略。
    """
    st.write_stream(_stream_text(rebal_text, speed=0.01))

    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    if pf.empty:
        st.toast("⚠️ 請先在 4.1 配置資產 / Please configure assets in 4.1", icon="⚡")
        return

    # Get current prices
    asset_tickers = pf[pf['資產類別'] != 'Cash']['資產代號'].tolist()
    lp_map = {}
    if asset_tickers:
        try:
            tickers_query = [f"{t}.TW" if re.match(r'^[0-9]', t) else t for t in asset_tickers]
            pd_ = yf.download(tickers_query, period="1d", progress=False)['Close']
            if len(tickers_query) == 1:
                lp_map = {asset_tickers[0]: float(pd_.iloc[-1])}
            else:
                raw = pd_.iloc[-1].to_dict() if isinstance(pd_, pd.DataFrame) else {}
                for orig, query in zip(asset_tickers, tickers_query):
                    lp_map[orig] = raw.get(query, raw.get(orig, 1.0))
        except Exception:
            pass

    pf = pf.copy()
    pf['現價'] = pf['資產代號'].map(lp_map).fillna(1.0)
    pf['目前市值'] = pf['持有數量 (股)'] * pf['現價']
    total_v = pf['目前市值'].sum()
    pf['目前權重 %'] = (pf['目前市值'] / total_v * 100) if total_v > 0 else 0

    st.markdown("#### 設定目標權重 (Target Weights)")
    weights = {}
    cols = st.columns(len(pf))
    for i, row in pf.iterrows():
        with cols[i]:
            weights[row['資產代號']] = st.number_input(
                f"{row['資產代號']} (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(row['目前權重 %']),
                step=0.1,
                key=f"weight_{row['資產代號']}_v200"
            )

    pf['目標權重 %'] = pf['資產代號'].map(weights)
    total_w = pf['目標權重 %'].sum()
    
    if abs(total_w - 100.0) > 0.1:
        st.toast(f"⚠️ 目標權重總和 {total_w:.1f}%，建議調整至 100% / Weight sum should be 100%", icon="⚡")

    st.markdown('<div class="t4-action-g">', unsafe_allow_html=True)
    calc_rebal = st.button("⚖️ 計算調倉", key="btn_rebal_v200")
    st.markdown('</div>', unsafe_allow_html=True)

    if calc_rebal:
        st.toast("🚀 計算中 / Calculating rebalance...", icon="⏳")
        try:
            pf['目標市值'] = pf['目標權重 %'] / 100 * total_v
            pf['目標股數'] = (pf['目標市值'] / pf['現價']).round(0).astype(int)
            pf['調倉股數'] = pf['目標股數'] - pf['持有數量 (股)']

            st.toast("✅ 調倉計算完成 / Rebalance calculated", icon="🎯")
            
            st.markdown("#### 📋 調倉建議 (Rebalancing Actions)")
            st.dataframe(
                pf[['資產代號', '現價', '持有數量 (股)', '目前市值', '目前權重 %', 
                    '目標權重 %', '目標市值', '調倉股數']],
                column_config={
                    '資產代號': st.column_config.TextColumn('資產', width='small'),
                    '現價': st.column_config.NumberColumn('現價', format='%.2f'),
                    '持有數量 (股)': st.column_config.NumberColumn('持有股數', format='%,d'),
                    '目前市值': st.column_config.NumberColumn('目前市值', format='%,.0f'),
                    '目前權重 %': st.column_config.NumberColumn('目前權重 %', format='%.1f%%'),
                    '目標權重 %': st.column_config.NumberColumn('目標權重 %', format='%.1f%%'),
                    '目標市值': st.column_config.NumberColumn('目標市值', format='%,.0f'),
                    '調倉股數': st.column_config.NumberColumn('調倉股數', format='%+,d'),
                },
                use_container_width=True,
                hide_index=True,
            )

            # Before/After Pie side-by-side
            st.divider()
            b_col, a_col = st.columns(2)
            pal = ['#FF3131','#FFD700','#00F5FF','#00FF7F','#FF9A3C','#B77DFF']

            def _mini_pie(labels, values, title, col):
                with col:
                    fig = go.Figure(go.Pie(
                        labels=labels, values=values, hole=0.48,
                        marker=dict(colors=pal[:len(labels)],
                                    line=dict(color='rgba(0,0,0,.3)', width=1.2)),
                        textfont=dict(color='#DDE', size=11, family='Rajdhani'),
                    ))
                    fig.update_layout(
                        title=dict(text=title, font=dict(color='rgba(200,215,230,.4)',
                                   size=11, family='JetBrains Mono')),
                        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
                        height=260, margin=dict(t=30,b=0,l=0,r=0),
                        legend=dict(font=dict(color='#A0B0C0', size=10, family='Rajdhani')),
                    )
                    st.plotly_chart(fig, use_container_width=True)

            _mini_pie(pf['資產代號'].tolist(), pf['目前市值'].tolist(), "⬅ BEFORE", b_col)
            _mini_pie(pf['資產代號'].tolist(), pf['目標市值'].tolist(), "AFTER ➡", a_col)

        except Exception as e:
            st.toast(f"❌ 計算失敗 / Calculation failed: {e}", icon="⚡")


# ══════════════════════════════════════════════════════════════════
#  SECTION 4.5 — 全球黑天鵝壓力測試 (RED ALERT CARDS)
# ══════════════════════════════════════════════════════════════════
def _s45():
    st.markdown('<div class="t4-sec-head" style="--sa:#FF3131"><div class="t4-sec-num">4.5</div><div><div class="t4-sec-title" style="color:#FF3131;">黑天鵝壓力測試</div><div class="t4-sec-sub">Global Systemic Shock Simulation · 4 Scenarios</div></div></div>', unsafe_allow_html=True)
    
    # [DC3] Streaming intro
    stress_text = """
    **壓力測試系統:**
    
    模擬 COVID-19 崩盤 (-35%)、2008 金融海嘯 (-42%)、中美貿易戰 (-22%)、全球通膨衝擊 (-18%) 四大情境。
    評估您的投資組合在極端市場環境下的韌性與最大可能損失。
    """
    st.write_stream(_stream_text(stress_text, speed=0.01))

    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    if pf.empty:
        st.toast("⚠️ 請先在 4.1 配置資產 / Please configure assets in 4.1", icon="⚡")
        return

    st.markdown('<div class="t4-action t4-action-r">', unsafe_allow_html=True)
    run_stress = st.button("💥 啟動壓力測試", key="btn_stress_v200")
    st.markdown('</div>', unsafe_allow_html=True)

    if run_stress:
        portfolio_text = "\n".join(
            f"{row['資產代號']};{row['持有數量 (股)']}" for _, row in pf.iterrows())
        
        st.toast("🚀 執行壓力測試 / Running stress test...", icon="⏳")
        with st.spinner("執行全球壓力測試…"):
            results_df, summary = _run_stress_test(portfolio_text)
        
        if "error" in summary:
            st.toast(f"❌ {summary['error']}", icon="⚡")
        elif not results_df.empty:
            st.session_state.stress_test_results = (results_df, summary)
            st.toast("✅ 壓力測試完成 / Stress test complete", icon="🎯")
        else:
            st.toast("❌ 壓力測試失敗 / Stress test failed", icon="⚡")

    if 'stress_test_results' not in st.session_state: return
    results_df, summary = st.session_state.stress_test_results
    total_v = summary.get('total_value', 0)

    # Portfolio value header
    st.markdown(f"""
<div style="text-align:center;padding:10px 0 6px;">
  <div style="font-family:var(--f-i);font-size:48px;font-weight:800;color:#FFF;letter-spacing:-2px;line-height:1;">{total_v:,.0f}</div>
  <div style="font-family:var(--f-m);font-size:9px;color:rgba(255,49,49,.4);letter-spacing:4px;text-transform:uppercase;margin-top:4px;">Portfolio Value (TWD) — Stress Scenarios</div>
</div>""", unsafe_allow_html=True)

    pnl_cols  = [c for c in results_df.columns if '損益' in c]
    total_pnl = results_df[pnl_cols].sum()

    # ── RED ALERT CARDS ──
    st.markdown('<div class="stress-alert-grid">', unsafe_allow_html=True)
    for sc, pnl in total_pnl.items():
        pct   = (pnl / total_v * 100) if total_v > 0 else 0
        label = sc.replace('損益_', '')
        st.markdown(f"""
<div class="stress-alert-card">
  <div class="stress-alert-label">{label}</div>
  <div class="stress-alert-val">{pnl:,.0f}</div>
  <div class="stress-alert-pct">{pct:.1f}%</div>
</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # st.metric row (identical to original)
    kpi_cols = st.columns(len(total_pnl))
    for i, (sc, pnl) in enumerate(total_pnl.items()):
        loss_pct = (pnl / total_v) * 100 if total_v > 0 else 0
        kpi_cols[i].metric(
            label=sc.replace('損益_',''),
            value=f"{pnl:,.0f} TWD",
            delta=f"{loss_pct:.1f}%",
        )

    # N×4 Heatmap
    st.divider()
    st.markdown('<div class="t4-chart-panel"><div class="t4-chart-lbl">▸ shock heatmap — per-asset × scenario</div>', unsafe_allow_html=True)
    try:
        heat_df = results_df[['ticker'] + pnl_cols].copy().set_index('ticker')
        heat_df.columns = [c.replace('損益_','') for c in heat_df.columns]
        zvals = heat_df.values.astype(float)
        fig_h = go.Figure(go.Heatmap(
            z=zvals, x=heat_df.columns.tolist(), y=heat_df.index.tolist(),
            colorscale=[[0,'#FF3131'],[0.5,'#1a1a2e'],[1,'#00FF7F']], zmid=0,
            text=[[f"{v:,.0f}" for v in row] for row in zvals],
            texttemplate="%{text}",
            textfont=dict(size=11, family='JetBrains Mono'),
            showscale=True,
            colorbar=dict(tickfont=dict(color='#A0B0C0', size=10),
                          outlinecolor='rgba(255,255,255,0.08)'),
        ))
        fig_h.update_layout(
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)', height=280,
            margin=dict(t=10,b=40,l=80,r=20),
            xaxis=dict(tickfont=dict(color='#B0C0D0', size=11, family='Rajdhani')),
            yaxis=dict(tickfont=dict(color='#B0C0D0', size=11, family='Rajdhani')),
        )
        st.plotly_chart(fig_h, use_container_width=True)
    except Exception as e:
        st.toast(f"⚠️ 熱力圖無法生成 / Heatmap failed: {e}", icon="⚡")
    st.markdown('</div>', unsafe_allow_html=True)

    # [FIX] Build format dict dynamically from actual column names
    fmt = {'value_twd':'{:,.0f}', 'price':'{:,.2f}', 'shares':'{:,.0f}'}
    for c in pnl_cols:
        fmt[c] = '{:,.0f}'
    st.dataframe(results_df.style.format(fmt), use_container_width=True)


# ══════════════════════════════════════════════════════════════════
#  MAIN ENTRY
# ══════════════════════════════════════════════════════════════════
def render():
    """Tab 4 — 全球決策  Cinematic Wealth Command Center V200 — DIRECTOR'S CUT"""
    _inject_css()
    _ensure_portfolio()

    # ── [DC1] TACTICAL GUIDE MODAL (First Visit) ──
    if 't4_guide_shown' not in st.session_state:
        show_tactical_guide()
        return

    # ── 1. THE HERO BILLBOARD (first thing user sees) ──
    _render_hero_billboard()

    # ── 2. THE NAVIGATION RAIL (5 Poster Cards) ──
    _render_nav_rail()

    # ── 3. ACTIVE SECTION ──
    section_map = {
        "4.1": (_s41, "4.1"),
        "4.2": (_s42, "4.2"),
        "4.3": (_s43, "4.3"),
        "4.4": (_s44, "4.4"),
        "4.5": (_s45, "4.5"),
    }

    active = st.session_state.get('active_section', '4.1')
    fn, label = section_map.get(active, (_s41, "4.1"))
    try:
        fn()
    except Exception as exc:
        import traceback
        st.toast(f"❌ Section {label} 發生錯誤 / Error occurred: {exc}", icon="⚡")
        with st.expander(f"🔍 Debug — {label}"):
            st.code(traceback.format_exc())

    # ── FOOTER ──
    st.markdown(
        f'<div class="t4-foot">Titan Cinematic Wealth Command Center V200 — Director\'s Cut · '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',
        unsafe_allow_html=True,
    )
