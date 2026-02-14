# ui_desktop/tab1_macro.py
# Titan SOP V100.0 — Tab 1: 宏觀風控
# [靈魂注入 V82.0 → V100.0]
# 完整移植：
#   1.1 宏觀風控 (MacroRiskEngine 全指標)
#   1.2 高價權值股多空溫度計
#   1.3 PR90 籌碼分佈圖
#   1.4 族群熱度雷達 (Sector Heatmap)
#   1.5 成交重心即時預測 (動態 Top 100)
#   1.6 高價權值股趨勢雷達 (Top 50)
#   1.7 台指期月K結算目標價推導

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime

# ── V82 引擎導入 ──────────────────────────────────────────────────────────────
from macro_risk import MacroRiskEngine
from knowledge_base import TitanKnowledgeBase
from config import Config

# ── 信號燈對照表 ──────────────────────────────────────────────────────────────
SIGNAL_MAP = {
    "GREEN_LIGHT": "🟢 綠燈：積極進攻",
    "YELLOW_LIGHT": "🟡 黃燈：區間操作",
    "RED_LIGHT": "🔴 紅燈：現金為王"
}

# ── 緩存初始化 (只載入一次，跨 session 共享) ──────────────────────────────────
@st.cache_resource
def _load_engines():
    """單例模式載入重型引擎，防止每次 rerun 都重建"""
    from strategy import TitanStrategyEngine
    kb = TitanKnowledgeBase()
    macro = MacroRiskEngine()
    strat = TitanStrategyEngine()
    strat.kb = kb
    return macro, kb, strat

@st.cache_data(ttl=600)
def _get_macro_data(_macro, _df_hash):
    """10 分鐘緩存宏觀數據，避免重複下載"""
    # _df_hash 作為緩存鍵，實際數據透過 session_state 傳入
    df = st.session_state.get('df', pd.DataFrame())
    return _macro.check_market_status(cb_df=df)


# ── 輔助函式：render_leader_dashboard ────────────────────────────────────────
def _render_leader_dashboard(
    session_state_key: str,
    fetch_function,
    top_n: int,
    sort_key_name: str
):
    """
    雙雷達趨勢掃描 (V78.2 完整版)
    用於 1.5 / 1.6 兩個窗口
    """
    macro, kb, strat = _load_engines()

    st.info(f"此功能將掃描指定股票池，依「{sort_key_name}」找出市場最關注的 Top {top_n}，並對其進行高階趨勢預測。")

    if session_state_key not in st.session_state:
        st.session_state[session_state_key] = pd.DataFrame()

    if st.button(f"🛰️ 掃描 {sort_key_name} Top {top_n}", key=f"btn_{session_state_key}"):
        with st.spinner(f"正在掃描並進行高階運算… (可能需要 1-2 分鐘)"):
            st.session_state[session_state_key] = fetch_function(top_n=top_n)

    leaders_df = st.session_state[session_state_key]

    if leaders_df.empty:
        st.info("點擊上方按鈕以啟動掃描。")
        return

    if "error" in leaders_df.columns:
        st.error(leaders_df.iloc[0]["error"])
        return

    # ── 榜單表格 ──
    def style_status(status):
        if "多頭" in str(status):
            return f"<span style='color:#FF4B4B;font-weight:bold'>{status}</span>"
        if "空頭" in str(status):
            return f"<span style='color:#26A69A;font-weight:bold'>{status}</span>"
        return status

    def style_deduction(signal):
        if "助漲" in str(signal):
            return f"<span style='color:#FF4B4B;'>{signal}</span>"
        if "壓力" in str(signal):
            return f"<span style='color:#26A69A;'>{signal}</span>"
        return signal

    display_df = leaders_df.copy()
    display_df['排名'] = display_df['rank']
    display_df['代號'] = display_df['ticker']
    display_df['名稱'] = display_df['name']
    display_df['產業'] = display_df['industry']
    display_df['現價'] = display_df['current_price'].apply(lambda x: f"{x:.2f}")
    display_df['趨勢狀態'] = display_df['trend_status'].apply(style_status)
    display_df['持續天數'] = display_df['trend_days']
    display_df['87MA扣抵預判'] = display_df['deduction_signal'].apply(style_deduction)

    st.subheader(f"📈 今日 {sort_key_name} Top {top_n} 榜單")
    cols_show = ['排名', '代號', '名稱', '產業', '現價', '趨勢狀態', '持續天數', '87MA扣抵預判']
    st.markdown(
        display_df[cols_show].to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
    st.divider()

    # ── 深度預測 ──
    st.subheader("🔍 選擇一檔主流股進行深度預測")
    options = [f"{row['rank']}. {row['name']} ({row['ticker']})" for _, row in leaders_df.iterrows()]
    selected_str = st.selectbox("選擇標的", options=options, key=f"select_{session_state_key}")

    if selected_str:
        selected_rank = int(selected_str.split('.')[0])
        sel = leaders_df[leaders_df['rank'] == selected_rank].iloc[0]

        stock_df = sel['stock_df']
        deduction_df = sel['deduction_df']
        adam_df = sel['adam_df']
        current_price = sel['current_price']
        ma87 = sel['ma87']

        kpi_c1, kpi_c2 = st.columns(2)
        kpi_c1.metric("目前股價", f"{current_price:.2f}")

        bias_pct = ((current_price - ma87) / ma87) * 100 if ma87 > 0 else 0
        is_recent_bo = (current_price > ma87) and (stock_df['Close'].iloc[-5] < ma87)
        granville = strat._get_granville_status(current_price, ma87, is_recent_bo, bias_pct)
        kpi_c2.metric("格蘭碧法則狀態", granville)
        st.markdown("---")

        t_c1, t_c2, t_c3, t_c4 = st.columns(4)
        t_c1.metric("趨勢波段", sel['trend_status'])
        t_c2.metric("已持續天數", f"{sel['trend_days']} 天")
        t_c3.metric("生命線斜率", f"{sel['ma87_slope']:.2f}°")
        t_c4.metric("87MA扣抵預判", sel['deduction_signal'])

        tab_deduct, tab_adam = st.tabs(["**87MA 扣抵值預測**", "**亞當理論二次反射**"])

        with tab_deduct:
            if not deduction_df.empty:
                chart_data = deduction_df.reset_index()
                chart_data['Current_Price'] = current_price
                base = alt.Chart(chart_data).encode(x='Date:T')
                line_d = (base.mark_line(color='orange', strokeDash=[5, 5])
                          .encode(y=alt.Y('Deduction_Value', title='Price'),
                                  tooltip=['Date', 'Deduction_Value'])
                          .properties(title="未來60日 87MA 扣抵值預測"))
                line_c = base.mark_line(color='#4B9CD3').encode(y='Current_Price')
                st.altair_chart((line_d + line_c).interactive(), use_container_width=True)
            else:
                st.warning("歷史資料不足，無法預測均線扣抵值。")

        with tab_adam:
            if not adam_df.empty:
                hist_d = stock_df.iloc[-60:].reset_index()
                hist_d['Type'] = '歷史路徑'
                proj_d = adam_df.reset_index()
                proj_d['Type'] = '亞當投影'
                proj_d.rename(columns={'Projected_Price': 'Close', 'Date': 'Date'}, inplace=True)
                combined = pd.concat([hist_d[['Date', 'Close', 'Type']], proj_d[['Date', 'Close', 'Type']]])
                chart = (alt.Chart(combined)
                         .mark_line()
                         .encode(
                             x='Date:T',
                             y=alt.Y('Close', title='Price', scale=alt.Scale(zero=False)),
                             color='Type:N',
                             strokeDash='Type:N'
                         )
                         .properties(title="亞當理論二次反射路徑圖")
                         .interactive())
                st.altair_chart(chart, use_container_width=True)
            else:
                st.warning("歷史資料不足，無法進行亞當理論投影。")


# ── 輔助函式：台指期結算目標 ─────────────────────────────────────────────────
def _calculate_futures_targets():
    """V82.0 台指期月K結算目標價推導"""
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
            d = wed.iloc[2]['Date']
            val = d.item() if hasattr(d, 'item') else d
            if not df[df['Date'] >= val].empty:
                s_dates.append(val)

    stats = []
    for i in range(len(s_dates) - 1):
        mask = (df['Date'] > s_dates[i]) & (df['Date'] <= s_dates[i + 1])
        m_data = df.loc[mask]
        if not m_data.empty:
            h = m_data['High'].max()
            l = m_data['Low'].min()
            hv = float(h.item() if hasattr(h, 'item') else h)
            lv = float(l.item() if hasattr(l, 'item') else l)
            stats.append(hv - lv)

    if len(stats) < 12:
        return {"error": "資料不足"}

    l12 = stats[-12:]
    min_a = min(l12)
    avg_a = sum(l12) / 12
    max_a = max(l12)

    curr = df[df['Date'] > s_dates[-1]]
    if curr.empty:
        return {"error": "新合約未開始"}

    op_v = float(curr.iloc[0]['Open'])
    cl_v = float(curr.iloc[-1]['Close'])
    is_red = cl_v >= op_v
    sign = 1 if is_red else -1

    targets = {
        "1B": op_v + sign * min_a * 0.5,
        "2B": op_v + sign * min_a,
        "3B": op_v + sign * avg_a,
        "HR": op_v + sign * max_a
    }
    return {"name": ticker_name, "anc": op_v, "price": cl_v, "is_red": is_red, "t": targets}


# ═════════════════════════════════════════════════════════════════════════════
#  主渲染入口
# ═════════════════════════════════════════════════════════════════════════════
def render():
    """Tab 1: 宏觀風控 — 全功能復原版 (V82 靈魂 + V100 外殼)"""

    macro, kb, strat = _load_engines()
    df = st.session_state.get('df', pd.DataFrame())

    # ── 計算緩存鍵（用 df 長度+列名hash 代替傳入 df 本身）
    df_hash = f"{len(df)}_{list(df.columns)}" if not df.empty else "empty"

    # ─────────────────────────────────────────────────────────────────────────
    # 1.1 宏觀風控 (Macro Risk)
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("1.1 🚦 宏觀風控 (Macro Risk)", expanded=True):
        if not df.empty:
            macro_data = _get_macro_data(macro, df_hash)

            c1, c2, c3, c4 = st.columns(4)
            signal_text = SIGNAL_MAP.get(macro_data['signal'], "⚪ 未知")
            signal_emoji, signal_desc = (
                signal_text.split('：') if '：' in signal_text else (signal_text, "")
            )
            c1.metric("🚦 總體燈號", signal_emoji, help=signal_desc)
            c2.metric("😱 VIX恐慌指數", f"{macro_data['vix']:.2f}", "高於25為綠燈")
            c3.metric("🔥 PR90市場熱度",
                      f"{macro_data['price_distribution']['pr90']:.2f}",
                      "高於130為紅燈")
            ptt_ratio = macro_data['ptt_ratio']
            ptt_text = f"{ptt_ratio:.1f}%" if ptt_ratio != -1.0 else "N/A"
            c4.metric("📊 PTT空頭比例", ptt_text, help="空頭家數佔比，高於50%為紅燈")

            st.subheader("🇹🇼 台股加權指數深度分析")
            tse = macro_data['tse_analysis']
            k1, k2, k3 = st.columns(3)
            k1.metric(f"目前點位: {tse['price']:.2f}", tse['momentum'])
            k2.metric("神奇均線趨勢", tse['magic_ma'])
            k3.metric("格蘭碧法則", tse['granville'])
            st.text("扣抵與斜率: " + " | ".join(tse['deduct_slope']))
        else:
            st.info("請於左側上傳 CB 清單以啟動戰情室。")

    # ─────────────────────────────────────────────────────────────────────────
    # 1.2 高價權值股多空溫度計
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("1.2 🌡️ 高價權值股多空溫度計", expanded=False):
        if 'high_50_sentiment' not in st.session_state:
            st.session_state.high_50_sentiment = None

        if st.button("🔄 刷新市場多空溫度", key="btn_sentiment"):
            with st.spinner("正在分析高價權值股…"):
                st.session_state.high_50_sentiment = macro.analyze_high_50_sentiment()

        if st.session_state.high_50_sentiment:
            sentiment = st.session_state.high_50_sentiment
            if "error" in sentiment:
                st.error(sentiment["error"])
            else:
                col1, col2 = st.columns(2)
                col1.metric("市場氣氛", sentiment['sentiment'])
                col2.metric(
                    "多空比例 (站上/跌破87MA)",
                    f"🐂 {sentiment['bull_ratio']:.1f}% | 🐻 {sentiment['bear_ratio']:.1f}%",
                    help=f"基於 {sentiment['total']} 檔高價權值股分析"
                )

                # 視覺化多空比例
                import plotly.graph_objects as go
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=sentiment['bull_ratio'],
                    title={'text': "多頭佔比 (%)"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#FF4B4B"},
                        'steps': [
                            {'range': [0, 35], 'color': '#1a3a4a'},
                            {'range': [35, 65], 'color': '#2d4a2d'},
                            {'range': [65, 100], 'color': '#4a1a1a'},
                        ],
                        'threshold': {
                            'line': {'color': "gold", 'width': 4},
                            'thickness': 0.75,
                            'value': 50
                        }
                    }
                ))
                fig.update_layout(height=300, template="plotly_dark",
                                  paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("點擊按鈕以分析市場多空溫度。")

    # ─────────────────────────────────────────────────────────────────────────
    # 1.3 PR90 籌碼分佈圖
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("1.3 📊 PR90 籌碼分佈圖", expanded=False):
        if not df.empty:
            macro_data = _get_macro_data(macro, df_hash)
            price_dist = macro_data.get('price_distribution', {})
            chart_data = price_dist.get('chart_data')

            if chart_data is not None and not chart_data.empty:
                c1, c2, c3 = st.columns(3)
                c1.metric("PR90 (過熱線)", f"{price_dist.get('pr90', 0):.2f}",
                          help="90%的CB低於此價，代表市場熱度")
                c2.metric("PR75 (機會線)", f"{price_dist.get('pr75', 0):.2f}",
                          help="75%的CB低於此價，尋寶機會區")
                c3.metric("市場均價", f"{price_dist.get('avg', 0):.2f}")

                # Altair 黑金風柱狀圖
                bar_chart = (
                    alt.Chart(chart_data)
                    .mark_bar(color='#FFD700', opacity=0.85)
                    .encode(
                        x=alt.X('區間:N', sort=None, title='CB 市價區間'),
                        y=alt.Y('數量:Q', title='檔數'),
                        tooltip=['區間', '數量']
                    )
                    .properties(title="CB 市場籌碼分佈 (Price Distribution)")
                )
                st.altair_chart(bar_chart, use_container_width=True)
            else:
                st.warning("無法生成籌碼分佈圖，請檢查 CB 清單中的價格欄位。")
        else:
            st.info("請上傳 CB 清單以生成籌碼分佈圖。")

    # ─────────────────────────────────────────────────────────────────────────
    # 1.4 族群熱度雷達 (Sector Heatmap)
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("1.4 🗺️ 族群熱度雷達 (Sector Heatmap)", expanded=False):
        if not df.empty:
            if 'sector_heatmap' not in st.session_state:
                st.session_state.sector_heatmap = pd.DataFrame()

            if st.button("🛰️ 掃描市場族群熱度", key="btn_heatmap"):
                with st.spinner("正在分析族群資金流向…"):
                    st.session_state.sector_heatmap = macro.analyze_sector_heatmap(df, kb)

            if not st.session_state.sector_heatmap.empty:
                st.info("「多頭比例」代表該族群中，有多少比例的標的股價站上 87MA 生命線。")
                # 顏色條件樣式
                heatmap_df = st.session_state.sector_heatmap.copy()

                def colorize_ratio(val):
                    try:
                        v = float(val)
                        if v >= 70:
                            return 'background-color: rgba(255,75,75,0.4)'
                        elif v >= 50:
                            return 'background-color: rgba(255,215,0,0.3)'
                        else:
                            return 'background-color: rgba(38,166,154,0.3)'
                    except Exception:
                        return ''

                styled = heatmap_df.style.applymap(
                    colorize_ratio, subset=['多頭比例 (%)']
                )
                st.dataframe(styled, use_container_width=True)
            else:
                st.info("點擊按鈕或上傳包含「漲跌幅」欄位的 CB 清單以分析族群熱度。")
        else:
            st.info("請上傳 CB 清單以啟動族群熱度雷達。")

    # ─────────────────────────────────────────────────────────────────────────
    # 1.5 成交重心即時預測 (動態 Top 100)
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("1.5 💹 成交重心即時預測 (動態 Top 100)", expanded=False):
        _render_leader_dashboard(
            session_state_key="w15_data",
            fetch_function=macro.get_dynamic_turnover_leaders,
            top_n=100,
            sort_key_name="成交值"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 1.6 高價權值股趨勢雷達 (Top 50)
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("1.6 👑 高價權值股趨勢雷達 (Top 50)", expanded=False):
        _render_leader_dashboard(
            session_state_key="w16_data",
            fetch_function=macro.get_high_price_leaders,
            top_n=50,
            sort_key_name="股價"
        )

    # ─────────────────────────────────────────────────────────────────────────
    # 1.7 台指期月K結算目標價推導 (Settlement Radar)
    # ─────────────────────────────────────────────────────────────────────────
    with st.expander("1.7 🎯 台指期月K結算目標價推導 (Settlement Radar)", expanded=False):
        st.info("💡 獨門戰法：利用過去 12 個月結算慣性，推導本月台指期 (TX) 的「虛擬 K 棒」與目標價。")

        if st.button("🔮 推導台指期目標", key="btn_futures"):
            with st.spinner("推導台指期…"):
                st.session_state['futures_result'] = _calculate_futures_targets()

        res = st.session_state.get('futures_result', None)

        if res is None:
            st.info("點擊按鈕以推導台指期目標價。")
        elif "error" in res:
            st.warning(f"⚠️ {res['error']}")
        else:
            is_red = res['is_red']
            st.subheader(f"📊 {res['name']}：{'🔴 多方控盤' if is_red else '🟢 空方控盤'}")

            c1, c2 = st.columns(2)
            c1.metric("定錨開盤價", f"{res['anc']:.0f}")
            c2.metric("目前點位", f"{res['price']:.0f}",
                      f"{res['price'] - res['anc']:.0f}")

            if is_red:
                st.success("🔥 多方贏慣性：易收長紅。")
            else:
                st.success("💀 空方贏慣性：易收長黑。")

            def check_hit(tg):
                return "✅ 達標" if (is_red and res['price'] >= tg) or \
                       (not is_red and res['price'] <= tg) else "⏳ 未達"

            t1, t2, t3, t4 = st.columns(4)
            t1.metric("1壘", f"{res['t']['1B']:.0f}", check_hit(res['t']['1B']))
            t2.metric("2壘", f"{res['t']['2B']:.0f}", check_hit(res['t']['2B']))
            t3.metric("3壘", f"{res['t']['3B']:.0f}", check_hit(res['t']['3B']))
            t4.metric("HR", f"{res['t']['HR']:.0f}", check_hit(res['t']['HR']))

            # Altair 虛擬K棒圖
            chart_df = pd.DataFrame({
                "Label": ["本月"],
                "Anchor": [res['anc']],
                "Current": [res['price']],
                "Target_HR": [res['t']['HR']],
                "Target_1B": [res['t']['1B']],
                "Target_2B": [res['t']['2B']],
                "Target_3B": [res['t']['3B']]
            })

            base = alt.Chart(chart_df).encode(x=alt.X('Label', axis=None))
            ghost = (base.mark_bar(size=40,
                                   color="#ffcccc" if is_red else "#ccffcc",
                                   opacity=0.5)
                     .encode(y=alt.Y('Anchor', scale=alt.Scale(zero=False), title='Price'),
                             y2='Target_HR'))
            real = (base.mark_bar(size=20,
                                  color="#d62728" if is_red else "#2ca02c")
                    .encode(y='Anchor', y2='Current'))

            chart = ghost + real
            for k in ['1B', '2B', '3B']:
                chart += (
                    base.mark_tick(color='gold', thickness=2, size=50)
                    .encode(y=f'Target_{k}')
                    + base.mark_text(dx=38, align='left', color='gold')
                    .encode(y=f'Target_{k}',
                            text=alt.value(f"{k}  {res['t'][k]:.0f}"))
                )
            chart += (
                base.mark_tick(color='red', thickness=4, size=60)
                .encode(y='Target_HR')
                + base.mark_text(dx=42, align='left', color='red')
                .encode(y='Target_HR',
                        text=alt.value(f"HR  {res['t']['HR']:.0f}"))
            )

            _, chart_col, _ = st.columns([1, 2, 1])
            with chart_col:
                st.altair_chart(chart, use_container_width=True)

        st.caption(f"📅 數據更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
