# ui_desktop/tab2_radar.py
# Titan SOP V300 — 獵殺雷達 (Kill Radar) + 戰略兵工廠 (Strategic Arsenal)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  "DIRECTOR'S CUT V300" + ARSENAL TRANSPLANT                      ║
# ║  SURGICAL CODE TRANSPLANT from tab5_wiki.py → Section 2.5        ║
# ║  ✅ Sections 2.1-2.4 PRESERVED 100% (NO CASTRATION)              ║
# ║  ✅ New Section 2.5: 戰略兵工廠 (Strategic Arsenal)               ║
# ║      → Tool A: Intel Hunter (情報獵殺)                            ║
# ║      → Tool B: CBAS Calculator (試算儀)                           ║
# ║      → Tool C: Strategy Calendar (行事曆)                         ║
# ╚═══════════════════════════════════════════════════════════════════╝

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
#  CSS  共用設計語言（與 tab1_macro V300 完全一致）
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
.t2-rule-card.pass { border-top:3px solid #00FF7F; }
.t2-rule-card.fail { border-top:3px solid #FF3131; }
.t2-rule-card.pass::after {
    content:'✓'; position:absolute; top:6px; right:10px;
    font-size:18px; color:rgba(0,255,127,.18); font-weight:900;
}
.t2-rule-card.fail::after {
    content:'✗'; position:absolute; top:6px; right:10px;
    font-size:18px; color:rgba(255,49,49,.18); font-weight:900;
}
.t2-rule-icon { font-size:28px; margin-bottom:8px; }
.t2-rule-title { font-family:var(--f-mono); font-size:9px; color:rgba(140,155,178,.5); text-transform:uppercase; letter-spacing:2px; margin-bottom:6px; }
.t2-rule-val { font-family:var(--f-display); font-size:24px; color:#FFF; }

/* ── KELLY ALLOCATION ──────────────────────────────────────────── */
.t2-kelly-box {
    background:rgba(255,255,255,.020); border:2px solid rgba(255,215,0,.25);
    border-radius:16px; padding:26px 20px 22px; text-align:center;
    position:relative; overflow:hidden;
}
.t2-kelly-box::before {
    content:''; position:absolute; top:0; right:0;
    width:160px; height:160px;
    background:radial-gradient(circle at top right,rgba(255,215,0,.06),transparent 70%);
}
.t2-kelly-lbl { font-family:var(--f-mono); font-size:9px; color:rgba(255,215,0,.4); letter-spacing:2px; text-transform:uppercase; margin-bottom:12px; }
.t2-kelly-num { font-family:var(--f-display); font-size:96px; color:#FFD700; line-height:.9; text-shadow:0 0 36px rgba(255,215,0,.22); }
.t2-kelly-pct { font-size:48px; opacity:.75; }
.t2-kelly-sub { font-family:var(--f-mono); font-size:11px; color:rgba(255,215,0,.3); margin-top:10px; letter-spacing:1.5px; }

/* ── PORTFOLIO ROWS ────────────────────────────────────────────── */
.t2-port-row {
    font-family:var(--f-body); font-size:14px; color:#D0DDE8;
    padding:10px 14px; background:rgba(255,255,255,.015);
    border:1px solid rgba(255,255,255,.04); border-radius:10px; margin-bottom:8px;
}
.t2-port-row .nm { color:#FFD700; font-weight:700; }
.t2-port-row .hl { color:#00F5FF; font-weight:700; }

/* ── CHART WRAP ────────────────────────────────────────────────── */
.t2-chart-wrap {
    background:rgba(255,255,255,.015); border:1px solid rgba(255,255,255,.04);
    border-radius:14px; padding:12px 8px; margin-top:12px;
}

/* ── CONTENT & FOOTER ──────────────────────────────────────────── */
.t2-content { padding:10px 0 20px; }
.t2-foot { font-family:var(--f-mono); font-size:9px; color:rgba(140,155,178,.2); letter-spacing:2px; text-align:center; margin-top:40px; padding-top:20px; border-top:1px solid rgba(255,255,255,.03); }

/* ══════════════════════════════════════════════════════════════ */
/* SECTION 2.5 ARSENAL STYLES (Transplanted from tab5_wiki.py)   */
/* ══════════════════════════════════════════════════════════════ */

/* ARSENAL HEADER */
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
#  2.1 — 自動獵殺 (AUTO SCAN)  **PRESERVED 100%**
# ══════════════════════════════════════════════════════════════════════════════
@st.fragment
def render_2_1(df):
    """
    Section 2.1 — 自動獵殺 (AUTO SCAN)
    CRITICAL: PRESERVED 100% - DO NOT MODIFY
    """
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:#00F5FF;
            letter-spacing:2px;margin-bottom:18px;
            text-shadow:0 0 24px rgba(0,245,255,0.26);">
  📡 自動獵殺 — AUTO SCAN
</div>""", unsafe_allow_html=True)

    if df.empty:
        st.warning("⚠️ 尚未上傳 CB 清單。請於左側匯入文件以啟動雷達掃描。")
        return

    strat, kb = _load_engines()

    # ── TOAST SCAN LAUNCH ──
    if 'scan_results' not in st.session_state or st.button("🚀 啟動全市場掃描", type="primary", use_container_width=True):
        with st.spinner("🔍 SCANNING .TW/.TWO MARKETS..."):
            time.sleep(0.8)
        try:
            scan_data, full_census = strat.scan_market()
            st.session_state['scan_results']      = scan_data
            st.session_state['full_census_data']  = full_census
            st.toast("✅ 掃描完成 — 6 大策略面板已就緒", icon="🎯")
        except Exception as e:
            st.toast(f"❌ 掃描失敗: {e}", icon="💀")
            st.error(f"市場普查失敗: {e}")
            return

    scan_res = st.session_state.get('scan_results')
    if not scan_res:
        return

    # ── STATUS HUD ──
    tw  = scan_res.get('tw_count',  0)
    two = scan_res.get('two_count', 0)
    tot = scan_res.get('total',     0)
    sop = scan_res.get('sop_count', 0)
    st.markdown('<div class="t2-hud-grid">', unsafe_allow_html=True)
    _HUD = [
        ("🎯 上市 (.TW)",   tw,  "#00F5FF", "0,245,255"),
        ("📡 上櫃 (.TWO)",  two, "#FFD700", "255,215,0"),
        ("📊 合計掃描",    tot, "#00FF7F", "0,255,127"),
        ("⭐ SOP 精選",    sop, "#FF9A3C", "255,154,60"),
    ]
    for lbl, val, c, rgb in _HUD:
        st.markdown(
            f'<div class="t2-hud-card" style="--hc:{c}">'
            f'<div class="t2-hud-lbl">{lbl}</div>'
            f'<div class="t2-hud-val">{val}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # ── STRATEGY PILL RAIL ──
    _STRATS = [
        ("census",      "📋 FULL CENSUS"),
        ("sop",         "⭐ SOP 精選"),
        ("honeymoon",   "🍯 蜜月期"),
        ("matured",     "🏔️ 滿年券"),
        ("put_shield",  "🛡️ 賣回保衛"),
        ("industry",    "🏭 產業風口"),
    ]
    act_strat = st.session_state.get('t2_active_strat', 'census')
    st.markdown('<div class="t2-pill-rail">', unsafe_allow_html=True)
    for code, label in _STRATS:
        cls = " active" if act_strat == code else ""
        st.markdown(f'<div class="t2-pill{cls}">{label}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    strat_cols = st.columns(len(_STRATS))
    for col, (code, _) in zip(strat_cols, _STRATS):
        if col.button(code, key=f"pill_{code}", use_container_width=True):
            st.session_state.t2_active_strat = code
            st.rerun()

    # ── DISPLAY LOGIC ──
    census_df = st.session_state.get('full_census_data', pd.DataFrame())

    if act_strat == 'census':
        st.markdown("### 📋 完整市場普查 (Full Census)")
        if not census_df.empty:
            st.dataframe(census_df, use_container_width=True, height=500)
        else:
            st.info("無普查數據。")

    elif act_strat == 'sop':
        sop_df = scan_res.get('sop_df')
        st.markdown("### ⭐ SOP 黃金標準精選")
        if sop_df is not None and not sop_df.empty:
            st.markdown(f"**命中數量**: {len(sop_df)}")
            st.dataframe(sop_df, use_container_width=True, height=500)
        else:
            st.info("無符合 SOP 條件的標的。")

    elif act_strat == 'honeymoon':
        hm_df = scan_res.get('honeymoon_df')
        st.markdown("### 🍯 新券蜜月策略 (Listing < 90d)")
        if hm_df is not None and not hm_df.empty:
            st.dataframe(hm_df, use_container_width=True, height=500)
        else:
            st.info("無蜜月期標的。")

    elif act_strat == 'matured':
        mt_df = scan_res.get('matured_df')
        st.markdown("### 🏔️ 滿年沈澱 (Listing > 365d)")
        if mt_df is not None and not mt_df.empty:
            st.dataframe(mt_df, use_container_width=True, height=500)
        else:
            st.info("無滿年券標的。")

    elif act_strat == 'put_shield':
        ps_df = scan_res.get('put_shield_df')
        st.markdown("### 🛡️ 賣回保衛戰 (Put Date < 60d)")
        if ps_df is not None and not ps_df.empty:
            st.dataframe(ps_df, use_container_width=True, height=500)
        else:
            st.info("無即將到期賣回標的。")

    elif act_strat == 'industry':
        ind = scan_res.get('industry_breakdown', {})
        st.markdown("### 🏭 產業族群分佈")
        if ind:
            for sector, stocks in sorted(ind.items()):
                with st.expander(f"**{sector}** ({len(stocks)} 檔)", expanded=False):
                    sect_df = census_df[census_df.get('code','').isin(stocks)] if not census_df.empty else pd.DataFrame()
                    if not sect_df.empty:
                        st.dataframe(sect_df, use_container_width=True)
                    else:
                        st.write(", ".join(sorted(stocks)))
        else:
            st.info("無產業分類資訊。")


# ══════════════════════════════════════════════════════════════════════════════
#  2.2 — 核心檢核 (SNIPER SCOPE)  **PRESERVED 100%**
# ══════════════════════════════════════════════════════════════════════════════
@st.fragment
def render_2_2():
    """
    Section 2.2 — 核心檢核 (SNIPER SCOPE)
    CRITICAL: PRESERVED 100% - DO NOT MODIFY
    """
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:#00FF7F;
            letter-spacing:2px;margin-bottom:18px;
            text-shadow:0 0 24px rgba(0,255,127,0.26);">
  📈 核心檢核 — SNIPER SCOPE
</div>""", unsafe_allow_html=True)

    strat, kb = _load_engines()

    cb_code = st.text_input("🔍 輸入 CB 代號 (e.g. 33531)", key="t2_cb_code").strip()
    if not cb_code:
        st.info("請輸入 CB 代號以啟動 K 線 + 四大天條檢核。")
        return

    with st.spinner(f"🎯 正在檢核 {cb_code}..."):
        try:
            # ── 1) 拉 K 線 ──
            stock_code = cb_code[:4] if cb_code.startswith('3') else cb_code
            tw_ticker  = f"{stock_code}.TW"
            two_ticker = f"{stock_code}.TWO"
            df_k = None
            for ticker in [tw_ticker, two_ticker]:
                try:
                    tmp = yf.download(ticker, period='1y', progress=False)
                    if not tmp.empty:
                        df_k = tmp
                        break
                except:
                    pass

            if df_k is None or df_k.empty:
                st.warning(f"⚠️ 無法取得 {cb_code} 的 K 線資料。")
                return

            # ── 2) 計算均線 ──
            df_k['87MA']  = df_k['Close'].rolling(87, min_periods=1).mean()
            df_k['284MA'] = df_k['Close'].rolling(284, min_periods=1).mean()

            # ── 3) Plotly 圖表 ──
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=df_k.index, open=df_k['Open'], high=df_k['High'],
                low=df_k['Low'], close=df_k['Close'], name='K線'
            ))
            fig.add_trace(go.Scatter(x=df_k.index, y=df_k['87MA'],  mode='lines', name='87MA',  line=dict(color='#FFD700', width=2)))
            fig.add_trace(go.Scatter(x=df_k.index, y=df_k['284MA'], mode='lines', name='284MA', line=dict(color='#00F5FF', width=2)))
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=450, margin=dict(l=0,r=0,t=30,b=0),
                xaxis_title='Date', yaxis_title='Price',
                legend=dict(font=dict(color='#B0C0D0', size=10))
            )
            st.plotly_chart(fig, use_container_width=True)

            # ── 4) 四大天條檢核卡 ──
            latest = df_k.iloc[-1]
            close  = latest['Close']
            ma87   = latest['87MA']
            ma284  = latest['284MA']

            # Fetch from KB
            try:
                sop_rules = kb.get_sop_rules()
                price_rule = sop_rules.get('entry_conditions',{}).get('price_ceiling',120)
            except:
                price_rule = 120

            # 4 checks
            price_pass = (close < price_rule)
            trend_pass = (ma87 > ma284)
            # Dummy converted ratio & score (replace with real logic if available)
            conv_ratio = 0  # placeholder
            conv_pass  = (conv_ratio < 30)
            score      = 85 if price_pass and trend_pass else 60
            score_pass = (score >= 70)

            st.markdown('<div class="t2-rule-grid">', unsafe_allow_html=True)
            _RULES = [
                ("💰 價格天條", f"{close:.1f}", price_pass, f"< {price_rule}"),
                ("📈 均線天條", "87>284" if trend_pass else "87<284", trend_pass, "多頭排列"),
                ("📊 轉換率",   f"{conv_ratio:.1f}%", conv_pass, "< 30%"),
                ("⭐ 綜合評分", f"{score}", score_pass, "≥ 70"),
            ]
            for icon_lbl, val_str, passed, criteria in _RULES:
                cls = "pass" if passed else "fail"
                st.markdown(
                    f'<div class="t2-rule-card {cls}">'
                    f'<div class="t2-rule-icon">{icon_lbl.split()[0]}</div>'
                    f'<div class="t2-rule-title">{icon_lbl.split(maxsplit=1)[1]}</div>'
                    f'<div class="t2-rule-val">{val_str}</div>'
                    f'<div style="font-family:var(--f-mono);font-size:9px;color:rgba(140,155,178,.3);margin-top:6px;">{criteria}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"檢核失敗: {e}")


# ══════════════════════════════════════════════════════════════════════════════
#  2.3 — 風險雷達 (RISK RADAR)  **PRESERVED 100%**
# ══════════════════════════════════════════════════════════════════════════════
@st.fragment
def render_2_3():
    """
    Section 2.3 — 風險雷達 (RISK RADAR)
    CRITICAL: PRESERVED 100% - DO NOT MODIFY
    """
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:#FF3131;
            letter-spacing:2px;margin-bottom:18px;
            text-shadow:0 0 24px rgba(255,49,49,0.26);">
  ⚠️ 風險雷達 — RISK RADAR
</div>""", unsafe_allow_html=True)

    census_df = st.session_state.get('full_census_data', pd.DataFrame())
    if census_df.empty:
        st.info("無市場普查資料。請先執行 2.1 自動獵殺。")
        return

    # ── Detect columns ──
    conv_col = None
    for c in ['converted_ratio','conv_rate']:
        if c in census_df.columns:
            conv_col = c
            break
    prem_col = next((c for c in census_df.columns if 'premium' in c.lower()), None)
    vol_col  = next((c for c in census_df.columns if 'avg_volume' in c.lower() or 'volume' in c.lower()), None)

    warnings = []

    # ── 1) Converted Ratio > 50% (反轉邏輯) ──
    if conv_col:
        tmp = census_df.copy()
        tmp[conv_col] = pd.to_numeric(tmp[conv_col], errors='coerce')
        raw_high = tmp[tmp[conv_col] > 50]
        if not raw_high.empty:
            # 反轉
            for _, row in raw_high.iterrows():
                raw_val = row[conv_col]
                flipped = 100 - raw_val
                if flipped < 30:
                    w_code = row.get('code','N/A')
                    w_name = row.get('name','')
                    warnings.append(('red', w_code, w_name, f'已轉換率 {raw_val:.1f}% (反轉 {flipped:.1f}%) — 籌碼過度鬆動'))

    # ── 2) Premium > 20% ──
    if prem_col:
        tmp = census_df.copy()
        tmp[prem_col] = pd.to_numeric(tmp[prem_col], errors='coerce')
        high_prem = tmp[tmp[prem_col] > 20]
        for _, row in high_prem.iterrows():
            prem = row[prem_col]
            w_code = row.get('code','N/A')
            w_name = row.get('name','')
            warnings.append(('gold', w_code, w_name, f'溢價率 {prem:.1f}% — 進場成本過高'))

    # ── 3) Avg Volume < 1000 ──
    if vol_col:
        tmp = census_df.copy()
        tmp[vol_col] = pd.to_numeric(tmp[vol_col], errors='coerce')
        low_vol = tmp[tmp[vol_col] < 1000]
        for _, row in low_vol.iterrows():
            vol = row[vol_col]
            w_code = row.get('code','N/A')
            w_name = row.get('name','')
            warnings.append(('', w_code, w_name, f'日均量 {vol:.0f} 張 — 流動性不足'))

    # ── Display ──
    if warnings:
        st.markdown(f"### ⚠️ 檢測到 {len(warnings)} 個風險警示")
        for cls, code, name, msg in warnings:
            st.markdown(f'<div class="codex-card {cls}"><div class="codex-card-title">{code} {name}</div><div class="codex-card-detail">{msg}</div></div>', unsafe_allow_html=True)
    else:
        st.success("✅ 未檢測到重大風險訊號。")


# ══════════════════════════════════════════════════════════════════════════════
#  2.4 — 資金配置 (PORTFOLIO)  **PRESERVED 100%**
# ══════════════════════════════════════════════════════════════════════════════
@st.fragment
def render_2_4():
    """
    Section 2.4 — 資金配置 (PORTFOLIO)
    CRITICAL: PRESERVED 100% - DO NOT MODIFY
    """
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:#FFD700;
            letter-spacing:2px;margin-bottom:18px;
            text-shadow:0 0 24px rgba(255,215,0,0.26);">
  💰 資金配置 — PORTFOLIO ALLOCATION
</div>""", unsafe_allow_html=True)

    scan_res = st.session_state.get('scan_results')
    if not scan_res:
        st.info("請先執行 2.1 自動獵殺。")
        return

    sop_df = scan_res.get('sop_df')
    if sop_df is None or sop_df.empty:
        st.warning("⚠️ 無 SOP 精選標的，無法配置。")
        return

    top5 = sop_df.head(5)
    if len(top5) == 0:
        st.warning("SOP 精選為空，無法配置。")
        return

    # Kelly = 20% per stock (等權重)
    kelly_pct = 20
    total_cap = st.number_input("💵 總資金 (元)", value=1000000, step=100000, key="t2_port_cap")

    left_col, right_col = st.columns([1.2, 1])

    with left_col:
        # ── 96px Kelly Number
        st.markdown(f"""
<div class="t2-kelly-box">
  <div class="t2-kelly-lbl">建議投資組合 (Top 5) — 每檔配置</div>
  <div class="t2-kelly-num">{kelly_pct}<span class="t2-kelly-pct">%</span></div>
  <div class="t2-kelly-sub">等權重分散 &nbsp;·&nbsp; 原版 20% / 檔模型</div>
</div>""", unsafe_allow_html=True)

        # [UPGRADE #3] Typewriter for portfolio summary
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

        # ── Portfolio lines（原版邏輯：每檔 20%，CB 一張面額10萬）
        port_lines = ""
        for _, row in top5.iterrows():
            cb_price  = pd.to_numeric(row.get('price', 0), errors='coerce') or 0.0
            name      = row.get('name','未知')
            code      = row.get('code','0000')
            if cb_price > 0:
                invest        = total_cap * 0.20
                market_val    = cb_price * 1000        # 原版：一張 = price * 1000
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
        # ── Plotly Pie（暗色主題）
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
#  2.5 — 戰略兵工廠 (STRATEGIC ARSENAL) **NEW SECTION**
#  Surgical Transplant from tab5_wiki.py sections 5.2, 5.3, 5.4
# ══════════════════════════════════════════════════════════════════════════════
@st.fragment
def render_2_5():
    """
    Section 2.5 — 戰略兵工廠 (Strategic Arsenal)
    Transplanted from tab5_wiki.py:
      - Tool A: Intel Hunter (情報獵殺) from 5.2
      - Tool B: CBAS Calculator (試算儀) from 5.3
      - Tool C: Strategy Calendar (行事曆) from 5.4
    """
    st.markdown("""
<div style="font-family:'Bebas Neue',sans-serif;font-size:28px;color:#FF9A3C;
            letter-spacing:2px;margin-bottom:18px;
            text-shadow:0 0 24px rgba(255,154,60,0.26);">
  🛠️ 戰略兵工廠 — STRATEGIC ARSENAL
</div>""", unsafe_allow_html=True)

    # Sub-navigation using st.tabs
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
                                    # Valkyrie Typewriter for AI report
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

    # Wide input area
    col_in, col_space = st.columns([2, 1])
    with col_in:
        cb_price = st.number_input(
            "輸入 CB 市價 (元)", min_value=100.0, value=110.0, step=0.5, format="%.2f",
            key="cbas_price_arsenal"
        )

    premium_cost = cb_price - 100

    if premium_cost > 0:
        leverage = cb_price / premium_cost
        # Determine color
        if leverage > 5:
            lev_cls = "green"
        elif leverage > 3:
            lev_cls = "gold"
        else:
            lev_cls = "red"

        prem_cls = "green" if premium_cost < 15 else ("gold" if premium_cost < 25 else "red")

        # MASSIVE CALC SCREEN (80px)
        st.markdown(f"""
<div class="calc-screen">
  <div class="calc-lbl">Theoretical Premium (理論權利金)</div>
  <div class="calc-val {prem_cls}">{premium_cost:.2f}<span class="calc-unit">元</span></div>
  <div class="calc-divider"></div>
  <div class="calc-lbl">Leverage Ratio (槓桿倍數)</div>
  <div class="calc-val {lev_cls}">{leverage:.1f}<span class="calc-unit">×</span></div>
</div>""", unsafe_allow_html=True)

        # Interpretation
        st.markdown("")  # spacer
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

        # Quick reference strip
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

    # Column detection (PRESERVED)
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

        # Summary counter
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

        # Episode Cards
        for ev in upcoming_events:
            days_left = (ev['date'] - today).days
            # Color code by urgency
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
#  FIRE CONTROL DECK CONFIG (Updated with 2.5)
# ══════════════════════════════════════════════════════════════════════════════
FIRE_BTNS = [
    ("2.1", "📡", "自動獵殺",  "AUTO SCAN",    "#00F5FF", "0,245,255"),
    ("2.2", "📈", "核心檢核",  "SNIPER SCOPE", "#00FF7F", "0,255,127"),
    ("2.3", "⚠️", "風險雷達",  "RISK RADAR",   "#FF3131", "255,49,49"),
    ("2.4", "💰", "資金配置",  "PORTFOLIO",    "#FFD700", "255,215,0"),
    ("2.5", "🛠️", "戰略兵工廠", "ARSENAL",      "#FF9A3C", "255,154,60"),
]


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY  ──  ★ @st.fragment 已補回（對齊原版）
#  [UPGRADE #1] Tactical Guide Dialog on first visit
# ══════════════════════════════════════════════════════════════════════════════
@st.fragment
def render():
    """Tab 2 — 獵殺雷達 + 戰略兵工廠  Director's Cut V300 + Arsenal"""
    _inject_css()

    # [UPGRADE #1] Onboarding dialog — show once per session
    if not st.session_state.get('tab2_guided', False):
        _show_tactical_guide()
        return  # dialog blocks rendering; will rerun after close

    df = st.session_state.get('df', pd.DataFrame())

    if 't2_active' not in st.session_state:
        st.session_state.t2_active = "2.1"
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
      KILL RADAR V300 + ARSENAL
    </span>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
              color:rgba(200,215,230,0.20);letter-spacing:2px;text-align:right;line-height:1.7;">
    {datetime.now().strftime('%H:%M:%S')}<br>{datetime.now().strftime('%Y · %m · %d')}
  </div>
</div>""", unsafe_allow_html=True)

    # ── FIRE CONTROL DECK (Now with 5 buttons) ─────────────────────────────────────────
    st.markdown(
        '<div style="background:linear-gradient(165deg,#07080f,#0b0c16);'
        'border:1px solid rgba(255,255,255,0.055);border-radius:18px;'
        'padding:16px 14px 13px;margin-bottom:16px;">'
        '<div style="font-family:JetBrains Mono,monospace;font-size:8px;letter-spacing:4px;'
        'color:rgba(0,245,255,0.18);text-transform:uppercase;margin-bottom:12px;padding-left:2px;">'
        '⬡ fire control deck — select module (5 stations)</div>',
        unsafe_allow_html=True
    )

    fire_cols = st.columns(5)
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
        if active == "2.1":
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
        f'<div class="t2-foot">Titan Kill Radar + Arsenal V300 &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )
    st.markdown('</div>', unsafe_allow_html=True)
