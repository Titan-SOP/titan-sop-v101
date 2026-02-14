# utils_ui.py
# Titan SOP V100.0 — UI Utilities
# 包含：CSS 注入、發光標題、信評徽章、顏色映射、共用卡片元件

import streamlit as st
import pandas as pd


# ═══════════════════════════════════════════════════════════════
#  Bloomberg Terminal Dark Theme CSS
# ═══════════════════════════════════════════════════════════════

_DESKTOP_CSS = """
<style>
/* ── 全域背景 ── */
.stApp { background-color: #0a0a0a; color: #FFFFFF; }

/* ── 側邊欄 ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111111 0%, #0d0d0d 100%);
    border-right: 1px solid #222;
}

/* ── 頂部標題列 ── */
[data-testid="stHeader"] { background-color: #0a0a0a; }

/* ── Metric 卡片 ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2a2a4a;
    border-radius: 10px;
    padding: 12px;
}
[data-testid="metric-container"] label { color: #888 !important; font-size: 12px; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00FF00 !important;
    font-size: 1.4em;
    font-weight: bold;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background-color: #111;
    border-bottom: 2px solid #00FF00;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #1a1a1a;
    color: #888;
    border-radius: 6px 6px 0 0;
    padding: 8px 16px;
    font-size: 13px;
}
.stTabs [aria-selected="true"] {
    background-color: #00FF00 !important;
    color: #000 !important;
    font-weight: bold;
}

/* ── 按鈕 ── */
.stButton > button {
    background: linear-gradient(135deg, #1a3a1a 0%, #0d2a0d 100%);
    color: #00FF00;
    border: 1px solid #00FF00;
    border-radius: 6px;
    font-weight: bold;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    background: #00FF00 !important;
    color: #000 !important;
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
}

/* ── 主按鈕 ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #003300 0%, #006600 100%);
    color: #00FF00;
    border: 2px solid #00FF00;
    font-size: 15px;
}

/* ── 輸入框 ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #1a1a1a !important;
    color: #FFFFFF !important;
    border: 1px solid #333 !important;
    border-radius: 6px;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #00FF00 !important;
    box-shadow: 0 0 8px rgba(0, 255, 0, 0.3) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #111;
    border: 1px solid #222;
    border-radius: 8px;
    margin-bottom: 8px;
}
[data-testid="stExpander"] summary:hover { background-color: #1a1a1a; }

/* ── DataFrame / 表格 ── */
.dataframe { font-size: 13px; }
thead tr th { background-color: #1a1a1a !important; color: #FFD700 !important; }
tbody tr:nth-child(even) td { background-color: #0f0f0f !important; }
tbody tr:hover td { background-color: #1a2a1a !important; }

/* ── Divider ── */
hr { border-color: #222 !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
    background-color: #1a1a1a !important;
    color: #FFF !important;
    border: 1px solid #333 !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div { background-color: #00FF00 !important; }

/* ── Code blocks ── */
code { background-color: #1a1a1a; color: #00FF00; border-radius: 4px; padding: 2px 6px; }

/* ── 隱藏 Streamlit 品牌 ── */
#MainMenu, footer { visibility: hidden; }

/* ── Scrollbar ── */
::-webkit-scrollbar       { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0a; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00FF00; }
</style>
"""

_MOBILE_CSS = """
<style>
.stApp { background-color: #0d0d0d; }
[data-testid="stSidebar"] { background: #111; border-right: 1px solid #222; }
[data-testid="metric-container"] {
    background: #1a1a2e; border: 1px solid #2a2a4a;
    border-radius: 8px; padding: 8px;
}
.stButton > button { min-height: 48px; font-size: 15px; border-radius: 10px; }
.stTabs [data-baseweb="tab"] { font-size: 12px; padding: 6px 10px; }
.dataframe td, .dataframe th { font-size: 12px !important; }
#MainMenu, footer, header { visibility: hidden; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #333; border-radius: 2px; }
</style>
"""


def inject_css(mode: str = "desktop"):
    """注入對應模式的 CSS。mode: 'desktop' | 'mobile'"""
    css = _DESKTOP_CSS if mode == "desktop" else _MOBILE_CSS
    st.markdown(css, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  發光標題
# ═══════════════════════════════════════════════════════════════

def create_glowing_title(text: str, color: str = "#00FF00") -> str:
    """生成發光標題 HTML 字串"""
    return f"""
<h2 style="color:{color}; text-shadow: 0 0 10px {color}, 0 0 20px {color};
   text-align:center; font-weight:bold; letter-spacing:2px; margin:8px 0;">
{text}
</h2>
"""


def titan_hero_banner(text: str = "🏛️ Titan SOP V100") -> None:
    """渲染主標題橫幅"""
    st.markdown(
        f'<h1 style="text-align:center; color:white; '
        f'text-shadow: 0 0 10px #00FF00, 0 0 20px #00FF00, 0 0 40px #00FF00; '
        f'font-size:2.2em; letter-spacing:4px; margin:16px 0;">{text}</h1>',
        unsafe_allow_html=True
    )


# ═══════════════════════════════════════════════════════════════
#  信評工具
# ═══════════════════════════════════════════════════════════════

def get_rating_color(level: str) -> str:
    """根據信評等級回傳對應十六進位顏色"""
    MAP = {
        "SSS": "#FFD700", "AAA": "#FF4500", "Phoenix": "#FF6347",
        "Launchpad": "#32CD32", "AA+": "#FFA500", "AA": "#FFD700",
        "AA-": "#ADFF2F", "A+": "#7FFF00", "A": "#98FB98",
        "BBB+": "#F0E68C", "BBB": "#D3D3D3", "BBB-": "#DDA0DD",
        "Divergence": "#FF1493", "BB+": "#FFA07A", "BB": "#FF6347",
        "BB-": "#DC143C", "B+": "#8B0000", "B": "#800000",
        "C": "#4B0082", "D": "#000000", "Reversal": "#00CED1",
    }
    return MAP.get(level, "#808080")


def render_rating_card(level: str, name: str, desc: str, color: str) -> None:
    """渲染信評卡片 HTML"""
    st.markdown(f"""
<div style="background:linear-gradient(135deg,{color} 0%,#000 100%);
     color:white; padding:24px; border-radius:12px; text-align:center;
     box-shadow:0 8px 32px rgba(0,0,0,0.5); margin:8px 0;">
  <h1 style="margin:0; font-size:42px; text-shadow:0 0 10px rgba(255,255,255,0.5);">{level}</h1>
  <h2 style="margin:8px 0; font-size:24px;">{name}</h2>
  <p style="margin:4px 0; font-size:16px; opacity:0.9;">{desc}</p>
</div>
""", unsafe_allow_html=True)


def format_rating_badge(level: str, name: str) -> str:
    """生成單行信評徽章 HTML（用於表格內嵌）"""
    color = get_rating_color(level)
    return (f'<span style="background:{color}; color:#000; font-weight:bold; '
            f'padding:2px 8px; border-radius:4px; font-size:12px;">{level}</span> {name}')


# ═══════════════════════════════════════════════════════════════
#  角度顏色映射
# ═══════════════════════════════════════════════════════════════

def angle_to_color(angle: float) -> str:
    """將幾何角度轉為顏色"""
    if angle > 30:   return "#00FF00"
    if angle > 0:    return "#ADFF2F"
    if angle > -30:  return "#FFD700"
    return "#FF4500"


def render_angle_card(period: str, angle: float, r2: float) -> None:
    """渲染單個幾何角度卡片"""
    color = angle_to_color(angle)
    st.markdown(f"""
<div style="background:linear-gradient(135deg,#2a2a2a 0%,#1a1a1a 100%);
     padding:12px; border-radius:8px; border:2px solid {color};
     text-align:center; margin-bottom:8px;">
  <h4 style="color:{color}; margin:0; font-size:14px;">{period}</h4>
  <h1 style="color:white; margin:4px 0; font-size:32px;">{angle}°</h1>
  <p style="color:#888; margin:0; font-size:11px;">R² = {r2}</p>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  通用 CB 卡片
# ═══════════════════════════════════════════════════════════════

def render_cb_mini_card(name: str, code: str, price: float,
                        trend: str, score: int) -> None:
    """渲染精簡版 CB 資訊卡片"""
    trend_color = "#00FF00" if "多頭" in trend else "#FF4500"
    score_color = "#00FF00" if score >= 70 else ("#FFD700" if score >= 40 else "#FF4500")
    st.markdown(f"""
<div style="background:#1a1a2e; border:1px solid #2a2a4a; border-radius:8px;
     padding:10px 14px; margin:4px 0; display:flex; justify-content:space-between; align-items:center;">
  <div>
    <span style="color:#FFD700; font-weight:bold; font-size:15px;">{name}</span>
    <span style="color:#666; font-size:12px; margin-left:8px;">({code})</span><br/>
    <span style="color:#888; font-size:13px;">市價：{price:.1f} 元</span>
  </div>
  <div style="text-align:right;">
    <span style="color:{trend_color}; font-size:13px;">{trend}</span><br/>
    <span style="color:{score_color}; font-weight:bold; font-size:18px;">{score}</span>
    <span style="color:#666; font-size:11px;"> 分</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  DataFrame 格式化輔助
# ═══════════════════════════════════════════════════════════════

def style_cb_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """為 CB 列表 DataFrame 套用標準格式"""
    fmt = {}
    if 'close' in df.columns:         fmt['close']          = '{:.1f}'
    if 'premium_pct' in df.columns:   fmt['premium_pct']    = '{:+.1f}%'
    if 'converted_ratio' in df.columns:fmt['converted_ratio']= '{:.1f}%'
    if 'bias_pct' in df.columns:      fmt['bias_pct']       = '{:+.1f}%'
    if 'score' in df.columns:         fmt['score']          = '{:.0f}'
    try:
        return df.style.format(fmt)
    except Exception:
        return df.style


def format_pct_change(val: float) -> str:
    """格式化百分比變動，正數顯示 + 號"""
    if val > 0: return f"+{val:.2f}%"
    return f"{val:.2f}%"
