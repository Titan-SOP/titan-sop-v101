# ui_desktop/tab1_macro.py
# Titan SOP V100.0 — Tab 1: 宏觀風控指揮中心
# 架構：Sub-Module Navigation System (Big Buttons)
# 邏輯：完整保留 V82 靈魂（MacroRiskEngine / Altair / Plotly）

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
from datetime import datetime

from macro_risk import MacroRiskEngine
from knowledge_base import TitanKnowledgeBase
from config import Config

# ══════════════════════════════════════════════════════════════
#  常數
# ══════════════════════════════════════════════════════════════
SIGNAL_MAP = {
    "GREEN_LIGHT":  "🟢 綠燈：積極進攻",
    "YELLOW_LIGHT": "🟡 黃燈：區間操作",
    "RED_LIGHT":    "🔴 紅燈：現金為王",
}

SUB_MODULES = [
    ("1.1", "🚦", "風控儀表"),
    ("1.2", "🌡️", "多空溫度"),
    ("1.3", "📊", "PR90籌碼"),
    ("1.4", "🗺️", "族群熱度"),
    ("1.5", "💹", "成交重心"),
    ("1.6", "👑", "趨勢雷達"),
    ("1.7", "🎯", "台指獵殺"),
]

# ══════════════════════════════════════════════════════════════
#  CSS — Titan OS 大按鈕控制台
# ══════════════════════════════════════════════════════════════
NAV_CSS = """
<style>
/* ── 控制台外框 ─────────────────────────── */
.titan-nav-deck {
    background: linear-gradient(135deg, #0d0d0d 0%, #1a1a2e 100%);
    border: 1px solid #333;
    border-radius: 16px;
    padding: 24px 20px 16px;
    margin-bottom: 24px;
}
.titan-nav-title {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 3px;
    color: #555;
    text-transform: uppercase;
    margin-bottom: 14px;
}

/* ── 導航按鈕 ────────────────────────────── */
div[data-testid="column"] > div > div > div > button.titan-nav-btn,
div.stButton > button[data-nav="true"] {
    background: #1a1a2e !important;
    border: 1px solid #333 !important;
    border-radius: 12px !important;
    color: #AAAAAA !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 14px 8px !important;
    min-height: 72px !important;
    width: 100% !important;
    transition: all 0.25s ease !important;
    line-height: 1.4 !important;
}
div.stButton > button[data-nav="true"]:hover {
    border-color: #FFD700 !important;
    color: #FFD700 !important;
    background: rgba(255,215,0,0.08) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(255,215,0,0.2) !important;
}

/* ── 選中態（用 key 無法精準控制，靠 active class 模擬）─ */
.nav-active-card {
    background: linear-gradient(135deg, #2a2a1a 0%, #1a2a1a 100%) !important;
    border: 2px solid #FFD700 !important;
    border-radius: 12px !important;
    padding: 12px 8px !important;
    min-height: 72px !important;
    text-align: center !important;
    color: #FFD700 !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    cursor: default !important;
    box-shadow: 0 0 20px rgba(255,215,0,0.25) !important;
    line-height: 1.4 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-direction: column !important;
}

/* ── 內容區 ─────────────────────────────── */
.titan-content-area {
    background: #111118;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 28px 24px;
    margin-top: 4px;
}
.section-header {
    font-size: 22px;
    font-weight: 700;
    color: #FFD700;
    text-shadow: 0 0 12px rgba(255,215,0,0.4);
    margin-bottom: 20px;
    border-left: 4px solid #FFD700;
    padding-left: 14px;
}

/* ── 覆蓋首頁的綠色按鈕 ─────────────────── */
.titan-content-area div.stButton > button,
.titan-nav-deck ~ div div.stButton > button {
    background: linear-gradient(135deg, #2a2a3e, #1a1a2e) !important;
    color: #FFD700 !important;
    border: 1px solid #FFD700 !important;
    box-shadow: none !important;
}
.titan-content-area div.stButton > button:hover,
.titan-nav-deck ~ div div.stButton > button:hover {
    background: rgba(255,215,0,0.1) !important;
    box-shadow: 0 4px 16px rgba(255,215,0,0.3) !important;
}
</style>
"""


# ══════════════════════════════════════════════════════════════
#  引擎（單例 + 緩存）
# ══════════════════════════════════════════════════════════════
@st.cache_resource
def _load_engines():
    from strategy import TitanStrategyEngine
    kb    = TitanKnowledgeBase()
    macro = MacroRiskEngine()
    strat = TitanStrategyEngine()
    strat.kb = kb
    return macro, kb, strat


@st.cache_data(ttl=600)
def _get_macro_data(_macro, _df_hash):
    df = st.session_state.get('df', pd.DataFrame())
    return _macro.check_market_status(cb_df=df)


# ══════════════════════════════════════════════════════════════
#  通用工具
# ══════════════════════════════════════════════════════════════
def _render_leader_dashboard(session_state_key: str, fetch_function, top_n: int, sort_key_name: str):
    """雙雷達趨勢掃描（V78.2 完整版）"""
    macro, kb, strat = _load_engines()

    st.info(f"此功能將掃描指定股票池，依「{sort_key_name}」找出市場最關注的 Top {top_n}，並對其進行高階趨勢預測。")

    if session_state_key not in st.session_state:
        st.session_state[session_state_key] = pd.DataFrame()

    if st.button(f"🛰️ 掃描 {sort_key_name} Top {top_n}", key=f"btn_{session_state_key}"):
        with st.spinner("正在掃描並進行高階運算… (可能需要 1-2 分鐘)"):
            st.session_state[session_state_key] = fetch_function(top_n=top_n)

    leaders_df = st.session_state[session_state_key]

    if leaders_df.empty:
        st.info("點擊上方按鈕以啟動掃描。")
        return
    if "error" in leaders_df.columns:
        st.error(leaders_df.iloc[0]["error"])
        return

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
    display_df['排名']       = display_df['rank']
    display_df['代號']       = display_df['ticker']
    display_df['名稱']       = display_df['name']
    display_df['產業']       = display_df['industry']
    display_df['現價']       = display_df['current_price'].apply(lambda x: f"{x:.2f}")
    display_df['趨勢狀態']   = display_df['trend_status'].apply(style_status)
    display_df['持續天數']   = display_df['trend_days']
    display_df['87MA扣抵預判'] = display_df['deduction_signal'].apply(style_deduction)

    st.subheader(f"📈 今日 {sort_key_name} Top {top_n} 榜單")
    cols_show = ['排名', '代號', '名稱', '產業', '現價', '趨勢狀態', '持續天數', '87MA扣抵預判']
    st.markdown(display_df[cols_show].to_html(escape=False, index=False), unsafe_allow_html=True)
    st.divider()

    st.subheader("🔍 選擇一檔主流股進行深度預測")
    options = [f"{row['rank']}. {row['name']} ({row['ticker']})" for _, row in leaders_df.iterrows()]
    selected_str = st.selectbox("選擇標的", options=options, key=f"select_{session_state_key}")

    if selected_str:
        selected_rank = int(selected_str.split('.')[0])
        sel = leaders_df[leaders_df['rank'] == selected_rank].iloc[0]

        stock_df      = sel['stock_df']
        deduction_df  = sel['deduction_df']
        adam_df       = sel['adam_df']
        current_price = sel['current_price']
        ma87          = sel['ma87']

        kpi_c1, kpi_c2 = st.columns(2)
        kpi_c1.metric("目前股價", f"{current_price:.2f}")
        bias_pct    = ((current_price - ma87) / ma87) * 100 if ma87 > 0 else 0
        is_recent_bo = (current_price > ma87) and (stock_df['Close'].iloc[-5] < ma87)
        granville   = strat._get_granville_status(current_price, ma87, is_recent_bo, bias_pct)
        kpi_c2.metric("格蘭碧法則狀態", granville)
        st.markdown("---")

        t_c1, t_c2, t_c3, t_c4 = st.columns(4)
        t_c1.metric("趨勢波段",   sel['trend_status'])
        t_c2.metric("已持續天數", f"{sel['trend_days']} 天")
        t_c3.metric("生命線斜率", f"{sel['ma87_slope']:.2f}°")
        t_c4.metric("87MA扣抵預判", sel['deduction_signal'])

        tab_deduct, tab_adam = st.tabs(["**87MA 扣抵值預測**", "**亞當理論二次反射**"])

        with tab_deduct:
            if not deduction_df.empty:
                chart_data = deduction_df.reset_index()
                chart_data['Current_Price'] = current_price
                base   = alt.Chart(chart_data).encode(x='Date:T')
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
            d   = wed.iloc[2]['Date']
            val = d.item() if hasattr(d, 'item') else d
            if not df[df['Date'] >= val].empty:
                s_dates.append(val)

    stats = []
    for i in range(len(s_dates) - 1):
        mask   = (df['Date'] > s_dates[i]) & (df['Date'] <= s_dates[i + 1])
        m_data = df.loc[mask]
        if not m_data.empty:
            h  = m_data['High'].max()
            l  = m_data['Low'].min()
            hv = float(h.item() if hasattr(h, 'item') else h)
            lv = float(l.item() if hasattr(l, 'item') else l)
            stats.append(hv - lv)

    if len(stats) < 12:
        return {"error": "資料不足"}

    l12   = stats[-12:]
    min_a = min(l12)
    avg_a = sum(l12) / 12
    max_a = max(l12)

    curr = df[df['Date'] > s_dates[-1]]
    if curr.empty:
        return {"error": "新合約未開始"}

    op_v   = float(curr.iloc[0]['Open'])
    cl_v   = float(curr.iloc[-1]['Close'])
    is_red = cl_v >= op_v
    sign   = 1 if is_red else -1

    targets = {
        "1B": op_v + sign * min_a * 0.5,
        "2B": op_v + sign * min_a,
        "3B": op_v + sign * avg_a,
        "HR": op_v + sign * max_a
    }
    return {"name": ticker_name, "anc": op_v, "price": cl_v, "is_red": is_red, "t": targets}


# ══════════════════════════════════════════════════════════════
#  7 個子模組渲染函式
# ══════════════════════════════════════════════════════════════

def render_1_1_hud():
    """1.1 🚦 宏觀風控儀表（HUD）"""
    st.markdown('<div class="section-header">🚦 1.1 宏觀風控儀表</div>', unsafe_allow_html=True)
    macro, kb, strat = _load_engines()
    df      = st.session_state.get('df', pd.DataFrame())
    df_hash = f"{len(df)}_{list(df.columns)}" if not df.empty else "empty"

    if not df.empty:
        macro_data   = _get_macro_data(macro, df_hash)
        signal_text  = SIGNAL_MAP.get(macro_data['signal'], "⚪ 未知")
        signal_emoji, signal_desc = (
            signal_text.split('：') if '：' in signal_text else (signal_text, "")
        )

        # ── 四格 KPI ──
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🚦 總體燈號",    signal_emoji, help=signal_desc)
        c2.metric("😱 VIX恐慌指數", f"{macro_data['vix']:.2f}", "高於25為警示")
        c3.metric("🔥 PR90市場熱度",
                  f"{macro_data['price_distribution']['pr90']:.2f}",
                  "高於130為紅燈")
        ptt_ratio = macro_data['ptt_ratio']
        ptt_text  = f"{ptt_ratio:.1f}%" if ptt_ratio != -1.0 else "N/A"
        c4.metric("📊 PTT空頭比例", ptt_text, help="空頭家數佔比，高於50%為紅燈")

        st.divider()

        # ── 台股加權 ──
        st.subheader("🇹🇼 台股加權指數深度分析")
        tse = macro_data['tse_analysis']
        k1, k2, k3 = st.columns(3)
        k1.metric(f"目前點位: {tse['price']:.2f}", tse['momentum'])
        k2.metric("神奇均線趨勢", tse['magic_ma'])
        k3.metric("格蘭碧法則",   tse['granville'])
        st.text("扣抵與斜率: " + " | ".join(tse['deduct_slope']))

        # ── 信號燈視覺化 ──
        st.divider()
        signal_color = {"GREEN_LIGHT": "#00FF00", "YELLOW_LIGHT": "#FFD700", "RED_LIGHT": "#FF4B4B"}
        sig = macro_data['signal']
        st.markdown(f"""
        <div style="
            background: radial-gradient(circle, {signal_color.get(sig,'#555')}22 0%, transparent 70%);
            border: 2px solid {signal_color.get(sig,'#555')};
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            font-size: 28px;
            font-weight: bold;
            color: {signal_color.get(sig,'#FFF')};
            text-shadow: 0 0 20px {signal_color.get(sig,'#555')}99;
            margin-top: 12px;
        ">
            {SIGNAL_MAP.get(sig, '⚪ 未知')}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background:#1a1a2e; border:1px dashed #444; border-radius:12px;
                    padding:40px; text-align:center; color:#888;">
            <div style="font-size:48px; margin-bottom:12px;">📂</div>
            <div style="font-size:18px;">請於左側側邊欄上傳 CB 清單以啟動戰情室</div>
        </div>""", unsafe_allow_html=True)


def render_1_2_thermometer():
    """1.2 🌡️ 高價權值股多空溫度計"""
    st.markdown('<div class="section-header">🌡️ 1.2 高價權值股多空溫度計</div>', unsafe_allow_html=True)
    macro, _, _ = _load_engines()

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

            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=sentiment['bull_ratio'],
                title={'text': "多頭佔比 (%)"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar':  {'color': "#FF4B4B"},
                    'steps': [
                        {'range': [0,   35], 'color': '#1a3a4a'},
                        {'range': [35,  65], 'color': '#2d4a2d'},
                        {'range': [65, 100], 'color': '#4a1a1a'},
                    ],
                    'threshold': {
                        'line': {'color': "gold", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))
            fig.update_layout(height=340, template="plotly_dark",
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            # ── 多空分類標籤 ──
            ratio = sentiment['bull_ratio']
            if ratio >= 65:
                label, color = "🔥 強勢多頭市場，攻擊態勢", "#FF4B4B"
            elif ratio >= 50:
                label, color = "🟢 多方略佔優勢，持股向好", "#00FF7F"
            elif ratio >= 35:
                label, color = "🟡 多空交戰，審慎選股", "#FFD700"
            else:
                label, color = "🔴 空頭市場，輕倉防守", "#26A69A"
            st.markdown(f"""
            <div style="border:1px solid {color}; border-radius:10px; padding:14px;
                        color:{color}; font-size:18px; font-weight:bold; text-align:center;
                        background:rgba(0,0,0,0.3); margin-top:12px;">
                {label}
            </div>""", unsafe_allow_html=True)
    else:
        st.info("點擊上方按鈕以分析市場多空溫度。")


def render_1_3_pr90():
    """1.3 📊 PR90 籌碼分佈圖"""
    st.markdown('<div class="section-header">📊 1.3 PR90 籌碼分佈圖</div>', unsafe_allow_html=True)
    macro, _, _ = _load_engines()
    df      = st.session_state.get('df', pd.DataFrame())
    df_hash = f"{len(df)}_{list(df.columns)}" if not df.empty else "empty"

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
            c3.metric("市場均價",     f"{price_dist.get('avg', 0):.2f}")

            st.divider()

            # Altair 黑金風柱狀圖（v6 相容：用 DataFrame 欄位做色彩，不用巢狀 condition）
            pr90_val = price_dist.get('pr90', 999)
            pr75_val = price_dist.get('pr75', 999)

            chart_data = chart_data.copy()

            def _zone(label):
                try:
                    mid = float(str(label).split('~')[0])
                except Exception:
                    return "正常區"
                if mid >= pr90_val:
                    return "PR90 過熱區"
                if mid >= pr75_val:
                    return "PR75 警示區"
                return "正常區"

            chart_data['區域'] = chart_data['區間'].apply(_zone)

            bar_chart = (
                alt.Chart(chart_data)
                .mark_bar(opacity=0.88)
                .encode(
                    x=alt.X('區間:N', sort=None, title='CB 市價區間'),
                    y=alt.Y('數量:Q', title='檔數'),
                    color=alt.Color(
                        '區域:N',
                        scale=alt.Scale(
                            domain=["正常區", "PR75 警示區", "PR90 過熱區"],
                            range=["#4B9CD3", "#FFD700", "#FF4B4B"]
                        ),
                        legend=alt.Legend(orient='top', labelColor='#AAAAAA',
                                          titleColor='#AAAAAA')
                    ),
                    tooltip=['區間', '數量', '區域']
                )
                .properties(
                    title=alt.TitleParams(
                        text="CB 市場籌碼分佈 (Price Distribution)",
                        color='#FFD700'
                    ),
                    height=320
                )
                .configure_axis(labelColor='#AAAAAA', titleColor='#AAAAAA')
                .configure_view(strokeOpacity=0)
            )
            st.altair_chart(bar_chart, use_container_width=True)

            st.markdown("""
            <div style="display:flex; gap:12px; margin-top:8px; font-size:12px;">
                <span style="color:#4B9CD3">■ 正常區</span>
                <span style="color:#FFD700">■ PR75 警示區</span>
                <span style="color:#FF4B4B">■ PR90 過熱區</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.warning("無法生成籌碼分佈圖，請檢查 CB 清單中的價格欄位。")
    else:
        st.info("請上傳 CB 清單以生成籌碼分佈圖。")


def render_1_4_heatmap():
    """1.4 🗺️ 族群熱度雷達"""
    st.markdown('<div class="section-header">🗺️ 1.4 族群熱度雷達</div>', unsafe_allow_html=True)
    macro, kb, _ = _load_engines()
    df = st.session_state.get('df', pd.DataFrame())

    if not df.empty:
        if 'sector_heatmap' not in st.session_state:
            st.session_state.sector_heatmap = pd.DataFrame()

        if st.button("🛰️ 掃描市場族群熱度", key="btn_heatmap"):
            with st.spinner("正在分析族群資金流向…"):
                st.session_state.sector_heatmap = macro.analyze_sector_heatmap(df, kb)

        if not st.session_state.sector_heatmap.empty:
            st.info("「多頭比例」代表該族群中，有多少比例的標的股價站上 87MA 生命線。")

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

            styled = heatmap_df.style.applymap(colorize_ratio, subset=['多頭比例 (%)'])
            st.dataframe(styled, use_container_width=True)

            # ── Plotly 圓餅圖（族群佔比）──
            if '產業' in heatmap_df.columns and 'CB 數量' in heatmap_df.columns:
                try:
                    fig_pie = go.Figure(go.Pie(
                        labels=heatmap_df['產業'],
                        values=heatmap_df['CB 數量'],
                        hole=0.4,
                        marker=dict(colors=[
                            '#FF4B4B', '#FFD700', '#4B9CD3', '#00FF7F',
                            '#FF69B4', '#FFA07A', '#9370DB', '#26A69A',
                        ])
                    ))
                    fig_pie.update_layout(
                        title="各族群 CB 數量佔比",
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)',
                        height=320
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                except Exception:
                    pass
        else:
            st.info("點擊按鈕以分析族群熱度。")
    else:
        st.info("請上傳 CB 清單以啟動族群熱度雷達。")


def render_1_5_turnover():
    """1.5 💹 成交重心即時預測（動態 Top 100）"""
    st.markdown('<div class="section-header">💹 1.5 成交重心即時預測 (Top 100)</div>', unsafe_allow_html=True)
    macro, _, _ = _load_engines()
    _render_leader_dashboard(
        session_state_key="w15_data",
        fetch_function=macro.get_dynamic_turnover_leaders,
        top_n=100,
        sort_key_name="成交值"
    )


def render_1_6_trend_radar():
    """1.6 👑 高價權值股趨勢雷達（Top 50）"""
    st.markdown('<div class="section-header">👑 1.6 高價權值股趨勢雷達 (Top 50)</div>', unsafe_allow_html=True)
    macro, _, _ = _load_engines()
    _render_leader_dashboard(
        session_state_key="w16_data",
        fetch_function=macro.get_high_price_leaders,
        top_n=50,
        sort_key_name="股價"
    )


def render_1_7_predator():
    """1.7 🎯 台指期月K結算目標價推導（Baseball Chart）"""
    st.markdown('<div class="section-header">🎯 1.7 台指期月K結算目標價推導</div>', unsafe_allow_html=True)
    st.info("💡 獨門戰法：利用過去 12 個月結算慣性，推導本月台指期 (TX) 的「虛擬 K 棒」與目標價。")

    if st.button("🔮 推導台指期目標", key="btn_futures"):
        with st.spinner("推導台指期…"):
            st.session_state['futures_result'] = _calculate_futures_targets()

    res = st.session_state.get('futures_result', None)

    if res is None:
        st.info("點擊按鈕以推導台指期目標價。")
        return

    if "error" in res:
        st.warning(f"⚠️ {res['error']}")
        return

    is_red = res['is_red']
    color  = "#d62728" if is_red else "#2ca02c"

    st.subheader(f"📊 {res['name']}：{'🔴 多方控盤' if is_red else '🟢 空方控盤'}")

    c1, c2 = st.columns(2)
    c1.metric("定錨開盤價", f"{res['anc']:.0f}")
    c2.metric("目前點位",   f"{res['price']:.0f}", f"{res['price'] - res['anc']:.0f}")

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
    t4.metric("HR",  f"{res['t']['HR']:.0f}", check_hit(res['t']['HR']))

    st.divider()

    # ── Altair Baseball K棒圖（完整保留）──
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
    ghost = (base.mark_bar(size=60, color="#ffcccc" if is_red else "#ccffcc", opacity=0.5)
             .encode(y=alt.Y('Anchor', scale=alt.Scale(zero=False), title='Price'),
                     y2='Target_HR'))
    real  = (base.mark_bar(size=30, color=color)
             .encode(y='Anchor', y2='Current'))

    chart = ghost + real
    for k in ['1B', '2B', '3B']:
        chart += (
            base.mark_tick(color='gold', thickness=2, size=70)
            .encode(y=f'Target_{k}')
            + base.mark_text(dx=44, align='left', color='gold', fontSize=13, fontWeight='bold')
            .encode(y=f'Target_{k}', text=alt.value(f"{k}  {res['t'][k]:.0f}"))
        )
    chart += (
        base.mark_tick(color='#FF4B4B', thickness=4, size=80)
        .encode(y='Target_HR')
        + base.mark_text(dx=48, align='left', color='#FF4B4B', fontSize=14, fontWeight='bold')
        .encode(y='Target_HR', text=alt.value(f"HR  {res['t']['HR']:.0f}"))
    )

    _, chart_col, _ = st.columns([1, 2, 1])
    with chart_col:
        st.altair_chart(
            chart.properties(height=420)
                 .configure_view(strokeOpacity=0)
                 .configure_axis(labelColor='#AAAAAA'),
            use_container_width=True
        )

    st.caption(f"📅 數據更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


# ══════════════════════════════════════════════════════════════
#  主渲染入口
# ══════════════════════════════════════════════════════════════

RENDER_MAP = {
    "1.1": render_1_1_hud,
    "1.2": render_1_2_thermometer,
    "1.3": render_1_3_pr90,
    "1.4": render_1_4_heatmap,
    "1.5": render_1_5_turnover,
    "1.6": render_1_6_trend_radar,
    "1.7": render_1_7_predator,
}


def render():
    """Tab 1 主入口 — Titan OS Sub-Module Navigator"""

    # ── CSS 注入 ──────────────────────────────────────────────
    st.markdown(NAV_CSS, unsafe_allow_html=True)

    # ── Session State ─────────────────────────────────────────
    if 'tab1_active' not in st.session_state:
        st.session_state.tab1_active = "1.1"

    active = st.session_state.tab1_active

    # ── 標題 ──────────────────────────────────────────────────
    st.markdown("""
    <div style="
        font-size: 28px;
        font-weight: 800;
        color: #FFD700;
        text-shadow: 0 0 16px rgba(255,215,0,0.5);
        letter-spacing: 2px;
        margin-bottom: 20px;
    ">🛡️ 宏觀風控指揮中心</div>
    """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    #  控制台：7 大導航按鈕
    # ══════════════════════════════════════════════════════════
    st.markdown('<div class="titan-nav-deck">', unsafe_allow_html=True)
    st.markdown('<div class="titan-nav-title">🎛️ SELECT MODULE</div>', unsafe_allow_html=True)

    # Row 1：4 個按鈕
    row1_modules = SUB_MODULES[:4]
    cols_r1 = st.columns(4)
    for col, (code, icon, label) in zip(cols_r1, row1_modules):
        with col:
            if active == code:
                # 選中態：顯示金色卡片
                st.markdown(f"""
                <div class="nav-active-card">
                    <div style="font-size:24px">{icon}</div>
                    <div style="font-size:11px; margin-top:4px">{code}</div>
                    <div style="font-size:14px; font-weight:700">{label}</div>
                </div>""", unsafe_allow_html=True)
            else:
                if st.button(f"{icon}\n{code} {label}", key=f"nav_{code}",
                             use_container_width=True):
                    st.session_state.tab1_active = code
                    st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Row 2：3 個按鈕 + 空欄
    row2_modules = SUB_MODULES[4:]
    cols_r2 = st.columns(4)
    for i, (code, icon, label) in enumerate(row2_modules):
        with cols_r2[i]:
            if active == code:
                st.markdown(f"""
                <div class="nav-active-card">
                    <div style="font-size:24px">{icon}</div>
                    <div style="font-size:11px; margin-top:4px">{code}</div>
                    <div style="font-size:14px; font-weight:700">{label}</div>
                </div>""", unsafe_allow_html=True)
            else:
                if st.button(f"{icon}\n{code} {label}", key=f"nav_{code}",
                             use_container_width=True):
                    st.session_state.tab1_active = code
                    st.rerun()
    # 第四欄空白（美觀佔位）
    with cols_r2[3]:
        st.markdown("<div style='min-height:72px'></div>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # .titan-nav-deck

    # ══════════════════════════════════════════════════════════
    #  內容區：只渲染選中的子模組
    # ══════════════════════════════════════════════════════════
    st.markdown('<div class="titan-content-area">', unsafe_allow_html=True)
    render_fn = RENDER_MAP.get(active)
    if render_fn:
        try:
            render_fn()
        except Exception as e:
            import traceback
            st.error(f"❌ 子模組 {active} 渲染失敗: {e}")
            with st.expander("🔍 錯誤詳情"):
                st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)  # .titan-content-area
