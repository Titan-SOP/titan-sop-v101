# ui_desktop/tab4_decision.py
# Titan SOP V200 — Tab 4: 全球決策 (CINEMATIC WEALTH COMMAND CENTER)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  Design: Netflix × Palantir × Tesla — "Director's Cut"          ║
# ║  Hero Billboard → Poster Rail Navigation → Tactical Modules     ║
# ║  ALL backtest engines preserved verbatim from V100               ║
# ║  Bug Fixes carried forward: session key race, format dict,      ║
# ║    fillna chaining DeprecationWarning                            ║
# ╚═══════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import re
import io
from datetime import datetime


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
        bench = yf.download(['USDTWD=X'], period="1mo", progress=False)
        if isinstance(bench.columns, pd.MultiIndex): bench.columns = bench.columns.get_level_values(0)
        twd_fx = float(bench['Close'].iloc[-1]) if not bench.empty else 32.0
    except: twd_fx = 32.0

    results = []
    scenarios = {
        '回檔 (-5%)':      -0.05,
        '修正 (-10%)':    -0.10,
        '技術熊市 (-20%)': -0.20,
        '金融海嘯 (-30%)': -0.30,
    }
    for asset in portfolio:
        orig   = asset['ticker']
        shares = asset['shares']
        if orig in ['CASH', 'USD', 'TWD']:
            row = {'ticker': orig, 'type': 'Cash', 'shares': shares,
                   'price': 1.0, 'value_twd': shares}
            for k in scenarios: row[f'損益_{k}'] = 0
            results.append(row)
            continue

        ticker = orig
        is_tw  = bool(re.match(r'^[0-9]', orig)) and 4 <= len(orig) <= 6
        if is_tw: ticker = f"{orig}.TW"
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
#  CSS — CINEMATIC WEALTH COMMAND CENTER
# ══════════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root{
  --c-gold:#FFD700;--c-cyan:#00F5FF;--c-red:#FF3131;
  --c-green:#00FF7F;--c-orange:#FF9A3C;
  --f-d:'Bebas Neue',sans-serif;
  --f-b:'Rajdhani',sans-serif;
  --f-m:'JetBrains Mono',monospace;
  --f-i:'Inter',sans-serif;
}

/* ══════════════════════════════════════════
   TITAN TAB 4 — HERO BILLBOARD
   ══════════════════════════════════════════ */
.hero-container {
  padding: 50px 40px 44px;
  background: linear-gradient(180deg,
    rgba(20,20,20,0) 0%,
    rgba(10,10,14,0.6) 40%,
    rgba(0,0,0,0.85) 100%);
  border-bottom: 1px solid #333;
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
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(255,215,0,0.15) 20%,
    rgba(255,215,0,0.35) 50%,
    rgba(255,215,0,0.15) 80%,
    transparent 100%);
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

/* ══════════════════════════════════════════
   NAVIGATION RAIL — POSTER CARDS
   ══════════════════════════════════════════ */
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

/* ══════════════════════════════════════════
   KELLY TACTICAL CHIPS (4.2)
   ══════════════════════════════════════════ */
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

/* ══════════════════════════════════════════
   RED ALERT CARDS (4.5 Stress)
   ══════════════════════════════════════════ */
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

/* ══════════════════════════════════════════
   SECTION HEADERS (cinematic)
   ══════════════════════════════════════════ */
.t4-sec-head{display:flex;align-items:center;gap:14px;
  padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,.052);margin-bottom:20px;}
.t4-sec-num{font-family:var(--f-d);font-size:56px;color:rgba(0,245,255,.06);letter-spacing:2px;line-height:1;}
.t4-sec-title{font-family:var(--f-d);font-size:22px;color:var(--sa,#00F5FF);letter-spacing:2px;}
.t4-sec-sub{font-family:var(--f-m);font-size:9px;color:rgba(0,245,255,.28);letter-spacing:2px;text-transform:uppercase;margin-top:2px;}

/* ══════════════════════════════════════════
   CHART PANELS
   ══════════════════════════════════════════ */
.t4-chart-panel{background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.055);
  border-radius:16px;padding:18px 12px 10px;margin:14px 0;overflow:hidden;}
.t4-chart-lbl{font-family:var(--f-m);font-size:9px;color:rgba(0,245,255,.28);
  letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;padding-left:6px;}

/* ══════════════════════════════════════════
   ACTION BUTTONS (styled)
   ══════════════════════════════════════════ */
.t4-action div.stButton>button{
  background:rgba(0,245,255,.05)!important;
  border:1px solid rgba(0,245,255,.25)!important;
  color:rgba(0,245,255,.85)!important;
  font-family:var(--f-m)!important;font-size:11px!important;
  letter-spacing:2px!important;min-height:48px!important;
  border-radius:12px!important;text-transform:uppercase!important;
  transition: all 0.3s ease!important;
}
.t4-action div.stButton>button:hover{
  background:rgba(0,245,255,.10)!important;
  box-shadow:0 0 24px rgba(0,245,255,.18)!important;
}
.t4-action-r div.stButton>button{border-color:rgba(255,49,49,.3)!important;color:rgba(255,100,100,.85)!important;background:rgba(255,49,49,.04)!important;}
.t4-action-r div.stButton>button:hover{background:rgba(255,49,49,.1)!important;box-shadow:0 0 20px rgba(255,49,49,.15)!important;}
.t4-action-g div.stButton>button{border-color:rgba(0,255,127,.22)!important;color:rgba(0,255,127,.85)!important;}
.t4-action-g div.stButton>button:hover{background:rgba(0,255,127,.07)!important;}

/* ══════════════════════════════════════════
   LEGACY COMPAT (kelly row for fallback)
   ══════════════════════════════════════════ */
.t4-kelly-row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px;}

/* ══════════════════════════════════════════
   FOOTER
   ══════════════════════════════════════════ */
.t4-foot{font-family:var(--f-m);font-size:9px;color:rgba(70,90,110,.28);
  letter-spacing:2px;text-align:right;margin-top:28px;text-transform:uppercase;}
</style>""", unsafe_allow_html=True)


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
  <div class="hero-time">TITAN GLOBAL DECISION V200 &nbsp;&middot;&nbsp; {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}</div>
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
    st.info("💡 台股 1 張請輸入 1000；美股以 1 股為單位；現金請輸入總額。此處可直接編輯您的資產。")

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
                st.warning("⚠️ 無法獲取即時市價，部分計算欄位將不顯示。")
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

    st.markdown('<div class="t4-action">', unsafe_allow_html=True)
    run_bt = st.button("🚀 啟動全球回測", key="btn_backtest_v200")
    st.markdown('</div>', unsafe_allow_html=True)

    if run_bt:
        pf = st.session_state.get('portfolio_df', pd.DataFrame())
        if pf.empty:
            st.warning("請先在 4.1 配置您的戰略資產。")
        else:
            with st.spinner("正在對全球資產執行回測…"):
                bt_list = []
                for _, row in pf.iterrows():
                    r = _run_fast_backtest(str(row['資產代號']).strip(), initial_capital=1_000_000)
                    if r:
                        r['Ticker'] = str(row['資產代號']).strip()
                        bt_list.append(r)
                st.session_state.backtest_results = bt_list

    if 'backtest_results' not in st.session_state: return
    results = st.session_state.backtest_results
    if not results:
        st.error("所有資產回測失敗，請檢查代號是否正確。"); return

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

    # Collapsible data table
    with st.expander("📋 回測績效數據表", expanded=False):
        st.dataframe(pd.DataFrame(summary_data).style.format({
            '最新價':'{:.2f}','年化報酬 (CAGR)':'{:.2%}',
            '投資性價比 (Sharpe)':'{:.2f}','最大回撤':'{:.2%}','凱利建議 %':'{:.2%}',
        }), use_container_width=True)

    st.divider()

    # Multi-asset overlay (normalized to 100)
    st.markdown('<div class="t4-chart-panel"><div class="t4-chart-lbl">▸ multi-asset equity curve overlay (base = 100)</div>', unsafe_allow_html=True)
    pal = ['#00F5FF','#FFD700','#00FF7F','#FF9A3C','#B77DFF','#FF3131']
    fig_ov = go.Figure()
    for i, res in enumerate(results):
        eq = res['equity_curve']
        norm = (eq / eq.iloc[0]) * 100
        fig_ov.add_trace(go.Scatter(x=norm.index, y=norm.values, name=res['Ticker'],
            line=dict(color=pal[i % len(pal)], width=2),
            hovertemplate=f"<b>{res['Ticker']}</b> %{{y:.1f}}<extra></extra>"))
    fig_ov.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.12)")
    fig_ov.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', height=340, hovermode='x unified',
        legend=dict(font=dict(color='#B0C0D0',size=11,family='Rajdhani')),
        margin=dict(t=10,b=40,l=50,r=10),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),)
    st.plotly_chart(fig_ov, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Individual deep-dive
    st.subheader("深度圖表分析")
    sel = st.selectbox("選擇要查看的資產", [r['Ticker'] for r in results], key="bt_sel_v200")
    res = next((r for r in results if r['Ticker'] == sel), None)
    if res:
        eq = res['equity_curve'].reset_index(); eq.columns = ['Date','Equity']
        fig = px.line(eq, x='Date', y='Equity', title=f"{sel} 權益曲線 (Equity Curve)",
                      labels={'Equity':'投資組合價值','Date':'日期'})
        fig.update_traces(line_color='#17BECF')
        fig.update_layout(template='plotly_dark')
        st.plotly_chart(fig, use_container_width=True)

        dd = res['drawdown_series'].reset_index(); dd.columns = ['Date','Drawdown']
        dd['Drawdown_pct'] = dd['Drawdown'] * 100
        fig2 = px.area(dd, x='Date', y='Drawdown_pct',
                       title=f"{sel} 水下回撤圖 (Underwater Plot)",
                       labels={'Drawdown_pct':'從高點回落 (%)','Date':'日期'})
        fig2.update_traces(fillcolor='rgba(255,87,51,0.4)', line_color='rgba(255,87,51,1.0)')
        fig2.update_yaxes(ticksuffix="%")
        fig2.update_layout(template='plotly_dark')
        st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
#  SECTION 4.3 — 均線戰法回測實驗室
# ══════════════════════════════════════════════════════════════════
def _s43():
    st.markdown('<div class="t4-sec-head" style="--sa:#FF9A3C"><div class="t4-sec-num">4.3</div><div><div class="t4-sec-title" style="color:#FF9A3C;">均線戰法實驗室</div><div class="t4-sec-sub">15 MA Strategies · 10-Year Wealth Projection</div></div></div>', unsafe_allow_html=True)
    st.info("選擇一檔標的，自動執行 15 種均線策略回測，推演 10 年財富變化。")

    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    if pf.empty:
        st.warning("請先在 4.1 配置您的戰略資產。"); return

    sel_t = st.selectbox("選擇回測標的", options=pf['資產代號'].tolist(), key="ma_lab_ticker_v200")
    strategies = [
        "價格 > 20MA","價格 > 43MA","價格 > 60MA","價格 > 87MA","價格 > 284MA",
        "非對稱: P>20進 / P<60出",
        "20/60 黃金/死亡交叉","20/87 黃金/死亡交叉","20/284 黃金/死亡交叉",
        "43/87 黃金/死亡交叉","43/284 黃金/死亡交叉",
        "60/87 黃金/死亡交叉","60/284 黃金/死亡交叉",
        "🔥 核心戰法: 87MA ↗ 284MA",
        "雙確認: P>20 & P>60 進 / P<60 出",
    ]

    st.markdown('<div class="t4-action">', unsafe_allow_html=True)
    run_lab = st.button("🔬 啟動 15 種均線實驗", key="start_ma_lab_v200")
    st.markdown('</div>', unsafe_allow_html=True)

    if run_lab:
        with st.spinner(f"正在對 {sel_t} 執行 15 種均線策略回測…"):
            ma_results = [r for s in strategies
                          if (r := _run_ma_strategy_backtest(sel_t, s,
                              start_date="2015-01-01", initial_capital=1_000_000))]
            # [FIX] Save ticker key separately to prevent stale display
            st.session_state.ma_lab_results     = ma_results
            st.session_state.ma_lab_result_tick = sel_t

    # [FIX] Check the saved ticker key (not the widget key) to prevent stale display
    if ('ma_lab_results' not in st.session_state
            or st.session_state.get('ma_lab_result_tick') != sel_t):
        return

    results = st.session_state.ma_lab_results
    if not results:
        st.error(f"無法取得 {sel_t} 的回測數據。"); return

    st.success(f"✅ {sel_t} — 15 種均線策略回測完成")
    wd = pd.DataFrame([{
        '策略名稱':           r['strategy_name'],
        '年化報酬 (CAGR)':   r['cagr'],
        '回測期末資金':       r['final_equity'],
        '最大回撤':           r['max_drawdown'],
        '未來 10 年預期資金': r['future_10y_capital'],
        '回測年數':           r['num_years'],
    } for r in results]).sort_values('年化報酬 (CAGR)', ascending=False)

    st.subheader("📊 策略績效與財富推演")
    st.dataframe(wd.style.format({
        '年化報酬 (CAGR)':   '{:.2%}', '回測期末資金':       '{:,.0f}',
        '最大回撤':           '{:.2%}', '未來 10 年預期資金': '{:,.0f}',
        '回測年數':           '{:.1f}',
    }), use_container_width=True)

    # CAGR Ranking Bar Chart
    st.markdown('<div class="t4-chart-panel"><div class="t4-chart-lbl">▸ CAGR strategy ranking</div>', unsafe_allow_html=True)
    bar_s = wd.sort_values('年化報酬 (CAGR)', ascending=True)
    colors = ['#00FF7F' if v > 0.10 else ('#FFD700' if v > 0 else '#FF6B6B')
              for v in bar_s['年化報酬 (CAGR)']]
    fig_bar = go.Figure(go.Bar(
        x=bar_s['年化報酬 (CAGR)'] * 100, y=bar_s['策略名稱'], orientation='h',
        marker_color=colors,
        text=[f"{v:.1f}%" for v in bar_s['年化報酬 (CAGR)'] * 100],
        textposition='outside',
        textfont=dict(color='#DDE', size=11, family='JetBrains Mono'),
    ))
    fig_bar.add_vline(x=0, line_color='rgba(255,255,255,0.15)', line_width=1)
    fig_bar.update_layout(
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', height=420,
        xaxis=dict(ticksuffix="%", gridcolor='rgba(255,255,255,0.04)'),
        yaxis=dict(tickfont=dict(size=11, family='Rajdhani', color='#B0C0D0')),
        margin=dict(t=10, b=30, l=230, r=60),
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Excel download
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as w:
        wd.to_excel(w, index=False, sheet_name='MA_Backtest_Report')
    st.markdown('<div class="t4-action-g">', unsafe_allow_html=True)
    st.download_button("📥 下載戰術回測報表 (Excel)", buf.getvalue(),
        f"{sel_t}_ma_lab_report.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # Strategy chart
    st.subheader("📈 策略視覺化")
    sel_s = st.selectbox("選擇策略查看圖表",
                         [r['strategy_name'] for r in results], key="ma_chart_v200")
    sel_r = next((r for r in results if r['strategy_name'] == sel_s), None)
    if sel_r:
        eq = sel_r['equity_curve'].reset_index(); eq.columns = ['Date','Equity']
        fig_eq = px.line(eq, x='Date', y='Equity',
                         title=f"{sel_t} — {sel_s} 權益曲線",
                         labels={'Equity':'資金 (元)','Date':'日期'})
        fig_eq.update_traces(line_color='#2ECC71')
        fig_eq.update_layout(template='plotly_dark')
        st.plotly_chart(fig_eq, use_container_width=True)

        dd = sel_r['drawdown_series'].reset_index(); dd.columns = ['Date','Drawdown']
        dd['Drawdown_pct'] = dd['Drawdown'] * 100
        fig_dd = px.area(dd, x='Date', y='Drawdown_pct',
                         title=f"{sel_t} — {sel_s} 水下回撤圖",
                         labels={'Drawdown_pct':'回撤 (%)','Date':'日期'})
        fig_dd.update_traces(fillcolor='rgba(231,76,60,0.3)', line_color='rgba(231,76,60,1.0)')
        fig_dd.update_yaxes(ticksuffix="%")
        fig_dd.update_layout(template='plotly_dark')
        st.plotly_chart(fig_dd, use_container_width=True)


# ══════════════════════════════════════════════════════════════════
#  SECTION 4.4 — 智慧調倉計算機
# ══════════════════════════════════════════════════════════════════
def _s44():
    st.markdown('<div class="t4-sec-head" style="--sa:#00FF7F"><div class="t4-sec-num">4.4</div><div><div class="t4-sec-title" style="color:#00FF7F;">智慧調倉計算機</div><div class="t4-sec-sub">Target Weight → Delta Shares Rebalancing Plan</div></div></div>', unsafe_allow_html=True)

    pf = st.session_state.get('portfolio_df', pd.DataFrame()).copy()
    if pf.empty or '資產代號' not in pf.columns:
        st.warning("請先在 4.1 配置您的戰略資產。"); return

    tickers = pf['資產代號'].tolist()
    with st.spinner("正在獲取最新市價…"):
        try:
            pd_ = yf.download(tickers, period="1d", progress=False)['Close']
            latest = pd_.iloc[-1] if isinstance(pd_, pd.DataFrame) else pd_
            # [FIX] avoid chained fillna DeprecationWarning
            lp_series = pf['資產代號'].map(
                latest.to_dict() if hasattr(latest, 'to_dict') else {})
            pf['最新市價']   = pd.to_numeric(lp_series, errors='coerce').fillna(1.0)
            pf['目前市值']   = pf['持有數量 (股)'] * pf['最新市價']
            total_v          = pf['目前市值'].sum()
            pf['目前權重 %'] = (pf['目前市值'] / total_v) * 100

            st.markdown(f"""
<div style="text-align:center;padding:10px 0 18px;">
  <div style="font-family:var(--f-m);font-size:9px;color:rgba(0,255,127,.35);letter-spacing:4px;text-transform:uppercase;margin-bottom:6px;">CURRENT TOTAL ASSETS</div>
  <div style="font-family:var(--f-i);font-size:52px;font-weight:800;color:#FFF;letter-spacing:-2px;line-height:1;">{total_v:,.0f}</div>
  <div style="font-family:var(--f-m);font-size:10px;color:rgba(255,255,255,.2);letter-spacing:3px;margin-top:4px;">TWD</div>
</div>""", unsafe_allow_html=True)

            # Horizontal column inputs
            st.write("**請輸入各資產目標權重（橫向快速設定）：**")
            tw_cols = st.columns(len(pf))
            target_weights = []
            for col, (_, row) in zip(tw_cols, pf.iterrows()):
                with col:
                    w = st.number_input(f"{row['資產代號']}",
                        min_value=0.0, max_value=100.0,
                        value=float(round(row['目前權重 %'], 1)),
                        step=1.0, key=f"target_{row['資產代號']}_v200")
                    target_weights.append(w)

            total_w = sum(target_weights)
            if not (99 <= total_w <= 101):
                st.warning(f"⚠️ 目標權重總和 {total_w:.1f}%，建議調整至接近 100%。")

            pf['目標權重 %'] = target_weights
            pf['目標市值']   = (pf['目標權重 %'] / 100) * total_v
            pf['調倉市值']   = pf['目標市值'] - pf['目前市值']
            pf['調倉股數']   = (pf['調倉市值'] / pf['最新市價']).astype(int)

            st.subheader("調倉計畫")
            st.dataframe(
                pf[['資產代號','目前權重 %','目標權重 %','調倉股數']].style.format({
                    '目前權重 %': '{:.1f}%', '目標權重 %': '{:.1f}%', '調倉股數': '{:+,}',
                }),
                use_container_width=True,
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
            st.error(f"獲取市價或計算失敗: {e}")


# ══════════════════════════════════════════════════════════════════
#  SECTION 4.5 — 全球黑天鵝壓力測試 (RED ALERT CARDS)
# ══════════════════════════════════════════════════════════════════
def _s45():
    st.markdown('<div class="t4-sec-head" style="--sa:#FF3131"><div class="t4-sec-num">4.5</div><div><div class="t4-sec-title" style="color:#FF3131;">黑天鵝壓力測試</div><div class="t4-sec-sub">Global Systemic Shock Simulation · 4 Scenarios</div></div></div>', unsafe_allow_html=True)
    st.info("此功能將讀取您在 4.1 配置的資產，模擬全球系統性風險下的投資組合衝擊。")

    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    if pf.empty:
        st.warning("請先在 4.1 配置您的戰略資產。"); return

    st.markdown('<div class="t4-action t4-action-r">', unsafe_allow_html=True)
    run_stress = st.button("💥 啟動壓力測試", key="btn_stress_v200")
    st.markdown('</div>', unsafe_allow_html=True)

    if run_stress:
        portfolio_text = "\n".join(
            f"{row['資產代號']};{row['持有數量 (股)']}" for _, row in pf.iterrows())
        with st.spinner("執行全球壓力測試…"):
            results_df, summary = _run_stress_test(portfolio_text)
        if "error" in summary:
            st.error(summary["error"])
        elif not results_df.empty:
            st.session_state.stress_test_results = (results_df, summary)
        else:
            st.error("壓力測試失敗，未返回任何結果。")

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
        st.warning(f"熱力圖無法生成: {e}")
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
    """Tab 4 — 全球決策  Cinematic Wealth Command Center V200"""
    _inject_css()
    _ensure_portfolio()

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
        st.error(f"❌ Section {label} 發生錯誤: {exc}")
        with st.expander(f"🔍 Debug — {label}"):
            st.code(traceback.format_exc())

    # ── FOOTER ──
    st.markdown(
        f'<div class="t4-foot">Titan Cinematic Wealth Command Center V200 · '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',
        unsafe_allow_html=True,
    )
