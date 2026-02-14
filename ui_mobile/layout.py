# ui_mobile/layout_mobile.py
# Titan SOP V100.0 — Mobile UI (完全獨立重設計版)
# ════════════════════════════════════════════════════════════════
# UX 設計原則：
#   1. 底部固定導航列 (App 風格，6 圖示)
#   2. 單欄卡片式佈局，取代寬表格
#   3. 所有功能完整保留，重組為「快查 → 深挖」兩層結構
#   4. 觸控目標 ≥ 48px，圖表高度固定 280px
#   5. 大量掃描功能可在手機執行，含進度條
# ════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy.stats import linregress

from data_engine import load_cb_data_from_upload
from core_logic import compute_7d_geometry, titan_rating_system, download_full_history


# ════════════════════════════════════════════════════════════════
#  CSS：底部導航 + 全局手機樣式
# ════════════════════════════════════════════════════════════════
MOBILE_CSS = """
<style>
/* ── 全局 ── */
.stApp { background-color: #0a0a0a; color: #f0f0f0; font-size: 14px; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stHeader"]  { display: none !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

/* ── 底部導航列 ── */
.m-nav {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 9999;
    background: #111; border-top: 1px solid #333;
    display: flex; justify-content: space-around; align-items: center;
    padding: 6px 0 env(safe-area-inset-bottom, 6px);
}
.m-nav-btn {
    flex: 1; text-align: center; cursor: pointer;
    padding: 4px 0; font-size: 10px; color: #888;
    border: none; background: none; line-height: 1.3;
}
.m-nav-btn.active { color: #00FF00; }
.m-nav-icon { font-size: 20px; display: block; }

/* ── 頁面內容留底部導航空間 ── */
.main .block-container {
    padding-bottom: 80px !important;
    padding-top: 12px !important;
    padding-left: 12px !important;
    padding-right: 12px !important;
    max-width: 100% !important;
}

/* ── 卡片 ── */
.m-card {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 12px; padding: 14px; margin-bottom: 10px;
}
.m-card-title {
    font-size: 12px; color: #888; margin-bottom: 4px;
}
.m-card-value {
    font-size: 22px; font-weight: bold; color: #fff;
}
.m-card-sub { font-size: 12px; color: #aaa; margin-top: 2px; }

/* ── 評級徽章 ── */
.m-rating-badge {
    display: inline-block; padding: 6px 16px;
    border-radius: 20px; font-weight: bold;
    font-size: 15px; text-align: center;
}

/* ── 觸控按鈕 ── */
.stButton > button {
    min-height: 48px; font-size: 14px;
    border-radius: 10px; width: 100%;
}
.stButton > button[kind="primary"] { background: #00AA44 !important; }

/* ── 表格精簡 ── */
.dataframe td, .dataframe th { font-size: 11px !important; padding: 4px 6px !important; }

/* ── Metric ── */
[data-testid="metric-container"] {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 10px; padding: 8px 12px;
}
[data-testid="stMetricValue"] { font-size: 18px !important; }
[data-testid="stMetricLabel"] { font-size: 11px !important; }

/* ── Expander ── */
.streamlit-expanderHeader { min-height: 44px; font-size: 13px; }

/* ── 頁面標題 ── */
.m-page-title {
    font-size: 18px; font-weight: bold; color: #00FF00;
    margin: 0 0 12px 0; display: flex; align-items: center; gap: 8px;
}

/* ── 訊號燈 ── */
.m-signal { border-radius: 10px; padding: 14px; text-align: center; margin-bottom: 12px; }

/* ── 底部間距 ── */
.m-spacer { height: 20px; }
</style>
"""


# ════════════════════════════════════════════════════════════════
#  底部導航列（HTML + st.button 混合實作）
# ════════════════════════════════════════════════════════════════
NAV_ITEMS = [
    ("🛡️", "宏觀",  "macro"),
    ("🏹", "雷達",  "radar"),
    ("🎯", "狙擊",  "sniper"),
    ("🚀", "決策",  "decision"),
    ("📚", "百科",  "wiki"),
    ("🧠", "元趨勢", "meta"),
]

def _render_bottom_nav():
    cur = st.session_state.get('mobile_page', 'macro')
    cols = st.columns(len(NAV_ITEMS))
    for col, (icon, label, page) in zip(cols, NAV_ITEMS):
        with col:
            style = "background:#1a1a1a; border:1px solid #00FF00;" if cur == page else "background:#111; border:1px solid #333;"
            color = "#00FF00" if cur == page else "#888"
            if st.button(f"{icon}\n{label}", key=f"nav_{page}",
                         help=label, use_container_width=True):
                st.session_state['mobile_page'] = page
                st.rerun()


# ════════════════════════════════════════════════════════════════
#  側邊欄（隱藏，改用 Streamlit secrets 或 session）
#  上傳功能改為內嵌在各頁面頂部的折疊區
# ════════════════════════════════════════════════════════════════
def _upload_zone():
    """每頁頂部的快速上傳/設定折疊區"""
    df_cur = st.session_state.get('df', pd.DataFrame())
    label  = f"⚙️ 設定　✅{len(df_cur)}筆CB" if not df_cur.empty else "⚙️ 設定 (點此上傳CB清單)"
    with st.expander(label, expanded=df_cur.empty):
        f = st.file_uploader("CB 清單 (Excel/CSV)", type=['csv','xlsx'], label_visibility="collapsed")
        if f:
            with st.spinner("解析中…"):
                df = load_cb_data_from_upload(f)
                if df is not None and not df.empty:
                    st.session_state['df'] = df
                    st.success(f"✅ 載入 {len(df)} 筆")
                    st.rerun()
        st.divider()
        key = st.text_input("Gemini Key (選填)", type="password",
                            value=st.session_state.get('api_key',''), label_visibility="collapsed",
                            placeholder="Gemini API Key（用於AI分析）")
        if key: st.session_state['api_key'] = key
        intel = st.file_uploader("情報文件 (PDF/TXT)", type=['pdf','txt'],
                                  accept_multiple_files=True, label_visibility="collapsed")
        if intel: st.session_state['intel_files'] = intel


# ════════════════════════════════════════════════════════════════
#  輔助函式
# ════════════════════════════════════════════════════════════════
def _metric_card(title, value, sub="", color="#fff"):
    st.markdown(f"""
    <div class="m-card">
        <div class="m-card-title">{title}</div>
        <div class="m-card-value" style="color:{color}">{value}</div>
        {"<div class='m-card-sub'>" + sub + "</div>" if sub else ""}
    </div>""", unsafe_allow_html=True)

def _signal_box(text, bg="#1a3a1a", color="#00FF00"):
    st.markdown(f'<div class="m-signal" style="background:{bg};color:{color};font-size:16px;font-weight:bold">{text}</div>',
                unsafe_allow_html=True)

def _download_stock(ticker_raw, period="1y"):
    """下載股票日K，自動處理台股雙軌"""
    cands = ([f"{ticker_raw}.TW", f"{ticker_raw}.TWO"]
             if ticker_raw.isdigit() and len(ticker_raw) >= 4
             else [ticker_raw.upper()])
    for c in cands:
        try:
            df = yf.download(c, period=period, progress=False, auto_adjust=True)
            if not df.empty:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                return df
        except Exception:
            pass
    return pd.DataFrame()

def _mini_candle(df, height=280, title=""):
    """輕量 Altair K 線圖（手機尺寸）"""
    recent = df.tail(60).copy().reset_index()
    if 'Date' not in recent.columns and recent.columns[0] != 'Date':
        recent = recent.rename(columns={recent.columns[0]: 'Date'})
    recent['MA87']  = df['Close'].rolling(87).mean().tail(60).values
    recent['MA284'] = df['Close'].rolling(284).mean().tail(60).values
    base  = alt.Chart(recent).encode(x=alt.X('Date:T', axis=alt.Axis(format='%m/%d', tickCount=6)))
    rules = base.mark_rule(color='#888').encode(
        y=alt.Y('Low:Q', scale=alt.Scale(zero=False), title=''), y2='High:Q')
    bars  = base.mark_bar().encode(
        y='Open:Q', y2='Close:Q',
        color=alt.condition('datum.Open<=datum.Close', alt.value('#FF4B4B'), alt.value('#26A69A')))
    l87  = base.mark_line(color='#FFA500', strokeWidth=1.5).encode(y='MA87:Q')
    l284 = base.mark_line(color='#00BFFF', strokeWidth=1.5).encode(y='MA284:Q')
    chart = (rules + bars + l87 + l284).properties(
        height=height, title=alt.TitleParams(title, fontSize=12)
    ).configure_axis(
        gridColor='#222', domainColor='#444', labelColor='#888', titleColor='#888'
    ).configure_view(strokeWidth=0).interactive()
    st.altair_chart(chart, use_container_width=True)
    st.caption("🟠 87MA   🔵 284MA")


# ════════════════════════════════════════════════════════════════
#  PAGE 1: 宏觀大盤
# ════════════════════════════════════════════════════════════════
def _page_macro():
    st.markdown('<div class="m-page-title">🛡️ 宏觀大盤</div>', unsafe_allow_html=True)
    _upload_zone()

    # 直接呼叫桌面版 render（宏觀大盤天然單欄）
    try:
        from tab1_macro import render as r1
        r1()
    except Exception as e:
        st.error(f"載入失敗: {e}")
        # Fallback：手動顯示關鍵指標
        _macro_fallback()

def _macro_fallback():
    """宏觀大盤 Fallback：手動抓取關鍵指數"""
    INDICES = {
        "S&P 500": "^GSPC", "Nasdaq": "^IXIC",
        "台股加權": "^TWII", "恐慌指數(VIX)": "^VIX",
    }
    st.subheader("📊 全球指數快覽")
    for name, sym in INDICES.items():
        try:
            d = yf.download(sym, period="2d", progress=False)
            if not d.empty and isinstance(d.columns, pd.MultiIndex):
                d.columns = d.columns.get_level_values(0)
            if d.empty: continue
            cp = float(d['Close'].iloc[-1])
            pp = float(d['Close'].iloc[-2]) if len(d) > 1 else cp
            chg = (cp - pp) / pp * 100
            color = "#00FF00" if chg >= 0 else "#FF4444"
            _metric_card(name, f"{cp:,.2f}", f"{chg:+.2f}%", color)
        except Exception:
            pass


# ════════════════════════════════════════════════════════════════
#  PAGE 2: 獵殺雷達（完整功能，手機 UX）
# ════════════════════════════════════════════════════════════════
def _page_radar():
    st.markdown('<div class="m-page-title">🏹 獵殺雷達</div>', unsafe_allow_html=True)
    _upload_zone()
    df = st.session_state.get('df', pd.DataFrame())
    if df.empty:
        st.info("請上傳 CB 清單後使用此功能"); return

    # ── 2.1 SOP 自動獵殺掃描 ──────────────────────────────────────
    with st.expander("🔍 2.1 SOP 黃金掃描", expanded=True):
        if st.button("🚀 啟動全市場掃描", type="primary", key="m_radar_scan"):
            try:
                from tab2_radar import _run_census
                with st.spinner("掃描全市場 CB…"):
                    results = _run_census(df, min_score=40)
                    st.session_state['scan_results'] = results
            except Exception as e:
                # fallback：本地輕量掃描
                with st.spinner("掃描中（輕量模式）…"):
                    _mobile_quick_scan(df)

        if 'scan_results' in st.session_state:
            sr = st.session_state['scan_results']
            if hasattr(sr, '__len__') and len(sr) > 0:
                df_sr = pd.DataFrame(sr) if isinstance(sr, list) else sr
                st.success(f"✅ 找到 {len(df_sr)} 檔潛力標的")
                _render_cb_cards_mobile(df_sr)
            else:
                st.info("無符合條件的標的")

    # ── 2.2 核心策略檢核 ──────────────────────────────────────────
    with st.expander("📋 2.2 核心策略檢核"):
        try:
            from tab2_radar import render as r2_full
            # 只渲染策略檢核部分
            st.info("切換至桌面版可查看完整 K 線圖與詳細報告")
            _mobile_strategy_check(df)
        except Exception:
            _mobile_strategy_check(df)

    # ── 2.3 風險雷達 ──────────────────────────────────────────────
    with st.expander("⚠️ 2.3 潛在風險雷達"):
        _mobile_risk_radar(df)

    # ── 2.4 資金配置試算 ──────────────────────────────────────────
    with st.expander("💰 2.4 資金配置試算"):
        total_funds = st.number_input("可動用資金 (元)", value=500000, step=50000, format="%d")
        if 'scan_results' in st.session_state:
            sr = st.session_state['scan_results']
            df_sr = pd.DataFrame(sr) if isinstance(sr, list) else sr
            if not df_sr.empty and 'price' in df_sr.columns:
                top5 = df_sr.head(5)
                alloc = total_funds / len(top5) if len(top5) > 0 else 0
                for _, row in top5.iterrows():
                    price = float(row.get('price', 100))
                    lots  = int(alloc / (price * 1000)) if price > 0 else 0
                    _metric_card(
                        row.get('name', row.get('code','')),
                        f"建議 {lots} 張",
                        f"市價 {price:.1f}元 | 配置 {alloc:,.0f}元"
                    )
        else:
            st.info("請先執行掃描")


def _mobile_quick_scan(df):
    """輕量本地掃描（不呼叫 yfinance，純 CB 數據過濾）"""
    work = df.copy()
    price_col = next((c for c in ['close','price','cb_price'] if c in work.columns), None)
    conv_col  = next((c for c in ['conv_rate','converted_ratio','已轉換比例'] if c in work.columns), None)

    if price_col:
        work[price_col] = pd.to_numeric(work[price_col], errors='coerce')
        work = work[work[price_col] < 120]
    results = work.head(20).to_dict('records')
    st.session_state['scan_results'] = results
    st.success(f"✅ 輕量掃描完成，找到 {len(results)} 筆候選")


def _render_cb_cards_mobile(df_sr):
    """以卡片形式顯示 CB 掃描結果"""
    price_col = next((c for c in ['price','close','cb_price'] if c in df_sr.columns), None)
    name_col  = next((c for c in ['name','名稱'] if c in df_sr.columns), None)
    trend_col = next((c for c in ['trend_status','trend'] if c in df_sr.columns), None)
    score_col = next((c for c in ['score','分數'] if c in df_sr.columns), None)

    for _, row in df_sr.head(15).iterrows():
        name  = row.get(name_col, row.get('code','')) if name_col else str(row.get('code',''))
        price = f"{float(row[price_col]):.1f}" if price_col and pd.notna(row.get(price_col)) else "N/A"
        trend = row.get(trend_col, '') if trend_col else ''
        score = f"{row[score_col]:.0f}分" if score_col and pd.notna(row.get(score_col)) else ''
        color = "#00FF00" if "多頭" in str(trend) else "#888"
        _metric_card(name, price + " 元", f"{trend}　{score}", color)


def _mobile_strategy_check(df):
    """簡化版策略檢核（4大天條 + 篩選）"""
    price_col  = next((c for c in ['close','price'] if c in df.columns), None)
    conv_col   = next((c for c in ['conv_rate','converted_ratio'] if c in df.columns), None)
    name_col   = next((c for c in ['name','名稱'] if c in df.columns), None)

    if price_col is None:
        st.warning("CB 清單缺少市價欄位"); return

    df2 = df.copy()
    df2[price_col] = pd.to_numeric(df2[price_col], errors='coerce')

    # 天條 1: 價格
    ok = df2[df2[price_col] < 120]
    st.metric("符合天條①價格<120", f"{len(ok)} 檔", f"全部{len(df2)}檔")

    # 天條 2: 轉換率
    if conv_col:
        df2[conv_col] = pd.to_numeric(df2[conv_col], errors='coerce')
        ok2 = df2[(df2[price_col] < 120) & (df2[conv_col] < 30)]
        st.metric("符合天條①②（+轉換率<30%）", f"{len(ok2)} 檔")
        names = ok2[name_col].head(8).tolist() if name_col else []
        if names:
            st.caption("候選標的: " + " / ".join(str(n) for n in names))


def _mobile_risk_radar(df):
    """風險雷達：籌碼鬆動 / 高溢價 / 流動性"""
    r1, r2, r3 = st.tabs(["☠️ 籌碼鬆動", "⚠️ 高溢價", "🧊 流動性"])
    name_col = next((c for c in ['name','名稱'] if c in df.columns), None)

    with r1:
        col = next((c for c in ['conv_rate','converted_ratio'] if c in df.columns), None)
        if col:
            d = df.copy()
            d[col] = pd.to_numeric(d[col], errors='coerce')
            bad = d[d[col] > 30]
            if bad.empty: st.success("✅ 無籌碼鬆動標的")
            else:
                st.warning(f"⚠️ {len(bad)} 檔轉換率>30%")
                disp = bad[[name_col, col]].head(10) if name_col else bad[[col]].head(10)
                st.dataframe(disp, use_container_width=True, hide_index=True)

    with r2:
        pcol = next((c for c in ['premium','premium_rate'] if c in df.columns), None)
        if pcol:
            d = df.copy(); d[pcol] = pd.to_numeric(d[pcol], errors='coerce')
            bad = d[d[pcol] > 20]
            if bad.empty: st.success("✅ 無高溢價標的")
            else:
                st.warning(f"⚠️ {len(bad)} 檔溢價率>20%")
                disp = bad[[name_col, pcol]].head(10) if name_col else bad[[pcol]].head(10)
                st.dataframe(disp, use_container_width=True, hide_index=True)
        else:
            st.info("CB 清單無溢價率欄位")

    with r3:
        vcol = next((c for c in ['avg_volume','volume'] if c in df.columns), None)
        if vcol:
            d = df.copy(); d[vcol] = pd.to_numeric(d[vcol], errors='coerce')
            bad = d[d[vcol] < 10]
            if bad.empty: st.success("✅ 無流動性風險標的")
            else:
                st.warning(f"⚠️ {len(bad)} 檔均量<10張")
                disp = bad[[name_col, vcol]].head(10) if name_col else bad[[vcol]].head(10)
                st.dataframe(disp, use_container_width=True, hide_index=True)
        else:
            st.info("CB 清單無成交量欄位")


# ════════════════════════════════════════════════════════════════
#  PAGE 3: 單兵狙擊（7 子分頁完整）
# ════════════════════════════════════════════════════════════════
def _page_sniper():
    st.markdown('<div class="m-page-title">🎯 單兵狙擊</div>', unsafe_allow_html=True)

    ticker_in = st.text_input("輸入標的（台股/美股/加密）",
                               value=st.session_state.get('sniper_ticker','2330'),
                               placeholder="2330 / TSLA / BTC-USD",
                               key="m_sniper_ticker_v2").strip()
    if not ticker_in: return
    st.session_state['sniper_ticker'] = ticker_in

    if st.button("📡 載入標的", type="primary", key="m_sniper_load"):
        with st.spinner(f"下載 {ticker_in} 數據…"):
            df = _download_stock(ticker_in, period="2y")
            if df.empty:
                st.error("查無數據，請確認代號"); return
            st.session_state['sniper_df']     = df
            st.session_state['sniper_ticker'] = ticker_in
            st.rerun()

    if 'sniper_df' not in st.session_state: return
    df   = st.session_state['sniper_df']
    tkr  = st.session_state.get('sniper_ticker', ticker_in)

    # MA 計算
    df['MA20']  = df['Close'].rolling(20).mean()
    df['MA87']  = df['Close'].rolling(87).mean()
    df['MA284'] = df['Close'].rolling(284).mean()
    cp    = float(df['Close'].iloc[-1])
    m87   = float(df['MA87'].dropna().iloc[-1]) if not df['MA87'].dropna().empty else 0
    m284  = float(df['MA284'].dropna().iloc[-1]) if not df['MA284'].dropna().empty else 0

    # 快速資訊列
    c1, c2, c3 = st.columns(3)
    c1.metric("現價",  f"{cp:.2f}")
    color_87  = "normal" if cp > m87  else "inverse"
    color_284 = "normal" if cp > m284 else "inverse"
    c2.metric("87MA",  f"{m87:.2f}",  f"{cp-m87:+.2f}",  delta_color=color_87)
    c3.metric("284MA", f"{m284:.2f}", f"{cp-m284:+.2f}", delta_color=color_284)

    trend = "✅ 中期多頭" if m87 > m284 else "❌ 空頭/整理"
    bias  = ((cp - m87) / m87 * 100) if m87 > 0 else 0
    color_trend = "#1a3a1a" if "多頭" in trend else "#3a1a1a"
    fg_trend    = "#00FF00" if "多頭" in trend else "#FF4444"
    _signal_box(f"{trend}　乖離 {bias:+.1f}%", color_trend, fg_trend)

    # 7 子分頁
    tabs = st.tabs(["📈 K線", "🔮 量子路徑", "📐 亞當理論",
                    "💰 ARK估值", "🧮 智能估值", "🌊 Elliott波", "📊 月K"])

    with tabs[0]:  # 日K線
        _mini_candle(df, height=280, title=f"{tkr} 日K線 (近60日)")
        vol_df = df.tail(60).copy().reset_index()
        if 'Date' not in vol_df.columns: vol_df.rename(columns={vol_df.columns[0]:'Date'}, inplace=True)
        st.altair_chart(
            alt.Chart(vol_df).mark_bar(color='#00bfff', opacity=0.6).encode(
                x=alt.X('Date:T', axis=alt.Axis(format='%m/%d', tickCount=6)),
                y=alt.Y('Volume:Q', title='', axis=alt.Axis(format='~s'))
            ).properties(height=80).configure_view(strokeWidth=0),
            use_container_width=True)

    with tabs[1]:  # 量子路徑（G-Score）
        _sniper_quantum_path(df, cp, m87, m284)

    with tabs[2]:  # 亞當理論
        _sniper_adam_theory(df, cp)

    with tabs[3]:  # ARK DCF
        _sniper_ark_dcf(cp, tkr)

    with tabs[4]:  # 智能估值
        _sniper_smart_valuation()

    with tabs[5]:  # Elliott Wave
        _sniper_elliott(df, tkr)

    with tabs[6]:  # 月K
        _sniper_monthly(tkr)


def _sniper_quantum_path(df, cp, m87, m284):
    st.subheader("🔮 量子路徑 G-Score")
    # G-Score 計算
    score = 0
    notes = []
    if m87 > m284:   score += 30; notes.append("✅ 雙均線多頭 +30")
    else:             notes.append("❌ 雙均線空頭 -0")
    if cp > m87:     score += 20; notes.append("✅ 站上87MA +20")
    bias = ((cp - m87)/m87*100) if m87 > 0 else 0
    if -5 < bias < 15: score += 20; notes.append("✅ 乖離健康 +20")
    elif bias > 25:    notes.append("⚠️ 乖離過大 +0")
    if len(df) > 10:
        ret5 = (cp / float(df['Close'].iloc[-6]) - 1)*100 if len(df) > 5 else 0
        if ret5 > 3: score += 15; notes.append(f"✅ 5日漲勢 {ret5:+.1f}% +15")
    score = min(100, score + 15)  # base

    color = "#00FF00" if score >= 80 else ("#FFD700" if score >= 50 else "#FF4444")
    status= "🔥 Clear Sky" if score >= 80 else ("⚠️ 區間震盪" if score >= 50 else "🐻 空頭壓力")
    _signal_box(f"G-Score: {score}/100　{status}", "#1a1a1a", color)

    for n in notes: st.caption(n)

    # 波動率錐
    rets  = df['Close'].pct_change().dropna().tail(60)
    vol   = rets.std() * (252**0.5)
    days  = 20
    bull  = cp * (1 + vol/np.sqrt(252/days))
    bear  = cp * (1 - vol/np.sqrt(252/days))
    st.markdown(f"""
    **20日波動率錐**
    - 中性軌道: {cp:.2f}
    - 樂觀情境: **{bull:.2f}** (+{(bull/cp-1)*100:.1f}%)
    - 悲觀情境: **{bear:.2f}** ({(bear/cp-1)*100:.1f}%)
    - 年化波動率: {vol*100:.1f}%
    """)


def _sniper_adam_theory(df, cp):
    st.subheader("📐 亞當理論（20日對稱投影）")
    if len(df) < 20:
        st.warning("數據不足"); return
    hist = df['Close'].tail(20)
    low  = float(hist.min()); high = float(hist.max())
    proj = [cp + (cp - float(hist.iloc[-(i+1)])) for i in range(1, 11)]
    c1, c2 = st.columns(2)
    c1.metric("近20日低點", f"{low:.2f}")
    c2.metric("近20日高點", f"{high:.2f}")
    mid = (high + low) / 2
    st.metric("中軸", f"{mid:.2f}", f"現價偏離 {(cp-mid)/mid*100:+.1f}%")
    if cp > mid:
        _signal_box("站上中軸，多方略佔優勢", "#1a3a1a", "#00FF00")
    else:
        _signal_box("跌破中軸，謹慎持有", "#3a1a1a", "#FF8844")


def _sniper_ark_dcf(cp, tkr):
    st.subheader("💰 ARK 三情境 DCF")
    c1, c2 = st.columns(2)
    g   = c1.slider("年增長率 (%)", 5, 80, 20) / 100
    m   = c2.slider("淨利率 (%)",   5, 50, 15) / 100
    rev = st.number_input("當年營收 (百萬USD)", value=1000, step=100)
    pe  = st.slider("終端 PE", 10, 80, 30)
    yr  = 5

    def dcf(mult):
        r = rev * (mult)
        for _ in range(yr): r *= (1 + g)
        return r * m * pe

    bear = dcf(0.8); base = dcf(1.0); bull = dcf(1.2)
    c1, c2, c3 = st.columns(3)
    c1.metric("🐻 悲觀", f"${bear:,.0f}M")
    c2.metric("📊 基準", f"${base:,.0f}M")
    c3.metric("🚀 樂觀", f"${bull:,.0f}M")
    st.caption(f"以上為 {yr} 年後預估市值（百萬USD）。當前股價: ${cp:.2f}")


def _sniper_smart_valuation():
    st.subheader("🧮 智能估值引擎")
    templates = {
        "軟體/SaaS": (25, 50), "生技":  (30, 40),
        "硬體/電子": (15, 25), "傳統製造": (8, 15)
    }
    industry = st.selectbox("選擇產業模板", list(templates.keys()))
    m_def, pe_def = templates[industry]
    eps = st.number_input("EPS (元)", value=5.0, step=0.5)
    g   = st.slider("未來5年年均成長率 (%)", 0, 50, 15) / 100
    m   = st.slider("淨利率 (%)", 1, 50, m_def) / 100
    pe  = st.slider("合理 PE 倍數", 5, 100, pe_def)
    fair = eps * (1 + g)**5 * pe
    c1, c2 = st.columns(2)
    c1.metric("5年後合理股價", f"{fair:.1f}")
    c2.metric("年化成長空間", f"{((fair/eps)**(1/5)-1)*100:.1f}%")


def _sniper_elliott(df, tkr):
    st.subheader("🌊 Elliott 5波模擬")
    if len(df) < 20:
        st.warning("數據不足"); return
    closes = df['Close'].tail(120).values
    # 簡化 zigzag
    pivots = []; dev = 0.03
    last_p = closes[0]; last_d = None
    for i, p in enumerate(closes):
        if last_d is None:
            if abs(p - last_p)/last_p > dev:
                last_d = 'up' if p > last_p else 'down'
                pivots.append((i, last_p)); last_p = p
        elif last_d == 'up':
            if p > last_p: last_p = p
            elif (last_p - p)/last_p > dev:
                pivots.append((len(closes)-len(closes)+i, last_p)); last_d = 'down'; last_p = p
        else:
            if p < last_p: last_p = p
            elif (p - last_p)/last_p > dev:
                pivots.append((i, last_p)); last_d = 'up'; last_p = p
    pivots.append((len(closes)-1, closes[-1]))

    if len(pivots) >= 2:
        w1 = pivots[-2][1]; w0 = pivots[-3][1] if len(pivots) >= 3 else w1 * 0.9
        w2_target = w1 - (w1 - w0) * 0.382
        w3_target = w1 + (w1 - w0) * 1.618
        w4_target = w3_target - (w3_target - w0) * 0.382
        w5_target = w3_target + (w3_target - w0) * 1.0
        cp_ = closes[-1]
        st.markdown(f"""
        **波浪位置判斷**
        - W2 目標（0.382回檔）: **{w2_target:.2f}**
        - W3 目標（1.618延伸）: **{w3_target:.2f}**
        - W4 目標（0.382回檔）: **{w4_target:.2f}**
        - W5 目標（1.0延伸）:   **{w5_target:.2f}**
        - 當前價格: **{cp_:.2f}**
        """)
    else:
        st.info("數據波動不足，無法識別波浪")


def _sniper_monthly(tkr):
    st.subheader("📊 月K線")
    with st.spinner("下載月K…"):
        df = _download_stock(tkr, period="max")
        if df.empty: st.error("無法載入"); return
        monthly = df.resample('M').agg({'Open':'first','High':'max','Low':'min','Close':'last','Volume':'sum'}).dropna()
        monthly['MA43']  = monthly['Close'].rolling(43).mean()
        monthly['MA87']  = monthly['Close'].rolling(87).mean()
        monthly['MA284'] = monthly['Close'].rolling(284).mean()
        rec = monthly.tail(60).reset_index()
        rec.rename(columns={rec.columns[0]:'Date'}, inplace=True)
        base  = alt.Chart(rec).encode(x=alt.X('Date:T', axis=alt.Axis(format='%Y-%m', tickCount=8)))
        rules = base.mark_rule(color='#888').encode(y=alt.Y('Low:Q', scale=alt.Scale(zero=False)), y2='High:Q')
        bars  = base.mark_bar().encode(y='Open:Q', y2='Close:Q',
            color=alt.condition('datum.Open<=datum.Close', alt.value('#FF4B4B'), alt.value('#26A69A')))
        l43  = base.mark_line(color='yellow',  strokeWidth=1).encode(y='MA43:Q')
        l87  = base.mark_line(color='#FFA500', strokeWidth=1.5).encode(y='MA87:Q')
        l284 = base.mark_line(color='#00BFFF', strokeWidth=1.5).encode(y='MA284:Q')
        chart = (rules+bars+l43+l87+l284).properties(height=300, title="月K線 (近60月)").configure_axis(
            gridColor='#222', labelColor='#888').configure_view(strokeWidth=0).interactive()
        st.altair_chart(chart, use_container_width=True)
        st.caption("🟡 43MA   🟠 87MA   🔵 284MA")


# ════════════════════════════════════════════════════════════════
#  PAGE 4: 全球決策（完整 4.1~4.5）
# ════════════════════════════════════════════════════════════════
def _page_decision():
    st.markdown('<div class="m-page-title">🚀 全球決策</div>', unsafe_allow_html=True)
    _upload_zone()

    tabs = st.tabs(["📋 持倉", "📈 回測", "🧪 均線實驗", "⚖️ 調倉", "🌪️ 壓力測試"])

    with tabs[0]:  # 4.1 持倉
        _decision_portfolio()

    with tabs[1]:  # 4.2 回測
        _decision_backtest()

    with tabs[2]:  # 4.3 均線實驗室
        _decision_ma_lab()

    with tabs[3]:  # 4.4 調倉
        _decision_rebalance()

    with tabs[4]:  # 4.5 壓力測試
        _decision_stress()


def _ensure_portfolio():
    if 'portfolio_df' not in st.session_state or st.session_state.portfolio_df.empty:
        st.session_state.portfolio_df = pd.DataFrame([
            {'資產代號':'2330.TW','持有數量 (股)':1000,'買入均價':550.0,'資產類別':'Stock'},
            {'資產代號':'NVDA',   '持有數量 (股)':10,  '買入均價':400.0,'資產類別':'US_Stock'},
            {'資產代號':'CASH',   '持有數量 (股)':1,   '買入均價':500000.0,'資產類別':'Cash'},
        ])


def _decision_portfolio():
    _ensure_portfolio()
    pf = st.session_state.portfolio_df.copy()
    st.subheader("📋 我的持倉")

    # 快速價格更新
    if st.button("🔄 更新市價", key="m_pf_refresh"):
        tickers = pf[pf['資產類別']!='Cash']['資產代號'].tolist()
        if tickers:
            try:
                prices = yf.download(tickers, period="1d", progress=False)['Close'].iloc[-1]
                pf['現價']  = pf['資產代號'].map(prices if hasattr(prices,'to_dict') else prices.to_dict()).fillna(1.0)
                pf['市值']  = pf['持有數量 (股)'] * pf['現價']
                pf['損益']  = (pf['現價'] - pf['買入均價']) * pf['持有數量 (股)']
                pf.loc[pf['資產類別']=='Cash','現價'] = 1.0
                pf.loc[pf['資產類別']=='Cash','市值'] = pf.loc[pf['資產類別']=='Cash','買入均價']
                pf.loc[pf['資產類別']=='Cash','損益'] = 0
                st.session_state['pf_enriched'] = pf
            except Exception as e:
                st.warning(f"市價更新失敗: {e}")

    display = st.session_state.get('pf_enriched', pf)
    total = display.get('市值', display['持有數量 (股)'] * display['買入均價']).sum()
    st.metric("💼 總資產", f"{total:,.0f}")

    for _, row in display.iterrows():
        pnl   = row.get('損益', 0) if '損益' in display.columns else 0
        mv    = row.get('市值', row['持有數量 (股)'] * row['買入均價'])
        color = "#00FF00" if pnl >= 0 else "#FF4444"
        _metric_card(
            f"{row['資產代號']} ({row['資產類別']})",
            f"{mv:,.0f}",
            f"損益: {pnl:+,.0f}　均價: {row['買入均價']:.2f}",
            color
        )

    st.divider()
    st.subheader("➕ 新增/修改持倉")
    with st.form("m_pf_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        new_t  = c1.text_input("代號")
        new_q  = c2.number_input("數量", value=100, step=100)
        c3, c4 = st.columns(2)
        new_p  = c3.number_input("買入均價", value=100.0, step=1.0, format="%.2f")
        new_cl = c4.selectbox("類別", ['Stock','ETF','US_Stock','US_Bond','Cash'])
        if st.form_submit_button("💾 存入", type="primary"):
            new_row = pd.DataFrame([{'資產代號':new_t,'持有數量 (股)':new_q,'買入均價':new_p,'資產類別':new_cl}])
            st.session_state.portfolio_df = pd.concat([st.session_state.portfolio_df, new_row], ignore_index=True)
            st.success("✅ 已新增"); st.rerun()


def _decision_backtest():
    _ensure_portfolio()
    pf = st.session_state.portfolio_df
    st.subheader("📈 績效回測 + 凱利建議")

    if st.button("🚀 啟動回測", type="primary", key="m_backtest"):
        try:
            from backtest import run_fast_backtest
            results = []
            prog = st.progress(0)
            for i, (_, row) in enumerate(pf.iterrows()):
                r = run_fast_backtest(str(row['資產代號']), initial_capital=1_000_000)
                if r: r['Ticker'] = row['資產代號']; results.append(r)
                prog.progress((i+1)/len(pf))
            prog.empty()
            st.session_state['m_backtest_results'] = results
        except Exception as e:
            st.error(f"回測模組載入失敗: {e}")

    if 'backtest_results' in st.session_state or 'm_backtest_results' in st.session_state:
        results = st.session_state.get('m_backtest_results', st.session_state.get('backtest_results',[]))
        for res in results:
            kc = res.get('kelly', 0) * 0.5
            advice = "🔥🔥 重注" if kc > 0.1 else ("✅ 穩健" if kc > 0.025 else "🧊 觀望")
            cagr   = res.get('cagr', 0)
            dd     = res.get('max_drawdown', 0)
            color  = "#00FF00" if cagr > 0.1 else ("#FFD700" if cagr > 0 else "#FF4444")
            _metric_card(
                res['Ticker'],
                f"CAGR {cagr:.1%}",
                f"最大回撤 {dd:.1%} | 凱利 {kc:.1%} → {advice}",
                color
            )

            if 'equity_curve' in res:
                eq = res['equity_curve'].reset_index()
                eq.columns = ['Date','Equity']
                st.altair_chart(
                    alt.Chart(eq).mark_line(color='#17BECF').encode(
                        x='Date:T', y=alt.Y('Equity:Q', scale=alt.Scale(zero=False))
                    ).properties(height=180).configure_view(strokeWidth=0),
                    use_container_width=True)


def _decision_ma_lab():
    _ensure_portfolio()
    pf = st.session_state.portfolio_df
    st.subheader("🧪 均線戰法實驗室")
    lab_t = st.selectbox("選擇標的", pf['資產代號'].tolist(), key="m_ma_lab_t")
    strategies = [
        "價格 > 20MA","價格 > 87MA","價格 > 284MA",
        "20/60 交叉","20/87 交叉","43/284 交叉",
        "🔥 核心戰法: 87MA ↗ 284MA"
    ]
    sel_strats = st.multiselect("選擇策略（可多選）", strategies, default=strategies[:3])

    if st.button("🔬 執行實驗", type="primary", key="m_ma_run"):
        try:
            from backtest import run_ma_strategy_backtest
            results = []
            prog = st.progress(0)
            for i, s in enumerate(sel_strats):
                r = run_ma_strategy_backtest(lab_t, s, "2015-01-01", 1_000_000)
                if r: results.append(r)
                prog.progress((i+1)/len(sel_strats))
            prog.empty()
            st.session_state['m_ma_results'] = results
        except Exception as e:
            st.error(f"均線實驗模組失敗: {e}")

    if 'm_ma_results' in st.session_state:
        results = sorted(st.session_state['m_ma_results'],
                         key=lambda x: x.get('cagr',0), reverse=True)
        for res in results:
            cagr = res.get('cagr', 0)
            dd   = res.get('max_drawdown', 0)
            fy   = res.get('future_10y_capital', 0)
            color= "#00FF00" if cagr > 0.1 else ("#FFD700" if cagr > 0 else "#FF4444")
            _metric_card(
                res['strategy_name'],
                f"CAGR {cagr:.1%}",
                f"最大回撤 {dd:.1%} | 10年後 {fy:,.0f}",
                color
            )


def _decision_rebalance():
    _ensure_portfolio()
    pf = st.session_state.portfolio_df.copy()
    st.subheader("⚖️ 智慧調倉計算機")

    tickers = pf['資產代號'].tolist()
    if st.button("💰 計算調倉", type="primary", key="m_rebal"):
        try:
            prices = yf.download(tickers, period="1d", progress=False)['Close'].iloc[-1]
            pf['現價'] = pf['資產代號'].map(prices if hasattr(prices,'to_dict') else prices.to_dict()).fillna(1.0)
            pf.loc[pf['資產類別']=='Cash','現價'] = 1.0
            pf['市值'] = pf['持有數量 (股)'] * pf['現價']
            total = pf['市值'].sum()
            pf['目前權重'] = pf['市值'] / total * 100
            st.session_state['m_rebal_pf'] = pf
            st.session_state['m_rebal_total'] = total
        except Exception as e:
            st.error(f"市價載入失敗: {e}")

    if 'm_rebal_pf' in st.session_state:
        pf_r = st.session_state['m_rebal_pf'].copy()
        total = st.session_state['m_rebal_total']
        st.metric("總資產", f"{total:,.0f}")

        targets = []
        for _, row in pf_r.iterrows():
            t = st.slider(f"{row['資產代號']} 目標%",
                          0.0, 100.0, float(row['目前權重']), 1.0,
                          key=f"m_tgt_{row['資產代號']}")
            targets.append(t)

        pf_r['目標權重'] = targets
        pf_r['目標市值'] = pf_r['目標權重'] / 100 * total
        pf_r['調倉金額'] = pf_r['目標市值'] - pf_r['市值']
        pf_r['調倉股數'] = (pf_r['調倉金額'] / pf_r['現價']).astype(int)

        if abs(sum(targets)-100) > 1:
            st.warning(f"⚠️ 目標權重合計 {sum(targets):.1f}%（應為100%）")

        for _, row in pf_r.iterrows():
            op = "買入" if row['調倉股數'] > 0 else ("賣出" if row['調倉股數'] < 0 else "不動")
            color = "#00AA44" if row['調倉股數'] > 0 else ("#FF4444" if row['調倉股數'] < 0 else "#888")
            _metric_card(
                row['資產代號'],
                f"{op} {abs(row['調倉股數'])} 股",
                f"目前 {row['目前權重']:.1f}% → 目標 {row['目標權重']:.1f}%",
                color
            )


def _decision_stress():
    _ensure_portfolio()
    pf = st.session_state.portfolio_df.copy()
    st.subheader("🌪️ 黑天鵝壓力測試")

    SCENARIOS = {
        "回檔 -5%":    -0.05,
        "修正 -10%":   -0.10,
        "技術熊市 -20%": -0.20,
        "金融海嘯 -30%": -0.30,
        "大崩盤 -50%":  -0.50,
    }

    if st.button("💥 執行壓力測試", type="primary", key="m_stress"):
        tickers = pf[pf['資產類別']!='Cash']['資產代號'].tolist()
        try:
            prices = yf.download(tickers, period="1d", progress=False)['Close'].iloc[-1]
            pf['現價'] = pf['資產代號'].map(prices if hasattr(prices,'to_dict') else prices.to_dict()).fillna(1.0)
            pf.loc[pf['資產類別']=='Cash','現價'] = 1.0
            pf['市值'] = pf['持有數量 (股)'] * pf['現價']
            total = pf['市值'].sum()
            st.session_state['m_stress_data'] = (pf, total)
        except Exception as e:
            st.error(f"市價失敗: {e}")

    if 'm_stress_data' in st.session_state:
        pf_s, total = st.session_state['m_stress_data']
        stock_mv = pf_s[pf_s['資產類別']!='Cash']['市值'].sum()
        st.metric("股票部位市值", f"{stock_mv:,.0f}")
        st.metric("總資產", f"{total:,.0f}")
        st.divider()
        for scenario, drop in SCENARIOS.items():
            loss     = stock_mv * drop
            new_total= total + loss
            pct      = loss / total * 100
            color    = "#FF4444" if drop < -0.2 else ("#FF8844" if drop < -0.1 else "#FFD700")
            _metric_card(scenario, f"{loss:,.0f}", f"總資產變為 {new_total:,.0f} ({pct:+.1f}%)", color)


# ════════════════════════════════════════════════════════════════
#  PAGE 5: 戰略百科（完整功能）
# ════════════════════════════════════════════════════════════════
def _page_wiki():
    st.markdown('<div class="m-page-title">📚 戰略百科</div>', unsafe_allow_html=True)

    tabs = st.tabs(["📖 SOP規則", "💰 CBAS", "📅 行事曆", "🕵️ 情報分析"])

    with tabs[0]:
        _wiki_sop()
    with tabs[1]:
        _wiki_cbas()
    with tabs[2]:
        _wiki_calendar()
    with tabs[3]:
        _wiki_intel()


def _wiki_sop():
    try:
        from knowledge_base import TitanKnowledgeBase
        kb = TitanKnowledgeBase()
        rules = kb.get_all_rules_for_ui()

        st_tabs = st.tabs(["⏰ 時間套利","📋 進出場","🏭 產業","🧠 心法"])

        with st_tabs[0]:
            events = rules.get("time_arbitrage", [])
            if events:
                for r in events: st.markdown(f"- {r}")
            else: _wiki_time_default()

        with st_tabs[1]:
            ee = rules.get("entry_exit", {})
            if isinstance(ee, dict):
                st.text_area("📥 進場", ee.get('entry',''), height=250)
                st.text_area("📤 出場", ee.get('exit',''), height=250)
            else: _wiki_entry_default()

        with st_tabs[2]:
            ind = rules.get("industry_story", {})
            sm  = ind.get("sector_map", {}) if isinstance(ind, dict) else {}
            if sm:
                for s, stks in sorted(sm.items()):
                    with st.expander(f"🏭 {s}"):
                        st.write(", ".join(sorted(stks)))
            else: _wiki_sector_default()

        with st_tabs[3]:
            tactics = rules.get("special_tactics", [])
            if tactics:
                for t in tactics: st.markdown(f"---\n{t}")
            else: _wiki_tactics_default()

    except Exception:
        # Fallback 完整內嵌文字
        _wiki_entry_default()
        _wiki_time_default()


def _wiki_time_default():
    st.markdown("""
**⏰ 四大黃金時間套利窗口**

🍯 **新券蜜月 (0-90天)**  
CB上市初期，大戶定調。進場甜蜜點：105~115元

📦 **滿年沈澱 (350-420天)**  
洗牌結束，底部有支撐。觸發點：CB站上87MA帶量突破

🛡️ **賣回保衛 (距賣回 < 180天)**  
下檔有賣回保護。甜甜圈區間：95~105元，最佳風報比

⏳ **百日轉換窗口 (距到期 < 100天)**  
最後機會。需股價 > 轉換價 × 1.05 才有意義
    """)

def _wiki_entry_default():
    st.markdown("""
**⚔️ SOP 四大天條**

1. **價格天條**：CB 市價 < 120 元（理想 105~115）
2. **均線天條**：87MA > 284MA（中期多頭排列）
3. **身分認證**：領頭羊（族群指標股）或風口豬
4. **發債故事**：從無到有 / 擴產 / 政策三選一

**🛑 出場天條**

- 跌破 100 元立刻停損（無例外）
- 目標 152 元以上分批出場
- 持有超過 90 天未啟動，重新評估
    """)

def _wiki_sector_default():
    sectors = [
        ("AI伺服器","廣達 緯創 英業達 技嘉"),
        ("散熱","奇鋐 雙鴻 建準"),
        ("CoWoS封測","日月光 矽品"),
        ("重電/電網","華城 士電 中興電"),
        ("半導體設備","弘塑 辛耘 漢微科"),
        ("航運","長榮 陽明 萬海"),
    ]
    for name, stocks in sectors:
        with st.expander(f"🏭 {name}"):
            st.write(stocks)

def _wiki_tactics_default():
    tactics = [
        ("賣出是種藝術","目標區間到達後，分批出場。「留魚尾」策略讓下一次持倉更安心。"),
        ("跌破100是天條","不管故事多美，CB跌破100元立刻離場，沒有例外。"),
        ("族群共振才是主力","2~3檔同族群CB同步上攻，才是真正主力進場訊號。"),
        ("溢價率的陷阱","溢價率>20%的CB上漲空間有限，選低溢價（5~15%）的標的。"),
        ("尾盤定勝負","13:25後最後25分鐘是多空最誠實的表態，收盤站穩才是真突破。"),
    ]
    for title, desc in tactics:
        with st.expander(f"🧠 {title}"):
            st.write(desc)


def _wiki_cbas():
    st.subheader("💰 CBAS 槓桿試算儀")
    cb_p = st.slider("CB 市價 (元)", 100.0, 150.0, 110.0, 0.5)
    prem = cb_p - 100
    if prem > 0:
        lev  = cb_p / prem
        c1, c2 = st.columns(2)
        c1.metric("⚖️ 槓桿倍數", f"{lev:.2f}x")
        c2.metric("💰 理論權利金", f"{prem:.2f} 元")
        if lev > 3:
            _signal_box(f"🔥 高槓桿甜蜜點！以 {prem:.2f}元 控制 100元 轉換價值", "#1a3a1a", "#00FF00")
        else:
            _signal_box("⚠️ 槓桿效益偏低，風報比不佳", "#3a2a1a", "#FFD700")
        st.markdown(f"""
        **試算說明**
        - 若標的股漲 10%，CB 理論增值 ≈ {10*lev:.1f}%
        - 若標的股漲 20%，CB 理論增值 ≈ {20*lev:.1f}%
        - 若標的股跌 10%，CB 下檔保護（賣回保護區間）
        """)


def _wiki_calendar():
    st.subheader("📅 時間套利行事曆")
    df = st.session_state.get('df', pd.DataFrame())
    if df.empty:
        st.info("請上傳 CB 清單後使用此功能"); return

    days_ahead = st.slider("掃描未來天數", 7, 90, 30)
    today      = datetime.now().date()
    future     = today + timedelta(days=days_ahead)

    try:
        from execution import CalendarAgent
        calendar = CalendarAgent()
        code_col = next((c for c in ['code'] if c in df.columns), None)
        name_col = next((c for c in ['name'] if c in df.columns), None)
        list_col = next((c for c in df.columns if 'list' in c.lower() or 'issue' in c.lower()), None)
        put_col  = next((c for c in df.columns if 'put' in c.lower() or '賣回' in c.lower()), None)

        events = []
        for _, row in df.iterrows():
            try:
                evs = calendar.calculate_time_traps(
                    str(row.get(code_col,'')) if code_col else '',
                    str(row.get(list_col,'')) if list_col else '',
                    str(row.get(put_col,''))  if put_col  else ''
                )
                for ev in evs:
                    ev_date = pd.to_datetime(ev['date']).date()
                    if today <= ev_date <= future:
                        events.append({'名稱': row.get(name_col,'') if name_col else '',
                                       '日期': ev_date,
                                       '事件': ev['event'],
                                       '天後': (ev_date - today).days})
            except Exception:
                pass

        if events:
            events.sort(key=lambda x: x['日期'])
            for ev in events:
                _metric_card(f"{ev['事件']}", ev['名稱'], f"{ev['天後']}天後 {ev['日期']}", "#FFD700")
        else:
            st.success(f"✅ 未來 {days_ahead} 天內無特殊事件")
    except Exception as e:
        st.warning(f"行事曆模組載入失敗: {e}")
        # Fallback：顯示靜態說明
        _wiki_time_default()


def _wiki_intel():
    st.subheader("🕵️ 情報分析")
    intel_files = st.session_state.get('intel_files', [])
    if not intel_files:
        st.info("請在頂部⚙️設定區上傳情報文件 (PDF/TXT)")
        return

    df = st.session_state.get('df', pd.DataFrame())
    kb = None
    try:
        from knowledge_base import TitanKnowledgeBase
        kb = TitanKnowledgeBase()
    except Exception:
        pass

    for file in intel_files:
        with st.expander(f"📄 {file.name}"):
            try:
                from intelligence import IntelligenceEngine
                intel = IntelligenceEngine()
                result = intel.analyze_file(file, kb, df)
                st.markdown(result.get("local_analysis_md","分析失敗"))
                api_key = st.session_state.get('api_key','')
                if api_key:
                    if st.button(f"🤖 AI深度分析", key=f"ai_{file.name}"):
                        with st.spinner("Gemini 分析中…"):
                            try:
                                import google.generativeai as genai
                                genai.configure(api_key=api_key)
                                from intelligence import IntelligenceEngine
                                ie = IntelligenceEngine()
                                r  = ie.analyze_with_gemini(result.get("full_text",""))
                                st.markdown(r)
                            except Exception as e:
                                st.error(f"AI失敗: {e}")
            except Exception as e:
                st.warning(f"分析模組未就緒: {e}")


# ════════════════════════════════════════════════════════════════
#  PAGE 6: 元趨勢戰法（完整：7D幾何+信評+戰略工廠+獵殺清單+全境獵殺）
# ════════════════════════════════════════════════════════════════
def _page_meta():
    st.markdown('<div class="m-page-title">🧠 元趨勢戰法</div>', unsafe_allow_html=True)

    tabs = st.tabs(["📐 7D幾何", "🏭 戰略工廠", "📝 獵殺清單", "🚀 全境獵殺"])

    with tabs[0]:
        _meta_geometry()
    with tabs[1]:
        _meta_strategy_factory()
    with tabs[2]:
        _meta_kill_list()
    with tabs[3]:
        _meta_full_hunt()


def _meta_geometry():
    ticker = st.text_input("輸入標的",
                            value=st.session_state.get('meta_target','2330'),
                            key="m_meta_geo_t").strip()
    if st.button("📐 啟動掃描", type="primary", key="m_meta_geo_scan"):
        if not ticker: return
        with st.spinner(f"計算 {ticker} 7D幾何…"):
            geo = compute_7d_geometry(ticker)
            if geo is None:
                st.error("查無數據"); return
            rating = titan_rating_system(geo)
            st.session_state['meta_geo']     = geo
            st.session_state['meta_rating']  = rating
            st.session_state['meta_target']  = ticker
            st.rerun()

    if 'meta_geo' not in st.session_state: return

    geo    = st.session_state['meta_geo']
    rating = st.session_state['meta_rating']
    tkr    = st.session_state.get('meta_target', '')
    level, name, desc, color = rating

    # 信評徽章
    st.markdown(f"""
    <div style="background:{color};border-radius:12px;padding:16px;text-align:center;margin-bottom:12px">
        <div style="font-size:28px;font-weight:bold;color:white">{level}</div>
        <div style="font-size:16px;color:white">{name}</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.8)">{desc}</div>
    </div>""", unsafe_allow_html=True)

    # 7D 角度
    periods = ['35Y','10Y','5Y','3Y','1Y','6M','3M']
    for p in periods:
        angle = geo[p]['angle']; r2 = geo[p]['r2']
        color_p = "#00FF00" if angle > 30 else ("#ADFF2F" if angle > 0 else ("#FFD700" if angle > -30 else "#FF4500"))
        _metric_card(p, f"{angle:+.1f}°", f"R² = {r2:.4f}", color_p)

    c1, c2 = st.columns(2)
    acc = geo['acceleration']
    c1.metric("⚡ 加速度", f"{acc:+.1f}°", "3M-1Y")
    c2.metric("🐦 Phoenix", "🔥 觸發" if geo['phoenix_signal'] else "❄️ 未觸發")

    # 雷達圖
    angles_data = [geo[p]['angle'] for p in periods]
    fig = go.Figure(go.Scatterpolar(
        r=angles_data, theta=periods,
        fill='toself', line=dict(color='#00FF00', width=2)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[-90,90])),
        template="plotly_dark", height=280, showlegend=False,
        margin=dict(l=20,r=20,t=20,b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    # 全歷史回歸圖
    if tkr in st.session_state.get('daily_price_data', {}):
        dfd = st.session_state['daily_price_data'][tkr]
        if dfd is not None and not dfd.empty:
            dfc = dfd.copy().reset_index()
            dfc.rename(columns={dfc.columns[0]:'Date'}, inplace=True)
            dfc['Days']    = np.arange(len(dfc))
            lp             = np.log(dfc['Close'].values)
            sl, ic, rv, _, _ = linregress(dfc['Days'].values, lp)
            dfc['Trend']   = np.exp(ic + sl * dfc['Days'])
            dev            = ((float(dfc['Close'].iloc[-1]) / float(dfc['Trend'].iloc[-1])) - 1) * 100
            st.metric("趨勢線乖離", f"{dev:+.1f}%")
            base   = alt.Chart(dfc).encode(x=alt.X('Date:T', axis=alt.Axis(format='%Y', tickCount=8)))
            line   = base.mark_line(color='#00FF00', strokeWidth=1.5).encode(
                        y=alt.Y('Close:Q', scale=alt.Scale(type='log', zero=False), title=''))
            trend_ = base.mark_line(color='#4169E1', strokeWidth=1.5, strokeDash=[5,5]).encode(
                        y=alt.Y('Trend:Q', scale=alt.Scale(type='log', zero=False)))
            st.altair_chart((line + trend_).properties(height=220).configure_axis(
                gridColor='#222', labelColor='#888').configure_view(strokeWidth=0).interactive(),
                use_container_width=True)
            st.caption("🟢 實際價格   🔵 全歷史趨勢線（對數座標）")


def _meta_strategy_factory():
    geo    = st.session_state.get('meta_geo')
    rating = st.session_state.get('meta_rating')
    tkr    = st.session_state.get('meta_target','')

    if geo is None:
        st.info("請先在「7D幾何」頁面執行掃描"); return

    st.subheader(f"🏭 {tkr} 戰略工廠")
    level, name, desc, color = rating

    # 快捷連結
    with st.expander("🔗 智能快捷連結"):
        is_tw = tkr.isdigit()
        st.markdown(f"📈 [TradingView](https://www.tradingview.com/chart/?symbol={tkr})")
        if is_tw:
            st.markdown(f"📊 [Yahoo台股](https://tw.stock.yahoo.com/quote/{tkr})")
            st.markdown(f"💰 [Goodinfo](https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID={tkr})")
        else:
            st.markdown(f"📊 [Yahoo Finance](https://finance.yahoo.com/quote/{tkr})")
            st.markdown(f"📋 [Finviz](https://finviz.com/quote.ashx?t={tkr})")
        st.markdown(f"🎙️ [AlphaMemo法說會](https://www.alphamemo.ai/free-transcripts)")

    # 情報注入
    intel_text = st.text_area("🕵️ 情報注入（貼上法說會/財報重點）",
                               height=120, key="m_factory_intel",
                               placeholder="例：Q3 AI伺服器營收 +150% YoY…")

    # 第一性原則選擇
    principles = [
        "[成長] 萊特定律：產量翻倍成本降15%？",
        "[成長] TAM邊界：市場已達80%為何還買？",
        "[生存] 燒錢率：18月融不到資會死嗎？",
        "[生存] 自由現金流真偽：扣SBC還賺嗎？",
        "[泡沫] 均值回歸：利潤率回歸均值股價腰斬？",
        "[泡沫] 內部人逃生：高管買還是賣？",
        "[終極] 不可替代性：明天消失世界有差嗎？",
        "[終極] 百倍股基因：2033年還活著嗎？",
    ]
    sel_p = st.multiselect("🎯 第一性原則（AI將回答這些問題）", principles, key="m_factory_p")
    note  = st.text_area("✍️ 統帥筆記", height=80, key="m_factory_note")

    if st.button("🚀 生成五大角鬥士提示詞", type="primary", key="m_factory_gen"):
        try:
            from tab6_metatrend import TitanAgentCouncil
            cp_val = 0
            if tkr in st.session_state.get('daily_price_data', {}):
                dfd = st.session_state['daily_price_data'][tkr]
                if dfd is not None and not dfd.empty:
                    cp_val = float(dfd['Close'].iloc[-1])
            council = TitanAgentCouncil()
            prompt  = council.generate_battle_prompt(tkr, cp_val, geo, rating, intel_text, note, sel_p)
            st.session_state['m_factory_prompt'] = prompt
        except Exception as e:
            st.error(f"提示詞生成失敗: {e}")

    if 'm_factory_prompt' in st.session_state:
        st.success("✅ 提示詞已生成！")
        prompt = st.session_state['m_factory_prompt']
        st.text_area("📋 複製後貼到 Gemini / Claude", value=prompt, height=300)
        st.download_button("💾 下載提示詞",  prompt,
                            f"TITAN_{tkr}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                            "text/plain", use_container_width=True)
        st.caption(f"📊 {len(prompt)} 字元")


def _meta_kill_list():
    st.subheader("📝 獵殺清單 (Kill List)")

    # 錄入表單
    with st.expander("➕ 新增獵殺目標", expanded=False):
        with st.form("m_kill_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            log_t  = c1.text_input("代號", value=st.session_state.get('meta_target',''))
            log_a  = c2.selectbox("操作", ["Buy","Sell"])
            c3, c4 = st.columns(2)
            log_e  = c3.number_input("進場價",  min_value=0.0, format="%.2f")
            log_tp = c4.number_input("目標價",  min_value=0.0, format="%.2f")
            log_sl = st.number_input("停損價",  min_value=0.0, format="%.2f")
            log_r  = st.text_area("進場理由", height=60)
            if st.form_submit_button("💾 存入", type="primary"):
                if not log_t or log_e <= 0:
                    st.warning("請填寫代號與進場價")
                else:
                    if 'watchlist' not in st.session_state:
                        st.session_state.watchlist = pd.DataFrame(columns=[
                            "Date","Ticker","Action","Entry Price","Target Price",
                            "Stop Loss","Rationale","Status","Current Price","PnL %"])
                    nr = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"),
                                         "Ticker": log_t.upper(), "Action": log_a,
                                         "Entry Price": log_e, "Target Price": log_tp,
                                         "Stop Loss": log_sl, "Rationale": log_r,
                                         "Status":"⏳ Holding","Current Price": np.nan,"PnL %": np.nan}])
                    st.session_state.watchlist = pd.concat([st.session_state.watchlist, nr], ignore_index=True)
                    st.success("✅ 已存入"); st.rerun()

    # 更新市價
    if st.button("🔄 更新戰況", use_container_width=True, key="m_wl_refresh"):
        if 'watchlist' in st.session_state and not st.session_state.watchlist.empty:
            wl = st.session_state.watchlist.copy()
            tickers = wl['Ticker'].unique().tolist()
            try:
                prices_data = yf.download(tickers, period="1d", progress=False)['Close']
                for i, row in wl.iterrows():
                    try:
                        cp_ = float(prices_data[row['Ticker']].iloc[-1]) if len(tickers)>1 else float(prices_data.iloc[-1])
                        wl.at[i,'Current Price'] = cp_
                        if row['Action']=='Buy':
                            pnl_ = (cp_/row['Entry Price'] - 1)*100
                        else:
                            pnl_ = (row['Entry Price']/cp_ - 1)*100
                        wl.at[i,'PnL %'] = pnl_
                        if row['Action']=='Buy':
                            wl.at[i,'Status'] = '🏆 Win' if cp_>=row['Target Price'] else ('💀 Loss' if cp_<=row['Stop Loss'] else '⏳ Holding')
                        else:
                            wl.at[i,'Status'] = '🏆 Win' if cp_<=row['Target Price'] else ('💀 Loss' if cp_>=row['Stop Loss'] else '⏳ Holding')
                    except Exception:
                        pass
                st.session_state.watchlist = wl
                st.toast("戰況已更新", icon="🔄")
            except Exception as e:
                st.warning(f"市價更新失敗: {e}")

    # 顯示清單
    if 'watchlist' not in st.session_state or st.session_state.watchlist.empty:
        st.info("清單為空，請新增獵殺目標")
        return

    wl = st.session_state.watchlist
    m1,m2,m3 = st.columns(3)
    m1.metric("持倉",  len(wl[wl['Status']=='⏳ Holding']))
    m2.metric("勝場",  len(wl[wl['Status']=='🏆 Win']))
    m3.metric("敗場",  len(wl[wl['Status']=='💀 Loss']))

    for _, row in wl.iterrows():
        pnl_  = row.get('PnL %', float('nan'))
        pnl_s = f"{pnl_:+.1f}%" if not pd.isna(pnl_) else "未更新"
        color = "#00FF00" if not pd.isna(pnl_) and pnl_ > 0 else ("#FF4444" if not pd.isna(pnl_) and pnl_ < 0 else "#888")
        _metric_card(
            f"{row['Ticker']} {row['Action']} | {row['Status']}",
            pnl_s,
            f"進場:{row['Entry Price']:.2f} → 目標:{row['Target Price']:.2f} / 停損:{row['Stop Loss']:.2f}",
            color
        )

    if st.button("🗑️ 清空清單", key="m_wl_clear"):
        st.session_state.watchlist = pd.DataFrame(columns=wl.columns)
        st.rerun()


def _meta_full_hunt():
    st.subheader("🚀 全境獵殺雷達")
    try:
        from config import WAR_THEATERS
        theaters = list(WAR_THEATERS.keys())
    except Exception:
        st.warning("WAR_THEATERS 設定未找到，請確認 config.py"); return

    sel = st.selectbox("選擇戰區", theaters, key="m_hunt_theater")
    if sel:
        st.info(f"{sel}：{len(WAR_THEATERS[sel])} 檔標的")

    if st.button("🔍 啟動全境掃描", type="primary", key="m_hunt_scan"):
        tickers = WAR_THEATERS[sel]
        results = []
        prog    = st.progress(0, text="掃描中…")
        for i, t in enumerate(tickers):
            geo_ = compute_7d_geometry(t)
            prog.progress((i+1)/len(tickers), text=f"{t} ({i+1}/{len(tickers)})")
            if geo_:
                match = None
                if geo_['10Y']['angle'] < 10 and geo_['3M']['angle'] > 45: match = "🔥 Phoenix"
                elif abs(geo_['35Y']['angle']) < 15 and geo_['acceleration'] > 20: match = "🦁 Awakening"
                elif geo_['3M']['angle'] > 60: match = "🚀 Rocket"
                if match:
                    cp_ = 0
                    if t in st.session_state.get('daily_price_data', {}):
                        dfd_ = st.session_state['daily_price_data'][t]
                        if dfd_ is not None and not dfd_.empty:
                            cp_ = float(dfd_['Close'].iloc[-1])
                    results.append({'代號':t,'現價':cp_,'3M角度':geo_['3M']['angle'],
                                    'G力':geo_['acceleration'],'型態':match})
        prog.empty()
        st.session_state[f'm_hunt_{sel}'] = pd.DataFrame(results)
        st.success(f"✅ 發現 {len(results)} 個目標")

    key_ = f'm_hunt_{sel}'
    if key_ in st.session_state and not st.session_state[key_].empty:
        rd = st.session_state[key_]
        for _, row in rd.iterrows():
            _metric_card(
                f"{row['代號']} {row['型態']}",
                f"現價 {row['現價']:.2f}",
                f"3M角度 {row['3M角度']:.1f}° | G力 {row['G力']:+.1f}°",
                "#FFD700"
            )
        csv = rd.to_csv(index=False).encode('utf-8')
        st.download_button("📥 下載戰果 CSV", csv,
                            f"hunt_{sel}_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")


# ════════════════════════════════════════════════════════════════
#  主渲染入口
# ════════════════════════════════════════════════════════════════
def render():
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

    if 'mobile_page' not in st.session_state:
        st.session_state['mobile_page'] = 'macro'

    page = st.session_state['mobile_page']

    dispatch = {
        'macro':    _page_macro,
        'radar':    _page_radar,
        'sniper':   _page_sniper,
        'decision': _page_decision,
        'wiki':     _page_wiki,
        'meta':     _page_meta,
    }
    dispatch.get(page, _page_macro)()

    st.markdown('<div class="m-spacer"></div>', unsafe_allow_html=True)
    _render_bottom_nav()
