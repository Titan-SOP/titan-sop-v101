# ui_desktop/tab5_wiki.py
# Titan OS V500 — Tab 5: 通用市場分析儀 (Universal Market Analyzer)
# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Architecture : 6-Module Universal Analyzer — CB-Decoupled          ║
# ║  Supports     : US Stocks · TW Stocks · ETFs · Crypto               ║
# ║  Fixes V500   : Altair nested-condition bug · Nav overlay · 28/26px ║
# ╚══════════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import yfinance as yf
from datetime import datetime, timedelta
import traceback


# ════════════════════════════════════════════════════════════════════
# CSS
# ════════════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;700&family=Orbitron:wght@400;600;700;900&display=swap" rel="stylesheet">
<style>
:root{
    --c-gold:#FFD700;--c-cyan:#00F5FF;--c-red:#FF3131;
    --c-green:#00FF7F;--c-orange:#FF9A3C;--c-purple:#B77DFF;
    --f-d:'Bebas Neue',sans-serif;--f-b:'Rajdhani',sans-serif;
    --f-m:'JetBrains Mono',monospace;--f-o:'Orbitron',sans-serif;
}
.t5-hero{padding:44px 40px 30px;background:linear-gradient(180deg,rgba(8,8,20,0) 0%,rgba(4,4,14,.8) 55%,rgba(0,0,0,.96) 100%);border-bottom:1px solid rgba(0,245,255,.06);text-align:center;margin-bottom:22px;}
.t5-hero-label{font-family:var(--f-o);font-size:9px;color:rgba(255,49,49,.38);letter-spacing:10px;text-transform:uppercase;margin-bottom:10px;}
.t5-hero-title{font-family:var(--f-d);font-size:66px;color:#FFF;letter-spacing:4px;line-height:1;text-shadow:0 0 60px rgba(0,245,255,.07);}
.t5-hero-sub{font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,.25);letter-spacing:4px;text-transform:uppercase;margin-top:9px;}
.t5-nav-rail{background:linear-gradient(165deg,#07080f,#0b0c18);border:1px solid rgba(255,255,255,.05);border-radius:18px;padding:18px 14px 14px;margin-bottom:22px;}
.t5-nav-lbl{font-family:var(--f-m);font-size:8px;letter-spacing:4px;color:rgba(0,245,255,.22);text-transform:uppercase;margin-bottom:14px;text-align:center;}
/* NAV BUTTON: slim strip below each visual card */
.t5-nav-rail [data-testid="stButton"]>button{background:transparent !important;border:none !important;color:rgba(0,245,255,.0) !important;font-size:1px !important;padding:2px 0 !important;margin-top:4px !important;height:22px !important;min-height:22px !important;box-shadow:none !important;cursor:pointer !important;width:100% !important;}
.t5-hd{display:flex;align-items:center;gap:16px;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,.05);margin-bottom:24px;}
.t5-hd-num{font-family:var(--f-d);font-size:50px;color:rgba(0,245,255,.05);line-height:1;}
.t5-hd-main{font-family:var(--f-d);font-size:22px;letter-spacing:2px;}
.t5-hd-sub{font-family:var(--f-m);font-size:8px;color:rgba(160,176,208,.28);letter-spacing:2px;text-transform:uppercase;margin-top:3px;}
.t5-kpi{background:rgba(255,255,255,.022);border:1px solid rgba(255,255,255,.06);border-top:2px solid var(--kc,#00F5FF);border-radius:14px;padding:18px 16px;text-align:center;}
.t5-kpi-lbl{font-family:var(--f-m);font-size:9px;color:rgba(140,155,178,.48);text-transform:uppercase;letter-spacing:2px;margin-bottom:7px;}
.t5-kpi-val{font-family:var(--f-d);font-size:44px;color:#FFF;line-height:.9;}
.t5-kpi-sub{font-family:var(--f-b);font-size:11px;color:var(--kc,#00F5FF);font-weight:600;margin-top:5px;}
.t5-sig{padding:15px 20px;border-radius:0 12px 12px 0;border-left:4px solid;margin:14px 0;}
.ccard{background:rgba(255,255,255,.022);border:1px solid rgba(80,90,110,.22);border-left:4px solid #00F5FF;padding:20px 22px 15px;margin-bottom:12px;border-radius:0 10px 10px 0;position:relative;overflow:hidden;}
.ccard::before{content:'CLASSIFIED';position:absolute;top:8px;right:12px;font-family:var(--f-o);font-size:7px;color:rgba(255,49,49,.14);letter-spacing:4px;}
.ccard.gold{border-left-color:#FFD700;}.ccard.gold::before{content:'PRIORITY';}
.ccard.red{border-left-color:#FF3131;}.ccard.red::before{content:'CRITICAL';}
.ccard.green{border-left-color:#00FF7F;}.ccard.green::before{content:'ACTIVE';}
.ccard-t{font-family:var(--f-b);font-size:17px;font-weight:700;color:#FFF;letter-spacing:1px;margin-bottom:5px;}
.ccard-k{font-family:var(--f-b);font-size:14px;font-weight:600;color:rgba(0,245,255,.8);line-height:1.5;margin-bottom:5px;}
.ccard-d{font-family:var(--f-m);font-size:11px;color:rgba(160,176,208,.46);line-height:1.7;}
.tl-wrap{display:flex;justify-content:center;gap:28px;padding:36px 20px;background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.05);border-radius:20px;margin:14px 0;}
.tl-circle{width:116px;height:116px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:var(--f-b);font-size:13px;font-weight:700;letter-spacing:.5px;position:relative;}
.tl-circle.dim{opacity:.1;filter:grayscale(.9);}
.tl-circle.active::after{content:'';position:absolute;inset:-8px;border-radius:50%;border:2px solid currentColor;animation:tl-pulse 2s ease-in-out infinite;}
@keyframes tl-pulse{0%,100%{transform:scale(1);opacity:.5;}50%{transform:scale(1.07);opacity:1;}}
.tl-red{background:radial-gradient(circle at 35% 35%,#ff5555,#991111);color:#FFB3B3;}
.tl-yellow{background:radial-gradient(circle at 35% 35%,#FFD700,#9A7A00);color:#FFF3B0;}
.tl-green{background:radial-gradient(circle at 35% 35%,#00FF7F,#006635);color:#B3FFD8;}
.whale-row{display:flex;align-items:center;gap:12px;padding:10px 15px;background:rgba(255,255,255,.014);border:1px solid rgba(255,255,255,.04);border-radius:8px;margin-bottom:5px;}
.w-rank{font-family:var(--f-o);font-size:10px;min-width:24px;letter-spacing:1px;}
.w-name{font-family:var(--f-b);font-size:13px;font-weight:600;color:rgba(0,245,255,.8);flex:1;}
.w-shares{font-family:var(--f-m);font-size:11px;color:rgba(160,176,208,.48);min-width:80px;text-align:right;}
.w-pct{font-family:var(--f-m);font-size:11px;color:rgba(0,255,127,.6);min-width:60px;text-align:right;}
.srow{display:flex;align-items:center;gap:12px;padding:9px 14px;background:rgba(255,255,255,.014);border:1px solid rgba(255,255,255,.04);border-radius:8px;margin-bottom:5px;}
.srow-name{font-family:var(--f-b);font-size:14px;font-weight:700;color:rgba(0,245,255,.7);min-width:120px;}
.srow-stk{font-family:var(--f-m);font-size:11px;color:rgba(160,176,208,.46);}
.calc-scr{background:#000;border:2px solid rgba(80,90,110,.32);border-radius:14px;padding:32px 28px;text-align:center;position:relative;overflow:hidden;margin-top:16px;}
.calc-scr::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,245,255,.2),transparent);}
.calc-scr::after{content:'CBAS LEVERAGE ENGINE';position:absolute;top:10px;left:16px;font-family:var(--f-o);font-size:7px;color:rgba(0,245,255,.14);letter-spacing:4px;}
.t5-foot{font-family:var(--f-m);font-size:9px;color:rgba(70,90,110,.2);letter-spacing:2px;text-align:right;margin-top:30px;padding-top:16px;border-top:1px solid rgba(255,255,255,.03);text-transform:uppercase;}
</style>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# DATA FETCHER
# ════════════════════════════════════════════════════════════════════
import re as _re

def _is_tw_ticker(symbol: str) -> bool:
    """Detect if symbol looks like a TW/TWO ticker (no suffix yet)."""
    return bool(_re.fullmatch(r'\d{4,5}[A-Z0-9]*', symbol.upper()))

@st.cache_data(ttl=300, show_spinner=False)
def _fetch(symbol: str):
    try:
        # Auto-resolve TW/TWO suffix if missing
        sym_upper = symbol.upper()
        if _is_tw_ticker(sym_upper):
            # Try TWSE (.TW) first, then OTC (.TWO)
            for suffix in [".TW", ".TWO"]:
                try:
                    _tk = yf.Ticker(sym_upper + suffix)
                    _h = _tk.history(period="5d")
                    if not _h.empty:
                        symbol = sym_upper + suffix
                        break
                except Exception:
                    continue
        tk = yf.Ticker(symbol)
        h1 = tk.history(period="1y")
        h3 = tk.history(period="3y")
        if h1.empty:
            return pd.DataFrame(), pd.DataFrame(), {}, pd.DataFrame(), \
                   f"查無數據 '{symbol}'。請確認代號是否正確。"
        for h in [h1, h3]:
            if hasattr(h.index, "tz") and h.index.tz is not None:
                h.index = h.index.tz_localize(None)
        info = tk.info or {}
        try:
            holders = tk.institutional_holders
            if holders is None:
                holders = pd.DataFrame()
        except Exception:
            holders = pd.DataFrame()
        return h1, h3, info, holders, None
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), {}, pd.DataFrame(), str(e)


# ════════════════════════════════════════════════════════════════════
# HERO + SEARCH
# ════════════════════════════════════════════════════════════════════
def _hero(symbol: str):
    st.markdown(f"""
<div class="t5-hero">
  <div class="t5-hero-label">titan os v500 · universal market analyzer</div>
  <div class="t5-hero-title">MARKET INTEL HUB</div>
  <div class="t5-hero-sub">US · TW · ETF — TARGET: <span style="color:#00F5FF;opacity:.9;">{symbol}</span></div>
</div>""", unsafe_allow_html=True)


def _search() -> str:
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:rgba(0,245,255,.28);letter-spacing:3px;text-transform:uppercase;margin-bottom:6px;">⬡ TARGET ACQUISITION</div>', unsafe_allow_html=True)
    ca, cb, cc = st.columns([3, 1, 4])
    with ca:
        sym = st.text_input("Symbol", value=st.session_state.get("t5_symbol","SPY"),
                            placeholder="AAPL · NVDA · 2330 · 00675L · 5274",
                            label_visibility="collapsed", key="t5_sym_inp")
    with cb:
        if st.button("🔍 鎖定", use_container_width=True, type="primary"):
            st.session_state["t5_symbol"] = sym.strip().upper()
            st.rerun()
    with cc:
        st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(160,176,208,.28);padding:8px 0;line-height:1.7;">美股: AAPL · NVDA · TSLA &nbsp;|&nbsp; 台股: 2330 · 2454 · 5274 &nbsp;|&nbsp; ETF: SPY · 0050 · 00675L</div>', unsafe_allow_html=True)
    return st.session_state.get("t5_symbol", sym.strip().upper() if sym else "SPY")


# ════════════════════════════════════════════════════════════════════
# NAV RAIL
# ════════════════════════════════════════════════════════════════════
_NAV = [
    ("5.1","🕵️","籌碼K線","Chip Master",   "#00F5FF"),
    ("5.2","🚀","起漲K線","Rising K",       "#00FF7F"),
    ("5.3","⚡","權證小哥","Tick Master",   "#FFD700"),
    ("5.4","🚦","艾蜜莉", "Value Queen",   "#FF9A3C"),
    ("5.5","🐋","13F巨鯨","Whale Watcher", "#B77DFF"),
    ("5.6","📜","戰略百科","The Codex",    "#FF3131"),
]

def _nav():
    if "t5_active" not in st.session_state:
        st.session_state.t5_active = "5.1"
    active = st.session_state.t5_active
    st.markdown('<div class="t5-nav-rail"><div class="t5-nav-lbl">⬡ ANALYSIS MODULES — CLICK TO SELECT</div>', unsafe_allow_html=True)
    cols = st.columns(6)
    for col, (sid, icon, title, sub, accent) in zip(cols, _NAV):
        is_a  = (active == sid)
        brd   = f"2px solid {accent}" if is_a else "1px solid rgba(255,255,255,.06)"
        bg    = "rgba(0,0,0,.2)"      if is_a else "rgba(255,255,255,.015)"
        glow  = f"0 0 22px {accent}28,0 4px 18px rgba(0,0,0,.5)" if is_a else "0 2px 10px rgba(0,0,0,.4)"
        lc    = accent if is_a else "rgba(200,215,230,.68)"
        tc    = accent if is_a else "rgba(100,120,140,.42)"
        top   = f'<div style="position:absolute;top:0;left:15%;right:15%;height:2px;background:{accent};border-radius:0 0 2px 2px;"></div>' if is_a else ""
        with col:
            st.markdown(f"""
<div style="height:120px;background:{bg};border:{brd};border-radius:14px;
    display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;
    box-shadow:{glow};overflow:hidden;position:relative;">
  {top}
  <div style="font-size:24px;line-height:1;filter:drop-shadow(0 0 6px {accent}44);">{icon}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:12px;font-weight:700;color:{lc};text-align:center;padding:0 4px;letter-spacing:.3px;">{sid} {title}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:7px;color:{tc};letter-spacing:2px;text-transform:uppercase;">{sub}</div>
</div>""", unsafe_allow_html=True)
            if st.button(f"▶ {sid}", key=f"t5_nav_{sid}", use_container_width=True):
                st.session_state.t5_active = sid
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════
def _hd(num, title, sub, color="#00F5FF"):
    st.markdown(f"""
<div class="t5-hd">
  <div class="t5-hd-num">{num}</div>
  <div>
    <div class="t5-hd-main" style="color:{color};">{title}</div>
    <div class="t5-hd-sub">{sub}</div>
  </div>
</div>""", unsafe_allow_html=True)

def _kpi(col, label, value, sub, color):
    col.markdown(f"""
<div class="t5-kpi" style="--kc:{color};">
  <div class="t5-kpi-lbl">{label}</div>
  <div class="t5-kpi-val">{value}</div>
  <div class="t5-kpi-sub">{sub}</div>
</div>""", unsafe_allow_html=True)

def _banner(msg_big, msg_small, color, icon=""):
    st.markdown(f"""
<div class="t5-sig" style="background:rgba(0,0,0,.18);border-color:{color};">
  <div style="font-family:'Rajdhani',sans-serif;font-size:20px;font-weight:700;color:{color};">
    {icon} {msg_big}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:{color}88;margin-top:4px;">
    {msg_small}</div>
</div>""", unsafe_allow_html=True)

def _prep(hist: pd.DataFrame) -> pd.DataFrame:
    df = hist.copy().reset_index()
    for c in df.columns:
        if str(c).lower() in ["date","datetime","index"]:
            df.rename(columns={c: "Date"}, inplace=True); break
    if "Date" not in df.columns:
        df["Date"] = df.index
    df["Date"] = pd.to_datetime(df["Date"])
    return df

def _sec28(text):
    st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:28px;font-weight:900;color:#FFF;letter-spacing:2px;margin-bottom:4px;">{text}</div>', unsafe_allow_html=True)

def _sec26(text, color="rgba(160,176,208,.4)"):
    st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:{color};margin-bottom:10px;">{text}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# 5.1  籌碼K線  CHIP MASTER
# ════════════════════════════════════════════════════════════════════
def _s51(hist: pd.DataFrame, info: dict, symbol: str):
    _hd("5.1","🕵️ 主力籌碼透視 (Smart Money Flow)",
        "VWAP·20 · VWAP·50 · OBV · Smart Money Score · Volume Profile","#00F5FF")
    if hist.empty: st.error("⚠️ 無歷史數據"); return
    df = _prep(hist)

    df["TP"]     = (df["High"]+df["Low"]+df["Close"])/3
    df["VWAP"]   = (df["TP"]*df["Volume"]).rolling(20).sum()/df["Volume"].rolling(20).sum()
    df["VWAP50"] = (df["TP"]*df["Volume"]).rolling(50).sum()/df["Volume"].rolling(50).sum()

    obv=[0]
    for i in range(1,len(df)):
        d=df["Volume"].iloc[i]
        obv.append(obv[-1]+d if df["Close"].iloc[i]>df["Close"].iloc[i-1]
                   else obv[-1]-d if df["Close"].iloc[i]<df["Close"].iloc[i-1] else obv[-1])
    df["OBV"]=obv
    df["OBV_MA"]=df["OBV"].rolling(20).mean()

    cp=float(df["Close"].iloc[-1])
    vwap=float(df["VWAP"].iloc[-1]) if not pd.isna(df["VWAP"].iloc[-1]) else cp
    v50=float(df["VWAP50"].iloc[-1]) if not pd.isna(df["VWAP50"].iloc[-1]) else cp
    obv_c=float(df["OBV"].iloc[-1])
    obv_p=float(df["OBV"].iloc[-21]) if len(df)>21 else float(df["OBV"].iloc[0])
    vwap_dev=(cp-vwap)/vwap*100 if vwap>0 else 0
    obv_up=obv_c>obv_p
    score=50+min(30,vwap_dev*3 if vwap_dev>0 else max(-30,vwap_dev*3))+(20 if obv_up else -20)
    score=int(max(0,min(100,score)))
    sc="#00FF7F" if score>=60 else ("#FFD700" if score>=40 else "#FF3131")

    c1,c2,c3,c4,c5=st.columns(5)
    _kpi(c1,"目前股價",f"{cp:.2f}","","#00F5FF")
    _kpi(c2,"VWAP 20日",f"{vwap:.2f}",f"偏離 {vwap_dev:+.1f}%","#00FF7F" if cp>vwap else "#FF3131")
    _kpi(c3,"VWAP 50日",f"{v50:.2f}",f"{'上方✓' if cp>v50 else '下方✗'}","#00FF7F" if cp>v50 else "#FF6060")
    _kpi(c4,"OBV趨勢","累積▲" if obv_up else "派發▼","Smart Money方向","#00FF7F" if obv_up else "#FF3131")
    _kpi(c5,"籌碼評分",f"{score}","0弱→100強",sc)
    st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)

    if score>=60:   _banner("🟢 法人多頭佈局 ACCUMULATION",f"Price({cp:.2f})>VWAP20({vwap:.2f}) ✦ OBV上升 ✦ Score {score}/100","#00FF7F")
    elif score>=40: _banner("🟡 法人觀望 NEUTRAL",f"籌碼混沌，VWAP偏離 {vwap_dev:+.1f}% ✦ 等待方向","#FFD700")
    else:           _banner("🔴 法人賣壓 DISTRIBUTION",f"Price({cp:.2f})<VWAP20({vwap:.2f}) ✦ OBV下降 ✦ Score {score}/100","#FF3131")

    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    _sec28("PRICE × VWAP OVERLAY")
    _sec26("青色=收盤價 · 金色=VWAP20 · 橙色=VWAP50")

    tail=120
    dp=df[["Date","Close","VWAP","VWAP50"]].dropna().tail(tail)
    dm=dp.melt("Date",var_name="Series",value_name="Price")
    ch=alt.Chart(dm).mark_line(strokeWidth=1.8).encode(
        x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
        y=alt.Y("Price:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
        color=alt.Color("Series:N",scale=alt.Scale(domain=["Close","VWAP","VWAP50"],range=["#00F5FF","#FFD700","#FF9A3C"]),
                        legend=alt.Legend(labelColor="#aaa",titleColor="#aaa",orient="top-right"))
    ).properties(background="transparent",height=260).configure_view(strokeOpacity=0)
    st.altair_chart(ch,use_container_width=True)

    _sec28("ON-BALANCE VOLUME (OBV)")
    _sec26("紫色=OBV原始 · 橙色=20日均線 — 斜率向上=法人買進")
    do=df[["Date","OBV","OBV_MA"]].dropna().tail(tail)
    dom=do.melt("Date",var_name="Series",value_name="Value")
    ch2=alt.Chart(dom).mark_line(strokeWidth=1.6).encode(
        x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
        y=alt.Y("Value:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
        color=alt.Color("Series:N",scale=alt.Scale(domain=["OBV","OBV_MA"],range=["#B77DFF","#FF9A3C"]),
                        legend=alt.Legend(labelColor="#aaa",titleColor="#aaa",orient="top-right"))
    ).properties(background="transparent",height=200).configure_view(strokeOpacity=0)
    st.altair_chart(ch2,use_container_width=True)

    _sec28("VOLUME PROFILE (90D)")
    _sec26("綠柱=收漲 · 紅柱=收跌 · 金色虛線=20日均量")
    dv=df[["Date","Volume","Close"]].tail(90).copy()
    dv["AvgVol"]=dv["Volume"].rolling(20).mean()
    dv["clr"]=dv["Close"].diff().apply(lambda x:"#00FF7F" if x>=0 else "#FF6060")
    cv=alt.Chart(dv).mark_bar(opacity=0.75,cornerRadiusTopLeft=2,cornerRadiusTopRight=2).encode(
        x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
        y=alt.Y("Volume:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
        color=alt.Color("clr:N",scale=None,legend=None))
    ca2=alt.Chart(dv).mark_line(color="#FFD700",strokeWidth=1.4,strokeDash=[4,4]).encode(x="Date:T",y="AvgVol:Q")
    st.altair_chart((cv+ca2).properties(background="transparent",height=180).configure_view(strokeOpacity=0),use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# 5.2  起漲K線  RISING K
# ════════════════════════════════════════════════════════════════════
def _s52(hist: pd.DataFrame, symbol: str):
    _hd("5.2","🚀 動能突破偵測 (Momentum Ignition)",
        "Bollinger Squeeze · Keltner Confirm · BW% · Momentum Histogram","#00FF7F")
    if hist.empty: st.error("⚠️ 無歷史數據"); return
    df=_prep(hist)

    df["BB_mid"]=df["Close"].rolling(20).mean()
    df["BB_std"]=df["Close"].rolling(20).std()
    df["BB_up"]=df["BB_mid"]+2*df["BB_std"]
    df["BB_dn"]=df["BB_mid"]-2*df["BB_std"]
    df["BW"]=(df["BB_up"]-df["BB_dn"])/df["BB_mid"]*100
    df["TR"]=np.maximum(df["High"]-df["Low"],np.maximum(abs(df["High"]-df["Close"].shift(1)),abs(df["Low"]-df["Close"].shift(1))))
    df["ATR14"]=df["TR"].rolling(14).mean()
    df["KC_up"]=df["BB_mid"]+1.5*df["ATR14"]
    df["KC_dn"]=df["BB_mid"]-1.5*df["ATR14"]
    df["Squeeze"]=(df["BB_up"]<df["KC_up"])&(df["BB_dn"]>df["KC_dn"])
    df["MOM"]= df["Close"]-((df["High"].rolling(20).max()+df["Low"].rolling(20).min())/2+df["BB_mid"])/2

    bw_now=float(df["BW"].iloc[-1]) if not df["BW"].isna().all() else None
    bw_6mlo=float(df["BW"].tail(126).min()) if len(df)>=20 else None
    sq_now=bool(df["Squeeze"].iloc[-1]) if not df["Squeeze"].isna().all() else False
    mom_now=float(df["MOM"].iloc[-1]) if not df["MOM"].isna().all() else 0
    cp=float(df["Close"].iloc[-1])

    c1,c2,c3,c4=st.columns(4)
    _kpi(c1,"目前股價",f"{cp:.2f}","","#00F5FF")
    _kpi(c2,"帶寬 BW%",f"{bw_now:.1f}%" if bw_now else "N/A","<12%=蓄勢","#00FF7F" if bw_now and bw_now<12 else "#FFD700")
    _kpi(c3,"BB×KC Squeeze","🔥 擠壓中" if sq_now else "⬜ 無擠壓","BB inside KC" if sq_now else "BB在KC外","#00FF7F" if sq_now else "#888")
    _kpi(c4,"動能方向","▲ 多頭" if mom_now>0 else "▼ 空頭",f"MOM {mom_now:+.2f}","#00FF7F" if mom_now>0 else "#FF3131")
    st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)

    if sq_now and mom_now>0:   _banner("🔥 蓄勢待發 SQUEEZE — 多頭爆發",f"BB inside KC ✦ BW={bw_now:.1f}% ✦ 動能向上 {mom_now:+.2f}","#00FF7F","🚀")
    elif sq_now and mom_now<0: _banner("⚠️ 擠壓出現 SQUEEZE — 空頭方向",f"BB inside KC ✦ BW={bw_now:.1f}% ✦ 動能向下 {mom_now:+.2f}","#FF9A3C","⚠️")
    elif bw_now and bw_now<12: _banner("🟡 帶寬收窄 LOW BANDWIDTH",f"BW={bw_now:.1f}% ✦ 等待KC確認","#FFD700")
    else:                      _banner("⬜ 正常震盪 NORMAL",f"BW={bw_now:.1f}% — 持續監控帶寬","#888")

    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    _sec28("BOLLINGER BANDS + KELTNER CHANNEL")
    _sec26("綠帶=BB · 橙帶=KC · BB在KC內=擠壓 · 青線=收盤價")

    dp=df[["Date","Close","BB_up","BB_dn","BB_mid","KC_up","KC_dn"]].dropna().tail(120)
    base=alt.Chart(dp)
    bb_area=base.mark_area(opacity=0.08,color="#00FF7F").encode(x="Date:T",y="BB_dn:Q",y2="BB_up")
    kc_area=base.mark_area(opacity=0.05,color="#FF9A3C").encode(x="Date:T",y="KC_dn:Q",y2="KC_up")
    cl=base.mark_line(color="#00F5FF",strokeWidth=2).encode(x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),y=alt.Y("Close:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")))
    ml=base.mark_line(color="#FFD70055",strokeWidth=1,strokeDash=[4,4]).encode(x="Date:T",y="BB_mid:Q")
    bbu=base.mark_line(color="#00FF7F60",strokeWidth=1).encode(x="Date:T",y="BB_up:Q")
    bbd=base.mark_line(color="#00FF7F60",strokeWidth=1).encode(x="Date:T",y="BB_dn:Q")
    kcu=base.mark_line(color="#FF9A3C50",strokeWidth=1,strokeDash=[2,2]).encode(x="Date:T",y="KC_up:Q")
    kcd=base.mark_line(color="#FF9A3C50",strokeWidth=1,strokeDash=[2,2]).encode(x="Date:T",y="KC_dn:Q")
    st.altair_chart((bb_area+kc_area+cl+ml+bbu+bbd+kcu+kcd).properties(background="transparent",height=280).configure_view(strokeOpacity=0).configure_axis(labelColor="#555",gridColor="#1a1a2a"),use_container_width=True)

    _sec28("BANDWIDTH % HISTORY")
    _sec26("低帶寬=能量壓縮 · 帶寬急升=爆發 · 紅虛線=12%門檻")
    dbw=df[["Date","BW"]].dropna().tail(120)
    bw_line=alt.Chart(dbw).mark_area(line={"color":"#00FF7F","strokeWidth":1.4},color=alt.Gradient(gradient="linear",stops=[alt.GradientStop(color="rgba(0,255,127,.22)",offset=0),alt.GradientStop(color="rgba(0,255,127,.0)",offset=1)],x1=1,x2=1,y1=1,y2=0)).encode(x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),y=alt.Y("BW:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")))
    ref12=alt.Chart(pd.DataFrame({"y":[12.0]})).mark_rule(color="#FF3131",strokeDash=[4,4],strokeWidth=1,opacity=0.6).encode(y="y:Q")
    st.altair_chart((bw_line+ref12).properties(background="transparent",height=180).configure_view(strokeOpacity=0),use_container_width=True)

    _sec28("SQUEEZE MOMENTUM HISTOGRAM")
    _sec26("綠柱=多頭動能 · 紅柱=空頭動能 — 擠壓後第一根彩柱=方向確認")
    dm2=df[["Date","MOM"]].dropna().tail(90).copy()
    dm2["clr"]=dm2["MOM"].apply(lambda v:"#00FF7F" if v>=0 else "#FF3131")
    mb=alt.Chart(dm2).mark_bar(opacity=0.8,cornerRadiusTopLeft=2,cornerRadiusTopRight=2).encode(x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),y=alt.Y("MOM:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),color=alt.Color("clr:N",scale=None,legend=None))
    zero=alt.Chart(pd.DataFrame({"y":[0.0]})).mark_rule(color="#888",strokeWidth=0.8,opacity=0.4).encode(y="y:Q")
    st.altair_chart((mb+zero).properties(background="transparent",height=180).configure_view(strokeOpacity=0),use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# 5.3  權證小哥  TICK MASTER  (★ ALTAIR BUG FIXED)
# ════════════════════════════════════════════════════════════════════
def _s53(hist: pd.DataFrame, symbol: str):
    _hd("5.3","⚡ 短線當沖雷達 (Day Trade Radar)",
        "ATR14 波動點數 · 爆量比 RelVol · 隔日沖風險矩陣","#FFD700")
    if hist.empty: st.error("⚠️ 無歷史數據"); return
    df=_prep(hist)

    df["TR"]=np.maximum(df["High"]-df["Low"],np.maximum(abs(df["High"]-df["Close"].shift(1)),abs(df["Low"]-df["Close"].shift(1))))
    df["ATR14"]=df["TR"].rolling(14).mean()
    df["ATR7"]=df["TR"].rolling(7).mean()
    df["AvgVol20"]=df["Volume"].rolling(20).mean()
    df["RelVol"]=df["Volume"]/df["AvgVol20"].replace(0,np.nan)
    df["Ret1"]=df["Close"].pct_change(1)*100
    df["Ret5"]=df["Close"].pct_change(5)*100

    cp=float(df["Close"].iloc[-1])
    atr14=float(df["ATR14"].iloc[-1]) if not pd.isna(df["ATR14"].iloc[-1]) else 0
    atr7=float(df["ATR7"].iloc[-1])   if not pd.isna(df["ATR7"].iloc[-1])  else 0
    atr_pct=atr14/cp*100 if cp>0 else 0
    rv=float(df["RelVol"].iloc[-1])   if not pd.isna(df["RelVol"].iloc[-1]) else 1.0
    vol_now=int(df["Volume"].iloc[-1])
    avg_vol=int(df["AvgVol20"].iloc[-1]) if not pd.isna(df["AvgVol20"].iloc[-1]) else 0
    r1=float(df["Ret1"].iloc[-1]) if not pd.isna(df["Ret1"].iloc[-1]) else 0
    r5=float(df["Ret5"].iloc[-1]) if not pd.isna(df["Ret5"].iloc[-1]) else 0
    rv_color="#FF3131" if rv>3 else ("#FFD700" if rv>1.5 else "#00FF7F")

    c1,c2,c3,c4,c5,c6=st.columns(6)
    _kpi(c1,"ATR14 波動點",f"{atr14:.2f}",f"佔股價 {atr_pct:.1f}%","#00F5FF")
    _kpi(c2,"ATR7 近期波動",f"{atr7:.2f}",f"{'↑加速' if atr7>atr14 else '↓緩和'}","#FF9A3C" if atr7>atr14 else "#00FF7F")
    _kpi(c3,"爆量比 RelVol",f"{rv:.1f}×","今日/20日均量",rv_color)
    _kpi(c4,"今日成交量",f"{vol_now/1e6:.1f}M" if vol_now>1e6 else f"{vol_now:,}","","#B77DFF")
    _kpi(c5,"日漲跌 Ret1D",f"{r1:+.1f}%","","#00FF7F" if r1>0 else "#FF3131")
    _kpi(c6,"週漲跌 Ret5D",f"{r5:+.1f}%","","#00FF7F" if r5>0 else "#FF3131")
    st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)

    if rv>3:       _banner("⚠️ 隔日沖極高風險 HIGH OVERNIGHT RISK",f"RelVol {rv:.1f}× > 3 ✦ ATR {atr14:.2f} ({atr_pct:.1f}%) ✦ 建議當天平倉","#FF3131","🚨")
    elif rv>1.5:   _banner("🟡 量能放大 ELEVATED VOLUME",f"RelVol {rv:.1f}× > 1.5 ✦ 方向正確可跟進，錯誤快速停損","#FFD700","📊")
    else:          _banner("🟢 量能平穩 NORMAL RANGE",f"RelVol {rv:.1f}× — 正常量能，ATR停損參考 {atr14:.2f}","#00FF7F","✅")

    # ATR Stop Grid
    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    _sec28("ATR STOP-LOSS GRID")
    cg1,cg2,cg3,cg4=st.columns(4)
    for col,mult,tag,c in[(cg1,0.5,"保守 Conservative","#00FF7F"),(cg2,1.0,"標準 Standard","#FFD700"),(cg3,1.5,"積極 Aggressive","#FF9A3C"),(cg4,2.0,"極限 Maximum","#FF3131")]:
        sl=cp-atr14*mult
        col.markdown(f'<div style="padding:14px;background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.05);border-top:2px solid {c};border-radius:10px;text-align:center;"><div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:{c}88;letter-spacing:2px;margin-bottom:5px;">{tag}</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:32px;color:{c};line-height:1;">{sl:.2f}</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(160,176,208,.4);margin-top:3px;">ATR × {mult}</div></div>',unsafe_allow_html=True)

    ca_col,cb_col=st.columns(2)
    with ca_col:
        _sec28("ATR14 VOLATILITY HISTORY")
        da=df[["Date","ATR14","ATR7"]].dropna().tail(90)
        dam=da.melt("Date",var_name="Series",value_name="ATR")
        st.altair_chart(alt.Chart(dam).mark_line(strokeWidth=1.6).encode(
            x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            y=alt.Y("ATR:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            color=alt.Color("Series:N",scale=alt.Scale(domain=["ATR14","ATR7"],range=["#00F5FF","#FF9A3C"]),legend=alt.Legend(labelColor="#aaa",titleColor="#aaa",orient="top-right"))
        ).properties(background="transparent",height=200).configure_view(strokeOpacity=0),use_container_width=True)

    with cb_col:
        # ★ FIX: use pandas column for bar colors — avoids nested alt.condition()
        _sec28("RELATIVE VOLUME 爆量比")
        _sec26("紅=爆量(>3×) · 黃=放量(1.5-3×) · 綠=正常(<1.5×)")
        drv=df[["Date","RelVol"]].dropna().tail(90).copy()
        drv["clr"]=drv["RelVol"].apply(lambda v:"#FF3131" if v>3 else ("#FFD700" if v>1.5 else "#00FF7F"))
        rv_bar=alt.Chart(drv).mark_bar(opacity=0.78,cornerRadiusTopLeft=2,cornerRadiusTopRight=2).encode(
            x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            y=alt.Y("RelVol:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            color=alt.Color("clr:N",scale=None,legend=None))
        r1r=alt.Chart(pd.DataFrame({"y":[1.5]})).mark_rule(color="#FFD700",strokeDash=[4,4],strokeWidth=1,opacity=0.5).encode(y="y:Q")
        r3r=alt.Chart(pd.DataFrame({"y":[3.0]})).mark_rule(color="#FF3131",strokeDash=[4,4],strokeWidth=1,opacity=0.5).encode(y="y:Q")
        st.altair_chart((rv_bar+r1r+r3r).properties(background="transparent",height=200).configure_view(strokeOpacity=0),use_container_width=True)

    _sec28("SHORT-TERM TRADING GUIDANCE")
    gm=[(("ATR波動評級","🔴 高波動" if atr_pct>3 else ("🟡 中波動" if atr_pct>1.5 else "🟢 低波動"),f"每日ATR {atr_pct:.1f}%","#FFD700")),
        ("量能狀態","⚠️ 爆量警戒" if rv>3 else ("⚡ 量能放大" if rv>1.5 else "✅ 量能正常"),f"RelVol {rv:.1f}×",rv_color),
        ("當日趨勢",f"{'▲ 漲勢' if r1>0 else '▼ 跌勢'}",f"日漲跌 {r1:+.1f}%","#00FF7F" if r1>0 else "#FF3131"),
        ("5日趨勢",f"{'▲ 強勢' if r5>2 else ('⬜ 整理' if abs(r5)<2 else '▼ 弱勢')}",f"週漲跌 {r5:+.1f}%","#00FF7F" if r5>2 else ("#888" if abs(r5)<2 else "#FF3131"))]
    gc1,gc2,gc3,gc4=st.columns(4)
    for col,(title,val,sub,c) in zip([gc1,gc2,gc3,gc4],gm):
        col.markdown(f'<div style="padding:14px;background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.05);border-top:2px solid {c};border-radius:10px;"><div style="font-family:\'Rajdhani\',sans-serif;font-size:12px;font-weight:700;color:{c};margin-bottom:5px;">{title}</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:22px;color:#FFF;line-height:1.1;">{val}</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(160,176,208,.4);margin-top:4px;">{sub}</div></div>',unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# 5.4  艾蜜莉定存  VALUE QUEEN
# ════════════════════════════════════════════════════════════════════
def _s54(hist3y: pd.DataFrame, info: dict, symbol: str):
    _hd("5.4","🚦 價值紅綠燈 (Valuation Traffic Light)",
        "3Y Historical PE · 25/50/75 Percentile · DDM Fair Value · PE Gauge","#FF9A3C")

    eps=info.get("trailingEps") or info.get("forwardEps")
    pe_trail=info.get("trailingPE"); pe_fwd=info.get("forwardPE")
    pb=info.get("priceToBook"); ps=info.get("priceToSalesTrailing12Months")
    div_y=info.get("dividendYield",0) or 0; roe=info.get("returnOnEquity",0) or 0
    cp=info.get("currentPrice") or info.get("regularMarketPrice") or (float(hist3y["Close"].iloc[-1]) if not hist3y.empty else 0)

    pe_25=pe_50=pe_75=hist_pe=None
    if not hist3y.empty and eps and float(eps)>0:
        pe_ser=(hist3y["Close"]/float(eps)).replace([np.inf,-np.inf],np.nan).dropna()
        pe_ser=pe_ser[pe_ser>0]
        if len(pe_ser)>20:
            pe_25=float(np.percentile(pe_ser,25)); pe_50=float(np.percentile(pe_ser,50))
            pe_75=float(np.percentile(pe_ser,75)); hist_pe=float(pe_ser.iloc[-1])

    use_pe=hist_pe or pe_trail or pe_fwd
    if use_pe and pe_25 and pe_75:
        signal="cheap" if use_pe<pe_25 else ("expensive" if use_pe>pe_75 else "fair")
    elif use_pe:
        signal="cheap" if use_pe<15 else ("expensive" if use_pe>35 else "fair")
    else:
        signal="neutral"

    sm={"cheap":("🟢 便宜 CHEAP","#00FF7F","建議逢低佈局"),
        "fair":("🟡 合理 FAIR","#FFD700","持有觀望"),
        "expensive":("🔴 昂貴 EXPENSIVE","#FF3131","謹慎操作"),
        "neutral":("⬜ 無PE數據","#888888","改看P/B · P/S")}
    sig_lbl,sig_c,sig_desc=sm[signal]

    ddm_val=None
    if div_y>0 and cp>0:
        D=cp*div_y; g=min(roe*0.5,0.08) if roe>0 else 0.03; r=0.10
        if r>g: ddm_val=D/(r-g)

    c1,c2,c3,c4,c5=st.columns(5)
    _kpi(c1,"目前股價",f"{cp:.2f}" if cp else "N/A","","#00F5FF")
    _kpi(c2,"EPS (TTM)",f"{float(eps):.2f}" if eps else "N/A","","#FFD700")
    _kpi(c3,"P/E 本益比",f"{use_pe:.1f}×" if use_pe else "N/A","當前PE",sig_c)
    _kpi(c4,"P/B 股價淨值",f"{pb:.2f}×" if pb else "N/A",">3偏貴","#B77DFF")
    _kpi(c5,"DDM 估值",f"{ddm_val:.2f}" if ddm_val else "N/A",f"{'低估✓' if ddm_val and cp<ddm_val else '高估✗' if ddm_val else '無配息'}","#00FF7F" if ddm_val and cp<ddm_val else "#FF6060")
    st.markdown("<div style='height:18px'></div>",unsafe_allow_html=True)

    def _circle(lbl,sub,cls,active):
        a="active" if active else "dim"
        return f'<div class="tl-circle {cls} {a}"><div style="font-size:13px;font-weight:800;">{lbl}</div><div style="font-size:9px;opacity:.7;margin-top:3px;">{sub}</div></div>'
    if pe_25 and pe_75:
        rows=[(signal=="expensive","tl-red","🔴 昂貴",f"PE>{pe_75:.0f}"),(signal=="fair","tl-yellow","🟡 合理",f"PE {pe_25:.0f}-{pe_75:.0f}"),(signal=="cheap","tl-green","🟢 便宜",f"PE<{pe_25:.0f}")]
    else:
        rows=[(signal=="expensive","tl-red","🔴 昂貴","PE>35"),(signal=="fair","tl-yellow","🟡 合理","PE 15-35"),(signal=="cheap","tl-green","🟢 便宜","PE<15")]
    circles="".join(_circle(lb,sb,cls,act) for act,cls,lb,sb in rows)
    st.markdown(f'<div class="tl-wrap">{circles}</div>',unsafe_allow_html=True)

    st.markdown(f'<div style="margin:12px 0;padding:18px 24px;background:rgba(0,0,0,.2);border:1px solid {sig_c}33;border-left:5px solid {sig_c};border-radius:0 12px 12px 0;text-align:center;"><div style="font-family:\'Rajdhani\',sans-serif;font-size:28px;font-weight:800;color:{sig_c};">{sig_lbl}</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:rgba(160,176,208,.4);margin-top:6px;">{sig_desc} · PE: {f"{use_pe:.1f}" if use_pe else "N/A"} · P/B: {f"{pb:.2f}" if pb else "N/A"} · Div: {div_y*100:.2f}%</div></div>',unsafe_allow_html=True)

    if not hist3y.empty and eps and float(eps)>0:
        _sec28("3Y HISTORICAL P/E CHART")
        _sec26("橙線=PE走勢 · 虛線=25/50/75分位 · 落在哪個區間=燈號依據")
        dpe=hist3y.copy().reset_index()
        for c in dpe.columns:
            if str(c).lower() in ["date","datetime","index"]:
                dpe.rename(columns={c:"Date"},inplace=True); break
        if "Date" not in dpe.columns: dpe["Date"]=dpe.index
        dpe["PE"]=dpe["Close"]/float(eps)
        dpe=dpe[["Date","PE"]].dropna(); dpe=dpe[dpe["PE"]>0]
        pe_chart=alt.Chart(dpe).mark_line(color="#FF9A3C",strokeWidth=1.8).encode(x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),y=alt.Y("PE:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")))
        rules=[]
        if pe_25:
            for pv,pc,pn in[(pe_25,"#00FF7F","25th"),(pe_50,"#FFD700","50th"),(pe_75,"#FF3131","75th")]:
                rules.append(alt.Chart(pd.DataFrame({"y":[pv]})).mark_rule(strokeDash=[4,4],color=pc,strokeWidth=1,opacity=0.65).encode(y="y:Q"))
        st.altair_chart(alt.layer(pe_chart,*rules).properties(background="transparent",height=250).configure_view(strokeOpacity=0),use_container_width=True)
        if pe_25 and pe_75 and use_pe:
            pct_pos=min(100,max(0,(use_pe-pe_25)/(pe_75-pe_25+0.001)*100))
            c_pos="#FF3131" if pct_pos>80 else ("#FFD700" if pct_pos>40 else "#00FF7F")
            st.markdown(f'<div style="margin:12px 0;"><div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:rgba(160,176,208,.35);letter-spacing:2px;margin-bottom:6px;">PE PERCENTILE GAUGE</div><div style="background:rgba(255,255,255,.05);border-radius:20px;height:8px;position:relative;overflow:hidden;"><div style="position:absolute;left:0;top:0;height:100%;width:{pct_pos:.0f}%;background:linear-gradient(90deg,#00FF7F,{c_pos});border-radius:20px;"></div></div><div style="font-family:\'Orbitron\',sans-serif;font-size:11px;color:{c_pos};margin-top:5px;text-align:right;">{pct_pos:.0f}th PERCENTILE</div></div>',unsafe_allow_html=True)
    else:
        st.info("💡 此標的無EPS數據（ETF/未獲利公司）。")
        if pe_trail: st.markdown(f"**Trailing P/E**: {pe_trail:.1f}×")
        if pe_fwd:   st.markdown(f"**Forward P/E**:  {pe_fwd:.1f}×")
        if ps:       st.markdown(f"**P/S (TTM)**:    {ps:.2f}×")


# ════════════════════════════════════════════════════════════════════
# 5.5  13F巨鯨  WHALE WATCHER
# ════════════════════════════════════════════════════════════════════
def _s55(holders: pd.DataFrame, info: dict, symbol: str):
    _hd("5.5","🐋 機構持倉揭秘 (Institutional Holdings)",
        "SEC 13F · Top 10 Holders · Concentration Donut · Bar Chart","#B77DFF")

    inst_pct=info.get("institutionPercentHeld"); insider_pct=info.get("heldPercentInsiders")
    short_pct=info.get("shortPercentOfFloat")
    c1,c2,c3,c4=st.columns(4)
    _kpi(c1,"機構持股%",f"{inst_pct*100:.1f}%" if inst_pct else "N/A","Institutional Held","#B77DFF")
    _kpi(c2,"內部人持股%",f"{insider_pct*100:.1f}%" if insider_pct else "N/A","Insider Held","#FF9A3C")
    _kpi(c3,"空單比 Short%",f"{short_pct*100:.1f}%" if short_pct else "N/A","Short Float","#FF3131" if short_pct and short_pct>0.1 else "#00FF7F")
    _kpi(c4,"Type",info.get("quoteType","N/A"),info.get("sector",""),"#00F5FF")
    st.markdown("<div style='height:16px'></div>",unsafe_allow_html=True)

    if holders is None or holders.empty:
        st.markdown('<div style="text-align:center;padding:60px 20px;background:rgba(255,255,255,.012);border:1px solid rgba(255,255,255,.05);border-radius:16px;"><div style="font-size:52px;opacity:.2;margin-bottom:14px;">🐋</div><div style="font-family:\'Rajdhani\',sans-serif;font-size:28px;color:rgba(255,255,255,.3);letter-spacing:2px;margin-bottom:8px;">暫無 13F 數據</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:rgba(160,176,208,.25);letter-spacing:2px;">台股 · ETF · 部分小型股無 SEC 13F 申報</div></div>',unsafe_allow_html=True)
        return

    hdf=holders.copy()
    col_map={}
    for c in hdf.columns:
        cl=str(c).lower()
        if any(k in cl for k in ["holder","institution","name","org"]): col_map[c]="Holder"
        elif "share" in cl and "pct" not in cl and "%" not in cl: col_map[c]="Shares"
        elif "value" in cl or ("market" in cl and "cap" not in cl): col_map[c]="Value"
        elif "pct" in cl or "percent" in cl or "%" in cl: col_map[c]="PctHeld"
    hdf.rename(columns=col_map,inplace=True)
    for need in ["Holder","Shares","Value","PctHeld"]:
        if need not in hdf.columns: hdf[need]=None
    hdf=hdf.head(10)
    # Normalize numeric columns — safely extract a single Python scalar from any cell type
    def _to_scalar(x):
        try:
            if x is None: return None
            if isinstance(x, (int, float)): return x
            if isinstance(x, pd.Series): x = x.iloc[0]
            elif isinstance(x, np.ndarray): x = x.flat[0]
            if hasattr(x, "item"): return float(x.item())
            return float(x)
        except Exception:
            return None
    for _nc in ["Shares","Value","PctHeld"]:
        hdf[_nc] = pd.to_numeric(hdf[_nc].apply(_to_scalar), errors="coerce")

    _sec28("TOP 10 INSTITUTIONAL HOLDERS")
    rank_colors=["#FFD700","#C0C0C0","#CD7F32"]+["#B77DFF"]*7
    for i,(_,row) in enumerate(hdf.iterrows()):
        holder=str(row.get("Holder","Unknown")); shares=row.get("Shares"); value=row.get("Value"); pct=row.get("PctHeld")
        rc=rank_colors[i]
        # Values are already float or NaN after normalization
        shares = float(shares) if shares is not None and not (isinstance(shares, float) and pd.isna(shares)) else None
        value  = float(value)  if value  is not None and not (isinstance(value,  float) and pd.isna(value))  else None
        pct    = float(pct)    if pct    is not None and not (isinstance(pct,    float) and pd.isna(pct))    else None
        sh_s=(f"{shares/1e9:.2f}B" if shares and shares>1e9 else f"{shares/1e6:.1f}M" if shares and shares>1e6 else f"{int(shares):,}" if shares else "N/A")
        vl_s=(f"${value/1e9:.2f}B" if value and value>1e9 else f"${value/1e6:.0f}M" if value and value>1e6 else "N/A")
        pc_s=(f"{pct*100:.2f}%" if pct is not None and pct < 1 else f"{pct:.2f}%" if pct is not None else "—")
        st.markdown(f'<div class="whale-row"><div class="w-rank" style="color:{rc};">#{i+1}</div><div class="w-name">{holder}</div><div class="w-shares">{sh_s}</div><div class="w-shares" style="color:rgba(255,154,60,.55);">{vl_s}</div><div class="w-pct">{pc_s}</div></div>',unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)
    _sec28("HOLDER CONCENTRATION CHART")
    ca_col,cb_col=st.columns([1,1])
    with ca_col:
        pct_data=hdf[["Holder","PctHeld"]].dropna().head(5)
        if len(pct_data)>=2:
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:rgba(183,125,255,.3);letter-spacing:3px;margin-bottom:6px;">DONUT — TOP 5 BY % HELD</div>',unsafe_allow_html=True)
            donut=alt.Chart(pct_data).mark_arc(innerRadius=45,outerRadius=110).encode(theta=alt.Theta("PctHeld:Q"),color=alt.Color("Holder:N",scale=alt.Scale(range=["#B77DFF","#00F5FF","#FFD700","#00FF7F","#FF9A3C"]),legend=alt.Legend(labelColor="#aaa",titleColor="#aaa",labelFontSize=10)),tooltip=["Holder:N",alt.Tooltip("PctHeld:Q",format=".4f")]).properties(background="transparent",height=260).configure_view(strokeOpacity=0)
            st.altair_chart(donut,use_container_width=True)
        else:
            st.info("持股比例數據不足。")
    with cb_col:
        sh_data=hdf[["Holder","Shares"]].dropna().head(8)
        if not sh_data.empty:
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:rgba(0,245,255,.3);letter-spacing:3px;margin-bottom:6px;">BAR — TOP 8 BY SHARES</div>',unsafe_allow_html=True)
            bar=alt.Chart(sh_data).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4,opacity=0.85).encode(x=alt.X("Shares:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),y=alt.Y("Holder:N",sort="-x",axis=alt.Axis(labelColor="#aaa",labelLimit=150)),color=alt.Color("Holder:N",scale=alt.Scale(range=["#B77DFF","#8B5CF6","#7C3AED","#6D28D9","#5B21B6","#4C1D95","#3730A3","#312E81"]),legend=None)).properties(background="transparent",height=260).configure_view(strokeOpacity=0)
            st.altair_chart(bar,use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# 5.6  戰略百科  THE CODEX
# ════════════════════════════════════════════════════════════════════
def _s56():
    _hd("5.6","📜 戰略百科 — The Codex",
        "SOP · Entry/Exit · Sector Map · Mindset · CBAS Engine · OTC MA","#FF3131")
    tabs=st.tabs(["⏰ 四大時間套利","📋 進出場紀律","🏭 產業族群庫","🧠 特殊心法","⚡ CBAS試算","📈 OTC神奇均線"])

    # T1
    with tabs[0]:
        _sec28("四大時間套利視窗")
        for cls,num,title,period,key,detail in [
            ("gold","01","新券蜜月期","上市 0–90 天","上市初期追蹤，大戶定調，股性未定","進場甜蜜點：105–115 元。前 90 天是觀察期也是機會期，關注大股東動態與首批券商報告。"),
            ("green","02","滿年沈澱","上市 350–420 天","沈澱洗牌結束，底部有支撐","觸發點：CB 站上 87MA 且帶量。一年洗盤後仍存活的標的底部結構扎實。"),
            ("","03","賣回保衛戰","距賣回日 < 180 天","下檔保護最強，CB 價 95–105 甜甜圈","最佳風報比窗口。賣回日臨近時，市場自然形成底部支撐，CB 不易跌破 100。"),
            ("red","04","百日轉換窗口","距到期 < 100 天","最後一搏，轉換或歸零","股價需站上轉換價 × 1.05 才有轉換意義。時間價值快速遞減，必須精確把握。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;"><div style="font-family:\'Orbitron\',sans-serif;font-size:28px;font-weight:900;color:rgba(0,245,255,.08);">{num}</div><div><div class="ccard-t">{title}</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:rgba(160,176,208,.28);letter-spacing:2px;">{period}</div></div></div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>',unsafe_allow_html=True)

    # T2
    with tabs[1]:
        _sec28("進出場鐵律")
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:26px;font-weight:700;color:rgba(0,255,127,.75);letter-spacing:2px;margin-bottom:10px;">📥 核心進場條件 — 4 COMMANDMENTS</div>',unsafe_allow_html=True)
        for cls,title,key,detail in [
            ("green","價格天條","CB 市價 < 120 元 (理想 105–115)","超過 120 = 溢價過高，槓桿效益不足。最佳甜蜜點 108–113 元。"),
            ("green","均線天條","87MA > 284MA","中期多頭確認。均線交叉後回踩 87MA 不破 = 最佳進場。"),
            ("","身分認證","領頭羊 or 風口豬","族群指標股或主流題材二軍，單兵不做。"),
            ("gold","發債故事","從無到有 / 擴產 / 政策事件","三選一。故事是引爆點，沒有故事的 CB 只是數字。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div class="ccard-t">{title}</div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>',unsafe_allow_html=True)
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:26px;font-weight:700;color:rgba(255,49,49,.75);letter-spacing:2px;margin:18px 0 10px;">📤 核心出場條件</div>',unsafe_allow_html=True)
        for cls,title,key,detail in [
            ("red","🛑 停損天條","CB 跌破 100 元","保本天條不妥協，沒有例外。跌破即離場。"),
            ("gold","💰 停利策略","目標 152 元以上","留魚尾策略：分批出場，讓剩餘倉位跟跑。"),
            ("","⏰ 時間停損","持有超過 90 天未動","超過 90 天無動能，重新評估或減倉。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div class="ccard-t">{title}</div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>',unsafe_allow_html=True)

    # T3
    with tabs[2]:
        _sec28("產業族群資料庫")
        ca2,cb2=st.columns(2)
        tw=[("🤖 AI伺服器","廣達·緯創·英業達·技嘉"),("🌡️ 散熱","奇鋐·雙鴻·建準"),("⚙️ CoWoS封測","日月光·矽品·力成"),("⚡ 重電/電網","華城·士電·中興電"),("🔬 半導體設備","弘塑·辛耘·漢微科"),("🚢 航運","長榮·陽明·萬海"),("💊 生技新藥","藥華藥·合一·浩鼎"),("🔋 電池/EV","立凱·必翔·台達電")]
        us=[("🧠 AI大模型","NVDA·AMD·MSFT·GOOGL·META"),("⚛️ 量子計算","QBTS·IONQ·RGTI·QUBT"),("🚀 太空/國防","PLTR·RKLB·LUNR"),("🏦 金融科技","SOFI·AFRM·UPST·SQ"),("☁️ Cloud SaaS","SNOW·DDOG·CRWD·MDB"),("🌿 Clean Energy","ENPH·FSLR·PLUG")]
        etfs=[("🇺🇸 美股核心","SPY·QQQ·VTI·IVV"),("🇹🇼 台股核心","0050.TW·006208.TW·00878.TW")]
        with ca2:
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:rgba(0,245,255,.6);letter-spacing:2px;margin-bottom:8px;">🇹🇼 台股族群</div>',unsafe_allow_html=True)
            for n,s in tw: st.markdown(f'<div class="srow"><div class="srow-name">{n}</div><div class="srow-stk">{s}</div></div>',unsafe_allow_html=True)
        with cb2:
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:rgba(255,154,60,.6);letter-spacing:2px;margin-bottom:8px;">🇺🇸 美股族群</div>',unsafe_allow_html=True)
            for n,s in us: st.markdown(f'<div class="srow"><div class="srow-name">{n}</div><div class="srow-stk">{s}</div></div>',unsafe_allow_html=True)
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:16px;font-weight:700;color:rgba(183,125,255,.6);letter-spacing:2px;margin:10px 0 8px;">📦 核心 ETF</div>',unsafe_allow_html=True)
            for n,s in etfs: st.markdown(f'<div class="srow"><div class="srow-name">{n}</div><div class="srow-stk">{s}</div></div>',unsafe_allow_html=True)

    # T4
    with tabs[3]:
        _sec28("交易心法 Mindset OS")
        for i,(title,desc) in enumerate([
            ("賣出是種藝術","目標區間到達後分批出場，留魚尾策略。永遠不要賣在最頂，讓利潤奔跑。"),
            ("跌破100是天條","不管故事多美，CB跌破100元立刻離場。保住本金才有下一仗。"),
            ("族群共振才是主力","2~3檔同族群CB同步上攻，才是真正主力進場訊號。"),
            ("87MA是生命線","站上87MA且均線向上才安全。跌破=第一警戒，284MA跌破=大逃殺。"),
            ("溢價率的陷阱","溢價率 > 20% 上漲空間有限。選低溢價（5~15%）彈性最大。"),
            ("籌碼鬆動就跑","已轉換比例超過30%，股東結構改變，籌碼不乾淨立刻警惕。"),
            ("尾盤定勝負","13:25後最後25分鐘是多空最誠實表態。收盤站穩才是真突破。"),
            ("消息面最後出現","基本面+技術面打底，消息面是確認彈，不是買入理由。"),
            ("停損是最高策略","每次停損是自我保護。不怕停損，怕的是一次大虧抹掉所有獲利。"),
            ("複利思維操盤","月報酬5%，一年79.6%。急著翻倍的人，最快的路是歸零。"),
        ],1):
            st.markdown(f'<div style="display:flex;align-items:flex-start;gap:14px;padding:14px 16px;background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.04);border-radius:10px;margin-bottom:8px;"><div style="font-family:\'Orbitron\',sans-serif;font-size:30px;font-weight:900;color:rgba(255,215,0,.1);min-width:44px;line-height:1;">{i:02d}</div><div><div style="font-family:\'Rajdhani\',sans-serif;font-size:16px;font-weight:700;color:#FFF;margin-bottom:3px;">{title}</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:rgba(160,176,208,.44);line-height:1.7;">{desc}</div></div></div>',unsafe_allow_html=True)

    # T5: CBAS
    with tabs[4]:
        _sec28("CBAS 槓桿試算引擎")
        ca3,cb3=st.columns(2)
        with ca3:
            cb_price=st.number_input("CB 市價 (元)",min_value=100.0,max_value=200.0,value=108.0,step=0.5,key="cb5_price")
            lot=st.number_input("張數 (手)",min_value=1,max_value=500,value=1,step=1,key="cb5_lot")
        with cb3:
            conv_px=st.number_input("轉換價 (元)",min_value=1.0,max_value=2000.0,value=50.0,step=0.5,key="cb5_conv")
            stk_px=st.number_input("正股現價 (元)",min_value=0.01,max_value=2000.0,value=45.0,step=0.5,key="cb5_stk")
        if cb_price>100:
            prem_cost=cb_price-100; leverage=cb_price/prem_cost if prem_cost>0 else 0
            total_inv=cb_price*lot*1000; conv_prem_pct=(stk_px-conv_px)/conv_px*100 if conv_px>0 else 0
            conv_ratio=100000/conv_px if conv_px>0 else 0
            lev_c="#00FF7F" if leverage>=5 else ("#FFD700" if leverage>=3 else "#FF6B6B")
            conv_c="#00FF7F" if conv_prem_pct<-5 else ("#FFD700" if abs(conv_prem_pct)<5 else "#FF3131")
            st.markdown(f'<div class="calc-scr"><div style="display:flex;justify-content:space-around;align-items:center;flex-wrap:wrap;gap:20px;"><div style="text-align:center;"><div style="font-family:\'Orbitron\',sans-serif;font-size:64px;font-weight:900;color:{lev_c};text-shadow:0 0 30px {lev_c}55;line-height:1;">{leverage:.2f}<span style="font-size:22px;opacity:.4;">×</span></div><div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:rgba(160,176,208,.4);text-transform:uppercase;letter-spacing:3px;margin-top:6px;">IMPLIED LEVERAGE</div></div><div style="height:80px;width:1px;background:rgba(255,255,255,.06);"></div><div><div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:rgba(160,176,208,.3);letter-spacing:2px;margin-bottom:4px;">CB 溢價權利金</div><div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:#FFF;">{prem_cost:.1f} 元</div></div><div style="height:80px;width:1px;background:rgba(255,255,255,.06);"></div><div><div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:rgba(160,176,208,.3);letter-spacing:2px;margin-bottom:4px;">總投資額</div><div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:#FFF;">{total_inv/10000:.1f} 萬</div></div><div style="height:80px;width:1px;background:rgba(255,255,255,.06);"></div><div><div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:rgba(160,176,208,.3);letter-spacing:2px;margin-bottom:4px;">每張換股數</div><div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:#FFF;">{conv_ratio:.0f} 股</div></div></div></div>',unsafe_allow_html=True)
            st.markdown(f'<div style="margin-top:14px;padding:14px 20px;background:rgba(0,0,0,.2);border-left:4px solid {conv_c};border-radius:0 10px 10px 0;"><span style="font-family:\'Rajdhani\',sans-serif;font-size:26px;font-weight:700;color:{conv_c};">{"✅ 正股低於轉換價 — 轉換機率低" if conv_prem_pct<-10 else ("⚠️ 接近轉換價 — 關注轉換訊號" if abs(conv_prem_pct)<5 else "🚀 正股高於轉換價 — 具轉換價值")}</span><span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:rgba(160,176,208,.4);margin-left:12px;">轉換溢價率 {conv_prem_pct:+.1f}%</span></div>',unsafe_allow_html=True)
            st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:9px;color:rgba(160,176,208,.25);letter-spacing:2px;text-transform:uppercase;margin:14px 0 8px;">QUICK REF: LEVERAGE AT DIFFERENT PRICES</div>',unsafe_allow_html=True)
            refs=st.columns(5)
            for i,p in enumerate([103,105,110,115,120]):
                pm=p-100; lv=p/pm if pm>0 else 0; lc="#00FF7F" if lv>5 else ("#FFD700" if lv>3 else "#FF6B6B")
                refs[i].markdown(f'<div style="text-align:center;padding:10px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.04);border-radius:8px;"><div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:rgba(160,176,208,.35);">CB {p}元</div><div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:{lc};line-height:1.2;">{lv:.1f}×</div></div>',unsafe_allow_html=True)
        else:
            st.warning("CB 市價需高於 100 元才有槓桿效應。")

    # T6: OTC均線
    with tabs[5]:
        _sec28("OTC 神奇均線法則")
        for cls,title,key,detail in [
            ("gold","87MA = 季線生命線","87MA 向上且股價站上","台股OTC核心均線。87MA向上=買進訊號；跌破且均線轉下=出場。CB操作的基礎框架。"),
            ("","284MA = 年線壓力/支撐","284MA 是長期趨勢分界線","284MA 之上=多頭，之下=空頭。87MA穿越284MA向上=黃金交叉；反之=死亡交叉。"),
            ("green","乖離率區間管理","正乖離<25%，負乖離<-25%","CB股價距87MA正乖離超過25%=過熱警示；負乖離超過25%=超跌反彈點。"),
            ("red","格蘭碧6大訊號","G1突破買·G2假跌買·G3回測買 | G4跌破賣·G5假突賣·G6反壓賣","買點(G1~G3)配合均線方向；賣點(G4~G6)配合背離與放量。"),
            ("","扣抵原理","284MA的扣抵天數=284天前的收盤價","284天前的價格偏低，今日284MA容易上揚（利多）；偏高則容易下壓（利空）。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div class="ccard-t">{title}</div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>',unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# MAIN ENTRY
# ════════════════════════════════════════════════════════════════════
def render():
    _inject_css()
    symbol=_search()
    _hero(symbol)

    with st.spinner(f"⬡ 鎖定目標: {symbol}…"):
        h1,h3,info,holders,err=_fetch(symbol)

    if err:
        st.error(f"❌ {err}")
        st.info("💡 美股: AAPL · NVDA  |  台股直接輸入: 2330 · 00675L · 5274  |  ETF: SPY · QQQ")
        _nav()
        if st.session_state.get("t5_active")=="5.6": _s56()
        return

    cp_now=info.get("currentPrice") or info.get("regularMarketPrice") or (float(h1["Close"].iloc[-1]) if not h1.empty else 0)
    name=info.get("longName") or info.get("shortName") or symbol
    sector=info.get("sector") or info.get("category") or "—"
    mktcap=info.get("marketCap")
    mktcap_s=(f"${mktcap/1e12:.2f}T" if mktcap and mktcap>1e12 else f"${mktcap/1e9:.1f}B" if mktcap and mktcap>1e9 else "N/A")
    day_chg=info.get("regularMarketChangePercent",0) or 0
    chg_c="#00FF7F" if day_chg>=0 else "#FF3131"
    w52_h=info.get("fiftyTwoWeekHigh",0) or 0; w52_l=info.get("fiftyTwoWeekLow",0) or 0
    w52_pct=(cp_now-w52_l)/(w52_h-w52_l)*100 if (w52_h-w52_l)>0 else 0

    st.markdown(f'<div style="display:flex;align-items:center;gap:20px;padding:14px 20px;background:rgba(255,255,255,.016);border:1px solid rgba(255,255,255,.05);border-radius:14px;margin-bottom:18px;flex-wrap:wrap;"><div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:30px;color:#FFF;letter-spacing:2px;line-height:1;">{symbol}</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(160,176,208,.4);margin-top:2px;">{name}</div></div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:44px;color:#FFF;line-height:1;margin-left:auto;">{cp_now:.2f}</div><div style="font-family:\'Rajdhani\',sans-serif;font-size:20px;font-weight:700;color:{chg_c};">{"▲" if day_chg>=0 else "▼"} {abs(day_chg):.2f}%</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(160,176,208,.32);line-height:1.7;"><div>Sector: {sector}</div><div>Mkt Cap: {mktcap_s}</div><div>52W: {w52_l:.2f}–{w52_h:.2f} ({w52_pct:.0f}%)</div></div></div>',unsafe_allow_html=True)

    _nav()
    active=st.session_state.get("t5_active","5.1")
    st.markdown("<div style='margin-top:6px;'>",unsafe_allow_html=True)
    try:
        if   active=="5.1": _s51(h1,info,symbol)
        elif active=="5.2": _s52(h1,symbol)
        elif active=="5.3": _s53(h1,symbol)
        elif active=="5.4": _s54(h3,info,symbol)
        elif active=="5.5": _s55(holders,info,symbol)
        elif active=="5.6": _s56()
        else:               _s51(h1,info,symbol)
    except Exception as exc:
        st.error(f"❌ Module {active} Error: {exc}")
        with st.expander("🔍 Debug"):
            st.code(traceback.format_exc())
    st.markdown("</div>",unsafe_allow_html=True)

    st.markdown(f'<div class="t5-foot">Titan Universal Market Analyzer V500 · God-Tier · {symbol} · {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',unsafe_allow_html=True)


if __name__=="__main__":
    render()
