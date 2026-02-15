# ui_desktop/tab6_metatrend.py
# Titan SOP V200 — Tab 6: 元趨勢戰法 (GLOBAL MARKET HOLOGRAM)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  Design: Netflix × Palantir × Sci-Fi Trading Interface           ║
# ║  Hero Billboard → Poster Rail → Holographic Content              ║
# ║  ALL engines preserved verbatim:                                  ║
# ║    7D Geometry (linregress), 22-Tier Titan Rating,               ║
# ║    Valkyrie Intel, TitanAgentCouncil, Geo Backtest               ║
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
# [SLOT-6.1] 數據引擎 (PRESERVED VERBATIM)
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
# [SLOT-6.2] 數學引擎 (PRESERVED VERBATIM — linregress)
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
# [SLOT-6.3] 22 階泰坦信評引擎 (PRESERVED VERBATIM)
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
# [SLOT-6.x] 瓦爾基里情報局 (PRESERVED VERBATIM)
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
# [SLOT-6.4] 戰略提示詞生成器 (PRESERVED VERBATIM)
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
# 視覺化輔助：7D 雷達圖 + K線圖 (PRESERVED VERBATIM)
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
# 宏觀對沖輔助：批次下載多資產收盤價 (PRESERVED VERBATIM)
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def _fetch_prices(tickers, period="1y"):
    try:
        raw = yf.download(list(tickers), period=period, progress=False, auto_adjust=True)
        prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
        return prices.dropna(how="all")
    except Exception:
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════
# 幾何回測引擎 (PRESERVED VERBATIM)
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=7200)
def _geo_backtest(ticker, thresh, period_k, start, capital):
    try:
        orig = ticker
        if ticker.isdigit() and len(ticker) >= 4:
            ticker = f"{ticker}.TW"
        df = yf.download(ticker, start=start, progress=False, auto_adjust=True)
        if df.empty and orig.isdigit():
            df = yf.download(f"{orig}.TWO", start=start, progress=False, auto_adjust=True)
        if df.empty or len(df) < 30:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if "Close" not in df.columns:
            return None
        if not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        monthly = df.resample("ME").agg({"Close": "last"}).dropna()
        if len(monthly) < 6:
            return None
        nm = {"3M": 3, "6M": 6, "1Y": 12, "3Y": 36}.get(period_k, 3)
        sigs = []
        for i in range(nm, len(monthly)):
            sl = monthly.iloc[i - nm:i]
            lp = np.log(sl["Close"].values)
            x  = np.arange(len(lp))
            s, *_ = linregress(x, lp)
            ang = float(np.arctan(s * 100) * (180 / np.pi))
            sigs.append({"Date": monthly.index[i], "Sig": 1 if ang > thresh else 0})
        sg = pd.DataFrame(sigs)
        if sg.empty:
            return None
        dfd = df.copy()
        dfd["Sig"] = 0
        for k in range(len(sg) - 1):
            mask = (dfd.index > sg.iloc[k]["Date"]) & (dfd.index <= sg.iloc[k + 1]["Date"])
            dfd.loc[mask, "Sig"] = sg.iloc[k]["Sig"]
        dfd.loc[dfd.index > sg.iloc[-1]["Date"], "Sig"] = sg.iloc[-1]["Sig"]
        dfd["Pct"]   = dfd["Close"].pct_change()
        dfd["Strat"] = dfd["Sig"].shift(1) * dfd["Pct"]
        dfd["BH"]    = dfd["Pct"]
        dfd["Eq"]    = (1 + dfd["Strat"].fillna(0)).cumprod() * capital
        dfd["BH_Eq"] = (1 + dfd["BH"].fillna(0)).cumprod()    * capital
        dfd["DD"]    = (dfd["Eq"] / dfd["Eq"].cummax()) - 1
        ny      = max(len(dfd) / 252, 0.01)
        tr      = dfd["Eq"].iloc[-1] / capital - 1
        cagr    = (1 + tr) ** (1 / ny) - 1
        dr      = dfd["Strat"].dropna()
        sharpe  = (dr.mean() * 252 - 0.02) / (dr.std() * np.sqrt(252)) if dr.std() > 0 else 0
        bh_r    = dfd["BH_Eq"].iloc[-1] / capital - 1
        bh_cagr = (1 + bh_r) ** (1 / ny) - 1
        return {
            "cagr": cagr, "mdd": dfd["DD"].min(), "sharpe": sharpe,
            "fe": dfd["Eq"].iloc[-1], "bh_cagr": bh_cagr,
            "eq": dfd["Eq"], "bh": dfd["BH_Eq"], "dd": dfd["DD"]
        }
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════
# CSS — GLOBAL MARKET HOLOGRAM
# ═══════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root{
  --c-gold:#FFD700;--c-cyan:#00F5FF;--c-red:#FF3131;
  --c-green:#00FF7F;--c-orange:#FF9A3C;
  --f-d:'Bebas Neue',sans-serif;
  --f-b:'Rajdhani',sans-serif;
  --f-m:'JetBrains Mono',monospace;
  --f-i:'Inter',sans-serif;
  --f-o:'Orbitron',sans-serif;
}

/* ══════════════════════════════════════════
   HERO BILLBOARD
   ══════════════════════════════════════════ */
.t6-hero {
  padding: 48px 40px 42px;
  background: linear-gradient(180deg,
    rgba(8,8,16,0) 0%,
    rgba(4,4,12,0.7) 50%,
    rgba(0,0,0,0.9) 100%);
  border-bottom: 1px solid rgba(0,245,255,0.1);
  text-align: center;
  margin-bottom: 30px;
  position: relative;
  overflow: hidden;
}
.t6-hero::before {
  content: '';
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 800px; height: 800px;
  background: radial-gradient(circle, rgba(0,245,255,0.03) 0%, transparent 60%);
  pointer-events: none;
}
.t6-hero::after {
  content: '';
  position: absolute;
  bottom: 50px; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%, rgba(0,245,255,0.12) 20%,
    rgba(0,245,255,0.3) 50%, rgba(0,245,255,0.12) 80%,
    transparent 100%);
  pointer-events: none;
}
.t6-hero-surtitle {
  font-family: var(--f-o);
  font-size: 11px;
  color: rgba(0,245,255,0.35);
  letter-spacing: 8px;
  text-transform: uppercase;
  margin-bottom: 14px;
}
.t6-hero-status {
  font-family: var(--f-i);
  font-size: 100px;
  font-weight: 900;
  letter-spacing: -4px;
  line-height: 1;
  margin-bottom: 10px;
}
.t6-hero-status.bull {
  color: #00FF7F;
  text-shadow: 0 0 60px rgba(0,255,127,0.25), 0 0 120px rgba(0,255,127,0.08);
}
.t6-hero-status.bear {
  color: #FF3131;
  text-shadow: 0 0 60px rgba(255,49,49,0.25), 0 0 120px rgba(255,49,49,0.08);
}
.t6-hero-status.neutral {
  color: #FFD700;
  text-shadow: 0 0 60px rgba(255,215,0,0.2);
}
.t6-hero-sub {
  font-family: var(--f-m);
  font-size: 10px;
  color: rgba(160,176,208,0.35);
  letter-spacing: 4px;
  text-transform: uppercase;
  margin-top: 6px;
}

/* ══════════════════════════════════════════
   NAVIGATION RAIL — 6 POSTER CARDS
   ══════════════════════════════════════════ */
.t6-nav-rail {
  display: flex; gap: 10px;
  margin-bottom: 32px;
  overflow-x: auto;
}
.t6-poster {
  flex: 1; min-width: 110px; min-height: 150px;
  background: rgba(255,255,255,0.015);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 14px;
  padding: 18px 12px 14px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center;
  position: relative; overflow: hidden;
  transition: all 0.3s ease;
}
.t6-poster::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--pa, rgba(255,255,255,0.04));
  border-radius: 14px 14px 0 0;
  opacity: 0.5;
}
.t6-poster.active {
  border-color: var(--c-cyan);
  background: rgba(0,245,255,0.04);
  box-shadow: 0 0 30px rgba(0,245,255,0.08), inset 0 0 30px rgba(0,245,255,0.02);
}
.t6-poster.active::before { opacity: 1; background: var(--c-cyan); }
.t6-poster-icon { font-size: 28px; margin-bottom: 8px; }
.t6-poster-title {
  font-family: var(--f-d);
  font-size: 14px; color: #FFF;
  letter-spacing: 1.5px; line-height: 1.3;
}
.t6-poster-sub {
  font-family: var(--f-m);
  font-size: 7px; color: rgba(140,155,178,0.4);
  letter-spacing: 1.5px; text-transform: uppercase;
  margin-top: 3px;
}

/* ══════════════════════════════════════════
   RANK BADGE (120px Metallic S-Tier)
   ══════════════════════════════════════════ */
.rank-badge {
  font-size: 120px; font-weight: 900;
  color: #FFF;
  text-shadow: 0 0 50px rgba(255,215,0,0.8), 2px 2px 0px #000;
  background: linear-gradient(135deg, #FFD700 0%, #B8860B 50%, #FFD700 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  font-family: var(--f-o);
  line-height: 1; letter-spacing: -2px;
  filter: drop-shadow(0 4px 12px rgba(255,215,0,0.3));
}
.rank-badge-wrap {
  text-align: center;
  padding: 30px 0 10px;
  position: relative;
}
.rank-badge-wrap::before {
  content: '';
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%,-50%);
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(255,215,0,0.06) 0%, transparent 60%);
  pointer-events: none;
}
.rank-badge-name {
  font-family: var(--f-b);
  font-size: 20px; font-weight: 700;
  color: rgba(255,215,0,0.7);
  letter-spacing: 2px; margin-top: 8px;
}
.rank-badge-desc {
  font-family: var(--f-m);
  font-size: 10px;
  color: rgba(160,176,192,0.4);
  letter-spacing: 2px; text-transform: uppercase;
  margin-top: 4px;
}

/* ══════════════════════════════════════════
   7D SPECTRUM ANALYZER (Trend Bars)
   ══════════════════════════════════════════ */
.trend-bar-container {
  display: flex; gap: 10px;
  justify-content: space-between;
  margin: 24px 0;
}
.trend-card {
  background: #111; border: 1px solid #333;
  flex: 1; padding: 16px 10px; text-align: center;
  border-radius: 10px;
  transition: transform 0.25s ease, box-shadow 0.25s ease;
  position: relative; overflow: hidden;
}
.trend-card:hover {
  transform: scale(1.08);
  box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
.trend-card::after {
  content: '';
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 4px;
  background: var(--tc-accent, #555);
  border-radius: 0 0 10px 10px;
}
.trend-card.up { --tc-accent: #00FF7F; border-color: rgba(0,255,127,0.2); }
.trend-card.dn { --tc-accent: #FF3131; border-color: rgba(255,49,49,0.2); }
.trend-card.flat { --tc-accent: #FFD700; border-color: rgba(255,215,0,0.15); }
.trend-card-period {
  font-family: var(--f-o);
  font-size: 11px; color: rgba(160,176,208,0.5);
  letter-spacing: 2px; margin-bottom: 8px;
}
.trend-val {
  font-size: 26px; font-weight: 800;
  font-family: var(--f-i);
  letter-spacing: -1px; line-height: 1;
}
.trend-val.up { color: #00FF7F; }
.trend-val.dn { color: #FF6B6B; }
.trend-val.flat { color: #FFD700; }
.trend-r2 {
  font-family: var(--f-m); font-size: 9px;
  color: rgba(160,176,208,0.35);
  letter-spacing: 1px; margin-top: 6px;
}

/* ══════════════════════════════════════════
   TERMINAL BOX (Valkyrie Intel)
   ══════════════════════════════════════════ */
.terminal-box {
  background: #0D1117;
  border: 1px solid #30363d;
  border-left: 4px solid #00F5FF;
  border-radius: 0 10px 10px 0;
  padding: 22px 24px;
  font-family: var(--f-m);
  color: #00F5FF;
  font-size: 12px;
  line-height: 1.6;
  position: relative;
  margin: 16px 0;
}
.terminal-box::before {
  content: '> VALKYRIE INTEL TERMINAL';
  display: block;
  font-size: 9px; letter-spacing: 3px;
  color: rgba(0,245,255,0.3);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0,245,255,0.08);
}

/* ══════════════════════════════════════════
   HUNTER LIST — TOP 10 RANK STYLE
   ══════════════════════════════════════════ */
.hunt-rank-card {
  display: flex; align-items: center; gap: 16px;
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 14px 18px;
  margin-bottom: 8px;
  transition: background 0.2s;
}
.hunt-rank-card:hover { background: rgba(255,255,255,0.04); }
.hunt-rank-num {
  font-family: var(--f-i);
  font-size: 36px; font-weight: 900;
  color: rgba(255,215,0,0.25);
  min-width: 50px; text-align: center;
  letter-spacing: -2px;
}
.hunt-rank-info { flex: 1; }
.hunt-rank-ticker {
  font-family: var(--f-d);
  font-size: 22px; color: #FFF;
  letter-spacing: 2px;
}
.hunt-rank-detail {
  font-family: var(--f-m);
  font-size: 10px;
  color: rgba(160,176,208,0.45);
  letter-spacing: 1px; margin-top: 2px;
}
.hunt-rank-badge {
  font-family: var(--f-o);
  font-size: 14px; font-weight: 700;
  padding: 4px 12px; border-radius: 20px;
  letter-spacing: 1px;
}

/* ══════════════════════════════════════════
   SECTION HEADER
   ══════════════════════════════════════════ */
.t6-sec-head{display:flex;align-items:center;gap:14px;
  padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,.052);margin-bottom:20px;}
.t6-sec-num{font-family:var(--f-d);font-size:56px;color:rgba(0,245,255,.06);letter-spacing:2px;line-height:1;}
.t6-sec-title{font-family:var(--f-d);font-size:22px;color:var(--sa,#00F5FF);letter-spacing:2px;}
.t6-sec-sub{font-family:var(--f-m);font-size:9px;color:rgba(0,245,255,.28);letter-spacing:2px;text-transform:uppercase;margin-top:2px;}

/* ══════════════════════════════════════════
   CHART PANEL
   ══════════════════════════════════════════ */
.t6-chart-panel{background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.055);
  border-radius:16px;padding:18px 12px 10px;margin:14px 0;overflow:hidden;}
.t6-chart-lbl{font-family:var(--f-m);font-size:9px;color:rgba(0,245,255,.28);
  letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;padding-left:6px;}

/* ══════════════════════════════════════════
   ACTION BUTTONS
   ══════════════════════════════════════════ */
.t6-action div.stButton>button{
  background:rgba(0,245,255,.05)!important;
  border:1px solid rgba(0,245,255,.25)!important;
  color:rgba(0,245,255,.85)!important;
  font-family:var(--f-m)!important;font-size:11px!important;
  letter-spacing:2px!important;min-height:48px!important;
  border-radius:12px!important;text-transform:uppercase!important;
}
.t6-action div.stButton>button:hover{
  background:rgba(0,245,255,.10)!important;
  box-shadow:0 0 24px rgba(0,245,255,.18)!important;
}

/* ══════════════════════════════════════════
   FOOTER
   ══════════════════════════════════════════ */
.t6-foot{font-family:var(--f-m);font-size:9px;color:rgba(70,90,110,.28);
  letter-spacing:2px;text-align:right;margin-top:28px;text-transform:uppercase;}
</style>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# HERO BILLBOARD — Global Trend Status
# ═══════════════════════════════════════════════════════════════
def _render_hero():
    """100px Bull/Bear/Neutral status — first thing user sees."""
    # Determine global trend from session if available
    status = "SCANNING"
    css_cls = "neutral"
    sub_text = "Awaiting analysis"

    if 'globe_scan_results' in st.session_state:
        df = st.session_state['globe_scan_results']
        if '3M角度' in df.columns and len(df) > 0:
            avg_3m = df['3M角度'].mean()
            if avg_3m > 15:
                status = "BULL"; css_cls = "bull"; sub_text = f"Global 3M avg: {avg_3m:+.1f}°"
            elif avg_3m < -15:
                status = "BEAR"; css_cls = "bear"; sub_text = f"Global 3M avg: {avg_3m:+.1f}°"
            else:
                status = "NEUTRAL"; css_cls = "neutral"; sub_text = f"Global 3M avg: {avg_3m:+.1f}°"

    if 'deep_geo' in st.session_state and 'deep_ticker' in st.session_state:
        geo = st.session_state['deep_geo']
        if geo:
            a3 = geo['3M']['angle']
            tk = st.session_state['deep_ticker']
            if a3 > 15:
                status = "BULL"; css_cls = "bull"; sub_text = f"{tk} 3M: {a3:+.1f}°"
            elif a3 < -15:
                status = "BEAR"; css_cls = "bear"; sub_text = f"{tk} 3M: {a3:+.1f}°"
            else:
                status = "NEUTRAL"; css_cls = "neutral"; sub_text = f"{tk} 3M: {a3:+.1f}°"

    st.markdown(f"""
<div class="t6-hero">
  <div class="t6-hero-surtitle">META-TREND HOLOGRAPHIC DECK</div>
  <div class="t6-hero-status {css_cls}">{status}</div>
  <div class="t6-hero-sub">{sub_text} &nbsp;&middot;&nbsp; {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# NAVIGATION RAIL — 6 Poster Cards
# ═══════════════════════════════════════════════════════════════
def _render_nav_rail():
    if 't6_active' not in st.session_state:
        st.session_state.t6_active = "6.1"

    cards = [
        ("6.1", "🌍", "全球視野",   "Global View"),
        ("6.2", "💎", "個股深鑽",   "Deep Dive"),
        ("6.3", "📜", "獵殺清單",   "Hunter List"),
        ("6.4", "⚔️",  "全境獵殺",   "Full Scan"),
        ("6.5", "🛡️", "宏觀對沖",   "Hedge"),
        ("6.6", "🧪", "回測沙盒",   "Sandbox"),
    ]
    cols = st.columns(6)
    for i, (sid, icon, title, sub) in enumerate(cards):
        with cols[i]:
            is_active = st.session_state.t6_active == sid
            cls = "active" if is_active else ""
            st.markdown(f"""
<div class="t6-poster {cls}" style="--pa:{'var(--c-cyan)' if is_active else 'rgba(255,255,255,0.04)'};">
  <div class="t6-poster-icon">{icon}</div>
  <div class="t6-poster-title">{sid} {title}</div>
  <div class="t6-poster-sub">{sub}</div>
</div>""", unsafe_allow_html=True)
            if st.button(f"Open {sid}", key=f"t6nav_{sid}", use_container_width=True):
                st.session_state.t6_active = sid
                st.rerun()


# ═══════════════════════════════════════════════════════════════
# 7D SPECTRUM ANALYZER HELPER
# ═══════════════════════════════════════════════════════════════
def _render_spectrum_analyzer(geo: dict, ticker: str):
    """7 vertical trend cards — the holographic 7D visualizer."""
    periods = ['35Y','10Y','5Y','3Y','1Y','6M','3M']
    st.markdown(f'<div class="trend-bar-container">', unsafe_allow_html=True)
    for p in periods:
        g = geo.get(p, {})
        angle = g.get('angle', 0)
        r2 = g.get('r2', 0)
        if angle > 5:
            cls = "up"; vcls = "up"
        elif angle < -5:
            cls = "dn"; vcls = "dn"
        else:
            cls = "flat"; vcls = "flat"
        st.markdown(f"""
<div class="trend-card {cls}">
  <div class="trend-card-period">{p}</div>
  <div class="trend-val {vcls}">{angle:+.1f}°</div>
  <div class="trend-r2">R² {r2:.3f}</div>
</div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SECTION 6.1 — 全球視野
# ═══════════════════════════════════════════════════════════════
def _s61():
    st.markdown('<div class="t6-sec-head" style="--sa:#00F5FF"><div class="t6-sec-num">6.1</div><div><div class="t6-sec-title">全球視野 — 多標的比較掃描</div><div class="t6-sec-sub">Multi-Asset 7D Geometry Comparison</div></div></div>', unsafe_allow_html=True)
    st.info("輸入多個代號(逗號分隔)，一鍵取得 7D 幾何信評對比。")

    col_in, col_btn = st.columns([3, 1])
    tickers_raw = col_in.text_input("標的代號", "NVDA,TSLA,2330.TW,2454.TW", key="globe_tickers")
    st.markdown('<div class="t6-action">', unsafe_allow_html=True)
    do_scan = col_btn.button("🔍 掃描", type="primary", key="globe_scan")
    st.markdown('</div>', unsafe_allow_html=True)

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


# ═══════════════════════════════════════════════════════════════
# SECTION 6.2 — 個股深鑽 (THE CROWN JEWEL)
# ═══════════════════════════════════════════════════════════════
def _s62():
    st.markdown('<div class="t6-sec-head" style="--sa:#FFD700"><div class="t6-sec-num">6.2</div><div><div class="t6-sec-title" style="color:#FFD700;">個股深鑽 — 7D 幾何 + 22 階信評 + 戰略提示詞</div><div class="t6-sec-sub">Deep Dive · Spectrum Analyzer · Rank Badge</div></div></div>', unsafe_allow_html=True)

    ticker_in = st.text_input("輸入代號", "NVDA", key="deep_ticker_v200").strip()

    st.markdown('<div class="t6-action">', unsafe_allow_html=True)
    do_deep = st.button("🚀 啟動深鑽分析", type="primary", key="btn_deep_v200")
    st.markdown('</div>', unsafe_allow_html=True)

    if do_deep:
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

        # ── THE RANK BADGE (120px S-Tier Metallic) ──
        st.markdown(f"""
<div class="rank-badge-wrap">
  <div class="rank-badge">{lvl}</div>
  <div class="rank-badge-name">{name}</div>
  <div class="rank-badge-desc">{desc}</div>
</div>""", unsafe_allow_html=True)

        if geo:
            # ── 7D SPECTRUM ANALYZER ──
            st.markdown("")
            _render_spectrum_analyzer(geo, ticker_in)

            # Acceleration & Phoenix indicators
            c1, c2 = st.columns(2)
            acc = geo['acceleration']
            acc_c = "#00FF7F" if acc > 0 else "#FF6B6B"
            c1.markdown(f"""
<div style="text-align:center;padding:12px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:12px;">
  <div style="font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:3px;margin-bottom:6px;">ACCELERATION (G-FORCE)</div>
  <div style="font-family:var(--f-i);font-size:42px;font-weight:800;color:{acc_c};line-height:1;letter-spacing:-1px;">{acc:+.1f}°</div>
</div>""", unsafe_allow_html=True)
            phx = geo['phoenix_signal']
            phx_c = "#FF6347" if phx else "rgba(100,115,135,0.3)"
            phx_txt = "🔥 TRIGGERED" if phx else "— INACTIVE"
            c2.markdown(f"""
<div style="text-align:center;padding:12px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);border-radius:12px;">
  <div style="font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,0.4);letter-spacing:3px;margin-bottom:6px;">PHOENIX SIGNAL</div>
  <div style="font-family:var(--f-i);font-size:28px;font-weight:800;color:{phx_c};line-height:1;">{phx_txt}</div>
</div>""", unsafe_allow_html=True)

            st.markdown("")
            _render_radar(geo, ticker_in)
            _render_monthly_chart(ticker_in)

        st.divider()

        # ── BATTLE PROMPT GENERATOR ──
        st.subheader("🤖 戰略提示詞生成器")

        left, right = st.columns(2)
        with left:
            st.markdown('<div class="t6-action">', unsafe_allow_html=True)
            if st.button("🤖 啟動瓦爾基里 (Auto-Fetch)", key="btn_valkyrie_v200"):
                with st.spinner("抓取情報…"):
                    st.session_state['valkyrie_report'] = _valkyrie_report(ticker_in)
                st.success("✅ 情報抓取完成！")
            st.markdown('</div>', unsafe_allow_html=True)
            intel_text = st.text_area("情報內容 (可編輯)",
                                      value=st.session_state.get('valkyrie_report',''),
                                      height=200, key="intel_text_deep_v200")
            note = st.text_area("統帥筆記", height=80, key="note_deep_v200",
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
            sel_p = st.multiselect("第一性原則", PRINCIPLES, key="principles_deep_v200")

        st.markdown('<div class="t6-action">', unsafe_allow_html=True)
        if st.button("📋 生成戰略提示詞", type="primary", key="gen_prompt_v200"):
            p = st.session_state.get('daily_price_data', {})
            price = 0.0
            for k, v in p.items():
                if ticker_in.split('.')[0] in k and v is not None and not v.empty:
                    price = float(v['Close'].iloc[-1]); break
            prompt = _generate_battle_prompt(ticker_in, price, geo or {}, rating, intel_text, note, sel_p)
            st.session_state['battle_prompt'] = prompt
            st.success("✅ 提示詞已生成！")
        st.markdown('</div>', unsafe_allow_html=True)

        if 'battle_prompt' in st.session_state:
            # ── TERMINAL BOX for output ──
            prompt_text = st.session_state['battle_prompt']
            st.markdown(f'<div class="terminal-box"><pre style="white-space:pre-wrap;margin:0;color:#c9d1d9;font-size:11px;">{prompt_text[:2000]}{"…" if len(prompt_text)>2000 else ""}</pre></div>', unsafe_allow_html=True)
            st.text_area("📋 完整提示詞 (可複製)", value=prompt_text,
                         height=300, key="prompt_out_v200")
            st.download_button("💾 下載提示詞",
                               prompt_text,
                               file_name=f"TITAN_{ticker_in}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                               use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# SECTION 6.3 — 獵殺清單 (TOP 10 RANK STYLE)
# ═══════════════════════════════════════════════════════════════
def _s63():
    st.markdown('<div class="t6-sec-head" style="--sa:#FF9A3C"><div class="t6-sec-num">6.3</div><div><div class="t6-sec-title" style="color:#FF9A3C;">獵殺清單 (Kill List)</div><div class="t6-sec-sub">V90.3 · Manual Entry + Real-time PnL Tracking</div></div></div>', unsafe_allow_html=True)

    # ── Entry UI ──
    with st.expander("➕ 新增獵殺目標", expanded=False):
        kc1, kc2, kc3 = st.columns(3)
        log_ticker = kc1.text_input("代號", key="kill_ticker_v200")
        log_action = kc2.selectbox("動作", ["Buy","Sell"], key="kill_action_v200")
        log_entry  = kc3.number_input("進場價", min_value=0.0, key="kill_entry_v200", step=0.01)
        kc4, kc5 = st.columns(2)
        log_target = kc4.number_input("目標價", min_value=0.0, key="kill_target_v200", step=0.01)
        log_stop   = kc5.number_input("停損價", min_value=0.0, key="kill_stop_v200",   step=0.01)
        log_note   = st.text_input("理由", key="kill_rationale_v200", placeholder="策略依據…")

        if st.button("✅ 加入清單", key="add_kill_v200"):
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
    st.markdown('<div class="t6-action">', unsafe_allow_html=True)
    if st.button("🔄 更新最新戰況 (Refresh PnL)", use_container_width=True, key="refresh_kl_v200"):
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
    st.markdown('</div>', unsafe_allow_html=True)

    # ── TOP 10 RANK DISPLAY ──
    if 'watchlist' in st.session_state and not st.session_state.watchlist.empty:
        wl = st.session_state.watchlist

        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("目前持倉", f"{len(wl[wl['Status']=='⏳ Holding'])} 檔")
        m2.metric("勝場",     f"{len(wl[wl['Status']=='🏆 Win'])} 檔")
        m3.metric("敗場",     f"{len(wl[wl['Status']=='💀 Loss'])} 檔")
        m4.metric("平均 PnL", f"{wl['PnL %'].mean():.2f}%" if not wl['PnL %'].isna().all() else "N/A")

        st.markdown("")
        # Render as rank cards
        for idx, (_, row) in enumerate(wl.iterrows()):
            pnl_val = row.get('PnL %', 0)
            pnl_display = f"{pnl_val:+.2f}%" if pd.notna(pnl_val) else "N/A"
            pnl_color = "#00FF7F" if pd.notna(pnl_val) and pnl_val >= 0 else "#FF6B6B"
            status = row.get('Status', '⏳')
            badge_bg = "rgba(0,255,127,0.12)" if "Win" in str(status) else ("rgba(255,49,49,0.12)" if "Loss" in str(status) else "rgba(255,215,0,0.08)")
            badge_border = "#00FF7F" if "Win" in str(status) else ("#FF6B6B" if "Loss" in str(status) else "#FFD700")
            st.markdown(f"""
<div class="hunt-rank-card">
  <div class="hunt-rank-num">{idx+1}</div>
  <div class="hunt-rank-info">
    <div class="hunt-rank-ticker">{row.get('Ticker','')}</div>
    <div class="hunt-rank-detail">{row.get('Action','')} @ {row.get('Entry Price',0):.2f} &nbsp;→&nbsp; Target {row.get('Target Price',0):.2f} &nbsp;|&nbsp; Stop {row.get('Stop Loss',0):.2f}</div>
  </div>
  <div style="text-align:right;">
    <div style="font-family:var(--f-i);font-size:22px;font-weight:800;color:{pnl_color};letter-spacing:-1px;">{pnl_display}</div>
    <div class="hunt-rank-badge" style="background:{badge_bg};border:1px solid {badge_border};color:{badge_border};">{status}</div>
  </div>
</div>""", unsafe_allow_html=True)

        # Fallback dataframe + clear
        with st.expander("📋 完整數據表", expanded=False):
            st.dataframe(wl.style.format({
                "Entry Price": "{:.2f}", "Target Price": "{:.2f}",
                "Stop Loss": "{:.2f}", "Current Price": "{:.2f}", "PnL %": "{:+.2f}%"
            }), use_container_width=True)
        if st.button("🗑️ 清空清單", type="secondary", use_container_width=True, key="clear_kl_v200"):
            st.session_state.watchlist = pd.DataFrame(columns=wl.columns)
            st.rerun()
    else:
        st.info("獵殺清單目前無目標。")


# ═══════════════════════════════════════════════════════════════
# SECTION 6.4 — 全境獵殺 (WAR_THEATERS)
# ═══════════════════════════════════════════════════════════════
def _s64():
    st.markdown('<div class="t6-sec-head" style="--sa:#FF3131"><div class="t6-sec-num">6.4</div><div><div class="t6-sec-title" style="color:#FF3131;">全境獵殺雷達 (The Hunter)</div><div class="t6-sec-sub">War Theater Scan · Phoenix / Awakening / Rocket Detection</div></div></div>', unsafe_allow_html=True)

    with st.expander("🎯 獵殺控制台", expanded=True):
        theater = st.selectbox("選擇掃描戰區", list(WAR_THEATERS.keys()), key="theater_sel_v200")
        count   = len(WAR_THEATERS.get(theater, []))
        st.info(f"戰區 **{theater}**，共 **{count}** 檔。")

        st.markdown('<div class="t6-action">', unsafe_allow_html=True)
        if st.button("🚀 啟動全境掃描", type="primary", key="btn_hunt_v200"):
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
        st.markdown('</div>', unsafe_allow_html=True)

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
            target = st.selectbox("選擇索敵目標", hr['代號'].tolist(), key="hunt_target_v200")
            st.markdown('<div class="t6-action">', unsafe_allow_html=True)
            if st.button("🔍 鎖定目標", type="primary", key="lock_target_v200"):
                with st.spinner(f"鎖定 {target}…"):
                    tgeo = _compute_7d(target)
                if tgeo:
                    trating = _titan_rating(tgeo)
                    st.session_state['hunt_tgeo']   = tgeo
                    st.session_state['hunt_trating'] = trating
                    st.session_state['hunt_target_name'] = target
                    st.success(f"✅ 鎖定！信評: **{trating[0]} — {trating[1]}**")
            st.markdown('</div>', unsafe_allow_html=True)

            if 'hunt_tgeo' in st.session_state and st.session_state.get('hunt_target_name') == target:
                tgeo = st.session_state['hunt_tgeo']
                trating = st.session_state['hunt_trating']
                lvl, name_t, desc_t, color_t = trating

                # Rank badge for target
                st.markdown(f"""
<div class="rank-badge-wrap">
  <div class="rank-badge" style="font-size:80px;">{lvl}</div>
  <div class="rank-badge-name">{name_t}</div>
  <div class="rank-badge-desc">{desc_t}</div>
</div>""", unsafe_allow_html=True)
                _render_spectrum_analyzer(tgeo, target)
                _render_radar(tgeo, target)

                st.markdown('<div class="t6-action">', unsafe_allow_html=True)
                if st.button("🤖 瓦爾基里情報", key="valk_hunt_v200"):
                    with st.spinner("抓取…"):
                        st.session_state['hunt_valk'] = _valkyrie_report(target)
                st.markdown('</div>', unsafe_allow_html=True)

                intel_h = st.text_area("情報", value=st.session_state.get('hunt_valk',''),
                                       height=150, key="intel_hunt_v200")
                note_h  = st.text_input("統帥筆記", key="note_hunt_v200")
                if st.button("📋 生成提示詞", key="gen_hunt_v200"):
                    dp = st.session_state.get('daily_price_data', {})
                    price_h = 0.0
                    for k,v in dp.items():
                        if target.split('.')[0] in k and v is not None and not v.empty:
                            price_h = float(v['Close'].iloc[-1]); break
                    pt = _generate_battle_prompt(target, price_h, tgeo, trating, intel_h, note_h, [])
                    st.markdown(f'<div class="terminal-box"><pre style="white-space:pre-wrap;margin:0;color:#c9d1d9;font-size:11px;">{pt[:1500]}</pre></div>', unsafe_allow_html=True)
                    st.text_area("提示詞", value=pt, height=300, key="hunt_prompt_out_v200")
                    st.download_button("💾 下載", pt,
                                       file_name=f"TITAN_HUNT_{target}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
        else:
            st.info("未發現符合條件的目標，請嘗試其他戰區。")


# ═══════════════════════════════════════════════════════════════
# SECTION 6.5 — 宏觀對沖
# ═══════════════════════════════════════════════════════════════
def _s65():
    st.markdown('<div class="t6-sec-head" style="--sa:#00FF7F"><div class="t6-sec-num">6.5</div><div><div class="t6-sec-title" style="color:#00FF7F;">宏觀對沖 (Macro Hedge)</div><div class="t6-sec-sub">Global Snapshot · Correlation Matrix · Beta Hedge + Rolling Beta</div></div></div>', unsafe_allow_html=True)

    # ── 全球市場快照 ────────────────────────────────────
    st.markdown("#### 全球市場即時快照 (最近5日)")
    SNAPS = [
        ("SPY","S&P500"), ("QQQ","NASDAQ100"), ("GLD","黃金"), ("TLT","美債20Y"),
        ("BTC-USD","比特幣"), ("^TWII","台灣加權"), ("DX-Y.NYB","美元指數"), ("^VIX","VIX恐慌"),
    ]
    with st.spinner("載入快照…"):
        try:
            snap_raw = yf.download([s for s, _ in SNAPS], period="5d",
                                   progress=False, auto_adjust=True)
            snap_px = (snap_raw["Close"]
                       if isinstance(snap_raw.columns, pd.MultiIndex)
                       else snap_raw).dropna(how="all")
        except Exception:
            snap_px = pd.DataFrame()
    if not snap_px.empty and len(snap_px) >= 2:
        hud_cols = st.columns(len(SNAPS))
        for idx, (tk, lbl) in enumerate(SNAPS):
            if tk not in snap_px.columns:
                continue
            s_col = snap_px[tk].dropna()
            if len(s_col) < 2:
                continue
            cur  = float(s_col.iloc[-1])
            prev = float(s_col.iloc[-2])
            chg  = (cur - prev) / prev * 100
            hud_cols[idx].metric(lbl, f"{cur:,.2f}", f"{chg:+.2f}%",
                                 delta_color="normal")
    else:
        st.warning("市場快照暫時無法取得，請稍後重試。")

    st.divider()

    # ── 多資產相關性矩陣 ───────────────────────────────────
    st.markdown("#### 多資產相關性矩陣")
    DEF_A = ["SPY","QQQ","GLD","TLT","BTC-USD","DX-Y.NYB"]
    col_a, col_b = st.columns([3, 1])
    with col_a:
        corr_tickers = st.multiselect(
            "選擇資產（可自由新增）",
            options=DEF_A + ["IWM","EEM","HYG","SOXX","NVDA","AAPL","TSLA","^VIX"],
            default=DEF_A, key="corr_tickers_t5_v200")
    with col_b:
        corr_period = st.selectbox("計算區間", ["1y","2y","3y","5y"], key="corr_period_t5_v200")

    st.markdown('<div class="t6-action">', unsafe_allow_html=True)
    if st.button("計算相關性矩陣", use_container_width=True, key="run_corr_t5_v200"):
        if len(corr_tickers) >= 2:
            with st.spinner("下載價格並計算…"):
                px_data = _fetch_prices(tuple(corr_tickers), corr_period)
            if not px_data.empty:
                corr_mat = px_data.pct_change().dropna().corr().round(3)
                st.session_state["corr_mat_t5"] = corr_mat
                st.toast("相關性矩陣計算完成", icon="✅")
            else:
                st.error("數據不足，請確認代號與網路。")
    st.markdown('</div>', unsafe_allow_html=True)

    if "corr_mat_t5" in st.session_state:
        cm = st.session_state["corr_mat_t5"]
        fig_hm = go.Figure(go.Heatmap(
            z=cm.values, x=cm.columns.tolist(), y=cm.index.tolist(),
            colorscale=[[0,"#FF3131"],[.5,"#1a1a2e"],[1,"#00FF7F"]],
            zmin=-1, zmax=1, zmid=0,
            text=cm.values.round(2), texttemplate="%{text:.2f}",
            textfont=dict(size=11, family="JetBrains Mono"),
            colorbar=dict(tickfont=dict(color="#A0B0C0", size=9))
        ))
        fig_hm.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=420,
            margin=dict(t=10, b=40, l=80, r=20),
            xaxis=dict(tickfont=dict(color="#B0C0D0", size=11)),
            yaxis=dict(tickfont=dict(color="#B0C0D0", size=11))
        )
        st.plotly_chart(fig_hm, use_container_width=True)
        high_pairs = [
            f"**{cm.columns[ii]} vs {cm.columns[jj]}**: {cm.iloc[ii,jj]:.2f}"
            for ii in range(len(cm.columns))
            for jj in range(ii + 1, len(cm.columns))
            if abs(cm.iloc[ii, jj]) > 0.75
        ]
        if high_pairs:
            st.info("高度相關對 (|r|>0.75)：" + " | ".join(high_pairs))

    st.divider()

    # ── Beta 對沖分析 + 滾動 Beta ──────────────────────────
    st.markdown("#### Beta 對沖分析 + 滾動 60 日 Beta")
    BENCH_MAP = {
        "SPY (S&P 500)": "SPY",
        "QQQ (NASDAQ 100)": "QQQ",
        "^TWII (台灣加權)": "^TWII",
        "GLD (黃金)": "GLD"
    }
    ba, bb, bc = st.columns([2, 1, 1])
    with ba:
        bench_name  = st.selectbox("基準指數", list(BENCH_MAP.keys()), key="bench_t5_v200")
    with bb:
        beta_period = st.selectbox("計算區間", ["1y","2y","3y"], key="beta_per_t5_v200")
    with bc:
        beta_ticker = st.text_input("分析標的", "NVDA", key="beta_tk_t5_v200")
    bench_tk = BENCH_MAP[bench_name]

    st.markdown('<div class="t6-action">', unsafe_allow_html=True)
    if st.button("計算 Beta", use_container_width=True, key="run_beta_t5_v200"):
        with st.spinner("計算中…"):
            beta_px = _fetch_prices(tuple([beta_ticker, bench_tk]), beta_period)
        if not beta_px.empty and beta_ticker in beta_px.columns and bench_tk in beta_px.columns:
            beta_ret = beta_px.pct_change().dropna()
            cov_v    = beta_ret[beta_ticker].cov(beta_ret[bench_tk])
            var_v    = beta_ret[bench_tk].var()
            beta_v   = round(cov_v / var_v, 3) if var_v > 0 else 0
            corr_v   = round(beta_ret[beta_ticker].corr(beta_ret[bench_tk]), 3)
            avol_v   = round(beta_ret[beta_ticker].std() * np.sqrt(252) * 100, 2)
            st.session_state["beta_result_t5"] = {
                "beta": beta_v, "corr": corr_v, "avol": avol_v,
                "ret": beta_ret, "tk": beta_ticker, "bk": bench_tk
            }
            st.toast("Beta 計算完成", icon="✅")
        else:
            st.error("數據不足，請確認代號。")
    st.markdown('</div>', unsafe_allow_html=True)

    if "beta_result_t5" in st.session_state:
        br = st.session_state["beta_result_t5"]
        bv = br["beta"]
        bk1, bk2, bk3, bk4 = st.columns(4)
        bk1.metric("Beta (β)",      f"{bv:.3f}")
        bk2.metric("與基準相關性",     f"{br['corr']:.3f}")
        bk3.metric("年化波動率",       f"{br['avol']:.2f}%")
        bk4.metric("建議對沖比例",     f"{abs(bv):.3f} x")
        if   bv > 1.5: st.warning(f"Beta {bv}: 高槓桿攻擊型，波動大幅放大市場")
        elif bv > 1.0: st.info(f"Beta {bv}: 略微放大市場波動，進攻型配置")
        elif bv > 0.5: st.success(f"Beta {bv}: 溫和跟隨市場，風險可控")
        elif bv > 0:   st.success(f"Beta {bv}: 防禦型，弱相關大盤")
        else:          st.info(f"Beta {bv} <= 0: 天然對沖工具，與大盤反向")

        rb_ret = br["ret"]; tk_b = br["tk"]; bk_b = br["bk"]; W = 60
        if len(rb_ret) > W:
            roll_b = [
                {"Date": rb_ret.index[i],
                 "Rolling Beta": (rb_ret.iloc[i-W:i][tk_b].cov(rb_ret.iloc[i-W:i][bk_b]) /
                                  rb_ret.iloc[i-W:i][bk_b].var()
                                  if rb_ret.iloc[i-W:i][bk_b].var() > 0 else 0)}
                for i in range(W, len(rb_ret))
            ]
            rb_df = pd.DataFrame(roll_b)
            fig_rb = px.line(rb_df, x="Date", y="Rolling Beta",
                             title=f"{tk_b} - 60日 Rolling Beta vs {bk_b}",
                             labels={"Rolling Beta": "Beta", "Date": "日期"})
            fig_rb.update_traces(line_color="#FF9A3C", line_width=1.8)
            fig_rb.add_hline(y=1, line_dash="dash", line_color="rgba(255,255,255,.2)",
                             annotation_text="Beta=1",
                             annotation_font_color="#aaa")
            fig_rb.add_hline(y=0, line_dash="dash",
                             line_color="rgba(255,255,255,.1)")
            fig_rb.update_layout(
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", height=270,
                margin=dict(t=30, b=40, l=60, r=10)
            )
            st.plotly_chart(fig_rb, use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# SECTION 6.6 — 回測沙盒
# ═══════════════════════════════════════════════════════════════
def _s66():
    st.markdown('<div class="t6-sec-head" style="--sa:#B77DFF"><div class="t6-sec-num">6.6</div><div><div class="t6-sec-title" style="color:#B77DFF;">幾何回測沙盒 (Geometry Backtest Sandbox)</div><div class="t6-sec-sub">Angle Signal · Dynamic Position · Equity Curve · Threshold Sweep · vs Buy & Hold</div></div></div>', unsafe_allow_html=True)

    # ── 參數設定 ──────────────────────────────────────────
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        bt_ticker = st.text_input("回測標的", "NVDA", key="bt_ticker_v200")
        bt_start  = st.date_input("起始日期", value=datetime(2015, 1, 1), key="bt_start_v200")
        bt_cap    = st.number_input("初始資金", value=1_000_000, step=100_000, key="bt_cap_v200")
    with col_p2:
        bt_win    = st.selectbox("幾何計算窗口", ["3M","6M","1Y","3Y"], key="bt_win_v200",
                                 help="每月底回望此窗口計算幾何角度")
        bt_thresh = st.slider("進場角度門檻 (°)", -90, 90, 10, key="bt_thresh_v200",
                              help="幾何角度 > 此值 → 下月持倉，否則空倉現金")
        st.info(f"策略：每月底計算 {bt_win} 幾何角度 > {bt_thresh} 度則持倉，否則現金")

    st.markdown('<div class="t6-action">', unsafe_allow_html=True)
    if st.button("啟動幾何回測", type="primary", use_container_width=True, key="run_bt_v200"):
        with st.spinner(f"回測 {bt_ticker} ({bt_win} > {bt_thresh})…"):
            r = _geo_backtest(bt_ticker, float(bt_thresh), bt_win,
                              bt_start.strftime("%Y-%m-%d"), float(bt_cap))
        if r:
            st.session_state["gbt"]     = r
            st.session_state["gbt_lbl"] = f"{bt_ticker} - {bt_win} - >{bt_thresh} deg"
            st.success(
                f"CAGR {r['cagr']:.2%} | Sharpe {r['sharpe']:.2f} | "
                f"MDD {r['mdd']:.2%} | B&H CAGR {r['bh_cagr']:.2%}"
            )
        else:
            st.error("回測失敗，請確認代號或延長起始日期。")
    st.markdown('</div>', unsafe_allow_html=True)

    if "gbt" in st.session_state:
        r   = st.session_state["gbt"]
        lbl = st.session_state.get("gbt_lbl", "")

        bm1, bm2, bm3, bm4, bm5 = st.columns(5)
        bm1.metric("CAGR",      f"{r['cagr']:.2%}")
        bm2.metric("Sharpe",    f"{r['sharpe']:.2f}")
        bm3.metric("最大回撤",  f"{r['mdd']:.2%}")
        bm4.metric("期末資金",  f"{r['fe']:,.0f}")
        bm5.metric("B&H CAGR", f"{r['bh_cagr']:.2%}")

        alpha = r["cagr"] - r["bh_cagr"]
        if alpha >= 0:
            st.success(f"幾何策略 Alpha: +{alpha:.2%} (優於買入持有策略)")
        else:
            st.warning(f"幾何策略 Alpha: {alpha:.2%} (落後買入持有策略)")

        st.divider()

        # 權益曲線
        eq_df = r["eq"].reset_index(); eq_df.columns = ["Date", "Equity"]
        bh_df = r["bh"].reset_index(); bh_df.columns = ["Date", "BH"]
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=eq_df["Date"], y=eq_df["Equity"], name="幾何策略",
            line=dict(color="#00F5FF", width=2),
            hovertemplate="幾何策略 $%{y:,.0f}<extra></extra>"))
        fig_eq.add_trace(go.Scatter(
            x=bh_df["Date"], y=bh_df["BH"], name="Buy & Hold",
            line=dict(color="rgba(255,215,0,.6)", width=1.5, dash="dot"),
            hovertemplate="B&H $%{y:,.0f}<extra></extra>"))
        fig_eq.update_layout(
            title=dict(text=f"權益曲線 - {lbl}",
                       font=dict(color="rgba(0,245,255,.4)", size=11,
                                 family="JetBrains Mono")),
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=360,
            legend=dict(font=dict(color="#B0C0D0", size=11)),
            margin=dict(t=30, b=40, l=70, r=10), hovermode="x unified",
            yaxis=dict(gridcolor="rgba(255,255,255,.04)"),
            xaxis=dict(gridcolor="rgba(255,255,255,.04)"))
        st.plotly_chart(fig_eq, use_container_width=True)

        # Underwater 回撤圖
        dd_df = r["dd"].reset_index(); dd_df.columns = ["Date", "DD"]
        dd_df["DD_pct"] = dd_df["DD"] * 100
        fig_dd = px.area(dd_df, x="Date", y="DD_pct",
                         labels={"DD_pct": "回撤 (%)", "Date": "日期"},
                         title="Underwater 回撤曲線")
        fig_dd.update_traces(fillcolor="rgba(255,49,49,.22)",
                             line_color="rgba(255,49,49,.75)")
        fig_dd.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", height=230,
            yaxis=dict(ticksuffix="%", gridcolor="rgba(255,255,255,.04)"),
            margin=dict(t=30, b=40, l=60, r=10))
        st.plotly_chart(fig_dd, use_container_width=True)

        st.divider()

        # ── 多門檻掃描 ─────────────────────────────────
        st.subheader("多門檻掃描 (Threshold Sweep)")
        st.caption("自動掃描 -30 到 +50 度（步進 5 度），找出最優 CAGR / Sharpe 組合")

        st.markdown('<div class="t6-action">', unsafe_allow_html=True)
        if st.button("啟動門檻掃描", use_container_width=True, key="run_sweep_v200"):
            sweep_list = list(range(-30, 55, 5))
            sweep_rows = []
            sweep_prog = st.progress(0, "掃描中…")
            for sw_idx, sw_th in enumerate(sweep_list):
                sw_r = _geo_backtest(bt_ticker, float(sw_th), bt_win,
                                     bt_start.strftime("%Y-%m-%d"), float(bt_cap))
                sweep_prog.progress((sw_idx + 1) / len(sweep_list),
                                    text=f"門檻 {sw_th} 度…")
                if sw_r:
                    sweep_rows.append({
                        "門檻 (度)": sw_th,
                        "CAGR":     sw_r["cagr"],
                        "Sharpe":   sw_r["sharpe"],
                        "MDD":      sw_r["mdd"]
                    })
            sweep_prog.empty()
            if sweep_rows:
                sw_df = pd.DataFrame(sweep_rows)
                best  = sw_df.loc[sw_df["CAGR"].idxmax()]
                st.success(
                    f"最優門檻: {int(best['門檻 (度)'])} 度 "
                    f"-> CAGR {best['CAGR']:.2%} | Sharpe {best['Sharpe']:.2f}")
                st.session_state["sweep_df"] = sw_df
            else:
                st.error("掃描失敗，請確認標的代號。")
        st.markdown('</div>', unsafe_allow_html=True)

        if "sweep_df" in st.session_state:
            sw_df = st.session_state["sweep_df"]
            best  = sw_df.loc[sw_df["CAGR"].idxmax()]

            fig_sw = go.Figure()
            fig_sw.add_trace(go.Scatter(
                x=sw_df["門檻 (度)"], y=sw_df["CAGR"] * 100,
                name="CAGR (%)", mode="lines+markers",
                line=dict(color="#00FF7F", width=2),
                hovertemplate="%{x} deg -> CAGR %{y:.2f}%<extra></extra>"))
            fig_sw.add_trace(go.Scatter(
                x=sw_df["門檻 (度)"], y=sw_df["Sharpe"],
                name="Sharpe", mode="lines+markers",
                line=dict(color="#FFD700", width=1.5, dash="dash"),
                yaxis="y2",
                hovertemplate="Sharpe %{y:.2f}<extra></extra>"))
            fig_sw.add_vline(
                x=int(best["門檻 (度)"]), line_dash="dot",
                line_color="rgba(255,215,0,.4)",
                annotation_text=f"最優 {int(best['門檻 (度)'])} 度",
                annotation_font=dict(color="#FFD700", size=11))
            fig_sw.update_layout(
                title=dict(text=f"門檻掃描 - {bt_ticker} - {bt_win}",
                           font=dict(color="rgba(255,215,0,.35)", size=11)),
                template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)", height=310,
                yaxis=dict(title="CAGR (%)", ticksuffix="%",
                           gridcolor="rgba(255,255,255,.04)",
                           titlefont=dict(color="#00FF7F"),
                           tickfont=dict(color="#778899", size=10)),
                yaxis2=dict(title="Sharpe", overlaying="y", side="right",
                            titlefont=dict(color="#FFD700"),
                            tickfont=dict(color="#778899", size=10)),
                xaxis=dict(ticksuffix=" deg",
                           gridcolor="rgba(255,255,255,.04)",
                           tickfont=dict(color="#778899", size=10)),
                legend=dict(font=dict(color="#B0C0D0", size=11)),
                margin=dict(t=30, b=40, l=70, r=70),
                hovermode="x unified")
            st.plotly_chart(fig_sw, use_container_width=True)

            st.dataframe(sw_df.style.format({
                "CAGR": "{:.2%}", "Sharpe": "{:.2f}", "MDD": "{:.2%}"
            }), use_container_width=True)

            buf_xl = io.BytesIO()
            try:
                with pd.ExcelWriter(buf_xl, engine="xlsxwriter") as wr:
                    sw_df.to_excel(wr, index=False, sheet_name="Threshold_Sweep")
                st.download_button(
                    "下載掃描報表 (Excel)", buf_xl.getvalue(),
                    f"{bt_ticker}_geo_sweep_{bt_win}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            except Exception:
                st.download_button(
                    "下載掃描報表 (CSV)", sw_df.to_csv(index=False).encode(),
                    f"{bt_ticker}_geo_sweep_{bt_win}.csv", "text/csv",
                    use_container_width=True)


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY
# ═══════════════════════════════════════════════════════════════
def render():
    """Tab 6 — 元趨勢戰法  Global Market Hologram V200"""
    _inject_css()

    # ── 1. HERO BILLBOARD ──
    _render_hero()

    # ── 2. NAVIGATION RAIL ──
    _render_nav_rail()

    # ── 3. ACTIVE SECTION ──
    section_map = {
        "6.1": (_s61, "6.1"),
        "6.2": (_s62, "6.2"),
        "6.3": (_s63, "6.3"),
        "6.4": (_s64, "6.4"),
        "6.5": (_s65, "6.5"),
        "6.6": (_s66, "6.6"),
    }

    active = st.session_state.get('t6_active', '6.1')
    fn, label = section_map.get(active, (_s61, "6.1"))
    try:
        fn()
    except Exception as exc:
        import traceback
        st.error(f"❌ Section {label} 發生錯誤: {exc}")
        with st.expander(f"🔍 Debug — {label}"):
            st.code(traceback.format_exc())

    # ── FOOTER ──
    st.markdown(
        f'<div class="t6-foot">Titan MetaTrend Holographic Deck V200 · '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',
        unsafe_allow_html=True,
    )
