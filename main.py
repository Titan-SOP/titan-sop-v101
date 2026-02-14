# main.py
# Titan SOP V100.0 - Main Entry Point

import streamlit as st
import time

try:
    from utils_ui import load_lottie_url, inject_css, get_lottie_animation
except ImportError:
    st.error("❌ 無法導入 utils_ui 模組")
    st.stop()


def import_ui_modules():
    """
    多路徑嘗試 import，相容所有命名方式：
    ui_desktop/layout.py 或 layout.py
    ui_mobile/layout.py 或 ui_mobile/layout_mobile.py
    """
    import importlib

    # ── 桌面版 ──────────────────────────────────
    desktop_layout = None
    for path in ["ui_desktop.layout", "layout"]:
        try:
            desktop_layout = importlib.import_module(path)
            break
        except ImportError:
            continue

    # ── 手機版（多種命名都支援）──────────────────
    mobile_layout = None
    for path in ["ui_mobile.layout", "ui_mobile.layout_mobile", "layout_mobile"]:
        try:
            mobile_layout = importlib.import_module(path)
            break
        except ImportError:
            continue

    if desktop_layout is None:
        st.warning("⚠️ 桌面版模組未找到")
    if mobile_layout is None:
        st.warning("⚠️ 手機版模組未找到")

    return desktop_layout, mobile_layout


st.set_page_config(
    page_title="Titan SOP V100.0 - Ray of Hope",
    layout="wide",
    page_icon="🌅",
    initial_sidebar_state="collapsed"
)

import pandas as pd
from datetime import datetime, timedelta

# ── Session State ────────────────────────────────────────────
for k, v in {
    'animation_shown':  False,
    'device_mode':      None,
    'choice_confirmed': False,
    'api_key':          '',
    'intel_files':      [],
    'df':               pd.DataFrame(),
    'mobile_page':      'macro',
    'last_active_time': datetime.now(),
    'portfolio_df': pd.DataFrame([
        {'資產代號': '2330.TW', '持有數量 (股)': 1000, '買入均價': 550.0,     '資產類別': 'Stock'},
        {'資產代號': 'NVDA',    '持有數量 (股)': 10,   '買入均價': 400.0,     '資產類別': 'US_Stock'},
        {'資產代號': 'TLT',     '持有數量 (股)': 20,   '買入均價': 95.0,      '資產類別': 'US_Bond'},
        {'資產代號': 'CASH',    '持有數量 (股)': 1,    '買入均價': 500000.0,  '資產類別': 'Cash'},
    ]),
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

_now = datetime.now()
if (_now - st.session_state.last_active_time) > timedelta(minutes=120):
    pass  # 由各 tab 處理重置
st.session_state.last_active_time = _now

# ── Main CSS ─────────────────────────────────────────────────
MAIN_CSS = """
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
        color: #FFFFFF;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .choice-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%);
        border: 2px solid #444;
        border-radius: 24px;
        padding: 60px 40px;
        text-align: center;
        transition: all 0.4s ease;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .choice-icon  { font-size: 80px; margin-bottom: 20px; }
    .choice-title { font-size: 28px; font-weight: bold; color: #FFD700; margin-bottom: 16px; }
    .choice-subtitle { font-size: 16px; color: #AAAAAA; line-height: 1.6; }
    .page-title {
        font-size: 48px; font-weight: bold; text-align: center;
        color: #FFD700;
        text-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
        margin-bottom: 20px;
    }
    .page-subtitle { font-size: 20px; text-align: center; color: #AAAAAA; margin-bottom: 60px; }
    div.stButton > button {
        background: linear-gradient(135deg, #00FF00 0%, #00CC00 100%);
        color: #000000; font-size: 18px; font-weight: bold;
        border-radius: 12px; border: none;
        box-shadow: 0 4px 16px rgba(0, 255, 0, 0.3);
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0 8px 24px rgba(0, 255, 0, 0.5);
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
</style>
"""
st.markdown(MAIN_CSS, unsafe_allow_html=True)


# ── 日出動畫 ─────────────────────────────────────────────────
def render_sunrise_animation():
    lottie_data = load_lottie_url(get_lottie_animation("sunrise"))
    if lottie_data:
        try:
            from streamlit_lottie import st_lottie
            st_lottie(lottie_data, speed=1.0, height=300, key="sunrise")
        except Exception:
            pass

    st.markdown("""
        <h1 style='text-align:center; color:#FFD700;
            text-shadow:0 0 10px rgba(255,215,0,0.7), 0 0 20px rgba(255,215,0,0.5);
            font-size:3em; letter-spacing:2px;'>🌅 Titan SOP V100.0</h1>
        <p style='text-align:center; font-size:1.5rem; color:#AAAAAA; margin-top:16px;'>
            在混亂的股海中，這是你的希望之光。</p>
    """, unsafe_allow_html=True)

    if st.button("🚀 確認進入戰情室", use_container_width=True):
        st.session_state.animation_shown = True
        st.rerun()


# ── 裝置選擇 ─────────────────────────────────────────────────
def render_device_selection():
    st.markdown('<div class="page-title">🏛️ Titan SOP V100.0</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Choose Your Battle Station | 選擇你的戰鬥模式</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div class="choice-card">
            <div class="choice-icon">🖥️</div>
            <div class="choice-title">Desktop War Room</div>
            <div class="choice-subtitle">
                Bloomberg Terminal 風格<br>
                高密度資訊顯示<br>
                專業級數據分析<br>
                適合：深度研究、多螢幕操作
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("⚔️ Enter Desktop Mode", key="desktop_btn", use_container_width=True):
            st.session_state.device_mode     = "desktop"
            st.session_state.choice_confirmed = True
            st.rerun()

    with col2:
        st.markdown("""
        <div class="choice-card">
            <div class="choice-icon">📱</div>
            <div class="choice-title">Mobile Command Post</div>
            <div class="choice-subtitle">
                Netflix / Robinhood 風格<br>
                大按鈕 + 底部導航列<br>
                觸控完全重設計<br>
                適合：快速決策、移動狙擊
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("🎯 Enter Mobile Mode", key="mobile_btn", use_container_width=True):
            st.session_state.device_mode     = "mobile"
            st.session_state.choice_confirmed = True
            st.rerun()

    st.markdown("---")
    st.markdown('<div style="text-align:center; color:#666; font-size:14px; margin-top:20px;">'
                '💡 提示：選擇後可隨時在設定中切換模式</div>', unsafe_allow_html=True)


# ── UI 路由 ──────────────────────────────────────────────────
def render_ui():
    desktop_layout, mobile_layout = import_ui_modules()

    if st.session_state.device_mode == "desktop":
        if desktop_layout is None:
            st.error("❌ 桌面版模組載入失敗，請確認 ui_desktop/layout.py 存在")
            if st.button("🔄 重新選擇", key="retry_d"):
                st.session_state.choice_confirmed = False
                st.rerun()
            return
        try:
            desktop_layout.render()
        except Exception as e:
            st.error(f"❌ 桌面版渲染失敗: {e}")
            import traceback; st.code(traceback.format_exc())

    elif st.session_state.device_mode == "mobile":
        if mobile_layout is None:
            st.error("❌ 手機版模組載入失敗，請確認 ui_mobile/layout_mobile.py 存在")
            if st.button("🔄 重新選擇", key="retry_m"):
                st.session_state.choice_confirmed = False
                st.rerun()
            return
        try:
            mobile_layout.render()
        except Exception as e:
            st.error(f"❌ 手機版渲染失敗: {e}")
            import traceback; st.code(traceback.format_exc())


# ── 主流程 ───────────────────────────────────────────────────
def main():
    if not st.session_state.animation_shown:
        render_sunrise_animation()
        return
    if st.session_state.device_mode is None or not st.session_state.choice_confirmed:
        render_device_selection()
        return
    render_ui()


if __name__ == "__main__":
    main()