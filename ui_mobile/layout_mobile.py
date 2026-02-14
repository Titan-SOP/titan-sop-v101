# ui_mobile/layout_mobile.py
# Titan SOP V100.0 — Mobile UI Layout
# 手機版：精簡化、觸控優化、單欄佈局

import streamlit as st
import pandas as pd
from datetime import datetime

from data_engine import load_cb_data_from_upload
from utils_ui import inject_css


# ═══════════════════════════════════════════════════════════════
#  手機版 CSS
# ═══════════════════════════════════════════════════════════════
MOBILE_CSS = """
<style>
    /* 背景 */
    .stApp { background-color: #0d0d0d; }

    /* 主標題 */
    .mobile-title {
        text-align: center;
        color: #00FF00;
        text-shadow: 0 0 8px #00FF00;
        font-size: 1.4em;
        font-weight: bold;
        padding: 8px 0;
    }

    /* 手機版 metric 卡片 */
    [data-testid="metric-container"] {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 8px;
    }

    /* 觸控按鈕放大 */
    .stButton > button {
        min-height: 48px;
        font-size: 15px;
        border-radius: 10px;
    }

    /* 精簡 expander */
    .streamlit-expanderHeader {
        font-size: 14px;
        padding: 8px 12px;
    }

    /* 單欄模式 */
    @media (max-width: 640px) {
        .row-widget.stHorizontal > div { flex: 100% !important; }
    }

    /* 數據表格字體 */
    .dataframe td, .dataframe th { font-size: 12px !important; }

    /* 隱藏多餘元素 */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
    header    { visibility: hidden; }
</style>
"""


# ═══════════════════════════════════════════════════════════════
#  手機版各模組
# ═══════════════════════════════════════════════════════════════

def _mobile_upload_sidebar():
    """側邊欄：上傳 CB 清單"""
    with st.sidebar:
        st.markdown("### ⚙️ 設定")
        f = st.file_uploader("📂 CB 清單 (Excel/CSV)", type=['csv','xlsx'])
        if f:
            df = load_cb_data_from_upload(f)
            if df is not None and not df.empty:
                st.session_state['df'] = df
                st.success(f"✅ {len(df)} 筆 CB")
        st.divider()
        st.session_state['api_key'] = st.text_input("🔑 Gemini Key (選填)", type="password",
                                                      value=st.session_state.get('api_key',''))
        intel = st.file_uploader("📎 情報文件 (PDF/TXT)", type=['pdf','txt'], accept_multiple_files=True)
        st.session_state['intel_files'] = intel or []


# ─────────────────────────────────────────────────────────────
# 手機版首頁：磚塊導航
# ─────────────────────────────────────────────────────────────
def _mobile_home():
    st.markdown('<div class="mobile-title">🏛️ Titan SOP V100</div>', unsafe_allow_html=True)
    st.caption("全自動戰情室 | 手機版")
    st.divider()

    PAGES = [
        ("🛡️ 宏觀大盤", "macro"),
        ("🏹 獵殺雷達", "radar"),
        ("🎯 單兵狙擊", "sniper"),
        ("🚀 全球決策", "decision"),
        ("📚 戰略百科", "wiki"),
        ("🧠 元趨勢",   "meta"),
    ]
    for i in range(0, len(PAGES), 2):
        c1, c2 = st.columns(2)
        for col, (label, page) in zip([c1, c2], PAGES[i:i+2]):
            with col:
                if st.button(label, use_container_width=True, key=f"nav_{page}"):
                    st.session_state['mobile_page'] = page
                    st.rerun()


# ─────────────────────────────────────────────────────────────
# 手機版 Tab 1：宏觀大盤（精簡版）
# ─────────────────────────────────────────────────────────────
def _mobile_macro():
    st.markdown("### 🛡️ 宏觀大盤")
    if st.button("← 返回", key="back_macro"):
        st.session_state['mobile_page'] = 'home'; st.rerun()
    st.divider()
    try:
        from tab1_macro import render as r1
        r1()
    except Exception as e:
        st.warning(f"宏觀模組載入中…({e})")


# ─────────────────────────────────────────────────────────────
# 手機版 Tab 2：獵殺雷達（精簡版）
# ─────────────────────────────────────────────────────────────
def _mobile_radar():
    st.markdown("### 🏹 獵殺雷達")
    if st.button("← 返回", key="back_radar"):
        st.session_state['mobile_page'] = 'home'; st.rerun()
    st.divider()

    df = st.session_state.get('df', pd.DataFrame())
    if df.empty:
        st.info("請在側欄上傳 CB 清單。"); return

    # 精簡掃描結果展示
    if 'scan_results' in st.session_state and not st.session_state['scan_results'].empty:
        sr = st.session_state['scan_results']
        st.success(f"✅ SOP 黃金清單：{len(sr)} 檔")
        cols = [c for c in ['name','price','trend_status','score'] if c in sr.columns]
        st.dataframe(sr[cols].head(15), use_container_width=True)
        st.caption("詳細分析請切換至桌面版查看 K 線圖")
    else:
        st.info("尚未掃描，請切換至桌面版執行全市場普查。")

    # 快速風險雷達
    if 'full_census_data' in st.session_state:
        st.subheader("⚠️ 快速風險提示")
        full = pd.DataFrame(st.session_state['full_census_data'])
        loose = full[pd.to_numeric(full.get('conv_rate', pd.Series()), errors='coerce') > 30]
        if not loose.empty:
            st.warning(f"籌碼鬆動 (轉換率>30%)：{len(loose)} 檔")
            st.dataframe(loose[['name','conv_rate']].head(5), use_container_width=True)


# ─────────────────────────────────────────────────────────────
# 手機版 Tab 3：單兵狙擊（精簡版）
# ─────────────────────────────────────────────────────────────
def _mobile_sniper():
    st.markdown("### 🎯 單兵狙擊")
    if st.button("← 返回", key="back_sniper"):
        st.session_state['mobile_page'] = 'home'; st.rerun()
    st.divider()

    import yfinance as yf
    ticker_in = st.text_input("輸入代號", value="2330", key="m_sniper_ticker").strip()
    if not ticker_in:
        return

    cands = [f"{ticker_in}.TW", f"{ticker_in}.TWO"] if ticker_in.isdigit() else [ticker_in.upper()]
    sdf = pd.DataFrame()
    with st.spinner("下載中…"):
        for c in cands:
            try:
                tmp = yf.download(c, period="1y", progress=False)
                if not tmp.empty:
                    sdf = tmp; break
            except Exception:
                pass

    if sdf.empty:
        st.error("查無數據"); return

    if isinstance(sdf.columns, pd.MultiIndex):
        sdf.columns = sdf.columns.get_level_values(0)
    sdf['MA87']  = sdf['Close'].rolling(87).mean()
    sdf['MA284'] = sdf['Close'].rolling(284).mean()

    cp    = float(sdf['Close'].iloc[-1])
    m87   = float(sdf['MA87'].iloc[-1])  if not pd.isna(sdf['MA87'].iloc[-1])  else 0
    m284  = float(sdf['MA284'].iloc[-1]) if not pd.isna(sdf['MA284'].iloc[-1]) else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("現價",    f"{cp:.1f}")
    c2.metric("87MA",   f"{m87:.1f}",  f"{cp-m87:.1f}")
    c3.metric("284MA",  f"{m284:.1f}", f"{cp-m284:.1f}")

    trend = "✅ 中期多頭" if m87 > m284 else "❌ 空頭整理"
    bias  = ((cp - m87) / m87 * 100) if m87 > 0 else 0
    st.markdown(f"**趨勢狀態**: {trend} | **乖離率**: {bias:.1f}%")

    # 精簡 K 線（Altair）
    import altair as alt
    recent = sdf.tail(60).reset_index()
    base   = alt.Chart(recent).encode(x='Date:T')
    bars   = (base.mark_rule().encode(y=alt.Y('Low', scale=alt.Scale(zero=False)), y2='High') +
              base.mark_bar().encode(y='Open', y2='Close',
                  color=alt.condition("datum.Open<=datum.Close", alt.value("#FF4B4B"), alt.value("#26A69A"))))
    l87  = base.mark_line(color='orange', strokeWidth=1.5).encode(y='MA87')
    l284 = base.mark_line(color='#00bfff', strokeWidth=1.5).encode(y='MA284')
    st.altair_chart((bars + l87 + l284).properties(height=260).interactive(), use_container_width=True)
    st.caption("🔶 87MA | 🔷 284MA")


# ─────────────────────────────────────────────────────────────
# 手機版 Tab 4：全球決策（精簡版）
# ─────────────────────────────────────────────────────────────
def _mobile_decision():
    st.markdown("### 🚀 全球決策")
    if st.button("← 返回", key="back_decision"):
        st.session_state['mobile_page'] = 'home'; st.rerun()
    st.divider()

    # 簡化版投資組合
    pf = st.session_state.get('portfolio_df', pd.DataFrame())
    if pf.empty:
        st.info("請在桌面版設定投資組合 (4.1)"); return

    import yfinance as yf
    tickers = pf['資產代號'].tolist()
    try:
        prices = yf.download(tickers, period="1d", progress=False)['Close'].iloc[-1]
        pf = pf.copy()
        pf['現價']    = pf['資產代號'].map(prices.to_dict() if hasattr(prices, 'to_dict') else {}).fillna(1.0)
        pf['市值']    = pf['持有數量 (股)'] * pf['現價']
        pf['損益']    = (pf['現價'] - pf['買入均價']) * pf['持有數量 (股)']
        total = pf['市值'].sum()
        st.metric("總資產", f"{total:,.0f}")
        st.dataframe(pf[['資產代號','市值','損益']].style.format({'市值': '{:,.0f}', '損益': '{:+,.0f}'}),
                     use_container_width=True)
    except Exception as e:
        st.warning(f"市價載入失敗: {e}")
        st.dataframe(pf[['資產代號','持有數量 (股)','買入均價']], use_container_width=True)


# ─────────────────────────────────────────────────────────────
# 手機版 Tab 5：戰略百科（精簡版）
# ─────────────────────────────────────────────────────────────
def _mobile_wiki():
    st.markdown("### 📚 戰略百科")
    if st.button("← 返回", key="back_wiki"):
        st.session_state['mobile_page'] = 'home'; st.rerun()
    st.divider()

    with st.expander("⚔️ 4 大天條速查"):
        st.markdown("""
1. **價格 < 120** (理想 105~115)
2. **87MA > 284MA** (中期多頭)
3. **身分**：領頭羊 / 風口豬
4. **故事**：從無到有 / 擴產 / 政策
        """)

    with st.expander("💰 CBAS 槓桿試算"):
        cb_p = st.number_input("CB 市價", 100.0, 200.0, 110.0, 0.5)
        prem = cb_p - 100
        if prem > 0:
            lev = cb_p / prem
            st.metric("槓桿倍數", f"{lev:.2f}x")
            st.metric("權利金",   f"{prem:.2f} 元")

    with st.expander("📅 關鍵時間窗口"):
        st.markdown("""
- **0-90天** → 蜜月期，進場甜蜜點
- **350-420天** → 滿年沈澱，突破買點
- **距賣回<180天** → 保衛期，下檔有限
        """)


# ─────────────────────────────────────────────────────────────
# 手機版 Tab 6：元趨勢（精簡版）
# ─────────────────────────────────────────────────────────────
def _mobile_meta():
    st.markdown("### 🧠 元趨勢戰法")
    if st.button("← 返回", key="back_meta"):
        st.session_state['mobile_page'] = 'home'; st.rerun()
    st.divider()

    import yfinance as yf
    import numpy as np
    from scipy.stats import linregress

    ticker = st.text_input("輸入標的", value=st.session_state.get('meta_target','2330'), key="m_meta_t").strip()
    if st.button("📐 掃描", type="primary", key="m_meta_scan"):
        cands = [f"{ticker}.TW", f"{ticker}.TWO"] if ticker.isdigit() else [ticker.upper()]
        with st.spinner("計算幾何數據…"):
            for c in cands:
                try:
                    df = yf.download(c, start="1990-01-01", progress=False, auto_adjust=True)
                    if not df.empty:
                        if isinstance(df.columns, pd.MultiIndex):
                            df.columns = df.columns.get_level_values(0)
                        monthly = df.resample('M').agg({'Close':'last'}).dropna()
                        st.session_state['m_monthly'] = monthly
                        st.session_state['meta_target'] = ticker
                        break
                except Exception:
                    pass

    if 'm_monthly' in st.session_state:
        monthly = st.session_state['m_monthly']
        periods = {'35Y':420,'10Y':120,'5Y':60,'3Y':36,'1Y':12,'6M':6,'3M':3}
        results = {}
        for label, months in periods.items():
            sl = monthly.iloc[-months:] if len(monthly) >= months else monthly
            if len(sl) < 3:
                results[label] = 0; continue
            lp = np.log(sl['Close'].values)
            slope, _, rv, _, _ = linregress(np.arange(len(lp)), lp)
            results[label] = round(np.arctan(slope*100)*(180/np.pi), 1)

        st.subheader("📐 7D 幾何角度")
        for label, angle in results.items():
            color = "🟢" if angle > 15 else ("🔴" if angle < -15 else "🟡")
            st.markdown(f"{color} **{label}**: {angle:+.1f}°")

        acc = results.get('3M', 0) - results.get('1Y', 0)
        st.metric("⚡ 加速度", f"{acc:+.1f}°")

        if results.get('10Y', 0) < 0 and results.get('3M', 0) > 25:
            st.success("🔥 **Phoenix 浴火重生信號觸發！**長空短多逆轉")
        elif results.get('3M', 0) > 45:
            st.success("🚀 短期強勢！3M 角度超過 45°")
        elif results.get('1Y', 0) > 30:
            st.info("✅ 中期健康多頭")
        else:
            st.warning("整理/空頭區間，謹慎操作")


# ═══════════════════════════════════════════════════════════════
#  手機版主渲染入口
# ═══════════════════════════════════════════════════════════════
def render():
    """手機版主入口"""
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)
    _mobile_upload_sidebar()

    if 'mobile_page' not in st.session_state:
        st.session_state['mobile_page'] = 'home'

    page = st.session_state['mobile_page']

    dispatch = {
        'home':     _mobile_home,
        'macro':    _mobile_macro,
        'radar':    _mobile_radar,
        'sniper':   _mobile_sniper,
        'decision': _mobile_decision,
        'wiki':     _mobile_wiki,
        'meta':     _mobile_meta,
    }
    dispatch.get(page, _mobile_home)()
