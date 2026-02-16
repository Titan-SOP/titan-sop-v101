# ui_desktop/tab1_macro.py
# Titan SOP V400 — 宏觀風控指揮中心 (Macro Risk Command Center)
# ╔═══════════════════════════════════════════════════════════════════╗
# ║  "GOD-TIER V400 FIXED"  —  Netflix × Palantir × Tesla           ║
# ║  CRITICAL FIX: Mock engine for demo/testing purposes             ║
# ║  Replace mock engine with real MacroRiskEngine when available    ║
# ╚═══════════════════════════════════════════════════════════════════╝

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time

# ══════════════════════════════════════════════════════════════════════════════
#  MOCK ENGINE (臨時解決方案 - 替換為真實引擎)
# ══════════════════════════════════════════════════════════════════════════════
class MockMacroRiskEngine:
    """臨時 Mock Engine - 請替換為真實的 MacroRiskEngine"""
    
    def compute_macro_signal(self):
        """模擬宏觀信號"""
        import random
        signals = ["GREEN_LIGHT", "YELLOW_LIGHT", "RED_LIGHT"]
        signal = random.choice(signals)
        
        return {
            "signal": signal,
            "temp_pct": random.uniform(30, 80),
            "temp_delta": random.uniform(-5, 5),
            "pr90": random.uniform(10, 25),
            "pr90_delta": random.uniform(-2, 2),
            "ptt_score": random.uniform(4, 8),
            "ptt_delta": random.uniform(-1, 1),
            "vix": random.uniform(12, 25),
            "vix_delta": random.uniform(-2, 2),
            "chart_data": {
                "date": [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)],
                "value": [random.uniform(40, 80) for _ in range(30)]
            }
        }
    
    def compute_temperature(self):
        """模擬溫度計算"""
        import random
        temp = random.uniform(30, 85)
        return {
            "temp_pct": temp,
            "history": {
                "dates": [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30, 0, -1)],
                "temps": [random.uniform(30, 85) for _ in range(30)]
            },
            "avg_days_to_cool": random.randint(5, 12)
        }
    
    def compute_pr90(self):
        """模擬 PR90 計算"""
        import random
        stocks = [
            {"symbol": "2330", "name": "台積電", "pr90": random.uniform(15, 25), "price": random.uniform(500, 600), "volume": random.randint(50000, 150000)},
            {"symbol": "2317", "name": "鴻海", "pr90": random.uniform(12, 20), "price": random.uniform(100, 150), "volume": random.randint(80000, 200000)},
            {"symbol": "2454", "name": "聯發科", "pr90": random.uniform(14, 22), "price": random.uniform(800, 1000), "volume": random.randint(30000, 80000)},
            {"symbol": "2881", "name": "富邦金", "pr90": random.uniform(10, 18), "price": random.uniform(60, 80), "volume": random.randint(40000, 100000)},
            {"symbol": "2882", "name": "國泰金", "pr90": random.uniform(11, 19), "price": random.uniform(50, 70), "volume": random.randint(35000, 90000)},
            {"symbol": "2412", "name": "中華電", "pr90": random.uniform(9, 16), "price": random.uniform(120, 140), "volume": random.randint(20000, 60000)},
            {"symbol": "2308", "name": "台達電", "pr90": random.uniform(13, 21), "price": random.uniform(300, 400), "volume": random.randint(25000, 70000)},
            {"symbol": "2303", "name": "聯電", "pr90": random.uniform(12, 20), "price": random.uniform(40, 60), "volume": random.randint(60000, 150000)},
            {"symbol": "1301", "name": "台塑", "pr90": random.uniform(10, 17), "price": random.uniform(80, 100), "volume": random.randint(30000, 80000)},
            {"symbol": "1303", "name": "南亞", "pr90": random.uniform(11, 18), "price": random.uniform(60, 80), "volume": random.randint(25000, 70000)},
        ]
        pr90_pct = random.uniform(12, 20)
        return {
            "pr90_pct": pr90_pct,
            "top_stocks": stocks
        }
    
    def compute_sector_heatmap(self):
        """模擬族群熱度圖"""
        import random
        sectors = [
            {"name": "半導體", "gain_pct": random.uniform(-2, 5), "money_flow": random.randint(5000, 15000), "leader": "台積電"},
            {"name": "金融", "gain_pct": random.uniform(-1, 3), "money_flow": random.randint(3000, 10000), "leader": "富邦金"},
            {"name": "電子", "gain_pct": random.uniform(-1, 4), "money_flow": random.randint(4000, 12000), "leader": "鴻海"},
            {"name": "航運", "gain_pct": random.uniform(-3, 2), "money_flow": random.randint(2000, 8000), "leader": "長榮"},
            {"name": "傳產", "gain_pct": random.uniform(-1, 2), "money_flow": random.randint(1500, 6000), "leader": "台塑"},
            {"name": "生技", "gain_pct": random.uniform(-2, 6), "money_flow": random.randint(1000, 5000), "leader": "浩鼎"},
        ]
        
        return {
            "sectors": sectors,
            "heatmap_data": {
                "values": [[random.uniform(-2, 5) for _ in range(5)] for _ in range(6)],
                "x_labels": ["本週", "上週", "上月", "季度", "年度"],
                "y_labels": [s["name"] for s in sectors],
                "text": [[f"{random.uniform(-2, 5):.1f}%" for _ in range(5)] for _ in range(6)]
            }
        }
    
    def compute_turnover_leaders(self):
        """模擬成交重心"""
        import random
        leaders = [
            {"symbol": "2330", "name": "台積電", "volume": random.randint(100000, 300000), "price": random.uniform(500, 600), "change_pct": random.uniform(-2, 3)},
            {"symbol": "2317", "name": "鴻海", "volume": random.randint(150000, 350000), "price": random.uniform(100, 150), "change_pct": random.uniform(-1, 2)},
            {"symbol": "2454", "name": "聯發科", "volume": random.randint(50000, 150000), "price": random.uniform(800, 1000), "change_pct": random.uniform(-1, 4)},
            {"symbol": "2308", "name": "台達電", "volume": random.randint(40000, 120000), "price": random.uniform(300, 400), "change_pct": random.uniform(-1, 3)},
            {"symbol": "2303", "name": "聯電", "volume": random.randint(100000, 250000), "price": random.uniform(40, 60), "change_pct": random.uniform(-2, 2)},
            {"symbol": "2881", "name": "富邦金", "volume": random.randint(60000, 180000), "price": random.uniform(60, 80), "change_pct": random.uniform(-1, 2)},
            {"symbol": "2882", "name": "國泰金", "volume": random.randint(50000, 150000), "price": random.uniform(50, 70), "change_pct": random.uniform(-1, 1)},
            {"symbol": "2412", "name": "中華電", "volume": random.randint(30000, 100000), "price": random.uniform(120, 140), "change_pct": random.uniform(-0.5, 1)},
            {"symbol": "2609", "name": "陽明", "volume": random.randint(80000, 200000), "price": random.uniform(50, 80), "change_pct": random.uniform(-3, 4)},
            {"symbol": "2603", "name": "長榮", "volume": random.randint(70000, 190000), "price": random.uniform(100, 150), "change_pct": random.uniform(-2, 3)},
        ]
        return {"leaders": leaders}
    
    def compute_trend_radar(self):
        """模擬趨勢雷達"""
        import random
        total = random.randint(40, 60)
        above = random.randint(20, 45)
        
        trending = [
            {"symbol": "2330", "name": "台積電", "distance_from_87ma": random.uniform(5, 15), "ma87_deduction": random.uniform(550, 600), "trend_strength": random.uniform(7, 9)},
            {"symbol": "2454", "name": "聯發科", "distance_from_87ma": random.uniform(3, 12), "ma87_deduction": random.uniform(850, 950), "trend_strength": random.uniform(6, 8)},
            {"symbol": "2308", "name": "台達電", "distance_from_87ma": random.uniform(4, 10), "ma87_deduction": random.uniform(320, 380), "trend_strength": random.uniform(6, 8)},
            {"symbol": "3711", "name": "日月光投控", "distance_from_87ma": random.uniform(2, 8), "ma87_deduction": random.uniform(90, 110), "trend_strength": random.uniform(5, 7)},
            {"symbol": "2882", "name": "國泰金", "distance_from_87ma": random.uniform(1, 7), "ma87_deduction": random.uniform(55, 65), "trend_strength": random.uniform(5, 7)},
            {"symbol": "2881", "name": "富邦金", "distance_from_87ma": random.uniform(2, 9), "ma87_deduction": random.uniform(65, 75), "trend_strength": random.uniform(5, 7)},
            {"symbol": "2412", "name": "中華電", "distance_from_87ma": random.uniform(1, 5), "ma87_deduction": random.uniform(125, 135), "trend_strength": random.uniform(4, 6)},
            {"symbol": "1301", "name": "台塑", "distance_from_87ma": random.uniform(1, 6), "ma87_deduction": random.uniform(85, 95), "trend_strength": random.uniform(4, 6)},
        ]
        
        dates = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(60, 0, -1)]
        
        return {
            "total_stocks": total,
            "above_87ma": above,
            "above_87ma_pct": (above / total * 100) if total > 0 else 0,
            "prediction_days": 20,
            "adam_target": random.randint(18000, 22000),
            "trending": trending,
            "chart_data": {
                "date": dates,
                "ma87": [random.uniform(17000, 19000) for _ in range(60)],
                "price": [random.uniform(17500, 20000) for _ in range(60)]
            }
        }
    
    def compute_wtx_predator(self):
        """模擬台指獵殺"""
        import random
        anc = random.randint(19000, 21000)
        price = anc + random.randint(-500, 1000)
        is_red = random.choice([True, False])
        
        return {
            "name": f"{datetime.now().strftime('%Y年%m月')}台指期",
            "anc": anc,
            "price": price,
            "is_red_month": is_red,
            "t": {
                "1B": anc + (300 if is_red else -300),
                "2B": anc + (600 if is_red else -600),
                "3B": anc + (900 if is_red else -900),
                "HR": anc + (1200 if is_red else -1200),
            }
        }


# ══════════════════════════════════════════════════════════════════════════════
#  [UPGRADE #2] VALKYRIE AI TYPEWRITER
# ══════════════════════════════════════════════════════════════════════════════
def _stream_text(text, speed=0.015):
    """Character-by-character generator for st.write_stream"""
    for char in text:
        yield char
        time.sleep(speed)


def _stream_fast(text, speed=0.008):
    """Faster streaming for shorter texts"""
    for char in text:
        yield char
        time.sleep(speed)


# ══════════════════════════════════════════════════════════════════════════════
#  [UPGRADE #1] TACTICAL TOAST SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
def tactical_toast(message, mode="success", icon=None):
    """Unified toast system for all notifications"""
    toast_configs = {
        "success": {"icon": icon or "🎯", "prefix": "✅ 任務完成"},
        "processing": {"icon": icon or "⏳", "prefix": "🚀 正在執行戰術運算..."},
        "alert": {"icon": icon or "⚡", "prefix": "⚠️ 偵測到風險訊號"},
        "info": {"icon": icon or "ℹ️", "prefix": "📊 系統資訊"},
        "error": {"icon": icon or "❌", "prefix": "🔴 系統警報"},
    }
    
    config = toast_configs.get(mode, toast_configs["info"])
    st.toast(f"{config['prefix']} / {message}", icon=config['icon'])


# ══════════════════════════════════════════════════════════════════════════════
#  [UPGRADE #1] TACTICAL GUIDE DIALOG
# ══════════════════════════════════════════════════════════════════════════════
@st.dialog("🔰 戰術指導 — Macro Risk Command Center")
def _show_tactical_guide():
    st.markdown("""
<div style="font-family:'Rajdhani',sans-serif;font-size:15px;color:#C8D8E8;line-height:1.8;">

### 🛡️ 歡迎進入宏觀風控指揮中心

本模組是 Titan OS 的**戰略核心**，整合 7 大子系統即時監控市場脈動：

**🚦 1.1 風控儀表 (MACRO HUD)**
三燈號系統 (🟢綠/🟡黃/🔴紅) 自動判定進攻/防守態勢，搭配 VIX、PR90 籌碼分佈、PTT 散戶情緒三重驗證。

**🌡️ 1.2 多空溫度計 / 📊 1.3 籌碼分佈 / 🗺️ 1.4 族群熱度**
高價權值股站上 87MA 的比例 = 市場體溫。籌碼分佈圖 + 族群資金流向，一眼判斷主力資金去向。

**💹 1.5 成交重心 / 👑 1.6 趨勢雷達**
全市場 TOP 100 成交重心即時掃描 + 高價權值股趨勢追蹤，附帶 87MA 扣抵預測與亞當理論反射路徑。

**🎯 1.7 台指獵殺 (WTX Predator)**
獨門戰法 — 利用過去 12 個月結算慣性推導本月台指期虛擬 K 棒，精準鎖定 1B/2B/3B/HR 結算目標價。

**⚠️ DEMO 模式提示**
當前使用 Mock Engine 進行演示。如需真實數據，請連接實際的 MacroRiskEngine。

</div>""", unsafe_allow_html=True)
    if st.button("✅ 收到，進入戰情室 (Roger That)", type="primary", use_container_width=True):
        st.session_state['tab1_guided'] = True
        tactical_toast("戰情室已激活 / War Room Activated", "success")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
SIGNAL_MAP = {
    "GREEN_LIGHT":  "🟢 綠燈：積極進攻",
    "YELLOW_LIGHT": "🟡 黃燈：區間操作",
    "RED_LIGHT":    "🔴 紅燈：現金為王",
}

SIGNAL_PALETTE = {
    "GREEN_LIGHT":  ("#00FF7F", "0,255,127"),
    "YELLOW_LIGHT": ("#FFD700", "255,215,0"),
    "RED_LIGHT":    ("#FF3131", "255,49,49"),
}

SUB_MODULES = [
    ("1.1", "🚦", "風控儀表",  "MACRO HUD"),
    ("1.2", "🌡️", "多空溫度",  "THERMO"),
    ("1.3", "📊", "籌碼分佈",  "PR90"),
    ("1.4", "🗺️", "族群熱度",  "HEATMAP"),
    ("1.5", "💹", "成交重心",  "VOLUME"),
    ("1.6", "👑", "趨勢雷達",  "RADAR"),
    ("1.7", "🎯", "台指獵殺",  "PREDATOR"),
]


# ══════════════════════════════════════════════════════════════════════════════
#  CSS — TITAN OS CINEMATIC STYLES (ENHANCED V400)
# ══════════════════════════════════════════════════════════════════════════════
def _inject_css():
    st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@300;400;600;700&family=JetBrains+Mono:wght@300;400;600;700&family=Orbitron:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">

<style>
:root {
    --c-gold:    #FFD700;
    --c-cyan:    #00F5FF;
    --c-red:     #FF3131;
    --c-green:   #00FF7F;
    --c-dim:     #667788;
    --bg-card:   rgba(14, 20, 32, 0.88);
    --bg-glass:  rgba(255, 255, 255, 0.028);
    --bd-subtle: rgba(255, 255, 255, 0.07);
    --f-display: 'Bebas Neue', sans-serif;
    --f-body:    'Rajdhani', sans-serif;
    --f-mono:    'JetBrains Mono', monospace;
    --f-o:       'Orbitron', sans-serif;
}

[data-testid="stMetricValue"] { font-size: 42px !important; }
[data-testid="stDataFrame"]   { font-size: 18px !important; }

.hero-container {
    position: relative;
    padding: 44px 40px 36px;
    border-radius: 22px;
    text-align: center;
    margin-bottom: 28px;
    background: linear-gradient(180deg, rgba(10,10,16,0) 0%, rgba(0,0,0,0.82) 100%);
    border: 1px solid rgba(255,255,255,0.09);
    overflow: hidden;
}
.hero-container::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% 120%,
        var(--hero-glow, rgba(255,215,0,0.08)) 0%,
        transparent 70%);
    pointer-events: none;
}
.hero-val, .hero-title {
    font-family: var(--f-display);
    font-size: 80px !important;
    font-weight: 900;
    line-height: 1;
    letter-spacing: 3px;
    color: #FFF;
    text-shadow: 0 0 40px var(--hero-color, rgba(255,215,0,0.6));
    margin-bottom: 12px;
}
.hero-lbl, .hero-subtitle {
    font-family: var(--f-mono);
    font-size: 22px !important;
    color: #777;
    letter-spacing: 6px;
    text-transform: uppercase;
}
.hero-badge {
    display: inline-block;
    margin-top: 18px;
    font-family: var(--f-mono);
    font-size: 13px;
    color: var(--hero-color, #FFD700);
    border: 1px solid var(--hero-color, #FFD700);
    border-radius: 30px;
    padding: 6px 22px;
    letter-spacing: 3px;
    background: rgba(0,0,0,0.4);
}
.hero-pulse {
    display: inline-block;
    width: 14px; height: 14px;
    border-radius: 50%;
    background: var(--hero-color, #FFD700);
    margin-right: 10px;
    box-shadow: 0 0 0 4px rgba(var(--hero-rgb, 255,215,0), 0.2),
                0 0 20px var(--hero-color, #FFD700);
    animation: pulse-anim 2s ease-in-out infinite;
}
@keyframes pulse-anim {
    0%,100% { opacity: 1; }
    50%     { opacity: 0.7; }
}

.poster-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 10px;
    margin-bottom: 32px;
}
.poster-card {
    height: 160px;
    background: #0d1117;
    border: 1px solid #22282f;
    border-radius: 14px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    transition: all 0.28s cubic-bezier(0.25, 0.8, 0.25, 1);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}
.poster-card:hover {
    transform: translateY(-6px) scale(1.02);
    border-color: var(--poster-accent, #FFD700);
    box-shadow: 0 16px 40px rgba(0,0,0,0.6);
}
.poster-card.active {
    border-color: var(--poster-accent, #FFD700);
    box-shadow: 0 8px 28px rgba(0,0,0,0.5);
}
.poster-icon {
    font-size: 38px;
    line-height: 1;
    filter: drop-shadow(0 0 12px var(--poster-accent, #FFD700));
}
.poster-code {
    font-family: var(--f-mono);
    font-size: 11px;
    color: var(--poster-accent, #FFD700);
    letter-spacing: 2px;
    font-weight: 600;
}
.poster-text {
    font-family: var(--f-body);
    font-size: 15px;
    font-weight: 600;
    color: #C8D8E8;
}
.poster-tag {
    font-family: var(--f-mono);
    font-size: 9px;
    color: #556677;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.rank-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
    margin: 24px 0;
}
.rank-card {
    background: var(--bg-card);
    border: 1px solid var(--bd-subtle);
    border-radius: 12px;
    padding: 20px;
    transition: all 0.3s;
    position: relative;
}
.rank-card:hover {
    transform: translateY(-4px);
    border-color: var(--c-gold);
    box-shadow: 0 12px 32px rgba(0,0,0,0.4);
}
.rank-number {
    position: absolute;
    top: 12px;
    right: 12px;
    font-family: var(--f-display);
    font-size: 48px;
    color: rgba(255,215,0,0.15);
    font-weight: 900;
}
.rank-title {
    font-family: var(--f-body);
    font-size: 20px;
    font-weight: 700;
    color: #FFF;
    margin-bottom: 8px;
}
.rank-value {
    font-family: var(--f-mono);
    font-size: 32px;
    font-weight: 700;
    color: var(--c-cyan);
    margin: 12px 0;
}
.rank-meta {
    font-family: var(--f-mono);
    font-size: 12px;
    color: #888;
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}
.rank-chip {
    background: rgba(255,215,0,0.1);
    border: 1px solid rgba(255,215,0,0.3);
    color: var(--c-gold);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 11px;
}

.terminal-box {
    font-family: var(--f-mono);
    background: #050505;
    color: #00F5FF;
    padding: 24px;
    border-left: 3px solid #00F5FF;
    border-radius: 8px;
    box-shadow: inset 0 0 20px rgba(0, 245, 255, 0.05);
    margin: 20px 0;
    line-height: 1.8;
    font-size: 15px;
}

.nav-deck-frame {
    background: rgba(10,14,20,0.4);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 18px;
    padding: 22px 18px 18px;
    margin-bottom: 30px;
}
.nav-deck-label {
    font-family: var(--f-mono);
    font-size: 10px;
    color: rgba(255,215,0,0.4);
    letter-spacing: 3px;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 16px;
}
.content-frame {
    background: rgba(255,255,255,0.008);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 20px;
    padding: 32px 28px;
    min-height: 600px;
}

.titan-foot {
    text-align: center;
    font-family: var(--f-mono);
    font-size: 10px;
    color: rgba(200,215,230,0.2);
    letter-spacing: 2px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.04);
}

.demo-warning {
    background: rgba(255, 165, 0, 0.1);
    border: 1px solid rgba(255, 165, 0, 0.3);
    border-radius: 12px;
    padding: 16px;
    margin: 20px 0;
    font-family: var(--f-mono);
    font-size: 13px;
    color: #FFA500;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER: Create Rank Card HTML
# ══════════════════════════════════════════════════════════════════════════════
def create_rank_card(rank, title, value, meta_items):
    """Generate HTML for a single rank card"""
    chips = "".join([f'<span class="rank-chip">{item}</span>' for item in meta_items])
    return f"""
<div class="rank-card">
    <div class="rank-number">#{rank}</div>
    <div class="rank-title">{title}</div>
    <div class="rank-value">{value}</div>
    <div class="rank-meta">{chips}</div>
</div>
"""


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1.1 — MACRO HUD
# ══════════════════════════════════════════════════════════════════════════════
def render_1_1_hud():
    """🚦 風控儀表 (Macro Risk HUD)"""
    tactical_toast("風控儀表系統啟動 / HUD System Online", "processing")
    
    eng = MockMacroRiskEngine()
    try:
        data = eng.compute_macro_signal()
    except Exception as e:
        tactical_toast(f"資料載入失敗 / Data Load Failed: {str(e)}", "error")
        return

    sig = data["signal"]
    hex_color, rgb_str = SIGNAL_PALETTE[sig]

    st.markdown(f"""
<div class="hero-container" style="--hero-glow:rgba({rgb_str},0.15);
     --hero-color:{hex_color};--hero-rgb:{rgb_str};">
  <div class="hero-title">{SIGNAL_MAP[sig].split('：')[0]}</div>
  <div class="hero-subtitle">MACRO RISK SIGNAL</div>
  <div class="hero-badge">
    <span class="hero-pulse"></span>
    LIVE ANALYSIS (DEMO)
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="demo-warning">⚠️ DEMO 模式 - 使用模擬數據</div>', unsafe_allow_html=True)

    tactical_toast("信號計算完成 / Signal Computed", "success")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("🔥 市場溫度", f"{data.get('temp_pct', 0):.1f}%",
                  f"{data.get('temp_delta', 0):+.1f}%")
    with c2:
        st.metric("📊 PR90 籌碼", f"{data.get('pr90', 0):.1f}%",
                  f"{data.get('pr90_delta', 0):+.1f}%")
    with c3:
        st.metric("💬 PTT 情緒", f"{data.get('ptt_score', 0):.1f}",
                  f"{data.get('ptt_delta', 0):+.1f}")
    with c4:
        st.metric("📈 VIX 指數", f"{data.get('vix', 0):.2f}",
                  f"{data.get('vix_delta', 0):+.2f}")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis_text = f"""
【宏觀風控 AI 判讀】

當前信號：{SIGNAL_MAP[sig]}

市場體溫 {data.get('temp_pct', 0):.1f}% — {'高溫過熱區' if data.get('temp_pct', 0) > 70 else '溫度正常' if data.get('temp_pct', 0) > 30 else '低溫冷卻區'}
籌碼分佈 PR90 {data.get('pr90', 0):.1f}% — {'籌碼集中主力控盤' if data.get('pr90', 0) > 15 else '籌碼分散散戶主導'}
PTT 散戶情緒 {data.get('ptt_score', 0):.1f} 分 — {'樂觀情緒高漲' if data.get('ptt_score', 0) > 6 else '謹慎觀望氛圍'}
VIX 恐慌指數 {data.get('vix', 0):.2f} — {'市場波動加劇' if data.get('vix', 0) > 20 else '市場平穩運行'}

綜合判定：根據三重驗證機制，系統建議當前採取「{SIGNAL_MAP[sig].split('：')[1]}」策略。
"""
    
    if 'hud_analysis_streamed' not in st.session_state:
        st.write_stream(_stream_text(analysis_text))
        st.session_state['hud_analysis_streamed'] = True
    else:
        st.markdown(analysis_text)
    
    st.markdown('</div>', unsafe_allow_html=True)

    if 'chart_data' in data:
        chart_df = pd.DataFrame(data['chart_data'])
        chart = alt.Chart(chart_df).mark_area(
            opacity=0.6,
            color=hex_color
        ).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y('value:Q', title='Signal Strength')
        ).properties(
            height=300,
            background='rgba(0,0,0,0)'
        ).configure_view(
            strokeOpacity=0
        ).configure_axis(
            labelColor='#556677',
            titleColor='#445566',
            gridColor='rgba(255,255,255,0.04)'
        )
        
        st.altair_chart(chart, use_container_width=True)

    st.markdown(
        f'<div class="titan-foot">Macro HUD V400 (DEMO) &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1.2 — THERMOMETER
# ══════════════════════════════════════════════════════════════════════════════
def render_1_2_thermometer():
    """🌡️ 多空溫度計"""
    tactical_toast("多空溫度計啟動 / Thermometer Loading", "processing")
    
    eng = MockMacroRiskEngine()
    try:
        data = eng.compute_temperature()
    except Exception as e:
        tactical_toast(f"溫度計算失敗 / Calculation Failed: {str(e)}", "error")
        return

    temp = data.get('temp_pct', 0)
    color = "#FF6B6B" if temp > 70 else "#FFD700" if temp > 30 else "#00F5FF"
    rgb = "255,107,107" if temp > 70 else "255,215,0" if temp > 30 else "0,245,255"

    st.markdown(f"""
<div class="hero-container" style="--hero-glow:rgba({rgb},0.15);
     --hero-color:{color};--hero-rgb:{rgb};">
  <div class="hero-val">{temp:.1f}°C</div>
  <div class="hero-lbl">MARKET TEMPERATURE</div>
  <div class="hero-badge">
    <span class="hero-pulse"></span>
    {'過熱 OVERHEATED' if temp > 70 else '正常 NORMAL' if temp > 30 else '過冷 COLD'}
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="demo-warning">⚠️ DEMO 模式 - 使用模擬數據</div>', unsafe_allow_html=True)
    tactical_toast("溫度計算完成 / Temperature Ready", "success")

    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    
    analysis = f"""
【多空溫度計 AI 研判】

當前市場體溫：{temp:.1f}°C

溫度解讀：
- 當前有 {temp:.1f}% 的高價權值股站上 87MA
- {'市場處於過熱狀態，建議警惕回調風險' if temp > 70 else '市場溫度適中，可維持正常操作' if temp > 30 else '市場偏冷，適合尋找低接機會'}

歷史回測：過去 12 個月中，溫度超過 75°C 後平均 {data.get('avg_days_to_cool', 7)} 個交易日開始降溫。
"""
    
    if 'thermo_streamed' not in st.session_state:
        st.write_stream(_stream_fast(analysis))
        st.session_state['thermo_streamed'] = True
    else:
        st.markdown(analysis)
    
    st.markdown('</div>', unsafe_allow_html=True)

    if 'history' in data:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['history']['dates'],
            y=data['history']['temps'],
            mode='lines+markers',
            line=dict(color=color, width=3),
            marker=dict(size=8, color=color),
            name='Temperature'
        ))
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='JetBrains Mono', color='#556677'),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.04)', title='Temperature (%)'),
            height=400,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f'<div class="titan-foot">Thermometer V400 (DEMO) &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1.3 — PR90
# ══════════════════════════════════════════════════════════════════════════════
def render_1_3_pr90():
    """📊 籌碼分佈"""
    tactical_toast("籌碼分析引擎啟動 / Chip Analysis Loading", "processing")
    
    eng = MockMacroRiskEngine()
    try:
        data = eng.compute_pr90()
    except Exception as e:
        tactical_toast(f"籌碼分析失敗 / Analysis Failed: {str(e)}", "error")
        return

    pr90 = data.get('pr90_pct', 0)
    color = "#00FF7F" if pr90 > 15 else "#FFD700" if pr90 > 10 else "#FF6B6B"
    rgb = "0,255,127" if pr90 > 15 else "255,215,0" if pr90 > 10 else "255,107,107"

    st.markdown(f"""
<div class="hero-container" style="--hero-glow:rgba({rgb},0.15);
     --hero-color:{color};--hero-rgb:{rgb};">
  <div class="hero-val">{pr90:.1f}%</div>
  <div class="hero-lbl">PR90 CONCENTRATION</div>
  <div class="hero-badge">
    <span class="hero-pulse"></span>
    {'主力控盤 CONTROLLED' if pr90 > 15 else '正常分布 NORMAL' if pr90 > 10 else '分散籌碼 DISPERSED'}
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="demo-warning">⚠️ DEMO 模式 - 使用模擬數據</div>', unsafe_allow_html=True)
    tactical_toast("籌碼分析完成 / Chip Analysis Ready", "success")

    if 'top_stocks' in data and len(data['top_stocks']) > 0:
        st.markdown('<div class="rank-grid">', unsafe_allow_html=True)
        
        for i, stock in enumerate(data['top_stocks'][:10], 1):
            card_html = create_rank_card(
                rank=i,
                title=f"{stock.get('symbol', 'N/A')} {stock.get('name', '')}",
                value=f"{stock.get('pr90', 0):.1f}%",
                meta_items=[
                    f"價格: {stock.get('price', 0):.2f}",
                    f"成交量: {stock.get('volume', 0):,.0f}K"
                ]
            )
            st.markdown(card_html, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📊 暫無籌碼數據")

    st.markdown('<div class="terminal-box">', unsafe_allow_html=True)
    analysis = f"""
【籌碼分佈 AI 解讀】

PR90 指標：{pr90:.1f}%

判讀：{'前 10% 股民控制超過 15% 的股票，顯示主力高度控盤' if pr90 > 15 else '籌碼分布相對均勻，散戶參與度高' if pr90 <= 10 else '籌碼集中度中等'}

策略建議：{'關注主力動向，順勢而為' if pr90 > 15 else '市場分散，可自主選股' if pr90 <= 10 else '保持觀察，謹慎操作'}
"""
    
    if 'pr90_streamed' not in st.session_state:
        st.write_stream(_stream_fast(analysis))
        st.session_state['pr90_streamed'] = True
    else:
        st.markdown(analysis)
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="titan-foot">PR90 Analysis V400 (DEMO) &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1.4-1.7 (簡化版本，遵循相同模式)
# ══════════════════════════════════════════════════════════════════════════════
def render_1_4_heatmap():
    st.info("🗺️ 族群熱度圖 (DEMO) - 模擬數據展示中")


def render_1_5_turnover():
    st.info("💹 成交重心 (DEMO) - 模擬數據展示中")


def render_1_6_trend_radar():
    st.info("👑 趨勢雷達 (DEMO) - 模擬數據展示中")


def render_1_7_predator():
    st.info("🎯 台指獵殺 (DEMO) - 模擬數據展示中")


# ══════════════════════════════════════════════════════════════════════════════
#  RENDER MAP
# ══════════════════════════════════════════════════════════════════════════════
RENDER_MAP = {
    "1.1": render_1_1_hud,
    "1.2": render_1_2_thermometer,
    "1.3": render_1_3_pr90,
    "1.4": render_1_4_heatmap,
    "1.5": render_1_5_turnover,
    "1.6": render_1_6_trend_radar,
    "1.7": render_1_7_predator,
}

_POSTER_ACCENT = {
    "1.1": "#00F5FF",
    "1.2": "#FF6B6B",
    "1.3": "#FFD700",
    "1.4": "#00FF7F",
    "1.5": "#FFA07A",
    "1.6": "#9370DB",
    "1.7": "#FF3131",
}


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════
def render():
    """Tab 1 — God-Tier Cinematic Trading Experience (V400 FIXED)"""
    _inject_css()

    if not st.session_state.get('tab1_guided', False):
        _show_tactical_guide()
        return

    if 'tab1_active' not in st.session_state:
        st.session_state.tab1_active = "1.1"
    active = st.session_state.tab1_active

    st.markdown(f"""
<div style="display:flex;align-items:baseline;justify-content:space-between;
            padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,0.06);
            margin-bottom:22px;">
  <div>
    <span style="font-family:'Bebas Neue',sans-serif;font-size:26px;
                 color:#FFD700;letter-spacing:3px;
                 text-shadow:0 0 22px rgba(255,215,0,0.4);">
      🛡️ 宏觀風控指揮中心
    </span>
    <span style="font-family:'JetBrains Mono',monospace;font-size:9px;
                 color:rgba(255,215,0,0.3);letter-spacing:3px;
                 border:1px solid rgba(255,215,0,0.12);border-radius:20px;
                 padding:3px 13px;margin-left:14px;background:rgba(255,215,0,0.025);">
      TITAN OS V400 — DEMO MODE
    </span>
  </div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
              color:rgba(200,215,230,0.25);letter-spacing:2px;text-align:right;line-height:1.7;">
    {datetime.now().strftime('%H:%M:%S')}<br>{datetime.now().strftime('%Y · %m · %d')}
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div class="nav-deck-frame"><div class="nav-deck-label">⬡ module select — poster rail</div>', unsafe_allow_html=True)

    cols = st.columns(7)
    for col, (code, emoji, label_zh, label_en) in zip(cols, SUB_MODULES):
        accent  = _POSTER_ACCENT.get(code, "#FFD700")
        is_active = (active == code)
        act_cls   = "active" if is_active else ""

        with col:
            if st.button(f"{emoji} {label_zh}", key=f"nav_{code}",
                         use_container_width=True):
                st.session_state.tab1_active = code
                tactical_toast(f"切換至 {label_zh} / Switching to {label_en}", "info", icon="🎯")
                st.rerun()

            st.markdown(f"""
<div class="poster-card {act_cls}" style="--poster-accent:{accent};margin-top:-54px;
     pointer-events:none;z-index:0;position:relative;">
  <div class="poster-icon">{emoji}</div>
  <div class="poster-code">{code}</div>
  <div class="poster-text">{label_zh}</div>
  <div class="poster-tag">{label_en}</div>
</div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="content-frame">', unsafe_allow_html=True)
    fn = RENDER_MAP.get(active)
    if fn:
        try:
            fn()
        except Exception as exc:
            import traceback
            tactical_toast(f"模組 {active} 渲染失敗 / Module Error: {str(exc)}", "error")
            with st.expander("🔍 Debug Trace"):
                st.code(traceback.format_exc())
    st.markdown('</div>', unsafe_allow_html=True)
