# ui_desktop/tab2_radar.py
# Titan SOP V300 — 獵殺雷達 (Kill Radar) + 戰略兵工廠 (Strategic Arsenal)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  "DIRECTOR'S CUT V300" + SURGICAL ARSENAL TRANSPLANT            ║
# ║  ✅ NEW Section 2.0: 籌碼序幕 (Chips Prologue)                    ║
# ║  ✅ Sections 2.1-2.4 PRESERVED 100% (NO CASTRATION)              ║
# ║  ✅ NEW Section 2.5: 戰略兵工廠 (Strategic Arsenal)               ║
# ║      → Tool A: Intel Hunter (情報獵殺)                            ║
# ║      → Tool B: CBAS Calculator (試算儀)                           ║
# ║      → Tool C: Strategy Calendar (行事曆)                         ║
# ║  SURGICAL TRANSPLANT FROM tab5_wiki.py                           ║
# ╚═══════════════════════════════════════════════════════════════════╝
#
# 原版邏輯完整對應：
#  2.0 籌碼序幕  → Market Battlefield Map (Interactive Scatter + Lazy Load)
#  2.1 自動獵殺  → Fire Control Deck + Strategy Pills
#  2.2 核心檢核  → Sniper Scope (K-line + 4 Commandments)
#  2.3 風險雷達  → Warning Cards (converted_ratio/premium/avg_volume)
#  2.4 資金配置  → Kelly Display + Portfolio (原版 20% 等權邏輯)
#  2.5 戰略兵工廠 → Intel/CBAS/Calendar (transplanted from tab5)

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import yfinance as yf
import time

from strategy import TitanStrategyEngine
from knowledge_base import TitanKnowledgeBase
from execution import CalendarAgent


# ══════════════════════════════════════════════════════════════════════════════
#  [UPGRADE #3] VALKYRIE AI TYPEWRITER — Sci-Fi Terminal Streaming
# ══════════════════════════════════════════════════════════════════════════════
def _stream_text(text, speed=0.018):
    """Character-by-character generator for st.write_stream"""
    for char in text:
        yield char
        time.sleep(speed)

def stream_generator(text):
    """Word-by-word generator for Section 2.5"""
    for word in text.split():
        yield word + " "
        time.sleep(0.02)


# ══════════════════════════════════════════════════════════════════════════════
#  [UPGRADE #1] TACTICAL GUIDE DIALOG — Onboarding Modal
# ══════════════════════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導 — Kill Radar Command Center")
def _show_tactical_guide():
    st.markdown("""
<div style="font-family:'Rajdhani',sans-serif;font-size:15px;color:#C8D8E8;line-height:1.8;">

### 🎯 歡迎進入獵殺雷達

本模組是 Titan OS 的**核心狙擊系統**，執行全市場普查與精準打擊：

**🎬 2.0 籌碼序幕 (CHIPS PROLOGUE)**
市場戰場地圖 — 互動式散點圖，X軸為轉換溢價率（成本），Y軸為收盤價（價值），顏色顯示已轉換比例熱度。快速鎖定狙擊區與避雷區。

**📡 2.1 自動獵殺 (AUTO SCAN)**
全市場雙軌普查 (.TW/.TWO)，自動篩選 SOP 黃金標準標的 (價格<120 + 多頭排列 + 轉換率<30%)。
含 6 大策略面板：全市場 / SOP菁英 / 新券蜜月 / 滿年沈澱 / 賣回保衛 / 產業風口。

**📈 2.2 核心檢核 (SNIPER SCOPE)**
輸入 CB 代號即時拉取 K 線 + 87MA/284MA，搭配四大天條檢核卡 (價格/趨勢/轉換率/評分)。

**⚠️ 2.3 風險雷達 / 💰 2.4 資金配置**
負面表列警示 (籌碼鬆動/高溢價/流動性陷阱) + Top 5 等權重 20% 資金配置試算。

**🛠️ 2.5 戰略兵工廠 (NEW!)**
情報獵殺分析 + CBAS 槓桿試算儀 + 戰略行事曆（整合自 Tab 5）。

</div>""", unsafe_allow_html=True)
    if st.button("✅ 收到，開始獵殺 (Roger That)", type="primary", use_container_width=True):
        st.session_state['tab2_guided'] = True
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  ENGINES  (取代原版全域 strategy 變數)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def _load_engines():
    kb    = TitanKnowledgeBase()
    strat = TitanStrategyEngine()
    strat.kb = kb
    return strat, kb

@st.cache_resource
def _load_calendar():
    return CalendarAgent()


# ══════════════════════════════════════════════════════════════════════════════
#  CSS  共用設計語言（與 tab1_macro V300 完全一致）+ Arsenal Styles
# ══════════════════════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;600;700&family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
:root {
    --c-gold:#FFD700; --c-cyan:#00F5FF;
    --c-red:#FF3131;  --c-green:#00FF7F;
    --c-orange:#FF9A3C;
    --f-display:'Bebas Neue',sans-serif;
    --f-body:'Rajdhani',sans-serif;
    --f-mono:'JetBrains Mono',monospace;
    --f-o:'Orbitron',sans-serif;
    --f-i:'Inter',sans-serif;
}

/* ── FIRE CONTROL DECK ─────────────────────────────────────────── */
.t2-fire-card {
    height:110px; border-radius:16px;
    display:flex; flex-direction:column; align-items:center;
    justify-content:center; gap:6px;
    transition:all .24s cubic-bezier(.4,0,.2,1);
    position:relative; overflow:hidden;
}
.t2-fire-card::after {
    content:''; position:absolute; bottom:0; left:12%; right:12%; height:2px;
    background:var(--fa,#00F5FF); opacity:0; border-radius:2px;
    transition:opacity .24s ease;
}
.t2-fire-card.active::after { opacity:1; }
.t2-fire-card.active { transform:translateY(-3px); }
.t2-fire-icon  { font-size:30px; line-height:1; }
.t2-fire-label { font-family:var(--f-body);  font-size:14px; font-weight:700; color:#CDD; }
.t2-fire-tag   { font-family:var(--f-mono);  font-size:7.5px; color:#334; letter-spacing:2px; text-transform:uppercase; }
.t2-fire-card.active .t2-fire-label { color:var(--fa,#00F5FF); }

/* ── STRATEGY PILL RAIL ────────────────────────────────────────── */
.t2-pill-rail {
    display:flex; gap:8px; flex-wrap:wrap;
    padding:13px 15px; margin-bottom:18px;
    background:rgba(0,0,0,.20);
    border:1px solid rgba(255,255,255,.052);
    border-radius:13px;
}
.t2-pill {
    font-family:var(--f-mono); font-size:11px; font-weight:700;
    color:rgba(150,168,195,.48); letter-spacing:1.5px;
    padding:7px 16px; border-radius:30px;
    border:1px solid rgba(255,255,255,.065);
    background:rgba(255,255,255,.022);
    text-transform:uppercase; white-space:nowrap;
    transition:all .2s ease; cursor:pointer;
}
.t2-pill:hover { border-color:rgba(0,245,255,.42); color:rgba(0,245,255,.82); }
.t2-pill.active {
    border-color:rgba(255,215,0,.55);
    background:rgba(255,215,0,.07); color:#FFD700;
    box-shadow:0 0 12px rgba(255,215,0,.12);
}

/* ── SCANNER STATUS HUD ────────────────────────────────────────── */
.t2-hud-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:18px; }
.t2-hud-card {
    background:rgba(255,255,255,.022);
    border:1px solid rgba(255,255,255,.062);
    border-top:2px solid var(--hc,#00F5FF);
    border-radius:14px; padding:13px 14px 11px;
    position:relative; overflow:hidden;
}
.t2-hud-card::after {
    content:''; position:absolute; top:0; right:0;
    width:72px; height:72px;
    background:radial-gradient(circle at top right,var(--hc,#00F5FF),transparent 68%);
    opacity:.04; pointer-events:none;
}
.t2-hud-lbl { font-family:var(--f-mono); font-size:8px; color:rgba(140,155,178,.55); text-transform:uppercase; letter-spacing:2px; margin-bottom:8px; }
.t2-hud-val { font-family:var(--f-display); font-size:44px; color:#FFF; line-height:.95; margin-bottom:5px; }
.t2-hud-sub { font-family:var(--f-body); font-size:12px; color:var(--hc,#00F5FF); opacity:.85; font-weight:600; }

/* ── RESULT TABLE ──────────────────────────────────────────────── */
.t2-tbl { width:100%; border-collapse:collapse; font-family:var(--f-body); }
.t2-tbl th {
    font-family:var(--f-mono); font-size:8.5px; font-weight:700;
    letter-spacing:2px; text-transform:uppercase;
    color:rgba(0,245,255,.62); background:rgba(0,245,255,.04);
    padding:9px 12px; border-bottom:1px solid rgba(0,245,255,.09);
}
.t2-tbl td { padding:8px 12px; border-bottom:1px solid rgba(255,255,255,.028); color:rgba(210,222,238,.82); font-size:14px; }
.t2-tbl tr:hover td { background:rgba(0,245,255,.023); }

/* ── SNIPER CHECKLIST CARDS ────────────────────────────────────── */
.t2-rule-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:20px; }
.t2-rule-card {
    background:rgba(255,255,255,.022); border:1px solid rgba(255,255,255,.062);
    border-radius:14px; padding:16px 12px 13px; text-align:center;
    position:relative; overflow:hidden; transition:transform .18s ease;
}
.t2-rule-card:hover { transform:translateY(-2px); }
.t2-rule-card.pass { border-color:rgba(0,255,127,.32); background:rgba(0,255,127,.03); }
.t2-rule-card.fail { border-color:rgba(255,49,49,.32);  background:rgba(255,49,49,.03); }
.t2-rule-card.warn { border-color:rgba(255,215,0,.30);  background:rgba(255,215,0,.025); }
.t2-rule-icon  { font-size:28px; margin-bottom:9px; }
.t2-rule-title { font-family:var(--f-mono); font-size:8.5px; color:rgba(145,162,185,.55); text-transform:uppercase; letter-spacing:1.5px; margin-bottom:7px; }
.t2-rule-val   { font-family:var(--f-display); font-size:24px; color:#FFF; margin-bottom:6px; }
.t2-rule-badge { font-family:var(--f-body); font-size:12px; font-weight:700; display:inline-block; padding:3px 10px; border-radius:20px; }
.pass .t2-rule-badge { background:rgba(0,255,127,.14); color:#00FF7F; }
.fail .t2-rule-badge { background:rgba(255,49,49,.14);  color:#FF6B6B; }
.warn .t2-rule-badge { background:rgba(255,215,0,.12);  color:#FFD700; }

/* ── WARNING CARDS ─────────────────────────────────────────────── */
.t2-warn-card {
    border:1px solid rgba(255,49,49,.28);
    background:rgba(255,49,49,.03);
    border-left:3px solid #FF3131;
    border-radius:14px; padding:14px 18px 12px;
    margin-bottom:10px;
    box-shadow:0 0 16px rgba(255,49,49,.07);
    transition:transform .18s ease;
    position:relative; overflow:hidden;
}
.t2-warn-card:hover { transform:translateX(4px); }
.t2-warn-header { font-family:var(--f-body); font-size:16px; font-weight:700; color:#FF6B6B; margin-bottom:5px; }
.t2-warn-meta   { font-family:var(--f-mono); font-size:9.5px; color:#445566; letter-spacing:1px; }
.t2-warn-value  { font-family:var(--f-display); font-size:30px; color:#FF3131; position:absolute; right:18px; top:12px; }
.t2-warn-ok     { font-family:var(--f-mono); font-size:10px; color:#00FF7F; border:1px solid rgba(0,255,127,.2); background:rgba(0,255,127,.04); border-radius:9px; padding:10px 14px; letter-spacing:2px; text-align:center; text-transform:uppercase; }

/* ── KELLY BIG NUMBER ──────────────────────────────────────────── */
.t2-kelly-box {
    text-align:center; padding:28px 20px 22px;
    background:rgba(0,0,0,.30); border:1px solid rgba(255,215,0,.14);
    border-radius:20px; margin-bottom:18px; position:relative; overflow:hidden;
}
.t2-kelly-box::before {
    content:''; position:absolute; top:-40px; left:50%; transform:translateX(-50%);
    width:220px; height:220px; border-radius:50%;
    background:radial-gradient(circle,rgba(255,215,0,.07) 0%,transparent 70%);
    pointer-events:none;
}
.t2-kelly-lbl { font-family:var(--f-mono); font-size:8.5px; color:rgba(255,215,0,.38); letter-spacing:3px; text-transform:uppercase; margin-bottom:12px; }
.t2-kelly-num { font-family:var(--f-display); font-size:96px; color:#FFD700; line-height:1; text-shadow:0 0 38px rgba(255,215,0,.32); letter-spacing:4px; }
.t2-kelly-pct { font-family:var(--f-display); font-size:38px; color:rgba(255,215,0,.5); }
.t2-kelly-sub { font-family:var(--f-body); font-size:13px; color:#445566; margin-top:10px; }

/* ── PORTFOLIO ROW ─────────────────────────────────────────────── */
.t2-port-row {
    font-family:var(--f-body); font-size:14px; color:#8BAABB;
    padding:9px 0; border-bottom:1px solid rgba(255,255,255,.04);
}
.t2-port-row span.nm { color:#CDD; font-weight:700; }
.t2-port-row span.hl { color:#FFD700; font-weight:700; }

/* ── SHARED ────────────────────────────────────────────────────── */
.t2-sec-title {
    font-family:var(--f-display); font-size:22px; letter-spacing:2px;
    color:var(--c-cyan); text-shadow:0 0 16px rgba(0,245,255,.22);
    margin-bottom:18px; padding-bottom:12px;
    border-bottom:1px solid rgba(255,255,255,.052);
}
.t2-chart-wrap {
    background:rgba(0,0,0,.32); border:1px solid rgba(255,255,255,.055);
    border-radius:16px; padding:14px 8px 5px; margin:14px 0; overflow:hidden;
}
.t2-action div.stButton > button {
    background:rgba(0,245,255,.05) !important;
    border:1px solid rgba(0,245,255,.28) !important;
    color:rgba(0,245,255,.85) !important;
    font-family:var(--f-mono) !important; font-size:11px !important;
    letter-spacing:2px !important; min-height:46px !important;
    border-radius:12px !important; text-transform:uppercase !important;
}
.t2-action div.stButton > button:hover {
    background:rgba(0,245,255,.10) !important;
    box-shadow:0 0 20px rgba(0,245,255,.2) !important;
}
.t2-content {
    background:linear-gradient(175deg,#06090e 0%,#090c14 100%);
    border:1px solid rgba(255,255,255,.05);
    border-radius:20px; padding:24px 22px 30px; min-height:420px;
    position:relative;
}
.t2-content::after {
    content:''; position:absolute; bottom:0; left:8%; right:8%; height:1px;
    background:linear-gradient(90deg,transparent,rgba(0,245,255,.10) 50%,transparent);
}
.t2-empty {
    border:1px dashed rgba(255,255,255,.07); border-radius:16px;
    padding:58px 30px; text-align:center;
}
.t2-empty-icon { font-size:42px; opacity:.22; margin-bottom:14px; }
.t2-empty-text { font-family:var(--f-mono); font-size:11px; color:#2a3844; letter-spacing:2.5px; text-transform:uppercase; }
.t2-foot { font-family:var(--f-mono); font-size:9px; color:rgba(70,90,110,.28); letter-spacing:2px; text-align:right; margin-top:18px; text-transform:uppercase; }

/* ══════════════════════════════════════════════════════════════ */
/* SECTION 2.5 ARSENAL STYLES (Transplanted from tab5_wiki.py)   */
/* ══════════════════════════════════════════════════════════════ */

/* ARSENAL SECTION HEADER */
.t5-sec-head{display:flex;align-items:center;gap:14px;padding-bottom:14px;border-bottom:1px solid rgba(255,255,255,.052);margin-bottom:20px;}
.t5-sec-num{font-family:var(--f-display);font-size:56px;color:rgba(0,245,255,.06);letter-spacing:2px;line-height:1;}
.t5-sec-title{font-family:var(--f-display);font-size:22px;color:var(--sa,#00F5FF);letter-spacing:2px;}
.t5-sec-sub{font-family:var(--f-mono);font-size:9px;color:rgba(0,245,255,.28);letter-spacing:2px;text-transform:uppercase;margin-top:2px;}

/* CLASSIFIED FILE CARDS */
.codex-card{background:rgba(255,255,255,.025);border:1px solid rgba(80,90,110,.25);border-left:4px solid #00F5FF;padding:22px 24px 18px;margin-bottom:14px;border-radius:0 10px 10px 0;position:relative;overflow:hidden;}
.codex-card::before{content:'CLASSIFIED';position:absolute;top:8px;right:12px;font-family:var(--f-o);font-size:7px;color:rgba(255,49,49,.18);letter-spacing:4px;}
.codex-card.gold{border-left-color:#FFD700;}
.codex-card.gold::before{content:'PRIORITY';}
.codex-card.red{border-left-color:#FF3131;}
.codex-card.red::before{content:'CRITICAL';}
.codex-card.green{border-left-color:#00FF7F;}
.codex-card.green::before{content:'ACTIVE';}
.codex-card-title{font-family:var(--f-body);font-size:18px;font-weight:700;color:#FFF;letter-spacing:1px;margin-bottom:6px;}
.codex-card-key{font-family:var(--f-i);font-size:15px;font-weight:600;color:rgba(0,245,255,.85);line-height:1.6;margin-bottom:8px;}
.codex-card-detail{font-family:var(--f-mono);font-size:11px;color:rgba(160,176,208,.5);line-height:1.7;}

/* CALC SCREEN (80px MASSIVE DISPLAY) */
.calc-screen{background:#000;border:2px solid rgba(80,90,110,.35);border-radius:14px;padding:32px 28px;text-align:center;margin-top:16px;position:relative;overflow:hidden;}
.calc-screen::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,245,255,.2),transparent);}
.calc-screen::after{content:'CBAS LEVERAGE ENGINE';position:absolute;top:10px;left:16px;font-family:var(--f-o);font-size:7px;color:rgba(0,245,255,.15);letter-spacing:4px;}
.calc-val{font-size:80px;font-weight:900;font-family:var(--f-o);line-height:1;letter-spacing:-2px;}
.calc-val.green{color:#00FF7F;text-shadow:0 0 30px rgba(0,255,127,.35);}
.calc-val.gold{color:#FFD700;text-shadow:0 0 30px rgba(255,215,0,.35);}
.calc-val.red{color:#FF6B6B;text-shadow:0 0 30px rgba(255,107,107,.35);}
.calc-lbl{font-family:var(--f-mono);font-size:11px;color:rgba(160,176,208,.4);text-transform:uppercase;letter-spacing:3px;margin-top:8px;}
.calc-unit{font-family:var(--f-mono);font-size:14px;color:rgba(255,255,255,.25);margin-left:4px;}
.calc-divider{width:60%;height:1px;background:rgba(255,255,255,.05);margin:20px auto;}

/* EVENT CARDS */
.event-card{background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:20px;margin-bottom:12px;display:flex;align-items:center;gap:20px;}
.event-day{font-size:60px;font-weight:900;font-family:var(--f-o);color:#FFD700;text-shadow:0 0 20px rgba(255,215,0,.2);line-height:1;min-width:100px;text-align:center;}
.event-day-unit{font-family:var(--f-mono);font-size:9px;color:rgba(255,215,0,.4);letter-spacing:2px;text-transform:uppercase;margin-top:4px;text-align:center;}
.event-body{flex:1;}
.event-name{font-family:var(--f-body);font-size:17px;font-weight:700;color:#FFF;letter-spacing:1px;}
.event-type{font-family:var(--f-mono);font-size:11px;color:rgba(0,245,255,.6);letter-spacing:1px;margin-top:3px;}
.event-date{font-family:var(--f-mono);font-size:10px;color:rgba(160,176,208,.35);margin-top:2px;}
.event-desc{font-family:var(--f-mono);font-size:10px;color:rgba(160,176,208,.3);margin-top:5px;line-height:1.5;}

/* TERMINAL BOX */
.t5-terminal{background:#0D1117;border:1px solid #30363d;border-left:4px solid #00F5FF;border-radius:0 10px 10px 0;padding:22px 24px;font-family:var(--f-mono);color:#c9d1d9;font-size:12px;line-height:1.7;margin:12px 0;}
.t5-terminal::before{content:'> INTEL TERMINAL';display:block;font-size:9px;letter-spacing:3px;color:rgba(0,245,255,.25);margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid rgba(0,245,255,.06);}

</style>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS  （與原版邏輯完全一致）
# ══════════════════════════════════════════════════════════════════════════════

def _safe_conv(row) -> float:
    """
    已轉換率智慧反轉邏輯（與原版 100% 一致）
    原版：raw_conv > 50 視為「餘額比率」→ 反轉；否則視為已轉換率
    """
    raw = pd.to_numeric(row.get('conv_rate', row.get('balance_rate', 100)), errors='coerce') or 100.0
    converted = (100.0 - raw) if raw > 50 else raw
    return max(0.0, converted)


# ── K-LINE CHART  (原版 plot_candle_chart 直接移植，加 dark theme wrapper) ──
def _plot_candle_chart(cb_code: str):
    """互動式 K 線圖（紅漲綠跌）+ 87/284MA  ── 與原版邏輯一致"""
    target_code = str(cb_code).strip()
    # 5碼 CB 代號自動截取前4碼（原版關鍵修正）
    if len(target_code) == 5 and target_code.isdigit():
        target_code = target_code[:4]
    try:
        chart_df = yf.download(f"{target_code}.TW", period="2y", progress=False)
        if chart_df.empty:
            chart_df = yf.download(f"{target_code}.TWO", period="2y", progress=False)
        if chart_df.empty:
            st.toast(f"⚠️ Yahoo Finance 查無 {target_code} K 線資料", icon="⚡")
            return

        if isinstance(chart_df.columns, pd.MultiIndex):
            chart_df.columns = chart_df.columns.get_level_values(0)
        chart_df = chart_df.reset_index()
        chart_df['MA87']  = chart_df['Close'].rolling(87).mean()
        chart_df['MA284'] = chart_df['Close'].rolling(284).mean()

        base = alt.Chart(chart_df).encode(
            x=alt.X('Date:T', axis=alt.Axis(format='%Y-%m', labelColor='#445566',
                                             titleColor='#334455', title=''))
        )
        color_cond = alt.condition("datum.Open <= datum.Close",
                                   alt.value("#FF4B4B"), alt.value("#26A69A"))
        candles = (
            base.mark_rule(color='#445566').encode(
                y=alt.Y('Low', title='股價', scale=alt.Scale(zero=False),
                        axis=alt.Axis(labelColor='#445566', titleColor='#334455')),
                y2='High')
            + base.mark_bar(size=3).encode(
                y='Open', y2='Close', color=color_cond,
                tooltip=['Date:T', 'Open:Q', 'Close:Q', 'High:Q', 'Low:Q'])
        )
        line_87  = base.mark_line(color='orange', strokeWidth=2).encode(y='MA87')
        line_284 = base.mark_line(color='#00bfff', strokeWidth=2).encode(y='MA284')

        st.markdown('<div class="t2-chart-wrap">', unsafe_allow_html=True)
        st.altair_chart(
            (candles + line_87 + line_284).interactive()
            .configure_view(strokeOpacity=0, fill='rgba(0,0,0,0)')
            .configure_axis(gridColor='rgba(255,255,255,0.04)'),
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption(f"📈 標的股票代碼: {target_code}  ·  🔶 橘線: 87MA  ·  🔷 藍線: 284MA")
    except Exception as e:
        st.toast(f"⚠️ K 線圖生成失敗: {e}", icon="⚡")


# ── TPEX DATA  (原版 get_tpex_data 完整移植，含30大分類chain_map) ─────────
@st.cache_data(ttl=3600)
def _get_tpex_data(df_json: str) -> pd.DataFrame:
    """IC.TPEX 官方30大產業分類（原版 Tab5 產業風口地圖邏輯）"""
    raw_df = pd.read_json(df_json)

    chain_map = {
        # [1. 半導體]
        '世芯':('半導體','⬆️ 上游-IC設計','IP/ASIC'), '創意':('半導體','⬆️ 上游-IC設計','IP/ASIC'),
        '聯發科':('半導體','⬆️ 上游-IC設計','手機SoC'), '瑞昱':('半導體','⬆️ 上游-IC設計','網通IC'),
        '台積':('半導體','↔️ 中游-製造','晶圓代工'), '聯電':('半導體','↔️ 中游-製造','晶圓代工'),
        '弘塑':('半導體','↔️ 中游-設備','濕製程'), '辛耘':('半導體','↔️ 中游-設備','CoWoS'),
        '萬潤':('半導體','↔️ 中游-設備','封測設備'), '日月光':('半導體','⬇️ 下游-封測','封裝'),
        # [2. 通信網路]
        '智邦':('通信網路','⬇️ 下游-網通設備','交換器'), '啟碁':('通信網路','⬇️ 下游-網通設備','衛星/車用'),
        '中磊':('通信網路','⬇️ 下游-網通設備','寬頻'), '全新':('通信網路','⬆️ 上游-元件','PA砷化鎵'),
        '穩懋':('通信網路','⬆️ 上游-元件','PA代工'), '華星光':('通信網路','↔️ 中游-光通訊','CPO模組'),
        '波若威':('通信網路','↔️ 中游-光通訊','光纖元件'), '聯亞':('通信網路','↔️ 中游-光通訊','雷射二極體'),
        # [3. 電腦週邊]
        '廣達':('電腦週邊','⬇️ 下游-組裝','AI伺服器'), '緯創':('電腦週邊','⬇️ 下游-組裝','AI伺服器'),
        '技嘉':('電腦週邊','⬇️ 下游-品牌','板卡/Server'), '微星':('電腦週邊','⬇️ 下游-品牌','電競'),
        '奇鋐':('電腦週邊','↔️ 中游-散熱','3D VC'), '雙鴻':('電腦週邊','↔️ 中游-散熱','水冷板'),
        '勤誠':('電腦週邊','↔️ 中游-機殼','伺服器機殼'), '川湖':('電腦週邊','↔️ 中游-機構','導軌'),
        '樺漢':('電腦週邊','⬇️ 下游-工業電腦','IPC'), '研華':('電腦週邊','⬇️ 下游-工業電腦','IPC'),
        # [4. 電子零組件]
        '台光電':('電子零組件','⬆️ 上游-材料','CCL銅箔基板'), '台燿':('電子零組件','⬆️ 上游-材料','CCL高頻'),
        '金像電':('電子零組件','↔️ 中游-PCB','伺服器板'), '健鼎':('電子零組件','↔️ 中游-PCB','HDI'),
        '欣興':('電子零組件','↔️ 中游-PCB','ABF載板'), '南電':('電子零組件','↔️ 中游-PCB','ABF載板'),
        '國巨':('電子零組件','↔️ 中游-被動元件','MLCC'), '華新科':('電子零組件','↔️ 中游-被動元件','MLCC'),
        '凡甲':('電子零組件','↔️ 中游-連接器','車用/Server'), '嘉澤':('電子零組件','↔️ 中游-連接器','CPU Socket'),
        # [5. 光電]
        '大立光':('光電','⬆️ 上游-光學','鏡頭'), '玉晶光':('光電','⬆️ 上游-光學','鏡頭'),
        '亞光':('光電','⬆️ 上游-光學','車載鏡頭'), '群創':('光電','↔️ 中游-面板','LCD'),
        '友達':('光電','↔️ 中游-面板','LCD'), '中光電':('光電','⬇️ 下游-背光','背光模組'),
        # [9. 生技醫療]
        '藥華藥':('生技醫療','⬆️ 上游-新藥','新藥研發'), '合一':('生技醫療','⬆️ 上游-新藥','新藥研發'),
        '保瑞':('生技醫療','↔️ 中游-製造','CDMO'), '美時':('生技醫療','↔️ 中游-製造','學名藥'),
        '晶碩':('生技醫療','⬇️ 下游-醫材','隱形眼鏡'), '視陽':('生技醫療','⬇️ 下游-醫材','隱形眼鏡'),
        '大樹':('生技醫療','⬇️ 下游-通路','藥局'), '長佳智能':('生技醫療','⬆️ 上游-資訊','AI醫療'),
        # [11. 電機機械]
        '上銀':('電機機械','⬆️ 上游-傳動','滾珠螺桿'), '亞德客':('電機機械','⬆️ 上游-氣動','氣動元件'),
        '東元':('電機機械','↔️ 中游-馬達','工業馬達'), '中砂':('電機機械','⬆️ 上游-耗材','鑽石碟'),
        # [14. 建材營造]
        '華固':('建材營造','⬇️ 下游-建設','住宅商辦'), '長虹':('建材營造','⬇️ 下游-建設','住宅商辦'),
        '興富發':('建材營造','⬇️ 下游-建設','住宅'), '遠雄':('建材營造','⬇️ 下游-建設','廠辦'),
        '國產':('建材營造','⬆️ 上游-材料','預拌混凝土'),
        # [15. 航運業]
        '長榮':('航運業','↔️ 中游-海運','貨櫃'), '陽明':('航運業','↔️ 中游-海運','貨櫃'),
        '萬海':('航運業','↔️ 中游-海運','貨櫃'), '長榮航':('航運業','↔️ 中游-空運','航空'),
        '華航':('航運業','↔️ 中游-空運','航空'), '星宇':('航運業','↔️ 中游-空運','航空'),
        '慧洋':('航運業','↔️ 中游-散裝','散裝航運'), '裕民':('航運業','↔️ 中游-散裝','散裝航運'),
        # [24. 汽車工業]
        '東陽':('汽車工業','↔️ 中游-零組件','AM保險桿'), '堤維西':('汽車工業','↔️ 中游-零組件','AM車燈'),
        '帝寶':('汽車工業','↔️ 中游-零組件','AM車燈'), '裕隆':('汽車工業','⬇️ 下游-整車','品牌製造'),
        '中華':('汽車工業','⬇️ 下游-整車','商用車'), '和泰車':('汽車工業','⬇️ 下游-代理','TOYOTA'),
        # [27. 綠能環保（含重電）]
        '華城':('綠能環保','↔️ 中游-重電','變壓器'), '士電':('綠能環保','↔️ 中游-重電','配電盤'),
        '中興電':('綠能環保','↔️ 中游-重電','GIS開關'), '亞力':('綠能環保','↔️ 中游-重電','輸配電'),
        '世紀鋼':('綠能環保','⬆️ 上游-風電','水下基礎'), '森崴':('綠能環保','⬇️ 下游-能源','綠電開發'),
        '雲豹':('綠能環保','⬇️ 下游-能源','儲能/太陽能'),
        # [30. 其他（含軍工）]
        '漢翔':('其他','↔️ 中游-航太','軍工/民航'), '龍德':('其他','↔️ 中游-造船','軍艦'),
    }

    def classify(name):
        for k, v in chain_map.items():
            if k in name: return v
        if any(x in name for x in ['電','科','矽','晶','半']):
            return ('光電','一般光電','光電') if '光' in name else ('半導體','其他半導體','半導體')
        if any(x in name for x in ['網','通','訊']): return ('通信網路','網通設備','通信')
        if any(x in name for x in ['腦','機','資']): return ('電腦週邊','系統','電腦')
        if any(x in name for x in ['板','線','器','零']): return ('電子零組件','被動/連接','零組件')
        if any(x in name for x in ['生','醫','藥']): return ('生技醫療','生技','醫療')
        if any(x in name for x in ['綠','能','源']): return ('綠能環保','能源','綠能')
        if any(x in name for x in ['航','運','船']): return ('航運業','運輸','航運')
        if any(x in name for x in ['營','建','地']): return ('建材營造','建設','營造')
        if any(x in name for x in ['金','銀','保']): return ('金融業','金融','金控')
        if any(x in name for x in ['車','汽']): return ('汽車工業','零組件','汽車')
        return ('其他','未分類','其他')

    d = raw_df.copy()
    d[['L1','L2','L3']] = d['name'].apply(lambda x: pd.Series(classify(x)))
    d['ma87']       = pd.to_numeric(d.get('ma87', pd.Series(dtype=float)), errors='coerce')
    d['price']      = pd.to_numeric(d.get('stock_price_real', pd.Series(dtype=float)), errors='coerce')
    d['bias']       = (d['price'] - d['ma87']) / d['ma87'] * 100
    d['bias_clean'] = d['bias'].fillna(0).clip(-25, 25)
    d['bias_label'] = d['bias'].apply(lambda x: f"{x:+.1f}%" if pd.notnull(x) else "N/A")
    d['size_metric']= d['price'].fillna(10)
    return d


# ══════════════════════════════════════════════════════════════════════════════
#  CENSUS ENGINE  （原版 spinner 迴圈 100% 保留）
# ══════════════════════════════════════════════════════════════════════════════
def _run_census(df: pd.DataFrame, min_score: int):
    strat, _ = _load_engines()
    work_df  = df.copy()

    # 欄位對應（原版 rename_map 完整）
    rename_map = {
        '代號':'code', '名稱':'name', '可轉債市價':'price',
        '轉換價格':'conv_price', '轉換標的':'stock_code',
        '已轉換比例':'conv_rate', '轉換價值':'conv_value',
        '發行日':'issue_date', '賣回日':'put_date',
        '餘額比例':'balance_ratio'
    }
    work_df.rename(columns=lambda c: rename_map.get(c.strip(), c.strip()), inplace=True)

    # 餘額比例優先計算已轉換率（原版修正2）
    if 'balance_ratio' in work_df.columns:
        bal = pd.to_numeric(work_df['balance_ratio'], errors='coerce').fillna(100.0)
        work_df['conv_rate'] = 100.0 - bal

    # 數值欄位型別安全
    for col in ['price','conv_rate','conv_price','conv_value']:
        work_df[col] = pd.to_numeric(work_df.get(col, pd.Series(dtype=float)),
                                     errors='coerce').fillna(0.0)

    # 日期欄位處理
    for dcol in ['issue_date','put_date','list_date']:
        if dcol in work_df.columns:
            work_df[dcol] = pd.to_datetime(work_df[dcol], errors='coerce')
    if 'issue_date' not in work_df.columns and 'list_date' in work_df.columns:
        work_df['issue_date'] = work_df['list_date']

    try:
        scan_df = strat.scan_entire_portfolio(work_df)
        records = scan_df.to_dict('records')
    except Exception as e:
        st.toast(f"⚠️ 策略掃描失敗: {e}", icon="⚡")
        return pd.DataFrame(), pd.DataFrame()

    total = len(records)
    pbar  = st.progress(0)
    stxt  = st.empty()
    enriched = []

    for i, row in enumerate(records):
        name = row.get('name', '')
        stxt.text(f"普查進行中 ({i+1}/{total}): {name}…")

        code = str(row.get('stock_code', '')).strip()
        row.update({
            'stock_price_real': 0.0, 'ma87': 0.0, 'ma284': 0.0,
            'trend_status': '⚠️ 資料不足',
            'cb_price':       row.get('price', 0.0),
            'conv_price_val': row.get('conv_price', 0.0),
            'conv_value_val': row.get('conv_value', 0.0),
        })

        if code:
            try:
                hist = yf.Ticker(f"{code}.TW").history(period="2y")
                if hist.empty:
                    hist = yf.Ticker(f"{code}.TWO").history(period="2y")
                if not hist.empty and len(hist) > 284:
                    curr  = float(hist['Close'].iloc[-1])
                    ma87  = float(hist['Close'].rolling(87).mean().iloc[-1])
                    ma284 = float(hist['Close'].rolling(284).mean().iloc[-1])
                    row.update({'stock_price_real': curr, 'ma87': ma87, 'ma284': ma284})
                    if ma87 > ma284:
                        row['trend_status'] = '✅ 中期多頭'
                        row['score'] = min(100, row.get('score', 0) + 20)
                    else:
                        row['trend_status'] = '整理/空頭'
            except Exception:
                pass

        enriched.append(row)
        pbar.progress((i + 1) / total)

    stxt.text("✅ 普查完成！資料已同步至戰情室與全系統。")

    full_df = pd.DataFrame(enriched)
    for col in ['price','conv_rate']:
        if col not in full_df.columns:
            full_df[col] = 0.0

    sop_mask = (
        (full_df['price'] < 120) &
        (full_df['trend_status'].str.contains('多頭', na=False)) &
        (full_df['conv_rate'] < 30)
    )
    sop_df = full_df[sop_mask].sort_values('score', ascending=False)
    if 'score' in sop_df.columns:
        sop_df = sop_df[sop_df['score'] >= min_score]

    st.toast(f"✅ 全市場掃描結束，符合 SOP 黃金標準共 {len(sop_df)} 檔", icon="🎯")
    return sop_df, full_df


# ══════════════════════════════════════════════════════════════════════════════
#  REUSABLE PRIMITIVES (PRESERVED)
# ══════════════════════════════════════════════════════════════════════════════

def _scanner_hud(total: int, sop: int, bull: int, avg_score: float):
    st.markdown(f"""
<div class="t2-hud-grid">
  <div class="t2-hud-card" style="--hc:#00F5FF">
    <div class="t2-hud-lbl">Total Scanned</div>
    <div class="t2-hud-val">{total}</div>
    <div class="t2-hud-sub">CB 標的數量</div>
  </div>
  <div class="t2-hud-card" style="--hc:#00FF7F">
    <div class="t2-hud-lbl">SOP Targets</div>
    <div class="t2-hud-val">{sop}</div>
    <div class="t2-hud-sub">通過黃金標準</div>
  </div>
  <div class="t2-hud-card" style="--hc:#FF9A3C">
    <div class="t2-hud-lbl">Bull Trend</div>
    <div class="t2-hud-val">{bull}</div>
    <div class="t2-hud-sub">87MA &gt; 284MA</div>
  </div>
  <div class="t2-hud-card" style="--hc:#FFD700">
    <div class="t2-hud-lbl">Avg Score</div>
    <div class="t2-hud-val">{avg_score:.0f}</div>
    <div class="t2-hud-sub">SOP 平均評分</div>
  </div>
</div>""", unsafe_allow_html=True)


def _rule_card(icon, title, value, badge, state) -> str:
    return (
        f'<div class="t2-rule-card {state}">'
        f'<div class="t2-rule-icon">{icon}</div>'
        f'<div class="t2-rule-title">{title}</div>'
        f'<div class="t2-rule-val">{value}</div>'
        f'<div class="t2-rule-badge">{badge}</div>'
        f'</div>'
    )


def _four_commandments(row):
    """4 張 Sniper Checklist Cards（與原版天條完全一致）"""
    price    = pd.to_numeric(row.get('price'),  errors='coerce') or 0.0
    ma87     = pd.to_numeric(row.get('ma87'),   errors='coerce') or 0.0
    ma284    = pd.to_numeric(row.get('ma284'),  errors='coerce') or 0.0
    score    = pd.to_numeric(row.get('score'),  errors='coerce') or 0
    conv_pct = _safe_conv(row)
    is_bull  = ma87 > ma284

    html = "".join([
        _rule_card("✅" if price < 120 else "❌", "1. 價格天條",
                   f"{price:.1f}", "PASS &lt;120" if price < 120 else "FAIL ≥120",
                   "pass" if price < 120 else "fail"),
        _rule_card("✅" if is_bull else "⚠️",    "2. 中期多頭",
                   "87MA >" if is_bull else "87MA <",
                   "BULLISH" if is_bull else "BEARISH",
                   "pass" if is_bull else "warn"),
        _rule_card("✅" if conv_pct < 30 else "❌", "3. 已轉換率",
                   f"{conv_pct:.1f}%",
                   "CLEAN" if conv_pct < 30 else "HEAVY",
                   "pass" if conv_pct < 30 else "fail"),
        _rule_card("✅" if score >= 60 else "⚠️", "4. 策略評分",
                   f"{int(score)}", "ELITE ≥60" if score >= 60 else "WATCH",
                   "pass" if score >= 60 else "warn"),
    ])
    st.markdown(f'<div class="t2-rule-grid">{html}</div>', unsafe_allow_html=True)


def _detailed_report(row, title="📄 查看詳細分析報告 (Detailed Report)"):
    """原版詳細報告內容（4 Commandments + 決策輔助 + 交易計畫 + K 線）"""
    cb_code  = str(row.get('code', row.get('stock_code','0000'))).strip()
    cb_name  = row.get('name','未知')
    price    = pd.to_numeric(row.get('price'),  errors='coerce') or 0.0
    ma87     = pd.to_numeric(row.get('ma87'),   errors='coerce') or 0.0
    ma284    = pd.to_numeric(row.get('ma284'),  errors='coerce') or 0.0
    conv_pct = _safe_conv(row)
    is_bull  = ma87 > ma284
    cp       = pd.to_numeric(row.get('conv_price_val', 0.01), errors='coerce') or 0.01
    sp       = pd.to_numeric(row.get('stock_price_real', 0.0), errors='coerce') or 0.0
    cv       = pd.to_numeric(row.get('conv_value_val', 0.0), errors='coerce') or 0.0
    parity   = (sp / cp * 100) if cp > 0 else 0.0
    premium  = ((price - cv) / cv * 100) if cv > 0 else 0.0

    with st.expander(title, expanded=False):
        st.markdown(f"## 📊 {cb_name} ({cb_code}) 策略分析")

        analysis_summary = (
            f"【{cb_name} ({cb_code}) 狙擊分析】"
            f"CB市價 {price:.1f}，87MA {ma87:.2f}，284MA {ma284:.2f}。"
            f"{'多頭排列 ✅' if is_bull else '整理/空頭 ⚠️'}。"
            f"已轉換率 {conv_pct:.1f}%，理論價 {parity:.2f}，溢價率 {premium:.1f}%。"
        )
        stream_key = f"report_{cb_code}"
        if stream_key not in st.session_state:
            st.write_stream(_stream_text(analysis_summary, speed=0.010))
            st.session_state[stream_key] = True
        else:
            st.caption(analysis_summary)

        st.markdown("#### 1. 核心策略檢核 (The 4 Commandments)")
        st.markdown(f"1. 價格天條 (<115): {'✅ 通過' if price < 115 else '⚠️ 警戒'} (目前 **{price:.1f}**)")
        st.markdown(f"2. 中期多頭排列: {'✅ 通過' if is_bull else '⚠️ 整理中'}")
        st.markdown(f"> 均線數據: 87MA **{ma87:.2f}** {' > ' if is_bull else ' < '} 284MA **{ma284:.2f}**")
        st.markdown("3. 身分認證: ☐ 領頭羊 / ☐ 風口豬")
        st.markdown("4. 發債故事: ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")
        st.markdown("#### 2. 決策輔助 (Decision Support)")
        c1, c2, c3 = st.columns(3)
        c1.metric("理論價 (Parity)", f"{parity:.2f}")
        c2.metric("溢價率 (Premium)", f"{premium:.2f}%")
        c3.metric("已轉換比例", f"{conv_pct:.2f}%")
        st.markdown("#### 4. 交易計畫 (Trading Plan)")
        st.caption("🕒 關鍵時段：09:00 開盤後30分鐘 / 13:25 收盤前25分鐘")
        st.markdown("* 🎯 進場佈局: 105~115 元區間")
        st.markdown("* 🚀 加碼時機: 股價帶量突破 87MA 或 284MA")
        st.markdown("#### 5. 出場/風控 (Exit/Risk)")
        st.markdown("* 🛑 停損: CB 跌破 100 元")
        st.markdown("* 💰 停利: 目標價 152 元以上，嚴守「留魚尾」策略")
        st.divider()
        _plot_candle_chart(cb_code)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2.0 — 籌碼序幕 (CHIPS PROLOGUE) — Market Battlefield Map
# ══════════════════════════════════════════════════════════════════════════════
def render_2_0(df):
    """
    🎬 Section 2.0: 籌碼序幕 (Chips Prologue)
    Market Battlefield Map — Interactive Scatter Plot
    X-Axis: 轉換溢價率 (Premium Rate)
    Y-Axis: 收盤價 (Closing Price)
    Color: 已轉換比例 (Converted Ratio) or Premium heat
    """
    st.markdown("""
<div style="margin-bottom:20px;">
  <div style="font-family:var(--f-display);font-size:34px;color:#FFD700;
              letter-spacing:2px;margin-bottom:8px;
              text-shadow:0 0 30px rgba(255,215,0,.3);">
    🎬 籌碼序幕
  </div>
  <div style="font-family:var(--f-mono);font-size:11px;color:rgba(255,215,0,.4);
              letter-spacing:3px;text-transform:uppercase;">
    CHIPS PROLOGUE — MARKET BATTLEFIELD MAP
  </div>
</div>""", unsafe_allow_html=True)

    # Lazy loading mechanism
    if 'battlefield_loaded' not in st.session_state:
        st.session_state.battlefield_loaded = False

    if not st.session_state.battlefield_loaded:
        # Show initialization button
        if st.button("📡 初始化戰場地圖 (Initialize Battlefield Map)", 
                     use_container_width=True, type="primary"):
            st.session_state.battlefield_loaded = True
            st.rerun()
        
        st.markdown("""
<div style="text-align:center;padding:60px 30px;
            background:rgba(255,215,0,.02);
            border:1px solid rgba(255,215,0,.08);
            border-radius:16px;margin-top:20px;">
  <div style="font-size:56px;margin-bottom:16px;opacity:.3;">🗺️</div>
  <div style="font-family:var(--f-body);font-size:16px;color:rgba(255,215,0,.5);
              letter-spacing:2px;line-height:1.8;">
    戰場地圖尚未啟動<br>
    點擊上方按鈕以載入互動式籌碼分佈圖
  </div>
</div>""", unsafe_allow_html=True)
        return

    # Check if data is available
    if df.empty:
        st.warning("⚠️ 無可用數據。請先在首頁載入 CB 資料。")
        return

    # Find required columns (flexible column naming for actual Excel structure)
    # 債券代號 (A列), 標的債券 (B列), 可轉債市價 (N列), 溢(折)價率 (U列)
    code_col = next((c for c in df.columns if c == '債券代號' or 'code' in c.lower() or '代號' in c), None)
    name_col = next((c for c in df.columns if c == '標的債券' or ('標的' in c and '債券' in c)), None)
    price_col = next((c for c in df.columns if c == '可轉債市價' or ('可轉債' in c and '市價' in c)), None)
    premium_col = next((c for c in df.columns if c == '溢(折)價率' or ('溢' in c and '價率' in c)), None)
    balance_col = next((c for c in df.columns if '餘額比例' in c or 'balance' in c.lower()), None)

    if not all([code_col, name_col, price_col, premium_col]):
        st.error("❌ 資料欄位不完整。需要：代號、名稱、市價、溢(折)價率")
        st.info(f"偵測到的欄位: 代號={code_col}, 名稱={name_col}, 市價={price_col}, 溢價={premium_col}")
        st.info(f"前10個可用欄位：{', '.join(df.columns[:10])}...")
        return

    # Prepare data for visualization
    plot_df = df[[code_col, name_col, price_col, premium_col]].copy()
    plot_df.columns = ['ticker', 'name', 'price', 'premium']
    
    # Calculate converted ratio from balance ratio (100% - 餘額比例 = 已轉換比例)
    if balance_col:
        balance = pd.to_numeric(df[balance_col], errors='coerce').fillna(100.0)
        plot_df['converted'] = 100.0 - balance
    else:
        plot_df['converted'] = 0  # Default if not available

    # Clean data - handle premium as string with % symbol
    plot_df = plot_df.dropna(subset=['price', 'premium'])
    plot_df['price'] = pd.to_numeric(plot_df['price'], errors='coerce')
    
    # Handle premium - may contain % symbol or be negative/string
    def clean_premium(val):
        if pd.isna(val):
            return None
        if isinstance(val, str):
            # Remove % and other non-numeric characters except . and -
            val = val.replace('%', '').replace(',', '').strip()
            try:
                return float(val)
            except:
                return None
        return float(val)
    
    plot_df['premium'] = plot_df['premium'].apply(clean_premium)
    plot_df['converted'] = pd.to_numeric(plot_df['converted'], errors='coerce').fillna(0)
    plot_df = plot_df.dropna(subset=['price', 'premium'])

    if plot_df.empty:
        st.warning("⚠️ 清理後無有效數據可視覺化")
        return

    # Create zone classifications
    def classify_zone(row):
        if row['premium'] < 10 and row['price'] < 120:
            return '🟩 Sniper Zone (獵殺區)'
        elif row['premium'] > 30 or row['price'] > 150:
            return '🟥 Danger Zone (避雷區)'
        else:
            return '🟨 Neutral Zone (中性區)'
    
    plot_df['zone'] = plot_df.apply(classify_zone, axis=1)

    # Stats summary
    total = len(plot_df)
    sniper = len(plot_df[plot_df['zone'].str.contains('Sniper')])
    danger = len(plot_df[plot_df['zone'].str.contains('Danger')])
    neutral = total - sniper - danger

    st.markdown(f"""
<div class="t2-hud-grid">
  <div class="t2-hud-card" style="--hc:#FFD700;">
    <div class="t2-hud-lbl">TOTAL CBs</div>
    <div class="t2-hud-val">{total}</div>
    <div class="t2-hud-sub">Market Size</div>
  </div>
  <div class="t2-hud-card" style="--hc:#00FF7F;">
    <div class="t2-hud-lbl">SNIPER ZONE</div>
    <div class="t2-hud-val">{sniper}</div>
    <div class="t2-hud-sub">{sniper/total*100:.1f}% 優質標的</div>
  </div>
  <div class="t2-hud-card" style="--hc:#FF3131;">
    <div class="t2-hud-lbl">DANGER ZONE</div>
    <div class="t2-hud-val">{danger}</div>
    <div class="t2-hud-sub">{danger/total*100:.1f}% 高風險</div>
  </div>
  <div class="t2-hud-card" style="--hc:#00F5FF;">
    <div class="t2-hud-lbl">NEUTRAL ZONE</div>
    <div class="t2-hud-val">{neutral}</div>
    <div class="t2-hud-sub">{neutral/total*100:.1f}% 觀察中</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Create interactive scatter plot
    fig = px.scatter(
        plot_df,
        x='premium',
        y='price',
        color='converted',
        size='price',
        hover_data={
            'ticker': True,
            'name': True,
            'price': ':.2f',
            'premium': ':.2f',
            'converted': ':.2f',
            'zone': True
        },
        color_continuous_scale='RdYlGn_r',
        title='Market Battlefield Map — 籌碼分佈圖'
    )

    # Add zone boundaries
    fig.add_shape(
        type="rect",
        x0=-5, x1=10, y0=0, y1=120,
        fillcolor="rgba(0,255,127,0.08)",
        line=dict(color="rgba(0,255,127,0.3)", width=2, dash="dash"),
        layer="below"
    )
    
    fig.add_shape(
        type="rect",
        x0=30, x1=plot_df['premium'].max() + 5, y0=0, y1=plot_df['price'].max() + 10,
        fillcolor="rgba(255,49,49,0.08)",
        line=dict(color="rgba(255,49,49,0.3)", width=2, dash="dash"),
        layer="below"
    )

    # Customize layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Rajdhani, sans-serif', color='#CCD'),
        xaxis=dict(
            title='轉換溢價率 (%) — Premium Rate (Cost Axis)',
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=False
        ),
        yaxis=dict(
            title='收盤價 (元) — Closing Price (Value Axis)',
            gridcolor='rgba(255,255,255,0.05)',
            zeroline=False
        ),
        coloraxis_colorbar=dict(
            title="已轉換比例 (%)",
            tickfont=dict(family='JetBrains Mono'),
            titlefont=dict(family='Rajdhani')
        ),
        height=600,
        hovermode='closest'
    )

    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='rgba(255,255,255,0.3)'),
            sizemode='diameter',
            sizemin=4
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Zone interpretation guide
    st.markdown("""
<div style="background:rgba(255,255,255,.015);border:1px solid rgba(255,255,255,.05);
            border-radius:12px;padding:18px 20px;margin-top:20px;">
  <div style="font-family:var(--f-body);font-size:16px;font-weight:700;
              color:#00F5FF;margin-bottom:12px;">
    📊 戰場區域解讀 (Zone Interpretation)
  </div>
  <div style="font-family:var(--f-body);font-size:13px;color:#BBC;line-height:1.8;">
    <strong style="color:#00FF7F;">🟩 Sniper Zone (獵殺區)</strong>: 低溢價 (<10%) + 低價格 (<120) = 高 CP 值標的<br>
    <strong style="color:#FFD700;">🟨 Neutral Zone (中性區)</strong>: 觀察中標的，需進一步分析趨勢與籌碼<br>
    <strong style="color:#FF3131;">🟥 Danger Zone (避雷區)</strong>: 高溢價 (>30%) 或高價 (>150) = 風險較高
  </div>
</div>""", unsafe_allow_html=True)

    # Top sniper targets
    if sniper > 0:
        sniper_df = plot_df[plot_df['zone'].str.contains('Sniper')].copy()
        sniper_df = sniper_df.sort_values('premium').head(10)
        
        st.markdown("""
<div style="margin-top:24px;margin-bottom:12px;">
  <div style="font-family:var(--f-body);font-size:18px;font-weight:700;
              color:#00FF7F;text-shadow:0 0 20px rgba(0,255,127,.2);">
    🎯 Top 10 Sniper Targets (優質獵殺標的)
  </div>
</div>""", unsafe_allow_html=True)

        # Create table HTML
        table_rows = ""
        for idx, row in sniper_df.iterrows():
            table_rows += f"""
<tr>
  <td style="font-family:var(--f-mono);color:#00F5FF;">{row['ticker']}</td>
  <td>{row['name']}</td>
  <td style="font-family:var(--f-mono);text-align:right;">{row['price']:.2f}</td>
  <td style="font-family:var(--f-mono);text-align:right;color:#00FF7F;">{row['premium']:.2f}%</td>
  <td style="font-family:var(--f-mono);text-align:right;">{row['converted']:.2f}%</td>
</tr>"""

        st.markdown(f"""
<table class="t2-tbl">
  <thead>
    <tr>
      <th>Ticker</th>
      <th>Name</th>
      <th style="text-align:right;">Price</th>
      <th style="text-align:right;">Premium</th>
      <th style="text-align:right;">Converted</th>
    </tr>
  </thead>
  <tbody>
    {table_rows}
  </tbody>
</table>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2.1  ──  自動獵殺 + 6 Strategy Pills  **PRESERVED 100%**
# ══════════════════════════════════════════════════════════════════════════════
def render_2_1(df: pd.DataFrame):
    st.markdown('<div class="t2-sec-title">📡 2.1 自動獵殺推薦 — Strategy Matrix</div>',
                unsafe_allow_html=True)

    if df.empty:
        st.markdown('<div class="t2-empty"><div class="t2-empty-icon">📂</div>'
                    '<div class="t2-empty-text">Upload CB List to Activate Census</div></div>',
                    unsafe_allow_html=True)
        return

    st.caption("此模組執行「全市場雙軌普查 (.TW/.TWO)」，並同步更新全系統連動資料庫。")

    ctrl_l, ctrl_r = st.columns([3, 1])
    with ctrl_l:
        min_score = st.slider("最低評分門檻", 0, 100, 50, key="t21_minscore")
    with ctrl_r:
        st.markdown('<div class="t2-action" style="margin-top:24px;">', unsafe_allow_html=True)
        if st.button("🚀  LAUNCH CENSUS", key="btn_census"):
            st.toast("🚀 全市場雙軌普查啟動中…", icon="⏳")
            with st.spinner("執行全市場雙軌普查 (.TW / .TWO)…"):
                sop_df, full_df = _run_census(df, min_score)
                st.session_state['scan_results']     = sop_df
                st.session_state['full_census_data'] = full_df.to_dict('records')
        st.markdown('</div>', unsafe_allow_html=True)

    full_data = pd.DataFrame(st.session_state.get('full_census_data', []))
    sop_df    = st.session_state.get('scan_results', pd.DataFrame())

    if not full_data.empty:
        bull_n = 0
        if 'trend_status' in full_data.columns:
            bull_n = len(full_data[full_data['trend_status'].str.contains('多頭', na=False)])
        avg_sc = float(sop_df['score'].mean()) if (not sop_df.empty and 'score' in sop_df.columns) else 0.0
        _scanner_hud(len(full_data), len(sop_df), bull_n, avg_sc)

        census_text = (
            f"【普查摘要】共掃描 {len(full_data)} 檔 CB，"
            f"其中 {bull_n} 檔處於多頭排列 (87MA > 284MA)，"
            f"通過 SOP 黃金標準 {len(sop_df)} 檔"
            f"{'，平均評分 ' + f'{avg_sc:.0f}' if avg_sc > 0 else ''}。"
        )
        if 'census_streamed' not in st.session_state:
            st.write_stream(_stream_text(census_text, speed=0.012))
            st.session_state['census_streamed'] = True
        else:
            st.caption(census_text)

        for dcol in ['issue_date','put_date']:
            if dcol in full_data.columns:
                full_data[dcol] = pd.to_datetime(full_data[dcol], errors='coerce')
    else:
        st.caption("↑ 點擊 LAUNCH CENSUS 啟動普查")

    # ── Strategy Pill Rail ────────────────────────────────────────
    PILLS = [
        ("global",    "🌍", "全市場"),
        ("sop",       "🏆", "SOP菁英"),
        ("honeymoon", "👶", "新券蜜月"),
        ("sediment",  "⚓", "滿年沈澱"),
        ("put",       "🛡️", "賣回保衛"),
        ("sector",    "🌪️", "產業風口"),
    ]
    if 't21_pill' not in st.session_state:
        st.session_state.t21_pill = "global"

    pill_cols = st.columns(len(PILLS))
    for col, (key, icon, label) in zip(pill_cols, PILLS):
        is_a  = (key == st.session_state.t21_pill)
        brd   = "1.5px solid rgba(255,215,0,0.55)" if is_a else "1px solid rgba(255,255,255,0.065)"
        bg_c  = "rgba(255,215,0,0.07)" if is_a else "rgba(255,255,255,0.022)"
        txt_c = "#FFD700" if is_a else "rgba(148,168,196,0.48)"
        shd   = "0 0 12px rgba(255,215,0,0.12)" if is_a else "none"
        with col:
            st.markdown(
                f'<div style="background:{bg_c};border:{brd};border-radius:30px;'
                f'text-align:center;padding:7px 2px;font-family:JetBrains Mono,monospace;'
                f'font-size:11px;letter-spacing:1.5px;color:{txt_c};box-shadow:{shd};'
                f'text-transform:uppercase;margin-bottom:-54px;pointer-events:none;'
                f'position:relative;z-index:0;">{icon} {label}</div>',
                unsafe_allow_html=True
            )
            if st.button(f"{icon} {label}", key=f"pill_{key}", use_container_width=True):
                st.session_state.t21_pill = key
                st.rerun()

    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    if full_data.empty:
        return

    now  = datetime.now()
    pill = st.session_state.t21_pill

    # ── 🌍 全市場 ──────────────────────────────────────────────────
    if pill == "global":
        if not sop_df.empty:
            st.markdown(
                f'<div style="font-family:var(--f-mono);font-size:10px;color:#00FF7F;'
                f'letter-spacing:1.5px;margin:12px 0 10px;text-transform:uppercase;">'
                f'✅ {len(sop_df)} 檔通過 SOP 黃金標準</div>', unsafe_allow_html=True)
            disp = [c for c in ['code','name','price','stock_price_real',
                                 'trend_status','conv_rate','score'] if c in sop_df.columns]
            st.dataframe(sop_df[disp].head(30), use_container_width=True)
        else:
            st.caption("執行普查後，全市場 SOP 標的將顯示於此。")

    # ── 🏆 SOP菁英 (原版 Tab1 邏輯) ────────────────────────────────
    elif pill == "sop":
        df_t = sop_df.head(20) if not sop_df.empty else pd.DataFrame()
        if df_t.empty:
            mask = ((full_data.get('price', pd.Series(0)) < 120) &
                    (full_data.get('trend_status', pd.Series('')).str.contains('多頭', na=False)))
            df_t = full_data[mask].sort_values('score', ascending=False).head(20) \
                   if 'score' in full_data.columns else full_data[mask].head(20)
        if df_t.empty:
            st.caption("無符合 SOP 黃金標準的標的。"); return

        st.caption(f"共 {len(df_t)} 檔通過 SOP 黃金標準")
        for _, row in df_t.iterrows():
            cb_name  = row.get('name','未知')
            cb_code  = str(row.get('code', row.get('stock_code','0000'))).strip()
            price    = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
            score    = pd.to_numeric(row.get('score'), errors='coerce') or 0
            conv_pct = _safe_conv(row)
            ma87     = pd.to_numeric(row.get('ma87'), errors='coerce') or 0.0
            ma284    = pd.to_numeric(row.get('ma284'), errors='coerce') or 0.0

            title = f"👑 {cb_name} ({cb_code}) | CB價: {price:.1f} | 評分: {int(score)}"
            with st.expander(title):
                st.markdown(
                    f"### 🛡️ 天條檢核: "
                    f"`✅ 價格<120` | `✅ 均線多頭` | `✅ 已轉換率 {conv_pct:.2f}%`"
                )
                st.divider()
                _four_commandments(row)
                _detailed_report(row)

    # ── 👶 新券蜜月 ───────────────────────────────────────────────────────
    elif pill == "honeymoon":
        if 'issue_date' not in full_data.columns:
            st.toast("⚠️ 普查資料無 issue_date 欄位", icon="⚡"); return
        mask = (
            full_data['issue_date'].notna() &
            ((now - full_data['issue_date']).dt.days < 90) &
            (full_data.get('price', pd.Series(999)) < 130) &
            (full_data.get('conv_rate', pd.Series(100)) < 30)
        )
        df_t = full_data[mask].sort_values('issue_date', ascending=False)
        if df_t.empty:
            st.caption("目前無符合「新券蜜月」標準 (上市<90天 · 價格<130 · 轉換率<30%)。"); return

        st.caption(f"共 {len(df_t)} 檔蜜月期新券")
        for _, row in df_t.iterrows():
            name     = row.get('name','未知')
            cb_code  = str(row.get('code', row.get('stock_code','0000'))).strip()
            days     = int((now - row['issue_date']).days)
            price    = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
            conv_pct = _safe_conv(row)
            ma87     = pd.to_numeric(row.get('ma87'),  errors='coerce') or 0.0
            ma284    = pd.to_numeric(row.get('ma284'), errors='coerce') or 0.0
            is_bull  = ma87 > ma284
            cp       = pd.to_numeric(row.get('conv_price_val',0.01), errors='coerce') or 0.01
            sp       = pd.to_numeric(row.get('stock_price_real',0.0), errors='coerce') or 0.0
            cv       = pd.to_numeric(row.get('conv_value_val',0.0),  errors='coerce') or 0.0
            parity   = (sp/cp*100) if cp > 0 else 0.0
            premium  = ((price-cv)/cv*100) if cv > 0 else 0.0
            trend_t  = "✅ 多頭排列" if is_bull else ("⚠️ 資料不足或整理中" if ma87 == 0 else "❌ 偏弱")

            title = f"👶 {name} ({cb_code}) | 上市 {days} 天 | CB價: {price:.1f}"
            with st.expander(title):
                st.markdown(
                    f"### 🛡️ 新券檢核: `✅ 上市 {days} 天` | "
                    f"`✅ 價格 < 130` | `✅ 已轉換 {conv_pct:.2f}%`"
                )
                st.divider()
                _four_commandments(row)
                with st.expander("📄 查看蜜月期深度分析 (Honeymoon Report)", expanded=False):
                    st.markdown(f"## 📊 {name} ({cb_code}) 蜜月期戰略")

                    honey_text = (
                        f"【蜜月期戰略分析】{name} ({cb_code}) 上市 {days} 天。"
                        f"CB市價 {price:.1f}，理論價 {parity:.2f}，溢價率 {premium:.1f}%。"
                        f"趨勢: {trend_t}。已轉換率 {conv_pct:.1f}%。"
                    )
                    hkey = f"honey_{cb_code}"
                    if hkey not in st.session_state:
                        st.write_stream(_stream_text(honey_text, speed=0.010))
                        st.session_state[hkey] = True
                    else:
                        st.caption(honey_text)

                    st.markdown("#### 1. 核心策略檢核 (The 4 Commandments)")
                    st.markdown(f"1. 蜜月期價格: {'✅ 通過' if price < 115 else '⚠️ 監控'} (新券甜蜜區 105-115，目前 **{price:.1f}**)")
                    st.markdown(f"2. 中期多頭排列: {trend_t}")
                    if ma87 > 0:
                        st.markdown(f"> 均線數據: 87MA **{ma87:.2f}** {' > ' if is_bull else ' < '} 284MA **{ma284:.2f}**")
                    else:
                        st.caption("(新券上市天數較短，均線指標僅供參考)")
                    st.markdown("3. 身分認證: ☐ 領頭羊 / ☐ 風口豬")
                    st.markdown("4. 發債故事: ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")
                    st.markdown("#### 2. 決策輔助 (Decision Support)")
                    c1,c2,c3 = st.columns(3)
                    c1.metric("理論價 (Parity)", f"{parity:.2f}")
                    c2.metric("溢價率 (Premium)", f"{premium:.2f}%")
                    c3.metric("已轉換比例", f"{conv_pct:.2f}%")
                    st.markdown("#### 4. 交易計畫 (Trading Plan)")
                    st.caption("🕒 09:00 開盤後30分鐘 / 13:25 收盤前25分鐘")
                    st.markdown("* 🎯 新券上市初期若 ≤110 為極佳安全邊際")
                    st.markdown("* 🚀 加碼: 帶量突破 87MA 或 284MA")
                    st.markdown("#### 5. 出場/風控")
                    st.markdown("* 🛑 停損: CB 跌破 100 元  · 💰 停利: 152 元以上")
                    st.divider()
                    _plot_candle_chart(cb_code)

    # ── ⚓ 滿年沈澱 ────────────────────────────────────────────────────────
    elif pill == "sediment":
        if 'issue_date' not in full_data.columns:
            st.toast("⚠️ 普查資料無 issue_date 欄位", icon="⚡"); return
        fd = full_data.copy().dropna(subset=['issue_date'])
        fd['days_old'] = (now - fd['issue_date']).dt.days

        def check_mask_t3(row):
            try:
                if not (350 <= row['days_old'] <= 420): return False
                p = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                if p >= 115 or p <= 0: return False
                raw_c = pd.to_numeric(row.get('conv_rate',100), errors='coerce') or 100.0
                actual_conv = (100.0 - raw_c) if raw_c > 50 else raw_c
                return actual_conv < 30
            except: return False

        df_t = fd[fd.apply(check_mask_t3, axis=1)].sort_values('days_old')
        if df_t.empty:
            st.caption("目前無符合「滿年沈澱」標準 (上市滿一年 · 價格<115 · 轉換率<30%)。"); return

        st.caption(f"共 {len(df_t)} 檔滿年沈澱標的")
        for _, row in df_t.iterrows():
            name     = row.get('name','未知')
            cb_code  = str(row.get('code', row.get('stock_code','0000'))).strip()
            days     = int(row['days_old'])
            price    = pd.to_numeric(row.get('price'),  errors='coerce') or 0.0
            ma87     = pd.to_numeric(row.get('ma87'),   errors='coerce') or 0.0
            ma284    = pd.to_numeric(row.get('ma284'),  errors='coerce') or 0.0
            sp       = pd.to_numeric(row.get('stock_price_real'), errors='coerce') or 0.0
            conv_pct = _safe_conv(row)
            is_above = sp > ma87 if ma87 > 0 else False

            title = f"⚓ {name} ({cb_code}) | 沈澱 {days} 天 (滿週年) | CB價: {price:.1f}"
            with st.expander(title):
                st.markdown(
                    f"### 🛡️ 沈澱檢核: `✅ 上市 {days} 天` | `✅ 價格 < 115` | "
                    f"`{'✅ 已站上 87MA' if is_above else '⚠️ 均線下方'}`"
                )
                st.divider()
                _four_commandments(row)
                with st.expander("📄 查看滿年沈澱深度分析 (Consolidation Report)", expanded=False):
                    st.markdown(f"## 📊 {name} ({cb_code}) 滿年甦醒評估")
                    st.markdown("#### 1. 核心策略檢核 (The 4 Commandments)")
                    st.markdown(f"1. 價格天條 (<115): ✅ 通過 (沈澱期最佳成本區，目前 **{price:.1f}**)")
                    check_t = "✅ 通過 (已站上 87MA)" if is_above else "⚠️ 均線整理中"
                    st.markdown(f"2. 中期多頭排列: {check_t}")
                    if ma87 > 0:
                        st.markdown(f"> 現價 **{sp:.2f}** {' > ' if is_above else ' < '} 87MA **{ma87:.2f}**")
                    st.markdown("3. 身分認證: ☐ 領頭羊 / ☐ 風口豬")
                    st.markdown("4. 發債故事: ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")
                    st.markdown("#### 2. 決策輔助")
                    cp = pd.to_numeric(row.get('conv_price_val',0.01), errors='coerce') or 0.01
                    cv = pd.to_numeric(row.get('conv_value_val',0.0),  errors='coerce') or 0.0
                    parity  = (sp/cp*100) if cp > 0 else 0.0
                    premium = ((price-cv)/cv*100) if cv > 0 else 0.0
                    c1,c2,c3 = st.columns(3)
                    c1.metric("理論價", f"{parity:.2f}")
                    c2.metric("溢價率", f"{premium:.2f}%")
                    c3.metric("已轉換", f"{conv_pct:.2f}%")
                    st.markdown("#### 4. 交易計畫")
                    st.markdown("* 🎯 站穩 87MA 即為首波觀察進場點")
                    st.markdown("* 🚀 87MA 由平轉上揚時加碼")
                    st.markdown("#### 5. 出場/風控")
                    st.markdown("* 🛑 停損: CB 跌破 100 元  · 💰 停利: 152 元以上")
                    st.divider()
                    _plot_candle_chart(cb_code)

    # ── 🛡️ 賣回保衛 ─────────────────────────────────────────────────
    elif pill == "put":
        if 'put_date' not in full_data.columns:
            st.toast("⚠️ 普查資料無 put_date 欄位", icon="⚡"); return
        fd = full_data.copy()
        fd['put_date']    = pd.to_datetime(fd['put_date'], errors='coerce')
        fd['days_to_put'] = (fd['put_date'] - now).dt.days

        def check_mask_t4(row):
            try:
                dtp = row['days_to_put']
                if pd.isna(dtp) or not (0 < dtp < 180): return False
                p = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
                if not (95 <= p <= 105): return False
                raw_c = pd.to_numeric(row.get('conv_rate',100), errors='coerce') or 100.0
                actual_conv = (100.0 - raw_c) if raw_c > 50 else raw_c
                return actual_conv < 30
            except: return False

        df_t = fd[fd.apply(check_mask_t4, axis=1)].sort_values('days_to_put')
        if df_t.empty:
            st.caption("目前無符合「賣回保衛」標準 (距賣回<180天 · 價格 95~105 · 轉換率<30%)。"); return

        st.caption(f"共 {len(df_t)} 檔賣回套利機會")
        for _, row in df_t.iterrows():
            name     = row.get('name','未知')
            cb_code  = str(row.get('code', row.get('stock_code','0000'))).strip()
            left     = int(row['days_to_put'])
            price    = pd.to_numeric(row.get('price'),  errors='coerce') or 0.0
            ma87     = pd.to_numeric(row.get('ma87'),   errors='coerce') or 0.0
            ma284    = pd.to_numeric(row.get('ma284'),  errors='coerce') or 0.0
            sp       = pd.to_numeric(row.get('stock_price_real'), errors='coerce') or 0.0
            conv_pct = _safe_conv(row)
            pd_str   = row['put_date'].strftime('%Y-%m-%d') if pd.notnull(row['put_date']) else 'N/A'
            is_bull  = ma87 > ma284
            cp       = pd.to_numeric(row.get('conv_price_val',0.01), errors='coerce') or 0.01
            cv       = pd.to_numeric(row.get('conv_value_val',0.0),  errors='coerce') or 0.0
            parity   = (sp/cp*100) if cp > 0 else 0.0
            premium  = ((price-cv)/cv*100) if cv > 0 else 0.0

            title = f"🛡️ {name} ({cb_code}) | 賣回倒數 {left} 天 | CB價: {price:.1f}"
            with st.expander(title):
                st.markdown(
                    f"### 🚨 保衛警告: `📅 賣回日: {pd_str}` | "
                    f"`✅ 價格甜甜圈區間` | `✅ 已轉換 {conv_pct:.2f}%`"
                )
                st.divider()
                _four_commandments(row)
                with st.expander("📄 查看賣回保衛戰術報告 (Put Protection Report)", expanded=False):
                    st.markdown(f"## 📊 {name} ({cb_code}) 賣回壓力測試")
                    st.markdown("#### 1. 核心策略檢核 (The 4 Commandments)")
                    st.markdown(f"1. 價格天條 (95-105): ✅ 通過 (目前 **{price:.1f}**)")
                    st.markdown(f"2. 中期多頭排列: {'✅ 通過' if is_bull else '⚠️ 整理中'}")
                    st.markdown("3. 身分認證: ☐ 領頭羊 / ☐ 風口豬")
                    st.markdown("4. 發債故事: ☐ 從無到有 / ☐ 擴產 / ☐ 政策事件")
                    st.markdown("#### 2. 決策輔助")
                    c1,c2,c3 = st.columns(3)
                    c1.metric("距離賣回", f"{left} 天")
                    c2.metric("溢價率 (Premium)", f"{premium:.2f}%")
                    c3.metric("目標價", "152+", delta="保本套利")
                    st.markdown("#### 4. 交易計畫")
                    st.markdown(f"* 🎯 {pd_str} 前買入，下檔風險極低")
                    st.markdown("* 🚀 爆發點: 觀察賣回日前 2-3 個月，股價站上 87MA 且量增")
                    st.markdown("#### 5. 出場/風控")
                    st.markdown("* 🛑 停損: 原則上不需停損  · 💰 停利: 152 元以上，或賣回當天執行")
                    st.divider()
                    _plot_candle_chart(cb_code)

    # ── 🌪️ 產業風口地圖 ─────────────────────────────────────────────────
    elif pill == "sector":
        if 'full_census_data' not in st.session_state:
            st.toast("⚠️ 請先執行普查", icon="⚡"); return

        full_json = pd.DataFrame(st.session_state['full_census_data']).to_json()
        df_gal    = _get_tpex_data(full_json)
        if df_gal.empty:
            st.caption("無資料，請先執行普查。"); return

        # ─ Treemap
        fig = px.treemap(
            df_gal, path=['L1','L2','L3','name'], values='size_metric',
            color='bias_clean',
            color_continuous_scale=['#00FF00','#262730','#FF0000'],
            color_continuous_midpoint=0,
            hover_data={'name':True,'bias_label':True,'L3':True,
                        'size_metric':False,'bias_clean':False},
            title='<b>🎯 資金流向熱力圖 (IC.TPEX 官方分類版)</b>'
        )
        fig.update_layout(
            margin=dict(t=30,l=10,r=10,b=10), height=500,
            font=dict(size=14,family='Rajdhani'),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            title_font_color='#FFD700'
        )
        fig.update_traces(
            textinfo="label+text",
            texttemplate="%{label}<br>%{customdata[1]}",
            textposition="middle center"
        )
        st.markdown('<div class="t2-chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.divider()

        # ─ Sector Roster
        st.markdown(
            '<div style="font-family:var(--f-display);font-size:20px;color:#00F5FF;'
            'letter-spacing:2px;margin-bottom:14px;">🏆 全產業戰力排行榜</div>',
            unsafe_allow_html=True
        )
        st.caption("💡 點擊下方官方產業板塊，展開查看「上中下游」兵力部署")

        sector_stats = df_gal.groupby('L1')['bias'].mean().sort_values(ascending=False)
        for sector, avg_bias in sector_stats.items():
            sector_df = df_gal[df_gal['L1'] == sector]
            count     = len(sector_df)
            if count == 0: continue
            bulls     = len(sector_df[sector_df['bias'] > 0])
            flag      = "🔴" if avg_bias > 0 else "🟢"
            header    = f"{flag} **{sector}** (均 {avg_bias:+.1f}%) | 強勢 {bulls}/{count} 檔"

            with st.expander(header):
                l2_groups = sector_df.groupby('L2')
                sorted_l2 = sorted(l2_groups.groups.keys(),
                                    key=lambda x: 0 if '上' in str(x) else (1 if '中' in str(x) else 2))
                for l2 in sorted_l2:
                    sub_df = l2_groups.get_group(l2).sort_values('bias', ascending=False)
                    st.markdown(f"**{l2}**")
                    cols = st.columns(3)
                    for _, row in sub_df.iterrows():
                        color = "red" if row['bias'] > 0 else "#00FF00"
                        st.markdown(
                            f"<span style='color:{color};font-weight:bold;'>"
                            f"{row.get('code','')} {row['name']}</span> "
                            f"<span style='color:#aaa;font-size:.9em;'>({row['bias_label']})</span>",
                            unsafe_allow_html=True
                        )
                    st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2.2  ──  核心策略檢核 (Sniper Scope)  **PRESERVED 100%**
# ══════════════════════════════════════════════════════════════════════════════
def render_2_2():
    st.markdown('<div class="t2-sec-title">📈 2.2 核心策略檢核 — Sniper Scope</div>',
                unsafe_allow_html=True)

    if 'full_census_data' not in st.session_state:
        st.toast("⚠️ 請先至 2.1 執行 SOP 全市場普查", icon="⚡")
        return

    full_data = pd.DataFrame(st.session_state['full_census_data'])
    if 'issue_date' in full_data.columns:
        full_data['issue_date'] = pd.to_datetime(full_data['issue_date'], errors='coerce')

    st.caption("↓ 輸入 CB 代號 (5碼) 拉取即時 K 線 + 4 天條檢核")
    cb_input = st.text_input("CB 代號 (5碼)", value="", placeholder="e.g. 12345",
                              label_visibility="collapsed", key="t22_input")

    if cb_input.strip():
        _plot_candle_chart(cb_input.strip())
        code_col = 'code' if 'code' in full_data.columns else None
        matched  = full_data[full_data[code_col] == cb_input.strip()] if code_col else pd.DataFrame()
        if not matched.empty:
            st.markdown(
                '<div style="font-family:var(--f-mono);font-size:10px;color:#334455;'
                'letter-spacing:2px;margin:16px 0 10px;text-transform:uppercase;">'
                'Commandment Status ── from Census Data</div>', unsafe_allow_html=True)
            _four_commandments(matched.iloc[0])
            row = matched.iloc[0]
            cb_name  = row.get('name','未知')
            price    = pd.to_numeric(row.get('price'), errors='coerce') or 0.0
            score    = pd.to_numeric(row.get('score'), errors='coerce') or 0
            with st.expander(f"👑 {cb_name} ({cb_input.strip()}) | CB價: {price:.1f} | 評分: {int(score)}"):
                _detailed_report(row)
        else:
            st.caption("⚠️ 此代號不在普查資料中，顯示 K 線圖但無法顯示檢核卡。請先執行 2.1 普查。")
    else:
        sop = st.session_state.get('scan_results', pd.DataFrame())
        if not sop.empty:
            st.caption("或從 SOP 候選標的中選取：")
            opts = [f"{r.get('code','')} — {r.get('name','')}" for _, r in sop.head(20).iterrows()]
            sel  = st.selectbox("選擇標的", ["— 請選擇 —"] + opts, key="t22_sel")
            if sel != "— 請選擇 —":
                code = sel.split("—")[0].strip()
                _plot_candle_chart(code)
                m = sop[sop.get('code', pd.Series()) == code]
                if not m.empty:
                    _four_commandments(m.iloc[0])
                    _detailed_report(m.iloc[0])
        else:
            st.markdown('<div class="t2-empty"><div class="t2-empty-icon">🎯</div>'
                        '<div class="t2-empty-text">Run Census in 2.1 or enter CB code above</div></div>',
                        unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2.3  ──  風險雷達  **PRESERVED 100%**
# ══════════════════════════════════════════════════════════════════════════════
def render_2_3():
    st.markdown('<div class="t2-sec-title">⚠️ 2.3 潛在風險雷達 — Negative Screener</div>',
                unsafe_allow_html=True)

    if 'scan_results' not in st.session_state or st.session_state['scan_results'].empty:
        st.caption("請先執行本頁上方的掃描以啟動風險雷達。")
        return

    scan = st.session_state['scan_results']
    st.caption("此區塊為「負面表列」清單，旨在警示符合特定風險條件的標的，提醒您「避開誰」。")

    conv_col   = 'converted_ratio' if 'converted_ratio' in scan.columns else \
                 ('conv_rate'       if 'conv_rate'       in scan.columns else None)
    prem_col   = 'premium'    if 'premium'    in scan.columns else None
    vol_col    = 'avg_volume' if 'avg_volume' in scan.columns else None

    if conv_col and prem_col and vol_col:
        tab1_w13, tab2_w13, tab3_w13 = st.tabs([
            "**☠️ 籌碼鬆動 (主力落跑)**",
            "**⚠️ 高溢價 (肉少湯喝)**",
            "**🧊 流動性陷阱 (殭屍債)**"
        ])

        with tab1_w13:
            loose = scan[scan[conv_col] > 30].sort_values(conv_col, ascending=False)
            if not loose.empty:
                st.toast(f"⚠️ 發現 {len(loose)} 檔籌碼鬆動標的", icon="⚡")
                for _, row in loose.head(20).iterrows():
                    cr    = pd.to_numeric(row.get(conv_col, 0), errors='coerce') or 0.0
                    price = pd.to_numeric(row.get('price', 0),  errors='coerce') or 0.0
                    name  = row.get('name',''); code = row.get('code','')
                    st.markdown(f"""
<div class="t2-warn-card">
  <div class="t2-warn-value">{cr:.1f}%</div>
  <div class="t2-warn-header">{name}  ({code})</div>
  <div class="t2-warn-meta">CB市價 {price:.1f} &nbsp;·&nbsp; 已轉換 {cr:.1f}% &nbsp;·&nbsp; 籌碼鬆動風險</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="t2-warn-ok">✅ 目前無標的觸發「籌碼鬆動」警示。</div>',
                            unsafe_allow_html=True)

        with tab2_w13:
            overp = scan[scan[prem_col] > 20].sort_values(prem_col, ascending=False)
            if not overp.empty:
                st.toast(f"⚠️ 發現 {len(overp)} 檔高溢價標的", icon="⚡")
                for _, row in overp.head(20).iterrows():
                    prm   = pd.to_numeric(row.get(prem_col, 0), errors='coerce') or 0.0
                    price = pd.to_numeric(row.get('price', 0),  errors='coerce') or 0.0
                    name  = row.get('name',''); code = row.get('code','')
                    st.markdown(f"""
<div class="t2-warn-card" style="border-color:rgba(255,215,0,0.28);background:rgba(255,215,0,0.025);
     border-left-color:#FFD700;box-shadow:0 0 14px rgba(255,215,0,0.06);">
  <div class="t2-warn-value" style="color:#FFD700">{prm:.1f}%</div>
  <div class="t2-warn-header" style="color:#E8C400">{name}  ({code})</div>
  <div class="t2-warn-meta">CB市價 {price:.1f} &nbsp;·&nbsp; 溢價率 {prm:.1f}% &nbsp;·&nbsp; 肉少湯喝</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="t2-warn-ok">✅ 目前無標的觸發「高溢價」警示。</div>',
                            unsafe_allow_html=True)

        with tab3_w13:
            illiq = scan[scan[vol_col] < 10].sort_values(vol_col)
            if not illiq.empty:
                st.toast(f"⚠️ 發現 {len(illiq)} 檔殭屍債 (日均量<10張)", icon="⚡")
                for _, row in illiq.head(20).iterrows():
                    vol   = pd.to_numeric(row.get(vol_col, 0), errors='coerce') or 0.0
                    price = pd.to_numeric(row.get('price', 0), errors='coerce') or 0.0
                    name  = row.get('name',''); code = row.get('code','')
                    st.markdown(f"""
<div class="t2-warn-card">
  <div class="t2-warn-value">{vol:.0f}張</div>
  <div class="t2-warn-header">{name}  ({code})</div>
  <div class="t2-warn-meta">CB市價 {price:.1f} &nbsp;·&nbsp; 日均量 {vol:.0f} 張 &nbsp;·&nbsp; 出場困難</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="t2-warn-ok">✅ 目前無標的觸發「流動性陷阱」警示。</div>',
                            unsafe_allow_html=True)
    else:
        st.toast(
            "⚠️ 掃描結果缺少風險分析欄位 (converted_ratio/conv_rate, premium, avg_volume)",
            icon="⚡"
        )


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2.4  ──  資金配置  **PRESERVED 100%**
# ══════════════════════════════════════════════════════════════════════════════
def render_2_4():
    st.markdown('<div class="t2-sec-title">💰 2.4 資金配置試算 — Position Sizing</div>',
                unsafe_allow_html=True)

    if 'scan_results' not in st.session_state or st.session_state['scan_results'].empty:
        st.caption("請先執行本頁上方的掃描以獲取買進建議。")
        return

    buy_recs = st.session_state['scan_results']
    n_tgts   = len(buy_recs)

    st.markdown(
        f'<div style="font-family:var(--f-mono);font-size:10px;color:#00FF7F;'
        f'letter-spacing:1.5px;margin-bottom:18px;text-transform:uppercase;">'
        f'✅ 已同步獵殺結果：{n_tgts} 檔可配置標的</div>',
        unsafe_allow_html=True
    )

    total_cap = st.number_input(
        "輸入您的總操作資金 (元)", min_value=100_000, value=2_000_000, step=100_000, key="t24_cap"
    )

    sort_col  = 'score' if 'score' in buy_recs.columns else 'price'
    top5      = buy_recs.sort_values(sort_col, ascending=False).head(5)
    kelly_pct = 20

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown(f"""
<div class="t2-kelly-box">
  <div class="t2-kelly-lbl">建議投資組合 (Top 5) — 每檔配置</div>
  <div class="t2-kelly-num">{kelly_pct}<span class="t2-kelly-pct">%</span></div>
  <div class="t2-kelly-sub">等權重分散 &nbsp;·&nbsp; 原版 20% / 檔模型</div>
</div>""", unsafe_allow_html=True)

        port_summary = (
            f"【資金配置建議】總資金 {total_cap:,} 元，"
            f"Top 5 標的各配置 20% = {int(total_cap * 0.20):,} 元/檔。"
            f"剩餘 {'0' if len(top5) >= 5 else str(100 - len(top5) * 20)}% 為現金保留。"
        )
        if 'port_streamed' not in st.session_state:
            st.write_stream(_stream_text(port_summary, speed=0.012))
            st.session_state['port_streamed'] = True
        else:
            st.caption(port_summary)

        port_lines = ""
        for _, row in top5.iterrows():
            cb_price  = pd.to_numeric(row.get('price', 0), errors='coerce') or 0.0
            name      = row.get('name','未知')
            code      = row.get('code','0000')
            if cb_price > 0:
                invest        = total_cap * 0.20
                market_val    = cb_price * 1000
                num_lots      = int(invest / market_val)
                port_lines += (
                    f'<div class="t2-port-row">'
                    f'<span class="nm">{name} ({code})</span>'
                    f'  ·  市價 <span>{cb_price:.1f}</span>'
                    f'  ·  建議 <span class="hl">{num_lots} 張</span>'
                    f'  ≈ {int(invest):,} 元'
                    f'</div>'
                )
        st.markdown(port_lines, unsafe_allow_html=True)

    with right_col:
        labels = [r.get('name','') for _, r in top5.iterrows()]
        alloc  = [kelly_pct] * len(top5)
        remain = 100 - sum(alloc)
        if remain > 0:
            labels.append('現金保留'); alloc.append(remain)

        fig = go.Figure(go.Pie(
            labels=labels, values=alloc, hole=0.52,
            marker=dict(
                colors=['#FF3131','#FFD700','#00F5FF','#00FF7F','#FF9A3C','#445566'],
                line=dict(color='rgba(0,0,0,0.4)', width=1)
            ),
            textfont=dict(color='#DDE', size=12, family='Rajdhani'),
        ))
        fig.update_layout(
            title=dict(text="建議資金配置",
                       font=dict(color='#FFD700', size=13, family='JetBrains Mono')),
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=360, margin=dict(t=44,b=0,l=0,r=0),
            legend=dict(font=dict(color='#B0C0D0', size=11, family='Rajdhani'))
        )
        st.markdown('<div class="t2-chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2.5  ──  戰略兵工廠 (Strategic Arsenal)  **NEW SECTION**
#  Surgical Transplant from tab5_wiki.py
# ══════════════════════════════════════════════════════════════════════════════
def render_2_5():
    """
    Section 2.5 — 戰略兵工廠 (Strategic Arsenal)
    3 Sub-Tools transplanted from tab5_wiki.py:
      - Tool A: Intel Hunter (情報獵殺)
      - Tool B: CBAS Calculator (試算儀)
      - Tool C: Strategy Calendar (行事曆)
    """
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:#FF9A3C;
            letter-spacing:2px;margin-bottom:18px;
            text-shadow:0 0 24px rgba(255,154,60,0.26);">
  🛠️ 戰略兵工廠 — STRATEGIC ARSENAL
</div>""", unsafe_allow_html=True)

    # Sub-Navigation using tabs
    tool_a, tool_b, tool_c = st.tabs([
        "🔍 Intel Hunter (情報)",
        "🧮 CBAS Calculator (試算)",
        "📅 Strategy Calendar (日曆)"
    ])

    with tool_a:
        _render_intel_hunter()

    with tool_b:
        _render_cbas_calculator()

    with tool_c:
        _render_strategy_calendar()


def _render_intel_hunter():
    """Tool A: Intel Hunter — Transplanted from tab5_wiki.py section 5.2"""
    st.markdown("""
<div class="t5-sec-head" style="--sa:#FF9A3C">
  <div class="t5-sec-num">A</div>
  <div>
    <div class="t5-sec-title" style="color:#FF9A3C;">情報獵殺 — Intel Analysis Engine</div>
    <div class="t5-sec-sub">Upload · Parse · Local Analysis · Gemini AI Deep Dive</div>
  </div>
</div>""", unsafe_allow_html=True)

    kb = _load_engines()[1]
    df = st.session_state.get('df', pd.DataFrame())

    intel_files = st.session_state.get('intel_files', [])
    if intel_files:
        for file in intel_files:
            st.markdown(f'<div class="codex-card gold"><div class="codex-card-title">📄 {file.name}</div><div class="codex-card-detail">情報檔案已上傳，展開查看分析結果</div></div>', unsafe_allow_html=True)
            with st.expander(f"🔍 展開分析報告: {file.name}", expanded=False):
                try:
                    from intelligence import IntelligenceEngine
                    intel = IntelligenceEngine()
                    result = intel.analyze_file(file, kb, df)
                    if "error" in result:
                        st.toast(f"❌ {result['error']}", icon="💀")
                    else:
                        st.markdown(f'<div class="t5-terminal">{result.get("local_analysis_md", "本地分析失敗。")}</div>', unsafe_allow_html=True)
                        st.divider()
                        api_key = st.session_state.get('api_key', '')
                        if api_key:
                            with st.spinner(f"執行 Gemini AI 深度分析: {file.name}…"):
                                try:
                                    import google.generativeai as genai
                                    genai.configure(api_key=api_key)
                                    report = intel.analyze_with_gemini(result["full_text"])
                                    st.markdown("### 💎 **Gemini AI 深度解析**")
                                    st.write_stream(stream_generator(report))
                                except Exception as e:
                                    st.toast(f"❌ Gemini 失敗: {e}", icon="💀")
                        else:
                            st.toast("ℹ️ 未輸入 Gemini API Key，跳過 AI 深度解析。", icon="📡")
                except ImportError:
                    st.toast(f"ℹ️ 📄 已上傳: {file.name}（情報引擎尚未掛載，請確認 intelligence.py）", icon="📡")
    else:
        st.markdown("""
<div style="text-align:center;padding:60px 30px;">
  <div style="font-size:48px;margin-bottom:16px;opacity:.3;">🕵️</div>
  <div style="font-family:var(--f-body);font-size:18px;color:rgba(255,255,255,.4);letter-spacing:2px;margin-bottom:8px;">NO INTEL FILES DETECTED</div>
  <div style="font-family:var(--f-mono);font-size:11px;color:rgba(160,176,208,.3);letter-spacing:2px;">請於左側上傳情報文件 (PDF/TXT) 以啟動分析引擎</div>
</div>""", unsafe_allow_html=True)


def _render_cbas_calculator():
    """Tool B: CBAS Calculator — Transplanted from tab5_wiki.py section 5.3"""
    st.markdown("""
<div class="t5-sec-head" style="--sa:#00FF7F">
  <div class="t5-sec-num">B</div>
  <div>
    <div class="t5-sec-title" style="color:#00FF7F;">CBAS 槓桿試算儀</div>
    <div class="t5-sec-sub">Convertible Bond Arbitrage Simulator · Leverage Engine</div>
  </div>
</div>""", unsafe_allow_html=True)

    col_in, col_space = st.columns([2, 1])
    with col_in:
        cb_price = st.number_input(
            "輸入 CB 市價 (元)", min_value=100.0, value=110.0, step=0.5, format="%.2f",
            key="cbas_price_arsenal"
        )

    premium_cost = cb_price - 100

    if premium_cost > 0:
        leverage = cb_price / premium_cost
        if leverage > 5:
            lev_cls = "green"
        elif leverage > 3:
            lev_cls = "gold"
        else:
            lev_cls = "red"

        prem_cls = "green" if premium_cost < 15 else ("gold" if premium_cost < 25 else "red")

        st.markdown(f"""
<div class="calc-screen">
  <div class="calc-lbl">Theoretical Premium (理論權利金)</div>
  <div class="calc-val {prem_cls}">{premium_cost:.2f}<span class="calc-unit">元</span></div>
  <div class="calc-divider"></div>
  <div class="calc-lbl">Leverage Ratio (槓桿倍數)</div>
  <div class="calc-val {lev_cls}">{leverage:.1f}<span class="calc-unit">×</span></div>
</div>""", unsafe_allow_html=True)

        st.markdown("")
        if leverage > 3:
            st.markdown(f"""
<div class="codex-card green">
  <div class="codex-card-title">🔥 高槓桿甜蜜點 — 適合以小博大</div>
  <div class="codex-card-key">CB 市價 {cb_price:.0f} 元 = 以 {premium_cost:.2f} 元「時間價值」控制 100 元股票轉換價值</div>
  <div class="codex-card-detail">若標的股票上漲 10%，CB 理論增值幅度約 {10 * leverage:.1f}%（{leverage:.2f} 倍槓桿效益）。風險有限，報酬可觀。</div>
</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div class="codex-card red">
  <div class="codex-card-title">⚠️ 肉少湯多 — 槓桿效益偏低</div>
  <div class="codex-card-key">槓桿 {leverage:.2f}× = 風險報酬比可能不佳</div>
  <div class="codex-card-detail">CB 溢價過高（{premium_cost:.2f} 元），槓桿效益有限。建議考慮直接買進 CB 現股或等待價格回落。</div>
</div>""", unsafe_allow_html=True)

        st.markdown("")
        st.markdown('<div style="font-family:var(--f-mono);font-size:9px;color:rgba(160,176,208,.25);letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Quick Reference: Leverage at Different CB Prices</div>', unsafe_allow_html=True)
        ref_cols = st.columns(5)
        for i, p in enumerate([103, 105, 110, 115, 120]):
            prem = p - 100
            lev = p / prem if prem > 0 else 0
            color = "#00FF7F" if lev > 5 else ("#FFD700" if lev > 3 else "#FF6B6B")
            ref_cols[i].markdown(f"""
<div style="text-align:center;padding:10px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.04);border-radius:8px;">
  <div style="font-family:var(--f-mono);font-size:9px;color:rgba(160,176,208,.35);letter-spacing:1px;">CB {p}元</div>
  <div style="font-family:var(--f-i);font-size:26px;font-weight:800;color:{color};line-height:1.2;">{lev:.1f}×</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div class="calc-screen">
  <div class="calc-lbl">CB 市價需高於 100 元</div>
  <div class="calc-val" style="color:rgba(160,176,208,.15);">—.—<span class="calc-unit">×</span></div>
</div>""", unsafe_allow_html=True)
        st.toast("ℹ️ CB 市價需高於 100 元才能計算 CBAS 權利金。市價 = 100 時無溢價可供槓桿操作。", icon="📡")


def _render_strategy_calendar():
    """Tool C: Strategy Calendar — Transplanted from tab5_wiki.py section 5.4"""
    st.markdown("""
<div class="t5-sec-head" style="--sa:#FFD700">
  <div class="t5-sec-num">C</div>
  <div>
    <div class="t5-sec-title" style="color:#FFD700;">戰略行事曆 — Time Arbitrage Calendar</div>
    <div class="t5-sec-sub">Upcoming Events · Countdown · Honeymoon / Put / Conversion Windows</div>
  </div>
</div>""", unsafe_allow_html=True)

    calendar = _load_calendar()
    df = st.session_state.get('df', pd.DataFrame())

    if df.empty:
        st.markdown("""
<div style="text-align:center;padding:60px 30px;">
  <div style="font-size:48px;margin-bottom:16px;opacity:.3;">📅</div>
  <div style="font-family:var(--f-body);font-size:18px;color:rgba(255,255,255,.4);letter-spacing:2px;margin-bottom:8px;">NO CB DATA LOADED</div>
  <div style="font-family:var(--f-mono);font-size:11px;color:rgba(160,176,208,.3);letter-spacing:2px;">請上傳 CB 清單以掃描時間套利事件</div>
</div>""", unsafe_allow_html=True)
        return

    days_ahead = st.slider("掃描未來天數", 7, 90, 30, key="cal_days_arsenal")
    today = datetime.now().date()
    future_date = today + timedelta(days=days_ahead)
    upcoming_events = []

    code_col = next((c for c in df.columns if 'code' in c.lower()), None)
    name_col = next((c for c in df.columns if 'name' in c.lower()), None)
    list_col = next((c for c in df.columns if 'list' in c.lower() or 'issue' in c.lower()), None)
    put_col  = next((c for c in df.columns if 'put' in c.lower() or '賣回' in c.lower()), None)

    if code_col and name_col:
        for _, row in df.iterrows():
            try:
                events = calendar.calculate_time_traps(
                    str(row.get(code_col, '')),
                    str(row.get(list_col, '')) if list_col else '',
                    str(row.get(put_col, ''))  if put_col  else ''
                )
                for ev in events:
                    ev_date = pd.to_datetime(ev['date']).date()
                    if today <= ev_date <= future_date:
                        upcoming_events.append({
                            "name":  row.get(name_col, ''),
                            "date":  ev_date,
                            "event": ev['event'],
                            "desc":  ev.get('desc', '')
                        })
            except Exception:
                pass

    if upcoming_events:
        upcoming_events.sort(key=lambda x: x['date'])

        st.markdown(f"""
<div style="display:flex;gap:16px;margin-bottom:20px;">
  <div style="flex:1;text-align:center;padding:18px;background:rgba(255,215,0,.03);border:1px solid rgba(255,215,0,.1);border-radius:12px;">
    <div style="font-family:var(--f-o);font-size:42px;font-weight:900;color:#FFD700;line-height:1;">{len(upcoming_events)}</div>
    <div style="font-family:var(--f-mono);font-size:9px;color:rgba(255,215,0,.4);letter-spacing:2px;margin-top:6px;">UPCOMING EVENTS</div>
  </div>
  <div style="flex:1;text-align:center;padding:18px;background:rgba(0,245,255,.02);border:1px solid rgba(0,245,255,.08);border-radius:12px;">
    <div style="font-family:var(--f-o);font-size:42px;font-weight:900;color:#00F5FF;line-height:1;">{days_ahead}</div>
    <div style="font-family:var(--f-mono);font-size:9px;color:rgba(0,245,255,.35);letter-spacing:2px;margin-top:6px;">DAY SCAN WINDOW</div>
  </div>
</div>""", unsafe_allow_html=True)

        for ev in upcoming_events:
            days_left = (ev['date'] - today).days
            if days_left <= 7:
                day_color = "#FF3131"
            elif days_left <= 14:
                day_color = "#FFD700"
            else:
                day_color = "#00F5FF"

            desc_html = f'<div class="event-desc">{ev["desc"]}</div>' if ev.get("desc") else ""
            st.markdown(f"""
<div class="event-card">
  <div style="min-width:100px;text-align:center;">
    <div class="event-day" style="color:{day_color};text-shadow:0 0 20px {day_color}40;">{days_left}</div>
    <div class="event-day-unit">days left</div>
  </div>
  <div class="event-body">
    <div class="event-name">{ev['name']}</div>
    <div class="event-type">{ev['event']}</div>
    <div class="event-date">{ev['date'].strftime('%Y-%m-%d')}</div>
    {desc_html}
  </div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div style="text-align:center;padding:50px 30px;">
  <div style="font-size:40px;margin-bottom:16px;opacity:.2;">✅</div>
  <div style="font-family:var(--f-body);font-size:16px;color:rgba(255,255,255,.35);letter-spacing:2px;">未來 {days_ahead} 天內無觸發任何時間套利事件</div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FIRE CONTROL DECK CONFIG (Updated with 2.0 + 2.5)
# ══════════════════════════════════════════════════════════════════════════════
FIRE_BTNS = [
    ("2.0", "🎬", "籌碼序幕",  "CHIPS PROLOGUE", "#9370DB", "147,112,219"),
    ("2.1", "📡", "自動獵殺",  "AUTO SCAN",      "#00F5FF", "0,245,255"),
    ("2.2", "📈", "核心檢核",  "SNIPER SCOPE",   "#00FF7F", "0,255,127"),
    ("2.3", "⚠️", "風險雷達",  "RISK RADAR",     "#FF3131", "255,49,49"),
    ("2.4", "💰", "資金配置",  "PORTFOLIO",      "#FFD700", "255,215,0"),
    ("2.5", "🛠️", "戰略兵工廠", "ARSENAL",        "#FF9A3C", "255,154,60"),
]


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY  ──  ★ @st.fragment 已補回（對齊原版）
# ══════════════════════════════════════════════════════════════════════════════
@st.fragment
def render():
    """Tab 2 — 獵殺雷達 + 戰略兵工廠  Director's Cut V300 + Arsenal Transplant + Chips Prologue"""
    _inject_css()

    if not st.session_state.get('tab2_guided', False):
        _show_tactical_guide()
        return

    df = st.session_state.get('df', pd.DataFrame())

    if 't2_active' not in st.session_state:
        st.session_state.t2_active = "2.0"  # Default to new Section 2.0
    active = st.session_state.t2_active

    # ── SYSTEM BAR ────────────────────────────────────────────────
    st.markdown(f"""
<div style="display:flex;align-items:baseline;justify-content:space-between;
            padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.052);
            margin-bottom:18px;">
  <div>
    <span style="font-family:'Bebas Neue',sans-serif;font-size:26px;
                 color:#00F5FF;letter-spacing:3px;
                 text-shadow:0 0 22px rgba(0,245,255,0.32);">
      🎯 獵殺雷達 + 兵工廠
    </span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:9px;
                 color:rgba(0,245,255,0.26);letter-spacing:3px;
                 border:1px solid rgba(0,245,255,0.10);border-radius:20px;
                 padding:3px 13px;margin-left:14px;background:rgba(0,245,255,0.022);">
      KILL RADAR V300 + ARSENAL + PROLOGUE
    </span>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
              color:rgba(200,215,230,0.20);letter-spacing:2px;text-align:right;line-height:1.7;">
    {datetime.now().strftime('%H:%M:%S')}<br>{datetime.now().strftime('%Y · %m · %d')}
  </div>
</div>""", unsafe_allow_html=True)

    # ── FIRE CONTROL DECK (6 buttons) ─────────────────────────────────────────
    st.markdown(
        '<div style="background:linear-gradient(165deg,#07080f,#0b0c16);'
        'border:1px solid rgba(255,255,255,0.055);border-radius:18px;'
        'padding:16px 14px 13px;margin-bottom:16px;">'
        '<div style="font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:4px;'
        'color:rgba(0,245,255,0.18);text-transform:uppercase;margin-bottom:12px;padding-left:2px;">'
        '⬡ fire control deck — select module (6 stations)</div>',
        unsafe_allow_html=True
    )

    fire_cols = st.columns(6)
    for col, (code, icon, label_zh, label_en, accent, rgb) in zip(fire_cols, FIRE_BTNS):
        is_a  = (active == code)
        brd   = f"2px solid {accent}" if is_a else "1px solid #1b2030"
        bg_c  = f"rgba({rgb},0.08)"   if is_a else "#090c14"
        lbl_c = accent                 if is_a else "#AABB"
        glow  = f"0 0 20px rgba({rgb},0.14), 0 8px 26px rgba(0,0,0,0.4)" if is_a else "none"
        with col:
            st.markdown(
                f'<div style="height:108px;background:{bg_c};border:{brd};border-radius:16px;'
                f'display:flex;flex-direction:column;align-items:center;justify-content:center;'
                f'gap:6px;box-shadow:{glow};margin-bottom:-56px;pointer-events:none;'
                f'position:relative;z-index:0;">'
                f'<div style="font-size:28px">{icon}</div>'
                f'<div style="font-family:Rajdhani,sans-serif;font-size:14px;font-weight:700;color:{lbl_c}">{label_zh}</div>'
                f'<div style="font-family:JetBrains Mono,monospace;font-size:7px;color:#223;letter-spacing:2px">{label_en}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            if st.button(f"{icon} {label_zh}", key=f"fire_{code}", use_container_width=True):
                st.session_state.t2_active = code
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── CONTENT FRAME ─────────────────────────────────────────────
    st.markdown('<div class="t2-content">', unsafe_allow_html=True)

    try:
        if active == "2.0":
            render_2_0(df)
        elif active == "2.1":
            render_2_1(df)
        elif active == "2.2":
            render_2_2()
        elif active == "2.3":
            render_2_3()
        elif active == "2.4":
            render_2_4()
        elif active == "2.5":
            render_2_5()
    except Exception as exc:
        import traceback
        st.error(f"❌ 子模組 {active} 渲染失敗: {exc}")
        with st.expander("🔍 Debug Trace"):
            st.code(traceback.format_exc())

    st.markdown(
        f'<div class="t2-foot">Titan Kill Radar + Arsenal V300 + Chips Prologue &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
