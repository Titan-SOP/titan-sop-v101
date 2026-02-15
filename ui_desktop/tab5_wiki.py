# ui_desktop/tab5_wiki.py — DIRECTOR'S CUT
# Titan SOP V300 — Tab 5: 戰略知識法典 (Strategic Knowledge Codex)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  🎬 DIRECTOR'S CUT FEATURES:                                      ║
# ║  [DC1] 🔰 Tactical Guide Modal (Onboarding)                      ║
# ║  [DC2] 🍞 Toast Notifications (No More Green Boxes)              ║
# ║  [DC3] ⌨️ Valkyrie AI Typewriter (Streaming Text)                ║
# ║  [DC4] 🎬 Cinematic Visuals (Hero Billboard + Glassmorphism)     ║
# ║  ALL original logic preserved 100% verbatim                      ║
# ╚═══════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

from knowledge_base import TitanKnowledgeBase
from execution import CalendarAgent


# ── [DC3] VALKYRIE AI TYPEWRITER ──────────────────────────────────
def _stream_text(text, speed=0.02):
    """Character-by-character text streaming for cinematic effect"""
    for char in text:
        yield char
        time.sleep(speed)


# ── Cached Resources (PRESERVED) ──────────────────────────────────
@st.cache_resource
def _load_kb():
    return TitanKnowledgeBase()

@st.cache_resource
def _load_calendar():
    return CalendarAgent()


# ═══════════════════════════════════════════════════════════════
# [DC4] DIRECTOR'S CUT MASTER CSS
# ═══════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@300;400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
/* ═══════════════════════════════════════════════════════ */
/* TITAN OS MASTER CSS — DIRECTOR'S CUT */
/* ═══════════════════════════════════════════════════════ */
:root {
  --c-gold: #FFD700;
  --c-cyan: #00F5FF;
  --c-red: #FF3131;
  --c-green: #00FF7F;
  --bg-card: #0D1117;
  --f-d: 'Bebas Neue', sans-serif;
  --f-b: 'Rajdhani', sans-serif;
  --f-m: 'JetBrains Mono', monospace;
  --f-i: 'Inter', sans-serif;
  --f-o: 'Orbitron', sans-serif;
}

/* 1. HERO BILLBOARD (CINEMATIC) */
.hero-container {
  padding: 48px 40px 36px;
  background: linear-gradient(180deg, rgba(10,10,10,0) 0%, rgba(0,0,0,0.9) 100%);
  border-bottom: 1px solid rgba(255,215,0,0.2);
  text-align: center;
  margin-bottom: 28px;
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

/* T5-specific hero styling */
.t5-hero {
  padding: 48px 40px 36px;
  background: linear-gradient(180deg, rgba(8,8,16,0) 0%, rgba(4,4,12,.7) 50%, rgba(0,0,0,.9) 100%);
  border-bottom: 1px solid rgba(0,245,255,.08);
  text-align: center;
  margin-bottom: 28px;
}
.t5-hero-sur {
  font-family: var(--f-o);
  font-size: 10px;
  color: rgba(255,49,49,.45);
  letter-spacing: 10px;
  text-transform: uppercase;
  margin-bottom: 12px;
}
.t5-hero-title {
  font-family: var(--f-i);
  font-size: 84px;
  font-weight: 900;
  letter-spacing: -3px;
  line-height: 1;
  color: #FFF;
  text-shadow: 0 0 40px rgba(255,255,255,.06);
}
.t5-hero-sub {
  font-family: var(--f-m);
  font-size: 10px;
  color: rgba(160,176,208,.3);
  letter-spacing: 4px;
  text-transform: uppercase;
  margin-top: 10px;
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

/* T5-specific poster styling */
.t5-poster {
  flex: 1;
  min-width: 110px;
  min-height: 130px;
  background: rgba(255,255,255,.015);
  border: 1px solid rgba(255,255,255,.05);
  border-radius: 14px;
  padding: 16px 10px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  transition: all .2s ease;
}
.t5-poster.active {
  border-color: var(--c-cyan);
  background: rgba(0,245,255,.04);
  box-shadow: 0 0 30px rgba(0,245,255,.08);
}
.t5-poster:hover {
  border-color: var(--c-gold);
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.t5-poster-icon {
  font-size: 28px;
  margin-bottom: 6px;
}
.t5-poster-title {
  font-family: var(--f-d);
  font-size: 14px;
  color: #FFF;
  letter-spacing: 1.5px;
}
.t5-poster-sub {
  font-family: var(--f-m);
  font-size: 7px;
  color: rgba(140,155,178,.4);
  letter-spacing: 1.5px;
  text-transform: uppercase;
  margin-top: 3px;
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

/* SECTION HEADER */
.t5-sec-head {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(255,255,255,.052);
  margin-bottom: 20px;
}
.t5-sec-num {
  font-family: var(--f-d);
  font-size: 56px;
  color: rgba(0,245,255,.06);
  letter-spacing: 2px;
  line-height: 1;
}
.t5-sec-title {
  font-family: var(--f-d);
  font-size: 22px;
  color: var(--sa, #00F5FF);
  letter-spacing: 2px;
}
.t5-sec-sub {
  font-family: var(--f-m);
  font-size: 9px;
  color: rgba(0,245,255,.28);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-top: 2px;
}

/* CLASSIFIED FILE CARDS (GLASSMORPHISM) */
.codex-card {
  background: rgba(255,255,255,.025);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(80,90,110,.25);
  border-left: 4px solid #00F5FF;
  padding: 22px 24px 18px;
  margin-bottom: 14px;
  border-radius: 0 10px 10px 0;
  position: relative;
  overflow: hidden;
}
.codex-card::before {
  content: 'CLASSIFIED';
  position: absolute;
  top: 8px;
  right: 12px;
  font-family: var(--f-o);
  font-size: 7px;
  color: rgba(255,49,49,.18);
  letter-spacing: 4px;
}
.codex-card.gold {
  border-left-color: #FFD700;
}
.codex-card.gold::before {
  content: 'PRIORITY';
}
.codex-card.red {
  border-left-color: #FF3131;
}
.codex-card.red::before {
  content: 'CRITICAL';
}
.codex-card.green {
  border-left-color: #00FF7F;
}
.codex-card.green::before {
  content: 'ACTIVE';
}
.codex-card.purple {
  border-left-color: #B77DFF;
}
.codex-card.purple::before {
  content: 'TACTICAL';
}
.codex-card-title {
  font-family: var(--f-b);
  font-size: 18px;
  font-weight: 700;
  color: #FFF;
  letter-spacing: 1px;
  margin-bottom: 6px;
}
.codex-card-key {
  font-family: var(--f-i);
  font-size: 15px;
  font-weight: 600;
  color: rgba(0,245,255,.85);
  line-height: 1.6;
  margin-bottom: 8px;
}
.codex-card-detail {
  font-family: var(--f-m);
  font-size: 11px;
  color: rgba(160,176,208,.5);
  line-height: 1.7;
}

/* MINDSET CARD */
.mindset-card {
  background: rgba(255,255,255,.02);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,.05);
  border-radius: 12px;
  padding: 18px 20px;
  margin-bottom: 10px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
}
.mindset-num {
  font-family: var(--f-i);
  font-size: 36px;
  font-weight: 900;
  color: rgba(255,215,0,.15);
  min-width: 48px;
  line-height: 1;
}
.mindset-title {
  font-family: var(--f-b);
  font-size: 15px;
  font-weight: 700;
  color: #FFF;
  margin-bottom: 3px;
}
.mindset-desc {
  font-family: var(--f-m);
  font-size: 11px;
  color: rgba(160,176,208,.45);
  line-height: 1.6;
}

/* CALC SCREEN (MASSIVE DISPLAY) */
.calc-screen {
  background: #000;
  border: 2px solid rgba(80,90,110,.35);
  border-radius: 14px;
  padding: 32px 28px;
  text-align: center;
  margin-top: 16px;
  position: relative;
  overflow: hidden;
}
.calc-screen::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0,245,255,.2), transparent);
}
.calc-screen::after {
  content: 'CBAS LEVERAGE ENGINE';
  position: absolute;
  top: 10px;
  left: 16px;
  font-family: var(--f-o);
  font-size: 7px;
  color: rgba(0,245,255,.15);
  letter-spacing: 4px;
}
.calc-val {
  font-size: 84px;
  font-weight: 900;
  font-family: var(--f-o);
  line-height: 1;
  letter-spacing: -2px;
}
.calc-val.green {
  color: #00FF7F;
  text-shadow: 0 0 30px rgba(0,255,127,.35);
}
.calc-val.gold {
  color: #FFD700;
  text-shadow: 0 0 30px rgba(255,215,0,.35);
}
.calc-val.red {
  color: #FF6B6B;
  text-shadow: 0 0 30px rgba(255,107,107,.35);
}
.calc-lbl {
  font-family: var(--f-m);
  font-size: 11px;
  color: rgba(160,176,208,.4);
  text-transform: uppercase;
  letter-spacing: 3px;
  margin-top: 8px;
}
.calc-unit {
  font-family: var(--f-m);
  font-size: 14px;
  color: rgba(255,255,255,.25);
  margin-left: 4px;
}
.calc-divider {
  width: 60%;
  height: 1px;
  background: rgba(255,255,255,.05);
  margin: 20px auto;
}

/* EVENT EPISODE CARDS */
.event-card {
  background: rgba(255,255,255,.02);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,.06);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 20px;
}
.event-day {
  font-size: 60px;
  font-weight: 900;
  font-family: var(--f-o);
  color: #FFD700;
  text-shadow: 0 0 20px rgba(255,215,0,.2);
  line-height: 1;
  min-width: 100px;
  text-align: center;
}
.event-day-unit {
  font-family: var(--f-m);
  font-size: 9px;
  color: rgba(255,215,0,.4);
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-top: 4px;
  text-align: center;
}
.event-body {
  flex: 1;
}
.event-name {
  font-family: var(--f-b);
  font-size: 17px;
  font-weight: 700;
  color: #FFF;
  letter-spacing: 1px;
}
.event-type {
  font-family: var(--f-m);
  font-size: 11px;
  color: rgba(0,245,255,.6);
  letter-spacing: 1px;
  margin-top: 3px;
}
.event-date {
  font-family: var(--f-m);
  font-size: 10px;
  color: rgba(160,176,208,.35);
  margin-top: 2px;
}
.event-desc {
  font-family: var(--f-m);
  font-size: 10px;
  color: rgba(160,176,208,.3);
  margin-top: 5px;
  line-height: 1.5;
}

/* SECTOR TABLE */
.sector-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 16px;
  background: rgba(255,255,255,.015);
  border: 1px solid rgba(255,255,255,.04);
  border-radius: 8px;
  margin-bottom: 6px;
}
.sector-name {
  font-family: var(--f-b);
  font-size: 14px;
  font-weight: 700;
  color: rgba(0,245,255,.7);
  min-width: 120px;
}
.sector-stocks {
  font-family: var(--f-m);
  font-size: 11px;
  color: rgba(160,176,208,.5);
  line-height: 1.5;
}

/* TERMINAL BOX (GLASSMORPHISM) */
.t5-terminal {
  background: rgba(13, 17, 23, 0.6);
  backdrop-filter: blur(10px);
  border: 1px solid #30363d;
  border-left: 4px solid #00F5FF;
  border-radius: 0 10px 10px 0;
  padding: 22px 24px;
  font-family: var(--f-m);
  color: #c9d1d9;
  font-size: 12px;
  line-height: 1.7;
  margin: 12px 0;
}
.t5-terminal::before {
  content: '> INTEL TERMINAL';
  display: block;
  font-size: 9px;
  letter-spacing: 3px;
  color: rgba(0,245,255,.25);
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(0,245,255,.06);
}

/* FOOTER */
.t5-foot {
  font-family: var(--f-m);
  font-size: 9px;
  color: rgba(70,90,110,.25);
  letter-spacing: 2px;
  text-align: right;
  margin-top: 28px;
  text-transform: uppercase;
}
</style>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# [DC1] TACTICAL GUIDE MODAL
# ═══════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導 / Tactical Guide")
def show_tactical_guide():
    st.markdown("""
    ### 戰略知識法典操作指南
    
    **核心功能 / Core Functions:**
    
    • **📖 戰略法典 (5.1)** — SOP標準作業程序：四大時間套利、進出場紀律、產業族群、特殊心法、OTC均線  
    • **🧠 情報獵殺 (5.2)** — 上傳PDF/TXT情報文件，本地解析 + Gemini AI深度分析，快速掌握關鍵訊息  
    • **⚡ CBAS試算 (5.3)** — CB套利槓桿試算儀，輸入CB市價即時計算理論權利金與槓桿倍數  
    
    **操作流程 / Workflow:**
    1. 在 5.1 查閱SOP戰略法典，建立交易紀律
    2. 在 5.2 上傳情報文件進行AI分析
    3. 在 5.3 試算CB槓桿效益評估進場價值
    4. 在 5.4 追蹤時間套利事件行事曆
    
    ---
    *此系統整合知識管理、情報分析、計算工具、日曆追蹤，是戰略決策的知識中樞。*
    """)
    
    if st.button("✅ Roger that (收到)", type="primary", use_container_width=True):
        st.session_state.t5_guide_shown = True
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# HERO BILLBOARD
# ═══════════════════════════════════════════════════════════════
def _render_hero():
    st.markdown("""
<div class="t5-hero">
  <div class="t5-hero-sur">🔒 classified · restricted access</div>
  <div class="t5-hero-title">STRATEGIC CODEX</div>
  <div class="t5-hero-sub">Standard Operating Procedures · Arbitrage Intelligence · CBAS Engine</div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# POSTER RAIL NAVIGATION
# ═══════════════════════════════════════════════════════════════
def _render_nav():
    if 't5_active' not in st.session_state:
        st.session_state.t5_active = "5.1"
    cards = [
        ("5.1", "📖", "戰略法典", "SOP Rules"),
        ("5.2", "🧠", "情報獵殺", "Intel Analysis"),
        ("5.3", "⚡", "CBAS試算", "Leverage Calc"),
        ("5.4", "📅", "戰略日曆", "Calendar"),
    ]
    cols = st.columns(4)
    for i, (sid, icon, title, sub) in enumerate(cards):
        with cols[i]:
            ac = "active" if st.session_state.t5_active == sid else ""
            st.markdown(f"""
<div class="t5-poster {ac}">
  <div class="t5-poster-icon">{icon}</div>
  <div class="t5-poster-title">{sid} {title}</div>
  <div class="t5-poster-sub">{sub}</div>
</div>""", unsafe_allow_html=True)
            if st.button(f"Open {sid}", key=f"t5nav_{sid}", use_container_width=True):
                st.session_state.t5_active = sid
                st.rerun()


# ═══════════════════════════════════════════════════════════════
# 5.1 — SOP 戰略法典 (Classified File Cards)
# ═══════════════════════════════════════════════════════════════
def _s51(kb):
    st.markdown("""
<div class="t5-sec-head" style="--sa:#00F5FF">
  <div class="t5-sec-num">5.1</div>
  <div>
    <div class="t5-sec-title">戰略法典 — SOP Strategy Encyclopedia</div>
    <div class="t5-sec-sub">Time Arbitrage · Entry/Exit Discipline · Sector Intel · Hidden Tactics · OTC MA</div>
  </div>
</div>""", unsafe_allow_html=True)

    # [DC3] Streaming intro text
    intro_text = """
    **戰略法典系統:**
    
    本法典整合四大時間套利、進出場鐵律、產業族群情報、特殊心法與OTC均線秘技。
    這是Titan系統的知識核心，所有交易決策必須遵循此處的標準作業程序。
    """
    st.write_stream(_stream_text(intro_text, speed=0.01))

    # Load rules from knowledge base (PRESERVED)
    if 'all_rules' not in st.session_state:
        st.session_state.all_rules = kb.get_all_rules_for_ui()
    all_rules = st.session_state.all_rules

    # Sub-navigation via tabs (5 doctrine categories)
    w1, w2, w3, w4, w5 = st.tabs([
        "⏰ 四大時間套利", "📋 進出場紀律", "🏭 產業族群庫",
        "🧠 特殊心法", "📈 OTC 神奇均線"
    ])

    # ── W1: 四大時間套利 ──
    with w1:
        events = all_rules.get("time_arbitrage", [])
        if events:
            for rule in events:
                st.markdown(f'<div class="codex-card"><div class="codex-card-detail">{rule}</div></div>', unsafe_allow_html=True)
        else:
            _ARBS = [
                ("gold", "01", "新券蜜月期", "上市 0 – 90 天",
                 "上市初期追蹤，大戶定調，股性未定",
                 "進場甜蜜點：105–115 元。前 90 天是觀察期也是機會期，關注大股東動態與首批券商報告。"),
                ("green", "02", "滿年沈澱", "上市 350 – 420 天",
                 "沈澱洗牌結束，底部有支撐",
                 "觸發點：CB 站上 87MA 且帶量。經過一年的洗盤與沈澱，仍存活的標的底部結構扎實。"),
                ("", "03", "賣回保衛戰", "距賣回日 < 180 天",
                 "下檔保護最強，CB價 95–105 甜甜圈",
                 "最佳風報比窗口。賣回日臨近時，市場自然形成底部支撐，CB 價格不易跌破 100。"),
                ("red", "04", "百日轉換窗口", "距到期 < 100 天",
                 "最後一搏，轉換或歸零",
                 "股價需站上轉換價 × 1.05 才有轉換意義。時間價值快速遞減，必須精確把握時機。"),
            ]
            for cls, num, title, period, key_rule, detail in _ARBS:
                st.markdown(f"""
<div class="codex-card {cls}">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
    <div style="font-family:var(--f-o);font-size:28px;font-weight:900;color:rgba(0,245,255,.1);">{num}</div>
    <div>
      <div class="codex-card-title">{title}</div>
      <div style="font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,.3);letter-spacing:2px;">{period}</div>
    </div>
  </div>
  <div class="codex-card-key">{key_rule}</div>
  <div class="codex-card-detail">{detail}</div>
</div>""", unsafe_allow_html=True)

    # ── W2: 進出場紀律 ──
    with w2:
        ee = all_rules.get("entry_exit", {})
        if isinstance(ee, dict) and ee.get('entry'):
            st.text_area("📥 進場條件 (Entry)", value=ee.get('entry', '無紀錄'), height=300)
            st.text_area("📤 出場條件 (Exit)", value=ee.get('exit', '無紀錄'), height=300)
        else:
            # Entry cards
            st.markdown('<div style="font-family:var(--f-b);font-size:16px;color:rgba(0,255,127,.7);letter-spacing:2px;margin-bottom:14px;">📥 核心進場條件 — THE 4 COMMANDMENTS</div>', unsafe_allow_html=True)
            _ENTRIES = [
                ("green", "價格天條", "CB 市價 < 120 元", "理想區間 105 ~ 115 元。超過 120 = 溢價過高，槓桿效益不足。"),
                ("green", "均線天條", "87MA > 284MA", "中期多頭排列確認。均線交叉後回踩 87MA 不破 = 最佳進場。"),
                ("", "身分認證", "領頭羊 or 風口豬", "族群指標股（領頭羊）或主流題材二軍（風口豬），單兵不做。"),
                ("gold", "發債故事", "從無到有 / 擴產 / 政策事件", "三選一，故事是引爆點，沒有故事的 CB 只是數字。"),
            ]
            for cls, title, key, detail in _ENTRIES:
                st.markdown(f'<div class="codex-card {cls}"><div class="codex-card-title">{title}</div><div class="codex-card-key">{key}</div><div class="codex-card-detail">{detail}</div></div>', unsafe_allow_html=True)

            st.markdown('<div style="font-family:var(--f-b);font-size:16px;color:rgba(255,49,49,.7);letter-spacing:2px;margin:20px 0 14px;">📤 核心出場條件</div>', unsafe_allow_html=True)
            _EXITS = [
                ("red", "🛑 停損天條", "CB 跌破 100 元", "保本天條不妥協。不管故事多美，跌破即離場，沒有例外。"),
                ("gold", "💰 停利策略", "目標 152 元以上", "留魚尾策略：到達目標區間後分批出場，讓剩餘倉位跟跑。"),
                ("", "⏰ 時間停損", "持有超過 90 天未動", "靜止 = 機會成本燒蝕。超過 90 天無動能，重新評估或減倉。"),
            ]
            for cls, title, key, detail in _EXITS:
                st.markdown(f'<div class="codex-card {cls}"><div class="codex-card-title">{title}</div><div class="codex-card-key">{key}</div><div class="codex-card-detail">{detail}</div></div>', unsafe_allow_html=True)

    # ── W3: 產業族群庫 ──
    with w3:
        ind = all_rules.get("industry_story", {})
        stories = ind.get("general_issuance_stories", []) if isinstance(ind, dict) else []
        if stories:
            st.markdown("#### 發債故事總覽")
            st.text_area("General Issuance Stories", "\n\n".join(stories), height=200)
        sector_map = ind.get("sector_map", {}) if isinstance(ind, dict) else {}
        st.markdown("---")
        if sector_map:
            for s, stks in sorted(sector_map.items()):
                st.markdown(f'<div class="sector-row"><div class="sector-name">{s}</div><div class="sector-stocks">{", ".join(sorted(list(stks)))}</div></div>', unsafe_allow_html=True)
        else:
            _SECTORS = [
                ("AI伺服器", "廣達、緯創、英業達、技嘉"),
                ("散熱", "奇鋐、雙鴻、建準"),
                ("CoWoS封測", "日月光、矽品"),
                ("重電/電網", "華城、士電、中興電"),
                ("半導體設備", "弘塑、辛耘、漢微科"),
                ("航運", "長榮、陽明、萬海"),
                ("生技新藥", "藥華藥、合一"),
            ]
            for sect, stocks in _SECTORS:
                st.markdown(f'<div class="sector-row"><div class="sector-name">{sect}</div><div class="sector-stocks">{stocks}</div></div>', unsafe_allow_html=True)

    # ── W4: 特殊心法 ──
    with w4:
        tactics = all_rules.get("special_tactics", [])
        if tactics:
            st.text_area("Tactics & Mindset", "\n\n---\n\n".join(tactics), height=500)
        else:
            _MINDSETS = [
                ("賣出是種藝術", "目標區間到達後，分批出場，絕不一次梭哈。「留魚尾」策略讓下一次持倉更安心。"),
                ("跌破100是天條", "不管故事多美，CB跌破100元立刻離場，沒有例外，沒有感情。"),
                ("族群共振才是主力", "單兵突破假象居多。觀察是否有2~3檔同族群CB同步上攻，才是真正主力進場訊號。"),
                ("87MA是生命線", "股價站上87MA且均線向上，才是安全進場時機。跌破87MA視為第一警戒。"),
                ("溢價率的陷阱", "溢價率 > 20% 的CB，上漲空間有限。避開高溢價，選擇低溢價（5~15%）的標的。"),
                ("籌碼鬆動就跑", "已轉換比例超過 30%，代表大量轉換股票，股東結構改變，籌碼不乾淨，警惕。"),
                ("尾盤定勝負", "13:25後的最後25分鐘，是當天多空最誠實的表態。收盤站穩才是真突破。"),
                ("消息面最後出現", "有基本面、技術面支撐，消息面是最後確認彈，不是買入理由。"),
                ("跟隨資金流向", "先看哪個產業有錢進來，再找該產業中CB價格最低、溢價最小的標的。"),
                ("做錯立刻認錯", "沒有人能100%準確，做錯了立刻認錯出場，留下現金才能把握下一次機會。"),
            ]
            for i, (title, desc) in enumerate(_MINDSETS, 1):
                st.markdown(f"""
<div class="mindset-card">
  <div class="mindset-num">{i:02d}</div>
  <div style="flex:1">
    <div class="mindset-title">{title}</div>
    <div class="mindset-desc">{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── W5: OTC 神奇均線 ──
    with w5:
        try:
            otc = kb.get_otc_magic_rules()
            for name, desc in otc.items():
                label = name.replace('_', ' ').title()
                st.markdown(f'<div class="codex-card purple"><div class="codex-card-title">{label}</div><div class="codex-card-detail">{desc}</div></div>', unsafe_allow_html=True)
        except Exception:
            _OTC = [
                ("87日均線 (季線)", "OTC市場的核心生命線。多頭時支撐強，空頭時壓力大。站穩 87MA 是進場的最低門檻。"),
                ("284日均線 (年線)", "長線多空分界。284MA 翻揚 = 機構開始佈局訊號。跌破年線需嚴格減倉。"),
                ("雙線黃金交叉", "87MA 由下往上穿越 284MA，啟動中期多頭，歷史勝率 >70%。是系統性做多的核心信號。"),
                ("上櫃特性", "OTC 成交量較小，主力更容易控盤。單日異常量能（>3 倍均量）需特別警覺——可能是出貨日。"),
            ]
            for title, desc in _OTC:
                st.markdown(f'<div class="codex-card purple"><div class="codex-card-title">{title}</div><div class="codex-card-detail">{desc}</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 5.2 — 情報獵殺分析結果 (ALL LOGIC PRESERVED)
# ═══════════════════════════════════════════════════════════════
def _s52(kb, df):
    st.markdown("""
<div class="t5-sec-head" style="--sa:#FF9A3C">
  <div class="t5-sec-num">5.2</div>
  <div>
    <div class="t5-sec-title" style="color:#FF9A3C;">情報獵殺 — Intel Analysis Engine</div>
    <div class="t5-sec-sub">Upload · Parse · Local Analysis · Gemini AI Deep Dive</div>
  </div>
</div>""", unsafe_allow_html=True)

    # [DC3] Streaming intro
    intel_intro = """
    **情報獵殺系統:**
    
    上傳PDF或TXT情報文件，系統將執行本地解析提取關鍵資訊。
    配置Gemini API Key後，可啟動AI深度分析，自動生成情報摘要與戰略建議。
    """
    st.write_stream(_stream_text(intel_intro, speed=0.01))

    intel_files = st.session_state.get('intel_files', [])
    if intel_files:
        st.toast("🎯 偵測到情報檔案 / Intel files detected", icon="🔍")
        
        for file in intel_files:
            st.markdown(f'<div class="codex-card gold"><div class="codex-card-title">📄 {file.name}</div><div class="codex-card-detail">情報檔案已上傳，展開查看分析結果</div></div>', unsafe_allow_html=True)
            with st.expander(f"🔍 展開分析報告: {file.name}", expanded=False):
                try:
                    from intelligence import IntelligenceEngine
                    intel = IntelligenceEngine()
                    
                    st.toast("🚀 系統分析中 / Analyzing...", icon="⏳")
                    result = intel.analyze_file(file, kb, df)
                    
                    if "error" in result:
                        st.toast(f"❌ 分析失敗 / Analysis failed: {result['error']}", icon="⚡")
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
                                    st.markdown(report)
                                    st.toast("✅ AI分析完成 / AI analysis complete", icon="🎯")
                                except Exception as e:
                                    st.toast(f"❌ Gemini失敗 / Gemini failed: {e}", icon="⚡")
                        else:
                            st.toast("⚠️ 未輸入API Key / No API key provided", icon="⚡")
                except ImportError:
                    st.toast(f"⚠️ 情報引擎未掛載 / Intel engine not mounted", icon="⚡")
    else:
        st.markdown("""
<div style="text-align:center;padding:60px 30px;">
  <div style="font-size:48px;margin-bottom:16px;opacity:.3;">🕵️</div>
  <div style="font-family:var(--f-b);font-size:18px;color:rgba(255,255,255,.4);letter-spacing:2px;margin-bottom:8px;">NO INTEL FILES DETECTED</div>
  <div style="font-family:var(--f-m);font-size:11px;color:rgba(160,176,208,.3);letter-spacing:2px;">請於左側上傳情報文件 (PDF/TXT) 以啟動分析引擎</div>
</div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 5.3 — CBAS 槓桿試算儀 (84px MASSIVE DISPLAY)
# ═══════════════════════════════════════════════════════════════
def _s53():
    st.markdown("""
<div class="t5-sec-head" style="--sa:#00FF7F">
  <div class="t5-sec-num">5.3</div>
  <div>
    <div class="t5-sec-title" style="color:#00FF7F;">CBAS 槓桿試算儀</div>
    <div class="t5-sec-sub">Convertible Bond Arbitrage Simulator · Leverage Engine</div>
  </div>
</div>""", unsafe_allow_html=True)

    # [DC3] Streaming explanation
    cbas_intro = """
    **CBAS槓桿試算系統:**
    
    輸入CB市價，系統自動計算理論權利金（CB價 - 100元）與槓桿倍數。
    槓桿倍數 = CB市價 ÷ 權利金，高槓桿（>5×）適合以小博大，低槓桿（<3×）風報比偏低。
    """
    st.write_stream(_stream_text(cbas_intro, speed=0.01))

    # Wide input area
    col_in, col_space = st.columns([2, 1])
    with col_in:
        cb_price = st.number_input(
            "輸入 CB 市價 (元)", min_value=100.0, value=110.0, step=0.5, format="%.2f",
            key="cbas_price_v300"
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

        # MASSIVE CALC SCREEN
        st.markdown(f"""
<div class="calc-screen">
  <div class="calc-lbl">Theoretical Premium (理論權利金)</div>
  <div class="calc-val {prem_cls}">{premium_cost:.2f}<span class="calc-unit">元</span></div>
  <div class="calc-divider"></div>
  <div class="calc-lbl">Leverage Ratio (槓桿倍數)</div>
  <div class="calc-val {lev_cls}">{leverage:.1f}<span class="calc-unit">×</span></div>
</div>""", unsafe_allow_html=True)

        st.toast("✅ 試算完成 / Calculation complete", icon="🎯")

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
        st.markdown('<div style="font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,.25);letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;">Quick Reference: Leverage at Different CB Prices</div>', unsafe_allow_html=True)
        ref_cols = st.columns(5)
        for i, p in enumerate([103, 105, 110, 115, 120]):
            prem = p - 100
            lev = p / prem if prem > 0 else 0
            color = "#00FF7F" if lev > 5 else ("#FFD700" if lev > 3 else "#FF6B6B")
            ref_cols[i].markdown(f"""
<div style="text-align:center;padding:10px;background:rgba(255,255,255,.02);border:1px solid rgba(255,255,255,.04);border-radius:8px;">
  <div style="font-family:var(--f-m);font-size:9px;color:rgba(160,176,208,.35);letter-spacing:1px;">CB {p}元</div>
  <div style="font-family:var(--f-i);font-size:26px;font-weight:800;color:{color};line-height:1.2;">{lev:.1f}×</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
<div class="calc-screen">
  <div class="calc-lbl">CB 市價需高於 100 元</div>
  <div class="calc-val" style="color:rgba(160,176,208,.15);">—.—<span class="calc-unit">×</span></div>
</div>""", unsafe_allow_html=True)
        st.toast("⚠️ CB市價需>100元 / CB price must be >100", icon="⚡")


# ═══════════════════════════════════════════════════════════════
# 5.4 — 時間套利行事曆 (Episode Cards + Big Day Counter)
# ═══════════════════════════════════════════════════════════════
def _s54(calendar, df):
    st.markdown("""
<div class="t5-sec-head" style="--sa:#FFD700">
  <div class="t5-sec-num">5.4</div>
  <div>
    <div class="t5-sec-title" style="color:#FFD700;">戰略行事曆 — Time Arbitrage Calendar</div>
    <div class="t5-sec-sub">Upcoming Events · Countdown · Honeymoon / Put / Conversion Windows</div>
  </div>
</div>""", unsafe_allow_html=True)

    # [DC3] Streaming calendar intro
    calendar_intro = """
    **時間套利行事曆:**
    
    掃描CB清單中的關鍵時間點：蜜月期、賣回日、轉換窗口等事件。
    系統自動計算倒數天數，提前預警時間套利機會，確保不錯過任何窗口。
    """
    st.write_stream(_stream_text(calendar_intro, speed=0.01))

    if df.empty:
        st.markdown("""
<div style="text-align:center;padding:60px 30px;">
  <div style="font-size:48px;margin-bottom:16px;opacity:.3;">📅</div>
  <div style="font-family:var(--f-b);font-size:18px;color:rgba(255,255,255,.4);letter-spacing:2px;margin-bottom:8px;">NO CB DATA LOADED</div>
  <div style="font-family:var(--f-m);font-size:11px;color:rgba(160,176,208,.3);letter-spacing:2px;">請上傳 CB 清單以掃描時間套利事件</div>
</div>""", unsafe_allow_html=True)
        return

    days_ahead = st.slider("掃描未來天數", 7, 90, 30, key="cal_days_v300")
    today = datetime.now().date()
    future_date = today + timedelta(days=days_ahead)
    upcoming_events = []

    # Column detection (PRESERVED)
    code_col = next((c for c in df.columns if 'code' in c.lower()), None)
    name_col = next((c for c in df.columns if 'name' in c.lower()), None)
    list_col = next((c for c in df.columns if 'list' in c.lower() or 'issue' in c.lower()), None)
    put_col  = next((c for c in df.columns if 'put' in c.lower() or '賣回' in c.lower()), None)

    st.toast("🚀 掃描事件中 / Scanning events...", icon="⏳")

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
        st.toast(f"✅ 發現{len(upcoming_events)}個事件 / Found {len(upcoming_events)} events", icon="🎯")

        # Summary counter
        st.markdown(f"""
<div style="display:flex;gap:16px;margin-bottom:20px;">
  <div style="flex:1;text-align:center;padding:18px;background:rgba(255,215,0,.03);border:1px solid rgba(255,215,0,.1);border-radius:12px;">
    <div style="font-family:var(--f-o);font-size:42px;font-weight:900;color:#FFD700;line-height:1;">{len(upcoming_events)}</div>
    <div style="font-family:var(--f-m);font-size:9px;color:rgba(255,215,0,.4);letter-spacing:2px;margin-top:6px;">UPCOMING EVENTS</div>
  </div>
  <div style="flex:1;text-align:center;padding:18px;background:rgba(0,245,255,.02);border:1px solid rgba(0,245,255,.08);border-radius:12px;">
    <div style="font-family:var(--f-o);font-size:42px;font-weight:900;color:#00F5FF;line-height:1;">{days_ahead}</div>
    <div style="font-family:var(--f-m);font-size:9px;color:rgba(0,245,255,.35);letter-spacing:2px;margin-top:6px;">DAY SCAN WINDOW</div>
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
  <div style="font-family:var(--f-b);font-size:16px;color:rgba(255,255,255,.35);letter-spacing:2px;">未來 {days_ahead} 天內無觸發任何時間套利事件</div>
</div>""", unsafe_allow_html=True)
        st.toast("⚠️ 無即將到來的事件 / No upcoming events", icon="⚡")


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY
# ═══════════════════════════════════════════════════════════════
def render():
    """Tab 5 — 戰略知識法典 (Strategic Knowledge Codex) V300 — DIRECTOR'S CUT"""
    _inject_css()
    
    # ── [DC1] TACTICAL GUIDE MODAL (First Visit) ──
    if 't5_guide_shown' not in st.session_state:
        show_tactical_guide()
        return
    
    _render_hero()
    _render_nav()

    kb       = _load_kb()
    calendar = _load_calendar()
    df       = st.session_state.get('df', pd.DataFrame())

    section_map = {
        "5.1": lambda: _s51(kb),
        "5.2": lambda: _s52(kb, df),
        "5.3": _s53,
        "5.4": lambda: _s54(calendar, df),
    }
    active = st.session_state.get('t5_active', '5.1')
    fn = section_map.get(active, lambda: _s51(kb))
    try:
        fn()
    except Exception as exc:
        import traceback
        st.toast(f"❌ Section {active} 錯誤 / Error: {exc}", icon="⚡")
        with st.expander("Debug"):
            st.code(traceback.format_exc())

    st.markdown(f'<div class="t5-foot">Titan Strategic Codex V300 — Director\'s Cut · {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>', unsafe_allow_html=True)
