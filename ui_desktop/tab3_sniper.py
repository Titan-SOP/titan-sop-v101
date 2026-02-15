# ui_desktop/tab3_sniper.py — DIRECTOR'S CUT
# Titan SOP V100 — Tab 3: 單兵狙擊 (CINEMATIC EDITION)
# ══════════════════════════════════════════════════════════════
#  🎬 DIRECTOR'S CUT FEATURES:
#    [DC1] 🔰 Tactical Guide Modal (Onboarding)
#    [DC2] 🍞 Toast Notifications (No More Green Boxes)
#    [DC3] ⌨️ Valkyrie AI Typewriter (Streaming Text)
#    [DC4] 🎬 Cinematic Visuals (Hero Billboard + Glassmorphism)
# ══════════════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import yfinance as yf
from datetime import datetime
from macro_risk import MacroRiskEngine
import time

@st.cache_resource
def _get_macro():
    return MacroRiskEngine()

# ── [DC3] VALKYRIE AI TYPEWRITER ───────────────────────────────
def _stream_text(text, speed=0.02):
    """Character-by-character text streaming for cinematic effect"""
    for char in text:
        yield char
        time.sleep(speed)

# ── HELPERS (verbatim from original V82) ──────────────────────
def safe_clamp(val, min_v, max_v):
    if val is None or pd.isna(val): return min_v
    return max(min_v, min(max_v, float(val)))

def get_advanced_granville(cp, op, ma87_curr, ma87_prev5):
    slope=ma87_curr-ma87_prev5; bias=((cp-ma87_curr)/ma87_curr)*100 if ma87_curr>0 else 0
    is_rising=slope>0.3; is_falling=slope<-0.3
    if bias>25:  return "🔴 正乖離過大","乖離>25%，過熱"
    if bias<-25: return "🟢 負乖離過大","乖離<-25%，超跌"
    if cp>ma87_curr and op<ma87_curr and not is_falling: return "🚀 G1 突破買點","突破生命線且均線未下彎"
    if cp<ma87_curr and is_rising:                       return "🛡️ G2 假跌破(買)","跌破上揚均線"
    if cp>ma87_curr and bias<3 and is_rising:            return "🧱 G3 回測支撐","回測生命線有守"
    if cp>ma87_curr and op<ma87_curr and not is_rising:  return "💀 G4 跌破賣點","跌破生命線且均線未上揚"
    if cp>ma87_curr and is_falling:                      return "🎣 G5 假突破(賣)","突破下彎均線"
    if cp<ma87_curr and bias>-3 and is_falling:          return "🚧 G6 反彈遇壓","反彈生命線不過"
    return "盤整(無訊號)","均線走平，區間震盪"

def calculate_zigzag(df, deviation=0.03):
    df=df.reset_index()
    dc=next((c for c in df.columns if str(c).lower() in ['date','index']),None)
    if dc: df.rename(columns={dc:'Date'},inplace=True)
    if 'Close' not in df.columns or 'Date' not in df.columns: return pd.DataFrame()
    closes=df['Close'].values; dates=df['Date'].values
    if len(closes)==0: return pd.DataFrame()
    pivots=[{'idx':0,'Price':closes[0],'Type':'Start','Date':dates[0]}]
    trend=0; lp=closes[0]; li=0
    for i in range(1,len(closes)):
        diff=(closes[i]-lp)/lp
        if trend==0:
            if diff>deviation:    trend=1;  lp=closes[i]; li=i
            elif diff<-deviation: trend=-1; lp=closes[i]; li=i
        elif trend==1:
            if closes[i]>lp: lp=closes[i]; li=i
            elif diff<-deviation:
                pivots.append({'idx':li,'Price':lp,'Type':'High','Date':dates[li]})
                trend=-1; lp=closes[i]; li=i
        elif trend==-1:
            if closes[i]<lp: lp=closes[i]; li=i
            elif diff>deviation:
                pivots.append({'idx':li,'Price':lp,'Type':'Low','Date':dates[li]})
                trend=1; lp=closes[i]; li=i
    pivots.append({'idx':len(closes)-1,'Price':closes[-1],'Type':'Current','Date':dates[-1]})
    return pd.DataFrame(pivots)

def calculate_5_waves(zigzag_df):
    if len(zigzag_df)<2: return pd.DataFrame()
    last=zigzag_df.iloc[-1]; prev=zigzag_df.iloc[-2]
    direction=1 if last['Price']>prev['Price'] else -1
    wl=abs(last['Price']-prev['Price']); sp=last['Price']; sd=last['Date']
    pts=[]
    if direction==1:
        p1=sp-wl*0.382; d1=sd+pd.Timedelta(days=10); pts.append({'Date':d1,'Price':p1,'Label':'W2(回)'})
        p2=p1+wl*1.618; d2=d1+pd.Timedelta(days=20); pts.append({'Date':d2,'Price':p2,'Label':'W3(推)'})
        p3=p2-(p2-p1)*0.382; d3=d2+pd.Timedelta(days=15); pts.append({'Date':d3,'Price':p3,'Label':'W4(回)'})
        p4=p3+wl; d4=d3+pd.Timedelta(days=15); pts.append({'Date':d4,'Price':p4,'Label':'W5(末)'})
    else:
        p1=sp+wl*0.5; d1=sd+pd.Timedelta(days=10); pts.append({'Date':d1,'Price':p1,'Label':'B波(彈)'})
        p2=p1-wl;     d2=d1+pd.Timedelta(days=20); pts.append({'Date':d2,'Price':p2,'Label':'C波(殺)'})
    return pd.concat([pd.DataFrame([{'Date':sd,'Price':sp,'Label':'Origin'}]),pd.DataFrame(pts)],ignore_index=True)

def calculate_ark_scenarios(rev_ttm,shares,cp,g,m,pe,years=5):
    if not rev_ttm or not shares or shares==0: return None
    cases={'Bear':{'g_m':0.8,'pe_m':0.8,'m_adj':-0.05},'Base':{'g_m':1.0,'pe_m':1.0,'m_adj':0.0},'Bull':{'g_m':1.2,'pe_m':1.2,'m_adj':0.05}}
    out={}
    for c,mults in cases.items():
        tg=g*mults['g_m']; tpe=pe*mults['pe_m']; tm=max(0.01,m+mults['m_adj'])
        target=(rev_ttm*((1+tg)**years)*tm*tpe)/shares
        out[c]={'Target':target,'CAGR':(target/cp)**(1/years)-1 if cp>0 else 0}
    return out

def calculate_smart_valuation(eps,rev,shares,g,m,pe,dr=0.1,y=10):
    if not rev or shares==0: return 0
    return (rev*((1+g)**y)*m*pe/((1+dr)**y))/shares

# ── [DC4] DIRECTOR'S CUT MASTER CSS ────────────────────────────
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;700&display=swap" rel="stylesheet">
<style>
/* ═══════════════════════════════════════════════════════ */
/* TITAN OS MASTER CSS — DIRECTOR'S CUT */
/* ═══════════════════════════════════════════════════════ */
:root {
  --c-gold: #FFD700;
  --c-cyan: #00F5FF;
  --c-red: #FF3131;
  --c-green: #00FF7F;
  --c-orange: #FF9A3C;
  --bg-card: #0D1117;
  --f-d: 'Bebas Neue', sans-serif;
  --f-b: 'Rajdhani', sans-serif;
  --f-m: 'JetBrains Mono', monospace;
}

/* 1. HERO BILLBOARD (CINEMATIC) */
.hero-container {
  padding: 40px;
  border-radius: 20px;
  text-align: center;
  margin-bottom: 30px;
  background: linear-gradient(180deg, rgba(10,10,10,0) 0%, rgba(0,0,0,0.9) 100%);
  border-bottom: 1px solid rgba(255,215,0,0.2);
}
.hero-val {
  font-size: 84px !important;
  font-weight: 900;
  line-height: 1;
  color: #FFF;
  text-shadow: 0 0 40px rgba(0,245,255,0.3);
  font-family: 'Arial Black', sans-serif;
}
.hero-lbl {
  font-size: 16px;
  letter-spacing: 4px;
  color: #888;
  text-transform: uppercase;
}

/* 2. POSTER NAV RAIL (NETFLIX STYLE) */
.poster-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}
div.stButton > button[kind="secondary"] {
  height: 140px !important;
  border: 1px solid #333 !important;
  background: #161b22 !important;
  font-size: 16px !important;
  font-weight: 700 !important;
  color: #888 !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  padding-bottom: 20px !important;
  transition: all 0.3s;
}
div.stButton > button[kind="secondary"]:hover {
  border-color: var(--c-gold) !important;
  color: #FFF !important;
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
div.stButton > button[kind="primary"] {
  background: linear-gradient(45deg, #FFD700, #DAA520) !important;
  color: #000 !important;
  border: none !important;
  box-shadow: 0 0 20px rgba(255,215,0,0.4);
}

/* 3. STREAMING TEXT & DATA (GLASSMORPHISM) */
.stMarkdown p {
  font-size: 18px !important;
  line-height: 1.6;
}
[data-testid="stDataFrame"] {
  font-size: 16px !important;
  background: rgba(13, 17, 23, 0.6) !important;
  backdrop-filter: blur(10px);
  border-radius: 12px;
  padding: 10px;
}

/* ORIGINAL STYLES PRESERVED */
.t3-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin: 12px 0;
}
.t3-kpi-card {
  background: rgba(255,255,255,.022);
  border: 1px solid rgba(255,255,255,.062);
  border-top: 2px solid var(--kc, #00F5FF);
  border-radius: 14px;
  padding: 13px 14px 10px;
  position: relative;
  overflow: hidden;
}
.t3-kpi-card::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 70px;
  height: 70px;
  background: radial-gradient(circle at top right, var(--kc, #00F5FF), transparent 68%);
  opacity: .04;
  pointer-events: none;
}
.t3-kpi-lbl {
  font-family: var(--f-m);
  font-size: 8px;
  color: rgba(140,155,178,.55);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin-bottom: 7px;
}
.t3-kpi-val {
  font-family: var(--f-d);
  font-size: 48px;
  color: #FFF;
  line-height: .9;
  margin-bottom: 4px;
}
.t3-kpi-sub {
  font-family: var(--f-b);
  font-size: 12px;
  color: var(--kc, #00F5FF);
  font-weight: 600;
}
.t3-badge-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 8px 0 12px;
}
.t3-badge {
  font-family: var(--f-m);
  font-size: 10px;
  letter-spacing: 1px;
  border: 1px solid var(--bc, rgba(255,255,255,.10));
  background: rgba(0,0,0,.01);
  color: var(--bc, #778899);
  border-radius: 20px;
  padding: 4px 12px;
}
.t3-rail {
  background: linear-gradient(165deg, #07080f, #0b0c16);
  border: 1px solid rgba(255,255,255,.055);
  border-radius: 18px;
  padding: 14px 12px 11px;
  margin-bottom: 13px;
}
.t3-rail-lbl {
  font-family: var(--f-m);
  font-size: 8px;
  letter-spacing: 4px;
  color: rgba(255,154,60,.18);
  text-transform: uppercase;
  margin-bottom: 10px;
}
.t3-content {
  background: rgba(255,255,255,.008);
  border: 1px solid rgba(255,255,255,.04);
  border-radius: 18px;
  padding: 18px 15px 14px;
  margin-bottom: 12px;
}
.t3-chart {
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(8px);
  border-radius: 12px;
  padding: 15px;
  margin: 10px 0;
}
.t3-action button {
  background: linear-gradient(135deg, #FF9A3C 0%, #FF6B3C 100%) !important;
  color: #FFF !important;
  font-weight: 700 !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(255,154,60,.25);
}
.t3-foot {
  font-family: var(--f-m);
  font-size: 8px;
  color: rgba(100,115,130,.22);
  text-align: center;
  letter-spacing: 3px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(255,255,255,.025);
}
</style>
""", unsafe_allow_html=True)

# ── [DC1] TACTICAL GUIDE MODAL ─────────────────────────────────
@st.dialog("🔰 戰術指導 / Tactical Guide")
def show_tactical_guide():
    st.markdown("""
    ### 單兵狙擊系統操作指南
    
    **核心功能 / Core Functions:**
    
    • **🔮 雙軌扣抵預演** — 預測均線扣抵效應，掌握季線/年線轉折點  
    • **📐 亞當理論 + 🕯️ K線分析** — 技術型態識別，配合RSI動量指標  
    • **🧠 ARK戰情桌 + 💎 智能估值** — 基本面情境分析，多空推演  
    
    **操作流程 / Workflow:**
    1. 輸入股票代號 (支援台股/美股/加密貨幣)
    2. 點擊 🔍 搜尋啟動掃描
    3. 在下方模組海報選擇分析維度
    
    ---
    *系統已針對長時程回測進行優化，建議使用桌面端以獲得最佳體驗。*
    """)
    
    if st.button("✅ Roger that (收到)", type="primary", use_container_width=True):
        st.session_state.t3_guide_shown = True
        st.rerun()

# ── SUB-MODULES ────────────────────────────────────────────────
def _render_badges(sdf, cp, m87, m284, bias):
    """[E2] Technical Overview Badges"""
    st.markdown('<div class="t3-badge-row">', unsafe_allow_html=True)
    
    # Trend Badge
    trend_color = "#00FF7F" if m87 > m284 else "#FF6B6B"
    st.markdown(f'<span class="t3-badge" style="--bc:{trend_color};">{"🐂 BULL TREND" if m87>m284 else "🐻 BEAR TREND"}</span>', unsafe_allow_html=True)
    
    # Bias Badge
    bias_status = "OVERBOUGHT" if bias > 15 else ("OVERSOLD" if bias < -15 else "NEUTRAL")
    bias_color = "#FF3131" if abs(bias) > 15 else "#FFD700"
    st.markdown(f'<span class="t3-badge" style="--bc:{bias_color};">📊 {bias_status}</span>', unsafe_allow_html=True)
    
    # Volume Badge
    if 'Volume' in sdf.columns:
        vol_avg = sdf['Volume'].tail(20).mean()
        vol_curr = sdf['Volume'].iloc[-1]
        vol_ratio = vol_curr / vol_avg if vol_avg > 0 else 1
        vol_color = "#00F5FF" if vol_ratio > 1.5 else "#888"
        st.markdown(f'<span class="t3-badge" style="--bc:{vol_color};">🔊 VOL {vol_ratio:.1f}x</span>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def _t1(sdf, ticker, cp, m87, m87p5, m284):
    """🔮 雙軌扣抵預演 (Deduction Forecast)"""
    st.markdown("### 🔮 雙軌扣抵預演 / Deduction Forecast")
    
    # [DC3] Stream the analysis text
    analysis_text = f"""
    **系統分析 / System Analysis:**
    
    雙軌扣抵系統正在計算 {ticker} 的季線 (MA87) 與年線 (MA284) 未來扣抵影響。
    當前股價 ${cp:.2f}，季線位於 ${m87:.2f}，年線位於 ${m284:.2f}。
    
    扣抵效應將在未來 30-90 天內對均線產生重要影響，請密切關注轉折點。
    """
    
    st.write_stream(_stream_text(analysis_text, speed=0.01))
    
    # Deduction Direction Indicator [E3]
    st.markdown("#### 📍 扣抵方向預測")
    future_days = [30, 60, 90]
    cols = st.columns(3)
    
    for col, days in zip(cols, future_days):
        with col:
            # Simple prediction logic
            if len(sdf) > days:
                old_close = sdf['Close'].iloc[-(days+1)]
                direction = "📈 UP" if cp > old_close else "📉 DOWN"
                direction_color = "#00FF7F" if cp > old_close else "#FF3131"
            else:
                direction = "➡️ HOLD"
                direction_color = "#FFD700"
            
            st.markdown(f"""
            <div style="text-align:center;padding:15px;background:rgba(0,0,0,0.3);border-radius:10px;border:1px solid {direction_color};">
                <div style="font-size:28px;margin-bottom:5px;">{direction}</div>
                <div style="font-size:12px;color:#888;">D+{days}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Show deduction table
    st.markdown("#### 📊 扣抵明細表")
    ded_data = []
    for i in range(min(90, len(sdf))):
        future_date = sdf.index[-1] + pd.Timedelta(days=i+1)
        if len(sdf) > 87 + i:
            drop_value = sdf['Close'].iloc[-(87+i+1)]
        else:
            drop_value = sdf['Close'].iloc[0]
        ded_data.append({
            'Date': future_date.strftime('%Y-%m-%d'),
            'Drop Value': f"{drop_value:.2f}",
            'Days': f"D+{i+1}"
        })
    
    if ded_data:
        ded_df = pd.DataFrame(ded_data[:30])  # Show first 30 days
        st.dataframe(ded_df, use_container_width=True, hide_index=True)

def _t2(sdf, ticker):
    """📐 亞當理論 (Adam Theory)"""
    st.markdown("### 📐 亞當理論 / Adam Theory")
    
    analysis_text = f"""
    **亞當理論核心原則:**
    
    市場永遠是對的。順勢而為，不預測反轉。
    在 {ticker} 的走勢中，我們追蹤對稱性與慣性延續。
    """
    
    st.write_stream(_stream_text(analysis_text, speed=0.015))
    
    # Calculate simple slope
    if len(sdf) >= 10:
        slope_10 = (sdf['Close'].iloc[-1] - sdf['Close'].iloc[-10]) / 10
        path_inertia = "🚀 向上慣性" if slope_10 > 0 else "🔻 向下慣性"
        
        st.metric("10日斜率", f"{slope_10:.3f}", path_inertia)
    
    # Plot recent price action
    recent = sdf.tail(60).reset_index()
    chart = alt.Chart(recent).mark_line(color='#00F5FF', strokeWidth=2).encode(
        x=alt.X('Date:T', title='Date'),
        y=alt.Y('Close:Q', title='Price', scale=alt.Scale(zero=False))
    ).properties(height=300)
    
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def _t3(sdf, ticker):
    """🕯️ 日K+RSI (Daily K + RSI)"""
    st.markdown("### 🕯️ 日K線 + RSI 指標 / Daily K-Line with RSI")
    
    # Calculate RSI [E1]
    delta = sdf['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    sdf['RSI'] = 100 - (100 / (1 + rs))
    
    # Prepare data
    recent = sdf.tail(120).reset_index()
    
    # Candlestick chart
    base = alt.Chart(recent).encode(x=alt.X('Date:T', title='Date'))
    
    rule = base.mark_rule(color='#888').encode(
        y=alt.Y('Low:Q', title='Price', scale=alt.Scale(zero=False)),
        y2='High:Q'
    )
    
    bars = base.mark_bar().encode(
        y='Open:Q',
        y2='Close:Q',
        color=alt.condition(
            "datum.Close >= datum.Open",
            alt.value("#00FF7F"),
            alt.value("#FF3131")
        )
    )
    
    candlestick = (rule + bars).properties(height=300)
    
    # RSI subplot
    rsi_chart = alt.Chart(recent).mark_line(color='#FFD700', strokeWidth=2).encode(
        x=alt.X('Date:T', title=''),
        y=alt.Y('RSI:Q', title='RSI', scale=alt.Scale(domain=[0, 100]))
    ).properties(height=100)
    
    # Add RSI threshold lines
    rsi_upper = alt.Chart(pd.DataFrame({'y': [70]})).mark_rule(color='#FF3131', strokeDash=[5, 5]).encode(y='y:Q')
    rsi_lower = alt.Chart(pd.DataFrame({'y': [30]})).mark_rule(color='#00FF7F', strokeDash=[5, 5]).encode(y='y:Q')
    
    rsi_with_lines = rsi_chart + rsi_upper + rsi_lower
    
    # Combined chart
    combined = alt.vconcat(candlestick, rsi_with_lines).resolve_scale(x='shared')
    
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(combined, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Current RSI value
    current_rsi = sdf['RSI'].iloc[-1]
    rsi_status = "超買" if current_rsi > 70 else ("超賣" if current_rsi < 30 else "中性")
    st.metric("當前 RSI(14)", f"{current_rsi:.1f}", rsi_status)

def _t4(sdf, ticker):
    """🗓️ 月K線 (Monthly K-Line)"""
    st.markdown("### 🗓️ 月K線圖 / Monthly K-Line")
    
    # Resample to monthly
    monthly = sdf.resample('ME').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    }).dropna()
    
    if len(monthly) == 0:
        st.toast("⚠️ 數據不足 / Insufficient Data", icon="⚡")
        return
    
    monthly_reset = monthly.reset_index()
    
    base = alt.Chart(monthly_reset).encode(x=alt.X('Date:T', title='Month'))
    
    rule = base.mark_rule(color='#666').encode(
        y=alt.Y('Low:Q', title='Price', scale=alt.Scale(zero=False)),
        y2='High:Q'
    )
    
    bars = base.mark_bar(width=20).encode(
        y='Open:Q',
        y2='Close:Q',
        color=alt.condition(
            "datum.Close >= datum.Open",
            alt.value("#00FF7F"),
            alt.value("#FF3131")
        )
    )
    
    chart = (rule + bars).properties(height=400)
    
    st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
    st.altair_chart(chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.toast("✅ 月K數據載入完成 / Monthly Data Loaded", icon="🎯")

def _t5(ticker, cp):
    """🧠 ARK戰情桌 (ARK Scenarios)"""
    st.markdown("### 🧠 ARK 投資戰情推演 / ARK Investment Scenarios")
    
    intro_text = """
    **ARK戰情推演系統:**
    
    基於 Cathie Wood 的情境分析方法，我們建構熊市/基準/牛市三種情境，
    推算未來5年的目標價與年化報酬率 (CAGR)。
    """
    
    st.write_stream(_stream_text(intro_text, speed=0.01))
    
    # Input parameters
    col1, col2 = st.columns(2)
    with col1:
        rev_ttm = st.number_input("年營收 (TTM)", value=100000000000.0, step=1000000000.0)
        shares = st.number_input("流通股數", value=1000000000.0, step=1000000.0)
    with col2:
        growth = st.slider("預期成長率", 0.0, 0.5, 0.15, 0.01)
        margin = st.slider("淨利率", 0.0, 0.5, 0.10, 0.01)
        pe = st.slider("目標本益比", 5.0, 100.0, 25.0, 1.0)
    
    if st.button("🚀 運算情境", type="primary"):
        st.toast("🚀 系統運算中 / Processing...", icon="⏳")
        
        scenarios = calculate_ark_scenarios(rev_ttm, shares, cp, growth, margin, pe)
        
        if scenarios:
            st.markdown("#### 📊 情境推演結果")
            
            cols = st.columns(3)
            scenario_colors = {'Bear': '#FF3131', 'Base': '#FFD700', 'Bull': '#00FF7F'}
            
            for col, (name, data) in zip(cols, scenarios.items()):
                with col:
                    st.markdown(f"""
                    <div style="background:rgba(0,0,0,0.3);padding:20px;border-radius:12px;border:2px solid {scenario_colors[name]};text-align:center;">
                        <div style="font-size:18px;color:{scenario_colors[name]};font-weight:700;margin-bottom:10px;">{name} Case</div>
                        <div style="font-size:32px;color:#FFF;margin:10px 0;">${data['Target']:.2f}</div>
                        <div style="font-size:14px;color:#888;">CAGR: {data['CAGR']*100:.1f}%</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.toast("✅ 情境推演完成 / Scenarios Calculated", icon="🎯")
        else:
            st.toast("⚠️ 參數錯誤 / Invalid Parameters", icon="⚡")

def _t6(ticker, cp):
    """💎 智能估值 (Smart Valuation)"""
    st.markdown("### 💎 智能估值引擎 / Smart Valuation Engine")
    
    valuation_text = """
    **DCF折現估值模型:**
    
    採用10年期現金流折現，結合成長率、利潤率、本益比與折現率，
    計算公司的內在價值 (Intrinsic Value)。
    """
    
    st.write_stream(_stream_text(valuation_text, speed=0.01))
    
    col1, col2 = st.columns(2)
    with col1:
        eps = st.number_input("每股盈餘 (EPS)", value=5.0, step=0.1)
        rev = st.number_input("營收 (億)", value=100.0, step=1.0) * 100000000
        shares = st.number_input("股數 (億)", value=10.0, step=0.1) * 100000000
    with col2:
        growth = st.slider("成長率", 0.0, 0.3, 0.10, 0.01, key="val_g")
        margin = st.slider("淨利率", 0.0, 0.3, 0.08, 0.01, key="val_m")
        pe = st.slider("本益比", 5.0, 50.0, 20.0, 1.0, key="val_pe")
        dr = st.slider("折現率", 0.05, 0.20, 0.10, 0.01)
    
    if st.button("💎 計算內在價值", type="primary"):
        st.toast("🚀 估值引擎啟動 / Valuation Engine Starting...", icon="⏳")
        
        fair_value = calculate_smart_valuation(eps, rev, shares, growth, margin, pe, dr)
        
        if fair_value > 0:
            upside = ((fair_value - cp) / cp) * 100
            upside_color = "#00FF7F" if upside > 0 else "#FF3131"
            
            st.markdown(f"""
            <div class="hero-container">
                <div class="hero-lbl">FAIR VALUE</div>
                <div class="hero-val">${fair_value:.2f}</div>
                <div style="font-size:24px;color:{upside_color};margin-top:15px;">
                    {"🚀 UPSIDE" if upside > 0 else "⚠️ DOWNSIDE"}: {abs(upside):.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.toast("✅ 估值完成 / Valuation Complete", icon="🎯")
        else:
            st.toast("⚠️ 估值失敗 / Valuation Failed", icon="⚡")

def _t7(sdf):
    """🌊 艾略特5波推演 (Elliott Wave Projection)"""
    st.markdown("### 🌊 艾略特5波模擬 / Elliott Wave Projection")
    
    wave_text = """
    **艾略特波浪理論:**
    
    識別當前波段的轉折點，並基於費波那契比例推演未來5波結構。
    系統將自動標記關鍵支撐/壓力位。
    """
    
    st.write_stream(_stream_text(wave_text, speed=0.01))
    
    # Calculate ZigZag
    st.toast("🚀 計算波浪結構 / Calculating Wave Structure...", icon="⏳")
    
    zigzag = calculate_zigzag(sdf, deviation=0.05)
    
    if not zigzag.empty and len(zigzag) >= 2:
        # Wave projection
        wave_sim = calculate_5_waves(zigzag)
        
        # Wave completion progress [E4]
        completion = min(100, (len(zigzag) / 8) * 100)  # Assume 8 pivots = complete cycle
        st.markdown(f"""
        <div style="margin:15px 0;">
            <div style="font-size:12px;color:#888;margin-bottom:5px;">波浪完成度 / Wave Completion</div>
            <div style="background:rgba(255,255,255,0.1);border-radius:10px;height:20px;overflow:hidden;">
                <div style="background:linear-gradient(90deg, #00F5FF, #FFD700);height:100%;width:{completion}%;transition:width 0.5s;"></div>
            </div>
            <div style="font-size:12px;color:#00F5FF;margin-top:5px;text-align:right;">{completion:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Prepare chart data
        chart_data = sdf.tail(200).reset_index()
        
        base_chart = alt.Chart(chart_data).mark_line(color='#444', strokeWidth=1).encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('Close:Q', title='Price', scale=alt.Scale(zero=False))
        )
        
        # ZigZag pivots
        zigzag_chart = alt.Chart(zigzag).mark_line(
            color='#00F5FF',
            strokeWidth=2,
            point=alt.OverlayMarkDef(filled=True, size=100, color='#FFD700')
        ).encode(
            x='Date:T',
            y='Price:Q'
        )
        
        # Wave projection
        if not wave_sim.empty:
            wave_chart = alt.Chart(wave_sim).mark_line(
                color='#FF9A3C',
                strokeWidth=2,
                strokeDash=[5, 5]
            ).encode(
                x='Date:T',
                y='Price:Q'
            )
            
            wave_labels = alt.Chart(wave_sim[wave_sim['Label'] != 'Origin']).mark_text(
                dy=-20,
                color='#FF9A3C',
                fontSize=12,
                fontWeight='bold'
            ).encode(
                x='Date:T',
                y='Price:Q',
                text='Label'
            )
            
            combined = base_chart + zigzag_chart + wave_chart + wave_labels
        else:
            combined = base_chart + zigzag_chart
        
        st.markdown('<div class="t3-chart">', unsafe_allow_html=True)
        st.altair_chart(combined.interactive(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.toast("✅ 波浪推演完成 / Wave Projection Complete", icon="🎯")
    else:
        st.toast("⚠️ 波動過小無法計算 / Volatility Too Low", icon="⚡")

# ── POSTER CONFIG ──────────────────────────────────────────────
POSTERS=[("t1","🔮","雙軌扣抵","DEDUCTION","#00F5FF"),("t2","📐","亞當理論","ADAM","#FFD700"),
         ("t3","🕯️","日K+RSI","DAILY K","#FF9A3C"),("t4","🗓️","月K線","MONTHLY","#FF3131"),
         ("t5","🧠","ARK戰情","ARK DESK","#00FF7F"),("t6","💎","智能估值","VALUATION","#B77DFF"),
         ("t7","🌊","5波模擬","ELLIOTT","#FF6BFF")]
RENDER={"t1":_t1,"t2":_t2,"t3":_t3,"t4":_t4,"t5":_t5,"t6":_t6,"t7":_t7}

# ── MAIN ───────────────────────────────────────────────────────
@st.fragment
def render():
    _inject_css()
    
    # [DC1] Show tactical guide modal on first visit
    if 't3_guide_shown' not in st.session_state:
        show_tactical_guide()
        return
    
    if 't3_active' not in st.session_state: 
        st.session_state.t3_active = "t1"
    
    # Header
    st.markdown(f"""<div style="display:flex;align-items:baseline;justify-content:space-between;
  padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,.052);margin-bottom:16px;">
  <div><span style="font-family:'Bebas Neue',sans-serif;font-size:26px;color:#FF9A3C;letter-spacing:3px;text-shadow:0 0 22px rgba(255,154,60,.32);">🎯 單兵狙擊</span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,154,60,.26);letter-spacing:3px;border:1px solid rgba(255,154,60,.10);border-radius:20px;padding:3px 13px;margin-left:14px;">SOLO SNIPER V100 — DIRECTOR'S CUT</span></div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(200,215,230,.20);letter-spacing:2px;text-align:right;line-height:1.7;">{datetime.now().strftime('%H:%M:%S')}<br>{datetime.now().strftime('%Y·%m·%d')}</div>
</div>""", unsafe_allow_html=True)
    
    with st.expander("3.1 萬用個股狙擊雷達 (Universal Sniper)", expanded=True):
        # [DC2] Replace st.info with toast
        st.toast("🌍 全球戰情模式已啟動 / Global Combat Mode Active", icon="🎯")
        
        ic, bc = st.columns([5, 1])
        with ic:
            w17_in = st.text_input("輸入代號或股名", value=st.session_state.get('t3_ticker', '2330'),
                                  placeholder="2330 / TSLA / BTC-USD", key="w17_final_v102").strip()
        with bc:
            st.markdown('<div style="margin-top:22px;"><div class="t3-action">', unsafe_allow_html=True)
            if st.button("🔍 搜尋", key="t3_search", use_container_width=True):
                st.session_state.t3_ticker = w17_in
            st.markdown('</div></div>', unsafe_allow_html=True)
        
        ticker_in = st.session_state.get('t3_ticker', '2330').strip()
        
        if not ticker_in:
            st.toast("⚠️ 請輸入標的代號 / Please Enter Ticker", icon="⚡")
            return
        
        try:
            from macro_risk import STOCK_METADATA
            N2T = {v['name'].strip(): k for k, v in STOCK_METADATA.items()}
            if ticker_in in N2T:
                ticker_in = N2T[ticker_in]
        except Exception:
            pass
        
        cands = [ticker_in]
        if ticker_in.isdigit():
            cands = [f"{ticker_in}.TW", f"{ticker_in}.TWO"]
        elif not ticker_in.endswith((".TW", ".TWO")):
            cands = [ticker_in.upper(), f"{ticker_in.upper()}.TW"]
        
        macro = _get_macro()
        sdf = pd.DataFrame()
        v_ticker = None
        
        with st.spinner("掃描全球資料庫..."):
            for c in cands:
                temp = macro.get_single_stock_data(c, period="max")
                if not temp.empty and len(temp) >= 300:
                    sdf = temp
                    v_ticker = c
                    break
        
        if sdf.empty:
            st.toast("❌ 查無數據或數據不足 / No Data or Insufficient History", icon="⚡")
            return
        
        # Data preprocessing
        try:
            if isinstance(sdf.columns, pd.MultiIndex):
                sdf.columns = sdf.columns.get_level_values(0)
            sdf.columns = [str(c).strip().capitalize() for c in sdf.columns]
            sdf = sdf.reset_index()
            dc = next((c for c in sdf.columns if str(c).lower() in ['date', 'datetime', 'index']), None)
            if dc:
                sdf.rename(columns={dc: 'Date'}, inplace=True)
                sdf['Date'] = pd.to_datetime(sdf['Date'])
                sdf.set_index('Date', inplace=True)
                sdf.sort_index(inplace=True)
            col_map = {}
            for c in sdf.columns:
                if c.lower() in ['close', 'price']:
                    col_map[c] = 'Close'
                elif c.lower() in ['volume', 'vol']:
                    col_map[c] = 'Volume'
            sdf.rename(columns=col_map, inplace=True)
            for req in ['Open', 'High', 'Low']:
                if req not in sdf.columns:
                    sdf[req] = sdf['Close']
            if 'Volume' not in sdf.columns:
                sdf['Volume'] = 0
            for c in ['Close', 'Open', 'High', 'Low', 'Volume']:
                sdf[c] = pd.to_numeric(sdf[c], errors='coerce')
            sdf = sdf.dropna(subset=['Close'])
        except Exception as e:
            st.toast(f"⚠️ 資料格式錯誤 / Data Format Error: {e}", icon="⚡")
            return
        
        # Calculate indicators
        sdf['MA87'] = sdf['Close'].rolling(87).mean()
        sdf['MA284'] = sdf['Close'].rolling(284).mean()
        sdf['Prev_MA87'] = sdf['MA87'].shift(1)
        sdf['Prev_MA284'] = sdf['MA284'].shift(1)
        sdf['Cross_Signal'] = 0
        sdf.loc[(sdf['Prev_MA87'] <= sdf['Prev_MA284']) & (sdf['MA87'] > sdf['MA284']), 'Cross_Signal'] = 1
        sdf.loc[(sdf['Prev_MA87'] >= sdf['Prev_MA284']) & (sdf['MA87'] < sdf['MA284']), 'Cross_Signal'] = -1
        
        cp = float(sdf['Close'].iloc[-1])
        op = float(sdf['Open'].iloc[-1])
        m87 = float(sdf['MA87'].iloc[-1]) if not pd.isna(sdf['MA87'].iloc[-1]) else 0
        m87p5 = float(sdf['MA87'].iloc[-6]) if len(sdf) > 6 and not pd.isna(sdf['MA87'].iloc[-6]) else m87
        m284 = float(sdf['MA284'].iloc[-1]) if not pd.isna(sdf['MA284'].iloc[-1]) else 0
        bias = ((cp - m87) / m87) * 100 if m87 > 0 else 0
        
        trend_days = 0
        trend_str = "整理中"
        trend_c = "#FFD700"
        
        if m87 > 0 and m284 > 0:
            is_bull = m87 > m284
            trend_str = "🔥 中期多頭 (87>284)" if is_bull else "❄️ 中期空頭 (87<284)"
            trend_c = "#00FF7F" if is_bull else "#FF6B6B"
            bs = sdf['MA87'] > sdf['MA284']
            cs = bs.iloc[-1]
            for i in range(len(bs) - 1, -1, -1):
                if bs.iloc[i] == cs:
                    trend_days += 1
                else:
                    break
        
        g_title, g_desc = get_advanced_granville(cp, op, m87, m87p5)
        bias_c = "#FF3131" if abs(bias) > 15 else ("#FFD700" if abs(bias) > 7 else "#00FF7F")
        
        st.toast("✅ 掃描完成 / Target Locked", icon="🎯")
        
        st.subheader(f"🎯 {v_ticker} 戰情報告")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("目前股價", f"{cp:.2f}")
        c2.metric("87MA (季線)", f"{m87:.2f}", f"{cp - m87:.2f}")
        c3.metric("284MA (年線)", f"{m284:.2f}", f"{cp - m284:.2f}")
        c4.metric("乖離率 (Bias)", f"{bias:.1f}%")
        
        st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:14px;color:rgba(200,215,230,.6);margin:6px 0 4px;"><span style="color:{trend_c};font-weight:700;">{trend_str}</span> &nbsp;·&nbsp; 持續 <span style="color:#FFD700;font-weight:700;">{trend_days}</span> 天 &nbsp;·&nbsp; 格蘭碧：<span style="color:#00F5FF;font-weight:700;">{g_title}</span> — {g_desc}</div>', unsafe_allow_html=True)
        
        _render_badges(sdf, cp, m87, m284, bias)
        
        st.markdown("---")
        
        # Poster Rail
        active = st.session_state.t3_active
        st.markdown('<div class="t3-rail"><div class="t3-rail-lbl">⬡ analysis modules — click to select</div>', unsafe_allow_html=True)
        p_cols = st.columns(7)
        for col, (key, icon, label, tag, accent) in zip(p_cols, POSTERS):
            is_a = (active == key)
            brd = f"2px solid {accent}" if is_a else "1px solid #1b2030"
            bg_c = "rgba(255,154,60,.08)" if is_a else "#090c14"
            lbl_c = accent if is_a else "rgba(200,215,230,.7)"
            glow = f"0 0 18px rgba(255,154,60,.10)" if is_a else "none"
            with col:
                st.markdown(f'<div style="height:128px;background:{bg_c};border:{brd};border-radius:14px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;box-shadow:{glow};margin-bottom:-51px;pointer-events:none;z-index:0;position:relative;"><div style="font-size:23px">{icon}</div><div style="font-family:Rajdhani,sans-serif;font-size:11px;font-weight:700;color:{lbl_c};text-align:center;padding:0 2px;">{label}</div><div style="font-family:JetBrains Mono,monospace;font-size:6px;color:#223;letter-spacing:1.5px;">{tag}</div></div>', unsafe_allow_html=True)
                if st.button(f"{icon}", key=f"p3_{key}", use_container_width=True):
                    st.session_state.t3_active = key
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="t3-content">', unsafe_allow_html=True)
        try:
            fn = RENDER[active]
            if active == "t1":
                fn(sdf, v_ticker, cp, m87, m87p5, m284)
            elif active in ("t2", "t3", "t4"):
                fn(sdf, v_ticker)
            elif active in ("t5", "t6"):
                fn(v_ticker, cp)
            elif active == "t7":
                fn(sdf)
        except Exception as exc:
            import traceback
            st.toast(f"❌ 子模組渲染失敗 / Module Render Failed: {exc}", icon="⚡")
            with st.expander("🔍 Debug"):
                st.code(traceback.format_exc())
        
        st.markdown(f'<div class="t3-foot">Titan Solo Sniper V100 — Director\'s Cut · {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
