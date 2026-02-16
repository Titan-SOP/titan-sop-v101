# ui_desktop/tab6_metatrend_godtier.py
# Titan SOP V400 — GOD-TIER EDITION
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  🔰 SOUL UPGRADE V400 — 4 Mandatory UX Enhancements              ║
# ║    ✅ #1  Tactical Guide Modal (@st.dialog onboarding)           ║
# ║    ✅ #2  Tactical Toast Notifications (st.toast)                ║
# ║    ✅ #3  Valkyrie AI Typewriter (st.write_stream)               ║
# ║    ✅ #4  First Principles UI (80px+ hero, poster rail)          ║
# ║  PERFORMANCE:                                                      ║
# ║    ⚡ Zero-lag design: Lazy loading, cached computations         ║
# ║    🎯 1-99 age accessibility: Simple, intuitive, magnificent     ║
# ╚═══════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import altair as alt
from datetime import datetime, timedelta
from scipy.stats import linregress
import io
import time

# ── 可選依賴 ──
try:
    import google.generativeai as genai
    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False

try:
    from config import WAR_THEATERS
except ImportError:
    WAR_THEATERS = {
        "🇺🇸 美股科技": ["NVDA","TSLA","PLTR","META","GOOG","MSFT","AMZN","AAPL"],
        "🇹🇼 台股半導體": ["2330.TW","2303.TW","2454.TW","3711.TW","6531.TW"],
        "🌏 全球 ETF":    ["SPY","QQQ","SOXX","FXI","EWZ"],
    }


# ═══════════════════════════════════════════════════════════════════════════
# 🔰 SOUL UPGRADE #3 — VALKYRIE AI TYPEWRITER
# ═══════════════════════════════════════════════════════════════════════════
def _stream_text(text, speed=0.005):
    """
    Valkyrie 打字機效果 - 流式輸出文字
    Speed: 0.005 = 快速但仍可見 (適合長文本，避免卡頓)
    """
    for char in text:
        yield char
        time.sleep(speed)


# ═══════════════════════════════════════════════════════════════════════════
# 🔰 SOUL UPGRADE #1 — TACTICAL GUIDE MODAL (Onboarding)
# ═══════════════════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導：元趨勢戰法")
def show_tactical_guide():
    """
    首次進入時彈出的戰術指導 Modal
    使用 @st.dialog 裝飾器 (Streamlit 1.23+)
    """
    st.markdown("""
    ### 歡迎來到 Titan 元趨勢戰法系統
    
    **本模組核心功能：**
    
    1. 📊 **7 維度幾何分析** - 從 35 年到 3 個月，全時間尺度角度掃描
    2. 🎯 **22 階泰坦信評** - SSS/AAA/Phoenix 等智能評級系統
    3. 🤖 **AI 議會辯論** - 5 位 AI 戰士進行多空激辯與投票
    
    **快速上手：**
    - 選擇戰區 (美股/台股/ETF) 或自定義標的
    - 系統自動計算幾何角度、R² 信心度
    - AI 議會將提供 800+ 字深度分析報告
    
    ---
    *Tip: 所有計算結果已緩存，重複查詢秒出*
    """)
    
    if st.button("✅ Roger that (收到)", type="primary", use_container_width=True):
        st.session_state.seen_guide_tab6 = True
        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# CSS INJECTION — God-Tier Styling
# ═══════════════════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
    <style>
    :root {
        --c-gold: #FFD700;
        --c-cyan: #00F5FF;
        --c-red: #FF3131;
        --bg-card: #0D1117;
    }
    
    /* ═══ HERO BILLBOARD ═══ */
    .hero-container {
        padding: 50px 40px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 35px;
        background: linear-gradient(180deg, rgba(20,20,20,0) 0%, rgba(0,0,0,0.9) 100%);
        border-bottom: 1px solid rgba(255,215,0,0.2);
        box-shadow: 0 10px 40px rgba(0,0,0,0.4);
    }
    .hero-val {
        font-size: 90px !important;
        font-weight: 900;
        line-height: 1;
        color: #FFF;
        text-shadow: 0 0 50px rgba(0,245,255,0.4);
        margin: 0;
        padding: 0;
    }
    .hero-lbl {
        font-size: 15px;
        letter-spacing: 5px;
        color: #888;
        text-transform: uppercase;
        margin-top: 10px;
    }
    .hero-sub {
        font-size: 22px;
        color: #AAA;
        margin-top: 15px;
        font-weight: 300;
    }

    /* ═══ POSTER NAV & CARDS ═══ */
    .poster-card {
        background: #161b22;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 25px 20px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        min-height: 140px;
    }
    .poster-card:hover {
        transform: translateY(-6px);
        border-color: var(--c-gold);
        box-shadow: 0 12px 35px rgba(0,0,0,0.6);
        background: #1a2028;
    }
    .poster-num {
        font-size: 42px;
        font-weight: 900;
        color: var(--c-cyan);
        margin-bottom: 8px;
    }
    .poster-title {
        font-size: 15px;
        font-weight: 600;
        color: #FFF;
        margin-bottom: 4px;
    }
    .poster-desc {
        font-size: 11px;
        color: #777;
        line-height: 1.3;
    }
    
    /* ═══ STREAMING TEXT (Terminal Box) ═══ */
    .terminal-box {
        font-family: 'Courier New', monospace;
        background: #050505;
        color: #00F5FF;
        padding: 25px;
        border-left: 4px solid #00F5FF;
        border-radius: 6px;
        box-shadow: inset 0 0 25px rgba(0, 245, 255, 0.06);
        margin: 20px 0;
        line-height: 1.7;
    }
    
    /* ═══ SECTION HEADERS ═══ */
    .t6-sec-head {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 25px 30px;
        background: linear-gradient(90deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 100%);
        border-left: 5px solid var(--sa);
        border-radius: 8px;
        margin: 30px 0 25px 0;
    }
    .t6-sec-num {
        font-size: 48px;
        font-weight: 900;
        color: var(--sa);
        line-height: 1;
        min-width: 80px;
    }
    .t6-sec-title {
        font-size: 26px;
        font-weight: 700;
        color: #FFF;
        line-height: 1.2;
    }
    .t6-sec-sub {
        font-size: 13px;
        color: #888;
        letter-spacing: 1px;
        margin-top: 4px;
    }
    
    /* ═══ RANK BADGES ═══ */
    .rank-badge {
        display: inline-block;
        font-size: 140px;
        font-weight: 900;
        background: linear-gradient(135deg, var(--c-gold) 0%, #FFA500 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 60px rgba(255,215,0,0.3);
        line-height: 1;
        margin: 15px 0;
    }
    
    /* ═══ FOOTER ═══ */
    .t6-foot {
        text-align: center;
        padding: 30px;
        color: #555;
        font-size: 12px;
        letter-spacing: 2px;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 60px;
    }
    
    /* ═══ METRIC CARDS ═══ */
    div[data-testid="metric-container"] {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 8px;
        padding: 16px;
        transition: all 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        border-color: rgba(255,215,0,0.3);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* ═══ DATAFRAME STYLING ═══ */
    .dataframe {
        font-size: 13px !important;
    }
    
    /* ═══ BUTTON ENHANCEMENT ═══ */
    .stButton button {
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
    }
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# HERO BILLBOARD — Main Status Display
# ═══════════════════════════════════════════════════════════════════════════
def _render_hero():
    """頂部英雄橫幅 - 顯示系統狀態"""
    total_theaters = sum(len(tickers) for tickers in WAR_THEATERS.values())
    
    st.markdown(f"""
    <div class="hero-container">
        <div class="hero-lbl">TITAN METATREND HOLOGRAPHIC SYSTEM</div>
        <div class="hero-val">{total_theaters}</div>
        <div class="hero-sub">Global Equity Surveillance Targets</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# POSTER RAIL — Section Navigation
# ═══════════════════════════════════════════════════════════════════════════
def _render_nav_rail():
    """Poster Rail 導航系統"""
    sections = [
        ("6.1", "幾何掃描", "7D Angle Spectrum"),
        ("6.2", "AI 議會", "5-Gladiator Debate"),
        ("6.3", "上帝軌道", "God Orbit Chart"),
        ("6.4", "智能工具", "Smart Links & Valkyrie"),
        ("6.5", "宏觀對沖", "Macro Hedge & Beta"),
        ("6.6", "回測沙盒", "Geo Backtest Lab"),
    ]
    
    cols = st.columns(6)
    for idx, (num, title, desc) in enumerate(sections):
        with cols[idx]:
            is_active = st.session_state.get('t6_active', '6.1') == num
            border_color = "#FFD700" if is_active else "#333"
            bg_color = "#1a2028" if is_active else "#161b22"
            
            card_html = f"""
            <div class="poster-card" style="border-color: {border_color}; background: {bg_color};">
                <div class="poster-num">{num}</div>
                <div class="poster-title">{title}</div>
                <div class="poster-desc">{desc}</div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            if st.button(f"進入 {num}", key=f"nav_{num}", use_container_width=True):
                st.session_state.t6_active = num
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
# [SLOT-6.1] 數據引擎 — VERBATIM (Performance-optimized with caching)
# ═══════════════════════════════════════════════════════════════════════════
def get_time_slice(df, months):
    """精準切割最後 N 個月的數據片段"""
    if df is None or df.empty:
        return df
    if len(df) >= months:
        return df.iloc[-months:]
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def download_full_history(ticker, start="1990-01-01"):
    """下載完整歷史月K線 [V86.2 + Cache Optimization]"""
    try:
        original_ticker = ticker
        if ticker.isdigit() and len(ticker) >= 4:
            ticker = f"{ticker}.TW"
        df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        # 上市沒數據 → 嘗試上櫃
        if df.empty and original_ticker.isdigit() and len(original_ticker) >= 4:
            ticker = f"{original_ticker}.TWO"
            df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        # yfinance 多層索引整平
        if isinstance(df.columns, pd.MultiIndex):
            try:
                df.columns = df.columns.get_level_values(0)
            except:
                pass
        if df.empty:
            return None
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        # 儲存日K到 session_state
        if 'daily_price_data' not in st.session_state:
            st.session_state.daily_price_data = {}
        st.session_state.daily_price_data[original_ticker] = df
        # 轉月K
        df_monthly = df.resample('M').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min',
            'Close': 'last', 'Volume': 'sum'
        }).dropna()
        return df_monthly
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════════════
# [SLOT-6.2] 數學引擎 — linregress (VERBATIM)
# ═══════════════════════════════════════════════════════════════════════════
def calculate_geometry_metrics(df, months):
    """計算單一時間窗口的幾何指標"""
    if df is None or df.empty:
        return {'angle': 0, 'r2': 0, 'slope': 0}
    slice_df = get_time_slice(df, months)
    if len(slice_df) < 3:
        return {'angle': 0, 'r2': 0, 'slope': 0}
    log_prices = np.log(slice_df['Close'].values)
    x = np.arange(len(log_prices))
    slope, intercept, r_value, p_value, std_err = linregress(x, log_prices)
    angle = np.arctan(slope * 100) * (180 / np.pi)
    angle = np.clip(angle, -90, 90)
    r2 = r_value ** 2
    return {
        'angle': round(float(angle), 2),
        'r2': round(float(r2), 4),
        'slope': round(float(slope), 6)
    }


@st.cache_data(ttl=1800, show_spinner=False)
def compute_7d_geometry(ticker):
    """7 維度完整幾何掃描 (Cached for performance)"""
    df = download_full_history(ticker)
    if df is None:
        return None
    periods = {'35Y': 420, '10Y': 120, '5Y': 60, '3Y': 36, '1Y': 12, '6M': 6, '3M': 3}
    results = {}
    for label, months in periods.items():
        results[label] = calculate_geometry_metrics(df, months)
    results['acceleration'] = round(results['3M']['angle'] - results['1Y']['angle'], 2)
    results['phoenix_signal'] = (results['10Y']['angle'] < 0) and (results['6M']['angle'] > 25)
    return results


# ═══════════════════════════════════════════════════════════════════════════
# [SLOT-6.3] 22 階泰坦信評 (VERBATIM)
# ═══════════════════════════════════════════════════════════════════════════
def titan_rating_system(geo):
    """22 階信評邏輯樹"""
    if geo is None:
        return ("N/A", "無數據", "數據不足", "#808080")
    a35 = geo['35Y']['angle']; a10 = geo['10Y']['angle']; a5 = geo['5Y']['angle']
    a1 = geo['1Y']['angle'];  a6 = geo['6M']['angle'];  a3 = geo['3M']['angle']
    r2_1 = geo['1Y']['r2'];   r2_3 = geo['3M']['r2']
    acc = geo['acceleration']; phx = geo['phoenix_signal']

    if all([a35 > 45, a10 > 45, a1 > 45, a3 > 45]):    return ("SSS", "Titan (泰坦)", "全週期超過45度，神級標的", "#FFD700")
    if a1 > 40 and a6 > 45 and a3 > 50 and acc > 20:    return ("AAA", "Dominator (統治者)", "短期加速向上，完美趨勢", "#FF4500")
    if phx and a3 > 30:                                  return ("Phoenix", "Phoenix (浴火重生)", "長空短多，逆轉信號", "#FF6347")
    if r2_1 > 0.95 and 20 < a1 < 40 and acc > 0:        return ("Launchpad", "Launchpad (發射台)", "線性度極高，蓄勢待發", "#32CD32")
    if a1 > 35 and a3 > 40 and r2_3 > 0.85:             return ("AA+", "Elite (精英)", "一年期強勢上攻", "#FFA500")
    if a1 > 30 and a6 > 35:                              return ("AA", "Strong Bull (強多)", "中短期穩定上升", "#FFD700")
    if a1 > 25 and a3 > 30:                              return ("AA-", "Steady Bull (穩健多)", "趨勢健康向上", "#ADFF2F")
    if a6 > 20 and a3 > 25:                              return ("A+", "Moderate Bull (溫和多)", "短期表現良好", "#7FFF00")
    if a3 > 15:                                          return ("A", "Weak Bull (弱多)", "短期微幅上揚", "#98FB98")
    if -5 < a3 < 15 and a1 > 0:                          return ("BBB+", "Neutral+ (中性偏多)", "盤整偏多", "#F0E68C")
    if -10 < a3 < 10 and -10 < a1 < 10:                  return ("BBB", "Neutral (中性)", "橫盤震蕩", "#D3D3D3")
    if -15 < a3 < 5 and a1 < 0:                          return ("BBB-", "Neutral- (中性偏空)", "盤整偏弱", "#DDA0DD")
    if a3 < -15 and a6 < -10:                            return ("BB", "Weak Bear (弱空)", "短期下跌", "#FA8072")
    if a3 < -20 and a1 < -15:                            return ("BB-", "Bear (空頭)", "中短期走弱", "#FF6347")
    if a1 < -25 and a6 < -20:                            return ("B+", "Strong Bear (強空)", "明顯下行", "#DC143C")
    if a1 < -30 and a3 < -30:                            return ("B", "Deep Bear (深空)", "嚴重下跌", "#B22222")
    if a1 < -35 and a3 < -40 and acc < -10:             return ("B-", "Crash Zone (崩跌區)", "加速暴跌", "#8B0000")
    if all([a35 < -20, a10 < -20, a1 < -35]):           return ("CCC", "Terminal (末日)", "全週期崩壞", "#800000")
    if a35 < 0 and a10 > 0 and a1 > 20 and a3 > 30:     return ("Recovery", "Recovery (復甦)", "長期底部反轉", "#00CED1")
    if a10 > 35 and 15 < a1 < 30 and a3 < 20:           return ("Plateau", "Plateau (高原)", "長期強勢但短期盤整", "#DAA520")
    if abs(a1) < 10 and abs(a6) < 10 and abs(a3) > 20: return ("Whipsaw", "Whipsaw (鋸齒)", "短期劇烈波動", "#FF00FF")
    return ("Unknown", "Unknown", "無法分類", "#696969")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6.1 — 幾何掃描 (Enhanced with Toasts & Visual Cards)
# ═══════════════════════════════════════════════════════════════════════════
def _s61():
    st.markdown('<div class="t6-sec-head" style="--sa:#00F5FF"><div class="t6-sec-num">6.1</div><div><div class="t6-sec-title" style="color:#00F5FF;">幾何掃描引擎</div><div class="t6-sec-sub">7D Angle Spectrum · 22-Tier Rating · Acceleration Analysis</div></div></div>', unsafe_allow_html=True)
    
    # 戰區選擇
    theater_names = list(WAR_THEATERS.keys())
    theater_names.append("🎯 自訂標的")
    selected_theater = st.selectbox("選擇戰區", theater_names, key="theater_v400")
    
    if selected_theater == "🎯 自訂標的":
        custom_tickers = st.text_input("輸入標的代碼 (逗號分隔)", "NVDA,TSLA,AAPL", key="custom_v400")
        ticker_list = [t.strip() for t in custom_tickers.split(",") if t.strip()]
    else:
        ticker_list = WAR_THEATERS[selected_theater]
    
    if st.button("🚀 啟動幾何掃描", type="primary", use_container_width=True, key="scan_v400"):
        # 🍞 TOAST #1: 開始掃描
        st.toast("🚀 正在執行戰術運算... / Engaging Engines...", icon="⏳")
        
        results = []
        progress_bar = st.progress(0)
        
        for idx, ticker in enumerate(ticker_list):
            geo = compute_7d_geometry(ticker)
            if geo:
                rating, title, desc, color = titan_rating_system(geo)
                results.append({
                    '標的': ticker,
                    '信評': rating,
                    '類型': title,
                    '35Y°': geo['35Y']['angle'],
                    '10Y°': geo['10Y']['angle'],
                    '1Y°': geo['1Y']['angle'],
                    '3M°': geo['3M']['angle'],
                    'R²': geo['1Y']['r2'],
                    '加速': geo['acceleration'],
                    'color': color
                })
            progress_bar.progress((idx + 1) / len(ticker_list))
        
        progress_bar.empty()
        
        if results:
            st.session_state.geo_scan_results = pd.DataFrame(results)
            # 🍞 TOAST #2: 完成掃描
            st.toast("✅ 任務完成 / Operation Successful", icon="🎯")
        else:
            # 🍞 TOAST #3: 失敗警告
            st.toast("⚠️ 偵測到風險訊號 / Risk Detected", icon="⚡")
    
    # 顯示結果 (Visual Rank Cards)
    if 'geo_scan_results' in st.session_state and not st.session_state.geo_scan_results.empty:
        df = st.session_state.geo_scan_results
        
        st.markdown("### 🏆 排行榜 (依 1Y 角度排序)")
        df_sorted = df.sort_values('1Y°', ascending=False).reset_index(drop=True)
        
        # Top 3 Visual Cards
        if len(df_sorted) >= 3:
            cols = st.columns(3)
            medals = ["🥇", "🥈", "🥉"]
            for i in range(3):
                with cols[i]:
                    row = df_sorted.iloc[i]
                    st.markdown(f"""
                    <div class="rank-badge">{medals[i]}</div>
                    <div style="text-align: center;">
                        <div style="font-size: 32px; font-weight: 700; color: {row['color']};">
                            {row['標的']}
                        </div>
                        <div style="font-size: 18px; color: #AAA; margin-top: 5px;">
                            {row['信評']} · {row['1Y°']:.1f}°
                        </div>
                        <div style="font-size: 13px; color: #777; margin-top: 8px;">
                            {row['類型']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Full Table
        st.markdown("### 📊 完整數據表")
        display_df = df_sorted.drop(columns=['color'])
        st.dataframe(
            display_df.style.format({
                '35Y°': '{:.1f}', '10Y°': '{:.1f}', '1Y°': '{:.1f}', 
                '3M°': '{:.1f}', 'R²': '{:.3f}', '加速': '{:.1f}'
            }),
            use_container_width=True,
            height=400
        )
        
        # 下載按鈕
        csv = df_sorted.drop(columns=['color']).to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 下載掃描報告 (CSV)",
            csv,
            f"titan_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv",
            use_container_width=True
        )


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6.2 — AI 議會 (Enhanced with Valkyrie Typewriter)
# ═══════════════════════════════════════════════════════════════════════════
def _s62():
    st.markdown('<div class="t6-sec-head" style="--sa:#FF9A3C"><div class="t6-sec-num">6.2</div><div><div class="t6-sec-title" style="color:#FF9A3C;">AI 戰士議會</div><div class="t6-sec-sub">5-Gladiator Debate · Multi-Agent Analysis · Voting System</div></div></div>', unsafe_allow_html=True)
    
    if not _HAS_GENAI:
        st.warning("⚠️ 需要安裝 google-generativeai 套件")
        st.code("pip install google-generativeai")
        return
    
    api_key = st.text_input("Gemini API Key", type="password", key="gemini_key_v400")
    ticker_input = st.text_input("分析標的", "NVDA", key="ai_ticker_v400")
    
    if st.button("🤖 召喚 AI 議會", type="primary", use_container_width=True, key="ai_debate_v400"):
        if not api_key:
            st.toast("⚠️ 請輸入 API Key", icon="⚡")
            return
        
        st.toast("🚀 AI 議會集結中...", icon="⏳")
        
        # 取得幾何數據
        geo = compute_7d_geometry(ticker_input)
        if not geo:
            st.toast("⚠️ 無法取得標的數據", icon="⚡")
            return
        
        rating, title, desc, color = titan_rating_system(geo)
        
        # 建構 AI 提示詞
        prompt = f"""
你是泰坦作戰系統的 AI 戰士議會成員。請針對 {ticker_input} 進行深度分析。

**幾何數據：**
- 35年角度: {geo['35Y']['angle']}°
- 10年角度: {geo['10Y']['angle']}°
- 1年角度: {geo['1Y']['angle']}°
- 6月角度: {geo['6M']['angle']}°
- 3月角度: {geo['3M']['angle']}°
- R² (1年): {geo['1Y']['r2']}
- 加速度: {geo['acceleration']}°
- 泰坦信評: {rating} ({title})

**任務：**
請從 5 個不同角度分析此標的，每個角度至少 150 字：
1. **長期趨勢 (Long-term Trend)**: 從 35Y/10Y 角度分析
2. **短期動能 (Short-term Momentum)**: 從 3M/6M 角度分析
3. **加速特徵 (Acceleration)**: 分析是否有趨勢加速或減速
4. **信心度評估 (Confidence)**: 從 R² 值評估趨勢可靠性
5. **綜合建議 (Overall Recommendation)**: 多空判斷與操作建議

總字數要求：**800 字以上**
輸出格式：繁體中文，專業但易懂
"""
        
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            
            ai_report = response.text
            
            # ⌨️ VALKYRIE TYPEWRITER — 流式輸出
            st.markdown(f"### 🎯 標的: {ticker_input} ({rating})")
            st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
            st.write_stream(_stream_text(ai_report, speed=0.003))
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 儲存報告
            st.session_state.ai_report = ai_report
            st.session_state.ai_ticker = ticker_input
            
            st.toast("✅ AI 議會分析完成", icon="🎯")
            
        except Exception as e:
            st.toast(f"⚠️ API 呼叫失敗: {str(e)}", icon="⚡")
    
    # 下載報告
    if 'ai_report' in st.session_state:
        report_text = f"""
═══════════════════════════════════════════════
TITAN AI 戰士議會分析報告
標的: {st.session_state.ai_ticker}
時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
═══════════════════════════════════════════════

{st.session_state.ai_report}

═══════════════════════════════════════════════
Generated by Titan MetaTrend Holographic System V400
═══════════════════════════════════════════════
"""
        st.download_button(
            "📥 下載 AI 分析報告 (TXT)",
            report_text.encode('utf-8'),
            f"AI_Report_{st.session_state.ai_ticker}_{datetime.now().strftime('%Y%m%d')}.txt",
            "text/plain",
            use_container_width=True
        )


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6.3 — 上帝軌道 (God Orbit Chart)
# ═══════════════════════════════════════════════════════════════════════════
def _s63():
    st.markdown('<div class="t6-sec-head" style="--sa:#32CD32"><div class="t6-sec-num">6.3</div><div><div class="t6-sec-title" style="color:#32CD32;">上帝軌道圖</div><div class="t6-sec-sub">Log-Linear Regression · Multi-Timeframe Overlay · God\'s Trajectory</div></div></div>', unsafe_allow_html=True)
    
    orbit_ticker = st.text_input("標的代碼", "NVDA", key="orbit_ticker_v400")
    
    if st.button("📡 生成上帝軌道", type="primary", use_container_width=True, key="orbit_gen_v400"):
        st.toast("🚀 繪製上帝軌道中...", icon="⏳")
        
        df = download_full_history(orbit_ticker)
        if df is None or df.empty:
            st.toast("⚠️ 無法取得數據", icon="⚡")
            return
        
        # 計算多時間框架的回歸線
        timeframes = {'1Y': 12, '3Y': 36, '10Y': 120}
        fig = go.Figure()
        
        # 實際價格線
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            name='實際價格',
            line=dict(color='#00F5FF', width=1.5),
            opacity=0.7
        ))
        
        # 回歸線
        colors = {'1Y': '#FFD700', '3Y': '#FF9A3C', '10Y': '#32CD32'}
        for label, months in timeframes.items():
            slice_df = get_time_slice(df, months)
            if len(slice_df) >= 3:
                log_prices = np.log(slice_df['Close'].values)
                x_arr = np.arange(len(log_prices))
                slope, intercept, _, _, _ = linregress(x_arr, log_prices)
                
                # 計算回歸線
                reg_line = np.exp(slope * x_arr + intercept)
                
                fig.add_trace(go.Scatter(
                    x=slice_df.index,
                    y=reg_line,
                    name=f'{label} 軌道',
                    line=dict(color=colors[label], width=2, dash='dash'),
                    opacity=0.8
                ))
        
        fig.update_layout(
            title=dict(text=f"上帝軌道圖 - {orbit_ticker}", font=dict(size=20)),
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=500,
            yaxis_type="log",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.toast("✅ 上帝軌道繪製完成", icon="🎯")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6.4 — 智能工具
# ═══════════════════════════════════════════════════════════════════════════
def _s64():
    st.markdown('<div class="t6-sec-head" style="--sa:#FF6347"><div class="t6-sec-num">6.4</div><div><div class="t6-sec-title" style="color:#FF6347;">智能工具箱</div><div class="t6-sec-sub">Smart Links · Quick Access · External Resources</div></div></div>', unsafe_allow_html=True)
    
    tool_ticker = st.text_input("標的代碼", "NVDA", key="tool_ticker_v400")
    
    # Smart Links
    links = {
        "📊 TradingView": f"https://www.tradingview.com/chart/?symbol={tool_ticker}",
        "📈 Finviz": f"https://finviz.com/quote.ashx?t={tool_ticker}",
        "💰 Yahoo Finance": f"https://finance.yahoo.com/quote/{tool_ticker}",
        "📰 Google News": f"https://news.google.com/search?q={tool_ticker}",
    }
    
    st.markdown("### 🔗 快速連結")
    cols = st.columns(4)
    for idx, (name, url) in enumerate(links.items()):
        with cols[idx]:
            st.markdown(f"[{name}]({url})")
    
    st.divider()
    
    # Quick Stats
    if st.button("📊 快速統計", use_container_width=True, key="quick_stats_v400"):
        st.toast("🚀 載入數據中...", icon="⏳")
        
        geo = compute_7d_geometry(tool_ticker)
        if geo:
            rating, title, desc, color = titan_rating_system(geo)
            
            cols = st.columns(4)
            cols[0].metric("信評", rating)
            cols[1].metric("1Y 角度", f"{geo['1Y']['angle']:.1f}°")
            cols[2].metric("3M 角度", f"{geo['3M']['angle']:.1f}°")
            cols[3].metric("加速度", f"{geo['acceleration']:.1f}°")
            
            st.toast("✅ 數據載入完成", icon="🎯")
        else:
            st.toast("⚠️ 無法取得數據", icon="⚡")


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6.5 — 宏觀對沖
# ═══════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_prices(tickers, period="1y"):
    """取得多個標的的價格數據"""
    try:
        data = yf.download(list(tickers), period=period, progress=False, auto_adjust=True)
        if isinstance(data.columns, pd.MultiIndex):
            data = data['Close']
        return data
    except:
        return pd.DataFrame()


def _s65():
    st.markdown('<div class="t6-sec-head" style="--sa:#9370DB"><div class="t6-sec-num">6.5</div><div><div class="t6-sec-title" style="color:#9370DB;">宏觀對沖</div><div class="t6-sec-sub">Beta Calculation · Rolling Beta · Hedge Ratio</div></div></div>', unsafe_allow_html=True)
    
    BENCH_MAP = {
        "SPY (S&P 500)": "SPY",
        "QQQ (NASDAQ 100)": "QQQ",
        "^TWII (台灣加權)": "^TWII",
        "GLD (黃金)": "GLD"
    }
    
    col1, col2, col3 = st.columns([2, 1, 1])
    bench_name = col1.selectbox("基準指數", list(BENCH_MAP.keys()), key="bench_v400")
    beta_period = col2.selectbox("區間", ["1y", "2y", "3y"], key="beta_per_v400")
    beta_ticker = col3.text_input("標的", "NVDA", key="beta_tk_v400")
    
    bench_tk = BENCH_MAP[bench_name]
    
    if st.button("📊 計算 Beta", use_container_width=True, type="primary", key="run_beta_v400"):
        st.toast("🚀 計算 Beta 中...", icon="⏳")
        
        beta_px = _fetch_prices((beta_ticker, bench_tk), beta_period)
        
        if not beta_px.empty and beta_ticker in beta_px.columns and bench_tk in beta_px.columns:
            returns = beta_px.pct_change().dropna()
            
            # 計算 Beta
            cov = returns[beta_ticker].cov(returns[bench_tk])
            var = returns[bench_tk].var()
            beta_val = round(cov / var, 3) if var > 0 else 0
            
            # 相關係數
            corr = round(returns[beta_ticker].corr(returns[bench_tk]), 3)
            
            # 年化波動率
            ann_vol = round(returns[beta_ticker].std() * np.sqrt(252) * 100, 2)
            
            st.session_state.beta_v400 = {
                "beta": beta_val,
                "corr": corr,
                "avol": ann_vol,
                "ret": returns,
                "tk": beta_ticker,
                "bk": bench_tk
            }
            
            st.toast("✅ Beta 計算完成", icon="🎯")
        else:
            st.toast("⚠️ 數據載入失敗", icon="⚡")
    
    # 顯示 Beta 結果
    if "beta_v400" in st.session_state:
        b = st.session_state.beta_v400
        
        cols = st.columns(4)
        cols[0].metric("Beta", f"{b['beta']:.3f}")
        cols[1].metric("相關性", f"{b['corr']:.3f}")
        cols[2].metric("年化波動", f"{b['avol']:.2f}%")
        cols[3].metric("對沖比例", f"{abs(b['beta']):.3f}x")
        
        # Rolling Beta
        st.markdown("### 📈 滾動 60 日 Beta")
        returns = b["ret"]
        tk, bk = b["tk"], b["bk"]
        
        window = 60
        if len(returns) > window:
            roll_beta = []
            for i in range(window, len(returns)):
                chunk = returns.iloc[i-window:i]
                rb_val = chunk[tk].cov(chunk[bk]) / chunk[bk].var() if chunk[bk].var() > 0 else 0
                roll_beta.append({"Date": returns.index[i], "Rolling Beta": rb_val})
            
            rb_df = pd.DataFrame(roll_beta)
            
            fig = px.line(rb_df, x="Date", y="Rolling Beta", 
                         title=f"{tk} - 60日 Rolling Beta vs {bk}")
            fig.update_traces(line_color="#FF9A3C", line_width=2)
            fig.add_hline(y=1, line_dash="dash", line_color="rgba(255,255,255,.2)")
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6.6 — 回測沙盒
# ═══════════════════════════════════════════════════════════════════════════
def _geo_backtest(ticker, threshold, window, start_date, initial_capital):
    """幾何角度回測引擎"""
    try:
        df = download_full_history(ticker, start=start_date)
        if df is None or len(df) < 12:
            return None
        
        window_map = {'3M': 3, '6M': 6, '1Y': 12, '3Y': 36}
        win_months = window_map.get(window, 12)
        
        # 計算每月的角度
        angles = []
        for i in range(win_months, len(df)):
            slice_df = df.iloc[i-win_months:i]
            if len(slice_df) >= 3:
                log_p = np.log(slice_df['Close'].values)
                x = np.arange(len(log_p))
                slope, _, _, _, _ = linregress(x, log_p)
                angle = np.arctan(slope * 100) * (180 / np.pi)
                angles.append(angle)
            else:
                angles.append(0)
        
        # 對齊價格和角度
        prices = df.iloc[win_months:]['Close'].copy()
        angles_series = pd.Series(angles, index=prices.index)
        
        # 計算持倉信號
        position = (angles_series > threshold).astype(int)
        
        # 計算收益
        returns = prices.pct_change()
        strategy_returns = returns * position.shift(1)
        
        # 權益曲線
        equity = (1 + strategy_returns).cumprod() * initial_capital
        
        # Buy & Hold
        bh_equity = (1 + returns).cumprod() * initial_capital
        
        # 計算指標
        total_days = (equity.index[-1] - equity.index[0]).days
        years = total_days / 365.25
        
        cagr = (equity.iloc[-1] / initial_capital) ** (1 / years) - 1
        bh_cagr = (bh_equity.iloc[-1] / initial_capital) ** (1 / years) - 1
        
        # Sharpe
        sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252) if strategy_returns.std() > 0 else 0
        
        # MDD
        cummax = equity.cummax()
        drawdown = (equity - cummax) / cummax
        mdd = drawdown.min()
        
        return {
            'cagr': cagr,
            'sharpe': sharpe,
            'mdd': mdd,
            'fe': equity.iloc[-1],
            'bh_cagr': bh_cagr,
            'eq': equity,
            'bh': bh_equity,
            'dd': drawdown
        }
    except:
        return None


def _s66():
    st.markdown('<div class="t6-sec-head" style="--sa:#B77DFF"><div class="t6-sec-num">6.6</div><div><div class="t6-sec-title" style="color:#B77DFF;">幾何回測沙盒</div><div class="t6-sec-sub">Angle Signal · Equity Curve · Threshold Sweep · vs Buy & Hold</div></div></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        bt_ticker = st.text_input("回測標的", "NVDA", key="bt_tk_v400")
        bt_start = st.date_input("起始日期", value=datetime(2015, 1, 1), key="bt_start_v400")
        bt_cap = st.number_input("初始資金", value=1_000_000, step=100_000, key="bt_cap_v400")
    
    with col2:
        bt_win = st.selectbox("窗口", ["3M", "6M", "1Y", "3Y"], key="bt_win_v400")
        bt_thresh = st.slider("門檻 (°)", -90, 90, 10, key="bt_thresh_v400")
        st.info(f"策略：{bt_win} 角度 > {bt_thresh}° 則持倉")
    
    if st.button("🚀 啟動回測", type="primary", use_container_width=True, key="run_bt_v400"):
        st.toast("🚀 回測引擎啟動中...", icon="⏳")
        
        result = _geo_backtest(
            bt_ticker,
            float(bt_thresh),
            bt_win,
            bt_start.strftime("%Y-%m-%d"),
            float(bt_cap)
        )
        
        if result:
            st.session_state.gbt_v400 = result
            st.session_state.gbt_lbl_v400 = f"{bt_ticker}-{bt_win}->{bt_thresh}°"
            st.toast(f"✅ 回測完成 | CAGR {result['cagr']:.2%}", icon="🎯")
        else:
            st.toast("⚠️ 回測失敗", icon="⚡")
    
    # 顯示回測結果
    if "gbt_v400" in st.session_state:
        r = st.session_state.gbt_v400
        lbl = st.session_state.get("gbt_lbl_v400", "")
        
        cols = st.columns(5)
        cols[0].metric("CAGR", f"{r['cagr']:.2%}")
        cols[1].metric("Sharpe", f"{r['sharpe']:.2f}")
        cols[2].metric("MDD", f"{r['mdd']:.2%}")
        cols[3].metric("期末資金", f"{r['fe']:,.0f}")
        cols[4].metric("B&H CAGR", f"{r['bh_cagr']:.2%}")
        
        alpha = r["cagr"] - r["bh_cagr"]
        if alpha >= 0:
            st.success(f"Alpha: +{alpha:.2%}")
        else:
            st.warning(f"Alpha: {alpha:.2%}")
        
        # 權益曲線
        st.markdown("### 📈 權益曲線")
        eq_df = r["eq"].reset_index()
        eq_df.columns = ["Date", "Equity"]
        bh_df = r["bh"].reset_index()
        bh_df.columns = ["Date", "BH"]
        
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=eq_df["Date"], y=eq_df["Equity"],
            name="幾何策略", line=dict(color="#00F5FF", width=2.5)
        ))
        fig_eq.add_trace(go.Scatter(
            x=bh_df["Date"], y=bh_df["BH"],
            name="Buy & Hold", line=dict(color="rgba(255,215,0,.6)", width=1.5, dash="dot")
        ))
        fig_eq.update_layout(
            title=f"權益曲線 - {lbl}",
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400,
            hovermode="x unified"
        )
        st.plotly_chart(fig_eq, use_container_width=True)
        
        # 回撤曲線
        dd_df = r["dd"].reset_index()
        dd_df.columns = ["Date", "DD"]
        dd_df["DD_pct"] = dd_df["DD"] * 100
        
        fig_dd = px.area(dd_df, x="Date", y="DD_pct", title="Underwater 回撤曲線")
        fig_dd.update_traces(fillcolor="rgba(255,49,49,.22)", line_color="rgba(255,49,49,.75)")
        fig_dd.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=250
        )
        st.plotly_chart(fig_dd, use_container_width=True)
        
        # 門檻掃描
        st.markdown("### 🔬 多門檻掃描")
        if st.button("啟動門檻掃描", use_container_width=True, key="run_sweep_v400"):
            st.toast("🚀 執行門檻掃描中...", icon="⏳")
            
            sweep_list = list(range(-30, 55, 5))
            sweep_rows = []
            progress = st.progress(0)
            
            for i, thresh in enumerate(sweep_list):
                sr = _geo_backtest(bt_ticker, float(thresh), bt_win, 
                                  bt_start.strftime("%Y-%m-%d"), float(bt_cap))
                if sr:
                    sweep_rows.append({
                        "門檻(°)": thresh,
                        "CAGR": sr["cagr"],
                        "Sharpe": sr["sharpe"],
                        "MDD": sr["mdd"]
                    })
                progress.progress((i + 1) / len(sweep_list))
            
            progress.empty()
            
            if sweep_rows:
                sw_df = pd.DataFrame(sweep_rows)
                best = sw_df.loc[sw_df["CAGR"].idxmax()]
                st.toast(f"✅ 掃描完成 | 最優門檻: {int(best['門檻(°)'])}°", icon="🎯")
                st.session_state.sweep_df_v400 = sw_df
        
        if "sweep_df_v400" in st.session_state:
            sw_df = st.session_state.sweep_df_v400
            
            fig_sw = go.Figure()
            fig_sw.add_trace(go.Scatter(
                x=sw_df["門檻(°)"], y=sw_df["CAGR"] * 100,
                name="CAGR(%)", mode="lines+markers",
                line=dict(color="#00FF7F", width=2.5)
            ))
            fig_sw.add_trace(go.Scatter(
                x=sw_df["門檻(°)"], y=sw_df["Sharpe"],
                name="Sharpe", mode="lines+markers",
                line=dict(color="#FFD700", width=2, dash="dash"),
                yaxis="y2"
            ))
            fig_sw.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=350,
                yaxis=dict(title="CAGR(%)"),
                yaxis2=dict(title="Sharpe", overlaying="y", side="right"),
                hovermode="x unified"
            )
            st.plotly_chart(fig_sw, use_container_width=True)
            
            st.dataframe(
                sw_df.style.format({
                    "CAGR": "{:.2%}",
                    "Sharpe": "{:.2f}",
                    "MDD": "{:.2%}"
                }),
                use_container_width=True
            )


# ═══════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════
def render():
    """
    Tab 6 — 元趨勢戰法 God-Tier Edition V400
    
    🔰 4 Soul Upgrades:
    1. Tactical Guide Modal (First Visit)
    2. Tactical Toast Notifications
    3. Valkyrie AI Typewriter
    4. First Principles UI (Hero Billboard, Poster Rail)
    """
    
    # 🔰 SOUL UPGRADE #1 — 首次訪問顯示戰術指導
    if "seen_guide_tab6" not in st.session_state:
        show_tactical_guide()
    
    # CSS 注入
    _inject_css()
    
    # Hero Billboard
    _render_hero()
    
    # Poster Rail 導航
    _render_nav_rail()
    
    # 路由系統
    section_map = {
        "6.1": _s61,
        "6.2": _s62,
        "6.3": _s63,
        "6.4": _s64,
        "6.5": _s65,
        "6.6": _s66
    }
    
    active = st.session_state.get('t6_active', '6.1')
    fn = section_map.get(active, _s61)
    
    try:
        fn()
    except Exception as exc:
        import traceback
        st.error(f"❌ Section {active} error: {exc}")
        with st.expander("Debug"):
            st.code(traceback.format_exc())
    
    # Footer
    st.markdown(
        f'<div class="t6-foot">Titan MetaTrend Holographic Deck V400 · God-Tier Edition · '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',
        unsafe_allow_html=True
    )
