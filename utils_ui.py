# utils_ui.py
# Titan SOP V100.0 — UI Utilities
# 包含：CSS 注入、發光標題、信評徽章、顏色映射、共用卡片元件
# [V100 向下相容層]：保留 V82 舊版函式，避免 import crash

import streamlit as st
import pandas as pd


_DESKTOP_CSS = """
<style>
.stApp { background-color: #0a0a0a; color: #FFFFFF; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111111 0%, #0d0d0d 100%);
    border-right: 1px solid #222;
}
[data-testid="stHeader"] { background-color: #0a0a0a; }
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2a2a4a; border-radius: 10px; padding: 12px;
}
[data-testid="metric-container"] label { color: #888 !important; font-size: 12px; }
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00FF00 !important; font-size: 1.4em; font-weight: bold;
}
.stTabs [data-baseweb="tab-list"] {
    background-color: #111; border-bottom: 2px solid #00FF00; gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #1a1a1a; color: #888;
    border-radius: 6px 6px 0 0; padding: 8px 16px; font-size: 13px;
}
.stTabs [aria-selected="true"] {
    background-color: #00FF00 !important; color: #000 !important; font-weight: bold;
}
.stButton > button {
    background: linear-gradient(135deg, #1a3a1a 0%, #0d2a0d 100%);
    color: #00FF00; border: 1px solid #00FF00;
    border-radius: 6px; font-weight: bold; transition: all 0.2s ease;
}
.stButton > button:hover {
    background: #00FF00 !important; color: #000 !important;
    box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #003300 0%, #006600 100%);
    color: #00FF00; border: 2px solid #00FF00; font-size: 15px;
}
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #1a1a1a !important; color: #FFFFFF !important;
    border: 1px solid #333 !important; border-radius: 6px;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #00FF00 !important;
    box-shadow: 0 0 8px rgba(0, 255, 0, 0.3) !important;
}
[data-testid="stExpander"] {
    background: #111; border: 1px solid #222;
    border-radius: 8px; margin-bottom: 8px;
}
[data-testid="stExpander"] summary:hover { background-color: #1a1a1a; }
.dataframe { font-size: 13px; }
thead tr th { background-color: #1a1a1a !important; color: #FFD700 !important; }
tbody tr:nth-child(even) td { background-color: #0f0f0f !important; }
tbody tr:hover td { background-color: #1a2a1a !important; }
hr { border-color: #222 !important; }
.stSelectbox > div > div {
    background-color: #1a1a1a !important; color: #FFF !important;
    border: 1px solid #333 !important;
}
[data-testid="stProgressBar"] > div { background-color: #00FF00 !important; }
code { background-color: #1a1a1a; color: #00FF00; border-radius: 4px; padding: 2px 6px; }
#MainMenu, footer { visibility: hidden; }
::-webkit-scrollbar { width: 6px; }
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
    css = _DESKTOP_CSS if mode == "desktop" else _MOBILE_CSS
    st.markdown(css, unsafe_allow_html=True)


def create_glowing_title(text: str, color: str = "#00FF00") -> str:
    return f"""
<h2 style="color:{color}; text-shadow: 0 0 10px {color}, 0 0 20px {color};
   text-align:center; font-weight:bold; letter-spacing:2px; margin:8px 0;">
{text}
</h2>
"""


def titan_hero_banner(text: str = "🏛️ Titan SOP V100") -> None:
    st.markdown(
        f'<h1 style="text-align:center; color:white; '
        f'text-shadow: 0 0 10px #00FF00, 0 0 20px #00FF00, 0 0 40px #00FF00; '
        f'font-size:2.2em; letter-spacing:4px; margin:16px 0;">{text}</h1>',
        unsafe_allow_html=True
    )


def get_rating_color(level: str) -> str:
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
    color = get_rating_color(level)
    return (f'<span style="background:{color}; color:#000; font-weight:bold; '
            f'padding:2px 8px; border-radius:4px; font-size:12px;">{level}</span> {name}')


def angle_to_color(angle: float) -> str:
    if angle > 30:  return "#00FF00"
    if angle > 0:   return "#ADFF2F"
    if angle > -30: return "#FFD700"
    return "#FF4500"


def render_angle_card(period: str, angle: float, r2: float) -> None:
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


def render_cb_mini_card(name: str, code: str, price: float, trend: str, score: int) -> None:
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


def style_cb_table(df: pd.DataFrame):
    fmt = {}
    if 'close' in df.columns:          fmt['close']           = '{:.1f}'
    if 'premium_pct' in df.columns:    fmt['premium_pct']     = '{:+.1f}%'
    if 'converted_ratio' in df.columns: fmt['converted_ratio'] = '{:.1f}%'
    if 'bias_pct' in df.columns:       fmt['bias_pct']        = '{:+.1f}%'
    if 'score' in df.columns:          fmt['score']           = '{:.0f}'
    try:
        return df.style.format(fmt)
    except Exception:
        return df.style


def format_pct_change(val: float) -> str:
    if val > 0: return f"+{val:.2f}%"
    return f"{val:.2f}%"


# ═══════════════════════════════════════════════════════════════
#  V82 → V100 向下相容層
# ═══════════════════════════════════════════════════════════════

def render_sidebar_utilities(kb=None, df=None):
    """V82 相容：側邊欄工具區"""
    try:
        from data_engine import load_cb_data_from_upload
    except ImportError:
        load_cb_data_from_upload = None

    with st.sidebar:
        st.markdown(create_glowing_title("⚙️ Titan V100"), unsafe_allow_html=True)
        st.header("📂 CB 資料上傳")
        uploaded_file = st.file_uploader(
            "上傳 CB 清單 (Excel/CSV)", type=['csv', 'xlsx'], key="sidebar_cb_upload"
        )
        if uploaded_file and load_cb_data_from_upload:
            with st.spinner("載入中…"):
                df_loaded = load_cb_data_from_upload(uploaded_file)
                if df_loaded is not None and not df_loaded.empty:
                    st.session_state.df = df_loaded
                    st.success(f"✅ {len(df_loaded)} 筆 CB")
        df_cur = st.session_state.get('df', pd.DataFrame())
        if not df_cur.empty:
            st.caption(f"目前：{len(df_cur)} 筆")
        st.divider()
        st.header("🔑 AI 功能")
        key = st.text_input("Gemini API Key (選填)", type="password",
                            value=st.session_state.get('api_key', ''), key="sidebar_api_key")
        st.session_state.api_key = key
        st.divider()
        st.header("🕵️ 情報上傳")
        intel = st.file_uploader("情報文件 (PDF/TXT)", type=['pdf', 'txt'],
                                  accept_multiple_files=True, key="sidebar_intel")
        st.session_state.intel_files = intel or []
        st.divider()
        if st.button("🗑️ 清除快取", use_container_width=True, key="sidebar_clear_cache"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.toast("快取已清除 ✅")
        st.caption("Titan SOP V100.0")


def load_lottie_url(url: str):
    """V82 相容：不再使用 Lottie，回傳 None"""
    return None


def get_lottie_animation(name: str):
    """V82 相容：回傳 None"""
    return None


def render_glowing_header(text: str, color: str = "#00FF00") -> None:
    """V82 相容"""
    st.markdown(create_glowing_title(text, color), unsafe_allow_html=True)


def render_signal_badge(signal: str) -> None:
    """V82 相容：渲染多空燈號"""
    colors = {
        "GREEN_LIGHT":  ("#00FF00", "🟢 綠燈：積極進攻"),
        "YELLOW_LIGHT": ("#FFD700", "🟡 黃燈：區間操作"),
        "RED_LIGHT":    ("#FF4444", "🔴 紅燈：現金為王"),
    }
    color, label = colors.get(signal, ("#888", signal))
    st.markdown(
        f'<div style="background:#1a1a1a; border:2px solid {color}; '
        f'border-radius:8px; padding:12px; text-align:center; '
        f'font-size:18px; font-weight:bold; color:{color};">{label}</div>',
        unsafe_allow_html=True
    )