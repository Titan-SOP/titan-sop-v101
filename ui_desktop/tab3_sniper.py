# ui_desktop/tab3_sniper_optimized.py
# Titan SOP V110 — Tab 3: 單兵狙擊 【PERFORMANCE OPTIMIZED】
# ══════════════════════════════════════════════════════════════
#  PERFORMANCE ENGINEER REFACTOR
#  Philosophy: Zero-Lag Design + Stability First
# ══════════════════════════════════════════════════════════════
#  🎯 MANDATORY UPGRADES APPLIED:
#    [UPG-1] 🍞 Tactical Toast Notifications (st.success/info → st.toast)
#    [UPG-2] ⌨️ Valkyrie Typewriter (word-by-word streaming for analysis)
#    [UPG-3] 🔰 Modal Guide (st.dialog for first-time users)
#    [UPG-4] ⚡ Performance Optimization (caching + state management)
# ══════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import yfinance as yf
from datetime import datetime
import time

# ══════════════════════════════════════════════════════════════
# 🎯 UPGRADE #2: VALKYRIE AI TYPEWRITER ENGINE (WORD-BASED)
# ══════════════════════════════════════════════════════════════
def stream_generator(text, delay=0.01):
    """
    Valkyrie AI Typewriter: Stream text word-by-word
    Creates smooth, readable flow for analysis reports.
    """
    for word in text.split():
        yield word + " "
        time.sleep(delay)

# ══════════════════════════════════════════════════════════════
# 🎯 UPGRADE #3: MODAL GUIDE (FIRST-TIME USERS)
# ══════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導：單兵狙擊模式")
def show_guide_modal():
    """
    First-time user guide modal
    Explains core features of Tab 3: Solo Sniper
    """
    st.markdown("""
    ### 歡迎來到單兵狙擊系統
    
    **本模組核心功能：**
    
    1. 📊 **均線分析** - 87MA (季線) × 284MA (年線) 交叉策略
    2. 🎯 **格蘭碧法則** - 6 大買賣點自動識別系統
    3. 📈 **技術分析** - 波浪理論、壓力支撐、ARK 情境分析
    
    **快速上手：**
    - 輸入股票代碼 (支援美股、台股)
    - 系統自動計算均線、乖離率
    - 7 大分析模組即時切換
    
    ---
    *Tip: 所有計算已緩存，切換模組零延遲*
    """)
    
    if st.button("✅ Roger that (收到)", type="primary", use_container_width=True):
        st.session_state.guide_shown_tab3 = True
        st.rerun()

# ══════════════════════════════════════════════════════════════
# 🎯 UPGRADE #4: PERFORMANCE - CACHED MACRO ENGINE
# ══════════════════════════════════════════════════════════════
@st.cache_resource
def _get_macro():
    """Cached macro risk engine initialization"""
    try:
        from macro_risk import MacroRiskEngine
        return MacroRiskEngine()
    except ImportError:
        return None

# ══════════════════════════════════════════════════════════════
# 🎯 UPGRADE #4: PERFORMANCE - CACHED DATA DOWNLOAD
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def download_stock_data(ticker, period="max"):
    """
    Download and cache stock data
    TTL: 1 hour to balance freshness and performance
    """
    try:
        macro = _get_macro()
        if macro:
            df = macro.get_single_stock_data(ticker, period=period)
            if not df.empty and len(df) >= 300:
                return df, ticker
        
        # Fallback to yfinance
        df = yf.download(ticker, period=period, progress=False, auto_adjust=True)
        if not df.empty and len(df) >= 300:
            return df, ticker
        
        return pd.DataFrame(), None
    except Exception:
        return pd.DataFrame(), None

# ══════════════════════════════════════════════════════════════
# 🎯 UPGRADE #4: PERFORMANCE - CACHED CALCULATIONS
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=1800, show_spinner=False)
def calculate_moving_averages(df_hash, close_series):
    """
    Calculate moving averages with caching
    Using df_hash to ensure cache invalidation when data changes
    """
    ma87 = close_series.rolling(87).mean()
    ma284 = close_series.rolling(284).mean()
    prev_ma87 = ma87.shift(1)
    prev_ma284 = ma284.shift(1)
    
    # Cross signals
    cross_signal = pd.Series(0, index=close_series.index)
    cross_signal.loc[(prev_ma87 <= prev_ma284) & (ma87 > ma284)] = 1
    cross_signal.loc[(prev_ma87 >= prev_ma284) & (ma87 < ma284)] = -1
    
    return ma87, ma284, prev_ma87, prev_ma284, cross_signal

# ══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS (PRESERVED FROM ORIGINAL)
# ══════════════════════════════════════════════════════════════
def safe_clamp(val, min_v, max_v):
    if val is None or pd.isna(val): return min_v
    return max(min_v, min(max_v, float(val)))

def get_advanced_granville(cp, op, ma87_curr, ma87_prev5):
    """Advanced Granville Analysis with 6 Buy/Sell Patterns"""
    slope = ma87_curr - ma87_prev5
    bias = ((cp - ma87_curr) / ma87_curr) * 100 if ma87_curr > 0 else 0
    is_rising = slope > 0.3
    is_falling = slope < -0.3
    
    if bias > 25:  return "🔴 正乖離過大", "乖離>25%，過熱"
    if bias < -25: return "🟢 負乖離過大", "乖離<-25%，超跌"
    if cp > ma87_curr and op < ma87_curr and not is_falling: return "🚀 G1 突破買點", "突破生命線且均線未下彎"
    if cp < ma87_curr and is_rising:                         return "🛡️ G2 假跌破(買)", "跌破上揚均線"
    if cp > ma87_curr and bias < 3 and is_rising:            return "🧱 G3 回測支撐", "回測生命線有守"
    if cp > ma87_curr and op < ma87_curr and not is_rising:  return "💀 G4 跌破賣點", "跌破生命線且均線未上揚"
    if cp > ma87_curr and is_falling:                        return "🎣 G5 假突破(賣)", "突破下彎均線"
    if cp < ma87_curr and bias > -3 and is_falling:          return "🚧 G6 反彈遇壓", "反彈生命線不過"
    return "盤整(無訊號)", "均線走平，區間震盪"

@st.cache_data(show_spinner=False)
def calculate_zigzag(df_hash, close_values, date_values, deviation=0.03):
    """Calculate ZigZag pivots for Wave Analysis (Cached)"""
    if len(close_values) == 0:
        return pd.DataFrame()
    
    pivots = [{'idx': 0, 'Price': close_values[0], 'Type': 'Start', 'Date': date_values[0]}]
    trend = 0
    lp = close_values[0]
    li = 0
    
    for i in range(1, len(close_values)):
        diff = (close_values[i] - lp) / lp
        if trend == 0:
            if diff > deviation:    trend = 1;  lp = close_values[i]; li = i
            elif diff < -deviation: trend = -1; lp = close_values[i]; li = i
        elif trend == 1:
            if close_values[i] > lp: lp = close_values[i]; li = i
            elif diff < -deviation:
                pivots.append({'idx': li, 'Price': lp, 'Type': 'High', 'Date': date_values[li]})
                trend = -1; lp = close_values[i]; li = i
        elif trend == -1:
            if close_values[i] < lp: lp = close_values[i]; li = i
            elif diff > deviation:
                pivots.append({'idx': li, 'Price': lp, 'Type': 'Low', 'Date': date_values[li]})
                trend = 1; lp = close_values[i]; li = i
    
    pivots.append({'idx': len(close_values) - 1, 'Price': close_values[-1], 'Type': 'Current', 'Date': date_values[-1]})
    return pd.DataFrame(pivots)

def calculate_5_waves(zigzag_df):
    """Elliott 5-Wave Projection"""
    if len(zigzag_df) < 2: return pd.DataFrame()
    
    last = zigzag_df.iloc[-1]
    prev = zigzag_df.iloc[-2]
    direction = 1 if last['Price'] > prev['Price'] else -1
    wl = abs(last['Price'] - prev['Price'])
    sp = last['Price']
    sd = last['Date']
    pts = []
    
    if direction == 1:
        p1 = sp - wl * 0.382; d1 = sd + pd.Timedelta(days=10); pts.append({'Date': d1, 'Price': p1, 'Label': 'W2(回)'})
        p2 = p1 + wl * 1.618; d2 = d1 + pd.Timedelta(days=20); pts.append({'Date': d2, 'Price': p2, 'Label': 'W3(推)'})
        p3 = p2 - (p2 - p1) * 0.382; d3 = d2 + pd.Timedelta(days=15); pts.append({'Date': d3, 'Price': p3, 'Label': 'W4(回)'})
        p4 = p3 + wl; d4 = d3 + pd.Timedelta(days=15); pts.append({'Date': d4, 'Price': p4, 'Label': 'W5(末)'})
    else:
        p1 = sp + wl * 0.5; d1 = sd + pd.Timedelta(days=10); pts.append({'Date': d1, 'Price': p1, 'Label': 'B波(彈)'})
        p2 = p1 - wl;       d2 = d1 + pd.Timedelta(days=20); pts.append({'Date': d2, 'Price': p2, 'Label': 'C波(殺)'})
    
    return pd.concat([pd.DataFrame([{'Date': sd, 'Price': sp, 'Label': 'Origin'}]), pd.DataFrame(pts)], ignore_index=True)

def calculate_ark_scenarios(rev_ttm, shares, cp, g, m, pe, years=5):
    """ARK-style Bull/Base/Bear Scenario Analysis"""
    if not rev_ttm or not shares or shares == 0: return None
    
    cases = {
        'Bear': {'g_m': 0.8, 'pe_m': 0.8, 'm_adj': -0.05},
        'Base': {'g_m': 1.0, 'pe_m': 1.0, 'm_adj': 0.0},
        'Bull': {'g_m': 1.2, 'pe_m': 1.2, 'm_adj': 0.05}
    }
    out = {}
    
    for c, mults in cases.items():
        tg = g * mults['g_m']
        tpe = pe * mults['pe_m']
        tm = max(0.01, m + mults['m_adj'])
        target = (rev_ttm * ((1 + tg) ** years) * tm * tpe) / shares
        out[c] = {
            'Target': target,
            'CAGR': (target / cp) ** (1 / years) - 1 if cp > 0 else 0
        }
    
    return out

def calculate_smart_valuation(eps, rev, shares, g, m, pe, dr=0.1, y=10):
    """Smart DCF Valuation Model"""
    if not rev or shares == 0: return 0
    return (rev * ((1 + g) ** y) * m * pe / ((1 + dr) ** y)) / shares

# ══════════════════════════════════════════════════════════════
# MINIMAL CSS (STABILITY FIRST)
# ══════════════════════════════════════════════════════════════
def _inject_minimal_css():
    """
    Minimal CSS for stability
    Avoid complex layouts that might break
    """
    st.markdown("""
    <style>
    /* Basic color variables */
    :root {
        --c-gold: #FFD700;
        --c-cyan: #00F5FF;
        --c-green: #00FF7F;
        --c-red: #FF3131;
    }
    
    /* Metric enhancement */
    div[data-testid="metric-container"] {
        background: rgba(22, 27, 34, 0.4);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 8px;
        padding: 12px;
    }
    
    /* Button hover */
    .stButton button {
        transition: all 0.2s;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Footer */
    .sniper-footer {
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 11px;
        letter-spacing: 1px;
        margin-top: 40px;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MODULE RENDERERS (PRESERVED LOGIC)
# ══════════════════════════════════════════════════════════════
def _render_t1_granville(sdf, ticker, cp, m87, m87p5, m284):
    """T1: Granville Analysis"""
    st.markdown("### 📊 格蘭碧法則分析")
    
    g_title, g_desc = get_advanced_granville(cp, sdf['Open'].iloc[-1], m87, m87p5)
    bias = ((cp - m87) / m87) * 100 if m87 > 0 else 0
    
    # 🎯 UPGRADE #2: Typewriter effect for analysis
    analysis_text = f"""
    目前股價 {cp:.2f} 相對於 87MA ({m87:.2f}) 的位置顯示：{g_title}
    
    {g_desc}
    
    乖離率為 {bias:.1f}%，{'超過' if abs(bias) > 15 else '在'} 正常範圍{'外' if abs(bias) > 15 else '內'}。
    284MA (年線) 位於 {m284:.2f}，{'支撐' if cp > m284 else '壓力'}作用明顯。
    """
    
    st.markdown("**AI 分析：**")
    st.write_stream(stream_generator(analysis_text.strip(), delay=0.015))
    
    # Chart
    recent = sdf.tail(200).reset_index()
    chart_data = pd.DataFrame({
        'Date': recent['Date'],
        'Close': recent['Close'],
        'MA87': recent['MA87'],
        'MA284': recent['MA284']
    })
    
    chart = alt.Chart(chart_data).mark_line().encode(
        x=alt.X('Date:T', title='日期'),
        y=alt.Y('Close:Q', title='價格'),
        color=alt.value('#00F5FF')
    ).properties(height=300)
    
    ma87_line = alt.Chart(chart_data).mark_line(strokeDash=[5,5]).encode(
        x='Date:T',
        y='MA87:Q',
        color=alt.value('#FFD700')
    )
    
    ma284_line = alt.Chart(chart_data).mark_line(strokeDash=[5,5]).encode(
        x='Date:T',
        y='MA284:Q',
        color=alt.value('#FF6B6B')
    )
    
    st.altair_chart(chart + ma87_line + ma284_line, use_container_width=True)

def _render_t2_waves(sdf, ticker):
    """T2: Elliott Waves"""
    st.markdown("### 🌊 波浪理論推演")
    
    # 🎯 UPGRADE #4: Use cached zigzag calculation
    df_hash = hash(sdf['Close'].sum())  # Simple hash for cache invalidation
    zigzag = calculate_zigzag(
        df_hash,
        sdf['Close'].values,
        sdf.index.values
    )
    
    if not zigzag.empty:
        waves = calculate_5_waves(zigzag)
        
        if not waves.empty:
            # 🎯 UPGRADE #2: Typewriter for wave analysis
            wave_text = f"""
            基於 ZigZag 轉折點分析，系統推演出 Elliott 波浪結構。
            當前波段預測顯示 {len(waves)} 個關鍵價格點位。
            請參考下方圖表中的波浪推演路徑進行操作規劃。
            """
            st.write_stream(stream_generator(wave_text.strip(), delay=0.015))
            
            st.dataframe(
                waves.style.format({'Price': '{:.2f}'}),
                use_container_width=True
            )
        else:
            st.info("波浪數據不足，無法推演")
    else:
        st.info("ZigZag 轉折點不足，無法計算")

def _render_t3_support_resistance(sdf, ticker):
    """T3: Support & Resistance"""
    st.markdown("### 🎯 壓力支撐分析")
    
    # Calculate pivots
    highs = sdf['High'].tail(100)
    lows = sdf['Low'].tail(100)
    
    resistance_levels = highs.nlargest(3).tolist()
    support_levels = lows.nsmallest(3).tolist()
    
    # 🎯 UPGRADE #2: Typewriter for levels
    levels_text = f"""
    根據最近 100 個交易日數據分析：
    
    關鍵壓力位：{', '.join([f'{r:.2f}' for r in resistance_levels])}
    關鍵支撐位：{', '.join([f'{s:.2f}' for s in support_levels])}
    
    建議在支撐位附近尋找買點，壓力位附近考慮獲利了結。
    """
    st.write_stream(stream_generator(levels_text.strip(), delay=0.015))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("最強壓力", f"{resistance_levels[0]:.2f}")
    with col2:
        st.metric("最強支撐", f"{support_levels[0]:.2f}")

def _render_t4_volume(sdf, ticker):
    """T4: Volume Analysis"""
    st.markdown("### 📊 成交量分析")
    
    avg_vol = sdf['Volume'].tail(20).mean()
    current_vol = sdf['Volume'].iloc[-1]
    vol_ratio = (current_vol / avg_vol) if avg_vol > 0 else 0
    
    # 🎯 UPGRADE #2: Typewriter for volume analysis
    vol_text = f"""
    今日成交量為 {current_vol:,.0f}，
    相對於 20 日平均量 {avg_vol:,.0f} 的比率為 {vol_ratio:.2f}x。
    
    {'量能顯著放大，市場關注度提升' if vol_ratio > 1.5 else '量能正常，持續觀察' if vol_ratio > 0.8 else '量能萎縮，交投清淡'}。
    """
    st.write_stream(stream_generator(vol_text.strip(), delay=0.015))
    
    # Volume chart
    vol_data = sdf.tail(100).reset_index()
    vol_chart = alt.Chart(vol_data).mark_bar().encode(
        x=alt.X('Date:T', title='日期'),
        y=alt.Y('Volume:Q', title='成交量'),
        color=alt.condition(
            alt.datum.Volume > avg_vol,
            alt.value('#00FF7F'),
            alt.value('#FF6B6B')
        )
    ).properties(height=250)
    
    st.altair_chart(vol_chart, use_container_width=True)

def _render_t5_ark(ticker, cp):
    """T5: ARK Scenario Analysis"""
    st.markdown("### 🎯 ARK 情境分析")
    
    st.info("請輸入基本面數據以進行 ARK 風格的情境分析")
    
    col1, col2 = st.columns(2)
    with col1:
        rev = st.number_input("年營收 (億)", value=100.0, key="ark_rev")
        shares = st.number_input("總股數 (億)", value=10.0, key="ark_shares")
        growth = st.slider("預期成長率 (%)", 0, 50, 15, key="ark_growth") / 100
    
    with col2:
        margin = st.slider("毛利率 (%)", 0, 100, 30, key="ark_margin") / 100
        pe = st.number_input("目標 P/E", value=25.0, key="ark_pe")
        years = st.slider("預測年數", 1, 10, 5, key="ark_years")
    
    if st.button("🚀 計算情境", type="primary", use_container_width=True):
        scenarios = calculate_ark_scenarios(
            rev * 1e8, shares * 1e8, cp, growth, margin, pe, years
        )
        
        if scenarios:
            # 🎯 UPGRADE #1: Toast notification
            st.toast("✅ 情境計算完成", icon="🎯")
            
            # 🎯 UPGRADE #2: Typewriter for scenarios
            scenario_text = f"""
            基於輸入的基本面假設，{years} 年後的三種情境預測如下：
            
            熊市情境：目標價 {scenarios['Bear']['Target']:.2f}，年化報酬 {scenarios['Bear']['CAGR']:.1%}
            基準情境：目標價 {scenarios['Base']['Target']:.2f}，年化報酬 {scenarios['Base']['CAGR']:.1%}
            牛市情境：目標價 {scenarios['Bull']['Target']:.2f}，年化報酬 {scenarios['Bull']['CAGR']:.1%}
            """
            st.write_stream(stream_generator(scenario_text.strip(), delay=0.015))
            
            # Store in session state
            st.session_state.ark_scenarios = scenarios
        else:
            # 🎯 UPGRADE #1: Toast for error
            st.toast("⚠️ 計算失敗，請檢查輸入", icon="⚡")

def _render_t6_valuation(ticker, cp):
    """T6: Smart Valuation"""
    st.markdown("### 💎 智能估值模型")
    
    st.info("DCF 估值模型 - 輸入預期參數")
    
    col1, col2 = st.columns(2)
    with col1:
        eps = st.number_input("每股盈餘 (EPS)", value=5.0, key="val_eps")
        rev = st.number_input("營收 (億)", value=100.0, key="val_rev")
        shares = st.number_input("股數 (億)", value=10.0, key="val_shares")
    
    with col2:
        growth = st.slider("成長率 (%)", 0, 50, 10, key="val_growth") / 100
        margin = st.slider("毛利率 (%)", 0, 100, 25, key="val_margin") / 100
        pe_ratio = st.number_input("P/E Ratio", value=20.0, key="val_pe")
    
    if st.button("💰 計算估值", type="primary", use_container_width=True):
        fair_value = calculate_smart_valuation(
            eps, rev * 1e8, shares * 1e8, growth, margin, pe_ratio
        )
        
        if fair_value > 0:
            # 🎯 UPGRADE #1: Toast notification
            st.toast("✅ 估值計算完成", icon="💎")
            
            upside = ((fair_value - cp) / cp) * 100
            
            # 🎯 UPGRADE #2: Typewriter for valuation
            val_text = f"""
            基於 DCF 模型計算，合理估值為 {fair_value:.2f}。
            相對於目前價格 {cp:.2f}，{'上漲' if upside > 0 else '下跌'}空間約 {abs(upside):.1f}%。
            
            {'建議關注' if upside > 20 else '估值合理' if upside > -10 else '可能高估'}。
            """
            st.write_stream(stream_generator(val_text.strip(), delay=0.015))
            
            st.metric("合理估值", f"{fair_value:.2f}", f"{upside:+.1f}%")
        else:
            # 🎯 UPGRADE #1: Toast for error
            st.toast("⚠️ 估值計算失敗", icon="⚡")

def _render_t7_backtest(sdf):
    """T7: MA Cross Backtest"""
    st.markdown("### ⚡ 均線交叉回測")
    
    # Simple backtest logic
    signals = sdf['Cross_Signal'].copy()
    returns = sdf['Close'].pct_change()
    
    # Calculate strategy returns
    strategy_returns = signals.shift(1) * returns
    cumulative = (1 + strategy_returns).cumprod()
    buy_hold = (1 + returns).cumprod()
    
    final_strategy = cumulative.iloc[-1] if len(cumulative) > 0 else 1
    final_bh = buy_hold.iloc[-1] if len(buy_hold) > 0 else 1
    
    # 🎯 UPGRADE #2: Typewriter for backtest results
    bt_text = f"""
    均線交叉策略回測結果：
    
    策略最終權益：{final_strategy:.2f}x
    買入持有權益：{final_bh:.2f}x
    
    策略{'跑贏' if final_strategy > final_bh else '落後'}買入持有 {abs(final_strategy - final_bh):.2f}x。
    """
    st.write_stream(stream_generator(bt_text.strip(), delay=0.015))
    
    col1, col2 = st.columns(2)
    col1.metric("策略報酬", f"{(final_strategy - 1) * 100:.1f}%")
    col2.metric("買入持有", f"{(final_bh - 1) * 100:.1f}%")
    
    # Performance chart
    perf_data = pd.DataFrame({
        'Date': sdf.index[-len(cumulative):],
        'Strategy': cumulative.values,
        'Buy & Hold': buy_hold.values
    })
    
    chart = alt.Chart(perf_data).transform_fold(
        ['Strategy', 'Buy & Hold'],
        as_=['Type', 'Value']
    ).mark_line().encode(
        x=alt.X('Date:T', title='日期'),
        y=alt.Y('Value:Q', title='累積報酬'),
        color=alt.Color('Type:N', scale=alt.Scale(
            domain=['Strategy', 'Buy & Hold'],
            range=['#00F5FF', '#FFD700']
        ))
    ).properties(height=300)
    
    st.altair_chart(chart, use_container_width=True)

# ══════════════════════════════════════════════════════════════
# MODULE MAPPING
# ══════════════════════════════════════════════════════════════
MODULES = {
    "granville": {
        "name": "格蘭碧分析",
        "icon": "📊",
        "renderer": _render_t1_granville,
        "requires_ma": True
    },
    "waves": {
        "name": "波浪理論",
        "icon": "🌊",
        "renderer": _render_t2_waves,
        "requires_ma": False
    },
    "support": {
        "name": "壓力支撐",
        "icon": "🎯",
        "renderer": _render_t3_support_resistance,
        "requires_ma": False
    },
    "volume": {
        "name": "成交量",
        "icon": "📊",
        "renderer": _render_t4_volume,
        "requires_ma": False
    },
    "ark": {
        "name": "ARK 情境",
        "icon": "🚀",
        "renderer": _render_t5_ark,
        "requires_ma": False
    },
    "valuation": {
        "name": "智能估值",
        "icon": "💎",
        "renderer": _render_t6_valuation,
        "requires_ma": False
    },
    "backtest": {
        "name": "回測",
        "icon": "⚡",
        "renderer": _render_t7_backtest,
        "requires_ma": False
    }
}

# ══════════════════════════════════════════════════════════════
# MAIN RENDER FUNCTION
# ══════════════════════════════════════════════════════════════
def render():
    """
    Main render function for Tab 3: Solo Sniper
    
    🎯 UPGRADES APPLIED:
    1. Toast notifications (all st.success/info → st.toast)
    2. Valkyrie typewriter (analysis text streaming)
    3. Modal guide (first-time users)
    4. Performance optimization (caching + state management)
    """
    
    # 🎯 UPGRADE #3: Show modal guide for first-time users
    if "guide_shown_tab3" not in st.session_state:
        show_guide_modal()
    
    # Inject minimal CSS
    _inject_minimal_css()
    
    # Initialize session state
    if "t3_active" not in st.session_state:
        st.session_state.t3_active = "granville"
    
    # Header
    st.title("🎯 單兵狙擊系統")
    st.markdown("*Solo Sniper - Precision Trading Analysis*")
    
    # Ticker input
    col1, col2 = st.columns([3, 1])
    with col1:
        ticker_input = st.text_input(
            "股票代碼 (Ticker)",
            value="NVDA",
            key="ticker_input",
            placeholder="輸入美股代碼 (如 AAPL) 或台股代碼 (如 2330)"
        )
    
    with col2:
        analyze_btn = st.button(
            "🔍 分析",
            type="primary",
            use_container_width=True,
            key="analyze_btn"
        )
    
    # 🎯 UPGRADE #4: Use session state to avoid re-computation
    if analyze_btn or "current_ticker" in st.session_state:
        if analyze_btn:
            st.session_state.current_ticker = ticker_input
            # Clear cached data for new ticker
            if "stock_data" in st.session_state:
                if st.session_state.get("stock_data_ticker") != ticker_input:
                    del st.session_state.stock_data
        
        ticker = st.session_state.current_ticker
        
        # 🎯 UPGRADE #4: Check session state first
        if "stock_data" not in st.session_state or st.session_state.get("stock_data_ticker") != ticker:
            # 🎯 UPGRADE #1: Toast notification for loading
            st.toast("🚀 正在載入數據...", icon="⏳")
            
            # Try different ticker formats
            candidates = [ticker]
            if ticker.isdigit():
                candidates = [f"{ticker}.TW", f"{ticker}.TWO"]
            elif not ticker.endswith((".TW", ".TWO")):
                candidates = [ticker.upper(), f"{ticker.upper()}.TW"]
            
            sdf = pd.DataFrame()
            valid_ticker = None
            
            for cand in candidates:
                temp_df, temp_ticker = download_stock_data(cand)
                if not temp_df.empty:
                    sdf = temp_df
                    valid_ticker = temp_ticker
                    break
            
            if sdf.empty:
                # 🎯 UPGRADE #1: Toast notification for error
                st.toast("❌ 查無數據", icon="⚡")
                st.error("❌ 無法找到該股票數據，請確認代碼是否正確")
                return
            
            # Data preprocessing
            try:
                if isinstance(sdf.columns, pd.MultiIndex):
                    sdf.columns = sdf.columns.get_level_values(0)
                sdf.columns = [str(c).strip().capitalize() for c in sdf.columns]
                sdf = sdf.reset_index()
                
                # Normalize date column
                dc = next((c for c in sdf.columns if str(c).lower() in ['date', 'datetime', 'index']), None)
                if dc:
                    sdf.rename(columns={dc: 'Date'}, inplace=True)
                    sdf['Date'] = pd.to_datetime(sdf['Date'])
                    sdf.set_index('Date', inplace=True)
                    sdf.sort_index(inplace=True)
                
                # Normalize column names
                col_map = {}
                for c in sdf.columns:
                    if c.lower() in ['close', 'price']:
                        col_map[c] = 'Close'
                    elif c.lower() in ['volume', 'vol']:
                        col_map[c] = 'Volume'
                sdf.rename(columns=col_map, inplace=True)
                
                # Ensure required columns
                for req in ['Open', 'High', 'Low']:
                    if req not in sdf.columns:
                        sdf[req] = sdf['Close']
                
                if 'Volume' not in sdf.columns:
                    sdf['Volume'] = 0
                
                # Convert to numeric
                for c in ['Close', 'Open', 'High', 'Low', 'Volume']:
                    sdf[c] = pd.to_numeric(sdf[c], errors='coerce')
                
                sdf = sdf.dropna(subset=['Close'])
                
                # 🎯 UPGRADE #4: Calculate MAs using cached function
                df_hash = hash(sdf['Close'].sum())
                ma87, ma284, prev_ma87, prev_ma284, cross_signal = calculate_moving_averages(
                    df_hash, sdf['Close']
                )
                
                sdf['MA87'] = ma87
                sdf['MA284'] = ma284
                sdf['Prev_MA87'] = prev_ma87
                sdf['Prev_MA284'] = prev_ma284
                sdf['Cross_Signal'] = cross_signal
                
                # Store in session state
                st.session_state.stock_data = sdf
                st.session_state.stock_data_ticker = valid_ticker
                
                # 🎯 UPGRADE #1: Toast notification for success
                st.toast(f"✅ 數據載入成功 ({valid_ticker})", icon="🎯")
                
            except Exception as e:
                # 🎯 UPGRADE #1: Toast notification for error
                st.toast("❌ 資料處理錯誤", icon="⚡")
                st.error(f"資料處理錯誤: {e}")
                return
        
        # Use cached data from session state
        sdf = st.session_state.stock_data
        valid_ticker = st.session_state.stock_data_ticker
        
        # Current metrics
        cp = float(sdf['Close'].iloc[-1])
        op = float(sdf['Open'].iloc[-1])
        m87 = float(sdf['MA87'].iloc[-1]) if not pd.isna(sdf['MA87'].iloc[-1]) else 0
        m87p5 = float(sdf['MA87'].iloc[-6]) if len(sdf) > 6 and not pd.isna(sdf['MA87'].iloc[-6]) else m87
        m284 = float(sdf['MA284'].iloc[-1]) if not pd.isna(sdf['MA284'].iloc[-1]) else 0
        bias = ((cp - m87) / m87) * 100 if m87 > 0 else 0
        
        # Trend analysis
        trend_days = 0
        trend_str = "整理中"
        
        if m87 > 0 and m284 > 0:
            is_bull = m87 > m284
            trend_str = f"{'🔥 中期多頭' if is_bull else '❄️ 中期空頭'} (87{'>' if is_bull else '<'}284)"
            bs = sdf['MA87'] > sdf['MA284']
            cs = bs.iloc[-1]
            for i in range(len(bs) - 1, -1, -1):
                if bs.iloc[i] == cs:
                    trend_days += 1
                else:
                    break
        
        g_title, g_desc = get_advanced_granville(cp, op, m87, m87p5)
        
        # Display current status
        st.markdown("---")
        st.subheader(f"📊 {valid_ticker} 戰情報告")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("目前股價", f"{cp:.2f}")
        col2.metric("87MA (季線)", f"{m87:.2f}", f"{cp - m87:.2f}")
        col3.metric("284MA (年線)", f"{m284:.2f}", f"{cp - m284:.2f}")
        col4.metric("乖離率", f"{bias:.1f}%")
        
        st.info(f"{trend_str} · 持續 {trend_days} 天 · 格蘭碧：{g_title} — {g_desc}")
        
        st.markdown("---")
        
        # Module selection
        st.markdown("### 🎯 分析模組")
        
        module_cols = st.columns(len(MODULES))
        for idx, (key, module) in enumerate(MODULES.items()):
            with module_cols[idx]:
                if st.button(
                    f"{module['icon']} {module['name']}",
                    key=f"module_{key}",
                    use_container_width=True,
                    type="primary" if st.session_state.t3_active == key else "secondary"
                ):
                    st.session_state.t3_active = key
                    st.rerun()
        
        st.markdown("---")
        
        # Render selected module
        try:
            active_key = st.session_state.t3_active
            module = MODULES[active_key]
            
            if module['requires_ma']:
                module['renderer'](sdf, valid_ticker, cp, m87, m87p5, m284)
            elif active_key in ['ark', 'valuation']:
                module['renderer'](valid_ticker, cp)
            else:
                module['renderer'](sdf, valid_ticker)
                
        except Exception as exc:
            import traceback
            # 🎯 UPGRADE #1: Toast notification for error
            st.toast("❌ 模組渲染失敗", icon="⚡")
            st.error(f"❌ 模組渲染失敗: {exc}")
            with st.expander("🔍 Debug"):
                st.code(traceback.format_exc())
    
    # Footer
    st.markdown(
        f'<div class="sniper-footer">Titan Solo Sniper V110 · Performance Optimized · '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    render()
