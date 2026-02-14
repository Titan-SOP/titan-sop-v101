# ui_desktop/tab6_metatrend.py
# Titan SOP V100.0 — Tab 6: 元趨勢戰法
# [靈魂注入 V90.3 PROJECT VALKYRIE → V100.0]
# 完整移植：
#   6 子分頁: 全球視野 / 個股深鑽 / 獵殺清單 / 全境獵殺 / 宏觀對沖 / 回測沙盒
#   7D 幾何引擎 (35Y/10Y/5Y/3Y/1Y/6M/3M)
#   22 階泰坦信評系統
#   瓦爾基里自動情報 (Yahoo Finance)
#   TitanAgentCouncil 戰略提示詞生成器

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import altair as alt
from datetime import datetime, timedelta
from scipy.stats import linregress
import io

# ── 嘗試導入可選依賴 ─────────────────────────────────────────────────────────
try:
    import google.generativeai as genai
    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False

# ── V100 配置導入 ─────────────────────────────────────────────────────────────
try:
    from config import WAR_THEATERS
except ImportError:
    WAR_THEATERS = {
        "🇺🇸 美股科技": ["NVDA","TSLA","PLTR","META","GOOG","MSFT","AMZN","AAPL"],
        "🇹🇼 台股半導體": ["2330.TW","2303.TW","2454.TW","3711.TW","6531.TW"],
        "🌏 全球 ETF":    ["SPY","QQQ","SOXX","FXI","EWZ"],
    }


# ═══════════════════════════════════════════════════════════════
# [SLOT-6.1] 數據引擎
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def _download_monthly(ticker: str) -> pd.DataFrame | None:
    """下載全歷史月K，支援台股雙軌 (.TW/.TWO)"""
    orig = ticker
    if ticker.isdigit() and len(ticker) >= 4:
        ticker = f"{ticker}.TW"
    try:
        df = yf.download(ticker, start="1990-01-01", progress=False, auto_adjust=True)
        if df.empty and orig.isdigit():
            df = yf.download(f"{orig}.TWO", start="1990-01-01", progress=False, auto_adjust=True)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        # 存日K供圖表用
        if 'daily_price_data' not in st.session_state:
            st.session_state.daily_price_data = {}
        st.session_state.daily_price_data[orig] = df
        monthly = df.resample('M').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
        return monthly
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════
# [SLOT-6.2] 數學引擎
# ═══════════════════════════════════════════════════════════════
def _geometry_slice(df: pd.DataFrame, months: int) -> dict:
    sl = df.iloc[-months:] if len(df) >= months else df
    if len(sl) < 3: return {'angle': 0, 'r2': 0, 'slope': 0}
    lp = np.log(sl['Close'].values)
    x  = np.arange(len(lp))
    slope, _, r_val, _, _ = linregress(x, lp)
    angle = float(np.clip(np.arctan(slope * 100) * (180 / np.pi), -90, 90))
    return {'angle': round(angle, 2), 'r2': round(r_val**2, 4), 'slope': round(slope, 6)}

def _compute_7d(ticker: str) -> dict | None:
    df = _download_monthly(ticker)
    if df is None: return None
    periods = {'35Y':420,'10Y':120,'5Y':60,'3Y':36,'1Y':12,'6M':6,'3M':3}
    res = {k: _geometry_slice(df, v) for k, v in periods.items()}
    res['acceleration']   = round(res['3M']['angle'] - res['1Y']['angle'], 2)
    res['phoenix_signal'] = (res['10Y']['angle'] < 0) and (res['6M']['angle'] > 25)
    return res


# ═══════════════════════════════════════════════════════════════
# [SLOT-6.3] 22 階泰坦信評引擎
# ═══════════════════════════════════════════════════════════════
def _titan_rating(geo: dict) -> tuple:
    if not geo: return ("N/A","無數據","數據不足","#808080")
    a35=geo['35Y']['angle']; a10=geo['10Y']['angle']; a5=geo['5Y']['angle']
    a1=geo['1Y']['angle'];   a6=geo['6M']['angle'];   a3=geo['3M']['angle']
    r2_1=geo['1Y']['r2'];    r2_3=geo['3M']['r2']
    acc=geo['acceleration']; phx=geo['phoenix_signal']

    if all([a35>45, a10>45, a1>45, a3>45]):        return ("SSS","Titan (泰坦)","全週期超45°，神級標的","#FFD700")
    if a1>40 and a6>45 and a3>50 and acc>20:       return ("AAA","Dominator (統治者)","短期加速向上","#FF4500")
    if phx and a3>30:                              return ("Phoenix","Phoenix (浴火重生)","長空短多逆轉","#FF6347")
    if r2_1>0.95 and 20<a1<40 and acc>0:           return ("Launchpad","Launchpad (發射台)","線性度極高蓄勢","#32CD32")
    if a1>35 and a3>40 and r2_3>0.85:             return ("AA+","Elite (精英)","一年期強勢上攻","#FFA500")
    if a1>30 and a6>35:                            return ("AA","Strong Bull (強多)","中短期穩定上升","#FFD700")
    if a1>25 and a3>30:                            return ("AA-","Steady Bull (穩健多)","趨勢健康向上","#ADFF2F")
    if a6>20 and a3>25:                            return ("A+","Moderate Bull (溫和多)","短期表現良好","#7FFF00")
    if a3>15:                                      return ("A","Weak Bull (弱多)","短期微幅上揚","#98FB98")
    if -5<a3<15 and a1>0:                          return ("BBB+","Neutral+ (中性偏多)","盤整偏多","#F0E68C")
    if -10<a3<10 and -10<a1<10:                    return ("BBB","Neutral (中性)","橫盤震盪","#D3D3D3")
    if -15<a3<5 and a1<0:                          return ("BBB-","Neutral- (中性偏空)","盤整偏弱","#DDA0DD")
    if a1>20 and a3<-10:                           return ("Divergence","Divergence (背離)","創高但動能衰竭","#FF1493")
    if -25<a3<-15 and a1>-10:                      return ("BB+","Weak Bear (弱空)","短期下跌","#FFA07A")
    if -35<a3<-25:                                 return ("BB","Moderate Bear (中等空)","下跌趨勢明確","#FF6347")
    if -45<a3<-35:                                 return ("BB-","Strong Bear (強空)","跌勢凌厲","#DC143C")
    if a3<-45 and a1<-30:                          return ("B+","Severe Bear (重度空)","崩跌模式","#8B0000")
    if a10<-30 and a3<-40:                         return ("B","Depression (蕭條)","長期熊市","#800000")
    if a35<-20 and a10<-35:                        return ("C","Structural Decline (結構衰退)","世代熊市","#4B0082")
    if a3<-60:                                     return ("D","Collapse (崩盤)","極度危險","#000000")
    if a10<-20 and a3>15 and acc>30:               return ("Reversal","Reversal (觸底反彈)","熊市V型反轉","#00CED1")
    return ("N/A","Unknown (未分類)","無法歸類","#808080")


# ═══════════════════════════════════════════════════════════════
# [SLOT-6.x] 瓦爾基里情報局
# ═══════════════════════════════════════════════════════════════
def _valkyrie_report(ticker: str) -> str:
    orig = ticker
    if ticker.isdigit() and len(ticker) >= 4: ticker = f"{ticker}.TW"
    try:
        t    = yf.Ticker(ticker)
        info = t.info or {}
        if not info.get('symbol') and orig.isdigit():
            ticker = f"{orig}.TWO"; t = yf.Ticker(ticker); info = t.info or {}

        def fmt_pct(v): return f"{v*100:.2f}%" if isinstance(v,(int,float)) else str(v)
        def fmt_bn(v):  return f"${v/1e9:.2f}B" if isinstance(v,(int,float)) and v>1e9 else (f"${v/1e6:.2f}M" if isinstance(v,(int,float)) else str(v))

        mc   = fmt_bn(info.get('marketCap','N/A'))
        fcf  = fmt_bn(info.get('freeCashflow','N/A'))
        summ = str(info.get('longBusinessSummary','N/A'))[:300] + "…"
        lines = [
            f"# 🤖 瓦爾基里情報報告 — {ticker}",
            f"**抓取時間**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "", "## 📊 基本面",
            f"**市值**: {mc} | **現價**: ${info.get('currentPrice','N/A')} | **Forward PE**: {info.get('forwardPE','N/A')}",
            f"**機構目標價**: ${info.get('targetMeanPrice','N/A')} | **52W高**: ${info.get('fiftyTwoWeekHigh','N/A')} | **52W低**: ${info.get('fiftyTwoWeekLow','N/A')}",
            f"**營收成長**: {fmt_pct(info.get('revenueGrowth','N/A'))} | **毛利率**: {fmt_pct(info.get('grossMargins','N/A'))} | **ROE**: {fmt_pct(info.get('returnOnEquity','N/A'))}",
            f"**自由現金流**: {fcf} | **負債比**: {info.get('debtToEquity','N/A')}",
            f"**產業**: {info.get('industry','N/A')}", "",
            f"**公司簡介**: {summ}", "", "## 📰 最新新聞",
        ]
        news = t.news or []
        for i, n in enumerate(news[:5], 1):
            ts = n.get('providerPublishTime', 0)
            dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d') if ts else 'N/A'
            lines.append(f"{i}. **{n.get('title','N/A')}** — {n.get('publisher','N/A')} ({dt})")
            lines.append(f"   [{n.get('link','#')}]({n.get('link','#')})")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ 情報抓取失敗: {e}\n\n請手動貼上情報。"


# ═══════════════════════════════════════════════════════════════
# [SLOT-6.4] 戰略提示詞生成器 (TitanAgentCouncil)
# ═══════════════════════════════════════════════════════════════
def _generate_battle_prompt(ticker, price, geo, rating, intel, note, principles):
    level, name, desc, _ = rating
    geo_str = "\n".join([
        f"  • {k}: 角度={v['angle']}° | R²={v['r2']}"
        for k, v in geo.items() if isinstance(v, dict)
    ])
    return f"""# TITAN BATTLE ORDER — {ticker}
## 信評: {level} — {name} ({desc})
## 現價: {price} | 加速度: {geo.get('acceleration',0)}° | Phoenix: {geo.get('phoenix_signal',False)}

### 7D 幾何儀表板
{geo_str}

### 情報摘要
{intel or '(無情報)'}

### 統帥筆記
{note or '(無)'}

### 選定第一性原則
{chr(10).join(f'- {p}' for p in (principles or []))}

---
## 🎯 任務簡令

你是由五位頂尖分析師組成的辯論庭。請針對 {ticker} 進行激烈辯論：

1. **幾何死神 (Quant)**: 從 7D 幾何數據判斷趨勢生死
2. **內部人 (Insider)**: 從籌碼/財報找出機構動向
3. **大賣空 (Burry)**: 找出最大的隱藏風險與泡沫
4. **創世紀 (Visionary)**: 描繪 5 年後最瘋狂的牛市劇本
5. **上帝裁決 (Arbiter)**: 綜合所有觀點，給出最終進出場決策

格式要求:
- 每人論述 100-200 字，不得敷衍
- 最終裁決: 明確給出「買/賣/觀望」+ 進場價/目標價/停損價
- 以繁體中文回答
"""


# ═══════════════════════════════════════════════════════════════
# 視覺化輔助：7D 雷達圖 + K線圖
# ═══════════════════════════════════════════════════════════════
def _render_radar(geo: dict, ticker: str):
    categories = ['35Y','10Y','5Y','3Y','1Y','6M','3M']
    angles     = [geo[c]['angle'] for c in categories]
    fig = go.Figure(go.Scatterpolar(
        r=angles, theta=categories,
        fill='toself', fillcolor='rgba(255,165,0,0.25)',
        line=dict(color='orange', width=2),
        name='角度 (°)'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[-90,90])),
        title=f"{ticker} — 7D 幾何雷達圖",
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def _render_monthly_chart(ticker: str, months: int = 120):
    df = st.session_state.get('daily_price_data', {}).get(ticker)
    if df is None: st.warning("無日K數據，請先執行分析。"); return
    if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
    df = df.copy().reset_index()
    date_c = next((c for c in df.columns if str(c).lower() in ['date','index']), None)
    if date_c: df.rename(columns={date_c:'Date'}, inplace=True)
    for c in ['Open','High','Low','Close','Volume']:
        if c not in df.columns: df[c] = df.get('Close', 0)
    df = df.tail(months * 22)  # ~months月的交易日
    df['MA87']  = df['Close'].rolling(87).mean()
    df['MA284'] = df['Close'].rolling(284).mean()
    bk = alt.Chart(df).encode(x=alt.X('Date:T'))
    col = alt.condition("datum.Open<=datum.Close", alt.value("#FF4B4B"), alt.value("#26A69A"))
    candles = (bk.mark_rule().encode(y=alt.Y('Low', scale=alt.Scale(zero=False)), y2='High', color=col) +
               bk.mark_bar().encode(y='Open', y2='Close', color=col))
    l87  = bk.mark_line(color='orange', strokeWidth=2).encode(y='MA87')
    l284 = bk.mark_line(color='#00bfff', strokeWidth=2).encode(y='MA284')
    st.altair_chart((candles + l87 + l284).interactive().properties(height=400), use_container_width=True)
    st.caption("🔶 橘線: 87MA | 🔷 藍線: 284MA")


# ═══════════════════════════════════════════════════════════════
# 主渲染入口
# ═══════════════════════════════════════════════════════════════
def render():
    """Tab 6: 元趨勢戰法 — 全功能復原版 (V90.3 PROJECT VALKYRIE + V100 外殼)"""

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🌍 全球視野", "🔬 個股深鑽", "🎯 獵殺清單",
        "🚀 全境獵殺", "🛡️ 宏觀對沖", "🧪 回測沙盒"
    ])

    # ════════════════════════════════════════════════════════════
    # Tab 1: 全球視野 — 批次掃描多標的
    # ════════════════════════════════════════════════════════════
    with tab1:
        st.subheader("🌍 全球視野 — 多標的比較掃描")
        st.info("輸入多個代號(逗號分隔)，一鍵取得 7D 幾何信評對比。")

        col_in, col_btn = st.columns([3, 1])
        tickers_raw = col_in.text_input("標的代號", "NVDA,TSLA,2330.TW,2454.TW", key="globe_tickers")
        do_scan = col_btn.button("🔍 掃描", type="primary", key="globe_scan")

        if do_scan and tickers_raw:
            tickers = [t.strip() for t in tickers_raw.split(",") if t.strip()]
            results = []
            prog = st.progress(0); status = st.empty()
            for i, t in enumerate(tickers):
                status.text(f"分析 {t}… ({i+1}/{len(tickers)})")
                geo = _compute_7d(t)
                if geo:
                    rating = _titan_rating(geo)
                    price = 0.0
                    dp = st.session_state.get('daily_price_data', {}).get(
                        t if not t.endswith(('.TW','.TWO')) else t.split('.')[0])
                    if dp is not None and not dp.empty: price = float(dp['Close'].iloc[-1])
                    results.append({
                        '代號': t, '現價': price, '信評': f"{rating[0]} {rating[1]}",
                        '35Y角度': geo['35Y']['angle'], '10Y角度': geo['10Y']['angle'],
                        '1Y角度':  geo['1Y']['angle'],  '3M角度':  geo['3M']['angle'],
                        '加速度': geo['acceleration'], 'Phoenix': '✅' if geo['phoenix_signal'] else '—'
                    })
                prog.progress((i+1)/len(tickers))
            status.text("✅ 掃描完成")
            prog.empty()
            if results:
                res_df = pd.DataFrame(results).sort_values('1Y角度', ascending=False)
                st.dataframe(res_df.style.format({
                    '現價': '{:.2f}', '35Y角度': '{:.1f}°', '10Y角度': '{:.1f}°',
                    '1Y角度': '{:.1f}°', '3M角度': '{:.1f}°', '加速度': '{:+.1f}°'
                }), use_container_width=True)
                st.session_state['globe_scan_results'] = res_df

    # ════════════════════════════════════════════════════════════
    # Tab 2: 個股深鑽 — 完整 7D 分析 + 提示詞生成
    # ════════════════════════════════════════════════════════════
    with tab2:
        st.subheader("🔬 個股深鑽 — 7D 幾何 + 22 階信評 + 戰略提示詞")

        ticker_in = st.text_input("輸入代號", "NVDA", key="deep_ticker").strip()

        if st.button("🚀 啟動深鑽分析", type="primary", key="btn_deep"):
            with st.spinner(f"正在分析 {ticker_in}…"):
                geo    = _compute_7d(ticker_in)
                rating = _titan_rating(geo) if geo else ("N/A","N/A","N/A","#808080")
            st.session_state['deep_geo']    = geo
            st.session_state['deep_rating'] = rating
            st.session_state['deep_ticker'] = ticker_in

        if 'deep_geo' in st.session_state and st.session_state.get('deep_ticker') == ticker_in:
            geo    = st.session_state['deep_geo']
            rating = st.session_state['deep_rating']
            lvl, name, desc, color = rating

            # 信評卡
            st.markdown(f"""
<div style="background:{color};padding:16px;border-radius:10px;text-align:center;">
<h3 style="color:white;margin:0;">{lvl} — {name}</h3>
<p style="color:white;margin:5px 0;">{desc}</p>
</div>""", unsafe_allow_html=True)
            st.write("")

            if geo:
                # 指標表格
                angle_df = pd.DataFrame([
                    {'時間窗口': k, '角度 (°)': v['angle'], 'R²': v['r2']}
                    for k, v in geo.items() if isinstance(v, dict)
                ])
                c1, c2 = st.columns(2)
                c1.dataframe(angle_df, use_container_width=True)
                c2.metric("加速度 (G力)", f"{geo['acceleration']:+.1f}°")
                c2.metric("Phoenix 信號", "✅ 觸發" if geo['phoenix_signal'] else "— 未觸發")
                _render_radar(geo, ticker_in)
                _render_monthly_chart(ticker_in)

            st.divider()
            st.subheader("🤖 戰略提示詞生成器")

            left, right = st.columns(2)
            with left:
                if st.button("🤖 啟動瓦爾基里 (Auto-Fetch)", key="btn_valkyrie"):
                    with st.spinner("抓取情報…"):
                        st.session_state['valkyrie_report'] = _valkyrie_report(ticker_in)
                    st.success("✅ 情報抓取完成！")
                intel_text = st.text_area("情報內容 (可編輯)",
                                          value=st.session_state.get('valkyrie_report',''),
                                          height=200, key="intel_text_deep")
                note = st.text_area("統帥筆記", height=80, key="note_deep",
                                    placeholder="補充分析指令…")

            PRINCIPLES = [
                "[成長] 萊特定律檢視：產量翻倍，成本是否下降 15%？",
                "[成長] 非線性爆發點：用戶/算力是否指數成長？",
                "[成長] TAM 邊界測試：若已達 80%，為何還要買？",
                "[生存] 燒錢率測試：18 個月融不到資，會死嗎？",
                "[生存] 自由現金流真偽：扣 SBC 後真的有賺嗎？",
                "[泡沫] 均值回歸引力：利潤率回歸平均會腰斬嗎？",
                "[泡沫] 敘事與現實乖離：CEO 提 AI 次數 vs 實際佔比。",
                "[泡沫] 內部人逃生：高管是在買進還是賣出？",
                "[終極] 不可替代性：若明天消失，世界有差嗎？",
                "[終極] 百倍股基因：2033 年活著，它會變成什麼？"
            ]
            with right:
                sel_p = st.multiselect("第一性原則", PRINCIPLES, key="principles_deep")

            if st.button("📋 生成戰略提示詞", type="primary", key="gen_prompt"):
                p = st.session_state.get('daily_price_data', {})
                price = 0.0
                for k, v in p.items():
                    if ticker_in.split('.')[0] in k and v is not None and not v.empty:
                        price = float(v['Close'].iloc[-1]); break
                prompt = _generate_battle_prompt(ticker_in, price, geo or {}, rating, intel_text, note, sel_p)
                st.session_state['battle_prompt'] = prompt
                st.success("✅ 提示詞已生成！")

            if 'battle_prompt' in st.session_state:
                st.text_area("📋 複製此提示詞", value=st.session_state['battle_prompt'],
                             height=350, key="prompt_out")
                st.download_button("💾 下載提示詞",
                                   st.session_state['battle_prompt'],
                                   file_name=f"TITAN_{ticker_in}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                                   use_container_width=True)

    # ════════════════════════════════════════════════════════════
    # Tab 3: 獵殺清單 (V90.3 動態戰果追蹤)
    # ════════════════════════════════════════════════════════════
    with tab3:
        st.subheader("🎯 獵殺清單 (Kill List)")
        st.caption("V90.3 升級：手動錄入 AI 裁決 + 即時 PnL 追蹤")

        # 錄入介面
        with st.expander("➕ 新增獵殺目標", expanded=False):
            kc1, kc2, kc3 = st.columns(3)
            log_ticker = kc1.text_input("代號", key="kill_ticker")
            log_action = kc2.selectbox("動作", ["Buy","Sell"], key="kill_action")
            log_entry  = kc3.number_input("進場價", min_value=0.0, key="kill_entry", step=0.01)
            kc4, kc5 = st.columns(2)
            log_target = kc4.number_input("目標價", min_value=0.0, key="kill_target", step=0.01)
            log_stop   = kc5.number_input("停損價", min_value=0.0, key="kill_stop",   step=0.01)
            log_note   = st.text_input("理由", key="kill_rationale", placeholder="策略依據…")

            if st.button("✅ 加入清單", key="add_kill"):
                if log_ticker and log_entry > 0:
                    if 'watchlist' not in st.session_state:
                        st.session_state.watchlist = pd.DataFrame(columns=[
                            "Date","Ticker","Action","Entry Price","Target Price",
                            "Stop Loss","Rationale","Status","Current Price","PnL %"
                        ])
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Ticker": log_ticker.upper(),
                        "Action": log_action,
                        "Entry Price": log_entry,
                        "Target Price": log_target,
                        "Stop Loss": log_stop,
                        "Rationale": log_note,
                        "Status": "⏳ Holding",
                        "Current Price": np.nan,
                        "PnL %": np.nan
                    }])
                    st.session_state.watchlist = pd.concat([st.session_state.watchlist, new_row], ignore_index=True)
                    st.success(f"✅ {log_ticker} 已加入獵殺清單！")
                else:
                    st.warning("請輸入有效代號與進場價。")

        st.markdown("---")
        if st.button("🔄 更新最新戰況 (Refresh PnL)", use_container_width=True, key="refresh_kl"):
            if 'watchlist' in st.session_state and not st.session_state.watchlist.empty:
                wl = st.session_state.watchlist.copy()
                tks = wl['Ticker'].unique().tolist()
                try:
                    raw = yf.download(tks, period="1d", progress=False)
                    rows = []
                    for _, row in wl.iterrows():
                        try:
                            cp = float(raw['Close'][row['Ticker']].iloc[-1]) if len(tks)>1 else float(raw['Close'].iloc[-1])
                            row['Current Price'] = cp
                            pnl = ((cp/row['Entry Price'])-1)*100 if row['Action']=='Buy' else ((row['Entry Price']/cp)-1)*100
                            row['PnL %'] = pnl
                            if row['Action']=='Buy':
                                if cp >= row['Target Price']: row['Status'] = '🏆 Win'
                                elif cp <= row['Stop Loss']:  row['Status'] = '💀 Loss'
                                else:                         row['Status'] = '⏳ Holding'
                            else:
                                if cp <= row['Target Price']: row['Status'] = '🏆 Win'
                                elif cp >= row['Stop Loss']:  row['Status'] = '💀 Loss'
                                else:                         row['Status'] = '⏳ Holding'
                        except Exception:
                            pass
                        rows.append(row)
                    st.session_state.watchlist = pd.DataFrame(rows)
                    st.toast("戰況已更新！", icon="🔄")
                except Exception as e:
                    st.error(f"價格更新失敗: {e}")
            else:
                st.info("清單為空。")

        if 'watchlist' in st.session_state and not st.session_state.watchlist.empty:
            wl = st.session_state.watchlist
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("目前持倉", f"{len(wl[wl['Status']=='⏳ Holding'])} 檔")
            m2.metric("勝場",     f"{len(wl[wl['Status']=='🏆 Win'])} 檔")
            m3.metric("敗場",     f"{len(wl[wl['Status']=='💀 Loss'])} 檔")
            m4.metric("平均 PnL", f"{wl['PnL %'].mean():.2f}%" if not wl['PnL %'].isna().all() else "N/A")
            st.dataframe(wl.style.format({
                "Entry Price": "{:.2f}", "Target Price": "{:.2f}",
                "Stop Loss": "{:.2f}", "Current Price": "{:.2f}", "PnL %": "{:+.2f}%"
            }), use_container_width=True)
            if st.button("🗑️ 清空清單", type="secondary", use_container_width=True, key="clear_kl"):
                st.session_state.watchlist = pd.DataFrame(columns=wl.columns)
                st.rerun()
        else:
            st.info("獵殺清單目前無目標。")

    # ════════════════════════════════════════════════════════════
    # Tab 4: 全境獵殺 (WAR_THEATERS 掃描)
    # ════════════════════════════════════════════════════════════
    with tab4:
        st.subheader("🚀 全境獵殺雷達 (The Hunter)")
        st.caption("掃描預設戰區，自動篩選 Phoenix / Awakening / Rocket 型態")

        with st.expander("🎯 獵殺控制台", expanded=True):
            theater = st.selectbox("選擇掃描戰區", list(WAR_THEATERS.keys()), key="theater_sel")
            count   = len(WAR_THEATERS.get(theater, []))
            st.info(f"戰區 **{theater}**，共 **{count}** 檔。")

            if st.button("🚀 啟動全境掃描", type="primary", key="btn_hunt"):
                tickers = WAR_THEATERS[theater]
                results = []
                prog = st.progress(0)
                for i, t in enumerate(tickers):
                    geo = _compute_7d(t)
                    prog.progress((i+1)/len(tickers), text=f"掃描 {t}…")
                    if geo:
                        cp = 0.0
                        dp = st.session_state.get('daily_price_data', {}).get(t.split('.')[0])
                        if dp is not None and not dp.empty: cp = float(dp['Close'].iloc[-1])
                        mt = None
                        if geo['10Y']['angle'] < 10 and geo['3M']['angle'] > 45:     mt = "🔥 Phoenix"
                        elif abs(geo['35Y']['angle']) < 15 and geo['acceleration'] > 20: mt = "🦁 Awakening"
                        elif geo['3M']['angle'] > 60:                                mt = "🚀 Rocket"
                        if mt:
                            results.append({
                                "代號":t, "現價":cp, "35Y角度":geo['35Y']['angle'],
                                "10Y角度":geo['10Y']['angle'], "3M角度":geo['3M']['angle'],
                                "G力":geo['acceleration'], "型態":mt
                            })
                prog.empty()
                st.session_state[f'hunt_{theater}'] = pd.DataFrame(results)
                st.success(f"✅ 掃描完成，發現 **{len(results)}** 個潛在目標！")

        if f'hunt_{theater}' in st.session_state:
            hr = st.session_state[f'hunt_{theater}']
            if not hr.empty:
                st.markdown("### ⚔️ 戰果清單")
                st.dataframe(hr.style.format({
                    "現價": "{:.2f}", "35Y角度": "{:.1f}°",
                    "10Y角度": "{:.1f}°", "3M角度": "{:.1f}°", "G力": "{:+.1f}°"
                }), use_container_width=True)
                csv = hr.to_csv(index=False).encode('utf-8')
                st.download_button("📥 下載戰果 CSV", csv,
                                   file_name=f"hunt_{theater}_{datetime.now().strftime('%Y%m%d')}.csv")

                # 索敵模式
                st.markdown("---")
                st.subheader("🎯 索敵模式 (Target Acquisition)")
                target = st.selectbox("選擇索敵目標", hr['代號'].tolist(), key="hunt_target")
                if st.button("🔍 鎖定目標", type="primary", key="lock_target"):
                    with st.spinner(f"鎖定 {target}…"):
                        tgeo = _compute_7d(target)
                    if tgeo:
                        trating = _titan_rating(tgeo)
                        st.session_state['hunt_tgeo']   = tgeo
                        st.session_state['hunt_trating'] = trating
                        st.session_state['hunt_target_name'] = target
                        st.success(f"✅ 鎖定！信評: **{trating[0]} — {trating[1]}**")

                if 'hunt_tgeo' in st.session_state and st.session_state.get('hunt_target_name') == target:
                    tgeo = st.session_state['hunt_tgeo']
                    trating = st.session_state['hunt_trating']
                    lvl, name, desc, color = trating
                    st.markdown(f"""
<div style="background:{color};padding:12px;border-radius:8px;text-align:center;">
<h3 style="color:white;margin:0;">{lvl} — {name}</h3>
<p style="color:white;margin:4px 0;">{desc}</p>
</div>""", unsafe_allow_html=True)
                    _render_radar(tgeo, target)

                    if st.button("🤖 瓦爾基里情報", key="valk_hunt"):
                        with st.spinner("抓取…"):
                            st.session_state['hunt_valk'] = _valkyrie_report(target)
                    intel_h = st.text_area("情報", value=st.session_state.get('hunt_valk',''),
                                           height=150, key="intel_hunt")
                    note_h  = st.text_input("統帥筆記", key="note_hunt")
                    if st.button("📋 生成提示詞", key="gen_hunt"):
                        dp = st.session_state.get('daily_price_data', {})
                        price_h = 0.0
                        for k,v in dp.items():
                            if target.split('.')[0] in k and v is not None and not v.empty:
                                price_h = float(v['Close'].iloc[-1]); break
                        pt = _generate_battle_prompt(target, price_h, tgeo, trating, intel_h, note_h, [])
                        st.text_area("提示詞", value=pt, height=300, key="hunt_prompt_out")
                        st.download_button("💾 下載", pt,
                                           file_name=f"TITAN_HUNT_{target}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
            else:
                st.info("未發現符合條件的目標，請嘗試其他戰區。")

    # ════════════════════════════════════════════════════════════
    # Tab 5: 宏觀對沖 (開發預覽)
    # ════════════════════════════════════════════════════════════
    with tab5:
        st.subheader("🛡️ 宏觀對沖 (Macro Hedge)")
        st.warning("""**功能預覽**：
- 多資產相關性矩陣
- Beta 對沖策略建議
- 全球市場聯動分析

🚧 此功能正在開發中，敬請期待…""")

    # ════════════════════════════════════════════════════════════
    # Tab 6: 回測沙盒 (開發預覽)
    # ════════════════════════════════════════════════════════════
    with tab6:
        st.subheader("🧪 回測沙盒 (Backtest Sandbox)")
        st.warning("""**功能預覽**：
- 基於 7D 幾何信號的自動化回測
- 動態倉位管理模擬
- 夏普比率與最大回撤計算

🚧 此功能正在開發中，敬請期待…""")
