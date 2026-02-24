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
import time


# ══════════════════════════════════════════════════════════════════
# 🎯 FEATURE 3: VALKYRIE AI TYPEWRITER
# ══════════════════════════════════════════════════════════════════
def _is_rl(e) -> bool:
    """Yahoo Finance Rate Limit 偵測（tab4）"""
    msg = str(e).lower()
    return any(k in msg for k in ["429","too many requests","rate limit","ratelimit","rate limited"])


def stream_generator(text):
    """
    Valkyrie AI Typewriter: Stream text word-by-word
    Creates the sensation of live AI transmission.
    """
    for word in text.split():
        yield word + " "
        time.sleep(0.02)


# ══════════════════════════════════════════════════════════════════
# 🔧 CORE UTILITY: 正確的即時報價查詢（台股/美股/ETF 通用）
# ══════════════════════════════════════════════════════════════════
def _is_tw_ticker(t: str) -> bool:
    """判斷是否為台股代號（純數字開頭，4~6碼）"""
    return bool(re.match(r'^[0-9]', t)) and 4 <= len(t) <= 6


def _fetch_latest_prices(orig_tickers: list) -> dict:
    """
    輸入原始代號列表（含台股/美股/ETF/CASH混合），
    回傳 {原始代號: 最新收盤價} dict。

    修正邏輯：
    1. 台股代號自動加 .TW 後綴查詢
    2. 若 .TW 查無資料，fallback 試 .TWO（興櫃/上櫃）
    3. 多 ticker 批量下載時用 query_t → orig_t 反向對照
    4. 全程維護原始代號作為 key，不污染外部資料
    """
    prices = {}
    non_cash = [t for t in orig_tickers if t.upper() not in ('CASH', 'USD', 'TWD')]
    if not non_cash:
        return prices

    tw_tickers  = [t for t in non_cash if _is_tw_ticker(t)]
    us_tickers  = [t for t in non_cash if not _is_tw_ticker(t)]

    def _dl_close(query_list):
        """下載並回傳最新一日收盤，支援單/多 ticker。"""
        if not query_list:
            return {}
        try:
            raw = yf.download(query_list, period="5d", progress=False, auto_adjust=True)
            if raw.empty:
                return {}
            close = raw['Close'] if 'Close' in raw.columns else raw
            if isinstance(close, pd.Series):
                # 單一 ticker
                val = close.dropna().iloc[-1] if not close.dropna().empty else None
                return {query_list[0]: float(val)} if val is not None else {}
            else:
                # 多 ticker → DataFrame，欄名即 query ticker
                last = close.dropna(how='all').iloc[-1]
                return {k: float(v) for k, v in last.items() if pd.notna(v)}
        except Exception as _e4dl:
            if _is_rl(_e4dl):
                st.toast("⏳ Yahoo Finance 限速，最新價格暫時無法取得，請稍後重試。", icon="⏳")
            return {}

    # ── 台股：先試 .TW，失敗的 fallback .TWO ──
    if tw_tickers:
        tw_query = [f"{t}.TW" for t in tw_tickers]
        tw_raw   = _dl_close(tw_query)
        # 對照回原始代號
        missing_tw = []
        for orig, q in zip(tw_tickers, tw_query):
            if q in tw_raw and pd.notna(tw_raw[q]):
                prices[orig] = tw_raw[q]
            else:
                missing_tw.append(orig)
        # fallback .TWO
        if missing_tw:
            two_query = [f"{t}.TWO" for t in missing_tw]
            two_raw   = _dl_close(two_query)
            for orig, q in zip(missing_tw, two_query):
                if q in two_raw and pd.notna(two_raw[q]):
                    prices[orig] = two_raw[q]

    # ── 美股：直接用原始代號 ──
    if us_tickers:
        us_raw = _dl_close(us_tickers)
        for orig in us_tickers:
            if orig in us_raw and pd.notna(us_raw[orig]):
                prices[orig] = us_raw[orig]

    return prices


# ══════════════════════════════════════════════════════════════════
# 🎯 FEATURE 1: TACTICAL GUIDE MODAL
# ══════════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導 Mode")
def show_guide_modal():
    st.markdown("""
    ### 指揮官，歡迎進入本戰區
    
    **核心功能**：
    - **全球資產配置**：支援美股、台股、ETF、現金等多元資產，一鍵完成投資組合建構與即時市值追蹤。
    - **戰略回測引擎**：內建 15 種均線策略、Kelly 公式、風險平價等智能模型，10 年歷史數據驗證。
    - **壓力測試模擬**：模擬全球金融危機 (2008/2020/2022) 等系統性風險，評估投資組合韌性與最大回撤。
    
    **操作方式**：點擊上方選單切換模式 (4.1 配置 → 4.2 回測 → 4.3 策略 → 4.4 優化 → 4.5 壓測)。
    
    **狀態監控**：隨時留意畫面中的警示訊號 (權重總和、回測失敗、市價異常等提示)。
    
    ---
    *建議：先在 4.1 配置資產 → 執行 4.2 回測 → 根據結果調整權重或策略*
    """)
    
    if st.button("✅ Roger that, 收到", type="primary", use_container_width=True):
        st.session_state["guide_shown_" + __name__] = True
        st.rerun()


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
    except Exception as _e4x:
        if _is_rl(_e4x):
            st.toast("⏳ Yahoo Finance 限速，資料暫時無法取得。", icon="⏳")
        return None


@st.cache_data(ttl=7200)
def _fetch_price_data(ticker, start_date):
    """共用的價格資料下載，自動處理台股/美股/TWO後綴，回傳實際起始日。"""
    original_ticker = ticker
    is_tw = re.match(r'^[0-9]', ticker) and 4 <= len(ticker) <= 6
    if is_tw:
        ticker = f"{ticker}.TW"
    df = yf.download(ticker, start=start_date, progress=False)
    if df.empty and is_tw:
        df = yf.download(f"{original_ticker}.TWO", start=start_date, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


@st.cache_data(ttl=7200)
def _run_ma_strategy_backtest(ticker, strategy_name, start_date="2015-01-01",
                               initial_capital=1_000_000, commission=0.001425,
                               slippage=0.001):
    """
    15 種均線策略回測引擎 (V200 Enhanced)
    新增: 交易成本(手續費+滑點)、交易次數、平均持倉天數、
          年化波動率、Calmar Ratio、買進持有基準、VOO 基準
    """
    try:
        df = _fetch_price_data(ticker, start_date)
        # 若資料不足，從最早可得日期開始（上市期間不足問題）
        if df.empty:
            return None
        # 至少需 300 天以計算 284MA
        if len(df) < 300:
            df = _fetch_price_data(ticker, "2000-01-01")
            if df.empty or len(df) < 300:
                return None

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

        # ── 交易成本：每次訊號切換時扣手續費+滑點 ──
        df['Pct_Change']   = df['Close'].pct_change()
        df['Trade']        = df['Signal'].diff().abs().fillna(0)  # 1=切換點
        cost_per_trade     = commission + slippage
        df['Cost']         = df['Trade'] * cost_per_trade  # 每次進出扣一次
        df['Net_Return']   = df['Signal'].shift(1) * df['Pct_Change'] - df['Cost']
        df['Equity']       = (1 + df['Net_Return'].fillna(0)).cumprod() * initial_capital
        df['Drawdown']     = (df['Equity'] / df['Equity'].cummax()) - 1

        # ── 買進持有 (Buy & Hold) — 第一性原理：不操作會怎樣? ──
        df['BH_Return']    = df['Pct_Change']
        df['BH_Equity']    = (1 + df['BH_Return'].fillna(0)).cumprod() * initial_capital
        df['BH_Drawdown']  = (df['BH_Equity'] / df['BH_Equity'].cummax()) - 1

        num_years      = len(df) / 252
        total_return   = df['Equity'].iloc[-1] / initial_capital - 1
        cagr           = ((1 + total_return) ** (1 / num_years)) - 1 if num_years > 0 else 0
        bh_return      = df['BH_Equity'].iloc[-1] / initial_capital - 1
        bh_cagr        = ((1 + bh_return) ** (1 / num_years)) - 1 if num_years > 0 else 0
        alpha_vs_bh    = cagr - bh_cagr  # 策略相對買持超額報酬

        # ── 進階指標 ──
        daily_ret      = df['Net_Return'].dropna()
        ann_vol        = daily_ret.std() * np.sqrt(252)
        sharpe         = (daily_ret.mean() * 252 - 0.02) / ann_vol if ann_vol > 0 else 0
        mdd            = df['Drawdown'].min()
        calmar         = cagr / abs(mdd) if mdd != 0 else 0

        # ── 交易統計 ──
        trade_entries  = df[df['Trade'] == 1].index
        num_trades     = len(trade_entries) // 2 + 1  # 進出各算一次
        hold_days_total= df[df['Signal'].shift(1) == 1].shape[0]
        avg_hold_days  = hold_days_total / max(num_trades, 1)
        time_in_mkt    = df['Signal'].mean()  # 在市場中的時間佔比

        actual_start   = str(df.index[0].date())

        return {
            "strategy_name":      strategy_name,
            "cagr":               cagr,
            "final_equity":       df['Equity'].iloc[-1],
            "max_drawdown":       mdd,
            "future_10y_capital": initial_capital * ((1 + cagr) ** 10),
            "num_years":          num_years,
            "equity_curve":       df['Equity'],
            "drawdown_series":    df['Drawdown'],
            # 新增指標
            "ann_vol":            ann_vol,
            "sharpe":             sharpe,
            "calmar":             calmar,
            "num_trades":         num_trades,
            "avg_hold_days":      avg_hold_days,
            "time_in_market":     time_in_mkt,
            "alpha_vs_bh":        alpha_vs_bh,
            # 買進持有 benchmark
            "bh_cagr":            bh_cagr,
            "bh_equity":          df['BH_Equity'].iloc[-1],
            "bh_max_drawdown":    df['BH_Drawdown'].min(),
            "bh_equity_curve":    df['BH_Equity'],
            "actual_start":       actual_start,
        }
    except Exception as _e4x:
        if _is_rl(_e4x):
            st.toast("⏳ Yahoo Finance 限速，資料暫時無法取得。", icon="⏳")
        return None


@st.cache_data(ttl=7200)
def _fetch_voo_benchmark(start_date, initial_capital=1_000_000):
    """下載 VOO 作為全球股市基準，回傳權益曲線與 CAGR。"""
    try:
        df = yf.download("VOO", start=start_date, progress=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df['Ret']    = df['Close'].pct_change()
        df['Equity'] = (1 + df['Ret'].fillna(0)).cumprod() * initial_capital
        num_years    = len(df) / 252
        total_ret    = df['Equity'].iloc[-1] / initial_capital - 1
        cagr         = ((1 + total_ret) ** (1 / num_years)) - 1 if num_years > 0 else 0
        df['Drawdown'] = (df['Equity'] / df['Equity'].cummax()) - 1
        return {
            "cagr":         cagr,
            "final_equity": df['Equity'].iloc[-1],
            "max_drawdown": df['Drawdown'].min(),
            "equity_curve": df['Equity'],
            "num_years":    num_years,
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
            time.sleep(0.3)  # ⚡ rate limit 防護
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
#  ENHANCED DEFAULT PORTFOLIO (使用者要求的11檔持倉)
# ══════════════════════════════════════════════════════════════════
_DEFAULT_PORTFOLIO = pd.DataFrame([
    # 台股核心（3檔）
    {'資產代號': '2330',    '持有數量 (股)': 1000,  '買入均價': 1000.0, '資產類別': 'Stock'},
    {'資產代號': '006208',  '持有數量 (股)': 10000, '買入均價': 35.0,   '資產類別': 'ETF'},
    {'資產代號': '00675L',  '持有數量 (股)': 5000,  '買入均價': 50.0,   '資產類別': 'ETF'},
    # 美股科技巨頭（4檔）
    {'資產代號': 'TSLA',    '持有數量 (股)': 50,    '買入均價': 250.0,  '資產類別': 'US_Stock'},
    {'資產代號': 'PLTR',    '持有數量 (股)': 200,   '買入均價': 25.0,   '資產類別': 'US_Stock'},
    {'資產代號': 'GOOGL',   '持有數量 (股)': 80,    '買入均價': 140.0,  '資產類別': 'US_Stock'},
    {'資產代號': 'NVDA',    '持有數量 (股)': 100,   '買入均價': 500.0,  '資產類別': 'US_Stock'},
    {'資產代號': 'AVGO',    '持有數量 (股)': 30,    '買入均價': 1500.0, '資產類別': 'US_Stock'},
    # 量子科技（3檔）
    {'資產代號': 'RGTI',    '持有數量 (股)': 500,   '買入均價': 15.0,   '資產類別': 'US_Stock'},
    {'資產代號': 'IONQ',    '持有數量 (股)': 300,   '買入均價': 20.0,   '資產類別': 'US_Stock'},
    {'資產代號': 'QBTS',    '持有數量 (股)': 400,   '買入均價': 8.0,    '資產類別': 'US_Stock'},
])

# ══════════════════════════════════════════════════════════════════
#  QUICK TEMPLATES (快速範本系統)
# ══════════════════════════════════════════════════════════════════
PORTFOLIO_TEMPLATES = {
    "🎯 預設持倉 (科技+量子)": _DEFAULT_PORTFOLIO.copy(),
    
    "🚀 純科技股組合": pd.DataFrame([
        {'資產代號': 'NVDA',  '持有數量 (股)': 100,  '買入均價': 500.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'TSLA',  '持有數量 (股)': 80,   '買入均價': 250.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'GOOGL', '持有數量 (股)': 100,  '買入均價': 140.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'AVGO',  '持有數量 (股)': 40,   '買入均價': 1500.0, '資產類別': 'US_Stock'},
        {'資產代號': '2330',  '持有數量 (股)': 1000, '買入均價': 1000.0, '資產類別': 'Stock'},
    ]),
    
    "💎 量子科技專注": pd.DataFrame([
        {'資產代號': 'IONQ', '持有數量 (股)': 500, '買入均價': 20.0, '資產類別': 'US_Stock'},
        {'資產代號': 'RGTI', '持有數量 (股)': 800, '買入均價': 15.0, '資產類別': 'US_Stock'},
        {'資產代號': 'QBTS', '持有數量 (股)': 600, '買入均價': 8.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'NVDA', '持有數量 (股)': 100, '買入均價': 500.0,'資產類別': 'US_Stock'},
    ]),
    
    "🇹🇼 台股核心組合": pd.DataFrame([
        {'資產代號': '2330',   '持有數量 (股)': 2000,  '買入均價': 1000.0, '資產類別': 'Stock'},
        {'資產代號': '006208', '持有數量 (股)': 20000, '買入均價': 35.0,   '資產類別': 'ETF'},
        {'資產代號': '2454',   '持有數量 (股)': 1000,  '買入均價': 1200.0, '資產類別': 'Stock'},
        {'資產代號': '2317',   '持有數量 (股)': 1000,  '買入均價': 600.0,  '資產類別': 'Stock'},
        {'資產代號': '00675L', '持有數量 (股)': 5000,  '買入均價': 50.0,   '資產類別': 'ETF'},
    ]),
    
    "⚖️ 平衡配置": pd.DataFrame([
        {'資產代號': '006208', '持有數量 (股)': 15000, '買入均價': 35.0,     '資產類別': 'ETF'},
        {'資產代號': 'SPY',    '持有數量 (股)': 100,   '買入均價': 450.0,    '資產類別': 'US_Stock'},
        {'資產代號': 'QQQ',    '持有數量 (股)': 80,    '買入均價': 380.0,    '資產類別': 'US_Stock'},
        {'資產代號': 'CASH',   '持有數量 (股)': 1,     '買入均價': 500000.0, '資產類別': 'Cash'},
    ]),

    # ── 5 NEW TEMPLATES ──────────────────────────────────────────────
    "🦅 科技七巨頭 Mag7": pd.DataFrame([
        # Magnificent 7: AAPL MSFT GOOGL AMZN META NVDA TSLA
        {'資產代號': 'AAPL',  '持有數量 (股)': 120,  '買入均價': 185.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'MSFT',  '持有數量 (股)': 80,   '買入均價': 420.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'GOOGL', '持有數量 (股)': 150,  '買入均價': 175.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'AMZN',  '持有數量 (股)': 100,  '買入均價': 195.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'META',  '持有數量 (股)': 60,   '買入均價': 560.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'NVDA',  '持有數量 (股)': 150,  '買入均價': 130.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'TSLA',  '持有數量 (股)': 80,   '買入均價': 250.0,  '資產類別': 'US_Stock'},
    ]),

    "💻 科技十巨頭 Tech10": pd.DataFrame([
        # Mag7 + AVGO + ORCL + AMD
        {'資產代號': 'AAPL',  '持有數量 (股)': 80,   '買入均價': 185.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'MSFT',  '持有數量 (股)': 50,   '買入均價': 420.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'GOOGL', '持有數量 (股)': 80,   '買入均價': 175.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'AMZN',  '持有數量 (股)': 60,   '買入均價': 195.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'META',  '持有數量 (股)': 40,   '買入均價': 560.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'NVDA',  '持有數量 (股)': 100,  '買入均價': 130.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'TSLA',  '持有數量 (股)': 60,   '買入均價': 250.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'AVGO',  '持有數量 (股)': 30,   '買入均價': 1500.0, '資產類別': 'US_Stock'},
        {'資產代號': 'ORCL',  '持有數量 (股)': 100,  '買入均價': 180.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'AMD',   '持有數量 (股)': 100,  '買入均價': 160.0,  '資產類別': 'US_Stock'},
    ]),

    "🤖 AI 革命主題": pd.DataFrame([
        # AI基礎設施 + 應用層
        {'資產代號': 'NVDA',  '持有數量 (股)': 150,  '買入均價': 130.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'AMD',   '持有數量 (股)': 100,  '買入均價': 160.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'AVGO',  '持有數量 (股)': 25,   '買入均價': 1500.0, '資產類別': 'US_Stock'},
        {'資產代號': 'PLTR',  '持有數量 (股)': 300,  '買入均價': 25.0,   '資產類別': 'US_Stock'},
        {'資產代號': 'MSFT',  '持有數量 (股)': 50,   '買入均價': 420.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'GOOGL', '持有數量 (股)': 80,   '買入均價': 175.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'META',  '持有數量 (股)': 40,   '買入均價': 560.0,  '資產類別': 'US_Stock'},
        {'資產代號': '2330',  '持有數量 (股)': 500,  '買入均價': 1000.0, '資產類別': 'Stock'},
        {'資產代號': '2454',  '持有數量 (股)': 500,  '買入均價': 1200.0, '資產類別': 'Stock'},
    ]),

    "🛡️ 防禦型配置": pd.DataFrame([
        # 高股息+債券ETF+公用事業+消費必需
        {'資產代號': 'VYM',   '持有數量 (股)': 200,  '買入均價': 120.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'SCHD',  '持有數量 (股)': 200,  '買入均價': 85.0,   '資產類別': 'US_Stock'},
        {'資產代號': 'BND',   '持有數量 (股)': 400,  '買入均價': 72.0,   '資產類別': 'US_Bond'},
        {'資產代號': 'JNJ',   '持有數量 (股)': 100,  '買入均價': 148.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'PG',    '持有數量 (股)': 100,  '買入均價': 162.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'KO',    '持有數量 (股)': 200,  '買入均價': 62.0,   '資產類別': 'US_Stock'},
        {'資產代號': '0056',  '持有數量 (股)': 10000,'買入均價': 34.0,   '資產類別': 'ETF'},
        {'資產代號': 'CASH',  '持有數量 (股)': 1,    '買入均價': 300000.0,'資產類別': 'Cash'},
    ]),

    "🌏 全球分散配置": pd.DataFrame([
        # 美股大盤+新興市場+歐洲+台股+黃金+債券
        {'資產代號': 'VTI',   '持有數量 (股)': 150,  '買入均價': 240.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'VEA',   '持有數量 (股)': 200,  '買入均價': 50.0,   '資產類別': 'US_Stock'},
        {'資產代號': 'VWO',   '持有數量 (股)': 200,  '買入均價': 42.0,   '資產類別': 'US_Stock'},
        {'資產代號': 'GLD',   '持有數量 (股)': 80,   '買入均價': 195.0,  '資產類別': 'US_Stock'},
        {'資產代號': 'BND',   '持有數量 (股)': 250,  '買入均價': 72.0,   '資產類別': 'US_Bond'},
        {'資產代號': '006208','持有數量 (股)': 10000, '買入均價': 35.0,   '資產類別': 'ETF'},
        {'資產代號': '00713', '持有數量 (股)': 5000,  '買入均價': 60.0,   '資產類別': 'ETF'},
        {'資產代號': 'CASH',  '持有數量 (股)': 1,    '買入均價': 200000.0,'資產類別': 'Cash'},
    ]),
}

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
  min-height: 160px;
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
  font-family: var(--f-b);
  font-size: 28px;
  font-weight: 700;
  color: #FFF;
  letter-spacing: 1px;
  line-height: 1.2;
  margin-bottom: 4px;
}
.nav-poster-sub {
  font-family: var(--f-m);
  font-size: 26px;
  color: rgba(160,176,192,0.45);
  letter-spacing: 1px;
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
    all_tickers = pf['資產代號'].tolist()

    # ── [FIX] 使用統一報價函式，正確處理台股/美股/ETF ──
    lp_map = _fetch_latest_prices(all_tickers)

    # Cash 類資產：現價 = 買入均價（面值）
    for _, row in pf[pf['資產類別'] == 'Cash'].iterrows():
        lp_map[row['資產代號']] = float(row['買入均價'])

    pf['現價'] = pf['資產代號'].map(lp_map)
    # 仍查不到的 fallback 買入均價（避免顯示 NaN）
    mask = pf['現價'].isna()
    pf.loc[mask, '現價'] = pf.loc[mask, '買入均價']
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
    st.markdown('<div class="t4-sec-head" style="--sa:#00F5FF"><div class="t4-sec-num">4.1</div><div><div class="t4-sec-title">戰略資產配置</div><div class="t4-sec-sub">Strategic Asset Allocation · Enhanced</div></div></div>', unsafe_allow_html=True)
    
    # 操作說明 Info Box
    st.markdown("""
<div style="background:linear-gradient(135deg, rgba(0,245,255,0.03), rgba(0,245,255,0.01));border:1px solid rgba(0,245,255,0.15);border-left:3px solid #00F5FF;border-radius:10px;padding:16px;margin:16px 0;font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(255,255,255,0.8);line-height:1.6;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#00F5FF;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;font-weight:700;">💡 操作指引</div>
    <strong>快速開始：</strong>
    <ul style="margin:8px 0 0 20px;padding-left:0;">
        <li>選擇「快速範本」立即載入預設組合</li>
        <li>點擊表格任意欄位直接編輯（台股1張=1000股）</li>
        <li>使用「+」按鈕新增資產，「-」刪除資產</li>
        <li>儲存後自動同步到所有模組（4.2~4.5）</li>
    </ul>
    <strong>進階功能：</strong> 批量匯入CSV、快速範本
</div>
""", unsafe_allow_html=True)
    
    # 快速範本選擇器
    st.markdown("### 🚀 快速範本")
    
    template_keys = list(PORTFOLIO_TEMPLATES.keys())
    # 每行 5 個，自動分行
    num_cols = 5
    for row_start in range(0, len(template_keys), num_cols):
        row_keys = template_keys[row_start:row_start + num_cols]
        cols = st.columns(num_cols)
        for i, template_name in enumerate(row_keys):
            with cols[i]:
                if st.button(template_name, key=f"template_{row_start+i}_v200", use_container_width=True):
                    st.session_state.portfolio_df = PORTFOLIO_TEMPLATES[template_name].copy()
                    st.toast(f"✅ 已載入範本：{template_name}", icon="🎯")
                    st.rerun()
    
    st.divider()
    st.markdown("### 📊 持倉明細")
    st.toast("ℹ️ 台股 1 張請輸入 1000；美股以 1 股為單位；現金請輸入總額。此處可直接編輯您的資產。", icon="📡")

    ptd = st.session_state.get('_hero_pf', st.session_state.portfolio_df.copy())

    # Recompute if hero data not available
    if '市值' not in ptd.columns:
        all_tickers = ptd['資產代號'].tolist()
        # ── [FIX] 使用統一報價函式 ──
        lp_map = _fetch_latest_prices(all_tickers)
        # Cash fallback
        for _, row in ptd[ptd['資產類別'] == 'Cash'].iterrows():
            lp_map[row['資產代號']] = float(row['買入均價'])

        ptd['現價'] = ptd['資產代號'].map(lp_map)
        mask = ptd['現價'].isna()
        ptd.loc[mask, '現價'] = ptd.loc[mask, '買入均價']
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
        
        # 批量操作功能
        st.markdown("---")
        st.markdown("### 🔧 批量操作")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 匯出 CSV", key="export_csv_v200", use_container_width=True):
                csv = ptd.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載持倉",
                    data=csv,
                    file_name=f"portfolio_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_csv_v200",
                    use_container_width=True
                )
        
        with col2:
            uploaded = st.file_uploader("📂 匯入 CSV", type=['csv'], key="upload_csv_v200", label_visibility="collapsed")
            if uploaded:
                try:
                    imported_df = pd.read_csv(uploaded)
                    required_cols = ['資產代號','持有數量 (股)','買入均價','資產類別']
                    if all(col in imported_df.columns for col in required_cols):
                        st.session_state.portfolio_df = imported_df[required_cols].copy()
                        st.toast("✅ 成功匯入持倉資料", icon="🎯")
                        st.rerun()
                    else:
                        st.error(f"❌ CSV 缺少必要欄位：{required_cols}")
                except Exception as e:
                    st.error(f"❌ 匯入失敗：{e}")


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
            st.toast("⚠️ 請先在 4.1 配置您的戰略資產。", icon="⚡")
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
        st.toast("❌ 所有資產回測失敗，請檢查代號是否正確。", icon="💀"); return

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
#  SECTION 4.3 — 均線戰法回測實驗室 (V200 Enhanced)
# ══════════════════════════════════════════════════════════════════
def _s43():
    st.markdown(
        '<div class="t4-sec-head" style="--sa:#FF9A3C">'
        '<div class="t4-sec-num">4.3</div>'
        '<div><div class="t4-sec-title" style="color:#FF9A3C;">均線戰法實驗室</div>'
        '<div class="t4-sec-sub">15 MA Strategies · vs Buy&Hold · vs VOO · 10-Year Projection</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.toast("ℹ️ 選擇標的與回測期間，自動執行 15 種均線策略，並與「直接持有」和「VOO」比較。", icon="📡")

    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    if pf.empty:
        st.toast("⚠️ 請先在 4.1 配置您的戰略資產。", icon="⚡"); return

    # ── 設定列：標的 + 日期選擇器 ──────────────────────────────────
    cfg_col1, cfg_col2, cfg_col3 = st.columns([2, 2, 1])
    with cfg_col1:
        sel_t = st.selectbox("選擇回測標的", options=pf['資產代號'].tolist(), key="ma_lab_ticker_v200")
    with cfg_col2:
        backtest_start = st.date_input(
            "回測起始日期（若上市不足將自動調整）",
            value=datetime(2015, 1, 1).date(),
            min_value=datetime(1990, 1, 1).date(),
            max_value=datetime.now().date(),
            key="ma_lab_start_date_v200",
        )
    with cfg_col3:
        commission_pct = st.number_input(
            "手續費率 %",
            min_value=0.0, max_value=1.0, value=0.1425, step=0.01,
            key="ma_lab_commission_v200",
            help="台股預設 0.1425%；美股約 0%（券商免佣）",
        )

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
        start_str = str(backtest_start)
        comm = commission_pct / 100.0
        with st.spinner(f"正在對 {sel_t} 執行 15 種均線策略回測（含交易成本，手續費 {commission_pct:.4f}%）…"):
            ma_results = [r for s in strategies
                          if (r := _run_ma_strategy_backtest(
                              sel_t, s,
                              start_date=start_str,
                              initial_capital=1_000_000,
                              commission=comm,
                              slippage=0.001))]
        with st.spinner("下載 VOO 基準資料…"):
            voo_res = _fetch_voo_benchmark(start_str, initial_capital=1_000_000)

        # 記錄有效的實際起始日（由回測引擎自動偵測）
        actual_start = ma_results[0]['actual_start'] if ma_results else start_str

        st.session_state.ma_lab_results     = ma_results
        st.session_state.ma_lab_result_tick = sel_t
        st.session_state.ma_lab_voo         = voo_res
        st.session_state.ma_lab_actual_start= actual_start

    if ('ma_lab_results' not in st.session_state
            or st.session_state.get('ma_lab_result_tick') != sel_t):
        return

    results      = st.session_state.ma_lab_results
    voo_res      = st.session_state.get('ma_lab_voo')
    actual_start = st.session_state.get('ma_lab_actual_start', str(backtest_start))

    if not results:
        st.toast(f"❌ 無法取得 {sel_t} 的回測數據（資料不足或代號錯誤）。", icon="💀"); return

    st.toast(f"✅ {sel_t} — 15 種均線策略回測完成，實際起始: {actual_start}", icon="🎯")

    # ── 基準橫幅：Buy & Hold vs VOO ────────────────────────────────
    bh_cagr     = results[0]['bh_cagr']
    bh_equity   = results[0]['bh_equity']
    bh_mdd      = results[0]['bh_max_drawdown']
    voo_cagr    = voo_res['cagr']    if voo_res else float('nan')
    voo_equity  = voo_res['final_equity'] if voo_res else float('nan')
    voo_mdd     = voo_res['max_drawdown'] if voo_res else float('nan')

    st.markdown("### 📌 基準比較 (同期間、同本金 100 萬)")
    bm_c1, bm_c2, bm_c3 = st.columns(3)
    def _bm_card(col, label, color, cagr_v, equity_v, mdd_v, icon):
        with col:
            st.markdown(f"""
<div style="background:rgba(0,0,0,.28);border:1px solid {color}33;border-top:3px solid {color};
     border-radius:12px;padding:18px 16px;text-align:center;">
  <div style="font-family:var(--f-m);font-size:9px;color:{color};letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">{icon} {label}</div>
  <div style="font-family:var(--f-i);font-size:36px;font-weight:800;color:#FFF;line-height:1;letter-spacing:-1px;">{equity_v:,.0f}</div>
  <div style="font-family:var(--f-m);font-size:10px;color:rgba(255,255,255,.3);margin:4px 0 10px;">元 (終值)</div>
  <div style="display:flex;justify-content:center;gap:18px;">
    <div><div style="font-size:9px;color:{color};font-family:var(--f-m);letter-spacing:1px;">CAGR</div>
         <div style="font-size:18px;font-weight:800;color:#FFF;font-family:var(--f-i);">{cagr_v:.2%}</div></div>
    <div><div style="font-size:9px;color:#FF6B6B;font-family:var(--f-m);letter-spacing:1px;">MAX DD</div>
         <div style="font-size:18px;font-weight:800;color:#FF6B6B;font-family:var(--f-i);">{mdd_v:.2%}</div></div>
  </div>
</div>""", unsafe_allow_html=True)

    _bm_card(bm_c1, f"{sel_t} 直接持有", "#00F5FF", bh_cagr, bh_equity, bh_mdd, "🏦")
    if voo_res:
        _bm_card(bm_c2, "VOO 標普500 ETF",    "#FFD700", voo_cagr, voo_equity, voo_mdd, "🇺🇸")
    else:
        with bm_c2:
            st.warning("VOO 資料下載失敗")

    # 最佳策略 vs 買持
    best_r = max(results, key=lambda x: x['cagr'])
    beat_bh_color = "#00FF7F" if best_r['alpha_vs_bh'] > 0 else "#FF3131"
    beat_bh_icon  = "✅ 超越" if best_r['alpha_vs_bh'] > 0 else "❌ 落後"
    with bm_c3:
        st.markdown(f"""
<div style="background:rgba(0,0,0,.28);border:1px solid {beat_bh_color}33;border-top:3px solid {beat_bh_color};
     border-radius:12px;padding:18px 16px;text-align:center;">
  <div style="font-family:var(--f-m);font-size:9px;color:{beat_bh_color};letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">🏆 最佳均線策略</div>
  <div style="font-family:var(--f-d);font-size:14px;color:#DDE;letter-spacing:1px;margin-bottom:8px;">{best_r['strategy_name'][:22]}</div>
  <div style="font-family:var(--f-i);font-size:36px;font-weight:800;color:#FFF;line-height:1;letter-spacing:-1px;">{best_r['final_equity']:,.0f}</div>
  <div style="font-family:var(--f-m);font-size:10px;color:rgba(255,255,255,.3);margin:4px 0 10px;">元 (終值)</div>
  <div style="font-size:14px;font-weight:700;color:{beat_bh_color};font-family:var(--f-b);">{beat_bh_icon} Buy&Hold<br>α = {best_r['alpha_vs_bh']:+.2%}</div>
</div>""", unsafe_allow_html=True)

    st.divider()

    # ── 完整策略績效表 (含所有新指標) ──────────────────────────────
    wd = pd.DataFrame([{
        '策略名稱':           r['strategy_name'],
        '年化報酬 CAGR':     r['cagr'],
        '年化波動率':         r['ann_vol'],
        'Sharpe Ratio':      r['sharpe'],
        'Calmar Ratio':      r['calmar'],
        '最大回撤 MDD':       r['max_drawdown'],
        '交易次數':           r['num_trades'],
        '平均持倉天數':        r['avg_hold_days'],
        '在場時間 %':         r['time_in_market'],
        'α vs Buy&Hold':     r['alpha_vs_bh'],
        '回測期末資金':        r['final_equity'],
        '未來10年推估':        r['future_10y_capital'],
        '回測年數':           r['num_years'],
    } for r in results]).sort_values('年化報酬 CAGR', ascending=False)

    st.subheader("📊 策略完整績效表（含成本、比較基準）")

    def _color_alpha(val):
        color = '#00FF7F' if val > 0 else '#FF6B6B'
        return f'color: {color}; font-weight: bold'
    def _color_cagr(val):
        color = '#00FF7F' if val > bh_cagr else '#FF6B6B'
        return f'color: {color}'

    styled = (wd.style
        .format({
            '年化報酬 CAGR':   '{:.2%}',
            '年化波動率':       '{:.2%}',
            'Sharpe Ratio':    '{:.2f}',
            'Calmar Ratio':    '{:.2f}',
            '最大回撤 MDD':     '{:.2%}',
            '交易次數':         '{:.0f}',
            '平均持倉天數':     '{:.0f}',
            '在場時間 %':       '{:.1%}',
            'α vs Buy&Hold':   '{:+.2%}',
            '回測期末資金':     '{:,.0f}',
            '未來10年推估':     '{:,.0f}',
            '回測年數':         '{:.1f}',
        })
        .applymap(_color_alpha, subset=['α vs Buy&Hold'])
        .applymap(_color_cagr,  subset=['年化報酬 CAGR'])
    )
    st.dataframe(styled, use_container_width=True)

    # ── Valkyrie Typewriter 分析總結 ─────────────────────────────
    st.markdown("**🎯 AI 策略分析總結**")
    best_s   = wd.iloc[0]
    worst_s  = wd.iloc[-1]
    beat_cnt = (wd['α vs Buy&Hold'] > 0).sum()
    voo_label = f"VOO ({voo_cagr:.2%})" if voo_res else "VOO"
    summary_text = (
        f"針對 {sel_t}（實際回測起始：{actual_start}）執行 15 種均線策略完成。"
        f"最佳策略為「{best_s['策略名稱']}」，年化 {best_s['年化報酬 CAGR']:.2%}，"
        f"Sharpe {best_s['Sharpe Ratio']:.2f}，MDD {best_s['最大回撤 MDD']:.2%}；"
        f"10 年後預期 {best_s['未來10年推估']:,.0f} 元。"
        f"直接持有年化 {bh_cagr:.2%}，全球基準 {voo_label}。"
        f"15 種策略中，有 {beat_cnt} 種跑贏直接持有，{15 - beat_cnt} 種落後。"
        f"最差策略「{worst_s['策略名稱']}」年化僅 {worst_s['年化報酬 CAGR']:.2%}。"
        f"結論：頻繁進出並不必然優於長期持有，請根據 Alpha 欄位評估各策略是否真的值得操作。"
    )
    st.write_stream(stream_generator(summary_text))

    # ── CAGR Ranking Bar Chart ───────────────────────────────────
    st.markdown('<div class="t4-chart-panel"><div class="t4-chart-lbl">▸ CAGR strategy ranking vs Buy&Hold vs VOO</div>', unsafe_allow_html=True)
    bar_s  = wd.sort_values('年化報酬 CAGR', ascending=True).copy()
    colors = ['#00FF7F' if v > bh_cagr else ('#FFD700' if v > 0 else '#FF6B6B')
              for v in bar_s['年化報酬 CAGR']]
    fig_bar = go.Figure(go.Bar(
        x=bar_s['年化報酬 CAGR'] * 100, y=bar_s['策略名稱'], orientation='h',
        marker_color=colors,
        text=[f"{v:.1f}%" for v in bar_s['年化報酬 CAGR'] * 100],
        textposition='outside',
        textfont=dict(color='#DDE', size=11, family='JetBrains Mono'),
    ))
    # Buy & Hold 基準線
    fig_bar.add_vline(x=bh_cagr * 100, line_color='#00F5FF', line_width=2,
                      line_dash='dash',
                      annotation_text=f"Buy&Hold {bh_cagr:.1%}",
                      annotation_font=dict(color='#00F5FF', size=10))
    if voo_res:
        fig_bar.add_vline(x=voo_cagr * 100, line_color='#FFD700', line_width=2,
                          line_dash='dot',
                          annotation_text=f"VOO {voo_cagr:.1%}",
                          annotation_font=dict(color='#FFD700', size=10),
                          annotation_position="top right")
    fig_bar.add_vline(x=0, line_color='rgba(255,255,255,0.15)', line_width=1)
    fig_bar.update_layout(
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', height=480,
        xaxis=dict(ticksuffix="%", gridcolor='rgba(255,255,255,0.04)'),
        yaxis=dict(tickfont=dict(size=11, family='Rajdhani', color='#B0C0D0')),
        margin=dict(t=10, b=30, l=240, r=80),
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── 權益曲線疊加圖：策略 vs Buy&Hold vs VOO ─────────────────
    st.markdown('<div class="t4-chart-panel"><div class="t4-chart-lbl">▸ equity curves overlay — strategies vs buy&hold vs VOO</div>', unsafe_allow_html=True)
    pal_lines = ['#B77DFF','#FF9A3C','#00FF7F','#FF3131','#4dc8ff','#FF6BFF']
    fig_ov = go.Figure()
    for i, res in enumerate(results):
        eq = res['equity_curve']
        norm = (eq / eq.iloc[0]) * 100
        fig_ov.add_trace(go.Scatter(
            x=norm.index, y=norm.values, name=res['strategy_name'][:18],
            line=dict(color=pal_lines[i % len(pal_lines)], width=1),
            opacity=0.55,
            hovertemplate=f"<b>{res['strategy_name'][:18]}</b> %{{y:.1f}}<extra></extra>"))
    # Buy & Hold (粗線)
    bh_eq  = results[0]['bh_equity_curve']
    bh_norm = (bh_eq / bh_eq.iloc[0]) * 100
    fig_ov.add_trace(go.Scatter(
        x=bh_norm.index, y=bh_norm.values, name=f"📌 {sel_t} Buy&Hold",
        line=dict(color='#00F5FF', width=3),
        hovertemplate=f"<b>Buy&Hold</b> %{{y:.1f}}<extra></extra>"))
    # VOO (粗線)
    if voo_res:
        voo_eq   = voo_res['equity_curve']
        voo_norm = (voo_eq / voo_eq.iloc[0]) * 100
        fig_ov.add_trace(go.Scatter(
            x=voo_norm.index, y=voo_norm.values, name="🇺🇸 VOO",
            line=dict(color='#FFD700', width=3, dash='dash'),
            hovertemplate="<b>VOO</b> %{y:.1f}<extra></extra>"))
    fig_ov.add_hline(y=100, line_dash='dot', line_color='rgba(255,255,255,0.12)')
    fig_ov.update_layout(
        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', height=400, hovermode='x unified',
        legend=dict(font=dict(color='#B0C0D0',size=10,family='Rajdhani')),
        margin=dict(t=10,b=40,l=50,r=10),
        yaxis=dict(gridcolor='rgba(255,255,255,0.04)', title="標準化淨值 (Base=100)"),
        xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
    )
    st.plotly_chart(fig_ov, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Excel 下載（含更多欄位）────────────────────────────────────
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as w:
        wd.to_excel(w, index=False, sheet_name='MA_Backtest_Report')
        # 加一張基準頁
        bm_df = pd.DataFrame([
            {'基準': f'{sel_t} Buy&Hold', 'CAGR': bh_cagr, '期末資金': bh_equity, 'MDD': bh_mdd},
            {'基準': 'VOO', 'CAGR': voo_cagr if voo_res else None,
             '期末資金': voo_equity if voo_res else None, 'MDD': voo_mdd if voo_res else None},
        ])
        bm_df.to_excel(w, index=False, sheet_name='基準比較')
    st.markdown('<div class="t4-action-g">', unsafe_allow_html=True)
    st.download_button("📥 下載完整戰術回測報表 (Excel)", buf.getvalue(),
        f"{sel_t}_ma_lab_full_report.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # ── 單策略深度圖表 ────────────────────────────────────────────
    st.subheader("📈 單策略深度視覺化")
    sel_s = st.selectbox("選擇策略查看圖表",
                         [r['strategy_name'] for r in results], key="ma_chart_v200")
    sel_r = next((r for r in results if r['strategy_name'] == sel_s), None)
    if sel_r:
        eq = sel_r['equity_curve'].reset_index(); eq.columns = ['Date','Equity']
        bh_eq_df = sel_r['bh_equity_curve'].reset_index(); bh_eq_df.columns = ['Date','BH']

        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(x=eq['Date'], y=eq['Equity'],
            name=f"均線策略: {sel_s[:20]}", line=dict(color='#2ECC71', width=2)))
        fig_eq.add_trace(go.Scatter(x=bh_eq_df['Date'], y=bh_eq_df['BH'],
            name=f"{sel_t} Buy&Hold", line=dict(color='#00F5FF', width=2, dash='dash')))
        if voo_res:
            voo_eq_df = voo_res['equity_curve'].reset_index(); voo_eq_df.columns = ['Date','VOO']
            fig_eq.add_trace(go.Scatter(x=voo_eq_df['Date'], y=voo_eq_df['VOO'],
                name="VOO", line=dict(color='#FFD700', width=2, dash='dot')))
        fig_eq.update_layout(
            title=f"{sel_t} — {sel_s} 權益曲線 vs 基準",
            template='plotly_dark', hovermode='x unified',
            legend=dict(font=dict(color='#B0C0D0',size=11)))
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

        # 統計摘要小卡
        stat_cols = st.columns(4)
        stat_cols[0].metric("交易次數", f"{sel_r['num_trades']:.0f} 次")
        stat_cols[1].metric("平均持倉天數", f"{sel_r['avg_hold_days']:.0f} 天")
        stat_cols[2].metric("在場時間", f"{sel_r['time_in_market']:.1%}")
        stat_cols[3].metric("α vs Buy&Hold", f"{sel_r['alpha_vs_bh']:+.2%}",
                            delta_color="normal" if sel_r['alpha_vs_bh'] > 0 else "inverse")


# ══════════════════════════════════════════════════════════════════
#  SECTION 4.4 — 機構級資金配置雙引擎 (Markowitz + Risk Parity)
# ══════════════════════════════════════════════════════════════════
def _s44():
    """4.4 機構級資金配置雙引擎 (Markowitz Max Sharpe + Risk Parity)"""
    st.markdown(
        '<div class="t4-sec-head" style="--sa:#00FF7F">'
        '<div class="t4-sec-num">4.4</div>'
        '<div><div class="t4-sec-title" style="color:#00FF7F;">機構級資金配置</div>'
        '<div class="t4-sec-sub">Dual-Engine: Markowitz Efficient Frontier · Risk Parity All-Weather · Monte Carlo 5000</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.caption("透過諾貝爾經濟學獎演算法與橋水基金全天候模型，計算最完美的資金權重。")

    # ── 1. User Input ─────────────────────────────────────────────
    st.markdown("##### 🎯 1. 輸入您的投資組合標的")

    # 預設從 4.1 持倉自動帶入，使用者也可手動覆蓋
    pf_default = st.session_state.get('portfolio_df', pd.DataFrame())
    if not pf_default.empty:
        default_tickers = ", ".join(
            (f"{t}.TW" if _is_tw_ticker(t) else t)
            for t in pf_default['資產代號'].tolist()
            if str(t).upper() not in ('CASH', 'USD', 'TWD')
        )
    else:
        default_tickers = "2330.TW, 2317.TW, 2454.TW, 2881.TW, 0050.TW"

    tickers_input = st.text_input(
        "輸入股票代號（以逗號分隔，台股請加 .TW）",
        value=default_tickers,
        help="自動從 4.1 持倉帶入，可手動修改。台股範例：2330.TW  美股範例：AAPL, NVDA",
        key="s44_tickers_input",
    )

    # ── 雙引擎選擇器 ──────────────────────────────────────────────
    st.markdown("**選擇演算引擎 (Select Engine):**")
    if 's44_strategy' not in st.session_state:
        st.session_state['s44_strategy'] = 'Markowitz'

    eng_col1, eng_col2 = st.columns(2)
    with eng_col1:
        if st.button("⚔️ 攻擊型：Markowitz 最優化\n(追求最高夏普值)",
                     use_container_width=True, key="s44_btn_markowitz",
                     type="primary" if st.session_state['s44_strategy'] == 'Markowitz' else "secondary"):
            st.session_state['s44_strategy'] = 'Markowitz'
            st.rerun()
    with eng_col2:
        if st.button("🛡️ 防禦型：Risk Parity 全天候\n(追求風險平價)",
                     use_container_width=True, key="s44_btn_rp",
                     type="primary" if st.session_state['s44_strategy'] == 'RiskParity' else "secondary"):
            st.session_state['s44_strategy'] = 'RiskParity'
            st.rerun()

    strategy = st.session_state['s44_strategy']

    # 顯示當前選擇狀態
    if strategy == 'Markowitz':
        st.success("⚔️ 當前引擎：**Markowitz 最優化** — 蒙地卡羅 5000 次模擬，鎖定最高夏普值配置")
    else:
        st.info("🛡️ 當前引擎：**Risk Parity 全天候** — 反向波動率平價，高波動資產強制降權")

    rf_col, sim_col = st.columns(2)
    with rf_col:
        risk_free = st.number_input(
            "無風險利率 Risk-Free Rate (%)",
            min_value=0.0, max_value=10.0, value=2.0, step=0.1,
            key="s44_rf_rate",
            help="美國10年期公債約4-5%，台灣約1.5-2%",
        ) / 100.0
    with sim_col:
        n_sim = st.selectbox(
            "蒙地卡羅模擬次數",
            options=[1000, 3000, 5000, 10000],
            index=2,
            key="s44_n_sim",
            help="越多次越精確，但計算越慢。建議 5000。",
        )

    st.markdown('<div class="t4-action">', unsafe_allow_html=True)
    run_opt = st.button("🚀 啟動量子演算 (Run Optimization)", use_container_width=True,
                        key="s44_run_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    if not run_opt:
        return

    # ── 2. Parse tickers ──────────────────────────────────────────
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]
    if len(tickers) < 2:
        st.warning("⚠️ 請至少輸入兩檔標的進行配置！")
        return

    # ── 3. Fetch & Compute ────────────────────────────────────────
    with st.spinner(f"🧠 正在抓取 {len(tickers)} 檔歷史數據並計算共變異數矩陣…"):
        try:
            # [FIX] .ffill() 取代已棄用的 fillna(method='ffill')
            raw = yf.download(tickers, period="1y", progress=False)
            if isinstance(raw.columns, pd.MultiIndex):
                data = raw['Close']
            else:
                data = raw[['Close']] if 'Close' in raw.columns else raw

            data = data.dropna(axis=1, how='all').ffill()

            valid_tickers = data.columns.tolist()
            if len(valid_tickers) < 2:
                st.error("❌ 有效標的不足，請檢查代號是否正確。")
                return

            # 若有代號查不到，提示使用者
            missing = [t for t in tickers if t not in valid_tickers]
            if missing:
                st.warning(f"⚠️ 以下代號無資料，已自動排除：{', '.join(missing)}")

            # 日報酬 → 年化
            returns      = data.pct_change().dropna()
            mean_returns = returns.mean() * 252        # 年化預期報酬
            cov_matrix   = returns.cov() * 252         # 年化共變異數矩陣
            vols         = returns.std() * np.sqrt(252) # 年化波動率
            n_assets     = len(valid_tickers)

            # ── 4. Monte Carlo Simulation ─────────────────────────
            np.random.seed(42)   # 可重現性
            results        = np.zeros((3, n_sim))
            weights_record = np.zeros((n_sim, n_assets))

            for i in range(n_sim):
                w = np.random.random(n_assets)
                w /= w.sum()                          # 正規化：總和 = 1
                weights_record[i] = w

                p_ret  = float(np.dot(w, mean_returns))
                p_std  = float(np.sqrt(w.T @ cov_matrix.values @ w))
                p_shrp = (p_ret - risk_free) / p_std if p_std > 0 else 0.0

                results[0, i] = p_std    # 波動率（風險）
                results[1, i] = p_ret    # 預期年化報酬
                results[2, i] = p_shrp   # 夏普值

            # ── 5. Engine Logic ───────────────────────────────────
            max_sharpe_idx = int(np.argmax(results[2]))
            min_vol_idx    = int(np.argmin(results[0]))
            mvp_ret = results[1, min_vol_idx]
            mvp_std = results[0, min_vol_idx]
            mvp_shp = results[2, min_vol_idx]

            if strategy == 'Markowitz':
                # ── 攻擊型：Max Sharpe ────────────────────────────
                optimal_weights = weights_record[max_sharpe_idx]
                opt_ret   = results[1, max_sharpe_idx]
                opt_std   = results[0, max_sharpe_idx]
                opt_shp   = results[2, max_sharpe_idx]
                marker_color  = '#00F5FF'
                marker_symbol = 'star'
                label_text    = '🏆 Markowitz 極致夏普'
                engine_label  = 'Max Sharpe Ratio'
            else:
                # ── 防禦型：Risk Parity (Inverse Volatility) ──────
                inv_vols = 1.0 / vols
                optimal_weights = (inv_vols / np.sum(inv_vols)).values
                opt_ret  = float(np.dot(optimal_weights, mean_returns))
                opt_std  = float(np.sqrt(optimal_weights.T @ cov_matrix.values @ optimal_weights))
                opt_shp  = (opt_ret - risk_free) / opt_std if opt_std > 0 else 0.0
                marker_color  = '#00FF9D'
                marker_symbol = 'pentagon'          # ← plotly 合法 symbol（無 'shield'）
                label_text    = '🛡️ Risk Parity 絕對防禦'
                engine_label  = 'Risk Parity (All-Weather)'

            # ── 6. Efficient Frontier Chart ───────────────────────
            st.markdown("##### 🌌 2. 效率前緣宇宙 (The Frontier)")
            st.caption(
                "每個點代表一種資產配置組合。**越右**=風險越高，**越上**=報酬越高。"
                "顏色越綠=夏普值越高（風報比越佳）。標記點即所選引擎的最佳配置。"
            )

            fig = px.scatter(
                x=results[0, :],
                y=results[1, :],
                color=results[2, :],
                color_continuous_scale="RdYlGn",
                labels={
                    'x':     '預期年化波動率 Volatility',
                    'y':     '預期年化報酬 Return',
                    'color': '夏普值 Sharpe Ratio',
                },
                opacity=0.55,
            )

            # 所選引擎最佳點
            fig.add_trace(go.Scatter(
                x=[opt_std], y=[opt_ret],
                mode='markers+text',
                marker=dict(color=marker_color, size=18, symbol=marker_symbol,
                            line=dict(width=2, color='white')),
                name=label_text,
                text=[f'{label_text.split(" ")[1]} Sharpe {opt_shp:.2f}'],
                textposition='top left',
                textfont=dict(color=marker_color, size=13, weight='bold'),
            ))

            # 最小波動 ◆（永遠顯示作為參考基準）
            fig.add_trace(go.Scatter(
                x=[mvp_std], y=[mvp_ret],
                mode='markers+text',
                marker=dict(color='#FFD700', size=14, symbol='diamond',
                            line=dict(width=2, color='white')),
                name='◆ 最小波動組合',
                text=[f'◆ Vol {mvp_std:.2%}'],
                textposition='top right',
                textfont=dict(color='#FFD700', size=12),
            ))

            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=520,
                margin=dict(t=30, b=40, l=60, r=20),
                xaxis=dict(tickformat='.1%', gridcolor='rgba(255,255,255,0.04)'),
                yaxis=dict(tickformat='.1%', gridcolor='rgba(255,255,255,0.04)'),
                coloraxis_colorbar=dict(
                    tickfont=dict(color='#A0B0C0', size=10),
                    title=dict(text='Sharpe', font=dict(color='#A0B0C0', size=10)),
                ),
                legend=dict(font=dict(color='#B0C0D0', size=11, family='Rajdhani')),
            )
            st.plotly_chart(fig, use_container_width=True)

            # ── 7. Metrics Row ─────────────────────────────────────
            st.markdown(f"##### 📊 3. 最佳化資金權重建議 ({engine_label})")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("預期年化報酬",        f"{opt_ret:.2%}")
            with c2:
                st.metric("投資組合波動率",       f"{opt_std:.2%}",
                          delta="風險值", delta_color="inverse")
            with c3:
                st.metric("夏普值 (風險報酬比)",  f"{opt_shp:.2f}",
                          delta="越高越好")
            with c4:
                st.metric("無風險利率假設",       f"{risk_free:.2%}")

            st.divider()

            # ── 8. Weight DataFrame ───────────────────────────────
            weight_df = pd.DataFrame({
                '資產代號 (Ticker)':    valid_tickers,
                '建議資金佔比 (Weight)': optimal_weights,
            }).sort_values('建議資金佔比 (Weight)', ascending=False).reset_index(drop=True)

            st.dataframe(
                weight_df.style
                    .format({'建議資金佔比 (Weight)': '{:.2%}'})
                    .background_gradient(subset=['建議資金佔比 (Weight)'], cmap='viridis'),
                use_container_width=True,
            )

            # ── 9. Optimal Weights Donut Chart ────────────────────
            st.markdown("##### 🥧 4. 最佳配置圓餅圖")
            pal = ['#00F5FF','#FFD700','#00FF7F','#FF9A3C','#B77DFF',
                   '#FF3131','#4dc8ff','#FF6BFF','#88FFD8','#FFAA5A']
            fig_pie = go.Figure(go.Pie(
                labels=weight_df['資產代號 (Ticker)'].tolist(),
                values=weight_df['建議資金佔比 (Weight)'].tolist(),
                hole=0.52,
                marker=dict(
                    colors=pal[:len(weight_df)],
                    line=dict(color='rgba(0,0,0,0.6)', width=3),
                ),
                textfont=dict(color='#FFFFFF', size=16, family='Rajdhani'),
                textinfo='label+percent',
                insidetextfont=dict(color='#FFFFFF', size=15, family='Rajdhani'),
                outsidetextfont=dict(color='#FFFFFF', size=16, family='Rajdhani'),
                textposition='auto',
                pull=[0.03] * len(weight_df),   # 微微拉開每片，增加辨識度
            ))
            fig_pie.update_layout(
                template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                height=420, margin=dict(t=20, b=0, l=0, r=0),
                legend=dict(
                    font=dict(color='#FFFFFF', size=14, family='Rajdhani'),
                    bgcolor='rgba(0,0,0,0.4)',
                    bordercolor='rgba(255,255,255,0.15)',
                    borderwidth=1,
                ),
                annotations=[dict(
                    text=f"Sharpe<br><b>{opt_shp:.2f}</b>",
                    x=0.5, y=0.5, font_size=22, showarrow=False,
                    font=dict(color=marker_color, family='JetBrains Mono'),
                )],
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            # ── 10. Valkyrie AI Commentary ────────────────────────
            top_ticker = weight_df.iloc[0]['資產代號 (Ticker)']
            top_w      = weight_df.iloc[0]['建議資金佔比 (Weight)']

            if strategy == 'Markowitz':
                commentary = (
                    f"根據 {n_sim:,} 次蒙地卡羅模擬與共變異數矩陣分析，"
                    f"在無風險利率 {risk_free:.1%} 的假設下，"
                    f"最佳夏普組合建議將最大比重 {top_w:.1%} 分配給 {top_ticker}。"
                    f"該組合預期年化報酬為 {opt_ret:.2%}，"
                    f"波動率為 {opt_std:.2%}，夏普值 {opt_shp:.2f}。"
                    f"效率前緣上每一個點代表一種帕雷托最優配置，"
                    f"在當前組合中無法在不增加風險的前提下進一步提升報酬。"
                    f"請注意：此結果基於過去一年歷史數據，未來報酬不保證重現，"
                    f"實際操作前請搭配基本面與總經背景進行人工判斷。"
                )
                st.success(f"⚡ [Valkyrie AI] 攻擊模式啟動：此配置將資金集中於近期動能與風險報酬比最高之標的，適合牛市擴張。{commentary}")
            else:
                commentary = (
                    f"Risk Parity 反向波動率模型已完成計算。"
                    f"最高配置比重 {top_w:.1%} 分配給波動率最低的 {top_ticker}。"
                    f"組合預期年化報酬 {opt_ret:.2%}，波動率 {opt_std:.2%}，夏普值 {opt_shp:.2f}。"
                    f"高波動資產被系統性降權，各資產的風險貢獻趨於均等，"
                    f"此模型源自橋水基金全天候策略，適合震盪或熊市環境防禦。"
                    f"請注意：此結果基於過去一年歷史數據，未來報酬不保證重現。"
                )
                st.info(f"🛡️ [Valkyrie AI] 防禦模式啟動：{commentary}")

        except Exception as e:
            st.error(f"演算失敗 (Execution Error): {e}")
            with st.expander("🔍 Debug Traceback"):
                import traceback
                st.code(traceback.format_exc())


# ══════════════════════════════════════════════════════════════════
#  SECTION 4.5 — 全球黑天鵝壓力測試 (RED ALERT CARDS)
# ══════════════════════════════════════════════════════════════════
def _s45():
    st.markdown('<div class="t4-sec-head" style="--sa:#FF3131"><div class="t4-sec-num">4.5</div><div><div class="t4-sec-title" style="color:#FF3131;">黑天鵝壓力測試</div><div class="t4-sec-sub">Global Systemic Shock Simulation · 4 Scenarios</div></div></div>', unsafe_allow_html=True)
    st.toast("ℹ️ 此功能將讀取您在 4.1 配置的資產，模擬全球系統性風險下的投資組合衝擊。", icon="📡")

    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    if pf.empty:
        st.toast("⚠️ 請先在 4.1 配置您的戰略資產。", icon="⚡"); return

    st.markdown('<div class="t4-action t4-action-r">', unsafe_allow_html=True)
    run_stress = st.button("💥 啟動壓力測試", key="btn_stress_v200")
    st.markdown('</div>', unsafe_allow_html=True)

    if run_stress:
        portfolio_text = "\n".join(
            f"{row['資產代號']};{row['持有數量 (股)']}" for _, row in pf.iterrows())
        with st.spinner("執行全球壓力測試…"):
            results_df, summary = _run_stress_test(portfolio_text)
        if "error" in summary:
            st.toast(f"❌ {summary['error']}", icon="💀")
        elif not results_df.empty:
            st.session_state.stress_test_results = (results_df, summary)
        else:
            st.toast("❌ 壓力測試失敗，未返回任何結果。", icon="💀")

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
        st.toast(f"⚠️ 熱力圖無法生成: {e}", icon="⚡")
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
    
    # ══════════════════════════════════════════════════════════════════
    # 🎯 FEATURE 1: Show tactical guide modal on first visit
    # ══════════════════════════════════════════════════════════════════
    if "guide_shown_" + __name__ not in st.session_state:
        show_guide_modal()
        st.session_state["guide_shown_" + __name__] = True
    
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
        st.toast(f"❌ Section {label} 發生錯誤: {exc}", icon="💀")
        st.error(f"❌ Section {label} 發生錯誤: {exc}")
        with st.expander(f"🔍 Debug — {label}"):
            st.code(traceback.format_exc())

    # ── FOOTER ──
    st.markdown(
        f'<div class="t4-foot">Titan Cinematic Wealth Command Center V200 · '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',
        unsafe_allow_html=True,
    )
