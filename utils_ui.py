# utils_ui.py
# Titan SOP V100.0 - UI Utilities & Styling

import streamlit as st
import requests
import json
from typing import Optional, Tuple

# ==========================================
# [1] LOTTIE 載入器（V82 相容）
# ==========================================

def load_lottie_url(url: str) -> Optional[dict]:
    if not url:
        return None
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

def get_lottie_animation(key: str) -> str:
    animations = {
        "sunrise": "https://lottie.host/801314d5-8930-466d-979c-7e930f6b489d/P9R9N6uO8c.json",
        "loading": "https://lottie.host/88168270-3490-4e7a-976c-37e0e7135e98/mK8eY2f1W0.json",
        "matrix":  "https://lottie.host/e0586e96-6e3e-4363-9524-7629c5e3f7f8/Matrix.json"
    }
    return animations.get(key, "")

# ==========================================
# [2] 桌面版 CSS (Bloomberg Terminal 風格)
# ==========================================

DESKTOP_CSS = """
<style>
    .stApp {
        background-color: #1a1a1a;
        color: #FAFAFA;
    }
    [data-testid="stSidebar"] {
        background-color: #2a2a2a;
        border-right: 2px solid #444;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #00FF00;
    }
    div.stButton > button {
        background-color: #2a2a2a;
        color: #FFFFFF;
        border: 2px solid #444;
        border-radius: 10px;
        padding: 20px;
        width: 100%;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 0 5px rgba(0, 255, 0, 0);
    }
    div.stButton > button:hover {
        border-color: #00FF00;
        color: #00FF00;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
        transform: translateY(-2px);
    }
    .dataframe { font-size: 14px; border-collapse: collapse; }
    .dataframe th {
        background-color: #3a3a3a !important;
        color: #00FF00 !important;
        font-weight: bold; padding: 12px;
        border-bottom: 2px solid #00FF00;
    }
    .dataframe td { padding: 10px; border-bottom: 1px solid #3a3a3a; color: #FAFAFA; }
    .dataframe tr:hover { background-color: #2a2a2a; }
    [data-testid="stMetricValue"] {
        font-size: 36px; font-weight: bold; color: #00FF00;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px; color: #AAAAAA; text-transform: uppercase;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background-color: #2a2a2a;
        padding: 10px; border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #3a3a3a; color: #FAFAFA;
        border-radius: 8px; padding: 10px 20px;
        font-weight: 600; border: 1px solid #444;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00FF00; color: #000000; border: none;
    }
    .stTextInput > div > div > input {
        background-color: #2a2a2a; color: #FFFFFF;
        border: 1px solid #444; border-radius: 5px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00FF00;
        box-shadow: 0 0 5px rgba(0, 255, 0, 0.5);
    }
    .stSelectbox > div > div { background-color: #2a2a2a; color: #FFFFFF; }
    .stSlider > div > div > div > div { background-color: #00FF00; }
    .stProgress > div > div > div > div { background-color: #00FF00; }
    .streamlit-expanderHeader {
        background-color: #2a2a2a; color: #00FF00; border-radius: 5px;
    }
    .stFileUploader > div {
        background-color: #2a2a2a;
        border: 2px dashed #444; border-radius: 10px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""

# ==========================================
# [3] 移動版 CSS (Netflix/Robinhood 風格)
# ==========================================

MOBILE_CSS = """
<style>
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="stHeader"]  { display: none !important; }
    .mobile-nav {
        position: fixed; bottom: 0; left: 0; right: 0;
        background: linear-gradient(180deg, #1A1A1A 0%, #000000 100%);
        border-top: 1px solid #333333;
        padding: 12px 0; z-index: 1000;
        display: flex; justify-content: space-around;
        box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.5);
    }
    .nav-item { display: flex; flex-direction: column; align-items: center; color: #888888; font-size: 12px; }
    .nav-item.active { color: #00FF00; transform: scale(1.1); }
    .nav-icon { font-size: 24px; margin-bottom: 4px; }
    .stButton > button {
        width: 100% !important;
        min-height: 60px !important;
        background: linear-gradient(135deg, #00FF00 0%, #00CC00 100%);
        color: #000000; font-size: 20px; font-weight: bold;
        border-radius: 16px; border: none;
        box-shadow: 0 4px 12px rgba(0, 255, 0, 0.3);
        transition: all 0.3s;
    }
    .stButton > button:active { transform: scale(0.95); }
    .mobile-card {
        background: linear-gradient(135deg, #1A1A1A 0%, #2A2A2A 100%);
        border-radius: 20px; padding: 24px; margin: 16px 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        border: 1px solid #333333;
    }
    .hud-price {
        font-size: 72px; font-weight: 900; color: #00FF00;
        text-align: center;
        text-shadow: 0 0 20px rgba(0, 255, 0, 0.5); margin: 20px 0;
    }
    .hud-angle { font-size: 48px; font-weight: bold; text-align: center; margin: 16px 0; }
    .angle-up  { color: #00FF7F; text-shadow: 0 0 15px rgba(0, 255, 127, 0.5); }
    .angle-down{ color: #FF4500; text-shadow: 0 0 15px rgba(255, 69, 0, 0.5); }
    .chat-bubble { background-color: #2A2A2A; border-radius: 18px; padding: 16px 20px; margin: 12px 0; }
    .chat-bubble.quant   { background: linear-gradient(135deg, #1E3A5F 0%, #2A5280 100%); }
    .chat-bubble.burry   { background: linear-gradient(135deg, #5F1E1E 0%, #802A2A 100%); }
    .chat-bubble.commander { background: linear-gradient(135deg, #5F4E1E 0%, #806A2A 100%); }
    .tiktok-card {
        background: linear-gradient(135deg, #1A1A1A 0%, #2A2A2A 100%);
        border-radius: 24px; padding: 32px 24px; margin: 20px 0;
        min-height: 400px; display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
    }
    .tiktok-icon { font-size: 80px; margin-bottom: 24px; }
    .tiktok-title { font-size: 28px; font-weight: bold; color: #00FF00; text-align: center; margin-bottom: 16px; }
    .tiktok-content { font-size: 18px; line-height: 1.6; text-align: center; color: #CCCCCC; }
    .stTextInput > div > div > input {
        background-color: #1A1A1A; color: #FFFFFF;
        border: 2px solid #333333; border-radius: 16px;
        padding: 16px 20px; font-size: 18px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00FF00; box-shadow: 0 0 12px rgba(0, 255, 0, 0.3);
    }
    [data-testid="stMetricValue"] {
        font-size: 48px; font-weight: 900; color: #00FF00;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
    [data-testid="stMetricLabel"] {
        font-size: 16px; color: #AAAAAA;
        text-transform: uppercase; letter-spacing: 1px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .main .block-container { padding-bottom: 100px; }
</style>
"""

HOMEPAGE_CSS = """
<style>
    .stApp { background-color: #1a1a1a; }
    div.stButton > button {
        background-color: #2a2a2a; color: #FFFFFF;
        border: 2px solid #444; border-radius: 10px;
        padding: 20px; width: 100%; height: 150px;
        font-size: 26px; font-weight: bold;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 0 5px rgba(0, 255, 0, 0); line-height: 1.3;
    }
    div.stButton > button:hover {
        border-color: #00FF00; color: #00FF00;
        box-shadow: 0 0 15px rgba(0, 255, 0, 0.7);
    }
</style>
"""

# ==========================================
# [4] CSS 注入
# ==========================================

def inject_css(mode: str = "desktop"):
    if mode == "mobile":
        st.markdown(MOBILE_CSS, unsafe_allow_html=True)
    elif mode == "homepage":
        st.markdown(HOMEPAGE_CSS, unsafe_allow_html=True)
    else:
        st.markdown(DESKTOP_CSS, unsafe_allow_html=True)

# ==========================================
# [5] 評級系統
# ==========================================

RATING_COLORS = {
    "SSS": "#FFD700", "AAA": "#FF4500", "Phoenix": "#FF6347",
    "Launchpad": "#32CD32", "AA+": "#FFA500", "AA": "#FFD700",
    "AA-": "#ADFF2F", "A+": "#7FFF00", "A": "#98FB98",
    "BBB+": "#F0E68C", "BBB": "#D3D3D3", "BBB-": "#DDA0DD",
    "Divergence": "#FF1493", "BB+": "#FFA07A", "BB": "#FF6347",
    "BB-": "#DC143C", "B+": "#8B0000", "B": "#800000",
    "C": "#4B0082", "D": "#000000", "Reversal": "#00CED1", "N/A": "#808080",
}

def get_rating_color(rating_str: str) -> str:
    if not isinstance(rating_str, str):
        return "#808080"
    level = rating_str.split(" ")[0]
    return RATING_COLORS.get(level, "#808080")

def format_rating_badge(rating_str: str, rating_name: str = "", color: str = None) -> str:
    if color is None:
        color = get_rating_color(rating_str)
    display = f"{rating_str}: {rating_name}" if rating_name else rating_str
    return (f'<div style="display:inline-block; background-color:{color}; color:#000000; '
            f'padding:8px 16px; border-radius:8px; font-weight:bold; font-size:18px; '
            f'box-shadow:0 2px 4px rgba(0,0,0,0.2); margin:4px;">{display}</div>')

# ==========================================
# [6] 標題 & 標牌元件
# ==========================================

def create_glowing_title(text: str, color: str = "#FFD700") -> str:
    """金色發光標題（你的風格）"""
    return f"""
    <div style="text-align:center; margin-bottom:30px; animation:fadeIn 1.5s ease-in;">
        <h1 style="font-family:'Roboto',sans-serif; color:{color}; font-size:3em;
            text-shadow:0 0 10px rgba(255,215,0,0.7), 0 0 20px rgba(255,215,0,0.5);
            margin:0; font-weight:700; letter-spacing:2px;">{text}</h1>
        <div style="height:2px; background:linear-gradient(90deg,transparent,{color},transparent);
            margin-top:10px; width:100%;"></div>
    </div>
    """

def render_glowing_header(text: str, color: str = "#FFD700") -> None:
    st.markdown(create_glowing_title(text, color), unsafe_allow_html=True)

def titan_hero_banner(text: str = "🏛️ Titan SOP V100") -> None:
    st.markdown(
        f'<h1 style="text-align:center; color:#FFD700; font-size:2.5em; letter-spacing:4px; '
        f'text-shadow:0 0 10px rgba(255,215,0,0.7), 0 0 20px rgba(255,215,0,0.5); '
        f'margin:16px 0;">{text}</h1>',
        unsafe_allow_html=True
    )

def render_signal_badge(signal: str) -> None:
    colors = {
        "GREEN_LIGHT":  ("#00FF00", "🟢 綠燈：積極進攻"),
        "YELLOW_LIGHT": ("#FFD700", "🟡 黃燈：區間操作"),
        "RED_LIGHT":    ("#FF4444", "🔴 紅燈：現金為王"),
    }
    color, label = colors.get(signal, ("#888", signal))
    st.markdown(
        f'<div style="background:#2a2a2a; border:2px solid {color}; border-radius:8px; '
        f'padding:12px; text-align:center; font-size:18px; font-weight:bold; '
        f'color:{color};">{label}</div>', unsafe_allow_html=True)

# ==========================================
# [7] 角度卡片
# ==========================================

def angle_to_color(angle: float) -> str:
    if angle > 30:  return "#00FF00"
    if angle > 0:   return "#ADFF2F"
    if angle > -30: return "#FFD700"
    return "#FF4500"

def render_angle_card(period: str, angle: float, r2: float) -> None:
    color = angle_to_color(angle)
    st.markdown(f"""
<div style="background:#2a2a2a; padding:12px; border-radius:8px;
     border:2px solid {color}; text-align:center; margin-bottom:8px;">
  <h4 style="color:{color}; margin:0; font-size:14px;">{period}</h4>
  <h1 style="color:white; margin:4px 0; font-size:32px;">{angle}°</h1>
  <p style="color:#888; margin:0; font-size:11px;">R² = {r2}</p>
</div>""", unsafe_allow_html=True)

def render_rating_card(level: str, name: str, desc: str, color: str) -> None:
    st.markdown(f"""
<div style="background:linear-gradient(135deg,{color} 0%,#1a1a1a 100%);
     color:white; padding:24px; border-radius:12px; text-align:center;
     box-shadow:0 8px 32px rgba(0,0,0,0.5); margin:8px 0;">
  <h1 style="margin:0; font-size:42px;">{level}</h1>
  <h2 style="margin:8px 0; font-size:24px;">{name}</h2>
  <p style="margin:4px 0; font-size:16px; opacity:0.9;">{desc}</p>
</div>""", unsafe_allow_html=True)

# ==========================================
# [8] CB 卡片
# ==========================================

def style_cb_table(df):
    """DataFrame 格式化（無 type hint 避免 pandas 版本問題）"""
    fmt = {}
    if 'close'           in df.columns: fmt['close']           = '{:.1f}'
    if 'premium_pct'     in df.columns: fmt['premium_pct']     = '{:+.1f}%'
    if 'converted_ratio' in df.columns: fmt['converted_ratio'] = '{:.1f}%'
    if 'bias_pct'        in df.columns: fmt['bias_pct']        = '{:+.1f}%'
    if 'score'           in df.columns: fmt['score']           = '{:.0f}'
    try:
        return df.style.format(fmt)
    except Exception:
        return df.style

def render_cb_mini_card(name: str, code: str, price: float, trend: str, score: int) -> None:
    trend_color = "#00FF00" if "多頭" in trend else "#FF4500"
    score_color = "#00FF00" if score >= 70 else ("#FFD700" if score >= 40 else "#FF4500")
    st.markdown(f"""
<div style="background:#2a2a2a; border:1px solid #444; border-radius:8px;
     padding:10px 14px; margin:4px 0; display:flex; justify-content:space-between;">
  <div>
    <span style="color:#FFD700; font-weight:bold;">{name}</span>
    <span style="color:#666; font-size:12px;"> ({code})</span><br/>
    <span style="color:#aaa; font-size:13px;">市價：{price:.1f} 元</span>
  </div>
  <div style="text-align:right;">
    <span style="color:{trend_color}; font-size:13px;">{trend}</span><br/>
    <span style="color:{score_color}; font-weight:bold; font-size:18px;">{score}</span>
    <span style="color:#666; font-size:11px;"> 分</span>
  </div>
</div>""", unsafe_allow_html=True)

def format_pct_change(val: float) -> str:
    return f"+{val:.2f}%" if val > 0 else f"{val:.2f}%"

# ==========================================
# [9] 移動版元件
# ==========================================

def create_hud_display(price: float, angle: float, g_force: float):
    angle_class = "angle-up" if angle > 0 else "angle-down"
    arrow = "↗️" if angle > 0 else "↘️"
    st.markdown(f"""
    <div class="mobile-card">
        <div class="hud-price">${price:.2f}</div>
        <div class="hud-angle {angle_class}">{arrow} {angle:.1f}°</div>
        <div style="text-align:center; font-size:24px; color:#AAA; margin-top:16px;">
            ⚡ G-Force: {g_force:+.1f}°
        </div>
    </div>""", unsafe_allow_html=True)

def create_chat_bubble(role: str, message: str):
    role_class = {"quant": "quant", "burry": "burry", "commander": "commander"}.get(role.lower(), "quant")
    role_emoji = {"quant": "🤖", "burry": "🐻", "commander": "⚔️"}.get(role.lower(), "💬")
    st.markdown(f"""
    <div class="chat-bubble {role_class}">
        <div style="font-weight:bold; margin-bottom:8px; color:#FFD700;">{role_emoji} {role}</div>
        <div style="line-height:1.5;">{message}</div>
    </div>""", unsafe_allow_html=True)

def create_tiktok_card(icon: str, title: str, content: str):
    st.markdown(f"""
    <div class="tiktok-card">
        <div class="tiktok-icon">{icon}</div>
        <div class="tiktok-title">{title}</div>
        <div class="tiktok-content">{content}</div>
    </div>""", unsafe_allow_html=True)

def create_swipe_buttons() -> Tuple[bool, bool]:
    col1, col2 = st.columns(2)
    with col1:
        p = st.button("❌ 跳過", key="btn_pass", use_container_width=True)
    with col2:
        l = st.button("❤️ 鎖定", key="btn_lock", use_container_width=True, type="primary")
    return p, l

def show_loading_skeleton():
    st.markdown("""
    <div style='animation:pulse 1.5s infinite;
        background:linear-gradient(90deg,#1A1A1A 25%,#2A2A2A 50%,#1A1A1A 75%);
        background-size:200% 100%; height:60px; border-radius:12px; margin:8px 0;'>
    </div>
    <style>@keyframes pulse{0%{background-position:200% 0}100%{background-position:-200% 0}}</style>
    """, unsafe_allow_html=True)

# ==========================================
# [10] 側邊欄工具（V82 相容）
# ==========================================

def render_sidebar_utilities(kb=None, df=None):
    try:
        from data_engine import load_cb_data_from_upload
    except ImportError:
        load_cb_data_from_upload = None
    import pandas as pd
    with st.sidebar:
        st.markdown(create_glowing_title("⚙️ Titan V100"), unsafe_allow_html=True)
        st.header("📂 CB 資料上傳")
        f = st.file_uploader("CB 清單 (Excel/CSV)", type=['csv','xlsx'], key="sidebar_cb_upload")
        if f and load_cb_data_from_upload:
            with st.spinner("載入中…"):
                df2 = load_cb_data_from_upload(f)
                if df2 is not None and not df2.empty:
                    st.session_state.df = df2
                    st.success(f"✅ {len(df2)} 筆 CB")
        df_cur = st.session_state.get('df', pd.DataFrame())
        if not df_cur.empty:
            st.caption(f"目前：{len(df_cur)} 筆")
        st.divider()
        st.header("🔑 AI 功能")
        key = st.text_input("Gemini API Key", type="password",
                            value=st.session_state.get('api_key',''), key="sidebar_api_key")
        st.session_state.api_key = key
        st.divider()
        st.header("🕵️ 情報上傳")
        intel = st.file_uploader("情報文件 (PDF/TXT)", type=['pdf','txt'],
                                  accept_multiple_files=True, key="sidebar_intel")
        st.session_state.intel_files = intel or []
        st.divider()
        if st.button("🗑️ 清除快取", use_container_width=True, key="sidebar_clear_cache"):
            st.cache_data.clear(); st.cache_resource.clear()
            st.toast("快取已清除 ✅")
        st.caption("Titan SOP V100.0")