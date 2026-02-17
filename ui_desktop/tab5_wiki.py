# ui_desktop/tab5_wiki.py
# Titan OS V400 — Tab 5: 通用市場分析儀 (Universal Market Analyzer)
# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Architecture: 6-Module Universal Analyzer (De-coupled from CB)     ║
# ║  Supports: US Stocks · TW Stocks · ETFs                             ║
# ║  5.1 籌碼K線  5.2 起漲K線  5.3 權證小哥                            ║
# ║  5.4 艾蜜莉  5.5 13F巨鯨  5.6 戰略百科                             ║
# ╚══════════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import yfinance as yf
from datetime import datetime, timedelta
import time
import traceback


# ══════════════════════════════════════════════════════════════
# 🎨 CSS — CLASSIFIED INTEL DOSSIER THEME (UPGRADED V400)
# ══════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;700&family=Orbitron:wght@400;600;700;900&display=swap" rel="stylesheet">
<style>
:root {
    --c-gold:   #FFD700;
    --c-cyan:   #00F5FF;
    --c-red:    #FF3131;
    --c-green:  #00FF7F;
    --c-orange: #FF9A3C;
    --c-purple: #B77DFF;
    --f-d: 'Bebas Neue', sans-serif;
    --f-b: 'Rajdhani', sans-serif;
    --f-m: 'JetBrains Mono', monospace;
    --f-o: 'Orbitron', sans-serif;
}

/* ── HERO ── */
.t5-hero {
    padding: 44px 40px 32px;
    background: linear-gradient(180deg, rgba(8,8,20,0) 0%, rgba(4,4,14,.75) 60%, rgba(0,0,0,.95) 100%);
    border-bottom: 1px solid rgba(0,245,255,.07);
    text-align: center;
    margin-bottom: 24px;
}
.t5-hero-label {
    font-family: var(--f-o);
    font-size: 9px;
    color: rgba(255,49,49,.4);
    letter-spacing: 10px;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.t5-hero-title {
    font-family: var(--f-d);
    font-size: 68px;
    color: #FFF;
    letter-spacing: 4px;
    line-height: 1;
    text-shadow: 0 0 60px rgba(0,245,255,.08);
}
.t5-hero-sub {
    font-family: var(--f-m);
    font-size: 9px;
    color: rgba(160,176,208,.28);
    letter-spacing: 4px;
    text-transform: uppercase;
    margin-top: 10px;
}

/* ── NAV POSTER RAIL ── */
.t5-nav-rail {
    background: linear-gradient(165deg, #07080f, #0b0c18);
    border: 1px solid rgba(255,255,255,.05);
    border-radius: 18px;
    padding: 18px 14px;
    margin-bottom: 20px;
}
.t5-nav-rail-lbl {
    font-family: var(--f-m);
    font-size: 8px;
    letter-spacing: 4px;
    color: rgba(0,245,255,.25);
    text-transform: uppercase;
    margin-bottom: 14px;
    text-align: center;
}

/* Nav card overlay pattern (same as tab3 fix) */
.t5-nav-rail [data-testid="stButton"] > button {
    opacity: 0 !important;
    height: 120px !important;
    margin-top: -120px !important;
    position: relative !important;
    z-index: 10 !important;
    cursor: pointer !important;
    width: 100% !important;
    min-height: 120px !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* ── SECTION HEADER ── */
.t5-sec-hd {
    display: flex;
    align-items: center;
    gap: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(255,255,255,.05);
    margin-bottom: 22px;
}
.t5-sec-num {
    font-family: var(--f-d);
    font-size: 52px;
    color: rgba(0,245,255,.05);
    line-height: 1;
}
.t5-sec-title {
    font-family: var(--f-d);
    font-size: 22px;
    letter-spacing: 2px;
}
.t5-sec-sub {
    font-family: var(--f-m);
    font-size: 8px;
    color: rgba(160,176,208,.3);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 3px;
}

/* ── KPI CARDS ── */
.t5-kpi {
    background: rgba(255,255,255,.022);
    border: 1px solid rgba(255,255,255,.06);
    border-top: 2px solid var(--kc, #00F5FF);
    border-radius: 14px;
    padding: 20px 18px;
    text-align: center;
}
.t5-kpi-lbl {
    font-family: var(--f-m);
    font-size: 9px;
    color: rgba(140,155,178,.5);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
}
.t5-kpi-val {
    font-family: var(--f-d);
    font-size: 48px;
    color: #FFF;
    line-height: .9;
}
.t5-kpi-sub {
    font-family: var(--f-b);
    font-size: 12px;
    color: var(--kc, #00F5FF);
    font-weight: 600;
    margin-top: 6px;
}

/* ── TRAFFIC LIGHT ── */
.tl-wrap {
    display: flex;
    justify-content: center;
    gap: 32px;
    padding: 36px 20px;
    background: rgba(0,0,0,.35);
    border: 1px solid rgba(255,255,255,.05);
    border-radius: 20px;
    margin: 16px 0;
}
.tl-circle {
    width: 110px;
    height: 110px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: var(--f-b);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    transition: all .3s;
    position: relative;
}
.tl-circle.dim {
    opacity: .12;
    filter: grayscale(.8);
}
.tl-circle.active {
    opacity: 1;
}
.tl-circle.active::after {
    content: '';
    position: absolute;
    inset: -8px;
    border-radius: 50%;
    border: 2px solid currentColor;
    animation: tl-pulse 2s ease-in-out infinite;
}
@keyframes tl-pulse {
    0%, 100% { transform: scale(1); opacity: .6; }
    50%       { transform: scale(1.08); opacity: 1; }
}
.tl-red    { background: radial-gradient(circle at 35% 35%, #ff5555, #991111); color: #FFB3B3; }
.tl-yellow { background: radial-gradient(circle at 35% 35%, #FFD700, #9A7A00); color: #FFF3B0; }
.tl-green  { background: radial-gradient(circle at 35% 35%, #00FF7F, #006635); color: #B3FFD8; }

/* ── CODEX CARDS ── */
.codex-card {
    background: rgba(255,255,255,.022);
    border: 1px solid rgba(80,90,110,.22);
    border-left: 4px solid #00F5FF;
    padding: 20px 22px 16px;
    margin-bottom: 12px;
    border-radius: 0 10px 10px 0;
    position: relative;
    overflow: hidden;
}
.codex-card::before {
    content: 'CLASSIFIED';
    position: absolute;
    top: 8px; right: 12px;
    font-family: var(--f-o);
    font-size: 7px;
    color: rgba(255,49,49,.15);
    letter-spacing: 4px;
}
.codex-card.gold { border-left-color: #FFD700; }
.codex-card.gold::before { content: 'PRIORITY'; }
.codex-card.red  { border-left-color: #FF3131; }
.codex-card.red::before  { content: 'CRITICAL'; }
.codex-card.green{ border-left-color: #00FF7F; }
.codex-card.green::before{ content: 'ACTIVE'; }
.codex-card-title  { font-family: var(--f-b); font-size: 17px; font-weight: 700; color: #FFF; letter-spacing: 1px; margin-bottom: 5px; }
.codex-card-key    { font-family: var(--f-b); font-size: 14px; font-weight: 600; color: rgba(0,245,255,.8); line-height: 1.5; margin-bottom: 6px; }
.codex-card-detail { font-family: var(--f-m); font-size: 11px; color: rgba(160,176,208,.48); line-height: 1.7; }

/* ── WHALE TABLE ── */
.whale-row {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 16px;
    background: rgba(255,255,255,.015);
    border: 1px solid rgba(255,255,255,.04);
    border-radius: 8px; margin-bottom: 6px;
}
.whale-rank { font-family: var(--f-o); font-size: 11px; color: rgba(255,215,0,.35); min-width: 26px; }
.whale-name { font-family: var(--f-b); font-size: 13px; font-weight: 600; color: rgba(0,245,255,.8); flex: 1; }
.whale-shares{ font-family: var(--f-m); font-size: 11px; color: rgba(160,176,208,.5); }
.whale-pct   { font-family: var(--f-m); font-size: 11px; color: rgba(0,255,127,.6); min-width: 60px; text-align: right; }

/* ── SECTOR ROW ── */
.sector-row { display: flex; align-items: center; gap: 12px; padding: 9px 14px; background: rgba(255,255,255,.015); border: 1px solid rgba(255,255,255,.04); border-radius: 8px; margin-bottom: 6px; }
.sector-name { font-family: var(--f-b); font-size: 14px; font-weight: 700; color: rgba(0,245,255,.7); min-width: 120px; }
.sector-stk  { font-family: var(--f-m); font-size: 11px; color: rgba(160,176,208,.48); }

/* ── SIGNAL BADGE ── */
.sig-badge {
    display: inline-block;
    font-family: var(--f-m);
    font-size: 11px;
    letter-spacing: 1px;
    border-radius: 20px;
    padding: 6px 16px;
    border: 1px solid;
    margin: 6px 4px;
}

/* ── FOOTER ── */
.t5-foot {
    font-family: var(--f-m);
    font-size: 9px;
    color: rgba(70,90,110,.22);
    letter-spacing: 2px;
    text-align: right;
    margin-top: 30px;
    padding-top: 18px;
    border-top: 1px solid rgba(255,255,255,.03);
    text-transform: uppercase;
}
</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 🌐 DATA FETCHER (Cached per ticker, TTL 5 min)
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def _fetch(symbol: str):
    """
    Returns (hist_1y, hist_3y, info, holders, error_str)
    All failures return empty frames + error message.
    """
    try:
        tk = yf.Ticker(symbol)
        hist_1y = tk.history(period="1y")
        hist_3y = tk.history(period="3y")
        if hist_1y.empty:
            return pd.DataFrame(), pd.DataFrame(), {}, pd.DataFrame(), f"No data for '{symbol}'. Check the symbol."
        # Drop tz-awareness for Altair compatibility
        if hasattr(hist_1y.index, 'tz') and hist_1y.index.tz is not None:
            hist_1y.index = hist_1y.index.tz_localize(None)
        if hasattr(hist_3y.index, 'tz') and hist_3y.index.tz is not None:
            hist_3y.index = hist_3y.index.tz_localize(None)
        info    = tk.info or {}
        try:
            holders = tk.institutional_holders
            if holders is None:
                holders = pd.DataFrame()
        except Exception:
            holders = pd.DataFrame()
        return hist_1y, hist_3y, info, holders, None
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), {}, pd.DataFrame(), str(e)


# ══════════════════════════════════════════════════════════════
# 🎴 HERO BILLBOARD
# ══════════════════════════════════════════════════════════════
def _render_hero(symbol: str):
    st.markdown(f"""
<div class="t5-hero">
  <div class="t5-hero-label">⬡ titan os v400 · universal market analyzer · restricted access</div>
  <div class="t5-hero-title">MARKET INTEL HUB</div>
  <div class="t5-hero-sub">US Stocks · TW Stocks · ETFs — Active Target: <span style="color:#00F5FF;opacity:.9;">{symbol}</span></div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 🔍 SEARCH BAR
# ══════════════════════════════════════════════════════════════
def _render_search() -> str:
    st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(0,245,255,.3);
    letter-spacing:3px;text-transform:uppercase;margin-bottom:6px;">
    ⬡ TARGET ACQUISITION — ENTER SYMBOL TO LOCK ON
</div>""", unsafe_allow_html=True)
    col_in, col_btn, col_tip = st.columns([3, 1, 4])
    with col_in:
        sym = st.text_input(
            "輸入代號 (Symbol)",
            value=st.session_state.get("t5_symbol", "SPY"),
            placeholder="AAPL · NVDA · 2330.TW · 0050.TW",
            label_visibility="collapsed",
            key="t5_sym_input"
        )
    with col_btn:
        if st.button("🔍 鎖定", use_container_width=True, type="primary"):
            st.session_state["t5_symbol"] = sym.strip().upper()
            st.rerun()
    with col_tip:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(160,176,208,.3);
    padding:8px 0;line-height:1.6;">
    美股: AAPL · NVDA · TSLA &nbsp;|&nbsp; 台股: 2330.TW · 2454.TW &nbsp;|&nbsp; ETF: SPY · 0050.TW
</div>""", unsafe_allow_html=True)
    return st.session_state.get("t5_symbol", sym.strip().upper() if sym else "SPY")


# ══════════════════════════════════════════════════════════════
# 🗺️ POSTER RAIL NAVIGATION
# ══════════════════════════════════════════════════════════════
_NAV = [
    ("5.1", "🕵️", "籌碼K線",  "Chip Master",    "#00F5FF"),
    ("5.2", "🚀", "起漲K線",  "Rising K",        "#00FF7F"),
    ("5.3", "⚡", "權證小哥", "Tick Master",      "#FFD700"),
    ("5.4", "🚦", "艾蜜莉",   "Value Queen",      "#FF9A3C"),
    ("5.5", "🐋", "13F巨鯨",  "Whale Watcher",    "#B77DFF"),
    ("5.6", "📜", "戰略百科", "The Codex",        "#FF3131"),
]

def _render_nav():
    if "t5_active" not in st.session_state:
        st.session_state.t5_active = "5.1"
    active = st.session_state.t5_active

    st.markdown('<div class="t5-nav-rail"><div class="t5-nav-rail-lbl">⬡ ANALYSIS MODULES — CLICK TO SELECT</div>', unsafe_allow_html=True)
    cols = st.columns(6)
    for col, (sid, icon, title, sub, accent) in zip(cols, _NAV):
        is_a = (active == sid)
        brd  = f"2px solid {accent}" if is_a else "1px solid rgba(255,255,255,0.06)"
        bg   = f"rgba(0,0,0,.15)" if is_a else "rgba(255,255,255,0.015)"
        glow = f"0 0 22px {accent}22, 0 4px 20px rgba(0,0,0,.5)" if is_a else "0 2px 12px rgba(0,0,0,.4)"
        lbl_c= accent if is_a else "rgba(200,215,230,.7)"
        tag_c= accent if is_a else "rgba(100,120,140,.45)"
        top_bar = f'<div style="position:absolute;top:0;left:15%;right:15%;height:2px;background:{accent};border-radius:0 0 2px 2px;"></div>' if is_a else ""
        with col:
            st.markdown(f"""
<div style="position:relative;height:120px;background:{bg};border:{brd};
    border-radius:14px;display:flex;flex-direction:column;align-items:center;
    justify-content:center;gap:5px;box-shadow:{glow};
    margin-bottom:-120px;pointer-events:none;z-index:1;overflow:hidden;">
  {top_bar}
  <div style="font-size:24px;line-height:1;filter:drop-shadow(0 0 6px {accent}44);">{icon}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:12px;font-weight:700;
      color:{lbl_c};text-align:center;padding:0 4px;letter-spacing:.3px;">{sid} {title}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:7px;color:{tag_c};
      letter-spacing:2px;text-transform:uppercase;">{sub}</div>
</div>""", unsafe_allow_html=True)
            if st.button(f"{title}", key=f"t5_nav_{sid}", use_container_width=True):
                st.session_state.t5_active = sid
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# HELPER: Section Header
# ══════════════════════════════════════════════════════════════
def _sec_header(num, title, sub, color="#00F5FF"):
    st.markdown(f"""
<div class="t5-sec-hd">
  <div class="t5-sec-num">{num}</div>
  <div>
    <div class="t5-sec-title" style="color:{color};">{title}</div>
    <div class="t5-sec-sub">{sub}</div>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 🕵️ 5.1 — 籌碼K線 CHIP MASTER (VWAP + OBV)
# ══════════════════════════════════════════════════════════════
def _s51(hist: pd.DataFrame, symbol: str):
    _sec_header("5.1", "🕵️ 主力籌碼透視 (Smart Money Flow)",
                "VWAP Deviation · OBV Trend · Institutional Pressure Gauge", "#00F5FF")

    if hist.empty:
        st.error("⚠️ 無法取得歷史數據。"); return

    df = hist.copy().reset_index()
    df.rename(columns={"index": "Date", "Datetime": "Date"}, inplace=True)
    if "Date" not in df.columns:
        df["Date"] = df.index

    # ── Calculate VWAP (rolling 20-day) ──────────────────────
    df["TP"]   = (df["High"] + df["Low"] + df["Close"]) / 3
    df["TVol"] = df["TP"] * df["Volume"]
    df["VWAP"] = df["TVol"].rolling(20).sum() / df["Volume"].rolling(20).sum()

    # ── OBV ──────────────────────────────────────────────────
    obv = [0]
    for i in range(1, len(df)):
        if df["Close"].iloc[i] > df["Close"].iloc[i - 1]:
            obv.append(obv[-1] + df["Volume"].iloc[i])
        elif df["Close"].iloc[i] < df["Close"].iloc[i - 1]:
            obv.append(obv[-1] - df["Volume"].iloc[i])
        else:
            obv.append(obv[-1])
    df["OBV"] = obv
    df["OBV_MA"] = df["OBV"].rolling(20).mean()

    # ── Current metrics ───────────────────────────────────────
    cp   = df["Close"].iloc[-1]
    vwap = df["VWAP"].iloc[-1]
    obv_now = df["OBV"].iloc[-1]
    obv_prev= df["OBV"].iloc[-21] if len(df) > 21 else df["OBV"].iloc[0]
    obv_trend = "🟢 累積 (Accumulating)" if obv_now > obv_prev else "🔴 派發 (Distributing)"
    vwap_signal = cp > vwap
    vwap_dev = ((cp - vwap) / vwap) * 100 if vwap > 0 else 0

    # ── KPI Row ───────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    kpi_data = [
        (c1, "目前股價", f"{cp:.2f}", "", "#00F5FF"),
        (c2, "VWAP (20日)", f"{vwap:.2f}", f"{'↑ 價在VWAP上方' if vwap_signal else '↓ 價在VWAP下方'}",
         "#00FF7F" if vwap_signal else "#FF3131"),
        (c3, "偏離度 Deviation", f"{abs(vwap_dev):.1f}%", "超過5%需注意", "#FFD700"),
        (c4, "OBV趨勢", obv_trend.split(" ")[0], obv_trend.split(" ", 1)[1], "#00FF7F" if "累積" in obv_trend else "#FF3131"),
    ]
    for col, lbl, val, sub, kc in kpi_data:
        col.markdown(f"""
<div class="t5-kpi" style="--kc:{kc};">
  <div class="t5-kpi-lbl">{lbl}</div>
  <div class="t5-kpi-val">{val}</div>
  <div class="t5-kpi-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

    # ── VWAP Signal Banner ─────────────────────────────────────
    if vwap_signal:
        st.markdown(f"""
<div style="margin:16px 0;padding:14px 20px;background:rgba(0,255,127,.06);border:1px solid rgba(0,255,127,.2);
    border-left:4px solid #00FF7F;border-radius:0 10px 10px 0;">
  <span style="font-family:'Rajdhani',sans-serif;font-size:15px;font-weight:700;color:#00FF7F;">
    🟢 法人支撐訊號 (Institutional Support)</span>
  <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(0,255,127,.6);margin-left:12px;">
    Price > VWAP ✦ Smart money bias = BULLISH</span>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div style="margin:16px 0;padding:14px 20px;background:rgba(255,49,49,.06);border:1px solid rgba(255,49,49,.2);
    border-left:4px solid #FF3131;border-radius:0 10px 10px 0;">
  <span style="font-family:'Rajdhani',sans-serif;font-size:15px;font-weight:700;color:#FF3131;">
    🔴 法人壓力訊號 (Institutional Pressure)</span>
  <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,49,49,.6);margin-left:12px;">
    Price &lt; VWAP ✦ Smart money bias = BEARISH</span>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Chart: Price vs VWAP ──────────────────────────────────
    df_plot = df[["Date","Close","VWAP"]].dropna().tail(120)
    df_melt = df_plot.melt("Date", var_name="Series", value_name="Price")

    color_scale = alt.Scale(
        domain=["Close", "VWAP"],
        range=["#00F5FF", "#FFD700"]
    )
    price_chart = alt.Chart(df_melt).mark_line(strokeWidth=1.5).encode(
        x=alt.X("Date:T", axis=alt.Axis(labelColor="#666", gridColor="#1a1a2a")),
        y=alt.Y("Price:Q", axis=alt.Axis(labelColor="#666", gridColor="#1a1a2a")),
        color=alt.Color("Series:N", scale=color_scale, legend=alt.Legend(
            labelColor="#aaa", titleColor="#aaa")),
        opacity=alt.condition(
            alt.datum["Series"] == "Close",
            alt.value(1.0), alt.value(0.7)
        )
    ).properties(height=260, background="transparent").configure_view(strokeOpacity=0)

    st.altair_chart(price_chart, use_container_width=True)

    # ── OBV Chart ─────────────────────────────────────────────
    st.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:9px;color:rgba(0,245,255,.3);letter-spacing:3px;margin-top:8px'>OBV — ON-BALANCE VOLUME TREND</div>", unsafe_allow_html=True)
    df_obv = df[["Date","OBV","OBV_MA"]].dropna().tail(120)
    obv_melt = df_obv.melt("Date", var_name="Series", value_name="Value")
    obv_chart = alt.Chart(obv_melt).mark_line(strokeWidth=1.5).encode(
        x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
        y=alt.Y("Value:Q", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
        color=alt.Color("Series:N", scale=alt.Scale(
            domain=["OBV","OBV_MA"], range=["#B77DFF","#FF9A3C"]
        ), legend=alt.Legend(labelColor="#aaa", titleColor="#aaa"))
    ).properties(height=180, background="transparent").configure_view(strokeOpacity=0)
    st.altair_chart(obv_chart, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# 🚀 5.2 — 起漲K線 RISING K (Bollinger Squeeze)
# ══════════════════════════════════════════════════════════════
def _s52(hist: pd.DataFrame, symbol: str):
    _sec_header("5.2", "🚀 動能突破偵測 (Momentum Ignition)",
                "Bollinger Band Squeeze · Bandwidth % · Energy Compression Radar", "#00FF7F")

    if hist.empty:
        st.error("⚠️ 無法取得歷史數據。"); return

    df = hist.copy().reset_index()
    df.rename(columns={"index": "Date", "Datetime": "Date"}, inplace=True)
    if "Date" not in df.columns:
        df["Date"] = df.index

    # ── Bollinger Bands (20, 2) ───────────────────────────────
    df["BB_mid"]   = df["Close"].rolling(20).mean()
    df["BB_std"]   = df["Close"].rolling(20).std()
    df["BB_upper"] = df["BB_mid"] + 2 * df["BB_std"]
    df["BB_lower"] = df["BB_mid"] - 2 * df["BB_std"]
    df["BW"]       = (df["BB_upper"] - df["BB_lower"]) / df["BB_mid"] * 100  # Bandwidth %

    bw_now   = df["BW"].iloc[-1] if not df["BW"].isna().all() else None
    bw_6m_lo = df["BW"].tail(126).min() if len(df) >= 20 else None

    # Squeeze detection: BW is near 6-month low
    is_squeeze = (bw_now is not None and bw_6m_lo is not None
                  and bw_now < 12 and abs(bw_now - bw_6m_lo) / (bw_6m_lo + 1e-9) < 0.15)

    # ── KPI Row ───────────────────────────────────────────────
    cp = df["Close"].iloc[-1]
    bb_u = df["BB_upper"].iloc[-1]
    bb_l = df["BB_lower"].iloc[-1]
    bb_m = df["BB_mid"].iloc[-1]

    c1, c2, c3, c4 = st.columns(4)
    for col, lbl, val, sub, kc in [
        (c1, "目前股價",   f"{cp:.2f}",  "",       "#00F5FF"),
        (c2, "上軌 Upper", f"{bb_u:.2f}","BB +2σ", "#FF9A3C"),
        (c3, "下軌 Lower", f"{bb_l:.2f}","BB -2σ", "#B77DFF"),
        (c4, "帶寬 BW%",   f"{bw_now:.1f}%" if bw_now else "N/A",
             "< 12% = 蓄勢", "#00FF7F" if is_squeeze else "#FFD700"),
    ]:
        col.markdown(f"""
<div class="t5-kpi" style="--kc:{kc};">
  <div class="t5-kpi-lbl">{lbl}</div>
  <div class="t5-kpi-val">{val}</div>
  <div class="t5-kpi-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

    # ── Squeeze Alert Banner ──────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    if is_squeeze:
        st.markdown(f"""
<div style="padding:16px 22px;background:rgba(0,255,127,.06);border:1px solid rgba(0,255,127,.25);
    border-left:4px solid #00FF7F;border-radius:0 12px 12px 0;animation:none;">
  <div style="font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#00FF7F;">
    🔥 蓄勢待發 — SQUEEZE ALERT!</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(0,255,127,.55);margin-top:5px;">
    Bandwidth {bw_now:.1f}% ≈ 6-Month Low → Energy Compression Detected → Breakout Imminent</div>
</div>""", unsafe_allow_html=True)
    else:
        color_bw = "#FF3131" if bw_now and bw_now > 30 else "#FFD700"
        label_bw = "⚡ 震盪擴張中 (Expanding)" if bw_now and bw_now > 30 else "⏳ 收斂中 (Contracting)"
        st.markdown(f"""
<div style="padding:14px 22px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.07);
    border-left:4px solid {color_bw};border-radius:0 12px 12px 0;">
  <span style="font-family:'Rajdhani',sans-serif;font-size:17px;font-weight:700;color:{color_bw};">
    {label_bw}</span>
  <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(160,176,208,.4);margin-left:12px;">
    BW = {bw_now:.1f}% — 等待帶寬收窄至 &lt;12% 視為蓄勢區</span>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Bollinger Chart (Altair) ──────────────────────────────
    df_p = df[["Date","Close","BB_upper","BB_lower","BB_mid"]].dropna().tail(120)

    base = alt.Chart(df_p)
    area = base.mark_area(opacity=0.06, color="#00FF7F").encode(
        x="Date:T",
        y=alt.Y("BB_lower:Q"),
        y2=alt.Y2("BB_upper")
    )
    close_line = base.mark_line(color="#00F5FF", strokeWidth=1.8).encode(
        x="Date:T", y=alt.Y("Close:Q", axis=alt.Axis(labelColor="#666", gridColor="#1a1a2a"))
    )
    mid_line = base.mark_line(color="#FFD70060", strokeWidth=1, strokeDash=[4,4]).encode(
        x="Date:T", y="BB_mid:Q"
    )
    upper_line = base.mark_line(color="#00FF7F50", strokeWidth=1).encode(x="Date:T", y="BB_upper:Q")
    lower_line = base.mark_line(color="#00FF7F50", strokeWidth=1).encode(x="Date:T", y="BB_lower:Q")

    chart = (area + close_line + mid_line + upper_line + lower_line).properties(
        height=280, background="transparent"
    ).configure_view(strokeOpacity=0).configure_axis(labelColor="#666", gridColor="#1a1a2a")
    st.altair_chart(chart, use_container_width=True)

    # ── Bandwidth Trend ───────────────────────────────────────
    st.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:9px;color:rgba(0,255,127,.3);letter-spacing:3px;'>BANDWIDTH % HISTORY (120D)</div>", unsafe_allow_html=True)
    df_bw = df[["Date","BW"]].dropna().tail(120)
    bw_chart = alt.Chart(df_bw).mark_area(
        line={"color": "#00FF7F", "strokeWidth": 1.2},
        color=alt.Gradient(gradient="linear", stops=[
            alt.GradientStop(color="rgba(0,255,127,.25)", offset=0),
            alt.GradientStop(color="rgba(0,255,127,.0)", offset=1)
        ], x1=1, x2=1, y1=1, y2=0)
    ).encode(
        x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
        y=alt.Y("BW:Q", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a"))
    ).properties(height=160, background="transparent").configure_view(strokeOpacity=0)
    st.altair_chart(bw_chart, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# ⚡ 5.3 — 權證小哥 TICK MASTER (ATR + Rel Vol)
# ══════════════════════════════════════════════════════════════
def _s53(hist: pd.DataFrame, symbol: str):
    _sec_header("5.3", "⚡ 短線當沖雷達 (Day Trade Radar)",
                "ATR Volatility · Relative Volume · Hot Money Signal", "#FFD700")

    if hist.empty:
        st.error("⚠️ 無法取得歷史數據。"); return

    df = hist.copy().reset_index()
    df.rename(columns={"index": "Date"}, inplace=True)
    if "Date" not in df.columns:
        df["Date"] = df.index

    # ── ATR (14) ─────────────────────────────────────────────
    df["H-L"]   = df["High"] - df["Low"]
    df["H-PC"]  = abs(df["High"] - df["Close"].shift(1))
    df["L-PC"]  = abs(df["Low"]  - df["Close"].shift(1))
    df["TR"]    = df[["H-L","H-PC","L-PC"]].max(axis=1)
    df["ATR14"] = df["TR"].rolling(14).mean()

    # ── Relative Volume ───────────────────────────────────────
    df["AvgVol20"] = df["Volume"].rolling(20).mean()
    df["RelVol"]   = df["Volume"] / df["AvgVol20"]

    cp       = df["Close"].iloc[-1]
    atr      = df["ATR14"].iloc[-1]
    atr_pct  = (atr / cp * 100) if cp > 0 else 0
    rel_vol  = df["RelVol"].iloc[-1]
    avg_vol  = df["AvgVol20"].iloc[-1]
    vol_now  = df["Volume"].iloc[-1]

    # ── KPI Row ───────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    rv_color = "#FF3131" if rel_vol > 3 else ("#FFD700" if rel_vol > 1.5 else "#00FF7F")
    for col, lbl, val, sub, kc in [
        (c1, "ATR14 (波動點數)", f"{atr:.2f}",     f"佔股價 {atr_pct:.1f}%", "#00F5FF"),
        (c2, "爆量比 Rel Vol",   f"{rel_vol:.1f}x", "今日量/20日均量",       rv_color),
        (c3, "今日成交量",       f"{vol_now/1e6:.1f}M" if vol_now > 1e6 else f"{int(vol_now):,}",
             "", "#B77DFF"),
        (c4, "20日均量",        f"{avg_vol/1e6:.1f}M" if avg_vol > 1e6 else f"{int(avg_vol):,}",
             "", "#FF9A3C"),
    ]:
        col.markdown(f"""
<div class="t5-kpi" style="--kc:{kc};">
  <div class="t5-kpi-lbl">{lbl}</div>
  <div class="t5-kpi-val">{val}</div>
  <div class="t5-kpi-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Risk Advisory ─────────────────────────────────────────
    if rel_vol > 3:
        st.markdown("""
<div style="padding:16px 22px;background:rgba(255,49,49,.07);border:1px solid rgba(255,49,49,.3);
    border-left:4px solid #FF3131;border-radius:0 12px 12px 0;">
  <div style="font-family:'Rajdhani',sans-serif;font-size:20px;font-weight:700;color:#FF3131;">
    ⚠️ 隔日沖風險警示 — HIGH TURNOVER RISK</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,49,49,.55);margin-top:5px;">
    Relative Volume > 3× · 大量熱錢涌入 · 隔日賣壓風險極高 · 謹慎操作</div>
</div>""", unsafe_allow_html=True)
    elif rel_vol > 1.5:
        st.markdown(f"""
<div style="padding:14px 22px;background:rgba(255,215,0,.05);border:1px solid rgba(255,215,0,.2);
    border-left:4px solid #FFD700;border-radius:0 12px 12px 0;">
  <span style="font-family:'Rajdhani',sans-serif;font-size:17px;font-weight:700;color:#FFD700;">
    🟡 量能放大 (Volume Expanding) — 留意方向</span>
  <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(255,215,0,.45);margin-left:10px;">
    RelVol {rel_vol:.1f}× — 量大但不足3×，跟蹤動向</span>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div style="padding:14px 22px;background:rgba(0,255,127,.04);border:1px solid rgba(0,255,127,.12);
    border-left:4px solid #00FF7F;border-radius:0 12px 12px 0;">
  <span style="font-family:'Rajdhani',sans-serif;font-size:17px;font-weight:700;color:#00FF7F;">
    🟢 量能平穩 (Normal Volume)</span>
  <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(0,255,127,.45);margin-left:10px;">
    RelVol {rel_vol:.1f}× — 無異常放量，風險可控</span>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── ATR & RelVol Chart ────────────────────────────────────
    df_tail = df[["Date","ATR14","RelVol"]].dropna().tail(90)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:9px;color:rgba(0,245,255,.3);letter-spacing:3px;margin-bottom:4px;'>ATR14 VOLATILITY HISTORY</div>", unsafe_allow_html=True)
        atr_chart = alt.Chart(df_tail).mark_area(
            line={"color":"#00F5FF","strokeWidth":1.5},
            color=alt.Gradient(gradient="linear",
                stops=[alt.GradientStop(color="rgba(0,245,255,.2)",offset=0),
                       alt.GradientStop(color="rgba(0,245,255,.0)",offset=1)],
                x1=1,x2=1,y1=1,y2=0)
        ).encode(
            x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            y=alt.Y("ATR14:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a"))
        ).properties(height=200,background="transparent").configure_view(strokeOpacity=0)
        st.altair_chart(atr_chart, use_container_width=True)

    with col_b:
        st.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:9px;color:rgba(255,215,0,.3);letter-spacing:3px;margin-bottom:4px;'>RELATIVE VOLUME (爆量比)</div>", unsafe_allow_html=True)
        rv_chart = alt.Chart(df_tail).mark_bar(opacity=0.7).encode(
            x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            y=alt.Y("RelVol:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            color=alt.condition(
                alt.datum["RelVol"] > 3,
                alt.value("#FF3131"),
                alt.condition(alt.datum["RelVol"] > 1.5, alt.value("#FFD700"), alt.value("#00FF7F"))
            )
        ).properties(height=200,background="transparent").configure_view(strokeOpacity=0)
        st.altair_chart(rv_chart, use_container_width=True)

    # ── Volatility Advice Grid ────────────────────────────────
    st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
    st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,215,0,.3);
    letter-spacing:3px;margin-bottom:10px;">TRADING GUIDANCE — BASED ON ATR × REL VOL</div>""", unsafe_allow_html=True)

    ca, cb, cc = st.columns(3)
    for col, icon, title, desc, c in [
        (ca, "🎯", "ATR 停損參考",
         f"保守: -{atr*0.5:.2f} | 標準: -{atr:.2f} | 積極: -{atr*1.5:.2f}", "#00F5FF"),
        (cb, "⚡", "波動率評級",
         f"{'高波動 HIGH' if atr_pct > 3 else '中波動 MED' if atr_pct > 1.5 else '低波動 LOW'} — ATR {atr_pct:.1f}%/日", "#FFD700"),
        (cc, "🔔", "量能評估",
         f"{'⚠️ 極度爆量 EXTREME' if rel_vol > 3 else '🟡 量能放大 ELEVATED' if rel_vol > 1.5 else '🟢 正常量能 NORMAL'}", "#FF9A3C"),
    ]:
        col.markdown(f"""
<div style="padding:14px 16px;background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.05);
    border-top:2px solid {c};border-radius:10px;">
  <div style="font-family:'Rajdhani',sans-serif;font-size:13px;font-weight:700;color:{c};margin-bottom:6px;">{icon} {title}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(160,176,208,.5);line-height:1.5;">{desc}</div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 🚦 5.4 — 艾蜜莉定存 VALUE QUEEN (PE Traffic Light)
# ══════════════════════════════════════════════════════════════
def _s54(hist3y: pd.DataFrame, info: dict, symbol: str):
    _sec_header("5.4", "🚦 價值紅綠燈 (Valuation Traffic Light)",
                "Historical PE · 25th-75th Percentile · Mean Reversion Signal", "#FF9A3C")

    # ── Attempt EPS from info ──────────────────────────────────
    eps = info.get("trailingEps") or info.get("forwardEps")
    pe_trail = info.get("trailingPE")
    pe_fwd   = info.get("forwardPE")
    cp = info.get("currentPrice") or info.get("regularMarketPrice") or (
        hist3y["Close"].iloc[-1] if not hist3y.empty else None)

    # Build historical PE from 3Y history if EPS available
    hist_pe = None
    pe_25 = pe_50 = pe_75 = None

    if not hist3y.empty and eps and eps > 0:
        hist_pe_series = hist3y["Close"] / eps
        hist_pe_series = hist_pe_series[hist_pe_series > 0].dropna()
        if len(hist_pe_series) > 20:
            pe_25 = float(np.percentile(hist_pe_series, 25))
            pe_50 = float(np.percentile(hist_pe_series, 50))
            pe_75 = float(np.percentile(hist_pe_series, 75))
            hist_pe = float(hist_pe_series.iloc[-1])

    # ── Determine signal ──────────────────────────────────────
    use_pe = hist_pe or pe_trail or pe_fwd
    signal = "neutral"
    if use_pe and pe_25 and pe_75:
        if use_pe < pe_25:    signal = "cheap"
        elif use_pe > pe_75:  signal = "expensive"
        else:                  signal = "fair"
    elif use_pe:
        if use_pe < 15:        signal = "cheap"
        elif use_pe > 35:      signal = "expensive"
        else:                   signal = "fair"

    label_map = {
        "cheap":     ("🟢 便宜 CHEAP",     "#00FF7F", "建議買入帶"),
        "fair":      ("🟡 合理 FAIR",       "#FFD700", "持有觀望帶"),
        "expensive": ("🔴 昂貴 EXPENSIVE",  "#FF3131", "謹慎操作帶"),
        "neutral":   ("⬜ 無PE數據",        "#888888", "數據不足"),
    }
    sig_label, sig_color, sig_desc = label_map[signal]

    # ── KPI Row ───────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    for col, lbl, val, sub, kc in [
        (c1, "目前股價",      f"{cp:.2f}"   if cp    else "N/A", "",       "#00F5FF"),
        (c2, "EPS (TTM)",    f"{eps:.2f}"  if eps   else "N/A", "基礎EPS","#FFD700"),
        (c3, "本益比 P/E",   f"{use_pe:.1f}"if use_pe else "N/A", "當前PE", sig_color),
        (c4, "50th PE",      f"{pe_50:.1f}" if pe_50 else "N/A", "歷史中位","#B77DFF"),
    ]:
        col.markdown(f"""
<div class="t5-kpi" style="--kc:{kc};">
  <div class="t5-kpi-lbl">{lbl}</div>
  <div class="t5-kpi-val">{val}</div>
  <div class="t5-kpi-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Traffic Light Circles ──────────────────────────────────
    is_cheap = (signal == "cheap")
    is_fair  = (signal == "fair")
    is_exp   = (signal == "expensive")

    def _circle(label, sub, css_cls, active):
        act = "active" if active else "dim"
        return f"""
<div class="tl-circle {css_cls} {act}">
  <div style="font-size:13px;font-weight:800;letter-spacing:.5px;">{label}</div>
  <div style="font-size:9px;opacity:.7;margin-top:3px;">{sub}</div>
</div>"""

    if pe_25 and pe_75:
        labels = [
            (is_exp,   "tl-red",    "🔴 昂貴",   f"PE > {pe_75:.0f}"),
            (is_fair,  "tl-yellow", "🟡 合理",   f"{pe_25:.0f}–{pe_75:.0f}"),
            (is_cheap, "tl-green",  "🟢 便宜",   f"PE < {pe_25:.0f}"),
        ]
    else:
        labels = [
            (is_exp,   "tl-red",    "🔴 昂貴",   "PE > 35"),
            (is_fair,  "tl-yellow", "🟡 合理",   "PE 15–35"),
            (is_cheap, "tl-green",  "🟢 便宜",   "PE < 15"),
        ]

    circles_html = "".join(_circle(lb, sb, cls, act) for act, cls, lb, sb in labels)
    st.markdown(f'<div class="tl-wrap">{circles_html}</div>', unsafe_allow_html=True)

    # ── Active Signal Banner ───────────────────────────────────
    st.markdown(f"""
<div style="margin:12px 0;padding:16px 22px;background:rgba(0,0,0,.2);border:1px solid {sig_color}33;
    border-left:5px solid {sig_color};border-radius:0 12px 12px 0;text-align:center;">
  <div style="font-family:'Rajdhani',sans-serif;font-size:26px;font-weight:800;color:{sig_color};">
    {sig_label}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(160,176,208,.45);margin-top:6px;">
    {sig_desc} · Current PE: {f'{use_pe:.1f}' if use_pe else 'N/A'}</div>
</div>""", unsafe_allow_html=True)

    # ── Historical PE Chart ────────────────────────────────────
    if not hist3y.empty and eps and eps > 0:
        st.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:9px;color:rgba(255,154,60,.3);letter-spacing:3px;margin-top:16px;'>3Y HISTORICAL P/E RATIO</div>", unsafe_allow_html=True)
        df_pe = hist3y.copy().reset_index()
        df_pe.rename(columns={"index":"Date","Datetime":"Date"}, inplace=True)
        if "Date" not in df_pe.columns:
            df_pe["Date"] = df_pe.index
        df_pe["PE"] = df_pe["Close"] / eps
        df_pe = df_pe[["Date","PE"]].dropna()
        df_pe = df_pe[df_pe["PE"] > 0]

        pe_chart = alt.Chart(df_pe).mark_line(color="#FF9A3C", strokeWidth=1.5).encode(
            x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
            y=alt.Y("PE:Q",   axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a"))
        )
        rules = []
        if pe_25:
            for pv, pc, pn in [(pe_25,"#00FF7F","25th"),(pe_50,"#FFD700","50th"),(pe_75,"#FF3131","75th")]:
                rules.append(alt.Chart(pd.DataFrame({"y":[pv]})).mark_rule(
                    strokeDash=[4,4], color=pc, strokeWidth=1, opacity=0.6).encode(y="y:Q"))
        full_chart = alt.layer(pe_chart, *rules).properties(
            height=240, background="transparent"
        ).configure_view(strokeOpacity=0)
        st.altair_chart(full_chart, use_container_width=True)
    else:
        st.info("💡 此標的無EPS數據 (可能為ETF/台股/未獲利公司)，P/E分析不適用。")
        if pe_trail:
            st.markdown(f"**Trailing P/E (from yfinance info):** {pe_trail:.1f}")
        if pe_fwd:
            st.markdown(f"**Forward P/E (from yfinance info):** {pe_fwd:.1f}")


# ══════════════════════════════════════════════════════════════
# 🐋 5.5 — 13F 巨鯨 WHALE WATCHER
# ══════════════════════════════════════════════════════════════
def _s55(holders: pd.DataFrame, info: dict, symbol: str):
    _sec_header("5.5", "🐋 機構持倉揭秘 (Institutional Holdings)",
                "SEC 13F Data · Top Holders · Smart Money Accumulation Map", "#B77DFF")

    if holders is None or holders.empty:
        st.markdown("""
<div style="text-align:center;padding:60px 20px;background:rgba(255,255,255,.015);
    border:1px solid rgba(255,255,255,.05);border-radius:16px;">
  <div style="font-size:48px;opacity:.25;margin-bottom:14px;">🐋</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:18px;color:rgba(255,255,255,.35);
      letter-spacing:2px;margin-bottom:8px;">暫無 13F 數據</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(160,176,208,.25);
      letter-spacing:2px;">No 13F Data Available — 台股 / ETF / 部分小型股可能無此數據</div>
</div>""", unsafe_allow_html=True)
        return

    # ── Normalize columns ─────────────────────────────────────
    hdf = holders.copy()
    col_map = {}
    for c in hdf.columns:
        cl = str(c).lower()
        if "holder" in cl or "institution" in cl or "name" in cl:
            col_map[c] = "Holder"
        elif "share" in cl:
            col_map[c] = "Shares"
        elif "value" in cl or "market" in cl:
            col_map[c] = "Value"
        elif "pct" in cl or "percent" in cl or "%" in cl:
            col_map[c] = "PctHeld"
    hdf.rename(columns=col_map, inplace=True)
    hdf = hdf.head(10)

    # Total institutional ownership
    inst_pct = info.get("institutionPercentHeld", None)
    float_pct = info.get("floatShares", None)

    # ── Summary KPIs ──────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    for col, lbl, val, kc in [
        (c1, "機構持股比 Inst%", f"{inst_pct*100:.1f}%" if inst_pct else "N/A", "#B77DFF"),
        (c2, "Top 10 機構數",   f"{len(hdf)}",                                  "#00F5FF"),
        (c3, "持股類型",        info.get("quoteType","N/A"),                     "#FF9A3C"),
    ]:
        col.markdown(f"""
<div class="t5-kpi" style="--kc:{kc};">
  <div class="t5-kpi-lbl">{lbl}</div>
  <div class="t5-kpi-val">{val}</div>
  <div class="t5-kpi-sub"></div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Top 10 Table ──────────────────────────────────────────
    st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(183,125,255,.4);
    letter-spacing:3px;text-transform:uppercase;margin-bottom:10px;">
    TOP 10 INSTITUTIONAL HOLDERS
</div>""", unsafe_allow_html=True)

    for i, (_, row) in enumerate(hdf.iterrows()):
        holder  = str(row.get("Holder", "Unknown"))
        shares  = row.get("Shares", 0)
        value   = row.get("Value", None)
        pct     = row.get("PctHeld", None)
        rank_color = ["#FFD700","#C0C0C0","#CD7F32"] + ["#B77DFF"] * 10
        rc = rank_color[i] if i < len(rank_color) else "#B77DFF"
        sh_str = f"{shares/1e6:.1f}M" if shares and shares > 1e6 else (f"{int(shares):,}" if shares else "N/A")
        val_str = f"${value/1e9:.2f}B" if value and value > 1e9 else (f"${value/1e6:.1f}M" if value else "N/A")
        pct_str = f"{pct*100:.2f}%" if pct and pct < 1 else (f"{pct:.2f}%" if pct else "—")
        st.markdown(f"""
<div class="whale-row">
  <div class="whale-rank" style="color:{rc};"># {i+1}</div>
  <div class="whale-name">{holder}</div>
  <div class="whale-shares">{sh_str}</div>
  <div class="whale-shares" style="color:rgba(255,154,60,.6);">{val_str}</div>
  <div class="whale-pct">{pct_str}</div>
</div>""", unsafe_allow_html=True)

    # ── Pie Chart (Top 5) ─────────────────────────────────────
    if "PctHeld" in hdf.columns and hdf["PctHeld"].notna().sum() >= 2:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:9px;color:rgba(183,125,255,.35);letter-spacing:3px;margin-bottom:8px;'>TOP 5 HOLDER DISTRIBUTION</div>", unsafe_allow_html=True)
        top5 = hdf.head(5)[["Holder","PctHeld"]].dropna()
        top5["PctHeld"] = pd.to_numeric(top5["PctHeld"], errors="coerce")
        top5 = top5.dropna()
        if not top5.empty:
            pie = alt.Chart(top5).mark_arc(innerRadius=50, outerRadius=120).encode(
                theta=alt.Theta("PctHeld:Q"),
                color=alt.Color("Holder:N", scale=alt.Scale(
                    range=["#B77DFF","#00F5FF","#FFD700","#00FF7F","#FF9A3C"]
                ), legend=alt.Legend(labelColor="#aaa", titleColor="#aaa")),
                tooltip=["Holder:N", alt.Tooltip("PctHeld:Q", format=".4f")]
            ).properties(height=280, background="transparent").configure_view(strokeOpacity=0)
            st.altair_chart(pie, use_container_width=True)
    else:
        # Fallback: just show shares bar
        if "Shares" in hdf.columns:
            top5 = hdf.head(5)[["Holder","Shares"]].copy()
            top5["Shares"] = pd.to_numeric(top5["Shares"], errors="coerce").fillna(0)
            bar = alt.Chart(top5).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                x=alt.X("Shares:Q", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
                y=alt.Y("Holder:N", sort="-x", axis=alt.Axis(labelColor="#aaa")),
                color=alt.value("#B77DFF")
            ).properties(height=220, background="transparent").configure_view(strokeOpacity=0)
            st.altair_chart(bar, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# 📜 5.6 — 戰略百科 THE CODEX (Original SOP Content)
# ══════════════════════════════════════════════════════════════
def _s56():
    _sec_header("5.6", "📜 戰略百科 — The Codex",
                "SOP · Entry/Exit Discipline · Sector Intel · Mindset · CB Leverage · OTC MA", "#FF3131")

    tabs = st.tabs([
        "⏰ 四大時間套利", "📋 進出場紀律",
        "🏭 產業族群庫",  "🧠 特殊心法",
        "⚡ CBAS試算",   "📈 OTC 神奇均線"
    ])

    # ── T1: 四大時間套利 ───────────────────────────────────────
    with tabs[0]:
        _ARBS = [
            ("gold",  "01", "新券蜜月期",  "上市 0–90 天",
             "上市初期追蹤，大戶定調，股性未定",
             "進場甜蜜點：105–115 元。前 90 天是觀察期也是機會期，關注大股東動態與首批券商報告。"),
            ("green", "02", "滿年沈澱",   "上市 350–420 天",
             "沈澱洗牌結束，底部有支撐",
             "觸發點：CB 站上 87MA 且帶量。經過一年的洗盤與沈澱，仍存活的標的底部結構扎實。"),
            ("",      "03", "賣回保衛戰", "距賣回日 < 180 天",
             "下檔保護最強，CB 價 95–105 甜甜圈",
             "最佳風報比窗口。賣回日臨近時，市場自然形成底部支撐，CB 價格不易跌破 100。"),
            ("red",   "04", "百日轉換窗口","距到期 < 100 天",
             "最後一搏，轉換或歸零",
             "股價需站上轉換價 × 1.05 才有轉換意義。時間價值快速遞減，必須精確把握時機。"),
        ]
        for cls, num, title, period, key, detail in _ARBS:
            st.markdown(f"""
<div class="codex-card {cls}">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
    <div style="font-family:'Orbitron',sans-serif;font-size:26px;font-weight:900;color:rgba(0,245,255,.1);">{num}</div>
    <div>
      <div class="codex-card-title">{title}</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(160,176,208,.3);letter-spacing:2px;">{period}</div>
    </div>
  </div>
  <div class="codex-card-key">{key}</div>
  <div class="codex-card-detail">{detail}</div>
</div>""", unsafe_allow_html=True)

    # ── T2: 進出場紀律 ─────────────────────────────────────────
    with tabs[1]:
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:17px;color:rgba(0,255,127,.7);letter-spacing:2px;margin-bottom:12px;font-weight:700;">📥 核心進場條件 — THE 4 COMMANDMENTS</div>', unsafe_allow_html=True)
        for cls, title, key, detail in [
            ("green", "價格天條",  "CB 市價 < 120 元",         "理想區間 105~115 元。超過 120 = 溢價過高，槓桿效益不足。"),
            ("green", "均線天條",  "87MA > 284MA",             "中期多頭排列確認。均線交叉後回踩 87MA 不破 = 最佳進場。"),
            ("",      "身分認證",  "領頭羊 or 風口豬",          "族群指標股（領頭羊）或主流題材二軍（風口豬），單兵不做。"),
            ("gold",  "發債故事",  "從無到有 / 擴產 / 政策事件","三選一，故事是引爆點，沒有故事的 CB 只是數字。"),
        ]:
            st.markdown(f'<div class="codex-card {cls}"><div class="codex-card-title">{title}</div><div class="codex-card-key">{key}</div><div class="codex-card-detail">{detail}</div></div>', unsafe_allow_html=True)

        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:17px;color:rgba(255,49,49,.7);letter-spacing:2px;margin:18px 0 12px;font-weight:700;">📤 核心出場條件</div>', unsafe_allow_html=True)
        for cls, title, key, detail in [
            ("red",  "🛑 停損天條", "CB 跌破 100 元",       "保本天條不妥協。不管故事多美，跌破即離場，沒有例外。"),
            ("gold", "💰 停利策略", "目標 152 元以上",       "留魚尾策略：到達目標區間後分批出場，讓剩餘倉位跟跑。"),
            ("",     "⏰ 時間停損", "持有超過 90 天未動", "靜止 = 機會成本燒蝕。超過 90 天無動能，重新評估或減倉。"),
        ]:
            st.markdown(f'<div class="codex-card {cls}"><div class="codex-card-title">{title}</div><div class="codex-card-key">{key}</div><div class="codex-card-detail">{detail}</div></div>', unsafe_allow_html=True)

    # ── T3: 產業族群庫 ─────────────────────────────────────────
    with tabs[2]:
        for sect, stocks in [
            ("AI伺服器",  "廣達、緯創、英業達、技嘉"),
            ("散熱",      "奇鋐、雙鴻、建準"),
            ("CoWoS封測", "日月光、矽品"),
            ("重電/電網",  "華城、士電、中興電"),
            ("半導體設備", "弘塑、辛耘、漢微科"),
            ("航運",      "長榮、陽明、萬海"),
            ("生技新藥",  "藥華藥、合一"),
            ("AI美股",    "NVDA · META · MSFT · GOOGL · AMZN"),
            ("量子計算",  "QBTS · IONQ · RGTI"),
            ("ETF 核心",  "SPY · QQQ · SCHD · 0050.TW · 00878.TW"),
        ]:
            st.markdown(f'<div class="sector-row"><div class="sector-name">{sect}</div><div class="sector-stk">{stocks}</div></div>', unsafe_allow_html=True)

    # ── T4: 特殊心法 ───────────────────────────────────────────
    with tabs[3]:
        for i, (title, desc) in enumerate([
            ("賣出是種藝術",    "目標區間到達後，分批出場，絕不一次梭哈。「留魚尾」策略讓下一次持倉更安心。"),
            ("跌破100是天條",   "不管故事多美，CB跌破100元立刻離場，沒有例外，沒有感情。"),
            ("族群共振才是主力", "單兵突破假象居多。觀察是否有2~3檔同族群CB同步上攻，才是真正主力進場訊號。"),
            ("87MA是生命線",    "股價站上87MA且均線向上，才是安全進場時機。跌破87MA視為第一警戒。"),
            ("溢價率的陷阱",    "溢價率 > 20% 的CB，上漲空間有限。避開高溢價，選擇低溢價（5~15%）的標的。"),
            ("籌碼鬆動就跑",    "已轉換比例超過30%，代表大量轉換股票，股東結構改變，籌碼不乾淨，警惕。"),
            ("尾盤定勝負",      "13:25後的最後25分鐘，是當天多空最誠實的表態。收盤站穩才是真突破。"),
            ("消息面最後出現",  "有基本面、技術面支撐，消息面是最後確認彈，不是買入理由。"),
        ], 1):
            st.markdown(f"""
<div style="display:flex;align-items:flex-start;gap:16px;padding:14px 16px;
    background:rgba(255,255,255,.018);border:1px solid rgba(255,255,255,.04);
    border-radius:10px;margin-bottom:8px;">
  <div style="font-family:'Orbitron',sans-serif;font-size:32px;font-weight:900;
      color:rgba(255,215,0,.1);min-width:44px;line-height:1;">{i:02d}</div>
  <div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:15px;font-weight:700;color:#FFF;margin-bottom:3px;">{title}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(160,176,208,.45);line-height:1.6;">{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── T5: CBAS試算 ───────────────────────────────────────────
    with tabs[4]:
        st.markdown("""
<div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(0,245,255,.3);
    letter-spacing:3px;text-transform:uppercase;margin-bottom:16px;">
    CBAS LEVERAGE ENGINE — 可轉債套利槓桿試算器
</div>""", unsafe_allow_html=True)

        ca, cb = st.columns(2)
        with ca:
            cb_price  = st.number_input("CB 市價 (元)", min_value=100.0, max_value=200.0, value=108.0, step=0.5, key="cb5_price")
            conv_prem = st.number_input("轉換溢價率 (%)", min_value=0.0, max_value=50.0, value=10.0, step=0.5, key="cb5_prem")
        with cb:
            lot_size  = st.number_input("張數 (手)", min_value=1, max_value=100, value=1, key="cb5_lot")
            face_val  = st.number_input("面額 (元)", min_value=100.0, value=100.0, step=1.0, key="cb5_face", disabled=True)

        if cb_price > 100:
            prem_cost = cb_price - 100
            leverage  = cb_price / prem_cost if prem_cost > 0 else 0
            total_inv = cb_price * lot_size * 1000

            lev_color = "#00FF7F" if leverage >= 5 else ("#FFD700" if leverage >= 3 else "#FF6B6B")
            st.markdown(f"""
<div style="background:#000;border:2px solid rgba(80,90,110,.35);border-radius:14px;
    padding:32px 28px;text-align:center;margin-top:16px;position:relative;overflow:hidden;">
  <div style="position:absolute;top:10px;left:16px;font-family:'Orbitron',sans-serif;
      font-size:7px;color:rgba(0,245,255,.15);letter-spacing:4px;">CBAS LEVERAGE ENGINE</div>
  <div style="font-family:'Orbitron',sans-serif;font-size:72px;font-weight:900;
      color:{lev_color};text-shadow:0 0 30px {lev_color}55;line-height:1;">
    {leverage:.2f}<span style="font-size:24px;opacity:.4;">×</span></div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
      color:rgba(160,176,208,.4);text-transform:uppercase;letter-spacing:3px;margin-top:8px;">
    IMPLIED LEVERAGE</div>
  <div style="width:60%;height:1px;background:rgba(255,255,255,.05);margin:20px auto;"></div>
  <div style="display:flex;justify-content:center;gap:40px;">
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(160,176,208,.3);
          letter-spacing:2px;margin-bottom:4px;">CB 溢價權利金</div>
      <div style="font-family:'Orbitron',sans-serif;font-size:24px;font-weight:700;color:#FFF;">
        {prem_cost:.1f}元</div>
    </div>
    <div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(160,176,208,.3);
          letter-spacing:2px;margin-bottom:4px;">總投資額</div>
      <div style="font-family:'Orbitron',sans-serif;font-size:24px;font-weight:700;color:#FFF;">
        {total_inv/10000:.1f}萬</div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

            # Quick reference
            st.markdown("<div style='font-family:JetBrains Mono,monospace;font-size:9px;color:rgba(160,176,208,.25);letter-spacing:2px;text-transform:uppercase;margin:14px 0 8px;'>Quick Reference: Leverage at Different Prices</div>", unsafe_allow_html=True)
            ref_cols = st.columns(5)
            for i, p in enumerate([103, 105, 110, 115, 120]):
                pm = p - 100
                lv = p / pm if pm > 0 else 0
                lc = "#00FF7F" if lv > 5 else ("#FFD700" if lv > 3 else "#FF6B6B")
                ref_cols[i].markdown(f"""
<div style="text-align:center;padding:10px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.04);border-radius:8px;">
  <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(160,176,208,.35);letter-spacing:1px;">CB {p}元</div>
  <div style="font-family:'Orbitron',sans-serif;font-size:24px;font-weight:700;color:{lc};line-height:1.2;">{lv:.1f}×</div>
</div>""", unsafe_allow_html=True)

    # ── T6: OTC 神奇均線 ───────────────────────────────────────
    with tabs[5]:
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:17px;color:rgba(255,215,0,.7);font-weight:700;letter-spacing:2px;margin-bottom:14px;">📈 OTC 神奇均線法則</div>', unsafe_allow_html=True)
        for cls, title, key, detail in [
            ("gold", "87MA = 季線生命線",  "87MA 向上且股價站上",
             "台股 OTC 市場的核心均線。87MA 向上時，買進訊號；跌破 87MA 且均線轉下，出場。"),
            ("",     "284MA = 年線壓力",   "284MA 是長期趨勢分界",
             "284MA 之上為多頭格局，之下為空頭格局。87MA 穿越 284MA 向上 = 黃金交叉信號。"),
            ("green","乖離率 < 25%",       "正乖離超過 25% = 過熱",
             "CB 股價距 87MA 正乖離超過 25%，為過熱警示；負乖離超過 25%，為超跌反彈點。"),
            ("red",  "格蘭碧 6 大訊號",    "G1 突破 / G2 假跌 / G3 回測",
             "結合格蘭碧理論：G1(突破買)、G2(假跌破買)、G3(回測支撐買)、G4-G6 對應賣點。"),
        ]:
            st.markdown(f'<div class="codex-card {cls}"><div class="codex-card-title">{title}</div><div class="codex-card-key">{key}</div><div class="codex-card-detail">{detail}</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 🎯 MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════
def render():
    """Tab 5 — 通用市場分析儀 (Universal Market Analyzer) V400"""

    _inject_css()

    # ── Search Bar ────────────────────────────────────────────
    symbol = _render_search()

    # ── Hero ──────────────────────────────────────────────────
    _render_hero(symbol)

    # ── Fetch Data (with loading spinner) ─────────────────────
    with st.spinner(f"⬡ 正在鎖定目標: {symbol} ..."):
        hist_1y, hist_3y, info, holders, err = _fetch(symbol)

    if err:
        st.error(f"❌ 數據獲取失敗: {err}")
        st.info("💡 請確認代號格式：美股直接輸入 `AAPL`；台股須加 `.TW` 如 `2330.TW`；OTC 加 `.TWO`。")
        # Still render Codex (no market data needed)
        _render_nav()
        if st.session_state.get("t5_active") == "5.6":
            _s56()
        return

    # ── Ticker Info Strip ─────────────────────────────────────
    cp_now  = info.get("currentPrice") or info.get("regularMarketPrice") or (
        float(hist_1y["Close"].iloc[-1]) if not hist_1y.empty else 0)
    name    = info.get("longName") or info.get("shortName") or symbol
    sector  = info.get("sector") or info.get("category") or "—"
    mktcap  = info.get("marketCap")
    mktcap_str = f"${mktcap/1e12:.2f}T" if mktcap and mktcap > 1e12 else (
                 f"${mktcap/1e9:.1f}B" if mktcap and mktcap > 1e9 else "N/A")
    day_chg = info.get("regularMarketChangePercent", 0) or 0
    chg_color = "#00FF7F" if day_chg >= 0 else "#FF3131"

    st.markdown(f"""
<div style="display:flex;align-items:center;gap:20px;padding:14px 20px;
    background:rgba(255,255,255,.018);border:1px solid rgba(255,255,255,.05);
    border-radius:14px;margin-bottom:18px;flex-wrap:wrap;">
  <div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:#FFF;letter-spacing:2px;line-height:1;">{symbol}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(160,176,208,.45);margin-top:2px;">{name}</div>
  </div>
  <div style="font-family:'Bebas Neue',sans-serif;font-size:42px;color:#FFF;line-height:1;margin-left:auto;">
    {cp_now:.2f}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:18px;font-weight:700;color:{chg_color};">
    {'▲' if day_chg >= 0 else '▼'} {abs(day_chg):.2f}%</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(160,176,208,.35);text-align:right;">
    <div>Sector: {sector}</div>
    <div>Mkt Cap: {mktcap_str}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Navigation ────────────────────────────────────────────
    _render_nav()
    active = st.session_state.get("t5_active", "5.1")

    # ── Module Dispatch ───────────────────────────────────────
    st.markdown('<div style="margin-top:8px;">', unsafe_allow_html=True)
    try:
        if   active == "5.1": _s51(hist_1y, symbol)
        elif active == "5.2": _s52(hist_1y, symbol)
        elif active == "5.3": _s53(hist_1y, symbol)
        elif active == "5.4": _s54(hist_3y, info, symbol)
        elif active == "5.5": _s55(holders, info, symbol)
        elif active == "5.6": _s56()
        else:                  _s51(hist_1y, symbol)
    except Exception as exc:
        st.error(f"❌ Module {active} Error: {exc}")
        with st.expander("🔍 Debug Traceback"):
            st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────
    st.markdown(f"""
<div class="t5-foot">
    Titan Universal Market Analyzer V400 · God-Tier Edition · {symbol} · {datetime.now().strftime("%Y-%m-%d %H:%M")}
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    render()
