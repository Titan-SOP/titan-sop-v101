# ui_desktop/tab5_wiki.py
# Titan OS V700 — Tab 5: 通用市場分析儀 (Universal Market Analyzer)
# ╔══════════════════════════════════════════════════════════════════════╗
# ║  V700: Tactical Edition — Toast · Typewriter · Dialog · 13F Rebuilt ║
# ║  5.1 籌碼+CMF+RSI  5.2 Squeeze+MACD  5.3 ATR詳解  5.4 DDM+Graham   ║
# ║  5.5 13F REBUILT — Multi-source · Normalized · ARK  5.6 Codex       ║
# ╚══════════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
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
@st.dialog("🔰 戰術指導 Mode — Titan V700")
def show_guide_modal():
    st.markdown("""
### 指揮官，歡迎進入 Titan 市場情報戰區

**6大分析模組**：
- 🕵️ **5.1 籌碼K線** — VWAP / OBV / CMF / RSI · 追蹤法人留下的量能腳印
- 🚀 **5.2 起漲偵測** — Squeeze Momentum + MACD · 找出爆發前的壓縮點
- ⚡ **5.3 權證小哥** — ATR波幅 + 凱利公式 · 最大化風報比
- 🚦 **5.4 艾蜜莉** — DDM / Graham / PE百分位 · 內在價值評估
- 🐋 **5.5 13F巨鯨** — SEC 13F機構持倉 + ARK 6 ETF · 跟隨聰明錢
- 📜 **5.6 戰略百科** — CB四大套利窗口 · 進出場SOP · CBAS引擎

**操作方式**：點擊上方 6 個板塊切換模組。每個模組均有**第一性原理解析**，
不只告訴你看什麼，更告訴你背後的邏輯。

**狀態燈號**：🟢 買入 / 🟡 觀望 / 🔴 警戒 — 隨時留意各模組的動能方向與籌碼評分。

---
*建議：從 5.1 籌碼K線 入手熟悉介面，再依需求切換。*
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
.whale-row{display:flex;align-items:center;gap:12px;padding:12px 16px;background:rgba(255,255,255,.018);border:1px solid rgba(255,255,255,.06);border-radius:10px;margin-bottom:6px;}
.w-rank{font-family:var(--f-o);font-size:11px;min-width:28px;letter-spacing:1px;}
.w-name{font-family:var(--f-b);font-size:16px;font-weight:700;color:rgba(0,245,255,.85);flex:1;}
.w-badge{font-family:var(--f-o);font-size:9px;padding:2px 7px;border-radius:4px;letter-spacing:1px;}
.w-shares{font-family:var(--f-m);font-size:12px;color:rgba(160,176,208,.55);min-width:90px;text-align:right;}
.w-pct{font-family:var(--f-m);font-size:12px;color:rgba(0,255,127,.65);min-width:65px;text-align:right;}
.w-chg{font-family:var(--f-m);font-size:12px;min-width:70px;text-align:right;}
.ark-row{display:flex;align-items:center;gap:14px;padding:14px 18px;border-radius:10px;margin-bottom:6px;border:1px solid;}
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
        try:
            holders = tk.institutional_holders
            if holders is None: holders = pd.DataFrame()
        except Exception:
            holders = pd.DataFrame()
        try:
            mf_holders = tk.mutualfund_holders
            if mf_holders is None: mf_holders = pd.DataFrame()
        except Exception:
            mf_holders = pd.DataFrame()
        return h1, h3, info, holders, mf_holders, None
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame(), {}, pd.DataFrame(), pd.DataFrame(), str(e)


# ARK ETF holdings fetcher
_ARK_ETFS = {
    "ARKK": ("ARK Innovation ETF",       "#00F5FF"),
    "ARKQ": ("ARK Autonomous & Robotics", "#00FF7F"),
    "ARKW": ("ARK Next Gen Internet",     "#FFD700"),
    "ARKG": ("ARK Genomic Revolution",    "#FF9A3C"),
    "ARKF": ("ARK Fintech Innovation",    "#B77DFF"),
    "ARKX": ("ARK Space Exploration",     "#FF3131"),
}

@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_ark_holdings(symbol: str) -> dict:
    """
    Fetch ARK ETF holdings from ARK's public CSV API.
    Returns dict: {fund_ticker: {"name":str, "shares":float, "weight":float, "value":float}}
    """
    results = {}
    # Normalize: strip .TW/.TWO for matching
    sym_clean = symbol.upper().replace(".TW","").replace(".TWO","")

    ark_csv_base = "https://ark-funds.com/wp-content/uploads/funds-etf-csv/"
    ark_csv_names = {
        "ARKK": "ARK_INNOVATION_ETF_ARKK_HOLDINGS.csv",
        "ARKQ": "ARK_AUTONOMOUS_TECHNOLOGY_&_ROBOTICS_ETF_ARKQ_HOLDINGS.csv",
        "ARKW": "ARK_NEXT_GENERATION_INTERNET_ETF_ARKW_HOLDINGS.csv",
        "ARKG": "ARK_GENOMIC_REVOLUTION_ETF_ARKG_HOLDINGS.csv",
        "ARKF": "ARK_FINTECH_INNOVATION_ETF_ARKF_HOLDINGS.csv",
        "ARKX": "ARK_SPACE_EXPLORATION_&_INNOVATION_ETF_ARKX_HOLDINGS.csv",
    }

    for fund, csv_name in ark_csv_names.items():
        try:
            url = ark_csv_base + csv_name
            resp = requests.get(url, timeout=8)
            if resp.status_code != 200:
                continue
            lines = resp.text.strip().split("\n")
            # Find header
            header_idx = 0
            for i, line in enumerate(lines):
                if "ticker" in line.lower() or "symbol" in line.lower():
                    header_idx = i
                    break
            df = pd.read_csv(
                __import__("io").StringIO("\n".join(lines[header_idx:])),
                on_bad_lines="skip"
            )
            df.columns = [c.strip().lower() for c in df.columns]
            # Find ticker column
            ticker_col = None
            for c in df.columns:
                if c in ["ticker","symbol"]: ticker_col = c; break
            if ticker_col is None:
                continue
            df[ticker_col] = df[ticker_col].astype(str).str.strip().str.upper()
            match = df[df[ticker_col] == sym_clean]
            if match.empty:
                continue
            row = match.iloc[0]
            # Parse fields
            def _sv(keys):
                for k in keys:
                    for col in df.columns:
                        if k in col:
                            try: return float(str(row[col]).replace(",","").replace("%",""))
                            except: pass
                return None
            shares = _sv(["shares","quantity"])
            weight = _sv(["weight","% of portfolio","pct"])
            value  = _sv(["market value","value","mkt val"])
            results[fund] = {
                "name":   _ARK_ETFS[fund][0],
                "color":  _ARK_ETFS[fund][1],
                "shares": shares,
                "weight": weight,
                "value":  value,
            }
        except Exception:
            continue
    return results


# ════════════════════════════════════════════════════════════════════
# HERO + SEARCH
# ════════════════════════════════════════════════════════════════════
def _hero(symbol: str):
    st.markdown(f"""
<div class="t5-hero">
  <div class="t5-hero-label">titan os v600 · universal market analyzer</div>
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
    """First-principles explanation box with Valkyrie AI Typewriter (st.write_stream)."""
    key_html = f'<div class="t5-explain-key">{keys}</div>' if keys else ""
    st.markdown(f"""
<div class="t5-explain" style="border-left-color:{color}44;background:rgba(0,0,0,.2);">
  <div class="t5-explain-title" style="color:{color};">▸ {title}</div>
  <div class="t5-explain-body">""", unsafe_allow_html=True)
    # 🎯 FEATURE 3: Valkyrie AI Typewriter — streams word-by-word
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
        if str(c).lower() in ["date","datetime","index"]:
            df.rename(columns={c: "Date"}, inplace=True); break
    if "Date" not in df.columns:
        df["Date"] = df.index
    df["Date"] = pd.to_datetime(df["Date"])
    return df


# ════════════════════════════════════════════════════════════════════
# 5.1  籌碼K線  CHIP MASTER
# First Principle: 法人買賣留下量的腳印，價格是果，量才是因
# ════════════════════════════════════════════════════════════════════
def _s51(hist: pd.DataFrame, info: dict, symbol: str):
    _hd("5.1","🕵️ 主力籌碼透視 (Smart Money Flow)",
        "VWAP20/50 · OBV · CMF · RSI · Smart Money Score","#00F5FF")
    if hist.empty: st.toast("⚠️ 無歷史數據，請確認代號", icon="⚠️"); return

    _explain(
        "第一性原理：主力籌碼分析",
        "股價是供需的結果，而非原因。機構法人在建倉時，必然在價量上留下痕跡。"
        "VWAP（量加權平均價）是機構執行的基準線：股價長期站上VWAP意味法人持續買進。"
        "OBV（量能累計）把每天的成交量依漲跌方向累加，斜率向上代表資金淨流入。"
        "CMF（Chaikin金錢流）衡量21天內買賣壓力，正值=多頭控盤，負值=空頭控盤。",
        "▸ VWAP 站上 = 法人基準線確認  ▸ OBV 斜率 > 0 = 資金持續流入  ▸ CMF > +0.1 = 強勢買盤"
    )

    df = _prep(hist)
    df["TP"]     = (df["High"]+df["Low"]+df["Close"])/3
    df["VWAP"]   = (df["TP"]*df["Volume"]).rolling(20).sum()/df["Volume"].rolling(20).sum()
    df["VWAP50"] = (df["TP"]*df["Volume"]).rolling(50).sum()/df["Volume"].rolling(50).sum()

    # OBV
    obv=[0]
    for i in range(1,len(df)):
        d=df["Volume"].iloc[i]
        obv.append(obv[-1]+d if df["Close"].iloc[i]>df["Close"].iloc[i-1]
                   else obv[-1]-d if df["Close"].iloc[i]<df["Close"].iloc[i-1] else obv[-1])
    df["OBV"]=obv
    df["OBV_MA"]=df["OBV"].rolling(20).mean()

    # CMF (Chaikin Money Flow, 21-day)
    df["MFM"]=((df["Close"]-df["Low"])-(df["High"]-df["Close"]))/(df["High"]-df["Low"]).replace(0,np.nan)
    df["MFV"]=df["MFM"]*df["Volume"]
    df["CMF"]=df["MFV"].rolling(21).sum()/df["Volume"].rolling(21).sum()

    # RSI 14
    delta=df["Close"].diff()
    gain=delta.clip(lower=0).rolling(14).mean()
    loss=(-delta.clip(upper=0)).rolling(14).mean()
    rs=gain/(loss.replace(0,np.nan))
    df["RSI"]=100-100/(1+rs)

    cp  =float(df["Close"].iloc[-1])
    vwap=float(df["VWAP"].iloc[-1]) if not pd.isna(df["VWAP"].iloc[-1]) else cp
    v50 =float(df["VWAP50"].iloc[-1]) if not pd.isna(df["VWAP50"].iloc[-1]) else cp
    obv_c=float(df["OBV"].iloc[-1])
    obv_p=float(df["OBV"].iloc[-21]) if len(df)>21 else float(df["OBV"].iloc[0])
    cmf_v=float(df["CMF"].iloc[-1]) if not pd.isna(df["CMF"].iloc[-1]) else 0
    rsi_v=float(df["RSI"].iloc[-1]) if not pd.isna(df["RSI"].iloc[-1]) else 50
    vwap_dev=(cp-vwap)/vwap*100 if vwap>0 else 0
    obv_up=obv_c>obv_p

    # Smart Money Score (0-100)
    score=50
    score+=min(20,vwap_dev*2) if vwap_dev>0 else max(-20,vwap_dev*2)
    score+=15 if obv_up else -15
    score+=15 if cmf_v>0.05 else (0 if cmf_v>-0.05 else -15)
    score=int(max(0,min(100,score)))
    sc="#00FF7F" if score>=60 else ("#FFD700" if score>=40 else "#FF3131")
    rsi_c="#FF3131" if rsi_v>70 else ("#00FF7F" if rsi_v<30 else "#FFD700")
    cmf_c="#00FF7F" if cmf_v>0.05 else ("#FF3131" if cmf_v<-0.05 else "#888")

    c1,c2,c3,c4,c5,c6=st.columns(6)
    _kpi(c1,"股價",f"{cp:.2f}","","#00F5FF")
    _kpi(c2,"VWAP 20日",f"{vwap:.2f}",f"偏離 {vwap_dev:+.1f}%","#00FF7F" if cp>vwap else "#FF3131")
    _kpi(c3,"VWAP 50日",f"{v50:.2f}",f"{'上方✓' if cp>v50 else '下方✗'}","#00FF7F" if cp>v50 else "#FF6060")
    _kpi(c4,"OBV方向","累積▲" if obv_up else "派發▼","Smart Money","#00FF7F" if obv_up else "#FF3131")
    _kpi(c5,"CMF(21)",f"{cmf_v:+.3f}",">+0.1=強買盤",cmf_c)
    _kpi(c6,"籌碼評分",f"{score}","0弱→100強",sc)
    st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)

    if score>=60:   _banner("🟢 法人多頭佈局 ACCUMULATION",f"VWAP偏離{vwap_dev:+.1f}% · OBV上升 · CMF{cmf_v:+.3f} · Score {score}/100","#00FF7F")
    elif score>=40: _banner("🟡 法人觀望 NEUTRAL",f"籌碼混沌，VWAP偏離 {vwap_dev:+.1f}% · CMF{cmf_v:+.3f}","#FFD700")
    else:           _banner("🔴 法人賣壓 DISTRIBUTION",f"VWAP偏離{vwap_dev:+.1f}% · OBV下降 · CMF{cmf_v:+.3f} · Score {score}/100","#FF3131")

    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    _sec28("PRICE × VWAP OVERLAY")
    _sec26("青色=收盤價 · 金色=VWAP20 · 橙色=VWAP50 — 站在均線上方代表法人買入成本在下方","rgba(160,176,208,.45)")

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

    col_obv, col_rsi = st.columns(2)
    with col_obv:
        _sec28("ON-BALANCE VOLUME")
        _sec26("紫=OBV · 橙=均線 · 斜率向上=法人持續買進","rgba(160,176,208,.45)")
        do=df[["Date","OBV","OBV_MA"]].dropna().tail(tail)
        dom=do.melt("Date",var_name="Series",value_name="Value")
        ch2=alt.Chart(dom).mark_line(strokeWidth=1.6).encode(
            x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            y=alt.Y("Value:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            color=alt.Color("Series:N",scale=alt.Scale(domain=["OBV","OBV_MA"],range=["#B77DFF","#FF9A3C"]),
                            legend=alt.Legend(labelColor="#aaa",titleColor="#aaa",orient="top-right"))
        ).properties(background="transparent",height=200).configure_view(strokeOpacity=0)
        st.altair_chart(ch2,use_container_width=True)

    with col_rsi:
        _sec28("RSI 14 + CMF 21")
        _sec26("RSI<30超賣 · RSI>70超買 · CMF正值=買盤主導","rgba(160,176,208,.45)")
        dr=df[["Date","RSI","CMF"]].dropna().tail(tail)
        rsi_chart=alt.Chart(dr).mark_line(color=rsi_c,strokeWidth=1.6).encode(
            x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            y=alt.Y("RSI:Q",scale=alt.Scale(domain=[0,100]),axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a",title="RSI"))
        )
        ob_line=alt.Chart(pd.DataFrame({"y":[70]})).mark_rule(strokeDash=[4,4],color="#FF3131",strokeWidth=1).encode(y="y:Q")
        os_line=alt.Chart(pd.DataFrame({"y":[30]})).mark_rule(strokeDash=[4,4],color="#00FF7F",strokeWidth=1).encode(y="y:Q")
        st.altair_chart(alt.layer(rsi_chart,ob_line,os_line).properties(background="transparent",height=120).configure_view(strokeOpacity=0),use_container_width=True)
        cmf_chart=alt.Chart(dr).mark_line(color="#00F5FF",strokeWidth=1.6).encode(
            x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            y=alt.Y("CMF:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a",title="CMF"))
        )
        zero=alt.Chart(pd.DataFrame({"y":[0]})).mark_rule(strokeDash=[3,3],color="#555",strokeWidth=1).encode(y="y:Q")
        st.altair_chart(alt.layer(cmf_chart,zero).properties(background="transparent",height=80).configure_view(strokeOpacity=0),use_container_width=True)

    _sec28("VOLUME PROFILE (90D)")
    _sec26("綠柱=收漲 · 紅柱=收跌 · 金色虛線=20日均量 — 量增價漲才是真突破","rgba(160,176,208,.45)")
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
# First Principle: 能量在壓縮中積累，方向在解放時確定
# ════════════════════════════════════════════════════════════════════
def _s52(hist: pd.DataFrame, symbol: str):
    _hd("5.2","🚀 動能突破偵測 (Momentum Ignition)",
        "Bollinger Squeeze · Keltner · BW% · MACD · Momentum Histogram","#00FF7F")
    if hist.empty: st.toast("⚠️ 無歷史數據，請確認代號", icon="⚠️"); return

    _explain(
        "第一性原理：起漲動能偵測",
        "波動率不是固定的，它像彈簧一樣壓縮再釋放。布林帶（BB）衡量短期波動，"
        "凱特納通道（KC）衡量真實波幅。當BB收縮到KC內側 = 擠壓（Squeeze）= 彈簧被壓緊。"
        "動量方向（MOM）決定彈出方向：正值=往上爆，負值=往下崩。"
        "MACD確認中期趨勢，RSI確認超買超賣邊界。",
        "▸ BB在KC內 + MOM向上 = 🔥多頭爆發候選  ▸ BW<12% = 歷史低波動 = 蓄能完成  ▸ MACD柱線翻正 = 動能換手",
        "#00FF7F"
    )

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
    df["MOM"]=df["Close"]-((df["High"].rolling(20).max()+df["Low"].rolling(20).min())/2+df["BB_mid"])/2

    # MACD
    ema12=df["Close"].ewm(span=12,adjust=False).mean()
    ema26=df["Close"].ewm(span=26,adjust=False).mean()
    df["MACD"]=ema12-ema26
    df["Signal"]=df["MACD"].ewm(span=9,adjust=False).mean()
    df["Hist"]=df["MACD"]-df["Signal"]

    bw_now   =float(df["BW"].iloc[-1]) if not df["BW"].isna().all() else None
    bw_6mlo  =float(df["BW"].tail(126).min()) if len(df)>=20 else None
    sq_now   =bool(df["Squeeze"].iloc[-1]) if not df["Squeeze"].isna().all() else False
    mom_now  =float(df["MOM"].iloc[-1]) if not df["MOM"].isna().all() else 0
    sq_days  =int(df["Squeeze"].tail(30).sum()) if not df["Squeeze"].isna().all() else 0
    hist_now =float(df["Hist"].iloc[-1]) if not df["Hist"].isna().all() else 0
    cp=float(df["Close"].iloc[-1])

    c1,c2,c3,c4,c5=st.columns(5)
    _kpi(c1,"股價",f"{cp:.2f}","","#00F5FF")
    _kpi(c2,"帶寬 BW%",f"{bw_now:.1f}%" if bw_now else "N/A","<12%=蓄勢完成","#00FF7F" if bw_now and bw_now<12 else "#FFD700")
    _kpi(c3,"Squeeze","🔥擠壓中" if sq_now else "⬜無擠壓",f"連續{sq_days}日","#00FF7F" if sq_now else "#888")
    _kpi(c4,"動能方向","▲ 多頭" if mom_now>0 else "▼ 空頭",f"MOM {mom_now:+.2f}","#00FF7F" if mom_now>0 else "#FF3131")
    _kpi(c5,"MACD柱","▲ 擴大" if hist_now>0 else "▼ 收縮",f"Hist {hist_now:+.4f}","#00FF7F" if hist_now>0 else "#FF3131")
    st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)

    if sq_now and mom_now>0:   _banner("🔥 蓄勢待發 — 多頭爆發",f"BB inside KC · BW={bw_now:.1f}% · 連擠{sq_days}日 · 動能向上","#00FF7F","🚀")
    elif sq_now and mom_now<0: _banner("⚠️ 擠壓出現 — 空頭方向",f"BB inside KC · BW={bw_now:.1f}% · 動能向下","#FF9A3C","⚠️")
    elif bw_now and bw_now<12: _banner("🟡 帶寬收窄 — 等待KC確認",f"BW={bw_now:.1f}% · 接近歷史低波動，隨時可能爆發","#FFD700")
    else:                      _banner("⬜ 正常震盪 — 持續監控",f"BW={bw_now:.1f}% · 無擠壓訊號","#888")

    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    _sec28("BOLLINGER BANDS × KELTNER CHANNEL")
    _sec26("綠帶=BB · 橙帶=KC · BB縮進KC內部=擠壓 · 青線=收盤價 — 擠壓越久爆發越猛","rgba(160,176,208,.45)")

    dp=df[["Date","Close","BB_up","BB_dn","BB_mid","KC_up","KC_dn"]].dropna().tail(120)
    base=alt.Chart(dp)
    bands=[
        base.mark_line(color="#00FF7F",strokeWidth=1,opacity=0.5).encode(x="Date:T",y="BB_up:Q"),
        base.mark_line(color="#00FF7F",strokeWidth=1,opacity=0.5).encode(x="Date:T",y="BB_dn:Q"),
        base.mark_line(color="#FF9A3C",strokeWidth=1,strokeDash=[3,3],opacity=0.5).encode(x="Date:T",y="KC_up:Q"),
        base.mark_line(color="#FF9A3C",strokeWidth=1,strokeDash=[3,3],opacity=0.5).encode(x="Date:T",y="KC_dn:Q"),
        base.mark_line(color="#00F5FF",strokeWidth=1.8).encode(x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),y=alt.Y("Close:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")))
    ]
    st.altair_chart(alt.layer(*bands).properties(background="transparent",height=250).configure_view(strokeOpacity=0),use_container_width=True)

    col_mom, col_macd = st.columns(2)
    with col_mom:
        _sec28("MOMENTUM HISTOGRAM")
        _sec26("正值=多頭動能 · 負值=空頭動能","rgba(160,176,208,.45)")
        dm=df[["Date","MOM"]].dropna().tail(120).copy()
        dm["clr"]=dm["MOM"].apply(lambda x:"#00FF7F" if x>=0 else "#FF6060")
        mch=alt.Chart(dm).mark_bar(opacity=0.8).encode(
            x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            y=alt.Y("MOM:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            color=alt.Color("clr:N",scale=None,legend=None)
        ).properties(background="transparent",height=180).configure_view(strokeOpacity=0)
        st.altair_chart(mch,use_container_width=True)
    with col_macd:
        _sec28("MACD 動能確認")
        _sec26("MACD柱翻正=動能換手 · 金叉=買進確認","rgba(160,176,208,.45)")
        dmacd=df[["Date","MACD","Signal","Hist"]].dropna().tail(120).copy()
        dmacd["clr"]=dmacd["Hist"].apply(lambda x:"#00FF7F" if x>=0 else "#FF6060")
        hist_chart=alt.Chart(dmacd).mark_bar(opacity=0.7).encode(
            x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            y=alt.Y("Hist:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            color=alt.Color("clr:N",scale=None,legend=None)
        )
        macd_l=alt.Chart(dmacd).mark_line(color="#00F5FF",strokeWidth=1.2).encode(x="Date:T",y="MACD:Q")
        sig_l=alt.Chart(dmacd).mark_line(color="#FF9A3C",strokeWidth=1.2,strokeDash=[3,3]).encode(x="Date:T",y="Signal:Q")
        st.altair_chart(alt.layer(hist_chart,macd_l,sig_l).properties(background="transparent",height=180).configure_view(strokeOpacity=0),use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# 5.3  權證小哥  TICK MASTER
# First Principle: 波動率是資產的真實風險定價，ATR是行情的呼吸頻率
# ════════════════════════════════════════════════════════════════════
def _s53(hist: pd.DataFrame, symbol: str):
    _hd("5.3","⚡ 短線操盤儀 (Tactical Trader)",
        "ATR波動 · 相對量能 · 布林通道位置 · 短線趨勢評分","#FFD700")
    if hist.empty: st.toast("⚠️ 無歷史數據，請確認代號", icon="⚠️"); return

    _explain(
        "第一性原理：短線波動管理",
        "ATR（Average True Range）是行情的「呼吸幅度」。每日ATR代表市場願意移動多少距離。"
        "相對成交量（RelVol）= 今日成交量 ÷ 20日均量，超過2倍代表異常資金進場。"
        "布林帶位置（%B）= (收盤-下軌)÷(上軌-下軌)，>0.8接近上軌=短線超買，<0.2接近下軌=超賣。"
        "短線進場的最佳條件：ATR適中（不過高不過低）+ RelVol放大 + %B從低點回升。",
        "▸ ATR% 1-3% = 最佳短線節奏  ▸ RelVol > 2× = 主力進場訊號  ▸ %B 從0.2上穿0.4 = 轉強",
        "#FFD700"
    )

    df=_prep(hist)
    df["TR"]=np.maximum(df["High"]-df["Low"],np.maximum(abs(df["High"]-df["Close"].shift(1)),abs(df["Low"]-df["Close"].shift(1))))
    df["ATR14"]=df["TR"].rolling(14).mean()
    df["ATR21"]=df["TR"].rolling(21).mean()
    df["AvgVol"]=df["Volume"].rolling(20).mean()
    df["RelVol"]=df["Volume"]/df["AvgVol"].replace(0,np.nan)
    df["BB_mid"]=df["Close"].rolling(20).mean()
    df["BB_std"]=df["Close"].rolling(20).std()
    df["BB_up"]=df["BB_mid"]+2*df["BB_std"]
    df["BB_dn"]=df["BB_mid"]-2*df["BB_std"]
    df["PctB"]=(df["Close"]-df["BB_dn"])/(df["BB_up"]-df["BB_dn"]).replace(0,np.nan)
    df["R1"]=df["Close"].pct_change(1)*100
    df["R5"]=df["Close"].pct_change(5)*100
    df["R20"]=df["Close"].pct_change(20)*100

    cp  =float(df["Close"].iloc[-1])
    atr =float(df["ATR14"].iloc[-1]) if not pd.isna(df["ATR14"].iloc[-1]) else 0
    atr_pct=atr/cp*100 if cp>0 else 0
    rv  =float(df["RelVol"].iloc[-1]) if not pd.isna(df["RelVol"].iloc[-1]) else 1
    pctb=float(df["PctB"].iloc[-1]) if not pd.isna(df["PctB"].iloc[-1]) else 0.5
    r1  =float(df["R1"].iloc[-1]) if not pd.isna(df["R1"].iloc[-1]) else 0
    r5  =float(df["R5"].iloc[-1]) if not pd.isna(df["R5"].iloc[-1]) else 0
    r20 =float(df["R20"].iloc[-1]) if not pd.isna(df["R20"].iloc[-1]) else 0

    rv_color="#FF3131" if rv>3 else ("#FF9A3C" if rv>2 else ("#FFD700" if rv>1.5 else "#00FF7F"))
    pctb_c="#FF3131" if pctb>0.8 else ("#00FF7F" if pctb<0.2 else "#FFD700")

    c1,c2,c3,c4,c5=st.columns(5)
    _kpi(c1,"股價",f"{cp:.2f}","","#00F5FF")
    _kpi(c2,"ATR 14",f"{atr:.2f}",f"波動率 {atr_pct:.1f}%","#FFD700" if atr_pct<3 else "#FF3131")
    _kpi(c3,"相對量能",f"{rv:.1f}×","1=均量","#00FF7F" if 1.5<rv<3 else rv_color)
    _kpi(c4,"布林位置 %B",f"{pctb:.2f}",">0.8超買 <0.2超賣",pctb_c)
    _kpi(c5,"20日漲跌",f"{r20:+.1f}%","月度動能","#00FF7F" if r20>0 else "#FF3131")
    st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)

    if rv>2 and r1>0:   _banner("⚡ 放量上攻 BULLISH BREAKOUT",f"RelVol {rv:.1f}× · 今日+{r1:.1f}% · %B={pctb:.2f}","#FFD700","📈")
    elif rv>2 and r1<0: _banner("⚠️ 放量殺跌 BEARISH FLUSH",f"RelVol {rv:.1f}× · 今日{r1:.1f}% · 注意支撐","#FF3131","📉")
    elif atr_pct<1:     _banner("💤 超低波動 COMPRESSION",f"ATR={atr_pct:.1f}% · 市場靜止 · 等待放量突破","#888")
    else:               _banner("📊 正常節奏 NORMAL RANGE",f"ATR={atr_pct:.1f}% · RelVol={rv:.1f}× · 持續觀察","#FFD700")

    _sec28("RELATIVE VOLUME + %B 位置")
    _sec26("橙=RelVol(左軸) · 青=%B(右軸) · %B>0.8超買 <0.2超賣","rgba(160,176,208,.45)")
    tail=90
    drv=df[["Date","RelVol","PctB"]].dropna().tail(tail)
    rv_chart=alt.Chart(drv).mark_bar(color="#FF9A3C",opacity=0.7).encode(
        x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
        y=alt.Y("RelVol:Q",axis=alt.Axis(labelColor="#FF9A3C",gridColor="#1a1a2a",title="RelVol"))
    )
    pctb_chart=alt.Chart(drv).mark_line(color="#00F5FF",strokeWidth=1.6).encode(
        x="Date:T",
        y=alt.Y("PctB:Q",axis=alt.Axis(labelColor="#00F5FF",title="%B"),scale=alt.Scale(domain=[0,1]))
    )
    ob=alt.Chart(pd.DataFrame({"y":[0.8]})).mark_rule(strokeDash=[3,3],color="#FF3131",strokeWidth=1).encode(y=alt.Y("y:Q",axis=None))
    os_=alt.Chart(pd.DataFrame({"y":[0.2]})).mark_rule(strokeDash=[3,3],color="#00FF7F",strokeWidth=1).encode(y=alt.Y("y:Q",axis=None))
    st.altair_chart(alt.layer(rv_chart).resolve_scale(y="independent").properties(background="transparent",height=220).configure_view(strokeOpacity=0),use_container_width=True)
    st.altair_chart(alt.layer(pctb_chart,ob,os_).properties(background="transparent",height=140).configure_view(strokeOpacity=0),use_container_width=True)

    _sec28("SHORT-TERM RETURNS")
    _sec26("今日/本週/本月漲跌幅 — 三個時間框架判斷短線力道","rgba(160,176,208,.45)")
    gm=[("ATR波動評級","🔴 高波動" if atr_pct>3 else ("🟡 中波動" if atr_pct>1.5 else "🟢 低波動"),f"每日ATR {atr_pct:.1f}%","#FFD700"),
        ("量能狀態","⚠️ 爆量警戒" if rv>3 else ("⚡ 量能放大" if rv>1.5 else "✅ 量能正常"),f"RelVol {rv:.1f}×",rv_color),
        ("今日趨勢",f"{'▲' if r1>0 else '▼'} {abs(r1):.1f}%",f"日漲跌","#00FF7F" if r1>0 else "#FF3131"),
        ("週漲跌",f"{'▲' if r5>0 else '▼'} {abs(r5):.1f}%",f"5日動能","#00FF7F" if r5>2 else ("#888" if abs(r5)<2 else "#FF3131")),
    ]
    gc1,gc2,gc3,gc4=st.columns(4)
    for col,(title,val,sub,c) in zip([gc1,gc2,gc3,gc4],gm):
        col.markdown(f'<div style="padding:16px;background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.05);border-top:2px solid {c};border-radius:10px;"><div style="font-family:\'Rajdhani\',sans-serif;font-size:14px;font-weight:700;color:{c};margin-bottom:5px;">{title}</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:26px;color:#FFF;line-height:1.1;">{val}</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:rgba(160,176,208,.4);margin-top:4px;">{sub}</div></div>',unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# 5.4  艾蜜莉定存  VALUE QUEEN
# First Principle: 股票的價值=未來所有現金流的現值，安全邊際=買在折扣
# ════════════════════════════════════════════════════════════════════
def _s54(hist3y: pd.DataFrame, info: dict, symbol: str):
    _hd("5.4","🚦 價值紅綠燈 (Valuation Traffic Light)",
        "3Y PE百分位 · DDM股息折現 · Graham公式 · P/B · P/S","#FF9A3C")

    _explain(
        "第一性原理：內在價值估算",
        "股票的公平價值等於未來所有自由現金流折現回今日的總和。PE歷史百分位告訴你，"
        "相對於過去三年，現在的定價是貴還是便宜。DDM（股息折現）用股息成長來計算理論價值。"
        "Graham公式（葛拉漢）= √(22.5 × EPS × BVPS)，是本益比×股價淨值比的幾何平均，"
        "給出一個保守的安全邊際價格。低於Graham值買入 = 雙重保護。",
        "▸ PE < 25th百分位 = 🟢 歷史低估  ▸ 股價 < Graham值 = 安全邊際存在  ▸ DDM值 > 股價 = 低估",
        "#FF9A3C"
    )

    eps=info.get("trailingEps") or info.get("forwardEps")
    pe_trail=info.get("trailingPE"); pe_fwd=info.get("forwardPE")
    pb=info.get("priceToBook"); ps=info.get("priceToSalesTrailing12Months")
    div_y=info.get("dividendYield",0) or 0; roe=info.get("returnOnEquity",0) or 0
    bvps=info.get("bookValue",0) or 0
    cp=info.get("currentPrice") or info.get("regularMarketPrice") or \
       (float(hist3y["Close"].iloc[-1]) if not hist3y.empty else 0)

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

    # DDM
    ddm_val=None
    if div_y>0 and cp>0:
        D=cp*div_y; g=min(roe*0.5,0.08) if roe>0 else 0.03; r=0.10
        if r>g: ddm_val=D/(r-g)

    # Graham Number
    graham_val=None
    if eps and float(eps)>0 and bvps>0:
        graham_val=float(np.sqrt(22.5*float(eps)*bvps))

    sm={"cheap":("🟢 便宜 CHEAP","#00FF7F","建議逢低佈局"),
        "fair":("🟡 合理 FAIR","#FFD700","持有觀望"),
        "expensive":("🔴 昂貴 EXPENSIVE","#FF3131","謹慎操作"),
        "neutral":("⬜ 無PE數據","#888888","改看P/B · P/S")}
    sig_lbl,sig_c,sig_desc=sm[signal]

    c1,c2,c3,c4,c5,c6=st.columns(6)
    _kpi(c1,"股價",f"{cp:.2f}" if cp else "N/A","","#00F5FF")
    _kpi(c2,"EPS (TTM)",f"{float(eps):.2f}" if eps else "N/A","每股盈餘","#FFD700")
    _kpi(c3,"P/E",f"{use_pe:.1f}×" if use_pe else "N/A","本益比",sig_c)
    _kpi(c4,"P/B",f"{pb:.2f}×" if pb else "N/A","股價淨值","#B77DFF")
    _kpi(c5,"DDM估值",f"{ddm_val:.2f}" if ddm_val else "N/A",
         f"{'低估✓' if ddm_val and cp<ddm_val else '高估✗' if ddm_val else '無配息'}",
         "#00FF7F" if ddm_val and cp<ddm_val else "#FF6060")
    _kpi(c6,"Graham值",f"{graham_val:.2f}" if graham_val else "N/A",
         f"{'低估✓' if graham_val and cp<graham_val else '高估✗' if graham_val else 'N/A'}",
         "#00FF7F" if graham_val and cp and cp<graham_val else "#FF6060")
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

    st.markdown(f'<div style="margin:12px 0;padding:18px 24px;background:rgba(0,0,0,.2);border:1px solid {sig_c}33;border-left:5px solid {sig_c};border-radius:0 12px 12px 0;text-align:center;"><div style="font-family:\'Rajdhani\',sans-serif;font-size:30px;font-weight:800;color:{sig_c};">{sig_lbl}</div><div style="font-family:\'Rajdhani\',sans-serif;font-size:18px;color:rgba(180,195,220,.65);margin-top:8px;">{sig_desc} &nbsp;·&nbsp; PE: {f"{use_pe:.1f}" if use_pe else "N/A"} &nbsp;·&nbsp; P/B: {f"{pb:.2f}" if pb else "N/A"} &nbsp;·&nbsp; Div: {div_y*100:.2f}% &nbsp;·&nbsp; Graham: {f"{graham_val:.2f}" if graham_val else "N/A"}</div></div>',unsafe_allow_html=True)

    if not hist3y.empty and eps and float(eps)>0:
        _sec28("3Y HISTORICAL P/E CHART")
        _sec26("橙線=PE走勢 · 虛線=25/50/75百分位 · 落在哪個區間決定燈號","rgba(160,176,208,.45)")
        dpe=hist3y.copy().reset_index()
        for c in dpe.columns:
            if str(c).lower() in ["date","datetime","index"]:
                dpe.rename(columns={c:"Date"},inplace=True); break
        if "Date" not in dpe.columns: dpe["Date"]=dpe.index
        dpe["PE"]=dpe["Close"]/float(eps)
        dpe=dpe[["Date","PE"]].dropna(); dpe=dpe[dpe["PE"]>0]
        pe_chart=alt.Chart(dpe).mark_line(color="#FF9A3C",strokeWidth=1.8).encode(
            x=alt.X("Date:T",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
            y=alt.Y("PE:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")))
        rules=[]
        if pe_25:
            for pv,pc,pn in[(pe_25,"#00FF7F","25th"),(pe_50,"#FFD700","50th"),(pe_75,"#FF3131","75th")]:
                rules.append(alt.Chart(pd.DataFrame({"y":[pv]})).mark_rule(strokeDash=[4,4],color=pc,strokeWidth=1,opacity=0.65).encode(y="y:Q"))
        st.altair_chart(alt.layer(pe_chart,*rules).properties(background="transparent",height=250).configure_view(strokeOpacity=0),use_container_width=True)
        if pe_25 and pe_75 and use_pe:
            pct_pos=min(100,max(0,(use_pe-pe_25)/(pe_75-pe_25+0.001)*100))
            c_pos="#FF3131" if pct_pos>80 else ("#FFD700" if pct_pos>40 else "#00FF7F")
            st.markdown(f'<div style="margin:12px 0;"><div style="font-family:\'Rajdhani\',sans-serif;font-size:18px;color:rgba(160,176,208,.5);margin-bottom:8px;">PE PERCENTILE GAUGE — 目前PE位於3年歷史的第 {pct_pos:.0f} 百分位</div><div style="background:rgba(255,255,255,.05);border-radius:20px;height:10px;position:relative;overflow:hidden;"><div style="position:absolute;left:0;top:0;height:100%;width:{pct_pos:.0f}%;background:linear-gradient(90deg,#00FF7F,{c_pos});border-radius:20px;"></div></div><div style="font-family:\'Orbitron\',sans-serif;font-size:12px;color:{c_pos};margin-top:6px;text-align:right;">{pct_pos:.0f}th PERCENTILE</div></div>',unsafe_allow_html=True)
    else:
        st.toast("💡 此標的無EPS數據（ETF/未獲利公司），顯示現有估值倍數", icon="💡")
        if pe_trail: st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:22px;color:#FFF;">Trailing P/E: <b>{pe_trail:.1f}×</b></div>',unsafe_allow_html=True)
        if pe_fwd:   st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:22px;color:#FFF;">Forward P/E: <b>{pe_fwd:.1f}×</b></div>',unsafe_allow_html=True)
        if ps:       st.markdown(f'<div style="font-family:Rajdhani,sans-serif;font-size:22px;color:#FFF;">P/S (TTM): <b>{ps:.2f}×</b></div>',unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# 5.5  13F巨鯨  WHALE WATCHER — FIRST PRINCIPLES REBUILD V700
# ────────────────────────────────────────────────────────────────────
# 根本問題診斷：
#   1. yfinance 各版本欄位名稱不一致 (% Out / pctHeld / PctHeld)
#   2. Yahoo Finance API 限速時 holders 可能回傳 None/空 DataFrame
#   3. 沒有多來源容錯機制，一旦 cache 拿到空資料就顯示「無數據」
#
# 第一性原則解法：
#   A. 獨立的 _normalize_inst() — 處理所有已知欄位名稱變體
#   B. _fetch_13f_robust(symbol) — 多方法輪詢（property + get_方法 + 直接 API）
#   C. _s55 內部呼叫 robust fetch，而非依賴外部傳入的可能為空的 cache
#   D. st.toast 通知每個資料來源的狀態
# ════════════════════════════════════════════════════════════════════

def _normalize_inst(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize institutional/mutual-fund holder DataFrame.
    Handles all known yfinance column name variants across versions:
      v0.1.x: Holder, Shares, Date Reported, % Out, Value
      v0.2.x: holder, shares, pctHeld, value, reportDate
      direct API: organization, position, pctHeld, value, reportDate
    """
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy().reset_index(drop=True)
    cm = {}
    for c in out.columns:
        cl = str(c).strip().lower()
        # Holder name — must check BEFORE generic "name" catches value/shares cols
        if (any(k == cl for k in ["holder","organization","fund","institution"]) or
            any(k in cl for k in ["holder","organization","fund","institution","name"])
            and "date" not in cl and "value" not in cl):
            if "Holder" not in cm.values():
                cm[c] = "Holder"
        # Shares / position (integer count)
        elif cl in ["shares","position","quantity"] or ("share" in cl and "%" not in cl and "pct" not in cl):
            if "Shares" not in cm.values():
                cm[c] = "Shares"
        # Market value in dollars
        elif "value" in cl or ("market" in cl and "cap" not in cl):
            if "Value" not in cm.values():
                cm[c] = "Value"
        # Percentage held  — catches "% Out", "pctHeld", "% held", "percentHeld"
        elif "%" in cl or "pct" in cl or "percent" in cl or "out" in cl:
            if "PctHeld" not in cm.values():
                cm[c] = "PctHeld"
        # Report date
        elif "date" in cl or "report" in cl or "filed" in cl:
            if "ReportDate" not in cm.values():
                cm[c] = "ReportDate"
    out.rename(columns=cm, inplace=True)
    for col in ["Holder", "Shares", "Value", "PctHeld"]:
        if col not in out.columns:
            out[col] = None
    return out


@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_13f_robust(symbol: str):
    """
    Multi-method 13F fetcher — tries every known yfinance access path.
    Returns: (inst_df, mf_df, source_label)

    Priority chain:
      1. tk.institutional_holders  (classic property, all versions)
      2. tk.get_institutional_holders()  (newer yfinance 0.2.x+)
      3. Direct Yahoo Finance v4 JSON API with crumb-less endpoint
      4. Empty DataFrame (display graceful empty state)
    """
    sym = symbol.upper()
    # For Taiwan stocks try base symbol too (strip .TW/.TWO)
    base = _re.sub(r"\.(TW|TWO)$", "", sym)
    candidates = [sym] if sym == base else [sym, base]

    inst_df = pd.DataFrame()
    mf_df   = pd.DataFrame()
    source  = "unavailable"

    for tsym in candidates:
        try:
            tk = yf.Ticker(tsym)

            # ── Method 1: classic property ─────────────────────────
            try:
                _d = tk.institutional_holders
                if _d is not None and not _d.empty:
                    inst_df = _d; source = f"yfinance ({tsym})"
            except Exception:
                pass

            # ── Method 2: .get_institutional_holders() — yfinance 0.2.x ──
            if inst_df.empty:
                try:
                    _d = tk.get_institutional_holders()
                    if _d is not None and not _d.empty:
                        inst_df = _d; source = f"yfinance.get ({tsym})"
                except Exception:
                    pass

            # ── Mutual fund holders ─────────────────────────────────
            try:
                _m = tk.mutualfund_holders
                if _m is not None and not _m.empty:
                    mf_df = _m
            except Exception:
                pass
            if mf_df.empty:
                try:
                    _m = tk.get_mutualfund_holders()
                    if _m is not None and not _m.empty:
                        mf_df = _m
                except Exception:
                    pass

            if not inst_df.empty:
                break  # data found — no need to try next symbol

        except Exception:
            continue

    # ── Method 3: Direct Yahoo Finance JSON API ─────────────────────
    # Tries the v4 holders endpoint directly (bypasses yfinance caching issues)
    if inst_df.empty:
        try:
            hdrs = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
                "Accept-Language": "en-US,en;q=0.9",
            }
            url = f"https://query2.finance.yahoo.com/v4/finance/holders/{base}"
            r = requests.get(url, headers=hdrs, timeout=12)
            if r.status_code == 200:
                data = r.json()
                raw_list = (data.get("holders", {})
                               .get("institutionOwnership", {})
                               .get("ownershipList", []))
                if raw_list:
                    rows = []
                    for item in raw_list:
                        def _rv(v):
                            return v.get("raw") if isinstance(v, dict) else v
                        def _fv(v):
                            return v.get("fmt") if isinstance(v, dict) else v
                        rows.append({
                            "Holder":     item.get("organization", "Unknown"),
                            "Shares":     _rv(item.get("position")),
                            "Value":      _rv(item.get("value")),
                            "PctHeld":    _rv(item.get("pctHeld")),
                            "ReportDate": _fv(item.get("reportDate", "")),
                        })
                    inst_df = pd.DataFrame(rows)
                    source  = "Yahoo Finance v4 API (direct)"
        except Exception:
            pass

    return _normalize_inst(inst_df), _normalize_inst(mf_df), source


def _s55(holders: pd.DataFrame, info: dict, symbol: str, mf_holders: pd.DataFrame = None):
    _hd("5.5","🐋 13F機構巨鯨 + ARK持倉 (Institutional Intelligence)",
        "SEC 13F · Top Institutions · Mutual Funds · ARK 6 ETFs · Concentration","#B77DFF")

    # ── 第一性原理說明（Valkyrie Typewriter）───────────────────
    _explain(
        "第一性原理：13F機構持倉情報",
        "美國SEC規定：任何管理資產超過1億美元的機構，必須在每季結束後45天內向SEC提交13F表格，"
        "公開所有美國上市股票的多頭持倉。這是全球最透明的「跟蹤巨鯨」工具。"
        "當貝萊德（BlackRock）、先鋒（Vanguard）、State Street等機構增持，代表長線資金認可這家公司。"
        "ARK Invest是最透明的主動型ETF，每日公布完整持倉，可以追蹤Cathie Wood的實際動向。",
        "▸ 機構持股>70% = 主流標的  ▸ 新增持倉 = 巨鯨初次建倉（最強訊號）  ▸ ARK持有 = 顛覆性科技認可",
        "#B77DFF"
    )

    # ── 取得資料 — 多方法容錯 ──────────────────────────────────
    # 優先使用傳入的 cache；如果是空的，立即啟動 robust 多方法抓取
    if holders is not None and not holders.empty:
        inst_df = _normalize_inst(holders)
        mf_df   = _normalize_inst(mf_holders) if mf_holders is not None else pd.DataFrame()
        data_source = "yfinance (cached)"
        st.toast(f"🐋 13F 資料已載入 — {len(inst_df)} 筆機構持倉", icon="✅")
    else:
        # 🎯 FEATURE 2: toast 通知正在重新抓取
        st.toast("⏳ yfinance cache 為空，啟動多方法抓取中…", icon="🔄")
        with st.spinner("🔍 13F 多方法抓取中（yfinance property → get方法 → 直接API）…"):
            inst_df, mf_df, data_source = _fetch_13f_robust(symbol)
        if not inst_df.empty:
            st.toast(f"✅ 13F 載入成功 — 來源：{data_source} · {len(inst_df)} 筆", icon="🐋")
        else:
            st.toast("⚠️ 無法取得13F數據（台股/小型股/API限流）", icon="⚠️")

    # ── 總覽 KPI ───────────────────────────────────────────────
    inst_pct    = info.get("institutionPercentHeld")
    insider_pct = info.get("heldPercentInsiders")
    short_pct   = info.get("shortPercentOfFloat")
    float_shares= info.get("floatShares")

    c1, c2, c3, c4, c5 = st.columns(5)
    _kpi(c1,"機構持股%",
         f"{inst_pct*100:.1f}%" if inst_pct else "N/A",
         ">70%=主流標的","#B77DFF")
    _kpi(c2,"內部人持股%",
         f"{insider_pct*100:.1f}%" if insider_pct else "N/A",
         ">10%=管理層有信心","#FF9A3C")
    _kpi(c3,"空單比 Short%",
         f"{short_pct*100:.1f}%" if short_pct else "N/A",
         "<5%=空方少 >20%=高風險",
         "#FF3131" if short_pct and short_pct>0.15 else ("#FFD700" if short_pct and short_pct>0.08 else "#00FF7F"))
    _kpi(c4,"流通股數",
         f"{float_shares/1e9:.2f}B" if float_shares and float_shares>1e9 else
         f"{float_shares/1e6:.0f}M" if float_shares else "N/A",
         "流通市場規模","#00F5FF")
    _kpi(c5,"股票類型",
         info.get("quoteType","N/A"),
         info.get("sector","") or info.get("category",""),"#FFD700")
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── 說明卡：如何解讀持倉數據 ──────────────────────────────
    st.markdown(f"""
<div style="display:flex;gap:16px;margin-bottom:20px;flex-wrap:wrap;">
  <div style="flex:1;min-width:200px;padding:14px 18px;background:rgba(183,125,255,.06);border:1px solid rgba(183,125,255,.15);border-radius:10px;">
    <div style="font-family:'Rajdhani',sans-serif;font-size:18px;font-weight:700;color:#B77DFF;margin-bottom:6px;">📋 數據來源</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(200,215,235,.55);line-height:1.8;">
      {data_source}<br>每季申報 · 有 ~45 天延遲</div>
  </div>
  <div style="flex:1;min-width:200px;padding:14px 18px;background:rgba(0,255,127,.04);border:1px solid rgba(0,255,127,.12);border-radius:10px;">
    <div style="font-family:'Rajdhani',sans-serif;font-size:18px;font-weight:700;color:#00FF7F;margin-bottom:6px;">🐋 三大指數巨頭</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:16px;color:rgba(200,215,235,.65);line-height:1.7;">
      Vanguard / BlackRock / State Street<br>持有幾乎所有S&amp;P500成分股（被動指數）</div>
  </div>
  <div style="flex:1;min-width:200px;padding:14px 18px;background:rgba(255,215,0,.04);border:1px solid rgba(255,215,0,.12);border-radius:10px;">
    <div style="font-family:'Rajdhani',sans-serif;font-size:18px;font-weight:700;color:#FFD700;margin-bottom:6px;">⚡ PctHeld 解讀</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:16px;color:rgba(200,215,235,.65);line-height:1.7;">
      &lt;1 (如 0.056) = 佔流通股 5.6%<br>&gt;1 (如 5.6) = 已是百分比格式</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # SECTION A: TOP 10 INSTITUTIONAL HOLDERS (13F)
    # ══════════════════════════════════════════════════════════
    _sec28("▸ SECTION A — TOP 10 機構持股 (SEC 13F)", "#B77DFF")
    _sec26("美國SEC 13F申報 · 管理資產>$1億美元的機構每季揭露 · 資料有45天延遲","rgba(183,125,255,.5)")

    def _to_scalar(x):
        try:
            if x is None: return None
            if isinstance(x, (int, float)) and not (isinstance(x, float) and pd.isna(x)): return float(x)
            if isinstance(x, pd.Series): x = x.iloc[0]
            elif isinstance(x, np.ndarray): x = x.flat[0]
            if hasattr(x, "item"): return float(x.item())
            return float(x)
        except Exception:
            return None

    if not inst_df.empty:
        hdf = inst_df.head(10).copy()
        for nc in ["Shares","Value","PctHeld"]:
            hdf[nc] = pd.to_numeric(hdf[nc].apply(_to_scalar), errors="coerce")

        rank_colors = ["#FFD700","#C0C0C0","#CD7F32"] + ["#B77DFF"] * 7
        st.markdown("""
<div style="display:grid;grid-template-columns:28px 1fr 80px 90px 90px 80px;gap:0;
  font-family:'JetBrains Mono',monospace;font-size:11px;color:rgba(160,176,208,.35);
  padding:6px 16px;border-bottom:1px solid rgba(255,255,255,.05);letter-spacing:1px;">
  <div>#</div><div>機構名稱</div><div style="text-align:right;">持股數</div>
  <div style="text-align:right;">市值</div><div style="text-align:right;">持股%</div><div style="text-align:right;">類型</div>
</div>""", unsafe_allow_html=True)

        for i, (_, row) in enumerate(hdf.iterrows()):
            holder = str(row.get("Holder","Unknown"))
            shares = row.get("Shares"); value = row.get("Value"); pct = row.get("PctHeld")
            shares = float(shares) if shares is not None and not pd.isna(shares) else None
            value  = float(value)  if value  is not None and not pd.isna(value)  else None
            pct    = float(pct)    if pct    is not None and not pd.isna(pct)    else None
            rc  = rank_colors[i]
            sh_s = (f"{shares/1e9:.2f}B" if shares and shares>1e9 else
                    f"{shares/1e6:.1f}M"  if shares and shares>1e6 else
                    f"{int(shares):,}"    if shares else "N/A")
            vl_s = (f"${value/1e9:.2f}B" if value and value>1e9 else
                    f"${value/1e6:.0f}M"  if value and value>1e6 else "N/A")
            # pct may be decimal (0.056) or percent (5.6) depending on data source
            pc_s = (f"{pct*100:.2f}%" if pct is not None and pct < 1 else
                    f"{pct:.2f}%"     if pct is not None else "—")
            hl = holder.lower()
            badge = ("ETF" if any(k in hl for k in ["vanguard","blackrock","state street","ishares","spdr","fidelity spar","dimensional"]) else
                     "ARK" if "ark" in hl else
                     "HF"  if any(k in hl for k in ["capital","partners","management","advisors","hedge"]) else "INST")
            badge_c = {"ETF":"#00F5FF","ARK":"#FF9A3C","HF":"#FFD700","INST":"#B77DFF"}[badge]
            st.markdown(f"""
<div class="whale-row">
  <div class="w-rank" style="color:{rc};">#{i+1}</div>
  <div class="w-name">{holder}</div>
  <div class="w-badge" style="background:{badge_c}18;border:1px solid {badge_c}44;color:{badge_c};">{badge}</div>
  <div class="w-shares">{sh_s}</div>
  <div class="w-shares" style="color:rgba(255,154,60,.65);">{vl_s}</div>
  <div class="w-pct">{pc_s}</div>
</div>""", unsafe_allow_html=True)

        # Charts
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        ca_col, cb_col = st.columns(2)
        with ca_col:
            pct_data = hdf[["Holder","PctHeld"]].dropna().head(5)
            if len(pct_data) >= 2:
                _sec26("持股比例集中度 — TOP 5（環形圖）","rgba(183,125,255,.5)")
                donut = alt.Chart(pct_data).mark_arc(innerRadius=50,outerRadius=110).encode(
                    theta=alt.Theta("PctHeld:Q"),
                    color=alt.Color("Holder:N",scale=alt.Scale(range=["#B77DFF","#00F5FF","#FFD700","#00FF7F","#FF9A3C"]),
                                    legend=alt.Legend(labelColor="#aaa",titleColor="#aaa",labelFontSize=11)),
                    tooltip=["Holder:N",alt.Tooltip("PctHeld:Q",format=".4f")]
                ).properties(background="transparent",height=280).configure_view(strokeOpacity=0)
                st.altair_chart(donut, use_container_width=True)
        with cb_col:
            sh_data = hdf[["Holder","Shares"]].dropna().head(8)
            if not sh_data.empty:
                _sec26("持股數量排名 — TOP 8（橫條圖）","rgba(183,125,255,.5)")
                bar = alt.Chart(sh_data).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4,opacity=0.85).encode(
                    x=alt.X("Shares:Q",axis=alt.Axis(labelColor="#555",gridColor="#1a1a2a")),
                    y=alt.Y("Holder:N",sort="-x",axis=alt.Axis(labelColor="#ccc",labelLimit=160,labelFontSize=11)),
                    color=alt.Color("Holder:N",scale=alt.Scale(range=["#B77DFF","#8B5CF6","#7C3AED","#6D28D9","#5B21B6","#4C1D95","#3730A3","#312E81"]),legend=None)
                ).properties(background="transparent",height=280).configure_view(strokeOpacity=0)
                st.altair_chart(bar, use_container_width=True)
    else:
        sym_clean = symbol.upper().replace(".TW","").replace(".TWO","")
        st.markdown(f"""
<div style="text-align:center;padding:40px 20px;background:rgba(255,255,255,.012);
  border:1px solid rgba(255,255,255,.05);border-radius:16px;">
  <div style="font-size:40px;opacity:.2;margin-bottom:12px;">🐋</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:26px;color:rgba(255,255,255,.3);">
    暫無 13F 機構持倉數據</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:18px;color:rgba(160,176,208,.25);margin-top:6px;">
    台股 · 部分ETF · 小型股無SEC 13F申報義務</div>
  <div style="margin-top:16px;font-family:'JetBrains Mono',monospace;font-size:12px;color:rgba(0,245,255,.3);">
    可手動查詢 → 
    <a href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=13F&dateb=&owner=include&count=40&search_text=" 
       target="_blank" style="color:#00F5FF;">SEC EDGAR 13F</a>
    &nbsp;|&nbsp;
    <a href="https://finviz.com/quote.ashx?t={sym_clean}" 
       target="_blank" style="color:#00F5FF;">Finviz Ownership</a>
  </div>
</div>""", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # SECTION B: MUTUAL FUND HOLDERS
    # ══════════════════════════════════════════════════════════
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    _sec28("▸ SECTION B — 共同基金持倉", "#00FF7F")
    _sec26("共同基金的買入代表散戶資金的間接機構化 · 覆蓋率高=更多退休金認可","rgba(0,255,127,.4)")

    if not mf_df.empty:
        mdf = mf_df.head(8).copy()
        for nc in ["Shares","Value","PctHeld"]:
            mdf[nc] = pd.to_numeric(mdf[nc].apply(_to_scalar), errors="coerce")

        mf_colors = ["#00FF7F","#00DD70","#00BB60","#009950","#007740","#005530","#003320","#001110"]
        for i, (_, row) in enumerate(mdf.iterrows()):
            holder = str(row.get("Holder","Unknown"))
            shares = row.get("Shares"); value = row.get("Value"); pct = row.get("PctHeld")
            shares = float(shares) if shares is not None and not pd.isna(shares) else None
            value  = float(value)  if value  is not None and not pd.isna(value)  else None
            pct    = float(pct)    if pct    is not None and not pd.isna(pct)    else None
            rc = mf_colors[i] if i < len(mf_colors) else "#00FF7F"
            sh_s = (f"{shares/1e9:.2f}B" if shares and shares>1e9 else f"{shares/1e6:.1f}M" if shares and shares>1e6 else f"{int(shares):,}" if shares else "N/A")
            vl_s = (f"${value/1e9:.2f}B" if value and value>1e9 else f"${value/1e6:.0f}M" if value and value>1e6 else "N/A")
            pc_s = (f"{pct*100:.2f}%" if pct is not None and pct < 1 else f"{pct:.2f}%" if pct is not None else "—")
            st.markdown(f"""
<div class="whale-row" style="border-color:rgba(0,255,127,.08);border-left:3px solid {rc}44;">
  <div class="w-rank" style="color:{rc};">#{i+1}</div>
  <div class="w-name" style="color:rgba(0,255,127,.8);">{holder}</div>
  <div class="w-badge" style="background:rgba(0,255,127,.08);border:1px solid rgba(0,255,127,.2);color:#00FF7F;">MF</div>
  <div class="w-shares">{sh_s}</div>
  <div class="w-shares" style="color:rgba(255,154,60,.65);">{vl_s}</div>
  <div class="w-pct">{pc_s}</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:\'Rajdhani\',sans-serif;font-size:20px;color:rgba(160,176,208,.3);padding:20px;text-align:center;">暫無共同基金持倉數據（ETF或非美股標的）</div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # SECTION C: ARK INVEST HOLDINGS
    # ══════════════════════════════════════════════════════════
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    _sec28("▸ SECTION C — ARK Invest 主動持倉追蹤", "#FF9A3C")
    _sec26("Cathie Wood旗下6支ETF每日公布完整持倉 · 橙=持有 灰=未持有","rgba(255,154,60,.4)")

    with st.spinner("🐋 獵鯨中 — 掃描 ARK 6 支 ETF 持倉…"):
        ark_results = _fetch_ark_holdings(symbol)

    if ark_results:
        st.toast(f"✅ ARK 掃描完成 — 在 {len(ark_results)}/6 支 ETF 發現持倉", icon="🐋")
    else:
        st.toast("ℹ️ 此標的未被任何 ARK ETF 持有，或網路封鎖", icon="📡")

    ark_cols = st.columns(3)
    for idx, (fund_ticker, (fund_name, fund_color)) in enumerate(_ARK_ETFS.items()):
        with ark_cols[idx % 3]:
            if fund_ticker in ark_results:
                d = ark_results[fund_ticker]
                shares_s = (f"{d['shares']/1e6:.2f}M" if d['shares'] and d['shares']>1e6 else
                            f"{d['shares']:,.0f}"     if d['shares'] else "N/A")
                weight_s = f"{d['weight']:.2f}%" if d['weight'] else "N/A"
                value_s  = (f"${d['value']/1e9:.2f}B" if d['value'] and d['value']>1e9 else
                            f"${d['value']/1e6:.1f}M"  if d['value'] else "N/A")
                st.markdown(f"""
<div style="padding:18px;background:rgba(255,154,60,.07);border:1px solid {fund_color};
  border-radius:12px;margin-bottom:12px;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
    <div style="font-family:'Orbitron',sans-serif;font-size:18px;font-weight:700;color:{fund_color};">{fund_ticker}</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(255,154,60,.5);letter-spacing:1px;">✅ HELD</div>
  </div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(200,215,235,.5);margin-bottom:10px;">{fund_name}</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
    <div style="text-align:center;padding:8px;background:rgba(0,0,0,.3);border-radius:8px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(160,176,208,.35);margin-bottom:3px;">SHARES</div>
      <div style="font-family:'Orbitron',sans-serif;font-size:16px;color:#FFF;">{shares_s}</div>
    </div>
    <div style="text-align:center;padding:8px;background:rgba(0,0,0,.3);border-radius:8px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:rgba(160,176,208,.35);margin-bottom:3px;">WEIGHT</div>
      <div style="font-family:'Orbitron',sans-serif;font-size:16px;color:{fund_color};">{weight_s}</div>
    </div>
  </div>
  <div style="margin-top:8px;text-align:center;font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(255,154,60,.6);">市值 {value_s}</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div style="padding:18px;background:rgba(255,255,255,.012);border:1px solid rgba(255,255,255,.06);
  border-radius:12px;margin-bottom:12px;opacity:0.45;">
  <div style="font-family:'Orbitron',sans-serif;font-size:18px;font-weight:700;color:rgba(255,255,255,.3);margin-bottom:6px;">{fund_ticker}</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:14px;color:rgba(160,176,208,.3);margin-bottom:8px;">{fund_name}</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:rgba(160,176,208,.2);letter-spacing:2px;">❌ NOT HELD</div>
</div>""", unsafe_allow_html=True)

    if not ark_results:
        st.markdown("""
<div style="padding:20px;background:rgba(255,49,49,.05);border:1px solid rgba(255,49,49,.15);border-radius:10px;text-align:center;">
  <div style="font-family:'Rajdhani',sans-serif;font-size:26px;color:rgba(255,49,49,.6);margin-bottom:6px;">🌐 ARK 資料載入失敗</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:18px;color:rgba(160,176,208,.4);">
    可能原因：網路封鎖 / ARK CSV格式更新 / 台股或非美股標的不在ARK持倉中<br>
    可手動查詢：<b>ark-funds.com</b> 或 <b>cathiesark.com</b>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        held_count = len(ark_results)
        st.markdown(f"""
<div style="margin-top:12px;padding:14px 20px;background:rgba(255,154,60,.06);
  border:1px solid rgba(255,154,60,.2);border-radius:10px;text-align:center;">
  <div style="font-family:'Rajdhani',sans-serif;font-size:26px;font-weight:700;color:#FF9A3C;">
    🐋 ARK 掃描完成 — 在 {held_count}/6 支 ETF 中發現 {symbol} 持倉</div>
  <div style="font-family:'Rajdhani',sans-serif;font-size:18px;color:rgba(160,176,208,.5);margin-top:4px;">
    {'高度ARK認可：Cathie Wood在多個基金同時持有' if held_count>=3 else '部分ARK認可' if held_count>0 else '未被ARK持有'}</div>
</div>""", unsafe_allow_html=True)



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
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:18px;color:rgba(160,176,208,.5);margin-bottom:16px;">CB的時間邊際：不同階段的風報比完全不同，對的時機才能用最低風險賺最大利潤。</div>',unsafe_allow_html=True)
        for cls,num,title,period,key,detail in [
            ("gold","01","新券蜜月期","上市 0–90 天","上市初期追蹤，大戶定調，股性未定","進場甜蜜點：105–115 元。前 90 天是觀察期也是機會期，關注大股東動態與首批券商報告。此期間CB流動性低，價格易被操控，需小量試水。"),
            ("green","02","滿年沈澱","上市 350–420 天","沈澱洗牌結束，底部有支撐","觸發點：CB 站上 87MA 且帶量。一年洗盤後仍存活的標的底部結構扎實，浮額已充分清洗，此時進場的持有成本往往最低。"),
            ("","03","賣回保衛戰","距賣回日 < 180 天","下檔保護最強，CB 價 95–105 甜甜圈","最佳風報比窗口。賣回日臨近時，市場自然形成底部支撐，CB 不易跌破 100。持有人有賣回保護，上有機會，下有底部。"),
            ("red","04","百日轉換窗口","距到期 < 100 天","最後一搏，轉換或歸零","股價需站上轉換價 × 1.05 才有轉換意義。時間價值快速遞減，必須精確把握。此階段CB波動最劇烈，高手賺尾段，新手最容易在此被套。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;"><div style="font-family:\'Orbitron\',sans-serif;font-size:28px;font-weight:900;color:rgba(0,245,255,.08);">{num}</div><div><div class="ccard-t">{title}</div><div style="font-family:\'Rajdhani\',sans-serif;font-size:16px;color:rgba(160,176,208,.45);">{period}</div></div></div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>',unsafe_allow_html=True)

    # T2
    with tabs[1]:
        _sec28("進出場鐵律")
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:26px;font-weight:700;color:rgba(0,255,127,.75);letter-spacing:1px;margin-bottom:12px;">📥 核心進場條件 — 4 COMMANDMENTS</div>',unsafe_allow_html=True)
        for cls,title,key,detail in [
            ("green","價格天條","CB 市價 < 120 元 (理想 105–115)","超過 120 = 溢價過高，槓桿效益不足。最佳甜蜜點 108–113 元。這條件保護你不在頂部追高，超過120的CB下跌幅度往往超出預期。"),
            ("green","均線天條","87MA > 284MA 且向上","中期多頭確認。均線交叉後回踩 87MA 不破 = 最佳進場。均線方向比位置更重要，上彎中的均線是最強的支撐。"),
            ("","身分認證","領頭羊 or 風口豬","族群指標股或主流題材二軍，單兵不做。如果整個族群都在動，才是真正的主力行情，單一個股異動往往是假訊號。"),
            ("gold","發債故事","從無到有 / 擴產 / 政策事件","三選一。故事是引爆點，沒有故事的 CB 只是數字。最強的故事是政府政策背書+公司從無到有的轉型。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div class="ccard-t">{title}</div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>',unsafe_allow_html=True)
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:26px;font-weight:700;color:rgba(255,49,49,.75);letter-spacing:1px;margin:20px 0 12px;">📤 核心出場條件</div>',unsafe_allow_html=True)
        for cls,title,key,detail in [
            ("red","🛑 停損天條","CB 跌破 100 元","保本天條不妥協，沒有例外。跌破即離場。這是整套系統最重要的規則，一次不執行就可能讓整年獲利歸零。"),
            ("gold","💰 停利策略","目標 152 元以上","留魚尾策略：分批出場，讓剩餘倉位跟跑。到達130時出50%，150時再出30%，剩20%讓它跑。"),
            ("","⏰ 時間停損","持有超過 90 天未動","超過 90 天無動能，重新評估或減倉。時間成本是隱形的機會成本，死水不如流水。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div class="ccard-t">{title}</div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>',unsafe_allow_html=True)

    # T3
    with tabs[2]:
        _sec28("產業族群資料庫")
        ca2,cb2=st.columns(2)
        tw=[("🤖 AI伺服器","廣達·緯創·英業達·技嘉·緯穎"),("🌡️ 散熱","奇鋐·雙鴻·建準·健策·力致"),("⚙️ CoWoS封測","日月光·矽品·力成·欣銓"),("⚡ 重電/電網","華城·士電·中興電·大同·亞力"),("🔬 半導體設備","弘塑·辛耘·漢微科·家登·旺矽"),("🚢 航運","長榮·陽明·萬海·台驊·慧洋"),("💊 生技新藥","藥華藥·合一·浩鼎·疫苗·醣基"),("🔋 電池/EV","立凱·必翔·台達電·正崴·帝寶")]
        us=[("🧠 AI大模型","NVDA·AMD·MSFT·GOOGL·META·AMZN"),("⚛️ 量子計算","QBTS·IONQ·RGTI·QUBT·IONQ"),("🚀 太空/國防","PLTR·RKLB·LUNR·LMT·RTX"),("🏦 金融科技","SOFI·AFRM·UPST·SQ·PYPL"),("☁️ Cloud SaaS","SNOW·DDOG·CRWD·MDB·NET"),("🌿 Clean Energy","ENPH·FSLR·PLUG·BE·ARRY")]
        etfs=[("🇺🇸 美股核心","SPY·QQQ·VTI·IVV·VOO"),("🇹🇼 台股核心","0050·006208·00878·00919·00929"),("🔥 主題ETF","ARKK·BOTZ·SOXX·ROBO·CIBR")]
        with ca2:
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:rgba(0,245,255,.7);margin-bottom:10px;">🇹🇼 台股族群</div>',unsafe_allow_html=True)
            for n,s in tw: st.markdown(f'<div class="srow"><div class="srow-name">{n}</div><div class="srow-stk">{s}</div></div>',unsafe_allow_html=True)
        with cb2:
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:rgba(255,154,60,.7);margin-bottom:10px;">🇺🇸 美股族群</div>',unsafe_allow_html=True)
            for n,s in us: st.markdown(f'<div class="srow"><div class="srow-name">{n}</div><div class="srow-stk">{s}</div></div>',unsafe_allow_html=True)
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:rgba(183,125,255,.7);margin:12px 0 10px;">📦 核心 ETF</div>',unsafe_allow_html=True)
            for n,s in etfs: st.markdown(f'<div class="srow"><div class="srow-name">{n}</div><div class="srow-stk">{s}</div></div>',unsafe_allow_html=True)

    # T4
    with tabs[3]:
        _sec28("交易心法 Mindset OS")
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:20px;color:rgba(160,176,208,.4);margin-bottom:16px;">交易是認知套利：你比市場更理解的部分，才是你的真實優勢。心法不是秘訣，是對人性弱點的系統性防禦。</div>',unsafe_allow_html=True)
        for i,(title,desc) in enumerate([
            ("賣出是種藝術","目標區間到達後分批出場，留魚尾策略。永遠不要賣在最頂，讓利潤奔跑。分批的意義在於：你不需要判斷最高點，只需要在高位持續兌現。"),
            ("跌破100是天條","不管故事多美，CB跌破100元立刻離場。保住本金才有下一仗。市場永遠有下一個機會，但帳戶歸零就沒有機會了。"),
            ("族群共振才是主力","2~3檔同族群CB同步上攻，才是真正主力進場訊號。個股異動是獨舞，族群共振才是群舞。主力進場一定有足跡。"),
            ("87MA是生命線","站上87MA且均線向上才安全。跌破=第一警戒，284MA跌破=大逃殺。均線系統是多空的最終裁判，不管當下消息多好。"),
            ("溢價率的陷阱","溢價率 > 20% 上漲空間有限，下跌空間卻大。選低溢價（5~15%）CB，彈性最大，風險最低。"),
            ("籌碼鬆動就跑","已轉換比例超過30%，股東結構改變，籌碼不乾淨立刻警惕。主力轉換後開始賣股，CB的上漲動力就消失了。"),
            ("尾盤定勝負","13:25後最後25分鐘是多空最誠實表態。收盤站穩才是真突破，收盤跌破才是真破壞。"),
            ("消息面最後出現","基本面+技術面打底，消息面是確認彈，不是買入理由。追消息買的，往往是主力出貨的對象。"),
            ("停損是最高策略","每次停損是自我保護。不怕停損，怕的是一次大虧抹掉所有獲利。系統化停損是交易員和賭徒的本質區別。"),
            ("複利思維操盤","月報酬5%，一年79.6%。急著翻倍的人，最快的路是歸零。複利的奇蹟需要時間和紀律，不需要奇蹟行情。"),
        ],1):
            st.markdown(f'<div style="display:flex;align-items:flex-start;gap:16px;padding:16px 18px;background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.04);border-radius:10px;margin-bottom:8px;"><div style="font-family:\'Orbitron\',sans-serif;font-size:28px;font-weight:900;color:rgba(255,215,0,.1);min-width:44px;line-height:1;">{i:02d}</div><div><div style="font-family:\'Rajdhani\',sans-serif;font-size:20px;font-weight:700;color:#FFF;margin-bottom:5px;">{title}</div><div style="font-family:\'Rajdhani\',sans-serif;font-size:17px;color:rgba(180,195,220,.55);line-height:1.7;">{desc}</div></div></div>',unsafe_allow_html=True)

    # T5: CBAS
    with tabs[4]:
        _sec28("CBAS 槓桿試算引擎")
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:20px;color:rgba(160,176,208,.4);margin-bottom:16px;">第一性原理：CB的隱含槓桿 = 總投資額 ÷ 溢價部分。110元的CB，溢價10元，槓桿=110÷10=11倍。</div>',unsafe_allow_html=True)
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
            st.markdown(f'<div class="calc-scr"><div style="display:flex;justify-content:space-around;align-items:center;flex-wrap:wrap;gap:20px;"><div style="text-align:center;"><div style="font-family:\'Orbitron\',sans-serif;font-size:64px;font-weight:900;color:{lev_c};text-shadow:0 0 30px {lev_c}55;line-height:1;">{leverage:.2f}<span style="font-size:22px;opacity:.4;">×</span></div><div style="font-family:\'Rajdhani\',sans-serif;font-size:16px;color:rgba(160,176,208,.4);text-transform:uppercase;letter-spacing:3px;margin-top:6px;">IMPLIED LEVERAGE</div></div><div style="height:80px;width:1px;background:rgba(255,255,255,.06);"></div><div><div style="font-family:\'Rajdhani\',sans-serif;font-size:14px;color:rgba(160,176,208,.3);margin-bottom:4px;">CB 溢價權利金</div><div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:#FFF;">{prem_cost:.1f} 元</div></div><div style="height:80px;width:1px;background:rgba(255,255,255,.06);"></div><div><div style="font-family:\'Rajdhani\',sans-serif;font-size:14px;color:rgba(160,176,208,.3);margin-bottom:4px;">總投資額</div><div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:#FFF;">{total_inv/10000:.1f} 萬</div></div><div style="height:80px;width:1px;background:rgba(255,255,255,.06);"></div><div><div style="font-family:\'Rajdhani\',sans-serif;font-size:14px;color:rgba(160,176,208,.3);margin-bottom:4px;">每張換股數</div><div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:#FFF;">{conv_ratio:.0f} 股</div></div></div></div>',unsafe_allow_html=True)
            st.markdown(f'<div style="margin-top:14px;padding:16px 20px;background:rgba(0,0,0,.2);border-left:4px solid {conv_c};border-radius:0 10px 10px 0;"><span style="font-family:\'Rajdhani\',sans-serif;font-size:26px;font-weight:700;color:{conv_c};">{"✅ 正股低於轉換價 — 轉換機率低" if conv_prem_pct<-10 else ("⚠️ 接近轉換價 — 關注轉換訊號" if abs(conv_prem_pct)<5 else "🚀 正股高於轉換價 — 具轉換價值")}</span><span style="font-family:\'Rajdhani\',sans-serif;font-size:18px;color:rgba(160,176,208,.4);margin-left:12px;">轉換溢價率 {conv_prem_pct:+.1f}%</span></div>',unsafe_allow_html=True)
            st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:18px;color:rgba(160,176,208,.3);margin:16px 0 8px;">QUICK REF: 不同市價的槓桿對照</div>',unsafe_allow_html=True)
            refs=st.columns(5)
            for i,p in enumerate([103,105,110,115,120]):
                pm=p-100; lv=p/pm if pm>0 else 0; lc="#00FF7F" if lv>5 else ("#FFD700" if lv>3 else "#FF6B6B")
                refs[i].markdown(f'<div style="text-align:center;padding:12px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.04);border-radius:8px;"><div style="font-family:\'Rajdhani\',sans-serif;font-size:14px;color:rgba(160,176,208,.35);">CB {p}元</div><div style="font-family:\'Orbitron\',sans-serif;font-size:22px;font-weight:700;color:{lc};line-height:1.2;">{lv:.1f}×</div></div>',unsafe_allow_html=True)
        else:
            st.toast("⚠️ CB 市價需高於 100 元才有槓桿效應", icon="⚡")

    # T6: OTC均線
    with tabs[5]:
        _sec28("OTC 神奇均線法則")
        st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:20px;color:rgba(160,176,208,.4);margin-bottom:16px;">台股OTC市場的特殊均線系統，由實戰統計出的關鍵參數，87日=一季多一週，284日=約一年</div>',unsafe_allow_html=True)
        for cls,title,key,detail in [
            ("gold","87MA = 季線生命線","87MA 向上且股價站上","台股OTC核心均線。87MA向上=買進訊號；跌破且均線轉下=出場。CB操作的基礎框架。所有CB操作以87MA為進出依據，均線本身的方向比位置更重要。"),
            ("","284MA = 年線壓力/支撐","284MA 是長期趨勢分界線","284MA 之上=多頭，之下=空頭。87MA穿越284MA向上=黃金交叉；反之=死亡交叉。黃金交叉後的第一次回踩是最佳進場時機。"),
            ("green","乖離率區間管理","正乖離<25%，負乖離<-25%","CB股價距87MA正乖離超過25%=過熱警示；負乖離超過25%=超跌反彈點。乖離率是均值回歸的量化工具，偏離越遠回歸拉力越強。"),
            ("red","格蘭碧6大訊號","G1突破買·G2假跌買·G3回測買 | G4跌破賣·G5假突賣·G6反壓賣","買點(G1~G3)配合均線方向；賣點(G4~G6)配合背離與放量。格蘭碧8法則適用所有時間框架，OTC的87MA是最佳應用均線。"),
            ("","扣抵原理","284MA的扣抵天數=284天前的收盤價","284天前的價格偏低，今日284MA容易上揚（利多）；偏高則容易下壓（利空）。提前知道均線未來走向，是台股獨有的時間套利工具。"),
        ]:
            st.markdown(f'<div class="ccard {cls}"><div class="ccard-t">{title}</div><div class="ccard-k">{key}</div><div class="ccard-d">{detail}</div></div>',unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# MAIN ENTRY
# ════════════════════════════════════════════════════════════════════
def render():
    # 🎯 FEATURE 1: 首次進入顯示戰術指導 Modal
    if not st.session_state.get("t5_guide_shown", False):
        show_guide_modal()

    _inject_css()
    symbol=_search()
    _hero(symbol)

    with st.spinner(f"⬡ 鎖定目標: {symbol}…"):
        h1,h3,info,holders,mf_holders,err=_fetch(symbol)

    if err:
        # 🎯 FEATURE 2: st.toast 取代醜醜的綠/紅色方塊
        icon = "⏳" if "429" in err or "頻繁" in err or "rate" in err.lower() else "💀"
        st.toast(f"❌ {err}", icon=icon)
        st.toast("💡 美股: AAPL · NVDA  |  台股: 2330 · 00675L · 5274  |  ETF: SPY · QQQ", icon="📡")
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
        elif active=="5.5": _s55(holders,info,symbol,mf_holders)
        elif active=="5.6": _s56()
        else:               _s51(h1,info,symbol)
    except Exception as exc:
        st.toast(f"❌ Module {active} Error: {exc}", icon="💀")
        with st.expander("🔍 Debug"):
            st.code(traceback.format_exc())
    st.markdown("</div>",unsafe_allow_html=True)

    st.markdown(f'<div class="t5-foot">Titan Universal Market Analyzer V700 · Tactical Edition · Toast · Typewriter · 13F Rebuilt · {symbol} · {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>',unsafe_allow_html=True)


if __name__=="__main__":
    render()
