# ui_desktop/tab4_decision.py
# Titan SOP V100.0 — Tab 4: 全球決策
# [靈魂注入 V82.0 → V100.0 完整版]
# 所有 backtest 函式已內建（不依賴外部 backtest 模組）

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf
import re
import io
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
#  內建回測引擎函式 (從 V82 移植)
# ═══════════════════════════════════════════════════════════════

@st.cache_data(ttl=600)
def _run_fast_backtest(ticker, start_date="2023-01-01", initial_capital=1_000_000):
    """極速向量化回測引擎 (V78.3)"""
    try:
        if ticker.upper() in ['CASH', 'USD', 'TWD']:
            dates = yf.download('^TWII', start=start_date, progress=False).index
            if dates.empty: return None
            df = pd.DataFrame(index=dates)
            df['Equity'] = initial_capital; df['Drawdown'] = 0.0
            return {"cagr": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0,
                    "win_rate": 0.0, "profit_factor": 0.0, "kelly": 0.0,
                    "equity_curve": df['Equity'], "drawdown_series": df['Drawdown'], "latest_price": 1.0}

        original_ticker = ticker
        if re.match(r'^[0-9]', ticker) and 4 <= len(ticker) <= 6:
            ticker = f"{ticker}.TW"
        df = yf.download(ticker, start=start_date, progress=False)
        if df.empty and re.match(r'^[0-9]', original_ticker) and 4 <= len(original_ticker) <= 6:
            df = yf.download(f"{original_ticker}.TWO", start=start_date, progress=False)
        if df.empty or len(df) < 21: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

        df['MA20'] = df['Close'].rolling(20).mean()
        df['Signal'] = (df['Close'] > df['MA20']).astype(int)
        df['Pct_Change'] = df['Close'].pct_change()
        df['Strategy_Return'] = df['Signal'].shift(1) * df['Pct_Change']
        df['Equity'] = (1 + df['Strategy_Return'].fillna(0)).cumprod() * initial_capital
        df['Drawdown'] = (df['Equity'] / df['Equity'].cummax()) - 1

        trade_days = df[df['Signal'].shift(1) == 1]
        if len(trade_days) >= 10:
            wins = trade_days[trade_days['Strategy_Return'] > 0]['Strategy_Return']
            losses = trade_days[trade_days['Strategy_Return'] < 0]['Strategy_Return']
            win_rate = len(wins) / len(trade_days)
            avg_win = wins.mean() if len(wins) > 0 else 0
            avg_loss = abs(losses.mean()) if len(losses) > 0 else 1
            pf = avg_win / avg_loss if avg_loss != 0 else 0
            kelly = max(0, win_rate - ((1 - win_rate) / pf)) if pf > 0 else 0
        else:
            win_rate = pf = kelly = 0

        num_years = len(df) / 252
        total_return = df['Equity'].iloc[-1] / initial_capital - 1
        cagr = ((1 + total_return) ** (1 / num_years)) - 1 if num_years > 0 else 0
        daily_ret = df['Strategy_Return'].dropna()
        sharpe = (daily_ret.mean() * 252 - 0.02) / (daily_ret.std() * np.sqrt(252)) if daily_ret.std() > 0 else 0

        return {"cagr": cagr, "sharpe_ratio": sharpe, "max_drawdown": df['Drawdown'].min(),
                "win_rate": win_rate, "profit_factor": pf, "kelly": kelly,
                "equity_curve": df['Equity'], "drawdown_series": df['Drawdown'],
                "latest_price": float(df['Close'].iloc[-1])}
    except Exception:
        return None


@st.cache_data(ttl=7200)
def _run_ma_strategy_backtest(ticker, strategy_name, start_date="2015-01-01", initial_capital=1_000_000):
    """15 種均線策略回測引擎"""
    try:
        original_ticker = ticker
        if re.match(r'^[0-9]', ticker) and 4 <= len(ticker) <= 6:
            ticker = f"{ticker}.TW"
        df = yf.download(ticker, start=start_date, progress=False)
        if df.empty and re.match(r'^[0-9]', original_ticker):
            df = yf.download(f"{original_ticker}.TWO", start=start_date, progress=False)
        if df.empty or len(df) < 300: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)

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
        elif sn == "🔥 核心戰法: 87MA ↗ 284MA": df.loc[df['MA87'] > df['MA284'], 'Signal'] = 1
        elif sn == "非對稱: P>20進 / P<60出":
            pos = False
            for i in range(1, len(df)):
                if not pos and df['Close'].iloc[i] > df['MA20'].iloc[i]: pos = True
                elif pos and df['Close'].iloc[i] < df['MA60'].iloc[i]: pos = False
                df.iloc[i, df.columns.get_loc('Signal')] = 1 if pos else 0
        elif sn == "雙確認: P>20 & P>60 進 / P<60 出":
            pos = False
            for i in range(1, len(df)):
                if not pos and df['Close'].iloc[i] > df['MA20'].iloc[i] and df['Close'].iloc[i] > df['MA60'].iloc[i]: pos = True
                elif pos and df['Close'].iloc[i] < df['MA60'].iloc[i]: pos = False
                df.iloc[i, df.columns.get_loc('Signal')] = 1 if pos else 0

        df['Pct_Change'] = df['Close'].pct_change()
        df['Strategy_Return'] = df['Signal'].shift(1) * df['Pct_Change']
        df['Equity'] = (1 + df['Strategy_Return'].fillna(0)).cumprod() * initial_capital
        df['Drawdown'] = (df['Equity'] / df['Equity'].cummax()) - 1

        num_years = len(df) / 252
        total_return = df['Equity'].iloc[-1] / initial_capital - 1
        cagr = ((1 + total_return) ** (1 / num_years)) - 1 if num_years > 0 else 0

        return {"strategy_name": strategy_name, "cagr": cagr,
                "final_equity": df['Equity'].iloc[-1],
                "max_drawdown": df['Drawdown'].min(),
                "future_10y_capital": initial_capital * ((1 + cagr) ** 10),
                "num_years": num_years,
                "equity_curve": df['Equity'], "drawdown_series": df['Drawdown']}
    except Exception:
        return None


@st.cache_data(ttl=7200)
def _run_stress_test(portfolio_text):
    """全球黑天鵝壓力測試 (V82.1)"""
    lines = [l.strip() for l in portfolio_text.split('\n') if l.strip()]
    portfolio = []
    for item in lines:
        parts = [p.strip() for p in item.split(';')]
        if len(parts) == 2:
            try: portfolio.append({'ticker': parts[0].upper(), 'shares': float(parts[1])})
            except: pass
    if not portfolio: return pd.DataFrame(), {}

    try:
        bench = yf.download(['USDTWD=X'], period="1mo", progress=False)
        if isinstance(bench.columns, pd.MultiIndex): bench.columns = bench.columns.get_level_values(0)
        twd_fx = float(bench['Close'].iloc[-1]) if not bench.empty else 32.0
    except: twd_fx = 32.0

    results = []
    scenarios = {'回檔 (-5%)': -0.05, '修正 (-10%)': -0.10, '技術熊市 (-20%)': -0.20, '金融海嘯 (-30%)': -0.30}
    for asset in portfolio:
        orig = asset['ticker']; shares = asset['shares']
        if orig in ['CASH','USD','TWD']:
            r = {'ticker': orig, 'type': 'Cash', 'shares': shares, 'price': 1.0, 'value_twd': shares}
            for k in scenarios: r[f'損益_{k}'] = 0
            results.append(r); continue
        ticker = orig
        is_tw = re.match(r'^[0-9]', orig) and 4 <= len(orig) <= 6
        if is_tw: ticker = f"{orig}.TW"
        try:
            data = yf.download(ticker, period="1mo", progress=False)
            if data.empty and is_tw:
                data = yf.download(f"{orig}.TWO", period="1mo", progress=False)
            if data.empty: continue
            if isinstance(data.columns, pd.MultiIndex): data.columns = data.columns.get_level_values(0)
            price = float(data['Close'].iloc[-1])
            value = price * shares * (1 if is_tw else twd_fx)
            r = {'ticker': orig, 'type': 'TW' if is_tw else 'US', 'shares': shares, 'price': price, 'value_twd': value}
            for k, shock in scenarios.items(): r[f'損益_{k}'] = value * shock
            results.append(r)
        except: continue

    if not results: return pd.DataFrame(), {"error": "無有效資產"}
    df = pd.DataFrame(results)
    return df, {'total_value': df['value_twd'].sum()}


# ═══════════════════════════════════════════════════════════════
#  預設投資組合
# ═══════════════════════════════════════════════════════════════
_DEFAULT_PORTFOLIO = pd.DataFrame([
    {'資產代號': '2330.TW',  '持有數量 (股)': 1000, '買入均價': 550.0,    '資產類別': 'Stock'},
    {'資產代號': 'NVDA',     '持有數量 (股)': 10,   '買入均價': 400.0,    '資產類別': 'US_Stock'},
    {'資產代號': 'CASH',     '持有數量 (股)': 1,    '買入均價': 500000.0, '資產類別': 'Cash'},
])

def _ensure_portfolio():
    if 'portfolio_df' not in st.session_state:
        st.session_state.portfolio_df = _DEFAULT_PORTFOLIO.copy()


# ═══════════════════════════════════════════════════════════════
#  主渲染入口
# ═══════════════════════════════════════════════════════════════
def render():
    """Tab 4: 全球決策 — V82 靈魂完整版"""
    _ensure_portfolio()

    # ── 4.1 戰略資產配置 ─────────────────────────────────────────
    with st.expander("4.1 📋 戰略資產配置 (Strategic Asset Allocation)", expanded=True):
        st.info("💡 台股 1 張請輸入 1000；美股以 1 股為單位；現金請輸入總額。此處可直接編輯您的資產。")
        ptd = st.session_state.portfolio_df.copy()
        asset_tickers = ptd[ptd['資產類別'] != 'Cash']['資產代號'].tolist()
        lp = {}
        if asset_tickers:
            try:
                raw = yf.download(asset_tickers, period="1d", progress=False)['Close']
                if len(asset_tickers) == 1:
                    lp = {asset_tickers[0]: float(raw.iloc[-1])}
                else:
                    lp = raw.iloc[-1].to_dict()
            except:
                st.warning("⚠️ 無法獲取即時市價，計算欄位暫不顯示。")

        ptd['現價']       = ptd['資產代號'].map(lp).fillna(1.0)
        ptd['市值']       = ptd['持有數量 (股)'] * ptd['現價']
        ptd['未實現損益'] = (ptd['現價'] - ptd['買入均價']) * ptd['持有數量 (股)']

        ed = st.data_editor(
            ptd,
            column_config={
                "資產代號":      st.column_config.TextColumn("資產代號", help="台股/美股代號或CASH"),
                "持有數量 (股)": st.column_config.NumberColumn("持有數量 (股)", format="%d"),
                "買入均價":      st.column_config.NumberColumn("買入均價",      format="%.2f"),
                "資產類別":      st.column_config.SelectboxColumn("資產類別",
                                    options=['Stock','ETF','US_Stock','US_Bond','Cash']),
                "現價":          st.column_config.NumberColumn("現價",          format="%.2f",  disabled=True),
                "市值":          st.column_config.NumberColumn("市值",          format="%.0f",  disabled=True),
                "未實現損益":    st.column_config.NumberColumn("未實現損益",    format="%+,.0f",disabled=True),
            },
            num_rows="dynamic",
            key="portfolio_editor_v100_final",
            use_container_width=True
        )
        st.session_state.portfolio_df = ed[['資產代號','持有數量 (股)','買入均價','資產類別']]

    # ── 4.2 績效回測與凱利決策 ──────────────────────────────────
    with st.expander("4.2 📈 績效回測與凱利決策 (Backtest & Kelly Analysis)", expanded=False):
        if st.button("🚀 啟動全球回測", key="btn_backtest_v100"):
            pf = st.session_state.get('portfolio_df', pd.DataFrame())
            if pf.empty:
                st.warning("請先在 4.1 配置您的戰略資產。")
            else:
                with st.spinner("正在對全球資產執行回測…"):
                    res_list = []
                    for _, row in pf.iterrows():
                        r = _run_fast_backtest(str(row['資產代號']).strip())
                        if r:
                            r['Ticker'] = row['資產代號']
                            res_list.append(r)
                    st.session_state.backtest_results = res_list

        if 'backtest_results' in st.session_state:
            res_list = st.session_state.backtest_results
            if not res_list:
                st.error("所有資產回測失敗，請檢查代號是否正確。")
            else:
                summary = []
                for res in res_list:
                    kc = res.get('kelly', 0) * 0.5
                    if kc > 0.1:   advice = "🔥🔥 重注進攻"
                    elif kc >= 0.025: advice = "✅ 穩健配置"
                    else:            advice = "🧊 觀望或試單"
                    summary.append({
                        '代號': res['Ticker'],
                        '最新價': res.get('latest_price', 0),
                        '年化報酬 (CAGR)': res.get('cagr', 0),
                        '投資性價比 (Sharpe)': res.get('sharpe_ratio', 0),
                        '最大回撤': res.get('max_drawdown', 0),
                        '凱利建議 %': kc,
                        '建議動作': advice
                    })
                st.dataframe(pd.DataFrame(summary).style.format({
                    '最新價': '{:.2f}', '年化報酬 (CAGR)': '{:.2%}',
                    '投資性價比 (Sharpe)': '{:.2f}', '最大回撤': '{:.2%}', '凱利建議 %': '{:.2%}',
                }), use_container_width=True)
                st.divider()

                sel = st.selectbox("選擇要查看的資產", [r['Ticker'] for r in res_list])
                res = next((r for r in res_list if r['Ticker'] == sel), None)
                if res:
                    eq = res['equity_curve'].reset_index()
                    eq.columns = ['Date', 'Equity']
                    fig = px.line(eq, x='Date', y='Equity',
                                  title=f"{sel} 權益曲線 (Equity Curve)",
                                  labels={'Equity': '投資組合價值', 'Date': '日期'})
                    fig.update_traces(line_color='#17BECF')
                    fig.update_layout(template='plotly_dark')
                    st.plotly_chart(fig, use_container_width=True)

                    dd = res['drawdown_series'].reset_index()
                    dd.columns = ['Date', 'Drawdown']
                    dd['Drawdown_pct'] = dd['Drawdown'] * 100
                    fig2 = px.area(dd, x='Date', y='Drawdown_pct',
                                   title=f"{sel} 水下回撤圖 (Underwater Plot)",
                                   labels={'Drawdown_pct': '從高點回落 (%)', 'Date': '日期'})
                    fig2.update_traces(fillcolor='rgba(255,87,51,0.4)', line_color='rgba(255,87,51,1.0)')
                    fig2.update_yaxes(ticksuffix="%")
                    fig2.update_layout(template='plotly_dark')
                    st.plotly_chart(fig2, use_container_width=True)

    # ── 4.3 均線戰法回測實驗室 ──────────────────────────────────
    with st.expander("4.3 🧪 均線戰法回測實驗室 (MA Strategy Lab)", expanded=False):
        st.info("選擇一檔標的，自動執行 15 種均線策略回測，推演 10 年財富變化。")
        pf = st.session_state.get('portfolio_df', pd.DataFrame())
        if pf.empty:
            st.warning("請先在 4.1 配置您的戰略資產。")
        else:
            lab_t = st.selectbox("選擇回測標的", pf['資產代號'].tolist(), key="ma_lab_ticker")
            strategies = [
                "價格 > 20MA", "價格 > 43MA", "價格 > 60MA", "價格 > 87MA", "價格 > 284MA",
                "非對稱: P>20進 / P<60出", "20/60 黃金/死亡交叉", "20/87 黃金/死亡交叉",
                "20/284 黃金/死亡交叉", "43/87 黃金/死亡交叉", "43/284 黃金/死亡交叉",
                "60/87 黃金/死亡交叉", "60/284 黃金/死亡交叉", "🔥 核心戰法: 87MA ↗ 284MA",
                "雙確認: P>20 & P>60 進 / P<60 出"
            ]

            if st.button("🔬 啟動 15 種均線實驗", key="start_ma_lab"):
                with st.spinner(f"正在對 {lab_t} 執行 15 種均線策略回測…"):
                    ma_res = [_run_ma_strategy_backtest(lab_t, s) for s in strategies]
                    st.session_state.ma_lab_results = [r for r in ma_res if r]
                    st.session_state.ma_lab_ticker  = lab_t

            if ('ma_lab_results' in st.session_state and
                    st.session_state.get('ma_lab_ticker') == lab_t and
                    st.session_state.ma_lab_results):
                ma_res = st.session_state.ma_lab_results
                st.success(f"✅ {lab_t} — 15 種均線策略回測完成")

                wd = pd.DataFrame([{
                    '策略名稱':           r['strategy_name'],
                    '年化報酬 (CAGR)':    r.get('cagr', 0),
                    '回測期末資金':       r.get('final_equity', 0),
                    '最大回撤':           r.get('max_drawdown', 0),
                    '未來 10 年預期資金': r.get('future_10y_capital', 0),
                    '回測年數':           r.get('num_years', 0),
                } for r in ma_res]).sort_values('年化報酬 (CAGR)', ascending=False)

                st.dataframe(wd.style.format({
                    '年化報酬 (CAGR)': '{:.2%}', '回測期末資金': '{:,.0f}',
                    '最大回撤': '{:.2%}', '未來 10 年預期資金': '{:,.0f}', '回測年數': '{:.1f}'
                }), use_container_width=True)

                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='xlsxwriter') as w:
                    wd.to_excel(w, index=False, sheet_name='MA_Backtest_Report')
                st.download_button(
                    "📥 下載戰術回測報表 (Excel)", buf.getvalue(),
                    f"{lab_t}_ma_lab_report.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.divider()

                sel_s = st.selectbox("選擇策略查看圖表", [r['strategy_name'] for r in ma_res], key="ma_chart_sel")
                sel_r = next((r for r in ma_res if r['strategy_name'] == sel_s), None)
                if sel_r:
                    eq = sel_r['equity_curve'].reset_index(); eq.columns = ['Date','Equity']
                    fig = px.line(eq, x='Date', y='Equity',
                                  title=f"{lab_t} - {sel_s} 權益曲線",
                                  labels={'Equity': '資金 (元)', 'Date': '日期'})
                    fig.update_traces(line_color='#2ECC71')
                    fig.update_layout(template='plotly_dark')
                    st.plotly_chart(fig, use_container_width=True)

                    dd = sel_r['drawdown_series'].reset_index(); dd.columns = ['Date','Drawdown']
                    dd['Drawdown_pct'] = dd['Drawdown'] * 100
                    fig2 = px.area(dd, x='Date', y='Drawdown_pct',
                                   title=f"{lab_t} - {sel_s} 水下回撤圖",
                                   labels={'Drawdown_pct': '回撤 (%)', 'Date': '日期'})
                    fig2.update_traces(fillcolor='rgba(231,76,60,0.3)', line_color='rgba(231,76,60,1.0)')
                    fig2.update_yaxes(ticksuffix="%")
                    fig2.update_layout(template='plotly_dark')
                    st.plotly_chart(fig2, use_container_width=True)

    # ── 4.4 智慧調倉計算機 ──────────────────────────────────────
    with st.expander("4.4 ⚖️ 智慧調倉計算機 (Rebalancing Calculator)", expanded=False):
        pf = st.session_state.get('portfolio_df', pd.DataFrame()).copy()
        if pf.empty or '資產代號' not in pf.columns:
            st.warning("請先在 4.1 配置您的戰略資產。")
        else:
            tickers = pf['資產代號'].tolist()
            with st.spinner("正在獲取最新市價…"):
                try:
                    prices_data = yf.download(tickers, period="1d", progress=False)['Close']
                    latest = prices_data.iloc[-1] if isinstance(prices_data, pd.DataFrame) else prices_data
                    pf['最新市價'] = pd.to_numeric(pf['資產代號'].map(latest.to_dict() if hasattr(latest,'to_dict') else {}), errors='coerce').fillna(1.0)
                    pf['目前市值'] = pf['持有數量 (股)'] * pf['最新市價']
                    total_v = pf['目前市值'].sum()
                    pf['目前權重 %'] = (pf['目前市值'] / total_v) * 100

                    st.metric("目前總資產 (TWD)", f"{total_v:,.0f} 元")
                    st.write("請輸入目標權重：")

                    target_weights = []
                    for _, row in pf.iterrows():
                        w = st.number_input(
                            f"{row['資產代號']} 目標權重 (%)",
                            min_value=0.0, max_value=100.0,
                            value=float(row['目前權重 %']),
                            step=1.0, key=f"target_{row['資產代號']}"
                        )
                        target_weights.append(w)

                    pf['目標權重 %'] = target_weights
                    total_w = sum(target_weights)
                    if not (99 <= total_w <= 101):
                        st.warning(f"目標權重總和 {total_w:.1f}%，建議調整至接近 100%。")

                    pf['目標市值'] = (pf['目標權重 %'] / 100) * total_v
                    pf['調倉市值'] = pf['目標市值'] - pf['目前市值']
                    pf['調倉股數'] = (pf['調倉市值'] / pf['最新市價']).astype(int)

                    st.subheader("調倉計畫")
                    st.dataframe(
                        pf[['資產代號','目前權重 %','目標權重 %','調倉股數']].style.format({
                            '目前權重 %': '{:.1f}%', '目標權重 %': '{:.1f}%', '調倉股數': '{:+,}'
                        })
                    )
                except Exception as e:
                    st.error(f"獲取市價或計算失敗: {e}")

    # ── 4.5 全球黑天鵝壓力測試 ──────────────────────────────────
    with st.expander("4.5 🌪️ 全球黑天鵝壓力測試 (Black Swan Stress Test)", expanded=False):
        st.info("此功能將讀取您在 4.1 配置的資產，模擬全球系統性風險下的投資組合衝擊。")
        pf = st.session_state.get('portfolio_df', pd.DataFrame())
        if pf.empty:
            st.warning("請先在 4.1 配置您的戰略資產。")
        else:
            if st.button("💥 啟動壓力測試", key="btn_stress_v100"):
                portfolio_text = "\n".join([f"{row['資產代號']};{row['持有數量 (股)']}" for _, row in pf.iterrows()])
                with st.spinner("執行全球壓力測試…"):
                    results_df, summary = _run_stress_test(portfolio_text)
                if "error" in summary:
                    st.error(summary["error"])
                elif not results_df.empty:
                    st.session_state.stress_test_results = (results_df, summary)
                else:
                    st.error("壓力測試失敗，未返回任何結果。")

            if 'stress_test_results' in st.session_state:
                results_df, summary = st.session_state.stress_test_results
                total_v = summary.get('total_value', 0)
                st.metric("目前總市值 (TWD)", f"{total_v:,.0f}")

                pnl_cols = [c for c in results_df.columns if '損益' in c]
                if pnl_cols:
                    total_pnl = results_df[pnl_cols].sum()
                    kpi_c = st.columns(len(total_pnl))
                    for i, (sc, pnl) in enumerate(total_pnl.items()):
                        pct = (pnl / total_v * 100) if total_v > 0 else 0
                        kpi_c[i].metric(sc.replace('損益_', ''), f"{pnl:,.0f} TWD", f"{pct:.1f}%")

                num_cols = results_df.select_dtypes(include='number').columns.tolist()
                fmt = {c: '{:,.2f}' if 'price' in c else '{:,.0f}' for c in num_cols}
                st.dataframe(results_df.style.format(fmt), use_container_width=True)
