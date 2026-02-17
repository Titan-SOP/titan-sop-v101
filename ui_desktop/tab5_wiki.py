# ui_desktop/tab5_wiki.py
# Titan OS V800 — Tab 5: 通用市場分析儀 (Universal Market Analyzer)
# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  V800: Niche Market Fusion Edition                                       ║
# ║  5.1 籌碼+CMF+當沖雷達  5.2 Squeeze+營收噴射  5.3 ATR詳解 (Preserved)  ║
# ║  5.4 艾蜜莉+PE河流圖+掃雷  5.5 ETF戰情室 (Replaces 13F)  5.6 Codex     ║
# ║  Architecture: First Principles · Dual Engine · Mine Sweeper            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
import yfinance as yf
import requests
import re as _re
from datetime import datetime, timedelta
import traceback
import time


# ══════════════════════════════════════════════════════════════════
# 🎯 FEATURE 3: VALKYRIE AI TYPEWRITER
# ══════════════════════════════════════════════════════════════════
def stream_generator(text: str):
    """Valkyrie AI Typewriter — streams text word-by-word for live AI feel."""
    for word in text.split():
        yield word + " "
        time.sleep(0.025)


# ══════════════════════════════════════════════════════════════════
# 🎯 FEATURE 1: TACTICAL GUIDE MODAL
# ══════════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導 Mode — Titan V800")
def show_guide_modal():
    st.markdown("""
### 指揮官，歡迎進入 Titan 市場情報戰區 V800

**6大分析模組（Niche Market Fusion）**：
- 🕵️ **5.1 籌碼K線** — VWAP / OBV / CMF / 當沖雷達 · 主力能量匿藏偵測
- 🚀 **5.2 起漲偵測** — Squeeze Momentum + 營收噴射引擎 · 雙引擎點火
- ⚡ **5.3 權證小哥** — ATR波幅 + 凱利公式 · 最大化風報比（原版保留）
- 🚦 **5.4 艾蜜莉** — PE河流圖 + 掃雷大隊 · 內在價值+財務健康雙保險
- 🛡️ **5.5 ETF戰情室** — 殖利率/費用比/Beta/X光透視 · 取代不穩定13F
- 📜 **5.6 戰略百科** — CB四大套利窗口 · 進出場SOP · CBAS引擎

**操作方式**：點擊上方 6 個板塊切換模組。每個模組均有**第一性原理解析**。

**狀態燈號**：🟢 買入 / 🟡 觀望 / 🔴 警戒 — 隨時留意各模組動能方向。

---
*建議：從 5.1 籌碼K線 入手熟悉介面，ETF分析請使用 5.5 ETF戰情室。*
""")
    if st.button("✅ Roger that，出發！", type="primary", use_container_width=True):
        st.session_state["t5_guide_shown"] = True
        st.rerun()


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
.t5-explain{background:rgba(0,245,255,.03);border:1px solid rgba(0,245,255,.08);border-left:4px solid rgba(0,245,255,.3);border-radius:0 12px 12px 0;padding:18px 22px;margin:14px 0 20px;}
.t5-explain-title{font-family:var(--f-b);font-size:26px;font-weight:700;color:rgba(0,245,255,.9);letter-spacing:1px;margin-bottom:8px;}
.t5-explain-body{font-family:var(--f-b);font-size:18px;color:rgba(200,215,235,.7);line-height:1.7;font-weight:400;}
.t5-explain-key{font-family:var(--f-m);font-size:13px;color:rgba(255,215,0,.6);margin-top:8px;line-height:1.8;}
.ccard{background:rgba(255,255,255,.022);border:1px solid rgba(80,90,110,.22);border-left:4px solid #00F5FF;padding:20px 22px 15px;margin-bottom:12px;border-radius:0 10px 10px 0;position:relative;overflow:hidden;}
.ccard::before{content:'CLASSIFIED';position:absolute;top:8px;right:12px;font-family:var(--f-o);font-size:7px;color:rgba(255,49,49,.14);letter-spacing:4px;}
.ccard.gold{border-left-color:#FFD700;}.ccard.gold::before{content:'PRIORITY';}
.ccard.red{border-left-color:#FF3131;}.ccard.red::before{content:'CRITICAL';}
.ccard.green{border-left-color:#00FF7F;}.ccard.green::before{content:'ACTIVE';}
.ccard-t{font-family:var(--f-b);font-size:20px;font-weight:700;color:#FFF;letter-spacing:1px;margin-bottom:5px;}
.ccard-k{font-family:var(--f-b);font-size:16px;font-weight:600;color:rgba(0,245,255,.8);line-height:1.6;margin-bottom:5px;}
.ccard-d{font-family:var(--f-b);font-size:15px;color:rgba(180,195,220,.65);line-height:1.7;}
.tl-wrap{display:flex;justify-content:center;gap:28px;padding:36px 20px;background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.05);border-radius:20px;margin:14px 0;}
.tl-circle{width:116px;height:116px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;font-family:var(--f-b);font-size:13px;font-weight:700;letter-spacing:.5px;position:relative;}
.tl-circle.dim{opacity:.1;filter:grayscale(.9);}
.tl-circle.active::after{content:'';position:absolute;inset:-8px;border-radius:50%;border:2px solid currentColor;animation:tl-pulse 2s ease-in-out infinite;}
@keyframes tl-pulse{0%,100%{transform:scale(1);opacity:.5;}50%{transform:scale(1.07);opacity:1;}}
.tl-red{background:radial-gradient(circle at 35% 35%,#ff5555,#991111);color:#FFB3B3;}
.tl-yellow{background:radial-gradient(circle at 35% 35%,#FFD700,#9A7A00);color:#FFF3B0;}
.tl-green{background:radial-gradient(circle at 35% 35%,#00FF7F,#006635);color:#B3FFD8;}
/* ETF X-Ray donut label */
.etf-metric{background:rgba(255,255,255,.022);border:1px solid rgba(255,255,255,.06);border-top:2px solid var(--mc,#00F5FF);border-radius:14px;padding:20px 16px;text-align:center;}
.etf-metric-lbl{font-family:var(--f-m);font-size:9px;color:rgba(140,155,178,.48);text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;}
.etf-metric-val{font-family:var(--f-d);font-size:52px;color:#FFF;line-height:.9;}
.etf-metric-sub{font-family:var(--f-b);font-size:12px;color:var(--mc,#00F5FF);font-weight:600;margin-top:5px;}
/* Mine sweeper alert */
.mine-alert{background:rgba(255,49,49,.07);border:1px solid rgba(255,49,49,.35);border-radius:12px;padding:18px 22px;margin:14px 0;}
.mine-safe{background:rgba(0,255,127,.05);border:1px solid rgba(0,255,127,.25);border-radius:12px;padding:18px 22px;margin:14px 0;}
/* Revenue badge */
.rev-badge{display:inline-block;padding:4px 14px;border-radius:20px;font-family:var(--f-m);font-size:10px;letter-spacing:2px;font-weight:700;}
/* Day trade badge */
.dt-badge{display:inline-block;padding:5px 16px;border-radius:20px;font-family:var(--f-m);font-size:11px;letter-spacing:2px;font-weight:700;margin:6px 0;}
.srow{display:flex;align-items:center;gap:12px;padding:9px 14px;background:rgba(255,255,255,.014);border:1px solid rgba(255,255,255,.04);border-radius:8px;margin-bottom:5px;}
.srow-name{font-family:var(--f-b);font-size:14px;font-weight:700;color:rgba(0,245,255,.7);min-width:120px;}
.srow-stk{font-family:var(--f-m);font-size:11px;color:rgba(160,176,208,.46);}
.calc-scr{background:#000;border:2px solid rgba(80,90,110,.32);border-radius:14px;padding:32px 28px;text-align:center;position:relative;overflow:hidden;margin-top:16px;}
.calc-scr::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,245,255,.2),transparent);}
.calc-scr::after{content:'CBAS LEVERAGE ENGINE';position:absolute;top:10px;left:16px;font-family:var(--f-o);font-size:7px;color:rgba(0,245,255,.14);letter-spacing:4px;}
.t5-foot{font-family:var(--f-m);font-size:9px;color:rgba(70,90,110,.2);letter-spacing:2px;text-align:right;margin-top:30px;padding-top:16px;border-top:1px solid rgba(255,255,255,.03);text-transform:uppercase;}
.sec26{font-family:'Rajdhani',sans-serif;font-size:26px;font-weight:700;color:#FFF;letter-spacing:1px;margin:18px 0 6px;}
.sec28{font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:900;color:#FFF;letter-spacing:2px;margin-bottom:4px;}
</style>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# DATA FETCHERS
# ════════════════════════════════════════════════════════════════════
def _is_tw_ticker(symbol: str) -> bool:
    return bool(_re.fullmatch(r'\d{4,6}[A-Z0-9]*', symbol.upper()))


@st.cache_data(ttl=300, show_spinner=False)
def _fetch(symbol: str):
    try:
        sym_upper = symbol.upper()
        if _is_tw_ticker(sym_upper):
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
            return pd.DataFrame(), pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame(), \
                   f"查無數據 '{symbol}'。請確認代號是否正確。"
        for h in [h1, h3]:
            if hasattr(h.index, "tz") and h.index.tz is not None:
                h.index = h.index.tz_localize(None)
        info = tk.info or {}
        # Also try to get top_holdings for ETF X-Ray
        try:
            inst_holders = tk.institutional_holders
            if inst_holders is None: inst_holders = pd.DataFrame()
        except Exception:
            inst_holders = pd.DataFrame()
        try:
            mf_holders = tk.mutualfund_holders
            if mf_holders is None: mf_holders = pd.DataFrame()
        except Exception:
            mf_holders = pd.DataFrame()
        return h1, h3, info, inst_holders, mf_holders, None
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame(), str(e)


# ════════════════════════════════════════════════════════════════════
# HERO + SEARCH
# ════════════════════════════════════════════════════════════════════
def _hero(symbol: str):
    st.markdown(f"""
<div class="t5-hero">
  <div class="t5-hero-label">titan os v800 · niche market fusion · universal market analyzer</div>
  <div class="t5-hero-title">MARKET INTEL HUB</div>
  <div class="t5-hero-sub">US · TW · ETF — TARGET: <span style="color:#00F5FF;opacity:.9;">{symbol}</span></div>
</div>""", unsafe_allow_html=True)


def _search() -> str:
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:rgba(0,245,255,.28);letter-spacing:3px;text-transform:uppercase;margin-bottom:6px;">⬡ TARGET ACQUISITION</div>', unsafe_allow_html=True)
    ca, cb, cc = st.columns([3, 1, 4])
    with ca:
        sym = st.text_input("Symbol", value=st.session_state.get("t5_symbol", "SPY"),
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
# NAV RAIL — V800: 5.5 = ETF Command (replaces 13F)
# ════════════════════════════════════════════════════════════════════
_NAV = [
    ("5.1", "🕵️", "籌碼K線",  "Chip+DayTrade",  "#00F5FF"),
    ("5.2", "🚀", "起漲K線",  "Squeeze+Rev",    "#00FF7F"),
    ("5.3", "⚡", "權證小哥", "Tick Master",    "#FFD700"),
    ("5.4", "🚦", "艾蜜莉",  "Value+River",    "#FF9A3C"),
    ("5.5", "🛡️", "ETF戰情室","ETF Command",   "#B77DFF"),
    ("5.6", "📜", "戰略百科", "The Codex",     "#FF3131"),
]


def _nav():
    if "t5_active" not in st.session_state:
        st.session_state.t5_active = "5.1"
    active = st.session_state.t5_active
    st.markdown('<div class="t5-nav-rail"><div class="t5-nav-lbl">⬡ ANALYSIS MODULES — CLICK TO SELECT</div>', unsafe_allow_html=True)
    cols = st.columns(6)
    for col, (sid, icon, title, sub, accent) in zip(cols, _NAV):
        is_a = (active == sid)
        brd  = f"2px solid {accent}" if is_a else "1px solid rgba(255,255,255,.06)"
        bg   = "rgba(0,0,0,.2)"      if is_a else "rgba(255,255,255,.015)"
        glow = f"0 0 22px {accent}28,0 4px 18px rgba(0,0,0,.5)" if is_a else "0 2px 10px rgba(0,0,0,.4)"
        lc   = accent if is_a else "rgba(200,215,230,.68)"
        tc   = accent if is_a else "rgba(100,120,140,.42)"
        top  = f'<div style="position:absolute;top:0;left:15%;right:15%;height:2px;background:{accent};border-radius:0 0 2px 2px;"></div>' if is_a else ""
        with col:
            st.markdown(f"""
<div style="height:160px;background:{bg};border:{brd};border-radius:14px;
    display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;
    box-shadow:{glow};overflow:hidden;position:relative;">
  {top}
  <div style="font-size:26px;line-height:1;filter:drop-shadow(0 0 6px {accent}44);">{icon}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:28px;font-weight:700;color:{lc};text-align:center;padding:0 4px;letter-spacing:.3px;line-height:1.1;">{title}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:26px;color:{tc};letter-spacing:1px;text-transform:uppercase;line-height:1.1;">{sub}</div>
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
  <div style="font-family:'Rajdhani',sans-serif;font-size:26px;font-weight:700;color:{color};">
    {icon} {msg_big}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:{color}88;margin-top:4px;">
    {msg_small}</div>
</div>""", unsafe_allow_html=True)


def _explain(title, body, keys="", color="#00F5FF"):
    key_html = f'<div class="t5-explain-key">{keys}</div>' if keys else ""
    st.markdown(f"""
<div class="t5-explain" style="border-left-color:{color}44;background:rgba(0,0,0,.2);">
  <div class="t5-explain-title" style="color:{color};">▸ {title}</div>
  <div class="t5-explain-body">""", unsafe_allow_html=True)
    st.write_stream(stream_generator(body))
    st.markdown(f"""</div>
  {key_html}
</div>""", unsafe_allow_html=True)


def _sec28(text, color="#FFF"):
    st.markdown(f'<div class="sec28" style="color:{color};">{text}</div>', unsafe_allow_html=True)


def _sec26(text, color="rgba(160,176,208,.55)"):
    st.markdown(f'<div class="sec26" style="color:{color};">{text}</div>', unsafe_allow_html=True)


def _prep(hist: pd.DataFrame) -> pd.DataFrame:
    df = hist.copy().reset_index()
    for c in df.columns:
        if str(c).lower() in ["date", "datetime", "index"]:
            df.rename(columns={c: "Date"}, inplace=True)
            break
    if "Date" not in df.columns:
        df["Date"] = df.index
    df["Date"] = pd.to_datetime(df["Date"])
    return df


# ════════════════════════════════════════════════════════════════════
# 5.1  籌碼K線 + Day Trade Radar + Hidden Energy (CMF Fusion)
# First Principle: Volume confirms Price. Turnover indicates Speculation.
# ════════════════════════════════════════════════════════════════════
def render_5_1_chips_daytrade(ticker: str, df: pd.DataFrame, info: dict):
    """
    Fusion: Smart Money Chip Analysis + Day Trade Radar + CMF Hidden Energy.
    Public-facing function name per spec.
    """
    _hd("5.1", "🕵️ 籌碼透視 + 當沖雷達 (Smart Money + Day Trade)",
        "VWAP · OBV · CMF主力能量匿藏 · 週轉率當沖雷達 · Smart Money Score", "#00F5FF")
    if df.empty:
        st.toast("⚠️ 無歷史數據，請確認代號", icon="⚠️")
        return

    _explain(
        "第一性原理：量能是價格的領先指標",
        "主力在建倉時必然在量能上留下痕跡。CMF（柴氏金錢流量）衡量21天的資金方向：CMF>0且價格橫盤或上漲，"
        "代表主力正在默默吃貨（主力能量匿藏）。週轉率=成交量÷流通股數，若單日超過10%（台股）或3%（美股大型股），"
        "代表短線當沖客大量介入，浮額燙手，需提高警覺。VWAP是機構執行的基準線，"
        "OBV斜率向上代表資金淨流入，是籌碼最直白的語言。",
        "▸ CMF>0 + 股價橫盤 = 主力吃貨 ▸ 週轉率>10% TW or >3% US = ⚠️當沖過熱  ▸ OBV斜率↑ + VWAP站上 = 多頭佈局"
    )

    hist_df = _prep(df)
    hist_df["TP"]     = (hist_df["High"] + hist_df["Low"] + hist_df["Close"]) / 3
    hist_df["VWAP"]   = (hist_df["TP"] * hist_df["Volume"]).rolling(20).sum() / hist_df["Volume"].rolling(20).sum()
    hist_df["VWAP50"] = (hist_df["TP"] * hist_df["Volume"]).rolling(50).sum() / hist_df["Volume"].rolling(50).sum()

    # OBV
    obv = [0]
    for i in range(1, len(hist_df)):
        v = hist_df["Volume"].iloc[i]
        obv.append(obv[-1] + v if hist_df["Close"].iloc[i] > hist_df["Close"].iloc[i-1]
                   else obv[-1] - v if hist_df["Close"].iloc[i] < hist_df["Close"].iloc[i-1]
                   else obv[-1])
    hist_df["OBV"]    = obv
    hist_df["OBV_MA"] = hist_df["OBV"].rolling(20).mean()

    # CMF (Chaikin Money Flow, 21-day) — Hidden Energy Proxy
    hist_df["MFM"] = ((hist_df["Close"] - hist_df["Low"]) - (hist_df["High"] - hist_df["Close"])) / \
                     (hist_df["High"] - hist_df["Low"]).replace(0, np.nan)
    hist_df["MFV"] = hist_df["MFM"] * hist_df["Volume"]
    hist_df["CMF"] = hist_df["MFV"].rolling(21).sum() / hist_df["Volume"].rolling(21).sum()

    # RSI 14
    delta = hist_df["Close"].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / (loss.replace(0, np.nan))
    hist_df["RSI"] = 100 - 100 / (1 + rs)

    # ── Day Trade Radar: Turnover Rate ──────────────────────────────
    shares_outstanding = info.get("sharesOutstanding") or info.get("impliedSharesOutstanding")
    is_tw = _is_tw_ticker(ticker.replace(".TW", "").replace(".TWO", ""))
    turnover_threshold = 10.0 if is_tw else 3.0  # TW=10%, US large cap=3%

    latest_vol = float(hist_df["Volume"].iloc[-1]) if not hist_df["Volume"].empty else 0
    turnover_rate = None
    if shares_outstanding and shares_outstanding > 0 and latest_vol > 0:
        turnover_rate = (latest_vol / shares_outstanding) * 100

    # ── Key metrics ─────────────────────────────────────────────────
    cp     = float(hist_df["Close"].iloc[-1])
    vwap   = float(hist_df["VWAP"].iloc[-1])  if not pd.isna(hist_df["VWAP"].iloc[-1])  else cp
    v50    = float(hist_df["VWAP50"].iloc[-1]) if not pd.isna(hist_df["VWAP50"].iloc[-1]) else cp
    obv_c  = float(hist_df["OBV"].iloc[-1])
    obv_p  = float(hist_df["OBV"].iloc[-21]) if len(hist_df) > 21 else float(hist_df["OBV"].iloc[0])
    cmf_v  = float(hist_df["CMF"].iloc[-1])  if not pd.isna(hist_df["CMF"].iloc[-1])  else 0
    rsi_v  = float(hist_df["RSI"].iloc[-1])  if not pd.isna(hist_df["RSI"].iloc[-1])  else 50
    vwap_dev = (cp - vwap) / vwap * 100 if vwap > 0 else 0
    obv_up   = obv_c > obv_p

    # Smart Money Score
    score = 50
    score += min(20, vwap_dev * 2) if vwap_dev > 0 else max(-20, vwap_dev * 2)
    score += 15 if obv_up else -15
    score += 15 if cmf_v > 0.05 else (0 if cmf_v > -0.05 else -15)
    score = int(max(0, min(100, score)))
    sc     = "#00FF7F" if score >= 60 else ("#FFD700" if score >= 40 else "#FF3131")
    rsi_c  = "#FF3131" if rsi_v > 70 else ("#00FF7F" if rsi_v < 30 else "#FFD700")
    cmf_c  = "#00FF7F" if cmf_v > 0.05 else ("#FF3131" if cmf_v < -0.05 else "#888")

    # Turnover rate display
    tr_str   = f"{turnover_rate:.2f}%" if turnover_rate is not None else "N/A"
    tr_color = ("#FF3131" if turnover_rate and turnover_rate > turnover_threshold
                else "#FFD700" if turnover_rate and turnover_rate > turnover_threshold * 0.6
                else "#00FF7F")

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    _kpi(c1, "股價",        f"{cp:.2f}",        "",                "#00F5FF")
    _kpi(c2, "VWAP 20日",  f"{vwap:.2f}",      f"偏離 {vwap_dev:+.1f}%", "#00FF7F" if cp > vwap else "#FF3131")
    _kpi(c3, "VWAP 50日",  f"{v50:.2f}",       f"{'上方✓' if cp>v50 else '下方✗'}", "#00FF7F" if cp > v50 else "#FF6060")
    _kpi(c4, "OBV方向",    "累積▲" if obv_up else "派發▼", "Smart Money", "#00FF7F" if obv_up else "#FF3131")
    _kpi(c5, "CMF(21)",    f"{cmf_v:+.3f}",    ">+0.1=強買盤",    cmf_c)
    _kpi(c6, "週轉率",     tr_str,             f"閾值>{turnover_threshold:.0f}%", tr_color)
    _kpi(c7, "籌碼評分",   f"{score}",         "0弱→100強",       sc)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Hidden Energy Signal (CMF Accumulation) ──────────────────────
    price_flat_or_up = (hist_df["Close"].iloc[-5:].pct_change().sum() if len(hist_df) >= 5 else 0) >= -0.02
    if cmf_v > 0 and price_flat_or_up:
        st.markdown("""
<div style="display:inline-block;padding:7px 18px;background:rgba(0,245,255,.07);border:1px solid rgba(0,245,255,.3);
  border-radius:20px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#00F5FF;letter-spacing:2px;margin-bottom:10px;">
  🔍 主力能量匿藏 (ACCUMULATION) — CMF>0 · 價格橫盤/上漲 = 法人悄悄吃貨
</div>""", unsafe_allow_html=True)

    # ── Day Trade Radar Badge ─────────────────────────────────────────
    if turnover_rate is not None and turnover_rate > turnover_threshold:
        st.markdown(f"""
<div style="display:inline-block;padding:7px 18px;background:rgba(255,49,49,.08);border:1px solid rgba(255,49,49,.35);
  border-radius:20px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#FF6B6B;letter-spacing:2px;margin-bottom:10px;">
  ⚠️ 當沖過熱 (OVERHEATED) — 週轉率 {turnover_rate:.2f}% &gt; {turnover_threshold:.0f}% 閾值 · 浮額燙手注意
</div>""", unsafe_allow_html=True)

    # Banners
    if score >= 60:    _banner("🟢 法人多頭佈局 ACCUMULATION",   f"VWAP偏離{vwap_dev:+.1f}% · OBV上升 · CMF{cmf_v:+.3f} · Score {score}/100", "#00FF7F")
    elif score >= 40:  _banner("🟡 法人觀望 NEUTRAL",            f"籌碼混沌，VWAP偏離 {vwap_dev:+.1f}% · CMF{cmf_v:+.3f}", "#FFD700")
    else:              _banner("🔴 法人賣壓 DISTRIBUTION",       f"VWAP偏離{vwap_dev:+.1f}% · OBV下降 · CMF{cmf_v:+.3f} · Score {score}/100", "#FF3131")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Charts ──────────────────────────────────────────────────────
    _sec28("PRICE × VWAP OVERLAY")
    _sec26("青色=收盤價 · 金色=VWAP20 · 橙色=VWAP50 — 站在均線上方代表法人買入成本在下方", "rgba(160,176,208,.45)")
    tail = 120
    dp = hist_df[["Date", "Close", "VWAP", "VWAP50"]].dropna().tail(tail)
    dm = dp.melt("Date", var_name="Series", value_name="Price")
    ch = alt.Chart(dm).mark_line(strokeWidth=1.8).encode(
        x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
        y=alt.Y("Price:Q", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
        color=alt.Color("Series:N",
                        scale=alt.Scale(domain=["Close", "VWAP", "VWAP50"],
                                        range=["#00F5FF", "#FFD700", "#FF9A3C"]),
                        legend=alt.Legend(labelColor="#aaa", titleColor="#aaa", orient="top-right"))
    ).properties(background="transparent", height=260).configure_view(strokeOpacity=0)
    st.altair_chart(ch, use_container_width=True)

    col_obv, col_cmf = st.columns(2)
    with col_obv:
        _sec28("ON-BALANCE VOLUME")
        _sec26("紫=OBV · 橙=均線 · 斜率向上=法人持續買進", "rgba(160,176,208,.45)")
        do = hist_df[["Date", "OBV", "OBV_MA"]].dropna().tail(tail)
        dom = do.melt("Date", var_name="Series", value_name="Value")
        ch2 = alt.Chart(dom).mark_line(strokeWidth=1.6).encode(
            x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
            y=alt.Y("Value:Q", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
            color=alt.Color("Series:N",
                            scale=alt.Scale(domain=["OBV", "OBV_MA"], range=["#B77DFF", "#FF9A3C"]),
                            legend=alt.Legend(labelColor="#aaa", titleColor="#aaa", orient="top-right"))
        ).properties(background="transparent", height=200).configure_view(strokeOpacity=0)
        st.altair_chart(ch2, use_container_width=True)

    with col_cmf:
        _sec28("CMF 主力能量匿藏 + RSI")
        _sec26("CMF>0=資金流入(買盤主導) · 平盤時CMF>0=主力暗中吃貨", "rgba(160,176,208,.45)")
        dr = hist_df[["Date", "RSI", "CMF"]].dropna().tail(tail)
        cmf_chart = alt.Chart(dr).mark_line(color="#00F5FF", strokeWidth=1.8).encode(
            x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
            y=alt.Y("CMF:Q", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a", title="CMF"))
        )
        # CMF area fill for positive/negative
        cmf_area_pos = alt.Chart(dr).mark_area(opacity=0.15, color="#00FF7F").encode(
            x="Date:T",
            y=alt.Y("CMF:Q", impute=alt.ImputeParams(value=0)),
            y2=alt.value(0)
        ).transform_filter(alt.datum.CMF > 0)
        cmf_area_neg = alt.Chart(dr).mark_area(opacity=0.15, color="#FF3131").encode(
            x="Date:T",
            y=alt.Y("CMF:Q"),
            y2=alt.value(0)
        ).transform_filter(alt.datum.CMF < 0)
        zero = alt.Chart(pd.DataFrame({"y": [0]})).mark_rule(strokeDash=[3, 3], color="#555", strokeWidth=1).encode(y="y:Q")
        st.altair_chart(
            alt.layer(cmf_area_pos, cmf_area_neg, cmf_chart, zero)
            .properties(background="transparent", height=180).configure_view(strokeOpacity=0),
            use_container_width=True
        )

    # Volume Profile
    _sec28("VOLUME PROFILE (90D) + 週轉率雷達")
    _sec26("綠柱=收漲 · 紅柱=收跌 · 金線=20日均量 · 橙色=當沖過熱閾值", "rgba(160,176,208,.45)")
    dv = hist_df[["Date", "Volume", "Close"]].tail(90).copy()
    dv["AvgVol"] = dv["Volume"].rolling(20).mean()
    dv["clr"] = dv["Close"].diff().apply(lambda x: "#00FF7F" if x >= 0 else "#FF6060")
    cv = alt.Chart(dv).mark_bar(opacity=0.75, cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
        x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
        y=alt.Y("Volume:Q", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
        color=alt.Color("clr:N", scale=None, legend=None)
    )
    ca2 = alt.Chart(dv).mark_line(color="#FFD700", strokeWidth=1.4, strokeDash=[4, 4]).encode(
        x="Date:T", y="AvgVol:Q"
    )
    st.altair_chart(
        (cv + ca2).properties(background="transparent", height=180).configure_view(strokeOpacity=0),
        use_container_width=True
    )


# Keep internal alias
def _s51(hist, info, symbol):
    render_5_1_chips_daytrade(symbol, hist, info)


# ════════════════════════════════════════════════════════════════════
# 5.2  起漲K線 + Revenue Growth Fusion (Dual Ignition Engine)
# First Principle: Explosive moves need Stored Energy (Tech) + Fuel (Fundamental)
# ════════════════════════════════════════════════════════════════════
def render_5_2_breakout_revenue(ticker: str, df: pd.DataFrame, info: dict):
    """
    Fusion: BB/KC Squeeze Momentum + Revenue Growth Dual Ignition Engine.
    Public-facing function name per spec.
    """
    _hd("5.2", "🚀 動能突破 + 營收噴射引擎 (Dual Ignition)",
        "BB Squeeze · Keltner · MACD · 營收成長 · 雙引擎點火條件", "#00FF7F")
    if df.empty:
        st.toast("⚠️ 無歷史數據，請確認代號", icon="⚠️")
        return

    _explain(
        "第一性原理：雙引擎點火 — 技術蓄能 × 基本面燃料",
        "技術面的布林帶擠壓（Squeeze）代表市場能量壓縮，像彈簧被緊壓。"
        "基本面的營收爆發（Revenue Surge）代表公司有實質業績支撐，是真實的燃料。"
        "當兩者同時出現：技術面擠壓尚未釋放 + 營收成長>20%（YoY），"
        "形成「雙引擎點火」——這是最強的突破候選訊號，爆發力遠超單純技術突破。"
        "MACD確認中期動能方向，確保不逆勢而為。",
        "▸ BW<12% + MOM↑ = 技術蓄能完成  ▸ RevenueGrowth>20% = 🔥營收爆發  ▸ 兩者同時 = ⭐⭐ 雙引擎噴出",
        "#00FF7F"
    )

    # ── Revenue Growth Fetch ──────────────────────────────────────────
    rev_growth = info.get("revenueGrowth")  # YoY decimal, e.g. 0.22 = 22%
    rev_growth_pct = rev_growth * 100 if rev_growth is not None else None

    hist_df = _prep(df)
    hist_df["BB_mid"] = hist_df["Close"].rolling(20).mean()
    hist_df["BB_std"] = hist_df["Close"].rolling(20).std()
    hist_df["BB_up"]  = hist_df["BB_mid"] + 2 * hist_df["BB_std"]
    hist_df["BB_dn"]  = hist_df["BB_mid"] - 2 * hist_df["BB_std"]
    hist_df["BW"]     = (hist_df["BB_up"] - hist_df["BB_dn"]) / hist_df["BB_mid"] * 100
    hist_df["TR"]     = np.maximum(
        hist_df["High"] - hist_df["Low"],
        np.maximum(abs(hist_df["High"] - hist_df["Close"].shift(1)),
                   abs(hist_df["Low"]  - hist_df["Close"].shift(1)))
    )
    hist_df["ATR14"]   = hist_df["TR"].rolling(14).mean()
    hist_df["KC_up"]   = hist_df["BB_mid"] + 1.5 * hist_df["ATR14"]
    hist_df["KC_dn"]   = hist_df["BB_mid"] - 1.5 * hist_df["ATR14"]
    hist_df["Squeeze"] = (hist_df["BB_up"] < hist_df["KC_up"]) & (hist_df["BB_dn"] > hist_df["KC_dn"])
    hist_df["MOM"]     = hist_df["Close"] - (
        (hist_df["High"].rolling(20).max() + hist_df["Low"].rolling(20).min()) / 2
        + hist_df["BB_mid"]
    ) / 2

    # MACD
    ema12 = hist_df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = hist_df["Close"].ewm(span=26, adjust=False).mean()
    hist_df["MACD"]   = ema12 - ema26
    hist_df["Signal"] = hist_df["MACD"].ewm(span=9, adjust=False).mean()
    hist_df["Hist"]   = hist_df["MACD"] - hist_df["Signal"]

    bw_now  = float(hist_df["BW"].iloc[-1])  if not hist_df["BW"].isna().all()      else None
    sq_now  = bool(hist_df["Squeeze"].iloc[-1]) if not hist_df["Squeeze"].isna().all() else False
    mom_now = float(hist_df["MOM"].iloc[-1]) if not hist_df["MOM"].isna().all()     else 0
    sq_days = int(hist_df["Squeeze"].tail(30).sum()) if not hist_df["Squeeze"].isna().all() else 0
    hist_n  = float(hist_df["Hist"].iloc[-1]) if not hist_df["Hist"].isna().all()   else 0
    cp      = float(hist_df["Close"].iloc[-1])

    # ── Revenue Badge ──────────────────────────────────────────────
    rev_surge  = rev_growth_pct is not None and rev_growth_pct > 20
    rev_color  = "#FF9A3C" if rev_surge else ("#FFD700" if rev_growth_pct and rev_growth_pct > 0 else "#888")
    rev_label  = (f"🔥 +{rev_growth_pct:.1f}%" if rev_surge
                  else f"+{rev_growth_pct:.1f}%" if rev_growth_pct and rev_growth_pct > 0
                  else f"{rev_growth_pct:.1f}%" if rev_growth_pct is not None
                  else "N/A")

    # ── Dual Ignition condition ────────────────────────────────────
    dual_ignition = sq_now and mom_now > 0 and rev_surge

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    _kpi(c1, "股價",      f"{cp:.2f}",             "",                                          "#00F5FF")
    _kpi(c2, "帶寬 BW%",  f"{bw_now:.1f}%" if bw_now else "N/A",  "<12%=蓄勢完成",             "#00FF7F" if bw_now and bw_now < 12 else "#FFD700")
    _kpi(c3, "Squeeze",   "🔥擠壓中" if sq_now else "⬜無擠壓",   f"連續{sq_days}日",           "#00FF7F" if sq_now else "#888")
    _kpi(c4, "動能方向",  "▲ 多頭" if mom_now > 0 else "▼ 空頭", f"MOM {mom_now:+.2f}",       "#00FF7F" if mom_now > 0 else "#FF3131")
    _kpi(c5, "營收成長",  rev_label,                               "YoY Revenue Growth",         rev_color)
    _kpi(c6, "MACD柱",   "▲ 擴大" if hist_n > 0 else "▼ 收縮",  f"Hist {hist_n:+.4f}",        "#00FF7F" if hist_n > 0 else "#FF3131")
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Revenue Surge Badge
    if rev_surge:
        st.markdown(f"""
<div style="display:inline-block;padding:7px 18px;background:rgba(255,154,60,.1);border:1px solid rgba(255,154,60,.4);
  border-radius:20px;font-family:'JetBrains Mono',monospace;font-size:11px;color:#FF9A3C;letter-spacing:2px;margin-bottom:10px;">
  🔥 營收爆發 (Rev Surge) — YoY {rev_growth_pct:.1f}% &gt; 20% 閾值 · 基本面燃料充足
</div>""", unsafe_allow_html=True)

    # Dual Ignition Badge
    if dual_ignition:
        st.markdown("""
<div style="display:inline-block;padding:9px 22px;background:rgba(0,255,127,.1);border:2px solid rgba(0,255,127,.5);
  border-radius:20px;font-family:'JetBrains Mono',monospace;font-size:12px;color:#00FF7F;
  letter-spacing:2px;margin-bottom:10px;box-shadow:0 0 20px rgba(0,255,127,.15);">
  ⭐⭐ 雙引擎噴出 (DUAL IGNITION) — 技術擠壓 × 營收爆發 同時觸發 · 最強突破候選
</div>""", unsafe_allow_html=True)

    # Main banners
    if dual_ignition:
        _banner("⭐⭐ 雙引擎噴出 — 技術+基本面共振",
                f"BB Squeeze · MOM向上 · 連擠{sq_days}日 · 營收成長{rev_growth_pct:.1f}%", "#00FF7F", "🚀")
    elif sq_now and mom_now > 0:
        _banner("🔥 蓄勢待發 — 多頭爆發",
                f"BB inside KC · BW={bw_now:.1f}% · 連擠{sq_days}日 · 動能向上", "#00FF7F", "🚀")
    elif sq_now and mom_now < 0:
        _banner("⚠️ 擠壓出現 — 空頭方向",
                f"BB inside KC · BW={bw_now:.1f}% · 動能向下 · 謹慎", "#FF9A3C", "⚠️")
    elif bw_now and bw_now < 12:
        _banner("🟡 帶寬收窄 — 等待KC確認",
                f"BW={bw_now:.1f}% · 接近歷史低波動，隨時可能爆發", "#FFD700")
    else:
        _banner("⬜ 正常震盪 — 持續監控",
                f"BW={f'{bw_now:.1f}' if bw_now else 'N/A'}% · 無擠壓訊號", "#888")

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # BB × KC Chart
    _sec28("BOLLINGER BANDS × KELTNER CHANNEL + 營收成長")
    _sec26("綠帶=BB · 橙帶=KC · BB縮進KC內部=擠壓 · 青線=收盤價", "rgba(160,176,208,.45)")

    # Revenue annotation on chart
    if rev_growth_pct is not None:
        rev_badge_html = (
            f'<span style="background:rgba(255,154,60,.12);border:1px solid rgba(255,154,60,.4);'
            f'border-radius:10px;padding:2px 10px;font-family:JetBrains Mono,monospace;font-size:11px;'
            f'color:#FF9A3C;margin-left:12px;">Revenue YoY: {rev_growth_pct:+.1f}%</span>'
        )
        st.markdown(
            f'<div style="font-family:Rajdhani,sans-serif;font-size:18px;color:rgba(160,176,208,.5);margin-bottom:8px;">'
            f'基本面快照 {rev_badge_html}</div>',
            unsafe_allow_html=True
        )

    dp = hist_df[["Date", "Close", "BB_up", "BB_dn", "BB_mid", "KC_up", "KC_dn"]].dropna().tail(120)
    base = alt.Chart(dp)
    bands = [
        base.mark_line(color="#00FF7F", strokeWidth=1, opacity=0.5).encode(x="Date:T", y="BB_up:Q"),
        base.mark_line(color="#00FF7F", strokeWidth=1, opacity=0.5).encode(x="Date:T", y="BB_dn:Q"),
        base.mark_line(color="#FF9A3C", strokeWidth=1, strokeDash=[3, 3], opacity=0.5).encode(x="Date:T", y="KC_up:Q"),
        base.mark_line(color="#FF9A3C", strokeWidth=1, strokeDash=[3, 3], opacity=0.5).encode(x="Date:T", y="KC_dn:Q"),
        base.mark_line(color="#00F5FF", strokeWidth=1.8).encode(
            x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
            y=alt.Y("Close:Q", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a"))
        )
    ]
    st.altair_chart(
        alt.layer(*bands).properties(background="transparent", height=250).configure_view(strokeOpacity=0),
        use_container_width=True
    )

    col_mom, col_macd = st.columns(2)
    with col_mom:
        _sec28("MOMENTUM HISTOGRAM")
        _sec26("正值=多頭動能 · 負值=空頭動能", "rgba(160,176,208,.45)")
        dm = hist_df[["Date", "MOM"]].dropna().tail(120).copy()
        dm["clr"] = dm["MOM"].apply(lambda x: "#00FF7F" if x >= 0 else "#FF6060")
        mch = alt.Chart(dm).mark_bar(opacity=0.8).encode(
            x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
            y=alt.Y("MOM:Q", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
            color=alt.Color("clr:N", scale=None, legend=None)
        ).properties(background="transparent", height=180).configure_view(strokeOpacity=0)
        st.altair_chart(mch, use_container_width=True)
    with col_macd:
        _sec28("MACD 動能確認")
        _sec26("MACD柱翻正=動能換手 · 金叉=買進確認", "rgba(160,176,208,.45)")
        dmacd = hist_df[["Date", "MACD", "Signal", "Hist"]].dropna().tail(120).copy()
        dmacd["clr"] = dmacd["Hist"].apply(lambda x: "#00FF7F" if x >= 0 else "#FF6060")
        hist_chart = alt.Chart(dmacd).mark_bar(opacity=0.7).encode(
            x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
            y=alt.Y("Hist:Q", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
            color=alt.Color("clr:N", scale=None, legend=None)
        )
        macd_l = alt.Chart(dmacd).mark_line(color="#00F5FF", strokeWidth=1.2).encode(x="Date:T", y="MACD:Q")
        sig_l  = alt.Chart(dmacd).mark_line(color="#FF9A3C", strokeWidth=1.2, strokeDash=[3, 3]).encode(x="Date:T", y="Signal:Q")
        st.altair_chart(
            alt.layer(hist_chart, macd_l, sig_l).properties(background="transparent", height=180).configure_view(strokeOpacity=0),
            use_container_width=True
        )


def _s52(hist, symbol, info=None):
    render_5_2_breakout_revenue(symbol, hist, info or {})


# ════════════════════════════════════════════════════════════════════
# 5.3  權證小哥  TICK MASTER  (Preserved verbatim)
# First Principle: ATR is the market's breathing rhythm
# ════════════════════════════════════════════════════════════════════
def _s53(hist: pd.DataFrame, symbol: str):
    _hd("5.3", "⚡ 短線操盤儀 (Tactical Trader)",
        "ATR波動 · 相對量能 · 布林通道位置 · 短線趨勢評分", "#FFD700")
    if hist.empty:
        st.toast("⚠️ 無歷史數據，請確認代號", icon="⚠️")
        return

    _explain(
        "第一性原理：短線波動管理",
        "ATR（Average True Range）是行情的「呼吸幅度」。每日ATR代表市場願意移動多少距離。"
        "相對成交量（RelVol）= 今日成交量 ÷ 20日均量，超過2倍代表異常資金進場。"
        "布林帶位置（%B）= (收盤-下軌)÷(上軌-下軌)，>0.8接近上軌=短線超買，<0.2接近下軌=超賣。"
        "短線進場的最佳條件：ATR適中（不過高不過低）+ RelVol放大 + %B從低點回升。",
        "▸ ATR% 1-3% = 最佳短線節奏  ▸ RelVol > 2× = 主力進場訊號  ▸ %B 從0.2上穿0.4 = 轉強",
        "#FFD700"
    )

    df = _prep(hist)
    df["TR"]     = np.maximum(df["High"] - df["Low"],
                               np.maximum(abs(df["High"] - df["Close"].shift(1)),
                                          abs(df["Low"]  - df["Close"].shift(1))))
    df["ATR14"]  = df["TR"].rolling(14).mean()
    df["ATR21"]  = df["TR"].rolling(21).mean()
    df["AvgVol"] = df["Volume"].rolling(20).mean()
    df["RelVol"] = df["Volume"] / df["AvgVol"].replace(0, np.nan)
    df["BB_mid"] = df["Close"].rolling(20).mean()
    df["BB_std"] = df["Close"].rolling(20).std()
    df["BB_up"]  = df["BB_mid"] + 2 * df["BB_std"]
    df["BB_dn"]  = df["BB_mid"] - 2 * df["BB_std"]
    df["PctB"]   = (df["Close"] - df["BB_dn"]) / (df["BB_up"] - df["BB_dn"]).replace(0, np.nan)
    df["R1"]  = df["Close"].pct_change(1)  * 100
    df["R5"]  = df["Close"].pct_change(5)  * 100
    df["R20"] = df["Close"].pct_change(20) * 100

    cp    = float(df["Close"].iloc[-1])
    atr   = float(df["ATR14"].iloc[-1]) if not pd.isna(df["ATR14"].iloc[-1]) else 0
    atr_pct = atr / cp * 100 if cp > 0 else 0
    rv    = float(df["RelVol"].iloc[-1]) if not pd.isna(df["RelVol"].iloc[-1]) else 1
    pctb  = float(df["PctB"].iloc[-1])  if not pd.isna(df["PctB"].iloc[-1])  else 0.5
    r1    = float(df["R1"].iloc[-1])  if not pd.isna(df["R1"].iloc[-1])  else 0
    r5    = float(df["R5"].iloc[-1])  if not pd.isna(df["R5"].iloc[-1])  else 0
    r20   = float(df["R20"].iloc[-1]) if not pd.isna(df["R20"].iloc[-1]) else 0

    rv_color  = "#FF3131" if rv > 3 else ("#FF9A3C" if rv > 2 else ("#FFD700" if rv > 1.5 else "#00FF7F"))
    pctb_c    = "#FF3131" if pctb > 0.8 else ("#00FF7F" if pctb < 0.2 else "#FFD700")

    c1, c2, c3, c4, c5 = st.columns(5)
    _kpi(c1, "股價",       f"{cp:.2f}",          "",              "#00F5FF")
    _kpi(c2, "ATR 14",     f"{atr:.2f}",         f"波動率 {atr_pct:.1f}%", "#FFD700" if atr_pct < 3 else "#FF3131")
    _kpi(c3, "相對量能",   f"{rv:.1f}×",         "1=均量",        "#00FF7F" if 1.5 < rv < 3 else rv_color)
    _kpi(c4, "布林位置 %B", f"{pctb:.2f}",       ">0.8超買 <0.2超賣", pctb_c)
    _kpi(c5, "20日漲跌",   f"{r20:+.1f}%",       "月度動能",      "#00FF7F" if r20 > 0 else "#FF3131")
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if rv > 2 and r1 > 0:   _banner("⚡ 放量上攻 BULLISH BREAKOUT", f"RelVol {rv:.1f}× · 今日+{r1:.1f}% · %B={pctb:.2f}", "#FFD700", "📈")
    elif rv > 2 and r1 < 0: _banner("⚠️ 放量殺跌 BEARISH FLUSH",   f"RelVol {rv:.1f}× · 今日{r1:.1f}% · 注意支撐",        "#FF3131", "📉")
    elif atr_pct < 1:        _banner("💤 超低波動 COMPRESSION",      f"ATR={atr_pct:.1f}% · 市場靜止 · 等待放量突破",       "#888")
    else:                    _banner("📊 正常節奏 NORMAL RANGE",     f"ATR={atr_pct:.1f}% · RelVol={rv:.1f}× · 持續觀察",   "#FFD700")

    _sec28("RELATIVE VOLUME + %B 位置")
    _sec26("橙=RelVol · 青=%B · %B>0.8超買 <0.2超賣", "rgba(160,176,208,.45)")
    tail = 90
    drv   = df[["Date", "RelVol", "PctB"]].dropna().tail(tail)
    rv_c  = alt.Chart(drv).mark_bar(color="#FF9A3C", opacity=0.7).encode(
        x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
        y=alt.Y("RelVol:Q", axis=alt.Axis(labelColor="#FF9A3C", gridColor="#1a1a2a", title="RelVol"))
    )
    pctb_c2 = alt.Chart(drv).mark_line(color="#00F5FF", strokeWidth=1.6).encode(
        x="Date:T",
        y=alt.Y("PctB:Q", axis=alt.Axis(labelColor="#00F5FF", title="%B"), scale=alt.Scale(domain=[0, 1]))
    )
    ob  = alt.Chart(pd.DataFrame({"y": [0.8]})).mark_rule(strokeDash=[3, 3], color="#FF3131",  strokeWidth=1).encode(y=alt.Y("y:Q", axis=None))
    os_ = alt.Chart(pd.DataFrame({"y": [0.2]})).mark_rule(strokeDash=[3, 3], color="#00FF7F", strokeWidth=1).encode(y=alt.Y("y:Q", axis=None))
    st.altair_chart(
        alt.layer(rv_c).resolve_scale(y="independent").properties(background="transparent", height=200).configure_view(strokeOpacity=0),
        use_container_width=True
    )
    st.altair_chart(
        alt.layer(pctb_c2, ob, os_).properties(background="transparent", height=130).configure_view(strokeOpacity=0),
        use_container_width=True
    )

    _sec28("SHORT-TERM RETURNS")
    _sec26("今日/本週/本月漲跌幅 — 三個時間框架判斷短線力道", "rgba(160,176,208,.45)")
    gm = [
        ("ATR波動評級", "🔴 高波動" if atr_pct > 3 else ("🟡 中波動" if atr_pct > 1.5 else "🟢 低波動"), f"每日ATR {atr_pct:.1f}%", "#FFD700"),
        ("量能狀態",  "⚠️ 爆量警戒" if rv > 3 else ("⚡ 量能放大" if rv > 1.5 else "✅ 量能正常"), f"RelVol {rv:.1f}×", rv_color),
        ("今日趨勢",  f"{'▲' if r1 > 0 else '▼'} {abs(r1):.1f}%", "日漲跌", "#00FF7F" if r1 > 0 else "#FF3131"),
        ("週漲跌",    f"{'▲' if r5 > 0 else '▼'} {abs(r5):.1f}%", "5日動能", "#00FF7F" if r5 > 2 else ("#888" if abs(r5) < 2 else "#FF3131")),
    ]
    gc1, gc2, gc3, gc4 = st.columns(4)
    for col, (title, val, sub, c) in zip([gc1, gc2, gc3, gc4], gm):
        col.markdown(
            f'<div style="padding:16px;background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.05);'
            f'border-top:2px solid {c};border-radius:10px;">'
            f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:14px;font-weight:700;color:{c};margin-bottom:5px;">{title}</div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:26px;color:#FFF;line-height:1.1;">{val}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:rgba(160,176,208,.4);margin-top:4px;">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


# ════════════════════════════════════════════════════════════════════
# 5.4  艾蜜莉定存 + PE River Chart + Mine Sweeper
# First Principle: Price reverts to mean. Avoid bankruptcy risks.
# ════════════════════════════════════════════════════════════════════
def render_5_4_value_river(ticker: str, info: dict, hist3y: pd.DataFrame):
    """
    Fusion: Value Traffic Light + PE River Chart (8x/12x/16x/20x) + Mine Sweeper.
    Public-facing function name per spec.
    """
    _hd("5.4", "🚦 價值紅綠燈 + PE河流圖 + 掃雷大隊",
        "PE河流 8×/12×/16×/20× · 財務地雷掃除 · DDM · Graham · 安全邊際", "#FF9A3C")

    _explain(
        "第一性原理：均值回歸 + 財務健康雙重保險",
        "PE河流圖是價值投資最直觀的視覺工具：用歷史EPS乘以不同PE倍數（8x/12x/16x/20x），"
        "畫出四條「價值河岸」。股價落在哪條河道，一眼判斷估值高低。"
        "掃雷大隊檢查兩個最危險的財務地雷：負債股權比>200%代表高槓桿風險，"
        "自由現金流<0代表公司正在燒錢。排雷後的低PE股票，才是真正的安全邊際。",
        "▸ 股價 < PE 8x帶 = 極度低估  ▸ 股價 > PE 20x帶 = 昂貴  ▸ 負債>200% + FCF<0 = 💣 財務地雷",
        "#FF9A3C"
    )

    cp      = info.get("currentPrice") or info.get("regularMarketPrice") or \
              (float(hist3y["Close"].iloc[-1]) if not hist3y.empty else 0)
    eps     = info.get("trailingEps") or info.get("forwardEps")
    pe_trail = info.get("trailingPE")
    pe_fwd   = info.get("forwardPE")
    pb      = info.get("priceToBook")
    ps      = info.get("priceToSalesTrailing12Months")
    div_y   = info.get("dividendYield", 0) or 0
    roe     = info.get("returnOnEquity", 0) or 0
    bvps    = info.get("bookValue", 0) or 0

    # ── Mine Sweeper ──────────────────────────────────────────────────
    debt_to_equity = info.get("debtToEquity")       # 0–100 scale typically
    free_cashflow  = info.get("freeCashflow")        # raw value in currency

    has_debt_mine = debt_to_equity is not None and float(debt_to_equity) > 200
    has_fcf_mine  = free_cashflow is not None  and float(free_cashflow)  < 0

    # ── Historical PE percentiles ─────────────────────────────────────
    pe_25 = pe_50 = pe_75 = hist_pe = None
    if not hist3y.empty and eps and float(eps) > 0:
        pe_ser = (hist3y["Close"] / float(eps)).replace([np.inf, -np.inf], np.nan).dropna()
        pe_ser = pe_ser[pe_ser > 0]
        if len(pe_ser) > 20:
            pe_25 = float(np.percentile(pe_ser, 25))
            pe_50 = float(np.percentile(pe_ser, 50))
            pe_75 = float(np.percentile(pe_ser, 75))
            hist_pe = float(pe_ser.iloc[-1])

    use_pe = hist_pe or pe_trail or pe_fwd
    if use_pe and pe_25 and pe_75:
        signal = "cheap" if use_pe < pe_25 else ("expensive" if use_pe > pe_75 else "fair")
    elif use_pe:
        signal = "cheap" if use_pe < 15 else ("expensive" if use_pe > 35 else "fair")
    else:
        signal = "neutral"

    # DDM
    ddm_val = None
    if div_y > 0 and cp > 0:
        D = cp * div_y
        g = min(roe * 0.5, 0.08) if roe > 0 else 0.03
        r = 0.10
        if r > g:
            ddm_val = D / (r - g)

    # Graham
    graham_val = None
    if eps and float(eps) > 0 and bvps > 0:
        graham_val = float(np.sqrt(22.5 * float(eps) * bvps))

    sm = {
        "cheap":    ("🟢 便宜 CHEAP",    "#00FF7F", "建議逢低佈局"),
        "fair":     ("🟡 合理 FAIR",     "#FFD700", "持有觀望"),
        "expensive":("🔴 昂貴 EXPENSIVE","#FF3131", "謹慎操作"),
        "neutral":  ("⬜ 無PE數據",      "#888888", "改看P/B · P/S"),
    }
    sig_lbl, sig_c, sig_desc = sm[signal]

    # ── KPI row ───────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    _kpi(c1, "股價",       f"{cp:.2f}" if cp else "N/A",                "",                                             "#00F5FF")
    _kpi(c2, "EPS (TTM)",  f"{float(eps):.2f}" if eps else "N/A",      "每股盈餘",                                     "#FFD700")
    _kpi(c3, "P/E",        f"{use_pe:.1f}×" if use_pe else "N/A",      "本益比",                                       sig_c)
    _kpi(c4, "P/B",        f"{pb:.2f}×" if pb else "N/A",              "股價淨值",                                     "#B77DFF")
    _kpi(c5, "DDM估值",    f"{ddm_val:.2f}" if ddm_val else "N/A",
         f"{'低估✓' if ddm_val and cp < ddm_val else '高估✗' if ddm_val else '無配息'}",
         "#00FF7F" if ddm_val and cp < ddm_val else "#FF6060")
    _kpi(c6, "Graham值",   f"{graham_val:.2f}" if graham_val else "N/A",
         f"{'低估✓' if graham_val and cp < graham_val else '高估✗' if graham_val else 'N/A'}",
         "#00FF7F" if graham_val and cp and cp < graham_val else "#FF6060")
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # Traffic light
    def _circle(lbl, sub, cls, active):
        a = "active" if active else "dim"
        return f'<div class="tl-circle {cls} {a}"><div style="font-size:13px;font-weight:800;">{lbl}</div><div style="font-size:9px;opacity:.7;margin-top:3px;">{sub}</div></div>'

    if pe_25 and pe_75:
        rows = [(signal == "expensive", "tl-red",    "🔴 昂貴", f"PE>{pe_75:.0f}"),
                (signal == "fair",     "tl-yellow",  "🟡 合理", f"PE {pe_25:.0f}-{pe_75:.0f}"),
                (signal == "cheap",    "tl-green",   "🟢 便宜", f"PE<{pe_25:.0f}")]
    else:
        rows = [(signal == "expensive", "tl-red",    "🔴 昂貴", "PE>35"),
                (signal == "fair",     "tl-yellow",  "🟡 合理", "PE 15-35"),
                (signal == "cheap",    "tl-green",   "🟢 便宜", "PE<15")]

    circles = "".join(_circle(lb, sb, cls, act) for act, cls, lb, sb in rows)
    st.markdown(f'<div class="tl-wrap">{circles}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="margin:12px 0;padding:18px 24px;background:rgba(0,0,0,.2);border:1px solid {sig_c}33;'
        f'border-left:5px solid {sig_c};border-radius:0 12px 12px 0;text-align:center;">'
        f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:30px;font-weight:800;color:{sig_c};">{sig_lbl}</div>'
        f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:18px;color:rgba(180,195,220,.65);margin-top:8px;">'
        f'{sig_desc} &nbsp;·&nbsp; PE: {f"{use_pe:.1f}" if use_pe else "N/A"} &nbsp;·&nbsp; '
        f'P/B: {f"{pb:.2f}" if pb else "N/A"} &nbsp;·&nbsp; Div: {div_y*100:.2f}% &nbsp;·&nbsp; '
        f'Graham: {f"{graham_val:.2f}" if graham_val else "N/A"}</div></div>',
        unsafe_allow_html=True
    )

    # ══════════════════════════════════════════════════════════════
    # PE RIVER CHART (Plotly) — 8x / 12x / 16x / 20x bands
    # ══════════════════════════════════════════════════════════════
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    _sec28("PE 價值河流圖 (PE River Chart)")
    _sec26("股價與四條PE估值帶的相對位置 — 落在哪條河道一眼看清估值高低", "rgba(160,176,208,.45)")

    if not hist3y.empty and eps and float(eps) > 0:
        eps_val = float(eps)
        river_df = hist3y.copy().reset_index()
        for c in river_df.columns:
            if str(c).lower() in ["date", "datetime", "index"]:
                river_df.rename(columns={c: "Date"}, inplace=True)
                break
        if "Date" not in river_df.columns:
            river_df["Date"] = river_df.index
        river_df["Date"]  = pd.to_datetime(river_df["Date"])
        river_df["PE8"]   = eps_val * 8
        river_df["PE12"]  = eps_val * 12
        river_df["PE16"]  = eps_val * 16
        river_df["PE20"]  = eps_val * 20

        fig_river = go.Figure()
        # Colored river bands (filled areas between PE lines)
        river_colors = [
            ("#00FF7F", "rgba(0,255,127,.08)",  "PE 8×",  "river_df.PE8",  "PE 12×", "river_df.PE12"),
            ("#FFD700", "rgba(255,215,0,.07)",  "PE 12×", "river_df.PE12", "PE 16×", "river_df.PE16"),
            ("#FF9A3C", "rgba(255,154,60,.07)", "PE 16×", "river_df.PE16", "PE 20×", "river_df.PE20"),
            ("#FF3131", "rgba(255,49,49,.07)",  "PE 20×", "river_df.PE20", None,     None),
        ]
        pe_band_data = [
            (river_df["PE8"],  river_df["PE12"],  "#00FF7F", "rgba(0,255,127,.06)",  "PE 8×–12×"),
            (river_df["PE12"], river_df["PE16"],  "#FFD700", "rgba(255,215,0,.06)",  "PE 12×–16×"),
            (river_df["PE16"], river_df["PE20"],  "#FF9A3C", "rgba(255,154,60,.06)", "PE 16×–20×"),
        ]
        for y_lower, y_upper, lc, fc, band_name in pe_band_data:
            fig_river.add_trace(go.Scatter(
                x=pd.concat([river_df["Date"], river_df["Date"][::-1]]),
                y=pd.concat([y_upper, y_lower[::-1]]),
                fill="toself", fillcolor=fc, line=dict(width=0),
                name=band_name, showlegend=True,
                hoverinfo="skip"
            ))
        # PE lines
        for pe_mult, pe_col, pe_col_line in [(8, "#00FF7F", "#00FF7F"), (12, "#FFD700", "#FFD700"),
                                              (16, "#FF9A3C", "#FF9A3C"), (20, "#FF3131", "#FF3131")]:
            fig_river.add_trace(go.Scatter(
                x=river_df["Date"], y=river_df[f"PE{pe_mult}"],
                name=f"PE {pe_mult}×", line=dict(color=pe_col_line, width=1.2, dash="dot"),
                hovertemplate=f"PE {pe_mult}× = %{{y:.2f}}<extra></extra>"
            ))
        # Price line on top
        fig_river.add_trace(go.Scatter(
            x=river_df["Date"], y=river_df["Close"],
            name="收盤價", line=dict(color="#00F5FF", width=2.2),
            hovertemplate="Price = %{y:.2f}<extra></extra>"
        ))
        fig_river.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=380,
            margin=dict(t=20, b=40, l=60, r=20),
            legend=dict(font=dict(color="#B0C0D0", size=11, family="Rajdhani"), orientation="h", y=-0.12),
            yaxis=dict(gridcolor="rgba(255,255,255,.04)", tickfont=dict(color="#778")),
            xaxis=dict(gridcolor="rgba(255,255,255,.03)", tickfont=dict(color="#778")),
        )
        st.plotly_chart(fig_river, use_container_width=True)
        # PE percentile bar
        if pe_25 and pe_75 and use_pe:
            pct_pos = min(100, max(0, (use_pe - pe_25) / (pe_75 - pe_25 + 0.001) * 100))
            c_pos   = "#FF3131" if pct_pos > 80 else ("#FFD700" if pct_pos > 40 else "#00FF7F")
            st.markdown(
                f'<div style="margin:12px 0;">'
                f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:18px;color:rgba(160,176,208,.5);margin-bottom:8px;">'
                f'PE PERCENTILE — 目前PE位於3年歷史的第 {pct_pos:.0f} 百分位</div>'
                f'<div style="background:rgba(255,255,255,.05);border-radius:20px;height:10px;position:relative;overflow:hidden;">'
                f'<div style="position:absolute;left:0;top:0;height:100%;width:{pct_pos:.0f}%;'
                f'background:linear-gradient(90deg,#00FF7F,{c_pos});border-radius:20px;"></div></div>'
                f'<div style="font-family:\'Orbitron\',sans-serif;font-size:12px;color:{c_pos};margin-top:6px;text-align:right;">'
                f'{pct_pos:.0f}th PERCENTILE</div></div>',
                unsafe_allow_html=True
            )
    else:
        st.toast("💡 此標的無EPS數據（ETF/未獲利公司），PE河流圖不可用", icon="💡")
        if pe_trail: st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:22px;color:#FFF;">Trailing P/E: <b>{pe_trail:.1f}×</b></div>', unsafe_allow_html=True)
        if pe_fwd:   st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:22px;color:#FFF;">Forward P/E: <b>{pe_fwd:.1f}×</b></div>',  unsafe_allow_html=True)
        if ps:       st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:22px;color:#FFF;">P/S (TTM): <b>{ps:.2f}×</b></div>',          unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════
    # MINE SWEEPER (掃雷大隊)
    # ══════════════════════════════════════════════════════════════
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    _sec28("💣 掃雷大隊 (Mine Sweeper)")
    _sec26("負債股權比 + 自由現金流 — 財務地雷偵測，排雷後的便宜股才是真低估", "rgba(255,154,60,.5)")

    mine_count = int(has_debt_mine) + int(has_fcf_mine)

    if mine_count == 0:
        st.markdown(f"""
<div class="mine-safe">
  <div style="font-family:'Rajdhani',sans-serif;font-size:28px;font-weight:700;color:#00FF7F;">
    ✅ 財務健康 — 無明顯地雷</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(0,255,127,.55);margin-top:6px;">
    D/E: {f"{debt_to_equity:.1f}%" if debt_to_equity is not None else "N/A"} (&lt;200% 安全) &nbsp;·&nbsp;
    FCF: {f"${free_cashflow/1e9:.2f}B" if free_cashflow and abs(free_cashflow)>1e9 else f"${free_cashflow/1e6:.0f}M" if free_cashflow else "N/A"} (&gt;0 健康)
  </div>
</div>""", unsafe_allow_html=True)
    else:
        debt_str = (f"{debt_to_equity:.1f}%" if debt_to_equity is not None else "N/A")
        fcf_str  = (f"${free_cashflow/1e9:.2f}B" if free_cashflow and abs(free_cashflow) > 1e9
                    else f"${free_cashflow/1e6:.0f}M" if free_cashflow else "N/A")
        st.markdown(f"""
<div class="mine-alert">
  <div style="font-family:'Rajdhani',sans-serif;font-size:28px;font-weight:700;color:#FF6B6B;">
    💣 財務地雷 (Mine Alert) — 偵測到 {mine_count} 個風險訊號</div>
  <div style="margin-top:12px;display:flex;gap:16px;flex-wrap:wrap;">""", unsafe_allow_html=True)

        if has_debt_mine:
            st.markdown(f"""
    <div style="flex:1;min-width:220px;padding:12px 16px;background:rgba(255,49,49,.06);
      border:1px solid rgba(255,49,49,.25);border-radius:10px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,100,100,.6);
        letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">💣 高負債風險</div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:36px;color:#FF6B6B;line-height:1;">{debt_str}</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(255,120,120,.6);margin-top:4px;">
        負債股權比 D/E &gt; 200% 警戒線</div>
    </div>""", unsafe_allow_html=True)

        if has_fcf_mine:
            st.markdown(f"""
    <div style="flex:1;min-width:220px;padding:12px 16px;background:rgba(255,49,49,.06);
      border:1px solid rgba(255,49,49,.25);border-radius:10px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(255,100,100,.6);
        letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">💣 自由現金流負值</div>
      <div style="font-family:'Bebas Neue',sans-serif;font-size:36px;color:#FF6B6B;line-height:1;">{fcf_str}</div>
      <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(255,120,120,.6);margin-top:4px;">
        FCF &lt; 0 · 公司正在燒錢</div>
    </div>""", unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

    # Mine sweeper metrics summary
    mc1, mc2, mc3, mc4 = st.columns(4)
    de_c = "#FF3131" if has_debt_mine else "#00FF7F"
    fc_c = "#FF3131" if has_fcf_mine  else "#00FF7F"
    _kpi(mc1, "負債股權比 D/E", f"{debt_to_equity:.0f}%" if debt_to_equity is not None else "N/A",
         ">200%=高風險", de_c)
    _kpi(mc2, "自由現金流",
         f"${free_cashflow/1e9:.1f}B" if free_cashflow and abs(free_cashflow) > 1e9
         else f"${free_cashflow/1e6:.0f}M" if free_cashflow else "N/A",
         ">0=健康", fc_c)
    _kpi(mc3, "流動比率", f"{info.get('currentRatio', 0) or 0:.2f}×", ">1.5=安全",
         "#00FF7F" if (info.get("currentRatio") or 0) > 1.5 else "#FFD700")
    _kpi(mc4, "ROE",
         f"{info.get('returnOnEquity', 0) * 100:.1f}%" if info.get("returnOnEquity") else "N/A",
         ">15%=優秀",
         "#00FF7F" if (info.get("returnOnEquity") or 0) > 0.15 else "#FFD700")


def _s54(hist3y, info, symbol):
    render_5_4_value_river(symbol, info, hist3y)


# ════════════════════════════════════════════════════════════════════
# 5.5  ETF 戰情室 (ETF Command Center) — REPLACES 13F
# First Principle: ETF = 透明工具，殖利率/費用/成分是核心三維
# ════════════════════════════════════════════════════════════════════
def render_5_5_etf_command(ticker: str, info: dict, hist: pd.DataFrame):
    """
    ETF Command Center: Yield, Expense Ratio, Beta, Sector X-Ray.
    Public-facing function name per spec. Replaces unstable 13F module.
    """
    _hd("5.5", "🛡️ ETF 戰略透視 (ETF Strategy)",
        "年化殖利率 · 費用比率 · Beta · 成分股X光透視 · 折溢價分析", "#B77DFF")

    _explain(
        "第一性原理：ETF三維分析框架",
        "ETF的本質是「打包好的多元化資產籃子」，分析ETF需看三個維度：\n"
        "第一維：殖利率（Yield）— 這個籃子每年給你多少現金？高殖利率ETF是被動收入的核心工具。\n"
        "第二維：費用比率（Expense Ratio）— 每年你要付給基金公司多少管理費？越低越好。\n"
        "第三維：Beta — 相對大盤的波動倍數。Beta>1爆發力強但風險高，Beta<1適合防禦配置。\n"
        "成分股X光透視讓你看穿ETF的「靈魂」——你真正買的是哪些板塊？",
        "▸ Yield>4% = 高息策略  ▸ Expense<0.2% = 低成本 ▸ Beta<0.8 = 防禦型  ▸ X光看清板塊集中度",
        "#B77DFF"
    )

    # ── Core ETF metrics ──────────────────────────────────────────
    etf_yield    = info.get("yield") or info.get("dividendYield") or 0
    expense_ratio= info.get("annualReportExpenseRatio") or info.get("fundInceptionDate") and None or None
    # Try alternate keys for expense ratio
    for key in ["expenseRatio", "annualReportExpenseRatio", "totalExpenseRatio"]:
        if info.get(key) is not None:
            expense_ratio = info.get(key)
            break
    beta         = info.get("beta") or info.get("beta3Year")
    nav          = info.get("navPrice") or info.get("previousClose")
    cp_now       = info.get("currentPrice") or info.get("regularMarketPrice") or \
                   (float(hist["Close"].iloc[-1]) if not hist.empty else None)
    category     = info.get("category") or info.get("fundFamily") or info.get("sector") or "—"
    total_assets = info.get("totalAssets")
    three_yr_ret = info.get("threeYearAverageReturn")
    five_yr_ret  = info.get("fiveYearAverageReturn")

    # Premium/Discount calc
    premium_disc = None
    if nav and cp_now and nav > 0:
        premium_disc = (cp_now - nav) / nav * 100

    # ── KPI Grid ──────────────────────────────────────────────────
    yield_pct     = etf_yield * 100 if etf_yield and etf_yield < 1 else (etf_yield or 0)
    expense_pct   = expense_ratio * 100 if expense_ratio and expense_ratio < 1 else (expense_ratio or 0)

    yield_c   = "#00FF7F" if yield_pct > 4 else ("#FFD700" if yield_pct > 2 else "#888")
    expense_c = "#00FF7F" if 0 < expense_pct < 0.2 else ("#FFD700" if expense_pct < 0.5 else "#FF3131")
    beta_c    = "#00FF7F" if beta and beta < 0.8 else ("#FFD700" if beta and beta < 1.2 else "#FF3131")

    st.markdown(f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px;">
  <div class="etf-metric" style="--mc:{yield_c};">
    <div class="etf-metric-lbl">年化殖利率 Yield</div>
    <div class="etf-metric-val" style="color:{yield_c};">{f"{yield_pct:.2f}" if yield_pct else "N/A"}</div>
    <div class="etf-metric-sub">{"%" if yield_pct else ""} {"🔥高息" if yield_pct>4 else "中息" if yield_pct>2 else "低/無息"}</div>
  </div>
  <div class="etf-metric" style="--mc:{expense_c};">
    <div class="etf-metric-lbl">費用比率 Expense</div>
    <div class="etf-metric-val" style="color:{expense_c};">{f"{expense_pct:.2f}" if expense_pct else "N/A"}</div>
    <div class="etf-metric-sub">{"% / yr" if expense_pct else ""} {"✅低費" if expense_pct and expense_pct<0.2 else "中費" if expense_pct and expense_pct<0.5 else ""}</div>
  </div>
  <div class="etf-metric" style="--mc:{beta_c};">
    <div class="etf-metric-lbl">Beta 波動係數</div>
    <div class="etf-metric-val" style="color:{beta_c};">{f"{beta:.2f}" if beta else "N/A"}</div>
    <div class="etf-metric-sub">{"防禦型" if beta and beta<0.8 else "均衡型" if beta and beta<1.2 else "進攻型" if beta else "—"}</div>
  </div>
  <div class="etf-metric" style="--mc:#00F5FF;">
    <div class="etf-metric-lbl">折溢價 Prem/Disc</div>
    <div class="etf-metric-val" style="color:{'#FF3131' if premium_disc and premium_disc>2 else '#00FF7F' if premium_disc and premium_disc<-1 else '#FFD700'};">
      {f"{premium_disc:+.2f}%" if premium_disc is not None else "N/A"}
    </div>
    <div class="etf-metric-sub">{"溢價買貴" if premium_disc and premium_disc>2 else "折價機會" if premium_disc and premium_disc<-1 else "接近淨值" if premium_disc is not None else "NAV未知"}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Summary banner
    if yield_pct > 4 and expense_pct and expense_pct < 0.3:
        _banner("🛡️ 優質高息 ETF — 高殖利率 + 低費用",
                f"Yield {yield_pct:.2f}% · Expense {expense_pct:.2f}% · Beta {beta:.2f}" if beta else f"Yield {yield_pct:.2f}%",
                "#00FF7F", "🛡️")
    elif beta and beta > 1.5:
        _banner("⚡ 高Beta進攻型 ETF — 放大市場波動",
                f"Beta {beta:.2f}× · 適合多頭行情配置 · 空頭時跌更多", "#FF9A3C", "⚡")
    elif beta and beta < 0.6:
        _banner("🛡️ 低波動防禦型 ETF",
                f"Beta {beta:.2f}× · 適合保守型投資人 · 熊市跌幅較小", "#B77DFF", "🛡️")

    # ── Additional info row ───────────────────────────────────────
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    ma1, ma2, ma3, ma4 = st.columns(4)
    assets_str = (f"${total_assets/1e9:.1f}B" if total_assets and total_assets > 1e9
                  else f"${total_assets/1e6:.0f}M" if total_assets else "N/A")
    _kpi(ma1, "總資產 AUM",    assets_str,                                  "基金規模",   "#00F5FF")
    _kpi(ma2, "類別/族群",     str(category)[:14],                          "Fund Category", "#FFD700")
    _kpi(ma3, "3年平均報酬",   f"{three_yr_ret*100:.1f}%" if three_yr_ret else "N/A",
         "年化", "#00FF7F" if three_yr_ret and three_yr_ret > 0.1 else "#FFD700")
    _kpi(ma4, "5年平均報酬",   f"{five_yr_ret*100:.1f}%" if five_yr_ret else "N/A",
         "年化", "#00FF7F" if five_yr_ret  and five_yr_ret > 0.08 else "#FFD700")

    # ── Price Chart ───────────────────────────────────────────────
    if not hist.empty:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        _sec28("ETF 價格走勢 + 均線")
        _sec26("青線=ETF收盤價 · 金線=20日均 · 橙線=50日均", "rgba(160,176,208,.45)")
        df_chart = _prep(hist)
        df_chart["MA20"] = df_chart["Close"].rolling(20).mean()
        df_chart["MA50"] = df_chart["Close"].rolling(50).mean()
        tail_n  = 252
        dpx     = df_chart[["Date", "Close", "MA20", "MA50"]].dropna().tail(tail_n)
        dpm     = dpx.melt("Date", var_name="Series", value_name="Price")
        etf_ch  = alt.Chart(dpm).mark_line(strokeWidth=1.8).encode(
            x=alt.X("Date:T", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
            y=alt.Y("Price:Q", axis=alt.Axis(labelColor="#555", gridColor="#1a1a2a")),
            color=alt.Color("Series:N",
                            scale=alt.Scale(domain=["Close", "MA20", "MA50"],
                                            range=["#B77DFF", "#FFD700", "#FF9A3C"]),
                            legend=alt.Legend(labelColor="#aaa", titleColor="#aaa", orient="top-right"))
        ).properties(background="transparent", height=260).configure_view(strokeOpacity=0)
        st.altair_chart(etf_ch, use_container_width=True)

    # ── X-Ray: Sector Weightings (Donut Chart) ────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    _sec28("X光 成分板塊透視 (Sector X-Ray)")
    _sec26("donut圖顯示ETF真實板塊配置 — 你到底在買哪些行業？", "rgba(183,125,255,.5)")

    sector_data = None
    # Try sectorWeightings (list of dicts)
    sw = info.get("sectorWeightings")
    if sw and isinstance(sw, list):
        try:
            rows = []
            for item in sw:
                if isinstance(item, dict):
                    for k, v in item.items():
                        rows.append({"Sector": k.replace("_", " ").title(), "Weight": float(v) * 100})
            if rows:
                sector_data = pd.DataFrame(rows).sort_values("Weight", ascending=False).head(10)
        except Exception:
            sector_data = None

    if sector_data is not None and not sector_data.empty:
        palette = ["#00F5FF", "#FFD700", "#00FF7F", "#FF9A3C", "#B77DFF",
                   "#FF3131", "#FF6BFF", "#4dc8ff", "#88FF88", "#FFB347"]

        fig_donut = go.Figure(go.Pie(
            labels=sector_data["Sector"].tolist(),
            values=sector_data["Weight"].tolist(),
            hole=0.55,
            marker=dict(colors=palette[:len(sector_data)],
                        line=dict(color="rgba(0,0,0,0.5)", width=2)),
            textfont=dict(color="#DDE", size=12, family="Rajdhani"),
            hovertemplate="%{label}: %{value:.1f}%<extra></extra>"
        ))
        fig_donut.update_layout(
            title=dict(text="SECTOR ALLOCATION", font=dict(color="rgba(183,125,255,.35)", size=11, family="JetBrains Mono")),
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
            height=340, margin=dict(t=36, b=0, l=0, r=0),
            legend=dict(font=dict(color="#B0C0D0", size=11, family="Rajdhani")),
        )
        col_donut, col_table = st.columns([1, 1])
        with col_donut:
            st.plotly_chart(fig_donut, use_container_width=True)
        with col_table:
            st.markdown("<div style='padding-top:20px;'>", unsafe_allow_html=True)
            for i, row in sector_data.iterrows():
                bar_w = min(100, row["Weight"] / sector_data["Weight"].max() * 100)
                pc    = palette[list(sector_data.index).index(i) % len(palette)]
                st.markdown(
                    f'<div style="margin-bottom:8px;">'
                    f'<div style="display:flex;justify-content:space-between;margin-bottom:3px;">'
                    f'<span style="font-family:Rajdhani,sans-serif;font-size:14px;color:rgba(200,215,235,.75);">{row["Sector"]}</span>'
                    f'<span style="font-family:JetBrains Mono,monospace;font-size:12px;color:{pc};">{row["Weight"]:.1f}%</span>'
                    f'</div>'
                    f'<div style="background:rgba(255,255,255,.05);border-radius:4px;height:5px;">'
                    f'<div style="width:{bar_w:.0f}%;height:100%;background:{pc};border-radius:4px;opacity:.75;"></div>'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Fallback: Try top holdings
        st.markdown(f"""
<div style="padding:28px;background:rgba(183,125,255,.04);border:1px solid rgba(183,125,255,.15);
  border-radius:14px;text-align:center;">
  <div style="font-size:36px;opacity:.3;margin-bottom:10px;">🔍</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:22px;color:rgba(255,255,255,.35);">
    板塊配置數據不可用</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(160,176,208,.25);margin-top:6px;">
    sectorWeightings 欄位未提供（部分ETF/台股ETF）<br>
    可手動查詢 ETF 官方網站獲取最新成分股配置</div>
</div>""", unsafe_allow_html=True)

    # ── Yield deep dive: Historical dividend ─────────────────────
    if not hist.empty:
        div_df = _prep(hist)
        if "Dividends" in div_df.columns:
            div_rows = div_df[div_df["Dividends"] > 0][["Date", "Dividends"]].tail(8)
            if not div_rows.empty:
                st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
                _sec28("配息歷史 (Dividend History)")
                _sec26("近8次除息記錄 — 殖利率一致性是配息ETF的生命線", "rgba(0,255,127,.4)")
                for _, drow in div_rows.iterrows():
                    d_date = str(drow["Date"])[:10]
                    d_val  = float(drow["Dividends"])
                    d_pct  = (d_val / cp_now * 100) if cp_now and cp_now > 0 else 0
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;align-items:center;'
                        f'padding:9px 16px;background:rgba(0,255,127,.025);border:1px solid rgba(0,255,127,.08);'
                        f'border-radius:8px;margin-bottom:5px;">'
                        f'<span style="font-family:JetBrains Mono,monospace;font-size:12px;color:rgba(160,176,208,.55);">{d_date}</span>'
                        f'<span style="font-family:Bebas Neue,sans-serif;font-size:22px;color:#00FF7F;">{d_val:.4f}</span>'
                        f'<span style="font-family:Rajdhani,sans-serif;font-size:14px;color:rgba(0,255,127,.6);">'
                        f'殖利率貢獻 {d_pct:.2f}%</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )


def _s55(holders, info, symbol, mf_holders=None):
    """Internal alias — routes to ETF Command for all tickers."""
    # Attempt to get latest hist from cache if needed
    # We call with empty hist since hist isn't passed here; render will show what it can
    h1_cache = st.session_state.get("_t5_h1_cache", pd.DataFrame())
    render_5_5_etf_command(symbol, info, h1_cache)


# ════════════════════════════════════════════════════════════════════
# 5.6  戰略百科  THE CODEX  (Preserved verbatim)
# ════════════════════════════════════════════════════════════════════
def _s56():
    _hd("5.6", "📜 戰略百科 — The Codex",
        "SOP · Entry/Exit · Sector Map · Mindset · CBAS Engine · OTC MA", "#FF3131")
    tabs = st.tabs(["⏰ 四大時間套利", "📋 進出場紀律", "🏭 產業族群庫", "🧠 特殊心法", "⚡ CBAS試算", "📈 OTC神奇均線"])

    # T1: 四大時間套利
    with tabs[0]:
        _sec28("四大時間套利視窗")
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:18px;color:rgba(160,176,208,.5);margin-bottom:16px;">CB的時間邊際：不同階段的風報比完全不同，對的時機才能用最低風險賺最大利潤。</div>', unsafe_allow_html=True)
        for cls, num, title, period, key, detail in [
            ("gold", "01", "新券蜜月期", "上市 0–90 天",   "上市初期追蹤，大戶定調，股性未定",       "進場甜蜜點：105–115 元。前 90 天是觀察期也是機會期，關注大股東動態與首批券商報告。此期間CB流動性低，價格易被操控，需小量試水。"),
            ("green","02", "滿年沈澱",   "上市 350–420 天","沈澱洗牌結束，底部有支撐",               "觸發點：CB 站上 87MA 且帶量。一年洗盤後仍存活的標的底部結構扎實，浮額已充分清洗，此時進場的持有成本往往最低。"),
            ("",     "03", "賣回保衛戰", "距賣回日 90 天",  "即將觸發賣回保護條款，下方有 100 元保底", "最低風險窗口：CB接近賣回日且價格接近100元。下有100元保底，上有正股上漲機會，是最純粹的不對稱報酬。"),
            ("red",  "04", "轉換套利",   "正股遠高於轉換價","具備直接轉換套利空間",                   "轉換溢價率接近零甚至負值時，可直接轉換正股賣出。套利窗口短暫，需快速執行。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div class="ccard-t">{num}. {title} — {period}</div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>', unsafe_allow_html=True)

    # T2: 進出場紀律
    with tabs[1]:
        _sec28("進出場 SOP 戰場紀律")
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:18px;color:rgba(160,176,208,.5);margin-bottom:16px;">沒有紀律的策略是紙上富貴。以下是Titan OS核心進出場條件，每條都是真實虧損換來的教訓。</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:26px;font-weight:700;color:rgba(0,245,255,.75);letter-spacing:1px;margin:20px 0 12px;">📥 核心進場條件</div>', unsafe_allow_html=True)
        for cls, title, key, detail in [
            ("gold",  "✅ 條件一：87MA向上站穩",    "收盤價>87MA且均線斜率向上",        "最重要的進場門檻。不管消息面多好，87MA向下一律不碰。均線方向代表趨勢，位置代表支撐，兩者都要對。"),
            ("green", "✅ 條件二：轉換溢價率合理",   "溢價率 5%–15%",                    "溢價太低（<5%）= 下方無保護；溢價太高（>20%）= 上漲空間被稀釋。5-15%是最佳彈性區間。"),
            ("",      "✅ 條件三：CB價格在合理區間",  "CB 105–120 元最優",               "105元以下有空間，120元以上溢價過高。尋找CB剛從100元底部回升、且正股技術面剛轉強的時間點。"),
            ("",      "✅ 條件四：族群共振確認",      "2-3檔同族群CB同步上攻",           "單一標的漲動可能是偶發，族群共振才是主力進場。等到族群整體啟動再進，勝率大幅提升。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div class="ccard-t">{title}</div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>', unsafe_allow_html=True)
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:26px;font-weight:700;color:rgba(255,49,49,.75);letter-spacing:1px;margin:20px 0 12px;">📤 核心出場條件</div>', unsafe_allow_html=True)
        for cls, title, key, detail in [
            ("red",   "🛑 停損天條",   "CB 跌破 100 元",    "保本天條不妥協，沒有例外。跌破即離場。這是整套系統最重要的規則，一次不執行就可能讓整年獲利歸零。"),
            ("gold",  "💰 停利策略",   "目標 152 元以上",   "留魚尾策略：分批出場，讓剩餘倉位跟跑。到達130時出50%，150時再出30%，剩20%讓它跑。"),
            ("",      "⏰ 時間停損",   "持有超過 90 天未動","超過 90 天無動能，重新評估或減倉。時間成本是隱形的機會成本，死水不如流水。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div class="ccard-t">{title}</div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>', unsafe_allow_html=True)

    # T3: 產業族群庫
    with tabs[2]:
        _sec28("產業族群資料庫")
        ca2, cb2 = st.columns(2)
        tw = [
            ("🤖 AI伺服器",  "廣達·緯創·英業達·技嘉·緯穎"),
            ("🌡️ 散熱",     "奇鋐·雙鴻·建準·健策·力致"),
            ("⚙️ CoWoS封測", "日月光·矽品·力成·欣銓"),
            ("⚡ 重電/電網",  "華城·士電·中興電·大同·亞力"),
            ("🔬 半導體設備", "弘塑·辛耘·漢微科·家登·旺矽"),
            ("🚢 航運",      "長榮·陽明·萬海·台驊·慧洋"),
            ("💊 生技新藥",   "藥華藥·合一·浩鼎·疫苗·醣基"),
            ("🔋 電池/EV",   "立凱·必翔·台達電·正崴·帝寶"),
        ]
        us = [
            ("🧠 AI大模型",  "NVDA·AMD·MSFT·GOOGL·META·AMZN"),
            ("⚛️ 量子計算",  "QBTS·IONQ·RGTI·QUBT"),
            ("🚀 太空/國防",  "PLTR·RKLB·LUNR·LMT·RTX"),
            ("🏦 金融科技",   "SOFI·AFRM·UPST·SQ·PYPL"),
            ("☁️ Cloud SaaS","SNOW·DDOG·CRWD·MDB·NET"),
            ("🌿 Clean Energy","ENPH·FSLR·PLUG·BE·ARRY"),
        ]
        etfs = [
            ("🇺🇸 美股核心", "SPY·QQQ·VTI·IVV·VOO"),
            ("🇹🇼 台股核心", "0050·006208·00878·00919·00929"),
            ("🔥 主題ETF",   "ARKK·BOTZ·SOXX·ROBO·CIBR"),
        ]
        with ca2:
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:rgba(0,245,255,.7);margin-bottom:10px;">🇹🇼 台股族群</div>', unsafe_allow_html=True)
            for n, s in tw:
                st.markdown(f'<div class="srow"><div class="srow-name">{n}</div><div class="srow-stk">{s}</div></div>', unsafe_allow_html=True)
        with cb2:
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:rgba(255,154,60,.7);margin-bottom:10px;">🇺🇸 美股族群</div>', unsafe_allow_html=True)
            for n, s in us:
                st.markdown(f'<div class="srow"><div class="srow-name">{n}</div><div class="srow-stk">{s}</div></div>', unsafe_allow_html=True)
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:rgba(183,125,255,.7);margin:12px 0 10px;">📦 核心 ETF</div>', unsafe_allow_html=True)
            for n, s in etfs:
                st.markdown(f'<div class="srow"><div class="srow-name">{n}</div><div class="srow-stk">{s}</div></div>', unsafe_allow_html=True)

    # T4: 心法
    with tabs[3]:
        _sec28("交易心法 Mindset OS")
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:20px;color:rgba(160,176,208,.4);margin-bottom:16px;">交易是認知套利：你比市場更理解的部分，才是你的真實優勢。心法不是秘訣，是對人性弱點的系統性防禦。</div>', unsafe_allow_html=True)
        for i, (title, desc) in enumerate([
            ("賣出是種藝術",  "目標區間到達後分批出場，留魚尾策略。永遠不要賣在最頂，讓利潤奔跑。分批的意義在於：你不需要判斷最高點，只需要在高位持續兌現。"),
            ("跌破100是天條", "不管故事多美，CB跌破100元立刻離場。保住本金才有下一仗。市場永遠有下一個機會，但帳戶歸零就沒有機會了。"),
            ("族群共振才是主力","2~3檔同族群CB同步上攻，才是真正主力進場訊號。個股異動是獨舞，族群共振才是群舞。主力進場一定有足跡。"),
            ("87MA是生命線", "站上87MA且均線向上才安全。跌破=第一警戒，284MA跌破=大逃殺。均線系統是多空的最終裁判，不管當下消息多好。"),
            ("溢價率的陷阱",  "溢價率 > 20% 上漲空間有限，下跌空間卻大。選低溢價（5~15%）CB，彈性最大，風險最低。"),
            ("籌碼鬆動就跑",  "已轉換比例超過30%，股東結構改變，籌碼不乾淨立刻警惕。主力轉換後開始賣股，CB的上漲動力就消失了。"),
            ("尾盤定勝負",   "13:25後最後25分鐘是多空最誠實表態。收盤站穩才是真突破，收盤跌破才是真破壞。"),
            ("消息面最後出現","基本面+技術面打底，消息面是確認彈，不是買入理由。追消息買的，往往是主力出貨的對象。"),
            ("停損是最高策略","每次停損是自我保護。不怕停損，怕的是一次大虧抹掉所有獲利。系統化停損是交易員和賭徒的本質區別。"),
            ("複利思維操盤",  "月報酬5%，一年79.6%。急著翻倍的人，最快的路是歸零。複利的奇蹟需要時間和紀律，不需要奇蹟行情。"),
        ], 1):
            st.markdown(
                f'<div style="display:flex;align-items:flex-start;gap:16px;padding:16px 18px;'
                f'background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.04);'
                f'border-radius:10px;margin-bottom:8px;">'
                f'<div style="font-family:\'Orbitron\',sans-serif;font-size:28px;font-weight:900;'
                f'color:rgba(255,215,0,.1);min-width:44px;line-height:1;">{i:02d}</div>'
                f'<div><div style="font-family:\'Rajdhani\',sans-serif;font-size:20px;font-weight:700;color:#FFF;margin-bottom:5px;">{title}</div>'
                f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:17px;color:rgba(180,195,220,.55);line-height:1.7;">{desc}</div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

    # T5: CBAS
    with tabs[4]:
        _sec28("CBAS 槓桿試算引擎")
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:20px;color:rgba(160,176,208,.4);margin-bottom:16px;">第一性原理：CB的隱含槓桿 = 總投資額 ÷ 溢價部分。110元的CB，溢價10元，槓桿=110÷10=11倍。</div>', unsafe_allow_html=True)
        ca3, cb3 = st.columns(2)
        with ca3:
            cb_price = st.number_input("CB 市價 (元)", min_value=100.0, max_value=200.0, value=108.0, step=0.5, key="cb5_price")
            lot      = st.number_input("張數 (手)",    min_value=1, max_value=500, value=1, step=1, key="cb5_lot")
        with cb3:
            conv_px = st.number_input("轉換價 (元)",   min_value=1.0, max_value=2000.0, value=50.0, step=0.5, key="cb5_conv")
            stk_px  = st.number_input("正股現價 (元)", min_value=0.01, max_value=2000.0, value=45.0, step=0.5, key="cb5_stk")
        if cb_price > 100:
            prem_cost = cb_price - 100
            leverage  = cb_price / prem_cost if prem_cost > 0 else 0
            total_inv = cb_price * lot * 1000
            conv_prem_pct = (stk_px - conv_px) / conv_px * 100 if conv_px > 0 else 0
            conv_ratio    = 100000 / conv_px if conv_px > 0 else 0
            lev_c  = "#00FF7F" if leverage >= 5 else ("#FFD700" if leverage >= 3 else "#FF6B6B")
            conv_c = "#00FF7F" if conv_prem_pct < -5 else ("#FFD700" if abs(conv_prem_pct) < 5 else "#FF3131")
            st.markdown(
                f'<div class="calc-scr"><div style="display:flex;justify-content:space-around;align-items:center;flex-wrap:wrap;gap:20px;">'
                f'<div style="text-align:center;"><div style="font-family:\'Orbitron\',sans-serif;font-size:64px;font-weight:900;color:{lev_c};text-shadow:0 0 30px {lev_c}55;line-height:1;">{leverage:.2f}<span style="font-size:22px;opacity:.4;">×</span></div>'
                f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:16px;color:rgba(160,176,208,.4);text-transform:uppercase;letter-spacing:3px;margin-top:6px;">IMPLIED LEVERAGE</div></div>'
                f'<div style="height:80px;width:1px;background:rgba(255,255,255,.06);"></div>'
                f'<div><div style="font-family:\'Rajdhani\',sans-serif;font-size:14px;color:rgba(160,176,208,.3);margin-bottom:4px;">CB 溢價權利金</div>'
                f'<div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:#FFF;">{prem_cost:.1f} 元</div></div>'
                f'<div style="height:80px;width:1px;background:rgba(255,255,255,.06);"></div>'
                f'<div><div style="font-family:\'Rajdhani\',sans-serif;font-size:14px;color:rgba(160,176,208,.3);margin-bottom:4px;">總投資額</div>'
                f'<div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:#FFF;">{total_inv/10000:.1f} 萬</div></div>'
                f'<div style="height:80px;width:1px;background:rgba(255,255,255,.06);"></div>'
                f'<div><div style="font-family:\'Rajdhani\',sans-serif;font-size:14px;color:rgba(160,176,208,.3);margin-bottom:4px;">每張換股數</div>'
                f'<div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:#FFF;">{conv_ratio:.0f} 股</div></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div style="margin-top:14px;padding:16px 20px;background:rgba(0,0,0,.2);border-left:4px solid {conv_c};border-radius:0 10px 10px 0;">'
                f'<span style="font-family:\'Rajdhani\',sans-serif;font-size:26px;font-weight:700;color:{conv_c};">'
                f'{"✅ 正股低於轉換價 — 轉換機率低" if conv_prem_pct < -10 else ("⚠️ 接近轉換價 — 關注轉換訊號" if abs(conv_prem_pct) < 5 else "🚀 正股高於轉換價 — 具轉換價值")}</span>'
                f'<span style="font-family:\'Rajdhani\',sans-serif;font-size:18px;color:rgba(160,176,208,.4);margin-left:12px;">轉換溢價率 {conv_prem_pct:+.1f}%</span></div>',
                unsafe_allow_html=True
            )
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:18px;color:rgba(160,176,208,.3);margin:16px 0 8px;">QUICK REF: 不同市價的槓桿對照</div>', unsafe_allow_html=True)
            refs = st.columns(5)
            for i, p in enumerate([103, 105, 110, 115, 120]):
                pm = p - 100; lv = p / pm if pm > 0 else 0
                lc = "#00FF7F" if lv > 5 else ("#FFD700" if lv > 3 else "#FF6B6B")
                refs[i].markdown(
                    f'<div style="text-align:center;padding:12px;background:rgba(255,255,255,.02);'
                    f'border:1px solid rgba(255,255,255,.04);border-radius:8px;">'
                    f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:14px;color:rgba(160,176,208,.35);">CB {p}元</div>'
                    f'<div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:{lc};line-height:1.2;">{lv:.1f}×</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.toast("⚠️ CB 市價需高於 100 元才有槓桿效應", icon="⚡")

    # T6: OTC均線
    with tabs[5]:
        _sec28("OTC 神奇均線法則")
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:20px;color:rgba(160,176,208,.4);margin-bottom:16px;">台股OTC市場的特殊均線系統，由實戰統計出的關鍵參數，87日=一季多一週，284日=約一年</div>', unsafe_allow_html=True)
        for cls, title, key, detail in [
            ("gold",  "87MA = 季線生命線",       "87MA 向上且股價站上",        "台股OTC核心均線。87MA向上=買進訊號；跌破且均線轉下=出場。CB操作的基礎框架。所有CB操作以87MA為進出依據，均線本身的方向比位置更重要。"),
            ("",      "284MA = 年線壓力/支撐",    "284MA 是長期趨勢分界線",     "284MA 之上=多頭，之下=空頭。87MA穿越284MA向上=黃金交叉；反之=死亡交叉。黃金交叉後的第一次回踩是最佳進場時機。"),
            ("green", "乖離率區間管理",            "正乖離<25%，負乖離<-25%",    "CB股價距87MA正乖離超過25%=過熱警示；負乖離超過25%=超跌反彈點。乖離率是均值回歸的量化工具，偏離越遠回歸拉力越強。"),
            ("red",   "格蘭碧6大訊號",            "G1突破買·G2假跌買·G3回測買 | G4跌破賣·G5假突賣·G6反壓賣", "買點(G1~G3)配合均線方向；賣點(G4~G6)配合背離與放量。格蘭碧8法則適用所有時間框架，OTC的87MA是最佳應用均線。"),
            ("",      "扣抵原理",                 "284MA的扣抵天數=284天前的收盤價", "284天前的價格偏低，今日284MA容易上揚（利多）；偏高則容易下壓（利空）。提前知道均線未來走向，是台股獨有的時間套利工具。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div class="ccard-t">{title}</div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# MAIN ENTRY
# ════════════════════════════════════════════════════════════════════
def render():
    # 🎯 FEATURE 1: 首次進入顯示戰術指導 Modal
    if not st.session_state.get("t5_guide_shown", False):
        show_guide_modal()

    _inject_css()
    symbol = _search()
    _hero(symbol)

    with st.spinner(f"⬡ 鎖定目標: {symbol}…"):
        h1, h3, info, holders, mf_holders, err = _fetch(symbol)

    if err:
        icon = "⏳" if "429" in err or "頻繁" in err or "rate" in err.lower() else "💀"
        st.toast(f"❌ {err}", icon=icon)
        st.toast("💡 美股: AAPL · NVDA  |  台股: 2330 · 00675L · 5274  |  ETF: SPY · QQQ", icon="📡")
        _nav()
        if st.session_state.get("t5_active") == "5.6":
            _s56()
        return

    # Cache h1 for _s55 alias
    st.session_state["_t5_h1_cache"] = h1

    cp_now   = info.get("currentPrice") or info.get("regularMarketPrice") or \
               (float(h1["Close"].iloc[-1]) if not h1.empty else 0)
    name     = info.get("longName") or info.get("shortName") or symbol
    sector   = info.get("sector") or info.get("category") or "—"
    mktcap   = info.get("marketCap")
    mktcap_s = (f"${mktcap/1e12:.2f}T" if mktcap and mktcap > 1e12
                else f"${mktcap/1e9:.1f}B" if mktcap and mktcap > 1e9 else "N/A")
    day_chg  = info.get("regularMarketChangePercent", 0) or 0
    chg_c    = "#00FF7F" if day_chg >= 0 else "#FF3131"
    w52_h    = info.get("fiftyTwoWeekHigh", 0) or 0
    w52_l    = info.get("fiftyTwoWeekLow",  0) or 0
    w52_pct  = (cp_now - w52_l) / (w52_h - w52_l) * 100 if (w52_h - w52_l) > 0 else 0

    # Quote ticker bar
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:20px;padding:14px 20px;background:rgba(255,255,255,.016);'
        f'border:1px solid rgba(255,255,255,.05);border-radius:14px;margin-bottom:18px;flex-wrap:wrap;">'
        f'<div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:30px;color:#FFF;letter-spacing:2px;line-height:1;">{symbol}</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(160,176,208,.4);margin-top:2px;">{name}</div></div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:44px;color:#FFF;line-height:1;margin-left:auto;">{cp_now:.2f}</div>'
        f'<div style="font-family:\'Rajdhani\',sans-serif;font-size:20px;font-weight:700;color:{chg_c};">{"▲" if day_chg>=0 else "▼"} {abs(day_chg):.2f}%</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:rgba(160,176,208,.32);line-height:1.7;">'
        f'<div>Sector: {sector}</div><div>Mkt Cap: {mktcap_s}</div>'
        f'<div>52W: {w52_l:.2f}–{w52_h:.2f} ({w52_pct:.0f}%)</div></div></div>',
        unsafe_allow_html=True
    )

    _nav()
    active = st.session_state.get("t5_active", "5.1")
    st.markdown("<div style='margin-top:6px;'>", unsafe_allow_html=True)
    try:
        if   active == "5.1": render_5_1_chips_daytrade(symbol, h1, info)
        elif active == "5.2": render_5_2_breakout_revenue(symbol, h1, info)
        elif active == "5.3": _s53(h1, symbol)
        elif active == "5.4": render_5_4_value_river(symbol, info, h3)
        elif active == "5.5": render_5_5_etf_command(symbol, info, h1)
        elif active == "5.6": _s56()
        else:                  render_5_1_chips_daytrade(symbol, h1, info)
    except Exception as exc:
        st.toast(f"❌ Module {active} Error: {exc}", icon="💀")
        with st.expander("🔍 Debug"):
            st.code(traceback.format_exc())
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f'<div class="t5-foot">Titan Universal Market Analyzer V800 · Niche Market Fusion · '
        f'DayTrade+CMF · RevSurge+Squeeze · PE River · Mine Sweeper · ETF Command · '
        f'{symbol} · {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    render()
